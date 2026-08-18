#!/usr/bin/env python3
"""Formal source identities, full-source loading, and prompt context policy.

``raw_data`` and ``source_manifest.md`` remain the complete source of truth.
Prompt construction is a separate layer: injected runners may request full
source context, while the manual workflow references already-read commentary
and embeds only deterministic task-aware STEP projections.
"""
import re
from dataclasses import dataclass
from pathlib import Path

MANIFEST_ROW_RE = re.compile(r"^\|(.+)\|\s*$")

# §9 超長章節判準（任一成立即視為大章節）
LARGE_VERSES = 60
LARGE_TOTAL_CHARS = 250_000
LARGE_SINGLE_CHARS = 120_000
STRUCTURED_TOTAL_CHARS = 120_000

FULL = "full"
MANUAL_PROJECTED = "manual_projected"

_SOURCE_SPECS = {
    "CT": {
        "identity": "ccbiblestudy CT", "kind": "逐節註解",
        "aliases": ("CT", "華人基督徒查經資料"),
    },
    "GT": {
        "identity": "ccbiblestudy GT", "kind": "拾穗",
        "aliases": ("GT", "聖經精讀本"),
    },
    "KC": {
        "identity": "KingComments", "kind": "研經註解",
        "aliases": ("KC", "KingComments"),
    },
    "BH": {
        "identity": "BibleHub Study", "kind": "研經註解",
        "aliases": ("BH", "BibleHub", "BibleHub Study"),
    },
    "STEP": {
        "identity": "STEP Bible", "kind": "原文資料",
        "aliases": ("STEP", "STEP Bible"),
    },
}


@dataclass(frozen=True)
class SourceIdentity:
    """One manifest source with canonical citation identity and legacy aliases."""

    key: str
    manifest_label: str
    manifest_kind: str
    identity: str
    kind: str
    url: str
    path: Path
    aliases: tuple[str, ...]

    @property
    def canonical_label(self) -> str:
        return f"{self.kind}（{self.identity}）"

    @property
    def is_structured(self) -> bool:
        return self.kind == "原文資料" or self.key == "STEP"

    @property
    def accepted_labels(self) -> tuple[str, ...]:
        labels = [
            self.canonical_label,
            self.identity,
            self.kind,
            self.manifest_kind,
            *self.aliases,
        ]
        # Bare 研經註解 is historically widespread.  It is accepted only after
        # the validator has already matched the exact manifest URL to this
        # identity; new prompts always emit the unambiguous canonical label.
        return tuple(dict.fromkeys(labels))


@dataclass(frozen=True)
class PromptContext:
    """Rendered prompt context plus exact data needed for before/after metrics."""

    text: str
    legacy_full_text: str
    policy: str
    commentary_omitted: tuple[dict, ...] = ()
    step_metrics: tuple[dict, ...] = ()


def _manifest_rows(manifest_path):
    """source_manifest.md 中狀態 OK 的資料列 → [(label, kind, url, rel_path)]。"""
    manifest_path = Path(manifest_path)
    rows = []
    if not manifest_path.exists():
        return rows
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        match = MANIFEST_ROW_RE.match(line.strip())
        if not match:
            continue
        cells = [cell.strip() for cell in match.group(1).split("|")]
        if len(cells) < 5:
            continue
        label, kind, url, rel_path, status = cells[:5]
        if "OK" not in status:
            continue
        rows.append((label, kind, url, rel_path))
    return rows


def _source_key(label: str, kind: str, url: str, rel_path: str) -> str:
    """Infer a stable source identity from all manifest fields, including legacy manifests."""
    joined = " ".join((label, kind, url, rel_path)).casefold()
    if "stepbible" in joined or "step bible" in joined or kind == "原文資料":
        return "STEP"
    if "kingcomments" in joined or re.search(r"(?:^|\W)kc(?:$|\W)", joined):
        return "KC"
    if "biblehub" in joined or re.search(r"(?:^|\W)bh(?:$|\W)", joined):
        return "BH"
    if ("ccbiblestudy" in joined and re.search(r"(?:_|/|\b)ct(?:_|\d|\b)", joined)) \
            or kind in {"CT", "逐節註解"}:
        return "CT"
    if ("ccbiblestudy" in joined and re.search(r"(?:_|/|\b)gt(?:_|\d|\b)", joined)) \
            or kind in {"GT", "拾穗"}:
        return "GT"
    return "OTHER"


