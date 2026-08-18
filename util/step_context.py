#!/usr/bin/env python3
"""Deterministic validation and compact prompt/query context for STEP TXT.

The formal source remains ``raw_data/stepbible_*.txt``.  This module parses
that complete renderer-owned format, validates it as structured data, and
projects task-relevant occurrences and selected candidate evidence.  Bounded
nearby chapter lookups are used strictly to evaluate lexical recurrence signals.
It never downloads data at runtime.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
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
_HEBREW_TOKEN_RE = re.compile(r"[\u0590-\u05ff\ufb1d-\ufb4f]+")
_GREEK_TOKEN_RE = re.compile(r"[\u0370-\u03ff\u1f00-\u1fff]+")
_HEBREW_RE = _HEBREW_TOKEN_RE
_GREEK_RE = _GREEK_TOKEN_RE


def _normalize_latin(text: str) -> str:
    if not text:
        return ""
    decomposed = unicodedata.normalize("NFKD", text)
    return re.sub(r"[^a-z0-9]", "", decomposed.lower())


def _normalize_hebrew_token(text: str) -> str:
    if not text:
        return ""
    decomposed = unicodedata.normalize("NFKD", text)
    return re.sub(r"[^\u05d0-\u05ea\ufb1d-\ufb4f]", "", decomposed)


def _normalize_greek_token(text: str) -> str:
    if not text:
        return ""
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return re.sub(r"[^\u0370-\u03ff\u1f00-\u1fff]", "", stripped.lower())


def _to_canonical_zh(book_or_code: str) -> str:
    cleaned = str(book_or_code).strip()
    if cleaned in extract_stepbible.BOOK_BY_CANONICAL_NAME:
        return cleaned
    if cleaned in extract_stepbible.BOOK_BY_CODE:
        return extract_stepbible.BOOK_BY_CODE[cleaned]["canonical_name"]
    for meta in extract_stepbible.BOOK_BY_CODE.values():
        if meta["name"].lower() == cleaned.lower() or cleaned in meta.get("aliases", ()):
            return meta["canonical_name"]
    return canonical_book_name(cleaned)


def load_validated_nearby_step(
    root: Path | str,
    book: str,
    chapter: int,
) -> tuple[Optional[extract_stepbible.StepDocument], Optional[str]]:
    """Load and validate a formal STEP source for an adjacent chapter.

    Returns (document, None) on success, (None, None) if source file is missing,
    or (None, error_str) if validation or parsing fails.
    """
    canonical = _to_canonical_zh(book)
    try:
        path = find_formal_step_source(root, canonical, chapter)
    except (FileNotFoundError, StepValidationError):
        return None, None

    try:
        scripture = Path(root) / "raw_scripture" / canonical / f"第{chapter}章.txt"
        verse_count = (
            len(scripture.read_text(encoding="utf-8").splitlines())
            if scripture.is_file()
            else None
        )
        validate_step_source(
            path,
            expected_book=canonical,
            expected_chapter=chapter,
            scripture_verse_count=verse_count,
        )
        raw = path.read_text(encoding="utf-8-sig", errors="strict")
        doc = extract_stepbible.parse_rendered_markdown_text(raw)
        if doc.reference.chapter != chapter or _to_canonical_zh(doc.reference.book_name) != canonical:
            raise StepValidationError(f"STEP chapter/book 不符：{path}")
        return doc, None
    except Exception as exc:
        return None, str(exc)


DEFAULT_CANDIDATE_MAX = 20
HARD_CANDIDATE_MAX = 40
DEFAULT_OCCURRENCE_MAX = 20
HARD_OCCURRENCE_MAX = 50
DEFAULT_NEARBY_WINDOW = 5
HARD_NEARBY_WINDOW = 10
DEFAULT_STEP_PROMPT_CHAR_BUDGET = 7000
DEFAULT_QUERY_MAX_RESULTS = 200
HARD_QUERY_MAX_RESULTS = 200
DEFAULT_QUERY_MAX_CHARS = 12000
HARD_QUERY_MAX_CHARS = 12000


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
    truncated: bool = False


@dataclass(frozen=True)
class StepCandidate:
    base_strong: str
    exact_strongs: tuple[str, ...]
    surface: str
    context_gloss: str
    lexicon_word: str
    lexicon_transliteration: str
    lexicon_short: str
    variants: tuple[dict, ...]
    occurrences: tuple[dict, ...]
    priority: str  # "HIGH", "MEDIUM", "LOW"
    signals: tuple[str, ...]

    @property
    def headword(self) -> str:
        return self.lexicon_word or self.surface

    @property
    def transliteration(self) -> str:
        return self.lexicon_transliteration or (
            self.occurrences[0]["transliteration"] if self.occurrences else ""
        )

    @property
    def short_gloss(self) -> str:
        return self.lexicon_short or self.context_gloss


@dataclass(frozen=True)
class StepEvidence:
    text: str
    candidate_count: int
    selected_count: int
    truncated: bool
    total_chars: int
    mode: str = "selected_candidates"
    selected_verses: tuple[int, ...] = ()
    occurrences: int = 0



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


NON_ORIGINAL_TYPES = {
    "人物", "地點", "神學", "背景", "文化", "歷史", "主題", "事件", "解經爭議", "互文"
}


def _is_non_original_entry(entry: dict) -> bool:
    stype = str(entry.get("suggested_type") or entry.get("type") or "").strip()
    if stype in NON_ORIGINAL_TYPES:
        name = str(entry.get("name") or "")
        evidence = str(entry.get("evidence") or "")
        if _HEBREW_TOKEN_RE.search(name) or _GREEK_TOKEN_RE.search(name):
            return False
        if re.search(r"\b[HG]\d+[A-Za-z]?\b", name + " " + evidence):
            return False
        if re.search(r"[（\(][a-zA-Z\s'\-]+[）\)]", name):
            return False
        return True
    return False


def select_candidate_verses(
    batch: Iterable[dict], available_verses: Iterable[int]
) -> VerseSelection:
    """Select M3 STEP verses from batch evidence/surfaces with fail-small policy."""
    available = set(int(verse) for verse in available_verses)
    batch_list = list(batch)
    if not batch_list:
        return VerseSelection((), "unresolved", ("候選清單為空",))

    if all(_is_non_original_entry(entry) for entry in batch_list):
        return VerseSelection(
            (),
            "non-original-skipped",
            ("本批候選均為非原文類條目，未自動注入該節全部原文詞彙；若需原文證據請用 query_step_context。",),
        )

    selected: set[int] = set()
    warnings: list[str] = []
    full_chapter = False
    for entry in batch_list:
        if _is_non_original_entry(entry):
            continue
        selected.update(_surface_verses(entry))
        parsed, parse_warnings, requested_full = _evidence_verses(entry.get("evidence", ""))
        selected.update(parsed)
        warnings.extend(f"{entry.get('name', 'candidate')}：{item}" for item in parse_warnings)
        full_chapter = full_chapter or requested_full

    if full_chapter:
        return VerseSelection(
            (),
            "full-chapter-evidence",
            ("候選範圍為全章，為避免 token 膨脹未自動投射整章 compact STEP；請使用 find_step_candidates 探索或 query_step_context 查詢。",),
        )

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
    root: Optional[Path | str] = None,
    verses: Optional[Iterable[int]] = None,
    plan_strongs: Optional[Iterable[str]] = None,
    nearby_window: int = DEFAULT_NEARBY_WINDOW,
    include_medium: bool = True,
    include_low: bool = False,
    max_results: int = DEFAULT_CANDIDATE_MAX,
    diagnostics: Optional[dict] = None,
) -> list[StepCandidate]:
    """Discover deterministic linguistic candidates from a validated STEP document.

    Excludes STEP control Strongs (H90xx), groups Extended Strong variants under
    their base Strong, scans bounded nearby chapters to score recurrence, and
    categorizes candidates into HIGH, MEDIUM, and LOW priorities.
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

    # Scan nearby window once to aggregate base Strong counts in adjacent chapters
    nearby_counts: dict[str, int] = {}
    nearby_root = Path(root) if root else (ROOT if (ROOT / "raw_data").is_dir() else None)
    nearby_missing_chapters: list[int] = []
    nearby_invalid_chapters: list[dict] = []
    nearby_scanned_chapters: list[int] = []
    if nearby_root and nearby_window > 0:
        window_val = min(max(1, int(nearby_window)), HARD_NEARBY_WINDOW)
        start_ch = max(1, document.reference.chapter - window_val)
        end_ch = document.reference.chapter + window_val
        for ch in range(start_ch, end_ch + 1):
            if ch == document.reference.chapter:
                continue
            doc, err = load_validated_nearby_step(nearby_root, document.reference.book_name, ch)
            if err:
                nearby_invalid_chapters.append({"chapter": ch, "error": err})
                continue
            if doc is None:
                nearby_missing_chapters.append(ch)
                continue
            nearby_scanned_chapters.append(ch)
            for _, w in _all_words(doc):
                if w.main_strong and not extract_stepbible.is_step_control_strong(w.main_strong):
                    base = extract_stepbible.base_strong(w.main_strong)
                    if base:
                        nearby_counts[base] = nearby_counts.get(base, 0) + 1

    if diagnostics is not None:
        diagnostics["scanned_chapters"] = nearby_scanned_chapters
        diagnostics["missing_chapters"] = nearby_missing_chapters
        diagnostics["invalid_chapters"] = nearby_invalid_chapters

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
            "lexicon_word": word.lexicon_word,
            "lexicon_transliteration": word.lexicon_transliteration,
            "lexicon_short": word.lexicon_short,
        })

    candidates: list[StepCandidate] = []
    for base, occs in groups.items():
        exact_strongs = tuple(sorted({o["exact_strong"] for o in occs if o["exact_strong"]}))
        surface = occs[0]["surface"]
        context_gloss = occs[0]["gloss"]
        lexicon_word = occs[0]["lexicon_word"] or occs[0]["surface"]
        lexicon_transliteration = occs[0]["lexicon_transliteration"] or occs[0]["transliteration"]
        lexicon_short = occs[0]["lexicon_short"]

        variants_map: dict[str, dict] = {}
        for o in occs:
            es = o["exact_strong"]
            if es not in variants_map:
                variants_map[es] = {
                    "exact_strong": es,
                    "lexicon_word": o["lexicon_word"] or o["surface"],
                    "lexicon_transliteration": o["lexicon_transliteration"] or o["transliteration"],
                    "lexicon_short": o["lexicon_short"],
                    "gloss": o["gloss"],
                }
        variants = tuple(variants_map[es] for es in exact_strongs)

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

        nearby_count = nearby_counts.get(base, 0)
        if nearby_count > 0:
            signals.append(f"nearby_chapter_recurrence_x{nearby_count}")

        if len(exact_strongs) > 1:
            signals.append(f"extended_variants_{len(exact_strongs)}")

        if is_plan_target or count >= 3:
            priority = "HIGH"
        elif count == 2 or (count == 1 and nearby_count > 0):
            priority = "MEDIUM"
        else:
            priority = "LOW"
            signals.append("single_occurrence")

        if not include_low and priority == "LOW":
            continue
        if not include_medium and priority != "HIGH":
            continue

        simplified_occs = tuple({
            "verse": o["verse"],
            "position": o["position"],
            "surface": o["surface"],
            "exact_strong": o["exact_strong"],
            "morphology": o["morphology"],
            "gloss": o["gloss"],
            "transliteration": o["transliteration"],
        } for o in occs)

        candidates.append(
            StepCandidate(
                base_strong=base,
                exact_strongs=exact_strongs,
                surface=surface,
                context_gloss=context_gloss,
                lexicon_word=lexicon_word,
                lexicon_transliteration=lexicon_transliteration,
                lexicon_short=lexicon_short,
                variants=variants,
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
    base_strong_value: Optional[str] = None,
    *,
    base_strong: Optional[str] = None,
    strong: Optional[str] = None,
    window: int = DEFAULT_NEARBY_WINDOW,
    max_results: int = DEFAULT_OCCURRENCE_MAX,
) -> dict:
    """Find occurrences of base_strong or exact strong across nearby chapters."""
    root = Path(root)
    canonical = canonical_book_name(book)
    chapter = int(chapter)
    window = min(max(1, int(window)), HARD_NEARBY_WINDOW)
    max_results = min(max(1, int(max_results)), HARD_OCCURRENCE_MAX)

    effective_base = base_strong or base_strong_value
    if strong and effective_base:
        return {
            "success": False,
            "error": "不可同時指定 base_strong 與 strong，請二選一：strong 為 exact match，base_strong 為 base/variant group match。",
            "book": canonical,
            "chapter": chapter,
            "occurrences": [],
        }
    if not strong and not effective_base:
        return {
            "success": False,
            "error": "必須指定 base_strong 或 strong",
            "book": canonical,
            "chapter": chapter,
            "occurrences": [],
        }

    target_exact = extract_stepbible.normalize_strong(strong) if strong else None
    target_base = extract_stepbible.base_strong(effective_base) if effective_base else None

    occurrences = []
    scanned_chapters = []
    missing_chapters = []
    invalid_chapters = []
    start_ch = max(1, chapter - window)
    end_ch = chapter + window
    limit_reached = False

    for ch in range(start_ch, end_ch + 1):
        doc, err = load_validated_nearby_step(root, canonical, ch)
        if err:
            invalid_chapters.append({"chapter": ch, "error": err})
            continue
        if doc is None:
            missing_chapters.append(ch)
            continue
        scanned_chapters.append(ch)

        for verse, word in _all_words(doc):
            if not word.main_strong:
                continue
            matches = False
            if target_exact:
                matches = (word.main_strong == target_exact)
            elif target_base:
                matches = (extract_stepbible.base_strong(word.main_strong) == target_base)

            if matches:
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
                    limit_reached = True
                    break
        if limit_reached:
            break

    return {
        "success": True,
        "book": canonical,
        "chapter": chapter,
        "strong": target_exact,
        "base_strong": target_base,
        "match_type": "exact" if target_exact else "base_group",
        "window": window,
        "occurrences": occurrences,
        "result_count": len(occurrences),
        "max_results": max_results,
        "truncated": limit_reached,
        "chapters_scanned": scanned_chapters,
        "missing_chapters": missing_chapters,
        "invalid_chapters": invalid_chapters,
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
        header_desc = f"{c.surface} / {c.lexicon_word}" if c.surface != c.lexicon_word else c.surface
        lines.append(f"### {c.base_strong} ({header_desc} / {c.lexicon_transliteration}) — {c.priority}")
        lines.append(f"- exact Strongs: {', '.join(c.exact_strongs)}")
        lines.append(f"- context gloss: {c.context_gloss}")
        if c.lexicon_short:
            lines.append(f"- brief lexicon: {c.lexicon_short}")
        lines.append(f"- occurrences in chapter: {len(c.occurrences)}")
        lines.append(f"- signals: {', '.join(c.signals)}")
        if len(c.variants) > 1:
            lines.append("- variants:")
            for v in c.variants:
                lines.append(
                    f"  - {v['exact_strong']} | {v['lexicon_word']} ({v['lexicon_transliteration']}) | {v['lexicon_short']}"
                )
        lines.append("- instances:")
        for occ in c.occurrences:
            lines.append(
                f"  - {occ['verse']}:{occ['position']} | {occ['surface']} | "
                f"{occ['exact_strong']} | {occ['morphology']} | {occ['gloss']}"
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def select_m3_candidate_evidence(
    document: extract_stepbible.StepDocument,
    batch: Iterable[dict],
    *,
    root: Optional[Path | str] = None,
    char_budget: int = DEFAULT_STEP_PROMPT_CHAR_BUDGET,
) -> StepEvidence:
    """Deterministically select compact STEP evidence for an M3 entry batch.

    Only injects candidate-relevant linguistic evidence for the entries in this batch.
    Never falls back to full-verse dumps of unrelated words.
    """
    batch_list = list(batch or [])
    if not batch_list:
        text = (
            "## STEP Bible selected candidates\n"
            f"- reference: {document.reference.book_name} {document.reference.chapter}\n"
            "- candidate count: 0\n"
            "- mode: unresolved\n"
            "- note: 候選清單為空；需要時請透過 MCP 工具查詢。\n"
        )
        return StepEvidence(
            text=text, candidate_count=0, selected_count=0,
            truncated=False, total_chars=len(text), mode="unresolved"
        )

    if all(_is_non_original_entry(entry) for entry in batch_list):
        text = (
            "## STEP Bible selected candidates\n"
            f"- reference: {document.reference.book_name} {document.reference.chapter}\n"
            "- candidate count: 0\n"
            "- mode: non-original-skipped\n"
            "- note: 本批候選均為非原文類條目，未自動注入原文詞彙；若需原文證據請用 query_step_context。\n"
        )
        return StepEvidence(
            text=text, candidate_count=0, selected_count=0,
            truncated=False, total_chars=len(text), mode="non-original-skipped"
        )

    for entry in batch_list:
        if "全章" in str(entry.get("evidence", "")):
            text = (
                "## STEP Bible selected candidates\n"
                f"- reference: {document.reference.book_name} {document.reference.chapter}\n"
                "- candidate count: 0\n"
                "- mode: full-chapter-evidence\n"
                "- note: 候選範圍為全章，為避免 token 膨脹未自動投射整章 compact STEP；請使用 find_step_candidates 探索或 query_step_context 查詢。\n"
            )
            return StepEvidence(
                text=text, candidate_count=0, selected_count=0,
                truncated=False, total_chars=len(text), mode="full-chapter-evidence"
            )

    base_occurrences: dict[str, list[extract_stepbible.WordEntry]] = {}
    base_seen_keys: dict[str, set[tuple[str, int]]] = {}
    all_selected_verses: set[int] = set()

    for entry in batch_list:
        if _is_non_original_entry(entry):
            continue
        entry_name = str(entry.get("name") or "")
        evidence = str(entry.get("evidence") or "")
        surfaces = entry.get("surfaces") or []
        verse_scope, _warnings, _is_full = _evidence_verses(evidence)
        verse_scope.update(_surface_verses(entry))
        if verse_scope:
            all_selected_verses.update(verse_scope)

        # 1. Extract explicit Strong codes from name and evidence
        strongs = extract_stepbible.extract_strongs(entry_name + " " + evidence)
        target_bases = {extract_stepbible.base_strong(s) for s in strongs if extract_stepbible.base_strong(s)}
        target_exacts = {extract_stepbible.normalize_strong(s) for s in strongs if extract_stepbible.normalize_strong(s)}

        # 2. Extract full Hebrew / Greek tokens
        all_text_to_scan = entry_name + " " + evidence + " " + " ".join(
            s.get("phrase", "") if isinstance(s, dict) else str(s) for s in surfaces
        )
        hebrew_tokens = [
            _normalize_hebrew_token(t)
            for t in _HEBREW_TOKEN_RE.findall(all_text_to_scan)
        ]
        hebrew_tokens = [t for t in hebrew_tokens if len(t) >= 2]

        greek_tokens = [
            _normalize_greek_token(t)
            for t in _GREEK_TOKEN_RE.findall(all_text_to_scan)
        ]
        greek_tokens = [t for t in greek_tokens if len(t) >= 2]

        # 3. Extract Latin transliteration in parentheses
        latin_transliterations = [
            t.strip() for t in re.findall(r"[（\(]([a-zA-Z\s'\-’]+)[）\)]", entry_name)
            if t.strip()
        ]

        # Scope words
        if verse_scope:
            words_in_scope = [
                (v, w) for v in sorted(verse_scope) if v in document.verses
                for w in document.verses[v]
                if w.main_strong and not extract_stepbible.is_step_control_strong(w.main_strong)
            ]
        else:
            words_in_scope = [
                (v, w) for v, w in _all_words(document)
                if w.main_strong and not extract_stepbible.is_step_control_strong(w.main_strong)
            ]

        # Search matching words
        entry_matched_bases: set[str] = set()
        for v, w in words_in_scope:
            base = extract_stepbible.base_strong(w.main_strong)
            if not base:
                continue
            # Match Strong
            if base in target_bases or w.main_strong in target_exacts:
                entry_matched_bases.add(base)
                continue
            # Match Hebrew token (whole normalized token equality)
            if hebrew_tokens:
                w_heb = _normalize_hebrew_token(w.word)
                w_heb_lex = _normalize_hebrew_token(w.lexicon_word or "")
                if any(t == w_heb or t == w_heb_lex for t in hebrew_tokens):
                    entry_matched_bases.add(base)
                    continue
            # Match Greek token (whole normalized token equality)
            if greek_tokens:
                w_grk = _normalize_greek_token(w.word)
                w_grk_lex = _normalize_greek_token(w.lexicon_word or "")
                if any(t == w_grk or t == w_grk_lex for t in greek_tokens):
                    entry_matched_bases.add(base)
                    continue
            # Match Transliteration
            if latin_transliterations:
                norm_w_trans = _normalize_latin(w.transliteration)
                norm_w_lex_trans = _normalize_latin(w.lexicon_transliteration or "")
                for t in latin_transliterations:
                    norm_t = _normalize_latin(t)
                    if len(norm_t) >= 2:
                        if norm_t == norm_w_trans or norm_t == norm_w_lex_trans or norm_t in norm_w_trans:
                            entry_matched_bases.add(base)
                            break

        # If no Strong / Hebrew / Greek / transliteration matched but verse scope exists, run discovery on those verses
        if not entry_matched_bases and verse_scope:
            discovered = discover_candidates(
                document, verses=verse_scope, root=root,
                include_medium=True, include_low=False, max_results=5
            )
            surface_phrases = [
                s.get("phrase", "") if isinstance(s, dict) else str(s)
                for s in surfaces
            ]
            for dc in discovered:
                if any(p and (p in dc.surface or p in dc.context_gloss) for p in surface_phrases):
                    entry_matched_bases.add(dc.base_strong)
            # NEVER guess HIGH words!

        for b in entry_matched_bases:
            seen_set = base_seen_keys.setdefault(b, set())
            occs_list = base_occurrences.setdefault(b, [])
            for _v, w in words_in_scope:
                if extract_stepbible.base_strong(w.main_strong) == b:
                    key = (w.reference, w.position)
                    if key not in seen_set:
                        seen_set.add(key)
                        occs_list.append(w)

    matched_candidates: list[StepCandidate] = []
    for b in sorted(base_occurrences.keys()):
        target_occs = base_occurrences[b]
        if not target_occs:
            continue
        first_w = target_occs[0]
        exact_strongs = tuple(sorted({w.main_strong for w in target_occs if w.main_strong}))
        variants_map = {}
        for w in target_occs:
            es = w.main_strong
            if es not in variants_map:
                variants_map[es] = {
                    "exact_strong": es,
                    "lexicon_word": w.lexicon_word or w.word,
                    "lexicon_transliteration": w.lexicon_transliteration or w.transliteration,
                    "lexicon_short": w.lexicon_short,
                    "gloss": w.gloss,
                }
        variants = tuple(variants_map[es] for es in exact_strongs)
        simplified_occs = tuple({
            "verse": int(w.reference.split(".")[-1]) if "." in w.reference else 1,
            "position": w.position,
            "surface": w.word,
            "exact_strong": w.main_strong,
            "morphology": w.morphology_raw or w.morphology,
            "gloss": w.gloss,
            "transliteration": w.transliteration,
        } for w in target_occs)
        matched_candidates.append(
            StepCandidate(
                base_strong=b,
                exact_strongs=exact_strongs,
                surface=first_w.word,
                context_gloss=first_w.gloss,
                lexicon_word=first_w.lexicon_word or first_w.word,
                lexicon_transliteration=first_w.lexicon_transliteration or first_w.transliteration,
                lexicon_short=first_w.lexicon_short,
                variants=variants,
                occurrences=simplified_occs,
                priority="HIGH",
                signals=("m3_targeted_candidate",),
            )
        )

    if not matched_candidates:
        text = (
            "## STEP Bible selected candidates\n"
            f"- reference: {document.reference.book_name} {document.reference.chapter}\n"
            "- candidate count: 0\n"
            "- mode: unresolved\n"
            "- note: 無法機械定位該候選原文詞彙；請使用 MCP 工具 query_step_context / find_step_candidates 精確查詢。\n"
        )
        return StepEvidence(
            text=text, candidate_count=0, selected_count=0,
            truncated=False, total_chars=len(text), mode="unresolved"
        )

    selected: list[StepCandidate] = []
    for c in matched_candidates:
        candidate_test = selected + [c]
        rendered = render_candidate_summary(
            candidate_test,
            book_name=document.reference.book_name,
            chapter=document.reference.chapter,
            truncated=len(candidate_test) < len(matched_candidates),
        )
        if len(rendered) <= char_budget:
            selected.append(c)
        else:
            break

    truncated = len(selected) < len(matched_candidates)
    final_text = render_candidate_summary(
        selected,
        book_name=document.reference.book_name,
        chapter=document.reference.chapter,
        truncated=truncated,
    )
    total_occs = sum(len(c.occurrences) for c in selected)
    return StepEvidence(
        text=final_text,
        candidate_count=len(matched_candidates),
        selected_count=len(selected),
        truncated=truncated,
        total_chars=len(final_text),
        mode="targeted",
        selected_verses=tuple(sorted(all_selected_verses)),
        occurrences=total_occs,
    )


def select_step_evidence(
    document: extract_stepbible.StepDocument,
    *,
    root: Optional[Path | str] = None,
    candidates: Optional[list[StepCandidate]] = None,
    plan_strongs: Optional[Iterable[str]] = None,
    verses: Optional[Iterable[int]] = None,
    nearby_window: int = DEFAULT_NEARBY_WINDOW,
    char_budget: int = DEFAULT_STEP_PROMPT_CHAR_BUDGET,
) -> StepEvidence:
    """Filter and render HIGH/MEDIUM candidates within char_budget without padding LOW words."""
    if candidates is None:
        candidates = discover_candidates(
            document,
            root=root,
            verses=verses,
            plan_strongs=plan_strongs,
            nearby_window=nearby_window,
            include_medium=True,
            include_low=False,
            max_results=HARD_CANDIDATE_MAX,
        )

    # Automatic prompt context NEVER injects LOW candidates to fill remaining budget
    candidates = [c for c in candidates if c.priority in ("HIGH", "MEDIUM")]

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
            mode="selected_candidates",
            selected_verses=(),
            occurrences=0,
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
    total_occs = sum(len(c.occurrences) for c in selected)
    all_verses = tuple(sorted({occ["verse"] for c in selected for occ in c.occurrences if "verse" in occ}))
    return StepEvidence(
        text=final_text,
        candidate_count=len(candidates),
        selected_count=len(selected),
        truncated=truncated,
        total_chars=len(final_text),
        mode="selected_candidates",
        selected_verses=all_verses,
        occurrences=total_occs,
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
    max_results: int = DEFAULT_QUERY_MAX_RESULTS,
    max_characters: int = DEFAULT_QUERY_MAX_CHARS,
    allow_full_chapter: bool = False,
    source_path: Optional[Path] = None,
) -> tuple[str, int, int, tuple[int, ...], bool]:
    """Render occurrences plus one lexicon row per exact Extended Strong with bounded budget."""
    if (
        not allow_full_chapter
        and verses is None
        and strong is None
        and base_strong is None
        and word is None
    ):
        raise ValueError(
            "至少必須提供 verses, strong, base_strong 或 word 其中之一進行精確查詢；若需探索本章原文候選，請使用 find_step_candidates。"
        )

    max_count = min(max(1, int(max_results)), HARD_QUERY_MAX_RESULTS)
    max_chars = min(max(500, int(max_characters)), HARD_QUERY_MAX_CHARS)

    selected = set(int(verse) for verse in verses) if verses is not None else set(document.verses)
    strong_filter = extract_stepbible.normalize_strong(strong) if strong else None
    base_filter = extract_stepbible.base_strong(base_strong) if base_strong else None
    word_filter = (word or "").casefold()
    all_matching = []
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
        all_matching.append((verse, entry))

    truncated = False
    if len(all_matching) > max_count:
        all_matching = all_matching[:max_count]
        truncated = True

    included_occurrences = []
    included_lexical: dict[str, str] = {}
    reference = document.reference
    source_label = source_path.as_posix() if source_path else "canonical STEP TXT"
    selected_present_all = sorted({verse for verse, _entry in all_matching})

    header_lines = [
        "## STEP Bible task projection",
        f"- source: {Path(source_label).name if source_path else source_label}",
        f"- reference: {reference.book_name} {reference.chapter}",
        f"- selected verses: {','.join(map(str, selected_present_all)) or 'none'}",
        "- boundary: lexicon 是可能義域，不等於本節語境義；morphology 不自行證明神學結論。",
    ]

    for verse, entry in all_matching:
        test_occs = included_occurrences + [(verse, entry)]
        test_lex = dict(included_lexical)
        if entry.main_strong and entry.lexicon_short:
            test_lex[entry.main_strong] = entry.lexicon_short

        occ_lines = []
        act_v = None
        for v, e in test_occs:
            if v != act_v:
                occ_lines.append(f"#### {reference.code} {reference.chapter}:{v}")
                act_v = v
            fields = [
                str(e.position),
                e.word,
                e.transliteration,
                e.main_strong,
                e.morphology_raw or e.morphology,
                e.gloss,
            ]
            occ_lines.append("- " + " | ".join(f.strip() for f in fields))

        lex_lines = ["", "### Lexicon（依 exact Extended Strong 去重）"]
        for sid, d in test_lex.items():
            lex_lines.append(f"- {sid} | {d}")

        total_len = sum(
            len(l) + 1
            for l in header_lines
            + [
                "",
                "### Occurrences",
                "format: position | original | transliteration | exact Extended Strong | morphology code | context gloss",
            ]
            + occ_lines
            + lex_lines
        )
        if total_len <= max_chars or not included_occurrences:
            included_occurrences = test_occs
            included_lexical = test_lex
        else:
            truncated = True
            break

    lines = list(header_lines)
    if truncated:
        lines.append("- note: 查詢結果已達到 max_results 或 max_characters 上限截斷。")
    lines.extend([
        "",
        "### Occurrences",
        "format: position | original | transliteration | exact Extended Strong | morphology code | context gloss",
    ])
    active_verse = None
    for verse, entry in included_occurrences:
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
    if not included_occurrences:
        lines.append("- （沒有符合查詢條件的 occurrence）")
    lines.extend(["", "### Lexicon（依 exact Extended Strong 去重）"])
    if included_lexical:
        for strong_id, definition in included_lexical.items():
            lines.append(f"- {strong_id} | {definition}")
    else:
        lines.append("- （沒有可用 brief lexicon）")
    text = "\n".join(lines).rstrip() + "\n"
    selected_present = tuple(sorted({verse for verse, _entry in included_occurrences}))
    return text, len(included_occurrences), len(included_lexical), selected_present, truncated


def project_step_source(
    path: Path | str,
    *,
    verses: Optional[Iterable[int]] = None,
    strong: Optional[str] = None,
    base_strong: Optional[str] = None,
    word: Optional[str] = None,
    max_results: int = DEFAULT_QUERY_MAX_RESULTS,
    max_characters: int = DEFAULT_QUERY_MAX_CHARS,
    allow_full_chapter: bool = False,
) -> StepProjection:
    path = Path(path)
    raw = path.read_text(encoding="utf-8-sig", errors="strict")
    document = extract_stepbible.parse_rendered_markdown_text(raw)
    text, occurrence_count, lexicon_count, selected, truncated = render_projection(
        document,
        verses=verses,
        strong=strong,
        base_strong=base_strong,
        word=word,
        max_results=max_results,
        max_characters=max_characters,
        allow_full_chapter=allow_full_chapter,
        source_path=path,
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
        truncated=truncated,
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
    canonical = _to_canonical_zh(book)
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
            result = find_nearby_occurrences(
                ROOT, args.book, args.chapter,
                base_strong=args.base_strong, strong=args.strong,
                window=args.window, max_results=args.max_results
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result.get("success") else 1


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
