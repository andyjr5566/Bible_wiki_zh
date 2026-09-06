#!/usr/bin/env python3
"""Render book-level ``introduction_content.yaml`` to Obsidian Markdown.

Schema v2 intentionally follows the familiar CT00 book-introduction rhythm:
book name -> author/composition -> writing time/background -> purpose ->
importance -> features -> relation to other books -> key verses/words -> outline.
External sources enrich those sections without replacing that narrative spine.

Project boundary remains: 「模型不碰結構，程式不碰內容」。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent


def _load(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: YAML root must be a mapping")
    return data


def _sources(ids: Any) -> str:
    values = [str(v).strip() for v in (ids or []) if str(v).strip()]
    return f"<!-- sources: {', '.join(values)} -->" if values else ""


def _paras(values: Any) -> str:
    return "\n\n".join(str(v).strip() for v in (values or []) if str(v).strip())


def _mermaid(code: Any) -> str:
    text = str(code or "").strip()
    return f"```mermaid\n{text}\n```" if text else ""


def _callout(kind: str, title: str, body: str) -> str:
    lines = [f"> [!{kind}] {title}"]
    for line in str(body).strip().splitlines():
        lines.append(f"> {line}" if line else ">")
    return "\n".join(lines)


def _section(title: str, paragraphs: Any, source_ids: Any = None) -> str:
    body = _paras(paragraphs)
    parts = [f"## {title}"]
    if body:
        parts += ["", body]
    source = _sources(source_ids)
    if source:
        parts += ["", source]
    return "\n".join(parts)


def render(data: dict[str, Any]) -> str:
    if int(data.get("schema_version", 0)) != 2:
        raise ValueError("render_book_introduction.py expects schema_version: 2")

    book = str(data.get("book", "")).strip()
    if not book:
        raise ValueError("book is required")

    nav = data.get("navigation") or {}
    nav_block = "\n".join([
        "<!-- book-introduction-navigation:start -->",
        f"| {nav.get('outline', '')} | {nav.get('first_chapter', '')} |",
        "| :--- | ---: |",
        "<!-- book-introduction-navigation:end -->",
    ])

    blocks: list[str] = [nav_block]

    hero = data.get("hero") or {}
    hero_lines = [f"# {hero.get('title') or book}"]
    if hero.get("eyebrow"):
        hero_lines += ["", f"*{str(hero['eyebrow']).strip()}*"]
    if hero.get("lead"):
        hero_lines += ["", str(hero["lead"]).strip()]
    if hero.get("source_ids"):
        hero_lines += ["", _sources(hero.get("source_ids"))]
    blocks.append("\n".join(hero_lines))

    facts = data.get("quick_facts") or []
    lines = ["## 一覽", "", "| 項目 | 資料 |", "| --- | --- |"]
    all_sources: list[str] = []
    for item in facts:
        lines.append(f"| **{item.get('label', '')}** | {item.get('value', '')} |")
        all_sources.extend(item.get("sources") or [])
    lines += ["", _sources(dict.fromkeys(all_sources))]
    blocks.append("\n".join(lines).rstrip())

    # 壹、書名
    name = data.get("book_name") or {}
    name_lines = [f"## 壹、{name.get('title', '書名')}", "", _paras(name.get("paragraphs"))]
    if name.get("callout"):
        c = name["callout"]
        name_lines += ["", _callout(c.get("kind", "note"), c.get("title", "補充"), c.get("body", ""))]
    name_lines += ["", _sources(name.get("source_ids"))]
    blocks.append("\n".join(name_lines).rstrip())

    # 貳、作者與成書
    authorship = data.get("authorship") or {}
    a_lines = [f"## 貳、{authorship.get('title', '作者與成書')}", "", _paras(authorship.get("paragraphs"))]
    views = authorship.get("views") or []
    if views:
        a_lines += ["", "| 問題 | 說明 |", "| --- | --- |"]
        for item in views:
            a_lines.append(f"| **{item.get('label', '')}** | {item.get('text', '')} |")
    if authorship.get("mermaid"):
        a_lines += ["", _mermaid(authorship.get("mermaid"))]
    if authorship.get("callout"):
        c = authorship["callout"]
        a_lines += ["", _callout(c.get("kind", "important"), c.get("title", "閱讀提醒"), c.get("body", ""))]
    a_lines += ["", _sources(authorship.get("source_ids"))]
    blocks.append("\n".join(a_lines).rstrip())

    # 叁、寫作時地與背景
    bg = data.get("time_and_background") or {}
    b_lines = [f"## 叁、{bg.get('title', '寫作時地與背景')}", "", _paras(bg.get("paragraphs"))]
    if bg.get("timeline_mermaid"):
        b_lines += ["", _mermaid(bg.get("timeline_mermaid"))]
    if bg.get("background_points"):
        b_lines += [""] + [f"- {item}" for item in bg.get("background_points")]
    if bg.get("callout"):
        c = bg["callout"]
        b_lines += ["", _callout(c.get("kind", "note"), c.get("title", "背景補充"), c.get("body", ""))]
    b_lines += ["", _sources(bg.get("source_ids"))]
    blocks.append("\n".join(b_lines).rstrip())

    # 肆、主旨要義
    theme = data.get("main_message") or {}
    t_lines = [f"## 肆、{theme.get('title', '主旨要義')}", "", _paras(theme.get("paragraphs"))]
    if theme.get("mermaid"):
        t_lines += ["", _mermaid(theme.get("mermaid"))]
    if theme.get("theme_table"):
        t_lines += ["", "| 主線 | 在《創世記》中如何展開 |", "| --- | --- |"]
        for item in theme.get("theme_table"):
            t_lines.append(f"| **{item.get('name', '')}** | {item.get('text', '')} |")
    t_lines += ["", _sources(theme.get("source_ids"))]
    blocks.append("\n".join(t_lines).rstrip())

    # 伍、寫作目的與原始讀者
    purpose = data.get("purpose") or {}
    blocks.append(_section(f"伍、{purpose.get('title', '寫作目的與原始讀者')}", purpose.get("paragraphs"), purpose.get("source_ids")))

    # 陸、本書的重要性
    importance = data.get("importance") or {}
    i_lines = [f"## 陸、{importance.get('title', '本書的重要性')}", "", _paras(importance.get("paragraphs"))]
    if importance.get("points"):
        i_lines += [""] + [f"{idx}. {item}" for idx, item in enumerate(importance.get("points"), 1)]
    i_lines += ["", _sources(importance.get("source_ids"))]
    blocks.append("\n".join(i_lines).rstrip())

    # 柒、本書的特點
    features = data.get("features") or {}
    f_lines = [f"## 柒、{features.get('title', '本書的特點')}", ""]
    for item in features.get("items") or []:
        f_lines += [f"### {item.get('title', '')}", str(item.get("text", "")).strip(), ""]
    if features.get("callout"):
        c = features["callout"]
        f_lines += [_callout(c.get("kind", "tip"), c.get("title", "閱讀提示"), c.get("body", "")), ""]
    f_lines += [_sources(features.get("source_ids"))]
    blocks.append("\n".join(f_lines).rstrip())

    # 捌、與其他書卷關係
    relation = data.get("relationships") or {}
    r_lines = [f"## 捌、{relation.get('title', '與其他聖經書卷的關係')}", "", _paras(relation.get("paragraphs"))]
    if relation.get("mermaid"):
        r_lines += ["", _mermaid(relation.get("mermaid"))]
    r_lines += ["", _sources(relation.get("source_ids"))]
    blocks.append("\n".join(r_lines).rstrip())

    # 玖、鑰節；拾、鑰字
    keys = data.get("keys") or {}
    k_lines = ["## 玖、鑰節", ""]
    for item in keys.get("verses") or []:
        k_lines += [f"> **{item.get('ref', '')}**　{item.get('text', '')}", ""]
    k_lines += ["## 拾、鑰字", ""]
    for item in keys.get("words") or []:
        k_lines.append(f"- **{item.get('word', '')}**：{item.get('note', '')}")
    k_lines += ["", _sources(keys.get("source_ids"))]
    blocks.append("\n".join(k_lines).rstrip())

    # 拾壹、內容大綱
    outline = data.get("outline") or {}
    o_lines = [f"## 拾壹、{outline.get('title', '內容大綱')}", "", str(outline.get("intro", "")).strip()]
    if outline.get("mermaid"):
        o_lines += ["", _mermaid(outline.get("mermaid"))]
    o_lines += ["", "| 範圍 | 段落 | 內容 |", "| --- | --- | --- |"]
    for item in outline.get("sections") or []:
        o_lines.append(f"| **{item.get('range', '')}** | {item.get('label', '')} | {item.get('summary', '')} |")
    if outline.get("callout"):
        c = outline["callout"]
        o_lines += ["", _callout(c.get("kind", "tip"), c.get("title", "結構提示"), c.get("body", ""))]
    o_lines += ["", _sources(outline.get("source_ids"))]
    blocks.append("\n".join(o_lines).rstrip())

    # 拾貳、補充導讀：專收外部補強層真正有用、但不適合塞進 CT00 主骨架的內容。
    extra = data.get("supplement") or {}
    if extra:
        e_lines = [f"## 拾貳、{extra.get('title', '補充導讀')}", "", _paras(extra.get("paragraphs"))]
        for item in extra.get("items") or []:
            e_lines += ["", f"### {item.get('title', '')}", str(item.get("text", "")).strip()]
        if extra.get("callout"):
            c = extra["callout"]
            e_lines += ["", _callout(c.get("kind", "question"), c.get("title", "閱讀時可以問"), c.get("body", ""))]
        e_lines += ["", _sources(extra.get("source_ids"))]
        blocks.append("\n".join(e_lines).rstrip())

    refs = data.get("references") or []
    ref_lines = ["> [!info]- 本頁來源與方法", ">", "> **四套既有註釋來源**：CT00、GT00、KC0、BH。BibleProject、Enter the Bible、Yale 為補強層，不加入四家註釋的共識票數。", ">"]
    for ref in refs:
        ref_lines.append(f"> - **{ref.get('id', '')}**｜[{ref.get('label', '')}]({ref.get('url', '')})")
    ref_lines += [">", "> 本頁以 CT00 的傳統書卷提要章法作為正文主骨架；其他來源用來補充文學結構、背景、學術成書觀與來源分歧。GT00 為多來源合輯，引用其中個別觀點時必須保留子來源身分。"]
    blocks.append("\n".join(ref_lines))

    blocks.append(nav_block)
    return "\n\n---\n\n".join(block.rstrip() for block in blocks if block.strip()) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a book Introduction.md")
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
        output = ROOT / folder / "Introduction.md"
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
