import argparse
import json
import sys
import tempfile
import unittest
from pathlib import Path

UTIL_DIR = Path(__file__).resolve().parents[1]
if str(UTIL_DIR) not in sys.path:
    sys.path.insert(0, str(UTIL_DIR))

import yaml

import run_chapter_manual as rcm
from semantic_lookup import _file_sha256, RERANK_POLICY_VERSION
from build_embedding_index import compute_index_fingerprint
from source_excerpts import SourceError


def _write(path, content=""):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_yaml(path, data):
    _write(path, yaml.safe_dump(data, allow_unicode=True))


class RunChapterManualFreshnessTests(unittest.TestCase):
    def _setup_root(self, tmp):
        root = Path(tmp)
        (root / "01 創世記").mkdir(parents=True, exist_ok=True)
        tmp_dir = root / "01 創世記" / ".tmp" / "第1章"
        _write(root / "raw_scripture" / "創世記" / "第1章.txt", "1. 起初神創造天地。")
        _write(tmp_dir / "source_manifest.md", (
            "| 來源 | 類型 | URL | raw_data 檔案 | 狀態 |\n"
            "|------|------|-----|---------------|------|\n"
            "| CT | commentary | https://example.com/ct | raw_data/創世記/1_1.txt | OK |\n"
            "| GT | commentary | https://example.com/gt | raw_data/創世記/1_2.txt | OK |\n"
            "| KC | commentary | https://example.com/kc | raw_data/創世記/1_3.txt | OK |\n"
            "| BH | commentary | https://example.com/bh | raw_data/創世記/1_4.txt | OK |\n"
            "| STEP | step_data | https://example.com/step | raw_data/創世記/1_5.txt | OK |\n"
        ))
        for kind in ["1_1.txt", "1_2.txt", "1_3.txt", "1_4.txt", "1_5.txt"]:
            _write(root / "raw_data" / "創世記" / kind, "起初神創造天地。\n" * 10)
        _write_yaml(tmp_dir / "link_candidates.yaml", {
            "book": "創世記",
            "chapter": 1,
            "candidates": [{"name": "創造", "type": "主題"}],
        })
        _write(root / "util" / "output" / "link_index.json", "{}")
        _write(root / "_config" / "link_homonyms.yaml", "{}")
        _write(root / "_config" / "reranker_calibration.yaml", "models: {}")
        _write(
            root / "_config" / "model_endpoints.yaml",
            yaml.safe_dump({
                "active": "test-ep",
                "endpoints": {
                    "test-ep": {
                        "type": "openai",
                        "base_url": "http://127.0.0.1:4001/v1",
                        "model": "test-model",
                    }
                },
                "tasks": {
                    "embedding": {
                        "endpoint": "test-ep",
                        "model": "test-embed",
                        "kind": "embedding",
                    },
                    "rerank": {
                        "endpoint": "test-ep",
                        "model": "test-reranker",
                        "kind": "rerank",
                    },
                },
            })
        )
        import numpy as np
        from build_embedding_index import _vectors_sha256, compute_index_fingerprint
        vectors = np.zeros((0, 4), dtype=np.float32)
        np.savez_compressed(root / "util" / "output" / "embedding_index.npz", vectors=vectors)
        meta = {
            "schema_version": 2,
            "model": "test-embed",
            "dim": 4,
            "input_type": "passage",
            "vectors_sha256": _vectors_sha256(vectors),
            "entries": [],
        }
        meta["index_fingerprint"] = compute_index_fingerprint(meta)
        _write(
            root / "util" / "output" / "embedding_index.meta.json",
            json.dumps(meta, ensure_ascii=False),
        )
        return root, tmp_dir

    def test_prompts_fails_when_similarity_report_missing(self):
        """當 candidate_similarity.md 缺失時，cmd_prompts 拋出 SourceError 阻止生成。"""
        with tempfile.TemporaryDirectory() as tmp:
            root, tmp_dir = self._setup_root(tmp)
            args = argparse.Namespace(book="創世記", chapter=1, confirm_stale=False, batch_size=9999, root=root)
            with self.assertRaises(SourceError) as ctx:
                rcm.cmd_prompts(args)
            self.assertIn("candidate_similarity.md", str(ctx.exception))

    def test_prompts_fails_when_similarity_report_stale(self):
        """當 candidates 變更使 similarity report 過期時，cmd_prompts 拋出 SourceError。"""
        from build_embedding_index import compute_index_fingerprint
        with tempfile.TemporaryDirectory() as tmp:
            root, tmp_dir = self._setup_root(tmp)
            meta_json = json.loads((root / "util" / "output" / "embedding_index.meta.json").read_text(encoding="utf-8"))
            fp = compute_index_fingerprint(meta_json)
            meta = (
                "<!-- candidate_similarity_meta\n"
                "schema_version: 1\n"
                "book: 創世記\n"
                "chapter: 1\n"
                "candidate_sha256: 0000000000000000000000000000000000000000000000000000000000000000\n"
                "embedding_model: test-embed\n"
                f"embedding_index_fingerprint: {fp}\n"
                f"link_index_sha256: {_file_sha256(root / 'util' / 'output' / 'link_index.json')}\n"
                f"homonyms_sha256: {_file_sha256(root / '_config' / 'link_homonyms.yaml')}\n"
                "rerank_model: test-reranker\n"
                f"rerank_policy_version: {RERANK_POLICY_VERSION}\n"
                f"calibration_sha256: {_file_sha256(root / '_config' / 'reranker_calibration.yaml')}\n"
                "rerank_status: success\n"
                "rerankable_candidates: 1\n"
                "rerank_attempted: 1\n"
                "rerank_succeeded: 1\n"
                "-->\n\n# 候選語義近鄰報告\n"
            )
            _write(tmp_dir / "candidate_similarity.md", meta)

            args = argparse.Namespace(book="創世記", chapter=1, confirm_stale=False, batch_size=9999, root=root)
            with self.assertRaises(SourceError) as ctx:
                rcm.cmd_prompts(args)
            self.assertIn("candidate_similarity.md 不存在或已過期", str(ctx.exception))

    def test_check_fails_when_rerank_disabled(self):
        """當 candidate_similarity.md 狀態為 disabled 時，cmd_check 回報 check 未過。"""
        from build_embedding_index import compute_index_fingerprint
        with tempfile.TemporaryDirectory() as tmp:
            root, tmp_dir = self._setup_root(tmp)
            meta_json = json.loads((root / "util" / "output" / "embedding_index.meta.json").read_text(encoding="utf-8"))
            fp = compute_index_fingerprint(meta_json)
            meta = (
                "<!-- candidate_similarity_meta\n"
                "schema_version: 1\n"
                "book: 創世記\n"
                "chapter: 1\n"
                f"candidate_sha256: {_file_sha256(tmp_dir / 'link_candidates.yaml')}\n"
                "embedding_model: test-embed\n"
                f"embedding_index_fingerprint: {fp}\n"
                f"link_index_sha256: {_file_sha256(root / 'util' / 'output' / 'link_index.json')}\n"
                f"homonyms_sha256: {_file_sha256(root / '_config' / 'link_homonyms.yaml')}\n"
                "rerank_model: none\n"
                f"rerank_policy_version: {RERANK_POLICY_VERSION}\n"
                f"calibration_sha256: {_file_sha256(root / '_config' / 'reranker_calibration.yaml')}\n"
                "rerank_status: disabled\n"
                "rerankable_candidates: 0\n"
                "rerank_attempted: 0\n"
                "rerank_succeeded: 0\n"
                "-->\n\n# 候選語義近鄰報告\n"
            )
            _write(tmp_dir / "candidate_similarity.md", meta)
            _write_yaml(tmp_dir / "link_plan.yaml", {"C_new_formal": [], "B_needs_update": []})

            args = argparse.Namespace(book="創世記", chapter=1, no_rewrite=True, root=root)
            rc = rcm.cmd_check(args)
            self.assertEqual(1, rc, "disabled 報告必須使 cmd_check 回傳 1 失敗")

    def test_run_fails_when_rerank_disabled(self):
        """當 candidate_similarity.md 狀態為 disabled 時，cmd_run 拋出 SourceError 拒絕執行。"""
        from build_embedding_index import compute_index_fingerprint
        with tempfile.TemporaryDirectory() as tmp:
            root, tmp_dir = self._setup_root(tmp)
            meta_json = json.loads((root / "util" / "output" / "embedding_index.meta.json").read_text(encoding="utf-8"))
            fp = compute_index_fingerprint(meta_json)
            meta = (
                "<!-- candidate_similarity_meta\n"
                "schema_version: 1\n"
                "book: 創世記\n"
                "chapter: 1\n"
                f"candidate_sha256: {_file_sha256(tmp_dir / 'link_candidates.yaml')}\n"
                "embedding_model: test-embed\n"
                f"embedding_index_fingerprint: {fp}\n"
                f"link_index_sha256: {_file_sha256(root / 'util' / 'output' / 'link_index.json')}\n"
                f"homonyms_sha256: {_file_sha256(root / '_config' / 'link_homonyms.yaml')}\n"
                "rerank_model: none\n"
                f"rerank_policy_version: {RERANK_POLICY_VERSION}\n"
                f"calibration_sha256: {_file_sha256(root / '_config' / 'reranker_calibration.yaml')}\n"
                "rerank_status: disabled\n"
                "rerankable_candidates: 0\n"
                "rerank_attempted: 0\n"
                "rerank_succeeded: 0\n"
                "-->\n\n# 候選語義近鄰報告\n"
            )
            _write(tmp_dir / "candidate_similarity.md", meta)
            _write_yaml(tmp_dir / "link_plan.yaml", {"C_new_formal": [], "B_needs_update": []})

            args = argparse.Namespace(book="創世記", chapter=1, keep_chapter=False, root=root)
            with self.assertRaises(SourceError) as ctx:
                rcm.cmd_run(args)
            self.assertIn("禁止 rerank_status: disabled", str(ctx.exception))


