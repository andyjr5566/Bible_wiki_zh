# -*- coding: utf-8 -*-
"""candidate_similarity.md 的「內文提及」一節：抓同一實體、不同譯名的既有條目。"""
import sys
import tempfile
import unittest
from pathlib import Path

UTIL_DIR = Path(__file__).resolve().parents[1]
if str(UTIL_DIR) not in sys.path:
    sys.path.insert(0, str(UTIL_DIR))
sys.path.insert(0, str(UTIL_DIR.parent))

import yaml

import semantic_lookup as sl
from semantic_lookup import candidate_report
from util.tests.test_embedding_tools import _FakeIndex


def _write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


BAMOTH = """---
type: 地點
secondary_types: []
aliases: []
status: formal
---

# 巴力的高處（Bamoth-baal）

## 定義

民數記22:41：巴勒領巴蘭到巴力的高處。

## 按書卷累積

### 約書亞記

<!-- accumulation:約書亞記:13:start -->
#### [[06 約書亞記/第13章|第13章]]
- 本章重點：本章自己寫的累積，提到巴末巴力與書13:17。
<!-- accumulation:約書亞記:13:end -->

## 主題發展

書13:17 同一個地名以「巴末巴力」出現在流便所得的城中。
"""

ONLY_OWN_ACCUMULATION = """---
type: 地點
aliases: []
---

# 別的地方

## 定義

這是別的地方。

<!-- accumulation:約書亞記:13:start -->
- 本章自己寫的：巴末巴力、書13:17。
<!-- accumulation:約書亞記:13:end -->
"""

CN_REFERENCE = """---
type: 地點
---

# 底本

## 定義

後來約書亞將這城給流便人（書十三16-17）。
"""

UNRELATED = """---
type: 人物
---

# 無關的人

## 定義

他住在書13:30 提到的地方，也提到書130:17（不是約書亞記13章）和走出13:17。
"""


class ReferenceRegexTests(unittest.TestCase):
    def setUp(self):
        self.regex = sl._chapter_reference_regex("約書亞記", 13)

    def _verses(self, text):
        found = set()
        for match in self.regex.finditer(text):
            found |= sl._parse_reference_verses(match.group(1) or match.group(2))
        return found

    def test_arabic_chinese_and_full_name_forms(self):
        self.assertEqual({17}, self._verses("見書13:17。"))
        self.assertEqual({16, 17}, self._verses("（書十三16-17）"))
        self.assertEqual({15, 16, 17, 18}, self._verses("約書亞記13:15-18"))
        self.assertEqual({3, 17}, self._verses("書13:3,17"))
        self.assertEqual({17}, self._verses("書13：17"))

    def test_other_chapters_and_other_words_do_not_match(self):
        self.assertEqual(set(), self._verses("書130:17"))
        self.assertEqual(set(), self._verses("書14:17"))
        self.assertEqual(set(), self._verses("走出13:17"))
        self.assertEqual(set(), self._verses("民13:17"))


class ScanBodyMentionsTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        _write(self.root / "link_folder" / "地點" / "巴力的高處（Bamoth-baal）.md", BAMOTH)
        _write(self.root / "link_folder" / "地點" / "別的地方.md", ONLY_OWN_ACCUMULATION)
        _write(self.root / "link_folder" / "地點" / "底本.md", CN_REFERENCE)
        _write(self.root / "link_folder" / "人物" / "無關的人.md", UNRELATED)
        self.candidate = {
            "name": "巴末巴力", "suggested_type": "地點",
            "evidence": "第17節；流便所得的城中有巴末巴力",
            "surfaces": [{"phrase": "巴末巴力", "verses": [17]}],
        }

    def test_finds_same_entity_under_a_different_translation(self):
        result = sl.scan_body_mentions([self.candidate], "約書亞記", 13, root=self.root)["巴末巴力"]
        self.assertEqual([17], result["verses"])
        self.assertEqual(["巴力的高處（Bamoth-baal）"], [h["title"] for h in result["name_hits"]])
        ref_titles = {h["title"] for h in result["ref_hits"]}
        self.assertEqual({"巴力的高處（Bamoth-baal）", "底本"}, ref_titles)   # 書十三16-17 也算

    def test_own_chapter_accumulation_block_and_frontmatter_are_excluded(self):
        result = sl.scan_body_mentions([self.candidate], "約書亞記", 13, root=self.root)["巴末巴力"]
        self.assertNotIn("別的地方", {h["title"] for h in result["name_hits"] + result["ref_hits"]})
        # 巴力的高處的命中必須來自「主題發展」，不是本章累積區塊那一句
        bamoth = next(h for h in result["name_hits"])
        self.assertIn("流便所得的城中", bamoth["snippet"])
        self.assertNotIn("本章自己寫的累積", bamoth["snippet"])

    def test_unrelated_entry_is_not_reported_and_other_verses_do_not_hit(self):
        result = sl.scan_body_mentions([self.candidate], "約書亞記", 13, root=self.root)["巴末巴力"]
        self.assertNotIn("無關的人", {h["title"] for h in result["name_hits"] + result["ref_hits"]})

    def test_parenthetical_transliteration_is_stripped_from_candidate_name(self):
        candidate = dict(self.candidate, name="巴末巴力（bamoth-baal）")
        result = sl.scan_body_mentions([candidate], "約書亞記", 13, root=self.root)
        self.assertEqual(1, len(result[candidate["name"]]["name_hits"]))

    def test_no_link_folder_is_fine(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = sl.scan_body_mentions([self.candidate], "約書亞記", 13, root=tmp)
        self.assertEqual([], result["巴末巴力"]["name_hits"])

    def test_scan_is_read_only(self):
        before = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        sl.scan_body_mentions([self.candidate], "約書亞記", 13, root=self.root)
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()})


