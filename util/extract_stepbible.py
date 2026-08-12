#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
extract_stepbible.py

Extract chapter / verse-range original-language data from STEPBible-Data
into agent-friendly Markdown or JSON.

Designed for:
  https://github.com/andyjr5566/Bible_wiki_zh

Data source:
  https://github.com/STEPBible/STEPBible-Data
  CC BY 4.0 — credit STEP Bible when using the data.

Examples (Windows PowerShell):

  # First run: download only the STEP files required for Genesis
  python .\extract_stepbible.py "創世記 1" `
    --data_path ".\.stepbible_data" `
    --output_path ".\raw_data" `
    --download

  # Extract only vv.1-8
  python .\extract_stepbible.py "Genesis 1:1-8" `
    --data_path ".\.stepbible_data" `
    --output_path ".\raw_data"

  # Daniel 3
  python .\extract_stepbible.py "Daniel 3" `
    --data_path ".\.stepbible_data" `
    --output_path ".\raw_data" `
    --download

  # JSON instead of Markdown
  python .\extract_stepbible.py "John 1:1-5" `
    --data_path ".\.stepbible_data" `
    --output_path ".\raw_data" `
    --download `
    --format json

Notes:
- This script does NOT scrape stepbible.org HTML.
- It reads the official tab-separated TAHOT/TAGNT datasets.
- Brief lexicon data comes from TBESH/TBESG.
- Morphology expansions come from TEHMC/TEGMC.
- Dictionary meanings are lexical ranges, not automatic contextual meanings.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import unicodedata
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Optional

try:
    from .book_paths import BOOKS as CANONICAL_BOOKS
except ImportError:
    from book_paths import BOOKS as CANONICAL_BOOKS


STEP_RAW_BASE = (
    "https://raw.githubusercontent.com/STEPBible/STEPBible-Data/master/"
)
DOWNLOAD_TIMEOUT_SECONDS = 60
DOWNLOAD_CHUNK_BYTES = 64 * 1024

# ---------------------------------------------------------------------------
# Bible book metadata
# ---------------------------------------------------------------------------

BOOKS = [
    # code, English canonical name, testament, aliases
    ("Gen", "Genesis", "OT", ["gen", "genesis", "創", "創世記"]),
    ("Exo", "Exodus", "OT", ["exo", "exod", "exodus", "出", "出埃及記"]),
    ("Lev", "Leviticus", "OT", ["lev", "leviticus", "利", "利未記"]),
    ("Num", "Numbers", "OT", ["num", "numbers", "民", "民數記"]),
    ("Deu", "Deuteronomy", "OT", ["deu", "deut", "deuteronomy", "申", "申命記"]),
    ("Jos", "Joshua", "OT", ["jos", "josh", "joshua", "書", "約書亞記"]),
    ("Jdg", "Judges", "OT", ["jdg", "judg", "judges", "士", "士師記"]),
    ("Rut", "Ruth", "OT", ["rut", "ruth", "得", "路得記"]),
    ("1Sa", "1 Samuel", "OT", ["1sa", "1 samuel", "撒上", "撒母耳記上"]),
    ("2Sa", "2 Samuel", "OT", ["2sa", "2 samuel", "撒下", "撒母耳記下"]),
    ("1Ki", "1 Kings", "OT", ["1ki", "1 kings", "王上", "列王紀上"]),
    ("2Ki", "2 Kings", "OT", ["2ki", "2 kings", "王下", "列王紀下"]),
    ("1Ch", "1 Chronicles", "OT", ["1ch", "1 chronicles", "代上", "歷代志上"]),
    ("2Ch", "2 Chronicles", "OT", ["2ch", "2 chronicles", "代下", "歷代志下"]),
    ("Ezr", "Ezra", "OT", ["ezr", "ezra", "拉", "以斯拉記"]),
    ("Neh", "Nehemiah", "OT", ["neh", "nehemiah", "尼", "尼希米記"]),
    ("Est", "Esther", "OT", ["est", "esther", "斯", "以斯帖記"]),
    ("Job", "Job", "OT", ["job", "伯", "約伯記"]),
    ("Psa", "Psalms", "OT", ["psa", "ps", "psalm", "psalms", "詩", "詩篇"]),
    ("Pro", "Proverbs", "OT", ["pro", "prov", "proverbs", "箴", "箴言"]),
    ("Ecc", "Ecclesiastes", "OT", ["ecc", "eccl", "ecclesiastes", "傳", "傳道書"]),
    ("Sng", "Song of Songs", "OT", ["sng", "song", "song of songs", "歌", "雅歌"]),
    ("Isa", "Isaiah", "OT", ["isa", "isaiah", "賽", "以賽亞書"]),
    ("Jer", "Jeremiah", "OT", ["jer", "jeremiah", "耶", "耶利米書"]),
    ("Lam", "Lamentations", "OT", ["lam", "lamentations", "哀", "耶利米哀歌"]),
    ("Ezk", "Ezekiel", "OT", ["ezk", "ezek", "ezekiel", "結", "以西結書"]),
    ("Dan", "Daniel", "OT", ["dan", "daniel", "但", "但以理書"]),
    ("Hos", "Hosea", "OT", ["hos", "hosea", "何", "何西阿書"]),
    ("Jol", "Joel", "OT", ["jol", "joel", "珥", "約珥書"]),
    ("Amo", "Amos", "OT", ["amo", "amos", "摩", "阿摩司書"]),
    ("Oba", "Obadiah", "OT", ["oba", "obad", "obadiah", "俄", "俄巴底亞書"]),
    ("Jon", "Jonah", "OT", ["jon", "jonah", "拿", "約拿書"]),
    ("Mic", "Micah", "OT", ["mic", "micah", "彌", "彌迦書"]),
    ("Nam", "Nahum", "OT", ["nam", "nah", "nahum", "鴻", "那鴻書"]),
    ("Hab", "Habakkuk", "OT", ["hab", "habakkuk", "哈", "哈巴谷書"]),
    ("Zep", "Zephaniah", "OT", ["zep", "zeph", "zephaniah", "番", "西番雅書"]),
    ("Hag", "Haggai", "OT", ["hag", "haggai", "該", "哈該書"]),
    ("Zec", "Zechariah", "OT", ["zec", "zech", "zechariah", "亞", "撒迦利亞書"]),
    ("Mal", "Malachi", "OT", ["mal", "malachi", "瑪", "瑪拉基書"]),
    ("Mat", "Matthew", "NT", ["mat", "matt", "matthew", "太", "馬太福音"]),
    ("Mrk", "Mark", "NT", ["mrk", "mark", "可", "馬可福音"]),
    ("Luk", "Luke", "NT", ["luk", "luke", "路", "路加福音"]),
    ("Jhn", "John", "NT", ["jhn", "john", "約", "約翰福音"]),
    ("Act", "Acts", "NT", ["act", "acts", "徒", "使徒行傳"]),
    ("Rom", "Romans", "NT", ["rom", "romans", "羅", "羅馬書"]),
    ("1Co", "1 Corinthians", "NT", ["1co", "1 corinthians", "林前", "哥林多前書"]),
    ("2Co", "2 Corinthians", "NT", ["2co", "2 corinthians", "林後", "哥林多後書"]),
    ("Gal", "Galatians", "NT", ["gal", "galatians", "加", "加拉太書"]),
    ("Eph", "Ephesians", "NT", ["eph", "ephesians", "弗", "以弗所書"]),
    ("Php", "Philippians", "NT", ["php", "phil", "philippians", "腓", "腓立比書"]),
    ("Col", "Colossians", "NT", ["col", "colossians", "西", "歌羅西書"]),
    ("1Th", "1 Thessalonians", "NT", ["1th", "1 thessalonians", "帖前", "帖撒羅尼迦前書"]),
    ("2Th", "2 Thessalonians", "NT", ["2th", "2 thessalonians", "帖後", "帖撒羅尼迦後書"]),
    ("1Ti", "1 Timothy", "NT", ["1ti", "1 timothy", "提前", "提摩太前書"]),
    ("2Ti", "2 Timothy", "NT", ["2ti", "2 timothy", "提後", "提摩太後書"]),
    ("Tit", "Titus", "NT", ["tit", "titus", "多", "提多書"]),
    ("Phm", "Philemon", "NT", ["phm", "philemon", "門", "腓利門書"]),
    ("Heb", "Hebrews", "NT", ["heb", "hebrews", "來", "希伯來書"]),
    ("Jas", "James", "NT", ["jas", "james", "雅", "雅各書"]),
    ("1Pe", "1 Peter", "NT", ["1pe", "1 peter", "彼前", "彼得前書"]),
    ("2Pe", "2 Peter", "NT", ["2pe", "2 peter", "彼後", "彼得後書"]),
    ("1Jn", "1 John", "NT", ["1jn", "1 john", "約一", "約翰一書"]),
    ("2Jn", "2 John", "NT", ["2jn", "2 john", "約二", "約翰二書"]),
    ("3Jn", "3 John", "NT", ["3jn", "3 john", "約三", "約翰三書"]),
    ("Jud", "Jude", "NT", ["jud", "jude", "猶", "猶大書"]),
    ("Rev", "Revelation", "NT", ["rev", "revelation", "啟", "啟示錄"]),
]

