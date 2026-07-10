#!/usr/bin/env python3
"""從 verse_links + chapter_content payload 渲染章節主檔 markdown。

模型只填兩份資料：
  * verse_links     —— 標注「哪一節、哪個詞、連到哪個 target、第幾次出現」；
                       實際把經文詞替換成 [[target|詞]] 由本程式完成，alias
                       格式因此永遠合規，且只連指定的那一次出現。
  * chapter_content —— 本章知識節點（分組 → target 清單）與本章整理正文。

經文本文一律取自 raw_scripture，模型不得改寫；H1、節次編號、H2 段落順序、
知識節點的 [[...]] 格式全由本程式產生。FHL「相關地圖」區塊由 build_fhl_maps.py
管理，本程式只作原樣保留（passthrough），不生成、不改寫。
"""
import argparse
import json
import re
import sys
from pathlib import Path

import yaml

try:
    from .book_paths import book_directory, canonical_book_name
except ImportError:
    from book_paths import book_directory, canonical_book_name

ROOT = Path(__file__).resolve().parent.parent
BOOK_CHAPTERS = json.loads(
    (ROOT / "_config" / "bible_books.json").read_text(encoding="utf-8")
)
MAP_BLOCK_RE = re.compile(
    r"<!-- fhl-map-links:start -->[\s\S]*?<!-- fhl-map-links:end -->"
)


def load_raw_verses(book, chapter):
    path = ROOT / "raw_scripture" / canonical_book_name(book) / f"第{chapter}章.txt"
    if not path.exists():
        raise FileNotFoundError(path)
    return [line.rstrip("\n") for line in path.read_text(encoding="utf-8").splitlines()]


# --------------------------------------------------------------------------- #
# 驗證（驗證左移）
# --------------------------------------------------------------------------- #
def _occurrence_span(raw, phrase, occurrence):
    index = -1
    for _ in range(occurrence):
        index = raw.find(phrase, index + 1)
        if index == -1:
            return None
    return (index, index + len(phrase))


def validate_verse_links(links, raw_verses):
    errors = []
    verse_count = len(raw_verses)
    spans_by_verse = {}
    for position, link in enumerate(links):
        prefix = f"links[{position}]"
        if not isinstance(link, dict):
            errors.append(f"{prefix} 必須是物件")
            continue
        verse = link.get("verse")
        if not isinstance(verse, int) or isinstance(verse, bool) or not (1 <= verse <= verse_count):
            errors.append(f"{prefix}.verse 必須是 1..{verse_count} 的整數")
            continue
        phrase = link.get("phrase")
        target = link.get("target")
        if not isinstance(phrase, str) or not phrase:
            errors.append(f"{prefix}.phrase 必填")
            continue
        if not isinstance(target, str) or not target.strip():
            errors.append(f"{prefix}.target 必填")
            continue
        occurrence = link.get("occurrence", 1)
        if not isinstance(occurrence, int) or isinstance(occurrence, bool) or occurrence < 1:
            errors.append(f"{prefix}.occurrence 必須是 ≥1 的整數")
            continue
        span = _occurrence_span(raw_verses[verse - 1], phrase, occurrence)
        if span is None:
            errors.append(
                f"{prefix}: 第{verse}節找不到第{occurrence}次出現的「{phrase}」"
            )
            continue
        spans_by_verse.setdefault(verse, []).append((span, phrase))
    for verse, spans in spans_by_verse.items():
        spans.sort()
        for (a_span, a_phrase), (b_span, b_phrase) in zip(spans, spans[1:]):
            if a_span[1] > b_span[0]:
                errors.append(
                    f"第{verse}節 link 範圍重疊：「{a_phrase}」與「{b_phrase}」"
                )
    return errors


def validate_chapter_content(content):
    errors = []
    nodes = content.get("knowledge_nodes")
    if not isinstance(nodes, dict) or not any(
        isinstance(v, list) and v for v in nodes.values()
    ):
        errors.append("chapter_content.knowledge_nodes 至少需一個分組且含節點")
    if not str(content.get("organization", "")).strip():
        errors.append("chapter_content.organization（本章整理）必填且不可為空")
    return errors


