"""Align STEP proper-name sequences across parallel Bible passages."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Sequence

try:
    from .step_names import ROOT, Word, chinese_verse, load_chapter, proper_nouns
except ImportError:
    from step_names import ROOT, Word, chinese_verse, load_chapter, proper_nouns


CHINESE_DIGITS = {
    "零": 0,
    "〇": 0,
    "一": 1,
    "二": 2,
    "兩": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
}
CHINESE_UNITS = {"十": 10, "百": 100, "千": 1000}
CHINESE_NUMERAL_CHARS = "零〇一二兩三四五六七八九十百千萬"


def chinese_number_to_int(value: str) -> int:
    """Convert a standard Chinese numeral, including sections joined by 萬."""
    total = section = current = 0
    for char in value:
        if char in CHINESE_DIGITS:
            current = CHINESE_DIGITS[char]
        elif char in CHINESE_UNITS:
            unit = CHINESE_UNITS[char]
            section += (current or 1) * unit
            current = 0
        elif char == "萬":
            section += current
            total += (section or 1) * 10000
            section = current = 0
        else:
            raise ValueError(f"不是支援的中文數字：{value}")
    return total + section + current


@dataclass(frozen=True)
class Passage:
    book: str
    chapter: int
    ranges: tuple[tuple[int, int], ...]

    def verses(self) -> list[int]:
        return [verse for start, end in self.ranges for verse in range(start, end + 1)]

    def display(self) -> str:
        return "、".join(f"{self.book}{self.chapter}:{start}–{end}" for start, end in self.ranges)


@dataclass(frozen=True)
class PairSpec:
    left: Passage
    right: Passage


@dataclass(frozen=True)
class GroupSpec:
    title: str
    pairs: tuple[PairSpec, ...]
    compare_family_counts: bool = False


@dataclass(frozen=True)
class NameRef:
    book: str
    chapter: int
    verse: int
    word: Word

    @property
    def reference(self) -> str:
        return f"{self.book}{self.chapter}:{self.verse}"


@dataclass(frozen=True)
class AlignedName:
    basic_strong: str
    left: NameRef | None
    right: NameRef | None
    status: str


@dataclass(frozen=True)
class FamilyCount:
    family: str
    book: str
    chapter: int
    verse: int
    count: int

    @property
    def reference(self) -> str:
        return f"{self.book}{self.chapter}:{self.verse}"


@dataclass(frozen=True)
class AlignedFamilyCount:
    left: FamilyCount | None
    right: FamilyCount | None
    status: str


def basic_strong(strong: str) -> str:
    return re.sub(r"(?<=[0-9])[A-Za-z]$", "", strong.strip())


def align_names(left: Sequence[NameRef], right: Sequence[NameRef]) -> list[AlignedName]:
    """Align occurrences by base Strong and retain extension-letter differences."""
    left_keys = [basic_strong(item.word.strong) for item in left]
    right_keys = [basic_strong(item.word.strong) for item in right]
    matcher = SequenceMatcher(a=left_keys, b=right_keys, autojunk=False)
    aligned: list[AlignedName] = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for offset in range(i2 - i1):
                a, b = left[i1 + offset], right[j1 + offset]
                status = "相同" if a.word.strong == b.word.strong else "擴充 Strong 不同"
                aligned.append(AlignedName(left_keys[i1 + offset], a, b, status))
        elif tag in ("delete", "replace"):
            aligned.extend(
                AlignedName(left_keys[index], left[index], None, "只在甲")
                for index in range(i1, i2)
            )
        if tag in ("insert", "replace"):
            aligned.extend(
                AlignedName(right_keys[index], None, right[index], "只在乙")
                for index in range(j1, j2)
            )
    return aligned


def _passage_names(passage: Passage) -> list[NameRef]:
    names: list[NameRef] = []
    for verse in passage.verses():
        names.extend(
            NameRef(passage.book, passage.chapter, verse, word)
            for word in proper_nouns(passage.book, passage.chapter, verse)
        )
    return names


def _escape_cell(value: str) -> str:
    return value.replace("|", r"\|").replace("\n", " ").replace("\r", " ")


def _name_cell(ref: NameRef | None) -> str:
    if ref is None:
        return ""
    return _escape_cell(f"{ref.word.translit}（{ref.word.gloss}）")


def _reference_cell(ref: NameRef | None) -> str:
    return ref.reference if ref else ""


def _passage_text(passage: Passage, role: str) -> list[str]:
    lines = [f"**{role}（{passage.display()}）**"]
    for verse in passage.verses():
        ref = f"{passage.book}{passage.chapter}:{verse}"
        text = chinese_verse(passage.book, passage.chapter, verse)
        if text is None:
            lines.append(f"- {ref}：**STEP／和合本節號無法對應，未猜測經文。**")
        else:
            lines.append(f"- {ref}：「{text}」")
    return lines


def _format_name_table(rows: Sequence[AlignedName]) -> list[str]:
    lines = [
        "| 基本 Strong | 甲方經節 | 甲方 translit（gloss）| 甲方擴充 Strong | 乙方經節 | 乙方 translit（gloss）| 乙方擴充 Strong | 狀況 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        left, right = row.left, row.right
        values = (
            row.basic_strong,
            _reference_cell(left),
            _name_cell(left),
            left.word.strong if left else "",
            _reference_cell(right),
            _name_cell(right),
            right.word.strong if right else "",
            row.status,
        )
        lines.append("| " + " | ".join(_escape_cell(value) for value in values) + " |")
    return lines


def _scripture_verse_count(book: str, chapter: int) -> int:
    folder_map = {
        "創": "創世記",
        "出": "出埃及記",
        "民": "民數記",
        "得": "路得記",
        "撒上": "撒母耳記上",
        "撒下": "撒母耳記下",
        "代上": "歷代志上",
        "代下": "歷代志下",
        "拉": "以斯拉記",
        "尼": "尼希米記",
        "太": "馬太福音",
        "路": "路加福音",
    }
    path = ROOT / "raw_scripture" / folder_map[book] / f"第{chapter}章.txt"
    if not path.is_file():
        return 0
    return sum(bool(line.strip()) for line in path.read_text(encoding="utf-8-sig").splitlines())


def verse_division_report(passages: Sequence[Passage]) -> list[str]:
    chapters = list(dict.fromkeys((p.book, p.chapter) for p in passages))
    report: list[str] = []
    for book, chapter in chapters:
        step_verses = set(load_chapter(book, chapter))
        scripture_count = _scripture_verse_count(book, chapter)
        scripture_verses = set(range(1, scripture_count + 1))
        step_only = sorted(step_verses - scripture_verses)
        scripture_only = sorted(scripture_verses - step_verses)
        if not step_only and not scripture_only:
            continue
        details = []
        if step_only:
            details.append("STEP 有、和合本無：" + "、".join(map(str, step_only)))
        if scripture_only:
            details.append("和合本有、STEP 無：" + "、".join(map(str, scripture_only)))
        report.append(
            f"- {book}{chapter}：STEP {len(step_verses)} 節、和合本 {scripture_count} 節；"
            + "；".join(details)
            + "。這些節號未作平移或猜配。"
        )
    return report


def _chinese_name_prefix(text: str, end: int) -> str:
    prefix = text[:end]
    start = max(prefix.rfind("；"), prefix.rfind("。"), prefix.rfind("："))
    previous_descendant = prefix.rfind("的子孫", start + 1)
    previous_separator = prefix.rfind("、", start + 1)
    if previous_descendant >= 0 and previous_separator > previous_descendant:
        start = previous_separator
    value = prefix[start + 1 :].strip(" ，、；：。")
    if value.startswith("就是"):
        value = value[2:]
    return value


def _family_names_in_verse(text: str) -> list[str]:
    names: list[str] = []
    for match in re.finditer(r"的子孫", text):
        if text[:match.start()].rstrip().endswith("他們"):
            continue
        name = _chinese_name_prefix(text, match.start())
        if name:
            names.append(name)
    return names


def family_counts(passage: Passage) -> list[FamilyCount]:
    """Read count-bearing descendant groups, carrying multi-verse lists to their total."""
    number_pattern = re.compile(rf"([{CHINESE_NUMERAL_CHARS}]+)名")
    pending: list[str] = []
    rows: list[FamilyCount] = []
    for verse in passage.verses():
        text = chinese_verse(passage.book, passage.chapter, verse)
        if text is None:
            continue
        names = _family_names_in_verse(text)
        number = number_pattern.search(text)
        if not number:
            if names and (pending or "：" in text or "所羅門僕人的後裔" in text):
                pending.extend(names)
            continue
        families = pending + names if names else pending
        pending = []
        if not families:
            continue
        rows.append(
            FamilyCount(
                family="、".join(families),
                book=passage.book,
                chapter=passage.chapter,
                verse=verse,
                count=chinese_number_to_int(number.group(1)),
            )
        )
    return rows

def align_family_counts(left: Sequence[FamilyCount], right: Sequence[FamilyCount]) -> list[AlignedFamilyCount]:
    matcher = SequenceMatcher(
        a=[item.family for item in left],
        b=[item.family for item in right],
        autojunk=False,
    )
    rows: list[AlignedFamilyCount] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for offset in range(i2 - i1):
                a, b = left[i1 + offset], right[j1 + offset]
                rows.append(
                    AlignedFamilyCount(a, b, "相同" if a.count == b.count else "人數不同")
                )
        elif tag in ("delete", "replace"):
            rows.extend(AlignedFamilyCount(left[index], None, "只在甲") for index in range(i1, i2))
        if tag in ("insert", "replace"):
            rows.extend(AlignedFamilyCount(None, right[index], "只在乙") for index in range(j1, j2))
    return rows


def _family_table(left: Passage, right: Passage) -> tuple[list[str], list[AlignedFamilyCount]]:
    rows = align_family_counts(family_counts(left), family_counts(right))
    lines = [
        "#### 拉 2 對尼 7 人數核對",
        "",
        "| 家族名（甲） | 甲方經節 | 甲方人數 | 家族名（乙） | 乙方經節 | 乙方人數 | 狀況 |",
        "|---|---|---:|---|---|---:|---|",
    ]
    for row in rows:
        a, b = row.left, row.right
        values = (
            a.family if a else "",
            a.reference if a else "",
            str(a.count) if a else "",
            b.family if b else "",
            b.reference if b else "",
            str(b.count) if b else "",
            row.status,
        )
        lines.append("| " + " | ".join(_escape_cell(value) for value in values) + " |")
    return lines, rows


def _stats(rows: Sequence[AlignedName]) -> dict[str, int]:
    return {status: sum(row.status == status for row in rows) for status in ("只在甲", "只在乙", "擴充 Strong 不同")}


def _passage(book: str, chapter: int, *ranges: tuple[int, int]) -> Passage:
    return Passage(book, chapter, tuple(ranges))


def _groups() -> list[GroupSpec]:
    chron1_1_4 = _passage("代上", 1, (1, 4))
    sam5 = _passage("撒下", 5, (14, 16))
    chron18 = _passage("代上", 18, (14, 17))
    return [
        GroupSpec(
            "代上1:1–4 對 創5:1–32",
            (PairSpec(chron1_1_4, _passage("創", 5, (1, 32))),),
        ),
        GroupSpec(
            "代上1:5–23 對 創10:1–32",
            (PairSpec(_passage("代上", 1, (5, 23)), _passage("創", 10, (1, 32))),),
        ),
        GroupSpec(
            "代上1:24–27 對 創11:10–26",
            (PairSpec(_passage("代上", 1, (24, 27)), _passage("創", 11, (10, 26))),),
        ),
        GroupSpec(
            "代上1:28–33 對 創25:1–4、創25:12–16",
            (PairSpec(_passage("代上", 1, (28, 33)), _passage("創", 25, (1, 4), (12, 16))),),
        ),
        GroupSpec(
            "代上1:34–54 對 創36:1–43",
            (PairSpec(_passage("代上", 1, (34, 54)), _passage("創", 36, (1, 43))),),
        ),
        GroupSpec(
            "撒下5:14–16 對 代上3:5–8、代上14:4–7",
            (
                PairSpec(sam5, _passage("代上", 3, (5, 8))),
                PairSpec(sam5, _passage("代上", 14, (4, 7))),
            ),
        ),
        GroupSpec(
            "拉2:1–70 對 尼7:6–73",
            (PairSpec(_passage("拉", 2, (1, 70)), _passage("尼", 7, (6, 73))),),
            compare_family_counts=True,
        ),
        GroupSpec(
            "代上18:14–17 對 撒下8:15–18、撒下20:23–26",
            (
                PairSpec(chron18, _passage("撒下", 8, (15, 18))),
                PairSpec(chron18, _passage("撒下", 20, (23, 26))),
            ),
        ),
    ]


def build_document() -> tuple[str, list[tuple[str, dict[str, int]]], list[str]]:
    groups = _groups()
    lines = [
        "# 平行名單逐名對照草稿",
        "",
        "依本機 STEP 人名的基本 Strong 編號對齊；擴充 Strong 字母保留在表中供人工辨認。每節和合本經文分列，節號不同的地方不作推測配對。",
        "",
    ]
    summary: list[tuple[str, dict[str, int]]] = []
    all_passages: list[Passage] = []

    for group in groups:
        lines.extend([f"## {group.title}", ""])
        for pair in group.pairs:
            all_passages.extend((pair.left, pair.right))
            rows = align_names(_passage_names(pair.left), _passage_names(pair.right))
            pair_title = f"{pair.left.display()} ↔ {pair.right.display()}"
            if len(group.pairs) > 1:
                lines.extend([f"### 逐名對照：{pair_title}", ""])
            else:
                lines.extend([f"### 逐名對照", ""])
            lines.extend(_format_name_table(rows))
            lines.append("")
            summary.append((pair_title, _stats(rows)))

            lines.extend(["### 和合本經文", ""])
            lines.extend(_passage_text(pair.left, "甲方"))
            lines.append("")
            lines.extend(_passage_text(pair.right, "乙方"))
            lines.append("")

            if group.compare_family_counts:
                table, _ = _family_table(pair.left, pair.right)
                lines.extend(table)
                lines.append("")

    mismatches = verse_division_report(all_passages)
    lines.extend(["## STEP 與和合本節數核對", ""])
    if mismatches:
        lines.extend(mismatches)
    else:
        lines.append("本次各參照章的 STEP 與和合本節號集合相同；沒有需要標出未對應的節號。")
    lines.append("")

    return "\n".join(lines), summary, mismatches


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    destination = ROOT / "appendix" / "genealogy" / "亞當到耶穌" / "對照草稿" / "平行名單.md"
    destination.parent.mkdir(parents=True, exist_ok=True)
    document, summary, mismatches = build_document()
    destination.write_text(document, encoding="utf-8")

    print(f"輸出：{destination.relative_to(ROOT)}")
    for pair_title, counts in summary:
        print(
            f"{pair_title}：只在甲 {counts['只在甲']}、只在乙 {counts['只在乙']}、"
            f"擴充 Strong 不同 {counts['擴充 Strong 不同']}"
        )
    if mismatches:
        print("STEP／和合本節數未對應：")
        for mismatch in mismatches:
            print(mismatch)
    else:
        print("STEP／和合本節數未對應：0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
