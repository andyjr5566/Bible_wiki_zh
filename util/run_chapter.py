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
def _model_step(ctx, out_path, prompt, validate, label, normalize=None):
    if out_path.exists():
        return _read_yaml(out_path)
    try:
        payload = call_model(prompt, validate=validate, runner=ctx.runner, label=label)
    except ModelValidationError as exc:
        ctx.manual_review.append(str(exc))
        return None
    if normalize:
        payload = normalize(payload)
    _write_yaml(out_path, payload)
    return payload


# --------------------------------------------------------------------------- #
# M3 entry_content（批量：一次 request 產出多個條目，全部來源直接餵入）
# --------------------------------------------------------------------------- #
BATCH_SIZE = 5


_ENTRY_EXAMPLE = (
    "- name: 施恩座（kapporet）        # 原文類用「中文（希伯來音譯）」；勿寫成「施恩座（原文）」\n"
    "  type: 原文                      # 必須是該條目的分類，不是詞性；不可寫 word/noun\n"
    "  secondary_types: []\n"
    "  aliases: [施恩座]\n"
    "  status: formal\n"
    "  definition: 希伯來文 kapporet，法櫃的蓋子……（完整說明原文、字義與本章用法）\n"
    "  accumulations:                  # 物件陣列，非字串；每項四個欄位\n"
    "    - book: 出埃及記\n"
    "      chapter: 27\n"
    "      summary: 本章對此條目的重點（一句）\n"
    "      relation: 與本章的神學關聯（一句）\n"
    "  related_entries: [法櫃（aron）]  # 只能取自下方允許清單；不可用裸經文引用\n"
    "  sources:                        # 每項含實際來源 URL（取自本章來源清單）\n"
    "    - 'BH: Exodus 27 — 施恩座的字義與位置（https://biblehub.com/study/exodus/27.htm）'\n"
)


def _batch_entry_prompt(ctx, batch, allowed_related, sources_text, raw_text,
                        feedback=None, source_urls=None):
    listing = "\n".join(f"- {e['name']}（分類：{e['suggested_type']}）" for e in batch)
    feedback_block = ""
    if feedback:
        feedback_block = (
            "\n【上一輪這些條目未通過驗證，請務必依錯誤修正】\n"
            + "\n".join(f"- {item}" for item in feedback) + "\n"
        )
    return (
        f"你是聖經研經資料整理員。任務：一次為以下 {len(batch)} 個 link_folder 條目"
        f"各填一份 entry_content payload。\n\n"
        f"【要寫的條目】（括號內是分類，不是名稱的一部分）\n{listing}\n\n"
        f"【本章經文（{ctx.book} 第{ctx.chapter}章）】\n{raw_text}\n\n"
        f"【本章全部來源（CT/GT/KC/BH 全文）】\n{sources_text}\n\n"
        f"【規則】\n"
        f"- 所有陳述須能對應經文或上述來源；未提及者不得寫入。\n"
        f"- type 欄位必須正好是該條目的分類（如 原文、神學），不是詞性——不可寫 word、noun。\n"
        f"- name：原文類用「中文（希伯來音譯）」，其餘用簡明中文；切勿把分類當音譯"
        f"寫成「X（原文）」。找不到音譯就用裸中文名。\n"
        f"- status 一律 formal。accumulations 是「物件陣列」，每項含 book、chapter、"
        f"summary、relation 四欄，且至少含本章（{ctx.book} 第{ctx.chapter}章）一筆、同章只給一筆。\n"
        f"- related_entries 只能從此清單選（用完整條目名，不可用「創3:24」這類裸經文引用）："
        f"{', '.join(allowed_related) or '（無）'}。\n"
        f"- sources 每項格式「標籤: 位置說明（URL）」，標籤與 URL 必須成對取自本章來源："
        f"{'；'.join(f'{kind}: {url}' for kind, url in (source_urls or [])) or '（本章無來源 URL）'}"
        f"——標籤寫錯對應（如 KC 標籤配 CT 的 URL）視為錯誤。\n"
        f"- 互文類條目 name 不可只有經文引用，須用「簡短標題（經文）」，"
        f"例如「天上真聖所（來9：23-24）」；括號內保留原經文、冒號用全形「：」。\n"
        f"- 每個 payload 的 name 必須能對回上面清單（可加音譯後綴）。\n"
        f"{feedback_block}\n"
        f"【輸出格式範例——照此結構輸出一個 YAML 陣列】\n{_ENTRY_EXAMPLE}\n"
        f"【輸出】只輸出一個 YAML 陣列（每個元素以 - 開頭），不要任何說明文字。"
        f"欄位定義見 {_schema_hint('entry_content.schema.json')}"
    )


