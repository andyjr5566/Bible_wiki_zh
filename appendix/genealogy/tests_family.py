from __future__ import annotations

import copy
import json
import re
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import yaml

from . import family as family_module
from .check_basis import check_basis
from .family import build_families, step_strongs
from .tools.tipnr import canonical_strong, load_tipnr
from .roster import build_roster
from .wall import build_wall


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "appendix" / "genealogy" / "亞當到耶穌"
FAMILY_PATH = DATA_DIR / "家族.yaml"
ROSTER_PATH = DATA_DIR / "名冊.yaml"
READING_PATH = (
    ROOT / "appendix" / "website" / "全聖經" / "亞當到耶穌" / "src" / "data" / "reading.json"
)
NEH3_PATH = ROOT / "raw_scripture" / "尼希米記" / "第3章.txt"
REF_RE = re.compile(r"^(.+?)(\d+):(\d+)$")
SCRIPTURE_BOOKS = {"拉": "以斯拉記", "尼": "尼希米記"}


class BuildFamiliesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = yaml.safe_load(FAMILY_PATH.read_text(encoding="utf-8"))
        cls.roster_spec = yaml.safe_load(ROSTER_PATH.read_text(encoding="utf-8"))
        cls.reading = json.loads(READING_PATH.read_text(encoding="utf-8"))
        cls.neh3_verses = NEH3_PATH.read_text(encoding="utf-8").splitlines()[:32]
        if not any(segment.get("id") == "neh3" for segment in cls.reading.get("segments", [])):
            cls.reading["segments"].append({
                "id": "neh3",
                "title": "耶路撒冷城牆",
                "chapters": [{
                    "book": "尼",
                    "n": 3,
                    "verses": [
                        {"v": index, "text": text, "t": []}
                        for index, text in enumerate(cls.neh3_verses, start=1)
                    ],
                }],
            })
        cls.wall_spec = yaml.safe_load((DATA_DIR / "城牆.yaml").read_text(encoding="utf-8"))

    @classmethod
    def verse_text(cls, ref: str) -> str | None:
        match = REF_RE.fullmatch(ref)
        if match is None:
            return None
        book, chapter_text, verse_text = match.groups()
        folder = SCRIPTURE_BOOKS.get(book)
        if folder is None:
            return None
        path = ROOT / "raw_scripture" / folder / f"第{chapter_text}章.txt"
        if not path.is_file():
            return None
        lines = path.read_text(encoding="utf-8").splitlines()
        verse = int(verse_text)
        return lines[verse - 1] if 1 <= verse <= len(lines) else None

    @classmethod
    def build(
        cls, spec: dict | None = None, step_strongs_callback=None
    ) -> tuple[dict, dict, list[str]]:
        reading = copy.deepcopy(cls.reading)
        roster, roster_errors = build_roster(
            cls.roster_spec,
            reading,
            cls.verse_text,
            reading.get("links", []),
        )
        wall, wall_errors = build_wall(
            cls.wall_spec,
            reading,
            cls.verse_text,
            reading.get("links", []),
        )
        errors = list(roster_errors) + list(wall_errors)
        errors.extend(build_families(
            cls.spec if spec is None else spec,
            reading,
            roster,
            wall,
            cls.verse_text,
            step_strongs if step_strongs_callback is None else step_strongs_callback,
            check_basis,
            ROOT,
        ))
        return roster, wall or {}, errors

    def test_repository_families_build_and_attach(self) -> None:
        roster, wall, errors = self.build()
        self.assertEqual(errors, [], "\n".join(errors[:30]))
        ezra2 = next(item for item in roster["rosters"] if item["segment"] == "ezra2")
        parosh_row = next(row for section in ezra2["sections"] for row in section["rows"] if row.get("at") == "拉2:3")
        self.assertTrue(parosh_row["fam"])
        parosh = next(item for item in roster["families"] if item["name"] == "巴錄的子孫")
        place = next(item for item in parosh["places"] if item["at"] == "拉2:3")
        self.assertEqual(place["count"], 2172)
        self.assertEqual(place["unit"], "名")
        meremoth = next(item for item in wall["families"] if item["name"] == "米利末")
        self.assertTrue(any(item["at"] == "尼3:4" for item in meremoth["places"]))

    def test_word_missing_from_verse_is_reported(self) -> None:
        changed = copy.deepcopy(self.spec)
        changed["families"][0]["places"][0]["word"] = "這個名字不存在@1"
        _, _, errors = self.build(changed)
        self.assertTrue(any("沒有出現在該節經文裡" in error for error in errors), errors)

    def test_word_must_be_one_of_family_forms(self) -> None:
        changed = copy.deepcopy(self.spec)
        parosh = next(f for f in changed["families"] if f["name"] == "巴錄的子孫")
        place = next(p for p in parosh["places"] if p["at"] == "拉10:25")
        place["word"] = "比拿雅@1"
        _, _, errors = self.build(changed)
        self.assertTrue(any("拉10:25" in error and "不在 forms 中" in error for error in errors), errors)

    def test_changed_strong_requires_commentary_basis(self) -> None:
        changed = copy.deepcopy(self.spec)
        changed["families"][0]["places"].append({
            "at": "拉8:3",
            "word": "撒迦利亞@1",
            "strong": "H6551H",
        })
        _, _, errors = self.build(changed)
        self.assertTrue(any("place.strong 和家族 strong 不同時必須有註釋 basis" in error for error in errors), errors)

    def test_different_tipnr_is_rejected_even_with_commentary_basis(self) -> None:
        changed = copy.deepcopy(self.spec)
        parosh = next(f for f in changed["families"] if f["name"] == "巴錄的子孫")
        parosh["places"].append({
            "at": "拉8:3",
            "word": "巴錄@1",
            "strong": "H6551H",
            "basis": [{
                "source": "biblehub_study_ezra_8.txt",
                "quote": "Phinehas, grandson of Aaron",
            }],
        })
        _, _, errors = self.build(changed)
        self.assertTrue(any("拉8:3" in error and "TIPNR 不是同一條" in error for error in errors), errors)

    def test_same_tipnr_override_with_commentary_basis_is_allowed(self) -> None:
        changed = copy.deepcopy(self.spec)
        parosh = next(f for f in changed["families"] if f["name"] == "巴錄的子孫")
        parosh["places"].append({
            "at": "拉8:3",
            "word": "巴錄@1",
            "strong": "H6551X",
            "basis": [{
                "source": "biblehub_study_ezra_8.txt",
                "quote": "Phinehas, grandson of Aaron",
            }],
        })
        real_index = load_tipnr()
        by_dstrong = dict(real_index.by_dstrong)
        parosh_person = next(
            person for person in by_dstrong[canonical_strong("H6551G")]
            if person.unique_name == parosh["tipnr"]
        )
        fake_code = canonical_strong("H6551X")
        by_dstrong[fake_code] = [*by_dstrong.get(fake_code, []), parosh_person]
        fake_index = SimpleNamespace(by_dstrong=by_dstrong)

        def with_alt_step_code(ref: str) -> set[str] | None:
            codes = step_strongs(ref)
            if ref == "拉8:3" and codes is not None:
                return codes | {"H6551X"}
            return codes

        with patch.object(family_module, "load_tipnr", return_value=fake_index):
            _, _, errors = self.build(changed, with_alt_step_code)
        self.assertFalse(any("TIPNR 不是同一條" in error for error in errors), errors)
        self.assertFalse(any("place.strong 不同時必須有註釋 basis" in error for error in errors), errors)

    def test_english_name_mapping_must_match_step_gloss(self) -> None:
        changed = copy.deepcopy(self.spec)
        bani = next(f for f in changed["families"] if "巴尼" in f.get("forms", []))
        real_loader = family_module.load_chapter
        chapter_words = real_loader("拉", 2)
        target_strong = canonical_strong(bani["strong"])
        altered = dict(chapter_words)
        altered[10] = [
            replace(word, gloss="unrelated gloss")
            if target_strong in {
                canonical_strong(code)
                for code in re.findall(r"[HG]\d+[A-Za-z]*", word.strong)
            } else word
            for word in chapter_words.get(10, [])
        ]

        def load_with_unrelated_gloss(book: str, chapter: int):
            if book == "拉" and chapter == 2:
                return altered
            return real_loader(book, chapter)

        with patch.object(family_module, "load_chapter", side_effect=load_with_unrelated_gloss):
            _, _, errors = self.build(changed)
        self.assertTrue(any("拉2:10" in error and ("STEP gloss" in error or "對不起來" in error) for error in errors), errors)

    def test_family_strong_must_exist_in_step(self) -> None:
        changed = copy.deepcopy(self.spec)
        changed["families"][0]["strong"] = "H999999"
        _, _, errors = self.build(changed)
        self.assertTrue(any("STEP 該節沒有編號 H999999" in error for error in errors), errors)

    def test_family_basis_is_required(self) -> None:
        changed = copy.deepcopy(self.spec)
        changed["families"][0].pop("basis")
        _, _, errors = self.build(changed)
        self.assertTrue(any("basis 必須是非空清單" in error for error in errors), errors)

    def test_place_without_roster_or_wall_anchor_is_reported(self) -> None:
        changed = copy.deepcopy(self.spec)
        changed["families"][0]["places"].append({
            "at": "拉8:15",
            "word": "我@1",
        })
        _, _, errors = self.build(changed)
        self.assertTrue(any("拉8:15" in error and "不在名冊或城牆上" in error for error in errors), errors)

    def test_place_off_the_reading_route_is_reported(self) -> None:
        # 尼 1:1 不在讀經路線上：家族軌跡的小籤點了跳不過去
        changed = copy.deepcopy(self.spec)
        changed["families"][0]["places"].append({"at": "尼1:1", "word": "尼希米@1"})
        _, _, errors = self.build(changed)
        self.assertTrue(any("尼1:1" in error and "不在 reading" in error for error in errors), errors)


    def _family(self, spec: dict, name: str) -> dict:
        return next(item for item in spec["families"] if item["name"] == name)

    def test_occurrence_is_bound_to_its_step_word(self) -> None:
        # 拉 8:11 第二個「比拜」是撒迦利亞的父親（H893H，TIPNR 另一條），不是比拜家族（H893G）
        changed = copy.deepcopy(self.spec)
        place = next(p for p in self._family(changed, "比拜的子孫")["places"] if p["at"] == "拉8:11")
        place["word"] = "比拜@2"
        _, _, errors = self.build(changed)
        self.assertTrue(any("拉8:11" in e and "第 2 個「比拜」" in e for e in errors), errors)

    def test_form_without_english_mapping_is_reported(self) -> None:
        changed = copy.deepcopy(self.spec)
        family = self._family(changed, "但以理")
        family["forms"] = ["但以理", "近頓"]
        next(p for p in family["places"] if p["at"] == "尼10:6")["word"] = "近頓@1"
        _, _, errors = self.build(changed)
        self.assertTrue(any("尼10:6" in e and "英文對照表沒有「近頓」" in e for e in errors), errors)

if __name__ == "__main__":
    unittest.main()
