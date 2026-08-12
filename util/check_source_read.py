#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Source-kind-aware read gate for commentary and structured STEP data.

背景：agent_maintenance_prompt.md 實戰要點 F 記過一次教訓——規格裡可機械驗證的
部分都有閘門（verify_links／validate_knowledge_base…），跑完會亮綠燈；「正式來源全讀」
沒有閘門，於是注意力流向會發亮的那些，通讀那條靜靜縮水，而四道閘門照樣全綠。
2026-08-03 再次復發：創48 的 BH、創49 的 KC 與 BH、創50 的 GT 後半／KC／BH 只做了
關鍵字 grep 就往下寫，漏掉整批材料（KC 創49 對中間六支派的末世解讀、GT 創50 丁良才
的約瑟預表基督對照表、BH 創48 的猶太祝福傳統）。

Commentary（逐節註解／拾穗／研經註解）：每章在 `.tmp/第x章/read_log.md`
登記每個 OK commentary，每個要給
  - 檔名（對得上 source_manifest 宣告的 raw_data 檔）
  - 三段逐字引句，其中**至少一段必須出自該檔後三分之一**
逐字比對 raw_data 原檔；對不上、缺來源、或三段都擠在前段，一律 FAIL。
只 grep 幾個關鍵字湊不出後段引句——這正是本閘門要擋的抄近路。

STEP（原文資料）不是 prose commentary，不要求 Agent 人工逐詞通讀數百 rows。
完整 raw STEP 由 deterministic parser 驗 book/chapter、verse coverage、word rows、
Strong、morphology、original script 與 SHA-256，receipt 寫到
`.tmp/第x章/step_source_receipt.json`。這是改驗證方式，不是免驗。

格式（read_log.md）：

    # 來源讀取回執：創世記 第46章

    ## raw_data/ccbiblestudy_CT_genesis_46.txt
    - 行數：308
    - 引句：本節的『獻祭』在原文是複數詞
    - 引句：這證明雅各那時心中躕躇、畏懼
    - 引句：因為凡牧羊的都被埃及人所厭惡

用法：
    python util/check_source_read.py 創世記 46
    python util/check_source_read.py 創世記 46 --strict-lines   # 併驗行數
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIN_QUOTES = 3
MIN_QUOTE_LEN = 8
TAIL_FRACTION = 2.0 / 3.0


def _chapter_dir(book: str, chapter: int, root: Path = ROOT) -> Path:
    for folder in sorted(Path(root).iterdir()):
        if folder.is_dir() and folder.name.endswith(f" {book}"):
            return folder / ".tmp" / f"第{chapter}章"
    raise SystemExit(f"❌ 找不到書卷資料夾：{book}")


def _manifest_identities(chapter_dir: Path, root: Path = ROOT):
    """Read the canonical identity/type mapping for every OK formal source."""
    manifest = chapter_dir / "source_manifest.md"
    try:
        try:
            from . import source_excerpts
        except ImportError:
            import source_excerpts
        return source_excerpts.manifest_source_identities(manifest, root)
    except (OSError, ValueError):
        return []


def _relative_source(identity, root: Path) -> str:
    try:
        return identity.path.relative_to(root).as_posix()
    except ValueError:
        return identity.path.as_posix()