# --------------------------------------------------------------------------- #
# 渲染
# --------------------------------------------------------------------------- #
def _link_verse(raw, links):
    spans = []
    for link in links:
        span = _occurrence_span(raw, link["phrase"], link.get("occurrence", 1))
        spans.append((span[0], span[1], link["target"]))
    spans.sort()
    out, cursor = [], 0
    for start, end, target in spans:
        out.append(raw[cursor:start])
        phrase = raw[start:end]
        out.append(f"[[{target}]]" if target == phrase else f"[[{target}|{phrase}]]")
        cursor = end
    out.append(raw[cursor:])
    return "".join(out)


def render_scripture(raw_verses, verse_links):
    by_verse = {}
    for link in verse_links:
        by_verse.setdefault(link["verse"], []).append(link)
    lines = []
    for number, raw in enumerate(raw_verses, 1):
        lines.append(f"{number}. {_link_verse(raw, by_verse.get(number, []))}")
    return "\n".join(lines)


def render_knowledge_nodes(nodes):
    parts = []
    for group, targets in nodes.items():
        rendered = [f"- [[{str(t).strip()}]]" for t in targets if str(t).strip()]
        if rendered:
            parts.append(f"### {group}\n" + "\n".join(rendered))
    return "\n\n".join(parts)


def render_chapter(verse_links_payload, chapter_content, *, raw_verses=None, map_block=""):
    book = verse_links_payload.get("book") or chapter_content.get("book")
    chapter = verse_links_payload.get("chapter") or chapter_content.get("chapter")
    if raw_verses is None:
        raw_verses = load_raw_verses(book, chapter)

    errors = validate_verse_links(verse_links_payload.get("links", []), raw_verses)
    errors.extend(validate_chapter_content(chapter_content))
    if errors:
        raise ValueError("payload 驗證失敗：\n- " + "\n- ".join(errors))

    scripture = render_scripture(raw_verses, verse_links_payload.get("links", []))
    nodes = render_knowledge_nodes(chapter_content["knowledge_nodes"])
    organization = str(chapter_content["organization"]).strip()

    blocks = [f"# {canonical_book_name(book)} 第{chapter}章", scripture]
    if map_block.strip():
        blocks.append(map_block.strip())
    blocks.append("---")
    blocks.append(f"## 本章知識節點\n\n{nodes}")
    blocks.append("---")
    blocks.append(f"## 本章整理\n\n{organization}")
    return "\n\n".join(blocks).rstrip() + "\n"


def chapter_path(book, chapter):
    return book_directory(ROOT, book) / f"第{chapter}章.md"


# --------------------------------------------------------------------------- #
# 反向解析（供 round-trip 測試與既有章節遷移）
# --------------------------------------------------------------------------- #
def _extract_links_from_rendered(text):
    raw_parts, links, raw_len, i = [], [], 0, 0
    while i < len(text):
        if text.startswith("[[", i):
            end = text.index("]]", i)
            inner = text[i + 2:end]
            target, sep, alias = inner.partition("|")
            phrase = alias if sep else target
            links.append((raw_len, phrase, target.strip()))
            raw_parts.append(phrase)
            raw_len += len(phrase)
            i = end + 2
        else:
            raw_parts.append(text[i])
            raw_len += 1
            i += 1
    return "".join(raw_parts), links


def _count_before(raw, phrase, start):
    count, index = 0, raw.find(phrase)
    while index != -1 and index < start:
        count += 1
        index = raw.find(phrase, index + 1)
    return count


