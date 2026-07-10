#!/usr/bin/env python3
"""章節製作 orchestrator：程式主導、模型只填 payload。

流程（每步以 .tmp/第x章/ 內的檔案存在與否斷點續跑）：

  P2 resolve         link_candidates(.yaml/.md) → link_plan.yaml            （程式）
  M3 entry_content   每個 C 類條目呼叫模型填 payload → schema 驗證 → 重試   （模型）
  M5 verse_links     呼叫模型標注經文 wiki-link → 對 raw_scripture 驗證      （模型）
  M6 chapter_content 呼叫模型填知識節點 + 本章整理                          （模型）
  P3 render          render_entry / render_chapter 產生 markdown            （程式）
  P4 validate        validate_knowledge_base 結構驗證                       （程式）

模型呼叫走 util.model_client.call_model（預設 shell 到 claude -p）；runner
可注入，讓整條流程能以假模型單元測試。P1 來源抓取與 P5 commit 屬側效步驟，
交由既有 util 腳本與人工 gate，不在本檔自動執行。
"""
import argparse
import json
import re
import sys
from pathlib import Path

import yaml

try:
    from .book_paths import book_directory, canonical_book_name
except ImportError:
    from book_paths import book_directory, canonical_book_name

import render_chapter
import render_entry
import resolve_link_candidates as resolver
import source_excerpts
import validate_knowledge_base as vkb
from model_client import ModelValidationError, call_model

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = ROOT / "_config" / "schemas"


class ChapterContext:
    def __init__(self, book, chapter, root=ROOT, runner=None, index=None, homonyms=None):
        self.book = canonical_book_name(book)
        self.chapter = int(chapter)
        self.root = Path(root)
        self.runner = runner  # None → model_client 預設 claude runner
        self.index = index  # None → resolver 讀真實 link_index.json
        self.homonyms = homonyms
        self.tmp = book_directory(self.root, book) / ".tmp" / f"第{self.chapter}章"
        self.manual_review = []

    def path(self, *parts):
        return self.tmp.joinpath(*parts)

    def raw_verses(self):
        path = self.root / "raw_scripture" / self.book / f"第{self.chapter}章.txt"
        if not path.exists():
            raise FileNotFoundError(path)
        return [line.rstrip("\n") for line in path.read_text(encoding="utf-8").splitlines()]

    def known_types(self):
        folder = self.root / "link_folder"
        if not folder.is_dir():
            return set()
        return {p.name for p in folder.iterdir() if p.is_dir() and not p.name.startswith(".")}

    def sources(self):
        if getattr(self, "_sources", None) is None:
            self._sources = source_excerpts.parse_manifest(
                self.path("source_manifest.md"), self.root
            )
        return self._sources


