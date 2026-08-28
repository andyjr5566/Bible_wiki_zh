#!/usr/bin/env python3
"""準備並安全套用 link_folder 的章節累積資料。"""
import argparse
import difflib
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

import yaml

try:
    from .book_paths import BOOK_NUMBERS, book_directory, canonical_book_name, chapter_link
    from . import console
except ImportError:
    from book_paths import BOOK_NUMBERS, book_directory, canonical_book_name, chapter_link
    import console

ROOT = Path(__file__).resolve().parent.parent
BOOK_ALIASES = {"約書亞記": "約書亞記"}

REVIEW_SCHEMA_VERSION = 2
REVIEW_BASELINE_FILENAME = "link_update_review_baseline.yaml"
REVIEW_DECISIONS = {"keep", "update"}
MIN_REVIEW_REASON_LENGTH_V1 = 8
REVIEW_KEEP_BASIS = {
    "definition": {"no_identity_change", "already_covered", "insufficient_evidence"},
    "development": {"already_covered", "single_chapter_only", "insufficient_evidence",
                    "standing_debt"},
}
REVIEW_GUIDANCE_V1 = {
    "definition": (
        "定義回答『這是誰／什麼、如何辨識、範圍與邊界是什麼』；只在本章資料改變或"
        "澄清條目的穩定身分時更新，不得寫成本章事件摘要。"
    ),
    "development": (
        "主題發展是跨章綜合：至少使用兩個章節（可跨卷）的累積，說明推進、轉折、對照或整體意義；"
        "不是逐章累積的加長版，不得把本章 summary／relation 換句話說後貼進來。"
    ),
    "accumulation": (
        "逐章累積只記本章明確資料：summary 是本章重點，relation 是本章與條目的關聯；"
        "每章各自成塊，不負責總體定義或跨章綜合。"
    ),
    "decision_rule": (
        "每個 B 類條目都必須分別填 definition／development 的 keep 或 update 並說明理由；"
        "這是審查義務，不是更新配額；keep 是正常且完整的結果，多數或全部 keep 都可通過。"
        "只有真正新增穩定定義或跨章發展才選 update，否則必須 keep，禁止為了顯得有做事而硬湊。"
    ),
}
REVIEW_GUIDANCE = {
    "review_input": (
        "判斷前先讀同資料夾的 review_evidence.md：它逐條列出目標條目的定義全文、"
        "主題發展段落索引與已累積章清單；段落索引不足以判定時再開條目原檔。"
        "再把本章 summary／relation 與既有內容一起判斷。"
    ),
    "review_evidence": (
        "review_evidence.md 由 prepare 產生，是本章審查的證據檔；"
        "它取代逐一開啟每個條目的讀法，但不取代 already_covered 的逐字舉證。"
    ),
    "definition": (
        "定義回答『這是誰／什麼、如何辨識、範圍與邊界是什麼』；只在本章資料改變或"
        "澄清條目的穩定身分時更新，不得寫成本章事件摘要。"
    ),
    "development": (
        "主題發展是跨章綜合：至少使用兩個章節（可跨卷）的累積，說明推進、轉折、對照或整體意義；"
        "不是逐章累積的加長版，不得把本章 summary／relation 換句話說後貼進來。"
    ),
    "accumulation": (
        "逐章累積只記本章明確資料：summary 是本章重點，relation 是本章與條目的關聯；"
        "每章各自成塊，不負責總體定義或跨章綜合。"
    ),
    "decision_rule": (
        "每個 B 類條目只須分別填 definition／development 的 keep 或 update；"
        "這是審查義務，不是更新配額，全部 keep 也可通過。程式提出 challenge 而仍選 keep 時，"
        "才用受控 basis 代碼；update 則由實際區塊 diff 證明。"
    ),
    "keep_basis": (
        "definition 可用 no_identity_change／already_covered／insufficient_evidence；"
        "development 可用 already_covered／single_chapter_only／insufficient_evidence／standing_debt。"
        "沒有 challenge 時直接填 keep。填 already_covered 必須同時給 covered_by："
        "從該區塊現有內容逐字節錄一句，程式會比對；引不出來就不是 already_covered。"
        "條目本身欠帳（累積過多或主題發展空白）而本章只給了一句帶過的提及時，"
        "填 standing_debt——它會被記進 util/output/development_debt.json 等維護回合處理，"
        "不是把問題抹掉；這種情況不可用 insufficient_evidence。"
    ),
    "signals": (
        "first_in_book=首次進入本卷；definition_blank／development_blank=總體區塊空白；"
        "many_accumulations=新增後超過提醒門檻。signals 只提高注意，不等於必須 update。"
    ),
}


def book_rank(book):
    canonical = BOOK_ALIASES.get(book, book)
    return BOOK_NUMBERS.get(canonical, len(BOOK_NUMBERS) + 1)


_H2_SECTION_RE = re.compile(r"(?ms)^##\s+(.+?)\s*$\n(.*?)(?=^##\s+|\Z)")
_ACCUM_META_RE = re.compile(r"<!-- accumulation:([^:]+):(\d+):start -->")
DEVELOPMENT_STALE_THRESHOLD = 7
_ACCUM_BLOCK_RE = re.compile(r"<!-- accumulation:[^:]+:\d+:start -->")
_DEFINITION_CUE_RE = re.compile(
    r"(?:又稱|亦稱|別名|身分(?:為|是)|指的是|專指|泛指|辨識方式|範圍(?:是|為)|定義為|邊界)"
)
_CROSS_CHAPTER_CUE_RE = re.compile(
    r"(?:既有累積|先前累積|本來只從|本章補上|"
    r"跨章|跨卷|整卷(?:書|本書)|全書層級|形成.{0,12}(?:對照|推進|轉折))"
)


def _squeeze(text):
    """Collapse all whitespace so a quoted anchor survives re-wrapping."""
    return "".join(str(text).split())


