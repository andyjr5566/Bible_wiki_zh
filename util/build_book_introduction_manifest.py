#!/usr/bin/env python3
"""Build a canonical source_manifest.yaml for one book Introduction.

The four existing commentary families are generated from
``_config/source_catalog.json``.  External enrichment sources are explicit
per-book overrides in ``_config/book_introduction_sources.yaml`` so the agent
never guesses BibleProject / Enter the Bible / Yale URLs.

Examples:

    python util/build_book_introduction_manifest.py 創世記 --print
    python util/build_book_introduction_manifest.py 創世記 --write
    python util/build_book_introduction_manifest.py 創世記 --write --force
"""

import sys
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "_config" / "source_catalog.json"
EXTERNAL_PATH = ROOT / "_config" / "book_introduction_sources.yaml"


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: root must be an object")
    return data


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: root must be a mapping")
    return data


def _canonical_book_name(book: str) -> str:
    try:
        from . import book_paths
    except ImportError:
        import book_paths
    return book_paths.canonical_book_name(book)


def _catalog_entries() -> dict[str, dict[str, Any]]:
    raw = _load_json(CATALOG_PATH)
    result: dict[str, dict[str, Any]] = {}
    for key, value in raw.items():
        if key.startswith("_"):
            continue
        if not isinstance(value, dict):
            raise ValueError(f"{CATALOG_PATH}: {key!r} must be an object")
        result[key] = value
    return result


def _match_book(book: str) -> tuple[str, dict[str, Any]]:
    canonical = _canonical_book_name(book)
    for key, meta in _catalog_entries().items():
        if key == book or _canonical_book_name(key) == canonical:
            return key, meta
    raise KeyError(
        f"_config/source_catalog.json 沒有「{book}」；"
        "請先把書卷加入共同 registry，再建立 Introduction manifest。"
    )


def _testament_for_key(book_key: str) -> str:
    try:
        number = int(book_key.split(" ", 1)[0])
    except (ValueError, IndexError) as exc:
        raise ValueError(f"cannot derive canonical book number from {book_key!r}") from exc
    return "Old%20Testament" if number <= 39 else "New%20Testament"


def _external_for(book_key: str) -> dict[str, Any]:
    config = _load_yaml(EXTERNAL_PATH)
    books = config.get("books") or {}
    if not isinstance(books, dict):
        raise ValueError(f"{EXTERNAL_PATH}: books must be a mapping")
    value = books.get(book_key) or {}
    if not isinstance(value, dict):
        raise ValueError(f"{EXTERNAL_PATH}: books.{book_key} must be a mapping")
    return value


def build_manifest(book: str) -> dict[str, Any]:
    book_key, meta = _match_book(book)
    cc_folder = str(meta.get("cc_folder", "")).strip()
    kc = str(meta.get("kc", "")).strip()
    en = str(meta.get("en", "")).strip()
    if not cc_folder or not kc or not en:
        raise ValueError(
            f"{CATALOG_PATH}: {book_key!r} requires cc_folder, kc and en"
        )

    num = "".join(ch for ch in cc_folder if ch.isdigit())
    if not num:
        raise ValueError(f"cannot derive CCBibleStudy number from {cc_folder!r}")
    testament = _testament_for_key(book_key)
    cc_base = f"https://www.ccbiblestudy.org/{testament}/{cc_folder}"

    sources: dict[str, Any] = {
        "CT00": {
            "family": "ccbiblestudy",
            "role": "commentary",
            "editorial_anchor": True,
            "label": f"CCBibleStudy {book_key.split(' ', 1)[-1]}提要（CT00）",
            "url": f"{cc_base}/{num}CT00.htm",
        },
        "GT00": {
            "family": "ccbiblestudy",
            "role": "commentary",
            "label": f"CCBibleStudy {book_key.split(' ', 1)[-1]}導論拾穗（GT00）",
            "url": f"{cc_base}/{num}GT00.htm",
            "provenance_rule": (
                "GT00 是多來源合輯；萃取時必須保留內部分來源名稱，"
                "不得把單一子來源寫成 GT00 全體結論。"
            ),
        },
        "KC0": {
            "family": "kingcomments",
            "role": "commentary",
            "label": f"KingComments {en} Introduction",
            "url": f"https://www.kingcomments.com/en/bible-studies/{kc}/0",
        },
        "BH": {
            "family": "biblehub",
            "role": "commentary",
            "label": f"BibleHub {en} overview",
            "url": f"https://biblehub.com/{en}/",
            "family_rule": (
                "BibleHub 內部即使引用多個底層資源，仍只算一個 BH 來源維度。"
            ),
        },
    }

    external = _external_for(book_key)
    for source_id, spec in external.items():
        if not isinstance(spec, dict):
            raise ValueError(
                f"{EXTERNAL_PATH}: {book_key}.{source_id} must be a mapping"
            )
        item = dict(spec)
        item.setdefault("family", source_id.lower())
        if not item.get("role"):
            raise ValueError(
                f"{EXTERNAL_PATH}: {book_key}.{source_id}.role is required"
            )
        if not item.get("url") and not item.get("urls"):
            raise ValueError(
                f"{EXTERNAL_PATH}: {book_key}.{source_id} requires url or urls"
            )
        sources[str(source_id)] = item

    return {
        "book": _canonical_book_name(book_key),
        "book_folder": book_key,
        "principles": {
            "editorial_anchor": "CT00",
            "commentary_vote_sources": ["CT00", "GT00", "KC0", "BH"],
            "external_context_sources": list(external.keys()),
            "note": (
                "CT00 提供 Introduction 的 editorial rhythm；CT00、GT00、KC0、BH "
                "才是四套 commentary 維度。外部來源只補強文學、背景與學術研究，"
                "不加入四家票數。"
            ),
        },
        "sources": sources,
    }


def _output_path(book_key: str) -> Path:
    canonical = _canonical_book_name(book_key)
    return ROOT / "raw_data" / "book_intro" / canonical / "source_manifest.yaml"


def main() -> int:
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8")  # Windows cp1252 保險絲
    parser = argparse.ArgumentParser(
        description="Build a book-level Introduction source manifest"
    )
    parser.add_argument("book")
    parser.add_argument("--print", action="store_true", dest="print_only")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if not args.print_only and not args.write:
        parser.error("choose --print or --write")

    book_key, _ = _match_book(args.book)
    manifest = build_manifest(args.book)
    text = yaml.safe_dump(
        manifest,
        allow_unicode=True,
        sort_keys=False,
        width=100,
    )

    if args.print_only:
        print(text, end="")

    if args.write:
        output = _output_path(book_key)
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.exists() and not args.force:
            raise FileExistsError(f"{output} exists; use --force to replace")
        output.write_text(text, encoding="utf-8", newline="\n")
        print(f"✅ 已寫入：{output.relative_to(ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