def _match_payload(entry, results):
    name = entry["name"]
    for payload in results:
        if isinstance(payload, dict) and payload.get("name") == name:
            return payload
    # 原文等：計畫用裸名（皂莢木），模型依慣例加音譯後綴（皂莢木（atzei shittim））。
    # 用「裸名（」前綴比對，避免 銅 誤配到 銅網（...）。
    for payload in results:
        pname = str(payload.get("name", "")) if isinstance(payload, dict) else ""
        if pname.startswith(f"{name}（") or pname.startswith(f"{name}("):
            return payload
    if entry["suggested_type"] == "互文":
        # 冒號無視：計畫用半形（來9:23-24），模型可能用全形（來9：23-24）
        norm = name.replace(":", "：")
        for payload in results:
            pname = str(payload.get("name", "")).replace(":", "：") if isinstance(payload, dict) else ""
            if norm in pname:
                return payload
    return None


_SOURCE_LABEL_RE = re.compile(r"^\s*([A-Z]{2,4})\s*[:：]")


def _entry_source_errors(payload, allowed_urls, url_kinds=None):
    """formal 條目 sources 每項必須含本章 source_manifest 的其中一個 URL，
    且行首標籤（BH/CT/GT/KC）須與該 URL 的 manifest 類型一致。

    manifest 無 URL（如純測試環境）時不啟用；經文引據寫進 definition／
    accumulations，sources 只放可回溯的來源出處。標籤↔URL 驗證（出25 實例：
    「KC: …（…02CT25.htm）」標籤寫 KC、URL 卻是 CT）只在標籤是 manifest
    已知類型時啟用，不限制其他自由寫法。
    """
    if not allowed_urls or payload.get("status") != "formal":
        return []
    url_kinds = url_kinds or {}
    errors = []
    for source in payload.get("sources") or []:
        text = str(source)
        hit = next((url for url in allowed_urls if url in text), None)
        if hit is None:
            errors.append(
                f"sources「{text}」未含本章來源 URL；每項格式「標籤: 位置說明（URL）」，"
                f"URL 取自：{'、'.join(allowed_urls)}"
            )
            continue
        kind = url_kinds.get(hit)
        label = _SOURCE_LABEL_RE.match(text)
        if kind and label and label.group(1) != kind:
            errors.append(
                f"sources「{text}」標籤「{label.group(1)}」與 URL 不符：該 URL 屬 {kind}，"
                f"請改用正確標籤或換成 {label.group(1)} 的 URL"
            )
    return errors


def _entry_alias_errors(entry, payload, owners):
    """aliases 驗證左移：不得與既有條目（名稱或 alias）、本章計畫或已接受的
    其他條目衝突，否則 build_link_index 才爆「alias 衝突／多重指向」。

    出25 實例：模型幫「甘心樂意的奉獻（林後9：7）」加 alias「甘心樂意的奉獻」
    撞上同批正式條目；兩個條目同時認領「山上指示的樣式」。條目以計畫裸名
    作自身 alias（皂莢木 ↔ 皂莢木（atzei shittim））屬合法慣例，不擋。
    """
    own = {
        render_entry.safe_name(str(payload.get("name", ""))),
        render_entry.safe_name(entry["name"]),
    }
    errors = []
    for alias in payload.get("aliases") or []:
        norm = render_entry.safe_name(str(alias))
        owner = owners.get(norm)
        if owner and owner not in own:
            errors.append(
                f"aliases「{alias}」已屬於條目「{owner}」（既有或同批），請移除此 alias"
            )
    return errors