def _section_body(text, heading):
    """Return one H2 section body without its heading."""
    for match in _H2_SECTION_RE.finditer(text):
        if match.group(1).strip() == heading:
            return match.group(2).strip()
    return ""


def _review_signals(text, book, chapter):
    """Return compact deterministic signals; the semantic verdict stays with the agent."""
    blocks = _ACCUM_META_RE.findall(text)
    marker = (book, str(chapter))
    after_count = len(blocks) + (0 if marker in blocks else 1)
    books = {canonical_book_name(block_book) for block_book, _ in blocks}
    signals = []
    if book not in books:
        signals.append("first_in_book")
    if not _section_body(text, "定義"):
        signals.append("definition_blank")
    if not _section_body(text, "主題發展"):
        signals.append("development_blank")
    if after_count > DEVELOPMENT_STALE_THRESHOLD:
        signals.append("many_accumulations")
    return signals, len(blocks), after_count


def _review_payload(text, book, chapter):
    signals, before_count, after_count = _review_signals(text, book, chapter)
    return {
        "signals": signals,
        "accumulation_count": [before_count, after_count],
        "definition": "pending",
        "development": "pending",
    }


def _review_baseline_entry(update, text, review=None):
    entry = {
        "title": str(update.get("title", "")),
        "path": str(update.get("path", "")),
        "definition": _section_body(text, "定義"),
        "development": _section_body(text, "主題發展"),
    }
    if review is not None:
        entry["signals"] = list(review.get("signals") or [])
        entry["accumulation_count"] = list(review.get("accumulation_count") or [])
    return entry


REVIEW_EVIDENCE_FILENAME = "review_evidence.md"
# 短定義直接給全文；長定義改給索引，需要逐字內容時開條目原檔。
EVIDENCE_DEFINITION_FULL_LIMIT = 400
_BOLD_LEAD_RE = re.compile(r"^\*\*(.+?)\*\*")
_PARAGRAPH_SPLIT_RE = re.compile(r"\n\s*\n")


def _opening_sentence(text, limit=64):
    """Return a paragraph label: its bold lead-in if it has one, else its opening clause."""
    flat = " ".join(str(text).split())
    lead = _BOLD_LEAD_RE.match(flat)
    if lead and len(lead.group(1)) <= limit:
        return lead.group(1)
    match = re.search(r"[。！？]", flat)
    if match and match.end() <= limit:
        return flat[: match.end()]
    return flat[:limit] + ("⋯" if len(flat) > limit else "")


EVIDENCE_OUTLINE_MAX_ROWS = 8


def _section_outline(body):
    """Index one section: its H3 headings when it has them, else its openings.

    A mature entry keeps growing paragraphs, so a per-paragraph index grows with
    it.  Headings already name what each block is about, so when they exist they
    are the whole index; headingless sections fall back to openings, capped.
    """
    chunks = [c.strip() for c in _PARAGRAPH_SPLIT_RE.split(str(body).strip()) if c.strip()]
    headings = [c for c in chunks if c.startswith("#")]
    if headings:
        outline = [("### " + c.lstrip("# ").strip(), 0) for c in headings]
        prose = [c for c in chunks if not c.startswith("#")]
        if prose:
            outline.append((
                f"（小標題以外另有 {len(prose)} 段散文，共 "
                f"{sum(len(_squeeze(c)) for c in prose)} 字；要內文請開條目原檔）", 0))
        return outline
    outline = [(_opening_sentence(c), len(_squeeze(c))) for c in chunks[:EVIDENCE_OUTLINE_MAX_ROWS]]
    rest = chunks[EVIDENCE_OUTLINE_MAX_ROWS:]
    if rest:
        outline.append((
            f"（另有 {len(rest)} 段，共 {sum(len(_squeeze(c)) for c in rest)} 字未列）", 0))
    return outline


def _accumulated_labels(text):
    return [f"{book}{chapter}" for book, chapter in _ACCUM_META_RE.findall(text)]


def _format_accumulated(text):
    """Group accumulated chapters by book so a 35-chapter entry stays one short line."""
    grouped = {}
    for book, chapter in _ACCUM_META_RE.findall(text):
        grouped.setdefault(book, []).append(chapter)
    return " ／ ".join(f"{book} {','.join(chapters)}" for book, chapters in grouped.items())


def _definition_evidence(body):
    """Short definitions ship whole; long ones ship as an index of their claims."""
    text = body.strip()
    if not text:
        return "### 定義：空白", []
    size = len(_squeeze(text))
    if size <= EVIDENCE_DEFINITION_FULL_LIMIT:
        return f"### 定義（{size} 字，全文）", [text]
    paragraphs = [c.strip() for c in _PARAGRAPH_SPLIT_RE.split(text) if c.strip()]
    lines = [paragraphs[0]] if paragraphs else []
    for chunk in paragraphs[1:]:
        if chunk.startswith("#") or chunk.startswith("|"):
            continue
        lines.append(f"- {_opening_sentence(chunk)}　〔{len(_squeeze(chunk))} 字〕")
    header = f"### 定義（{size} 字，索引；要逐字內容請開條目原檔）"
    return header, lines


