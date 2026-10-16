from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable

try:
    from .tools.step_names import BOOK_SLUGS, load_chapter
    from .tools.tipnr import canonical_strong, load_english_names, load_tipnr
except ImportError:
    from tools.step_names import BOOK_SLUGS, load_chapter
    from tools.tipnr import canonical_strong, load_english_names, load_tipnr


_REF_RE = re.compile(r"^(.+?)(\d+):(\d+)$")
_WORD_RE = re.compile(r"^(.+)@(\d+)$")
_STRONG_RE = re.compile(r"^[HG]\d+[A-Za-z]?$")
_STRONG_PART_RE = re.compile(r"[HG]\d+[A-Za-z]?")
_COMMENTARY_PREFIXES = (
    "ccbiblestudy_CT_", "ccbiblestudy_GT_", "kingcomments_", "biblehub_study_",
)


def _normalize_strong(value: str) -> str:
    match = re.fullmatch(r"([HG])(\d+)([A-Za-z]?)", value)
    if match is None:
        return ""
    return f"{match.group(1)}{int(match.group(2))}{match.group(3)}"


def _letters(text: Any) -> str:
    """只留英文字母（小寫），比對 STEP gloss 與英文名用。"""
    return re.sub(r"[^a-z]", "", text.casefold()) if isinstance(text, str) else ""


def _strip_gloss_prefixes(gloss: Any) -> str:
    """移除 STEP gloss 開頭的 and/、of/ 等語法提示。"""
    text = gloss.strip() if isinstance(gloss, str) else ""
    return re.sub(r"^(?:[A-Za-z]+/)+", "", text, flags=re.IGNORECASE)


def step_strongs(ref: str) -> set[str] | None:
    """回傳 STEP 該節所有 Strong 編號；來源檔不存在時回傳 None。"""
    match = _REF_RE.fullmatch(ref) if isinstance(ref, str) else None
    if match is None:
        return None
    book, chapter_text, verse_text = match.groups()
    if book not in BOOK_SLUGS:
        return None
    try:
        words = load_chapter(book, int(chapter_text)).get(int(verse_text))
    except (OSError, ValueError):
        return None
    if words is None:
        return None
    result: set[str] = set()
    for word in words:
        raw = getattr(word, "strong", "")
        if not isinstance(raw, str):
            continue
        for strong in _STRONG_PART_RE.findall(raw):
            normalized = _normalize_strong(strong)
            if normalized:
                result.add(normalized)
    return result


def _error(name: str, ref: Any, message: str) -> str:
    location = ref if isinstance(ref, str) and ref else "（缺少經節）"
    return f"家族.yaml {name} {location}：{message}"


def _reading_index(reading: dict) -> tuple[
    dict[str, str], dict[str, str], set[tuple[str, int]]
]:
    ref_segments: dict[str, str] = {}
    reading_texts: dict[str, str] = {}
    chapters: set[tuple[str, int]] = set()
    for segment in reading.get("segments", []) if isinstance(reading, dict) else []:
        if not isinstance(segment, dict) or not isinstance(segment.get("id"), str):
            continue
        segment_id = segment["id"]
        for chapter in segment.get("chapters", []):
            if not isinstance(chapter, dict):
                continue
            book, number = chapter.get("book"), chapter.get("n")
            if not isinstance(book, str) or isinstance(number, bool) or not isinstance(number, int):
                continue
            chapters.add((book, number))
            for verse in chapter.get("verses", []):
                if not isinstance(verse, dict) or isinstance(verse.get("v"), bool) or not isinstance(verse.get("v"), int):
                    continue
                ref = f"{book}{number}:{verse['v']}"
                ref_segments[ref] = segment_id
                if isinstance(verse.get("text"), str):
                    reading_texts[ref] = verse["text"]
    return ref_segments, reading_texts, chapters


def _occurrence(text: str, name: str, index: int) -> int | None:
    cursor = 0
    for _ in range(index):
        found = text.find(name, cursor)
        if found < 0:
            return None
        cursor = found + 1
    return cursor - 1 if index > 0 else None


