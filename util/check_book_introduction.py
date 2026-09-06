#!/usr/bin/env python3
"""Validate a book-level Introduction prototype.

The checker deliberately validates structure/provenance rather than theology.
It is meant to keep the book-introduction pipeline aligned with the project rule:
「模型不碰結構，程式不碰內容」。

Prototype usage:

    python util/check_book_introduction.py \
      "01 創世記/.tmp/introduction/introduction_content.yaml" \
      --manifest "raw_data/book_intro/創世記/source_manifest.yaml" \
      --rendered "01 創世記/Introduction.md"

Checks:
- all source IDs used by content exist in the manifest;
- commentary-vote and external-context source roles do not overlap;
- disputed authorship/date material keeps traditional and academic layers apart;
- public Introduction.md is exactly reproducible from introduction_content.yaml;
- the page contains useful Obsidian/Markdown visual structure (Mermaid + callouts);
- source URLs are present in the rendered references section.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Iterable

import yaml

ROOT = Path(__file__).resolve().parent.parent

try:
    from .render_book_introduction import render
except ImportError:
    from render_book_introduction import render


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: YAML root must be a mapping")
    return data


def source_ids_from_tree(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"sources", "source_ids"} and isinstance(child, list):
                found.update(str(item).strip() for item in child if str(item).strip())
            else:
                found.update(source_ids_from_tree(child))
    elif isinstance(value, list):
        for child in value:
            found.update(source_ids_from_tree(child))
    return found


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def as_set(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {str(item).strip() for item in value if str(item).strip()}


def reference_ids(content: dict[str, Any]) -> set[str]:
    refs = content.get("references") or []
    if not isinstance(refs, list):
        return set()
    return {
        str(ref.get("id", "")).strip()
        for ref in refs
        if isinstance(ref, dict) and str(ref.get("id", "")).strip()
    }


def source_urls(manifest: dict[str, Any]) -> list[str]:
    urls: list[str] = []
    for spec in (manifest.get("sources") or {}).values():
        if not isinstance(spec, dict):
            continue
        url = str(spec.get("url", "")).strip()
        if url:
            urls.append(url)
        values = spec.get("urls")
        if isinstance(values, list):
            urls.extend(str(item).strip() for item in values if str(item).strip())
    return urls


def question_labels(content: dict[str, Any]) -> set[str]:
    block = content.get("authorship_and_date") or {}
    questions = block.get("questions") or [] if isinstance(block, dict) else []
    return {
        str(item.get("label", "")).strip()
        for item in questions
        if isinstance(item, dict) and str(item.get("label", "")).strip()
    }


def count_mermaid(text: str) -> int:
    return text.count("```mermaid")


def count_callouts(text: str) -> int:
    return text.count("> [!")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate book Introduction content + rendering")
    parser.add_argument("content", type=Path)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--rendered", type=Path, required=True)
    parser.add_argument("--min-mermaid", type=int, default=2)
    parser.add_argument("--min-callouts", type=int, default=3)
    args = parser.parse_args()

    content_path = args.content if args.content.is_absolute() else ROOT / args.content
    manifest_path = args.manifest if args.manifest.is_absolute() else ROOT / args.manifest
    rendered_path = args.rendered if args.rendered.is_absolute() else ROOT / args.rendered

    content = load_yaml(content_path)
    manifest = load_yaml(manifest_path)
    rendered_text = rendered_path.read_text(encoding="utf-8")

    errors: list[str] = []
    warnings: list[str] = []

    source_specs = manifest.get("sources") or {}
    require(isinstance(source_specs, dict) and bool(source_specs), "manifest.sources must be a non-empty mapping", errors)
    known_sources = set(source_specs) if isinstance(source_specs, dict) else set()

    used_sources = source_ids_from_tree(content)
    unknown = sorted(used_sources - known_sources)
    require(not unknown, f"content uses unknown source IDs: {unknown}", errors)

    principles = manifest.get("principles") or {}
    commentary = as_set(principles.get("commentary_vote_sources")) if isinstance(principles, dict) else set()
    external = as_set(principles.get("external_context_sources")) if isinstance(principles, dict) else set()
    require(commentary == {"CT00", "GT00", "KC0", "BH"}, f"commentary vote set changed unexpectedly: {sorted(commentary)}", errors)
    require(not commentary.intersection(external), "commentary and external-context source roles overlap", errors)
    require(commentary.union(external).issubset(known_sources), "principle source IDs must exist in manifest.sources", errors)

    for source_id in commentary:
        spec = source_specs.get(source_id) or {}
        require(spec.get("role") == "commentary", f"{source_id} must keep role=commentary", errors)
    for source_id in external:
        spec = source_specs.get(source_id) or {}
        require(spec.get("role") != "commentary", f"{source_id} must not be counted as commentary", errors)

    gt = source_specs.get("GT00") or {}
    require(bool(gt.get("provenance_rule")), "GT00 must define provenance_rule because it is a multi-source anthology", errors)
    bh = source_specs.get("BH") or {}
    require(bool(bh.get("family_rule")), "BH must define family_rule so BibleHub subpages do not become extra votes", errors)

    labels = question_labels(content)
    required_labels = {"故事年代", "傳統作者歸屬", "傳統成書框架", "現代學術成書觀"}
    missing_labels = sorted(required_labels - labels)
    require(not missing_labels, f"authorship/date block missing layered questions: {missing_labels}", errors)

    refs = reference_ids(content)
    require(known_sources.issubset(refs), f"references section missing source IDs: {sorted(known_sources - refs)}", errors)

    expected = render(content)
    require(
        expected == rendered_text,
        "Introduction.md is not in sync with introduction_content.yaml; rerun render_book_introduction.py",
        errors,
    )

    mermaid_count = count_mermaid(rendered_text)
    callout_count = count_callouts(rendered_text)
    require(mermaid_count >= args.min_mermaid, f"only {mermaid_count} Mermaid diagrams; expected at least {args.min_mermaid}", errors)
    require(callout_count >= args.min_callouts, f"only {callout_count} Obsidian callouts; expected at least {args.min_callouts}", errors)

    require("[[01 創世記/全書目錄及綱要|全書目錄及綱要]]" in rendered_text, "outline wiki-link missing", errors)
    require("[[01 創世記/第1章|開始讀第1章]]" in rendered_text, "first-chapter wiki-link missing", errors)

    # Every canonical source landing URL should be discoverable to readers. For
    # multi-page sources (Enter the Bible), the references section may use the
    # course landing page rather than every lesson URL.
    for source_id, spec in source_specs.items():
        if not isinstance(spec, dict):
            continue
        canonical = str(spec.get("url", "")).strip()
        if not canonical:
            urls = spec.get("urls")
            canonical = str(urls[0]).strip() if isinstance(urls, list) and urls else ""
        if canonical and canonical not in rendered_text:
            warnings.append(f"{source_id}: canonical source URL is not visible in rendered references: {canonical}")

    print(f"book: {content.get('book', '(unknown)')}")
    print(f"sources: {len(known_sources)} known / {len(used_sources)} used")
    print(f"visuals: {mermaid_count} Mermaid / {callout_count} callouts")

    for warning in warnings:
        print(f"WARN: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("PASS: book Introduction prototype is structurally and provenance-consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
