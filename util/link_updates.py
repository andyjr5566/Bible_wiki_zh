#!/usr/bin/env python3
"""準備並安全套用 link_folder 的章節累積資料。"""
import argparse
import os
import re
import sys
import tempfile
from pathlib import Path

import yaml

try:
    from .book_paths import BOOK_NUMBERS, book_directory, canonical_book_name, chapter_link
    from . import console
except ImportError:
    from book_paths import BOOK_NUMBERS, book_directory, canonical_book_name, chapter_link
    import console

ROOT = Path(__file__).resolve().parent.parent
BOOK_ALIASES = {"約書亞記": "約書亞記"}


def book_rank(book):
    canonical = BOOK_ALIASES.get(book, book)
    return BOOK_NUMBERS.get(canonical, len(BOOK_NUMBERS) + 1)


def plan_updates(book, chapter):
    base = book_directory(ROOT, book) / ".tmp" / f"第{chapter}章"
    plan_yaml = base / "link_plan.yaml"
    plan_md = base / "link_plan.md"
    updates = []
    if plan_yaml.exists():  # orchestrator（run_chapter/resolver）的結構化輸出優先
        data = yaml.safe_load(plan_yaml.read_text(encoding="utf-8")) or {}
        for item in data.get("B_needs_update", []):
            updates.append({
                "title": item.get("existing_title") or item.get("name", ""),
                "path": item.get("existing_path", ""),
                "summary": "",
                "relation": "",
            })
    elif plan_md.exists():
        section = None
        for line in plan_md.read_text(encoding="utf-8").splitlines():
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
                })
    else:
        raise FileNotFoundError(plan_yaml)
    return {
        "book": book,
        "chapter": int(chapter),
        "updates": updates,
    }


def prepare(book, chapter):
    console.utf8_stdio()
    output = book_directory(ROOT, book) / ".tmp" / f"第{chapter}章" / "link_updates.yaml"
    if output.exists():
        raise FileExistsError(f"{output} 已存在；避免覆蓋人工內容")
    data = plan_updates(book, chapter)
    output.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_style='"'), encoding="utf-8"
    )
    print(f"✅ 已建立更新骨架：{output}（{len(data['updates'])} 條）")
    return output


def render_block(book, chapter, update):
    return (
        f"<!-- accumulation:{book}:{chapter}:start -->\n"
        f"#### {chapter_link(book, chapter)}\n"
        f"- 本章重點：{update['summary'].strip()}\n"
        f"- 與本章關聯：{update['relation'].strip()}\n"
        f"<!-- accumulation:{book}:{chapter}:end -->"
    )


def validate_update(update):
    required_text = ("title", "path", "summary", "relation")
    return [key for key in required_text if not str(update.get(key, "")).strip()]


def _entry_path(root, raw_path):
    """Resolve an update target, allowing only Markdown entries in link_folder."""
    if not isinstance(raw_path, str) or not raw_path.strip():
        raise ValueError("更新項目的 path 必須是非空字串")
    relative = Path(raw_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"不合法的條目路徑：{raw_path}")
    root = Path(root).resolve()
    link_root = (root / "link_folder").resolve()
    path = (root / relative).resolve()
    if path.suffix.lower() != ".md" or not path.is_relative_to(link_root):
        raise ValueError(f"更新目標必須是 link_folder/ 內的 .md 條目：{raw_path}")
    if not path.is_file():
        raise ValueError(f"找不到條目檔案：{raw_path}")
    return path


def _updated_text(text, book, chapter, update, path):
    """Return one entry's rendered accumulation update without writing it."""
    start = f"<!-- accumulation:{book}:{chapter}:start -->"
    end = f"<!-- accumulation:{book}:{chapter}:end -->"
    block = render_block(book, chapter, update)
    if start in text:
        pattern = re.compile(re.escape(start) + r"[\s\S]*?" + re.escape(end))
        new_text, count = pattern.subn(block, text, count=1)
        if count != 1:
            raise ValueError(f"{path}: 累積標記損壞")
        return new_text

    accumulation = re.search(
        r"^## 按書卷累積\s*$([\s\S]*?)(?=^## (?:主題發展|相關條目|來源依據)\s*$)",
        text, re.M,
    )
    if not accumulation:
        accumulation = re.search(r"^## 按書卷累積\s*$([\s\S]*)", text, re.M)
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
        return text[:insertion].rstrip() + "\n\n" + block + "\n" + text[insertion:].lstrip("\n")

    insertion = accumulation.end(1)
    for heading in re.finditer(r"^###\s+(.+?)\s*$", section, re.M):
        heading_name = canonical_book_name(heading.group(1))
        if BOOK_ALIASES.get(heading_name, heading_name) not in BOOK_NUMBERS:
            continue
        if book_rank(heading_name) > book_rank(book):
            insertion = accumulation.start(1) + heading.start()
            break
    group = f"### {book}\n\n{block}"
    return (
        text[:insertion].rstrip()
        + "\n\n"
        + group
        + "\n\n"
        + text[insertion:].lstrip()
    )


