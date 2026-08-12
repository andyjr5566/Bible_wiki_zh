#!/usr/bin/env python3
"""Idempotently attach formal STEP sources to completed chapter infrastructure.

This tool is deliberately narrower than ``run_chapter.py``: it only creates or
validates ``raw_data/stepbible_*.txt``, minimally adds the STEP row to an
existing source manifest, and writes a deterministic machine receipt.  It does
not call the commentary crawler, M3/M6, renderers, or any link workflow.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

try:
    from . import build_source_manifest, extract_stepbible, source_excerpts, step_context
    from .book_paths import book_directory, canonical_book_name
except ImportError:
    import build_source_manifest
    import extract_stepbible
    import source_excerpts
    import step_context
    from book_paths import book_directory, canonical_book_name


ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = Path(".tmp") / "step_backfill"


class BackfillError(RuntimeError):
    """A Phase-A invariant failed; no manifest may be marked OK for that chapter."""


@dataclass(frozen=True)
class SafetySnapshot:
    root: Path
    files: dict[str, dict[str, str]]

    def summary(self) -> dict:
        output = {}
        for name, hashes in self.files.items():
            joined = "\n".join(f"{path}|{digest}" for path, digest in sorted(hashes.items()))
            output[name] = {
                "count": len(hashes),
                "bytes": sum(
                    (self.root / path).stat().st_size
                    for path in hashes
                    if (self.root / path).is_file()
                ),
                "aggregate_sha256": hashlib.sha256(joined.encode("utf-8")).hexdigest(),
            }
        return output


def parse_chapter_spec(value: str) -> list[int]:
    normalized = (
        str(value).translate(str.maketrans("０１２３４５６７８９", "0123456789"))
        .replace("，", ",").replace("、", ",").replace("；", ",")
        .replace("–", "-").replace("—", "-").replace("－", "-")
        .replace("～", "-").replace("~", "-").replace("至", "-")
    )
    chapters: set[int] = set()
    for piece in normalized.split(","):
        piece = piece.strip()
        if not piece:
            continue
        if "-" in piece:
            bounds = [part.strip() for part in piece.split("-")]
            if len(bounds) != 2 or not all(part.isdigit() for part in bounds):
                raise ValueError(f"無法解析章範圍：{piece}")
            start, end = map(int, bounds)
            if start < 1 or end < start:
                raise ValueError(f"章範圍不合法：{piece}")
            chapters.update(range(start, end + 1))
        elif piece.isdigit() and int(piece) >= 1:
            chapters.add(int(piece))
        else:
            raise ValueError(f"無法解析章號：{piece}")
    if not chapters:
        raise ValueError("章範圍不可為空")
    return sorted(chapters)


def _numbered_files(directory: Path, pattern: str) -> dict[int, Path]:
    files = {}
    for path in directory.glob(pattern):
        stem = path.stem
        digits = "".join(character for character in stem if character.isdigit())
        if digits:
            files[int(digits)] = path
    return files


def select_chapters(root: Path, book: str, chapters: str | Iterable[int] | None):
    canonical = canonical_book_name(book)
    book_dir = book_directory(root, canonical)
    scripture_dir = root / "raw_scripture" / canonical
    production = _numbered_files(book_dir, "第*章.md")
    scripture = _numbered_files(scripture_dir, "第*章.txt")
    if not scripture:
        raise BackfillError(f"找不到經文基線：{scripture_dir}")
    expected = sorted(scripture)
    if chapters is None:
        selected = expected
    elif isinstance(chapters, str):
        selected = parse_chapter_spec(chapters)
    else:
        selected = sorted(set(int(chapter) for chapter in chapters))
    missing_scripture = [chapter for chapter in selected if chapter not in scripture]
    missing_production = [chapter for chapter in selected if chapter not in production]
    if missing_scripture or missing_production:
        raise BackfillError(
            f"章節不存在：raw_scripture={missing_scripture}, production={missing_production}"
        )
    return canonical, book_dir, scripture, expected, selected


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _hash_paths(root: Path, paths: Iterable[Path]) -> dict[str, str]:
    return {
        _relative(root, path): _sha256(path)
        for path in sorted(set(Path(item) for item in paths))
        if path.is_file()
    }


def safety_snapshot(root: Path, book: str, chapters: Iterable[int]) -> SafetySnapshot:
    root = Path(root)
    canonical = canonical_book_name(book)
    book_dir = book_directory(root, canonical)
    chapter_dirs = [book_dir / ".tmp" / f"第{chapter}章" for chapter in chapters]
    chapter_files = [book_dir / f"第{chapter}章.md" for chapter in chapters]
    link_files = list((root / "link_folder").rglob("*.md"))
    commentary = []
    for chapter_dir in chapter_dirs:
        manifest = chapter_dir / "source_manifest.md"
        for identity in source_excerpts.manifest_source_identities(manifest, root):
            if not identity.is_structured:
                commentary.append(identity.path)
    read_logs = [chapter_dir / "read_log.md" for chapter_dir in chapter_dirs]
    return SafetySnapshot(root=root.resolve(), files={
        "production_chapters": _hash_paths(root, chapter_files),
        "link_folder_markdown": _hash_paths(root, link_files),
        "commentary_raw": _hash_paths(root, commentary),
        "existing_commentary_read_logs": _hash_paths(root, read_logs),
    })


def compare_snapshots(before: SafetySnapshot, after: SafetySnapshot) -> dict:
    differences = []
    for group in sorted(set(before.files) | set(after.files)):
        old = before.files.get(group, {})
        new = after.files.get(group, {})
        for path in sorted(set(old) | set(new)):
            if old.get(path) != new.get(path):
                differences.append({
                    "group": group,
                    "path": path,
                    "before": old.get(path),
                    "after": new.get(path),
                })
    return {"byte_identical": not differences, "differences": differences}


class StepSourceExtractor:
    """Reuse extract_stepbible's official parser while caching lexicon metadata."""

    def __init__(self, data_path: Path, *, download: bool = False):
        self.data_path = Path(data_path)
        self.download = bool(download)
        self._resources = {}

    def __call__(self, book: str, chapter: int) -> str:
        reference = extract_stepbible.parse_reference(f"{book} {int(chapter)}")
        text_path, lex_path, morph_path = extract_stepbible.ensure_required_files(
            reference, self.data_path, self.download
        )
        key = (reference.testament, str(lex_path or ""), str(morph_path or ""))
        if key not in self._resources:
            language = "hebrew" if reference.testament == "OT" else "greek"
            self._resources[key] = (
                extract_stepbible.parse_lexicon(lex_path, language),
                extract_stepbible.parse_morphology_file(morph_path),
            )
        lexicon, morphology = self._resources[key]
        if reference.testament == "OT":
            verses = extract_stepbible.parse_tahot(
                text_path, reference, lexicon, morphology
            )
        else:
            verses = extract_stepbible.parse_tagnt(
                text_path, reference, lexicon, morphology
            )
        if not verses:
            raise BackfillError(f"{book} {chapter} 沒有匹配任何 STEP word rows")
        return extract_stepbible.render_markdown(
            reference, verses, include_full_definitions=False
        )