def _resolve_raw_path(root: Path, rel_path: str) -> Path | None:
    if not rel_path.endswith(".txt"):
        return None
    parts = Path(rel_path).parts
    if parts and parts[0] == "raw_data":
        return root / Path(rel_path)
    if len(parts) == 1:
        return root / "raw_data" / parts[0]
    return None


def manifest_source_identities(manifest_path, root=None) -> list[SourceIdentity]:
    """Return the single canonical identity/type/URL mapping for all OK sources."""
    manifest_path = Path(manifest_path)
    if root is None:
        # The project manifest is normally <root>/<book>/.tmp/第X章/source_manifest.md.
        root = manifest_path
        for _ in range(4):
            root = root.parent
    root = Path(root)
    identities = []
    for label, manifest_kind, url, rel_path in _manifest_rows(manifest_path):
        resolved = _resolve_raw_path(root, rel_path)
        if resolved is None:
            continue
        key = _source_key(label, manifest_kind, url, rel_path)
        spec = _SOURCE_SPECS.get(key)
        if spec:
            identity = spec["identity"]
            kind = spec["kind"]
            aliases = tuple(spec["aliases"])
        else:
            identity = label
            kind = manifest_kind
            aliases = ()
        identities.append(SourceIdentity(
            key=key,
            manifest_label=label,
            manifest_kind=manifest_kind,
            identity=identity,
            kind=kind,
            url=url,
            path=resolved,
            aliases=aliases,
        ))
    return identities


def parse_source_citation_label(text: str) -> str | None:
    """Extract the bounded label before a source citation's first colon."""
    text = str(text).strip().strip("\"'")
    positions = [position for position in (text.find(":"), text.find("：")) if position >= 0]
    if not positions:
        return None
    label = text[:min(positions)].strip()
    if not label or len(label) > 100 or "\n" in label or "\r" in label:
        return None
    return label


def source_label_matches(identity: SourceIdentity, label: str) -> bool:
    """Accept canonical labels and audited legacy labels without weakening identity checks."""
    normalized = str(label).strip()
    if normalized in identity.accepted_labels:
        return True
    # Historic payloads used labels such as "創世記 43章 CT".  Only a known
    # terminal identity alias is accepted; arbitrary free text is not.
    for alias in identity.aliases:
        if re.search(rf"(?:^|\s){re.escape(alias)}$", normalized, re.I):
            return True
    return False


def canonical_source_list(manifest_path, root=None) -> list[tuple[str, str]]:
    """Canonical prompt/validator labels and URLs from one shared mapping."""
    return [
        (identity.canonical_label, identity.url)
        for identity in manifest_source_identities(manifest_path, root)
        if identity.url.startswith("http")
    ]


class SourceError(RuntimeError):
    """source_manifest 宣告了 OK 來源、但實際讀不到任何 raw_data 檔時拋出。

    最典型成因：manifest 第4欄漏寫 `raw_data/` 前綴（裸檔名），舊版 parse_manifest
    會靜默丟棄整列 → M3/M6 拿到空來源、模型只能憑訓練知識杜撰註釋。此例外讓這種
    「閘門全過但內容其實沒讀到來源」的靜默失效當場爆出來。
    """


def manifest_records(manifest_path, root):
    """Return OK raw-data records as ``(label, kind, url, Path)`` tuples."""
    return [
        # Preserve the public loader's historical manifest label.  Canonical
        # prompt labels and validation still come from SourceIdentity; callers
        # that only read files do not need a surprise label migration.
        (item.manifest_label, item.kind, item.url, item.path)
        for item in manifest_source_identities(manifest_path, root)
    ]


def parse_manifest(manifest_path, root):
    """讀 source_manifest.md，回傳 [(label, Path)]（僅狀態含 OK 的來源）。

    第4欄可寫 `raw_data/xxx.txt` 或裸檔名 `xxx.txt`（裸檔名一律歸到 raw_data/ 下）。
    非 raw_data 的 .txt（如 raw_scripture/… 的經文本文列）不算正式補充來源，略過。
    """
    return [(label, path) for label, _kind, _url, path
            in manifest_records(manifest_path, root)]