def review_evidence_markdown(book, chapter, entries):
    """Render the compact review evidence: definition claims, development outlines."""
    lines = [
        f"# B 類累積審查證據：{book} 第{chapter}章",
        "",
        "判 overview_review 前讀這一份，不必逐一開啟每個目標條目。",
        f"定義 {EVIDENCE_DEFINITION_FULL_LIMIT} 字以內給全文，較長的給主張索引"
        "（首段全文＋其餘段落的粗體導語或開頭）；主題發展有小標題時只給小標題，"
        f"沒有小標題才給段落開頭（上限 {EVIDENCE_OUTLINE_MAX_ROWS} 段）。",
        "索引是分流用的：只要判斷不是單純 keep，就開條目原檔再確認。",
        "填 already_covered 一定要開檔逐字節錄 covered_by；"
        "條目本身欠帳而本章只有一句帶過的提及，填 standing_debt（會記進欠帳清單）。",
        "",
    ]
    for entry in entries:
        labels = entry["accumulated"]
        lines.append(f"## {entry['title']}")
        lines.append(
            "`{}`　signals：{}　累積 {} 章：{}".format(
                entry["path"],
                "、".join(entry["signals"]) or "無",
                len(labels),
                entry.get("accumulated_grouped") or "（無）",
            )
        )
        lines.append("")
        header, body = _definition_evidence(entry["definition"])
        lines.append(header)
        lines.extend(body)
        lines.append("")
        outline = _section_outline(entry["development"])
        if outline:
            total = len(_squeeze(entry["development"]))
            lines.append(f"### 主題發展（{len(outline)} 段／{total} 字，段落索引）")
            for text, size in outline:
                lines.append(f"- {text}" + (f"　〔{size} 字〕" if size else ""))
        else:
            lines.append("### 主題發展：空白")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def plan_updates(book, chapter):
    base = book_directory(ROOT, book) / ".tmp" / f"第{chapter}章"
    plan_yaml = base / "link_plan.yaml"
    plan_md = base / "link_plan.md"
    updates = []
    if plan_yaml.exists():  # orchestrator（run_chapter/resolver）的結構化輸出優先
        data = yaml.safe_load(plan_yaml.read_text(encoding="utf-8")) or {}
        for item in data.get("B_needs_update", []):
            updates.append({
                "title": item.get("existing_title") or item.get("name", ""),
                "path": item.get("existing_path", ""),
                "summary": "",
                "relation": "",
            })
    elif plan_md.exists():
        section = None
        for line in plan_md.read_text(encoding="utf-8").splitlines():
            if line.startswith("## "):
                section = line[3:]
                continue
            if not section or not section.startswith("B."):
                continue
            match = re.match(r"- \[\[(.+?)\]\] → ([^（]+)", line)
            if match:
                updates.append({
                    "title": match.group(1),
                    "path": match.group(2).strip(),
                    "summary": "",
                    "relation": "",
                })
    else:
        raise FileNotFoundError(plan_yaml)
    return {
        "book": book,
        "chapter": int(chapter),
        "updates": updates,
    }


def write_review_evidence(book, chapter):
    """(Re)generate the review evidence file from the manifest's current targets."""
    chapter_dir = book_directory(ROOT, book) / ".tmp" / f"第{chapter}章"
    manifest = chapter_dir / "link_updates.yaml"
    if manifest.exists():
        data = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
        updates = data.get("updates") or []
    else:
        updates = plan_updates(book, chapter)["updates"]
    rows = []
    for update in updates:
        text = _entry_path(ROOT, update["path"]).read_text(encoding="utf-8")
        signals, _, _ = _review_signals(text, book, int(chapter))
        rows.append({
            "title": str(update.get("title", "")),
            "path": str(update.get("path", "")),
            "signals": signals,
            "accumulated": _accumulated_labels(text),
            "accumulated_grouped": _format_accumulated(text),
            "definition": _section_body(text, "定義"),
            "development": _section_body(text, "主題發展"),
        })
    path = chapter_dir / REVIEW_EVIDENCE_FILENAME
    path.write_text(review_evidence_markdown(book, int(chapter), rows), encoding="utf-8")
    return path, len(rows)


def prepare(book, chapter):
    console.utf8_stdio()
    chapter_dir = book_directory(ROOT, book) / ".tmp" / f"第{chapter}章"
    output = chapter_dir / "link_updates.yaml"
    baseline_path = chapter_dir / REVIEW_BASELINE_FILENAME
    evidence_guard = chapter_dir / REVIEW_EVIDENCE_FILENAME
    existing = [
        path for path in (output, baseline_path, evidence_guard) if path.exists()
    ]
    if existing:
        raise FileExistsError(
            f"{existing[0]} 已存在；避免覆蓋人工內容或審查基線"
        )
    data = plan_updates(book, chapter)
    baselines = []
    evidence_rows = []
    for update in data["updates"]:
        path = _entry_path(ROOT, update["path"])
        text = path.read_text(encoding="utf-8")
        review = _review_payload(text, book, int(chapter))
        update["overview_review"] = review
        baselines.append(_review_baseline_entry(update, text, review))
        evidence_rows.append({
            "title": str(update.get("title", "")),
            "path": str(update.get("path", "")),
            "signals": list(review.get("signals") or []),
            "accumulated": _accumulated_labels(text),
            "accumulated_grouped": _format_accumulated(text),
            "definition": _section_body(text, "定義"),
            "development": _section_body(text, "主題發展"),
        })
    data = {
        "book": data["book"],
        "chapter": data["chapter"],
        "review_schema_version": REVIEW_SCHEMA_VERSION,
        "review_baseline": REVIEW_BASELINE_FILENAME,
        "review_guidance": REVIEW_GUIDANCE,
        "updates": data["updates"],
    }
    baseline = {
        "review_schema_version": REVIEW_SCHEMA_VERSION,
        "book": book,
        "chapter": int(chapter),
        "entries": baselines,
    }
    baseline_path.write_text(
        yaml.safe_dump(baseline, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    output.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_style='"'), encoding="utf-8"
    )
    evidence_path = chapter_dir / REVIEW_EVIDENCE_FILENAME
    evidence_path.write_text(
        review_evidence_markdown(book, int(chapter), evidence_rows), encoding="utf-8"
    )
    print(f"✅ 已建立更新骨架：{output}（{len(data['updates'])} 條）")
    print(f"📖 先讀審查證據檔：{evidence_path}")
    print("   它給定義全文、主題發展段落索引與已累積章清單；索引不足以判定時再開條目原檔。")
    print(
        "⚠️ 套用前必須逐條填 overview_review：definition／development 各自選 "
        "keep 或 update；keep 合法，不得把逐章 summary／relation 換句話說"
        "塞進定義或主題發展。程式提出 challenge 而仍 keep 時才填短 basis 代碼。"
    )
    print(
        "   development=update 時，synthesis_scope 至少列本章與另一章（書卷:章），"
        "並先修改條目對應區塊；preview 會驗證區塊確實改變並顯示 diff。"
    )
    return output