def _atomic_write_if_changed(path: Path, data: bytes) -> bool:
    if path.is_file() and path.read_bytes() == data:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    part = path.with_name(f".{path.name}.{os.getpid()}.{uuid.uuid4().hex}.part")
    try:
        part.write_bytes(data)
        os.replace(part, path)
    finally:
        part.unlink(missing_ok=True)
    return True


def _manifest_update_bytes(
    manifest: Path, book: str, chapter: int, root: Path
) -> tuple[bytes, bool]:
    if not manifest.is_file():
        raise BackfillError(f"缺 source_manifest.md：{manifest}")
    raw = manifest.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    updated = build_source_manifest.preserve_manifest_with_step(
        book, chapter, text, root=root, step_exists=True
    )
    encoded = updated.encode("utf-8")
    if bom:
        encoded = b"\xef\xbb\xbf" + encoded
    return encoded, encoded != raw


def _receipt_bytes(root: Path, book: str, chapter: int, receipt: dict) -> bytes:
    payload = dict(receipt)
    payload["path"] = (
        Path("raw_data") / extract_stepbible.stepbible_filename(book, chapter)
    ).as_posix()
    payload["canonical_source"] = "原文資料（STEP Bible）"
    wrapper = {
        "version": 1,
        "book": canonical_book_name(book),
        "chapter": int(chapter),
        "validation": "deterministic structured STEP source",
        "sources": [payload],
    }
    return (json.dumps(wrapper, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _validate_path(path: Path, book: str, chapter: int, scripture: Path) -> dict:
    verse_count = len(scripture.read_text(encoding="utf-8").splitlines())
    return step_context.validate_step_source(
        path,
        expected_book=book,
        expected_chapter=chapter,
        scripture_verse_count=verse_count,
    )


def _stage_text(text: str, directory: Path, filename: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    stage = directory / f".{filename}.{os.getpid()}.{uuid.uuid4().hex}.part"
    stage.write_bytes(text.encode("utf-8"))
    return stage


def _report_slug(book: str, chapter: int = 1) -> str:
    filename = extract_stepbible.stepbible_filename(book, chapter)
    return filename.removeprefix("stepbible_").rsplit("_", 1)[0]


def run_backfill(
    book: str,
    *,
    chapters: str | Iterable[int] | None = None,
    root: Path = ROOT,
    data_path: Path | None = None,
    dry_run: bool = False,
    force: bool = False,
    download: bool = False,
    extractor: Callable[[str, int], str] | None = None,
    write_report: bool = True,
) -> dict:
    root = Path(root).resolve()
    started = time.perf_counter()
    canonical, book_dir, scripture, expected, selected = select_chapters(root, book, chapters)
    before = safety_snapshot(root, canonical, selected)
    extractor = extractor or StepSourceExtractor(
        Path(data_path) if data_path is not None else root / ".stepbible_data",
        download=download,
    )
    details = []
    errors = []

    for chapter in selected:
        target = root / "raw_data" / extract_stepbible.stepbible_filename(canonical, chapter)
        manifest = book_dir / ".tmp" / f"第{chapter}章" / "source_manifest.md"
        receipt_path = book_dir / ".tmp" / f"第{chapter}章" / "step_source_receipt.json"
        stage = None
        item = {
            "chapter": chapter,
            "source": _relative(root, target),
            "action": None,
            "validation": "FAIL",
            "manifest": "not-updated",
            "receipt": "not-written",
        }
        try:
            if target.exists() and not force:
                validation = _validate_path(target, canonical, chapter, scripture[chapter])
                item["action"] = "reused"
            else:
                content = extractor(canonical, chapter)
                stage = _stage_text(content, target.parent, target.name)
                validation = _validate_path(stage, canonical, chapter, scripture[chapter])
                item["action"] = "would-generate" if dry_run else "generated"

            manifest_bytes, manifest_changed = _manifest_update_bytes(
                manifest, canonical, chapter, root
            )
            receipt_bytes = _receipt_bytes(root, canonical, chapter, validation)
            item.update({
                "validation": "PASS",
                "verses": validation["verses"],
                "words": validation["words"],
                "bytes": validation["bytes"],
                "sha256": validation["sha256"],
            })
            if dry_run:
                item["manifest"] = "would-update" if manifest_changed else "reused"
                item["receipt"] = (
                    "reused" if receipt_path.is_file() and receipt_path.read_bytes() == receipt_bytes
                    else "would-write"
                )
            else:
                if stage is not None:
                    os.replace(stage, target)
                    stage = None
                # Manifest is the public source-of-truth switch.  Commit it
                # last so a receipt write failure can never leave an OK STEP
                # row without its required machine receipt.
                receipt_written = _atomic_write_if_changed(receipt_path, receipt_bytes)
                manifest_written = _atomic_write_if_changed(manifest, manifest_bytes)
                item["manifest"] = "updated" if manifest_written else "reused"
                item["receipt"] = "written" if receipt_written else "reused"
        except Exception as exc:
            item["error"] = str(exc)
            errors.append(f"{canonical} {chapter}: {exc}")
        finally:
            if stage is not None:
                stage.unlink(missing_ok=True)
        details.append(item)

    after = safety_snapshot(root, canonical, selected)
    safety = compare_snapshots(before, after)
    if not safety["byte_identical"]:
        errors.append("production chapter/link/commentary/read-log safety fingerprint changed")

    report = {
        "version": 1,
        "mode": "dry-run" if dry_run else "write",
        "book": canonical,
        "chapters_expected": len(expected),
        "chapters_selected": selected,
        "chapters_processed": len(details),
        "generated": sum(item["action"] == "generated" for item in details),
        "would_generate": sum(item["action"] == "would-generate" for item in details),
        "reused": sum(item["action"] == "reused" for item in details),
        "failed": sum(item["validation"] != "PASS" for item in details),
        "step_validation_pass": sum(item["validation"] == "PASS" for item in details),
        "manifest_updated": sum(item["manifest"] == "updated" for item in details),
        "manifest_would_update": sum(item["manifest"] == "would-update" for item in details),
        "manifest_ready": sum(item["manifest"] in {"updated", "would-update", "reused"} for item in details),
        "receipt_generated": sum(item["receipt"] == "written" for item in details),
        "receipt_would_generate": sum(item["receipt"] == "would-write" for item in details),
        "receipt_ready": sum(item["receipt"] in {"written", "would-write", "reused"} for item in details),
        "step_verses": sum(item.get("verses", 0) for item in details),
        "step_words": sum(item.get("words", 0) for item in details),
        "step_raw_bytes": sum(item.get("bytes", 0) for item in details),
        "duration_seconds": round(time.perf_counter() - started, 3),
        "wall_behavior": "single process; official STEP cache reused; no commentary crawl; no M3/M6/render",
        "safety": {
            "before": before.summary(),
            "after": after.summary(),
            **safety,
        },
        "errors": errors,
        "chapters": details,
    }
    if write_report:
        slug = _report_slug(canonical)
        suffix = "_dry_run" if dry_run else ""
        report_path = root / REPORT_DIR / f"{slug}{suffix}.json"
        _atomic_write_if_changed(
            report_path,
            (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        )
        report["report_path"] = _relative(root, report_path)
    return report


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Idempotently backfill formal STEP sources without reopening chapter lifecycle"
    )
    parser.add_argument("book")
    parser.add_argument("--chapters", help="章號，例如 1-10 或 1,3,5-8；省略＝整卷")
    parser.add_argument("--dry-run", action="store_true", help="完整抽取／驗證但不寫 production artifacts")
    parser.add_argument("--force", action="store_true", help="明確重建既有 STEP；預設只驗證並 reuse")
    parser.add_argument("--download", action="store_true", help="本地 cache 缺官方檔時下載；不抓 commentary")
    parser.add_argument("--data-path", default=None, help="STEPBible-Data cache（預設 .stepbible_data）")
    return parser


def main(argv=None) -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")
    args = build_arg_parser().parse_args(argv)
    try:
        report = run_backfill(
            args.book,
            chapters=args.chapters,
            data_path=Path(args.data_path) if args.data_path else None,
            dry_run=args.dry_run,
            force=args.force,
            download=args.download,
        )
    except (OSError, UnicodeError, ValueError, BackfillError) as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1
    print(f"{report['book']} STEP backfill ({report['mode']})")
    print(f"chapters: {report['chapters_processed']} / expected {report['chapters_expected']}")
    print(
        f"generated: {report['generated']}  would_generate: {report['would_generate']}  "
        f"reused: {report['reused']}  failed: {report['failed']}"
    )
    print(
        f"STEP validation: {report['step_validation_pass']} PASS  "
        f"manifest: {report['manifest_ready']} ready  receipt: {report['receipt_ready']} ready"
    )
    print(f"report: {report.get('report_path', '(disabled)')}")
    print(
        "No production chapter/link/commentary/read-log content modified."
        if report["safety"]["byte_identical"]
        else "SAFETY FAILURE: protected content changed."
    )
    for error in report["errors"]:
        print(f"❌ {error}", file=sys.stderr)
    return 0 if not report["errors"] and report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
