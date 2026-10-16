from __future__ import annotations

import re
from typing import Any, Callable


_DIGITS = {
    "零": 0, "〇": 0, "一": 1, "二": 2, "兩": 2,
    "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9,
}
_NUMERAL_CHARS = "零〇一二三四五六七八九十百千萬兩"
_COUNT_RE = re.compile(r"([" + re.escape(_NUMERAL_CHARS) + r"]+)(達利克|彌拿|名|匹|隻|件|個)")
_REF_RE = re.compile(r"^(.+?)(\d+):(\d+)$")


def _format_under_10000(value: int) -> str:
    if value == 0:
        return "零"
    result: list[str] = []
    zero_pending = False
    started = False
    for unit, unit_text in ((1000, "千"), (100, "百"), (10, "十"), (1, "")):
        digit, value = divmod(value, unit)
        if digit:
            if zero_pending and started:
                result.append("零")
            if not (unit == 10 and digit == 1 and not started):
                result.append("零一二三四五六七八九"[digit])
            result.append(unit_text)
            started = True
            zero_pending = False
        elif started and value:
            zero_pending = True
    return "".join(result)


def _format_chinese_number(value: int) -> str:
    if value < 10000:
        return _format_under_10000(value)
    high, low = divmod(value, 10000)
    result = _format_under_10000(high) + "萬"
    if low:
        if low < 1000:
            result += "零"
        low_text = _format_under_10000(low)
        if 10 <= low < 20:
            low_text = "一" + low_text
        result += low_text
    return result


def _parse_under_10000(text: str) -> int | None:
    if not text:
        return None
    total = 0
    digit: int | None = None
    last_unit = 10000
    seen_unit = False
    for index, char in enumerate(text):
        if char in _DIGITS:
            value = _DIGITS[char]
            if value == 0:
                if not seen_unit or digit is not None or index == len(text) - 1:
                    return None
                if text[index + 1] in "十百千":
                    return None
                digit = 0
            else:
                if digit not in (None, 0):
                    return None
                digit = value
        elif char in "十百千":
            unit = {"十": 10, "百": 100, "千": 1000}[char]
            if unit >= last_unit or digit == 0:
                return None
            if digit is None:
                if unit != 10 or seen_unit:
                    return None
                value = 1
            else:
                value = digit
            total += value * unit
            digit = None
            last_unit = unit
            seen_unit = True
        else:
            return None
    if digit == 0:
        return None
    if digit is not None:
        total += digit
    return total if seen_unit or digit is not None else None


def chinese_number(text: str) -> int | None:
    """將常見的中文整數轉成阿拉伯數字；不合法的寫法回傳 None。"""
    if not isinstance(text, str) or not text:
        return None
    normalized = text.replace("兩", "二").replace("〇", "零")
    if any(char not in "零一二三四五六七八九十百千萬" for char in normalized):
        return None
    if normalized == "零":
        return 0
    if normalized.count("萬") > 1:
        return None
    if "萬" in normalized:
        high_text, low_text = normalized.split("萬", 1)
        high = _parse_under_10000(high_text)
        if high is None or high == 0:
            return None
        if low_text.startswith("零"):
            low_text = low_text[1:]
            if not low_text:
                return None
        low = _parse_under_10000(low_text) if low_text else 0
        if low is None:
            return None
        value = high * 10000 + low
    else:
        value = _parse_under_10000(normalized)
        if value is None:
            return None
    return value if _format_chinese_number(value) == normalized else None


def _all_occurrences(text: str, needle: str) -> list[int]:
    positions: list[int] = []
    start = 0
    while needle:
        position = text.find(needle, start)
        if position < 0:
            break
        positions.append(position)
        start = position + 1
    return positions


