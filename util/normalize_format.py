#!/usr/bin/env python3
"""將章節與 link_folder 條目無損正規化為 scheme.md 現行格式。"""
import argparse
import difflib
import io
import json
import re
import subprocess
import sys
import tarfile
from collections import OrderedDict
from pathlib import Path

import yaml

try:
    from .book_paths import book_directory, canonical_book_name
except ImportError:
    from book_paths import book_directory, canonical_book_name

ROOT = Path(__file__).resolve().parent.parent
LINK_FOLDER = ROOT / "link_folder"

DEFINITION = {"定義", "定義／基本資料", "定義／核心摘要", "定定義／核心摘要"}
CORE = {"核心摘要"}
ACCUMULATION = {
    "按書卷累積", "觸發來源", "聖經出現", "與目前整理書卷的關聯",
    "累積區", " bible_出現",
}
DEVELOPMENT = {
    "主題發展", "神學意義／研讀意義", "神學意義", "神學或研讀意義",
    "屬靈意義", "屬靈歷程", "字義分析", "三種主要解釋", "結論",
    "方舟豫表基督八方面", "聖經中「四十」的其他實例", "條文",
}
RELATED = {"相關條目", "関連項目", "相关条目", "參見"}
SOURCES = {"來源依據", "參考來源", "參考文獻"}
BOOK_ORDER = list(json.loads(
    (ROOT / "_config" / "bible_books.json").read_text(encoding="utf-8")
))
BOOK_RANK = {book: index for index, book in enumerate(BOOK_ORDER)}
CHINESE_DIGITS = {
    "零": 0, "一": 1, "二": 2, "三": 3, "四": 4,
    "五": 5, "六": 6, "七": 7, "八": 8, "九": 9,
}


def split_frontmatter(text):
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.DOTALL)
    if not match:
        return {}, text
    data = yaml.safe_load(match.group(1)) or {}
    return (data if isinstance(data, dict) else {}), text[match.end():]


def parse_h2(body):
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", body, re.M))
    prefix_end = matches[0].start() if matches else len(body)
    prefix = body[:prefix_end].rstrip()
    sections = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        sections.append((match.group(1).strip(), body[match.end():end].strip()))
    return prefix, sections


def first_paragraph(text):
    for block in re.split(r"\n\s*\n", text.strip()):
        cleaned = block.strip()
        if cleaned and not cleaned.startswith(("#", "-", "|", "<!--")):
            return cleaned
    return text.strip().splitlines()[0].strip() if text.strip() else ""


def merge_named(items, include_labels=True):
    chunks = []
    for name, content in items:
        if not content:
            continue
        if include_labels and len(items) > 1:
            chunks.append(f"### {name}\n\n{content}")
        else:
            chunks.append(content)
    return "\n\n".join(chunks).strip()


def chinese_number(value):
    value = value.replace("廿", "二十")
    if value == "十":
        return 10
    if "十" in value:
        left, right = value.split("十", 1)
        tens = CHINESE_DIGITS.get(left, 1) if left else 1
        ones = CHINESE_DIGITS.get(right, 0) if right else 0
        return tens * 10 + ones
    return CHINESE_DIGITS.get(value)


def parse_book_chapter(title):
    compact = re.sub(r"\s+", "", title)
    for book in sorted(BOOK_ORDER, key=len, reverse=True):
        prefix = f"{book}第"
        if not compact.startswith(prefix) or not compact.endswith("章"):
            continue
        number = compact[len(prefix):-1]
        chapter = int(number) if number.isdigit() else chinese_number(number)
        if chapter:
            return book, chapter
    return None