def render_block(book, chapter, update):
    return (
        f"<!-- accumulation:{book}:{chapter}:start -->\n"
        f"#### {chapter_link(book, chapter)}\n"
        f"- 本章重點：{update['summary'].strip()}\n"
        f"- 與本章關聯：{update['relation'].strip()}\n"
        f"<!-- accumulation:{book}:{chapter}:end -->"
    )


def validate_update(update):
    required_text = ("title", "path", "summary", "relation")
    return [key for key in required_text if not str(update.get(key, "")).strip()]


def _load_review_baselines(manifest, data, book, chapter):
    """Load immutable-at-prepare section snapshots for versioned review manifests."""
    version = data.get("review_schema_version")
    if version is None:
        return None  # Historical manifests remain readable/re-applicable.
    if version not in {1, REVIEW_SCHEMA_VERSION}:
        raise ValueError(
            f"不支援的 review_schema_version：{version}（支援 1、{REVIEW_SCHEMA_VERSION}）"
        )
    expected_guidance = REVIEW_GUIDANCE_V1 if version == 1 else REVIEW_GUIDANCE
    guidance = data.get("review_guidance")
    if not isinstance(guidance, dict) or any(
        guidance.get(key) != value for key, value in expected_guidance.items()
    ):
        raise ValueError(
            "review_guidance 缺漏或被改寫；定義、主題發展、逐章累積的定位不可移除，"
            "請重新 prepare"
        )
    raw_name = data.get("review_baseline")
    if not isinstance(raw_name, str) or Path(raw_name).name != raw_name:
        raise ValueError("review_baseline 必須是與 link_updates.yaml 同資料夾的單一檔名")
    baseline_path = (manifest.parent / raw_name).resolve()
    if baseline_path.parent != manifest.parent.resolve() or not baseline_path.is_file():
        raise ValueError(f"找不到 overview review 基線：{raw_name}；請重新 prepare")
    baseline = yaml.safe_load(baseline_path.read_text(encoding="utf-8")) or {}
    if (
        baseline.get("review_schema_version") != version
        or canonical_book_name(str(baseline.get("book", ""))) != book
        or baseline.get("chapter") != chapter
    ):
        raise ValueError("overview review 基線的版本或 book/chapter 與 manifest 不一致")
    entries = baseline.get("entries")
    if not isinstance(entries, list):
        raise ValueError("overview review 基線缺少 entries 清單")
    out = {}
    for entry in entries:
        if not isinstance(entry, dict) or not str(entry.get("path", "")).strip():
            raise ValueError("overview review 基線含無效條目")
        out[str(entry["path"])] = entry
    return version, out


def _added_section_text(before, after):
    before_lines = before.splitlines()
    after_lines = after.splitlines()
    added = []
    matcher = difflib.SequenceMatcher(a=before_lines, b=after_lines, autojunk=False)
    for tag, _i1, _i2, j1, j2 in matcher.get_opcodes():
        if tag in {"insert", "replace"}:
            added.extend(after_lines[j1:j2])
    return "\n".join(added).strip()


def _normalized_similarity_text(text):
    return re.sub(r"[\W_]+", "", str(text), flags=re.UNICODE).lower()


def _looks_like_accumulation_restatement(added, summary, relation):
    """Catch direct/high-overlap reuse; semantic paraphrases still require human review."""
    sources = [summary, relation, f"{summary}{relation}"]
    pieces = [added] + [piece for piece in re.split(r"\n\s*\n|\n", added) if piece.strip()]
    for piece in pieces:
        piece_norm = _normalized_similarity_text(piece)
        if len(piece_norm) < 20:
            continue
        for source in sources:
            source_norm = _normalized_similarity_text(source)
            if len(source_norm) < 20:
                continue
            shorter, longer = sorted((piece_norm, source_norm), key=len)
            if len(shorter) >= 24 and shorter in longer:
                return True
            if difflib.SequenceMatcher(
                a=piece_norm, b=source_norm, autojunk=False
            ).ratio() >= 0.72:
                return True
    return False


def _current_chapter_heading(added, book, chapter):
    short_book = book[0]
    heading = re.compile(
        rf"^#{{3,6}}\s*(?:(?:{re.escape(book)}|{re.escape(short_book)})\s*)?"
        rf"(?:第\s*)?{chapter}\s*章?(?:\s*[:：].*)?\s*$"
    )
    return next((line.strip() for line in added.splitlines() if heading.match(line.strip())), None)


def _validated_synthesis_scope(raw_scope, book, chapter):
    if not isinstance(raw_scope, list):
        raise ValueError("development.synthesis_scope 必須是清單，例如 [民數記:20, 民數記:35]")
    refs = []
    for raw in raw_scope:
        match = re.fullmatch(r"\s*([^:：]+)[:：](\d+)\s*", str(raw))
        if not match:
            raise ValueError(
                "development.synthesis_scope 每項須為「書卷:章」，例如 民數記:20"
            )
        scope_book = canonical_book_name(match.group(1).strip())
        if scope_book not in BOOK_NUMBERS or int(match.group(2)) < 1:
            raise ValueError(f"development.synthesis_scope 含無效章節：{raw}")
        refs.append(f"{scope_book}:{int(match.group(2))}")
    refs = list(dict.fromkeys(refs))
    current = f"{book}:{chapter}"
    if current not in refs or len(refs) < 2:
        raise ValueError(
            "development=update 必須在 synthesis_scope 列出本章與至少另一章；"
            "主題發展是跨章綜合，不是本章累積的改寫"
        )
    return refs


