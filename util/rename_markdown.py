#!/usr/bin/env python3
"""安全改名 Markdown 檔案，並同步更新整個 vault 內指向它的 WikiLink。"""

import argparse
import codecs
import re
import sys
import time
import unicodedata
from dataclasses import dataclass
from pathlib import Path


UTIL_DIR = Path(__file__).resolve().parent
ROOT = UTIL_DIR.parent
WIKILINK_RE = re.compile(r"\[\[(?P<body>[^\]\r\n]+)\]\]")
CODE_RE = re.compile(r"(```[\s\S]*?```|~~~[\s\S]*?~~~|`[^`\r\n]*`)")


def configure_console():
    """讓 Windows 非 UTF-8 locale 也能正常顯示中文訊息。"""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


class RenameError(RuntimeError):
    """改名前預檢或執行失敗。"""


@dataclass
class RenameResult:
    source: Path
    destination: Path
    changed_files: int
    changed_links: int
    dry_run: bool = False


def normalize_name(value):
    """依 Windows／Obsidian 實務做 Unicode 與大小寫正規化。"""
    return unicodedata.normalize("NFKC", str(value)).casefold()


def normalize_wiki_path(value):
    value = str(value).replace("\\", "/").strip()
    while value.startswith("./"):
        value = value[2:]
    return normalize_name(value.strip("/"))


def resolve_in_root(raw_path, root):
    root = Path(root).resolve()
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = root / path
    path = path.resolve(strict=False)
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise RenameError(f"路徑不可超出專案根目錄：{raw_path}") from exc
    return path


def collect_markdown_files(root):
    return sorted(
        path.resolve()
        for path in Path(root).rglob("*")
        if path.is_file() and path.suffix.casefold() == ".md"
    )


def decode_markdown(path):
    for attempt in range(3):
        try:
            data = path.read_bytes()
            break
        except FileNotFoundError:
            if attempt == 2:
                raise
            time.sleep(0.1)
    has_bom = data.startswith(codecs.BOM_UTF8)
    payload = data[len(codecs.BOM_UTF8):] if has_bom else data
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RenameError(f"Markdown 不是有效 UTF-8，未進行改名：{path}") from exc
    return data, text, has_bom


def encode_markdown(text, has_bom):
    data = text.encode("utf-8")
    return codecs.BOM_UTF8 + data if has_bom else data


class WikiLinkResolver:
    def __init__(self, root, markdown_files):
        self.root = Path(root).resolve()
        self.markdown_files = list(markdown_files)
        self.by_name = {}
        self.by_stem = {}
        self.relative_names = {}

        for path in self.markdown_files:
            relative = path.relative_to(self.root).as_posix()
            self.by_name.setdefault(normalize_name(path.name), []).append(path)
            self.by_stem.setdefault(normalize_name(path.stem), []).append(path)
            self.relative_names[path] = normalize_wiki_path(relative)

    def candidates(self, wiki_target):
        normalized = normalize_wiki_path(wiki_target)
        if not normalized:
            return []

        has_extension = normalized.endswith(".md")
        if "/" not in normalized:
            mapping = self.by_name if has_extension else self.by_stem
            return mapping.get(normalized, [])

        wanted = normalized if has_extension else normalized + ".md"
        return [
            path for path, relative in self.relative_names.items()
            if relative == wanted or relative.endswith("/" + wanted)
        ]


def split_target_fragment(target):
    indexes = [index for marker in ("#", "^") if (index := target.find(marker)) >= 0]
    if not indexes:
        return target, ""
    index = min(indexes)
    return target[:index], target[index:]


