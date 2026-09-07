#!/usr/bin/env python3
"""Render book-level ``introduction_content.yaml`` to public Obsidian Markdown.

Schema v3 keeps a stable editorial reading order while allowing irrelevant
modules to disappear. The renderer owns module order and Markdown structure;
the content payload owns prose and source attribution.

Canonical public output: ``<book_folder>/書卷導論.md``.

Project boundary: 「模型不碰結構，程式不碰內容」。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Iterable

import yaml

ROOT = Path(__file__).resolve().parent.parent

MODULE_ORDER = (
    "identity",
    "authorship_context",
    "message_purpose",
    "importance_features",
    "structure",
    "key_texts_themes",
    "canonical_relationship",
)

DEFAULT_TITLES = {
    "identity": "書名",
    "authorship_context": "作者、成書與背景",
    "message_purpose": "主旨與寫作目的",
    "importance_features": "本書的重要性與特色",
    "structure": "全書結構",
    "key_texts_themes": "鑰節、鑰字與核心主題",
    "canonical_relationship": "與其他書卷的關係",
}


def _load(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: YAML root must be a mapping")
    return data


def _normalize_prose(value: Any) -> str:
    """Normalize only prose values loaded from YAML folded scalars.

    YAML ``>-`` joins physical lines with one ASCII space. Traditional Chinese
    normally does not want that space after Chinese punctuation or between
    adjacent CJK tokens. This function is deliberately applied *before* Markdown
    structure is assembled, so table delimiters, reference labels and URLs are
    never rewritten.
    """
    text = str(value or "").strip()
    text = re.sub(r"(?<=[，。！？；：、）」』】》]) +(?=\S)", "", text)
    text = re.sub(r"(?<=[\u3400-\u9fff]) +(?=[\u3400-\u9fff「『（【《])", "", text)
    text = re.sub(r"(?<=—) +(?=[\u3400-\u9fff「『（【《])", "", text)
    return text


def _sources(ids: Any) -> str:
    values = [str(v).strip() for v in (ids or []) if str(v).strip()]
    return f"<!-- sources: {', '.join(values)} -->" if values else ""


def _paras(values: Any) -> str:
    return "\n\n".join(_normalize_prose(v) for v in (values or []) if str(v).strip())


def _mermaid(code: Any) -> str:
    text = str(code or "").strip()
    return f"```mermaid\n{text}\n```" if text else ""


def _callout(spec: Any) -> str:
    if not isinstance(spec, dict):
        return ""
    body = _normalize_prose(spec.get("body", ""))
    if not body:
        return ""
    kind = str(spec.get("kind", "note")).strip() or "note"
    title = str(spec.get("title", "")).strip()
    first = f"> [!{kind}] {title}" if title else f"> [!{kind}]"
    lines = [first]
    for line in body.splitlines():
        lines.append(f"> {line}" if line else ">")
    return "\n".join(lines)


def _table(headers: list[str], rows: Iterable[Iterable[Any]]) -> str:
    clean_headers = [str(v).strip() for v in headers]
    lines = [
        "| " + " | ".join(clean_headers) + " |",
        "| " + " | ".join("---" for _ in clean_headers) + " |",
    ]
    for row in rows:
        values = [_normalize_prose(v).replace("\n", "<br/>") for v in row]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def _render_overview(spec: dict[str, Any]) -> str:
    rows = spec.get("rows") or []
    if not rows:
        return ""
    table_rows = [(item.get("label", ""), item.get("value", "")) for item in rows]
    body = _table(["項目", "資料"], table_rows)
    title = str(spec.get("title") or "一覽").strip()
    section = f"## {title}\n\n{body}"
    source_comment = _sources(spec.get("source_ids"))
    if source_comment:
        section += f"\n\n{source_comment}"
    return section


def _render_identity(module: dict[str, Any]) -> str:
    parts = [_paras(module.get("paragraphs"))]
    if module.get("callout"):
        parts.append(_callout(module["callout"]))
    return "\n\n".join(p for p in parts if p)


def _render_authorship_context(module: dict[str, Any]) -> str:
    parts = [_paras(module.get("paragraphs"))]
    facts = module.get("facts") or []
    if facts:
        rows = [(item.get("label", ""), item.get("value", "")) for item in facts]
        parts.append(_table(["要分開看的問題", "本卷導論的處理"], rows))
    if module.get("callout"):
        parts.append(_callout(module["callout"]))
    return "\n\n".join(p for p in parts if p)


def _render_message_purpose(module: dict[str, Any]) -> str:
    parts = [_paras(module.get("paragraphs"))]
    if module.get("mermaid"):
        parts.append(_mermaid(module["mermaid"]))
    if module.get("callout"):
        parts.append(_callout(module["callout"]))
    return "\n\n".join(p for p in parts if p)


def _render_importance_features(module: dict[str, Any]) -> str:
    parts = [_paras(module.get("paragraphs"))]
    features = module.get("features") or []
    if features:
        lines: list[str] = []
        for item in features:
            title = str(item.get("title", "")).strip()
            text = _normalize_prose(item.get("text", ""))
            if title and text:
                lines.append(f"**{title}**  \n{text}")
        if lines:
            parts.append("\n\n".join(lines))
    if module.get("callout"):
        parts.append(_callout(module["callout"]))
    return "\n\n".join(p for p in parts if p)


def _render_structure(module: dict[str, Any]) -> str:
    parts = [_paras(module.get("paragraphs"))]
    if module.get("mermaid"):
        parts.append(_mermaid(module["mermaid"]))
    outline = module.get("outline") or []
    if outline:
        rows = [
            (item.get("range", ""), item.get("label", ""), item.get("summary", ""))
            for item in outline
        ]
        parts.append(_table(["範圍", "段落", "內容重點"], rows))
    if module.get("callout"):
        parts.append(_callout(module["callout"]))
    return "\n\n".join(p for p in parts if p)


def _render_key_texts_themes(module: dict[str, Any]) -> str:
    parts = [_paras(module.get("paragraphs"))]
    key_texts = module.get("key_texts") or []
    if key_texts:
        rows = [(item.get("ref", ""), item.get("significance", "")) for item in key_texts]
        parts.append(_table(["經文", "在全書中的位置"], rows))
    key_words = [str(v).strip() for v in (module.get("key_words") or []) if str(v).strip()]
    if key_words:
        parts.append("**鑰字／重複線索：** " + "、".join(key_words))
    themes = module.get("themes") or []
    if themes:
        lines = []
        for item in themes:
            name = str(item.get("name", "")).strip()
            text = _normalize_prose(item.get("text", ""))
            if name and text:
                lines.append(f"- **{name}**：{text}")
        if lines:
            parts.append("\n".join(lines))
    if module.get("callout"):
        parts.append(_callout(module["callout"]))
    return "\n\n".join(p for p in parts if p)


def _render_canonical_relationship(module: dict[str, Any]) -> str:
    parts = [_paras(module.get("paragraphs"))]
    if module.get("mermaid"):
        parts.append(_mermaid(module["mermaid"]))
    if module.get("callout"):
        parts.append(_callout(module["callout"]))
    return "\n\n".join(p for p in parts if p)


RENDERERS = {
    "identity": _render_identity,
    "authorship_context": _render_authorship_context,
    "message_purpose": _render_message_purpose,
    "importance_features": _render_importance_features,
    "structure": _render_structure,
    "key_texts_themes": _render_key_texts_themes,
    "canonical_relationship": _render_canonical_relationship,
}


def _render_references(data: dict[str, Any]) -> str:
    refs = data.get("references") or []
    if not refs:
        return ""
    policy = data.get("source_policy") or {}
    lines = ["> [!info]- 本頁來源與方法", ">"]
    lines.append(
        "> 本頁以 **CT00 的書卷提要節奏作為編排參考**；CT00、GT00、KC0、BH 是四套既有註釋來源，"
        "BibleProject、Enter the Bible、Yale 屬補強層，不加入四家共識票數。"
    )
    lines.append(">")
    for ref in refs:
        label = str(ref.get("label", "")).strip()
        url = str(ref.get("url", "")).strip()
        rid = str(ref.get("id", "")).strip()
        if label and url:
            lines.append(f"> - **{rid}**｜[{label}]({url})")
    note = _normalize_prose(policy.get("public_note", ""))
    if note:
        lines.extend([">", *[f"> {line}" if line else ">" for line in note.splitlines()]])
    return "\n".join(lines)


def render(data: dict[str, Any]) -> str:
    if int(data.get("schema_version", 0)) != 3:
        raise ValueError("render_book_introduction.py expects schema_version: 3")

    book = str(data.get("book", "")).strip()
    if not book:
        raise ValueError("book is required")

    blocks: list[str] = []
    nav = data.get("navigation") or {}
    nav_block = "\n".join(
        [
            "<!-- book-introduction-navigation:start -->",
            f"| {nav.get('outline', '')} | {nav.get('first_chapter', '')} |",
            "| :--- | ---: |",
            "<!-- book-introduction-navigation:end -->",
        ]
    )
    blocks.append(nav_block)

    header = data.get("header") or {}
    title = str(header.get("title") or book).strip()
    subtitle = str(header.get("subtitle", "")).strip()
    lead = _normalize_prose(header.get("lead", ""))
    header_lines = [f"# {title}"]
    if subtitle:
        header_lines.extend(["", f"*{subtitle}*"])
    if lead:
        header_lines.extend(["", lead])
    source_comment = _sources(header.get("source_ids"))
    if source_comment:
        header_lines.extend(["", source_comment])
    blocks.append("\n".join(header_lines))

    overview = data.get("overview")
    if isinstance(overview, dict):
        overview_block = _render_overview(overview).strip()
        if overview_block:
            blocks.append(overview_block)

    modules = data.get("modules") or {}
    if not isinstance(modules, dict):
        raise ValueError("modules must be a mapping")
    unknown = sorted(set(modules) - set(MODULE_ORDER))
    if unknown:
        raise ValueError(f"unknown introduction modules: {', '.join(unknown)}")

    for module_id in MODULE_ORDER:
        module = modules.get(module_id)
        if not isinstance(module, dict) or module.get("enabled") is False:
            continue
        body = RENDERERS[module_id](module).strip()
        if not body:
            continue
        title = str(module.get("title") or DEFAULT_TITLES[module_id]).strip()
        section = f"## {title}\n\n{body}"
        source_comment = _sources(module.get("source_ids"))
        if source_comment:
            section += f"\n\n{source_comment}"
        blocks.append(section)

    references = _render_references(data)
    if references:
        blocks.append(references)

    blocks.append(nav_block)
    return "\n\n---\n\n".join(block.rstrip() for block in blocks if block.strip()) + "\n"


def main() -> int:
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8")  # Windows cp1252 保險絲
    parser = argparse.ArgumentParser(description="Render a book 書卷導論.md")
    parser.add_argument("content", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    content_path = args.content if args.content.is_absolute() else ROOT / args.content
    data = _load(content_path)
    rendered = render(data)

    output = args.output
    if output is None:
        folder = str(data.get("book_folder", "")).strip()
        if not folder:
            raise ValueError("book_folder is required when --output is omitted")
        output = ROOT / folder / "書卷導論.md"
    elif not output.is_absolute():
        output = ROOT / output

    if args.write:
        if output.exists() and not args.force:
            raise FileExistsError(f"{output} exists; use --force to replace")
        output.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"✅ 已寫入：{output.relative_to(ROOT)}")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