def _review_challenges(update, baseline):
    """Return focused machine challenges; signals alone never force an update."""
    signals = set(baseline.get("signals") or [])
    counts = baseline.get("accumulation_count") or []
    after_count = counts[1] if len(counts) > 1 and isinstance(counts[1], int) else 0
    content = f"{update.get('summary', '')}\n{update.get('relation', '')}"
    challenges = {"definition": [], "development": []}
    if "definition_blank" in signals:
        challenges["definition"].append("definition_blank")
    if _DEFINITION_CUE_RE.search(content):
        challenges["definition"].append("identity_language")
    if "development_blank" in signals and after_count >= 2:
        challenges["development"].append("development_blank_with_history")
    if "many_accumulations" in signals:
        challenges["development"].append("many_accumulations")
    if _CROSS_CHAPTER_CUE_RE.search(content):
        challenges["development"].append("cross_chapter_language")
    return challenges


def _v2_verdict(verdict, title, key, heading, challenges, before):
    """Parse the compact v2 verdict and validate a challenged keep basis."""
    if isinstance(verdict, str):
        decision = verdict.strip().lower()
        basis = ""
        raw_scope = None
        covered_by = ""
    elif isinstance(verdict, dict):
        if str(verdict.get("reason", "")).strip():
            raise ValueError(
                f"{title} 的 {heading} 使用 schema v2，不要填 reason；"
                "只填 keep/update，程式提出 challenge 且仍 keep 時才填 basis"
            )
        decision = str(verdict.get("decision", "")).strip().lower()
        basis = str(verdict.get("basis", "")).strip().lower()
        raw_scope = verdict.get("synthesis_scope")
        covered_by = str(verdict.get("covered_by", "")).strip()
    else:
        raise ValueError(
            f"{title} 的 overview_review.{key} 必須是 keep/update，"
            "或含 decision 的物件"
        )
    if decision not in REVIEW_DECISIONS:
        raise ValueError(
            f"{title} 的 {heading} 尚未完成判斷：必須填 keep 或 update"
        )
    allowed = REVIEW_KEEP_BASIS[key]
    if basis and basis not in allowed:
        raise ValueError(
            f"{title} 的 {heading} basis「{basis}」不合法；可用：{', '.join(sorted(allowed))}"
        )
    if decision == "update":
        if basis:
            raise ValueError(f"{title} 的 {heading} 已選 update，不需要 basis")
        if covered_by:
            raise ValueError(f"{title} 的 {heading} 已選 update，不需要 covered_by")
        return decision, "", raw_scope, ""
    if challenges and not basis:
        raise ValueError(
            f"{title} 的 {heading} 有程式 challenge（{', '.join(challenges)}）；"
            "若仍 keep，請改填 {decision: keep, basis: 受控代碼}，不要寫理由作文"
        )
    if not challenges and basis:
        raise ValueError(f"{title} 的 {heading} 沒有 challenge，直接填 keep 即可，不需要 basis")
    if basis == "already_covered":
        if not before.strip():
            raise ValueError(f"{title} 的 {heading} 目前空白，basis 不能填 already_covered")
        if not covered_by:
            raise ValueError(
                f"{title} 的 {heading} 填 already_covered 時必須加 covered_by："
                "從該區塊現有內容逐字節錄一句（程式會比對）；引不出來就不是 already_covered"
            )
        if _squeeze(covered_by) not in _squeeze(before):
            raise ValueError(
                f"{title} 的 {heading} covered_by 在該區塊找不到逐字對應；"
                "already_covered 不成立，請改判 update 或其他 basis"
            )
    elif covered_by:
        raise ValueError(
            f"{title} 的 {heading} 只有 basis=already_covered 才填 covered_by"
        )
    debt_signals = [c for c in challenges
                    if c in ("many_accumulations", "development_blank_with_history")]
    if key == "development" and basis == "standing_debt" and not debt_signals:
        raise ValueError(
            f"{title} 的 {heading} 沒有存量欠帳訊號（many_accumulations／"
            "development_blank_with_history），basis 不能填 standing_debt"
        )
    if key == "development" and basis == "insufficient_evidence" and debt_signals:
        raise ValueError(
            f"{title} 的 {heading} 有存量欠帳訊號（{', '.join(debt_signals)}）；"
            "insufficient_evidence 會把欠帳抹掉，請改填 standing_debt（會被記進欠帳清單），"
            "或改判 update／already_covered／single_chapter_only"
        )
    if key == "development" and basis == "single_chapter_only" and "cross_chapter_language" in challenges:
        raise ValueError(
            f"{title} 的 relation/summary 已出現跨章綜合訊號，"
            "development basis 不能填 single_chapter_only；請重新判斷 update、"
            "already_covered 或 insufficient_evidence"
        )
    if raw_scope not in (None, []):
        raise ValueError(f"{title} 的主題發展選 keep，不需要 synthesis_scope")
    return decision, basis, raw_scope, covered_by


def _section_diff(before, after, heading):
    if before == after:
        return ""
    return "\n".join(difflib.unified_diff(
        before.splitlines(),
        after.splitlines(),
        fromfile=f"prepare 時的 {heading}",
        tofile=f"目前的 {heading}",
        lineterm="",
    ))


