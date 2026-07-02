#!/usr/bin/env python3
"""準備並安全套用 link_folder 的章節累積資料。"""
import argparse
import re
import sys
from pathlib import Path

import yaml

try:
    from .book_paths import book_directory
except ImportError:
    from book_paths import book_directory

ROOT = Path(__file__).resolve().parent.parent


def plan_updates(book, chapter):
    plan = book_directory(ROOT, book) / ".tmp" / f"第{chapter}章" / "link_plan.md"
    if not plan.exists():
        raise FileNotFoundError(plan)
    section = None
    updates = []
    for line in plan.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            section = line[3:]
            continue
        if not section or not section.startswith("B."):
            continue
        match = re.match(r"- \[\[(.+?)\]\] → ([^（]+)", line)
        if match:
            updates.append({
                "title": match.group(1),
                "path": match.group(2).strip(),
                "summary": "",
                "relation": "",
                "sources": [],
                "source_files": [],
            })
    return {
        "book": book,
        "chapter": int(chapter),
        "updates": updates,
    }


def prepare(book, chapter):
    output = book_directory(ROOT, book) / ".tmp" / f"第{chapter}章" / "link_updates.yaml"
    if output.exists():
        raise FileExistsError(f"{output} 已存在；避免覆蓋人工內容")
    data = plan_updates(book, chapter)
    output.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    print(f"✅ 已建立更新骨架：{output}（{len(data['updates'])} 條）")
    return output


def render_block(book, chapter, update):
    return (
        f"<!-- accumulation:{book}:{chapter}:start -->\n"
        f"#### 第{chapter}章\n"
        f"- 本章重點：{update['summary'].strip()}\n"
        f"- 與本章關聯：{update['relation'].strip()}\n"
        f"<!-- accumulation:{book}:{chapter}:end -->"
    )


def validate_update(update):
    required_text = ("title", "path", "summary", "relation")
    return [key for key in required_text if not str(update.get(key, "")).strip()]


def apply_updates(manifest, dry_run=False):
    data = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
    book, chapter = data.get("book"), data.get("chapter")
    if not book or not isinstance(chapter, int):
        raise ValueError("manifest 缺少合法 book/chapter")
    changed = 0
    for update in data.get("updates", []):
        missing = validate_update(update)
        if missing:
            raise ValueError(f"{update.get('title', '?')} 缺少欄位：{', '.join(missing)}")
        root = ROOT.resolve()
        path = (ROOT / update["path"]).resolve()
        if not path.exists() or (path != root and root not in path.parents):
            raise ValueError(f"不合法的條目路徑：{path}")
        text = path.read_text(encoding="utf-8")
        start = f"<!-- accumulation:{book}:{chapter}:start -->"
        end = f"<!-- accumulation:{book}:{chapter}:end -->"
        block = render_block(book, chapter, update)
        if start in text:
            pattern = re.compile(re.escape(start) + r"[\s\S]*?" + re.escape(end))
            new_text, count = pattern.subn(block, text, count=1)
            if count != 1:
                raise ValueError(f"{path}: 累積標記損壞")
        else:
            accumulation = re.search(
                r"^## 按書卷累積\s*$([\s\S]*?)(?=^## 主題發展\s*$)", text, re.M
            )
            if not accumulation:
                raise ValueError(f"{path}: 找不到合法的按書卷累積區")
            section = accumulation.group(1)
            book_heading = re.search(rf"^###\s+{re.escape(book)}\s*$", section, re.M)
            if book_heading:
                following = section[book_heading.end():]
                next_book = re.search(r"^###\s+", following, re.M)
                book_end = (
                    accumulation.start(1) + book_heading.end()
                    + (next_book.start() if next_book else len(following))
                )
                insertion = book_end
                for marker in re.finditer(
                    rf"^<!-- accumulation:{re.escape(book)}:(\d+):start -->",
                    section[book_heading.end():(book_heading.end() + (next_book.start() if next_book else len(following)))],
                    re.M,
                ):
                    if int(marker.group(1)) > chapter:
                        insertion = accumulation.start(1) + book_heading.end() + marker.start()
                        break
                new_text = text[:insertion].rstrip() + "\n\n" + block + "\n" + text[insertion:].lstrip("\n")
            else:
                insertion = accumulation.end(1)
                group = f"### {book}\n\n{block}"
                new_text = text[:insertion].rstrip() + "\n\n" + group + "\n\n" + text[insertion:].lstrip()
        if new_text != text:
            changed += 1
            if not dry_run:
                path.write_text(new_text, encoding="utf-8")
            print(f"{'預覽' if dry_run else '更新'}：{update['path']}")
    print(f"✅ {'預覽' if dry_run else '套用'}完成：{changed} 個檔案")
    return changed


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    prepare_parser = sub.add_parser("prepare")
    prepare_parser.add_argument("book")
    prepare_parser.add_argument("chapter")
    apply_parser = sub.add_parser("apply")
    apply_parser.add_argument("manifest", type=Path)
    apply_parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            prepare(args.book, args.chapter)
        else:
            apply_updates(
                args.manifest if args.manifest.is_absolute() else ROOT / args.manifest,
                args.dry_run,
            )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"❌ {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