def validate_structured_sources(
    book: str,
    chapter: int,
    *,
    root: Path = ROOT,
    write_receipt: bool = True,
) -> tuple[list[str], list[dict]]:
    """Machine-validate all manifest structured sources and persist receipts."""
    root = Path(root)
    chapter_dir = _chapter_dir(book, chapter, root)
    identities = _manifest_identities(chapter_dir, root)
    structured = [item for item in identities if item.is_structured]
    problems: list[str] = []
    receipts: list[dict] = []
    try:
        try:
            from .book_paths import canonical_book_name
        except ImportError:
            from book_paths import canonical_book_name
        canonical = canonical_book_name(book)
    except ValueError:
        canonical = book
    scripture_path = root / "raw_scripture" / canonical / f"第{int(chapter)}章.txt"
    scripture_count = None
    if scripture_path.is_file():
        scripture_count = len(scripture_path.read_text(encoding="utf-8").splitlines())
    try:
        try:
            from . import step_context
        except ImportError:
            import step_context
        for identity in structured:
            relative = _relative_source(identity, root)
            try:
                receipt = step_context.validate_step_source(
                    identity.path,
                    expected_book=book,
                    expected_chapter=chapter,
                    scripture_verse_count=scripture_count,
                )
                receipt["path"] = relative
                receipt["canonical_source"] = identity.canonical_label
                receipts.append(receipt)
            except (OSError, UnicodeError, ValueError) as exc:
                problems.append(f"{relative}：STEP machine validation FAIL（{exc}）")
                receipts.append({
                    "validation": "machine",
                    "status": "FAIL",
                    "path": relative,
                    "canonical_source": identity.canonical_label,
                    "error": str(exc),
                })
    except ImportError as exc:
        problems.append(f"STEP machine validator 無法載入：{exc}")

    if write_receipt and structured:
        payload = {
            "version": 1,
            "book": book,
            "chapter": int(chapter),
            "validation": "deterministic structured STEP source",
            "sources": receipts,
        }
        (chapter_dir / "step_source_receipt.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    return problems, receipts


def _parse_log(path: Path) -> dict[str, dict]:
    entries: dict[str, dict] = {}
    current: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        head = re.match(r"^##\s+(raw_data/\S+\.txt)\s*$", line.strip())
        if head:
            current = head.group(1)
            entries[current] = {"lines": None, "quotes": []}
            continue
        if current is None:
            continue
        stripped = line.strip()
        m_lines = re.match(r"^-\s*行數[：:]\s*(\d+)\s*$", stripped)
        if m_lines:
            entries[current]["lines"] = int(m_lines.group(1))
            continue
        m_quote = re.match(r"^-\s*引句[：:]\s*(.+?)\s*$", stripped)
        if m_quote:
            entries[current]["quotes"].append(m_quote.group(1))
    return entries


def _quote_position(raw_lines: list[str], quote: str) -> int | None:
    """回傳引句所在的行號（1-based）；找不到回 None。"""
    for idx, line in enumerate(raw_lines, 1):
        if quote in line:
            return idx
    # 允許跨行（raw 有硬換行）：把全文壓成一行再找，位置以字元比例換算
    joined = "".join(raw_lines)
    pos = joined.find(quote)
    if pos < 0:
        return None
    consumed = 0
    for idx, line in enumerate(raw_lines, 1):
        consumed += len(line)
        if consumed >= pos:
            return idx
    return len(raw_lines)


def check(book: str, chapter: int, strict_lines: bool = False, *, root: Path = ROOT) -> list[str]:
    root = Path(root)
    chapter_dir = _chapter_dir(book, chapter, root)
    problems: list[str] = []
    identities = _manifest_identities(chapter_dir, root)
    if not identities:
        problems.append(
            "source_manifest.md 沒有可辨識的 OK 正式來源；read gate 不得在空來源下通過"
        )
    commentary = [item for item in identities if not item.is_structured]
    declared = [_relative_source(item, root) for item in commentary]
    log_path = chapter_dir / "read_log.md"
    if commentary and not log_path.exists():
        problems.append(
            f"缺 {log_path.relative_to(root).as_posix()}——commentary 尚未登記全文讀取回執。"
            "CT／GT／KingComments／BibleHub 必須全文閱讀；STEP 另走 machine gate。"
        )
        logged = {}
    else:
        logged = _parse_log(log_path) if log_path.exists() else {}

    for src in declared:
        if src not in logged:
            problems.append(f"read_log.md 沒有登記來源：{src}")

    for src, info in logged.items():
        if src not in declared:
            # Legacy read_log may still contain a STEP quote block. It is no
            # longer required and must not override the machine validator.
            continue
        raw_path = root / src
        if not raw_path.exists():
            problems.append(f"{src}：raw_data 檔不存在")
            continue
        raw_lines = raw_path.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
        total = len(raw_lines)
        if strict_lines and info["lines"] is not None and info["lines"] != total:
            problems.append(f"{src}：登記行數 {info['lines']}，實際 {total}")
        quotes = [q for q in info["quotes"] if len(q) >= MIN_QUOTE_LEN]
        if len(quotes) < MIN_QUOTES:
            problems.append(
                f"{src}：需要 {MIN_QUOTES} 段逐字引句（每段至少 {MIN_QUOTE_LEN} 字），"
                f"目前 {len(quotes)} 段"
            )
            continue
        positions = []
        for quote in quotes:
            pos = _quote_position(raw_lines, quote)
            if pos is None:
                problems.append(f"{src}：引句在原檔逐字比對不到 →「{quote[:40]}」")
            else:
                positions.append(pos)
        if positions and max(positions) < total * TAIL_FRACTION:
            problems.append(
                f"{src}：{len(positions)} 段引句全部落在前 {int(TAIL_FRACTION * 100)}%"
                f"（最後一段在第 {max(positions)} 行／共 {total} 行）——"
                "至少要有一段出自檔案後三分之一，證明讀到底"
            )
    structured_problems, _receipts = validate_structured_sources(
        book, chapter, root=root, write_receipt=True
    )
    problems.extend(structured_problems)
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description="驗證本章所有 OK 正式來源的讀取回執")
    parser.add_argument("book")
    parser.add_argument("chapter", type=int)
    parser.add_argument("--strict-lines", action="store_true", help="併驗登記的行數")
    args = parser.parse_args()

    problems = check(args.book, args.chapter, args.strict_lines)
    if problems:
        print(f"❌ 來源讀取回執未過（{len(problems)} 項）：")
        for item in problems:
            print(f"   - {item}")
        print("結論：FAIL")
        return 1
    identities = _manifest_identities(_chapter_dir(args.book, args.chapter), ROOT)
    commentary_count = sum(not item.is_structured for item in identities)
    structured_count = sum(item.is_structured for item in identities)
    print(
        f"✅ {args.book} 第{args.chapter}章：{commentary_count} 個 commentary 全文回執通過；"
        f"{structured_count} 個 STEP structured source machine validation 通過"
    )
    print("結論：PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
