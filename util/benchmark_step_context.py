#!/usr/bin/env python3
"""Reproduce Phase-2 prompt-context benchmarks without touching the vault.

The benchmark uses the local official STEP cache, the real Genesis 1
commentaries/link plan/scripture, and the real John 1:1-5 TAGNT data.  All
generated sources/prompts live in a temporary workspace.  No network access,
production chapter rendering, or ``link_folder`` writes occur.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

import yaml

import build_source_manifest
import extract_stepbible
import run_chapter
import run_chapter_manual
import source_excerpts
import step_context
from book_paths import book_directory


ROOT = Path(__file__).resolve().parent.parent


def _extract(reference: str, data_path: Path, raw_dir: Path) -> Path:
    """Extract one real STEP source from the already-local official datasets."""
    ref = extract_stepbible.parse_reference(reference)
    tagged, lexicon_path, morphology_path = extract_stepbible.ensure_required_files(
        ref=ref, data_path=data_path, allow_download=False
    )
    language = "hebrew" if ref.testament == "OT" else "greek"
    lexicon = extract_stepbible.parse_lexicon(lexicon_path, language)
    morphology = extract_stepbible.parse_morphology_file(morphology_path)
    if ref.testament == "OT":
        verses = extract_stepbible.parse_tahot(tagged, ref, lexicon, morphology)
    else:
        verses = extract_stepbible.parse_tagnt(tagged, ref, lexicon, morphology)
    if not verses:
        raise RuntimeError(f"STEP cache 沒有資料：{reference}")
    path = raw_dir / extract_stepbible.stepbible_filename(
        ref.code, ref.chapter, ref.verse_start, ref.verse_end
    )
    path.write_text(
        extract_stepbible.render_markdown(ref, verses, include_full_definitions=False),
        encoding="utf-8",
    )
    return path


def _write_manifest(path: Path, rows) -> None:
    lines = [
        "| 來源 | 類型 | URL | raw_data 檔案 | 狀態 |",
        "|---|---|---|---|---|",
    ]
    lines.extend(
        f"| {label} | {kind} | {url} | {relative} | OK |"
        for label, kind, url, relative in rows
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _prepare_genesis(temp_root: Path, data_path: Path) -> tuple[run_chapter.ChapterContext, dict, Path]:
    raw_dir = temp_root / "raw_data"
    raw_dir.mkdir(parents=True)
    chapter_dir = book_directory(temp_root, "創世記") / ".tmp" / "第1章"
    chapter_dir.mkdir(parents=True)
    scripture_dir = temp_root / "raw_scripture" / "創世記"
    scripture_dir.mkdir(parents=True)
    shutil.copyfile(
        ROOT / "raw_scripture" / "創世記" / "第1章.txt",
        scripture_dir / "第1章.txt",
    )

    production_manifest = ROOT / "01 創世記" / ".tmp" / "第1章" / "source_manifest.md"
    commentary = [
        item for item in source_excerpts.manifest_source_identities(production_manifest, ROOT)
        if not item.is_structured
    ]
    if len(commentary) != 4:
        raise RuntimeError(f"Genesis 1 預期 4 套 commentary，實際 {len(commentary)}")
    rows = []
    for item in commentary:
        target = raw_dir / item.path.name
        shutil.copyfile(item.path, target)
        rows.append((item.manifest_label, item.kind, item.url, f"raw_data/{target.name}"))
    step_path = _extract("Genesis 1", data_path, raw_dir)
    rows.append((
        "STEP Bible", "原文資料", "https://github.com/STEPBible/STEPBible-Data",
        f"raw_data/{step_path.name}",
    ))
    _write_manifest(chapter_dir / "source_manifest.md", rows)

    real_plan = yaml.safe_load(
        (ROOT / "01 創世記" / ".tmp" / "第1章" / "link_plan.yaml").read_text(encoding="utf-8")
    ) or {}
    candidate = next(
        entry for entry in real_plan.get("C_new_formal", [])
        if entry.get("name") == "穹蒼（raqia）"
    )
    plan = {
        "A_use_directly": [], "B_needs_update": [],
        "C_new_formal": [candidate], "D_new_candidate": [], "E_skip": [],
    }
    return run_chapter.ChapterContext(
        "創世記", 1, root=temp_root, index={}, homonyms={}
    ), plan, step_path


def _prepare_john(temp_root: Path, data_path: Path) -> tuple[run_chapter.ChapterContext, dict, Path]:
    raw_dir = temp_root / "raw_data"
    raw_dir.mkdir(parents=True, exist_ok=True)
    chapter_dir = book_directory(temp_root, "約翰福音") / ".tmp" / "第1章"
    chapter_dir.mkdir(parents=True)
    scripture_dir = temp_root / "raw_scripture" / "約翰福音"
    scripture_dir.mkdir(parents=True)
    verses = (ROOT / "raw_scripture" / "約翰福音" / "第1章.txt").read_text(
        encoding="utf-8"
    ).splitlines()[:5]
    (scripture_dir / "第1章.txt").write_text("\n".join(verses) + "\n", encoding="utf-8")
    step_path = _extract("John 1:1-5", data_path, raw_dir)
    _write_manifest(chapter_dir / "source_manifest.md", [(
        "STEP Bible", "原文資料", "https://github.com/STEPBible/STEPBible-Data",
        f"raw_data/{step_path.name}",
    )])
    plan = {
        "A_use_directly": [], "B_needs_update": [],
        "C_new_formal": [{
            "name": "道（logos）", "suggested_type": "原文", "evidence": "1-5節",
            "surfaces": [{"phrase": "道", "verses": [1, 2, 3, 4, 5]}],
        }],
        "D_new_candidate": [], "E_skip": [],
    }
    return run_chapter.ChapterContext(
        "約翰福音", 1, root=temp_root, index={}, homonyms={}
    ), plan, step_path


def _metric(metric: dict) -> dict:
    before = metric["before"]
    after = metric["after"]
    step = metric["step"][0]
    return {
        "before_prompt_chars": before["chars"],
        "before_prompt_bytes": before["bytes"],
        "after_prompt_chars": after["chars"],
        "after_prompt_bytes": after["bytes"],
        "prompt_reduction_percent": round(
            (1 - after["chars"] / before["chars"]) * 100, 2
        ),
        "step_projected_chars": step["projected_chars"],
        "step_projected_bytes": step["projected_bytes"],
        "step_occurrences": step["occurrences"],
        "step_lexicon_entries": step["lexicon_entries"],
        "step_selected_verses": step["selected_verses"],
        "commentary_bodies_omitted": metric["commentary_bodies_omitted"],
    }


def _run_case(name: str, ctx, plan, step_path: Path, expected_words: int) -> dict:
    prompt_dir = ctx.path("benchmark_prompts")
    entry_capture = run_chapter_manual.PromptCapture(prompt_dir, "entry_batch", ctx=ctx)
    ctx.runner = entry_capture
    run_chapter.entry_content_step(
        ctx, plan, batch_size=1,
        source_context_policy=source_excerpts.MANUAL_PROJECTED,
    )
    chapter_capture = run_chapter_manual.PromptCapture(prompt_dir, "chapter_content", ctx=ctx)
    ctx.runner = chapter_capture
    run_chapter.chapter_content_step(
        ctx, plan, source_context_policy=source_excerpts.MANUAL_PROJECTED
    )
    if len(entry_capture.metrics) != 1 or len(chapter_capture.metrics) != 1:
        raise RuntimeError(f"{name} benchmark 未捕捉到唯一 M3/M6 prompt")
    receipt = step_context.validate_step_source(
        step_path,
        expected_book=ctx.book,
        expected_chapter=ctx.chapter,
        scripture_verse_count=len(ctx.raw_verses()),
    )
    if receipt["words"] != expected_words:
        raise RuntimeError(
            f"{name} STEP word count 漂移：預期 {expected_words}，實際 {receipt['words']}"
        )
    return {
        "case": name,
        "reference": f"{receipt['book']} {receipt['chapter']}",
        "step_raw_chars": receipt["chars"],
        "step_raw_bytes": receipt["bytes"],
        "step_verses": receipt["verses"],
        "step_words": receipt["words"],
        "m3": _metric(entry_capture.metrics[0]),
        "m6": _metric(chapter_capture.metrics[0]),
    }


def run_benchmarks(data_path: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="hermes-step-context-") as directory:
        temp_root = Path(directory)
        genesis = _prepare_genesis(temp_root / "genesis", data_path)
        john = _prepare_john(temp_root / "john", data_path)
        cases = [
            _run_case("Genesis 1 (M3: 穹蒼 6-8節)", *genesis, expected_words=434),
            _run_case("John 1:1-5", *john, expected_words=61),
        ]
    for case in cases:
        for stage in ("m3", "m6"):
            if case[stage]["prompt_reduction_percent"] < 30:
                raise RuntimeError(
                    f"{case['case']} {stage.upper()} prompt reduction < 30%："
                    f"{case[stage]['prompt_reduction_percent']}%"
                )
    return {
        "version": 1,
        "measurement": "Unicode code points (chars) and UTF-8 bytes; no token estimate",
        "source": "local official STEPBible-Data cache; no network",
        "cases": cases,
    }


def main(argv=None) -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-path", type=Path, default=ROOT / ".stepbible_data")
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args(argv)
    try:
        result = run_benchmarks(args.data_path)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1
    output = json.dumps(result, ensure_ascii=False, indent=2)
    print(output)
    if args.json_output:
        args.json_output.write_text(output + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