def require_sources(manifest_path, root):
    """M3/M6 生成前的護欄：回傳可用來源；宣告了 OK 來源卻一個都讀不到就報錯。

    回傳存在於磁碟的 [(label, Path)]。若 manifest 宣告了 OK 來源、但解析後沒有
    任何檔案存在，拋 SourceError 並指明最可能的成因與修法——避免模型在空來源下
    生成、卻一路通過結構閘門（申命記 1-6 的杜撰註釋即此因）。
    """
    declared = parse_manifest(manifest_path, root)
    present = [(label, path) for label, path in declared if Path(path).exists()]
    if declared and not present:
        sample = declared[0][1]
        raise SourceError(
            f"source_manifest.md 宣告了 {len(declared)} 個 OK 來源，但解析後沒有任何"
            f"檔案存在（例：{sample}）。最可能成因：manifest 第4欄漏寫 raw_data/ "
            f"前綴或檔名有誤，raw_data 尚未準備。M3/M6 需要來源全文，已中止以免"
            f"用空來源杜撰內容。請用 util/build_source_manifest.py 重新產生 manifest，"
            f"或確認 raw_data/ 下有對應 .txt 後重跑。\n  manifest：{manifest_path}"
        )
    missing = [path for label, path in declared if not Path(path).exists()]
    if missing:
        joined = "、".join(str(p.name) for p in missing)
        raise SourceError(
            f"source_manifest.md 有 {len(missing)} 個 OK 來源檔讀不到：{joined}。"
            f"部分來源缺檔會讓該來源的觀點在 M3/M6 靜默消失。請補齊 raw_data 或把"
            f"該列狀態改為非 OK 後重跑。\n  manifest：{manifest_path}"
        )
    return present


def manifest_urls(manifest_path):
    """讀 source_manifest.md，回傳 [(label, url)]（僅狀態 OK 且 URL 為 http(s)）。

    章節「參考資料」與條目「來源依據」的 URL 以此為唯一事實來源，不由模型手寫。
    """
    return [
        (label, url)
        for label, _kind, url, _rel_path in _manifest_rows(manifest_path)
        if url.startswith("http")
    ]


def manifest_kind_urls(manifest_path):
    """Return canonical ``[(kind（identity）, URL)]`` citation choices.

    This is kept as the public compatibility name, but no longer returns the
    ambiguous kind alone: KingComments and BibleHub both use ``研經註解``.
    """
    return canonical_source_list(manifest_path)


def _coerce_source(source):
    if isinstance(source, SourceIdentity):
        return source.identity, source.kind, source.path
    if len(source) == 2:
        label, path = source
        path = Path(path)
        joined = f"{label} {path.name}".casefold()
        kind = "原文資料" if "stepbible" in joined or "step bible" in joined else "commentary"
        return label, kind, path
    if len(source) == 4:
        label, kind, _url, path = source
        return label, kind, Path(path)
    raise ValueError(f"不支援的 source record：{source!r}")


def _read_all(sources):
    texts = []
    for source in sources:
        label, kind, path = _coerce_source(source)
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8").strip()
        if text:
            texts.append((label, kind, text))
    return texts


def _budgeted_texts(texts, budget):
    total = sum(len(text) for _label, _kind, text in texts)
    output = []
    for label, kind, text in texts:
        if total > budget:
            keep = max(1000, int(len(text) * budget / total))
            text = text[:keep] + "\n…（此 prompt context 達預算上限；正式 raw source 未截斷）"
        output.append((label, kind, text))
    return output


def full_source_text(
    sources, *, char_budget=LARGE_TOTAL_CHARS,
    structured_char_budget=STRUCTURED_TOTAL_CHARS,
):
    """Full prompt mode with independent commentary/structured budgets.

    A large structured STEP file can no longer shrink CT/GT/KC/BH prose.  This
    affects prompt context only; every formal ``raw_data`` file remains intact.
    """
    texts = _read_all(sources)
    commentary = [item for item in texts if item[1] != "原文資料"]
    structured = [item for item in texts if item[1] == "原文資料"]
    budgeted = _budgeted_texts(commentary, char_budget)
    budgeted.extend(_budgeted_texts(structured, structured_char_budget))
    chunks = []
    for label, _kind, text in budgeted:
        chunks.append(f"【{label}】\n{text}")
    return "\n\n".join(chunks)