def extract_chapter_blocks(content):
    """取出 H3/H4 章次資料，留下不屬於章次累積的原文。"""
    content = re.sub(r"^<!-- accumulation:[^>]+:(?:start|end) -->\s*\n?", "", content, flags=re.M)
    matches = list(re.finditer(r"^###\s+(.+?)\s*$", content, re.M))
    if not matches:
        return content.strip(), []
    prefix = content[:matches[0].start()].strip()
    kept = [prefix] if prefix else []
    chapters = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        title = match.group(1).strip()
        body = content[match.end():end].strip()
        combined = parse_book_chapter(title)
        if combined:
            chapters.append((*combined, body))
            continue
        if title in BOOK_RANK:
            h4s = list(re.finditer(r"^####\s+第\s*(\d+)\s*章\s*$", body, re.M))
            if h4s:
                group_prefix = body[:h4s[0].start()].strip()
                residual = [group_prefix] if group_prefix else []
                for h4_index, h4 in enumerate(h4s):
                    h4_end = h4s[h4_index + 1].start() if h4_index + 1 < len(h4s) else len(body)
                    chapters.append((title, int(h4.group(1)), body[h4.end():h4_end].strip()))
                if residual:
                    kept.append(f"### {title}\n\n" + "\n\n".join(residual))
                continue
        if body:
            kept.append(f"### {title}\n\n{body}".rstrip())
    return "\n\n".join(part for part in kept if part).strip(), chapters


def render_chapter_accumulation(chapters):
    grouped = {}
    for book, chapter, content in chapters:
        key = (book, chapter)
        values = grouped.setdefault(key, [])
        if content and content not in values:
            values.append(content)
    books = {}
    for (book, chapter), values in grouped.items():
        books.setdefault(book, []).append((chapter, "\n\n".join(values)))
    rendered = []
    for book in sorted(books, key=lambda item: (BOOK_RANK.get(item, 999), item)):
        blocks = []
        for chapter, content in sorted(books[book]):
            block = (
                f"<!-- accumulation:{book}:{chapter}:start -->\n"
                f"#### 第{chapter}章\n"
                f"{content}\n"
                f"<!-- accumulation:{book}:{chapter}:end -->"
            )
            blocks.append(block)
        rendered.append(f"### {book}\n\n" + "\n\n".join(blocks))
    return "\n\n".join(rendered)


def partition_accumulation(content):
    """累積區只留索引型資料；主題型 H3 移交主題發展。"""
    allowed = {"觸發來源", "聖經出現", "與目前整理書卷的關聯"}
    matches = list(re.finditer(r"^###\s+(.+?)\s*$", content, re.M))
    if not matches:
        return content.strip(), []
    prefix = content[:matches[0].start()].strip()
    kept = [prefix] if prefix else []
    moved = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        title = match.group(1).strip()
        body = content[match.end():end].strip()
        rendered = f"### {title}\n\n{body}".rstrip()
        if title in allowed:
            kept.append(rendered)
        elif body:
            moved.append((title, body))
    return "\n\n".join(kept).strip(), moved


def normalized_frontmatter(path, fm):
    status = fm.get("status", "candidate")
    if status not in {"formal", "candidate"}:
        status = "candidate"
    result = OrderedDict()
    result["type"] = path.parent.name
    result["secondary_types"] = fm.get("secondary_types", [])
    result["aliases"] = fm.get("aliases", [])
    result["status"] = status
    if status == "candidate" and fm.get("created_from"):
        result["created_from"] = fm["created_from"]
    result["source_scope"] = "collected_only"
    if not isinstance(result["secondary_types"], list):
        result["secondary_types"] = [result["secondary_types"]]
    if not isinstance(result["aliases"], list):
        result["aliases"] = [result["aliases"]]
    return result


