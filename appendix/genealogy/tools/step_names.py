"""Read proper names from the project's local STEP Bible chapter files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Literal


Kind = Literal["person_m", "person_f", "person", "place", "people", "title", "other"]
PERSON_KINDS: tuple[Kind, ...] = ("person_m", "person_f", "person")

BOOK_SLUGS = {
    "創": "genesis",
    "出": "exodus",
    "民": "numbers",
    "得": "ruth",
    "撒上": "1_samuel",
    "撒下": "2_samuel",
    "代上": "1_chronicles",
    "代下": "2_chronicles",
    "拉": "ezra",
    "尼": "nehemiah",
    "太": "matthew",
    "路": "luke",
}

BOOK_SCRIPTURE_FOLDERS = {
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

ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Word:
    index: int
    original: str
    translit: str
    gloss: str
    strong: str
    morph: str
    kind: Kind


def _morph_code(morph: str) -> str:
    return re.split(r"\s+—\s+", morph.strip(), maxsplit=1)[0].strip()


def _hebrew_kind(code: str) -> Kind | None:
    """Hebrew and Aramaic STEP codes use HNpm/HNpl and compound H*/A*/N* forms."""
    for part in code.split("/"):
        token = part.strip()
        if token.startswith(("H", "A")):
            token = token[1:]
        if not token.startswith("Np"):
            continue
        suffix = token[2:3]
        return {
            "m": "person_m",
            "f": "person_f",
            "l": "place",
            "g": "people",
            "t": "title",
            "": "person",
        }.get(suffix, "person")
    return None


def _greek_kind(code: str) -> Kind | None:
    """Classify Greek STEP proper nouns from the observed morphology suffixes.

    Matthew 1 and Luke 3 use N-...-P for people, -L (including -LG) for
    locations, and -T for titles. Gender is encoded in forms such as GSM/GSF.
    N-PRI is an indeclinable proper noun without a subtype, so keep it generic.
    """
    if not code.startswith("N-"):
        return None
    parts = code.split("-")
    if any(part.startswith("L") for part in parts[1:]):
        return "place"
    if "T" in parts:
        return "title"
    if "P" in parts or code == "N-PRI":
        gender_match = next(
            (re.fullmatch(r"[NGDAV][SP]([MFN])", part) for part in parts[1:]
             if re.fullmatch(r"[NGDAV][SP][MFN]", part)),
            None,
        )
        gender = gender_match.group(1) if gender_match else ""
        if gender == "M":
            return "person_m"
        if gender == "F":
            return "person_f"
        return "person"
    return None


def classify_kind(morph: str) -> Kind:
    code = _morph_code(morph)
    return _hebrew_kind(code) or _greek_kind(code) or "other"


def _step_path(book_abbr: str, chapter: int) -> Path:
    try:
        slug = BOOK_SLUGS[book_abbr]
    except KeyError as exc:
        raise ValueError(f"不支援的書卷簡稱：{book_abbr}") from exc
    return ROOT / "raw_data" / f"stepbible_{slug}_{chapter}.txt"


@lru_cache(maxsize=64)
def load_chapter(book_abbr: str, chapter: int) -> dict[int, list[Word]]:
    """Return STEP words grouped by verse, preserving table order."""
    path = _step_path(book_abbr, chapter)
    text = path.read_text(encoding="utf-8-sig")
    result: dict[int, list[Word]] = {}
    active_verse: int | None = None

    for line in text.splitlines():
        heading = re.match(r"^##\s+.+?\s+(\d+):(\d+)\s*$", line.strip())
        if heading:
            active_verse = int(heading.group(2))
            result.setdefault(active_verse, [])
            continue
        if active_verse is None or not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 7 or not cells[0].isdigit():
            continue
        index = int(cells[0])
        original, translit, gloss, strong, morph = cells[1:6]
        result[active_verse].append(
            Word(
                index=index,
                original=original,
                translit=translit,
                gloss=gloss,
                strong=strong,
                morph=morph,
                kind=classify_kind(morph),
            )
        )
    return result


def proper_nouns(
    book_abbr: str,
    chapter: int,
    verse: int,
    kinds: tuple[Kind, ...] = PERSON_KINDS,
) -> list[Word]:
    return [word for word in load_chapter(book_abbr, chapter).get(verse, []) if word.kind in kinds]


def chinese_verse(book_abbr: str, chapter: int, verse: int) -> str | None:
    try:
        folder = BOOK_SCRIPTURE_FOLDERS[book_abbr]
    except KeyError as exc:
        raise ValueError(f"不支援的書卷簡稱：{book_abbr}") from exc
    path = ROOT / "raw_scripture" / folder / f"第{chapter}章.txt"
    if not path.is_file():
        return None
    lines = [line.strip() for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    if verse < 1 or verse > len(lines):
        return None
    return lines[verse - 1]


def _reading_verses(data: dict) -> list[tuple[str, int, int, dict]]:
    entries: list[tuple[str, int, int, dict]] = []
    if isinstance(data.get("segments"), list):
        for segment in data["segments"]:
            for chapter in segment.get("chapters", []):
                book = chapter.get("book", segment.get("book"))
                if not book:
                    continue
                for verse in chapter.get("verses", []):
                    entries.append((book, int(chapter["n"]), int(verse["v"]), verse))
        return entries

    book = data.get("book")
    if book:
        for chapter in data.get("chapters", []):
            for verse in chapter.get("verses", []):
                verse_number = verse.get("v", verse.get("n"))
                if verse_number is not None:
                    entries.append((book, int(chapter["n"]), int(verse_number), verse))
    return entries


def audit_rows(reading_path: Path) -> list[str]:
    reading = json.loads(reading_path.read_text(encoding="utf-8-sig"))
    mismatches: list[str] = []
    step_total = marker_total = 0
    for book, chapter, verse, row in _reading_verses(reading):
        names = proper_nouns(book, chapter, verse)
        markers = [token for token in row.get("t", []) if token.get("k") == "p"]
        step_total += len(names)
        marker_total += len(markers)
        if len(names) == len(markers):
            continue
        text = str(row.get("text", ""))
        step_names = ", ".join(f"{word.translit}|{word.gloss}|{word.strong}" for word in names)
        marked_names = []
        for marker in markers:
            try:
                start, end = int(marker["s"]), int(marker["e"])
            except (KeyError, TypeError, ValueError):
                continue
            marked_names.append(text[start:end])
        reference = f"{book}{chapter}:{verse}"
        fields = (reference, str(len(names)), str(len(markers)), step_names, ", ".join(marked_names))
        mismatches.append("\t".join(value.replace("\t", " ").replace("\n", " ") for value in fields))
    mismatches.append(f"總計\t{step_total}\t{marker_total}\t\t")
    return ["經節\tSTEP人名數\t標記數\tSTEP人名（translit|gloss|strong）\t標記的中文字", *mismatches]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="從本機 STEP Bible 原文檔辨識人名並核對標記數")
    commands = parser.add_subparsers(dest="command", required=True)
    audit = commands.add_parser("audit", help="比較 reading JSON 內的人名標記與 STEP 人名數")
    audit.add_argument("--reading", required=True, type=Path)
    audit.add_argument("--out", type=Path)
    args = parser.parse_args(argv)

    if args.command == "audit":
        output = "\n".join(audit_rows(args.reading)) + "\n"
        if args.out:
            args.out.write_text(output, encoding="utf-8")
        else:
            sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
