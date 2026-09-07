#!/usr/bin/env python3
"""Bounded multi-agent evidence-review checkpoints for M3/M6/B payloads.

Each stage gets at most two substantive reviewer attempts total. Codex is the
primary reviewer; Antigravity may take over when Codex is unavailable or quota-
blocked. The budget belongs to the stage, not to a particular reviewer, so a
handoff never resets the counter.

After the second CHANGES_REQUIRED verdict, Claude gets one final correction.
When that correction changes the stage fingerprint, ``submit`` records a
FORCED PASS for the new hash instead of opening a third reviewer call. Forced
passes stay explicit in ``agent_review.yaml`` so they are never confused with a
clean reviewer PASS.

Typical flow::

  python util/agent_review.py submit 申命記 1 m3
  python util/agent_review.py verdict 申命記 1 m3 changes_required --sha <sha> --reviewer codex --findings-count 3
  # Claude fixes round-1 findings
  python util/agent_review.py submit 申命記 1 m3
  python util/agent_review.py verdict 申命記 1 m3 changes_required --sha <sha2> --reviewer codex --findings-count 1
  # Claude makes the final correction; NO third reviewer call
  python util/agent_review.py submit 申命記 1 m3
  python util/agent_review.py gate 申命記 1 m3

If the content already moved on before the verdict is recorded (the reversed
order that once evaporated an attempt), record it late against the sha the
reviewer actually saw::

  python util/agent_review.py verdict 申命記 1 m3 pass --sha <seen> --observed-sha <seen>

The attempt still counts (flagged ``late_recorded``) but is bound only to
``<seen>``; the current bytes must be re-submitted to pass the gate.

Stages (each fingerprint covers only that stage's own reviewed files, plus the
approved upstream stage hashes as parents; the exact list is written to the
receipt as ``hash_inputs`` so a verdict's scope is auditable after the fact):
- m3: ``entry_content/*.yaml``
- m6: ``chapter_content.yaml`` + current M3 fingerprint
- link_updates: ``link_updates.yaml`` + current M3/M6 fingerprints

There is deliberately no ``--allow-same-sha`` style bypass: if the recorded sha
does not match current content, re-submit (``FORCED PASS`` once the budget is
spent) — never widen the gate to make a stale verdict fit.
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
    from .yaml_io import write_yaml_atomic
except ImportError:
    from book_paths import book_directory, canonical_book_name
    from yaml_io import write_yaml_atomic

ROOT = Path(__file__).resolve().parent.parent
STATE_FILENAME = "agent_review.yaml"
STATE_VERSION = 2
STAGES = ("m3", "m6", "link_updates")
VERDICTS = ("pass", "changes_required", "blocked")
REVIEWERS = ("codex", "antigravity")
MAX_REVIEW_ATTEMPTS = 2


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
    # Older v1 receipts remain readable. They migrate lazily the next time a
    # stage is submitted or receives a verdict.
    data.setdefault("version", 1)
    data["book"] = canonical
    data["chapter"] = chapter_num
    data.setdefault("stages", {})
    return data


def _write_state(book: str, chapter: int, data: dict, root: Path = ROOT) -> Path:
    path = _state_path(book, chapter, root)
    data["version"] = STATE_VERSION
    return write_yaml_atomic(path, data)


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


def _stage_parts(book: str, chapter: int, stage: str,
                 root: Path = ROOT) -> tuple[list[tuple[str, bytes]], list[str]]:
    """(digest 輸入 parts, 人可讀的涵蓋清單)。

    每個 stage 只涵蓋「該 stage 實際被審的檔案」＋上游已核准 stage 的 hash 當
    parent，兩者一起決定 fingerprint。涵蓋清單會寫進 receipt 供事後稽核，也讓
    「只改 chapter_content.yaml → 只有 m6 hash 變」這件事看得見、可回歸。
    """
    if stage not in STAGES:
        raise ReviewGateError(f"未知 stage：{stage}")
    canonical, chapter_num, tmp = _ctx(book, chapter, root)

    if stage == "m3":
        entry_dir = tmp / "entry_content"
        files = sorted(entry_dir.glob("*.yaml")) if entry_dir.is_dir() else []
        parts = [("stage", b"m3")]
        parts.extend(_file_part(path, tmp) for path in files)
        covered = [path.relative_to(tmp).as_posix() for path in files]
        return parts, covered

    if stage == "m6":
        m3_hash = stage_fingerprint(canonical, chapter_num, "m3", root)
        parts = [
            ("stage", b"m6"),
            ("m3_sha256", m3_hash.encode("ascii")),
            _file_part(tmp / "chapter_content.yaml", tmp),
        ]
        return parts, [f"parent:m3={m3_hash}", "chapter_content.yaml"]

    m3_hash = stage_fingerprint(canonical, chapter_num, "m3", root)
    m6_hash = stage_fingerprint(canonical, chapter_num, "m6", root)
    parts = [
        ("stage", b"link_updates"),
        ("m3_sha256", m3_hash.encode("ascii")),
        ("m6_sha256", m6_hash.encode("ascii")),
        _file_part(tmp / "link_updates.yaml", tmp),
    ]
    return parts, [f"parent:m3={m3_hash}", f"parent:m6={m6_hash}", "link_updates.yaml"]


def stage_fingerprint(book: str, chapter: int, stage: str, root: Path = ROOT) -> str:
    parts, _covered = _stage_parts(book, chapter, stage, root)
    return _digest_parts(parts)


def stage_hash_inputs(book: str, chapter: int, stage: str, root: Path = ROOT) -> list[str]:
    """該 stage 的 fingerprint 實際涵蓋了哪些檔案／parent hash（寫進 receipt）。"""
    _parts, covered = _stage_parts(book, chapter, stage, root)
    return covered


def _stage_record(state: dict, stage: str) -> dict:
    stages = state.setdefault("stages", {})
    record = stages.get(stage)
    return record if isinstance(record, dict) else {}


def _review_status(record: dict) -> str:
    # v1 compatibility: old receipts stored the status under ``codex``.
    return str(record.get("reviewer_status") or record.get("codex") or "pending")


def _review_attempts(record: dict) -> int:
    try:
        return max(0, int(record.get("review_attempts") or 0))
    except (TypeError, ValueError):
        return 0


def _reviewer_agent(record: dict) -> str | None:
    value = record.get("reviewer_agent")
    if value:
        return str(value)
    if "codex" in record:
        return "codex"
    return None


def _history(record: dict) -> list[dict]:
    value = record.get("review_history")
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


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
            "舊 PASS 已失效；重新 submit。若兩次 review 已用完，submit 會建立明示的 FORCED PASS，"
            "不再呼叫 reviewer。"
        )
    # 補記（--observed-sha）的 verdict 掛在 reviewer 當時看過的 sha 上；若那不是
    # 目前內容，這次 PASS 不追認目前版本，仍須重新 submit（額度用盡則 FORCED PASS）。
    verdict_sha = str(record.get("verdict_sha") or recorded)
    if verdict_sha != current and not record.get("forced_pass"):
        raise ReviewGateError(
            f"{stage} 目前的 PASS 是補記在 reviewer 當時看到的版本（{verdict_sha}），"
            f"與目前內容（{current}）不同；重新 submit 讓程式對新版本判定"
            "（兩次 review 已用完時會自動 FORCED PASS）。"
        )
    status = _review_status(record)
    if status != "pass":
        raise ReviewGateError(
            f"{stage} 尚未 PASS（目前 {status}，review_attempts="
            f"{_review_attempts(record)}/{MAX_REVIEW_ATTEMPTS}）。"
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
        try:
            previous_revision = int(previous.get("revision") or previous.get("round") or 1)
        except (TypeError, ValueError):
            previous_revision = 1
        revision = previous_revision + (1 if changed else 0)
    else:
        revision = 1

    attempts = _review_attempts(previous)
    history = _history(previous)
    previous_status = _review_status(previous) if previous else "pending"
    next_review_round = min(attempts + 1, MAX_REVIEW_ATTEMPTS)

    if previous and not changed:
        # Re-submitting identical bytes must not erase an existing verdict or
        # manufacture another reviewer opportunity.
        record = dict(previous)
        record.setdefault("revision", revision)
        record.setdefault("review_attempts", attempts)
        record.setdefault("reviewer_status", previous_status)
        record.setdefault("reviewer_agent", _reviewer_agent(previous))
        record.setdefault("review_history", history)
        record["round"] = min(max(1, int(record.get("round") or next_review_round)), MAX_REVIEW_ATTEMPTS)
        record["sha256"] = current
    elif previous and changed and attempts >= MAX_REVIEW_ATTEMPTS:
        # Hard token-budget rule: after two substantive reviews, Claude may
        # make one final correction but NO third model review is allowed. Bind
        # a forced pass to the new bytes so the old hash cannot leak through.
        record = {
            "round": MAX_REVIEW_ATTEMPTS,
            "revision": revision,
            "sha256": current,
            "verdict_sha": current,
            "claude": "revised",
            "reviewer_status": "pass",
            "reviewer_agent": _reviewer_agent(previous),
            "review_attempts": attempts,
            "forced_pass": True,
            "forced_reason": "max_review_attempts_exhausted_after_final_revision",
            "review_history": history,
        }
        if previous.get("findings_count") is not None:
            record["forced_from_findings_count"] = int(previous.get("findings_count") or 0)
        if previous.get("thread_id"):
            record["thread_id"] = previous["thread_id"]
    else:
        record = {
            "round": next_review_round,
            "revision": revision,
            "sha256": current,
            "claude": "revised" if previous and changed else "ready",
            "reviewer_status": "pending",
            "reviewer_agent": None,
            "review_attempts": attempts,
            "forced_pass": False,
            "review_history": history,
        }
        if previous.get("thread_id"):
            record["thread_id"] = previous["thread_id"]

    # New v2 records use generic reviewer fields. Remove the old alias after a
    # stage is touched so Antigravity handoffs are represented honestly.
    record.pop("codex", None)
    # 稽核用：這個 sha 到底涵蓋了哪些檔案／上游 hash。事後看 receipt 就能確認
    # verdict 掛對了範圍，不必再靠「reviewer 自己加 --allow-same-sha」那種旁路。
    record["hash_inputs"] = stage_hash_inputs(canonical, chapter_num, stage, root)
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
    reviewer: str = "codex",
    thread_id: str | None = None,
    findings_count: int | None = None,
    observed_sha: str | None = None,
    root: Path = ROOT,
) -> tuple[Path, dict]:
    if verdict not in VERDICTS:
        raise ReviewGateError(f"verdict 必須是：{', '.join(VERDICTS)}")
    if reviewer not in REVIEWERS:
        raise ReviewGateError(f"reviewer 必須是：{', '.join(REVIEWERS)}")

    canonical, chapter_num, _ = _ctx(book, chapter, root)
    state = _read_state(canonical, chapter_num, root)
    record = _stage_record(state, stage)
    if not record:
        raise ReviewGateError(f"{stage} 尚未 submit，不能記錄 reviewer verdict")

    current = stage_fingerprint(canonical, chapter_num, stage, root)
    recorded = record.get("sha256")
    if observed_sha is not None and observed_sha != review_sha:
        raise ReviewGateError(
            "--observed-sha 必須等於 --sha（reviewer footer 的 REVIEW_SHA256）；"
            "這個旗標只是明示「我知道這個 sha 已非最新，仍要為那次 attempt 補記」。"
        )
    late_recorded = False
    if review_sha == current and review_sha == recorded:
        effective_sha = review_sha
    elif observed_sha is not None and review_sha == observed_sha:
        # 補記：reviewer 當時看到的是 observed_sha，之後內容或 submit 記錄已前進
        # （第1章 m6「搞反順序」那次就是這樣把一個 attempt 直接蒸發掉）。這次
        # attempt 照算，但只掛在 reviewer 實際看過的 sha 上——不追認目前內容。
        late_recorded = True
        effective_sha = observed_sha
    else:
        raise ReviewGateError(
            "reviewer verdict 的 SHA 與目前內容不一致；拒絕靜默丟棄這次 review。\n"
            f"  reviewer 看到（--sha）     ：{review_sha}\n"
            f"  submit 當時記錄（recorded）：{recorded or 'none'}\n"
            f"  目前內容（current）        ：{current}\n"
            "  若 verdict 確實是對 reviewer 當時看到的版本，明示補記（該次 attempt 照算）：\n"
            f"    python util/agent_review.py verdict {canonical} {chapter_num} {stage} "
            f"{verdict} --sha {review_sha} --observed-sha {review_sha}"
            + (f" --reviewer {reviewer}" if reviewer != "codex" else "")
            + (f" --findings-count {findings_count}" if findings_count is not None else "")
        )
    if record.get("forced_pass"):
        raise ReviewGateError(
            f"{stage} 已因兩次 review 用盡而 FORCED PASS；禁止再花 token 做第三次 review。"
        )

    attempts = _review_attempts(record)
    substantive = verdict in ("pass", "changes_required")
    if substantive:
        last_substantive = next(
            (item for item in reversed(_history(record)) if item.get("attempt") is not None),
            None,
        )
        if last_substantive and last_substantive.get("sha256") == review_sha:
            raise ReviewGateError(
                f"{stage} 這個 SHA 已做過 substantive review；不要把第二次機會浪費在同一版本。"
                "先讓 Claude 依 findings 修改並重新 submit；若只是 Codex quota/tool BLOCKED，"
                "則 blocked 不耗 attempt，Antigravity 可直接接手。"
            )
    if substantive and attempts >= MAX_REVIEW_ATTEMPTS:
        raise ReviewGateError(
            f"{stage} 的 {MAX_REVIEW_ATTEMPTS} 次 substantive review 已用完；"
            "不要再呼叫 reviewer。若上一輪要求修改，讓 Claude 做最後修正後重新 submit，"
            "程式會對新 hash 建立明示的 FORCED PASS。"
        )

    if substantive:
        attempts += 1

    record["reviewer_status"] = verdict
    record["reviewer_agent"] = reviewer
    record["review_attempts"] = attempts
    record["round"] = min(max(1, attempts if substantive else attempts + 1), MAX_REVIEW_ATTEMPTS)
    record["forced_pass"] = False
    # 這個 verdict 實際適用的 sha。正常情形 == 目前內容；補記時掛在 reviewer
    # 當時看過的舊 sha 上，require_pass 據此拒絕把補記誤當成對目前內容的 PASS。
    record["verdict_sha"] = effective_sha
    if thread_id:
        record["thread_id"] = thread_id
    if findings_count is not None:
        record["findings_count"] = int(findings_count)

    history = _history(record)
    history.append(
        {
            "attempt": attempts if substantive else None,
            "reviewer": reviewer,
            "sha256": effective_sha,
            "verdict": verdict,
            "findings_count": int(findings_count) if findings_count is not None else None,
            "late_recorded": late_recorded,
        }
    )
    record["review_history"] = history
    if verdict == "changes_required" and attempts >= MAX_REVIEW_ATTEMPTS:
        record["final_revision_required"] = True
    else:
        record.pop("final_revision_required", None)
    record.pop("codex", None)

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


def _print_hash_inputs(record: dict):
    inputs = record.get("hash_inputs")
    if isinstance(inputs, list) and inputs:
        print("   hash 涵蓋：" + "、".join(str(x) for x in inputs))


def _print_submit(book: str, chapter: int, stage: str, path: Path, record: dict):
    status = _review_status(record)
    attempts = _review_attempts(record)
    if record.get("forced_pass"):
        print(
            f"⚠️ FORCED PASS：{book} 第{chapter}章 {stage} "
            f"review_attempts={attempts}/{MAX_REVIEW_ATTEMPTS} revision={record.get('revision')}"
        )
        print(f"   sha256：{record['sha256']}")
        _print_hash_inputs(record)
        print("   原因：兩次 reviewer 機會已用完；此版是 Claude 最後修正版，不再呼叫第三次 reviewer。")
        print(f"   state：{path}")
        return

    if status == "pass":
        print(f"✅ review checkpoint 已 PASS：{book} 第{chapter}章 {stage}")
        print(f"   sha256：{record['sha256']}")
        _print_hash_inputs(record)
        print(f"   state：{path}")
        return

    remaining = max(0, MAX_REVIEW_ATTEMPTS - attempts)
    print(
        f"✅ Author checkpoint：{book} 第{chapter}章 {stage} "
        f"review round {record['round']}/{MAX_REVIEW_ATTEMPTS}"
    )
    print(f"   sha256：{record['sha256']}")
    _print_hash_inputs(record)
    print(f"   substantive review 已用：{attempts}/{MAX_REVIEW_ATTEMPTS}；剩餘：{remaining}")
    print(f"   state：{path}")
    print("   下一步：reviewer 讀 agent_evidence_audit_prompt.md。")
    print("   Round 1 必須一次列齊重要 findings；Round 2 是最後一次 reviewer 機會。")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    submit_parser = sub.add_parser("submit", help="作者完稿 checkpoint；計算 hash、控制兩次 review 預算")
    submit_parser.add_argument("book")
    submit_parser.add_argument("chapter", type=int)
    submit_parser.add_argument("stage", choices=STAGES)

    verdict_parser = sub.add_parser("verdict", help="記錄 Codex/Antigravity 對指定 hash 的 review 結果")
    verdict_parser.add_argument("book")
    verdict_parser.add_argument("chapter", type=int)
    verdict_parser.add_argument("stage", choices=STAGES)
    verdict_parser.add_argument("status", choices=VERDICTS)
    verdict_parser.add_argument("--sha", required=True, help="review footer 中的 REVIEW_SHA256")
    verdict_parser.add_argument("--reviewer", choices=REVIEWERS, default="codex")
    verdict_parser.add_argument("--thread-id")
    verdict_parser.add_argument("--findings-count", type=int)
    verdict_parser.add_argument(
        "--observed-sha",
        help="明示補記：verdict 是對 reviewer 當時看到的這個 sha（須等於 --sha）。"
        "內容或 submit 記錄已前進時用它，讓那次 attempt 照算但不追認目前內容。",
    )

    gate_parser = sub.add_parser("gate", help="確認目前 hash 已取得 reviewer PASS 或明示 FORCED PASS")
    gate_parser.add_argument("book")
    gate_parser.add_argument("chapter", type=int)
    gate_parser.add_argument("stage", choices=STAGES)

    status_parser = sub.add_parser("status", help="顯示三個 review stage 的 freshness / budget / verdict")
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
                reviewer=args.reviewer,
                thread_id=args.thread_id,
                findings_count=args.findings_count,
                observed_sha=args.observed_sha,
            )
            status = _review_status(record)
            if record.get("review_history") and record["review_history"][-1].get("late_recorded"):
                print("ℹ️ 已補記（late_recorded）：verdict 掛在 reviewer 當時看到的 sha；"
                      "目前內容仍需重新 submit 才能過 gate。")
            print(
                f"✅ reviewer verdict 已記錄：{args.stage}={status} "
                f"reviewer={record.get('reviewer_agent')} attempts="
                f"{record.get('review_attempts', 0)}/{MAX_REVIEW_ATTEMPTS} sha256={record['sha256']}"
            )
            if record.get("final_revision_required"):
                print("⚠️ 這是第 2/2 次 review，也是最後一次 reviewer 機會。")
                print("   請讓 Claude 完成最後修正後重新 submit；新 hash 會自動 FORCED PASS，禁止第三次 review。")
            print(f"   state：{path}")
            return 0 if status == "pass" else 2
        if args.command == "gate":
            record = require_pass(args.book, args.chapter, args.stage)
            forced = " FORCED" if record.get("forced_pass") else ""
            print(
                f"✅ review gate PASS{forced}：{canonical_book_name(args.book)} 第{args.chapter}章 "
                f"{args.stage} review_attempts={_review_attempts(record)}/{MAX_REVIEW_ATTEMPTS} "
                f"sha256={record['sha256']}"
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
            forced = " forced-pass" if record.get("forced_pass") else ""
            reviewer = _reviewer_agent(record) or "none"
            thread = f" thread={record.get('thread_id')}" if record.get("thread_id") else ""
            print(
                f"- {stage}: {freshness}{forced} review_round={record.get('round')} "
                f"revision={record.get('revision', record.get('round'))} "
                f"claude={record.get('claude')} reviewer={reviewer} status={_review_status(record)} "
                f"attempts={_review_attempts(record)}/{MAX_REVIEW_ATTEMPTS} "
                f"sha256={record.get('sha256')}{thread}"
            )
        return 0
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"❌ {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
