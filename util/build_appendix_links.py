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


def collect_plugin_entries(*, build_indexes: bool = True) -> list[dict]:
    """掃描每個 plugin，回傳 ``[{"plugin": ..., "title": ..., "entries": {ch_key: [item, ...]}}]``。

    ``build_indexes=False`` 時只做唯讀掃描（跳過各 plugin 的 build_maps_and_indexes）。
    """
    results: list[dict] = []
    for plugin in load_category_plugins():
        mod = plugin["module"]
        # 先執行 plugin 內建的檔案/索引建置程序（若有）
        if build_indexes and hasattr(mod, "build_maps_and_indexes"):
            try:
                mod.build_maps_and_indexes()
            except Exception as exc:
                print(f"⚠️ [{plugin['name']}] 建置索引時發生提示：{exc}")

        if hasattr(mod, "scan_all_entries"):
            results.append({
                "plugin": plugin,
                "title": getattr(mod, "CATEGORY_NAME", plugin["name"]),
                "entries": mod.scan_all_entries(),
            })
    return results


def sections_by_chapter_from(plugin_entries: list[dict]) -> dict[str, list[str]]:
    """把各 plugin 的入口整理成「每章一串 Markdown 段落」。"""
    sections_by_chapter: dict[str, list[str]] = defaultdict(list)
    for result in plugin_entries:
        for ch_key, items in result["entries"].items():
            # 標成 toc_only 的入口只列在全書目錄，不寫進章節檔
            items = [item for item in items if not item.get("toc_only")]
            if not items:
                continue
            lines = [f"### {result['title']}"]
            for item in items:
                if item.get("is_wikilink"):
                    lines.append(f"- [[{item['path']}|{item['title']}]]")
                else:
                    lines.append(f"- [{item['title']}]({item['path']})")
            sections_by_chapter[ch_key].append("\n".join(lines))
    return sections_by_chapter


def collect_all_appendix_sections(*, build_indexes: bool = True) -> dict[str, list[str]]:
    """收集所有 plugin 產出的 Markdown 段落。

    ``build_indexes=False`` 時只做唯讀掃描（跳過各 plugin 的 build_maps_and_indexes），
    供 check_chapter_files 這類「只想知道某章有沒有附錄資源」的一致性檢查用。
    """
    return sections_by_chapter_from(collect_plugin_entries(build_indexes=build_indexes))


# ---------------------------------------------------------------- 全書目錄及綱要
#
# plugin 若在模組裡宣告 ``BOOK_INDEX_HEADING = "🕹️ 互動網站"``，本程式除了把連結寫進各章，
# 也會依章節順序，把同一批連結整理成一段，放進該卷的「全書目錄及綱要.md」。
# 沒宣告的 plugin（例如 fhl_maps、video）不會動目錄頁。

BOOK_INDEX_FILE = "全書目錄及綱要.md"
BOOK_INDEX_BEFORE = re.compile(r"^## 🎬", re.MULTILINE)


def book_index_markers(plugin_name: str) -> tuple[str, str]:
    return (f"<!-- appendix-index:{plugin_name}:start -->", f"<!-- appendix-index:{plugin_name}:end -->")


def _chapter_sort_key(chapter_name: str) -> tuple[int, str]:
    m = re.search(r"第(\d+)", chapter_name)
    return (int(m.group(1)) if m else 10**6, chapter_name)


def book_index_block(plugin_name: str, heading: str, folder: str, items_by_chapter: dict[str, list[dict]]) -> str:
    """產出目錄頁裡屬於某個 plugin 的整段（含 start/end 標記）。章節依章號排序。"""
    start, end = book_index_markers(plugin_name)
    lines = [start, f"## {heading}", ""]
    # 同一組入口掛在好幾章時只列一次：連續的章節併成「第a–b章」，連到第一章
    groups: dict[tuple, list[str]] = {}
    for chapter_name in sorted(items_by_chapter, key=_chapter_sort_key):
        key = tuple((item["title"], item["path"], bool(item.get("is_wikilink"))) for item in items_by_chapter[chapter_name])
        groups.setdefault(key, []).append(chapter_name)
    rows: list[tuple[int, str]] = []
    for key, chapters in groups.items():
        links = "、".join(f"[[{path}|{title}]]" if wiki else f"[{title}]({path})" for title, path, wiki in key)
        runs: list[list[str]] = []
        for name in chapters:
            n = _chapter_sort_key(name)[0]
            if runs and _chapter_sort_key(runs[-1][-1])[0] + 1 == n:
                runs[-1].append(name)
            else:
                runs.append([name])
        # 同一組入口只出一列；不連續的章節（例如第2、10章）用頓號接在同一列
        labels = []
        for run in runs:
            a, b = _chapter_sort_key(run[0])[0], _chapter_sort_key(run[-1])[0]
            labels.append(f"第{a}章" if a == b else f"第{a}–{b}章")
        rows.append((_chapter_sort_key(runs[0][0])[0], f"- [[{folder}/{runs[0][0]}|{'、'.join(labels)}]]：{links}"))
    lines.extend(line for _, line in sorted(rows, key=lambda r: r[0]))
    lines.append(end)
    return "\n".join(lines)


