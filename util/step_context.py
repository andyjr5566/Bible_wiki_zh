#!/usr/bin/env python3
"""Deterministic validation and compact prompt/query context for STEP TXT.

The formal source remains ``raw_data/stepbible_*.txt``.  This module parses
that complete renderer-owned format, validates it as structured data, and
projects only task-relevant occurrences plus a deduplicated Extended-Strong
lexicon.  It never downloads data and never queries another chapter.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

try:
    from . import extract_stepbible
    from .book_paths import book_directory, canonical_book_name
except ImportError:
    import extract_stepbible
    from book_paths import book_directory, canonical_book_name


ROOT = Path(__file__).resolve().parent.parent
_DIGIT_TRANSLATION = str.maketrans("０１２３４５６７８９", "0123456789")
_HEBREW_RE = re.compile(r"[\u0590-\u05ff\ufb1d-\ufb4f]")
_GREEK_RE = re.compile(r"[\u0370-\u03ff\u1f00-\u1fff]")

DEFAULT_CANDIDATE_MAX = 20
HARD_CANDIDATE_MAX = 40
DEFAULT_OCCURRENCE_MAX = 20
HARD_OCCURRENCE_MAX = 50
DEFAULT_NEARBY_WINDOW = 5
HARD_NEARBY_WINDOW = 10
DEFAULT_STEP_PROMPT_CHAR_BUDGET = 7000


class StepValidationError(ValueError):
    """A formal STEP source exists but fails deterministic validation."""


@dataclass(frozen=True)
class VerseSelection:
    verses: tuple[int, ...]
    mode: str
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class StepProjection:
    text: str
    raw_chars: int
    raw_bytes: int
    projected_chars: int
    projected_bytes: int
    occurrence_count: int
    lexicon_count: int
    selected_verses: tuple[int, ...]


@dataclass(frozen=True)
class StepCandidate:
    base_strong: str
    exact_strongs: tuple[str, ...]
    headword: str
    transliteration: str
    short_gloss: str
    occurrences: tuple[dict, ...]
    priority: str  # "HIGH", "MEDIUM", "LOW"
    signals: tuple[str, ...]


@dataclass(frozen=True)
class StepEvidence:
    text: str
    candidate_count: int
    selected_count: int
    truncated: bool
    total_chars: int


def _normalize_verse_syntax(value: str) -> str:
    return (
        value.translate(_DIGIT_TRANSLATION)
        .replace("，", ",")
        .replace("、", ",")
        .replace("；", ",")
        .replace(";", ",")
        .replace("–", "-")
        .replace("—", "-")
        .replace("－", "-")
        .replace("～", "-")
        .replace("~", "-")
        .replace("至", "-")
        .replace("到", "-")
    )


def parse_verse_spec(value: str) -> set[int]:
    """Parse ``1,3-5``-style verse syntax with common Chinese punctuation."""
    normalized = _normalize_verse_syntax(value)
    verses: set[int] = set()
    for token in normalized.split(","):
        token = token.strip()
        if not token:
            continue
        if "-" in token:
            pieces = [piece.strip() for piece in token.split("-")]
            if len(pieces) != 2 or not all(piece.isdigit() for piece in pieces):
                raise ValueError(f"無法解析節範圍：{token}")
            start, end = map(int, pieces)
            if start < 1 or end < start:
                raise ValueError(f"節範圍不合法：{token}")
            verses.update(range(start, end + 1))
        elif token.isdigit() and int(token) >= 1:
            verses.add(int(token))
        else:
            raise ValueError(f"無法解析節號：{token}")
    if not verses:
        raise ValueError("節範圍不可為空")
    return verses


def _surface_verses(entry: dict) -> set[int]:
    verses: set[int] = set()
    for surface in entry.get("surfaces") or []:
        if not isinstance(surface, dict):
            continue
        for verse in surface.get("verses") or []:
            try:
                number = int(verse)
            except (TypeError, ValueError):
                continue
            if number >= 1:
                verses.add(number)
    return verses


def _evidence_verses(evidence: str) -> tuple[set[int], list[str], bool]:
    """Extract current-chapter verse expressions from the evidence lead clause."""
    evidence = str(evidence or "")
    if "全章" in evidence:
        return set(), [], True
    # Resolver evidence convention puts current-chapter verses before the first
    # semicolon; restricting parsing to that clause avoids interpreting cross-
    # references such as 詩33:6 later in the prose as this chapter's verses.
    lead = re.split(r"[；;]", evidence, maxsplit=1)[0]
    lead = lead.translate(_DIGIT_TRANSLATION)
    matches = re.findall(r"([0-9][0-9\s、,，\-–—－至到~～]*)節", lead)
    verses: set[int] = set()
    warnings: list[str] = []
    for expression in matches:
        try:
            verses.update(parse_verse_spec(expression))
        except ValueError as exc:
            warnings.append(str(exc))
    return verses, warnings, False


def select_candidate_verses(
    batch: Iterable[dict], available_verses: Iterable[int]
) -> VerseSelection:
    """Select M3 STEP verses from batch evidence/surfaces with fail-small policy."""
    available = set(int(verse) for verse in available_verses)
    selected: set[int] = set()
    warnings: list[str] = []
    full_chapter = False
    for entry in batch:
        selected.update(_surface_verses(entry))
        parsed, parse_warnings, requested_full = _evidence_verses(entry.get("evidence", ""))
        selected.update(parsed)
        warnings.extend(f"{entry.get('name', 'candidate')}：{item}" for item in parse_warnings)
        full_chapter = full_chapter or requested_full
    if full_chapter:
        return VerseSelection(tuple(sorted(available)), "full-chapter-evidence", tuple(warnings))
    outside = sorted(selected - available)
    if outside:
        warnings.append(f"evidence 節號超出 STEP source：{outside}")
    selected &= available
    if selected:
        return VerseSelection(tuple(sorted(selected)), "targeted", tuple(warnings))
    warnings.append(
        "evidence／surfaces 無法解析節號，未自動注入整章 STEP；"
        "請透過 MCP 工具 query_step_context / find_step_candidates 精確查詢。"
    )
    return VerseSelection((), "unresolved", tuple(warnings))


def _all_words(document: extract_stepbible.StepDocument):
    for verse in sorted(document.verses):
        for word in sorted(document.verses[verse], key=lambda item: item.position):
            yield verse, word


def discover_candidates(
    document: extract_stepbible.StepDocument,
    *,
    verses: Optional[Iterable[int]] = None,
    plan_strongs: Optional[Iterable[str]] = None,
    max_results: int = DEFAULT_CANDIDATE_MAX,
) -> list[StepCandidate]:
    """Discover deterministic linguistic candidates from a validated STEP document.

    Excludes STEP control Strongs (H90xx), groups Extended Strong variants under
    their base Strong, and assigns priority based on plan matches, chapter recurrence,
    and extended variants.
    """
    max_count = min(max(1, int(max_results)), HARD_CANDIDATE_MAX)
    selected_verses = set(int(v) for v in verses) if verses is not None else set(document.verses)

    plan_base_strongs: set[str] = set()
    plan_exact_strongs: set[str] = set()
    if plan_strongs:
        for item in plan_strongs:
            cleaned = str(item).strip()
            if not cleaned:
                continue
            base = extract_stepbible.base_strong(cleaned)
            if base:
                plan_base_strongs.add(base)
            norm = extract_stepbible.normalize_strong(cleaned)
            if norm:
                plan_exact_strongs.add(norm)

    groups: dict[str, list[dict]] = {}
    for verse, word in _all_words(document):
        if verse not in selected_verses:
            continue
        if not word.main_strong:
            continue
        if extract_stepbible.is_step_control_strong(word.main_strong):
            continue
        base = extract_stepbible.base_strong(word.main_strong)
        if not base:
            continue
        groups.setdefault(base, []).append({
            "verse": verse,
            "position": word.position,
            "surface": word.word,
            "transliteration": word.transliteration,
            "exact_strong": word.main_strong,
            "morphology": word.morphology_raw or word.morphology,
            "gloss": word.gloss,
            "lexicon": word.lexicon_short,
        })

    candidates: list[StepCandidate] = []
    for base, occs in groups.items():
        exact_strongs = tuple(sorted({o["exact_strong"] for o in occs if o["exact_strong"]}))
        headword = occs[0]["surface"]
        transliteration = occs[0]["transliteration"]
        short_gloss = occs[0]["lexicon"] or occs[0]["gloss"]

        signals: list[str] = []
        is_plan_target = (
            base in plan_base_strongs
            or any(es in plan_exact_strongs for es in exact_strongs)
        )
        if is_plan_target:
            signals.append("plan_target")

        count = len(occs)
        if count >= 3:
            signals.append(f"chapter_recurrence_x{count}")
        elif count == 2:
            signals.append("chapter_recurrence_x2")

        if len(exact_strongs) > 1:
            signals.append(f"extended_variants_{len(exact_strongs)}")

        if is_plan_target or count >= 3:
            priority = "HIGH"
        elif count == 2 or len(exact_strongs) > 1:
            priority = "MEDIUM"
        else:
            priority = "LOW"
            signals.append("single_occurrence")

        simplified_occs = tuple({
            "verse": o["verse"],
            "position": o["position"],
            "surface": o["surface"],
            "exact_strong": o["exact_strong"],
            "morphology": o["morphology"],
            "gloss": o["gloss"],
        } for o in occs)

        candidates.append(
            StepCandidate(
                base_strong=base,
                exact_strongs=exact_strongs,
                headword=headword,
                transliteration=transliteration,
                short_gloss=short_gloss,
                occurrences=simplified_occs,
                priority=priority,
                signals=tuple(signals),
            )
        )

    priority_weight = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    candidates.sort(
        key=lambda c: (
            priority_weight.get(c.priority, 3),
            -len(c.occurrences),
            c.base_strong,
        )
    )
    return candidates[:max_count]


def find_nearby_occurrences(
    root: Path | str,
    book: str,
    chapter: int,
    base_strong_value: str,
    *,
    window: int = DEFAULT_NEARBY_WINDOW,
    max_results: int = DEFAULT_OCCURRENCE_MAX,
) -> dict:
    """Find occurrences of base_strong across nearby chapters within a bounded window."""
    root = Path(root)
    canonical = canonical_book_name(book)
    chapter = int(chapter)
    window = min(max(1, int(window)), HARD_NEARBY_WINDOW)
    max_results = min(max(1, int(max_results)), HARD_OCCURRENCE_MAX)
    target_base = extract_stepbible.base_strong(base_strong_value)
    if not target_base:
        return {
            "success": False,
            "error": f"無法解析 base Strong：{base_strong_value}",
            "book": canonical,
            "chapter": chapter,
            "occurrences": [],
        }

    occurrences = []
    scanned_chapters = []
    start_ch = max(1, chapter - window)
    end_ch = chapter + window

    for ch in range(start_ch, end_ch + 1):
        filename = extract_stepbible.stepbible_filename(canonical, ch)
        path = root / "raw_data" / filename
        if not path.is_file():
            continue
        scanned_chapters.append(ch)
        try:
            raw = path.read_text(encoding="utf-8-sig", errors="strict")
            doc = extract_stepbible.parse_rendered_markdown_text(raw)
        except Exception:
            continue

        for verse, word in _all_words(doc):
            if not word.main_strong:
                continue
            if extract_stepbible.base_strong(word.main_strong) == target_base:
                occurrences.append({
                    "book": canonical,
                    "chapter": ch,
                    "verse": verse,
                    "position": word.position,
                    "reference": f"{doc.reference.code}.{ch}.{verse}",
                    "word": word.word,
                    "transliteration": word.transliteration,
                    "strong": word.main_strong,
                    "morphology": word.morphology_raw or word.morphology,
                    "gloss": word.gloss,
                })
                if len(occurrences) >= max_results:
                    break
        if len(occurrences) >= max_results:
            break

    return {
        "success": True,
        "book": canonical,
        "chapter": chapter,
        "base_strong": target_base,
        "window": window,
        "occurrences": occurrences[:max_results],
        "total_found": len(occurrences),
        "chapters_scanned": scanned_chapters,
    }


def render_candidate_summary(
    candidates: list[StepCandidate],
    *,
    book_name: str = "",
    chapter: int = 0,
    truncated: bool = False,
) -> str:
    """Render compact markdown summary for selected candidates."""
    lines = [
        "## STEP Bible selected candidates",
        f"- reference: {book_name} {chapter}".strip(),
        f"- candidate count: {len(candidates)}",
        "- note: 本區塊為 deterministic selector 挑出之候選原文證據；完整原文查詢請用 MCP 工具。",
    ]
    if truncated:
        lines.append("- note: 候選資料已依 token 預算截斷，更多詞彙請透過 MCP 查詢。")
    lines.append("")

    for c in candidates:
        lines.append(f"### {c.base_strong} ({c.headword} / {c.transliteration}) — {c.priority}")
        lines.append(f"- exact Strong: {', '.join(c.exact_strongs)}")
        lines.append(f"- brief gloss: {c.short_gloss}")
        lines.append(f"- occurrences in chapter: {len(c.occurrences)}")
        lines.append(f"- signals: {', '.join(c.signals)}")
        lines.append("- instances:")
        for occ in c.occurrences:
            lines.append(
                f"  - {occ['verse']}:{occ['position']} | {occ['surface']} | "
                f"{occ['exact_strong']} | {occ['morphology']} | {occ['gloss']}"
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def select_step_evidence(
    document: extract_stepbible.StepDocument,
    *,
    candidates: Optional[list[StepCandidate]] = None,
    plan_strongs: Optional[Iterable[str]] = None,
    verses: Optional[Iterable[int]] = None,
    char_budget: int = DEFAULT_STEP_PROMPT_CHAR_BUDGET,
) -> StepEvidence:
    """Filter and render candidates within char_budget without corrupting individual records."""
    if candidates is None:
        candidates = discover_candidates(
            document,
            verses=verses,
            plan_strongs=plan_strongs,
            max_results=HARD_CANDIDATE_MAX,
        )

    if not candidates:
        text = (
            "## STEP Bible selected candidates\n"
            f"- reference: {document.reference.book_name} {document.reference.chapter}\n"
            "- candidate count: 0\n"
            "- note: 本章無符合篩選條件之高優先級原文候選；需要時請透過 MCP 工具查詢。\n"
        )
        return StepEvidence(
            text=text,
            candidate_count=0,
            selected_count=0,
            truncated=False,
            total_chars=len(text),
        )

    selected: list[StepCandidate] = []
    # Progressively add candidates while within budget
    for c in candidates:
        candidate_test = selected + [c]
        rendered = render_candidate_summary(
            candidate_test,
            book_name=document.reference.book_name,
            chapter=document.reference.chapter,
            truncated=len(candidate_test) < len(candidates),
        )
        if len(rendered) <= char_budget:
            selected.append(c)
        else:
            break


    truncated = len(selected) < len(candidates)
    final_text = render_candidate_summary(
        selected,
        book_name=document.reference.book_name,
        chapter=document.reference.chapter,
        truncated=truncated,
    )
    return StepEvidence(
        text=final_text,
        candidate_count=len(candidates),
        selected_count=len(selected),
        truncated=truncated,
        total_chars=len(final_text),
    )


def validate_step_source(
    path: Path | str,
    *,
    expected_book: Optional[str] = None,
    expected_chapter: Optional[int] = None,
    scripture_verse_count: Optional[int] = None,
) -> dict:
    """Validate a complete/ranged STEP TXT and return its machine receipt."""
    path = Path(path)
    if not path.is_file():
        raise StepValidationError(f"STEP source 不存在：{path}")
    try:
        document = extract_stepbible.parse_rendered_markdown(path)
    except (OSError, UnicodeError, extract_stepbible.StepFormatError) as exc:
        raise StepValidationError(f"STEP source 無法解析：{exc}") from exc
    reference = document.reference
    if expected_book is not None:
        expected = extract_stepbible.parse_reference(f"{expected_book} {expected_chapter or reference.chapter}")
        if reference.code != expected.code:
            raise StepValidationError(
                f"STEP book 不符：檔案是 {reference.book_name}，預期 {expected.book_name}"
            )
    if expected_chapter is not None and reference.chapter != int(expected_chapter):
        raise StepValidationError(
            f"STEP chapter 不符：檔案是 {reference.chapter}，預期 {int(expected_chapter)}"
        )

    verse_numbers = sorted(document.verses)
    if reference.verse_start is not None:
        expected_verses = list(range(reference.verse_start, reference.verse_end + 1))
    elif scripture_verse_count is not None:
        expected_verses = list(range(1, int(scripture_verse_count) + 1))
    else:
        expected_verses = list(range(1, verse_numbers[-1] + 1))
    if verse_numbers != expected_verses:
        raise StepValidationError(
            f"STEP verse coverage 不符：實際 {verse_numbers}，預期 {expected_verses}"
        )

    words = list(_all_words(document))
    if not words:
        raise StepValidationError("STEP source 沒有 word rows")
    expected_script = _HEBREW_RE if reference.testament == "OT" else _GREEK_RE
    language_name = "Hebrew" if reference.testament == "OT" else "Greek"
    if not any(expected_script.search(word.word) for _verse, word in words):
        raise StepValidationError(f"STEP source 沒有 {language_name} original-language token")
    if not any(word.morphology.strip() for _verse, word in words):
        raise StepValidationError("STEP source 的 Morphology 欄沒有任何資料")

    seen_positions: dict[int, set[int]] = {}
    for verse, word in words:
        if word.position < 1 or word.position in seen_positions.setdefault(verse, set()):
            raise StepValidationError(
                f"STEP word position 不合法或重複：{reference.code} {reference.chapter}:{verse} #{word.position}"
            )
        seen_positions[verse].add(word.position)
        if not word.word.strip():
            raise StepValidationError(
                f"STEP original token 為空：{reference.code} {reference.chapter}:{verse} #{word.position}"
            )
        if not word.main_strong or not extract_stepbible.extract_strongs(word.main_strong):
            raise StepValidationError(
                f"STEP Strong 無法解析：{reference.code} {reference.chapter}:{verse} #{word.position}"
            )

    raw = path.read_bytes()
    first, last = verse_numbers[0], verse_numbers[-1]
    return {
        "validation": "machine",
        "status": "PASS",
        "path": path.as_posix(),
        "book": reference.book_name,
        "book_code": reference.code,
        "chapter": reference.chapter,
        "verse_start": reference.verse_start,
        "verse_end": reference.verse_end,
        "verses": len(verse_numbers),
        "words": len(words),
        "first": f"{reference.code} {reference.chapter}:{first}",
        "last": f"{reference.code} {reference.chapter}:{last}",
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "chars": len(raw.decode("utf-8-sig")),
    }


def render_projection(
    document: extract_stepbible.StepDocument,
    *,
    verses: Optional[Iterable[int]] = None,
    strong: Optional[str] = None,
    base_strong: Optional[str] = None,
    word: Optional[str] = None,
    source_path: Optional[Path] = None,
) -> tuple[str, int, int, tuple[int, ...]]:
    """Render occurrences plus one lexicon row per exact Extended Strong."""
    selected = set(int(verse) for verse in verses) if verses is not None else set(document.verses)
    strong_filter = extract_stepbible.normalize_strong(strong) if strong else None
    base_filter = extract_stepbible.base_strong(base_strong) if base_strong else None
    word_filter = (word or "").casefold()
    occurrences = []
    for verse, entry in _all_words(document):
        if verse not in selected:
            continue
        if strong_filter and entry.main_strong != strong_filter:
            continue
        if base_filter and extract_stepbible.base_strong(entry.main_strong) != base_filter:
            continue
        if word_filter and word_filter not in (
            entry.word + " " + entry.transliteration + " " + entry.lexicon_short
        ).casefold():
            continue
        occurrences.append((verse, entry))

    lexical: dict[str, str] = {}
    for _verse, entry in occurrences:
        if entry.main_strong and entry.lexicon_short:
            lexical.setdefault(entry.main_strong, entry.lexicon_short)
    reference = document.reference
    selected_present = tuple(sorted({verse for verse, _entry in occurrences}))
    source_label = source_path.as_posix() if source_path else "canonical STEP TXT"
    lines = [
        "## STEP Bible task projection",
        f"- source: {Path(source_label).name if source_path else source_label}",
        f"- reference: {reference.book_name} {reference.chapter}",
        f"- selected verses: {','.join(map(str, selected_present)) or 'none'}",
        "- boundary: lexicon 是可能義域，不等於本節語境義；morphology 不自行證明神學結論。",
        "",
        "### Occurrences",
        "format: position | original | transliteration | exact Extended Strong | morphology code | context gloss",
    ]
    active_verse = None
    for verse, entry in occurrences:
        if verse != active_verse:
            lines.append(f"#### {reference.code} {reference.chapter}:{verse}")
            active_verse = verse
        fields = [
            str(entry.position),
            entry.word,
            entry.transliteration,
            entry.main_strong,
            entry.morphology_raw or entry.morphology,
            entry.gloss,
        ]
        lines.append("- " + " | ".join(field.strip() for field in fields))
    if not occurrences:
        lines.append("- （沒有符合查詢條件的 occurrence）")
    lines.extend(["", "### Lexicon（依 exact Extended Strong 去重）"])
    if lexical:
        for strong_id, definition in lexical.items():
            lines.append(f"- {strong_id} | {definition}")
    else:
        lines.append("- （沒有可用 brief lexicon）")
    text = "\n".join(lines).rstrip() + "\n"
    return text, len(occurrences), len(lexical), selected_present


def project_step_source(
    path: Path | str,
    *,
    verses: Optional[Iterable[int]] = None,
    strong: Optional[str] = None,
    base_strong: Optional[str] = None,
    word: Optional[str] = None,
) -> StepProjection:
    path = Path(path)
    raw = path.read_text(encoding="utf-8-sig", errors="strict")
    document = extract_stepbible.parse_rendered_markdown_text(raw)
    text, occurrence_count, lexicon_count, selected = render_projection(
        document, verses=verses, strong=strong, base_strong=base_strong, word=word, source_path=path
    )
    return StepProjection(
        text=text,
        raw_chars=len(raw),
        raw_bytes=len(raw.encode("utf-8")),
        projected_chars=len(text),
        projected_bytes=len(text.encode("utf-8")),
        occurrence_count=occurrence_count,
        lexicon_count=lexicon_count,
        selected_verses=selected,
    )


def find_formal_step_source(
    root: Path | str,
    book: str,
    chapter: int,
    *,
    verses: Optional[Iterable[int]] = None,
) -> Path:
    """Resolve this chapter's manifest STEP source, then canonical raw filename."""
    root = Path(root)
    canonical = canonical_book_name(book)
    chapter = int(chapter)
    try:
        chapter_dir = book_directory(root, canonical) / ".tmp" / f"第{chapter}章"
        manifest = chapter_dir / "source_manifest.md"
        if manifest.exists():
            try:
                from . import source_excerpts
            except ImportError:
                import source_excerpts
            identities = source_excerpts.manifest_source_identities(manifest, root)
            matches = [item.path for item in identities if item.is_structured]
            if not matches:
                raise StepValidationError(
                    "本章已有 source_manifest.md，但未宣告 OK STEP／原文資料來源；"
                    "拒絕旁路 manifest 讀取其他 raw_data"
                )
            if len(matches) != 1:
                raise StepValidationError("本章 manifest 有多個 STEP／原文資料來源，無法唯一查詢")
            return matches[0]
    except FileNotFoundError:
        pass

    full = root / "raw_data" / extract_stepbible.stepbible_filename(canonical, chapter)
    if full.is_file():
        return full
    if verses:
        ordered = sorted(set(int(value) for value in verses))
        if ordered == list(range(ordered[0], ordered[-1] + 1)):
            ranged = root / "raw_data" / extract_stepbible.stepbible_filename(
                canonical, chapter, ordered[0], ordered[-1]
            )
            if ranged.is_file():
                return ranged
    raise FileNotFoundError(
        f"找不到本章正式 STEP source：{full}；先執行 extract_stepbible.py"
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Query deterministic compact context from this chapter's formal STEP TXT"
    )
    parser.add_argument("book")
    parser.add_argument("chapter", type=int)
    parser.add_argument("--verses", help="節號／範圍，例如 1-3,5")
    parser.add_argument("--strong", help="exact Extended Strong，例如 H1254A 或 G3056")
    parser.add_argument("--base-strong", help="base Strong 代碼（例如 H1254 或 G3056）")
    parser.add_argument("--word", help="原文、音譯或 lexicon headword 子字串")
    parser.add_argument("--candidates", action="store_true", help="輸出本章 deterministic candidates 候選清單")
    parser.add_argument("--occurrences", action="store_true", help="查詢相鄰章節 occurrences")
    parser.add_argument("--window", type=int, default=DEFAULT_NEARBY_WINDOW, help=f"相鄰章節視窗半徑（預設 {DEFAULT_NEARBY_WINDOW}）")
    parser.add_argument("--max-results", type=int, default=DEFAULT_CANDIDATE_MAX, help=f"最大回傳筆數（預設 {DEFAULT_CANDIDATE_MAX}）")
    parser.add_argument("--char-budget", type=int, default=DEFAULT_STEP_PROMPT_CHAR_BUDGET, help=f"STEP prompt 字元預算（預設 {DEFAULT_STEP_PROMPT_CHAR_BUDGET}）")
    parser.add_argument("--receipt", action="store_true", help="另輸出 machine validation receipt JSON")
    return parser


