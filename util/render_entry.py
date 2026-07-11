#!/usr/bin/env python3
"""從 entry_content payload 渲染 link_folder 條目 markdown。

模型只填 payload（YAML/JSON 欄位值），最終 markdown 一律由本程式生成，
確保 frontmatter、H2 順序、按書卷累積標記與 alias 格式永遠合規。結構
不再由模型「順便」寫出，因此不可能寫錯模板。

payload 契約見 ``_config/schemas/entry_content.schema.json``；本程式在
Python 端對照真實資料（link_folder 分類、bible_books.json）強制其中無法
由靜態 JSON Schema 表達的語義規則，不合格即拒絕渲染。
"""
import argparse
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
LINK_FOLDER = ROOT / "link_folder"
SCHEMA_PATH = ROOT / "_config" / "schemas" / "entry_content.schema.json"
BOOK_CHAPTERS = json.loads(
    (ROOT / "_config" / "bible_books.json").read_text(encoding="utf-8")
)
BOOK_ORDER = list(BOOK_CHAPTERS)
BOOK_RANK = {book: index for index, book in enumerate(BOOK_ORDER)}

VALID_STATUS = {"formal", "candidate"}
# Windows 檔名不可含半形 :（會被當成 NTFS 資料流，留下 0-byte 空檔）。互文條目
# 慣例用全形 ：（如「來10：19-20」），故半形冒號一律正規化為全形、不視為不安全。
UNSAFE_NAME_CHARS = set('/\\<>"|?*')
ACCUMULATION_FIELDS = ("book", "chapter", "summary", "relation")


def safe_name(name):
    """把條目名正規化為檔名安全形式：半形 : → 全形 ：（符合互文命名慣例）。"""
    return str(name).replace(":", "：").strip()
# 互文條目不可只有經文引用（如 來9:23-24、啟21:23）；須用「簡短標題（經文）」
BARE_SCRIPTURE_REF_RE = re.compile(r"^[一-鿿]{1,4}\d+([:：][\d\-,，]+)?$")


def valid_types():
    """link_folder 下實際存在的分類資料夾名（type 的合法值）。"""
    if not LINK_FOLDER.is_dir():
        return set()
    return {
        path.name
        for path in LINK_FOLDER.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    }


# --------------------------------------------------------------------------- #
# 驗證（驗證左移：payload 層擋掉結構／語義錯誤，不到成品才發現）
# --------------------------------------------------------------------------- #
def validate_payload(payload, *, known_types=None):
    """回傳 error 列表；非空即不得渲染。"""
    errors = []
    if not isinstance(payload, dict):
        return ["payload 必須是物件（mapping）"]

    name = payload.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append("name 必填且不可為空")
    else:
        name = safe_name(name)  # 半形冒號正規化為全形後再檢查
        if UNSAFE_NAME_CHARS & set(name):
            bad = "".join(sorted(UNSAFE_NAME_CHARS & set(name)))
            errors.append(f"name 含檔案系統不安全字元：{bad}")

    types = valid_types() if known_types is None else set(known_types)
    entry_type = payload.get("type")
    if not isinstance(entry_type, str) or not entry_type.strip():
        errors.append("type 必填")
    elif types and entry_type not in types:
        errors.append(
            f"type「{entry_type}」不是 link_folder 下的合法分類；"
            f"合法值：{', '.join(sorted(types))}"
        )

    if entry_type == "互文" and isinstance(name, str) and BARE_SCRIPTURE_REF_RE.match(name.strip()):
        errors.append(
            f"互文條目 name「{name}」不可只有經文引用，須用「簡短標題（經文）」，"
            "例如「天上真聖所（來9:23-24）」"
        )

    status = payload.get("status")
    if status not in VALID_STATUS:
        errors.append("status 必須是 formal 或 candidate")

    for field in ("secondary_types", "aliases"):
        value = payload.get(field, [])
        if not isinstance(value, list) or any(not isinstance(v, str) for v in value):
            errors.append(f"{field} 必須是字串陣列")

    if status == "formal":
        errors.extend(_validate_formal(payload))
    elif status == "candidate":
        errors.extend(_validate_candidate(payload))
    return errors


