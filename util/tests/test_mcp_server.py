import io
import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from util.mcp import server
from util import check_chapter_files


class UtilExecutionFallbackTests(unittest.TestCase):
    """The server must still run the util CLIs on hosts that block spawning.

    Such a host does not fail fast — every ``subprocess.run`` blocks until its
    own timeout — so the gates were unusable until the in-process path existed.
    """

    def _script(self, root, body):
        path = Path(root) / "fake_gate.py"
        path.write_text(body, encoding="utf-8")
        return path

    def test_in_process_run_captures_stdout_and_returncode(self):
        with tempfile.TemporaryDirectory() as name:
            script = self._script(name, "import sys\nprint('結論：PASS')\nsys.exit(0)\n")
            result = server._exec_util_inprocess(script, [], 30, ["cmd"])
        self.assertEqual(result["returncode"], 0)
        self.assertIn("結論：PASS", result["stdout"])
        self.assertTrue(result["in_process"])

    def test_in_process_run_reports_nonzero_exit(self):
        with tempfile.TemporaryDirectory() as name:
            script = self._script(name, "import sys\nprint('結論：FAIL')\nsys.exit(2)\n")
            result = server._exec_util_inprocess(script, [], 30, ["cmd"])
        self.assertEqual(result["returncode"], 2)

    def test_in_process_run_passes_argv_through_then_restores_it(self):
        before = sys.argv[:]
        with tempfile.TemporaryDirectory() as name:
            script = self._script(name, "import sys\nprint('|'.join(sys.argv[1:]))\n")
            result = server._exec_util_inprocess(script, ["利未記", "14"], 30, ["cmd"])
        self.assertIn("利未記|14", result["stdout"])
        self.assertEqual(sys.argv, before, "the server's own argv must not be clobbered")

    def test_in_process_run_survives_a_crashing_cli(self):
        with tempfile.TemporaryDirectory() as name:
            script = self._script(name, "raise RuntimeError('boom')\n")
            result = server._exec_util_inprocess(script, [], 30, ["cmd"])
        self.assertEqual(result["returncode"], 1)
        self.assertIn("boom", result["stderr"])

    def test_blocked_spawn_is_detected_and_not_retried(self):
        calls = []

        def fake_run(*args, **kwargs):
            calls.append(args)
            raise subprocess.TimeoutExpired(cmd="probe", timeout=10)

        with patch.object(server, "_spawn_allowed", None), patch.object(
            subprocess, "run", fake_run
        ):
            self.assertFalse(server._can_spawn())
            self.assertFalse(server._can_spawn())
        self.assertEqual(len(calls), 1, "the probe must be cached, not repeated per call")

    def test_probe_spawns_a_grandchild(self):
        """A one-level probe passes on hosts that block only nested spawning.

        check_chapter_files.py runs ``git`` itself, so it still hung at 180s
        after the one-level probe reported success.
        """
        seen = []

        def fake_run(cmd, **kwargs):
            seen.append(cmd)
            raise subprocess.TimeoutExpired(cmd="probe", timeout=10)

        with patch.object(server, "_spawn_allowed", None), patch.object(
            subprocess, "run", fake_run
        ):
            server._can_spawn()
        self.assertIn("subprocess", seen[0][-1], "the probe itself must spawn a child")

    def test_a_spawn_that_times_out_retries_in_process_and_stops_spawning(self):
        with tempfile.TemporaryDirectory() as name:
            script = self._script(name, "print('結論：PASS')\n")

            def fake_run(cmd, **kwargs):
                raise subprocess.TimeoutExpired(cmd=cmd, timeout=1)

            with patch.object(server, "_spawn_allowed", True), patch.object(
                subprocess, "run", fake_run
            ):
                result = server._exec_util(script, [], 30)
                self.assertFalse(server._spawn_allowed, "later calls must skip the wait")
        self.assertTrue(result["in_process"])
        self.assertIn("結論：PASS", result["stdout"])

    def test_exec_util_falls_back_to_in_process_when_spawn_is_blocked(self):
        with tempfile.TemporaryDirectory() as name:
            script = self._script(name, "print('結論：PASS')\n")
            with patch.object(server, "_spawn_allowed", False):
                result = server._exec_util(script, [], 30)
        self.assertTrue(result["in_process"])
        self.assertIn("結論：PASS", result["stdout"])

    def test_a_timed_out_worker_never_writes_to_the_real_stdout(self):
        """A stdio MCP server's stdout is the protocol; a leaked worker must miss it.

        The worker outlives the call that started it, so restoring the stream on
        timeout — which is what ``redirect_stdout`` does — would put the CLI's
        later output straight into the JSON-RPC stream.
        """
        with tempfile.TemporaryDirectory() as name:
            script = self._script(
                name,
                "import time\n"
                "time.sleep(0.4)\n"
                "print('這行不可以進入 stdio 傳輸')\n",
            )
            real = io.StringIO()
            with patch.object(sys, "stdout", real), patch.object(
                server, "_stdout_router", None
            ), patch.object(server, "_stderr_router", None):
                result = server._exec_util_inprocess(script, [], 0.05, ["cmd"])
                self.assertTrue(result["timed_out"])
                time.sleep(0.8)  # let the leaked worker reach its print
                print("呼叫端自己的輸出仍要送到真正的 stdout")
            self.assertNotIn("這行不可以進入 stdio 傳輸", real.getvalue())
            self.assertIn("呼叫端自己的輸出", real.getvalue())