if len(BOOKS) != len(CANONICAL_BOOKS):
    raise RuntimeError(
        "STEP 書卷表與 _config/bible_books.json 數量不一致："
        f"{len(BOOKS)} != {len(CANONICAL_BOOKS)}"
    )

BOOK_BY_CODE = {}
BOOK_BY_CANONICAL_NAME = {}
ALIAS_TO_CODE = {}
for (code, en_name, testament, aliases), canonical_zh in zip(BOOKS, CANONICAL_BOOKS):
    BOOK_BY_CODE[code] = {
        "code": code,
        "name": en_name,
        "canonical_name": canonical_zh,
        "testament": testament,
    }
    BOOK_BY_CANONICAL_NAME[canonical_zh] = BOOK_BY_CODE[code]
    for alias in [code, en_name, canonical_zh, *aliases]:
        ALIAS_TO_CODE[alias.lower().replace(".", "").strip()] = code


OT_GROUPS = {
    "TAHOT Gen-Deu": {"Gen", "Exo", "Lev", "Num", "Deu"},
    "TAHOT Jos-Est": {
        "Jos", "Jdg", "Rut", "1Sa", "2Sa", "1Ki", "2Ki", "1Ch", "2Ch", "Ezr", "Neh", "Est"
    },
    "TAHOT Job-Sng": {"Job", "Psa", "Pro", "Ecc", "Sng"},
    "TAHOT Isa-Mal": {
        "Isa", "Jer", "Lam", "Ezk", "Dan", "Hos", "Jol", "Amo", "Oba",
        "Jon", "Mic", "Nam", "Hab", "Zep", "Hag", "Zec", "Mal"
    },
}

NT_GROUPS = {
    "TAGNT Mat-Jhn": {"Mat", "Mrk", "Luk", "Jhn"},
    "TAGNT Act-Rev": {
        "Act", "Rom", "1Co", "2Co", "Gal", "Eph", "Php", "Col",
        "1Th", "2Th", "1Ti", "2Ti", "Tit", "Phm", "Heb", "Jas",
        "1Pe", "2Pe", "1Jn", "2Jn", "3Jn", "Jud", "Rev"
    },
}

