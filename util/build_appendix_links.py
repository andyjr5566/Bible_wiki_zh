#!/usr/bin/env python3
"""由 appendix 下各分類處理器 (Plugin) 動態建立本章附錄資源連結。"""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from collections import defaultdict
from pathlib import Path

try:
    from .book_paths import book_directory
    from . import console
    from .render_chapter import (
        CHAPTER_NAV_END,
        CHAPTER_NAV_START,
    )
except ImportError:
    from book_paths import book_directory
    import console
    from render_chapter import CHAPTER_NAV_END, CHAPTER_NAV_START


ROOT = Path(__file__).resolve().parent.parent
APPENDIX_DIR = ROOT / "appendix"

CHAPTER_BLOCK_START = "<!-- appendix-links:start -->"
CHAPTER_BLOCK_END = "<!-- appendix-links:end -->"

FHL_MAP_BLOCK_RE = re.compile(
    rf"\n*{re.escape('<!-- fhl-map-links:start -->')}.*?"
    rf"{re.escape('<!-- fhl-map-links:end -->')}\n*",
    re.DOTALL,
)
APPENDIX_BLOCK_RE = re.compile(
    rf"\n*{re.escape(CHAPTER_BLOCK_START)}.*?"
    rf"{re.escape(CHAPTER_BLOCK_END)}\n*",
    re.DOTALL,
)
CHAPTER_NAV_BLOCK_RE = re.compile(
    rf"\n*{re.escape(CHAPTER_NAV_START)}.*?"
    rf"{re.escape(CHAPTER_NAV_END)}\n*",
    re.DOTALL,
)

EXCLUDE_CATEGORIES = set()


def load_category_plugins() -> list[dict]:
    """動態載入 appendix/* 下的所有 plugin（包含 fhl_maps, website 等）。"""
    plugins = []
    if not APPENDIX_DIR.exists():
        return plugins

    for cat_dir in sorted(APPENDIX_DIR.iterdir()):
        if not cat_dir.is_dir() or cat_dir.name in EXCLUDE_CATEGORIES or cat_dir.name.startswith("."):
            continue
        plugin_file = cat_dir / "build.py"
        if plugin_file.exists():
            spec = importlib.util.spec_from_file_location(f"appendix_{cat_dir.name}", plugin_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                plugins.append({
                    "name": cat_dir.name,
                    "module": module,
                    "path": plugin_file,
                })
    return plugins


def collect_all_appendix_sections() -> dict[str, list[str]]:
    """收集所有 plugin 產出的 Markdown 段落。"""
    plugins = load_category_plugins()
    sections_by_chapter: dict[str, list[str]] = defaultdict(list)

    for plugin in plugins:
        mod = plugin["module"]
        # 先執行 plugin 內建的檔案/索引建置程序（若有）
        if hasattr(mod, "build_maps_and_indexes"):
            try:
                mod.build_maps_and_indexes()
            except Exception as exc:
                print(f"⚠️ [{plugin['name']}] 建置索引時發生提示：{exc}")

        if hasattr(mod, "scan_all_entries"):
            entries = mod.scan_all_entries()
            category_title = getattr(mod, "CATEGORY_NAME", plugin["name"])
            for ch_key, items in entries.items():
                if not items:
                    continue
                lines = [f"### {category_title}"]
                for item in items:
                    if item.get("is_wikilink"):
                        lines.append(f"- [[{item['path']}|{item['title']}]]")
                    else:
                        lines.append(f"- [{item['title']}]({item['path']})")
                sections_by_chapter[ch_key].append("\n".join(lines))
    return sections_by_chapter


def chapter_appendix_block(sections: list[str]) -> str:
    """產出整塊包含 start/end HTML 標籤的附錄 Markdown 區塊。"""
    lines = [CHAPTER_BLOCK_START, "## 附錄", ""]
    lines.append("\n\n".join(sections))
    lines.append(CHAPTER_BLOCK_END)
    return "\n".join(lines)


def sync_chapter(path: Path, sections: list[str]) -> str:
    """將附錄區塊動態注入或刪除至章節 Markdown 末尾（本章整理之後）。"""
    text = path.read_text(encoding="utf-8")
    text = FHL_MAP_BLOCK_RE.sub("\n\n", text)
    text = APPENDIX_BLOCK_RE.sub("\n\n", text)
    navigation_matches = list(CHAPTER_NAV_BLOCK_RE.finditer(text))
    navigation = navigation_matches[0].group(0).strip() if navigation_matches else ""
    text = CHAPTER_NAV_BLOCK_RE.sub("\n\n", text)
    text = text.rstrip()

    if navigation:
        heading = re.search(r"^# .+$", text, re.MULTILINE)
        if heading:
            body = text[heading.end():].lstrip("\n")
            text = f"{text[:heading.end()]}\n\n{navigation}\n\n{body}".rstrip()

    if sections:
        block = chapter_appendix_block(sections)
        text = f"{text}\n\n{block}"
    if navigation:
        text = f"{text}\n\n{navigation}"
    return text.rstrip() + "\n"


def write_or_check(path: Path, content: str, check: bool, changed: list[Path]):
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current == content:
        return
    changed.append(path)
    if not check:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")


def main() -> int:
    console.utf8_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="只檢查輸出是否需要更新，不寫入檔案",
    )
    args = parser.parse_args()

    sections_by_chapter = collect_all_appendix_sections()
    changed: list[Path] = []

    for ch_key, sections in sections_by_chapter.items():
        book, chapter_name = ch_key.split("/", 1)
        path = book_directory(ROOT, book) / f"{chapter_name}.md"
        if not path.exists():
            continue
        content = sync_chapter(path, sections)
        write_or_check(path, content, args.check, changed)

    action = "需要更新" if args.check else "已更新"
    print(f"{action} {len(changed)} 個章節檔案附錄區塊。")
    if args.check and changed:
        for path in changed:
            print(f"  {path.relative_to(ROOT)}")

    return 1 if args.check and changed else 0


if __name__ == "__main__":
    sys.exit(main())
