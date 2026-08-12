#!/usr/bin/env python3
"""Deterministic STEP audit for existing chapter and owned wiki claims.

The audit is intentionally read-only.  It finds high-confidence claims about
Hebrew spelling, transliteration, Strong identifiers and morphology, then
compares them with the chapter-local formal STEP sources.  Lexical/theological
interpretations are labelled rather than judged by a brief lexicon.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import unicodedata
import uuid
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import yaml

try:
    from . import backfill_step_sources, extract_stepbible, step_context
    from .book_paths import book_directory, canonical_book_name
except ImportError:
    import backfill_step_sources
    import extract_stepbible
    import step_context
    from book_paths import book_directory, canonical_book_name


ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = Path("reports") / "step_audit"
CLASSIFICATIONS = (
    "PASS", "REVIEW_LOW", "REVIEW_MEDIUM", "REVIEW_HIGH",
    "UNVERIFIABLE", "INTERPRETIVE",
)
_HEBREW_RUN_RE = re.compile(r"[\u0590-\u05ff\ufb1d-\ufb4f]+")
_STRONG_RE = re.compile(r"(?<![A-Za-z0-9])([HG]\d{1,5}[A-Za-z]?)(?![A-Za-z0-9])", re.I)
_WIKILINK_RE = re.compile(r"(?<!!)\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
_ACCUMULATION_RE = re.compile(
    r"<!--\s*accumulation:([^:>]+):(\d+):(start|end)\s*-->", re.I
)
_URL_RE = re.compile(r"https?://\S+")
_ITALIC_RE = re.compile(
    r"(?<!\*)\*([A-Za-zÀ-ɏʾʿ][A-Za-zÀ-ɏʾʿ'’\- ]{1,50})\*(?!\*)"
)
_PAREN_RE = re.compile(
    r"[（(]([A-Za-zÀ-ɏʾʿ][A-Za-zÀ-ɏʾʿ'’\- ]{1,50})[）)]"
)
_LANGUAGE_CUE_RE = re.compile(
    r"原文|希伯來文|希臘文|音譯|字根|詞形|文法|Strong|字義|意為|可譯", re.I
)
_TRANSLITERATION_CUE_RE = re.compile(r"原文|希伯來文|希臘文|音譯|transliteration", re.I)
_LEXICAL_CLAIM_RE = re.compile(r"字義|字根|意為|意思是|可譯(?:為|作)|原意")
_INTERPRETIVE_RE = re.compile(
    r"從無到有|ex\s+nihilo|三位一體|預表|象徵|救恩|屬靈|神學|末世|"
    r"彌賽亞|專用於神|神獨有|只用於神",
    re.I,
)
_TRANSLITERATION_STOP = {
    "biblehub", "kingcomments", "source", "formal", "collected only",
    "genesis", "exodus", "step bible", "strong", "hebrew", "greek",
    "pass", "review", "high", "medium", "low", "unknown", "note",
    "warning", "quote", "question", "cc by", "old testament",
    "new testament", "ex nihilo", "peace", "father", "prince", "double",
    "dungeon", "outwit", "understood",
}
_ENGLISH_FUNCTION_WORDS = {
    "a", "an", "and", "as", "at", "by", "for", "from", "his", "her",
    "in", "into", "of", "on", "or", "the", "their", "to", "with",
}

_MORPH_CLAIMS = (
    ("qal", re.compile(r"\bQal\b|Qal態", re.I)),
    ("piel", re.compile(r"\bPiel\b|Piel態", re.I)),
    ("pual", re.compile(r"\bPual\b|Pual態", re.I)),
    ("niphal", re.compile(r"\bNiphal\b|Niphal態", re.I)),
    ("hiphil", re.compile(r"\bHiphil\b|Hiphil態", re.I)),
    ("hophal", re.compile(r"\bHophal\b|Hophal態", re.I)),
    ("hithpael", re.compile(r"\bHithpael\b|Hitpael態", re.I)),
    ("perfect", re.compile(r"\bperfect\b|完成式", re.I)),
    ("imperfect", re.compile(r"\bimperfect\b|未完成式", re.I)),
    ("imperative", re.compile(r"\bimperative\b|命令式", re.I)),
    ("infinitive", re.compile(r"\binfinitive\b|不定詞", re.I)),
    ("participle", re.compile(r"\bparticiple\b|分詞", re.I)),
    ("noun", re.compile(r"\bnoun\b|名詞", re.I)),
    ("masculine", re.compile(r"\bmasculine\b|陽性", re.I)),
    ("feminine", re.compile(r"\bfeminine\b|陰性", re.I)),
    ("plural", re.compile(r"\bplural\b|複數", re.I)),
    ("singular", re.compile(r"\bsingular\b|單數", re.I)),
    ("3ms", re.compile(r"\b3ms\b|第三人稱陽性單數", re.I)),
    ("3mp", re.compile(r"\b3mp\b|第三人稱陽性複數", re.I)),
    ("3fs", re.compile(r"\b3fs\b|第三人稱陰性單數", re.I)),
    ("3fp", re.compile(r"\b3fp\b|第三人稱陰性複數", re.I)),
)


@dataclass(frozen=True)
class Occurrence:
    book_code: str
    chapter: int
    verse: int
    position: int
    original: str
    hebrew: str
    transliteration: str
    transliteration_strict: str
    transliteration_loose: str
    strong: str
    base_strong: str
    morphology_raw: str
    morphology: str
    lexicon: str

    def evidence(self) -> str:
        return (
            f"{self.book_code} {self.chapter}:{self.verse} #{self.position} "
            f"{self.original} | {self.transliteration} | {self.strong} | "
            f"{self.morphology_raw or self.morphology}"
        ).rstrip(" |")


@dataclass
class OwnedFile:
    path: Path
    chapters: set[int]
    evidence: set[str]
    is_chapter: bool = False


@dataclass(frozen=True)
class Finding:
    book: str
    chapter: int | None
    chapters: tuple[int, ...]
    file: str
    heading: str
    line: int
    claim: str
    claim_type: str
    step_evidence: tuple[str, ...]
    classification: str
    reason: str
    suggested_manual_action: str
    ownership_evidence: tuple[str, ...]


class EvidenceIndex:
    def __init__(self, occurrences: Iterable[Occurrence]):
        self.occurrences = tuple(occurrences)
        self.by_chapter = defaultdict(list)
        self.hebrew = defaultdict(list)
        self.trans_strict = defaultdict(list)
        self.trans_loose = defaultdict(list)
        self.strong = defaultdict(list)
        self.base_strong = defaultdict(list)
        for occurrence in self.occurrences:
            self.by_chapter[occurrence.chapter].append(occurrence)
            if occurrence.hebrew:
                self.hebrew[(occurrence.chapter, occurrence.hebrew)].append(occurrence)
            if occurrence.transliteration_strict:
                self.trans_strict[(occurrence.chapter, occurrence.transliteration_strict)].append(occurrence)
            if occurrence.transliteration_loose:
                self.trans_loose[(occurrence.chapter, occurrence.transliteration_loose)].append(occurrence)
            if occurrence.strong:
                self.strong[(occurrence.chapter, occurrence.strong)].append(occurrence)
            if occurrence.base_strong:
                self.base_strong[(occurrence.chapter, occurrence.base_strong)].append(occurrence)
        self.phrases = self._phrase_index()

    def _phrase_index(self):
        phrases = defaultdict(list)
        grouped = defaultdict(list)
        for occurrence in self.occurrences:
            grouped[(occurrence.chapter, occurrence.verse)].append(occurrence)
        for (chapter, _verse), occurrences in grouped.items():
            ordered = sorted(occurrences, key=lambda item: item.position)
            for start in range(len(ordered)):
                joined = ""
                for end in range(start, min(len(ordered), start + 4)):
                    token = ordered[end].transliteration_loose
                    if not token:
                        break
                    joined += token
                    phrases[(chapter, joined)].extend(ordered[start:end + 1])
        return phrases

    @staticmethod
    def _in_chapters(mapping, value, chapters):
        found = []
        for chapter in chapters:
            found.extend(mapping.get((chapter, value), ()))
        return _unique_occurrences(found)

    def hebrew_matches(self, value, chapters):
        return self._in_chapters(self.hebrew, value, chapters)

    def transliteration_matches(self, strict, loose, chapters):
        exact = self._in_chapters(self.trans_strict, strict, chapters)
        if exact:
            return exact, "exact"
        normalized = self._in_chapters(self.trans_loose, loose, chapters)
        if normalized:
            return normalized, "normalized"
        phrase = self._in_chapters(self.phrases, loose, chapters)
        if phrase:
            return phrase, "normalized phrase"
        return [], None

    def strong_matches(self, strong, chapters):
        exact = self._in_chapters(self.strong, strong, chapters)
        if exact:
            return exact, "exact Extended Strong"
        base = extract_stepbible.base_strong(strong)
        base_hits = self._in_chapters(self.base_strong, base, chapters)
        if base_hits and strong == base:
            return base_hits, "base Strong matched Extended Strong occurrence"
        return [], None


def normalize_hebrew(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", str(value))
    return "".join(character for character in decomposed if "א" <= character <= "ת")


def normalize_transliteration_strict(value: str) -> str:
    value = unicodedata.normalize("NFKC", str(value)).casefold()
    value = value.replace("’", "'").replace("ʼ", "'").replace("‘", "'")
    return re.sub(r"\s+", " ", value).strip(" -'")


def normalize_transliteration_loose(value: str) -> str:
    value = unicodedata.normalize("NFKD", str(value)).casefold()
    value = "".join(character for character in value if unicodedata.category(character) != "Mn")
    value = value.replace("ʾ", "").replace("ʿ", "")
    return "".join(character for character in value if "a" <= character <= "z")


def _unique_occurrences(values: Iterable[Occurrence]) -> list[Occurrence]:
    seen = set()
    output = []
    for value in values:
        key = (value.chapter, value.verse, value.position, value.strong)
        if key not in seen:
            seen.add(key)
            output.append(value)
    return output


def _lexicon_hebrew(value: str) -> set[str]:
    return {normalize_hebrew(token) for token in _HEBREW_RUN_RE.findall(value) if normalize_hebrew(token)}


def load_evidence(root: Path, book: str, chapters: Iterable[int]):
    occurrences = []
    receipts = []
    for chapter in chapters:
        path = step_context.find_formal_step_source(root, book, chapter)
        scripture = root / "raw_scripture" / book / f"第{chapter}章.txt"
        count = len(scripture.read_text(encoding="utf-8").splitlines())
        receipts.append(step_context.validate_step_source(
            path, expected_book=book, expected_chapter=chapter,
            scripture_verse_count=count,
        ))
        document = extract_stepbible.parse_rendered_markdown(path)
        for verse in sorted(document.verses):
            for word in sorted(document.verses[verse], key=lambda item: item.position):
                hebrew_forms = {normalize_hebrew(word.word)} | _lexicon_hebrew(word.lexicon_short)
                hebrew_forms.discard("")
                lexicon_transliterations = _PAREN_RE.findall(word.lexicon_short)
                transliterations = [word.transliteration, *lexicon_transliterations]
                for index, transliteration in enumerate(transliterations or [""]):
                    for hebrew in hebrew_forms or {""}:
                        occurrences.append(Occurrence(
                            book_code=document.reference.code,
                            chapter=chapter,
                            verse=verse,
                            position=word.position,
                            original=word.word,
                            hebrew=hebrew,
                            transliteration=transliteration,
                            transliteration_strict=normalize_transliteration_strict(transliteration),
                            transliteration_loose=normalize_transliteration_loose(transliteration),
                            strong=word.main_strong,
                            base_strong=extract_stepbible.base_strong(word.main_strong),
                            morphology_raw=word.morphology_raw,
                            morphology=word.morphology,
                            lexicon=word.lexicon_short,
                        ))
                    if index == 0 and not hebrew_forms:
                        break
    return EvidenceIndex(occurrences), receipts


def _load_link_index(root: Path) -> dict:
    path = root / "util" / "output" / "link_index.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"link index 無法讀取：{path}（{exc}）") from exc


def _resolve_entry_path(root: Path, index: dict, target: str) -> Path | None:
    target = str(target).strip().replace("\\", "/")
    if not target:
        return None
    direct = target.removesuffix(".md")
    candidates = [
        root / f"{direct}.md",
        root / "link_folder" / f"{direct}.md",
    ]
    for candidate in candidates:
        try:
            candidate.resolve().relative_to((root / "link_folder").resolve())
        except ValueError:
            continue
        if candidate.is_file():
            return candidate
    entry = index.get(target)
    if isinstance(entry, dict) and "alias_of" in entry:
        entry = index.get(entry["alias_of"])
    if isinstance(entry, dict) and entry.get("path"):
        path = root / entry["path"]
        if path.is_file():
            return path
    return None


def _yaml_values(value):
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in {"name", "existing_title", "existing_path"}:
                yield key, nested
            elif key == "knowledge_nodes":
                yield from (("knowledge_nodes", item) for item in _scalar_values(nested))
            yield from _yaml_values(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _yaml_values(nested)


def _scalar_values(value):
    if isinstance(value, dict):
        for nested in value.values():
            yield from _scalar_values(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _scalar_values(nested)
    elif isinstance(value, (str, int)):
        yield value


def collect_owned_files(root: Path, book: str, chapters: Iterable[int]):
    chapters = set(chapters)
    book_dir = book_directory(root, book)
    index = _load_link_index(root)
    owned: dict[Path, OwnedFile] = {}

    def add(path: Path | None, chapter: int, evidence: str, *, is_chapter=False):
        if path is None or not path.is_file():
            return
        resolved = path.resolve()
        item = owned.setdefault(resolved, OwnedFile(resolved, set(), set(), is_chapter))
        item.chapters.add(int(chapter))
        item.evidence.add(evidence)
        item.is_chapter = item.is_chapter or is_chapter

    for chapter in sorted(chapters):
        chapter_path = book_dir / f"第{chapter}章.md"
        add(chapter_path, chapter, f"production chapter {book} {chapter}", is_chapter=True)
        text = chapter_path.read_text(encoding="utf-8")
        for target in _WIKILINK_RE.findall(text):
            add(_resolve_entry_path(root, index, target), chapter, f"chapter wikilink: {target}")

        chapter_tmp = book_dir / ".tmp" / f"第{chapter}章"
        for artifact_name in ("link_plan.yaml", "chapter_content.yaml"):
            artifact = chapter_tmp / artifact_name
            if not artifact.is_file():
                continue
            try:
                payload = yaml.safe_load(artifact.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError:
                continue
            for key, value in _yaml_values(payload):
                values = value if isinstance(value, list) else [value]
                for candidate in values:
                    if isinstance(candidate, (dict, list)):
                        continue
                    if key == "existing_path":
                        path = root / str(candidate)
                    elif key in {"name", "existing_title"}:
                        path = _resolve_entry_path(root, index, str(candidate))
                    else:
                        path = _resolve_entry_path(root, index, str(candidate))
                    add(path, chapter, f"{artifact_name}:{key}={candidate}")
        entry_dir = chapter_tmp / "entry_content"
        if entry_dir.is_dir():
            for artifact in entry_dir.glob("*.yaml"):
                try:
                    payload = yaml.safe_load(artifact.read_text(encoding="utf-8")) or {}
                except yaml.YAMLError:
                    continue
                name = payload.get("name") or artifact.stem
                path = _resolve_entry_path(root, index, str(name))
                if path is None and payload.get("type"):
                    candidate = root / "link_folder" / str(payload["type"]) / f"{name}.md"
                    path = candidate if candidate.is_file() else None
                add(path, chapter, f"entry_content:{artifact.name}")

    # Accumulation markers are stronger ownership evidence than a transitive
    # related-entry link.  Scan the link corpus once and retain only this book's
    # selected chapters.
    for path in (root / "link_folder").rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for marker_book, marker_chapter, marker_kind in _ACCUMULATION_RE.findall(text):
            try:
                marker_book = canonical_book_name(marker_book.strip())
            except ValueError:
                continue
            marker_chapter = int(marker_chapter)
            if marker_kind.casefold() == "start" and marker_book == book and marker_chapter in chapters:
                add(path, marker_chapter, f"accumulation marker: {book}:{marker_chapter}")
    return sorted(owned.values(), key=lambda item: item.path.as_posix())


def _line_scope(item: OwnedFile, text: str, book: str, selected: set[int]):
    active = None
    for number, line in enumerate(text.splitlines(), 1):
        marker = _ACCUMULATION_RE.search(line)
        if marker:
            marker_book = canonical_book_name(marker.group(1).strip())
            marker_chapter = int(marker.group(2))
            if marker.group(3).casefold() == "start":
                active = (marker_book, marker_chapter)
            else:
                active = None
            continue
        if item.is_chapter:
            owners = set(item.chapters)
        elif active is None:
            owners = set(item.chapters)
        elif active[0] == book and active[1] in selected:
            owners = {active[1]}
        else:
            owners = set()
        if owners:
            yield number, line, owners


def _transliteration_candidates(line: str, *, heading: bool, original_entry: bool):
    clean = _URL_RE.sub("", line)
    explicit = bool(_TRANSLITERATION_CUE_RE.search(clean))
    candidates = [(value, explicit) for value in _ITALIC_RE.findall(clean)]
    if heading or original_entry or explicit:
        candidates.extend((value, explicit) for value in _PAREN_RE.findall(clean))
    output = []
    seen = {}
    for value, is_explicit in candidates:
        value = re.sub(r"\s+", " ", value).strip()
        strict = normalize_transliteration_strict(value)
        loose = normalize_transliteration_loose(value)
        words = {word.casefold() for word in value.split()}
        if len(loose) < 3 or strict in _TRANSLITERATION_STOP:
            continue
        if value.casefold() in _TRANSLITERATION_STOP:
            continue
        if value.isupper() and len(value) <= 5:
            continue
        if len(words) > 1 and words & _ENGLISH_FUNCTION_WORDS:
            continue
        seen[value] = seen.get(value, False) or is_explicit
    output.extend(seen.items())
    return output


def _strong_candidates(line: str):
    cue = bool(re.search(r"Strong|史特朗|希伯來文|希臘文|原文", line, re.I))
    has_hebrew = bool(_HEBREW_RUN_RE.search(line))
    output = []
    for raw in _STRONG_RE.findall(line):
        digits = re.sub(r"\D", "", raw)
        if cue or has_hebrew or len(digits) >= 3:
            output.append(raw)
    return output


def _evidence(values: Iterable[Occurrence], limit=5) -> tuple[str, ...]:
    return tuple(item.evidence() for item in _unique_occurrences(values)[:limit])


def _levenshtein_one(left: str, right: str) -> bool:
    if abs(len(left) - len(right)) > 1:
        return False
    if left == right:
        return True
    initials_match = left[:1] == right[:1] or {left[:1], right[:1]} == {"q", "k"}
    if not initials_match:
        return False
    if len(left) > len(right):
        left, right = right, left
    if len(left) == len(right):
        return sum(a != b for a, b in zip(left, right)) == 1
    index_left = index_right = differences = 0
    while index_left < len(left) and index_right < len(right):
        if left[index_left] == right[index_right]:
            index_left += 1
            index_right += 1
        else:
            differences += 1
            index_right += 1
            if differences > 1:
                return False
    return True


def _near_transliteration(index: EvidenceIndex, loose: str, chapters: Iterable[int]):
    if len(loose) < 5:
        return []
    return _unique_occurrences(
        occurrence for chapter in chapters for occurrence in index.by_chapter.get(chapter, ())
        if occurrence.transliteration_loose
        and _levenshtein_one(loose, occurrence.transliteration_loose)
    )


def _morph_value(value: str, occurrence: Occurrence):
    raw = occurrence.morphology_raw.casefold()
    expanded = occurrence.morphology.casefold()
    combined = f"{raw} {expanded}"
    if value in {"3ms", "3mp", "3fs", "3fp"}:
        return value in combined
    terms = {
        "qal": "qal", "piel": "piel", "pual": "pual", "niphal": "niphal",
        "hiphil": "hiphil", "hophal": "hophal", "hithpael": "hithpael",
        "perfect": "perfect", "imperfect": "imperfect", "imperative": "imperative",
        "infinitive": "infinitive", "participle": "participle", "noun": "noun",
        "masculine": "masculine", "feminine": "feminine", "plural": "plural",
        "singular": "singular",
    }
    term = terms[value]
    if re.search(rf"\b{re.escape(term)}\b", expanded):
        return True
    # An expanded morphology containing a conflicting member of the same
    # category is sufficient evidence for a deterministic mismatch.  A compact
    # unknown code alone is not.
    categories = (
        {"qal", "piel", "pual", "niphal", "hiphil", "hophal", "hithpael"},
        {"perfect", "imperfect", "imperative", "infinitive", "participle"},
        {"noun"}, {"masculine", "feminine"}, {"plural", "singular"},
    )
    group = next(group for group in categories if value in group)
    if any(re.search(rf"\b{re.escape(other)}\b", expanded) for other in group):
        return False
    if value == "qal" and ("v-qal" in combined or re.search(r"\bhv? q", combined)):
        return True
    return None


def _anchor_occurrences(index: EvidenceIndex, line: str, chapters, transliterations):
    anchored = []
    for token in _HEBREW_RUN_RE.findall(line):
        anchored.extend(index.hebrew_matches(normalize_hebrew(token), chapters))
    for raw in _strong_candidates(line):
        strong = extract_stepbible.normalize_strong(raw)
        if not extract_stepbible.is_step_control_strong(strong):
            matches, _mode = index.strong_matches(strong, chapters)
            anchored.extend(matches)
    for raw in transliterations:
        matches, _mode = index.transliteration_matches(
            normalize_transliteration_strict(raw),
            normalize_transliteration_loose(raw), chapters,
        )
        anchored.extend(matches)
    return _unique_occurrences(anchored)


def _finding(
    *, book, owners, relative, heading, line_number, claim, claim_type,
    evidence, classification, reason, action, ownership,
):
    ordered = tuple(sorted(owners))
    return Finding(
        book=book,
        chapter=ordered[0] if len(ordered) == 1 else None,
        chapters=ordered,
        file=relative,
        heading=heading,
        line=line_number,
        claim=claim.strip(),
        claim_type=claim_type,
        step_evidence=tuple(evidence),
        classification=classification,
        reason=reason,
        suggested_manual_action=action,
        ownership_evidence=tuple(sorted(ownership)),
    )


def audit_files(root: Path, book: str, selected: Iterable[int], owned, index: EvidenceIndex):
    selected = set(selected)
    findings = []
    seen = set()
    for item in owned:
        relative = item.path.relative_to(root).as_posix()
        text = item.path.read_text(encoding="utf-8")
        heading = item.path.stem
        original_entry = relative.startswith("link_folder/原文/")
        for line_number, line, owners in _line_scope(item, text, book, selected):
            if line.lstrip().startswith("#"):
                heading = line.lstrip("# ").strip() or heading
            transliteration_candidates = _transliteration_candidates(
                line, heading=line.lstrip().startswith("#"), original_entry=original_entry
            )
            transliterations = [value for value, _explicit in transliteration_candidates]
            transliteration_explicit = dict(transliteration_candidates)
            anchors = _anchor_occurrences(index, line, owners, transliterations)

            for token in sorted(set(_HEBREW_RUN_RE.findall(line))):
                normalized = normalize_hebrew(token)
                if not normalized:
                    continue
                matches = index.hebrew_matches(normalized, owners)
                if matches:
                    classification, reason = "PASS", "normalized Hebrew consonants found in chapter-local STEP"
                    action = "none"
                else:
                    strong_anchors = _anchor_occurrences(index, line, owners, transliterations)
                    if strong_anchors:
                        classification = "REVIEW_HIGH"
                        reason = "Hebrew spelling is absent, while another word/Strong on the same line resolves in STEP"
                    else:
                        classification = "UNVERIFIABLE"
                        reason = "normalized Hebrew spelling is outside the owned chapter occurrences and has no direct word/Strong anchor"
                    action = "manually verify the spelling and its chapter/verse ownership only if this global lemma is meant to claim a local occurrence"
                finding = _finding(
                    book=book, owners=owners, relative=relative, heading=heading,
                    line_number=line_number, claim=token, claim_type="hebrew",
                    evidence=_evidence(matches), classification=classification,
                    reason=reason, action=action, ownership=item.evidence,
                )
                key = (relative, line_number, "hebrew", token)
                if key not in seen:
                    seen.add(key); findings.append(finding)

            for raw in transliterations:
                strict = normalize_transliteration_strict(raw)
                loose = normalize_transliteration_loose(raw)
                matches, mode = index.transliteration_matches(strict, loose, owners)
                if mode == "exact":
                    classification, reason, action = "PASS", "case-insensitive transliteration found in STEP", "none"
                elif matches:
                    classification, reason, action = (
                        "REVIEW_LOW", "matches STEP after conservative diacritic/punctuation normalization",
                        "confirm the spelling variant; no automatic content change",
                    )
                else:
                    near = _near_transliteration(index, loose, owners)
                    matches = near
                    explicit = transliteration_explicit.get(raw, False)
                    if near:
                        classification = "REVIEW_LOW"
                        reason = "one-character spelling/romanization difference from a STEP transliteration"
                    elif explicit and anchors:
                        classification = "REVIEW_MEDIUM"
                        reason = "explicit transliteration is absent while another word/Strong on the line resolves in STEP"
                        matches = anchors
                    else:
                        classification = "UNVERIFIABLE"
                        reason = "unmatched romanized/foreign term has no resolvable local word/Strong anchor"
                    action = "manually verify against the cited verse and source convention; do not auto-rewrite"
                finding = _finding(
                    book=book, owners=owners, relative=relative, heading=heading,
                    line_number=line_number, claim=raw, claim_type="transliteration",
                    evidence=_evidence(matches), classification=classification,
                    reason=reason, action=action, ownership=item.evidence,
                )
                key = (relative, line_number, "transliteration", raw.casefold())
                if key not in seen:
                    seen.add(key); findings.append(finding)

            for raw in sorted(set(_strong_candidates(line))):
                strong = extract_stepbible.normalize_strong(raw)
                if extract_stepbible.is_step_control_strong(strong):
                    classification = "UNVERIFIABLE"
                    reason = "H90xx is a STEP control/grammar code, not a lexical Strong identity"
                    matches = []
                    action = "verify whether the content incorrectly presents this control code as a lexicon ID"
                else:
                    matches, mode = index.strong_matches(strong, owners)
                    if matches:
                        classification = "PASS"
                        reason = mode
                        action = "none"
                    elif anchors and any(item.strong for item in anchors):
                        classification = "REVIEW_HIGH"
                        reason = "claimed Strong conflicts with the STEP word anchored on the same line"
                        matches = anchors
                        action = "manually inspect the word-to-Strong pairing; do not auto-rewrite"
                    else:
                        classification = "REVIEW_MEDIUM"
                        reason = "Strong identifier does not occur in the owned chapter STEP sources"
                        action = "verify chapter/verse ownership and the intended Hebrew word"
                finding = _finding(
                    book=book, owners=owners, relative=relative, heading=heading,
                    line_number=line_number, claim=raw, claim_type="strong",
                    evidence=_evidence(matches), classification=classification,
                    reason=reason, action=action, ownership=item.evidence,
                )
                key = (relative, line_number, "strong", strong)
                if key not in seen:
                    seen.add(key); findings.append(finding)

            morph_claims = [name for name, pattern in _MORPH_CLAIMS if pattern.search(line)]
            if morph_claims and (_LANGUAGE_CUE_RE.search(line) or anchors):
                if not anchors:
                    classification = "UNVERIFIABLE"
                    reason = "high-confidence morphology phrase detected but no word/Strong anchor could be resolved"
                    evidence = ()
                else:
                    evaluations = [
                        tuple(_morph_value(claim, occurrence) for claim in morph_claims)
                        for occurrence in anchors
                    ]
                    if any(all(value is True for value in row) for row in evaluations):
                        classification = "PASS"
                        reason = "all explicit morphology attributes match a STEP occurrence"
                    elif any(value is not None for row in evaluations for value in row):
                        classification = "REVIEW_HIGH"
                        reason = "explicit morphology attributes conflict with anchored STEP morphology"
                    else:
                        classification = "UNVERIFIABLE"
                        reason = "STEP morphology code cannot be deterministically expanded for this claim"
                    evidence = _evidence(anchors)
                action = "manually inspect the exact occurrence morphology; do not infer theology from morphology"
                claim = ", ".join(morph_claims)
                finding = _finding(
                    book=book, owners=owners, relative=relative, heading=heading,
                    line_number=line_number, claim=claim, claim_type="morphology",
                    evidence=evidence, classification=classification,
                    reason=reason, action=action, ownership=item.evidence,
                )
                key = (relative, line_number, "morphology", claim)
                if key not in seen:
                    seen.add(key); findings.append(finding)

            language_anchor = bool(anchors or _HEBREW_RUN_RE.search(line) or transliterations)
            if language_anchor and _INTERPRETIVE_RE.search(line):
                finding = _finding(
                    book=book, owners=owners, relative=relative, heading=heading,
                    line_number=line_number, claim=line.strip(), claim_type="lexical_interpretation",
                    evidence=_evidence(anchors), classification="INTERPRETIVE",
                    reason="the claim is exegetical/theological and must not be adjudicated by STEP lexicon",
                    action="retain for human interpretive review only if desired; STEP absence is not a failure",
                    ownership=item.evidence,
                )
                key = (relative, line_number, "lexical_interpretation", line.strip())
                if key not in seen:
                    seen.add(key); findings.append(finding)
            elif language_anchor and _LEXICAL_CLAIM_RE.search(line):
                finding = _finding(
                    book=book, owners=owners, relative=relative, heading=heading,
                    line_number=line_number, claim=line.strip(), claim_type="lexical_meaning",
                    evidence=_evidence(anchors), classification="UNVERIFIABLE",
                    reason="brief lexicon provides a possible semantic range, not automatic contextual meaning",
                    action="only review a demonstrable word/Strong mismatch; do not treat lexicon wording as a verdict",
                    ownership=item.evidence,
                )
                key = (relative, line_number, "lexical_meaning", line.strip())
                if key not in seen:
                    seen.add(key); findings.append(finding)
    return findings


def _atomic_write_if_changed(path: Path, data: bytes) -> bool:
    if path.is_file() and path.read_bytes() == data:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    part = path.with_name(f".{path.name}.{os.getpid()}.{uuid.uuid4().hex}.part")
    try:
        part.write_bytes(data)
        os.replace(part, path)
    finally:
        part.unlink(missing_ok=True)
    return True


def _book_slug(book: str) -> str:
    filename = extract_stepbible.stepbible_filename(book, 1)
    return filename.removeprefix("stepbible_").rsplit("_", 1)[0]


def render_summary(report: dict) -> str:
    counts = report["classifications"]
    lines = [
        f"# {report['book']} STEP Original-Language Audit",
        "",
        f"- chapters: {len(report['chapters'])}",
        f"- production files scanned: {report['production_files_scanned']}",
        f"- claims detected: {report['claims_detected']}",
        f"- STEP verses / words: {report['step_verses']} / {report['step_words']}",
        "",
        "| Classification | Count |",
        "|---|---:|",
    ]
    lines.extend(f"| {classification} | {counts.get(classification, 0)} |" for classification in CLASSIFICATIONS)
    lines.extend([
        "",
        "> Boundary: STEP directly verifies spelling, occurrence, Strong and high-confidence morphology. "
        "It does not decide contextual meaning, exegesis or theology.",
        "",
        "## REVIEW queue",
        "",
    ])
    for classification in ("REVIEW_HIGH", "REVIEW_MEDIUM", "REVIEW_LOW", "UNVERIFIABLE", "INTERPRETIVE"):
        matches = [item for item in report["findings"] if item["classification"] == classification]
        lines.append(f"### {classification} ({len(matches)})")
        lines.append("")
        if not matches:
            lines.append("- （none）")
            lines.append("")
            continue
        for item in matches:
            location = f"{item['file']}:{item['line']}"
            evidence = "; ".join(item["step_evidence"]) or "no direct STEP occurrence"
            lines.extend([
                f"- **{location} — {item['heading']}**",
                f"  - chapter ownership: {item['chapters']}",
                f"  - type / claim: {item['claim_type']} — {item['claim']}",
                f"  - STEP: {evidence}",
                f"  - reason: {item['reason']}",
                f"  - manual action: {item['suggested_manual_action']}",
            ])
        lines.append("")
    lines.extend([
        "## Safety",
        "",
        "No production chapter, link_folder, commentary raw, or commentary read-log content was modified.",
        "",
    ])
    return "\n".join(lines)


def run_audit(
    book: str,
    *,
    chapters: str | Iterable[int] | None = None,
    root: Path = ROOT,
    dry_run: bool = False,
    write_reports: bool = True,
) -> dict:
    root = Path(root).resolve()
    started = time.perf_counter()
    canonical, _book_dir, _scripture, _expected, selected = backfill_step_sources.select_chapters(
        root, book, chapters
    )
    before = backfill_step_sources.safety_snapshot(root, canonical, selected)
    evidence, receipts = load_evidence(root, canonical, selected)
    owned = collect_owned_files(root, canonical, selected)
    findings = audit_files(root, canonical, selected, owned, evidence)
    after = backfill_step_sources.safety_snapshot(root, canonical, selected)
    safety = backfill_step_sources.compare_snapshots(before, after)
    counts = Counter(item.classification for item in findings)
    report = {
        "version": 1,
        "book": canonical,
        "chapters": selected,
        "production_files_scanned": len(owned),
        "chapter_files_scanned": sum(item.is_chapter for item in owned),
        "owned_link_files_scanned": sum(not item.is_chapter for item in owned),
        "claims_detected": len(findings),
        "classifications": {classification: counts.get(classification, 0) for classification in CLASSIFICATIONS},
        "step_verses": sum(item["verses"] for item in receipts),
        "step_words": sum(item["words"] for item in receipts),
        "duration_seconds": round(time.perf_counter() - started, 3),
        "scope": [
            {
                "file": item.path.relative_to(root).as_posix(),
                "chapters": sorted(item.chapters),
                "ownership_evidence": sorted(item.evidence),
            }
            for item in owned
        ],
        "safety": {
            "before": before.summary(),
            "after": after.summary(),
            **safety,
        },
        "findings": [asdict(item) for item in findings],
    }
    if not safety["byte_identical"]:
        raise RuntimeError(f"audit safety fingerprint changed: {safety['differences'][:5]}")
    if write_reports and not dry_run:
        slug = _book_slug(canonical)
        json_path = root / REPORT_DIR / f"{slug}_findings.json"
        summary_path = root / REPORT_DIR / f"{slug}_summary.md"
        _atomic_write_if_changed(
            json_path,
            (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        )
        _atomic_write_if_changed(summary_path, render_summary(report).encode("utf-8"))
        report["json_report"] = json_path.relative_to(root).as_posix()
        report["markdown_report"] = summary_path.relative_to(root).as_posix()
    return report


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only deterministic audit of existing original-language claims"
    )
    parser.add_argument("book")
    parser.add_argument("--chapters", help="章號，例如 1-10 或 1,3,5-8；省略＝整卷")
    parser.add_argument("--dry-run", action="store_true", help="執行完整 audit 但不寫 reports")
    return parser


def main(argv=None) -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")
    args = build_arg_parser().parse_args(argv)
    try:
        report = run_audit(args.book, chapters=args.chapters, dry_run=args.dry_run)
    except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1
    print(f"{report['book']} STEP Original-Language Audit")
    print(f"chapters: {len(report['chapters'])}")
    print(f"production files scanned: {report['production_files_scanned']}")
    print(f"claims detected: {report['claims_detected']}")
    for classification in CLASSIFICATIONS:
        print(f"{classification}: {report['classifications'][classification]}")
    print("No production content modified.")
    if report.get("markdown_report"):
        print(f"reports: {report['markdown_report']} / {report['json_report']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