class ReportIntegrationTests(unittest.TestCase):
    def _report(self, tmp, candidates, link_index=None):
        root = Path(tmp)
        (root / "06 約書亞記").mkdir(parents=True)
        _write(root / "link_folder" / "地點" / "巴力的高處（Bamoth-baal）.md", BAMOTH)
        _write(
            root / "06 約書亞記" / ".tmp" / "第13章" / "link_candidates.yaml",
            yaml.safe_dump({"book": "約書亞記", "chapter": 13, "candidates": candidates},
                           allow_unicode=True),
        )
        fake = _FakeIndex([
            [("毫不相關", 0.42, {"type": "地點", "path": "link_folder/地點/毫不相關.md"})]
            for _ in candidates
        ])
        path, total, flagged = candidate_report(
            "約書亞記", 13, root=root, index=fake, link_index=link_index or {}, homonyms={},
            use_rerank=False)
        return path.read_text(encoding="utf-8"), flagged

    def test_new_candidate_with_body_mention_gets_warning_in_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            content, flagged = self._report(tmp, [{
                "name": "巴末巴力", "type": "地點", "evidence": "第17節；流便所得的城中有巴末巴力",
                "surfaces": [{"phrase": "巴末巴力", "verses": [17]}],
            }])
        # 語義近鄰 0.42 < 門檻：舊行為會是「🆕 建議建立新條目」，現在摘要必須有 ⚠
        self.assertIn("🆕 建議建立新條目", content)
        summary = content.split("## 摘要：需要判斷的項目", 1)[1].split("\n## ", 1)[0]
        self.assertIn("- 巴末巴力：⚠ 內文提及：[[巴力的高處（Bamoth-baal）]]", summary)
        section = content.split("## 內文提及", 1)[1]
        self.assertIn("(a) 內文含候選名「巴末巴力」", section)
        self.assertIn("(b) 內文引用本章經節", section)
        self.assertEqual(1, flagged)

    def test_candidate_without_hits_has_no_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            content, flagged = self._report(tmp, [{
                "name": "完全沒人提過的地名", "type": "地點", "evidence": "第99節", "surfaces": [],
            }])
        summary = content.split("## 摘要：需要判斷的項目", 1)[1].split("\n## ", 1)[0]
        self.assertNotIn("內文提及", summary)
        self.assertIn("（沒有命中）", content)
        self.assertEqual(0, flagged)

    def test_literal_match_candidates_are_not_scanned(self):
        link_index = {"巴力的高處": {"title": "巴力的高處（Bamoth-baal）", "type": "地點",
                                      "path": "link_folder/地點/巴力的高處（Bamoth-baal）.md"}}
        with tempfile.TemporaryDirectory() as tmp:
            content, _flagged = self._report(tmp, [{
                "name": "巴力的高處", "type": "地點", "evidence": "第17節", "surfaces": [],
            }], link_index=link_index)
        self.assertNotIn("### 巴力的高處（", content.split("## 內文提及", 1)[1])


if __name__ == "__main__":
    unittest.main()
