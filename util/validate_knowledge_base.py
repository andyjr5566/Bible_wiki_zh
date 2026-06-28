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
BIBLE_BOOKS = list(json.loads(
    (ROOT / "_config" / "bible_books.json").read_text(encoding="utf-8")
))
BOOK_RANK = {book: index for index, book in enumerate(BIBLE_BOOKS)}
FORMAL_H2 = ["定義", "按書卷累積", "主題發展", "相關條目", "來源依據"]
CANDIDATE_H2 = ["類型", "觸發來源", "目前資料", "相關條目", "待補充"]
PROTECTED_HEADINGS = {
    "定義", "定義／基本資料", "定義／核心摘要", "定定義／核心摘要",
    "核心摘要", "主題發展",
}
PROTECTED_CANONICAL = {
    "定義／基本資料": "定義",
    "定義／核心摘要": "定義",
    "定定義／核心摘要": "定義",
    "核心摘要": "定義",
}
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
            accumulation = re.search(
                r"^## 按書卷累積\s*$([\s\S]*?)(?=^## 主題發展\s*$)", text, re.M
            )
            if not accumulation or not (
                accumulation.start(1) <= match.start() < accumulation.end(1)
            ):
                errors.append(f"{relative}: {key[0]}第{key[1]}章累積標記不在按書卷累積區")
            else:
                before_marker = text[accumulation.start(1):match.start()]
                parent_headings = re.findall(r"^###\s+(.+?)\s*$", before_marker, re.M)
                if not parent_headings or parent_headings[-1] != key[0]:
                    errors.append(
                        f"{relative}: {key[0]}第{key[1]}章不在「### {key[0]}」之下"
                    )
                if not re.match(rf"\s*####\s+第{key[1]}章\s*$", body, re.M):
                    errors.append(
                        f"{relative}: {key[0]}第{key[1]}章標記內缺少對應 H4"
                    )
    for key in stack:
        errors.append(f"{relative}: 累積標記未結束 {key[0]}第{key[1]}章")

    if status == "formal":
        if not re.search(r"^##\s+(定義|定義／基本資料)\s*$", text, re.M):
            (errors if strict else warnings).append(f"{relative}: 正式條目缺少定義區")
        if not re.search(r"^##\s+來源依據\s*$", text, re.M):
            (errors if strict else warnings).append(f"{relative}: 正式條目缺少來源依據")
        headings = re.findall(r"^##\s+(.+?)\s*$", text, re.M)
        if "賜福" in str(path):
            import sys
            print(f"DEBUG headings: {headings}", file=sys.stderr)
            print(f"DEBUG expected: {list(FORMAL_H2)}", file=sys.stderr)
            print(f"DEBUG match: {headings == FORMAL_H2}", file=sys.stderr)
            for i in range(min(len(headings), len(FORMAL_H2))):
                h, f = headings[i], FORMAL_H2[i]
                if h != f:
                    print(f"  DIFF[{i}]: got {repr(h)} ({h.encode('utf-8').hex()}) expected {repr(f)} ({f.encode('utf-8').hex()})", file=sys.stderr)
        if headings != FORMAL_H2:
            errors.append(f"{relative}: 正式條目 H2 順序不符合 scheme")
        marker_keys = [(m.group("book"), int(m.group("chapter"))) for m in MARKER_RE.finditer(text)
                       if m.group("edge") == "start"]
        ordered_keys = sorted(
            marker_keys,
            key=lambda item: (BOOK_RANK.get(item[0], 999), item[1]),
        )
        if marker_keys != ordered_keys:
            errors.append(f"{relative}: 按書卷累積未依書卷、章次排序")
        if re.search(r"^###\s+.+?第\s*[一二三四五六七八九十廿百\d]+\s*章\s*$", text, re.M):
            errors.append(f"{relative}: 章次必須使用「### 書卷／#### 第N章」結構")
    elif status == "candidate":
        headings = re.findall(r"^##\s+(.+?)\s*$", text, re.M)
        if headings != CANDIDATE_H2:
            errors.append(f"{relative}: 候選條目 H2 順序不符合 scheme")
    if re.search(r"（保護區）|根據目前已收集資料整理。", text):
        warnings.append(f"{relative}: 仍含模板占位文字")
    return errors, warnings


def validate_chapter(path):
    errors = []
    book = path.parent.name
    match = re.fullmatch(r"第(\d+)章", path.stem)
    if not match:
        return [f"{path.relative_to(ROOT)}: 章節檔名不合法"]
    chapter = int(match.group(1))
    text = path.read_text(encoding="utf-8")
    expected_h1 = f"# {book} 第{chapter}章"
    h1 = re.search(r"^#\s+.+$", text, re.M)
    if not h1 or h1.group(0) != expected_h1:
        errors.append(f"{path.relative_to(ROOT)}: H1 必須是「{expected_h1}」")
    headings = re.findall(r"^##\s+(.+?)\s*$", text, re.M)
    if headings != ["本章知識節點", "本章整理"]:
        errors.append(f"{path.relative_to(ROOT)}: H2 必須依序為本章知識節點、本章整理")
    knowledge_match = re.search(
        r"^## 本章知識節點\s*$([\s\S]*?)(?=^## 本章整理\s*$)", text, re.M
    )
    if not knowledge_match or not knowledge_match.group(1).strip():
        errors.append(f"{path.relative_to(ROOT)}: 本章知識節點不可為空")
    organization_match = re.search(r"^## 本章整理\s*$([\s\S]+)$", text, re.M)
    if not organization_match or not organization_match.group(1).strip():
        errors.append(f"{path.relative_to(ROOT)}: 本章整理不可為空")
    knowledge = text.find("## 本章知識節點")
    scripture = text[:knowledge] if knowledge >= 0 else text
    verses = [int(value) for value in re.findall(r"^(\d+)\.\s", scripture, re.M)]
    raw = ROOT / "raw_scripture" / book / f"第{chapter}章.txt"
    if raw.exists():
        expected_count = len(raw.read_text(encoding="utf-8").splitlines())
        if verses != list(range(1, expected_count + 1)):
            errors.append(
                f"{path.relative_to(ROOT)}: 經文節數／順序不符，"
                f"實際 {len(verses)}，應為 {expected_count}"
            )
    return errors


def extract_protected(text):
    sections = {}
    lines = text.splitlines()
    current = None
    buffer = []
    for line in lines:
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            if current is not None:
                content = "\n".join(buffer).strip()
                if content and content not in sections.get(current, ""):
                    sections[current] = "\n\n".join(filter(None, [sections.get(current), content]))
            name = PROTECTED_CANONICAL.get(heading.group(1), heading.group(1))
            current = name if name in PROTECTED_HEADINGS else None
            buffer = []
        elif current is not None:
            buffer.append(line)
    if current is not None:
        content = "\n".join(buffer).strip()
        if content and content not in sections.get(current, ""):
            sections[current] = "\n\n".join(filter(None, [sections.get(current), content]))
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
        old_sections = extract_protected(old.stdout)
        new_sections = extract_protected(path.read_text(encoding="utf-8"))
        changed = [
            section for section, old_content in old_sections.items()
            if old_content not in new_sections.get(section, "")
        ]
        if changed:
            errors.append(f"{name}: 既有正式條目的保護區被修改：{', '.join(changed)}")
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
    for book_dir in sorted(ROOT.iterdir()):
        if not book_dir.is_dir() or not (ROOT / "raw_scripture" / book_dir.name).exists():
            continue
        for chapter_path in sorted(book_dir.glob("第*章.md")):
            errors.extend(validate_chapter(chapter_path))
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