def _alias_owners(index, planned_names, payloads):
    """名稱／alias（safe_name 後）→ 擁有者條目名，供 alias 衝突驗證。

    涵蓋全庫索引（alias 歸還其正式條目）、本章計畫中的 C 類名稱、已接受的
    同章 payload（含其 aliases）。
    """
    owners = {}
    for key, info in (index or {}).items():
        if isinstance(info, dict):
            title = info.get("alias_of") or info.get("title") or key
        else:
            title = key
        owners[render_entry.safe_name(key)] = render_entry.safe_name(str(title))
    for name in planned_names:
        owners.setdefault(name, name)
    for payload in payloads.values():
        _register_alias_owner(owners, payload)
    return owners


def _register_alias_owner(owners, payload):
    name = render_entry.safe_name(str(payload.get("name", "")))
    owners[name] = name
    for alias in payload.get("aliases") or []:
        owners.setdefault(render_entry.safe_name(str(alias)), name)


def _run_entry_batch(ctx, batch, allowed_related, sources_text, raw_text, known,
                     feedback=None, source_urls=None, owners=None):
    """回傳 (通過驗證的 payloads, 各條目的失敗原因)。失敗原因供下一輪回饋模型。

    owners（名稱／alias → 擁有者）為可變 dict：payload 通過驗證即登記其名稱
    與 aliases，讓同批後續條目的 alias 衝突當場擋下。
    """
    prompt = _batch_entry_prompt(
        ctx, batch, allowed_related, sources_text, raw_text, feedback, source_urls
    )
    try:
        results = call_model(
            prompt,
            validate=lambda p: [] if isinstance(p, list) and p else ["需回傳非空的 payload 陣列"],
            runner=ctx.runner, label="entry_batch",
        )
    except ModelValidationError:
        return {}, {e["name"]: "模型未回傳有效 payload 陣列" for e in batch}
    matched, errors = {}, {}
    allowed_urls = [url for _, url in (source_urls or [])]
    url_kinds = dict((url, kind) for kind, url in (source_urls or []))
    for entry in batch:
        payload = _match_payload(entry, results)
        if payload is None:
            errors[entry["name"]] = "找不到對應此條目的 payload（name 需能對回清單）"
            continue
        verrs = render_entry.validate_payload(payload, known_types=known)
        verrs.extend(_entry_source_errors(payload, allowed_urls, url_kinds))
        if owners is not None:
            verrs.extend(_entry_alias_errors(entry, payload, owners))
        if verrs:
            errors[entry["name"]] = "；".join(verrs)
            continue
        matched[entry["name"]] = payload
        if owners is not None:
            _register_alias_owner(owners, payload)
    return matched, errors


