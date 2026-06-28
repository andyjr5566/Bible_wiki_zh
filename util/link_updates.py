#!/usr/bin/env python3
"""準備並安全套用 link_folder 的章節累積資料。"""
import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def plan_updates(book, chapter):
    plan = ROOT / book / ".tmp" / f"第{chapter}章" / "link_plan.md"
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
    output = ROOT / book / ".tmp" / f"第{chapter}章" / "link_updates.yaml"
    if output.exists():
        raise FileExistsError(f"{output} 已存在；避免覆蓋人工內容")
    data = plan_updates(book, chapter)
    output.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    print(f"✅ 已建立更新骨架：{output}（{len(data['updates'])} 條）")
    return output


def render_block(book, chapter, update):
    sources = "、".join(update["sources"])
    source_files = "、".join(update["source_files"])
    return (
        f"<!-- accumulation:{book}:{chapter}:start -->\n"
        f"### {book}\n\n"
        f"#### 第{chapter}章\n"
        f"- 本章重點：{update['summary'].strip()}\n"
        f"- 與本章關聯：{update['relation'].strip()}\n"
        f"- 觸發來源：{sources}\n"
        f"- 來源檔案：{source_files}\n"
        f"<!-- accumulation:{book}:{chapter}:end -->"
    )


def validate_update(update):
    required_text = ("title", "path", "summary", "relation")
    missing = [key for key in required_text if not str(update.get(key, "")).strip()]
    for key in ("sources", "source_files"):
        if not isinstance(update.get(key), list) or not update[key]:
            missing.append(key)
    return missing


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
        path = ROOT / update["path"]
        if not path.exists() or ROOT not in path.resolve().parents:
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
            insertion = text.find("\n## 來源依據")
            if insertion < 0:
                insertion = len(text.rstrip())
            new_text = text[:insertion].rstrip() + "\n\n" + block + "\n" + text[insertion:]
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
