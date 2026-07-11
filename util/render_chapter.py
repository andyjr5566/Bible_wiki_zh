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
def _phrase_positions(raw, phrase):
    positions, start = [], raw.find(phrase)
    while start != -1:
        positions.append(start)
        start = raw.find(phrase, start + 1)
    return positions


def _assign_spans(raw, links):
    """同一節的 links 依序對應到 phrase 的出現位置。

    模型無法可靠地數「第幾次出現」，所以不採信 occurrence，改依 link 出現
    順序把同一 phrase 對應到第 1、2、… 次出現；超出出現次數者捨棄，範圍
    重疊者保留較前、捨棄較後。回傳排序後的 [(start, end, target)]。
    """
    used = {}
    spans = []
    for link in links:
        phrase = link["phrase"]
        slot = used.setdefault(phrase, {"idxs": _phrase_positions(raw, phrase), "n": 0})
        if slot["n"] < len(slot["idxs"]):
            start = slot["idxs"][slot["n"]]
            slot["n"] += 1
            spans.append((start, start + len(phrase), link["target"]))
    spans.sort()
    filtered, last_end = [], -1
    for start, end, target in spans:
        if start >= last_end:
            filtered.append((start, end, target))
            last_end = end
    return filtered


def validate_verse_links(links, raw_verses):
    """只硬性檢查結構與「phrase 是否真的在該節」；occurrence／重疊／過量
    由 _assign_spans 於渲染時寬容處理，不讓整章因此失敗。"""
    errors = []
    verse_count = len(raw_verses)
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
        if phrase not in raw_verses[verse - 1]:
            errors.append(f"{prefix}: 第{verse}節沒有「{phrase}」")
    return errors


def coerce_knowledge_nodes(nodes):
    """把模型各種寫法統一成 {分組: [target, …]}。

    寬容處理：dict 值是字串 → 包成單元素 list；整個是 list（如
    [{group:…, nodes:[…]}, …]）→ 轉成 dict。無法辨識則回空 dict。
    """
    if isinstance(nodes, dict):
        result = {}
        for group, value in nodes.items():
            if isinstance(value, list):
                result[str(group)] = value
            elif value:
                result[str(group)] = [value]
        return result
    if isinstance(nodes, list):
        result = {}
        for item in nodes:
            if not isinstance(item, dict):
                continue
            group = item.get("group") or item.get("type") or item.get("category")
            values = item.get("nodes") or item.get("items") or item.get("targets") or []
            if group:
                result[str(group)] = values if isinstance(values, list) else [values]
        return result
    return {}


def _org_lines(value):
    if isinstance(value, list):
        return [f"- {str(v).strip()}" for v in value if str(v).strip()]
    text = str(value).strip()
    return [f"- {text}"] if text else []


def coerce_organization(org):
    """把 organization 統一成 markdown 字串。

    模型常把「本章整理」寫成 {主題: [重點, …]} 的 dict 或 list，直接 str() 會
    印出 Python repr。這裡一律轉成「**主題** + bullet」的 markdown；字串則原樣
    保留（維持既有章節 round-trip）。
    """
    if isinstance(org, str):
        return org.strip()
    if isinstance(org, dict):
        groups = []
        for key, value in org.items():
            groups.append("\n".join([f"**{key}**", *_org_lines(value)]))
        return "\n\n".join(g for g in groups if g.strip()).strip()
    if isinstance(org, list):
        return "\n".join(_org_lines(org)).strip()
    return ""


REFERENCES_RE = re.compile(r"\n?\*\*參考資料\*\*\s*\n(?P<body>[\s\S]*)\Z")


def split_references(text):
    """把「本章整理」正文結尾的 **參考資料** 區塊拆出 → (正文, [url, …])。"""
    match = REFERENCES_RE.search(text)
    if not match:
        return text.strip(), []
    references = [
        line.strip().lstrip("- ").strip()
        for line in match.group("body").splitlines()
        if line.strip()
    ]
    return text[: match.start()].strip(), references


def validate_chapter_content(content):
    errors = []
    nodes = coerce_knowledge_nodes(content.get("knowledge_nodes"))
    if not any(isinstance(v, list) and v for v in nodes.values()):
        errors.append("chapter_content.knowledge_nodes 至少需一個分組且含節點")
    if not coerce_organization(content.get("organization")).strip():
        errors.append("chapter_content.organization（本章整理）必填且不可為空")
    references = content.get("references")
    if references is not None and (
        not isinstance(references, list) or any(not isinstance(r, str) for r in references)
    ):
        errors.append("chapter_content.references 必須是字串陣列")
    return errors


# --------------------------------------------------------------------------- #
# 渲染
# --------------------------------------------------------------------------- #
def _link_verse(raw, links):
    out, cursor = [], 0
    for start, end, target in _assign_spans(raw, links):
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
    nodes = render_knowledge_nodes(coerce_knowledge_nodes(chapter_content["knowledge_nodes"]))
    # organization 內殘留的參考資料一併拆出，與 references 欄位合流，避免重複渲染
    organization, inline_refs = split_references(
        coerce_organization(chapter_content["organization"])
    )
    references = [
        str(r).strip() for r in (chapter_content.get("references") or []) if str(r).strip()
    ] or inline_refs

    blocks = [f"# {canonical_book_name(book)} 第{chapter}章", scripture]
    if map_block.strip():
        blocks.append(map_block.strip())
    blocks.append("---")
    blocks.append(f"## 本章知識節點\n\n{nodes}")
    blocks.append("---")
    organization_block = f"## 本章整理\n\n{organization}"
    if references:
        organization_block += "\n\n**參考資料**\n" + "\n".join(references)
    blocks.append(organization_block)
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
    organization, references = split_references(organization)

    chapter_content = {
        "book": book,
        "chapter": chapter,
        "knowledge_nodes": nodes,
        "organization": organization,
        "references": references,
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