def entry_content_step(ctx, plan, limit=None, batch_size=BATCH_SIZE):
    out_dir = ctx.path("entry_content")
    known = ctx.known_types()
    raw_text = "\n".join(f"{i}. {v}" for i, v in enumerate(ctx.raw_verses(), 1))
    sources_text = source_excerpts.full_source_text(ctx.sources())
    # 候選去重：計畫可能同名重複（柱子×2、銀座×2…），否則各批各建一次會產生重複條目
    seen_names = set()
    c_entries = [e for e in plan.get("C_new_formal", [])
                 if not (e["name"] in seen_names or seen_names.add(e["name"]))]
    # related_entries 允許清單＝A/B 既有條目標題＋本批 C 類候選名（同批建立）
    existing_titles = [
        e.get("existing_title") or e["name"]
        for key in ("A_use_directly", "B_needs_update")
        for e in plan.get(key, [])
    ]
    allowed_related = list(dict.fromkeys(existing_titles + [e["name"] for e in c_entries]))
    # (類型, url) 成對供 prompt 與標籤↔URL 驗證；類型即模型該寫的標籤（BH/CT/GT/KC）
    source_urls = source_excerpts.manifest_kind_urls(ctx.path("source_manifest.md"))
    if limit is not None:
        c_entries = c_entries[:limit]

    # resume：讀已存在的 payload。裸候選名（撚的細麻）要對得上實建全名（撚的細麻（…）），
    # 否則每次 resume 都判定未完成 → 重建出音譯略異的重複條目。
    existing = [_read_yaml(p) for p in sorted(out_dir.glob("*.yaml"))] if out_dir.exists() else []
    payloads = {p["name"]: p for p in existing if isinstance(p, dict) and p.get("name")}

    def done(entry):
        name = entry["name"]
        for payload in existing:
            title = payload.get("name", "") if isinstance(payload, dict) else ""
            if (title == name or title.startswith(f"{name}（") or title.startswith(f"{name}(")
                    or (entry["suggested_type"] == "互文"
                        and name.replace(":", "：") in title.replace(":", "："))):
                return True
        return False

    pending = [e for e in c_entries if not done(e)]
    # alias 衝突驗證左移：既有索引（alias 歸還正式條目）＋計畫中 C 類名稱＋
    # 已接受 payload（含 resume 讀回的）；批次內通過者即時登記，同批也擋。
    index = ctx.index if ctx.index is not None else resolver.load_index()
    planned_names = {render_entry.safe_name(e["name"]) for e in c_entries}
    owners = _alias_owners(index, planned_names, payloads)
    last_errors = {}
    for _ in range(2):  # 一輪批量 + 一輪（帶錯誤回饋的）重做
        failed, feedback = [], None
        for start in range(0, len(pending), batch_size):
            batch = pending[start:start + batch_size]
            if last_errors:
                feedback = [f"{e['name']}：{last_errors[e['name']]}"
                            for e in batch if e["name"] in last_errors]
            results, errors = _run_entry_batch(
                ctx, batch, allowed_related, sources_text, raw_text, known,
                feedback, source_urls, owners
            )
            for entry in batch:
                payload = results.get(entry["name"])
                if payload is None:
                    failed.append(entry)
                    last_errors[entry["name"]] = errors.get(entry["name"], "不合格")
                    continue
                last_errors.pop(entry["name"], None)
                payload["name"] = render_entry.safe_name(payload["name"])  # 半形冒號→全形
                _write_yaml(out_dir / f"{payload['name']}.yaml", payload)
                payloads[payload["name"]] = payload
        pending = failed
        if not pending:
            break
    for entry in pending:
        reason = last_errors.get(entry["name"], "不合格")
        ctx.manual_review.append(f"entry_content:{entry['name']}：批量重做後仍不合格（{reason}）")
    ctx.created_entry_names = list(payloads)
    return payloads


# --------------------------------------------------------------------------- #
# M5 verse_links
# --------------------------------------------------------------------------- #
def _created_title(candidate, created_names):
    """候選裸名 → 模型實建的完整條目名（皂莢木 → 皂莢木（atzei shittim））。"""
    name = candidate["name"]
    for full in created_names:
        if full == name or full.startswith(f"{name}（") or full.startswith(f"{name}("):
            return full
    if candidate.get("suggested_type") == "互文":
        norm = name.replace(":", "：")
        for full in created_names:
            if norm in full.replace(":", "："):
                return full
    return None


def build_surface_map(ctx, plan):
    """裸名（皂莢木、摩西）→ 條目全名（皂莢木（atzei shittim）、摩西）。

    A/B 用既有標題、C 用模型實建全名；再補上實建條目的裸名。這是「經文詞 →
    要連去的條目檔」的對照表。
    """
    surface_to_title = {}
    for key in ("A_use_directly", "B_needs_update"):
        for e in plan.get(key, []):
            surface_to_title.setdefault(e["name"], e.get("existing_title") or e["name"])
    created = list(getattr(ctx, "created_entry_names", []))
    for e in plan.get("C_new_formal", []):
        full = _created_title(e, created)
        if full:
            surface_to_title.setdefault(e["name"], full)
    for name in created:
        base = name.split("（", 1)[0].split("(", 1)[0].strip()
        if base:
            surface_to_title.setdefault(base, name)
    return surface_to_title