def _validate_formal(payload):
    errors = []
    if not str(payload.get("definition", "")).strip():
        errors.append("formal 條目 definition（定義）必填且不可為空")

    accums = payload.get("accumulations")
    if not isinstance(accums, list) or not accums:
        errors.append("formal 條目 accumulations（按書卷累積）至少需一項")
    else:
        for index, item in enumerate(accums):
            errors.extend(_validate_accumulation(item, index))

    sources = payload.get("sources")
    if not isinstance(sources, list) or not [s for s in sources if str(s).strip()]:
        errors.append("formal 條目 sources（來源依據）至少需一項")
    elif any(not isinstance(s, str) for s in sources):
        errors.append("sources 必須是字串陣列")

    related = payload.get("related_entries", [])
    if not isinstance(related, list) or any(not isinstance(r, str) for r in related):
        errors.append("related_entries 必須是字串陣列")
    return errors


def _validate_accumulation(item, index):
    prefix = f"accumulations[{index}]"
    if not isinstance(item, dict):
        return [f"{prefix} 必須是物件"]
    errors = []
    book = item.get("book")
    if book not in BOOK_RANK:
        errors.append(f"{prefix}.book「{book}」不在 bible_books.json 內")
    chapter = item.get("chapter")
    if not isinstance(chapter, int) or isinstance(chapter, bool) or chapter < 1:
        errors.append(f"{prefix}.chapter 必須是 ≥1 的整數")
    elif book in BOOK_CHAPTERS and chapter > BOOK_CHAPTERS[book]:
        errors.append(
            f"{prefix}.chapter {chapter} 超出「{book}」章數（{BOOK_CHAPTERS[book]}）"
        )
    for field in ("summary", "relation"):
        if not str(item.get(field, "")).strip():
            errors.append(f"{prefix}.{field} 必填且不可為空")
    return errors


def _validate_candidate(payload):
    errors = []
    triggers = payload.get("trigger_sources")
    if not isinstance(triggers, list) or not [t for t in triggers if str(t).strip()]:
        errors.append("candidate 條目 trigger_sources（觸發來源）至少需一項")
    elif any(not isinstance(t, str) for t in triggers):
        errors.append("trigger_sources 必須是字串陣列")
    if not str(payload.get("current_data", "")).strip():
        errors.append("candidate 條目 current_data（目前資料）必填且不可為空")
    related = payload.get("related_entries", [])
    if not isinstance(related, list) or any(not isinstance(r, str) for r in related):
        errors.append("related_entries 必須是字串陣列")
    return errors


# --------------------------------------------------------------------------- #
# 渲染
# --------------------------------------------------------------------------- #
def _frontmatter(payload):
    fm = OrderedDict()
    fm["type"] = payload["type"]
    fm["secondary_types"] = payload.get("secondary_types", []) or []
    fm["aliases"] = payload.get("aliases", []) or []
    fm["status"] = payload["status"]
    if payload["status"] == "candidate" and str(payload.get("created_from", "")).strip():
        fm["created_from"] = payload["created_from"].strip()
    fm["source_scope"] = "collected_only"
    return fm


def _wikilink(inner):
    """把相關條目內文包成 [[...]]；容忍模型已寫成 [[x]] 的情況。"""
    inner = inner.strip()
    match = re.fullmatch(r"\[\[(.+?)\]\]", inner)
    if match:
        inner = match.group(1).strip()
    return f"[[{inner}]]"


# GFM/Obsidian 只在 URL 前是行首、空白或半形 ( 時自動連結；來源依據慣用
# 「標籤: 位置說明（URL）」，全形括號緊貼 URL 使其渲染後不可點。渲染時把
# 這類 URL 包成 <URL>（CommonMark 顯式 autolink）；本可自動連結或已包 <>
# 的 URL 維持原樣，確保既有條目 round-trip 不變、重渲染冪等。
_UNLINKABLE_URL_RE = re.compile(r"(?<=[^\s(<\[])(https?://[^\s<>（）]+)")


def linkify_urls(text):
    return _UNLINKABLE_URL_RE.sub(r"<\1>", text)