OFFICIAL_FILES = {
    "TAHOT Gen-Deu":
        "Translators Amalgamated OT+NT/"
        "TAHOT Gen-Deu - Translators Amalgamated Hebrew OT - STEPBible.org CC BY.txt",
    "TAHOT Jos-Est":
        "Translators Amalgamated OT+NT/"
        "TAHOT Jos-Est - Translators Amalgamated Hebrew OT - STEPBible.org CC BY.txt",
    "TAHOT Job-Sng":
        "Translators Amalgamated OT+NT/"
        "TAHOT Job-Sng - Translators Amalgamated Hebrew OT - STEPBible.org CC BY.txt",
    "TAHOT Isa-Mal":
        "Translators Amalgamated OT+NT/"
        "TAHOT Isa-Mal - Translators Amalgamated Hebrew OT - STEPBible.org CC BY.txt",
    "TAGNT Mat-Jhn":
        "Translators Amalgamated OT+NT/"
        "TAGNT Mat-Jhn - Translators Amalgamated Greek NT - STEPBible.org CC-BY.txt",
    "TAGNT Act-Rev":
        "Translators Amalgamated OT+NT/"
        "TAGNT Act-Rev - Translators Amalgamated Greek NT - STEPBible.org CC-BY.txt",
    "TBESH":
        "Lexicons/"
        "TBESH - Translators Brief lexicon of Extended Strongs for Hebrew - STEPBible.org CC BY.txt",
    "TBESG":
        "Lexicons/"
        "TBESG - Translators Brief lexicon of Extended Strongs for Greek - STEPBible.org CC BY.txt",
    "TEHMC":
        "Morphology codes/"
        "TEHMC - Translators Expansion of Hebrew Morphology Codes - STEPBible.org CC BY.txt",
    "TEGMC":
        "Morphology codes/"
        "TEGMC - Translators Expansion of Greek Morphhology Codes - STEPBible.org CC BY.txt",
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Reference:
    code: str
    chapter: int
    verse_start: Optional[int] = None
    verse_end: Optional[int] = None

    @property
    def book_name(self) -> str:
        return BOOK_BY_CODE[self.code]["name"]

    @property
    def testament(self) -> str:
        return BOOK_BY_CODE[self.code]["testament"]


@dataclass
class LexiconEntry:
    strong: str
    base_strong: str
    word: str = ""
    transliteration: str = ""
    pos: str = ""
    short_definition: str = ""
    full_definition: str = ""


@dataclass
class WordEntry:
    reference: str
    position: int
    word: str
    transliteration: str
    gloss: str
    strongs_raw: str
    strongs: list[str]
    main_strong: str
    morphology_raw: str
    morphology: str
    lexicon_word: str = ""
    lexicon_transliteration: str = ""
    lexicon_pos: str = ""
    lexicon_short: str = ""
    lexicon_full: str = ""


@dataclass
class StepDocument:
    """Structured form of one canonical rendered STEP TXT source."""

    reference: Reference
    verses: dict[int, list[WordEntry]]


class StepFormatError(ValueError):
    """Raised when a rendered STEP TXT file violates its formal format."""


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

STRONG_RE = re.compile(r"\b([GH])0*(\d{1,4})([A-Za-z]?)\b")
VERSE_REF_RE = re.compile(
    r"^(?P<book>[1-3]?[A-Za-z]{2,3})\.(?P<chapter>\d+)\.(?P<verse>\d+)"
    r"(?:(?:#|\.)(?P<word>\d+))?"
)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def normalize_strong(value: str) -> str:
    """Normalize H0430G -> H430G, G0026 -> G26, preserving suffix."""
    m = STRONG_RE.search(value.strip())
    if not m:
        return value.strip().strip("{}")
    return f"{m.group(1).upper()}{int(m.group(2))}{m.group(3).upper()}"


def base_strong(value: str) -> str:
    m = re.match(r"^([GH])(\d+)", normalize_strong(value), re.I)
    if not m:
        return normalize_strong(value)
    return f"{m.group(1).upper()}{int(m.group(2))}"


def extract_strongs(field: str) -> list[str]:
    found: list[str] = []
    for m in STRONG_RE.finditer(field or ""):
        s = f"{m.group(1).upper()}{int(m.group(2))}{m.group(3).upper()}"
        if s not in found:
            found.append(s)
    return found


def is_step_control_strong(value: str) -> bool:
    """
    STEP uses H90xx codes for prefixes, punctuation and section markers.
    They are useful as structural metadata but usually not the lexical headword.
    """
    s = base_strong(value)
    m = re.match(r"^H(\d+)$", s)
    return bool(m and 9000 <= int(m.group(1)) <= 9999)


def choose_main_strong(values: list[str]) -> str:
    # Prefer a normal lexical Strong over STEP H90xx structural/affix codes.
    for value in values:
        if not is_step_control_strong(value):
            return value
    return values[0] if values else ""


def clean_html(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<br\s*/?>", "; ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    return " ".join(text.split())


def clean_original_for_display(text: str) -> str:
    # Keep morpheme separators in per-word rows, but remove them in verse display.
    text = text.replace("/", "")
    text = text.replace("\\׃", "׃").replace("\\־", "־").replace("\\׀", "׀")
    return text


def safe_name(text: str) -> str:
    text = re.sub(r"[^\w\-]+", "_", text, flags=re.UNICODE)
    return text.strip("_").lower()


def stepbible_filename(
    book: str,
    chapter: int,
    verse_start: Optional[int] = None,
    verse_end: Optional[int] = None,
    *,
    extension: str = ".txt",
) -> str:
    """Return the canonical STEP extract filename used by CLI and manifest.

    ``book`` accepts the same Chinese/English/code aliases as ``parse_reference``.
    Full-chapter production files omit a verse suffix; ranges are deliberately
    separate debug/research artifacts and are never substituted for a chapter file.
    """
    chapter = int(chapter)
    if chapter < 1:
        raise ValueError("chapter 必須大於 0")
    if verse_start is not None:
        verse_start = int(verse_start)
        verse_end = int(verse_end if verse_end is not None else verse_start)
        if verse_start < 1 or verse_end < verse_start:
            raise ValueError("verse range 必須是正整數且終點不得小於起點")
    elif verse_end is not None:
        raise ValueError("verse_end 不能在 verse_start 缺省時單獨使用")

    ref = parse_reference(f"{book} {chapter}")
    suffix = f"_{verse_start}-{verse_end}" if verse_start is not None else ""
    ext = extension if extension.startswith(".") else f".{extension}"
    return f"stepbible_{safe_name(ref.book_name)}_{chapter}{suffix}{ext.lower()}"


def validate_book_contract() -> list[str]:
    """Return all canonical 66-book filenames, raising on mapping drift."""
    names = []
    for canonical_zh in CANONICAL_BOOKS:
        meta = BOOK_BY_CANONICAL_NAME.get(canonical_zh)
        if not meta:
            raise RuntimeError(f"STEP 書卷表缺少 canonical book：{canonical_zh}")
        parsed = parse_reference(f"{canonical_zh} 1")
        if parsed.code != meta["code"]:
            raise RuntimeError(f"STEP alias 對應錯誤：{canonical_zh}")
        names.append(stepbible_filename(canonical_zh, 1))
    if len(names) != 66 or len(set(names)) != 66:
        raise RuntimeError("STEP 66 卷檔名契約不完整或有重複")
    return names


# ---------------------------------------------------------------------------
# Reference parsing
# ---------------------------------------------------------------------------

def parse_reference(value: str) -> Reference:
    raw = value.strip()
    raw = raw.replace("：", ":").replace("－", "-").replace("–", "-").replace("—", "-")
    raw = re.sub(r"第\s*(\d+)\s*章", r" \1 ", raw)
    raw = re.sub(r"第\s*(\d+)\s*節", r":\1", raw)
    raw = re.sub(r"\s+", " ", raw).strip()
    raw = re.sub(r"\s*:\s*", ":", raw)
    raw = re.sub(r"\s*-\s*", "-", raw)

    # Find chapter / verses at the tail.
    m = re.search(r"(\d+)(?::(\d+)(?:-(\d+))?)?\s*$", raw)
    if not m:
        raise ValueError(
            f"無法解析章節：{value!r}。例：'創世記 1'、'Genesis 1:1-8'、'Daniel 3'"
        )

    chapter = int(m.group(1))
    v1 = int(m.group(2)) if m.group(2) else None
    v2 = int(m.group(3)) if m.group(3) else v1

    book_part = raw[:m.start()].strip()
    book_key = book_part.lower().replace(".", "").strip()

    # Exact alias first.
    code = ALIAS_TO_CODE.get(book_key)

    # Then tolerate spaces removed.
    if not code:
        compact = book_key.replace(" ", "")
        for alias, candidate in ALIAS_TO_CODE.items():
            if alias.replace(" ", "") == compact:
                code = candidate
                break

    if not code:
        raise ValueError(f"無法辨識書卷：{book_part!r}")

    return Reference(code=code, chapter=chapter, verse_start=v1, verse_end=v2)


def ref_matches(target: Reference, ref_text: str) -> tuple[bool, int, int]:
    """
    Supports current/known STEP-style refs such as:
      Gen.1.1#01=L
      Gen.1.1.1
      Gen.1.1
    Returns: (matches, verse, word_position)
    """
    base = ref_text.split("=")[0].strip()
    m = VERSE_REF_RE.match(base)
    if not m:
        return False, 0, 0

    if m.group("book") != target.code:
        return False, 0, 0
    if int(m.group("chapter")) != target.chapter:
        return False, 0, 0

    verse = int(m.group("verse"))
    if target.verse_start is not None and verse < target.verse_start:
        return False, verse, 0
    if target.verse_end is not None and verse > target.verse_end:
        return False, verse, 0

    position = int(m.group("word") or 0)
    return True, verse, position


# ---------------------------------------------------------------------------
# Locate / download official STEP files
# ---------------------------------------------------------------------------

def dataset_group_for(ref: Reference) -> str:
    groups = OT_GROUPS if ref.testament == "OT" else NT_GROUPS
    for group, codes in groups.items():
        if ref.code in codes:
            return group
    raise RuntimeError(f"No STEP dataset group for {ref.code}")


def find_dataset_file(data_path: Path, key: str) -> Optional[Path]:
    exact_rel = OFFICIAL_FILES[key]
    exact = data_path / Path(exact_rel)
    if exact.exists():
        return exact

    # Allow users to clone the repository with its official folder structure,
    # or place files flat in a custom directory.
    prefix = key
    candidates = sorted(data_path.rglob(f"{prefix}*.txt"))
    return candidates[0] if candidates else None


def download_official_file(data_path: Path, key: str) -> Path:
    rel = OFFICIAL_FILES[key]
    dest = data_path / Path(rel)
    dest.parent.mkdir(parents=True, exist_ok=True)

    if dest.exists():
        return dest

    encoded = "/".join(urllib.parse.quote(part) for part in rel.split("/"))
    url = STEP_RAW_BASE + encoded
    eprint(f"[download] {key}")
    eprint(f"           {url}")
    # Never stream directly into the canonical cache path: interruption used to
    # leave a truncated file that the next run accepted as complete. Download to
    # a sibling .part file, verify Content-Length when supplied, then atomically
    # replace the destination. Socket reads have an explicit timeout.
    part = dest.with_suffix(dest.suffix + ".part")
    part.unlink(missing_ok=True)
    downloaded = 0
    expected = None
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "Hermes-Scripture/1.0"})
        with urllib.request.urlopen(request, timeout=DOWNLOAD_TIMEOUT_SECONDS) as response:
            length = response.headers.get("Content-Length")
            expected = int(length) if length and length.isdigit() else None
            reader = getattr(response, "read1", response.read)
            with part.open("wb") as output:
                while True:
                    chunk = reader(DOWNLOAD_CHUNK_BYTES)
                    if not chunk:
                        break
                    output.write(chunk)
                    downloaded += len(chunk)
                    if downloaded % (1024 * 1024) < len(chunk):
                        suffix = f"/{expected}" if expected is not None else ""
                        eprint(f"[download] {key}: {downloaded}{suffix} bytes")
        if expected is not None and downloaded != expected:
            raise OSError(
                f"{key} 下載不完整：收到 {downloaded} bytes，預期 {expected} bytes"
            )
        if downloaded == 0:
            raise OSError(f"{key} 下載結果為空檔")
        part.replace(dest)
    except Exception:
        part.unlink(missing_ok=True)
        raise
    return dest