def verse_links_step(ctx, plan):
    """程式化標注（不呼叫模型）：逐節掃描可連詞、長詞優先、同節不重疊。

    連詞是機械工作——把「已知詞彙」對到「經文子字串」——交給程式比模型可靠：
    模型多次無法穩定產出對得上經文的 phrase／target。程式直接掃 raw 經文，
    連出來的一定是經文子字串、target 一定是既有條目，零漂移。事件／互文等不會
    出現在經文字面的條目自然不會被連（它們屬章節層 knowledge_nodes，非內文連結）。
    """
    out_path = ctx.path("verse_links.yaml")
    if out_path.exists():
        return _read_yaml(out_path)
    raw_verses = ctx.raw_verses()
    surface_to_title = build_surface_map(ctx, plan)
    surfaces = [s for s in surface_to_title if s]
    links = []
    for vnum, verse in enumerate(raw_verses, 1):
        spans = []
        for surface in surfaces:
            idx = verse.find(surface)
            if idx != -1:  # 每詞每節只連首次出現，避免同詞洗版
                spans.append((idx, idx + len(surface), surface))
        spans.sort(key=lambda s: (s[0], -(s[1] - s[0])))  # 起點升冪、長詞優先
        last_end = -1
        for start, end, surface in spans:
            if start >= last_end:  # 不重疊：銅座 勝過 銅
                links.append({"verse": vnum, "phrase": surface,
                              "target": surface_to_title[surface]})
                last_end = end
    payload = {"book": ctx.book, "chapter": ctx.chapter, "links": links}
    _write_yaml(out_path, payload)
    return payload


# --------------------------------------------------------------------------- #
# M6 chapter_content
# --------------------------------------------------------------------------- #
def _org_requirements(verse_count):
    """本章整理的份量門檻（隨章節長度調整），供 prompt 與驗證共用。

    參考基準：已完成章節（出17–19）的本章整理為多個「### 段落小節」的長篇
    散文；沒有門檻時模型傾向交出三行條列（出25 第一次重做即如此）。
    """
    min_sections = 3 if verse_count >= 15 else 2
    min_chars = max(400, min(1500, verse_count * 40))
    return min_sections, min_chars


def _chapter_payload_validator(verse_count):
    min_sections, min_chars = _org_requirements(verse_count)

    def validate(payload):
        errors = render_chapter.validate_chapter_content(payload)
        organization, _ = render_chapter.split_references(
            render_chapter.coerce_organization(payload.get("organization"))
        )
        sections = re.findall(r"^###\s+\S", organization, re.M)
        if len(sections) < min_sections:
            errors.append(
                f"organization 需依本章段落結構分成至少 {min_sections} 個小節，"
                f"每小節以「### 標題（vX-Y）」開頭（目前只有 {len(sections)} 個）"
            )
        if len(organization) < min_chars:
            errors.append(
                f"organization 太薄（{len(organization)} 字）：需 ≥{min_chars} 字的"
                f"整合性散文，逐段整合各來源重點並標明出處（CT指出…、KC指出…）"
            )
        return errors

    return validate