def replacement_target(raw_target, source, destination, resolver, containing_file):
    leading = raw_target[:len(raw_target) - len(raw_target.lstrip())]
    trailing = raw_target[len(raw_target.rstrip()):]
    stripped = raw_target.strip()
    target, fragment = split_target_fragment(stripped)
    if not target:
        return None

    candidates = resolver.candidates(target)
    if source not in candidates:
        return None
    if len(candidates) != 1:
        display = containing_file.relative_to(resolver.root)
        raise RenameError(
            f"無法判定 {display} 中 [[{raw_target}]] 指向哪個檔案；"
            f"目前有 {len(candidates)} 個同名候選。請先改成含路徑的 WikiLink。"
        )

    target_uses_path = "/" in target.replace("\\", "/")
    target_has_extension = normalize_name(target).endswith(".md")
    if target_uses_path:
        new_target = destination.relative_to(resolver.root).as_posix()
        if not target_has_extension:
            new_target = new_target[:-3]
    else:
        new_target = destination.name if target_has_extension else destination.stem

    return leading + new_target + fragment + trailing


def update_wikilinks(text, source, destination, resolver, containing_file):
    count = 0

    def replace(match):
        nonlocal count
        body = match.group("body")
        target, separator, alias = body.partition("|")
        updated = replacement_target(
            target, source, destination, resolver, containing_file
        )
        if updated is None:
            return match.group(0)
        count += 1
        new_body = updated + (separator + alias if separator else "")
        return f"[[{new_body}]]"

    parts = CODE_RE.split(text)
    for index in range(0, len(parts), 2):
        parts[index] = WIKILINK_RE.sub(replace, parts[index])
    return "".join(parts), count


def update_source_h1(text, source, destination):
    """來源檔 H1 與舊檔名一致時，同步改成新檔名。"""
    pattern = re.compile(rf"^#\s+{re.escape(source.stem)}\s*$", re.M)
    return pattern.sub(f"# {destination.stem}", text, count=1)


def validate_paths(source, destination, root, markdown_files):
    if source.suffix.casefold() != ".md" or destination.suffix.casefold() != ".md":
        raise RenameError("來源與目標都必須是 .md 檔案。")
    if not source.is_file():
        raise RenameError(f"來源 Markdown 不存在：{source}")
    if source == destination:
        raise RenameError("來源與目標路徑相同，無須改名。")
    if not destination.parent.is_dir():
        raise RenameError(f"目標資料夾不存在：{destination.parent}")
    if destination.exists():
        raise RenameError(f"目標路徑已存在：{destination}")

    if normalize_name(source.name) != normalize_name(destination.name):
        wanted = normalize_name(destination.name)
        conflicts = [
            path for path in markdown_files
            if path != source and normalize_name(path.name) == wanted
        ]
        if conflicts:
            paths = "、".join(str(path.relative_to(root)) for path in conflicts)
            raise RenameError(f"目標檔名「{destination.name}」已存在：{paths}")


def rename_markdown(source_path, destination_path, root=ROOT, dry_run=False):
    root = Path(root).resolve()
    source = resolve_in_root(source_path, root)
    destination = resolve_in_root(destination_path, root)
    markdown_files = collect_markdown_files(root)
    validate_paths(source, destination, root, markdown_files)

    resolver = WikiLinkResolver(root, markdown_files)
    updates = {}
    changed_links = 0
    for path in markdown_files:
        original, text, has_bom = decode_markdown(path)
        updated_text, count = update_wikilinks(
            text, source, destination, resolver, path
        )
        if path == source:
            updated_text = update_source_h1(
                updated_text, source, destination
            )
        if count or updated_text != text:
            updates[path] = (
                original,
                encode_markdown(updated_text, has_bom),
            )
            changed_links += count

    if dry_run:
        return RenameResult(
            source, destination, len(updates), changed_links, dry_run=True
        )

    destination_created = False
    written_paths = []
    try:
        source.rename(destination)
        destination_created = True
        for original_path, (_, updated) in updates.items():
            actual_path = destination if original_path == source else original_path
            actual_path.write_bytes(updated)
            written_paths.append((actual_path, original_path))
    except OSError as exc:
        for actual_path, original_path in reversed(written_paths):
            original = updates[original_path][0]
            try:
                actual_path.write_bytes(original)
            except OSError:
                pass
        if destination_created and destination.exists() and not source.exists():
            try:
                destination.rename(source)
            except OSError:
                pass
        raise RenameError(f"寫入失敗，已嘗試回復原狀：{exc}") from exc

    return RenameResult(source, destination, len(updates), changed_links)