def ensure_required_files(
    ref: Reference,
    data_path: Path,
    allow_download: bool,
) -> tuple[Path, Optional[Path], Optional[Path]]:
    group_key = dataset_group_for(ref)
    lex_key = "TBESH" if ref.testament == "OT" else "TBESG"
    morph_key = "TEHMC" if ref.testament == "OT" else "TEGMC"

    result = []
    for key in (group_key, lex_key, morph_key):
        path = find_dataset_file(data_path, key)
        if not path and allow_download:
            try:
                path = download_official_file(data_path, key)
            except Exception as exc:
                eprint(f"[warning] 下載 {key} 失敗：{exc}")
        result.append(path)

    main_path, lex_path, morph_path = result
    if not main_path:
        raise FileNotFoundError(
            f"找不到 {group_key}。\n"
            f"請先 clone STEPBible-Data，或加上 --download。\n"
            f"data_path={data_path}"
        )

    if not lex_path:
        eprint(f"[warning] 找不到 {lex_key}，將只輸出詞形/Strong，不附字典。")
    if not morph_path:
        eprint(f"[warning] 找不到 {morph_key}，將保留 morphology code，不附展開說明。")

    return main_path, lex_path, morph_path


# ---------------------------------------------------------------------------
# Lexicon parsing
# ---------------------------------------------------------------------------

