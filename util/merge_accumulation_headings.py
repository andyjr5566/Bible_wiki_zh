#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把資料夾名的累積小節（「### 03 利未記」）併回書卷名小節（「### 利未記」）。

## 這個損害是怎麼來的

`link_updates.py apply` 舊版沒有正規化 manifest 的 `book` 欄位，於是資料夾名
（`03 利未記`）被原封不動寫進累積標記與 H3 標題。條目裡因此長出 `### 03 利未記`，
與既有的 `### 利未記` **並存且互不相認**：`check_existing_links` 找不到累積、
`validate_knowledge_base` 抱怨排序、下次重跑又寫一份。

`link_updates.py` 已於 2026-07 改為呼叫 `book_paths.canonical_book_name()`，
不會再產生新的損害。本腳本是用來收拾既有的。

## 用法

    python util/merge_accumulation_headings.py 民數記            # 預演
    python util/merge_accumulation_headings.py 民數記 --apply    # 實際寫入

一次只處理一個書卷。跑完必須 `python util/validate_knowledge_base.py` 為 0 errors。

## 進度

- 利未記 56 處：已於 2a5cda6b 併回
- 民數記 121 處、申命記 11 處：**尚未處理**

## 為什麼驗證有四道

這腳本前三版都有 bug，每次都是「少驗一項」而炸出一批 validate errors：

- 只驗自己書卷的區塊 → 沒發現利未記被整段插到出埃及記前面（18 errors）
- 只驗標題順序 → 利未記被插在「### 出埃及記」與它的區塊「之間」，
  標題順序完全正確，出埃及記的區塊卻全掛在利未記名下（67 errors）

四道驗證缺一不可，任一不過就跳過該檔而不是硬寫。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    from .book_paths import BOOK_NUMBERS, canonical_book_name
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from book_paths import BOOK_NUMBERS, canonical_book_name

ROOT = Path(__file__).resolve().parent.parent

ANY_BLOCK = re.compile(
    r"<!-- accumulation:([^:]+):(\d+):start -->([\s\S]*?)<!-- accumulation:\1:\2:end -->"
)


def _block_re(book: str) -> re.Pattern:
    return re.compile(
        r"<!-- accumulation:" + re.escape(book) + r":(\d+):start -->"
        r"([\s\S]*?)"
        r"<!-- accumulation:" + re.escape(book) + r":\1:end -->"
    )


def blocks_of(text: str, book: str) -> dict[int, str]:
    """回傳 {章: 內文}；內文不含 start/end 標記。"""
    return {int(m.group(1)): m.group(2) for m in _block_re(book).finditer(text)}


def all_blocks(text: str) -> dict[tuple[str, str], str]:
    return {(m.group(1), m.group(2)): m.group(3).strip() for m in ANY_BLOCK.finditer(text)}


