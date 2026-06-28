#!/usr/bin/env python3
"""知識庫結構、來源標記與保護區驗證。"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

from build_link_index import (
    EXCLUDE_PARTS,
    LINK_FOLDER,
    ROOT,
    collect_entries,
    load_resolutions,
    make_index,
)

VALID_STATUS = {"formal", "candidate"}
PROTECTED_HEADINGS = {"定義", "定義／基本資料", "核心摘要", "主題發展"}
MARKER_RE = re.compile(
    r"<!-- accumulation:(?P<book>[^:]+):(?P<chapter>\d+):"
    r"(?P<edge>start|end) -->"
)


def frontmatter(text):
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return None
    data = yaml.safe_load(match.group(1))
    return data if isinstance(data, dict) else None


def validate_file(path, strict=False):
    path = path if path.is_absolute() else ROOT / path
    errors, warnings = [], []
    text = path.read_text(encoding="utf-8")
    fm = frontmatter(text)
    relative = path.relative_to(ROOT)
    if fm is None:
        errors.append(f"{relative}: 缺少或無法解析 YAML frontmatter")
        return errors, warnings

    status = fm.get("status")
    if status not in VALID_STATUS:
        errors.append(f"{relative}: status 必須是 formal 或 candidate")
    for field in ("aliases", "secondary_types"):
        if field in fm and not isinstance(fm[field], list):
            errors.append(f"{relative}: {field} 必須是 YAML list")
    if fm.get("source_scope") != "collected_only":
        (errors if strict else warnings).append(
            f"{relative}: source_scope 不是 collected_only"
        )

    heading = re.search(r"^#\s+(.+?)\s*$", text, re.M)
    if not heading or heading.group(1) != path.stem:
        (errors if strict else warnings).append(f"{relative}: H1 必須與檔名一致")

    markers = {}
    stack = {}
    for match in MARKER_RE.finditer(text):
        key = (match.group("book"), match.group("chapter"))
        if match.group("edge") == "start":
            if key in stack or key in markers:
                errors.append(f"{relative}: 重複累積標記 {key[0]}第{key[1]}章")
            stack[key] = match.end()
        elif key not in stack:
            errors.append(f"{relative}: 累積結束標記沒有對應起點 {key}")
        else:
            body = text[stack.pop(key):match.start()]
            markers[key] = body
            if "來源" not in body:
                errors.append(f"{relative}: {key[0]}第{key[1]}章累積缺少來源")
    for key in stack:
        errors.append(f"{relative}: 累積標記未結束 {key[0]}第{key[1]}章")

    if status == "formal":
        if not re.search(r"^##\s+(定義|定義／基本資料)\s*$", text, re.M):
            (errors if strict else warnings).append(f"{relative}: 正式條目缺少定義區")
        if not re.search(r"^##\s+來源依據\s*$", text, re.M):
            (errors if strict else warnings).append(f"{relative}: 正式條目缺少來源依據")
    if re.search(r"（保護區）|根據目前已收集資料整理。", text):
        warnings.append(f"{relative}: 仍含模板占位文字")
    return errors, warnings


def extract_protected(text):
    sections = {}
    lines = text.splitlines()
    current = None
    buffer = []
    for line in lines:
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            if current is not None:
                sections[current] = "\n".join(buffer).strip()
            name = heading.group(1)
            current = name if name in PROTECTED_HEADINGS else None
            buffer = []
        elif current is not None:
            buffer.append(line)
    if current is not None:
        sections[current] = "\n".join(buffer).strip()
    return sections


def validate_protected_changes(base):
    errors = []
    command = ["git", "diff", "--name-only", f"{base}...HEAD", "--", "link_folder"]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if result.returncode:
        return [f"無法取得 protected section diff：{result.stderr.strip()}"]
    for name in result.stdout.splitlines():
        path = ROOT / name
        if not path.exists() or path.suffix != ".md":
            continue
        old = subprocess.run(
            ["git", "show", f"{base}:{name}"], cwd=ROOT,
            capture_output=True, text=True, encoding="utf-8",
        )
        if old.returncode:  # 新檔沒有保護區歷史
            continue
        if extract_protected(old.stdout) != extract_protected(path.read_text(encoding="utf-8")):
            errors.append(f"{name}: 既有正式條目的保護區被修改")
    return errors


def changed_link_files(base):
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...HEAD", "--", "link_folder"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode:
        return set()
    return {name.replace("\\", "/") for name in result.stdout.splitlines()}


def validate(base=None):
    errors, warnings = [], []
    entries, collect_errors = collect_entries()
    # type 不一致先列警告，讓舊資料逐卷清理；其他解析錯誤阻擋。
    for issue in collect_errors:
        (warnings if "與資料夾分類" in issue else errors).append(issue)
    _, index_errors = make_index(entries, load_resolutions())
    errors.extend(index_errors)

    changed = changed_link_files(base) if base else set()
    for path in sorted(LINK_FOLDER.rglob("*.md")):
        if EXCLUDE_PARTS & set(path.parts):
            continue
        relative = str(path.relative_to(ROOT)).replace("\\", "/")
        file_errors, file_warnings = validate_file(path, strict=relative in changed)
        errors.extend(file_errors)
        warnings.extend(file_warnings)
    if base:
        errors.extend(validate_protected_changes(base))
    return errors, warnings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", help="檢查相對此 Git revision 的保護區變更")
    parser.add_argument("--report", help="選填：將完整結果寫入指定 JSON")
    args = parser.parse_args()
    errors, warnings = validate(args.base)
    if args.report:
        report = {"errors": errors, "warnings": warnings}
        report_path = Path(args.report)
        if not report_path.is_absolute():
            report_path = ROOT / "util" / "output" / report_path
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    for item in errors:
        print(f"❌ {item}")
    for item in warnings:
        print(f"⚠️ {item}")
    print(f"結構驗證：{len(errors)} errors，{len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
