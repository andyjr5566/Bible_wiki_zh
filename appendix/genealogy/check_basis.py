"""Validate evidence attached to genealogy data."""
from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Mapping
from pathlib import Path, PureWindowsPath
from typing import Any

import yaml


BOOKS = {
    "創": "創世記", "出": "出埃及記", "利": "利未記", "民": "民數記",
    "申": "申命記", "書": "約書亞記", "士": "士師記", "得": "路得記",
    "撒上": "撒母耳記上", "撒下": "撒母耳記下",
    "王上": "列王紀上", "王下": "列王紀下",
    "代上": "歷代志上", "代下": "歷代志下",
    "拉": "以斯拉記", "尼": "尼希米記",
    "太": "馬太福音", "可": "馬可福音", "路": "路加福音",
    "約": "約翰福音", "徒": "使徒行傳",
}
COMMENTARY_PREFIXES = (
    "ccbiblestudy_CT_", "ccbiblestudy_GT_", "kingcomments_",
    "biblehub_study_", "stepbible_",
)
_BOOK_PATTERN = "|".join(re.escape(book) for book in sorted(BOOKS, key=len, reverse=True))
_REF_PATTERN = re.compile(
    rf"^(?P<book>{_BOOK_PATTERN})(?P<start_chapter>[0-9]+):(?P<start_verse>[0-9]+)"
    r"(?:-(?:(?P<end_chapter>[0-9]+):)?(?P<end_verse>[0-9]+))?$"
)


def _error(where: str, message: str) -> str:
    return f"{where}: {message}"


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _read_scripture_range(ref: str, root: Path, where: str) -> tuple[list[str] | None, str | None]:
    verses: list[str] = []
    chapter_cache: dict[tuple[str, int], list[str] | None] = {}
    segments = re.split(r"[,，、]", ref)
    if not segments or any(not segment.strip() for segment in segments):
        return None, _error(where, f"ref 格式無效：{ref!r}")

    for raw_segment in segments:
        segment = raw_segment.strip()
        match = _REF_PATTERN.fullmatch(segment)
        if match is None:
            return None, _error(where, f"ref 格式無效：{segment!r}")

        book = match.group("book")
        start_chapter = int(match.group("start_chapter"))
        start_verse = int(match.group("start_verse"))
        end_chapter = int(match.group("end_chapter") or start_chapter)
        end_verse = int(match.group("end_verse") or start_verse)
        start, end = (start_chapter, start_verse), (end_chapter, end_verse)
        if min(start_chapter, start_verse, end_chapter, end_verse) < 1 or end < start:
            return None, _error(where, f"ref 範圍無效：{segment!r}")

        chapter, verse = start
        while (chapter, verse) <= end:
            cache_key = (book, chapter)
            if cache_key not in chapter_cache:
                scripture_path = root / "raw_scripture" / BOOKS[book] / f"第{chapter}章.txt"
                try:
                    chapter_cache[cache_key] = scripture_path.read_text(encoding="utf-8").splitlines()
                except FileNotFoundError:
                    chapter_cache[cache_key] = None
                except OSError as exc:
                    return None, _error(where, f"無法讀取經文檔：{scripture_path.name}（{exc}）")

            lines = chapter_cache[cache_key]
            if lines is None:
                return None, _error(
                    where, f"經文檔不存在：raw_scripture/{BOOKS[book]}/第{chapter}章.txt"
                )
            if verse > len(lines):
                return None, _error(where, f"經節不存在：{book}{chapter}:{verse}")

            verses.append(lines[verse - 1])
            verse += 1
            if verse > len(lines):
                chapter, verse = chapter + 1, 1

    return verses, None


def _check_scripture(item: Mapping[str, Any], where: str, root: Path) -> list[str]:
    ref, quote = item.get("ref"), item.get("quote")
    if not _nonempty_string(ref):
        return [_error(where, "ref 必須是非空字串")]
    if not _nonempty_string(quote):
        return [_error(where, "quote 必填且必須是非空字串")]

    verses, ref_error = _read_scripture_range(ref, root, where)
    if ref_error:
        return [ref_error]
    if quote not in "\n".join(verses or []):
        return [_error(where, f"quote 未在指定經文中逐字出現：{quote!r}")]
    return []


def _collapse_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def _check_commentary(item: Mapping[str, Any], where: str, root: Path) -> list[str]:
    source, quote = item.get("source"), item.get("quote")
    if not _nonempty_string(source):
        return [_error(where, "source 必須是非空檔名字串")]
    if (
        "/" in source or "\\" in source or ":" in source
        or PureWindowsPath(source).name != source or Path(source).name != source
    ):
        return [_error(where, "source 必須是 raw_data/ 底下的檔名，不可含路徑")]
    if not source.startswith(COMMENTARY_PREFIXES):
        return [_error(where, f"source 檔名開頭不符合規定：{source!r}")]
    if not _nonempty_string(quote):
        return [_error(where, "quote 必填且必須是非空字串")]

    source_path = root / "raw_data" / source
    try:
        content = source_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return [_error(where, f"註釋來源檔不存在：raw_data/{source}")]
    except OSError as exc:
        return [_error(where, f"無法讀取註釋來源檔：{source}（{exc}）")]

    if _collapse_whitespace(quote) not in _collapse_whitespace(content):
        return [_error(where, f"quote 未在來源檔中逐字出現：{quote!r}")]
    return []