def chapter_content_step(ctx, plan):
    out_path = ctx.path("chapter_content.yaml")
    raw_verses = ctx.raw_verses()
    raw_text = "\n".join(f"{i}. {v}" for i, v in enumerate(raw_verses, 1))
    sources_text = source_excerpts.full_source_text(ctx.sources())
    created = list(getattr(ctx, "created_entry_names", []))
    created_hint = (
        f"\n本章新建條目（knowledge_nodes 若引用請用完整名稱）：{', '.join(created)}"
        if created else ""
    )
    min_sections, min_chars = _org_requirements(len(raw_verses))
    prompt = (
        f"你是聖經研經資料整理員。唯一任務：為 {ctx.book} 第{ctx.chapter}章填寫 "
        f"chapter_content payload（本章知識節點 + 本章整理）。\n\n【經文】\n{raw_text}\n\n"
        f"【本章全部來源（CT/GT/KC/BH 全文）】\n{sources_text}\n\n"
        f"【規則】knowledge_nodes 是「分組→節點清單」的物件，例如：\n"
        f"  神學: [會幕, 神的同在]\n  原文: [皂莢木（atzei shittim）]\n"
        f"只列值得跨章累積的核心節點，不重列所有經文 link。{created_hint}\n\n"
        f"organization（本章整理）是本章的詳盡研讀整理，要求：\n"
        f"- 依本章段落結構分成至少 {min_sections} 個小節，每小節以「### 標題（vX-Y）」"
        f"開頭；最後可加一個跨章脈絡／預表整理的主題小節。\n"
        f"- 每小節是連貫散文（不用條列），沿經文脈絡敘述並整合各來源觀點，"
        f"標明出處，寫法如「CT指出…」「GT指出…」「KC指出…」「BH指出…」。\n"
        f"- 全文合計 ≥{min_chars} 字；整合重點而非搬運來源全文，"
        f"也不得寫入來源未提及的內容。\n"
        f"- 不要寫「參考資料」清單——程式會自動附上來源 URL。\n\n"
        f"【輸出】只輸出 YAML：\n{_schema_hint('chapter_content.schema.json')}"
    )

    def _normalize(payload):
        payload["book"] = ctx.book
        payload["chapter"] = ctx.chapter
        return payload

    payload = _model_step(
        ctx, out_path, prompt,
        validate=_chapter_payload_validator(len(raw_verses)),
        label="chapter_content", normalize=_normalize,
    )
    return _inject_references(ctx, out_path, payload)


def _inject_references(ctx, out_path, payload):
    """章節「參考資料」不由模型手寫：程式從 source_manifest 注入 OK 來源的 URL。

    也涵蓋 resume（舊 payload 無 references）；organization 內殘留的參考資料
    區塊一併拆出合流，重跑冪等。
    """
    if payload is None:
        return None
    organization, inline_refs = render_chapter.split_references(
        render_chapter.coerce_organization(payload.get("organization"))
    )
    manifest_refs = [
        url for _, url in source_excerpts.manifest_urls(ctx.path("source_manifest.md"))
    ]
    references = manifest_refs or payload.get("references") or inline_refs
    updated = dict(payload, organization=organization, references=references)
    if updated != payload:
        _write_yaml(out_path, updated)
    return updated


# --------------------------------------------------------------------------- #
# P3 render（程式產生 markdown）
# --------------------------------------------------------------------------- #
_OTHER_CHAPTER_ACCUM_RE = re.compile(r"<!-- accumulation:([^:]+):(\d+):start -->")


def _would_destroy_data(ctx, target):
    """既有條目檔內含「其他章節」累積標記時，覆寫會毀掉跨章資料——拒絕覆寫。"""
    if not target.exists():
        return False
    text = target.read_text(encoding="utf-8")
    for book, chapter in _OTHER_CHAPTER_ACCUM_RE.findall(text):
        if not (book == ctx.book and chapter == str(ctx.chapter)):
            return True
    return False


def _related_title_map(ctx, plan, created_names):
    """裸名／別名 → 條目完整標題的對照，用於 related_entries 閉合。

    涵蓋全庫索引（含 aliases）、本章 A/B 既有條目、本批實建條目。
    """
    index = ctx.index if ctx.index is not None else resolver.load_index()
    mapping = {}
    for key, info in (index or {}).items():
        # alias 鍵歸還其正式條目名（alias_of），閉合結果一律是實際檔名
        if isinstance(info, dict):
            title = info.get("alias_of") or info.get("title") or key
        else:
            title = key
        mapping[render_entry.safe_name(key)] = title
    for category in ("A_use_directly", "B_needs_update"):
        for e in (plan or {}).get(category, []):
            title = e.get("existing_title") or e["name"]
            mapping[render_entry.safe_name(e["name"])] = title
            mapping[render_entry.safe_name(title)] = title
    for name in created_names:
        mapping[render_entry.safe_name(name)] = name
    return mapping


