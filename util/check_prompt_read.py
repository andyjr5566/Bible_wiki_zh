#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""M3/M6 Prompt 原檔「全讀」的機械閘門——把 Agent 讀取 Prompt 規格聲明換成可逐字驗證的回執。

背景：Agent 在人工模式手寫 payload 時，常憑經驗盲寫而忽略該章動態算出的 allowed_related/
allowed_links 白名單與字數下限。

作法：每章在 `.tmp/第x章/manual/prompt_read_log.md` 登記 manual/ 目錄下產出的各個 *.prompt.md，
每個要給：
  - 檔名（對得上 manual/ 下的 *.prompt.md 檔）
  - 三段逐字引句，其中至少一段必須出自該檔後三分之一

逐字比對 prompt 原檔；對不上、缺檔、或三段都擠在前段，一律 FAIL。

格式（manual/prompt_read_log.md）：

    # Prompt 讀取回執：民數記 第22章

    ## manual/entry_batch_1.prompt.md
    - 引句：你是聖經研經資料整理員，並且輸出以繁體中文為主
    - 引句：status 一律 formal。accumulations 是「物件陣列」
    - 引句：欄位定義見 entry_content.schema.json

    ## manual/chapter_content.prompt.md
    - 引句：你是聖經研經資料整理員。唯一任務：為 民數記 第22章填寫
    - 引句：organization（本章整理）用「裸 markdown」直接寫在分隔線之後
    - 引句：欄位定義見 chapter_content.schema.json

用法：
    python util/check_prompt_read.py 民數記 22
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIN_QUOTES = 3
MIN_QUOTE_LEN = 8
TAIL_FRACTION = 2.0 / 3.0


def _chapter_dir(book: str, chapter: int) -> Path:
    for folder in sorted(ROOT.iterdir()):
        if folder.is_dir() and folder.name.endswith(f" {book}"):
            return folder / ".tmp" / f"第{chapter}章"
    raise SystemExit(f"❌ 找不到書卷資料夾：{book}")


def _manual_prompts(manual_dir: Path) -> list[str]:
    """讀 manual/ 目錄下實存的所有 *.prompt.md 相對路徑。"""
    if not manual_dir.exists():
        return []
    prompts = sorted(manual_dir.glob("*.prompt.md"))
    return [f"manual/{p.name}" for p in prompts]


def _parse_log(path: Path) -> dict[str, dict]:
    entries: dict[str, dict] = {}
    current: str | None = None
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        head = re.match(r"^##\s+(manual/\S+\.prompt\.md)\s*$", line.strip())
        if head:
            current = head.group(1)
            entries[current] = {"quotes": []}
            continue
        if current is None:
            continue
        stripped = line.strip()
        m_quote = re.match(r"^-\s*引句[：:]\s*(.+?)\s*$", stripped)
        if m_quote:
            entries[current]["quotes"].append(m_quote.group(1))
    return entries


def _quote_position(raw_lines: list[str], quote: str) -> int | None:
    """回傳引句所在的行號（1-based）；找不到回 None。"""
    for idx, line in enumerate(raw_lines, 1):
        if quote in line:
            return idx
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


def check(book: str, chapter: int) -> list[str]:
    chapter_dir = _chapter_dir(book, chapter)
    manual_dir = chapter_dir / "manual"
    log_path = manual_dir / "prompt_read_log.md"
    
    declared_prompts = _manual_prompts(manual_dir)
    if not declared_prompts:
        # 若無 manual prompt 檔，代表未執行過 prompts 或無待寫項
        return []

    if not log_path.exists():
        return [
            f"缺 {log_path.relative_to(ROOT).as_posix()}——Prompt 原檔尚未登記讀取回執。"
            "請先閱讀 manual/*.prompt.md 原檔全文，再依 check_prompt_read.py 檔頭格式於 prompt_read_log.md 登記回執。"
        ]

    problems: list[str] = []
    logged = _parse_log(log_path)

    for p_rel in declared_prompts:
        if p_rel not in logged:
            problems.append(f"prompt_read_log.md 沒有登記 Prompt 檔：{p_rel}")

    for p_rel, info in logged.items():
        # p_rel 已含 manual/ 前綴，直接接在章目錄之後（先前誤把前綴剝掉，導致永遠找不到檔）
        prompt_path = chapter_dir / p_rel
        if not prompt_path.exists():
            problems.append(f"{p_rel}：Prompt 檔不存在")
            continue
        raw_lines = prompt_path.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
        total = len(raw_lines)
        quotes = [q for q in info["quotes"] if len(q) >= MIN_QUOTE_LEN]
        if len(quotes) < MIN_QUOTES:
            problems.append(
                f"{p_rel}：需要 {MIN_QUOTES} 段逐字引句（每段至少 {MIN_QUOTE_LEN} 字），"
                f"目前 {len(quotes)} 段"
            )
            continue
        positions = []
        for quote in quotes:
            pos = _quote_position(raw_lines, quote)
            if pos is None:
                problems.append(f"{p_rel}：引句在 Prompt 原檔中逐字比對不到 →「{quote[:40]}」")
            else:
                positions.append(pos)
        if positions and max(positions) < total * TAIL_FRACTION:
            problems.append(
                f"{p_rel}：{len(positions)} 段引句全部落在前 {int(TAIL_FRACTION * 100)}%"
                f"（最後一段在第 {max(positions)} 行／共 {total} 行）——"
                "至少要有一段出自檔案後三分之一，證明 Prompt 原檔已讀到底"
            )
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description="驗證本章 Prompt 規格檔的讀取回執")
    parser.add_argument("book")
    parser.add_argument("chapter", type=int)
    args = parser.parse_args()

    problems = check(args.book, args.chapter)
    if problems:
        print(f"❌ Prompt 讀取回執未過（{len(problems)} 項）：")
        for item in problems:
            print(f"   - {item}")
        print("結論：FAIL")
        return 1
    print(f"✅ {args.book} 第{args.chapter}章：Prompt 原檔讀取回執通過（各 Prompt 均有後段逐字引句）")
    print("結論：PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