def _family_lines(roster: Any, wall: Any, ref: str) -> list[dict[str, Any]]:
    lines: list[dict[str, Any]] = []
    if isinstance(roster, dict):
        for roster_item in roster.get("rosters", []) if isinstance(roster.get("rosters"), list) else []:
            if not isinstance(roster_item, dict):
                continue
            for section in roster_item.get("sections", []) if isinstance(roster_item.get("sections"), list) else []:
                if not isinstance(section, dict):
                    continue
                for row in section.get("rows", []) if isinstance(section.get("rows"), list) else []:
                    if isinstance(row, dict) and row.get("at") == ref:
                        names = row.get("names", [])
                        lines.append({
                            "row": row,
                            "names": [name for name in names if isinstance(name, dict)] if isinstance(names, list) else [],
                            "label": row.get("label"),
                            "ls": row.get("ls"),
                        })
    if isinstance(wall, dict):
        for row in wall.get("ring", []) if isinstance(wall.get("ring"), list) else []:
            if isinstance(row, dict) and row.get("at") == ref:
                names = row.get("names", [])
                lines.append({
                    "row": row,
                    "names": [name for name in names if isinstance(name, dict)] if isinstance(names, list) else [],
                    "label": None,
                    "ls": None,
                })
    return lines


def _add_family(target: dict[str, Any], index: int) -> None:
    current = target.get("fam")
    if not isinstance(current, list):
        current = []
        target["fam"] = current
    if index not in current:
        current.append(index)


