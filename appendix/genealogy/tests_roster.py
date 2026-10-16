from __future__ import annotations

import copy
import json
import re
import unittest
from functools import lru_cache
from pathlib import Path

import yaml

from .roster import build_roster, chinese_number


ROOT = Path(__file__).resolve().parents[2]
ROSTER_PATH = ROOT / "appendix" / "genealogy" / "亞當到耶穌" / "名冊.yaml"
READING_PATH = (
    ROOT / "appendix" / "website" / "全聖經" / "亞當到耶穌" / "src" / "data" / "reading.json"
)
SCRIPTURE_BOOKS = {"拉": "以斯拉記", "尼": "尼希米記"}
REF_PATTERN = re.compile(r"^(.+?)(\d+):(\d+)$")


def _find_row(spec: dict, segment: str, ref: str) -> dict:
    roster = next(item for item in spec["rosters"] if item["segment"] == segment)
    return next(
        row
        for section in roster["sections"]
        for row in section["rows"]
        if row["at"] == ref
    )


def _built_row(data: dict, segment: str, ref: str) -> dict:
    roster = next(item for item in data["rosters"] if item["segment"] == segment)
    return next(
        row
        for section in roster["sections"]
        for row in section["rows"]
        if row["at"] == ref
    )


class ChineseNumberTests(unittest.TestCase):
    def test_examples(self) -> None:
        examples = {
            "二千一百七十二": 2172,
            "一千零五十二": 1052,
            "二千零五十六": 2056,
            "一百一十二": 112,
            "九十五": 95,
            "十": 10,
            "一十": 10,
            "一十八": 18,
            "四萬二千三百六十": 42360,
            "一萬零一十": 10010,
            "六萬一千": 61000,
            "二萬": 20000,
            "兩百": 200,
            "零": 0,
            "〇": 0,
        }
        for text, expected in examples.items():
            with self.subTest(text=text):
                self.assertEqual(chinese_number(text), expected)

    def test_invalid_inputs_return_none(self) -> None:
        for text in ("", "一百百", "二千千", "零一十", "十十", "兩兩", "一萬萬", "十二百", "三百零十", "一萬零十", "１２"):
            with self.subTest(text=text):
                self.assertIsNone(chinese_number(text))


class BuildRosterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with ROSTER_PATH.open(encoding="utf-8") as source:
            cls.spec = yaml.safe_load(source)
        with READING_PATH.open(encoding="utf-8") as source:
            cls.reading = json.load(source)

    @staticmethod
    @lru_cache(maxsize=None)
    def _scripture_lines(book: str, chapter: int) -> tuple[str, ...]:
        book_folder = SCRIPTURE_BOOKS.get(book)
        if book_folder is None:
            return ()
        path = ROOT / "raw_scripture" / book_folder / f"第{chapter}章.txt"
        return tuple(path.read_text(encoding="utf-8").splitlines())

    @classmethod
    def verse_text(cls, ref: str) -> str | None:
        match = REF_PATTERN.fullmatch(ref)
        if not match:
            return None
        book, chapter_text, verse_text = match.groups()
        lines = cls._scripture_lines(book, int(chapter_text))
        verse = int(verse_text)
        return lines[verse - 1] if 1 <= verse <= len(lines) else None

    @classmethod
    def build(cls, spec: dict | None = None, links: list[dict] | None = None) -> tuple[dict, list[str]]:
        current_spec = cls.spec if spec is None else spec
        current_links = cls.reading["links"] if links is None else links
        return build_roster(
            current_spec,
            cls.reading,
            cls.verse_text,
            current_links,
        )

    def test_repository_labels_do_not_contain_chinese_numerals(self) -> None:
        numerals = set("零〇一二三四五六七八九十百千萬兩")
        labels = (
            row.get("label")
            for roster in self.spec["rosters"]
            for section in roster.get("sections", [])
            for row in section.get("rows", [])
        )
        violations = [label for label in labels if isinstance(label, str) and any(char in numerals for char in label)]
        self.assertEqual(violations, [])

    def test_repository_roster_builds_and_has_expected_values(self) -> None:
        data, errors = self.build()
        self.assertEqual(errors, [])

        ezra3 = _built_row(data, "ezra2", "拉2:3")
        self.assertEqual(ezra3["count"], 2172)
        self.assertTrue(ezra3["bar"])

        ezra64 = _built_row(data, "ezra2", "拉2:64")
        self.assertTrue(ezra64["big"])

        ezra = next(item for item in data["rosters"] if item["segment"] == "ezra2")
        nehemiah = next(item for item in data["rosters"] if item["segment"] == "neh7")
        self.assertEqual(ezra["max"], 3630)
        self.assertEqual(nehemiah["max"], 3930)

        self.assertTrue(_built_row(data, "neh7", "尼7:10")["differs"])
        self.assertNotIn("differs", _built_row(data, "neh7", "尼7:8"))

    def test_ezra8_counts_use_person_and_empty_units(self) -> None:
        data, errors = self.build()
        self.assertEqual(errors, [], "\n".join(errors))
        self.assertTrue(_built_row(data, "ezra8", "拉8:3")["bar"])
        self.assertEqual(_built_row(data, "ezra8", "拉8:3")["unit"], "人")
        self.assertTrue(_built_row(data, "ezra8", "拉8:4")["bar"])
        self.assertEqual(_built_row(data, "ezra8", "拉8:4")["unit"], "")

    def test_ezra8_count_mismatch_is_reported(self) -> None:
        changed = copy.deepcopy(self.spec)
        _find_row(changed, "ezra8", "拉8:4")["count"] = 201
        _, errors = self.build(changed)
        self.assertTrue(any("拉8:4" in error and "count 201" in error for error in errors), errors)

    def test_ezra8_person_unit_must_match_scripture(self) -> None:
        changed = copy.deepcopy(self.spec)
        _find_row(changed, "ezra8", "拉8:3")["unit"] = "名"
        _, errors = self.build(changed)
        self.assertTrue(any("拉8:3" in error and "量詞" in error for error in errors), errors)

    def test_ezra8_empty_unit_cannot_be_person(self) -> None:
        changed = copy.deepcopy(self.spec)
        _find_row(changed, "ezra8", "拉8:4")["unit"] = "人"
        _, errors = self.build(changed)
        self.assertTrue(any("拉8:4" in error and "找不到中文數字" in error for error in errors), errors)

    def test_ezra8_label_cannot_swallow_prefix_of_number(self) -> None:
        changed = copy.deepcopy(self.spec)
        row = _find_row(changed, "ezra8", "拉8:9")
        row["label"] = "屬約押的子孫有耶歇的兒子俄巴底亞，同著他有男丁二百"
        row.pop("names")
        row["count"] = 18
        data, errors = self.build(changed)
        self.assertEqual(_built_row(data, "ezra8", "拉8:9")["count"], 18)
        self.assertTrue(any("拉8:9" in error and "中文數字字" in error for error in errors), errors)
        self.assertTrue(any("拉8:9" in error and "左邊界" in error for error in errors), errors)

    def test_plain_roster_rejects_any_link_in_its_segment(self) -> None:
        links = list(self.reading["links"]) + [{"at": "拉10:25", "word": "巴錄@1"}]
        _, errors = self.build(links=links)
        self.assertTrue(any("plain 的名冊不得有冊上有名的連結" in error for error in errors), errors)

    def test_tone_seal_and_label_adjacent_name_are_exported(self) -> None:
        data, errors = self.build()
        self.assertEqual(errors, [], "\n".join(errors))
        ezra10 = next(item for item in data["rosters"] if item["segment"] == "ezra10")
        neh10 = next(item for item in data["rosters"] if item["segment"] == "neh10")
        ezra8 = next(item for item in data["rosters"] if item["segment"] == "ezra8")
        self.assertEqual(ezra10["tone"], "plain")
        self.assertTrue(neh10["seal"])
        section = next(item for item in ezra8["sections"] if item["title"] == "召來的首領和教習")
        self.assertEqual(section["rows"][1]["names"][0]["t"], "約雅立")

    def test_count_mismatch_is_reported(self) -> None:
        changed = copy.deepcopy(self.spec)
        _find_row(changed, "ezra2", "拉2:3")["count"] = 2173
        _, errors = self.build(changed)
        self.assertTrue(any("拉2:3" in error and "count" in error for error in errors), errors)

    def test_label_swallowing_its_number_is_reported(self) -> None:
        # 審查找到的漏洞：label 吞進自己的數字後，count 會對到下一項（騾子）的數字
        changed = copy.deepcopy(self.spec)
        row = _find_row(changed, "ezra2", "拉2:66")
        row["label"], row["count"] = "馬七百三十六匹", 245
        _, errors = self.build(changed)
        self.assertTrue(any("拉2:66" in error for error in errors), errors)

    def test_number_borrowed_across_another_label_is_reported(self) -> None:
        # 同一節的第一行標成「馬」卻宣稱騾子的數字：中間夾著「騾子」那一行的 label
        changed = copy.deepcopy(self.spec)
        rows = [r for s in changed["rosters"][0]["sections"] for r in s["rows"] if r.get("at") == "拉2:66"]
        rows[0]["count"] = 245
        _, errors = self.build(changed)
        self.assertTrue(any("拉2:66" in error for error in errors), errors)

    def test_changed_label_is_reported(self) -> None:
        changed = copy.deepcopy(self.spec)
        _find_row(changed, "ezra2", "拉2:3")["label"] = "巴錄的後裔"
        _, errors = self.build(changed)
        self.assertTrue(any("拉2:3" in error and "label" in error for error in errors), errors)

    def test_uncovered_verse_is_reported(self) -> None:
        changed = copy.deepcopy(self.spec)
        changed["rosters"][0]["narrative"].remove("拉2:63")
        _, errors = self.build(changed)
        self.assertTrue(any("拉2:63" in error and "narrative" in error for error in errors), errors)

    def test_changed_quote_is_reported(self) -> None:
        changed = copy.deepcopy(self.spec)
        quote = next(item for item in changed["rosters"] if item["segment"] == "neh7")["quote"]
        quote["text"] = quote["text"].replace("我", "他", 1)
        _, errors = self.build(changed)
        self.assertTrue(any("尼7:5" in error and "quote.text" in error for error in errors), errors)

    def test_out_of_order_rows_are_reported(self) -> None:
        changed = copy.deepcopy(self.spec)
        family = next(
            section
            for section in changed["rosters"][0]["sections"]
            if section["title"] == "照家族"
        )
        family["rows"][0], family["rows"][1] = family["rows"][1], family["rows"][0]
        _, errors = self.build(changed)
        self.assertTrue(any("拉2:3" in error and "順序" in error for error in errors), errors)

    def test_name_missing_a_character_is_reported(self) -> None:
        changed = copy.deepcopy(self.spec)
        _find_row(changed, "ezra2", "拉2:2")["names"][0] = "所羅"
        _, errors = self.build(changed)
        self.assertTrue(any("拉2:2" in error and "名字" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
