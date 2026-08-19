import json
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


def valid_step_text(reference="Genesis 1:1"):
    import extract_stepbible
    ref = extract_stepbible.parse_reference(reference)
    verse = ref.verse_start or 1
    strong = "H1254A" if ref.testament == "OT" else "G3056A"
    original = "בָּרָא" if ref.testament == "OT" else "λόγος"
    word = extract_stepbible.WordEntry(
        reference=f"{ref.code}.{ref.chapter}.{verse}",
        position=1,
        word=original,
        transliteration="bara" if ref.testament == "OT" else "logos",
        gloss="created" if ref.testament == "OT" else "word",
        strongs_raw=strong,
        strongs=[strong],
        main_strong=strong,
        morphology_raw="V-Qal-3ms" if ref.testament == "OT" else "N-NSM",
        morphology="V-Qal-3ms" if ref.testament == "OT" else "N-NSM",
        lexicon_short="create" if ref.testament == "OT" else "word; message",
    )
    return extract_stepbible.render_markdown(ref, {verse: [word]}, False)


class CheckChapterFilesTests(unittest.TestCase):
    def _root(self, tmp):
        root = Path(tmp)
        (root / "01 創世記").mkdir(parents=True, exist_ok=True)
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

    def _write_valid_sources(self, root, tmp_dir):
        (root / "raw_data").mkdir(parents=True, exist_ok=True)
        rows = [
            "| 來源 | 類型 | URL | raw_data 檔案 | 狀態 |",
            "|------|------|-----|---------------|------|",
        ]
        logs = ["# 來源讀取回執：創世記 第1章", ""]
        labels = [
            ("ccbiblestudy CT", "逐節註解", "https://www.ccbiblestudy.org/Old%20Testament/01Gen/01CT01.htm", "ccbiblestudy_CT_genesis_1.txt"),
            ("ccbiblestudy GT", "拾穗", "https://www.ccbiblestudy.org/Old%20Testament/01Gen/01GT01.htm", "ccbiblestudy_GT_genesis_1.txt"),
            ("KingComments", "研經註解", "https://www.kingcomments.com/en/bible-studies/Gen/1", "kingcomments_genesis_1.txt"),
            ("BibleHub Study", "研經註解", "https://biblehub.com/study/genesis/1.htm", "biblehub_study_genesis_1.txt"),
            ("STEP Bible", "原文資料", "https://www.stepbible.org/?q=version=ESV&reference=Gen.1", "stepbible_genesis_1.txt"),
        ]
        for label, kind, url, fname in labels:
            rel = f"raw_data/{fname}"
            p = root / rel
            if kind == "原文資料":
                _write(p, valid_step_text("Genesis 1:1"))
                rows.append(f"| {label} | {kind} | {url} | {rel} | OK |")
            else:
                raw_lines = [f"{label} 註釋內容逐字測試句長度第{i}行" for i in range(1, 10)]
                _write(p, "\n".join(raw_lines) + "\n")
                rows.append(f"| {label} | {kind} | {url} | {rel} | OK |")
                logs.extend([
                    f"## {rel}", "- 行數：9",
                    f"- 引句：{raw_lines[0]}", f"- 引句：{raw_lines[3]}",
                    f"- 引句：{raw_lines[8]}", "",
                ])
        _write(tmp_dir / "source_manifest.md", "\n".join(rows) + "\n")
        _write(tmp_dir / "read_log.md", "\n".join(logs) + "\n")

    def _write_synced_embedding_index(self, root):
        """空條目庫（link_index={}）對空索引（Schema v2）＝同步。"""
        import numpy as np
        from build_embedding_index import _vectors_sha256, compute_index_fingerprint
        from model_client import select_endpoint
        try:
            cur_embed_model = select_endpoint(task="embedding", root=root).get("model") or "test-embed"
        except Exception:
            cur_embed_model = "test-embed"
        vectors = np.zeros((0, 4), dtype=np.float32)
        np.savez_compressed(root / "util" / "output" / "embedding_index.npz", vectors=vectors)
        meta = {
            "schema_version": 2,
            "model": cur_embed_model,
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

    def _write_fresh_similarity_report(self, tmp_dir, root, overrides=None):
        from semantic_lookup import _file_sha256, RERANK_POLICY_VERSION
        from build_embedding_index import compute_index_fingerprint
        from model_client import select_endpoint
        meta_path = root / "util" / "output" / "embedding_index.meta.json"
        fp = "none"
        if meta_path.is_file():
            fp = compute_index_fingerprint(json.loads(meta_path.read_text(encoding="utf-8")))
        
        calib_sha = _file_sha256(root / "_config" / "reranker_calibration.yaml")
        if not (root / "_config" / "reranker_calibration.yaml").exists():
            _write(root / "_config" / "reranker_calibration.yaml", "models: {}")
            calib_sha = _file_sha256(root / "_config" / "reranker_calibration.yaml")

        try:
            cur_embed_model = select_endpoint(task="embedding", root=root).get("model") or "test-embed"
        except Exception:
            cur_embed_model = "test-embed"

        try:
            cur_rerank_model = select_endpoint(task="rerank", root=root).get("model") or "test-reranker"
        except Exception:
            cur_rerank_model = "test-reranker"

        meta_dict = {
            "schema_version": "1",
            "book": "創世記",
            "chapter": "1",
            "candidate_sha256": _file_sha256(tmp_dir / 'link_candidates.yaml'),
            "embedding_model": cur_embed_model,
            "embedding_index_fingerprint": fp,
            "link_index_sha256": _file_sha256(root / 'util' / 'output' / 'link_index.json'),
            "homonyms_sha256": _file_sha256(root / '_config' / 'link_homonyms.yaml'),
            "rerank_model": cur_rerank_model,
            "rerank_policy_version": RERANK_POLICY_VERSION,
            "calibration_sha256": calib_sha,
            "rerank_status": "success",
            "rerankable_candidates": "1",
            "rerank_attempted": "1",
            "rerank_succeeded": "1",
        }
        if overrides:
            meta_dict.update(overrides)

        lines = ["<!-- candidate_similarity_meta"]
        for k, v in meta_dict.items():
            if v is not None:
                lines.append(f"{k}: {v}")
        lines.extend(["-->", "", "# 候選語義近鄰報告", ""])
        _write(tmp_dir / "candidate_similarity.md", "\n".join(lines))

    def test_all_major_files_present_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(tmp)
            tmp_dir = root / "01 創世記" / ".tmp" / f"第{CHAPTER}章"
            _write(root / "raw_scripture" / BOOK / f"第{CHAPTER}章.txt", "1. 起初神創造天地。")
            self._write_valid_sources(root, tmp_dir)
            _write(tmp_dir / "link_candidates.yaml", "candidates")
            _write(root / "util" / "output" / "link_index.json", "{}")
            _write(root / "_config" / "link_homonyms.yaml", "{}")
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
            failed = [res.label for res in checks if not res.ok]
            self.assertEqual([], failed)

    def test_preflight_passes_with_only_steps_1_and_2(self):
        """--preflight 模式驗證前置包（經文、5來源 manifest、read_log、candidates、fresh similarity report）。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(tmp)
            tmp_dir = root / "01 創世記" / ".tmp" / f"第{CHAPTER}章"
            _write(root / "raw_scripture" / BOOK / f"第{CHAPTER}章.txt", "1. 起初神創造天地。")
            self._write_valid_sources(root, tmp_dir)
            _write(tmp_dir / "link_candidates.yaml", "candidates")
            _write(root / "util" / "output" / "link_index.json", "{}")
            _write(root / "_config" / "link_homonyms.yaml", "{}")
            self._write_synced_embedding_index(root)
            self._write_fresh_similarity_report(tmp_dir, root)

            checks = ccf.build_checks(BOOK, CHAPTER, root=root, preflight=True)
            self.assertEqual(5, len(checks))
            failed = [res.label for res in checks if not res.ok]
            self.assertEqual([], failed)

    def test_candidate_similarity_freshness_table_driven_mutations(self):
        """完整 11 個依賴因子與統計欄位突變時，Freshness 必須判 stale。"""
        mutations = [
            ("1. schema_version", {"schema_version": "99"}),
            ("2. book", {"book": "出埃及記"}),
            ("3. chapter", {"chapter": "99"}),
            ("4. candidate_sha256", {"candidate_sha256": "bad_hash"}),
            ("5. embedding_model", {"embedding_model": "old-unsupported-model"}),
            ("6. embedding_index_fingerprint", {"embedding_index_fingerprint": "bad_fp"}),
            ("7. link_index_sha256", {"link_index_sha256": "bad_hash"}),
            ("8. homonyms_sha256", {"homonyms_sha256": "bad_hash"}),
            ("9. rerank_model", {"rerank_model": "old-reranker-model"}),
            ("10. rerank_policy_version", {"rerank_policy_version": "1999.01.1"}),
            ("11. calibration_sha256", {"calibration_sha256": "bad_hash"}),
            ("rerank_status_missing", {"rerank_status": None}),
            ("rerank_status_invalid", {"rerank_status": "unknown_status"}),
            ("rerankable_candidates_missing", {"rerankable_candidates": None}),
            ("rerank_attempted_missing", {"rerank_attempted": None}),
            ("rerank_succeeded_missing", {"rerank_succeeded": None}),
        ]

        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(tmp)
            tmp_dir = root / "01 創世記" / ".tmp" / f"第{CHAPTER}章"
            _write(root / "raw_scripture" / BOOK / f"第{CHAPTER}章.txt", "1. 起初神創造天地。")
            self._write_valid_sources(root, tmp_dir)
            _write(tmp_dir / "link_candidates.yaml", "candidates")
            _write(root / "util" / "output" / "link_index.json", "{}")
            _write(root / "_config" / "link_homonyms.yaml", "{}")
            self._write_synced_embedding_index(root)

            for field_name, override in mutations:
                with self.subTest(field=field_name):
                    self._write_fresh_similarity_report(tmp_dir, root, overrides=override)
                    fresh, reason, _ = ccf.check_candidate_similarity_freshness(BOOK, CHAPTER, root=root)
                    self.assertFalse(fresh, f"欄位 {field_name} 突變應判定 stale，但回傳 fresh")

    def test_freshness_fails_closed_when_rerank_endpoint_error(self):
        """當 rerank route/endpoint 設定損壞時，Freshness 必須 Fail-Closed 回傳 False。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(tmp)
            tmp_dir = root / "01 創世記" / ".tmp" / f"第{CHAPTER}章"
            _write(root / "raw_scripture" / BOOK / f"第{CHAPTER}章.txt", "1. 起初神創造天地。")
            self._write_valid_sources(root, tmp_dir)
            _write(tmp_dir / "link_candidates.yaml", "candidates")
            _write(root / "util" / "output" / "link_index.json", "{}")
            _write(root / "_config" / "link_homonyms.yaml", "{}")
            # 寫入無效的 model_endpoints.yaml
            _write(root / "_config" / "model_endpoints.yaml", "tasks: {rerank: invalid_nonexistent_endpoint}")
            self._write_synced_embedding_index(root)
            self._write_fresh_similarity_report(tmp_dir, root)

            fresh, reason, _ = ccf.check_candidate_similarity_freshness(BOOK, CHAPTER, root=root)
            self.assertFalse(fresh, "端點設定錯誤時應 Fail-Closed 回傳 False")
            self.assertIn("無法解析", reason)

    def test_preflight_fails_when_manifest_has_duplicate_or_missing_sources(self):
        """來源宣告若不符合恰好五套 {CT, GT, KC, BH, STEP}，Preflight 必須 FAIL。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(tmp)
            tmp_dir = root / "01 創世記" / ".tmp" / f"第{CHAPTER}章"
            _write(root / "raw_scripture" / BOOK / f"第{CHAPTER}章.txt", "1. 起初神創造天地。")
            # 只有 CT 與 GT，缺 KC, BH, STEP
            _write(tmp_dir / "source_manifest.md", (
                "| 來源 | 類型 | URL | raw_data 檔案 | 狀態 |\n"
                "|---|---|---|---|---|\n"
                "| CT | 研經註解 | u | raw_data/1.txt | OK |\n"
                "| GT | 研經註解 | u | raw_data/2.txt | OK |\n"
            ))
            _write(tmp_dir / "link_candidates.yaml", "candidates")
            _write(root / "util" / "output" / "link_index.json", "{}")
            _write(root / "_config" / "link_homonyms.yaml", "{}")
            self._write_synced_embedding_index(root)
            self._write_fresh_similarity_report(tmp_dir, root)

            checks = ccf.build_checks(BOOK, CHAPTER, root=root, preflight=True)
            source_decl_check = next(c for c in checks if "完整五來源宣告" in c.label)
            self.assertFalse(source_decl_check.ok)
            self.assertIn("來源宣告不符合正好五套", source_decl_check.resume_hint)

    def test_preflight_fails_when_rerank_disabled(self):
        """正式 preflight 階段不接受 rerank_status: disabled（--no-rerank 產物）。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(tmp)
            tmp_dir = root / "01 創世記" / ".tmp" / f"第{CHAPTER}章"
            _write(root / "raw_scripture" / BOOK / f"第{CHAPTER}章.txt", "1. 起初神創造天地。")
            self._write_valid_sources(root, tmp_dir)
            _write(tmp_dir / "link_candidates.yaml", "candidates")
            _write(root / "util" / "output" / "link_index.json", "{}")
            _write(root / "_config" / "link_homonyms.yaml", "{}")
            self._write_synced_embedding_index(root)
            self._write_fresh_similarity_report(tmp_dir, root, overrides={"rerank_status": "disabled", "rerank_model": "none"})

            checks = ccf.build_checks(BOOK, CHAPTER, root=root, preflight=True)
            sim_check = next(c for c in checks if "candidate_similarity" in c.label)
            self.assertFalse(sim_check.ok)
            self.assertIn("禁止 rerank_status: disabled", sim_check.resume_hint)

    def test_manual_prompts_fails_when_rerank_disabled(self):
        """run_chapter_manual.py prompts 正式生產流程禁止 rerank_status: disabled。"""
        import run_chapter_manual as rcm
        import run_chapter as rc
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(tmp)
            tmp_dir = root / "01 創世記" / ".tmp" / f"第{CHAPTER}章"
            _write(root / "raw_scripture" / BOOK / f"第{CHAPTER}章.txt", "1. 起初神創造天地。")
            self._write_valid_sources(root, tmp_dir)
            _write(tmp_dir / "link_candidates.yaml", "candidates: []\nbook: 創世記\nchapter: 1\n")
            _write(root / "util" / "output" / "link_index.json", "{}")
            _write(root / "_config" / "link_homonyms.yaml", "{}")
            self._write_synced_embedding_index(root)
            self._write_fresh_similarity_report(tmp_dir, root, overrides={"rerank_status": "disabled", "rerank_model": "none"})

            ctx = rc.ChapterContext(BOOK, CHAPTER, root=root)
            with self.assertRaises(rcm.SourceError) as cm:
                rcm._require_candidate_similarity(ctx)
            self.assertIn("禁止 rerank_status: disabled", str(cm.exception))

    def test_preflight_warns_and_passes_when_rerank_degraded(self):
        """當 rerank_status 為 partial 或 degraded 時，Preflight 放行 PASS 並附帶 warning。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(tmp)
            tmp_dir = root / "01 創世記" / ".tmp" / f"第{CHAPTER}章"
            _write(root / "raw_scripture" / BOOK / f"第{CHAPTER}章.txt", "1. 起初神創造天地。")
            self._write_valid_sources(root, tmp_dir)
            _write(tmp_dir / "link_candidates.yaml", "candidates")
            _write(root / "util" / "output" / "link_index.json", "{}")
            _write(root / "_config" / "link_homonyms.yaml", "{}")
            self._write_synced_embedding_index(root)
            self._write_fresh_similarity_report(tmp_dir, root, overrides={"rerank_status": "degraded"})

            checks = ccf.build_checks(BOOK, CHAPTER, root=root, preflight=True)
            sim_check = next(c for c in checks if "candidate_similarity" in c.label)
            self.assertTrue(sim_check.ok)
            self.assertIn("Reranker 狀態為 degraded", sim_check.warning)

    def test_missing_similarity_report_fails_step2(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(tmp)
            tmp_dir = root / "01 創世記" / ".tmp" / f"第{CHAPTER}章"
            _write(tmp_dir / "link_candidates.yaml", "candidates")

            checks = ccf.build_checks(BOOK, CHAPTER, root=root)
            report_check = next(c for c in checks if "candidate_similarity" in c.label)
            self.assertFalse(report_check.ok)
            self.assertIn("--candidates", report_check.resume_hint)

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
            embed_check = next(c for c in checks if "embedding" in c.label)
            self.assertFalse(embed_check.ok)
            self.assertIn("build_embedding_index", embed_check.resume_hint)

    def test_absent_embedding_index_fails_with_bootstrap_hint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(tmp)
            checks = ccf.build_checks(BOOK, CHAPTER, root=root)
            embed_check = next(c for c in checks if "embedding" in c.label)
            self.assertFalse(embed_check.ok)
            self.assertIn("索引不存在", embed_check.resume_hint)

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
            entry_check = next(c for c in checks if "entry_content" in c.label)
            self.assertTrue(entry_check.ok, "去重後 1 個候選對 1 個檔案應視為完成")

    def test_link_updates_skipped_when_plan_has_no_b_class(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(tmp)
            tmp_dir = root / "01 創世記" / ".tmp" / f"第{CHAPTER}章"
            _write_yaml(tmp_dir / "link_plan.yaml", {"C_new_formal": [], "B_needs_update": []})

            checks = ccf.build_checks(BOOK, CHAPTER, root=root)
            update_check = next(c for c in checks if "link_updates.yaml" in c.label)
            self.assertTrue(update_check.ok, "計畫無 B 類候選時不應要求 link_updates.yaml")


if __name__ == "__main__":
    unittest.main()
