from __future__ import annotations

import copy
import re
import unittest
from pathlib import Path

import yaml

from .wall import build_wall


ROOT = Path(__file__).resolve().parents[2]
WALL_PATH = ROOT / "appendix" / "genealogy" / "亞當到耶穌" / "城牆.yaml"
SCRIPTURE_PATH = ROOT / "raw_scripture" / "尼希米記" / "第3章.txt"
REF_RE = re.compile(r"^尼3:(\d+)$")


class BuildWallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = yaml.safe_load(WALL_PATH.read_text(encoding="utf-8"))
        cls.verses = SCRIPTURE_PATH.read_text(encoding="utf-8").splitlines()[:32]
        cls.reading = {
            "segments": [{
                "id": "neh3",
                "title": "耶路撒冷城牆",
                "chapters": [{
                    "book": "尼",
                    "n": 3,
                    "verses": [
                        {"v": index, "text": text, "t": []}
                        for index, text in enumerate(cls.verses, start=1)
                    ],
                }],
            }],
            "links": [],
        }

    @classmethod
    def verse_text(cls, ref: str) -> str | None:
        match = REF_RE.fullmatch(ref)
        if match is None:
            return None
        verse = int(match.group(1))
        return cls.verses[verse - 1] if 1 <= verse <= len(cls.verses) else None

    @classmethod
    def build(cls, spec: dict | None = None, reading: dict | None = None) -> tuple[dict | None, list[str]]:
        return build_wall(
            cls.spec if spec is None else spec,
            cls.reading if reading is None else reading,
            cls.verse_text,
            (cls.reading if reading is None else reading).get("links", []),
        )

    def test_repository_wall_builds_complete_ring(self) -> None:
        data, errors = self.build()
        self.assertEqual(errors, [], "\n".join(errors))
        self.assertIsNotNone(data)
        assert data is not None
        self.assertEqual(len(data["ring"]), len(self.spec["ring"]))
        self.assertEqual(data["ring"][0]["kind"], "gate")
        self.assertEqual(data["ring"][0]["t"], "羊門")
        self.assertTrue(data["ring"][-1]["back"])

    def test_missing_gate_name_is_reported(self) -> None:
        changed = copy.deepcopy(self.spec)
        changed["ring"][0]["gate"] = "不存在的門"
        _, errors = self.build(changed)
        self.assertTrue(any("逐字" in error for error in errors), errors)

    def test_ring_order_is_reported(self) -> None:
        changed = copy.deepcopy(self.spec)
        second = next(i for i, item in enumerate(changed["ring"]) if item.get("at") == "尼3:2" and "names" in item)
        fourth = next(i for i, item in enumerate(changed["ring"]) if item.get("at") == "尼3:4" and "names" in item)
        changed["ring"][second], changed["ring"][fourth] = changed["ring"][fourth], changed["ring"][second]
        _, errors = self.build(changed)
        self.assertTrue(any("順序不可倒退" in error for error in errors), errors)

    def test_uncovered_verse_is_reported(self) -> None:
        changed = copy.deepcopy(self.spec)
        changed["ring"] = [item for item in changed["ring"] if item.get("at") != "尼3:26"]
        _, errors = self.build(changed)
        self.assertTrue(any("尼3:26" in error and "必須有城牆項目" in error for error in errors), errors)

    def test_same_verse_structures_follow_scripture_order(self) -> None:
        changed = copy.deepcopy(self.spec)
        first = next(i for i, item in enumerate(changed["ring"]) if item.get("at") == "尼3:1" and item.get("tower") == "哈米亞樓")
        second = next(i for i, item in enumerate(changed["ring"]) if item.get("at") == "尼3:1" and item.get("tower") == "哈楠業樓")
        changed["ring"][first], changed["ring"][second] = changed["ring"][second], changed["ring"][first]
        _, errors = self.build(changed)
        self.assertTrue(any("尼3:1" in error and "經文位置順序不可倒退" in error for error in errors), errors)

    def test_missing_name_is_reported(self) -> None:
        changed = copy.deepcopy(self.spec)
        item = next(item for item in changed["ring"] if item.get("at") == "尼3:2" and "names" in item)
        item["names"][0] = "不在經文"
        _, errors = self.build(changed)
        self.assertTrue(any("名字" in error and "沒有依序" in error for error in errors), errors)

    def test_back_is_required(self) -> None:
        changed = copy.deepcopy(self.spec)
        changed["ring"][-1].pop("back")
        _, errors = self.build(changed)
        self.assertTrue(any("恰好有一項 back" in error for error in errors), errors)

    def test_missing_reading_segment_is_reported(self) -> None:
        data, errors = self.build(reading={"segments": [], "links": []})
        self.assertIsNone(data)
        self.assertTrue(any("segment" in error and "不在 reading" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
