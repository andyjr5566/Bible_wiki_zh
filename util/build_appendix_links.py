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
except ImportError:
    from book_paths import book_directory
    import console


ROOT = Path(__file__).resolve().parent.parent
APPENDIX_DIR = ROOT / "appendix"

CHAPTER_BLOCK_START = "<!-- appendix-links:start -->"
CHAPTER_BLOCK_END = "<!-- appendix-links:end -->"
BLOCK_RE = re.compile(
    rf"\n*{re.escape(CHAPTER_BLOCK_START)}.*?"
    rf"{re.escape(CHAPTER_BLOCK_END)}\n*",
    re.DOTALL,
)

# 排除非 general 附錄外掛的內部資料夾
EXCLUDE_CATEGORIES = {"fhl_maps"}


def load_category_plugins() -> list[dict]:
    """動態載入 appendix/* 下的 plugin。"""
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
    """收集所有 plugin 產出的 Markdown 段落。

    回傳: {"創世記/第6章": ["### 互動網站\n- [挪亞方舟...](...)"]}
    """
    plugins = load_category_plugins()
    sections_by_chapter: dict[str, list[str]] = defaultdict(list)

    for plugin in plugins:
        mod = plugin["module"]
        if hasattr(mod, "scan_all_entries"):
            entries = mod.scan_all_entries()
            category_title = getattr(mod, "CATEGORY_NAME", plugin["name"])
            for ch_key, items in entries.items():
                if not items:
                    continue
                lines = [f"### {category_title}"]
                for item in items:
                    lines.append(f"- [{item['title']}]({item['path']})")
                sections_by_chapter[ch_key].append("\n".join(lines))
    return sections_by_chapter


def chapter_appendix_block(sections: list[str]) -> str:
    """產出整塊包含 start/end HTML 標籤的附錄 Markdown 區塊。"""
    lines = [CHAPTER_BLOCK_START, "## 相關資源", ""]
    lines.append("\n\n".join(sections))
    lines.append(CHAPTER_BLOCK_END)
    return "\n".join(lines)


def sync_chapter(path: Path, sections: list[str]) -> str:
    """將附錄區塊動態注入或刪除至章節 Markdown 中。"""
    text = path.read_text(encoding="utf-8")
    text = BLOCK_RE.sub("\n\n", text)
    if not sections:
        return text

    block = chapter_appendix_block(sections)
    lines = text.splitlines()

    saw_verse = False
    insert_at = None
    for index, line in enumerate(lines):
        if re.match(r"^\d+\.\s", line):
            saw_verse = True
        elif saw_verse and line.strip() == "---":
            insert_at = index
            break

    if insert_at is None:
        raise ValueError(f"找不到經文正文後的分隔線：{path}")

    before = "\n".join(lines[:insert_at]).rstrip()
    after = "\n".join(lines[insert_at:]).lstrip()
    return f"{before}\n\n{block}\n\n{after}\n"


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
