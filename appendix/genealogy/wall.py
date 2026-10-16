from __future__ import annotations

import re
from typing import Any, Callable


_WORD_RE = re.compile(r"^(.+)@(\d+)$")
_RING_KINDS = ("gate", "tower", "place", "names")


def _error(ref: Any, message: str) -> str:
    where = ref if isinstance(ref, str) and ref else "（缺少經節）"
    return f"城牆.yaml 經節：{where}：{message}"


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


def _reading_index(reading: dict) -> tuple[dict[str, dict], dict[str, str], dict[str, str], dict[str, int]]:
    segments: dict[str, dict] = {}
    verse_texts: dict[str, str] = {}
    ref_segments: dict[str, str] = {}
    ref_positions: dict[str, int] = {}
    for segment in reading.get("segments", []) if isinstance(reading, dict) else []:
        if not isinstance(segment, dict) or not isinstance(segment.get("id"), str):
            continue
        segment_id = segment["id"]
        segments[segment_id] = segment
        for chapter in segment.get("chapters", []):
            if not isinstance(chapter, dict):
                continue
            book, number = chapter.get("book"), chapter.get("n")
            if not isinstance(book, str) or not isinstance(number, int):
                continue
            for verse in chapter.get("verses", []):
                if not isinstance(verse, dict) or not isinstance(verse.get("v"), int):
                    continue
                ref = f"{book}{number}:{verse['v']}"
                if isinstance(verse.get("text"), str):
                    verse_texts[ref] = verse["text"]
                ref_segments[ref] = segment_id
                ref_positions[ref] = len(ref_positions)
    return segments, verse_texts, ref_segments, ref_positions


def _link_positions(links: Any, verse_texts: dict[str, str]) -> dict[str, list[tuple[int, int]]]:
    positions: dict[str, list[tuple[int, int]]] = {}
    for index, link in enumerate(links if isinstance(links, list) else []):
        if not isinstance(link, dict):
            continue
        ref, word = link.get("at"), link.get("word")
        match = _WORD_RE.fullmatch(word) if isinstance(word, str) else None
        if not isinstance(ref, str) or match is None:
            continue
        name, occurrence_text = match.groups()
        occurrences = _all_occurrences(verse_texts.get(ref, ""), name)
        occurrence = int(occurrence_text)
        if 1 <= occurrence <= len(occurrences):
            positions.setdefault(ref, []).append((occurrences[occurrence - 1], index))
    return positions


