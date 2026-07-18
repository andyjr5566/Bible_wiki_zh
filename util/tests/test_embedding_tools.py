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
from semantic_lookup import candidate_query_text, candidate_report


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
    def test_report_flags_above_threshold_and_counts(self):
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
                [("既有近似條目", 0.55, {"type": "主題"}),
                 ("低分條目", 0.20, {"type": "主題"})],
                [("不相關", 0.15, {"type": "神學"})],
            ])
            path, total, flagged = candidate_report(
                "創世記", 1, root=root, index=fake, link_index={}, homonyms={}, threshold=0.40
            )
            content = path.read_text(encoding="utf-8")
        self.assertEqual(2, total)
        self.assertEqual(1, flagged)
        self.assertIn("0.550 ⚠ 既有近似條目", content)
        self.assertIn("0.200 低分條目", content)
        self.assertIn("依據甲", fake.received[0])  # evidence 進了查詢文本
        self.assertEqual("candidate_similarity.md", path.name)

    def test_same_entity_hit_marked_not_flagged(self):
        """同名與括號前裸名命中都算同實體：註記、不標 ⚠。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "01 創世記" / ".tmp" / "第1章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 1,
                    "candidates": [
                        {"name": "既有條目", "type": "主題"},
                        {"name": "皂莢木", "type": "主題"},
                    ],
                }, allow_unicode=True),
            )
            fake = _FakeIndex([
                [("既有條目", 0.70, {"type": "主題"})],
                [("皂莢木（atzei shittim）", 0.70, {"type": "原文"})],  # 裸名命中
            ])
            path, total, flagged = candidate_report(
                "創世記", 1, root=root, index=fake, link_index={}, homonyms={}, threshold=0.60
            )
            content = path.read_text(encoding="utf-8")
        self.assertEqual(0, flagged)  # 同實體命中不算「待改名」
        self.assertEqual(2, content.count("resolver 可自動對上"))
        self.assertNotIn("0.700 ⚠", content)  # hit 行不得有 ⚠（表頭圖例不算）

    def test_only_top1_gets_flag(self):
        """⚠ 只標 top-1：排第二的高分近鄰只顯示、不標記。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "01 創世記" / ".tmp" / "第1章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 1,
                    "candidates": [{"name": "甲候選", "type": "主題"}],
                }, allow_unicode=True),
            )
            fake = _FakeIndex([[
                ("甲候選", 0.75, {"type": "主題"}),          # top1 同實體
                ("高分兄弟條目", 0.70, {"type": "主題"}),     # top2 高分但不標
            ]])
            path, total, flagged = candidate_report(
                "創世記", 1, root=root, index=fake, link_index={}, homonyms={}, threshold=0.60
            )
            content = path.read_text(encoding="utf-8")
        self.assertEqual(0, flagged)
        self.assertNotIn("0.750 ⚠", content)
        self.assertNotIn("0.700 ⚠", content)
        self.assertIn("0.700 高分兄弟條目", content)

    def test_type_incompatible_top1_not_flagged(self):
        """事件候選的 top-1 是其主角人物＝跨分類鄰居，不標 ⚠。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "01 創世記" / ".tmp" / "第1章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 1,
                    "candidates": [
                        {"name": "以色列戰勝巴珊王噩", "type": "事件"},
                        {"name": "同分類近似", "type": "主題"},
                    ],
                }, allow_unicode=True),
            )
            fake = _FakeIndex([
                [("巴珊王噩", 0.78, {"type": "人物", "secondary_types": []})],
                [("既有主題條目", 0.70, {"type": "主題", "secondary_types": []})],
            ])
            path, total, flagged = candidate_report(
                "創世記", 1, root=root, index=fake, link_index={}, homonyms={}, threshold=0.60
            )
            content = path.read_text(encoding="utf-8")
        self.assertEqual(1, flagged)  # 只有分類相容的那筆
        self.assertNotIn("0.780 ⚠", content)
        self.assertIn("0.700 ⚠ 既有主題條目", content)

    def test_secondary_type_counts_as_compatible(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01 創世記").mkdir(parents=True)
            _write(
                root / "01 創世記" / ".tmp" / "第1章" / "link_candidates.yaml",
                yaml.safe_dump({
                    "book": "創世記", "chapter": 1,
                    "candidates": [{"name": "雅博河", "type": "地點"}],
                }, allow_unicode=True),
            )
            fake = _FakeIndex([
                [("雅博", 0.77, {"type": "原文", "secondary_types": ["地點"]})],
            ])
            _, _, flagged = candidate_report(
                "創世記", 1, root=root, index=fake, link_index={}, homonyms={}, threshold=0.60
            )
        self.assertEqual(1, flagged)

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
            # 前兩列夾角極小（cos≈0.9），第三列正交
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
                "創世記", 1, root=root, index=fake, link_index={}, homonyms={}, threshold=0.60
            )
            content = path.read_text(encoding="utf-8")
        self.assertEqual(1, flagged)  # 索引近鄰全低分，只有互查一對
        self.assertIn("0.900 ⚠ 叛教之城甲 ↔ 叛教之城乙", content)
        self.assertNotIn("無關候選 ↔", content)


if __name__ == "__main__":
    unittest.main()