def _validate_overview_review(
    update, current_text, baseline, book, chapter,
    review_schema_version=REVIEW_SCHEMA_VERSION,
):
    title = str(update.get("title", "?"))
    review = update.get("overview_review")
    if not isinstance(review, dict):
        raise ValueError(
            f"{title} 缺少 overview_review；請分別判斷定義與主題發展，keep 合法但不可略過"
        )
    if review_schema_version == 1:
        challenges = {"definition": [], "development": []}
        result = {
            "review_attention": review.get("review_attention", "normal"),
            "trigger_reasons": list(review.get("trigger_reasons") or []),
        }
    else:
        signals = list(baseline.get("signals") or [])
        challenges = _review_challenges(update, baseline)
        result = {
            "review_attention": "high" if signals or any(challenges.values()) else "normal",
            "signals": signals,
            "challenges": challenges,
        }
    for key, heading in (("definition", "定義"), ("development", "主題發展")):
        verdict = review.get(key)
        before = str(baseline.get(key, ""))
        if review_schema_version == 1:
            if not isinstance(verdict, dict):
                raise ValueError(f"{title} 的 overview_review.{key} 必須是物件")
            decision = str(verdict.get("decision", "")).strip().lower()
            if decision not in REVIEW_DECISIONS:
                raise ValueError(
                    f"{title} 的 {heading} 尚未完成判斷：decision 必須是 keep 或 update"
                )
            reason = str(verdict.get("reason", "")).strip()
            if len(reason) < MIN_REVIEW_REASON_LENGTH_V1:
                raise ValueError(
                    f"{title} 的 {heading} 判斷理由過短；請說明本章是否改變穩定身分／"
                    "是否形成跨章發展，不能只填『不用』"
                )
            basis = ""
            covered_by = ""
            raw_scope = verdict.get("synthesis_scope")
        else:
            decision, basis, raw_scope, covered_by = _v2_verdict(
                verdict, title, key, heading, challenges[key], before
            )
        after = _section_body(current_text, heading)
        changed = before != after
        if decision == "update" and not changed:
            raise ValueError(
                f"{title} 的 {heading} 選了 update，但條目中的「## {heading}」沒有改變"
            )
        if decision == "keep" and changed:
            raise ValueError(
                f"{title} 的 {heading} 選了 keep，但條目中的「## {heading}」已被修改；"
                "請把 decision 改為 update，或還原該區塊"
            )
        added = _added_section_text(before, after) if changed else ""
        if decision == "update" and (
            _ACCUM_META_RE.search(added)
            or re.search(r"(?m)^####\s+\[\[[^\]]*第\d+章", added)
            or re.search(r"(?m)^-\s*(?:本章重點|與本章關聯)：", added)
        ):
            raise ValueError(
                f"{title} 的 {heading} 新增內容含逐章累積的標記／標題／欄位；"
                "三個區塊定位不同，不可把累積區塊搬入定義或主題發展"
            )
        if decision == "update" and _looks_like_accumulation_restatement(
            added, update.get("summary", ""), update.get("relation", "")
        ):
            raise ValueError(
                f"{title} 的 {heading} 新增內容與本章 summary／relation 高度重疊；"
                "逐章累積記單章事實，定義記穩定身分，主題發展做跨章綜合，"
                "不可把同一內容換句話說後重複貼入"
            )
        if decision == "update":
            bad_heading = _current_chapter_heading(added, book, chapter)
            if bad_heading:
                raise ValueError(
                    f"{title} 的{heading}新增了單章小標題「{bad_heading}」；"
                    "定義只處理穩定身分，主題發展只做跨章／跨卷綜合，"
                    "兩者都不可另建本章累積的改寫版"
                )
        item = {
            "decision": decision,
            "changed": changed,
            "diff": _section_diff(before, after, heading),
        }
        if review_schema_version == 1:
            item["reason"] = reason
        elif basis:
            item["basis"] = basis
            if covered_by:
                item["covered_by"] = covered_by
        if key == "development" and decision == "update":
            item["synthesis_scope"] = _validated_synthesis_scope(
                raw_scope, book, chapter
            )
        result[key] = item
    return result


def _entry_path(root, raw_path):
    """Resolve an update target, allowing only Markdown entries in link_folder."""
    if not isinstance(raw_path, str) or not raw_path.strip():
        raise ValueError("更新項目的 path 必須是非空字串")
    relative = Path(raw_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"不合法的條目路徑：{raw_path}")
    root = Path(root).resolve()
    link_root = (root / "link_folder").resolve()
    path = (root / relative).resolve()
    if path.suffix.lower() != ".md" or not path.is_relative_to(link_root):
        raise ValueError(f"更新目標必須是 link_folder/ 內的 .md 條目：{raw_path}")
    if not path.is_file():
        raise ValueError(f"找不到條目檔案：{raw_path}")
    return path


def _updated_text(text, book, chapter, update, path):
    """Return one entry's rendered accumulation update without writing it."""
    start = f"<!-- accumulation:{book}:{chapter}:start -->"
    end = f"<!-- accumulation:{book}:{chapter}:end -->"
    block = render_block(book, chapter, update)
    if start in text:
        pattern = re.compile(re.escape(start) + r"[\s\S]*?" + re.escape(end))
        new_text, count = pattern.subn(block, text, count=1)
        if count != 1:
            raise ValueError(f"{path}: 累積標記損壞")
        return new_text

    accumulation = re.search(
        r"^## 按書卷累積\s*$([\s\S]*?)(?=^## (?:主題發展|相關條目|來源依據)\s*$)",
        text, re.M,
    )
    if not accumulation:
        accumulation = re.search(r"^## 按書卷累積\s*$([\s\S]*)", text, re.M)
    if not accumulation:
        raise ValueError(f"{path}: 找不到合法的按書卷累積區")
    section = accumulation.group(1)
    book_heading = re.search(rf"^###\s+{re.escape(book)}\s*$", section, re.M)
    if book_heading:
        following = section[book_heading.end():]
        next_book = re.search(r"^###\s+", following, re.M)
        book_end = (
            accumulation.start(1) + book_heading.end()
            + (next_book.start() if next_book else len(following))
        )
        insertion = book_end
        for marker in re.finditer(
            rf"^<!-- accumulation:{re.escape(book)}:(\d+):start -->",
            section[book_heading.end():(book_heading.end() + (next_book.start() if next_book else len(following)))],
            re.M,
        ):
            if int(marker.group(1)) > chapter:
                insertion = accumulation.start(1) + book_heading.end() + marker.start()
                break
        return text[:insertion].rstrip() + "\n\n" + block + "\n" + text[insertion:].lstrip("\n")

    insertion = accumulation.end(1)
    for heading in re.finditer(r"^###\s+(.+?)\s*$", section, re.M):
        heading_name = canonical_book_name(heading.group(1))
        if BOOK_ALIASES.get(heading_name, heading_name) not in BOOK_NUMBERS:
            continue
        if book_rank(heading_name) > book_rank(book):
            insertion = accumulation.start(1) + heading.start()
            break
    group = f"### {book}\n\n{block}"
    return (
        text[:insertion].rstrip()
        + "\n\n"
        + group
        + "\n\n"
        + text[insertion:].lstrip()
    )


