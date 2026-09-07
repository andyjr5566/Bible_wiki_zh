#!/usr/bin/env python3
"""精確檢查章節主檔引用的既有條目是否已有該書卷／章資料。"""
import argparse
import json
import re
import sys
from pathlib import Path

import console
import remediation
from resolve_link_candidates import has_book_chapter_data
from book_paths import canonical_book_name

UTIL_DIR = Path(__file__).resolve().parent
ROOT = UTIL_DIR.parent
INDEX_FILE = UTIL_DIR / "output" / "link_index.json"


def parse_chapter_path(path):
    match = re.fullmatch(r"第(\d+)章", path.stem)
    if not match:
        raise ValueError(f"章節檔名格式錯誤：{path.name}")
    return canonical_book_name(path.parent.name), match.group(1)


def extract_links(filepath):
    text = filepath.read_text(encoding="utf-8")
    return list(dict.fromkeys(re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", text)))


def resolve_existing(targets, index):
    found = []
    for target in targets:
        record = index.get(target)
        if not record:
            continue
        if "alias_of" in record:
            title = record["alias_of"]
            record = index.get(title, {})
        else:
            title = record.get("title", target)
        if record.get("path"):
            found.append((title, record["path"]))
    return list(dict.fromkeys(found))


def iter_chapter_files(root, book=None):
    """庫內所有 `第N章.md`（可依書卷過濾），按書卷序＋章號排序。"""
    want = canonical_book_name(book) if book else None
    for book_dir in sorted(root.glob("[0-9][0-9] *")):
        if not book_dir.is_dir():
            continue
        try:
            canonical = canonical_book_name(book_dir.name)
        except Exception:
            continue
        if want and canonical != want:
            continue
        files = [p for p in book_dir.glob("第*章.md") if re.fullmatch(r"第\d+章", p.stem)]
        for path in sorted(files, key=lambda p: int(p.stem[1:-1])):
            yield path


def chapter_missing_links(filepath, index, root):
    """(book, chapter, existing, missing)：章節連到的既有條目中，尚無該章累積者。"""
    book, chapter = parse_chapter_path(filepath)
    existing = resolve_existing(extract_links(filepath), index)
    missing = [
        (name, path) for name, path in existing
        if not has_book_chapter_data(path, book, chapter, root)
    ]
    return book, chapter, existing, missing


def _run_corpus(index, book=None):
    rows = []
    total_missing = 0
    for filepath in iter_chapter_files(ROOT, book):
        try:
            bk, ch, existing, missing = chapter_missing_links(filepath, index, ROOT)
        except (ValueError, OSError) as exc:
            print(f"❌ {filepath.relative_to(ROOT)}：{exc}")
            continue
        if missing:
            total_missing += len(missing)
            rows.append((bk, ch, missing))
    scope = f"{canonical_book_name(book)} 全卷" if book else "全庫"
    if not rows:
        print(f"✅ {scope}：章節連到的既有條目都已補上對應章節的累積資料。")
        print("結論：PASS")
        return 0
    print(f"⚠️ {scope}：{len(rows)} 章共 {total_missing} 個既有條目被連結、卻尚無該章累積：")
    for bk, ch, missing in rows:
        print(f"  {bk}第{ch}章（{len(missing)}）：")
        for name, path in missing:
            print(f"    - [[{name}]] → {path}")
    print("結論：FAIL（逐章走流程步驟 4：link_updates.py prepare → 填 → apply --dry-run → apply）")
    return 1


def main():
    console.utf8_stdio()
    parser = argparse.ArgumentParser()
    parser.add_argument("chapter_file", nargs="?",
                        help="單章 markdown 路徑；與 --book／--all 三選一")
    parser.add_argument("--missing", action="store_true")
    parser.add_argument("--check")
    parser.add_argument("--book", help="掃整卷（標準書卷名）")
    parser.add_argument("--all", action="store_true", help="掃全庫")
    args = parser.parse_args()

    try:
        index = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"❌ {exc}")
        return 1

    if args.all or args.book:
        if args.chapter_file or args.check:
            print("❌ --all／--book 是全掃模式，不接受單章路徑或 --check")
            return 1
        return _run_corpus(index, book=args.book)

    if not args.chapter_file:
        print("❌ 需要單章 markdown 路徑，或用 --book／--all 全掃")
        return 1
    filepath = ROOT / args.chapter_file
    if not filepath.exists():
        print(f"❌ 檔案不存在：{filepath}")
        return 1
    try:
        book, chapter = parse_chapter_path(filepath)
    except (ValueError, OSError) as exc:
        print(f"❌ {exc}")
        return 1

    existing = resolve_existing(extract_links(filepath), index)
    if args.check:
        existing = [(name, path) for name, path in existing if name == args.check]
        if not existing:
            print(f"❌ 未找到條目：{args.check}")
            return 1

    missing = [
        (name, path) for name, path in existing
        if not has_book_chapter_data(path, book, chapter, ROOT)
    ]
    if args.missing:
        if missing:
            print(f"⚠️ 以下 {len(missing)} 個條目尚未補充{book}第{chapter}章資料：")
            for name, path in missing:
                print(f"  - [[{name}]] → {path}")
            remediation.print_fix_hints([(
                f"章節引用了既有條目，但它們還沒補上{book}第{chapter}章的累積資料（B 類累積，流程步驟 4）",
                [
                    f"python util/link_updates.py prepare {book} {chapter}",
                    "回經文與有效 raw text 填 link_updates.yaml 的 summary／relation，"
                    "先 apply --dry-run 再 apply（重跑 apply 必須 0 變更）。",
                ],
            )])
            return 1
        print(f"✅ 所有 {len(existing)} 個既有條目都有{book}第{chapter}章資料。")
        print("結論：PASS")
        return 0

    for name, path in existing:
        status = "✅" if (name, path) not in missing else "⚠️"
        print(f"{status} [[{name}]] → {path}")
    print(f"已補充：{len(existing) - len(missing)}/{len(existing)}")
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())