def _legacy_combined_source_text(sources, *, char_budget=LARGE_TOTAL_CHARS):
    """Reproduce the pre-Phase-2 all-source budget for benchmark metrics only.

    This deliberately keeps the retired behavior isolated from live prompt
    construction: STEP size could proportionally shrink commentary here.  It
    exists so ``prompt_metrics.json`` compares against the real former prompt,
    rather than against the new independent-budget FULL policy.
    """
    texts = []
    for source in sources:
        if isinstance(source, SourceIdentity):
            label, path = source.manifest_label, source.path
        else:
            label, _kind, path = _coerce_source(source)
        if path.exists():
            body = path.read_text(encoding="utf-8").strip()
            if body:
                texts.append((label, body))
    total = sum(len(body) for _label, body in texts)
    chunks = []
    for label, body in texts:
        if total > char_budget:
            keep = max(1000, int(len(body) * char_budget / total))
            body = body[:keep] + "\n…（大章節截斷，其餘見分段）"
        chunks.append(f"【{label}】\n{body}")
    return "\n\n".join(chunks)


def render_source_reading_plan(manifest_path, root) -> str:
    """Human-readable manual workflow plan: prose read, STEP machine validate."""
    root = Path(root)
    identities = manifest_source_identities(manifest_path, root)
    commentary = [item for item in identities if not item.is_structured]
    structured = [item for item in identities if item.is_structured]
    lines = [
        "# Source reading plan",
        "",
        "所有正式來源都完整保留於 raw_data，並納入 provenance／validation。",
        "",
        "## 必須由 Agent 全文閱讀",
        "",
    ]
    for item in commentary:
        relative = item.path.relative_to(root).as_posix()
        lines.extend([
            f"### {item.canonical_label}",
            f"- path: {relative}",
            f"- url: {item.url}",
            "- validation: human/agent full-read receipt（3 段逐字引句，至少 1 段在後 1/3）",
            "",
        ])
    if not commentary:
        lines.extend(["- （本章 manifest 沒有 OK commentary）", ""])
    lines.extend([
        "## Structured original-language source",
        "",
    ])
    for item in structured:
        relative = item.path.relative_to(root).as_posix()
        lines.extend([
            f"### {item.canonical_label}",
            f"- path: {relative}",
            f"- url: {item.url}",
            "- validation: deterministic machine gate（解析、book/chapter、verse coverage、word/Strong/morphology/original script、SHA-256）",
            "- 使用方式: M3/M6 prompt 會提供 task-aware compact projection；需要更多細節時執行 `python util/step_context.py 書名 章 --verses 範圍`。",
            "- 不要求 Agent 為 read receipt 人工逐詞通讀完整 STEP rows；完整 raw source 仍須通過 machine validation。",
            "",
        ])
    if not structured:
        lines.extend(["- （本章 manifest 沒有 OK STEP 原文資料）", ""])
    return "\n".join(lines).rstrip() + "\n"


def _manual_reference_block(identities, root):
    lines = [
        "## 本章 Commentary Sources",
        "",
        "你已依 manual/sources.md 全文閱讀以下正式 commentary；本 prompt 不重複內嵌原文全文。",
    ]
    for item in identities:
        if item.is_structured:
            continue
        lines.extend([
            f"- {item.canonical_label}",
            f"  path: {item.path.relative_to(root).as_posix()}",
            f"  URL: {item.url}",
        ])
    lines.extend([
        "",
        "所有 commentary 敘述仍必須忠於上述已全文閱讀來源；不得以摘要或關鍵字 grep 取代全文閱讀。",
    ])
    return "\n".join(lines).rstrip() + "\n"


STEP_PROMPT_DISCLAIMER = (
    "> 以下 STEP 區塊是 deterministic selector 為本任務挑出的少量候選，不是本章完整 STEP 資料。"
    "需要更多經節／詞彙時，請使用 MCP 工具 query_step_context / find_step_candidates 進行精確查詢。"
)


