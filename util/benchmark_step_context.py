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
    all_entries = [
        e for group in real_plan.values()
        if isinstance(group, list)
        for e in group if isinstance(e, dict)
    ]
    candidate = next(
        (entry for entry in all_entries if entry.get("name") == "穹蒼（raqia）"),
        {
            "name": "穹蒼（raqia）",
            "suggested_type": "原文",
            "evidence": "6-8節",
            "surfaces": [{"phrase": "空氣", "verses": [6, 7, 8]}],
        },
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


def _prepare_exodus(temp_root: Path, data_path: Path) -> tuple[run_chapter.ChapterContext, dict, Path]:
    raw_dir = temp_root / "raw_data"
    raw_dir.mkdir(parents=True, exist_ok=True)
    chapter_dir = book_directory(temp_root, "出埃及記") / ".tmp" / "第20章"
    chapter_dir.mkdir(parents=True)
    scripture_dir = temp_root / "raw_scripture" / "出埃及記"
    scripture_dir.mkdir(parents=True)
    shutil.copyfile(
        ROOT / "raw_scripture" / "出埃及記" / "第20章.txt",
        scripture_dir / "第20章.txt",
    )

    production_manifest = ROOT / "02 出埃及記" / ".tmp" / "第20章" / "source_manifest.md"
    commentary = [
        item for item in source_excerpts.manifest_source_identities(production_manifest, ROOT)
        if not item.is_structured
    ]
    rows = []
    for item in commentary:
        target = raw_dir / item.path.name
        shutil.copyfile(item.path, target)
        rows.append((item.manifest_label, item.kind, item.url, f"raw_data/{target.name}"))
    step_path = _extract("Exodus 20", data_path, raw_dir)
    rows.append((
        "STEP Bible", "原文資料", "https://github.com/STEPBible/STEPBible-Data",
        f"raw_data/{step_path.name}",
    ))
    _write_manifest(chapter_dir / "source_manifest.md", rows)

    real_plan = yaml.safe_load(
        (ROOT / "02 出埃及記" / ".tmp" / "第20章" / "link_plan.yaml").read_text(encoding="utf-8")
    ) or {}
    all_entries = [
        e for group in real_plan.values()
        if isinstance(group, list)
        for e in group if isinstance(e, dict)
    ]
    candidate = next(
        (entry for entry in all_entries if entry.get("name") == "敬畏神"),
        {
            "name": "敬畏神",
            "suggested_type": "神學",
            "evidence": "20節；CT 區分「敬畏」與「懼怕」",
            "surfaces": [{"phrase": "敬畏他", "verses": [20]}],
        },
    )
    plan = {
        "A_use_directly": [], "B_needs_update": [],
        "C_new_formal": [candidate], "D_new_candidate": [], "E_skip": [],
    }
    return run_chapter.ChapterContext(
        "出埃及記", 20, root=temp_root, index={}, homonyms={}
    ), plan, step_path



def _metric_3layer(
    before_full: dict,
    compact_full: dict,
    selected: dict,
    metric: dict,
) -> dict:
    step = metric["step"][0] if metric.get("step") else {}
    l1_chars = before_full["chars"]
    l1_bytes = before_full["bytes"]
    l2_chars = compact_full["chars"]
    l2_bytes = compact_full["bytes"]
    l3_chars = selected["chars"]
    l3_bytes = selected["bytes"]
    return {
        "layer1_legacy_full_chars": l1_chars,
        "layer1_legacy_full_bytes": l1_bytes,
        "layer2_current_compact_chars": l2_chars,
        "layer2_current_compact_bytes": l2_bytes,
        "layer3_selected_evidence_chars": l3_chars,
        "layer3_selected_evidence_bytes": l3_bytes,
        "reduction_l1_to_l3_percent": round((1 - l3_chars / l1_chars) * 100, 2),
        "reduction_l2_to_l3_percent": round((1 - l3_chars / l2_chars) * 100, 2),
        "step_selection_mode": step.get("selection_mode", "targeted"),
        "step_projected_chars": step.get("projected_chars", 0),
        "step_projected_bytes": step.get("projected_bytes", 0),
        "step_occurrences": step.get("occurrences", 0),
        "step_lexicon_entries": step.get("lexicon_entries", 0),
        "step_candidate_count": step.get("candidate_count", 0),
        "step_selected_candidate_count": step.get("selected_candidate_count", 0),
        "step_selected_verses": step.get("selected_verses", []),
        "step_truncated": step.get("truncated", False),
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
    m3_snapshot = ctx._last_prompt_context

    chapter_capture = run_chapter_manual.PromptCapture(prompt_dir, "chapter_content", ctx=ctx)
    ctx.runner = chapter_capture
    run_chapter.chapter_content_step(
        ctx, plan, source_context_policy=source_excerpts.MANUAL_PROJECTED
    )
    m6_snapshot = ctx._last_prompt_context

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

    # Compute Layer 2 (Phase 1 compact projection) prompt size for comparison
    ref_block = source_excerpts._manual_reference_block(
        source_excerpts.manifest_source_identities(ctx.path("source_manifest.md"), ctx.root), ctx.root
    )

    # M3 Layer 2: Phase 1 targeted-verse compact projection
    c_entries = plan.get("C_new_formal", [])
    phase1_verses = step_context.select_candidate_verses(c_entries, range(1, len(ctx.raw_verses()) + 1)).verses
    if phase1_verses:
        m3_phase1_proj = step_context.project_step_source(step_path, verses=phase1_verses, allow_full_chapter=True)
    else:
        m3_phase1_proj = step_context.project_step_source(step_path, allow_full_chapter=True)
    layer2_m3_context_text = f"{ref_block}\n\n{m3_phase1_proj.text}"

    # M6 Layer 2: Phase 1 full-chapter compact projection
    m6_phase1_proj = step_context.project_step_source(step_path, allow_full_chapter=True)
    layer2_m6_context_text = f"{ref_block}\n\n{m6_phase1_proj.text}"

    # M3 Layer 2 prompt
    m3_metric = entry_capture.metrics[0]
    m3_l3_prompt = (prompt_dir / m3_metric["path"]).read_text(encoding="utf-8")
    m3_l2_prompt = m3_l3_prompt
    if m3_snapshot and m3_snapshot.text in m3_l3_prompt:
        m3_l2_prompt = m3_l3_prompt.replace(m3_snapshot.text, layer2_m3_context_text, 1)

    # M6 Layer 2 prompt
    m6_metric = chapter_capture.metrics[0]
    m6_l3_prompt = (prompt_dir / m6_metric["path"]).read_text(encoding="utf-8")
    m6_l2_prompt = m6_l3_prompt
    if m6_snapshot and m6_snapshot.text in m6_l3_prompt:
        m6_l2_prompt = m6_l3_prompt.replace(m6_snapshot.text, layer2_m6_context_text, 1)

    m3_3layer = _metric_3layer(
        m3_metric["before"],
        {"chars": len(m3_l2_prompt), "bytes": len(m3_l2_prompt.encode("utf-8"))},
        m3_metric["after"],
        m3_metric,
    )
    m6_3layer = _metric_3layer(
        m6_metric["before"],
        {"chars": len(m6_l2_prompt), "bytes": len(m6_l2_prompt.encode("utf-8"))},
        m6_metric["after"],
        m6_metric,
    )

    return {
        "case": name,
        "reference": f"{receipt['book']} {receipt['chapter']}",
        "step_raw_chars": receipt["chars"],
        "step_raw_bytes": receipt["bytes"],
        "step_verses": receipt["verses"],
        "step_words": receipt["words"],
        "m3": m3_3layer,
        "m6": m6_3layer,
    }


def run_benchmarks(data_path: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="hermes-step-context-") as directory:
        temp_root = Path(directory)
        genesis = _prepare_genesis(temp_root / "genesis", data_path)
        john = _prepare_john(temp_root / "john", data_path)
        exodus = _prepare_exodus(temp_root / "exodus", data_path)
        cases = [
            _run_case("Genesis 1 (M3: 穹蒼 6-8節)", *genesis, expected_words=434),
            _run_case("John 1:1-5", *john, expected_words=61),
            _run_case("Exodus 20 (M3: 敬畏神 20節)", *exodus, expected_words=312),
        ]
    for case in cases:
        if case["case"].startswith("Genesis 1") or case["case"].startswith("Exodus 20"):
            for stage in ("m3", "m6"):
                if case[stage]["reduction_l1_to_l3_percent"] < 30:
                    raise RuntimeError(
                        f"{case['case']} {stage.upper()} prompt reduction vs Layer 1 < 30%："
                        f"{case[stage]['reduction_l1_to_l3_percent']}%"
                    )
                if case[stage]["reduction_l2_to_l3_percent"] <= 0:
                    raise RuntimeError(
                        f"{case['case']} {stage.upper()} prompt reduction vs Layer 2 <= 0%："
                        f"{case[stage]['reduction_l2_to_l3_percent']}%"
                    )
    return {

        "version": 2,
        "layers": {
            "layer1": "Legacy FULL (full commentary text + full raw STEP table in prompt)",
            "layer2": "Current Compact (commentary reference + full chapter compact STEP projection)",
            "layer3": "New Selected Evidence (commentary reference + targeted/selected candidates STEP)",
        },
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