class ChapterStatusGitTests(unittest.TestCase):
    """``get_chapter_status`` calls ``build_checks`` directly, not through ``_exec_util``.

    That library call shells out to ``git`` on its own, so the spawn fallback
    did not cover it: on a host that blocks child processes it hung with no
    bound at all until the client aborted at 1800s, while the same CLI takes
    about 2s in a shell.
    """

    def setUp(self):
        self.addCleanup(check_chapter_files.disable_git, None)

    def test_git_call_is_bounded_and_latches_off_after_a_hang(self):
        calls = []

        def fake_run(cmd, **kwargs):
            calls.append(kwargs.get("timeout"))
            raise subprocess.TimeoutExpired(cmd=cmd, timeout=kwargs.get("timeout"))

        check_chapter_files.disable_git(None)
        with patch.object(check_chapter_files.subprocess, "run", fake_run):
            self.assertIsNone(check_chapter_files._git_lines_z(ROOT, "status"))
            self.assertIsNone(check_chapter_files._git_lines_z(ROOT, "ls-files"))
        self.assertEqual(len(calls), 1, "the second call must not pay the timeout again")
        self.assertIsNotNone(calls[0], "an unbounded git call is what hung the server")
        self.assertIsNotNone(check_chapter_files.git_disabled_reason())

    def test_untracked_findings_degrade_to_empty_when_git_is_disabled(self):
        check_chapter_files.disable_git("測試")
        errors, pending, notes = check_chapter_files.untracked_entry_findings(
            ROOT, "利未記", 16
        )
        self.assertEqual((errors, pending, notes), ([], [], []))

    def test_status_disables_git_when_the_host_blocks_spawning(self):
        check_chapter_files.disable_git(None)
        with patch.object(server, "_spawn_allowed", False):
            result = server.get_chapter_status("利未記", 16)
        self.assertTrue(result["success"])
        self.assertIn("git_checks_skipped", result, "a skipped check must not read as passed")

    def test_status_keeps_git_enabled_when_spawning_works(self):
        check_chapter_files.disable_git(None)
        with patch.object(server, "_spawn_allowed", True):
            server.get_chapter_status("利未記", 16)
        self.assertIsNone(check_chapter_files.git_disabled_reason())


