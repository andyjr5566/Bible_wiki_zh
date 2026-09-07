#!/usr/bin/env python3
"""Validate every configured book-level 書卷導論.

A book is considered configured once ``raw_data/book_intro/<書名>/source_manifest.yaml``
exists. For each configured book this gate requires the matching semantic payload and
public Markdown, then delegates the actual policy/content/navigation checks to
``check_book_introduction.py``.

This keeps CI scalable: adding a new book introduction does not require editing the
workflow file again.
"""

from __future__ import annotations

import difflib
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent

try:
    from .check_book_introduction import check
    from .render_book_introduction import render
except ImportError:
    from check_book_introduction import check
    from render_book_introduction import render


def _load(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: YAML root must be a mapping")
    return data


def _configured_manifests() -> list[Path]:
    base = ROOT / "raw_data" / "book_intro"
    if not base.exists():
        return []
    return sorted(base.glob("*/source_manifest.yaml"))


def _print_render_diff(content_path: Path, rendered_path: Path) -> None:
    if not content_path.exists() or not rendered_path.exists():
        return
    try:
        content = _load(content_path)
        expected = render(content).splitlines(keepends=True)
        actual = rendered_path.read_text(encoding="utf-8").splitlines(keepends=True)
    except Exception as exc:  # checker will report the structural error too
        print(f"    unable to build render diff: {exc}")
        return

    if actual == expected:
        return

    rel_rendered = rendered_path.relative_to(ROOT)
    rel_content = content_path.relative_to(ROOT)
    print(f"    deterministic render diff ({rel_rendered} vs {rel_content}):")
    diff = difflib.unified_diff(
        actual,
        expected,
        fromfile=str(rel_rendered),
        tofile=f"render({rel_content})",
        n=2,
    )
    for line in diff:
        sys.stdout.write("    " + line)


def main() -> int:
    manifests = _configured_manifests()
    if not manifests:
        print("❌ No configured book introduction manifests found")
        return 1

    total_errors = 0
    checked = 0

    print(f"Checking {len(manifests)} configured book introductions...")

    for manifest_path in manifests:
        book = manifest_path.parent.name
        try:
            manifest = _load(manifest_path)
        except Exception as exc:
            print(f"❌ {book}: invalid source manifest: {exc}")
            total_errors += 1
            continue

        folder = str(manifest.get("book_folder", "")).strip()
        manifest_book = str(manifest.get("book", "")).strip() or book
        if not folder:
            print(f"❌ {manifest_book}: source_manifest.yaml missing book_folder")
            total_errors += 1
            continue

        content_path = ROOT / folder / ".tmp" / "introduction" / "introduction_content.yaml"
        rendered_path = ROOT / folder / "書卷導論.md"

        missing = [
            path.relative_to(ROOT)
            for path in (content_path, rendered_path)
            if not path.exists()
        ]
        if missing:
            print(f"❌ {manifest_book}: configured introduction is incomplete")
            for path in missing:
                print(f"  - missing: {path}")
            total_errors += len(missing)
            continue

        try:
            content = _load(content_path)
        except Exception as exc:
            print(f"❌ {manifest_book}: invalid introduction_content.yaml: {exc}")
            total_errors += 1
            continue

        content_folder = str(content.get("book_folder", "")).strip()
        content_book = str(content.get("book", "")).strip()
        preflight_errors: list[str] = []
        if content_folder != folder:
            preflight_errors.append(
                f"book_folder mismatch: manifest={folder!r}, content={content_folder!r}"
            )
        if content_book and content_book != manifest_book:
            preflight_errors.append(
                f"book mismatch: manifest={manifest_book!r}, content={content_book!r}"
            )

        errors = preflight_errors + check(content_path, manifest_path, rendered_path)
        checked += 1

        if errors:
            print(f"❌ {manifest_book}")
            for error in errors:
                print(f"  - {error}")
            if any("not exactly reproducible" in error for error in errors):
                _print_render_diff(content_path, rendered_path)
            total_errors += len(errors)
        else:
            print(f"✅ {manifest_book}: PASS")

    if total_errors:
        print(f"\n❌ Book introduction gate failed: {total_errors} error(s) across {checked} checked book(s)")
        return 1

    print(f"\n✅ All {checked} configured book introductions PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