def main(argv=None) -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")
    args = build_arg_parser().parse_args(argv)
    try:
        verses = parse_verse_spec(args.verses) if args.verses else None
        if args.occurrences:
            if not args.base_strong and not args.strong:
                print("❌ --occurrences 需要指定 --base-strong 或 --strong", file=sys.stderr)
                return 1
            strong_target = args.base_strong or args.strong
            result = find_nearby_occurrences(
                ROOT, args.book, args.chapter, strong_target,
                window=args.window, max_results=args.max_results
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        path = find_formal_step_source(ROOT, args.book, args.chapter, verses=verses)
        scripture = ROOT / "raw_scripture" / canonical_book_name(args.book) / f"第{args.chapter}章.txt"
        verse_count = len(scripture.read_text(encoding="utf-8").splitlines()) if scripture.is_file() else None
        receipt = validate_step_source(
            path, expected_book=args.book, expected_chapter=args.chapter,
            scripture_verse_count=verse_count,
        )

        if args.candidates:
            raw = path.read_text(encoding="utf-8-sig", errors="strict")
            doc = extract_stepbible.parse_rendered_markdown_text(raw)
            candidates = discover_candidates(doc, verses=verses, max_results=args.max_results)
            output = [
                {
                    "base_strong": c.base_strong,
                    "exact_strongs": list(c.exact_strongs),
                    "headword": c.headword,
                    "transliteration": c.transliteration,
                    "short_gloss": c.short_gloss,
                    "occurrences_count": len(c.occurrences),
                    "priority": c.priority,
                    "signals": list(c.signals),
                }
                for c in candidates
            ]
            print(json.dumps(output, ensure_ascii=False, indent=2))
            return 0

        projection = project_step_source(
            path, verses=verses, strong=args.strong, base_strong=args.base_strong, word=args.word
        )
    except (OSError, UnicodeError, ValueError, StepValidationError) as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1
    if args.receipt:
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
    print(projection.text, end="")
    return 0



if __name__ == "__main__":
    raise SystemExit(main())