def _development_stale_hint(before_text, after_text):
    """累積區塊數剛跨過門檻、或門檻之上又新增時，提醒回頭檢查條目總體區塊。

    只是提醒（manual_review 性質），不擋 apply：development 是否真的落後累積成長
    要人工讀過才能判斷（見 util/check_development_staleness.py 的討論），這裡只
    用區塊數當機械觸發點，避免每次套用都重複洗版同一句提醒。
    """
    count = len(_ACCUM_BLOCK_RE.findall(after_text))
    if count <= DEVELOPMENT_STALE_THRESHOLD:
        return None
    prev_count = len(_ACCUM_BLOCK_RE.findall(before_text))
    if prev_count == count:
        return None  # 這次套用沒有新增累積區塊，不是本次改動造成的
    return count


def preview_updates(manifest, root=None):
    """Validate every update and return all proposed file changes without writing."""
    manifest = Path(manifest)
    data = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("manifest 頂層必須是物件")
    book, chapter = data.get("book"), data.get("chapter")
    if not book or not isinstance(chapter, int) or chapter < 1:
        raise ValueError("manifest 缺少合法 book/chapter")
    book = canonical_book_name(book)
    if book not in BOOK_NUMBERS:
        raise ValueError(
            f"manifest 的 book「{data.get('book')}」不是合法書卷名；"
            f"應為 _config/bible_books.json 裡的書卷名（如「利未記」），不是資料夾名"
        )
    updates = data.get("updates", [])
    if not isinstance(updates, list):
        raise ValueError("manifest 的 updates 必須是清單")

    review_context = _load_review_baselines(manifest, data, book, chapter)
    review_schema_version = None
    review_baselines = None
    if review_context is not None:
        review_schema_version, review_baselines = review_context
    root = Path(ROOT if root is None else root).resolve()
    operations = []
    for update in updates:
        if not isinstance(update, dict):
            raise ValueError("updates 的每一項必須是物件")
        missing = validate_update(update)
        if missing:
            raise ValueError(f"{update.get('title', '?')} 缺少欄位：{', '.join(missing)}")
        path = _entry_path(root, update["path"])
        text = path.read_text(encoding="utf-8")
        overview_review = None
        if review_baselines is not None:
            baseline = review_baselines.get(str(update["path"]))
            if baseline is None:
                raise ValueError(
                    f"{update.get('title', '?')} 在 overview review 基線中沒有對應 path；"
                    "請重新 prepare"
                )
            if str(baseline.get("title", "")) != str(update.get("title", "")):
                raise ValueError(
                    f"{update.get('title', '?')} 的 overview review 基線 title 不一致；"
                    "請重新 prepare"
                )
            overview_review = _validate_overview_review(
                update, text, baseline, book, chapter, review_schema_version
            )
        new_text = _updated_text(text, book, chapter, update, path)
        operations.append({
            "path": path,
            "relative_path": path.relative_to(root).as_posix(),
            "title": str(update["title"]),
            "before": text,
            "after": new_text,
            "overview_review": overview_review,
        })
    return {"book": book, "chapter": chapter, "operations": operations}


def _stage_text(path, text):
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)
    return Path(name)


def _commit_operations(changes):
    """Stage all files before replacing any; attempt rollback on an OS failure."""
    staged = []
    replaced = []
    try:
        for operation in changes:
            staged.append((operation, _stage_text(operation["path"], operation["after"])))
        for operation, staged_path in staged:
            os.replace(staged_path, operation["path"])
            replaced.append(operation)
    except OSError as exc:
        rollback_errors = []
        for operation in reversed(replaced):
            try:
                rollback = _stage_text(operation["path"], operation["before"])
                os.replace(rollback, operation["path"])
            except OSError as rollback_exc:
                rollback_errors.append(str(rollback_exc))
        detail = "；".join(rollback_errors)
        raise OSError(
            "累積更新寫入失敗；已嘗試還原先前已替換的檔案"
            + (f"（還原另有錯誤：{detail}）" if detail else "")
        ) from exc
    finally:
        for _, staged_path in staged:
            try:
                staged_path.unlink(missing_ok=True)
            except OSError:
                pass


DEVELOPMENT_DEBT_PATH = "util/output/development_debt.json"


def _accumulation_fingerprint(text):
    """Stable fingerprint of an entry's accumulated (book, chapter) set."""
    marks = sorted({f"{b}:{c}" for b, c in _ACCUM_META_RE.findall(text)})
    digest = hashlib.sha256("|".join(marks).encode("utf-8")).hexdigest()[:16]
    return marks, digest


def _load_development_debt(root):
    path = Path(root) / DEVELOPMENT_DEBT_PATH
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    entries = data.get("entries") if isinstance(data, dict) else None
    return {str(item["path"]): item for item in entries or [] if isinstance(item, dict) and item.get("path")}


