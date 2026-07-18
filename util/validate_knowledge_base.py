#!/usr/bin/env python3
"""知識庫結構、來源標記與保護區驗證。"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

try:
    from .book_paths import canonical_book_name, existing_book_directories
    from . import console
    from . import remediation
except ImportError:
    from book_paths import canonical_book_name, existing_book_directories
    import console
    import remediation

from build_link_index import (
    EXCLUDE_PARTS,
    LINK_FOLDER,
    ROOT,
    collect_entries,
    load_resolutions,
    make_index,
)
from resolve_link_candidates import load_homonyms, normalize_name

VALID_STATUS = {"formal", "candidate"}
BIBLE_BOOKS = list(json.loads(
    (ROOT / "_config" / "bible_books.json").read_text(encoding="utf-8")
))
BOOK_RANK = {book: index for index, book in enumerate(BIBLE_BOOKS)}
FORMAL_H2 = ["定義", "按書卷累積", "主題發展", "相關條目", "來源依據"]
FORMAL_REQUIRED_H2 = ["定義", "按書卷累積", "來源依據"]
# 候選條目被 link_updates 累積後會多出「按書卷累積」（render_entry 初建時沒有）。
CANDIDATE_H2 = ["類型", "觸發來源", "目前資料", "按書卷累積", "相關條目", "待補充"]
CANDIDATE_REQUIRED_H2 = ["類型", "觸發來源", "目前資料", "待補充"]
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
WIKILINK_RE = re.compile(r"\[\[([^\]\r\n]+)\]\]")
INTERNAL_SOURCE_LINE_RE = re.compile(
    r"^\s*-\s*(?:觸發來源|來源檔案)(?:\s*[：:].*)?\s*$"
    r"|^\s*-?\s*raw_data\s*[：:].*$"
    r"|^\s*-\s*來源\s*[：:]\s*見本條目「來源依據」\s*$",
    re.M,
)


def frontmatter(text):
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return None
    data = yaml.safe_load(match.group(1))
    return data if isinstance(data, dict) else None


def ambiguous_wikilinks(text, homonyms):
    labels = {normalize_name(label): label for label in homonyms}
    found = []
    for match in WIKILINK_RE.finditer(text):
        target = match.group(1).partition("|")[0].strip()
        target = re.split(r"[#^]", target, maxsplit=1)[0].strip()
        label = labels.get(normalize_name(target))
        if label:
            line = text.count("\n", 0, match.start()) + 1
            found.append((label, line))
    return found


def validate_homonyms(homonyms, index):
    errors = []
    normalized_index_names = {normalize_name(name) for name in index}
    for label, options in homonyms.items():
        if len(options) < 2:
            errors.append(f"link_homonyms.yaml:「{label}」至少需要兩個不同 target")
        targets = [option["target"] for option in options]
        if len(targets) != len(set(targets)):
            errors.append(f"link_homonyms.yaml:「{label}」含重複 target")
        if normalize_name(label) in normalized_index_names:
            errors.append(
                f"link_homonyms.yaml: 歧義裸名「{label}」不得作正式檔名或 alias"
            )
        for option in options:
            target = option["target"]
            entry = index.get(target)
            if not entry or "alias_of" in entry:
                errors.append(
                    f"link_homonyms.yaml:「{label}」target 不存在或不是正式名稱：{target}"
                )
            elif entry.get("type") != option["type"]:
                errors.append(
                    f"link_homonyms.yaml:「{label}」target 類型不符："
                    f"{target} 應為 {option['type']}，實為 {entry.get('type')}"
                )
    return errors


def check_h2(relative, headings, scheme, required, label):
    """必填 H2 齊備，且出現的 scheme H2 依 scheme 順序排列（選填可缺）。"""
    errors = []
    missing = [name for name in required if name not in headings]
    if missing:
        errors.append(f"{relative}: {label}缺少必填 H2：{', '.join(missing)}")
    order = {name: index for index, name in enumerate(scheme)}
    present = [name for name in headings if name in order]
    if present != sorted(present, key=lambda name: order[name]):
        errors.append(f"{relative}: {label} H2 順序不符合 scheme")
    return errors


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

    if INTERNAL_SOURCE_LINE_RE.search(text):
        errors.append(f"{relative}: 不得顯示內部來源欄位或 raw_data 檔案路徑")

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
            accumulation = re.search(
                r"^## 按書卷累積\s*$([\s\S]*?)(?=^## (?:主題發展|相關條目|來源依據)\s*$)",
                text, re.M,
            )
            if not accumulation:
                accumulation = re.search(
                    r"^## 按書卷累積\s*$([\s\S]*)", text, re.M
                )
            if not accumulation or not (
                accumulation.start(1) <= match.start() < accumulation.end(1)
            ):
                errors.append(f"{relative}: {key[0]}第{key[1]}章累積標記不在按書卷累積區")
            else:
                before_marker = text[accumulation.start(1):match.start()]
                parent_headings = re.findall(r"^###\s+(.+?)\s*$", before_marker, re.M)
                # Normalize book names for comparison (strip "04 " prefix)
                normalized_parent_headings = [canonical_book_name(h) for h in parent_headings]
                normalized_key_book = canonical_book_name(key[0])
                if not normalized_parent_headings or normalized_parent_headings[-1] != normalized_key_book:
                    errors.append(
                        f"{relative}: {key[0]}第{key[1]}章不在「### {normalized_key_book}」之下"
                    )
                if not re.match(
                    rf"\s*####\s+(?:\[\[[^\]|]*\|)?第{key[1]}章(?:\]\])?\s*$", body, re.M):
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
        errors.extend(
            check_h2(relative, headings, FORMAL_H2, FORMAL_REQUIRED_H2, "正式條目")
        )
        marker_keys = [(m.group("book"), int(m.group("chapter"))) for m in MARKER_RE.finditer(text)
                       if m.group("edge") == "start"]
        # Normalize book names to canonical form for consistent sorting
        normalized_marker_keys = [(canonical_book_name(book), chapter) for book, chapter in marker_keys]
        ordered_keys = sorted(
            normalized_marker_keys,
            key=lambda item: (BOOK_RANK.get(item[0], 999), item[1]),
        )
        if normalized_marker_keys != ordered_keys:
            errors.append(f"{relative}: 按書卷累積未依書卷、章次排序")
        if re.search(r"^###\s+.+?第\s*[一二三四五六七八九十廿百\d]+\s*章\s*$", text, re.M):
            errors.append(f"{relative}: 章次必須使用「### 書卷／#### 第N章」結構")
    elif status == "candidate":
        headings = re.findall(r"^##\s+(.+?)\s*$", text, re.M)
        errors.extend(
            check_h2(relative, headings, CANDIDATE_H2, CANDIDATE_REQUIRED_H2, "候選條目")
        )
    if re.search(r"（保護區）|根據目前已收集資料整理。", text):
        warnings.append(f"{relative}: 仍含模板占位文字")
    return errors, warnings


def validate_chapter(path):
    errors = []
    book = canonical_book_name(path.parent.name)
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
    allowed_headings = (
        ["本章知識節點", "本章整理"],
        ["相關地圖", "本章知識節點", "本章整理"],
    )
    if headings not in allowed_headings:
        errors.append(
            f"{path.relative_to(ROOT)}: H2 必須依序為"
            "（可選）相關地圖、本章知識節點、本章整理"
        )
    if "相關地圖" in headings:
        start = text.count("<!-- fhl-map-links:start -->")
        end = text.count("<!-- fhl-map-links:end -->")
        if start != 1 or end != 1:
            errors.append(
                f"{path.relative_to(ROOT)}: 相關地圖必須由單一 fhl-map-links 區塊管理"
            )
        map_position = text.find("## 相關地圖")
        first_rule = text.find("---")
        last_verse = max(
            (m.start() for m in re.finditer(r"^\d+\.\s", text[:first_rule], re.M)),
            default=-1,
        )
        if not (last_verse < map_position < first_rule):
            errors.append(
                f"{path.relative_to(ROOT)}: 相關地圖必須位於經文正文後、第一條分隔線前"
            )
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
    index, index_errors = make_index(entries, load_resolutions())
    errors.extend(index_errors)
    try:
        homonyms = load_homonyms()
        errors.extend(validate_homonyms(homonyms, index))
    except (OSError, ValueError, yaml.YAMLError) as exc:
        homonyms = {}
        errors.append(f"link_homonyms.yaml 無法解析：{exc}")

    changed = changed_link_files(base) if base else set()
    for path in sorted(LINK_FOLDER.rglob("*.md")):
        if EXCLUDE_PARTS & set(path.parts):
            continue
        relative = str(path.relative_to(ROOT)).replace("\\", "/")
        file_errors, file_warnings = validate_file(path, strict=relative in changed)
        errors.extend(file_errors)
        warnings.extend(file_warnings)
    for _, book_dir in existing_book_directories(ROOT):
        for chapter_path in sorted(book_dir.glob("第*章.md")):
            errors.extend(validate_chapter(chapter_path))
            text = chapter_path.read_text(encoding="utf-8")
            for label, line in ambiguous_wikilinks(text, homonyms):
                errors.append(
                    f"{chapter_path.relative_to(ROOT)}:{line}: "
                    f"歧義裸 WikiLink [[{label}]] 必須改用完整 target"
                )
    for path in sorted(LINK_FOLDER.rglob("*.md")):
        if EXCLUDE_PARTS & set(path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        for label, line in ambiguous_wikilinks(text, homonyms):
            errors.append(
                f"{path.relative_to(ROOT)}:{line}: "
                f"歧義裸 WikiLink [[{label}]] 必須改用完整 target"
            )
    if base:
        errors.extend(validate_protected_changes(base))
    return errors, warnings


def fix_hints_for(errors):
    """依 errors 命中的類別，組出對應的修復指引（只放實際出現的類別）。"""
    hints = []
    if any("歧義裸 WikiLink" in e for e in errors):
        hints.append((
            "歧義裸 WikiLink：同名詞可指向多個條目，[[裸名]] 無法判定",
            [
                "把該行 [[裸名]] 改成完整 target：[[完整條目名|行文用詞]]。",
                "同名候選見 _config/link_homonyms.yaml；章節內文一般由 run_chapter "
                "程式化標注，若是它漏標，修 link_candidates 的 surfaces 後重跑該章。",
            ],
        ))
    if any("保護區" in e for e in errors):
        hints.append((
            "既有正式條目的保護區被手動修改（累積資料只能經標記區寫入）",
            [
                "還原被改的保護區（git checkout 該檔），改走 B 類："
                "python util/link_updates.py prepare 【書名】 X 再 apply。",
            ],
        ))
    if any("link_homonyms.yaml 無法解析" in e for e in errors):
        hints.append((
            "_config/link_homonyms.yaml 格式錯誤",
            ["依錯誤修正 YAML（homonyms 需為 mapping），再重跑本驗證。"],
        ))
    # 其餘結構／解析錯誤（frontmatter、H2 順序、來源標記…）：render 產物理應合規，
    # 手改壞了才會出現——多屬程式或手動編輯的結構問題。
    structural = [
        e for e in errors
        if not any(k in e for k in ("歧義裸 WikiLink", "保護區", "link_homonyms.yaml 無法解析"))
    ]
    if structural:
        hints.append((
            "條目／章節結構或來源標記違規",
            [
                "看上方每條 ❌ 的檔名與說明修正對應檔；render 程式產物理應合規，"
                "出錯多為手動編輯破壞了模板／H2 順序／frontmatter。",
                "若該檔是本次 run_chapter 產生的，刪掉重跑該章即可恢復合規結構。",
            ],
        ))
    return hints


def main():
    console.utf8_stdio()
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
    if errors:
        remediation.print_fix_hints(fix_hints_for(errors))
    else:
        print("結論：PASS")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