def _render_accumulations(accums):
    # 同一 (書卷, 章) 只能有一個累積標記區塊；模型常為不同節次各給一筆，
    # 這裡依 (書卷, 章) 合併 summary／relation，避免重複標記。
    merged = {}
    for item in accums:
        key = (item["book"], int(item["chapter"]))
        bucket = merged.setdefault(key, {"summaries": [], "relations": []})
        summary = str(item.get("summary", "")).strip()
        relation = str(item.get("relation", "")).strip()
        if summary and summary not in bucket["summaries"]:
            bucket["summaries"].append(summary)
        if relation and relation not in bucket["relations"]:
            bucket["relations"].append(relation)
    by_book = {}
    for book, chapter in merged:
        by_book.setdefault(book, set()).add(chapter)
    parts = []
    for book in sorted(by_book, key=lambda b: (BOOK_RANK.get(b, 999), b)):
        blocks = []
        for chapter in sorted(by_book[book]):
            bucket = merged[(book, chapter)]
            block = (
                f"<!-- accumulation:{book}:{chapter}:start -->\n"
                f"#### 第{chapter}章\n"
                f"- 本章重點：{'；'.join(bucket['summaries'])}\n"
                f"- 與本章關聯：{'；'.join(bucket['relations'])}\n"
                f"<!-- accumulation:{book}:{chapter}:end -->"
            )
            blocks.append(block)
        parts.append(f"### {book}\n\n" + "\n\n".join(blocks))
    return "\n\n".join(parts)


def _render_formal(payload):
    parts = [
        f"# {payload['name']}",
        f"## 定義\n\n{payload['definition'].strip()}",
        f"## 按書卷累積\n\n{_render_accumulations(payload['accumulations'])}",
    ]
    development = str(payload.get("development", "")).strip()
    if development:
        parts.append(f"## 主題發展\n\n{development}")
    related = [r for r in (payload.get("related_entries") or []) if r.strip()]
    if related:
        related_body = "\n".join(f"- {_wikilink(item)}" for item in related)
        parts.append(f"## 相關條目\n\n{related_body}")
    source_body = "\n".join(
        f"- {linkify_urls(str(source).strip())}"
        for source in payload["sources"]
        if str(source).strip()
    )
    parts.append(f"## 來源依據\n\n{source_body}")
    return "\n\n".join(part.rstrip() for part in parts).rstrip() + "\n"


def _render_candidate(payload):
    category = str(payload.get("category", "")).strip() or payload["type"]
    trigger_body = "\n".join(
        f"- {str(trigger).strip()}"
        for trigger in payload["trigger_sources"]
        if str(trigger).strip()
    )
    related = [r for r in (payload.get("related_entries") or []) if r.strip()]
    related_body = "\n".join(f"- {_wikilink(item)}" for item in related)
    parts = [
        f"# {payload['name']}",
        f"## 類型\n\n{category}",
        f"## 觸發來源\n\n{trigger_body}",
        f"## 目前資料\n\n{str(payload['current_data']).strip()}",
        f"## 相關條目\n\n{related_body}",
        f"## 待補充\n\n{str(payload.get('pending', '')).strip()}",
    ]
    return "\n\n".join(part.rstrip() for part in parts).rstrip() + "\n"


def render_entry(payload, *, known_types=None):
    """payload → 條目 markdown 全文（含 frontmatter）。不合格則丟 ValueError。"""
    errors = validate_payload(payload, known_types=known_types)
    if errors:
        raise ValueError("payload 驗證失敗：\n- " + "\n- ".join(errors))
    payload = {**payload, "name": safe_name(payload["name"])}
    fm = _frontmatter(payload)
    yaml_text = yaml.safe_dump(
        dict(fm), allow_unicode=True, sort_keys=False, default_flow_style=False
    ).strip()
    body = (
        _render_candidate(payload)
        if payload["status"] == "candidate"
        else _render_formal(payload)
    )
    return f"---\n{yaml_text}\n---\n\n{body}"


def entry_path(payload):
    return LINK_FOLDER / payload["type"] / f"{safe_name(payload['name'])}.md"


# --------------------------------------------------------------------------- #
# 反向解析（供 round-trip 測試與既有條目遷移）
# --------------------------------------------------------------------------- #
def _split_frontmatter(text):
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.DOTALL)
    if not match:
        return {}, text
    data = yaml.safe_load(match.group(1)) or {}
    return (data if isinstance(data, dict) else {}), text[match.end():]


