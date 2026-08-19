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
        root = Path(tmp)
        _write(root / "util" / "output" / "link_index.json",
               json.dumps(link_index, ensure_ascii=False))
        _write(root / "util" / "output" / "embedding_index.meta.json",
               json.dumps(meta, ensure_ascii=False))
        _write(root / "util" / "output" / "embedding_index.npz", "dummy")
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

    def test_fresh_index_reports_clean(self):
        entry = {"title": "甲", "type": "主題", "path": "link_folder/主題/甲.md", "aliases": []}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            correct = _hash(entry_embed_text("甲", entry, root=root))
            root = self._root_with(
                tmp,
                {"甲": entry, "甲別名": {"alias_of": "甲"}},  # alias 鍵應被忽略
                {"model": "m", "entries": [
                    {"title": "甲", "path": "p", "type": "主題", "hash": correct}
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

    def query_vectors(self, queries, top=3, return_matrix=False):
        self.received = list(queries)
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
        self.assertIn("判定：⚠ 未校準模型（uncalibrated-reranker），評分僅供排序參考，需人工確認", content)

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
        self.assertIn("判定：⚠ 分類不相容", content)

    def test_rerank_low_score_suggests_new_entry(self):
        """Rerank 所有候選分數皆低（<0.40）時判定為建議新條目。"""
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
            low = {"type": "主題", "secondary_types": []}
            fake = _FakeIndex(
                [[("條目", 0.2, low)], [("條目", 0.2, low)], [("條目", 0.2, low)]],
                matrix=matrix,
            )
            path, total, flagged = candidate_report(
                "創世記", 1, root=root, index=fake, link_index={}, homonyms={}, threshold=0.60,
                use_rerank=False,
            )
            content = path.read_text(encoding="utf-8")
        self.assertEqual(1, flagged)  # 索引近鄰全低分，只有互查一對
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


if __name__ == "__main__":
    unittest.main()
