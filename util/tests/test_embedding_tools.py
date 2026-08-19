import json
import sys
import tempfile
import unittest
from pathlib import Path

UTIL_DIR = Path(__file__).resolve().parents[1]
if str(UTIL_DIR) not in sys.path:
    sys.path.insert(0, str(UTIL_DIR))

import yaml

from build_embedding_index import _hash, entry_embed_text, stale_summary
from semantic_lookup import (
    candidate_query_text,
    candidate_rerank_query,
    candidate_report,
    entry_rerank_document,
)


def _write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class EntryEmbedTextTests(unittest.TestCase):
    def test_composes_sections_and_strips_markup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "link_folder" / "主題" / "甲.md", (
                "---\ntype: 主題\n---\n\n# 甲\n\n## 定義\n\n這是[[乙|別稱]]的定義。\n\n"
                "## 按書卷累積\n\n<!-- accumulation:創世記:1:start -->\n"
                "#### [[01 創世記/第1章|第1章]]\n- 本章重點：內容甲。\n"
                "<!-- accumulation:創世記:1:end -->\n\n"
                "## 主題發展\n\n發展敘述。\n\n## 相關條目\n\n- [[乙]]\n\n"
                "## 來源依據\n\n- BH: x（<https://example.com/1>）\n"
            ))
            entry = {"type": "主題", "path": "link_folder/主題/甲.md", "aliases": ["別名甲"]}
            text = entry_embed_text("甲", entry, root=root)
        self.assertIn("甲\n分類：主題\n別名：別名甲", text)
        self.assertIn("定義：這是乙的定義。", text)          # wikilink 只留概念名
        self.assertIn("主題發展：發展敘述。", text)
        self.assertIn("相關條目：乙", text)
        self.assertIn("本章重點：內容甲。", text)            # 累積內文保留
        self.assertNotIn("example.com", text)               # URL 剝除
        self.assertNotIn("accumulation", text)              # HTML 註解剝除
        self.assertNotIn("####", text)                      # 子標題剝除

    def test_missing_file_still_returns_title_block(self):
        entry = {"type": "人物", "path": "link_folder/人物/不存在.md", "aliases": []}
        text = entry_embed_text("某人", entry, root=Path("Z:/nonexistent"))
        self.assertEqual("某人\n分類：人物", text)