def build_prompt_context(
    manifest_path,
    root,
    *,
    policy=FULL,
    step_verses=None,
    step_candidates=None,
    m3_batch=None,
    step_char_budget=None,
):
    """Build one policy-controlled source context without changing source truth."""
    root = Path(root)
    identities = manifest_source_identities(manifest_path, root)
    present = [item for item in identities if item.path.is_file()]
    legacy = _legacy_combined_source_text(present)
    if policy == FULL:
        current_full = full_source_text(present)
        return PromptContext(
            text=current_full, legacy_full_text=legacy, policy=policy
        )
    if policy != MANUAL_PROJECTED:
        raise ValueError(f"未知 source context policy：{policy}")

    try:
        try:
            from . import step_context
            from . import extract_stepbible
        except ImportError:
            import step_context
            import extract_stepbible
        projections = []
        step_metrics = []
        for item in present:
            if not item.is_structured:
                continue
            raw_bytes = item.path.stat().st_size
            raw_chars = len(item.path.read_text(encoding="utf-8-sig", errors="replace"))

            if m3_batch is not None:
                budget = step_char_budget or step_context.DEFAULT_STEP_PROMPT_CHAR_BUDGET
                disclaimer_len = len(STEP_PROMPT_DISCLAIMER) + 2
                evidence_budget = max(500, budget - disclaimer_len)
                raw = item.path.read_text(encoding="utf-8-sig", errors="strict")
                doc = extract_stepbible.parse_rendered_markdown_text(raw)
                evidence = step_context.select_m3_candidate_evidence(
                    doc, m3_batch, root=root, char_budget=evidence_budget
                )
                text_with_disclaimer = f"{STEP_PROMPT_DISCLAIMER}\n\n{evidence.text}"
                projections.append(text_with_disclaimer)
                step_metrics.append({
                    "source": item.path.relative_to(root).as_posix(),
                    "selection_mode": evidence.mode,
                    "raw_chars": raw_chars,
                    "raw_bytes": raw_bytes,
                    "projected_chars": len(text_with_disclaimer),
                    "projected_bytes": len(text_with_disclaimer.encode("utf-8")),
                    "occurrences": evidence.occurrences,
                    "occurrence_count": evidence.occurrences,
                    "lexicon_entries": evidence.selected_count,
                    "selected_verses": list(evidence.selected_verses),
                    "candidate_count": evidence.candidate_count,
                    "selected_candidate_count": evidence.selected_count,
                    "truncated": evidence.truncated,
                    "returned_chars": len(text_with_disclaimer),
                    "budget": budget,
                    "fallback_used": False,
                })
            elif step_verses == ():
                # M3 unresolved / non-original-skipped / full-chapter-evidence fail-small mode
                notice = (
                    f"{STEP_PROMPT_DISCLAIMER}\n\n"
                    "## STEP Bible selected candidates\n"
                    f"- source: {item.path.name}\n"
                    "- selected verses: none\n"
                    "- mode: unresolved\n"
                    "- note: 未自動注入整章 STEP 資料；需要時請透過 MCP 工具 query_step_context / find_step_candidates 精確查詢。"
                )
                projections.append(notice)
                step_metrics.append({
                    "source": item.path.relative_to(root).as_posix(),
                    "selection_mode": "unresolved",
                    "raw_chars": raw_chars,
                    "raw_bytes": raw_bytes,
                    "projected_chars": len(notice),
                    "projected_bytes": len(notice.encode("utf-8")),
                    "occurrences": 0,
                    "occurrence_count": 0,
                    "lexicon_entries": 0,
                    "selected_verses": [],
                    "candidate_count": 0,
                    "selected_candidate_count": 0,
                    "truncated": False,
                    "returned_chars": len(notice),
                    "budget": step_char_budget or step_context.DEFAULT_STEP_PROMPT_CHAR_BUDGET,
                    "fallback_used": False,
                })
            elif step_verses is not None:
                # Phase 1 targeted verse projection (used by benchmark Layer 2 / backward compatibility)
                projection = step_context.project_step_source(
                    item.path, verses=step_verses, allow_full_chapter=True
                )
                text_with_disclaimer = f"{STEP_PROMPT_DISCLAIMER}\n\n{projection.text}"
                projections.append(text_with_disclaimer)
                step_metrics.append({
                    "source": item.path.relative_to(root).as_posix(),
                    "selection_mode": "targeted",
                    "raw_chars": projection.raw_chars,
                    "raw_bytes": projection.raw_bytes,
                    "projected_chars": len(text_with_disclaimer),
                    "projected_bytes": len(text_with_disclaimer.encode("utf-8")),
                    "occurrences": projection.occurrence_count,
                    "occurrence_count": projection.occurrence_count,
                    "lexicon_entries": projection.lexicon_count,
                    "selected_verses": list(projection.selected_verses),
                    "candidate_count": len(step_candidates) if step_candidates is not None else 1,
                    "selected_candidate_count": len(step_candidates) if step_candidates is not None else 1,
                    "truncated": projection.truncated,
                    "returned_chars": len(text_with_disclaimer),
                    "budget": step_char_budget or step_context.DEFAULT_STEP_PROMPT_CHAR_BUDGET,
                    "fallback_used": False,
                })
            else:
                # M6 selected candidates mode (step_verses is None)
                budget = step_char_budget or step_context.DEFAULT_STEP_PROMPT_CHAR_BUDGET
                disclaimer_len = len(STEP_PROMPT_DISCLAIMER) + 2
                evidence_budget = max(500, budget - disclaimer_len)
                raw = item.path.read_text(encoding="utf-8-sig", errors="strict")
                doc = extract_stepbible.parse_rendered_markdown_text(raw)
                evidence = step_context.select_step_evidence(
                    doc, root=root, candidates=step_candidates, char_budget=evidence_budget
                )
                text_with_disclaimer = f"{STEP_PROMPT_DISCLAIMER}\n\n{evidence.text}"
                projections.append(text_with_disclaimer)
                step_metrics.append({
                    "source": item.path.relative_to(root).as_posix(),
                    "selection_mode": "selected_candidates",
                    "raw_chars": raw_chars,
                    "raw_bytes": raw_bytes,
                    "projected_chars": len(text_with_disclaimer),
                    "projected_bytes": len(text_with_disclaimer.encode("utf-8")),
                    "occurrences": evidence.occurrences,
                    "occurrence_count": evidence.occurrences,
                    "lexicon_entries": evidence.selected_count,
                    "selected_verses": list(evidence.selected_verses),
                    "candidate_count": evidence.candidate_count,
                    "selected_candidate_count": evidence.selected_count,
                    "truncated": evidence.truncated,
                    "returned_chars": len(text_with_disclaimer),
                    "budget": budget,
                    "fallback_used": False,
                })
    except (OSError, UnicodeError, ValueError) as exc:
        raise SourceError(f"STEP prompt projection 失敗；不得靜默省略原文證據：{exc}") from exc

    omitted = tuple({
        "label": item.canonical_label,
        "path": item.path.relative_to(root).as_posix(),
        "chars": len(item.path.read_text(encoding="utf-8")),
        "bytes": item.path.stat().st_size,
    } for item in present if not item.is_structured)
    text = _manual_reference_block(present, root)
    if projections:
        text += "\n\n" + "\n\n".join(projections)
    else:
        text += "\n\n## STEP Bible task projection\n- （本章沒有 OK STEP 原文資料）\n"
    return PromptContext(
        text=text,
        legacy_full_text=legacy,
        policy=policy,
        commentary_omitted=omitted,
        step_metrics=tuple(step_metrics),
    )



def is_large_chapter(sources, raw_verses):
    """§9 判準：經文超過 60 節、單一來源過大、或來源合計過大。"""
    if len(raw_verses) > LARGE_VERSES:
        return True
    texts = _read_all(sources)
    if any(len(text) > LARGE_SINGLE_CHARS for _, _kind, text in texts):
        return True
    commentary_total = sum(
        len(text) for _label, kind, text in texts if kind != "原文資料"
    )
    structured_total = sum(
        len(text) for _label, kind, text in texts if kind == "原文資料"
    )
    return commentary_total > LARGE_TOTAL_CHARS or structured_total > STRUCTURED_TOTAL_CHARS