def _sections(body):
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", body, re.M))
    result = OrderedDict()
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        result[match.group(1).strip()] = body[match.end():end].strip()
    return result


def _bullets(section):
    return [
        line.strip()[2:].strip()
        for line in section.splitlines()
        if line.strip().startswith("- ")
    ]


def _parse_accumulations(section):
    accums = []
    pattern = re.compile(
        r"<!-- accumulation:(?P<book>[^:]+):(?P<chapter>\d+):start -->"
        r"(?P<body>[\s\S]*?)<!-- accumulation:(?P=book):(?P=chapter):end -->"
    )
    for match in pattern.finditer(section):
        block = match.group("body")
        summary = re.search(r"^- 本章重點：(.*)$", block, re.M)
        relation = re.search(r"^- 與本章關聯：(.*)$", block, re.M)
        accums.append({
            "book": match.group("book"),
            "chapter": int(match.group("chapter")),
            "summary": summary.group(1).strip() if summary else "",
            "relation": relation.group(1).strip() if relation else "",
        })
    return accums


def parse_entry(text):
    """條目 markdown → payload（render_entry 的反向操作，用於遷移／測試）。"""
    fm, body = _split_frontmatter(text)
    heading = re.search(r"^#\s+(.+?)\s*$", body, re.M)
    payload = {
        "name": heading.group(1).strip() if heading else "",
        "type": fm.get("type", ""),
        "secondary_types": fm.get("secondary_types", []) or [],
        "aliases": fm.get("aliases", []) or [],
        "status": fm.get("status", ""),
    }
    sections = _sections(body)
    if payload["status"] == "candidate":
        if fm.get("created_from"):
            payload["created_from"] = fm["created_from"]
        payload["category"] = sections.get("類型", "").strip()
        payload["trigger_sources"] = _bullets(sections.get("觸發來源", ""))
        payload["current_data"] = sections.get("目前資料", "").strip()
        payload["related_entries"] = [
            _wikilink(item)[2:-2] for item in _bullets(sections.get("相關條目", ""))
        ]
        payload["pending"] = sections.get("待補充", "").strip()
    else:
        payload["definition"] = sections.get("定義", "").strip()
        payload["accumulations"] = _parse_accumulations(sections.get("按書卷累積", ""))
        if sections.get("主題發展", "").strip():
            payload["development"] = sections["主題發展"].strip()
        payload["related_entries"] = [
            _wikilink(item)[2:-2] for item in _bullets(sections.get("相關條目", ""))
        ]
        payload["sources"] = _bullets(sections.get("來源依據", ""))
    return payload


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _load_payload(path):
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: payload 必須是 YAML/JSON 物件")
    return data


def _cmd_render(args):
    payload = _load_payload(args.payload)
    rendered = render_entry(payload)
    if args.write:
        target = entry_path(payload)
        if target.exists() and not args.force:
            raise FileExistsError(f"{target} 已存在；加 --force 才覆蓋")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
        print(f"✅ 已寫入：{target.relative_to(ROOT)}")
    else:
        sys.stdout.write(rendered)
    return 0


def _cmd_extract(args):
    payload = parse_entry(args.entry.read_text(encoding="utf-8"))
    sys.stdout.write(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False)
    )
    return 0


def main():
    # 條目名稱與內容含中文；在 Windows cp1252 stdout 下直接 print 會 UnicodeEncodeError。
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    render_parser = sub.add_parser("render", help="payload → 條目 markdown")
    render_parser.add_argument("payload", type=Path, help="entry_content.yaml 路徑")
    render_parser.add_argument("--write", action="store_true", help="寫入 link_folder")
    render_parser.add_argument("--force", action="store_true", help="允許覆蓋既有檔")
    render_parser.set_defaults(func=_cmd_render)

    extract_parser = sub.add_parser("extract", help="既有條目 markdown → payload")
    extract_parser.add_argument("entry", type=Path, help="條目 .md 路徑")
    extract_parser.set_defaults(func=_cmd_extract)

    args = parser.parse_args()
    try:
        return args.func(args)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"❌ {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
