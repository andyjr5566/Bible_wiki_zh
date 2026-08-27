#!/usr/bin/env python3
"""準備並安全套用 link_folder 的章節累積資料。"""
import argparse
import difflib
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

REVIEW_SCHEMA_VERSION = 1
REVIEW_BASELINE_FILENAME = "link_update_review_baseline.yaml"
REVIEW_DECISIONS = {"keep", "update"}
MIN_REVIEW_REASON_LENGTH = 8
REVIEW_GUIDANCE = {
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


def book_rank(book):
    canonical = BOOK_ALIASES.get(book, book)
    return BOOK_NUMBERS.get(canonical, len(BOOK_NUMBERS) + 1)


_H2_SECTION_RE = re.compile(r"(?ms)^##\s+(.+?)\s*$\n(.*?)(?=^##\s+|\Z)")
_ACCUM_META_RE = re.compile(r"<!-- accumulation:([^:]+):(\d+):start -->")
DEVELOPMENT_STALE_THRESHOLD = 7
_ACCUM_BLOCK_RE = re.compile(r"<!-- accumulation:[^:]+:\d+:start -->")


def _section_body(text, heading):
    """Return one H2 section body without its heading."""
    for match in _H2_SECTION_RE.finditer(text):
        if match.group(1).strip() == heading:
            return match.group(2).strip()
    return ""


def _review_priority(text, book, chapter):
    """Return deterministic attention signals; the semantic verdict stays human."""
    blocks = _ACCUM_META_RE.findall(text)
    marker = (book, str(chapter))
    after_count = len(blocks) + (0 if marker in blocks else 1)
    books = {canonical_book_name(block_book) for block_book, _ in blocks}
    reasons = ["本章將新增一筆 B 類逐章累積，須分別判斷定義與主題發展是否需要更新"]
    high_priority = False
    if book not in books:
        reasons.append("本章是此條目第一次累積到這一卷書")
        high_priority = True
    if not _section_body(text, "定義"):
        reasons.append("定義目前空白")
        high_priority = True
    if not _section_body(text, "主題發展"):
        reasons.append("主題發展目前空白")
        high_priority = True
    if after_count > DEVELOPMENT_STALE_THRESHOLD:
        reasons.append(
            f"套用後將有 {after_count} 筆逐章累積，超過 {DEVELOPMENT_STALE_THRESHOLD} 筆提醒門檻"
        )
        high_priority = True
    return "high" if high_priority else "normal", reasons, len(blocks), after_count


def _review_payload(text, book, chapter):
    priority, reasons, before_count, after_count = _review_priority(text, book, chapter)
    return {
        "review_attention": priority,
        "trigger_reasons": reasons,
        "accumulation_count_before": before_count,
        "accumulation_count_after": after_count,
        "definition": {"decision": "pending", "reason": ""},
        "development": {
            "decision": "pending",
            "reason": "",
            "synthesis_scope": [],
        },
    }


def _review_baseline_entry(update, text):
    return {
        "title": str(update.get("title", "")),
        "path": str(update.get("path", "")),
        "definition": _section_body(text, "定義"),
        "development": _section_body(text, "主題發展"),
    }


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


def prepare(book, chapter):
    console.utf8_stdio()
    chapter_dir = book_directory(ROOT, book) / ".tmp" / f"第{chapter}章"
    output = chapter_dir / "link_updates.yaml"
    baseline_path = chapter_dir / REVIEW_BASELINE_FILENAME
    existing = [path for path in (output, baseline_path) if path.exists()]
    if existing:
        raise FileExistsError(
            f"{existing[0]} 已存在；避免覆蓋人工內容或審查基線"
        )
    data = plan_updates(book, chapter)
    baselines = []
    for update in data["updates"]:
        path = _entry_path(ROOT, update["path"])
        text = path.read_text(encoding="utf-8")
        update["overview_review"] = _review_payload(text, book, int(chapter))
        baselines.append(_review_baseline_entry(update, text))
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
    print(f"✅ 已建立更新骨架：{output}（{len(data['updates'])} 條）")
    print(
        "⚠️ 套用前必須逐條填 overview_review：definition／development 各自選 "
        "keep 或 update 並說明理由；keep 合法，不得把逐章 summary／relation 換句話說"
        "塞進定義或主題發展。"
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
    """Load immutable-at-prepare section snapshots for schema-v1 manifests."""
    version = data.get("review_schema_version")
    if version is None:
        return None  # Historical manifests remain readable/re-applicable.
    if version != REVIEW_SCHEMA_VERSION:
        raise ValueError(
            f"不支援的 review_schema_version：{version}（目前為 {REVIEW_SCHEMA_VERSION}）"
        )
    guidance = data.get("review_guidance")
    if not isinstance(guidance, dict) or any(
        guidance.get(key) != value for key, value in REVIEW_GUIDANCE.items()
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
        baseline.get("review_schema_version") != REVIEW_SCHEMA_VERSION
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
    return out


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


def _validate_overview_review(update, current_text, baseline, book, chapter):
    title = str(update.get("title", "?"))
    review = update.get("overview_review")
    if not isinstance(review, dict):
        raise ValueError(
            f"{title} 缺少 overview_review；請分別判斷定義與主題發展，keep 合法但不可略過"
        )
    result = {
        "review_attention": review.get("review_attention", "normal"),
        "trigger_reasons": list(review.get("trigger_reasons") or []),
    }
    for key, heading in (("definition", "定義"), ("development", "主題發展")):
        verdict = review.get(key)
        if not isinstance(verdict, dict):
            raise ValueError(f"{title} 的 overview_review.{key} 必須是物件")
        decision = str(verdict.get("decision", "")).strip().lower()
        if decision not in REVIEW_DECISIONS:
            raise ValueError(
                f"{title} 的 {heading} 尚未完成判斷：decision 必須是 keep 或 update"
            )
        reason = str(verdict.get("reason", "")).strip()
        if len(reason) < MIN_REVIEW_REASON_LENGTH:
            raise ValueError(
                f"{title} 的 {heading} 判斷理由過短；請說明本章是否改變穩定身分／"
                "是否形成跨章發展，不能只填『不用』"
            )
        before = str(baseline.get(key, ""))
        after = _section_body(current_text, heading)
        changed = before != after
        if decision == "update" and not changed:
            raise ValueError(
                f"{title} 的 {heading} 選了 update，但條目中的「## {heading}」沒有改變"
            )
        if decision == "keep" and changed:
            raise ValueError(
                f"{title} 的 {heading} 選了 keep，但條目中的「## {heading}」已被修改；"
                "請把 decision 改為 update 並說明，或還原該區塊"
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
            "reason": reason,
            "changed": changed,
            "diff": _section_diff(before, after, heading),
        }
        if key == "development" and decision == "update":
            item["synthesis_scope"] = _validated_synthesis_scope(
                verdict.get("synthesis_scope"), book, chapter
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

    review_baselines = _load_review_baselines(manifest, data, book, chapter)
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
                update, text, baseline, book, chapter
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
        reporter(f"✅ {'預覽' if dry_run else '套用'}完成：{len(changes)} 個檔案")
    return len(changes)


def main():
    console.utf8_stdio()
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    prepare_parser = sub.add_parser("prepare")
    prepare_parser.add_argument("book")
    prepare_parser.add_argument("chapter")
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