def parse_lexicon(path: Optional[Path], language: str) -> dict[str, LexiconEntry]:
    """
    TBESH / TBESG robust parser.

    Known layout:
      0 base Strong
      1 extended relation
      2 extended Strong/backref
      3 original
      4 transliteration
      5 POS
      6 short definition
      7+ full definition

    Current STEP files can contain extra TABs in definition fields. We keep the
    stable first 7 columns and join the remainder instead of requiring an exact
    column count.
    """
    if not path:
        return {}

    exact: dict[str, LexiconEntry] = {}
    base_default: dict[str, LexiconEntry] = {}

    with path.open("r", encoding="utf-8-sig", errors="replace") as f:
        for line in f:
            line = line.rstrip("\r\n")
            if not line or line.startswith("#") or line.startswith("$"):
                continue

            parts = line.split("\t")
            if len(parts) < 7:
                continue

            first = normalize_strong(parts[0])
            if not re.match(r"^[GH]\d+[A-Z]?$", first):
                continue

            rel = parts[1].strip() if len(parts) > 1 else ""
            backref = parts[2].strip() if len(parts) > 2 else ""
            original = parts[3].strip() if len(parts) > 3 else ""
            translit = parts[4].strip() if len(parts) > 4 else ""
            pos = parts[5].strip() if len(parts) > 5 else ""
            short_def = clean_html(parts[6].strip() if len(parts) > 6 else "")
            full_def = clean_html("\t".join(parts[7:]) if len(parts) > 7 else "")

            backref_ids = extract_strongs(backref)
            # Column 1 starts with this record's own Extended Strong, e.g.
            # ``H0430G = a Name of``. Column 2 contains relationship targets;
            # treating it as the primary key lets an earlier cross-reference
            # steal another record's definition.
            rel_ids = extract_strongs(rel)
            own_strong = rel_ids[0] if rel_ids else first

            entry = LexiconEntry(
                strong=own_strong,
                base_strong=base_strong(own_strong),
                word=original,
                transliteration=translit,
                pos=pos,
                short_definition=short_def,
                full_definition=full_def,
            )

            # The relation column's first ID is the authoritative record key.
            # Base IDs keep their first/default sense, while relationship IDs
            # are aliases that never overwrite an authoritative row.
            exact[own_strong] = entry
            exact.setdefault(first, entry)
            alias_keys = [*backref_ids, *rel_ids[1:]]
            for key in alias_keys:
                exact.setdefault(key, entry)

            # Base Strong may have several disambiguated senses.
            # Keep the first/default record rather than overwriting unpredictably.
            base_default.setdefault(base_strong(first), entry)

    merged = dict(base_default)
    merged.update(exact)
    return merged


# ---------------------------------------------------------------------------
# Morphology parsing
# ---------------------------------------------------------------------------

def parse_morphology_file(path: Optional[Path]) -> dict[str, str]:
    """
    Parse STEP TEHMC / TEGMC records.

    STEP records are separated by '$'. A typical full-code record starts:
      HVqp3ms<TAB>Function=Verb; ...
          Verb (Qal, Perfective, 3rd Masculine Singular)
          ...
    We keep the first human-readable subline as the display expansion.
    """
    if not path:
        return {}

    mapping: dict[str, str] = {}
    current_code: Optional[str] = None
    human_lines: list[str] = []

    def flush():
        nonlocal current_code, human_lines
        if current_code:
            readable = next((x for x in human_lines if x), "")
            if readable:
                mapping.setdefault(current_code, readable.strip().strip('"'))
        current_code = None
        human_lines = []

    with path.open("r", encoding="utf-8-sig", errors="replace") as f:
        for raw in f:
            line = raw.rstrip("\r\n")
            if line.strip() == "$":
                flush()
                continue

            if not line.strip():
                continue

            # A record header has a non-indented code in column 0.
            if not line.startswith("\t") and "\t" in line:
                first = line.split("\t", 1)[0].strip()
                # Avoid prose/header tables; morphology codes contain no spaces.
                if first and " " not in first and len(first) <= 24:
                    flush()
                    current_code = first
                    continue

            if current_code and line.startswith("\t"):
                human_lines.append(line.strip())

    flush()
    return mapping


def expand_hebrew_morph(raw: str, mapping: dict[str, str]) -> str:
    if not raw:
        return ""
    if raw in mapping:
        return mapping[raw]

    # Composite OSHB-like morphology: HR/Ncfsa -> HR + HNcfsa
    pieces = raw.split("/")
    expanded = []
    lang_prefix = pieces[0][0] if pieces and pieces[0] and pieces[0][0] in "HA" else "H"
    for i, piece in enumerate(pieces):
        if not piece:
            continue
        key = piece
        if i > 0 and not piece.startswith(("H", "A")):
            key = lang_prefix + piece
        expanded.append(mapping.get(key, key))

    return " + ".join(expanded)