def normalize_formal(path, fm, body):
    _, sections = parse_h2(body)
    buckets = {key: [] for key in ("definition", "core", "accum", "development", "related", "sources", "other")}
    chapters = []
    for name, content in sections:
        content, found_chapters = extract_chapter_blocks(content)
        chapters.extend(found_chapters)
        if name in DEFINITION:
            buckets["definition"].append((name, content))
        elif name in CORE:
            buckets["core"].append((name, content))
        elif name in ACCUMULATION:
            buckets["accum"].append((name, content))
        elif name in DEVELOPMENT:
            buckets["development"].append((name, content))
        elif name in RELATED:
            buckets["related"].append((name, content))
        elif name in SOURCES:
            buckets["sources"].append((name, content))
        else:
            buckets["other"].append((name, content))

    migrated_development = []
    cleaned_accumulation = []
    for name, content in buckets["accum"]:
        kept, moved = partition_accumulation(content)
        if kept:
            cleaned_accumulation.append((name, kept))
        migrated_development.extend(moved)
    buckets["accum"] = cleaned_accumulation

    definition_parts = []
    for _, content in buckets["definition"] + buckets["core"]:
        if content and content not in definition_parts:
            definition_parts.append(content)
    definition = "\n\n".join(definition_parts)
    if not definition:
        definition = first_paragraph(merge_named(buckets["accum"], False))
    accumulation = merge_named(buckets["accum"])
    chapter_accumulation = render_chapter_accumulation(chapters)
    accumulation = "\n\n".join(filter(None, [accumulation, chapter_accumulation]))
    development_items = buckets["development"] + buckets["other"] + migrated_development
    development = merge_named(development_items)
    development = re.sub(r"^###\s+主題發展\s*\n+", "", development, count=1)
    related = merge_named(buckets["related"], False)
    sources = merge_named(buckets["sources"], False)
    if not sources:
        triggers = [item for item in buckets["accum"] if item[0] == "觸發來源"]
        sources = merge_named(triggers, False)

    content = [
        f"# {path.stem}",
        f"## 定義\n\n{definition}",
        f"## 按書卷累積\n\n{accumulation}",
        f"## 主題發展\n\n{development}",
        f"## 相關條目\n\n{related}",
        f"## 來源依據\n\n{sources}",
    ]
    return "\n\n".join(part.rstrip() for part in content).rstrip() + "\n"


def normalize_candidate(path, fm, body):
    _, sections = parse_h2(body)
    grouped = {name: content for name, content in sections}
    type_content = grouped.get("類型") or grouped.get("條目分類") or path.parent.name
    triggers = grouped.get("觸發來源", "")
    current = grouped.get("目前資料", "")
    related = next((grouped.get(name, "") for name in RELATED if grouped.get(name)), "")
    pending = grouped.get("待補充") or grouped.get("待確認事項", "")
    known = {"類型", "條目分類", "觸發來源", "目前資料", "待補充", "待確認事項"} | RELATED
    extras = [(name, content) for name, content in sections if name not in known]
    if extras:
        current = "\n\n".join(filter(None, [current, merge_named(extras)]))
    parts = [
        f"# {path.stem}",
        f"## 類型\n\n{type_content}",
        f"## 觸發來源\n\n{triggers}",
        f"## 目前資料\n\n{current}",
        f"## 相關條目\n\n{related}",
        f"## 待補充\n\n{pending}",
    ]
    return "\n\n".join(part.rstrip() for part in parts).rstrip() + "\n"


def normalize_entry(path):
    original = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(original)
    normalized_fm = normalized_frontmatter(path, fm)
    if normalized_fm["status"] == "candidate":
        normalized_body = normalize_candidate(path, fm, body)
    else:
        normalized_body = normalize_formal(path, fm, body)
    yaml_text = yaml.safe_dump(
        dict(normalized_fm), allow_unicode=True, sort_keys=False, default_flow_style=False
    ).strip()
    return f"---\n{yaml_text}\n---\n\n{normalized_body}"


