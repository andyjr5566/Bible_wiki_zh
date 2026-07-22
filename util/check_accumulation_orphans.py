#!/usr/bin/env python3
"""反向孤兒累積檢查：條目宣告了 accumulation:<書卷>:<章>，但那一章卻沒有連回這個條目。

三道既有閘門只驗「章→條目」單一方向：
  - verify_links.py        章節散文裡的 [[link]] → 目標存在（破鏈）
  - check_existing_links.py 章節「已連出去」的條目 → 有補該章累積（缺累積）
兩者都看不到反方向的缺口——條目 md 裡有 `<!-- accumulation:書卷:章 -->` 區塊、
卻沒有任何章節連回它。這種孤兒累積讀者永遠走不到，但連結本身有效、內容也在，
三道閘門一個都不會抱怨（利未記曾一次累積 12 個，全部靜默）。

判準（機械可證，命中即 error）：
  對每個 `accumulation:<書卷>:<章>:start` 標記，
  若對應的「第<章>章.md」存在、但該章所有 [[link]]（經 link_index 解析別名後）
  都不指向這個條目 → 就是孤兒累積。

  python util/check_accumulation_orphans.py 利未記      # 只查一卷
  python util/check_accumulation_orphans.py --all       # 全庫
"""
import argparse
import json
import re
import sys
from pathlib import Path

import console
from book_paths import canonical_book_name, ordered_book_dir_name

UTIL_DIR = Path(__file__).resolve().parent
ROOT = UTIL_DIR.parent
INDEX_FILE = UTIL_DIR / "output" / "link_index.json"
LINK_FOLDER = ROOT / "link_folder"

ACC_RE = re.compile(r"accumulation:([^:]+):(\d+):start")
WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")


def load_index():
    return json.loads(INDEX_FILE.read_text(encoding="utf-8"))


def resolve_path(target, index):
    """把一個 wiki-link target 解析成它指向的條目 md 路徑（跟隨 alias）。"""
    record = index.get(target.strip())
    if not record:
        return None
    if "alias_of" in record:
        record = index.get(record["alias_of"], {})
    return record.get("path")


def chapter_file(book, chapter):
    """第<章>章.md 的路徑（優先用 NN 書卷 排序資料夾，退回裸書卷名）。"""
    for folder in (ordered_book_dir_name(book), book):
        path = ROOT / folder / f"第{chapter}章.md"
        if path.exists():
            return path
    return None


def chapter_linked_paths(path, index):
    text = path.read_text(encoding="utf-8")
    paths = set()
    for target in WIKILINK_RE.findall(text):
        resolved = resolve_path(target, index)
        if resolved:
            paths.add(resolved)
    return paths


def find_orphans(book_filter, index):
    """回傳 [(書卷, 章, 條目相對路徑)]，依 (書卷, 章) 排序。"""
    chapter_cache = {}
    orphans = []
    for md in sorted(LINK_FOLDER.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        entry_path = md.relative_to(ROOT).as_posix()
        for book_raw, chap_raw in ACC_RE.findall(text):
            book = canonical_book_name(book_raw)
            if book_filter and book != book_filter:
                continue
            chapter = int(chap_raw)
            key = (book, chapter)
            if key not in chapter_cache:
                cf = chapter_file(book, chapter)
                chapter_cache[key] = (
                    chapter_linked_paths(cf, index) if cf else None
                )
            linked = chapter_cache[key]
            if linked is None:
                continue  # 章節檔尚未產生（未來書卷），不算孤兒
            if entry_path not in linked:
                orphans.append((book, chapter, entry_path))
    orphans.sort(key=lambda o: (o[0], o[1], o[2]))
    return orphans


def main():
    console.utf8_stdio()
    parser = argparse.ArgumentParser(description="反向孤兒累積檢查")
    parser.add_argument("book", nargs="?", help="書卷名（如 利未記）；省略需搭配 --all")
    parser.add_argument("--all", action="store_true", help="掃描全庫所有書卷")
    args = parser.parse_args()

    if not args.all and not args.book:
        parser.error("需指定書卷名，或使用 --all")

    book_filter = None if args.all else canonical_book_name(args.book)
    index = load_index()
    orphans = find_orphans(book_filter, index)

    scope = "全庫" if args.all else book_filter
    if orphans:
        print(f"⚠️ {scope} 發現 {len(orphans)} 個孤兒累積"
              f"（條目宣告該章累積、但該章沒有連回）：")
        for book, chapter, path in orphans:
            print(f"  - {book}第{chapter}章 ✗ {path}")
        print("\n修法：①該章確有此概念（有出處）→ 在該章散文補 [[連結]]；"
              "②概念其實不屬該章／查無出處 → 移除該條目的該章 accumulation 區塊；"
              "③重複條目（該章連的是別名/正名）→ merge_entries.py 併回正名。")
        print("結論：FAIL")
        return 1

    print(f"✅ {scope} 沒有孤兒累積：每個宣告的 accumulation 區塊都有對應章節連回。")
    print("結論：PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
