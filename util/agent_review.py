#!/usr/bin/env python3
"""Multi-agent evidence-review checkpoints for M3/M6/B-class payloads.

This tool records a tiny per-chapter review receipt in ``agent_review.yaml``.
The receipt is version-bound by SHA-256: once Claude changes reviewed content,
Codex's previous PASS becomes stale automatically.

Typical flow:

  python util/agent_review.py submit 申命記 1 m3
  # Claude delegates read-only review to Codex using agent_evidence_audit_prompt.md
  python util/agent_review.py verdict 申命記 1 m3 changes_required --sha <sha> --thread-id <id> --findings-count 3
  # Claude fixes payload and submits again
  python util/agent_review.py submit 申命記 1 m3
  python util/agent_review.py verdict 申命記 1 m3 pass --sha <new-sha> --thread-id <id> --findings-count 0
  python util/agent_review.py gate 申命記 1 m3

Stages:
- m3: ``entry_content/*.yaml``
- m6: ``chapter_content.yaml`` + current M3 fingerprint
- link_updates: ``link_updates.yaml`` + current M3/M6 fingerprints
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Iterable

import yaml

try:
    from .book_paths import book_directory, canonical_book_name
except ImportError:
    from book_paths import book_directory, canonical_book_name

ROOT = Path(__file__).resolve().parent.parent
STATE_FILENAME = "agent_review.yaml"
STATE_VERSION = 1
STAGES = ("m3", "m6", "link_updates")
VERDICTS = ("pass", "changes_required", "blocked")


class ReviewGateError(ValueError):
    pass


def _ctx(book: str, chapter: int, root: Path = ROOT):
    canonical = canonical_book_name(book)
    tmp = book_directory(Path(root), canonical) / ".tmp" / f"第{int(chapter)}章"
    return canonical, int(chapter), tmp


def _state_path(book: str, chapter: int, root: Path = ROOT) -> Path:
    return _ctx(book, chapter, root)[2] / STATE_FILENAME


def _read_state(book: str, chapter: int, root: Path = ROOT) -> dict:
    canonical, chapter_num, _ = _ctx(book, chapter, root)
    path = _state_path(canonical, chapter_num, root)
    if not path.is_file():
        return {
            "version": STATE_VERSION,
            "book": canonical,
            "chapter": chapter_num,
            "stages": {},
        }
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ReviewGateError(f"{path}: review state 必須是 YAML 物件")
    if data.get("book") not in (None, canonical) or data.get("chapter") not in (None, chapter_num):
        raise ReviewGateError(f"{path}: book/chapter 與目前章節不一致")
    data.setdefault("version", STATE_VERSION)
    data["book"] = canonical
    data["chapter"] = chapter_num
    data.setdefault("stages", {})
    return data


def _write_state(book: str, chapter: int, data: dict, root: Path = ROOT) -> Path:
    path = _state_path(book, chapter, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return path


def _digest_parts(parts: Iterable[tuple[str, bytes]]) -> str:
    digest = hashlib.sha256()
    for label, payload in parts:
        digest.update(label.encode("utf-8"))
        digest.update(b"\0")
        digest.update(payload)
        digest.update(b"\0")
    return digest.hexdigest()


def _file_part(path: Path, base: Path) -> tuple[str, bytes]:
    if not path.is_file():
        raise ReviewGateError(f"找不到 review 目標：{path}")
    return path.relative_to(base).as_posix(), path.read_bytes()


def stage_fingerprint(book: str, chapter: int, stage: str, root: Path = ROOT) -> str:
    if stage not in STAGES:
        raise ReviewGateError(f"未知 stage：{stage}")
    canonical, chapter_num, tmp = _ctx(book, chapter, root)

    if stage == "m3":
        entry_dir = tmp / "entry_content"
        files = sorted(entry_dir.glob("*.yaml")) if entry_dir.is_dir() else []
        # Empty M3 is still fingerprintable: chapters with no C-class entries may
        # legitimately have nothing to review in entry_content.
        parts = [("stage", b"m3")]
        parts.extend(_file_part(path, tmp) for path in files)
        return _digest_parts(parts)

    if stage == "m6":
        m3_hash = stage_fingerprint(canonical, chapter_num, "m3", root)
        parts = [
            ("stage", b"m6"),
            ("m3_sha256", m3_hash.encode("ascii")),
            _file_part(tmp / "chapter_content.yaml", tmp),
        ]
        return _digest_parts(parts)

    m3_hash = stage_fingerprint(canonical, chapter_num, "m3", root)
    m6_hash = stage_fingerprint(canonical, chapter_num, "m6", root)
    parts = [
        ("stage", b"link_updates"),
        ("m3_sha256", m3_hash.encode("ascii")),
        ("m6_sha256", m6_hash.encode("ascii")),
        _file_part(tmp / "link_updates.yaml", tmp),
    ]
    return _digest_parts(parts)


def _stage_record(state: dict, stage: str) -> dict:
    stages = state.setdefault("stages", {})
    record = stages.get(stage)
    return record if isinstance(record, dict) else {}


def require_pass(book: str, chapter: int, stage: str, root: Path = ROOT) -> dict:
    state = _read_state(book, chapter, root)
    record = _stage_record(state, stage)
    if not record:
        raise ReviewGateError(
            f"{stage} 尚未建立 review checkpoint；先跑："
            f"python util/agent_review.py submit {book} {chapter} {stage}"
        )
    current = stage_fingerprint(book, chapter, stage, root)
    recorded = str(record.get("sha256") or "")
    if recorded != current:
        raise ReviewGateError(
            f"{stage} 內容在上次 review 後已變更：recorded={recorded or 'none'} current={current}。"
            f"舊 PASS 已失效；重新 submit → Codex review。"
        )
    if record.get("codex") != "pass":
        raise ReviewGateError(
            f"{stage} 尚未取得 Codex PASS（目前 {record.get('codex', 'pending')}，round={record.get('round', 0)}）。"
        )
    return record


def submit(book: str, chapter: int, stage: str, root: Path = ROOT) -> tuple[Path, dict]:
    canonical, chapter_num, _ = _ctx(book, chapter, root)
    if stage == "m6":
        require_pass(canonical, chapter_num, "m3", root)
    elif stage == "link_updates":
        require_pass(canonical, chapter_num, "m6", root)

    state = _read_state(canonical, chapter_num, root)
    previous = _stage_record(state, stage)
    current = stage_fingerprint(canonical, chapter_num, stage, root)
    changed = previous.get("sha256") != current
    if previous:
        round_num = int(previous.get("round") or 1) + (1 if changed else 0)
        claude_status = "revised" if changed else str(previous.get("claude") or "ready")
    else:
        round_num = 1
        claude_status = "ready"

    record = {
        "round": round_num,
        "sha256": current,
        "claude": claude_status,
        "codex": "pending",
    }
    if previous.get("thread_id"):
        record["thread_id"] = previous["thread_id"]
    state["stages"][stage] = record
    path = _write_state(canonical, chapter_num, state, root)
    return path, record


def record_verdict(
    book: str,
    chapter: int,
    stage: str,
    verdict: str,
    review_sha: str,
    *,
    thread_id: str | None = None,
    findings_count: int | None = None,
    root: Path = ROOT,
) -> tuple[Path, dict]:
    if verdict not in VERDICTS:
        raise ReviewGateError(f"verdict 必須是：{', '.join(VERDICTS)}")
    canonical, chapter_num, _ = _ctx(book, chapter, root)
    state = _read_state(canonical, chapter_num, root)
    record = _stage_record(state, stage)
    if not record:
        raise ReviewGateError(f"{stage} 尚未 submit，不能記錄 Codex verdict")
    current = stage_fingerprint(canonical, chapter_num, stage, root)
    if review_sha != current or review_sha != record.get("sha256"):
        raise ReviewGateError(
            "Codex verdict 的 SHA 與目前內容不一致；拒絕記錄過期 review。"
            f" expected={current} submitted={record.get('sha256')} got={review_sha}"
        )
    record["codex"] = verdict
    if thread_id:
        record["thread_id"] = thread_id
    if findings_count is not None:
        record["findings_count"] = int(findings_count)
    state["stages"][stage] = record
    path = _write_state(canonical, chapter_num, state, root)
    return path, record


def status_rows(book: str, chapter: int, root: Path = ROOT) -> list[tuple[str, dict, str | None, bool]]:
    state = _read_state(book, chapter, root)
    rows = []
    for stage in STAGES:
        record = _stage_record(state, stage)
        current = None
        error = None
        try:
            current = stage_fingerprint(book, chapter, stage, root)
        except ReviewGateError as exc:
            error = str(exc)
        fresh = bool(record and current and record.get("sha256") == current)
        rows.append((stage, record, error, fresh))
    return rows


def _print_submit(book: str, chapter: int, stage: str, path: Path, record: dict):
    print(f"✅ Claude checkpoint：{book} 第{chapter}章 {stage} round {record['round']}")
    print(f"   sha256：{record['sha256']}")
    print(f"   state：{path}")
    if record.get("thread_id"):
        print(f"   Codex thread：{record['thread_id']}（優先 resume 同一 thread 做增量複核）")
    print("   下一步：讓 Codex read-only 讀 agent_evidence_audit_prompt.md，")
    print(f"   指定 stage={stage}、book={book}、chapter={chapter}、sha256={record['sha256']}。")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    submit_parser = sub.add_parser("submit", help="Claude 完稿 checkpoint；計算 hash 並令舊 PASS 失效")
    submit_parser.add_argument("book")
    submit_parser.add_argument("chapter", type=int)
    submit_parser.add_argument("stage", choices=STAGES)

    verdict_parser = sub.add_parser("verdict", help="記錄 Codex 對指定 hash 的 review 結果")
    verdict_parser.add_argument("book")
    verdict_parser.add_argument("chapter", type=int)
    verdict_parser.add_argument("stage", choices=STAGES)
    verdict_parser.add_argument("status", choices=VERDICTS)
    verdict_parser.add_argument("--sha", required=True, help="Codex 回覆 footer 中的 REVIEW_SHA256")
    verdict_parser.add_argument("--thread-id")
    verdict_parser.add_argument("--findings-count", type=int)

    gate_parser = sub.add_parser("gate", help="確認目前內容 hash 與 Codex PASS 完全一致")
    gate_parser.add_argument("book")
    gate_parser.add_argument("chapter", type=int)
    gate_parser.add_argument("stage", choices=STAGES)

    status_parser = sub.add_parser("status", help="顯示一章三個 review stage 的 freshness / verdict")
    status_parser.add_argument("book")
    status_parser.add_argument("chapter", type=int)

    args = parser.parse_args()
    try:
        if args.command == "submit":
            path, record = submit(args.book, args.chapter, args.stage)
            _print_submit(canonical_book_name(args.book), args.chapter, args.stage, path, record)
            return 0
        if args.command == "verdict":
            path, record = record_verdict(
                args.book,
                args.chapter,
                args.stage,
                args.status,
                args.sha,
                thread_id=args.thread_id,
                findings_count=args.findings_count,
            )
            print(
                f"✅ Codex verdict 已記錄：{args.stage}={record['codex']} "
                f"round={record['round']} sha256={record['sha256']}"
            )
            print(f"   state：{path}")
            return 0 if record["codex"] == "pass" else 2
        if args.command == "gate":
            record = require_pass(args.book, args.chapter, args.stage)
            print(
                f"✅ review gate PASS：{canonical_book_name(args.book)} 第{args.chapter}章 "
                f"{args.stage} round {record['round']} sha256={record['sha256']}"
            )
            return 0

        print(f"Review status：{canonical_book_name(args.book)} 第{args.chapter}章")
        for stage, record, error, fresh in status_rows(args.book, args.chapter):
            if error:
                print(f"- {stage}: unavailable（{error}）")
                continue
            if not record:
                print(f"- {stage}: not-submitted")
                continue
            freshness = "fresh" if fresh else "STALE"
            thread = f" thread={record.get('thread_id')}" if record.get("thread_id") else ""
            print(
                f"- {stage}: {freshness} round={record.get('round')} "
                f"claude={record.get('claude')} codex={record.get('codex')}"
                f" sha256={record.get('sha256')}{thread}"
            )
        return 0
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"❌ {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