def sync_book_index(text: str, plugin_name: str, block: str | None) -> str:
    """把某 plugin 的目錄段放進（或更新、或移除）目錄頁文字。

    已有標記就原地取代；沒有就放在「🎬 大衛鮑森舊約縱覽」之前，沒有那一段就放在檔尾。
    ``block`` 為 None 表示這一卷沒有入口，把舊的段落清掉。
    """
    start, end = book_index_markers(plugin_name)
    block_re = re.compile(rf"\n*{re.escape(start)}.*?{re.escape(end)}\n*", re.DOTALL)
    if block_re.search(text):
        replacement = f"\n\n{block}\n\n" if block else "\n\n"
        text = block_re.sub(lambda _m: replacement, text, count=1)
    elif block is not None:
        match = BOOK_INDEX_BEFORE.search(text)
        if match:
            text = f"{text[:match.start()].rstrip()}\n\n{block}\n\n{text[match.start():]}"
        else:
            text = f"{text.rstrip()}\n\n{block}\n"
    else:
        return text  # 這一卷沒有入口、目錄頁也沒有舊段落：原樣不動，不重排空白
    return text.rstrip() + "\n"


def book_index_updates(plugin_entries: list[dict]) -> dict[Path, str]:
    """回傳 ``{目錄頁路徑: 更新後全文}``，只含有宣告 BOOK_INDEX_HEADING 的 plugin。"""
    updates: dict[Path, str] = {}
    for result in plugin_entries:
        plugin = result["plugin"]
        heading = getattr(plugin["module"], "BOOK_INDEX_HEADING", None)
        if not heading:
            continue
        by_folder: dict[Path, dict[str, list[dict]]] = defaultdict(dict)
        for ch_key, items in result["entries"].items():
            if not items:
                continue
            book, chapter_name = ch_key.split("/", 1)
            folder = book_directory(ROOT, book)
            if (folder / f"{chapter_name}.md").exists():
                by_folder[folder][chapter_name] = items
        # 每一卷的目錄頁都要走一遍：沒有入口的卷，舊段落要清掉
        for outline in sorted(ROOT.glob(f"*/{BOOK_INDEX_FILE}")):
            folder = outline.parent
            items_by_chapter = by_folder.get(folder)
            block = book_index_block(plugin["name"], heading, folder.name, items_by_chapter) if items_by_chapter else None
            text = updates.get(outline, outline.read_text(encoding="utf-8"))
            updates[outline] = sync_book_index(text, plugin["name"], block)
    return updates


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

    plugin_entries = collect_plugin_entries()
    sections_by_chapter = sections_by_chapter_from(plugin_entries)
    changed: list[Path] = []

    for ch_key, sections in sections_by_chapter.items():
        book, chapter_name = ch_key.split("/", 1)
        path = book_directory(ROOT, book) / f"{chapter_name}.md"
        if not path.exists():
            continue
        content = sync_chapter(path, sections)
        write_or_check(path, content, args.check, changed)

    # 宣告了 BOOK_INDEX_HEADING 的 plugin，同一批連結也整理進各卷的全書目錄及綱要
    for path, content in book_index_updates(plugin_entries).items():
        write_or_check(path, content, args.check, changed)

    action = "需要更新" if args.check else "已更新"
    print(f"{action} {len(changed)} 個章節／目錄檔案附錄區塊。")
    if args.check and changed:
        for path in changed:
            print(f"  {path.relative_to(ROOT)}")

    return 1 if args.check and changed else 0


if __name__ == "__main__":
    sys.exit(main())
