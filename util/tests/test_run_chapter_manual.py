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


if __name__ == "__main__":
    unittest.main()
