#!/usr/bin/env python3
"""Validate a book-level 書卷導論 against ``introduction_scheme.md``.

The checker validates structure, provenance, reproducibility and the public
navigation contract rather than choosing a theological position. It deliberately
does *not* require a fixed number of public sections or a Mermaid diagram for
every book.

Example:

    python util/check_book_introduction.py \
      "01 創世記/.tmp/introduction/introduction_content.yaml" \
      --manifest "raw_data/book_intro/創世記/source_manifest.yaml" \
      --rendered "01 創世記/書卷導論.md"
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent

try:
    from .render_book_introduction import MODULE_ORDER, render
except ImportError:
    from render_book_introduction import MODULE_ORDER, render


COMMENTARY_ROLE = "commentary"
STYLE_PHRASES = (
    "一分鐘認識",
    "如果只記一件事",
    "你有沒有想過",
    "先別急著",
)
NUMBERED_HEADING = re.compile(
    r"^##\s+(?:\d+[\.、)]|[壹貳參叁肆伍陸柒捌玖拾]+[、．.])",
    re.MULTILINE,
)


def _load(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: YAML root must be a mapping")
    return data


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def _collect_source_ids(value: Any) -> set[str]:
    """Collect content provenance IDs, but not policy lists or reference IDs."""
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "source_ids" and isinstance(child, list):
                found.update(str(item).strip() for item in child if str(item).strip())
            elif key not in {"source_policy", "references"}:
                found.update(_collect_source_ids(child))
    elif isinstance(value, list):
        for child in value:
            found.update(_collect_source_ids(child))
    return found


def _module_text(module: dict[str, Any]) -> str:
    parts: list[str] = []

    def walk(value: Any) -> None:
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, dict):
            for key, child in value.items():
                if key not in {"source_ids", "mermaid"}:
                    walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(module)
    return "\n".join(parts)


def _manifest_roles(manifest: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for source_id, spec in (manifest.get("sources") or {}).items():
        if isinstance(spec, dict):
            result[str(source_id)] = str(spec.get("role", "")).strip()
    return result


def _errors_for_policy(
    content: dict[str, Any], manifest: dict[str, Any], errors: list[str]
) -> None:
    policy = content.get("source_policy") or {}
    commentary = [str(v) for v in policy.get("commentary_vote_sources") or []]
    external = [str(v) for v in policy.get("external_context_sources") or []]
    anchor = str(policy.get("editorial_anchor", "")).strip()

    if not commentary:
        errors.append("source_policy.commentary_vote_sources is required")
    if set(commentary) & set(external):
        errors.append("commentary vote sources and external context sources overlap")
    if anchor and anchor not in commentary:
        errors.append(f"editorial_anchor {anchor!r} is not a commentary vote source")

    roles = _manifest_roles(manifest)
    for source_id in commentary:
        if source_id not in roles:
            errors.append(f"commentary source {source_id!r} missing from manifest")
        elif roles[source_id] != COMMENTARY_ROLE:
            errors.append(
                f"commentary source {source_id!r} has manifest role {roles[source_id]!r}"
            )
    for source_id in external:
        if source_id not in roles:
            errors.append(f"external source {source_id!r} missing from manifest")
        elif roles[source_id] == COMMENTARY_ROLE:
            errors.append(f"external source {source_id!r} is incorrectly marked commentary")

    manifest_principles = manifest.get("principles") or {}
    manifest_commentary = {
        str(v) for v in manifest_principles.get("commentary_vote_sources") or []
    }
    if manifest_commentary and set(commentary) != manifest_commentary:
        errors.append(
            "content commentary_vote_sources do not match manifest principles: "
            f"content={sorted(commentary)}, manifest={sorted(manifest_commentary)}"
        )

    gt = (manifest.get("sources") or {}).get("GT00") or {}
    if "GT00" in commentary and not str(gt.get("provenance_rule", "")).strip():
        errors.append("GT00 must declare provenance_rule because it is an anthology")

    bh = (manifest.get("sources") or {}).get("BH") or {}
    if "BH" in commentary and not str(bh.get("family_rule", "")).strip():
        errors.append("BH must declare family_rule so its subresources do not add votes")


def _errors_for_modules(content: dict[str, Any], errors: list[str]) -> None:
    if int(content.get("schema_version", 0)) != 3:
        errors.append("schema_version must be 3")
        return

    modules = content.get("modules")
    if not isinstance(modules, dict):
        errors.append("modules must be a mapping")
        return

    unknown = sorted(set(modules) - set(MODULE_ORDER))
    if unknown:
        errors.append(f"unknown modules: {', '.join(unknown)}")

    # These are the minimum pieces that make a book introduction useful.
    for required in ("authorship_context", "message_purpose", "structure"):
        module = modules.get(required)
        if not isinstance(module, dict) or module.get("enabled") is False:
            errors.append(f"required module missing or disabled: {required}")

    # When traditional commentary and academic context are both used for
    # authorship/composition, the prose must visibly keep the layers apart.
    authorship = modules.get("authorship_context")
    if isinstance(authorship, dict):
        ids = set(str(v) for v in authorship.get("source_ids") or [])
        policy = content.get("source_policy") or {}
        commentary = set(str(v) for v in policy.get("commentary_vote_sources") or [])
        external = set(str(v) for v in policy.get("external_context_sources") or [])
        if ids & commentary and ids & external:
            text = _module_text(authorship)
            if "傳統" not in text:
                errors.append(
                    "authorship_context mixes commentary and academic sources but does not label the traditional layer"
                )
            if "現代" not in text and "近代" not in text and "研究" not in text:
                errors.append(
                    "authorship_context mixes commentary and academic sources but does not label the research layer"
                )


def _errors_for_navigation(
    content: dict[str, Any], rendered_path: Path, errors: list[str]
) -> None:
    folder = str(content.get("book_folder", "")).strip()
    if not folder:
        errors.append("book_folder is required for public navigation")
        return

    canonical_path = (ROOT / folder / "書卷導論.md").resolve()
    if rendered_path.resolve() != canonical_path:
        errors.append(
            "rendered public file must use canonical path "
            f"{folder}/書卷導論.md"
        )

    navigation = content.get("navigation") or {}
    expected = {
        "outline": f"[[{folder}/全書目錄及綱要|",
        "first_chapter": f"[[{folder}/第1章|",
    }
    for key, prefix in expected.items():
        value = str(navigation.get(key, "")).strip()
        if not value.startswith(prefix):
            errors.append(
                f"navigation.{key} must use full book path beginning with {prefix!r}"
            )


def _errors_for_rendered(
    content: dict[str, Any], rendered_path: Path, manifest: dict[str, Any], errors: list[str]
) -> None:
    if not rendered_path.exists():
        try:
            label = rendered_path.relative_to(ROOT)
        except ValueError:
            label = rendered_path
        errors.append(f"rendered file missing: {label}")
        return

    actual = rendered_path.read_text(encoding="utf-8")
    expected = render(content)
    if actual != expected:
        errors.append(
            "書卷導論.md is not exactly reproducible from introduction_content.yaml; "
            "rerun render_book_introduction.py"
        )

    if NUMBERED_HEADING.search(actual):
        errors.append("public 書卷導論 uses numbered H2 headings; the scheme forbids fixed-point presentation")

    for phrase in STYLE_PHRASES:
        if phrase in actual:
            errors.append(f"public 書卷導論 contains discouraged AI-guide phrase: {phrase}")

    mermaid_count = actual.count("```mermaid")
    if mermaid_count > 5:
        errors.append(f"too many Mermaid blocks ({mermaid_count}); visuals should compress, not repeat, the prose")

    refs = content.get("references") or []
    manifest_sources = manifest.get("sources") or {}
    ref_ids = {str(ref.get("id", "")).strip() for ref in refs if isinstance(ref, dict)}
    used_ids = _collect_source_ids(content)
    missing_refs = sorted(used_ids - ref_ids)
    if missing_refs:
        errors.append(f"used source IDs missing from public references: {', '.join(missing_refs)}")

    for ref in refs:
        if not isinstance(ref, dict):
            continue
        source_id = str(ref.get("id", "")).strip()
        url = str(ref.get("url", "")).strip()
        if source_id not in manifest_sources:
            errors.append(f"reference source {source_id!r} missing from manifest")
        if url and url not in actual:
            errors.append(f"reference URL for {source_id!r} missing from rendered Markdown")


def check(
    content_path: Path, manifest_path: Path, rendered_path: Path
) -> list[str]:
    content = _load(content_path)
    manifest = _load(manifest_path)
    errors: list[str] = []

    manifest_ids = set(str(v) for v in (manifest.get("sources") or {}).keys())
    used_ids = _collect_source_ids(content)
    unknown_sources = sorted(used_ids - manifest_ids)
    if unknown_sources:
        errors.append(f"content uses source IDs absent from manifest: {', '.join(unknown_sources)}")

    _errors_for_policy(content, manifest, errors)
    _errors_for_modules(content, errors)
    _errors_for_navigation(content, rendered_path, errors)
    _errors_for_rendered(content, rendered_path, manifest, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a book 書卷導論 prototype")
    parser.add_argument("content", type=Path)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--rendered", type=Path, required=True)
    args = parser.parse_args()

    content_path = _resolve(args.content)
    manifest_path = _resolve(args.manifest)
    rendered_path = _resolve(args.rendered)

    errors = check(content_path, manifest_path, rendered_path)
    if errors:
        print("❌ Book 書卷導論 check failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("✅ Book 書卷導論 check PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
