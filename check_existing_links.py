#!/usr/bin/env python3
"""精確檢查章節主檔引用的既有條目是否已有該書卷／章資料。"""
import argparse
import json
import re
import sys
from pathlib import Path

from resolve_link_candidates import has_book_chapter_data

ROOT = Path(__file__).resolve().parent
INDEX_FILE = ROOT / "link_folder" / "_index" / "link_index.json"


def parse_chapter_path(path):
    match = re.fullmatch(r"第(\d+)章", path.stem)
    if not match:
        raise ValueError(f"章節檔名格式錯誤：{path.name}")
    return path.parent.name, match.group(1)


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("chapter_file")
    parser.add_argument("--missing", action="store_true")
    parser.add_argument("--check")
    args = parser.parse_args()

    filepath = ROOT / args.chapter_file
    if not filepath.exists():
        print(f"❌ 檔案不存在：{filepath}")
        return 1
    try:
        book, chapter = parse_chapter_path(filepath)
        index = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
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
            return 1
        print(f"✅ 所有 {len(existing)} 個既有條目都有{book}第{chapter}章資料。")
        return 0

    for name, path in existing:
        status = "✅" if (name, path) not in missing else "⚠️"
        print(f"{status} [[{name}]] → {path}")
    print(f"已補充：{len(existing) - len(missing)}/{len(existing)}")
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())