def expand_greek_morph(raw: str, mapping: dict[str, str]) -> str:
    if not raw:
        return ""
    return mapping.get(raw, raw)


# ---------------------------------------------------------------------------
# Tagged-text parsing
# ---------------------------------------------------------------------------

def parse_tahot(
    path: Path,
    target: Reference,
    lexicon: dict[str, LexiconEntry],
    morph_map: dict[str, str],
) -> dict[int, list[WordEntry]]:
    verses: dict[int, list[WordEntry]] = {}

    with path.open("r", encoding="utf-8-sig", errors="replace") as f:
        for line in f:
            line = line.rstrip("\r\n")
            if not line or line.startswith("#"):
                continue

            parts = line.split("\t")
            if len(parts) < 4:
                continue

            matches, verse, position = ref_matches(target, parts[0].strip())
            if not matches:
                continue

            word = parts[1].strip() if len(parts) > 1 else ""
            transliteration = parts[2].strip() if len(parts) > 2 else ""
            gloss = parts[3].strip() if len(parts) > 3 else ""
            strong_field = parts[4].strip() if len(parts) > 4 else ""
            morph_raw = parts[5].strip() if len(parts) > 5 else ""

            # Some derived/older exports may contain source metadata where the
            # morphology field normally sits. Don't pretend it is morphology.
            if morph_raw in {"L", "Q", "K"}:
                morph_raw = ""

            strongs = extract_strongs(strong_field)
            main = choose_main_strong(strongs)
            lex = lexicon.get(main) or lexicon.get(base_strong(main))

            entry = WordEntry(
                reference=f"{target.code}.{target.chapter}.{verse}",
                position=position or (len(verses.get(verse, [])) + 1),
                word=word,
                transliteration=transliteration,
                gloss=gloss,
                strongs_raw=strong_field,
                strongs=strongs,
                main_strong=main,
                morphology_raw=morph_raw,
                morphology=expand_hebrew_morph(morph_raw, morph_map),
                lexicon_word=lex.word if lex else "",
                lexicon_transliteration=lex.transliteration if lex else "",
                lexicon_pos=lex.pos if lex else "",
                lexicon_short=lex.short_definition if lex else "",
                lexicon_full=lex.full_definition if lex else "",
            )
            verses.setdefault(verse, []).append(entry)

    return verses


def parse_tagnt(
    path: Path,
    target: Reference,
    lexicon: dict[str, LexiconEntry],
    morph_map: dict[str, str],
) -> dict[int, list[WordEntry]]:
    verses: dict[int, list[WordEntry]] = {}

    with path.open("r", encoding="utf-8-sig", errors="replace") as f:
        for line in f:
            line = line.rstrip("\r\n")
            if not line or line.startswith("#"):
                continue

            parts = line.split("\t")
            if len(parts) < 4:
                continue

            matches, verse, position = ref_matches(target, parts[0].strip())
            if not matches:
                continue

            # Current TAGNT:
            # 0 ref
            # 1 Greek + transliteration in parentheses
            # 2 contextual English
            # 3 dStrong=morphology
            # 4 dictionary=gloss
            # 5 editions
            greek_field = parts[1].strip()
            word = greek_field
            transliteration = ""
            m = re.match(r"^(.+?)\s*\(([^()]*)\)\s*$", greek_field)
            if m:
                word = m.group(1).strip()
                transliteration = m.group(2).strip()

            gloss = parts[2].strip() if len(parts) > 2 else ""
            sg_morph = parts[3].strip() if len(parts) > 3 else ""

            if "=" in sg_morph:
                strong_field, morph_raw = sg_morph.split("=", 1)
            else:
                strong_field, morph_raw = sg_morph, ""

            strongs = extract_strongs(strong_field)
            main = choose_main_strong(strongs)
            lex = lexicon.get(main) or lexicon.get(base_strong(main))

            entry = WordEntry(
                reference=f"{target.code}.{target.chapter}.{verse}",
                position=position or (len(verses.get(verse, [])) + 1),
                word=word.replace("¶", ""),
                transliteration=transliteration,
                gloss=gloss,
                strongs_raw=strong_field,
                strongs=strongs,
                main_strong=main,
                morphology_raw=morph_raw,
                morphology=expand_greek_morph(morph_raw, morph_map),
                lexicon_word=lex.word if lex else "",
                lexicon_transliteration=lex.transliteration if lex else "",
                lexicon_pos=lex.pos if lex else "",
                lexicon_short=lex.short_definition if lex else "",
                lexicon_full=lex.full_definition if lex else "",
            )
            verses.setdefault(verse, []).append(entry)

    return verses


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def verse_original(words: list[WordEntry]) -> str:
    return " ".join(clean_original_for_display(w.word) for w in words if w.word)


def markdown_escape_table(text: str) -> str:
    return (text or "").replace("|", r"\|").replace("\n", " ")


