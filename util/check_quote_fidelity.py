#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""引號字串與交叉引註回查。

本工具做 deterministic 的字串比對，只負責找出「引號內文字在正式來源語料中沒有逐字命中」
的疑點。它不能判斷該段文字究竟是直接引文、跨語言翻譯、具名轉述，或一般中文修辭；
因此引號字串 miss 預設只回報給 Evidence Reviewer，不自動判 production 內容錯誤。

判定原則：
  - 語料只放**本章** manifest 宣告為 OK 的 commentary＋全本本地經文。相鄰章 commentary
    不算，避免把異章污染洗掉。
  - 正規化：NFKC、彎引號轉直引號、去掉引號／空白／markdown 強調，wiki-link 還原顯示字。
  - 引句含 ⋯／… 時視為節錄，拆開後逐段回查。
  - 少於預設門檻或含頓線的引號內容不查；可用 --min-chars 調整掃描敏感度。
  - --strict 只適合呼叫端已經確定「待驗內容必須逐字命中」的情境；一般 production gate
    不應以 strict 模式推斷引號的語義角色。

條目模式（--entry）以該條目實際累積過的章節來源作 commentary 語料。
本工具只出報告，不改檔；命中不代表 attribution 正確，miss 也不等於內容錯誤。
"""
from __future__ import annotations

import argparse
import glob
import re
import sys
import unicodedata
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from util import console  # noqa: E402
from util.book_paths import book_directory, canonical_book_name  # noqa: E402
from util.source_excerpts import parse_manifest  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

MIN_QUOTE_CHARS = 10
MIN_FRAGMENT_CHARS = 5
QUOTE_PATTERNS = (
    re.compile(r"「((?:[^「」]|『[^『』]*』)+?)」"),
    re.compile(r"『([^『』]+?)』"),
)
ELLIPSIS_RE = re.compile(r"[⋯…]+")
WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
MARKDOWN_EMPHASIS_RE = re.compile(r"\*+|=={2,}|==")
CHAPTER_ORGANIZATION_HEADING = "## 本章整理"

_CN_DIGITS = "一二三四五六七八九"


def _strip_wikilinks(text: str) -> str:
    return WIKILINK_RE.sub(lambda m: m.group(2) or m.group(1), text)


def normalize(text) -> str:
    text = unicodedata.normalize("NFKC", str(text))
    text = _strip_wikilinks(text)
    for src, dst in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"')):
        text = text.replace(src, dst)
    text = "".join(c for c in text if not 0x2000 <= ord(c) <= 0x200B)
    text = text.translate({ord(c): None for c in "「」『』\"'"})
    text = MARKDOWN_EMPHASIS_RE.sub("", text)
    return "".join(text.split())


def chapter_corpus(book: str, chapter: int, root: Path = ROOT) -> tuple[str, list[str]]:
    """本章語料＝manifest 的 OK commentary＋全本本地經文。"""
    base = book_directory(root, book) / ".tmp" / f"第{chapter}章"
    manifest = base / "source_manifest.md"
    if not manifest.is_file():
        raise FileNotFoundError(f"找不到 {manifest}")
    paths = [path for _label, path in parse_manifest(manifest, root)]
    paths.extend(sorted((root / "raw_scripture").glob("*/第*章.txt")))
    parts, names, scripture = [], [], 0
    for path in paths:
        path = Path(path)
        if not path.is_file():
            continue
        parts.append(normalize(path.read_text(encoding="utf-8", errors="ignore")))
        if path.parent.parent.name == "raw_scripture":
            scripture += 1
        else:
            names.append(path.name)
    if scripture:
        names.append(f"和合本經文 {scripture} 章")
    return "".join(parts), names


ACCUM_META_RE = re.compile(r"<!-- accumulation:([^:]+):(\d+):start -->")


def entry_corpus(entry_path: Path, root: Path = ROOT) -> tuple[str, list[str]]:
    """條目語料＝它累積過的每一章的 OK commentary＋全本經文。"""
    text = entry_path.read_text(encoding="utf-8")
    parts, names = [], []
    seen = set()
    for book, chapter in ACCUM_META_RE.findall(text):
        book = canonical_book_name(book)
        manifest = book_directory(root, book) / ".tmp" / f"第{chapter}章" / "source_manifest.md"
        if not manifest.is_file():
            names.append(f"（缺 manifest：{book}{chapter}）")
            continue
        for _label, path in parse_manifest(manifest, root):
            path = Path(path)
            if path in seen or not path.is_file():
                continue
            seen.add(path)
            parts.append(normalize(path.read_text(encoding="utf-8", errors="ignore")))
        names.append(f"{book}{chapter}")
    scripture = 0
    for path in sorted((root / "raw_scripture").glob("*/第*章.txt")):
        parts.append(normalize(path.read_text(encoding="utf-8", errors="ignore")))
        scripture += 1
    if scripture:
        names.append(f"和合本經文 {scripture} 章")
    return "".join(parts), names


def entry_targets(entry_path: Path):
    text = entry_path.read_text(encoding="utf-8")
    out = []
    for heading in ("定義", "主題發展"):
        start = text.find(f"## {heading}")
        if start < 0:
            continue
        end = text.find("\n## ", start + 4)
        out.append((heading, text[start:end if end > start else len(text)]))
    return out


def _scan_text(text: str, corpus: str, min_chars: int):
    total, misses = 0, []
    seen = set()
    for pattern in QUOTE_PATTERNS:
        for match in pattern.finditer(text):
            quote = match.group(1).strip()
            if len(quote) < min_chars or quote in seen:
                continue
            if "／" in quote or "/" in quote:
                continue
            seen.add(quote)
            total += 1
            if normalize(quote) in corpus:
                continue
            if ELLIPSIS_RE.search(quote):
                pieces = [f.strip() for f in ELLIPSIS_RE.split(quote) if f.strip()]
                fragments = [f for f in pieces if len(f) >= MIN_FRAGMENT_CHARS] or pieces
                if fragments and all(normalize(f) in corpus for f in fragments):
                    continue
            misses.append(quote)
    return total, misses


def check_entry_quotes(entry_path: Path, root: Path = ROOT, min_chars: int = MIN_QUOTE_CHARS):
    corpus, names = entry_corpus(Path(entry_path), root)
    total, misses = 0, []
    for label, text in entry_targets(Path(entry_path)):
        subtotal, sub_misses = _scan_text(text, corpus, min_chars)
        total += subtotal
        misses.extend((label, quote) for quote in sub_misses)
    return total, misses, names


def _organization_section(markdown: str) -> str:
    index = markdown.find(CHAPTER_ORGANIZATION_HEADING)
    return markdown[index:] if index >= 0 else ""


def _yaml_strings(node, fields=None, inside=False):
    out = []
    if isinstance(node, dict):
        for key, value in node.items():
            hit = fields is None or key in fields
            out.extend(_yaml_strings(value, fields, inside or hit))
    elif isinstance(node, list):
        for item in node:
            out.extend(_yaml_strings(item, fields, inside))
    elif isinstance(node, str) and (fields is None or inside):
        out.append(node)
    return out


def _yaml_text(path: Path, fields=None) -> str:
    return "\n".join(_yaml_strings(yaml.safe_load(path.read_text(encoding="utf-8")), fields))


def collect_targets(book: str, chapter: int, root: Path = ROOT):
    base = book_directory(root, book) / ".tmp" / f"第{chapter}章"
    targets = []
    for path in sorted(glob.glob(str(base / "entry_content" / "*.yaml"))):
        targets.append((f"entry_content/{Path(path).name}", _yaml_text(Path(path))))
    chapter_yaml = base / "chapter_content.yaml"
    if chapter_yaml.is_file():
        targets.append(("chapter_content.yaml", _yaml_text(chapter_yaml)))
    updates = base / "link_updates.yaml"
    if updates.is_file():
        targets.append(("link_updates.yaml（summary／relation）",
                        _yaml_text(updates, {"summary", "relation"})))
    rendered = book_directory(root, book) / f"第{chapter}章.md"
    if rendered.is_file():
        section = _organization_section(rendered.read_text(encoding="utf-8"))
        if section:
            targets.append((f"第{chapter}章.md（本章整理）", section))
    return targets


def check_quotes(book: str, chapter: int, root: Path = ROOT, min_chars: int = MIN_QUOTE_CHARS):
    corpus, source_names = chapter_corpus(book, chapter, root)
    total, misses = 0, []
    for label, text in collect_targets(book, chapter, root):
        subtotal, sub_misses = _scan_text(text, corpus, min_chars)
        total += subtotal
        misses.extend((label, quote) for quote in sub_misses)
    return total, misses, source_names


def _chinese_number(value: int) -> str:
    if value <= 0:
        return str(value)
    if value < 10:
        return _CN_DIGITS[value - 1]
    if value == 10:
        return "十"
    if value < 20:
        return "十" + _CN_DIGITS[value - 11]
    if value < 100:
        tens, ones = divmod(value, 10)
        return _CN_DIGITS[tens - 1] + "十" + ("" if ones == 0 else _CN_DIGITS[ones - 1])
    return str(value)


REFERENCE_RE = re.compile(
    r"(?<![一-鿿])([一-鿿]{1,4}(?:福音|前書|後書|一書|二書|三書)?)"
    r"\s*(\d{1,3})\s*[:：]\s*(\d{1,3})"
)


def check_references(book: str, chapter: int, root: Path = ROOT):
    corpus, _names = chapter_corpus(book, chapter, root)
    seen: dict[tuple[str, str, str], set[str]] = {}
    for label, text in collect_targets(book, chapter, root):
        for match in REFERENCE_RE.finditer(text):
            book_name, ref_chapter, verse = match.groups()
            if book_name.endswith(("第", "節", "章")):
                continue
            seen.setdefault((book_name, ref_chapter, verse), set()).add(label)
    misses = []
    for (book_name, ref_chapter, verse), labels in sorted(seen.items()):
        variants = {ref_chapter}
        if ref_chapter.isdigit():
            variants.add(_chinese_number(int(ref_chapter)))
        forms = set()
        for variant in variants:
            for joiner in (":", "：", ""):
                forms.add(normalize(f"{book_name}{variant}{joiner}{verse}"))
        if not any(form in corpus for form in forms):
            misses.append((f"{book_name}{ref_chapter}:{verse}", sorted(labels)))
    return len(seen), misses


def main() -> int:
    console.utf8_stdio()
    parser = argparse.ArgumentParser(description="引號字串疑點與交叉引註回查（只出報告）")
    parser.add_argument("book", nargs="?")
    parser.add_argument("chapter", type=int, nargs="?")
    parser.add_argument("--entry", help="改掃單一 link_folder 條目的定義與主題發展")
    parser.add_argument("--references", action="store_true",
                        help="同時回查交叉引註；交叉引註 miss 仍視為錯誤")
    parser.add_argument("--min-chars", type=int, default=MIN_QUOTE_CHARS, metavar="N",
                        help=f"引號內容掃描長度下限（預設 {MIN_QUOTE_CHARS}）")
    parser.add_argument("--strict", action="store_true",
                        help="把引號字串 miss 視為失敗；只用於已知必須逐字命中的資料")
    args = parser.parse_args()
    if args.min_chars < 1:
        parser.error("--min-chars 至少要 1")

    if args.entry:
        path = Path(args.entry)
        if not path.is_absolute():
            path = ROOT / args.entry
        total, misses, names = check_entry_quotes(path, min_chars=args.min_chars)
        print(f"語料：{path.name} 累積過的 {'、'.join(names)}")
        print(f"引號字串 {total} 處，逐字回查不到 {len(misses)} 處")
        for label, quote in misses:
            print(f"   ? {label}：{quote[:80]}")
        if misses and args.strict:
            print("結論：FAIL（strict：存在未逐字命中的引號字串）")
            return 1
        if misses:
            print("結論：REVIEW_NEEDED（疑點交 Evidence Reviewer 判斷；不因字串 miss 自動改文）")
            return 0
        print("結論：PASS（字串全命中；仍不代表 attribution 一定正確）")
        return 0

    if not args.book or args.chapter is None:
        parser.error("要嘛給「書名 章」，要嘛給 --entry <條目路徑>")
    book = canonical_book_name(args.book)

    total, misses, source_names = check_quotes(book, args.chapter, min_chars=args.min_chars)
    print(f"語料：{'、'.join(source_names)}")
    print(f"引號字串 {total} 處，逐字回查不到 {len(misses)} 處")
    for label, quote in misses:
        print(f"   ? {label}：{quote[:80]}")

    ref_misses = []
    if args.references:
        ref_total, ref_misses = check_references(book, args.chapter)
        print(f"交叉引註 {ref_total} 組，回查不到 {len(ref_misses)} 組")
        for reference, labels in ref_misses:
            print(f"   ✗ {reference}　← {'、'.join(labels)}")

    if ref_misses:
        print("結論：FAIL（交叉引註查無對應）")
        return 1
    if misses and args.strict:
        print("結論：FAIL（strict：存在未逐字命中的引號字串）")
        return 1
    if misses:
        print("結論：REVIEW_NEEDED（字串比對不能判斷翻譯、轉述或修辭；交 Evidence Reviewer）")
        return 0
    print("結論：PASS（字串全命中；內容與 attribution 仍須 Evidence Reviewer 核對）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