def rename_markdown_directory(
    source_path, destination_path, root=ROOT, dry_run=False
):
    """Rename a directory tree and update path-qualified WikiLinks atomically."""
    root = Path(root).resolve()
    source = resolve_in_root(source_path, root)
    destination = resolve_in_root(destination_path, root)
    if not source.is_dir():
        raise RenameError(f"來源資料夾不存在：{source}")
    if destination.exists():
        raise RenameError(f"目標路徑已存在：{destination}")
    if not destination.parent.is_dir():
        raise RenameError(f"目標資料夾的上層不存在：{destination.parent}")
    if source == destination or source in destination.parents:
        raise RenameError("目標資料夾不可等於來源或位於來源之內")

    markdown_files = collect_markdown_files(root)
    source_markdown = [
        path for path in markdown_files if source == path.parent or source in path.parents
    ]
    if not source_markdown:
        raise RenameError(f"來源資料夾沒有 Markdown：{source}")
    destinations = {
        path: destination / path.relative_to(source) for path in source_markdown
    }
    conflicts = [path for path in destinations.values() if path.exists()]
    if conflicts:
        display = "、".join(str(path.relative_to(root)) for path in conflicts)
        raise RenameError(f"目標 Markdown 已存在：{display}")

    resolver = WikiLinkResolver(root, markdown_files)
    updates = {}
    changed_links = 0
    for path in markdown_files:
        original, text, has_bom = decode_markdown(path)
        updated_text = text
        for old_path, new_path in destinations.items():
            updated_text, count = update_wikilinks(
                updated_text, old_path, new_path, resolver, path
            )
            changed_links += count
        if updated_text != text:
            updates[path] = (
                original,
                encode_markdown(updated_text, has_bom),
            )

    if dry_run:
        return RenameResult(
            source, destination, len(updates), changed_links, dry_run=True
        )

    renamed = False
    try:
        source.rename(destination)
        renamed = True
        for original_path, (_, updated) in updates.items():
            if source == original_path.parent or source in original_path.parents:
                actual_path = destination / original_path.relative_to(source)
            else:
                actual_path = original_path
            actual_path.write_bytes(updated)
    except OSError as exc:
        if renamed and destination.exists() and not source.exists():
            try:
                destination.rename(source)
            except OSError:
                pass
        for original_path, (original, _) in updates.items():
            try:
                original_path.write_bytes(original)
            except OSError:
                pass
        raise RenameError(f"寫入失敗，已嘗試回復原狀：{exc}") from exc

    return RenameResult(source, destination, len(updates), changed_links)


def main(argv=None):
    configure_console()
    parser = argparse.ArgumentParser(
        description="改名 Markdown，並同步更新 vault 中所有指向該檔案的 WikiLink。"
    )
    parser.add_argument("source", help="目前的 .md 或資料夾路徑")
    parser.add_argument("destination", help="改名後的 .md 或資料夾路徑")
    parser.add_argument(
        "--dry-run", action="store_true", help="只預覽，不寫入或改名"
    )
    args = parser.parse_args(argv)

    try:
        source = resolve_in_root(args.source, ROOT)
        operation = rename_markdown_directory if source.is_dir() else rename_markdown
        result = operation(
            args.source, args.destination, root=ROOT, dry_run=args.dry_run
        )
    except RenameError as exc:
        print(f"❌ {exc}")
        return 1

    action = "預覽" if result.dry_run else "完成"
    print(f"✅ {action}：{result.source.relative_to(ROOT)}")
    print(f"   → {result.destination.relative_to(ROOT)}")
    print(f"   更新 WikiLink：{result.changed_links} 個（{result.changed_files} 個檔案）")
    if result.dry_run:
        print("   尚未寫入；移除 --dry-run 後才會正式執行。")
    return 0


if __name__ == "__main__":
    sys.exit(main())

'''
Usage:
    python util/rename_markdown.py <source> <destination> [--dry-run]
'''