def render_markdown(
    ref: Reference,
    verses: dict[int, list[WordEntry]],
    include_full_definitions: bool,
) -> str:
    if ref.verse_start is None:
        ref_label = f"{ref.book_name} {ref.chapter}"
    elif ref.verse_start == ref.verse_end:
        ref_label = f"{ref.book_name} {ref.chapter}:{ref.verse_start}"
    else:
        ref_label = (
            f"{ref.book_name} {ref.chapter}:{ref.verse_start}-{ref.verse_end}"
        )

    out = [
        f"# STEP Bible — {ref_label}",
        "",
        "> Source: STEP Bible / STEPBible-Data — https://github.com/STEPBible/STEPBible-Data",
        "> License: CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/",
        "> 本檔是「原文證據層」資料，不是 Commentary。",
        "> Lexicon 列的是詞彙可能義域；不可直接把所有字典義都當成本節語境義。",
        "",
    ]

    for verse in sorted(verses):
        words = sorted(verses[verse], key=lambda x: x.position)
        out.extend([
            f"## {ref.book_name} {ref.chapter}:{verse}",
            "",
            f"**Original:** {verse_original(words)}",
            "",
            "| # | 原文 | Transliteration | Context gloss | Strong | Morphology | Brief lexicon |",
            "|---:|---|---|---|---|---|---|",
        ])

        for w in words:
            # Keep both the canonical compact code and its human-readable
            # expansion in the formal source.  Prompt projections can retain
            # the exact per-occurrence code without repeating the expansion
            # hundreds of times; on-demand/raw reads still expose both.
            if w.morphology_raw and w.morphology and w.morphology_raw != w.morphology:
                morph = f"{w.morphology_raw} — {w.morphology}"
            else:
                morph = w.morphology_raw or w.morphology
            lex = w.lexicon_short
            if w.lexicon_word and w.lexicon_word != clean_original_for_display(w.word):
                lex_head = w.lexicon_word
                if w.lexicon_transliteration:
                    lex_head += f" ({w.lexicon_transliteration})"
                if lex:
                    lex = f"{lex_head}: {lex}"
                else:
                    lex = lex_head

            out.append(
                "| {pos} | {word} | {tr} | {gloss} | {strong} | {morph} | {lex} |".format(
                    pos=w.position,
                    word=markdown_escape_table(w.word),
                    tr=markdown_escape_table(w.transliteration),
                    gloss=markdown_escape_table(w.gloss),
                    strong=markdown_escape_table(w.main_strong or w.strongs_raw),
                    morph=markdown_escape_table(morph),
                    lex=markdown_escape_table(lex),
                )
            )

        if include_full_definitions:
            detailed = [w for w in words if w.main_strong and w.lexicon_full]
            if detailed:
                out.extend(["", "### Lexicon details", ""])
                seen = set()
                for w in detailed:
                    if w.main_strong in seen:
                        continue
                    seen.add(w.main_strong)
                    head = w.lexicon_word or w.word
                    out.append(
                        f"- **{head} — {w.main_strong}**: {w.lexicon_full}"
                    )

        out.append("")

    if not verses:
        out.extend([
            "## No data matched",
            "",
            "請檢查書卷、章節、STEP 資料版本與 reference 格式。",
            "",
        ])

    return "\n".join(out).rstrip() + "\n"


_STEP_TITLE_RE = re.compile(r"^# STEP Bible\s+[—-]\s+(.+?)\s*$")
_STEP_VERSE_HEADING_RE = re.compile(r"^##\s+(.+?)\s+(\d+):(\d+)\s*$")
_STEP_TABLE_HEADER = (
    "#", "原文", "Transliteration", "Context gloss", "Strong",
    "Morphology", "Brief lexicon",
)


def _parse_markdown_table_row(line: str) -> list[str]:
    """Parse one renderer-owned Markdown row, preserving escaped separators.

    This is the inverse of :func:`markdown_escape_table`, not a general-purpose
    Markdown parser.  Keeping it beside the renderer gives the STEP TXT format
    one tested parser instead of ad-hoc ``split('|')`` consumers.
    """
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        raise StepFormatError(f"STEP table row 缺少首尾 |：{line[:80]}")
    body = stripped[1:-1]
    cells: list[str] = []
    current: list[str] = []
    index = 0
    while index < len(body):
        char = body[index]
        if char == "\\" and index + 1 < len(body) and body[index + 1] == "|":
            current.append("|")
            index += 2
            continue
        if char == "|":
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
        index += 1
    cells.append("".join(current).strip())
    return cells


def parse_rendered_markdown_text(text: str) -> StepDocument:
    """Parse the canonical ``render_markdown`` TXT representation.

    The rendered TXT is the formal chapter source kept in ``raw_data``.  Prompt
    projections and machine validation use this strict state-machine parser so
    they do not depend on the optional upstream dataset cache.
    """
    lines = text.splitlines()
    title_line = next((line.strip() for line in lines if line.strip()), "")
    title_match = _STEP_TITLE_RE.match(title_line)
    if not title_match:
        raise StepFormatError("STEP TXT 缺少合法的 '# STEP Bible — 書卷 章[:範圍]' 標題")
    try:
        reference = parse_reference(title_match.group(1))
    except ValueError as exc:
        raise StepFormatError(f"STEP TXT 標題 reference 無法解析：{exc}") from exc

    verses: dict[int, list[WordEntry]] = {}
    current_verse: Optional[int] = None
    expecting_separator = False
    in_word_table = False
    seen_headings: set[int] = set()

    for line_number, raw_line in enumerate(lines, 1):
        line = raw_line.strip()
        heading = _STEP_VERSE_HEADING_RE.match(line)
        if heading:
            try:
                heading_ref = parse_reference(
                    f"{heading.group(1)} {heading.group(2)}:{heading.group(3)}"
                )
            except ValueError as exc:
                raise StepFormatError(
                    f"第 {line_number} 行 verse heading 無法解析：{exc}"
                ) from exc
            if (heading_ref.code != reference.code
                    or heading_ref.chapter != reference.chapter):
                raise StepFormatError(
                    f"第 {line_number} 行 verse heading 與標題書卷／章不一致"
                )
            current_verse = int(heading.group(3))
            if current_verse in seen_headings:
                raise StepFormatError(f"重複 verse heading：{current_verse}")
            seen_headings.add(current_verse)
            verses[current_verse] = []
            expecting_separator = False
            in_word_table = False
            continue

        if current_verse is None:
            continue
        if line.startswith("| # |"):
            cells = tuple(_parse_markdown_table_row(line))
            if cells != _STEP_TABLE_HEADER:
                raise StepFormatError(
                    f"第 {line_number} 行 STEP 欄位不符 canonical schema：{cells}"
                )
            expecting_separator = True
            in_word_table = False
            continue
        if expecting_separator:
            separator = _parse_markdown_table_row(line)
            if len(separator) != len(_STEP_TABLE_HEADER) or not all(
                    re.fullmatch(r":?-{3,}:?", cell) for cell in separator):
                raise StepFormatError(f"第 {line_number} 行 STEP table separator 不合法")
            expecting_separator = False
            in_word_table = True
            continue
        if not in_word_table or not line.startswith("|"):
            continue

        cells = _parse_markdown_table_row(line)
        if len(cells) != len(_STEP_TABLE_HEADER):
            raise StepFormatError(
                f"第 {line_number} 行 STEP word row 欄數應為 7，實際 {len(cells)}"
            )
        try:
            position = int(cells[0])
        except ValueError as exc:
            raise StepFormatError(
                f"第 {line_number} 行 STEP word position 不是整數：{cells[0]}"
            ) from exc
        strongs = extract_strongs(cells[4])
        main_strong = choose_main_strong(strongs)
        morphology_cell = cells[5]
        if " — " in morphology_cell:
            morphology_raw, morphology = morphology_cell.split(" — ", 1)
        else:
            # Phase-1 formal files stored only the expanded value.  Preserve
            # compatibility: it remains a valid exact morphology value even
            # though it is less compact in projections than a native code.
            morphology_raw = morphology = morphology_cell
        verses[current_verse].append(WordEntry(
            reference=f"{reference.code}.{reference.chapter}.{current_verse}",
            position=position,
            word=cells[1],
            transliteration=cells[2],
            gloss=cells[3],
            strongs_raw=cells[4],
            strongs=strongs,
            main_strong=main_strong,
            morphology_raw=morphology_raw,
            morphology=morphology,
            lexicon_short=cells[6],
        ))

    if not verses:
        raise StepFormatError("STEP TXT 沒有任何合法 verse heading")
    if expecting_separator:
        raise StepFormatError("STEP TXT table header 後缺少 separator row")
    empty = [verse for verse, words in verses.items() if not words]
    if empty:
        raise StepFormatError(f"STEP TXT verse heading 沒有 word rows：{empty}")
    return StepDocument(reference=reference, verses=verses)