def parse_chapter(text):
    """章節主檔 markdown → (verse_links_payload, chapter_content, map_block)。"""
    heading = re.search(r"^#\s+(.+?)\s+第(\d+)章\s*$", text, re.M)
    book = canonical_book_name(heading.group(1)) if heading else ""
    chapter = int(heading.group(2)) if heading else 0

    map_match = MAP_BLOCK_RE.search(text)
    map_block = map_match.group(0) if map_match else ""

    knowledge = text.find("## 本章知識節點")
    scripture_zone = text[:knowledge] if knowledge >= 0 else text
    if map_block:
        scripture_zone = scripture_zone.replace(map_block, "")

    links = []
    for match in re.finditer(r"^(\d+)\.\s(.*)$", scripture_zone, re.M):
        verse = int(match.group(1))
        raw, verse_links = _extract_links_from_rendered(match.group(2))
        for start, phrase, target in verse_links:
            links.append({
                "verse": verse,
                "phrase": phrase,
                "target": target,
                "occurrence": _count_before(raw, phrase, start) + 1,
            })
    verse_links_payload = {"book": book, "chapter": chapter, "links": links}

    nodes = {}
    node_match = re.search(
        r"^## 本章知識節點\s*$([\s\S]*?)(?=^## 本章整理\s*$)", text, re.M
    )
    if node_match:
        for group_match in re.finditer(
            r"^###\s+(.+?)\s*$([\s\S]*?)(?=^###\s+|\Z)", node_match.group(1), re.M
        ):
            targets = [
                inner.partition("|")[0].strip()
                for inner in re.findall(r"\[\[([^\]]+)\]\]", group_match.group(2))
            ]
            if targets:
                nodes[group_match.group(1).strip()] = targets

    organization_match = re.search(r"^## 本章整理\s*$([\s\S]+)$", text, re.M)
    organization = organization_match.group(1).strip() if organization_match else ""

    chapter_content = {
        "book": book,
        "chapter": chapter,
        "knowledge_nodes": nodes,
        "organization": organization,
    }
    return verse_links_payload, chapter_content, map_block


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _load(path):
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: payload 必須是 YAML/JSON 物件")
    return data


def _cmd_render(args):
    verse_links_payload = _load(args.verse_links)
    chapter_content = _load(args.chapter_content)
    book = verse_links_payload.get("book") or chapter_content.get("book")
    chapter = verse_links_payload.get("chapter") or chapter_content.get("chapter")
    map_block = ""
    target = chapter_path(book, chapter)
    if args.preserve_maps and target.exists():
        existing = MAP_BLOCK_RE.search(target.read_text(encoding="utf-8"))
        map_block = existing.group(0) if existing else ""
    rendered = render_chapter(
        verse_links_payload, chapter_content, map_block=map_block
    )
    if args.write:
        if target.exists() and not args.force:
            raise FileExistsError(f"{target} 已存在；加 --force 才覆蓋")
        target.write_text(rendered, encoding="utf-8")
        print(f"✅ 已寫入：{target.relative_to(ROOT)}")
    else:
        sys.stdout.write(rendered)
    return 0


def _cmd_extract(args):
    verse_links_payload, chapter_content, _ = parse_chapter(
        args.chapter.read_text(encoding="utf-8")
    )
    sys.stdout.write("# --- verse_links ---\n")
    sys.stdout.write(yaml.safe_dump(verse_links_payload, allow_unicode=True, sort_keys=False))
    sys.stdout.write("\n# --- chapter_content ---\n")
    sys.stdout.write(yaml.safe_dump(chapter_content, allow_unicode=True, sort_keys=False))
    return 0


def main():
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    render_parser = sub.add_parser("render", help="payload → 章節主檔 markdown")
    render_parser.add_argument("verse_links", type=Path)
    render_parser.add_argument("chapter_content", type=Path)
    render_parser.add_argument("--write", action="store_true")
    render_parser.add_argument("--force", action="store_true")
    render_parser.add_argument(
        "--preserve-maps", action="store_true",
        help="保留既有章節檔的 fhl-map-links 區塊",
    )
    render_parser.set_defaults(func=_cmd_render)

    extract_parser = sub.add_parser("extract", help="既有章節主檔 → payload")
    extract_parser.add_argument("chapter", type=Path)
    extract_parser.set_defaults(func=_cmd_extract)

    args = parser.parse_args()
    try:
        return args.func(args)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"❌ {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