def _resolve_related(item, mapping):
    """related_entries 單項 → 條目完整標題；無法唯一對應則回 None（丟棄）。

    對應序：完全同名（含別名）→ 音譯前綴（皂莢木 → 皂莢木（atzei shittim））
    → 裸經文引用對互文標題（創3:24 → 把守生命樹的道路（創3：24））。
    模型愛在相關條目塞裸經文引用，成品就是一堆沒有 md 的 [[創3:24]]——
    在這裡由程式閉合，related_entries 渲染出去必有對應條目。
    """
    inner = str(item).strip()
    match = re.fullmatch(r"\[\[(.+?)\]\]", inner)
    if match:
        inner = match.group(1)
    name = render_entry.safe_name(inner.partition("|")[0])
    if not name:
        return None
    title = mapping.get(name)
    if title:
        return title
    titles = sorted(set(mapping.values()))
    hits = [t for t in titles if t.startswith(f"{name}（")]
    if not hits and render_entry.BARE_SCRIPTURE_REF_RE.match(name):
        hits = [t for t in titles if name in t]
    return hits[0] if len(hits) == 1 else None


def _close_knowledge_nodes(chapter_content, mapping):
    """knowledge_nodes 與 related_entries 同法閉合：裸名／別名 → 條目全名，
    無對應者移除並回報。

    related_entries 有閉合而知識節點沒有，模型照樣寫裸名（出25 實例：寫
    「禮物」「法版」，實建條目是「禮物（terumah）」「法版（edut）」），
    渲染出的章節連結就是斷鏈——在這裡由程式閉合。回傳 (閉合後 payload,
    被移除清單)；不回寫 chapter_content.yaml，閉合是渲染期行為。
    """
    nodes = render_chapter.coerce_knowledge_nodes(chapter_content.get("knowledge_nodes"))
    closed, dropped = {}, []
    for group, items in nodes.items():
        resolved = []
        for item in items:
            title = _resolve_related(item, mapping)
            if title and title not in resolved:
                resolved.append(title)
            elif title is None:
                dropped.append(str(item))
        if resolved:
            closed[group] = resolved
    return dict(chapter_content, knowledge_nodes=closed), dropped


def render_step(ctx, entry_payloads, verse_links, chapter_content, plan=None):
    written = []
    known = ctx.known_types()
    # 章節 knowledge_nodes 也要閉合，無 C 類條目時仍需全庫對照表
    related_map = _related_title_map(ctx, plan, list(entry_payloads))
    for name, payload in entry_payloads.items():
        safe = render_entry.safe_name(name)
        resolved, dropped = [], []
        for item in payload.get("related_entries") or []:
            title = _resolve_related(item, related_map)
            if title == safe:
                continue  # 自我引用，靜默去除
            if title and title not in resolved:
                resolved.append(title)
            elif title is None:
                dropped.append(str(item))
        if dropped:
            ctx.manual_review.append(
                f"related_entries:{name}：無對應條目，已移除：{'、'.join(dropped)}"
            )
        payload = {**payload, "related_entries": resolved}
        target = ctx.root / "link_folder" / payload["type"] / f"{safe}.md"
        if _would_destroy_data(ctx, target):
            ctx.manual_review.append(
                f"entry_content:{name}：既有條目已含其他章節累積，跳過以免覆蓋（應歸 B 累積）"
            )
            continue
        markdown = render_entry.render_entry(payload, known_types=known)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(markdown, encoding="utf-8")
        written.append(target)
    if verse_links and chapter_content:
        chapter_content, node_dropped = _close_knowledge_nodes(chapter_content, related_map)
        if node_dropped:
            ctx.manual_review.append(
                f"knowledge_nodes：無對應條目，已移除：{'、'.join(node_dropped)}"
            )
        if not chapter_content.get("knowledge_nodes"):
            # 全數無對應（例如條目批量整批失敗）：跳過章節渲染交人工，
            # 不讓 render_chapter 的驗證把整條流程炸掉；resume 補完條目後重跑即可
            ctx.manual_review.append(
                "chapter：knowledge_nodes 閉合後全空，章節未渲染（先補條目再重跑）"
            )
            return written
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
    written = render_step(ctx, entry_payloads, verse_links, chapter_content, plan=plan)
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