def parse_rendered_markdown(path: Path | str) -> StepDocument:
    """Read and parse one canonical STEP TXT file from disk."""
    path = Path(path)
    return parse_rendered_markdown_text(
        path.read_text(encoding="utf-8-sig", errors="strict")
    )


def render_json(
    ref: Reference,
    verses: dict[int, list[WordEntry]],
) -> str:
    payload = {
        "source": "STEP Bible / STEPBible-Data",
        "source_url": "https://github.com/STEPBible/STEPBible-Data",
        "license": "CC BY 4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "book_code": ref.code,
        "book": ref.book_name,
        "chapter": ref.chapter,
        "verse_start": ref.verse_start,
        "verse_end": ref.verse_end,
        "warning": (
            "Lexicon meanings are lexical ranges, not automatic contextual meanings."
        ),
        "verses": [
            {
                "verse": verse,
                "original": verse_original(sorted(words, key=lambda x: x.position)),
                "words": [
                    asdict(w)
                    for w in sorted(words, key=lambda x: x.position)
                ],
            }
            for verse, words in sorted(verses.items())
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Extract STEPBible original-language data by Bible reference."
    )
    p.add_argument(
        "reference",
        help="e.g. '創世記 1', 'Genesis 1:1-8', 'Daniel 3', 'John 1:1-5'",
    )
    p.add_argument(
        "--data_path",
        default=".stepbible_data",
        help="Local STEPBible-Data directory (default: .stepbible_data)",
    )
    p.add_argument(
        "--output_path",
        default="raw_data",
        help="Output directory (default: raw_data)",
    )
    p.add_argument(
        "--output_filename",
        default=None,
        help="Optional output filename without extension",
    )
    p.add_argument(
        "--download",
        action="store_true",
        help="Download only required official STEP files if missing",
    )
    p.add_argument(
        "--format",
        choices=("txt", "md", "json"),
        default="txt",
        help="Output format (default: txt; fits this repo's raw_data/source_manifest flow)",
    )
    p.add_argument(
        "--full-definitions",
        action="store_true",
        help="Include long lexicon definitions (larger token cost)",
    )
    return p


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")
    args = build_arg_parser().parse_args()

    try:
        ref = parse_reference(args.reference)
    except ValueError as exc:
        eprint(f"[error] {exc}")
        return 2

    data_path = Path(args.data_path)
    output_path = Path(args.output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    try:
        text_path, lex_path, morph_path = ensure_required_files(
            ref=ref,
            data_path=data_path,
            allow_download=args.download,
        )
    except Exception as exc:
        eprint(f"[error] {exc}")
        return 3

    language = "hebrew" if ref.testament == "OT" else "greek"
    eprint(f"[STEP] reference : {ref.book_name} {ref.chapter}")
    eprint(f"[STEP] tagged    : {text_path}")
    eprint(f"[STEP] lexicon   : {lex_path or '(missing)'}")
    eprint(f"[STEP] morphology: {morph_path or '(missing)'}")

    lexicon = parse_lexicon(lex_path, language)
    morph_map = parse_morphology_file(morph_path)

    if ref.testament == "OT":
        verses = parse_tahot(text_path, ref, lexicon, morph_map)
    else:
        verses = parse_tagnt(text_path, ref, lexicon, morph_map)

    if not verses:
        eprint(
            "[error] 指定範圍沒有匹配任何 STEP 詞資料；"
            "未寫出空的正式來源檔。請檢查 reference 與資料版本。"
        )
        return 4

    if args.format == "json":
        content = render_json(ref, verses)
        extension = ".json"
    else:
        content = render_markdown(
            ref, verses, include_full_definitions=args.full_definitions
        )
        extension = ".txt" if args.format == "txt" else ".md"

    if args.output_filename:
        stem = args.output_filename
        filename = f"{stem}{extension}"
    else:
        filename = stepbible_filename(
            ref.code,
            ref.chapter,
            ref.verse_start,
            ref.verse_end,
            extension=extension,
        )

    out_file = output_path / filename
    out_file.write_text(content, encoding="utf-8")

    word_count = sum(len(words) for words in verses.values())
    eprint(
        f"[done] verses={len(verses)} words={word_count} output={out_file}"
    )
    print(out_file)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
