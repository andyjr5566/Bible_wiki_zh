import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from util.mcp import server


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
        self.assertTrue(result["passed"])
        self.assertEqual(calls[:2], ["build_link_index.py", "build_embedding_index.py"])
        self.assertNotIn("check_existing_links.py", calls)


if __name__ == "__main__":
    unittest.main()