class CmdPromptsInvalidationTests(unittest.TestCase):
    """直接打 cmd_prompts 本體，釘住它內部的作廢／回寫順序。

    只驗底層 API 串接是不夠的：把 cmd_prompts 裡的 _invalidate_after_plan 刪掉，
    那種測試照樣全綠，而 bug（verse_links 被靜默沿用）會無聲復活。
    """

    def _run_prompts(self, root):
        from unittest.mock import patch

        args = argparse.Namespace(
            book="出埃及記", chapter=26, root=root,
            confirm_stale=True, batch_size=None,
        )
        # 只擋掉與本測試無關的前置閘門（來源、相似度報告、STEP machine validation），
        # 作廢與回寫全部走真程式。
        with patch.object(rcm, "_require_sources", lambda ctx: {}), \
                patch.object(rcm, "_require_candidate_similarity", lambda ctx: None), \
                patch.object(rcm.rc.source_excerpts, "render_source_reading_plan",
                             lambda *a, **k: "# sources"), \
                patch.object(rcm.check_source_read, "validate_structured_sources",
                             lambda *a, **k: ([], {})):
            try:
                rcm.cmd_prompts(args)
            except Exception:
                # prompt 擷取階段本來就會以例外中止；本測試只看它之前的作廢行為。
                pass

    def test_cmd_prompts_invalidates_verse_links_before_advancing_the_baseline(self):
        from util.tests.test_run_chapter import OrchestratorTests, fake_runner
        import run_chapter

        helper = OrchestratorTests("test_untouched_candidates_still_resume")
        with tempfile.TemporaryDirectory() as tmp:
            root = helper._make_vault(tmp)
            run_chapter.run_chapter(
                "出埃及記", 26, root=root, runner=fake_runner, index={}, homonyms={},
            )
            tmp_dir = root / "02 出埃及記" / ".tmp" / "第26章"
            verse_links = tmp_dir / "verse_links.yaml"
            verse_links.write_text("# 過期佔位\n", encoding="utf-8")

            cand = tmp_dir / "link_candidates.yaml"
            data = yaml.safe_load(cand.read_text(encoding="utf-8"))
            data["candidates"][0]["surfaces"] = ["施恩座"]
            cand.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")

            self._run_prompts(root)

            self.assertFalse(
                verse_links.exists(),
                "cmd_prompts 推進基線之前必須先作廢 verse_links；"
                "少了 _invalidate_after_plan，run 會沿用這份過期檔且閘門全綠",
            )
            state = json.loads((tmp_dir / "pipeline_state.json").read_text(encoding="utf-8"))
            self.assertIn("link_plan.yaml", state, "基線仍應被推進，否則 run 會永遠拒絕執行")