def _find_name(text: str, name: str, start: int) -> int:
    before_delimiters = "、，；：。()（）「」『』"
    after_delimiters = "、，；：。()（）「」『』"
    before_phrases = ("同著", "從", "是", "和", "並", "與", "及")
    after_phrases = ("的", "回", "並", "共", "上來")
    for relative in _all_occurrences(text[start:], name):
        position = start + relative
        prefix = text[:position]
        suffix = text[position + len(name):]
        left_ok = (
            position == 0
            or text[position - 1] in before_delimiters
            or any(prefix.endswith(phrase) for phrase in before_phrases)
        )
        right_ok = (
            not suffix
            or suffix[0] in after_delimiters
            or any(suffix.startswith(phrase) for phrase in after_phrases)
        )
        if left_ok and right_ok:
            return position
    return -1


def _location(segment: str, ref: Any) -> str:
    return f"名冊.yaml {segment} {ref if ref else '（缺少經節）'}："


def build_roster(
    spec: dict,
    reading: dict,
    verse_text: Callable[[str], str | None],
    links: list[dict],
) -> tuple[dict, list[str]]:
    """驗證名冊並建置網站端 roster.json 的資料。"""
    errors: list[str] = []
    segments = {
        item.get("id"): item
        for item in reading.get("segments", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    verse_texts: dict[str, str] = {}
    for item in reading.get("segments", []):
        if not isinstance(item, dict):
            continue
        for chapter in item.get("chapters", []):
            if not isinstance(chapter, dict):
                continue
            book, number = chapter.get("book"), chapter.get("n")
            if not isinstance(book, str) or not isinstance(number, int):
                continue
            for verse in chapter.get("verses", []):
                if isinstance(verse, dict) and isinstance(verse.get("v"), int) and isinstance(verse.get("text"), str):
                    verse_texts[f"{book}{number}:{verse['v']}"] = verse["text"]

    refs_by_segment: dict[str, list[str]] = {}
    positions_by_segment: dict[str, dict[str, int]] = {}
    for segment_id, item in segments.items():
        refs: list[str] = []
        for chapter in item.get("chapters", []):
            if not isinstance(chapter, dict):
                continue
            book, number = chapter.get("book"), chapter.get("n")
            if isinstance(book, str) and isinstance(number, int):
                refs.extend(
                    f"{book}{number}:{verse['v']}"
                    for verse in chapter.get("verses", [])
                    if isinstance(verse, dict) and isinstance(verse.get("v"), int)
                )
        refs_by_segment[segment_id] = refs
        positions_by_segment[segment_id] = {ref: i for i, ref in enumerate(refs)}

    link_positions: dict[str, list[tuple[int, int]]] = {}
    for index, link in enumerate(links if isinstance(links, list) else []):
        if not isinstance(link, dict):
            continue
        ref, word = link.get("at"), link.get("word")
        match = re.fullmatch(r"(.+)@(\d+)", word) if isinstance(word, str) else None
        if not isinstance(ref, str) or not match:
            continue
        name, occurrence_text = match.groups()
        occurrences = _all_occurrences(verse_texts.get(ref, ""), name)
        occurrence = int(occurrence_text)
        if 1 <= occurrence <= len(occurrences):
            link_positions.setdefault(ref, []).append((occurrences[occurrence - 1], index))

    roster_specs = spec.get("rosters", []) if isinstance(spec, dict) else []
    if not isinstance(roster_specs, list):
        return {"rosters": []}, ["名冊.yaml：rosters 必須是清單。"]

    output_rosters: list[dict[str, Any]] = []
    work_rosters: list[dict[str, Any]] = []
    for roster in roster_specs:
        if not isinstance(roster, dict):
            errors.append("名冊.yaml：每份名冊必須是物件。")
            continue
        segment_id = roster.get("segment")
        if not isinstance(segment_id, str):
            segment_id = "（缺少段落）"
        if segment_id not in segments:
            errors.append(f"名冊.yaml {segment_id}：segment 不在 reading 的段落中。")
        refs = refs_by_segment.get(segment_id, [])
        positions = positions_by_segment.get(segment_id, {})
        prefix = f"名冊.yaml {segment_id}"

        narrative_value = roster.get("narrative", [])
        narrative = narrative_value if isinstance(narrative_value, list) else []
        if not isinstance(narrative_value, list):
            errors.append(f"{prefix}：narrative 必須是清單。")
        narrative_refs = {ref for ref in narrative if isinstance(ref, str)}
        for ref in narrative:
            if not isinstance(ref, str) or ref not in positions:
                errors.append(f"{_location(segment_id, ref)}narrative 經節不在該段落裡。")

        built: dict[str, Any] = {
            "segment": segment_id,
            "title": roster.get("title", ""),
            "verses": list(refs),
            "max": 0,
            "sections": [],
        }
        quote = roster.get("quote")
        if isinstance(quote, dict):
            ref, text = quote.get("ref"), quote.get("text")
            if not isinstance(ref, str) or not isinstance(text, str):
                errors.append(f"{prefix}：quote 必須包含 ref 與 text。")
            else:
                source = verse_text(ref)
                if source is None or text not in source:
                    errors.append(f"{_location(segment_id, ref)}quote.text 不是該節經文的逐字片段。")
                built["quote"] = {"ref": ref, "text": text}
        elif quote is not None:
            errors.append(f"{prefix}：quote 必須是物件。")

        covered = set(narrative_refs)
        rows: list[dict[str, Any]] = []
        last_position = -1
        label_cursor: dict[str, int] = {}
        name_cursor: dict[str, int] = {}
        sections = roster.get("sections", [])
        if not isinstance(sections, list):
            errors.append(f"{prefix}：sections 必須是清單。")
            sections = []

        for section in sections:
            if not isinstance(section, dict):
                errors.append(f"{prefix}：每個 section 必須是物件。")
                continue
            bars = section.get("bars", True)
            lost = section.get("lost", False)
            bars = bars if isinstance(bars, bool) else True
            lost = lost if isinstance(lost, bool) else False
            out_section = {
                "title": section.get("title", ""),
                "lost": lost,
                "bars": bars,
                "rows": [],
            }
            built["sections"].append(out_section)
            section_rows = section.get("rows", [])
            if not isinstance(section_rows, list):
                errors.append(f"{prefix} {section.get('title', '')}：rows 必須是清單。")
                continue

            for row in section_rows:
                if not isinstance(row, dict):
                    errors.append(f"{prefix}：每一行必須是物件。")
                    continue
                at = row.get("at")
                at = at if isinstance(at, str) else None
                location = _location(segment_id, at)
                out: dict[str, Any] = {}
                if at is None:
                    errors.append(f"{_location(segment_id, None)}每一行都必須有 at。")
                else:
                    out["at"] = at
                    if at not in positions:
                        errors.append(f"{location}at 不在這個 reading 段落裡。")
                    else:
                        covered.add(at)
                        current = positions[at]
                        if current < last_position:
                            errors.append(f"{location}所有行的經節順序不可倒退。")
                        last_position = max(current, last_position)
                text = verse_texts.get(at or "", "")

                label = row.get("label")
                label_pos: int | None = None
                if label is not None:
                    if not isinstance(label, str) or not label:
                        errors.append(f"{location}label 必須是非空字串。")
                    elif _COUNT_RE.search(label):
                        # 「馬七百三十六匹」這種把數字吞進 label 的寫法，會讓 count 對到下一項的數字
                        errors.append(f"{location}label「{label}」不可包含數字與量詞。")
                    else:
                        found = text.find(label, label_cursor.get(at or "", 0))
                        if found < 0:
                            errors.append(f"{location}label「{label}」沒有依序出現在經文裡。")
                        else:
                            label_pos = found
                            label_cursor[at or ""] = found + len(label)
                            out["label"], out["ls"] = label, found

                found_names: list[dict[str, Any]] = []
                names = row.get("names")
                last_name_end: int | None = None
                if names is not None:
                    if not isinstance(names, list):
                        errors.append(f"{location}names 必須是清單。")
                    else:
                        cursor = name_cursor.get(at or "", 0)
                        for name in names:
                            if not isinstance(name, str) or not name:
                                errors.append(f"{location}names 裡的每個名字都必須是非空字串。")
                                continue
                            found = _find_name(text, name, cursor)
                            if found < 0:
                                errors.append(f"{location}名字「{name}」沒有依序出現在經文裡。")
                                continue
                            found_names.append({"t": name, "s": found})
                            cursor = found + len(name)
                            last_name_end = cursor
                        name_cursor[at or ""] = cursor
                        if found_names:
                            out["names"] = found_names

                row_quote = row.get("quote")
                quote_pos: int | None = None
                if row_quote is not None:
                    if not isinstance(row_quote, str) or not row_quote:
                        errors.append(f"{location}quote 必須是非空字串。")
                    else:
                        quote_pos = text.find(row_quote)
                        if quote_pos < 0:
                            errors.append(f"{location}quote 不是該節經文的逐字片段。")
                        else:
                            out["quote"] = {"t": row_quote, "s": quote_pos}

                who = row.get("who")
                who_pos: int | None = None
                if who is not None:
                    if not isinstance(who, str) or not who:
                        errors.append(f"{location}who 必須是非空字串。")
                    else:
                        anchors = [p for p in (quote_pos, found_names[0]["s"] if found_names else None) if p is not None]
                        anchor = label_pos if label_pos is not None else min(anchors, default=len(text) + 1)
                        who_pos = next((p for p in _all_occurrences(text, who) if p < anchor), None)
                        if who_pos is None:
                            errors.append(f"{location}who「{who}」沒有出現在 label 之前。")
                        else:
                            out["who"] = who

                has_anchor = (
                    isinstance(row.get("label"), str) and bool(row.get("label"))
                ) or (
                    isinstance(row.get("names"), list) and bool(row.get("names"))
                ) or (
                    isinstance(row.get("quote"), str) and bool(row.get("quote"))
                )
                if not has_anchor:
                    errors.append(f"{location}每一行至少要有 label、names 或 quote。")
                for key in ("total", "big"):
                    if key in row:
                        out[key] = row[key]
                if ("total" in row or "big" in row) and "count" not in row:
                    errors.append(f"{location}total 或 big 的行必須有 count。")

                unit = row.get("unit", "名")
                count = row.get("count")
                if "count" in row:
                    if isinstance(count, bool) or not isinstance(count, int):
                        errors.append(f"{location}count 必須是整數。")
                    else:
                        out["count"], out["unit"] = count, unit
                        if unit not in ("名", "匹", "隻", "達利克", "彌拿", "件", "個"):
                            errors.append(f"{location}unit 不是支援的量詞。")
                        if last_name_end is not None:
                            start = last_name_end
                        elif label_pos is not None and isinstance(label, str):
                            start = label_pos + len(label)
                        elif isinstance(label, str):
                            start = label_cursor.get(at or "", 0)
                        else:
                            start = 0
                        quantity = next(iter(_COUNT_RE.finditer(text, start)), None)
                        if quantity is None:
                            errors.append(f"{location}label 或名字之後找不到中文數字與量詞。")
                        else:
                            parsed = chinese_number(quantity.group(1))
                            if parsed is None:
                                errors.append(f"{location}「{quantity.group(1)}」不是合法中文數字。")
                            elif parsed != count:
                                errors.append(f"{location}經文數字是 {parsed}，與 count {count} 不同。")
                            if quantity.group(2) != unit:
                                errors.append(f"{location}經文量詞是「{quantity.group(2)}」，與 unit「{unit}」不同。")
                            out["n"] = quantity.start(1)

                bar = bool(
                    bars and "count" in row and "total" not in row
                    and "big" not in row and unit == "名"
                )
                out["bar"] = bar
                if bar and isinstance(count, int) and not isinstance(count, bool):
                    built["max"] = max(built["max"], count)

                anchors = [
                    p for p in (
                        label_pos,
                        found_names[0]["s"] if found_names else None,
                        quote_pos,
                        who_pos,
                    ) if p is not None
                ]
                if anchors:
                    out["s"] = min(anchors)
                rows.append({
                    "source": row,
                    "output": out,
                    "at": at,
                    "row_index": 0,
                    "label_pos": label_pos,
                })
                out_section["rows"].append(out)

        for ref in refs:
            if ref not in covered:
                errors.append(f"{_location(segment_id, ref)}該節必須有名冊行或列在 narrative。")
        for ref in narrative_refs:
            if any(item["at"] == ref for item in rows):
                errors.append(f"{_location(segment_id, ref)}narrative 經節不能同時有名冊行。")

        rows_by_ref: dict[str, list[dict[str, Any]]] = {}
        for item in rows:
            if isinstance(item["at"], str):
                rows_by_ref.setdefault(item["at"], []).append(item)
        # 一行的數字必須是它自己那一項的：label 和它的數字中間不可夾著同一節別一行的 label
        for same_verse_rows in rows_by_ref.values():
            for item in same_verse_rows:
                start, number = item["label_pos"], item["output"].get("n")
                if start is None or number is None:
                    continue
                for other in same_verse_rows:
                    if other is not item and other["label_pos"] is not None and start < other["label_pos"] < number:
                        errors.append(f"{_location(segment_id, item['at'])}label「{item['source'].get('label')}」的數字跨過了"
                                      f"「{other['source'].get('label')}」，對到的是別一項的數字。")
        for same_verse_rows in rows_by_ref.values():
            for i, item in enumerate(same_verse_rows):
                item["row_index"] = i

        for item in rows:
            ref = item["at"]
            if not isinstance(ref, str):
                continue
            out = item["output"]
            indices: list[int] = []
            label_pos = item["label_pos"]
            label = item["source"].get("label")
            if isinstance(label, str) and label_pos is not None:
                end = label_pos + len(label)
                indices.extend(
                    index for position, index in link_positions.get(ref, [])
                    if label_pos <= position < end
                )
            for name in out.get("names", []):
                matching = [
                    index for position, index in link_positions.get(ref, [])
                    if position == name["s"]
                ]
                if matching:
                    name["link"] = matching[0]
                    indices.extend(matching)
            if indices:
                out["links"] = list(dict.fromkeys(indices))

        output_rosters.append(built)
        work_rosters.append({
            "segment": segment_id,
            "rows": rows,
            "rows_by_ref": rows_by_ref,
        })

    for current in work_rosters:
        for item in current["rows"]:
            par = item["source"].get("par")
            if par is None:
                continue
            location = _location(current["segment"], item["at"])
            range_match = re.fullmatch(r"(.+?)(\d+):(\d+)-(\d+)", par) if isinstance(par, str) else None
            if range_match:
                book, chapter, first, last = range_match.groups()
                first, last = int(first), int(last)
                if first > last:
                    errors.append(f"{location}par 範圍順序錯誤。")
                    continue
                par_refs = [f"{book}{chapter}:{verse}" for verse in range(first, last + 1)]
            elif isinstance(par, str):
                par_refs = [par]
            else:
                errors.append(f"{location}par 必須是經節或同章範圍。")
                continue

            other = next((
                candidate for candidate in work_rosters
                if candidate["segment"] != current["segment"]
                and all(ref in positions_by_segment.get(candidate["segment"], {}) for ref in par_refs)
            ), None)
            if other is None:
                errors.append(f"{location}par 必須指向另一份名冊段落的經節。")
                continue
            if range_match:
                item["output"]["differs"] = True
                continue
            comparison = other["rows_by_ref"].get(par_refs[0], [])
            index = item["row_index"]
            if index >= len(comparison):
                item["output"]["differs"] = True
                continue
            paired = comparison[index]["source"]
            source = item["source"]
            # 「拉瑪人和迦巴人」對「拉瑪人、迦巴人」、「耶書亞家，耶大雅」對「耶書亞家耶大雅」只是連接字不同，不算寫法不同
            def bare(value: Any) -> Any:
                return re.sub(r"[，、和]", "", value) if isinstance(value, str) else value
            if (
                bare(source.get("label")) != bare(paired.get("label"))
                or source.get("count") != paired.get("count")
                or source.get("names", []) != paired.get("names", [])
            ):
                item["output"]["differs"] = True

    return {"rosters": output_rosters}, errors
