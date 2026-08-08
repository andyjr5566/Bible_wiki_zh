#!/usr/bin/env python3
"""development 落後累積成長檢查：條目累積了很多章／跨了很多卷，「主題發展」欄
卻還停在條目首建當時的範圍，沒人回頭補。

条目的 development／related_entries／sources 只在 M3 首次產生 payload 時寫定；
之後每一章只靠 link_updates.py 補「按書卷累積」的逐章區塊，不會回頭碰這三欄。
累積量小的時候看不出差別，但像「摩西」這種橫跨創世記／出埃及記／利未記／民數記
四十九個累積區塊的條目，development 卻仍只寫出埃及記第2章一段——不是杜撰，是
沒人維護（見 memory: development-lags-accumulation-growth）。

這不是機械可證的錯誤，是需要人工讀過 development 內容才能判斷「有沒有跟上」的
啟發式——所以本工具只列候選名單（累積區塊數、涉及卷數、development 字數），
不自動判定通過或失敗，也不擋 build。逐條打開來讀，用同一套判準：development
是不是真的講了累積表裡「首建章節之外」的內容，還是只重述累積表已有的某一筆。

    python util/check_development_staleness.py 出埃及記   # 只查一卷
    python util/check_development_staleness.py --all       # 全庫
    python util/check_development_staleness.py --all --min-blocks 10
"""
import argparse
import re
import sys
from pathlib import Path

import console
from book_paths import canonical_book_name

UTIL_DIR = Path(__file__).resolve().parent
ROOT = UTIL_DIR.parent
LINK_FOLDER = ROOT / "link_folder"

ACCUM_RE = re.compile(r"<!-- accumulation:([^:]+):(\d+):start -->")
DEFAULT_MIN_BLOCKS = 7


def _sections(text):
    """把 md 內文依 `## 標題` 切成 {標題: 內文} — 不用貪婪 \\s* 邊界（曾在此踩雷：
    development 為空時，貪婪 \\s* 會吃掉分隔用的換行，把下一節整段吞進來）。"""
    parts = re.split(r"(?m)^## (.+)$", text)
    out = {}
    for i in range(1, len(parts), 2):
        out[parts[i].strip()] = (parts[i + 1] if i + 1 < len(parts) else "").strip()
    return out


def scan(book_filter, min_blocks):
    rows = []
    for md in sorted(LINK_FOLDER.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        blocks = ACCUM_RE.findall(text)
        if len(blocks) < min_blocks:
            continue
        books = sorted({canonical_book_name(b) for b, _c in blocks})
        if book_filter and book_filter not in books:
            continue
        dev = _sections(text).get("主題發展", "")
        rows.append({
            "path": md.relative_to(ROOT).as_posix(),
            "blocks": len(blocks),
            "books": books,
            "dev_len": len(dev),
        })
    rows.sort(key=lambda r: (-r["blocks"], r["path"]))
    return rows


def main():
    console.utf8_stdio()
    parser = argparse.ArgumentParser(description="development 落後累積成長檢查（人工複核用候選清單）")
    parser.add_argument("book", nargs="?", help="書卷名（如 出埃及記）；省略需搭配 --all")
    parser.add_argument("--all", action="store_true", help="掃描全庫所有書卷")
    parser.add_argument("--min-blocks", type=int, default=DEFAULT_MIN_BLOCKS,
                         help=f"累積區塊數門檻（預設 {DEFAULT_MIN_BLOCKS}）")
    args = parser.parse_args()

    if not args.all and not args.book:
        parser.error("需指定書卷名，或使用 --all")

    book_filter = None if args.all else canonical_book_name(args.book)
    rows = scan(book_filter, args.min_blocks)

    scope = "全庫" if args.all else book_filter
    if not rows:
        print(f"✅ {scope} 沒有累積區塊數 ≥ {args.min_blocks} 的條目——無候選需複核。")
        return 0

    print(f"ℹ️ {scope} 有 {len(rows)} 個條目累積區塊數 ≥ {args.min_blocks}，"
          "列出供人工逐條複核 development 是否已跟上累積範圍"
          "（本工具不判定對錯，只列候選；單書卷條目、development 留空但確實無跨卷內容"
          "可寫都是合法狀態，不必逐條都改）：\n")
    for row in rows:
        flag = "空白" if row["dev_len"] == 0 else f"{row['dev_len']}字"
        print(f"  - {row['blocks']:>3} 筆／{len(row['books'])} 卷（{'/'.join(row['books'])}）"
              f"　development {flag}　{row['path']}")
    print("\n複核方式：打開條目，讀 development 有沒有講到「首建那一卷/那一章之外」的"
          "累積內容——只重述某一筆累積、或完全沒提到後來累積的卷，才需要重寫；"
          "development 選填，沒有真正跨卷的內容留空優於硬湊。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
