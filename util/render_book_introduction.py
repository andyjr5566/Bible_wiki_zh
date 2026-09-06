#!/usr/bin/env python3
"""Render ``introduction_content.yaml`` into a public-facing Obsidian Markdown page.

The model owns semantic content in YAML; this program owns section order,
headings, tables, Mermaid fences, source provenance comments and references.
This mirrors the chapter rule: 「模型不碰結構，程式不碰內容」。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def _load(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: YAML root must be a mapping")
    return data


def _sources(ids) -> str:
    values = [str(value).strip() for value in (ids or []) if str(value).strip()]
    return f"<!-- sources: {', '.join(values)} -->" if values else ""


def _paragraphs(values) -> str:
    return "\n\n".join(str(value).strip() for value in (values or []) if str(value).strip())


def _mermaid(code: str) -> str:
    code = str(code or "").strip()
    return f"```mermaid\n{code}\n```" if code else ""


def _source_comment_from_items(items) -> str:
    ids = []
    for item in items or []:
        if isinstance(item, dict):
            ids.extend(item.get("sources") or [])
    return _sources(dict.fromkeys(str(value) for value in ids))


def render(data: dict) -> str:
    book = str(data.get("book", "")).strip()
    if not book:
        raise ValueError("book is required")

    blocks: list[str] = []
    nav = data.get("navigation") or {}
    blocks.append(
        "\n".join(
            [
                "<!-- book-introduction-navigation:start -->",
                f"| {nav.get('outline', '')} | {nav.get('first_chapter', '')} |",
                "| :--- | ---: |",
                "<!-- book-introduction-navigation:end -->",
            ]
        )
    )

    hero = data.get("hero") or {}
    blocks.append(
        "\n".join(
            line
            for line in [
                f"# {hero.get('title') or book}",
                f"*{hero.get('eyebrow', '').strip()}*" if hero.get("eyebrow") else "",
                "",
                str(hero.get("lead", "")).strip(),
                "",
                _sources(hero.get("source_ids")),
            ]
            if line != ""
        )
    )

    facts = data.get("quick_facts") or []
    fact_lines = ["## 一分鐘認識這卷書", "", "| | |", "| --- | --- |"]
    for item in facts:
        fact_lines.append(f"| **{item.get('label', '')}** | {item.get('value', '')} |")
    fact_lines.extend(["", _source_comment_from_items(facts)])
    blocks.append("\n".join(fact_lines).rstrip())

    name = data.get("name_and_place") or {}
    blocks.append(
        f"## {name.get('title', '書名')}\n\n"
        f"{_paragraphs(name.get('paragraphs'))}\n\n{_sources(name.get('source_ids'))}"
    )

    structure = data.get("structure") or {}
    structure_lines = [f"## {structure.get('title', '全書結構')}", "", str(structure.get("intro", "")).strip()]
    visual = (data.get("visuals") or {}).get("structure_mermaid")
    if visual:
        structure_lines.extend(["", _mermaid(visual)])
    structure_lines.extend(["", "| 範圍 | 鏡頭 | 這一段在做什麼 |", "| --- | --- | --- |"])
    for item in structure.get("macro") or []:
        structure_lines.append(
            f"| **{item.get('range', '')}** | {item.get('label', '')} | {item.get('summary', '')} |"
        )
    if structure.get("toledot_note"):
        structure_lines.extend(
            [
                "",
                "> [!tip] 家譜不是休息時間",
                *[f"> {line}" if line else ">" for line in str(structure["toledot_note"]).splitlines()],
            ]
        )
    structure_lines.extend(["", _sources(structure.get("source_ids"))])
    blocks.append("\n".join(structure_lines).rstrip())

    arc = data.get("story_arc") or {}
    arc_lines = [f"## {arc.get('title', '故事主線')}", ""]
    focus = (data.get("visuals") or {}).get("focus_mermaid")
    if focus:
        arc_lines.extend([_mermaid(focus), ""])
    for index, item in enumerate(arc.get("steps") or [], 1):
        arc_lines.append(f"**{index}. {item.get('title', '')}**  ")
        arc_lines.append(str(item.get("detail", "")).strip())
        arc_lines.append("")
    arc_lines.append(_source_comment_from_items(arc.get("steps")))
    blocks.append("\n".join(arc_lines).rstrip())

    authorship = data.get("authorship_and_date") or {}
    author_lines = [f"## {authorship.get('title', '作者與年代')}", "", str(authorship.get("intro", "")).strip()]
    authorship_visual = (data.get("visuals") or {}).get("authorship_mermaid")
    if authorship_visual:
        author_lines.extend(["", _mermaid(authorship_visual)])
    author_lines.extend(["", "| 問題 | 目前這個 prototype 的寫法 |", "| --- | --- |"])
    for item in authorship.get("questions") or []:
        author_lines.append(f"| **{item.get('label', '')}** | {item.get('answer', '')} |")
    if authorship.get("conclusion"):
        author_lines.extend(
            [
                "",
                "> [!important] 不把不同層次的問題混在一起",
                *[f"> {line}" if line else ">" for line in str(authorship["conclusion"]).splitlines()],
            ]
        )
    author_lines.extend(["", _sources(authorship.get("source_ids"))])
    blocks.append("\n".join(author_lines).rstrip())

    background = data.get("historical_background") or {}
    blocks.append(
        f"## {background.get('title', '歷史與文化背景')}\n\n"
        f"{_paragraphs(background.get('paragraphs'))}\n\n{_sources(background.get('source_ids'))}"
    )

    purpose = data.get("purpose_and_audience") or {}
    blocks.append(
        f"## {purpose.get('title', '原始讀者與寫作目的')}\n\n"
        f"{_paragraphs(purpose.get('paragraphs'))}\n\n{_sources(purpose.get('source_ids'))}"
    )

    themes = data.get("themes") or {}
    theme_lines = [f"## {themes.get('title', '核心主題')}", ""]
    for item in themes.get("items") or []:
        theme_lines.extend([f"### {item.get('name', '')}", str(item.get("text", "")).strip(), ""])
    theme_lines.append(_source_comment_from_items(themes.get("items")))
    blocks.append("\n".join(theme_lines).rstrip())

    literary = data.get("literary_features") or {}
    literary_lines = [f"## {literary.get('title', '文學特色')}", ""]
    for item in literary.get("items") or []:
        literary_lines.extend([f"**{item.get('title', '')}**  ", str(item.get("text", "")).strip(), ""])
    literary_lines.append(_sources(literary.get("source_ids")))
    blocks.append("\n".join(literary_lines).rstrip())

    relation = data.get("relationship_to_bible") or {}
    blocks.append(
        f"## {relation.get('title', '與其他書卷的關係')}\n\n"
        f"{_paragraphs(relation.get('paragraphs'))}\n\n{_sources(relation.get('source_ids'))}"
    )

    guide = data.get("reading_guide") or {}
    guide_lines = [f"## {guide.get('title', '怎麼讀')}", ""]
    for item in guide.get("items") or []:
        guide_lines.append(f"- {item}")
    guide_lines.extend(["", _sources(guide.get("source_ids"))])
    blocks.append("\n".join(guide_lines).rstrip())

    references = data.get("references") or []
    ref_lines = ["> [!info]- 本頁來源與方法", ">"]
    ref_lines.append(
        "> **四套既有註釋來源**：CT00、GT00、KC0、BH。BibleProject、Enter the Bible、Yale 是補強層，**不加入四家註釋的共識票數**。"
    )
    ref_lines.append(">")
    for ref in references:
        ref_lines.append(f"> - **{ref.get('id', '')}**｜[{ref.get('label', '')}]({ref.get('url', '')})")
    ref_lines.append(">")
    ref_lines.append(
        "> 有分歧的作者、年代、文類與歷史問題，本文保留不同框架並標示它們回答的是哪一層問題；不以單一來源替其他來源下裁決。"
    )
    blocks.append("\n".join(ref_lines))

    blocks.append(
        "\n".join(
            [
                "<!-- book-introduction-navigation:start -->",
                f"| {nav.get('outline', '')} | {nav.get('first_chapter', '')} |",
                "| :--- | ---: |",
                "<!-- book-introduction-navigation:end -->",
            ]
        )
    )
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