def build_wall(
    spec: dict,
    reading: dict,
    verse_text: Callable[[str], str | None],
    links: list[dict],
) -> tuple[dict | None, list[str]]:
    """驗證尼 3 城牆環線並建立 wall.json 資料。"""
    if not isinstance(spec, dict):
        return None, [_error(None, "根節點必須是物件。")]
    segment_id = spec.get("segment")
    segments, reading_texts, ref_segments, _ = _reading_index(reading)
    if not isinstance(segment_id, str) or not segment_id:
        return None, [_error(None, "segment 必須是非空字串。")]
    if segment_id not in segments:
        return None, [_error(None, f"segment「{segment_id}」不在 reading 的段落中。")]

    errors: list[str] = []
    refs = [ref for ref, owner in ref_segments.items() if owner == segment_id]
    positions = {ref: index for index, ref in enumerate(refs)}

    def text_for(ref: str) -> str:
        source = verse_text(ref)
        return source if isinstance(source, str) else reading_texts.get(ref, "")

    text_by_ref = {ref: text_for(ref) for ref in refs}
    link_positions = _link_positions(links, text_by_ref)
    narrative_value = spec.get("narrative", [])
    if not isinstance(narrative_value, list):
        errors.append(_error(None, "narrative 必須是清單。"))
        narrative_value = []
    narrative_refs = {ref for ref in narrative_value if isinstance(ref, str)}
    for ref in narrative_value:
        if not isinstance(ref, str) or ref not in positions:
            errors.append(_error(ref, "narrative 經節不在該段落裡。"))

    ring_value = spec.get("ring", [])
    if not isinstance(ring_value, list):
        errors.append(_error(None, "ring 必須是清單。"))
        ring_value = []
    output_ring: list[dict[str, Any]] = []
    covered = set(narrative_refs)
    name_cursor: dict[str, int] = {}
    last_position = -1
    back_items: list[tuple[int, dict[str, Any]]] = []
    feature_positions: dict[str, int] = {}

    for ring_index, item in enumerate(ring_value):
        if not isinstance(item, dict):
            errors.append(_error(None, "ring 每一項必須是物件。"))
            continue
        at = item.get("at")
        location = at if isinstance(at, str) else None
        if location is None:
            errors.append(_error(None, "ring 每一項都必須有 at。"))
        elif location not in positions:
            errors.append(_error(location, "at 不在城牆段落的經節裡。"))
        else:
            covered.add(location)
            current = positions[location]
            if current < last_position:
                errors.append(_error(location, "ring 的經節順序不可倒退。"))
            last_position = max(current, last_position)

        kind_keys = [kind for kind in _RING_KINDS if kind in item]
        if len(kind_keys) != 1:
            errors.append(_error(location, "每一項必須且只能指定 gate、tower、place 或 names 其中一種。"))
            continue
        kind = kind_keys[0]
        if location is None or location not in positions:
            continue
        source_text = text_by_ref.get(location, "")
        built_item: dict[str, Any] | None = None
        if kind == "names":
            names = item.get("names")
            if not isinstance(names, list) or not names:
                errors.append(_error(location, "names 必須是非空清單。"))
                continue
            cursor = name_cursor.get(location, 0)
            output_names: list[dict[str, Any]] = []
            for name in names:
                if not isinstance(name, str) or not name:
                    errors.append(_error(location, "names 裡的每個名字都必須是非空字串。"))
                    continue
                found = source_text.find(name, cursor)
                if found < 0:
                    errors.append(_error(location, f"名字「{name}」沒有依序出現在該節經文裡。"))
                    continue
                built_name: dict[str, Any] = {"t": name, "s": found}
                matching_links = [
                    link_index for position, link_index in link_positions.get(location, [])
                    if position == found
                ]
                if matching_links:
                    built_name["link"] = matching_links[0]
                output_names.append(built_name)
                cursor = found + len(name)
            name_cursor[location] = cursor
            if output_names:
                built_item = {"at": location, "kind": "part", "names": output_names}
        else:
            value = item.get(kind)
            if not isinstance(value, str) or not value:
                errors.append(_error(location, f"{kind} 必須是非空字串。"))
                continue
            found = source_text.find(value)
            if found < 0:
                errors.append(_error(location, f"{kind}「{value}」沒有逐字出現在該節經文裡。"))
                continue
            built_item = {"at": location, "kind": kind, "t": value, "s": found}

        if built_item is not None:
            output_ring.append(built_item)
            if kind in ("gate", "tower", "place"):
                feature_position = built_item["s"]
                previous = feature_positions.get(location)
                if previous is not None and feature_position < previous:
                    errors.append(_error(location, "gate、tower、place 彼此的經文位置順序不可倒退。"))
                feature_positions[location] = max(previous if previous is not None else feature_position, feature_position)
        if "back" in item:
            if not isinstance(item["back"], bool):
                errors.append(_error(location, "back 必須是布林值。"))
            elif item["back"]:
                back_items.append((ring_index, item))
                if built_item is not None:
                    built_item["back"] = True

    for ref in refs:
        if ref not in covered:
            errors.append(_error(ref, "該節必須有城牆項目或列在 narrative。"))
    for ref in narrative_refs:
        if any(isinstance(item, dict) and item.get("at") == ref for item in ring_value):
            errors.append(_error(ref, "narrative 經節不能同時有城牆項目。"))

    if not ring_value or not isinstance(ring_value[0], dict) or not isinstance(ring_value[0].get("gate"), str):
        errors.append(_error(None, "ring 第一項必須是 gate。"))
    if len(back_items) != 1:
        errors.append(_error(None, "ring 必須恰好有一項 back: true。"))
    elif back_items:
        back_index, back_item = back_items[0]
        first_gate = ring_value[0].get("gate") if ring_value and isinstance(ring_value[0], dict) else None
        back_gate = back_item.get("gate")
        if back_index != len(ring_value) - 1:
            errors.append(_error(back_item.get("at"), "back: true 必須是最後一項。"))
        if not isinstance(back_gate, str) or back_gate != first_gate:
            errors.append(_error(back_item.get("at"), "最後一項 back 必須是與起點同名的 gate。"))

    return {"segment": segment_id, "verses": refs, "ring": output_ring}, errors