class PipelineBaselineTests(unittest.TestCase):
    """細粒度作廢的基線回寫：這些漏洞都會靜默毀掉手寫 payload。"""

    def _ctx(self, tmp):
        root = Path(tmp)
        (root / "01 創世記" / ".tmp" / "第1章").mkdir(parents=True, exist_ok=True)
        return rcm.rc.ChapterContext("創世記", 1, root=root)

    def test_save_pipeline_nodes_writes_projection_keys_together(self):
        # 只回寫整檔指紋、不回寫投影指紋，會留下「半新半舊」的基線：
        # --keep-chapter 就是這樣把使用者明確要保留的 chapter_content 刪掉的。
        with tempfile.TemporaryDirectory() as tmp:
            ctx = self._ctx(tmp)
            entry_dir = ctx.path("entry_content")
            _write_yaml(entry_dir / "創造.yaml", {"name": "創造", "aliases": ["起初"]})

            rcm.rc.save_pipeline_nodes(ctx, ("entry_content",))
            state = rcm.rc._load_pipeline_state(ctx)
            self.assertIn("entry_content", state)
            self.assertIn(rcm.rc._ENTRY_IDENTITY_KEY, state)
            self.assertEqual(
                state[rcm.rc._ENTRY_IDENTITY_KEY],
                rcm.rc._entry_projection(entry_dir),
                "整檔指紋與投影指紋必須同一次寫入，不可只更新其中一個",
            )

    def test_save_pipeline_nodes_leaves_other_keys_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx = self._ctx(tmp)
            _write(ctx.path("link_plan.yaml"), "C_new_formal: []\n")
            rcm.rc._write_pipeline_state(ctx, {"chapter_content.yaml": "keep-me"})
            rcm.rc.save_pipeline_nodes(ctx, ("link_plan.yaml",))
            state = rcm.rc._load_pipeline_state(ctx)
            self.assertEqual("keep-me", state["chapter_content.yaml"])
            self.assertIn("link_plan.yaml", state)

    def test_entry_projection_distinguishes_empty_from_unreadable(self):
        # 條目被刪光時投影若回 None，_invalidate_edges 會當成「無基線」而完全不
        # 作廢，下游殘留過期的 wiki-link 與 surface 對照。
        with tempfile.TemporaryDirectory() as tmp:
            ctx = self._ctx(tmp)
            entry_dir = ctx.path("entry_content")
            empty = rcm.rc._entry_projection(entry_dir)
            self.assertIsNotNone(empty, "目錄不存在＝零條目，必須有指紋")

            entry_dir.mkdir(parents=True, exist_ok=True)
            self.assertEqual(empty, rcm.rc._entry_projection(entry_dir))

            _write_yaml(entry_dir / "創造.yaml", {"name": "創造", "aliases": []})
            populated = rcm.rc._entry_projection(entry_dir)
            self.assertIsNotNone(populated)
            self.assertNotEqual(empty, populated)

            for path in entry_dir.glob("*.yaml"):
                path.unlink()
            self.assertEqual(
                empty, rcm.rc._entry_projection(entry_dir),
                "刪光條目後必須回到零條目指紋，才能與基線比出差異",
            )

    def test_entry_projection_ignores_prose_edits(self):
        # 這是整個細粒度作廢要換來的東西：審查回合改條目正文不再連坐下游。
        with tempfile.TemporaryDirectory() as tmp:
            ctx = self._ctx(tmp)
            entry_dir = ctx.path("entry_content")
            _write_yaml(entry_dir / "創造.yaml", {
                "name": "創造", "aliases": ["起初"], "definition": "第一版",
            })
            before = rcm.rc._entry_projection(entry_dir)
            _write_yaml(entry_dir / "創造.yaml", {
                "name": "創造", "aliases": ["起初"], "definition": "改過的定義",
            })
            self.assertEqual(before, rcm.rc._entry_projection(entry_dir))

            _write_yaml(entry_dir / "創造.yaml", {
                "name": "創造", "aliases": ["起初", "太初"], "definition": "改過的定義",
            })
            self.assertNotEqual(
                before, rcm.rc._entry_projection(entry_dir),
                "aliases 變了必須作廢下游：verse_links 與別名驗證都吃它",
            )

    def test_plan_projection_ignores_surfaces(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx = self._ctx(tmp)
            plan_path = ctx.path("link_plan.yaml")
            plan = {
                "A_use_directly": [],
                "B_needs_update": [{"name": "光", "existing_title": "光（or）"}],
                "C_new_formal": [{"name": "創造", "suggested_type": "主題"}],
            }
            _write_yaml(plan_path, plan)
            entries = rcm.rc._plan_projection(plan_path, "entries")
            whitelist = rcm.rc._plan_projection(plan_path, "whitelist")

            plan["C_new_formal"][0]["surfaces"] = [{"phrase": "創造", "verses": [1]}]
            plan["B_needs_update"][0]["evidence"] = "改過的證據"
            _write_yaml(plan_path, plan)
            self.assertEqual(entries, rcm.rc._plan_projection(plan_path, "entries"))
            self.assertEqual(whitelist, rcm.rc._plan_projection(plan_path, "whitelist"))

            plan["C_new_formal"].append({"name": "諸水", "suggested_type": "主題"})
            _write_yaml(plan_path, plan)
            self.assertNotEqual(entries, rcm.rc._plan_projection(plan_path, "entries"))
            self.assertNotEqual(whitelist, rcm.rc._plan_projection(plan_path, "whitelist"))


if __name__ == "__main__":
    unittest.main()