def normalize_chapter(path):
    original = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(original)
    chapter = int(re.search(r"第(\d+)章", path.stem).group(1))
    body = re.sub(r"^#\s+創世記\s+第.+?章\s*$", f"# 創世記 第{chapter}章", body, count=1, flags=re.M)
    body = re.sub(rf"^(# 創世記 第{chapter}章)\n+", r"\1\n\n", body, count=1)
    body = re.sub(r"^##\s+經文\s*\n+", "", body, flags=re.M)
    body = re.sub(r"^##\s+補充資料\s*$", "## 本章整理", body, flags=re.M)
    body = re.sub(r"^##\s+第[一二三四]+段：[^\n]+\n+", "", body, flags=re.M)

    knowledge = re.search(r"^##\s+本章知識節點\s*$", body, re.M)
    organization = re.search(r"^##\s+本章整理\s*$", body, re.M)
    if not knowledge:
        insert_at = organization.start() if organization else len(body)
        before, after = body[:insert_at].rstrip(), body[insert_at:].lstrip()
        body = before + "\n\n---\n\n## 本章知識節點\n\n" + after
    if not re.search(r"^##\s+本章整理\s*$", body, re.M):
        body = body.rstrip() + "\n\n---\n\n## 本章整理\n"

    organization = re.search(r"^##\s+本章整理\s*$", body, re.M)
    head = body[:organization.end()]
    tail = body[organization.end():]
    tail = re.sub(r"^##\s+(待確認事項|資料來源|來源依據)\s*$", r"### \1", tail, flags=re.M)
    if fm.get("sources") and not re.search(r"^###\s+資料來源\s*$", tail, re.M):
        source_lines = "\n".join(f"- {source}" for source in fm["sources"])
        tail = tail.rstrip() + f"\n\n### 資料來源\n\n{source_lines}\n"
    body = head + tail

    knowledge = re.search(r"^##\s+本章知識節點\s*$", body, re.M)
    scripture_part = body[:knowledge.start()]
    rest = body[knowledge.start():]
    map_block_match = re.search(
        r"<!-- fhl-map-links:start -->[\s\S]*?<!-- fhl-map-links:end -->",
        scripture_part,
    )
    map_block = map_block_match.group(0).strip() if map_block_match else ""
    scripture_part = re.sub(r"^(\d+)(?![.\d])\s+", r"\1. ", scripture_part, flags=re.M)
    scripture_part = re.sub(r"^(\d+\..*)\n\n(?=\d+\.)", r"\1\n", scripture_part, flags=re.M)
    raw_path = ROOT / "raw_scripture" / "創世記" / f"第{chapter}章.txt"
    if raw_path.exists():
        raw_lines = raw_path.read_text(encoding="utf-8").splitlines()
        verse_numbers = [int(value) for value in re.findall(r"^(\d+)\.\s", scripture_part, re.M)]
        expected = list(range(1, len(raw_lines) + 1))
        if verse_numbers != expected:
            aliases = OrderedDict()
            for match in re.finditer(r"\[\[([^]|]+)(?:\|([^]]+))?\]\]", scripture_part):
                target, alias = match.group(1), match.group(2) or match.group(1)
                aliases.setdefault(alias, f"[[{target}|{alias}]]" if alias != target else f"[[{target}]]")
            linked_lines = []
            for number, raw_line in enumerate(raw_lines, 1):
                rendered = raw_line
                placeholders = {}
                for index, alias in enumerate(sorted(aliases, key=len, reverse=True)):
                    if alias not in rendered:
                        continue
                    token = f"\uFFF0{index}\uFFF1"
                    rendered = rendered.replace(alias, token)
                    placeholders[token] = aliases[alias]
                for token, link in placeholders.items():
                    rendered = rendered.replace(token, link)
                linked_lines.append(f"{number}. {rendered}")
            scripture_part = f"# 創世記 第{chapter}章\n\n" + "\n".join(linked_lines)
            if map_block:
                scripture_part += "\n\n" + map_block
    body = scripture_part.rstrip() + "\n\n---\n\n" + rest.lstrip()
    body = re.sub(r"\n---\n\n---\n", "\n---\n", body)
    knowledge_match = re.search(
        r"(^## 本章知識節點\s*$)([\s\S]*?)(?=^## 本章整理\s*$)", body, re.M
    )
    if knowledge_match and not knowledge_match.group(2).strip():
        organization_text = body[knowledge_match.end():]
        nodes = []
        for heading in re.findall(r"^###\s+(.+)$", organization_text, re.M):
            for target in re.findall(r"\[\[([^]|]+)(?:\|[^]]+)?\]\]", heading):
                if target not in nodes:
                    nodes.append(target)
        if not nodes:
            for target in re.findall(r"\[\[([^]|]+)(?:\|[^]]+)?\]\]", organization_text):
                if target not in nodes:
                    nodes.append(target)
        if not nodes:
            for target in re.findall(r"\[\[([^]|]+)(?:\|[^]]+)?\]\]", scripture_part):
                if target not in nodes:
                    nodes.append(target)
        if nodes:
            node_text = "\n\n### 主題\n\n" + "\n".join(f"- [[{node}]]" for node in nodes) + "\n\n"
            body = body[:knowledge_match.start(2)] + node_text + body[knowledge_match.end(2):]
    return body.strip() + "\n"