class StaleSummaryTests(unittest.TestCase):
    def _root_with(self, tmp, link_index, meta):
        import numpy as np
        from build_embedding_index import _vectors_sha256, compute_index_fingerprint
        root = Path(tmp)
        _write(root / "util" / "output" / "link_index.json",
               json.dumps(link_index, ensure_ascii=False))
        dim = meta.get("dim", 4)
        n = len(meta.get("entries", []))
        vectors = np.zeros((n, dim), dtype=np.float32)
        np.savez_compressed(root / "util" / "output" / "embedding_index.npz", vectors=vectors)
        if "schema_version" not in meta and not meta.get("legacy_test"):
            meta["schema_version"] = 2
        if "vectors_sha256" not in meta and not meta.get("legacy_test"):
            meta["vectors_sha256"] = _vectors_sha256(vectors)
        if "index_fingerprint" not in meta and not meta.get("legacy_test"):
            meta["index_fingerprint"] = compute_index_fingerprint(meta)
        _write(root / "util" / "output" / "embedding_index.meta.json",
               json.dumps(meta, ensure_ascii=False))
        return root

    def test_missing_index_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(stale_summary(Path(tmp)))

    def test_detects_changed_and_removed(self):
        entry = {"title": "甲", "type": "主題", "path": "link_folder/主題/甲.md", "aliases": []}
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root_with(
                tmp,
                {"甲": entry},
                {"model": "m", "entries": [
                    {"title": "乙", "path": "p", "type": "主題", "hash": "x"}
                ]},
            )
            summary = stale_summary(root)
        self.assertEqual(["甲"], summary["changed"])
        self.assertEqual(["乙"], summary["removed"])

    def test_path_change_causes_stale(self):
        """條目 path 改變時，即使文本 hash 相同也應判定為 stale。"""
        entry = {"title": "甲", "type": "主題", "path": "link_folder/主題/甲_新路徑.md", "aliases": []}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            correct = _hash(entry_embed_text("甲", entry, root=root))
            root = self._root_with(
                tmp,
                {"甲": entry},
                {"model": "m", "entries": [
                    {"title": "甲", "path": "link_folder/主題/甲_舊路徑.md", "type": "主題", "hash": correct}
                ]},
            )
            summary = stale_summary(root)
        self.assertEqual(["甲"], summary["changed"])

    def test_secondary_types_change_changes_embed_text_and_hash(self):
        """次分類變更會使 entry_embed_text 與 hash 改變。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entry1 = {"title": "甲", "type": "主題", "secondary_types": [], "path": "p", "aliases": []}
            entry2 = {"title": "甲", "type": "主題", "secondary_types": ["神學"], "path": "p", "aliases": []}
            t1 = entry_embed_text("甲", entry1, root=root)
            t2 = entry_embed_text("甲", entry2, root=root)
            self.assertNotIn("次分類：", t1)
            self.assertIn("次分類：神學", t2)
            self.assertNotEqual(_hash(t1), _hash(t2))

    def test_fresh_index_reports_clean(self):
        entry = {"title": "甲", "type": "主題", "path": "link_folder/主題/甲.md", "aliases": []}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            correct = _hash(entry_embed_text("甲", entry, root=root))
            root = self._root_with(
                tmp,
                {"甲": entry, "甲別名": {"alias_of": "甲"}},  # alias 鍵應被忽略
                {"model": "m", "entries": [
                    {"title": "甲", "path": "link_folder/主題/甲.md", "type": "主題", "hash": correct}
                ]},
            )
            summary = stale_summary(root)
        self.assertEqual([], summary["changed"])
        self.assertEqual([], summary["removed"])
        self.assertEqual(1, summary["total"])


class CandidateQueryTextTests(unittest.TestCase):
    def test_composes_all_signal_fields(self):
        text = candidate_query_text({
            "name": "不可搶奪鄰舍",
            "suggested_type": "神學",
            "evidence": "v13 不可欺壓你的鄰舍，也不可搶奪他的物",
            "surfaces": [{"phrase": "搶奪"}, {"phrase": "欺壓", "verses": [13]}],
        })
        self.assertEqual(
            "不可搶奪鄰舍\n分類：神學\nv13 不可欺壓你的鄰舍，也不可搶奪他的物\n"
            "經文用詞：搶奪、欺壓",
            text,
        )

    def test_bare_name_only(self):
        self.assertEqual(
            "甲\n分類：主題",
            candidate_query_text({"name": "甲", "suggested_type": "主題", "surfaces": []}),
        )


class CandidateRerankQueryTests(unittest.TestCase):
    def test_composes_rerank_fields(self):
        text = candidate_rerank_query({
            "name": "米甸",
            "suggested_type": "人物",
            "evidence": "創25:2 亞伯拉罕與基土拉所生的兒子",
            "surfaces": [{"phrase": "米甸"}],
        }, book="創世記", chapter=25)
        self.assertIn("待建立詞：米甸", text)
        self.assertIn("出現位置：創世記 第25章", text)
        self.assertIn("候選類型：人物", text)
        self.assertIn("本章上下文：創25:2 亞伯拉罕與基土拉所生的兒子", text)
        self.assertIn("經文用詞：米甸", text)


class _FakeIndex:
    def __init__(self, hits_per_query, matrix=None):
        self.meta = {"model": "test-embed"}
        self.entries = [{"title": "x"}]
        self.hits_per_query = hits_per_query
        self.matrix = matrix
        self.received = None
        self.received_top = None

    def query_vectors(self, queries, top=3, return_matrix=False):
        self.received = list(queries)
        self.received_top = top
        if return_matrix:
            import numpy as np
            matrix = self.matrix if self.matrix is not None else np.eye(
                len(queries), dtype=np.float32)
            return self.hits_per_query, matrix
        return self.hits_per_query


class CandidateReportTests(unittest.TestCase):
    def test_report_without_rerank_fallback_and_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "01 創世記" / ".tmp" / "第1章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 1,
                    "candidates": [
                        {"name": "近似候選", "type": "主題", "evidence": "依據甲"},
                        {"name": "獨特候選", "type": "神學"},
                    ],
                }, allow_unicode=True),
            )
            fake = _FakeIndex([
                [("既有近似條目", 0.75, {"type": "主題", "path": "link_folder/主題/既有近似條目.md"}),
                 ("低分條目", 0.20, {"type": "主題", "path": "link_folder/主題/低分條目.md"})],
                [("不相關", 0.15, {"type": "神學", "path": "link_folder/神學/不相關.md"})],
            ])
            path, total, flagged = candidate_report(
                "創世記", 1, root=root, index=fake, link_index={}, homonyms={}, threshold=0.60,
                use_rerank=False,
            )
            content = path.read_text(encoding="utf-8")
        self.assertEqual(2, total)
        self.assertEqual(1, flagged)
        self.assertIn("| 1 | 既有近似條目 | 0.750 | link_folder/主題/既有近似條目.md |", content)
        self.assertIn("判定：⚠ 語義相似度高", content)
        self.assertIn("依據甲", fake.received[0])
        self.assertEqual("candidate_similarity.md", path.name)

    def test_report_with_mock_reranker_calibrated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "_config" / "reranker_calibration.yaml",
                yaml.safe_dump({
                    "models": {
                        "test-reranker": {
                            "calibrated": True,
                            "thresholds": {
                                "score_high": 0.70,
                                "score_low": 0.40,
                                "margin_high": 0.20,
                                "margin_ambiguous": 0.15,
                            },
                        },
                    },
                }),
            )
            _write(
                root / "01 創世記" / ".tmp" / "第25章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 25,
                    "candidates": [
                        {"name": "亞伯拉罕之子米甸", "type": "人物", "evidence": "基土拉生了心蘭、約珊、米但、米甸"},
                    ],
                }, allow_unicode=True),
            )
            fake = _FakeIndex([
                [
                    ("米甸", 0.87, {"type": "人物", "path": "link_folder/人物/米甸.md"}),
                    ("米甸人", 0.91, {"type": "群體", "path": "link_folder/群體/米甸人.md"}),
                ],
            ])

            def fake_reranker(query, docs):
                return [
                    {"index": 0, "relevance_score": 0.962},
                    {"index": 1, "relevance_score": 0.314},
                ]

            fake_reranker.model_name = "test-reranker"

            path, total, flagged = candidate_report(
                "創世記", 25, root=root, index=fake, link_index={}, homonyms={},
                reranker=fake_reranker, use_rerank=True,
            )
            content = path.read_text(encoding="utf-8")

        self.assertEqual(1, total)
        self.assertEqual(0, flagged)  # 校準模型 + 高分且高 Margin
        self.assertIn("| Rank | Candidate | Similarity | Rerank | Path |", content)
        self.assertIn("| 1 | 米甸 | 0.870 | 0.962 | link_folder/人物/米甸.md |", content)
        self.assertIn("rerank_margin: 0.648", content)
        self.assertIn("判定：✅ 建議使用既有條目 [[米甸]]", content)

    def test_middle_band_similarity_is_flagged_not_declared_new(self):
        """0.50–0.70 這一段不得判「建新條目」——實測那裡真對應與無對應完全重疊。

        2026-08-20 的 96 組 gold pair 量到：正確目標奪冠時相似度中位數 0.700、
        最低 0.523；遮罩負例（該概念其實還沒有條目）中位數 0.621、最高 0.763。
        舊門檻 0.60 會把 10/57 的真對應判成 🆕 建新條目——那正是製造重複條目的路徑。
        本例 sim=0.55 落在舊門檻之下、新門檻之上，必須是 ⚠ 且不給方向。
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "_config" / "reranker_calibration.yaml",
                yaml.safe_dump({"models": {"test-reranker": {"calibrated": False}}}),
            )
            _write(
                root / "01 創世記" / ".tmp" / "第1章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 1,
                    "candidates": [{"name": "田角遺落的莊稼", "type": "主題"}],
                }, allow_unicode=True),
            )
            fake = _FakeIndex([[("田角拾穗顧念窮人的條例", 0.55,
                                 {"title": "田角拾穗顧念窮人的條例", "type": "主題", "path": "p"})]])

            def fake_reranker(query, docs):
                return [{"index": 0, "relevance_score": 0.95}]
            fake_reranker.model_name = "test-reranker"

            path, total, flagged = candidate_report(
                "創世記", 1, root=root, index=fake, link_index={}, homonyms={},
                reranker=fake_reranker, use_rerank=True,
            )
            content = path.read_text(encoding="utf-8")

        self.assertEqual(1, flagged)
        self.assertNotIn("🆕", content)
        self.assertIn("⚠ 相似度居中", content)
        self.assertIn("需逐一人工判斷", content)

    def test_uncalibrated_reranker_flags_warning(self):
        """未校準模型（calibrated: false 或未登錄）即使分數極高也只能給 ⚠ 供排序參考。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "01 創世記" / ".tmp" / "第25章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 25,
                    "candidates": [
                        {"name": "亞伯拉罕之子米甸", "type": "人物", "evidence": "基土拉生了心蘭、約珊、米但、米甸"},
                    ],
                }, allow_unicode=True),
            )
            fake = _FakeIndex([
                [
                    ("米甸", 0.87, {"type": "人物", "path": "link_folder/人物/米甸.md"}),
                ],
            ])

            def fake_reranker(query, docs):
                return [{"index": 0, "relevance_score": 0.98}]

            fake_reranker.model_name = "uncalibrated-reranker"

            path, total, flagged = candidate_report(
                "創世記", 25, root=root, index=fake, link_index={}, homonyms={},
                reranker=fake_reranker, use_rerank=True,
            )
            content = path.read_text(encoding="utf-8")

        self.assertEqual(1, flagged)
        # 未校準模型不得自動 ✅；判定回落到經實測校準的檢索規則，並標明重排未校準。
        self.assertIn("判定：⚠ 語義相似度高（0.870 ≥ 0.70）", content)
        self.assertIn("未校準", content)
        self.assertNotIn("判定：✅", content)

    def test_homonym_attention_strictly_overrides_reranker(self):
        """同名歧義候選（link_homonyms 中的 D 類詞）即使 Reranker 得分 0.99，也絕對只能判定為 ⚠。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "_config" / "link_homonyms.yaml",
                yaml.safe_dump({
                    "示劍": [
                        {"target": "示劍 (人物)", "note": "哈抹的兒子"},
                        {"target": "示劍 (地點)", "note": "迦南中部城邑"},
                    ],
                }, allow_unicode=True),
            )
            _write(
                root / "01 創世記" / ".tmp" / "第34章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 34,
                    "candidates": [
                        {"name": "示劍", "type": "人物", "evidence": "哈抹的兒子示劍看見她"},
                    ],
                }, allow_unicode=True),
            )
            homonyms = {
                "示劍": [
                    {"target": "示劍 (人物)", "note": "哈抹的兒子"},
                    {"target": "示劍 (地點)", "note": "迦南中部城邑"},
                ]
            }
            fake = _FakeIndex([
                [
                    ("示劍 (人物)", 0.95, {"type": "人物", "path": "link_folder/人物/示劍 (人物).md"}),
                ],
            ])

            def fake_reranker(query, docs):
                return [{"index": 0, "relevance_score": 0.999}]

            fake_reranker.model_name = "test-reranker"

            path, total, flagged = candidate_report(
                "創世記", 34, root=root, index=fake, link_index={}, homonyms=homonyms,
                reranker=fake_reranker, use_rerank=True,
            )
            content = path.read_text(encoding="utf-8")

        self.assertEqual(1, flagged)
        self.assertIn("字面解析：⚠ 同名詞需人工選擇（將歸 D）：示劍 (人物)、示劍 (地點)", content)
        self.assertIn("判定：⚠ 字面解析有歧義／需人工確認", content)
        self.assertNotIn("判定：✅", content)

    def test_rerank_ambiguous_margin_flagged(self):
        """Top1 與 Top2 分數相近（margin < 0.15）時標 ⚠ 需人工判斷。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "_config" / "reranker_calibration.yaml",
                yaml.safe_dump({
                    "models": {
                        "test-reranker": {
                            "calibrated": True,
                            "thresholds": {"score_high": 0.70, "score_low": 0.40, "margin_high": 0.20, "margin_ambiguous": 0.15},
                        }
                    }
                })
            )
            _write(
                root / "01 創世記" / ".tmp" / "第1章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 1,
                    "candidates": [{"name": "模糊候選", "type": "主題"}],
                }, allow_unicode=True),
            )
            fake = _FakeIndex([[
                ("概念甲", 0.70, {"type": "主題", "path": "p1"}),
                ("概念乙", 0.68, {"type": "主題", "path": "p2"}),
            ]])

            def fake_reranker(query, docs):
                return [
                    {"index": 0, "relevance_score": 0.65},
                    {"index": 1, "relevance_score": 0.62},  # margin = 0.03
                ]
            fake_reranker.model_name = "test-reranker"

            path, total, flagged = candidate_report(
                "創世記", 1, root=root, index=fake, link_index={}, homonyms={},
                reranker=fake_reranker, use_rerank=True,
            )
            content = path.read_text(encoding="utf-8")

        self.assertEqual(1, flagged)
        self.assertIn("rerank_margin: 0.030", content)
        self.assertIn("判定：⚠ 候選相近（Top1 與 Top2 分數差距 0.030 < 0.15）", content)

    def test_rerank_type_incompatible_flagged(self):
        """Rerank 分數高但分類不相容時標 ⚠。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "_config" / "reranker_calibration.yaml",
                yaml.safe_dump({"models": {"custom-reranker": {"calibrated": True, "score_high": 0.70}}})
            )
            _write(
                root / "01 創世記" / ".tmp" / "第1章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 1,
                    "candidates": [{"name": "戰勝巴珊王", "type": "事件"}],
                }, allow_unicode=True),
            )
            fake = _FakeIndex([[
                ("巴珊王噩", 0.75, {"type": "人物", "secondary_types": [], "path": "p"}),
            ]])

            def fake_reranker(query, docs):
                return [{"index": 0, "relevance_score": 0.85}]

            path, total, flagged = candidate_report(
                "創世記", 1, root=root, index=fake, link_index={}, homonyms={},
                reranker=fake_reranker, use_rerank=True,
            )
            content = path.read_text(encoding="utf-8")

        self.assertEqual(1, flagged)
        self.assertIn("判定：⚠ 近鄰分類不相容", content)

    def test_rerank_low_score_type_incompatible_flagged(self):
        """Rerank 分數極低（0.10）但分類不相容時，必須標 ⚠ 近鄰分類不相容，絕不可誤判 🆕。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "_config" / "reranker_calibration.yaml",
                yaml.safe_dump({"models": {"custom-reranker": {"calibrated": True, "score_high": 0.70, "score_low": 0.40}}})
            )
            _write(
                root / "01 創世記" / ".tmp" / "第1章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 1,
                    "candidates": [{"name": "擊打磐石事件", "type": "事件"}],
                }, allow_unicode=True),
            )
            fake = _FakeIndex([[
                ("摩西", 0.75, {"type": "人物", "secondary_types": [], "path": "p"}),
            ]])

            def fake_reranker(query, docs):
                return [{"index": 0, "relevance_score": 0.10}]
            fake_reranker.model_name = "custom-reranker"

            path, total, flagged = candidate_report(
                "創世記", 1, root=root, index=fake, link_index={}, homonyms={},
                reranker=fake_reranker, use_rerank=True,
            )
            content = path.read_text(encoding="utf-8")

        self.assertEqual(1, flagged)
        self.assertIn("判定：⚠ 近鄰分類不相容", content)
        self.assertNotIn("判定：🆕", content)

    def test_embedding_low_score_type_incompatible_flagged(self):
        """純 Embedding 降級下，相似度極低（0.20 < threshold）但分類不相容時，必須標 ⚠ 近鄰分類不相容，絕不可誤判 🆕。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "01 創世記" / ".tmp" / "第1章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 1,
                    "candidates": [{"name": "某事件", "type": "事件"}],
                }, allow_unicode=True),
            )
            fake = _FakeIndex([[
                ("某人物", 0.20, {"type": "人物", "secondary_types": [], "path": "p"}),
            ]])

            path, total, flagged = candidate_report(
                "創世記", 1, root=root, index=fake, link_index={}, homonyms={},
                threshold=0.60, use_rerank=False,
            )
            content = path.read_text(encoding="utf-8")

        self.assertEqual(1, flagged)
        self.assertIn("判定：⚠ 近鄰分類不相容", content)
        self.assertNotIn("判定：🆕", content)

    def test_rerank_low_score_suggests_new_entry(self):
        """Rerank 所有候選分數皆低（<0.40）且分類相容時判定為建議新條目。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "_config" / "reranker_calibration.yaml",
                yaml.safe_dump({
                    "models": {
                        "test-reranker": {
                            "calibrated": True,
                            "thresholds": {"score_high": 0.70, "score_low": 0.40, "margin_high": 0.20, "margin_ambiguous": 0.15},
                        }
                    }
                })
            )
            _write(
                root / "01 創世記" / ".tmp" / "第1章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 1,
                    "candidates": [{"name": "全新概念", "type": "神學"}],
                }, allow_unicode=True),
            )
            fake = _FakeIndex([[
                ("不相干條目", 0.30, {"type": "神學", "path": "p"}),
            ]])

            def fake_reranker(query, docs):
                return [{"index": 0, "relevance_score": 0.15}]
            fake_reranker.model_name = "test-reranker"

            path, total, flagged = candidate_report(
                "創世記", 1, root=root, index=fake, link_index={}, homonyms={},
                reranker=fake_reranker, use_rerank=True,
            )
            content = path.read_text(encoding="utf-8")

        self.assertEqual(0, flagged)
        self.assertIn("判定：🆕 建議建立新條目", content)

    def test_lexical_attention_skips_reranker_execution(self):
        """字面層已有歧義（attention）的候選，不應調用 Rerank API。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "01 創世記" / ".tmp" / "第1章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 1,
                    "candidates": [{"name": "希伯", "type": "人物"}],
                }, allow_unicode=True),
            )
            homonyms = {
                "希伯": [
                    {"target": "希伯（沙拉之子）", "type": "人物", "disambiguation": "沙拉之子"},
                    {"target": "希伯（迦得支派）", "type": "人物", "disambiguation": "迦得支派"},
                ]
            }
            fake = _FakeIndex([[
                ("希伯（沙拉之子）", 0.90, {"type": "人物", "path": "p1"}),
            ]])

            rerank_called = []
            def fake_reranker(query, docs):
                rerank_called.append(query)
                return [{"index": 0, "relevance_score": 0.99}]

            path, total, flagged = candidate_report(
                "創世記", 1, root=root, index=fake, link_index={}, homonyms=homonyms,
                reranker=fake_reranker, use_rerank=True,
            )
            content = path.read_text(encoding="utf-8")

        self.assertEqual(0, len(rerank_called))
        self.assertEqual(1, flagged)
        self.assertIn("判定：⚠ 字面解析有歧義", content)
        self.assertIn("rerankable_candidates: 0", content)

    def test_lexical_type_mismatch_skips_reranker_execution(self):
        """字面層同名但分類不相容（lexical type mismatch）的候選，不應調用 Rerank API。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "01 創世記" / ".tmp" / "第1章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 1,
                    "candidates": [{"name": "摩西", "type": "地點"}],  # 候選填地點
                }, allow_unicode=True),
            )
            link_index = {
                "摩西": {"title": "摩西", "type": "人物", "path": "link_folder/人物/摩西.md"},
            }
            fake = _FakeIndex([[
                ("摩西", 0.95, {"type": "人物", "path": "link_folder/人物/摩西.md"}),
            ]])

            rerank_called = []
            def fake_reranker(query, docs):
                rerank_called.append(query)
                return [{"index": 0, "relevance_score": 0.99}]

            path, total, flagged = candidate_report(
                "創世記", 1, root=root, index=fake, link_index=link_index, homonyms={},
                reranker=fake_reranker, use_rerank=True,
            )
            content = path.read_text(encoding="utf-8")

        self.assertEqual(0, len(rerank_called))
        self.assertEqual(1, flagged)
        self.assertIn("判定：⚠ 字面分類不相容", content)
        self.assertIn("rerankable_candidates: 0", content)

    def test_exact_match_skips_reranker(self):
        """字面完全命中條目跳過 Rerank API 呼叫。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "01 創世記" / ".tmp" / "第1章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 1,
                    "candidates": [{"name": "亞伯拉罕", "type": "人物"}],
                }, allow_unicode=True),
            )
            link_index = {
                "亞伯拉罕": {"title": "亞伯拉罕", "type": "人物", "path": "link_folder/人物/亞伯拉罕.md"},
            }
            fake = _FakeIndex([[
                ("亞伯拉罕", 0.95, {"type": "人物", "path": "link_folder/人物/亞伯拉罕.md"}),
            ]])

            rerank_called = []

            def fake_reranker(query, docs):
                rerank_called.append(query)
                return [{"index": 0, "relevance_score": 0.99}]

            path, total, flagged = candidate_report(
                "創世記", 1, root=root, index=fake, link_index=link_index, homonyms={},
                reranker=fake_reranker, use_rerank=True,
            )
            content = path.read_text(encoding="utf-8")

        self.assertEqual(0, len(rerank_called))  # 未調用 reranker
        self.assertEqual(0, flagged)
        self.assertIn("對上既有「亞伯拉罕」（exact，將歸 A/B 累積）", content)
        self.assertIn("判定：✅ 建議使用既有條目 [[亞伯拉罕]]（同名／字面對應）", content)

    def test_lexical_preview_flags_alias_redirect(self):
        """alias 導向不同名條目（安密巴誤含以實各谷型）要標「請確認」。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "01 創世記" / ".tmp" / "第1章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 1,
                    "candidates": [
                        {"name": "以實各谷", "type": "地點"},
                        {"name": "獨立新候選", "type": "主題"},
                    ],
                }, allow_unicode=True),
            )
            link_index = {
                "安密巴": {"title": "安密巴", "type": "地點",
                           "path": "link_folder/地點/安密巴.md",
                           "aliases": ["以實各谷"]},
                "以實各谷": {"alias_of": "安密巴"},
            }
            low = {"type": "地點", "secondary_types": []}
            fake = _FakeIndex([[("someplace", 0.2, low)], [("x", 0.2, low)]])
            path, _, _ = candidate_report(
                "創世記", 1, root=root, index=fake,
                link_index=link_index, homonyms={}, threshold=0.60,
                use_rerank=False,
            )
            content = path.read_text(encoding="utf-8")
        self.assertIn("經 alias 導向「安密巴」", content)
        self.assertIn("請確認", content)
        self.assertIn("無字面對應 → 新建（C）", content)

    def test_intra_pair_flagged_and_dup_name_noted(self):
        """候選互查：≥門檻的配對要標 ⚠，同名重複候選另註。"""
        import numpy as np
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "01 創世記" / ".tmp" / "第1章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 1,
                    "candidates": [
                        {"name": "叛教之城甲", "type": "主題"},
                        {"name": "叛教之城乙", "type": "主題"},
                        {"name": "無關候選", "type": "人物"},
                    ],
                }, allow_unicode=True),
            )
            matrix = np.array([
                [1.0, 0.0, 0.0],
                [0.9, np.sqrt(1 - 0.81), 0.0],
                [0.0, 0.0, 1.0],
            ], dtype=np.float32)
            low_theme = {"type": "主題", "secondary_types": []}
            low_person = {"type": "人物", "secondary_types": []}
            fake = _FakeIndex(
                [[("條目甲", 0.2, low_theme)], [("條目乙", 0.2, low_theme)], [("條目丙", 0.2, low_person)]],
                matrix=matrix,
            )
            path, total, flagged = candidate_report(
                "創世記", 1, root=root, index=fake, link_index={}, homonyms={}, threshold=0.60,
                use_rerank=False,
            )
            content = path.read_text(encoding="utf-8")
        self.assertEqual(1, flagged)  # 索引近鄰全低分且分類相容，只有互查一對

    def test_metadata_header_and_extraction(self):
        """測試 candidate_similarity.md 開頭的 metadata 註解能被 extract_report_metadata 完整解析。"""
        from semantic_lookup import extract_report_metadata, RERANK_POLICY_VERSION
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "01 創世記" / ".tmp" / "第1章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 1,
                    "candidates": [{"name": "亞伯拉罕之約", "type": "神學"}],
                }, allow_unicode=True),
            )
            fake = _FakeIndex([[("亞伯拉罕", 0.70, {"type": "人物", "path": "p"})]])

            def fake_reranker(query, docs):
                return [{"index": 0, "relevance_score": 0.88}]
            fake_reranker.model_name = "test-reranker"

            path, total, flagged = candidate_report(
                "創世記", 1, root=root, index=fake, link_index={}, homonyms={},
                reranker=fake_reranker, use_rerank=True,
            )
            meta = extract_report_metadata(path)

        self.assertIsNotNone(meta)
        self.assertEqual("創世記", meta.get("book"))
        self.assertEqual("1", meta.get("chapter"))
        self.assertEqual(RERANK_POLICY_VERSION, meta.get("rerank_policy_version"))
        self.assertEqual("test-reranker", meta.get("rerank_model"))
        self.assertEqual("success", meta.get("rerank_status"))
        self.assertEqual("1", meta.get("rerankable_candidates"))
        self.assertEqual("1", meta.get("rerank_succeeded"))

    def test_circuit_breaker_endpoint_system_failure(self):
        """端點系統故障（如 ConnectionRefusedError / URLError）會觸發熔斷，停止後續呼叫，狀態標為 degraded/partial。"""
        import urllib.error
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "01 創世記" / ".tmp" / "第1章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 1,
                    "candidates": [
                        {"name": "候選1", "type": "主題"},
                        {"name": "候選2", "type": "主題"},
                    ],
                }, allow_unicode=True),
            )
            fake = _FakeIndex([
                [("條目1", 0.5, {"type": "主題", "path": "p1"})],
                [("條目2", 0.5, {"type": "主題", "path": "p2"})],
            ])

            call_count = [0]

            def failing_reranker(query, docs):
                call_count[0] += 1
                raise urllib.error.URLError("Connection refused")

            failing_reranker.model_name = "failing-reranker"

            from semantic_lookup import extract_report_metadata
            path, total, flagged = candidate_report(
                "創世記", 1, root=root, index=fake, link_index={}, homonyms={},
                reranker=failing_reranker, use_rerank=True,
            )
            meta = extract_report_metadata(path)

        self.assertEqual(1, call_count[0])  # 第1次掛掉熔斷後，第2次不呼叫
        self.assertEqual("degraded", meta.get("rerank_status"))
        self.assertEqual("1", meta.get("rerank_attempted"))
        self.assertEqual("0", meta.get("rerank_succeeded"))

    def test_single_item_failure_does_not_trip_circuit_breaker(self):
        """單一候選解析錯誤不應熔斷整章，後續候選仍應繼續 rerank，狀態為 partial。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "01 創世記" / ".tmp" / "第1章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 1,
                    "candidates": [
                        {"name": "異常候選", "type": "主題"},
                        {"name": "正常候選", "type": "主題"},
                    ],
                }, allow_unicode=True),
            )
            fake = _FakeIndex([
                [("條目1", 0.5, {"type": "主題", "path": "p1"})],
                [("條目2", 0.5, {"type": "主題", "path": "p2"})],
            ])

            call_count = [0]

            def item_failing_reranker(query, docs):
                call_count[0] += 1
                if "異常" in query:
                    raise ValueError("JSON parse error for single candidate")
                return [{"index": 0, "relevance_score": 0.85}]

            item_failing_reranker.model_name = "item-failing-reranker"

            from semantic_lookup import extract_report_metadata
            path, total, flagged = candidate_report(
                "創世記", 1, root=root, index=fake, link_index={}, homonyms={},
                reranker=item_failing_reranker, use_rerank=True,
            )
            meta = extract_report_metadata(path)

        self.assertEqual(2, call_count[0])  # 兩次都有嘗試
        self.assertEqual("partial", meta.get("rerank_status"))
        self.assertEqual("2", meta.get("rerank_attempted"))
        self.assertEqual("1", meta.get("rerank_succeeded"))

    def test_not_needed_status_when_all_exact_matches(self):
        """若全章候選皆為確切命中（無 rerankable candidates），狀態為 not_needed，且 require_rerank 不報錯。"""
        from semantic_lookup import extract_report_metadata
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "01 創世記" / ".tmp" / "第1章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 1,
                    "candidates": [{"name": "摩西", "type": "人物"}],
                }, allow_unicode=True),
            )
            link_index = {"摩西": {"title": "摩西", "type": "人物", "path": "p"}}
            fake = _FakeIndex([[("摩西", 0.99, {"type": "人物", "path": "p"})]])

            path, total, flagged = candidate_report(
                "創世記", 1, root=root, index=fake, link_index=link_index, homonyms={},
                use_rerank=True, require_rerank=True,
            )
            meta = extract_report_metadata(path)

        self.assertEqual("not_needed", meta.get("rerank_status"))
        self.assertEqual("0", meta.get("rerankable_candidates"))

    def test_require_rerank_raises_on_failure(self):
        """當 require_rerank=True 且 rerank_status 處於 partial/degraded/disabled 時拋出 ModelError。"""
        from model_client import ModelError
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "01 創世記" / ".tmp" / "第1章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 1,
                    "candidates": [{"name": "模糊候選", "type": "主題"}],
                }, allow_unicode=True),
            )
            fake = _FakeIndex([[("條目", 0.5, {"type": "主題", "path": "p"})]])

            def failing_reranker(query, docs):
                raise TimeoutError("Endpoint timeout")
            failing_reranker.model_name = "failing-reranker"

            with self.assertRaises(ModelError):
                candidate_report(
                    "創世記", 1, root=root, index=fake, link_index={}, homonyms={},
                    reranker=failing_reranker, use_rerank=True, require_rerank=True,
                )

    def test_lexical_exact_separated_from_semantic_top1(self):
        """字面完全命中（摩西/人物）與語義 Top1（摩西之歌/主題）分離，判決使用字面命中，不報分類衝突。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "01 創世記" / ".tmp" / "第1章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 1,
                    "candidates": [{"name": "摩西", "type": "人物"}],
                }, allow_unicode=True),
            )
            link_index = {"摩西": {"title": "摩西", "type": "人物", "path": "link_folder/人物/摩西.md"}}
            fake = _FakeIndex([[("摩西之歌", 0.95, {"title": "摩西之歌", "type": "主題", "path": "link_folder/主題/摩西之歌.md"})]])

            path, total, flagged = candidate_report(
                "創世記", 1, root=root, index=fake, link_index=link_index, homonyms={},
                use_rerank=False,
            )
            content = path.read_text(encoding="utf-8")

        self.assertEqual(0, flagged)
        self.assertIn("判定：✅ 建議使用既有條目 [[摩西]]（同名／字面對應）", content)
        self.assertNotIn("摩西之歌", content.split("判定：")[-1])

    def test_lexical_type_mismatch_flags_warning(self):
        """字面同名條目若與候選分類不相容，必須判定 ⚠ 字面分類不相容（不得 ✅）。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "01 創世記" / ".tmp" / "第1章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 1,
                    "candidates": [{"name": "摩西", "type": "主題"}],
                }, allow_unicode=True),
            )
            link_index = {"摩西": {"title": "摩西", "type": "人物", "path": "link_folder/人物/摩西.md"}}
            fake = _FakeIndex([[("摩西", 0.99, {"title": "摩西", "type": "人物", "path": "link_folder/人物/摩西.md"})]])

            path, total, flagged = candidate_report(
                "創世記", 1, root=root, index=fake, link_index=link_index, homonyms={},
                use_rerank=False,
            )
            content = path.read_text(encoding="utf-8")

        self.assertEqual(1, flagged)
        self.assertIn("判定：⚠ 字面分類不相容", content)

    def test_uncalibrated_low_score_defers_to_retrieval_rule(self):
        """未校準模型的低重排分數不得當判準：判定改由經校準的檢索相似度規則決定。

        檢索也說沒有近鄰（0.30 < 0.60）時 🆕 才是正確答案——這正是加 Reranker
        之前跑了 5 卷的行為。真正要防的是「低重排分數把高相似度警告壓掉」，
        由下面的 sim=0.75 案例把關。
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "_config" / "reranker_calibration.yaml",
                yaml.safe_dump({"models": {"test-reranker": {"calibrated": False}}})
            )
            _write(
                root / "01 創世記" / ".tmp" / "第1章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 1,
                    "candidates": [{"name": "罕見詞", "type": "神學"}],
                }, allow_unicode=True),
            )
            fake = _FakeIndex([[("概念", 0.30, {"title": "概念", "type": "神學", "path": "p"})]])

            def fake_reranker(query, docs):
                return [{"index": 0, "relevance_score": 0.10}]
            fake_reranker.model_name = "test-reranker"

            path, total, flagged = candidate_report(
                "創世記", 1, root=root, index=fake, link_index={}, homonyms={},
                reranker=fake_reranker, use_rerank=True,
            )
            content = path.read_text(encoding="utf-8")

        self.assertEqual(0, flagged)
        self.assertIn("🆕 建議建立新條目", content)

        # 同一個低重排分數，但檢索說有 0.75 的近鄰：未校準的重排不得把警告壓掉。
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "_config" / "reranker_calibration.yaml",
                yaml.safe_dump({"models": {"test-reranker": {"calibrated": False}}})
            )
            _write(
                root / "01 創世記" / ".tmp" / "第1章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 1,
                    "candidates": [{"name": "罕見詞", "type": "神學"}],
                }, allow_unicode=True),
            )
            fake = _FakeIndex([[("概念", 0.75, {"title": "概念", "type": "神學", "path": "p"})]])

            def low_reranker(query, docs):
                return [{"index": 0, "relevance_score": 0.10}]
            low_reranker.model_name = "test-reranker"

            path, total, flagged = candidate_report(
                "創世記", 1, root=root, index=fake, link_index={}, homonyms={},
                reranker=low_reranker, use_rerank=True,
            )
            content = path.read_text(encoding="utf-8")

        self.assertEqual(1, flagged)
        self.assertIn("判定：⚠ 語義相似度高（0.750 ≥ 0.70）", content)
        self.assertNotIn("🆕", content)

    def test_calibrated_low_rerank_but_high_similarity_needs_human(self):
        """已校準模型說「都不相關」但檢索說有 ≥ 門檻近鄰時，不得逕自輸出 🆕。

        這條分支是製造重複條目的路徑：重排一旦在某語料上分數整體偏低
        （本專案實測 nvidia rerank 對中文條目只給 0.03–0.06），
        「top1 < score_low → 建新條目」就會對每個候選都成立。
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "_config" / "reranker_calibration.yaml",
                yaml.safe_dump({"models": {"calibrated-reranker": {
                    "calibrated": True,
                    "thresholds": {"score_high": 0.70, "score_low": 0.40,
                                   "margin_high": 0.20, "margin_ambiguous": 0.15},
                }}})
            )
            _write(
                root / "01 創世記" / ".tmp" / "第1章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 1,
                    "candidates": [{"name": "光的創造", "type": "神學"}],
                }, allow_unicode=True),
            )
            fake = _FakeIndex([[("光", 0.82, {"title": "光", "type": "神學", "path": "p"})]])

            def low_reranker(query, docs):
                return [{"index": 0, "relevance_score": 0.05}]
            low_reranker.model_name = "calibrated-reranker"

            path, total, flagged = candidate_report(
                "創世記", 1, root=root, index=fake, link_index={}, homonyms={},
                reranker=low_reranker, use_rerank=True,
            )
            content = path.read_text(encoding="utf-8")

        self.assertEqual(1, flagged)
        self.assertIn("判定：⚠ 兩階段判定不一致", content)
        self.assertNotIn("🆕", content)

    def test_rerank_sees_deeper_retrieval_than_displayed_top(self):
        """第一階段要檢索到 RERANK_RETRIEVE_TOP_K，重排後才截到 top 名顯示。

        否則 Cross-Encoder 只是把 bi-encoder 已經選出的同一批重排一次，
        召回上限完全由 bi-encoder 決定，兩階段架構沒有意義。
        """
        from semantic_lookup import RERANK_RETRIEVE_TOP_K
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "01 創世記" / ".tmp" / "第1章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 1,
                    "candidates": [{"name": "新詞", "type": "神學"}],
                }, allow_unicode=True),
            )
            # 檢索名次：正確答案「深處的條目」排在第 8 名，超出顯示的前 5 名
            hits = [
                (f"雜訊{i}", 0.70 - i * 0.01, {"title": f"雜訊{i}", "type": "神學", "path": f"p{i}"})
                for i in range(7)
            ]
            hits.append(("深處的條目", 0.61,
                         {"title": "深處的條目", "type": "神學", "path": "deep"}))
            fake = _FakeIndex([hits])

            def deep_reranker(query, docs):
                # 重排把第 8 筆拉到第一
                return [{"index": 7, "relevance_score": 0.9}] + [
                    {"index": i, "relevance_score": 0.1} for i in range(7)
                ]
            deep_reranker.model_name = "uncalibrated-reranker"

            path, total, flagged = candidate_report(
                "創世記", 1, root=root, index=fake, link_index={}, homonyms={},
                reranker=deep_reranker, use_rerank=True, top=5,
            )
            content = path.read_text(encoding="utf-8")

        self.assertEqual(RERANK_RETRIEVE_TOP_K, fake.received_top)
        self.assertIn("| 1 | 深處的條目 |", content)
        # 重排後只顯示 top 名
        self.assertNotIn("| 6 |", content)

    def test_type_mismatch_rerank_intermediate_score_flags_warning(self):
        """分類不相容候選在已校準模型給出中等重排分數（如 0.50）時必須標 ⚠ 近鄰分類不相容，不得輸出 🆕。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "_config" / "reranker_calibration.yaml",
                yaml.safe_dump({"models": {"test-reranker": {"calibrated": True, "score_low": 0.40, "score_high": 0.70}}})
            )
            _write(
                root / "01 創世記" / ".tmp" / "第1章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 1,
                    "candidates": [{"name": "戰役", "type": "事件"}],
                }, allow_unicode=True),
            )
            fake = _FakeIndex([[("某人物", 0.30, {"title": "某人物", "type": "人物", "path": "p"})]])

            def fake_reranker(query, docs):
                return [{"index": 0, "relevance_score": 0.50}]
            fake_reranker.model_name = "test-reranker"

            path, total, flagged = candidate_report(
                "創世記", 1, root=root, index=fake, link_index={}, homonyms={},
                reranker=fake_reranker, use_rerank=True,
            )
            content = path.read_text(encoding="utf-8")

        self.assertEqual(1, flagged)
        self.assertIn("判定：⚠ 近鄰分類不相容", content)
        self.assertNotIn("🆕", content)

    def test_type_mismatch_embedding_high_score_flags_warning(self):
        """純 embedding 降級路徑中，分類不相容候選在高相似度（如 0.70 ≥ threshold）時必須標 ⚠ 近鄰分類不相容。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "01 創世記" / ".tmp" / "第1章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 1,
                    "candidates": [{"name": "戰役", "type": "事件"}],
                }, allow_unicode=True),
            )
            fake = _FakeIndex([[("某人物", 0.70, {"title": "某人物", "type": "人物", "path": "p"})]])

            path, total, flagged = candidate_report(
                "創世記", 1, root=root, index=fake, link_index={}, homonyms={}, threshold=0.60,
                use_rerank=False,
            )
            content = path.read_text(encoding="utf-8")

        self.assertEqual(1, flagged)
        self.assertIn("判定：⚠ 近鄰分類不相容", content)
        self.assertNotIn("🆕", content)

    def test_circuit_breaker_cause_chain_wrapped_errors(self):
        """斷路器遍歷 cause 鏈：HTTP 500/429/Timeout 熔斷；HTTP 400/401/404 不熔斷。"""
        import urllib.error
        from model_client import ModelError
        from semantic_lookup import _is_circuit_breaker_exception

        http500 = urllib.error.HTTPError("url", 500, "Internal Error", {}, None)
        http429 = urllib.error.HTTPError("url", 429, "Too Many Requests", {}, None)
        http400 = urllib.error.HTTPError("url", 400, "Bad Request", {}, None)
        http401 = urllib.error.HTTPError("url", 401, "Unauthorized", {}, None)
        http404 = urllib.error.HTTPError("url", 404, "Not Found", {}, None)

        # Wrapped in ModelError
        err500 = ModelError("failed")
        err500.__cause__ = http500
        self.assertTrue(_is_circuit_breaker_exception(err500))

        err429 = ModelError("rate limited")
        err429.__cause__ = http429
        self.assertTrue(_is_circuit_breaker_exception(err429))

        err_timeout = ModelError("timed out")
        err_timeout.__cause__ = TimeoutError("socket timeout")
        self.assertTrue(_is_circuit_breaker_exception(err_timeout))

        err400 = ModelError("bad request")
        err400.__cause__ = http400
        self.assertFalse(_is_circuit_breaker_exception(err400))

        err401 = ModelError("unauthorized")
        err401.__cause__ = http401
        self.assertFalse(_is_circuit_breaker_exception(err401))

        err404 = ModelError("not found")
        err404.__cause__ = http404
        self.assertFalse(_is_circuit_breaker_exception(err404))

    def test_legacy_embedding_schema_and_vector_sha_mismatch(self):
        """Legacy schema 或 vector SHA mismatch 時 SemanticIndex.load 必須拋出 ModelError。"""
        from semantic_lookup import SemanticIndex
        from model_client import ModelError
        import numpy as np

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            meta_file = root / "embedding_index.meta.json"
            vec_file = root / "embedding_index.npz"

            # 1. Legacy Schema 1
            meta_v1 = {"schema_version": 1, "model": "test-embed", "dim": 4, "entries": []}
            _write(meta_file, json.dumps(meta_v1))
            np.savez_compressed(vec_file, vectors=np.zeros((0, 4), dtype=np.float32))

            with self.assertRaises(ModelError) as ctx:
                SemanticIndex.load(meta_file=meta_file, vectors_file=vec_file, check_model=False)
            self.assertIn("legacy schema", str(ctx.exception))

            # 2. Vector SHA mismatch
            meta_v2 = {
                "schema_version": 2,
                "model": "test-embed",
                "dim": 4,
                "vectors_sha256": "fake_hash",
                "entries": [],
            }
            _write(meta_file, json.dumps(meta_v2))
            with self.assertRaises(ModelError) as ctx:
                SemanticIndex.load(meta_file=meta_file, vectors_file=vec_file, check_model=False)
            self.assertIn("指紋不符", str(ctx.exception))

    def test_candidate_report_refuses_stale_embedding_index(self):
        """當 embedding 索引落後條目庫時，candidate_report 必須主動拒絕執行。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記" / ".tmp" / "第1章").mkdir(parents=True)
            _write(
                root / "01 創世記" / ".tmp" / "第1章" / "link_candidates.yaml",
                yaml.safe_dump({"book": "創世記", "chapter": 1, "candidates": [{"name": "候選", "type": "主題"}]}),
            )
            # 條目庫已有 1 條，但 index meta 為空
            _write(root / "util" / "output" / "link_index.json", json.dumps({
                "新條目": {"type": "主題", "path": "link_folder/主題/新條目.md", "aliases": []}
            }))
            _write(root / "link_folder" / "主題" / "新條目.md", "# 新條目\n\n## 定義\n內容")
            _write(root / "_config" / "link_homonyms.yaml", "{}")
            _write(root / "_config" / "reranker_calibration.yaml", "models: {}")
            _write(
                root / "_config" / "model_endpoints.yaml",
                yaml.safe_dump({
                    "active": "test-ep",
                    "endpoints": {"test-ep": {"type": "openai", "base_url": "http://127.0.0.1:4001/v1", "model": "test-model"}},
                    "tasks": {
                        "embedding": {"endpoint": "test-ep", "model": "test-embed", "kind": "embedding"},
                        "rerank": {"endpoint": "test-ep", "model": "test-reranker", "kind": "rerank"},
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
            _write(root / "util" / "output" / "embedding_index.meta.json", json.dumps(meta, ensure_ascii=False))

            with self.assertRaises(ValueError) as ctx:
                candidate_report("創世記", 1, root=root)
            self.assertIn("未與目前條目庫同步", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