class MCPReadBoundaryTests(unittest.TestCase):
    def _index(self, root):
        entry = {
            "title": "測試條目",
            "path": "link_folder/神學/測試條目.md",
            "type": "神學",
            "secondary_types": [],
            "status": "formal",
            "aliases": ["測試別名"],
        }
        index = {"測試條目": entry, "測試別名": {"alias_of": "測試條目"}}
        path = root / "util" / "output" / "link_index.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
        return entry

    def test_reads_only_indexed_link_folder_entry(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            entry = self._index(root)
            path = root / entry["path"]
            path.parent.mkdir(parents=True)
            path.write_text("# 測試條目\n\n內容", encoding="utf-8")
            with patch.object(server, "ROOT_DIR", root):
                result = server.read_wiki_entry("測試別名")
            self.assertTrue(result["success"])
            self.assertEqual("測試條目", result["title"])
            self.assertEqual("# 測試條目\n\n內容", result["content"])

    def test_rejects_parent_traversal_instead_of_reading_it(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "vault"
            root.mkdir()
            self._index(root)
            outside = root.parent / "secret.md"
            outside.write_text("不得讀取", encoding="utf-8")
            with patch.object(server, "ROOT_DIR", root):
                result = server.read_wiki_entry("../secret.md")
            self.assertFalse(result["success"])
            self.assertNotIn("content", result)

    def test_linter_treats_path_like_input_as_text(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("[[不該讀取]]", encoding="utf-8")
            with patch.object(server, "ROOT_DIR", root):
                result = server.lint_chapter_content("README.md")
            self.assertTrue(result["success"])
            self.assertTrue(result["passed"])

    def test_searches_aliases_from_canonical_index(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            entry = self._index(root)
            path = root / entry["path"]
            path.parent.mkdir(parents=True)
            path.write_text("# 測試條目", encoding="utf-8")
            with patch.object(server, "ROOT_DIR", root):
                result = server.search_wiki_entries("測試別名")
            self.assertTrue(result["success"])
            self.assertEqual("exact_alias", result["results"][0]["matched_by"])


class ManualCompletionTests(unittest.TestCase):
    def test_missing_m3_and_m6_are_incomplete(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tmp = root / "01 創世記" / ".tmp" / "第1章"
            tmp.mkdir(parents=True)
            (tmp / "link_plan.yaml").write_text(
                "C_new_formal:\n  - name: 新條目\n", encoding="utf-8"
            )
            with patch.object(server, "ROOT_DIR", root):
                missing = server._manual_completion("創世記", 1)
            self.assertTrue(any("C 類條目" in item for item in missing))
            self.assertTrue(any("chapter_content.yaml" in item for item in missing))


class StepExtractorToolTests(unittest.TestCase):
    def test_tool_uses_fixed_safe_paths_and_canonical_filename(self):
        calls = []

        def fake_run(script, *args, timeout=300):
            calls.append((script, args, timeout))
            return {"success": True, "returncode": 0, "stdout": "", "stderr": ""}

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "raw_data").mkdir()
            with patch.object(server, "ROOT_DIR", root), patch.object(server, "_run_util_command", fake_run):
                result = server.extract_stepbible(
                    "約翰福音", 1, verse_start=1, verse_end=5, download=True
                )
        self.assertTrue(result["success"])
        self.assertEqual("raw_data/stepbible_john_1_1-5.txt", result["path"])
        script, args, timeout = calls[0]
        self.assertEqual("extract_stepbible.py", script)
        self.assertIn("約翰福音 1:1-5", args)
        self.assertIn(".stepbible_data", args)
        self.assertIn("raw_data", args)
        self.assertIn("--download", args)
        self.assertLessEqual(timeout, 900)

    def test_tool_rejects_bad_range_before_running(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(server, "ROOT_DIR", root), patch.object(server, "_run_util_command") as run:
                result = server.extract_stepbible("創世記", 1, verse_start=5, verse_end=1)
        self.assertFalse(result["success"])
        run.assert_not_called()


class StepContextToolTests(unittest.TestCase):
    @staticmethod
    def _write_step(root):
        ref = server.step_extractor.parse_reference("Genesis 1")
        word = server.step_extractor.WordEntry(
            reference="Gen.1.1", position=1, word="בָּרָא", transliteration="bārāʾ",
            gloss="created", strongs_raw="H1254A", strongs=["H1254A"],
            main_strong="H1254A", morphology_raw="V-Qal-3ms",
            morphology="V-Qal-3ms", lexicon_short="create",
        )
        path = root / "raw_data" / "stepbible_genesis_1.txt"
        path.parent.mkdir(parents=True)
        path.write_text(
            server.step_extractor.render_markdown(ref, {1: [word]}, False),
            encoding="utf-8",
        )
        return path

    def test_queries_validated_local_projection_by_verse_and_exact_strong(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_step(root)
            with patch.object(server, "ROOT_DIR", root):
                result = server.query_step_context(
                    "創世記", 1, verses="1", strong="H1254A"
                )
        self.assertTrue(result["success"], result)
        self.assertEqual("PASS", result["validation"]["status"])
        self.assertEqual(1, result["metrics"]["occurrences"])
        self.assertIn("בָּרָא", result["context"])

    def test_existing_manifest_cannot_be_bypassed_by_unlisted_raw_step(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_step(root)
            tmp = root / "01 創世記" / ".tmp" / "第1章"
            tmp.mkdir(parents=True)
            (tmp / "source_manifest.md").write_text(
                "| 來源 | 類型 | URL | raw_data 檔案 | 狀態 |\n"
                "|---|---|---|---|---|\n"
                "| CT | 逐節註解 | https://x/ct | raw_data/ct.txt | OK |\n",
                encoding="utf-8",
            )
            with patch.object(server, "ROOT_DIR", root):
                result = server.query_step_context("創世記", 1, verses="1-3")
        self.assertFalse(result["success"])
        self.assertIn("未宣告 OK STEP", result["error"])

    def test_tool_does_not_overwrite_without_explicit_flag(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "raw_data" / "stepbible_genesis_1.txt"
            target.parent.mkdir()
            target.write_text("existing", encoding="utf-8")
            with patch.object(server, "ROOT_DIR", root), patch.object(server, "_run_util_command") as run:
                result = server.extract_stepbible("創世記", 1)
        self.assertFalse(result["success"])
        self.assertIn("overwrite=true", result["error"])
        run.assert_not_called()

    def test_read_chapter_source_blocks_step_raw_bypass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_step(root)
            tmp = root / "01 創世記" / ".tmp" / "第1章"
            tmp.mkdir(parents=True)
            (tmp / "source_manifest.md").write_text(
                "| 來源 | 類型 | URL | raw_data 檔案 | 狀態 |\n"
                "|---|---|---|---|---|\n"
                "| STEP Bible | 原文資料 | https://x/step | raw_data/stepbible_genesis_1.txt | OK |\n",
                encoding="utf-8",
            )
            with patch.object(server, "ROOT_DIR", root):
                result = server.read_chapter_source("創世記", 1, source="STEP Bible")
            self.assertFalse(result["success"])
            self.assertIn("structured", result["error"])
            self.assertIn("find_step_candidates", result.get("advice", result["error"]))

    def test_read_chapter_source_allows_commentary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "raw_data").mkdir()
            (root / "raw_data" / "ct.txt").write_text("CT commentary body", encoding="utf-8")
            tmp = root / "01 創世記" / ".tmp" / "第1章"
            tmp.mkdir(parents=True)
            (tmp / "source_manifest.md").write_text(
                "| 來源 | 類型 | URL | raw_data 檔案 | 狀態 |\n"
                "|---|---|---|---|---|\n"
                "| CT | 逐節註解 | https://x/ct | raw_data/ct.txt | OK |\n",
                encoding="utf-8",
            )
            with patch.object(server, "ROOT_DIR", root):
                result = server.read_chapter_source("創世記", 1, source="CT")
            self.assertTrue(result["success"])
            self.assertIn("CT commentary body", result["content"])

    def test_find_step_candidates_tool(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_step(root)
            tmp = root / "01 創世記" / ".tmp" / "第1章"
            tmp.mkdir(parents=True)
            (tmp / "source_manifest.md").write_text(
                "| 來源 | 類型 | URL | raw_data 檔案 | 狀態 |\n"
                "|---|---|---|---|---|\n"
                "| STEP Bible | 原文資料 | https://x/step | raw_data/stepbible_genesis_1.txt | OK |\n",
                encoding="utf-8",
            )
            with patch.object(server, "ROOT_DIR", root):
                result = server.find_step_candidates("創世記", 1)
            self.assertTrue(result["success"])
            self.assertIn("candidates", result)
            self.assertIn("validation", result)
            self.assertEqual("PASS", result["validation"]["status"])

    def test_find_step_occurrences_tool(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_step(root)
            with patch.object(server, "ROOT_DIR", root):
                result = server.find_step_occurrences("創世記", 1, base_strong="H1254")
            self.assertTrue(result["success"])
            self.assertIn("occurrences", result)

    def test_query_step_context_base_strong(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_step(root)
            with patch.object(server, "ROOT_DIR", root):
                result = server.query_step_context("創世記", 1, base_strong="H1254")
            self.assertTrue(result["success"])
            self.assertIn("בָּרָא", result["context"])
            self.assertEqual(1, result["result_count"])
            self.assertFalse(result["truncated"])

    def test_query_step_context_rejects_empty_targets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_step(root)
            with patch.object(server, "ROOT_DIR", root):
                result = server.query_step_context("創世記", 1)
            self.assertFalse(result["success"])
            self.assertIn("至少必須提供", result["error"])

    def test_find_step_occurrences_mutual_exclusivity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_step(root)
            with patch.object(server, "ROOT_DIR", root):
                # Both strong and base_strong provided -> error
                result_both = server.find_step_occurrences("創世記", 1, strong="H1254A", base_strong="H1254")
                self.assertFalse(result_both["success"])
                self.assertIn("不可同時指定", result_both["error"])

                # Neither provided -> error
                result_none = server.find_step_occurrences("創世記", 1)
                self.assertFalse(result_none["success"])
                self.assertIn("必須指定", result_none["error"])

    def test_find_step_candidates_include_low(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_step(root)
            with patch.object(server, "ROOT_DIR", root):
                res_default = server.find_step_candidates("創世記", 1, include_low=False)
                res_with_low = server.find_step_candidates("創世記", 1, include_low=True)
            self.assertTrue(res_default["success"])
            self.assertTrue(res_with_low["success"])
            self.assertIn("result_count", res_default)
            self.assertIn("truncated", res_default)
            self.assertIn("max_results", res_default)
            self.assertIn("chapters_scanned", res_default)
            self.assertGreaterEqual(res_with_low["result_count"], res_default["result_count"])




class MCPUpdateTokenTests(unittest.TestCase):
    def test_apply_rejects_a_preview_token_when_target_changed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            entry = root / "link_folder" / "主題" / "測試.md"
            entry.parent.mkdir(parents=True)
            entry.write_text(
                "# 測試\n\n## 按書卷累積\n\n## 主題發展\n", encoding="utf-8"
            )
            tmp = root / "01 創世記" / ".tmp" / "第1章"
            tmp.mkdir(parents=True)
            (tmp / "link_updates.yaml").write_text(
                "book: 創世記\nchapter: 1\nupdates:\n"
                "  - title: 測試\n"
                "    path: link_folder/主題/測試.md\n"
                "    summary: 本章重點\n"
                "    relation: 本章關聯\n",
                encoding="utf-8",
            )
            with patch.object(server, "ROOT_DIR", root), patch.object(server.link_updates, "ROOT", root):
                preview = server.preview_chapter_link_updates("創世記", 1)
                self.assertTrue(preview["success"])
                entry.write_text(entry.read_text(encoding="utf-8") + "\n外部修改\n", encoding="utf-8")
                result = server.apply_chapter_link_updates("創世記", 1, preview["preview_token"])
            self.assertFalse(result["success"])
            self.assertIn("preview_token", result["error"])


class LintChapterContentTests(unittest.TestCase):
    """Each rule below was measured corpus-wide at 0 false positives before landing."""

    def _errors(self, text, content_kind="markdown"):
        result = server.lint_chapter_content(text, content_kind)
        self.assertTrue(result["success"])
        return "\n".join(result["errors"])

    def test_flags_every_hard_format_rule(self):
        cases = {
            "```mermaid\ngraph LR\n  A[[巴蘭]] --> B\n```": "Mermaid",
            "![[圖.png]]": "![[",
            "<div>x</div>": "HTML",
            "## 參考資料\n\n- 某書": "參考資料",
            "| 欄 | 值 |\n|---|---|\n| [[甲|乙]] | x |": "表格",
            "舊版整段漏掉。": "流程註記",
            "本次維護補上。": "流程註記",
            "引用時應並陳而非擇一。": "流程註記",
            "#研經 內容": "#標籤",
        }
        for text, expected in cases.items():
            with self.subTest(text=text[:24]):
                self.assertIn(expected, self._errors(text))

    def test_accepts_conforming_content(self):
        good = (
            "### 這一段（v1-5）\n\n散文。\n\n"
            "| 欄 | 值 |\n|---|---|\n| [[甲]] | 不帶別名 |\n\n"
            '```mermaid\ngraph LR\n  A["甲"] --> B["乙"]\n```\n'
        )
        result = server.lint_chapter_content(good, "markdown")
        self.assertTrue(result["passed"], result["errors"])

    def test_unquoted_mermaid_label_is_only_a_warning(self):
        result = server.lint_chapter_content("```mermaid\ngraph LR\n  A[巴蘭] --> B\n```", "markdown")
        self.assertTrue(result["passed"])
        self.assertTrue(any("引號" in item for item in result["warnings"]))

    def test_self_wrapped_knowledge_node_flagged_in_yaml(self):
        payload = "knowledge_nodes:\n  人物:\n    - [[雅各]]\norganization: |\n  文字\n"
        self.assertIn("雙重括號", self._errors(payload, "yaml"))
        clean = "knowledge_nodes:\n  人物:\n    - 雅各\norganization: |\n  文字\n"
        self.assertEqual(self._errors(clean, "yaml"), "")

    def test_hash_heading_is_not_a_hashtag(self):
        self.assertEqual(self._errors("## 標題\n### 小標題（v1-3）"), "")


class ScanUnsourcedTokensTests(unittest.TestCase):
    def _chapter(self, root, entry_body):
        (root / "raw_data").mkdir(parents=True)
        # The corpus holds the bare Hebrew form; the entry may carry niqqud.
        (root / "raw_data" / "src.txt").write_text(
            "來源提到 Peniel 與 שלום，還有 temperate 這個字。", encoding="utf-8"
        )
        entry = root / "link_folder" / "原文" / "測試條目.md"
        entry.parent.mkdir(parents=True)
        entry.write_text(entry_body, encoding="utf-8")
        tmp = root / "01 創世記" / ".tmp" / "第1章"
        tmp.mkdir(parents=True)
        (tmp / "chapter_content.yaml").write_text(
            "knowledge_nodes:\n  原文:\n    - 測試條目\norganization: |\n  文字\n",
            encoding="utf-8",
        )

    def test_flags_a_bare_transliteration_introduced_by_a_marker_phrase(self):
        """利14 實測：杜撰的「希伯來文 mayim chayyim」不在括號也不是斜體。"""
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            self._chapter(root, "活水的希伯來文 mayim chayyim，指流動的水。\n")
            with patch.object(server, "ROOT_DIR", root):
                result = server.scan_unsourced_tokens("創世記", 1)
        latin = {item["token"] for item in result["unsourced_latin"]}
        self.assertIn("mayim chayyim", latin)

    def test_marker_phrase_does_not_flag_a_sourced_transliteration(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            self._chapter(root, "這地的希伯來文 Peniel 就是本節的用字。\n")
            with patch.object(server, "ROOT_DIR", root):
                result = server.scan_unsourced_tokens("創世記", 1)
        latin = {item["token"] for item in result["unsourced_latin"]}
        self.assertNotIn("Peniel", latin)

    def test_apostrophe_variant_is_reviewed_not_flagged_as_unsourced(self):
        """來源寫 Peniel、條目寫 Pen'iel：是拼法要對齊，不是查無出處。"""
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            self._chapter(root, "音譯 Pen'iel 見本節。\n")
            with patch.object(server, "ROOT_DIR", root):
                result = server.scan_unsourced_tokens("創世記", 1)
        hard = {item["token"] for item in result["unsourced_latin"]}
        review = {item["token"] for item in result["latin_needing_review"]}
        self.assertNotIn("Pen'iel", hard)
        self.assertIn("Pen'iel", review)

    def test_flags_only_tokens_absent_from_the_corpus(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            self._chapter(root, "有出處（Peniel）、查無出處（perat）、希伯來 שָׁלוֹם 與 אבגד\n")
            with patch.object(server, "ROOT_DIR", root):
                result = server.scan_unsourced_tokens("創世記", 1)
        self.assertTrue(result["success"])
        latin = {item["token"] for item in result["unsourced_latin"]}
        self.assertIn("perat", latin)          # word-boundary: not matched by "temperate"
        self.assertNotIn("Peniel", latin)      # present in the corpus
        hebrew = {item["token"] for item in result["unsourced_hebrew"]}
        self.assertIn("אבגד", hebrew)
        self.assertNotIn("שָׁלוֹם", hebrew)      # sourced once niqqud is stripped

    def test_clean_chapter_reports_no_flags(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            self._chapter(root, "只有中文與有出處的（Peniel）。\n")
            with patch.object(server, "ROOT_DIR", root):
                result = server.scan_unsourced_tokens("創世記", 1)
        self.assertEqual(result["flag_count"], 0)

    def test_pointed_corpus_form_counts_as_a_source(self):
        """STEP raw files are fully pointed; the corpus must be stripped too.

        Otherwise every vocalised form in STEP is invisible to the check and the
        entry's own lemma gets flagged as unsourced.
        """
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            self._chapter(root, "本節作 מִנְחָה，即素祭。\n")
            # A STEP-style raw file: same consonants, different pointing.
            (root / "raw_data" / "stepbible_x.txt").write_text(
                "| מִנְחָ֖ה | min.Chah | grain offering | H4503G |", encoding="utf-8"
            )
            with patch.object(server, "ROOT_DIR", root):
                result = server.scan_unsourced_tokens("創世記", 1)
        hebrew = {item["token"] for item in result["unsourced_hebrew"]}
        self.assertNotIn("מִנְחָה", hebrew)

    def test_transliteration_printed_against_cjk_counts_as_a_source(self):
        """These sources write the transliteration with no space around it.

        ``\\b`` treats CJK as word characters, so 「希伯來文shaphan音譯」 has no
        boundary on either side and the sourced token was reported as unsourced.
        """
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            self._chapter(root, "沙番（shaphan）是一種兔類的動物。\n")
            (root / "raw_data" / "gt_x.txt").write_text(
                "“沙番”從希伯來文shaphan音譯過來，一般認為就是“蹄兔”。", encoding="utf-8"
            )
            with patch.object(server, "ROOT_DIR", root):
                result = server.scan_unsourced_tokens("創世記", 1)
        latin = {item["token"] for item in result["unsourced_latin"]}
        self.assertNotIn("shaphan", latin)

    def test_substring_of_a_latin_word_is_still_unsourced(self):
        """Relaxing the bound must not let ``perat`` match ``temperate``."""
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            self._chapter(root, "伯拉大河（perat）。\n")
            (root / "raw_data" / "bh_x.txt").write_text(
                "a temperate climate encouraged cooperation", encoding="utf-8"
            )
            with patch.object(server, "ROOT_DIR", root):
                result = server.scan_unsourced_tokens("創世記", 1)
        latin = {item["token"] for item in result["unsourced_latin"]}
        self.assertIn("perat", latin)


class RunGatesTests(unittest.TestCase):
    def test_fail_conclusion_overrides_zero_exit_code(self):
        calls = []

        def fake_gate(script, *args, timeout=300):
            calls.append(script)
            failing = script == "check_accumulation_orphans.py"
            return {
                "gate": " ".join([script, *args]),
                "passed": not failing,
                "returncode": 0,
                "tail": "結論：FAIL" if failing else "結論：PASS",
                "stderr": "",
            }

        with patch.object(server, "_run_gate", fake_gate):
            result = server.run_gates("創世記", 1)
        self.assertFalse(result["success"])
        self.assertFalse(result["passed"])
        self.assertEqual(result["failed_gates"], ["check_accumulation_orphans.py 創世記"])
        self.assertIn("check_existing_links.py", calls)
        self.assertNotIn("build_link_index.py", calls)

    def test_rebuild_index_runs_both_index_builders_first(self):
        calls = []

        def fake_gate(script, *args, timeout=300):
            calls.append(script)
            return {"gate": script, "passed": True, "returncode": 0, "tail": "", "stderr": ""}

        with patch.object(server, "_run_gate", fake_gate):
            result = server.run_gates("創世記", rebuild_index=True)
        self.assertTrue(result["success"])
        self.assertTrue(result["passed"])
        self.assertEqual(calls[:2], ["build_link_index.py", "build_embedding_index.py"])
        self.assertNotIn("check_existing_links.py", calls)


if __name__ == "__main__":
    unittest.main()
