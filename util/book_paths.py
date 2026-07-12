#!/usr/bin/env python3
"""Resolve canonical Bible book names to ordered vault folder names."""

from __future__ import annotations

import json
import re
from pathlib import Path


UTIL_DIR = Path(__file__).resolve().parent
ROOT = UTIL_DIR.parent
BOOKS_FILE = ROOT / "_config" / "bible_books.json"
BOOKS = tuple(json.loads(BOOKS_FILE.read_text(encoding="utf-8")))
BOOK_NUMBERS = {book: index for index, book in enumerate(BOOKS, 1)}
ORDERED_BOOK_RE = re.compile(r"^(?P<number>\d{2})\s+(?P<book>.+)$")


def ordered_book_dir_name(book: str) -> str:
    """Return the canonical ordered folder name, e.g. ``01 創世記``."""
    try:
        number = BOOK_NUMBERS[book]
    except KeyError as exc:
        raise ValueError(f"未知書卷：{book}") from exc
    return f"{number:02d} {book}"


def canonical_book_name(folder_or_book: str) -> str:
    """Strip a valid canonical numeric prefix while preserving plain book names."""
    value = str(folder_or_book).strip()
    match = ORDERED_BOOK_RE.fullmatch(value)
    if not match:
        return value
    book = match.group("book")
    expected = BOOK_NUMBERS.get(book)
    if expected != int(match.group("number")):
        return value
    return book


def chapter_link(book: str, chapter) -> str:
    """Wikilink from an accumulation heading to its chapter note.

    Returns e.g. ``[[01 創世記/第1章|第1章]]`` so the ``#### 第N章`` heading
    resolves to the ordered book folder. Falls back to a plain ``第N章`` label
    when *book* is not a known canonical book, so callers never emit a broken
    ordered-folder prefix.
    """
    label = f"第{chapter}章"
    canonical = canonical_book_name(book)
    try:
        dir_name = ordered_book_dir_name(canonical)
    except ValueError:
        return label
    return f"[[{dir_name}/{label}|{label}]]"


def book_directory(root: Path, book: str) -> Path:
    """Resolve an existing ordered/legacy folder, preferring the ordered form."""
    root = Path(root)
    canonical = canonical_book_name(book)
    ordered = root / ordered_book_dir_name(canonical)
    if ordered.exists():
        return ordered
    legacy = root / canonical
    if legacy.exists():
        return legacy
    return ordered


def existing_book_directories(root: Path):
    """Yield ``(canonical book name, directory)`` in canonical order."""
    for book in BOOKS:
        directory = book_directory(root, book)
        if directory.is_dir():
            yield book, directory