def _check_external(item: Mapping[str, Any], where: str) -> list[str]:
    errors = [
        _error(where, f"{field} 必須是非空字串")
        for field in ("external", "version", "entry")
        if not _nonempty_string(item.get(field))
    ]
    external = item.get("external")
    if isinstance(external, str) and external.strip().casefold() in {"wikipedia", "維基百科"}:
        errors.append(_error(where, "external 不可使用 Wikipedia／維基百科"))
    return errors


def check_basis(items: list, where: str, root: Path) -> list[str]:
    """回傳根據清單的錯誤訊息；空清單代表通過。"""
    if not isinstance(items, list) or not items:
        return [_error(where, "basis 必須是非空清單")]

    allowed_keys = {
        "ref": {"ref", "quote", "note"},
        "source": {"source", "quote", "note"},
        "external": {"external", "version", "entry", "note"},
    }
    errors: list[str] = []
    for index, item in enumerate(items):
        item_where = f"{where}[{index}]"
        if not isinstance(item, Mapping):
            errors.append(_error(item_where, "basis 項目必須是 mapping"))
            continue

        kinds = [key for key in ("ref", "source", "external") if key in item]
        if len(kinds) != 1:
            errors.append(_error(item_where, "basis 項目必須且只能使用 ref、source、external 其中一種"))
            continue

        kind = kinds[0]
        if any(key not in allowed_keys[kind] for key in item):
            errors.append(_error(item_where, f"{kind} 類 basis 含有不允許的欄位"))
            continue
        if "note" in item and not isinstance(item["note"], str):
            errors.append(_error(item_where, "note 必須是字串"))
            continue

        if kind == "ref":
            errors.extend(_check_scripture(item, item_where, root))
        elif kind == "source":
            errors.extend(_check_commentary(item, item_where, root))
        else:
            errors.extend(_check_external(item, item_where))
    return errors


def scan_file(path: Path, root: Path) -> tuple[int, list[str]]:
    """遞迴檢查單一 YAML 檔案中的每一個 basis 欄位。"""
    path = Path(path)
    display_name = path.name
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        return 0, [_error(f"{display_name}:yaml", f"無法讀取 YAML：{exc}")]

    count = 0
    errors: list[str] = []
    active: set[int] = set()

    def visit(value: Any, location: str) -> None:
        nonlocal count
        if isinstance(value, Mapping):
            identity = id(value)
            if identity in active:
                return
            active.add(identity)
            try:
                for key, child in value.items():
                    child_location = f"{location}.{key}" if location else str(key)
                    if key == "basis":
                        count += len(child) if isinstance(child, list) else 1
                        errors.extend(check_basis(child, f"{display_name}:{child_location}", root))
                    visit(child, child_location)
            finally:
                active.remove(identity)
        elif isinstance(value, list):
            identity = id(value)
            if identity in active:
                return
            active.add(identity)
            try:
                for index, child in enumerate(value):
                    visit(child, f"{location}[{index}]")
            finally:
                active.remove(identity)

    visit(document, "")
    return count, errors


def _expand_inputs(inputs: list[str]) -> tuple[list[Path], list[str]]:
    files: list[Path] = []
    errors: list[str] = []
    for raw_path in inputs:
        path = Path(raw_path)
        if not path.exists():
            errors.append(_error(raw_path, "路徑不存在"))
        elif path.is_dir():
            files.extend(sorted(child for child in path.glob("*.yaml") if child.is_file()))
        elif path.is_file():
            files.append(path)
        else:
            errors.append(_error(raw_path, "不是一般檔案或資料夾"))
    return files, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="檢查家譜 YAML 的 basis 根據欄位")
    parser.add_argument("paths", nargs="+", help="YAML 檔案或資料夾")
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    root = Path(__file__).resolve().parents[2]
    files, errors = _expand_inputs(args.paths)
    total_items = 0
    total_errors = len(errors)
    for error in errors:
        print(error)
    for path in files:
        count, file_errors = scan_file(path, root)
        total_items += count
        total_errors += len(file_errors)
        print(f"{path}: {count} items")
        for error in file_errors:
            print(f"  {error}")

    if total_errors:
        print(f"FAIL ({total_errors} errors)")
        return 1
    print(f"PASS ({total_items} items)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