def preview_updates(manifest):
    """Validate every update and return all proposed file changes without writing."""
    manifest = Path(manifest)
    data = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("manifest 頂層必須是物件")
    book, chapter = data.get("book"), data.get("chapter")
    if not book or not isinstance(chapter, int) or chapter < 1:
        raise ValueError("manifest 缺少合法 book/chapter")
    book = canonical_book_name(book)
    if book not in BOOK_NUMBERS:
        raise ValueError(
            f"manifest 的 book「{data.get('book')}」不是合法書卷名；"
            f"應為 _config/bible_books.json 裡的書卷名（如「利未記」），不是資料夾名"
        )
    updates = data.get("updates", [])
    if not isinstance(updates, list):
        raise ValueError("manifest 的 updates 必須是清單")

    root = ROOT.resolve()
    operations = []
    for update in updates:
        if not isinstance(update, dict):
            raise ValueError("updates 的每一項必須是物件")
        missing = validate_update(update)
        if missing:
            raise ValueError(f"{update.get('title', '?')} 缺少欄位：{', '.join(missing)}")
        path = _entry_path(root, update["path"])
        text = path.read_text(encoding="utf-8")
        new_text = _updated_text(text, book, chapter, update, path)
        operations.append({
            "path": path,
            "relative_path": path.relative_to(root).as_posix(),
            "title": str(update["title"]),
            "before": text,
            "after": new_text,
        })
    return {"book": book, "chapter": chapter, "operations": operations}


def _stage_text(path, text):
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)
    return Path(name)


def _commit_operations(changes):
    """Stage all files before replacing any; attempt rollback on an OS failure."""
    staged = []
    replaced = []
    try:
        for operation in changes:
            staged.append((operation, _stage_text(operation["path"], operation["after"])))
        for operation, staged_path in staged:
            os.replace(staged_path, operation["path"])
            replaced.append(operation)
    except OSError as exc:
        rollback_errors = []
        for operation in reversed(replaced):
            try:
                rollback = _stage_text(operation["path"], operation["before"])
                os.replace(rollback, operation["path"])
            except OSError as rollback_exc:
                rollback_errors.append(str(rollback_exc))
        detail = "；".join(rollback_errors)
        raise OSError(
            "累積更新寫入失敗；已嘗試還原先前已替換的檔案"
            + (f"（還原另有錯誤：{detail}）" if detail else "")
        ) from exc
    finally:
        for _, staged_path in staged:
            try:
                staged_path.unlink(missing_ok=True)
            except OSError:
                pass


def apply_updates(manifest, dry_run=False, reporter=print):
    """Apply fully prevalidated updates with staged per-file replacements.

    ``reporter`` keeps CLI feedback out of MCP's stdout JSON-RPC transport.
    Pass ``None`` to suppress line-by-line output.
    """
    # CLI callers retain the repository's UTF-8 console guard.  MCP passes a
    # custom collector, so its JSON-RPC stdout is never reconfigured or used.
    if reporter is print:
        console.utf8_stdio()
    preview = preview_updates(manifest)
    changes = [item for item in preview["operations"] if item["after"] != item["before"]]
    if not dry_run and changes:
        _commit_operations(changes)
    if reporter:
        action = "預覽" if dry_run else "更新"
        for operation in changes:
            reporter(f"{action}：{operation['relative_path']}")
        reporter(f"✅ {'預覽' if dry_run else '套用'}完成：{len(changes)} 個檔案")
    return len(changes)


def main():
    console.utf8_stdio()
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    prepare_parser = sub.add_parser("prepare")
    prepare_parser.add_argument("book")
    prepare_parser.add_argument("chapter")
    apply_parser = sub.add_parser("apply")
    apply_parser.add_argument(
        "target", nargs="+",
        help="「書名 章」（與 prepare 同形式），或 link_updates.yaml 路徑",
    )
    apply_parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            prepare(args.book, args.chapter)
        else:
            # 與 prepare 同形式的「書名 章」是主要用法；manifest 路徑保留相容
            if len(args.target) == 2 and args.target[1].isdigit():
                book = canonical_book_name(args.target[0])
                manifest = (
                    book_directory(ROOT, book) / ".tmp"
                    / f"第{int(args.target[1])}章" / "link_updates.yaml"
                )
            elif len(args.target) == 1:
                manifest = Path(args.target[0])
                if not manifest.is_absolute():
                    manifest = ROOT / manifest
            else:
                print("❌ apply 用法：apply 書名 章 [--dry-run]，或 apply <manifest路徑>")
                return 2
            apply_updates(manifest, args.dry_run)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"❌ {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
