"""從大衛到所羅門（職位.yaml 第五類）的閘門測試：用真的建置資料，改一處看會不會擋下來。"""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import build_genealogy as bg  # noqa: E402
from check_basis import check_basis  # noqa: E402
from roles import build_roles  # noqa: E402


class SolomonRolesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = bg.LineageBuilder(HERE / "亞當到耶穌")
        cls.raw = cls.builder._yaml("職位.yaml", {})
        cls.helpers = {"parse_refs": bg.parse_refs, "prefix_book": bg.prefix_book, "display": bg.display,
                       "FULL_TO_ABBR": bg.FULL_TO_ABBR, "ROOT": bg.ROOT, "check_basis": check_basis}

    def build(self, raw: dict) -> tuple[dict, list[str]]:
        self.builder.errors = []
        data, _ = build_roles(self.builder, raw, self.helpers)
        return data, list(self.builder.errors)

    def box(self, raw: dict, box_id: str) -> dict:
        category = next(c for c in raw["categories"] if c["id"] == "solomon")
        return next(b for b in category["boxes"] if b["id"] == box_id)

    def test_repository_builds(self) -> None:
        data, errors = self.build(copy.deepcopy(self.raw))
        self.assertEqual(errors, [])
        category = next(c for c in data["categories"] if c["id"] == "solomon")
        court = next(b for b in category["boxes"] if b["id"] == "solomon-court")
        same = [row["same"] for row in court["rows"] if row.get("same")]
        self.assertEqual(sorted(same), ["亞多蘭", "約沙法#亞希律之子"])
        moved = [row["moved"]["key"] for row in court["rows"] if row.get("moved")]
        self.assertEqual(moved, ["比拿雅#耶何耶大之子"])
        officials = next(b for b in category["boxes"] if b["id"] == "solomon-officials")
        self.assertEqual(len(officials["members"]), 12)
        self.assertTrue(all("order" not in m for m in officials["members"]))

    def test_officials_kind_must_be_tiles(self) -> None:
        raw = copy.deepcopy(self.raw)
        self.box(raw, "solomon-officials")["kind"] = "list"
        _, errors = self.build(raw)
        self.assertTrue(any("kind 必須是 tiles" in e for e in errors), errors)

    def test_same_person_without_basis_is_reported(self) -> None:
        raw = copy.deepcopy(self.raw)
        # 撒督、亞比亞他：GT 說可能只是同名 → 不能寫成同一人（不是 people 定義、有根據的人）
        row = next(r for r in self.box(raw, "solomon-court")["rows"] if r["office"] == "祭司長")
        row["same"] = "撒督#王上4:4"
        row["solomon"] = ["亞比亞他#王上4:4"]
        _, errors = self.build(raw)
        self.assertTrue(any("同一人" in e for e in errors), errors)

    def test_month_on_officials_is_reported_even_when_kind_is_list(self) -> None:
        raw = copy.deepcopy(self.raw)
        box = self.box(raw, "solomon-officials")
        box["kind"] = "list"
        box["members"][0]["month"] = 1
        _, errors = self.build(raw)
        self.assertTrue(any("月份" in e for e in errors), errors)

    def test_order_on_officials_is_reported_even_when_kind_is_list(self) -> None:
        raw = copy.deepcopy(self.raw)
        box = self.box(raw, "solomon-officials")
        box["kind"] = "list"
        box["members"][0]["order"] = 1
        _, errors = self.build(raw)
        self.assertTrue(any("序號" in e for e in errors), errors)

    def test_eleven_officials_is_reported_even_when_kind_is_list(self) -> None:
        raw = copy.deepcopy(self.raw)
        box = self.box(raw, "solomon-officials")
        box["kind"] = "list"
        box["members"].pop()
        _, errors = self.build(raw)
        self.assertTrue(any("12 位" in e for e in errors), errors)

    def test_name_not_in_verse_is_reported(self) -> None:
        raw = copy.deepcopy(self.raw)
        row = next(r for r in self.box(raw, "solomon-court")["rows"] if r["office"] == "書記")
        row["david"][0]["ref"] = "代上18:15"  # 沙威沙不在代上 18:15
        _, errors = self.build(raw)
        self.assertTrue(any("沙威沙" in e for e in errors), errors)

    def test_solomon_non_reference_qualifier_must_be_in_verse(self) -> None:
        raw = copy.deepcopy(self.raw)
        box = self.box(raw, "solomon-court")
        member = next(m for m in box["members"] if m.get("n") == "撒督" and m.get("q") == "王上4:4")
        member["q"] = "不存在的父親"
        for row in box.get("rows", []):
            row["solomon"] = [
                "撒督#不存在的父親" if key == "撒督#王上4:4" else key
                for key in row.get("solomon", [])
            ]
        _, errors = self.build(raw)
        self.assertTrue(any("不存在的父親" in e and "限定詞" in e for e in errors), errors)

    def test_same_name_n_member_requires_valid_basis(self) -> None:
        raw = copy.deepcopy(self.raw)
        member = next(
            m for m in self.box(raw, "solomon-court")["members"]
            if m.get("n") == "撒督" and m.get("q") == "王上4:4"
        )
        member.pop("basis")
        _, errors = self.build(raw)
        self.assertTrue(any("同名不同人的分開要寫根據" in e for e in errors), errors)

    def test_same_name_as_tree_or_other_box_requires_basis(self) -> None:
        # 以拉的兒子示每：和家譜樹上、別的職位方塊裡的示每同名，拿掉根據要擋
        raw = copy.deepcopy(self.raw)
        member = next(m for m in self.box(raw, "solomon-officials")["members"] if m.get("n") == "示每")
        member.pop("basis")
        _, errors = self.build(raw)
        self.assertTrue(any("同名不同人的分開要寫根據" in e for e in errors), errors)

    def test_moved_person_must_be_in_row(self) -> None:
        raw = copy.deepcopy(self.raw)
        row = next(r for r in self.box(raw, "solomon-court")["rows"] if r["office"] == "元帥")
        row["solomon"] = []
        _, errors = self.build(raw)
        self.assertTrue(any("moved" in e for e in errors), errors)

    def test_member_left_out_of_rows_is_reported(self) -> None:
        raw = copy.deepcopy(self.raw)
        row = next(r for r in self.box(raw, "solomon-court")["rows"] if r["office"] == "家宰")
        row["solomon"] = []
        _, errors = self.build(raw)
        self.assertTrue(any("沒有排進任何一列" in e for e in errors), errors)

    def test_spouse_not_in_verse_is_reported(self) -> None:
        raw = copy.deepcopy(self.raw)
        member = next(m for m in self.box(raw, "solomon-officials")["members"] if m.get("spouse") == "他法")
        member["spouse"] = "巴實抹"
        _, errors = self.build(raw)
        self.assertTrue(any("巴實抹" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