def _read_yaml(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _write_yaml(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )


def _schema_hint(name):
    path = SCHEMA_DIR / name
    if not path.exists():
        return ""
    schema = json.loads(path.read_text(encoding="utf-8"))
    fields = ", ".join(schema.get("properties", {}))
    return f"payload 欄位：{fields}。詳見 _config/schemas/{name}。"


# --------------------------------------------------------------------------- #
# P2 resolve
# --------------------------------------------------------------------------- #
def resolve_step(ctx):
    plan_path = ctx.path("link_plan.yaml")
    if plan_path.exists():
        return _read_yaml(plan_path)
    index = resolver.load_index() if ctx.index is None else ctx.index
    homonyms = resolver.load_homonyms() if ctx.homonyms is None else ctx.homonyms
    candidates = resolver.load_candidates(ctx.book, ctx.chapter, root=ctx.root)
    plan = resolver.resolve(candidates, index, ctx.book, ctx.chapter, root=ctx.root, homonyms=homonyms)
    document = resolver.build_plan_document(plan, ctx.book, ctx.chapter)
    _write_yaml(plan_path, document)
    return document


# --------------------------------------------------------------------------- #
# 模型步驟共用：resume + call_model + 寫檔；失敗記入 manual_review
# --------------------------------------------------------------------------- #
def _model_step(ctx, out_path, prompt, validate, label):
    if out_path.exists():
        return _read_yaml(out_path)
    try:
        payload = call_model(prompt, validate=validate, runner=ctx.runner, label=label)
    except ModelValidationError as exc:
        ctx.manual_review.append(str(exc))
        return None
    _write_yaml(out_path, payload)
    return payload


# --------------------------------------------------------------------------- #
# M3 entry_content（批量：一次 request 產出多個條目，全部來源直接餵入）
# --------------------------------------------------------------------------- #
BATCH_SIZE = 5


def _batch_entry_prompt(ctx, batch, allowed_related, sources_text, raw_text):
    listing = "\n".join(f"- {e['name']}（{e['suggested_type']}）" for e in batch)
    return (
        f"你是聖經研經資料整理員。任務：一次為以下 {len(batch)} 個 link_folder 條目"
        f"各填一份 entry_content payload。\n\n"
        f"【要寫的條目】\n{listing}\n\n"
        f"【本章經文（{ctx.book} 第{ctx.chapter}章）】\n{raw_text}\n\n"
        f"【本章全部來源（CT/GT/KC/BH 全文）】\n{sources_text}\n\n"
        f"【規則】\n"
        f"- 所有陳述須能對應經文或上述來源；未提及者不得寫入。\n"
        f"- status 一律 formal；每個條目 accumulations 至少含本章一項，同一章只給一筆。\n"
        f"- related_entries 只能從此清單選：{', '.join(allowed_related) or '（無）'}。\n"
        f"- 互文類條目 name 不可只有經文引用，須用「簡短標題（經文）」，"
        f"例如「天上真聖所（來9:23-24）」；括號內保留原經文。\n"
        f"- 每個 payload 的 name 必須能對回上面清單。\n\n"
        f"【輸出】只輸出一個 YAML 陣列（每個元素以 - 開頭），每個元素是一份"
        f" entry_content payload，欄位：\n{_schema_hint('entry_content.schema.json')}"
    )


def _match_payload(entry, results):
    for payload in results:
        if isinstance(payload, dict) and payload.get("name") == entry["name"]:
            return payload
    if entry["suggested_type"] == "互文":
        for payload in results:
            if isinstance(payload, dict) and entry["name"] in str(payload.get("name", "")):
                return payload
    return None


def _run_entry_batch(ctx, batch, allowed_related, sources_text, raw_text, known):
    prompt = _batch_entry_prompt(ctx, batch, allowed_related, sources_text, raw_text)
    try:
        results = call_model(
            prompt,
            validate=lambda p: [] if isinstance(p, list) and p else ["需回傳非空的 payload 陣列"],
            runner=ctx.runner, label="entry_batch",
        )
    except ModelValidationError:
        return {}
    matched = {}
    for entry in batch:
        payload = _match_payload(entry, results)
        if payload is None or render_entry.validate_payload(payload, known_types=known):
            continue
        matched[entry["name"]] = payload
    return matched


def entry_content_step(ctx, plan, limit=None, batch_size=BATCH_SIZE):
    out_dir = ctx.path("entry_content")
    known = ctx.known_types()
    raw_text = "\n".join(f"{i}. {v}" for i, v in enumerate(ctx.raw_verses(), 1))
    sources_text = source_excerpts.full_source_text(ctx.sources())
    c_entries = plan.get("C_new_formal", [])
    allowed_related = [e["name"] for e in c_entries]
    if limit is not None:
        c_entries = c_entries[:limit]

    # resume：讀已存在的 payload（互文可能已改名，用「原名 ⊂ 檔名」判定）
    existing = [_read_yaml(p) for p in sorted(out_dir.glob("*.yaml"))] if out_dir.exists() else []
    payloads = {p["name"]: p for p in existing if isinstance(p, dict) and p.get("name")}

    def done(entry):
        for payload in existing:
            title = payload.get("name", "") if isinstance(payload, dict) else ""
            if title == entry["name"] or (
                entry["suggested_type"] == "互文" and entry["name"] in title
            ):
                return True
        return False

    pending = [e for e in c_entries if not done(e)]
    for _ in range(2):  # 一輪批量 + 一輪重做
        failed = []
        for start in range(0, len(pending), batch_size):
            batch = pending[start:start + batch_size]
            results = _run_entry_batch(ctx, batch, allowed_related, sources_text, raw_text, known)
            for entry in batch:
                payload = results.get(entry["name"])
                if payload is None:
                    failed.append(entry)
                    continue
                _write_yaml(out_dir / f"{payload['name']}.yaml", payload)
                payloads[payload["name"]] = payload
        pending = failed
        if not pending:
            break
    for entry in pending:
        ctx.manual_review.append(f"entry_content:{entry['name']}：批量重做後仍不合格")
    ctx.created_entry_names = list(payloads)
    return payloads


# --------------------------------------------------------------------------- #
# M5 verse_links
# --------------------------------------------------------------------------- #
def verse_links_step(ctx, plan):
    out_path = ctx.path("verse_links.yaml")
    raw_verses = ctx.raw_verses()
    raw_text = "\n".join(f"{i}. {v}" for i, v in enumerate(raw_verses, 1))
    linkable = [e["name"] for key in ("A_use_directly", "B_needs_update")
                for e in plan.get(key, [])] + list(getattr(ctx, "created_entry_names", []))
    sources_text = source_excerpts.full_source_text(ctx.sources())
    prompt = (
        f"你是聖經研經資料整理員。唯一任務：為 {ctx.book} 第{ctx.chapter}章標注經文 "
        f"wiki-link（verse_links payload）。\n\n【經文】\n{raw_text}\n\n"
        f"【本章全部來源】\n{sources_text}\n\n"
        f"【規則】phrase 必須是該節經文的子字串；target 只能用：{', '.join(linkable) or '（無）'}；"
        f"同一詞若要連多次就重複列出，不必自己數第幾次出現。\n\n"
        f"【輸出】只輸出 YAML：\n{_schema_hint('verse_links.schema.json')}"
    )
    return _model_step(
        ctx, out_path, prompt,
        validate=lambda p: render_chapter.validate_verse_links(p.get("links", []), raw_verses),
        label="verse_links",
    )


# --------------------------------------------------------------------------- #
# M6 chapter_content
# --------------------------------------------------------------------------- #
def chapter_content_step(ctx, plan):
    out_path = ctx.path("chapter_content.yaml")
    raw_text = "\n".join(f"{i}. {v}" for i, v in enumerate(ctx.raw_verses(), 1))
    sources_text = source_excerpts.full_source_text(ctx.sources())
    created = list(getattr(ctx, "created_entry_names", []))
    created_hint = (
        f"\n本章新建條目（knowledge_nodes 若引用請用完整名稱）：{', '.join(created)}"
        if created else ""
    )
    prompt = (
        f"你是聖經研經資料整理員。唯一任務：為 {ctx.book} 第{ctx.chapter}章填寫 "
        f"chapter_content payload（本章知識節點 + 本章整理）。\n\n【經文】\n{raw_text}\n\n"
        f"【本章全部來源（CT/GT/KC/BH 全文）】\n{sources_text}\n\n"
        f"【規則】knowledge_nodes 只列值得跨章累積的核心節點，不重列所有經文 link；"
        f"organization 整合上述來源重點，不搬運整段全文，也不得寫入來源未提及的內容。"
        f"{created_hint}\n\n"
        f"【輸出】只輸出 YAML：\n{_schema_hint('chapter_content.schema.json')}"
    )
    return _model_step(
        ctx, out_path, prompt,
        validate=render_chapter.validate_chapter_content,
        label="chapter_content",
    )


# --------------------------------------------------------------------------- #
# P3 render（程式產生 markdown）
# --------------------------------------------------------------------------- #
def render_step(ctx, entry_payloads, verse_links, chapter_content):
    written = []
    known = ctx.known_types()
    for name, payload in entry_payloads.items():
        markdown = render_entry.render_entry(payload, known_types=known)
        target = ctx.root / "link_folder" / payload["type"] / f"{name}.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(markdown, encoding="utf-8")
        written.append(target)
    if verse_links and chapter_content:
        chapter_path = book_directory(ctx.root, ctx.book) / f"第{ctx.chapter}章.md"
        chapter_path.parent.mkdir(parents=True, exist_ok=True)
        map_block = ""
        if chapter_path.exists():
            existing = render_chapter.MAP_BLOCK_RE.search(chapter_path.read_text(encoding="utf-8"))
            map_block = existing.group(0) if existing else ""
        markdown = render_chapter.render_chapter(
            verse_links, chapter_content, raw_verses=ctx.raw_verses(), map_block=map_block
        )
        chapter_path.write_text(markdown, encoding="utf-8")
        written.append(chapter_path)
    return written


# --------------------------------------------------------------------------- #
# P4 validate
# --------------------------------------------------------------------------- #
def validate_step(ctx, written):
    errors = []
    old_root = vkb.ROOT
    vkb.ROOT = ctx.root
    try:
        for path in written:
            if path.name.startswith("第") and path.suffix == ".md":
                errors.extend(vkb.validate_chapter(path))
            else:
                file_errors, _ = vkb.validate_file(path, strict=True)
                errors.extend(file_errors)
    finally:
        vkb.ROOT = old_root
    return errors


# --------------------------------------------------------------------------- #
# orchestrate
# --------------------------------------------------------------------------- #
def run_chapter(book, chapter, root=ROOT, runner=None, index=None, homonyms=None,
                entry_limit=None):
    ctx = ChapterContext(
        book, chapter, root=root, runner=runner, index=index, homonyms=homonyms
    )
    plan = resolve_step(ctx)
    entry_payloads = entry_content_step(ctx, plan, limit=entry_limit)
    verse_links = verse_links_step(ctx, plan)
    chapter_content = chapter_content_step(ctx, plan)
    written = render_step(ctx, entry_payloads, verse_links, chapter_content)
    errors = validate_step(ctx, written)
    return {
        "written": written,
        "errors": errors,
        "manual_review": ctx.manual_review,
        "entry_count": len(entry_payloads),
    }


def main():
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("book")
    parser.add_argument("chapter", type=int)
    parser.add_argument("--limit-entries", type=int, default=None,
                        help="只處理前 N 個 C 類新條目（試跑品質用）")
    args = parser.parse_args()
    try:
        result = run_chapter(args.book, args.chapter, entry_limit=args.limit_entries)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"❌ {exc}")
        return 1
    print(f"✅ 完成：寫入 {len(result['written'])} 檔，新增條目 {result['entry_count']}")
    if result["manual_review"]:
        print("⚠️ 需人工處理：")
        for item in result["manual_review"]:
            print(f"   - {item}")
    if result["errors"]:
        print("❌ 結構驗證未過：")
        for item in result["errors"]:
            print(f"   - {item}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