def record_development_debt(preview, root=None):
    """Record/settle standing development debt named by this chapter's review.

    ``standing_debt`` means the entry owes a cross-chapter synthesis that this
    chapter is too thin to pay.  Writing it down is the point: the ledger is what
    a later maintenance pass reads, so the basis cannot quietly erase the debt.
    """
    root = Path(ROOT if root is None else root).resolve()
    ledger = _load_development_debt(root)
    book, chapter = preview["book"], preview["chapter"]
    added, settled = [], []
    for op in preview["operations"]:
        review = op.get("overview_review") or {}
        development = review.get("development") or {}
        key = op["relative_path"]
        if development.get("basis") == "standing_debt":
            marks, digest = _accumulation_fingerprint(op["after"])
            ledger[key] = {
                "path": key,
                "title": op["title"],
                "deferred_at": f"{book}:{chapter}",
                "accumulated": len(marks),
                "fingerprint": digest,
            }
            added.append(op["title"])
        elif key in ledger and development.get("decision") == "update":
            ledger.pop(key)
            settled.append(op["title"])
    path = root / DEVELOPMENT_DEBT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "note": "主題發展存量欠帳；由 link_updates.py apply 依 basis=standing_debt 記錄，"
                "development=update 時清除。維護回合處理，不擋章節流程。",
        "entries": sorted(ledger.values(), key=lambda x: (-int(x.get("accumulated") or 0), x["path"])),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return added, settled


def apply_updates(manifest, dry_run=False, reporter=print):
    """Apply fully prevalidated updates with staged per-file replacements.

    ``reporter`` keeps CLI feedback out of MCP's stdout JSON-RPC transport.
    Pass ``None`` to suppress line-by-line output.
    """
    # CLI callers retain the repository's UTF-8 console guard.  MCP passes a
    # custom collector, so its JSON-RPC stdout is never reconfigured or used.
    if reporter is print:
        console.utf8_stdio()
    preview = preview_updates(manifest)
    changes = [item for item in preview["operations"] if item["after"] != item["before"]]
    if not dry_run and changes:
        _commit_operations(changes)
    debt_added, debt_settled = ([], [])
    if not dry_run:
        debt_added, debt_settled = record_development_debt(preview)
    if reporter:
        action = "預覽" if dry_run else "更新"
        for operation in changes:
            reporter(f"{action}：{operation['relative_path']}")
            review = operation.get("overview_review")
            if review:
                reporter(
                    "   overview_review："
                    f"definition={review['definition']['decision']}；"
                    f"development={review['development']['decision']}；"
                    f"attention={review.get('review_attention', 'normal')}"
                )
                if dry_run:
                    for key, label in (("definition", "定義"), ("development", "主題發展")):
                        diff = review[key].get("diff", "")
                        if diff:
                            reporter(f"   {label} diff：\n" + "\n".join(
                                f"      {line}" for line in diff.splitlines()
                            ))
            hint_count = _development_stale_hint(operation["before"], operation["after"])
            if hint_count is not None:
                reporter(
                    f"   ℹ️ {operation['relative_path']} 累積已達 {hint_count} 筆——"
                    "建議順手檢查 definition／development／related_entries／sources 是否已跟上"
                    "目前的累積範圍（不只停留在條目首建那一卷/那一章）"
                )
        if debt_added:
            reporter(
                f"📌 記入主題發展欠帳（{len(debt_added)} 筆）：{'、'.join(debt_added)}"
                f"　→ {DEVELOPMENT_DEBT_PATH}"
            )
        if debt_settled:
            reporter(f"✅ 已還清欠帳（{len(debt_settled)} 筆）：{'、'.join(debt_settled)}")
        reporter(f"✅ {'預覽' if dry_run else '套用'}完成：{len(changes)} 個檔案")
    return len(changes)


def main():
    console.utf8_stdio()
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    prepare_parser = sub.add_parser("prepare")
    prepare_parser.add_argument("book")
    prepare_parser.add_argument("chapter")
    evidence_parser = sub.add_parser(
        "evidence", help="重生審查證據檔（條目被改過或舊章補產生時使用）"
    )
    evidence_parser.add_argument("book")
    evidence_parser.add_argument("chapter")
    sub.add_parser("debt", help="列出主題發展存量欠帳清單（basis=standing_debt 累積而成）")
    apply_parser = sub.add_parser("apply")
    apply_parser.add_argument(
        "target", nargs="+",
        help="「書名 章」（與 prepare 同形式），或 link_updates.yaml 路徑",
    )
    apply_parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            prepare(args.book, args.chapter)
        elif args.command == "debt":
            ledger = _load_development_debt(ROOT)
            if not ledger:
                print("✅ 目前沒有主題發展存量欠帳")
            else:
                rows = sorted(ledger.values(),
                              key=lambda x: -int(x.get("accumulated") or 0))
                print(f"📌 主題發展存量欠帳 {len(rows)} 筆（{DEVELOPMENT_DEBT_PATH}）：")
                for item in rows:
                    print("   %-14s 累積 %2s 章　延後於 %s　%s" % (
                        item.get("title", "?"), item.get("accumulated", "?"),
                        item.get("deferred_at", "?"), item.get("path", "?")))
                print("   還帳方式：在後續章節或維護回合把該條目的 ## 主題發展 補成跨章綜合，")
                print("   並在該章的 overview_review 填 development=update——apply 會自動清除該筆。")
        elif args.command == "evidence":
            path, count = write_review_evidence(
                canonical_book_name(args.book), int(args.chapter)
            )
            print(f"✅ 審查證據檔已寫入：{path}（{count} 條）")
        else:
            # 與 prepare 同形式的「書名 章」是主要用法；manifest 路徑保留相容
            if len(args.target) == 2 and args.target[1].isdigit():
                book = canonical_book_name(args.target[0])
                manifest = (
                    book_directory(ROOT, book) / ".tmp"
                    / f"第{int(args.target[1])}章" / "link_updates.yaml"
                )
            elif len(args.target) == 1:
                manifest = Path(args.target[0])
                if not manifest.is_absolute():
                    manifest = ROOT / manifest
            else:
                print("❌ apply 用法：apply 書名 章 [--dry-run]，或 apply <manifest路徑>")
                return 2
            apply_updates(manifest, args.dry_run)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"❌ {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