def merge_file(text: str, target: str, bad: str, num: int) -> tuple[str | None, str | None]:
    """回傳 (新內容, 錯誤訊息)。新內容為 None 表示跳過。"""
    before_good = blocks_of(text, target)
    before_bad = blocks_of(text, bad)

    overlap = set(before_good) & set(before_bad)
    if overlap:
        return None, f"第 {sorted(overlap)} 章正確與錯誤標記都有，需人工判斷"

    new = text
    for ch, body in before_bad.items():
        new = new.replace(
            f"<!-- accumulation:{bad}:{ch}:start -->{body}"
            f"<!-- accumulation:{bad}:{ch}:end -->", "", 1)
    new = re.sub(rf"^###\s+{re.escape(bad)}\s*$\n*", "", new, flags=re.M)

    merged = {**before_good, **before_bad}
    rebuilt = "\n\n".join(
        f"<!-- accumulation:{target}:{ch}:start -->{merged[ch]}"
        f"<!-- accumulation:{target}:{ch}:end -->"
        for ch in sorted(merged)
    )

    if f"### {target}" in new:
        for ch, body in before_good.items():
            new = new.replace(
                f"<!-- accumulation:{target}:{ch}:start -->{body}"
                f"<!-- accumulation:{target}:{ch}:end -->", "", 1)
        new = re.sub(
            rf"(^###\s+{re.escape(target)}\s*$)\n*",
            lambda m: m.group(1) + "\n\n" + rebuilt + "\n\n",
            new, count=1, flags=re.M,
        )
    else:
        anchor = re.search(r"^## 按書卷累積\s*$", new, re.M)
        if not anchor:
            return None, "找不到「## 按書卷累積」"
        nxt_h2 = re.search(r"^## ", new[anchor.end():], re.M)
        sec_end = anchor.end() + (nxt_h2.start() if nxt_h2 else len(new) - anchor.end())

        # 插入點＝第一個「書卷次序比自己大」的小標題的 start()。
        # 不可用 end()——那會插進前一個書卷的標題與它的區塊之間。
        # 比對前要 canonical_book_name()，否則認不得別的書卷也是資料夾名標題。
        ins = sec_end
        for h in re.finditer(r"^###\s+(.+?)\s*$", new[anchor.end():sec_end], re.M):
            name = canonical_book_name(h.group(1))
            if name not in BOOK_NUMBERS:
                continue
            if BOOK_NUMBERS[name] > num:
                ins = anchor.end() + h.start()
                break
        head, tail = new[:ins].rstrip(), new[ins:].lstrip("\n")
        new = head + f"\n\n### {target}\n\n" + rebuilt + ("\n\n" + tail if tail.strip() else "\n")

    new = re.sub(r"\n{4,}", "\n\n\n", new).rstrip() + "\n"

    # 驗證 1：本書卷區塊集合與內文完全相同
    after = blocks_of(new, target)
    expect = {**before_good, **before_bad}
    if set(after) != set(expect):
        return None, f"章次集合不符 {sorted(expect)} → {sorted(after)}"
    if any(after[c].strip() != expect[c].strip() for c in expect):
        return None, "內文被改動"
    if blocks_of(new, bad):
        return None, "仍有壞標記"

    # 驗證 2：其他書卷的區塊一個都不能少或變動
    old_others = {k: v for k, v in all_blocks(text).items() if k[0] not in (target, bad)}
    new_others = {k: v for k, v in all_blocks(new).items() if k[0] not in (target, bad)}
    if old_others != new_others:
        return None, "其他書卷的累積被動到"

    # 驗證 3：書卷小標題必須遞增
    order = [BOOK_NUMBERS[h] for h in re.findall(r"^###\s+(.+?)\s*$", new, re.M)
             if h in BOOK_NUMBERS]
    if order != sorted(order):
        return None, f"書卷順序不對 {order}"

    # 驗證 4：每個區塊都要落在自己書卷的標題底下
    cur, misplaced = None, []
    for line in new.splitlines():
        h = re.match(r"^###\s+(.+?)\s*$", line)
        if h:
            cur = h.group(1) if h.group(1) in BOOK_NUMBERS else None
            continue
        m = re.match(r"^<!-- accumulation:([^:]+):(\d+):start -->", line)
        # 別的書卷的資料夾名標題是既有損害，本次不處理，略過以免被擋住
        if m and m.group(1) in BOOK_NUMBERS and m.group(1) != cur:
            misplaced.append(f"{m.group(1)}:{m.group(2)} 在「{cur}」之下")
    if misplaced:
        return None, f"區塊掛錯書卷 → {misplaced[:3]}"

    return new, None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("book", help="書卷名，如「民數記」（不是資料夾名）")
    parser.add_argument("--apply", action="store_true", help="實際寫入；預設只預演")
    args = parser.parse_args()

    try:
        from . import console
    except ImportError:
        import console
    console.utf8_stdio()

    target = canonical_book_name(args.book)
    if target not in BOOK_NUMBERS:
        print(f"❌ 未知書卷：{args.book}")
        return 1
    num = BOOK_NUMBERS[target]
    bad = f"{num:02d} {target}"

    scanned = changed = skipped = 0
    for path in sorted((ROOT / "link_folder").rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        if f"### {bad}" not in text and f"accumulation:{bad}:" not in text:
            continue
        scanned += 1
        new, err = merge_file(text, target, bad, num)
        if err:
            skipped += 1
            print(f"  ⚠️ 跳過 {path.name}：{err}")
            continue
        if new != text:
            changed += 1
            if args.apply:
                path.write_text(new, encoding="utf-8")

    verb = "已修" if args.apply else "可修"
    print(f"\n{target}：掃到 {scanned} 個條目，{verb} {changed} 個，跳過 {skipped} 個")
    if args.apply and changed:
        print("→ 請跑 python util/validate_knowledge_base.py 確認 0 errors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
