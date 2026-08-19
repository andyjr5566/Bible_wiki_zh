import sys
import tempfile
import unittest
from pathlib import Path

UTIL_DIR = Path(__file__).resolve().parents[1]
if str(UTIL_DIR) not in sys.path:
    sys.path.insert(0, str(UTIL_DIR))

import yaml

import check_chapter_files as ccf

BOOK = "創世記"
CHAPTER = 1


def _write(path, content=""):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_yaml(path, data):
    _write(path, yaml.safe_dump(data, allow_unicode=True))


class CheckChapterFilesTests(unittest.TestCase):
    def _root(self, tmp):
        root = Path(tmp)
        (root / "01 創世記").mkdir(parents=True, exist_ok=True)
        return root

    def test_stops_reporting_at_first_missing_step(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(tmp)
            _write(root / "raw_scripture" / BOOK / f"第{CHAPTER}章.txt", "1. 起初神創造天地。")
            # source_manifest.md 缺 → 步驟1 應是第一個失敗項
            checks = ccf.build_checks(BOOK, CHAPTER, root=root)
            labels_ok = [(label, ok) for label, ok, _ in checks]
            self.assertTrue(labels_ok[0][1], "raw_scripture 存在應通過")
            self.assertFalse(labels_ok[1][1], "source_manifest.md 缺檔應回報失敗")
            self.assertIn("步驟1", labels_ok[1][0])
            _, _, hint = checks[1]
            self.assertIn("source_manifest.md", hint)

    def _write_synced_embedding_index(self, root):
        """空條目庫（link_index={}）對空索引＝同步。"""
        _write(
            root / "util" / "output" / "embedding_index.meta.json",
            '{"model": "test-embed", "dim": 4, "entries": []}',
        )
        _write(root / "util" / "output" / "embedding_index.npz", "dummy")

    def _write_fresh_similarity_report(self, tmp_dir, root):
        from semantic_lookup import _file_sha256, RERANK_POLICY_VERSION
        from build_embedding_index import compute_index_fingerprint
        meta_path = root / "util" / "output" / "embedding_index.meta.json"
        fp = "none"
        if meta_path.is_file():
            import json
            fp = compute_index_fingerprint(json.loads(meta_path.read_text(encoding="utf-8")))
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
            "rerank_model: test-reranker\n"
            f"rerank_policy_version: {RERANK_POLICY_VERSION}\n"
            f"calibration_sha256: {_file_sha256(root / '_config' / 'reranker_calibration.yaml')}\n"
            "rerank_status: success\n"
            "-->\n\n# 候選語義近鄰報告\n"
        )
        _write(tmp_dir / "candidate_similarity.md", meta)

    def test_all_major_files_present_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(tmp)
            tmp_dir = root / "01 創世記" / ".tmp" / f"第{CHAPTER}章"
            _write(root / "raw_scripture" / BOOK / f"第{CHAPTER}章.txt", "1. 起初神創造天地。")
            _write(tmp_dir / "source_manifest.md", "manifest")
            _write(tmp_dir / "link_candidates.yaml", "candidates")
            _write(root / "util" / "output" / "link_index.json", "{}")
            _write(root / "util" / "output" / "link_quality_report.json", "{}")
            _write(root / "util" / "output" / "verify_report.json", "{}")
            _write(root / "util" / "output" / "verify_result.txt", "ok")
            self._write_synced_embedding_index(root)
            self._write_fresh_similarity_report(tmp_dir, root)
            _write_yaml(tmp_dir / "link_plan.yaml", {"C_new_formal": [], "B_needs_update": []})
            _write(tmp_dir / "verse_links.yaml", "links")
            _write(tmp_dir / "chapter_content.yaml", "content")
            _write(root / "01 創世記" / f"第{CHAPTER}章.md", "# 第1章")

            checks = ccf.build_checks(BOOK, CHAPTER, root=root)
            failed = [label for label, ok, _ in checks if not ok]
            self.assertEqual([], failed)

    def test_preflight_passes_with_only_steps_1_and_2(self):
        """--preflight 模式只驗證前置包（經文、manifest、candidates、fresh similarity report）。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(tmp)
            tmp_dir = root / "01 創世記" / ".tmp" / f"第{CHAPTER}章"
            _write(root / "raw_scripture" / BOOK / f"第{CHAPTER}章.txt", "1. 起初神創造天地。")
            _write(tmp_dir / "source_manifest.md", "manifest")
            _write(tmp_dir / "link_candidates.yaml", "candidates")
            _write(root / "util" / "output" / "link_index.json", "{}")
            self._write_synced_embedding_index(root)
            self._write_fresh_similarity_report(tmp_dir, root)

            checks = ccf.build_checks(BOOK, CHAPTER, root=root, preflight=True)
            self.assertEqual(4, len(checks))  # 只有步驟1與步驟2的4個檢查項
            failed = [label for label, ok, _ in checks if not ok]
            self.assertEqual([], failed)

    def test_stale_candidate_similarity_fails_check(self):
        """候選檔被修改後，未重跑 semantic_lookup 導致 hash 不一致時判定失敗。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(tmp)
            tmp_dir = root / "01 創世記" / ".tmp" / f"第{CHAPTER}章"
            _write(root / "raw_scripture" / BOOK / f"第{CHAPTER}章.txt", "1. 起初神創造天地。")
            _write(tmp_dir / "source_manifest.md", "manifest")
            _write(tmp_dir / "link_candidates.yaml", "candidates_v1")
            _write(root / "util" / "output" / "link_index.json", "{}")
            self._write_synced_embedding_index(root)
            self._write_fresh_similarity_report(tmp_dir, root)

            # 修改 candidates 檔案使其與報告記載之 hash 不符
            _write(tmp_dir / "link_candidates.yaml", "candidates_v2_modified")

            checks = ccf.build_checks(BOOK, CHAPTER, root=root, preflight=True)
            sim_check = next(c for c in checks if "candidate_similarity" in c[0])
            self.assertFalse(sim_check[1])
            self.assertIn("候選檔已變更", sim_check[2])

    def test_missing_similarity_report_fails_step2(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(tmp)
            tmp_dir = root / "01 創世記" / ".tmp" / f"第{CHAPTER}章"
            _write(tmp_dir / "link_candidates.yaml", "candidates")

            checks = ccf.build_checks(BOOK, CHAPTER, root=root)
            report_check = next(c for c in checks if "candidate_similarity" in c[0])
            self.assertFalse(report_check[1])
            self.assertIn("--candidates", report_check[2])

    def test_stale_embedding_index_fails_final_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(tmp)
            # link_index 有一條，meta 是空的 → 1 條未入索引
            _write(
                root / "util" / "output" / "link_index.json",
                '{"甲": {"title": "甲", "type": "主題", "path": "link_folder/主題/甲.md", "aliases": []}}',
            )
            self._write_synced_embedding_index(root)

            checks = ccf.build_checks(BOOK, CHAPTER, root=root)
            embed_check = next(c for c in checks if "embedding" in c[0])
            self.assertFalse(embed_check[1])
            self.assertIn("build_embedding_index", embed_check[2])

    def test_absent_embedding_index_fails_with_bootstrap_hint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(tmp)
            checks = ccf.build_checks(BOOK, CHAPTER, root=root)
            embed_check = next(c for c in checks if "embedding" in c[0])
            self.assertFalse(embed_check[1])
            self.assertIn("索引不存在", embed_check[2])

    def test_entry_content_count_dedupes_plan_names(self):
        """C_new_formal 計畫可能同名重複（run_chapter.py 建 entry 前會去重）。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(tmp)
            tmp_dir = root / "01 創世記" / ".tmp" / f"第{CHAPTER}章"
            _write_yaml(tmp_dir / "link_plan.yaml", {
                "C_new_formal": [
                    {"name": "重複詞", "suggested_type": "神學"},
                    {"name": "重複詞", "suggested_type": "神學"},
                ],
                "B_needs_update": [],
            })
            _write(tmp_dir / "entry_content" / "重複詞.yaml", "name: 重複詞")

            checks = ccf.build_checks(BOOK, CHAPTER, root=root)
            entry_check = next(c for c in checks if "entry_content" in c[0])
            self.assertTrue(entry_check[1], "去重後 1 個候選對 1 個檔案應視為完成")

    def test_link_updates_skipped_when_plan_has_no_b_class(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(tmp)
            tmp_dir = root / "01 創世記" / ".tmp" / f"第{CHAPTER}章"
            _write_yaml(tmp_dir / "link_plan.yaml", {"C_new_formal": [], "B_needs_update": []})

            checks = ccf.build_checks(BOOK, CHAPTER, root=root)
            update_check = next(c for c in checks if "link_updates.yaml" in c[0])
            self.assertTrue(update_check[1], "計畫無 B 類候選時不應要求 link_updates.yaml")


if __name__ == "__main__":
    unittest.main()