def apply_scope(scope, dry_run=False):
    paths = []
    if scope in {"genesis", "all"}:
        paths.extend(sorted(book_directory(ROOT, "創世記").glob("第*章.md"), key=lambda p: int(re.search(r"\d+", p.name).group())))
    if scope in {"links", "all"}:
        paths.extend(sorted(LINK_FOLDER.rglob("*.md")))
    changed = []
    for path in paths:
        rendered = (
            normalize_chapter(path)
            if canonical_book_name(path.parent.name) == "創世記"
            else normalize_entry(path)
        )
        if rendered != path.read_text(encoding="utf-8"):
            changed.append(path)
            if not dry_run:
                path.write_text(rendered, encoding="utf-8")
    print(f"{'預覽' if dry_run else '完成'}：{len(changed)}/{len(paths)} 個檔案需要變更")
    return changed


def verify_preservation(base):
    missing = []
    archive = subprocess.run(
        ["git", "archive", "--format=tar", base, "link_folder"],
        cwd=ROOT, capture_output=True,
    )
    if archive.returncode:
        print(f"❌ 無法讀取 {base} 的 link_folder")
        return False
    old_files = {}
    with tarfile.open(fileobj=io.BytesIO(archive.stdout), mode="r:") as bundle:
        for member in bundle.getmembers():
            if member.isfile() and member.name.endswith(".md"):
                extracted = bundle.extractfile(member)
                old_files[member.name] = extracted.read().decode("utf-8") if extracted else ""
    all_new_text = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted(LINK_FOLDER.rglob("*.md"))
    )
    def comparable(value):
        value = re.sub(r"（創[^）]+）", "", value)
        value = re.sub(r"（[A-Z/]+）", "", value)
        return re.sub(r"\s+", " ", value).strip()

    normalized_all_new = comparable(all_new_text)
    comparable_new_lines = [
        comparable(line) for line in all_new_text.splitlines() if comparable(line)
    ]
    for path in sorted(LINK_FOLDER.rglob("*.md")):
        relative = str(path.relative_to(ROOT)).replace("\\", "/")
        if relative not in old_files:
            continue
        _, old_body = split_frontmatter(old_files[relative])
        new_text = path.read_text(encoding="utf-8")
        old_lines = []
        for line in old_body.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            old_lines.append(comparable(stripped))
        for line in old_lines:
            if line not in normalized_all_new and not any(
                difflib.SequenceMatcher(None, line, candidate).ratio() >= 0.75
                for candidate in comparable_new_lines
            ):
                missing.append(f"{relative}: {line[:100]}")
    if missing:
        for item in missing[:50]:
            print(f"❌ 遺失內容：{item}")
        print(f"共 {len(missing)} 行舊內容未在新格式中找到")
        return False
    print("✅ link_folder 正文保存驗證通過")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", choices=("genesis", "links", "all"), default="all")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verify-base", help="與指定 Git revision 比較，確認條目正文未遺失")
    args = parser.parse_args()
    if args.verify_base and not verify_preservation(args.verify_base):
        return 1
    apply_scope(args.scope, args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