def build_families(
    spec: dict,
    reading: dict,
    roster: dict,
    wall: dict | None,
    verse_text: Callable[[str], str | None],
    step_strongs: Callable[[str], set[str] | None],
    check_basis: Callable[[list, str, Path], list[str]],
    root: Path,
) -> list[str]:
    """驗證家族軌跡並在名冊／城牆資料上標記家族序號。"""
    errors: list[str] = []
    if not isinstance(spec, dict):
        return ["家族.yaml：根節點必須是物件。"]
    family_specs = spec.get("families", [])
    if not isinstance(family_specs, list):
        return ["家族.yaml：families 必須是清單。"]

    ref_segments, reading_texts, reading_chapters = _reading_index(reading)
    try:
        tipnr_index = load_tipnr()
    except (OSError, ValueError) as exc:
        tipnr_index = None
        errors.append(f"家族.yaml：TIPNR 載入失敗：{exc}")
    try:
        english_names = load_english_names(
            root / "appendix" / "genealogy" / "亞當到耶穌" / "名字英文對照.tsv"
        )
    except OSError as exc:
        english_names = {}
        errors.append(f"家族.yaml：英文名字對照表載入失敗：{exc}")
    seen_places: set[tuple[str, str]] = set()
    output_families: list[dict[str, Any]] = []

    def basis_errors(items: Any, where: str) -> list[str]:
        if not callable(check_basis):
            return [f"{where}：basis 檢查器不可用。"]
        return check_basis(items, where, root)

    for family_index, family in enumerate(family_specs):
        if not isinstance(family, dict):
            errors.append(_error("（未命名）", None, "每個家族必須是物件。"))
            continue
        raw_name = family.get("name")
        name = raw_name.strip() if isinstance(raw_name, str) else ""
        display_name = name or "（未命名）"
        if not name:
            errors.append(_error(display_name, None, "name 必須是非空字串。"))

        raw_forms = family.get("forms")
        forms = (
            {form.strip() for form in raw_forms if isinstance(form, str) and form.strip()}
            if isinstance(raw_forms, list) else set()
        )
        if not forms or len(forms) != len(raw_forms if isinstance(raw_forms, list) else []):
            errors.append(_error(display_name, None, "forms 必須是包含非空名字的清單。"))
        tipnr_name = family.get("tipnr")
        if not isinstance(tipnr_name, str) or not tipnr_name.strip():
            errors.append(_error(display_name, None, "tipnr 必須是非空的 TIPNR UniqueName。"))
            tipnr_name = ""
        else:
            tipnr_name = tipnr_name.strip()

        family_strong = family.get("strong")
        if not isinstance(family_strong, str) or not _STRONG_RE.fullmatch(family_strong):
            errors.append(_error(display_name, None, "strong 格式必須是 H/G 編號，可帶一個字母後綴。"))
            family_strong = ""
        family_normalized = _normalize_strong(family_strong) if family_strong else ""

        family_basis = family.get("basis")
        errors.extend(basis_errors(family_basis, f"家族.yaml {display_name} （整體）basis"))

        places = family.get("places")
        if not isinstance(places, list):
            errors.append(_error(display_name, None, "places 必須是清單。"))
            places = []
        if len(places) < 2:
            errors.append(_error(display_name, None, "places 至少要有兩處。"))

        output_places: list[dict[str, Any]] = []
        for place in places:
            if not isinstance(place, dict):
                errors.append(_error(display_name, None, "每一處必須是物件。"))
                continue
            at = place.get("at")
            location = _error(display_name, at, "")
            if not isinstance(at, str) or not at:
                errors.append(_error(display_name, at, "at 必須是非空經節。"))
                continue
            word = place.get("word")
            word_match = _WORD_RE.fullmatch(word) if isinstance(word, str) else None
            if word_match is None or int(word_match.group(2)) < 1 or not word_match.group(1).strip():
                errors.append(_error(display_name, at, "word 必須使用「名字@n」格式，n 從 1 開始。"))
                word_name, occurrence = "", 0
            else:
                word_name, occurrence_text = word_match.groups()
                occurrence = int(occurrence_text)
                if word_name.strip() not in forms:
                    errors.append(_error(display_name, at, f"word 名字「{word_name.strip()}」不在 forms 中。"))
            place_key = (at, word if isinstance(word, str) else "")
            if place_key in seen_places:
                errors.append(_error(display_name, at, f"位置「{word}」已在另一個家族或本家族重複。"))
            seen_places.add(place_key)

            place_strong = place.get("strong", family_strong)
            if not isinstance(place_strong, str) or not _STRONG_RE.fullmatch(place_strong):
                errors.append(_error(display_name, at, "place.strong 格式無效。"))
                place_strong = ""
            normalized_place_strong = _normalize_strong(place_strong) if place_strong else ""
            is_override = "strong" in place and bool(place_strong) and normalized_place_strong != family_normalized
            place_basis = place.get("basis")
            place_basis_problems: list[str] = []
            has_commentary_basis = False
            if "basis" in place:
                place_basis_problems = basis_errors(place_basis, f"家族.yaml {display_name} {at} basis")
                errors.extend(place_basis_problems)
                has_commentary_basis = (
                    isinstance(place_basis, list)
                    and any(
                        isinstance(item, dict)
                        and isinstance(item.get("source"), str)
                        and item["source"].startswith(_COMMENTARY_PREFIXES)
                        for item in place_basis
                    )
                )
            if is_override:
                if "basis" not in place:
                    errors.append(_error(display_name, at, "place.strong 和家族 strong 不同時必須有註釋 basis。"))
                elif place_basis_problems or not has_commentary_basis:
                    errors.append(_error(display_name, at, "place.strong 不同時，basis 必須含通過檢查的註釋來源。"))

            verse = verse_text(at)
            reading_text = reading_texts.get(at)
            source_text = reading_text if isinstance(reading_text, str) else verse
            name_position: int | None = None
            if not isinstance(source_text, str):
                errors.append(_error(display_name, at, "找不到該節經文。"))
            elif word_match is not None:
                name_position = _occurrence(source_text, word_name, occurrence)
                if name_position is None:
                    errors.append(_error(display_name, at, f"名字「{word_name}」第 {occurrence} 次沒有出現在該節經文裡。"))

            active = at in ref_segments
            if not active:
                errors.append(_error(display_name, at, "at 不在 reading 的任何段落經節裡。"))

            step_codes = step_strongs(at)
            if step_codes is None:
                errors.append(_error(display_name, at, "找不到該節 STEP Strong 資料。"))
            elif normalized_place_strong and normalized_place_strong not in {
                _normalize_strong(code) for code in step_codes if isinstance(code, str)
            }:
                errors.append(_error(display_name, at, f"STEP 該節沒有編號 {place_strong}。"))

            if normalized_place_strong:
                tipnr_people = (
                    tipnr_index.by_dstrong.get(canonical_strong(place_strong), [])
                    if tipnr_index is not None else []
                )
                if not any(person.unique_name == tipnr_name for person in tipnr_people):
                    errors.append(_error(display_name, at, "TIPNR 不是同一條。"))

            # 名字綁定原文：中文第 n 次出現，對到 STEP 這一節裡英文名相符的第 n 個詞；那個詞的編號必須是這一處的編號
            mapped_english = english_names.get(word_name.strip(), set()) if word_match is not None else set()
            if word_match is not None and not mapped_english:
                errors.append(_error(display_name, at, f"名字英文對照表沒有「{word_name.strip()}」，無法核對原文。"))
            elif mapped_english and normalized_place_strong and isinstance(source_text, str):
                ref_match = _REF_RE.fullmatch(at)
                words = None
                if ref_match and ref_match.group(1) in BOOK_SLUGS:
                    try:
                        words = load_chapter(ref_match.group(1), int(ref_match.group(2))).get(int(ref_match.group(3)), [])
                    except (OSError, ValueError):
                        words = None
                targets = {_letters(name) for name in mapped_english if _letters(name)}

                def matches_name(step_word: Any) -> bool:
                    gloss = _letters(_strip_gloss_prefixes(getattr(step_word, "gloss", "")))
                    # 「Pahath-」「Moab」分成兩個詞：英文名以這個詞開頭就算（至少三個字母）
                    return len(gloss) >= 3 and any(target == gloss or target.startswith(gloss) for target in targets)
                named = [step_word for step_word in words or [] if matches_name(step_word)]
                chinese_count = source_text.count(word_name)
                if words is None:
                    errors.append(_error(display_name, at, "找不到該節 STEP 詞表。"))
                elif len(named) != chinese_count:
                    errors.append(_error(display_name, at, f"「{word_name}」中文出現 {chinese_count} 次，STEP 英文名相符的詞有 {len(named)} 個，對不起來。"))
                elif 1 <= occurrence <= len(named):
                    raw_codes = getattr(named[occurrence - 1], "strong", "")
                    codes = {canonical_strong(code) for code in re.findall(r"[HG]\d+[A-Za-z]*", raw_codes)} if isinstance(raw_codes, str) else set()
                    if canonical_strong(place_strong) not in codes:
                        errors.append(_error(display_name, at, f"第 {occurrence} 個「{word_name}」在 STEP 不是 {place_strong}。"))

            attached_line: dict[str, Any] | None = None
            if active and name_position is not None:
                lines = _family_lines(roster, wall, at)
                for line in lines:
                    label, label_start = line["label"], line["ls"]
                    if (
                        isinstance(label, str)
                        and isinstance(label_start, int)
                        and label_start <= name_position < label_start + len(label)
                    ):
                        attached_line = line
                        break
                target_name: dict[str, Any] | None = None
                if attached_line is None:
                    for line in lines:
                        target_name = next(
                            (item for item in line["names"] if item.get("s") == name_position),
                            None,
                        )
                        if target_name is not None:
                            attached_line = line
                            break
                if attached_line is None:
                    ordered_names = sorted(
                        (
                            (item.get("s"), line, item)
                            for line in lines
                            for item in line["names"]
                            if isinstance(item.get("s"), int) and item["s"] >= name_position
                        ),
                        key=lambda item: item[0],
                    )
                    if ordered_names:
                        _, attached_line, target_name = ordered_names[0]
                if attached_line is None and len(lines) == 1:
                    attached_line = lines[0]
                if attached_line is None:
                    errors.append(_error(display_name, at, "不在名冊或城牆上。"))
                else:
                    target = target_name if target_name is not None else attached_line["row"]
                    _add_family(target, family_index)

            if active and at in ref_segments:
                place_output: dict[str, Any] = {"at": at, "seg": ref_segments[at]}
                if attached_line is not None:
                    row = attached_line["row"]
                    if "count" in row and isinstance(row.get("count"), int) and not isinstance(row.get("count"), bool):
                        place_output["count"] = row["count"]
                        place_output["unit"] = row.get("unit", "")
                output_places.append(place_output)

        output_families.append({"name": name, "places": output_places})

    family_rows = [{"name": item["name"], "places": item["places"]} for item in output_families]
    if isinstance(roster, dict):
        roster["families"] = family_rows
    if isinstance(wall, dict):
        wall["families"] = family_rows
    return errors