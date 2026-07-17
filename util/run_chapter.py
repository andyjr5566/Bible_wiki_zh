#!/usr/bin/env python3
"""章節製作 orchestrator：程式主導、模型只填 payload。

流程（每步以 .tmp/第x章/ 內的檔案存在與否斷點續跑）：

  P2 resolve         link_candidates(.yaml/.md) → link_plan.yaml            （程式）
  M3 entry_content   每個 C 類條目呼叫模型填 payload → schema 驗證 → 重試   （模型）
  M5 verse_links     程式化標注（不呼叫模型）：逐節掃描可連詞、長詞優先、同節不重疊  (程式）
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


def _log(message):
    """進度訊息印到 stderr——模型呼叫可能單次卡數分鐘，讓終端機不要整段空白。"""
    print(message, file=sys.stderr, flush=True)


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
def _annotate_semantic(plan):
    """對 C／D 候選附語義近鄰提示；索引缺失或端點不通時降級略過，不擋流程。

    純附註供人工在 link_plan.yaml 判斷近似重複，不改分類、不建連結。
    """
    try:
        import semantic_lookup
        lookup = semantic_lookup.SemanticIndex.load()
    except Exception as exc:  # 索引未建、模型不符、端點不通都不該中斷主流程
        _log(f"  （語義提示略過：{exc}）")
        return
    try:
        resolver.annotate_plan_semantically(
            plan, lookup, threshold=resolver.SEMANTIC_HINT_THRESHOLD
        )
    except Exception as exc:
        _log(f"  （語義提示中途失敗，已略過：{exc}）")


def resolve_step(ctx):
    plan_path = ctx.path("link_plan.yaml")
    if plan_path.exists():
        return _read_yaml(plan_path)
    _log(f"▶ P2 resolve：{ctx.book} 第{ctx.chapter}章 連結計畫產生中…")
    index = resolver.load_index() if ctx.index is None else ctx.index
    homonyms = resolver.load_homonyms() if ctx.homonyms is None else ctx.homonyms
    candidates = resolver.load_candidates(ctx.book, ctx.chapter, root=ctx.root)
    plan = resolver.resolve(candidates, index, ctx.book, ctx.chapter, root=ctx.root, homonyms=homonyms)
    _annotate_semantic(plan)
    document = resolver.build_plan_document(plan, ctx.book, ctx.chapter)
    _write_yaml(plan_path, document)
    _log("✔ P2 resolve 完成")
    return document


# --------------------------------------------------------------------------- #
# 模型步驟共用：resume + call_model + 寫檔；失敗記入 manual_review
# --------------------------------------------------------------------------- #
def _model_step(ctx, out_path, prompt, validate, label, normalize=None, task=None):
    if out_path.exists():
        return _read_yaml(out_path)
    try:
        payload = call_model(prompt, validate=validate, runner=ctx.runner, label=label, task=task)
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
BATCH_SIZE = 10


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
    "      summary: 本章對此條目的重點\n"
    "      relation: 與本章的神學關聯\n"
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
        f"你是聖經研經資料整理員，並且輸出以繁體中文為主。任務：一次為以下 {len(batch)} 個 link_folder 條目"
        f"各填一份 entry_content payload。\n\n"
        f"【要寫的條目】（括號內是分類，不是名稱的一部分）\n{listing}\n\n"
        f"【本章經文（{ctx.book} 第{ctx.chapter}章）】\n{raw_text}\n\n"
        f"【本章全部來源）】\n{sources_text}\n\n"
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
            runner=ctx.runner, label="entry_batch", task="entry",
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
    if pending:
        _log(f"▶ M3 entry_content：{len(pending)} 個條目待建（每批 {batch_size} 個）")
    last_errors = {}
    for round_num in range(2):  # 一輪批量 + 一輪（帶錯誤回饋的）重做
        failed, feedback = [], None
        total_batches = (len(pending) + batch_size - 1) // batch_size
        for batch_num, start in enumerate(range(0, len(pending), batch_size), 1):
            batch = pending[start:start + batch_size]
            if last_errors:
                feedback = [f"{e['name']}：{last_errors[e['name']]}"
                            for e in batch if e["name"] in last_errors]
            _log(
                f"  · entry_content 第 {round_num + 1} 輪 批次 {batch_num}/{total_batches}"
                f"（{len(batch)} 條目）呼叫模型中…"
            )
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


def _base_surface(title):
    """括號前裸名（皂莢木（atzei shittim）→ 皂莢木）；無括號時回 None。"""
    base = title.split("（", 1)[0].split("(", 1)[0].strip()
    return base if base and base != title else None


def _payload_aliases(ctx):
    """本章 entry_content payload 的 aliases——C 類新條目尚未進全庫索引，
    其別稱只能從本章 payload 檔取得（斷點續跑也讀得到）。"""
    out_dir = ctx.path("entry_content")
    if not out_dir.exists():
        return {}
    aliases = {}
    for path in sorted(out_dir.glob("*.yaml")):
        data = _read_yaml(path)
        if isinstance(data, dict) and data.get("name"):
            aliases[data["name"]] = [
                str(a).strip() for a in (data.get("aliases") or []) if str(a).strip()
            ]
    return aliases


def build_surface_map(ctx, plan):
    """經文詞 →｛target, verses, declared｝對照表（verses=None 表全章可連）。

    詞彙推導層級（高→低；跨層由高層勝出、同層同詞指向不同條目＝歧義不連）：
      0. 候選宣告的 surfaces（人工判斷，可帶 verses 限定節次）
      1. 候選名稱（A/B 對 existing_title、C 對實建全名）
      2. 條目全名與其括號前裸名（皂莢木（atzei shittim）→ 皂莢木）
      3. 條目 aliases（A/B 取自全庫索引、C 取自本章 entry_content payload）

    aliases 與裸名入詞彙表是「raw data 有補充的經文詞也要連上」的關鍵：
    經文常用簡稱（法櫃、燈臺、皂莢木），只比對候選宣告名永遠對不上。
    歧義詞整詞不連並記 manual_review，對應 D 類「歧義交人工」精神。
    """
    index = ctx.index if ctx.index is not None else resolver.load_index()
    payload_aliases = _payload_aliases(ctx)
    created = list(getattr(ctx, "created_entry_names", []))
    records = []  # (priority, surface, target, verses)

    def add(priority, surface, target, verses=None):
        surface = (surface or "").strip()
        if surface and target:
            records.append((priority, surface, target, verses))

    def add_declared(entry, target):
        for item in entry.get("surfaces") or []:
            if isinstance(item, dict):
                verses = item.get("verses")
                add(0, item.get("phrase"), target,
                    {int(v) for v in verses} if verses else None)
            else:
                add(0, item, target)

    def add_title_forms(title):
        add(2, title, title)
        add(2, _base_surface(title), title)

    for key in ("A_use_directly", "B_needs_update"):
        for e in plan.get(key, []):
            title = e.get("existing_title") or e["name"]
            add_declared(e, title)
            add(1, e["name"], title)
            add_title_forms(title)
            info = index.get(title)
            for alias in (info or {}).get("aliases") or []:
                add(3, alias, title)
    for e in plan.get("C_new_formal", []):
        full = _created_title(e, created)
        if not full:
            continue
        add_declared(e, full)
        add(1, e["name"], full)
    for name in created:
        add_title_forms(name)
        for alias in payload_aliases.get(name, []):
            add(3, alias, name)

    by_surface = {}
    for record in records:
        by_surface.setdefault(record[1], []).append(record)
    surface_map, ambiguous = {}, []
    for surface, recs in by_surface.items():
        top_priority = min(r[0] for r in recs)
        top = [r for r in recs if r[0] == top_priority]
        targets = {r[2] for r in top}
        if len(targets) > 1:
            ambiguous.append(f"{surface}（{'／'.join(sorted(targets))}）")
            continue
        verses = None
        if all(r[3] is not None for r in top):
            verses = set().union(*(r[3] for r in top))
        surface_map[surface] = {
            "target": targets.pop(),
            "verses": verses,
            "declared": top_priority == 0,
        }
    if ambiguous:
        ctx.manual_review.append(
            f"verse_links：同一經文詞指向多個條目，歧義不自動連結：{'；'.join(sorted(ambiguous))}"
        )
    return surface_map


def verse_links_step(ctx, plan):
    """程式化標注（不呼叫模型）：逐節掃描可連詞、長詞優先、同節不重疊。

    連詞是機械工作——把「已知詞彙」對到「經文子字串」——交給程式比模型可靠：
    模型多次無法穩定產出對得上經文的 phrase／target。程式直接掃 raw 經文，
    連出來的一定是經文子字串、target 一定是既有條目，零漂移。事件／互文等不會
    出現在經文字面的條目自然不會被連（它們屬章節層 knowledge_nodes，非內文連結）。
    詞彙表的推導（含 aliases 與候選宣告 surfaces）見 build_surface_map。
    """
    out_path = ctx.path("verse_links.yaml")
    if out_path.exists():
        return _read_yaml(out_path)
    _log("▶ M5 verse_links：程式化標注中…")
    raw_verses = ctx.raw_verses()
    surface_map = build_surface_map(ctx, plan)
    links = []
    matched = set()
    for vnum, verse in enumerate(raw_verses, 1):
        spans = []
        for surface, info in surface_map.items():
            if info["verses"] is not None and vnum not in info["verses"]:
                continue
            idx = verse.find(surface)
            if idx != -1:  # 每詞每節只連首次出現，避免同詞洗版
                spans.append((idx, idx + len(surface), surface))
        spans.sort(key=lambda s: (s[0], -(s[1] - s[0])))  # 起點升冪、長詞優先
        last_end = -1
        for start, end, surface in spans:
            if start >= last_end:  # 不重疊：銅座 勝過 銅
                links.append({"verse": vnum, "phrase": surface,
                              "target": surface_map[surface]["target"]})
                matched.add(surface)
                last_end = end
    missing = sorted(
        s for s, info in surface_map.items() if info["declared"] and s not in matched
    )
    if missing:
        ctx.manual_review.append(
            f"verse_links：候選宣告的 surfaces 未連上任何節（不在經文或被長詞覆蓋）："
            f"{'、'.join(missing)}"
        )
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
    門檻只管份量，不管體裁——創8 那種散文混表格／編號清單的呈現是允許的，
    格式隨 rawdata 的材料性質調整。
    """
    min_sections = 1 #3 if verse_count >= 15 else 2
    min_chars = 200#max(400, min(1500, verse_count * 40))
    return min_sections, min_chars


_ORG_WIKILINK_RE = re.compile(r"\[\[([^\]\r\n]+)\]\]")


def _org_wikilink_targets(organization):
    """organization 內 wiki-link 的 target 集合（去掉 |顯示詞 與 #^ 錨點）。"""
    return {
        re.split(r"[#^]", match.group(1).partition("|")[0], maxsplit=1)[0].strip()
        for match in _ORG_WIKILINK_RE.finditer(organization)
    }


_ORG_NON_PROSE_RE = re.compile(r"^\s*(?:#{1,6}\s|>|\||[-*+]\s|\d+[.、)]\s?)")


def _org_prose_chars(organization):
    """散文主幹字數：去除標題、callout／引用、表格、條列行後的內文長度。"""
    return sum(
        len(line.strip())
        for line in organization.splitlines()
        if line.strip() and not _ORG_NON_PROSE_RE.match(line)
    )


_ORG_FENCE_RE = re.compile(r"```([^\n`]*)\n(.*?)```", re.S)

# mermaid 只放行這幾種穩定圖型；gantt/er 等模型產出易壞
_MERMAID_TYPES = ("flowchart", "graph", "timeline", "mindmap", "sequenceDiagram")


def _org_split_fences(organization):
    """拆出 ``` 圍欄區塊：回傳（圍欄外文字, [(語言標記, 內文), …]）。

    mermaid 的節點語法（A[[x]]、A --> B）會誤傷 wiki-link 判定與散文
    計數，所以 fence 內文先拆掉，其餘檢查只看圍欄外文字。
    """
    fences = [
        (m.group(1).strip(), m.group(2))
        for m in _ORG_FENCE_RE.finditer(organization)
    ]
    return _ORG_FENCE_RE.sub("", organization), fences


def _mermaid_type(body):
    """mermaid 區塊第一個有效字（跳過空行與 %% 註解），即圖型宣告。"""
    for line in body.splitlines():
        line = line.strip()
        if line and not line.startswith("%%"):
            return line.split()[0].rstrip(";")
    return ""


def _chapter_payload_validator(verse_count, allowed_links=None):
    """份量門檻＋散文主幹門檻＋（allowed_links 給定時）wiki-link 白名單檢查。

    體裁自由（表格／清單／callout／高亮／mermaid 圖表隨材料用），但兩頭有欄杆：
    - 白名單擋壞連結進 vault；零連結擋出34 式的圖譜孤島；
    - 散文主幹下限擋「大半內容包進表格、callout 或圖表」的放飛；
    - ![[]] 嵌入（重複條目內文）直接禁；``` 圍欄只放行 mermaid，
      且圖型限 _MERMAID_TYPES（其他圖型模型產出易壞）。
    """
    min_sections, min_chars = _org_requirements(verse_count)

    def validate(payload):
        errors = render_chapter.validate_chapter_content(payload)
        organization, _ = render_chapter.split_references(
            render_chapter.coerce_organization(payload.get("organization"))
        )
        org_text, fences = _org_split_fences(organization)
        sections = re.findall(r"^###\s+\S", org_text, re.M)
        if len(sections) < min_sections:
            errors.append(
                f"organization 需依本章段落結構分成至少 {min_sections} 個小節，"
                f"每小節以「### 標題（vX-Y）」開頭（目前只有 {len(sections)} 個）"
            )
        if len(organization) < min_chars:
            errors.append(
                f"organization 太薄（{len(organization)} 字）：需 ≥{min_chars} 字，"
                f"逐段整合各來源重點；散文為主，"
                f"適合對照的材料可用表格或編號清單"
            )
        prose_chars = _org_prose_chars(org_text)
        min_prose = min_chars // 2
        if prose_chars < min_prose:
            errors.append(
                f"organization 散文主幹太薄（{prose_chars} 字，需 ≥{min_prose} 字）："
                f"表格、清單、callout、圖表只是補充，整合性的連貫敘述才是主幹，"
                f"不可把大半內容包進去"
            )
        if "![[" in org_text:
            errors.append(
                "organization 不可用 ![[]] 嵌入（會在章節頁重複條目全文），"
                "改用一般 wiki-link [[完整條目名]]"
            )
        if "```" in org_text:
            errors.append(
                "organization 的 ``` 圍欄沒有閉合：每個 ```mermaid 區塊"
                "必須以獨立一行 ``` 結尾"
            )
        for lang, body in fences:
            if lang != "mermaid":
                errors.append(
                    f"organization 只能用 ```mermaid 圖表區塊，不可用其他"
                    f"程式碼區塊（發現 ```{lang or '（無語言標記）'}）"
                )
            elif _mermaid_type(body) not in _MERMAID_TYPES:
                errors.append(
                    f"mermaid 圖表第一行必須是 {'／'.join(_MERMAID_TYPES)} "
                    f"其中之一（發現「{_mermaid_type(body) or '空區塊'}」）"
                    f"——其他圖型易產出壞語法"
                )
            elif "[[" in body:
                errors.append(
                    "mermaid 圖內不可出現 [[（wiki-link 在圖中無效，"
                    "且會被 vault 連結檢查掃成壞連結）："
                    '節點一律用雙引號方形 A["標籤"]'
                )
        if allowed_links:
            targets = _org_wikilink_targets(org_text)
            unknown = sorted(targets - set(allowed_links))
            if unknown:
                errors.append(
                    f"organization 的 wiki-link 目標不在本章可連清單："
                    f"{'、'.join(unknown)}——只能連本章條目的完整名稱，"
                    f"行文用詞不同時寫 [[完整條目名|行文用詞]]"
                )
            if not targets:
                errors.append(
                    "organization 沒有任何 wiki-link：行文首次提到本章條目時，"
                    "應以 [[完整條目名|行文用詞]] 連結，讓整理接入 Obsidian 圖譜"
                )
        return errors

    return validate


def chapter_content_step(ctx, plan):
    out_path = ctx.path("chapter_content.yaml")
    if not out_path.exists():
        _log("▶ M6 chapter_content：本章整理呼叫模型中…")
    raw_verses = ctx.raw_verses()
    raw_text = "\n".join(f"{i}. {v}" for i, v in enumerate(raw_verses, 1))
    sources_text = source_excerpts.full_source_text(ctx.sources())
    created = list(getattr(ctx, "created_entry_names", []))
    created_hint = (
        f"\n本章新建條目（knowledge_nodes 若引用請用完整名稱）：{', '.join(created)}"
        if created else ""
    )
    # 本章整理可連的 wiki-link 白名單＝A/B 既有條目標題＋本章實建 C 條目
    existing_titles = [
        e.get("existing_title") or e["name"]
        for key in ("A_use_directly", "B_needs_update")
        for e in plan.get(key, [])
    ]
    allowed_links = list(dict.fromkeys(existing_titles + created))
    min_sections, min_chars = _org_requirements(len(raw_verses))
    prompt = (
        f"你是聖經研經資料整理員。唯一任務：為 {ctx.book} 第{ctx.chapter}章填寫 "
        f"chapter_content payload（本章知識節點 + 本章整理）。\n\n【經文】\n{raw_text}\n\n"
        f"【本章全部來源】\n{sources_text}\n\n"
        f"【規則】knowledge_nodes 是「分組→節點清單」的物件，值必須是純字串陣列"
        f"（既有條目或本章新建條目的完整名稱），不可用巢狀物件或額外欄位，例如：\n"
        f"  神學: [會幕, 神的同在]\n  原文: [皂莢木（atzei shittim）]\n"
        f"只列值得跨章累積的核心節點，不重列所有經文 link。{created_hint}\n"
        f"※ 條目名本身含逗號時「必須加引號」，例如 - \"信徒作祭司（彼前2：5,9）\"；"
        f"不加引號會被 YAML 拆成兩個碎片節點，兩個都對不上條目而被靜靜丟掉，"
        f"整個節點連同它的章節累積資料就消失了（程式會擋）。\n"
        f"※ 互文分組的節點要帶小標題，讓人一眼知道那節在講什麼："
        f"寫 [[出20：16|出20：16 第九誡不可作假見證]]，不要只寫 [[出20：16]]。\n\n"
        f"organization（本章整理）是單一 markdown 字串，"
        f"「一律用 YAML 的 | 字面區塊」，不可是巢狀物件或 YAML 陣列。\n"
        f"※ 用單引號 scalar 會把單一換行折成空格，整張 mermaid／表格／callout "
        f"會被擠成一行而無法渲染（程式會擋）。用 | 就不必在每列之間插空行。\n\n"
        f"【硬規格——程式會驗證，不符會退回重做】\n"
        f"- 依本章段落結構分成至少 {min_sections} 個小節，每小節以「### 標題（vX-Y）」"
        f"開頭；最後可加一個跨章脈絡／預表整理的主題小節。\n"
        f"- 全文合計 ≥{min_chars} 字，其中散文敘述至少 {min_chars // 2} 字——"
        f"沿經文脈絡整合各來源觀點的連貫敘述是主幹，表格、清單、callout "
        f"都是它的補充，不可把大半內容包進表格或 callout。\n"
        f"- 這是 Obsidian 筆記庫：行文首次提到本章條目時用 wiki-link 連結，"
        f"用詞不同寫 [[完整條目名|行文用詞]]，之後再提不必重連；至少要有一個連結，"
        f"且目標只能取自本章可連條目："
        f"{'、'.join(allowed_links) or '（本章無可連條目）'}——不可連清單外的目標。\n"
        f"- 內容只能出自上面的經文與來源；整合重點而非搬運來源全文。\n"
        f"- 表格儲存格內不可放帶別名的 wiki-link：[[目標|別名]] 在表格裡要跳脫成 "
        f"\\|，渲染後變成 [[目標\\]] 斷鏈（程式會擋）。表格內請用不帶別名的 "
        f"[[目標]]，或把連結寫在儲存格文字之後：文字（見 [[目標]]）。\n"
        f"- 引述來源請「直接引原話」並標明是哪一家（CT／GT／KC／BH 或 GT 內的"
        f"《丁道爾》《舊約背景註釋》《中文聖經註釋》《精讀本》等），不要改寫成"
        f"「CT指出…」的轉述體，也不可把甲家的話掛到乙家名下——已知實例："
        f"《舊約背景註釋》的古代近東材料被誤植為 KC、CT 的靈意註解被誤植為 KC。"
        f"某一家在某處沒有說法，就不要替他生一個。\n"
        f"- 各家彼此矛盾時要並陳，不要壓平成單一說法——例如出27 的壇，CT 說"
        f"「表徵耶穌的十字架」，KC 卻明說「不那麼是說到十字架，而是說到主耶穌"
        f"自己」，這種分歧本身就是重點。\n"
        f"- 不要寫「參考資料」清單——程式會自動附上來源 URL。\n\n"
        f"【設計空間——你是本章筆記的設計者】\n"
        f"硬規格之內體裁自由。動筆前先讀完材料，判斷每段資訊的形狀，"
        f"不要預設所有資訊都該寫成散文——不同形狀的知識用不同形式：\n"
        f"若rawdata含流程／階層／對照，至少嘗試一種對應視覺形式呈現，散文只是其中一種。\n"
        f"- 理解與整合（沿經文脈絡串起各來源解讀）→ 散文，這是主幹。\n"
        f"- 比較與對照（多項並列、新舊呼應、尺寸規格、來源間差異、重複模式）"
        f"→ markdown 表格或短編號清單。\n"
        f"- 流程與因果（獻祭步驟、制度建立、事件因果鏈）→ mermaid flowchart。\n"
        f"- 時間與發展（事件推進、跨章年代脈絡）→ mermaid timeline。\n"
        f"- 分類與階層（神學概念展開、支派分組、家譜樹）→ mermaid mindmap "
        f"或 flowchart 樹狀。\n"
        f"- 關係與空間（人物關係網、行程路線、空間配置）→ mermaid "
        f"graph／flowchart。\n"
        f"- 對答與往返（人與神的對話交涉、代求）→ mermaid sequenceDiagram。\n"
        f"- 補充與旁註 → callout：[!quote] 收來源關鍵引句、[!note]／[!info] 標"
        f"「這是來源解讀、非經文明言」的分辨、[!important] 突顯本章樞紐、"
        f"[!question] 留懸而未決的問題；補充性長內容可用可摺疊的"
        f"「> [!example]- 標題」預設收合。\n"
        f"- 關鍵詞句可用 ==高亮==。\n"
        f"mermaid 技術規格：圖型限 {'、'.join(_MERMAID_TYPES)}；節點標籤一律"
        f'用雙引號包住（如 A["燔祭壇"]）以免特殊字元破圖；圖內放不了 wiki-link，'
        f"關鍵詞仍要在行文中連結；圖旁配散文說明，不可只丟一張圖。\n"
        f"唯一原則：形式服務材料——用某個手法是因為材料是那個形狀，"
        f"不是為了裝飾；本章若沒有合適形狀的材料，整段散文完全正當。\n"
        f"【禁用】![[]] 嵌入、mermaid 以外的程式碼區塊、#標籤、HTML——"
        f"會重複條目內文、破壞頁面或污染 vault。\n\n"
        f"【輸出格式，極重要】只輸出 YAML，且 book/chapter/knowledge_nodes/organization "
        f"必須是最上層欄位——不可在外面再包一層 chapter_content 或任何其他 key。範例：\n"
        f"```yaml\nbook: {ctx.book}\nchapter: {ctx.chapter}\n"
        f"knowledge_nodes:\n  神學: [山上的樣式]\n  原文: [皂莢木（atzei shittim）]\n"
        f"organization: |\n  ### 標題一（v1-6）\n"
        f"  文字…神吩咐用 [[皂莢木（atzei shittim）|皂莢木]] 做櫃…\n\n"
        f"  ### 標題二（v7-13）\n  文字…\n```\n"
        f"{_schema_hint('chapter_content.schema.json')}"
    )

    def _normalize(payload):
        payload["book"] = ctx.book
        payload["chapter"] = ctx.chapter
        return payload

    payload = _model_step(
        ctx, out_path, prompt,
        validate=_chapter_payload_validator(len(raw_verses), allowed_links),
        label="chapter_content", normalize=_normalize, task="chapter",
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
        resolved, seen = [], set()
        for item in items:
            title = _resolve_related(item, mapping)
            if title is None:
                dropped.append(str(item))
                continue
            # 互文等分組要保留顯示用小標題（[[出20：16|出20：16 第九誡不可作假見證]]），
            # 否則渲染成裸引用，讀者無從得知該節在講什麼。去重仍以條目本身為準。
            alias = str(item).strip().partition("|")[2].strip()
            entry = f"{title}|{alias}" if alias else title
            if title not in seen:
                seen.add(title)
                resolved.append(entry)
        if resolved:
            closed[group] = resolved
    return dict(chapter_content, knowledge_nodes=closed), dropped


def render_step(ctx, entry_payloads, verse_links, chapter_content, plan=None):
    _log("▶ P3 render：產生 markdown 中…")
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
_LINK_RE = re.compile(r"\[\[([^\[\]\r\n]+)\]\]")


def _strip_links(text):
    """把 [[target|顯示詞]] 還原成顯示詞、[[target]] 還原成 target。"""
    return _LINK_RE.sub(lambda m: m.group(1).split("|")[-1], text)


def _scripture_tamper_errors(ctx, chapter_path):
    """經文竄改偵測：渲染後的經文去掉連結，必須與 raw_scripture 逐字相同。

    最嚴重的一類錯誤——出24 舊版為了讓 surface 對上條目名「山腳」，把經文
    「在山下築一座壇」改成「在山腳築一座壇」。連結可以改，經文一個字都不能動。
    """
    try:
        raw = ctx.raw_verses()
    except FileNotFoundError:
        return []
    errors = []
    for line in chapter_path.read_text(encoding="utf-8").splitlines():
        # 經文區只在檔首（# 標題之後、地圖區塊／## 區段之前）；再往下的編號
        # 是本章整理裡的清單，不可拿去比對。
        if line.startswith("## ") or line.startswith("<!--") or line.startswith("---"):
            break
        m = re.match(r"^(\d+)\.\s(.*)$", line)
        if not m:
            continue
        idx = int(m.group(1)) - 1
        if not (0 <= idx < len(raw)):
            continue
        got, want = _strip_links(m.group(2)).strip(), raw[idx].strip()
        if got != want:
            errors.append(
                f"{chapter_path.name}: 第{idx + 1}節經文與 raw_scripture 不符（經文不可改，"
                f"對不上請改 surface）\n      raw：{want}\n      渲染：{got}"
            )
    return errors


def _rendered_shape_errors(chapter_path):
    """渲染自檢：抓 YAML 折行與表格內別名連結這兩個反覆出現的坑。"""
    errors = []
    text = chapter_path.read_text(encoding="utf-8")
    for lineno, line in enumerate(text.splitlines(), 1):
        # organization 用單引號 scalar 時，單一換行會被折成空格，整張 mermaid／
        # 表格／callout 會擠成一行。organization 一律用 | 字面區塊即可避免。
        if len(re.findall(r"-->", line)) >= 3 or re.search(r"^\s*```mermaid.*```", line):
            errors.append(f"{chapter_path.name}:{lineno}: mermaid 被折成一行（organization 請用 YAML | 字面區塊）")
        elif re.search(r">\s*\[!.*?>\s*>", line):
            errors.append(f"{chapter_path.name}:{lineno}: callout 被折成一行（organization 請用 YAML | 字面區塊）")
        # 合法的分隔列，剝掉 callout 的 "> " 前綴後整列只有 | - : 空白；
        # 夾在一行裡還帶文字的，就是被折了
        elif re.search(r"\|\s*:?-{3,}:?\s*\|", line) and not re.fullmatch(
            r"[\s|:\-]+", re.sub(r"^\s*(>\s*)+", "", line).strip()
        ):
            errors.append(f"{chapter_path.name}:{lineno}: 表格被折成一行（organization 請用 YAML | 字面區塊）")
        # 表格儲存格裡寫 [[target|alias]] 要跳脫成 \|，渲染後變成 [[target\]] 斷鏈
        if re.search(r"\[\[[^\[\]\r\n]*\\\]\]", line):
            errors.append(f"{chapter_path.name}:{lineno}: 表格內有帶別名的 wiki-link（\\| 會造成斷鏈，請改用不帶別名的連結）")
    return errors


def _split_node_errors(ctx):
    """knowledge_nodes 被 YAML 逗號拆解偵測。

    條目名含逗號卻沒加引號時（如「信徒作祭司（彼前2：5,9）」），YAML 會把它
    拆成「信徒作祭司（彼前2：5」與「9）」兩個節點，兩個都對不上條目而被靜靜
    丟掉——整個節點連同它的章節累積資料就這樣消失。實測出28/29/30/39 共 8 例。
    """
    payload = ctx.path("chapter_content.yaml")
    if not payload.exists():
        return []
    try:
        data = yaml.safe_load(payload.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return []
    errors = []
    for group, items in (data.get("knowledge_nodes") or {}).items():
        if not isinstance(items, list):
            continue
        for item in items:
            s = str(item).strip()
            # 碎片特徵：有右括號沒左括號，或整項就是個裸片段
            if ("）" in s and "（" not in s) or (")" in s and "(" not in s):
                errors.append(
                    f"chapter_content.yaml: knowledge_nodes/{group} 的「{s}」看起來是被逗號拆開的碎片"
                    f"——條目名含逗號時必須加引號，例如 - \"信徒作祭司（彼前2：5,9）\""
                )
    return errors


_UNFILEABLE_RE = re.compile(r"[/\\]")


def _unknown_type_candidate_errors(ctx):
    """候選 type 不是 link_folder 底下的真實資料夾——條目永遠建不出來。

    合法 type 就是 link_folder/ 的資料夾名（主題、事件、互文、人物、原文、地點、
    文化、歷史、神學、背景、解經爭議）。寫成別的（利10 的「祭禮」、民9 的
    「儀式」、民10 的「器具」），resolver 認不得，只把它降級成 D_new_candidate
    並附一句 note「未知分類：X」——那是 plan 檔裡的一行字，不是錯誤，跑完照樣
    印「✅ 完成」。結果與斜線名同一個下場：條目沒建、surfaces 沒連上、
    knowledge_nodes 對不上被丟掉、本章累積從未寫入，全部靜默。

    利10 實際踩到：三個 type=祭禮 的候選全數蒸發，六道閘門一個都沒擋下來。
    全庫掃描另有民9／民10 共 3 筆（儀式×2、器具×1），無誤報——判準是純機械的
    集合比對，不涉推測，故列為 error 而非 manual_review。
    """
    payload = ctx.path("link_candidates.yaml")
    if not payload.exists():
        return []
    try:
        data = yaml.safe_load(payload.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return []
    link_root = Path(ctx.root) / "link_folder"
    if not link_root.is_dir():
        return []
    valid = sorted(p.name for p in link_root.iterdir() if p.is_dir())
    errors = []
    for cand in data.get("candidates") or []:
        if not isinstance(cand, dict):
            continue
        name = str(cand.get("name") or "").strip()
        ctype = str(cand.get("type") or "").strip()
        if not name or not ctype or ctype in valid:
            continue
        errors.append(
            f"link_candidates.yaml: 候選「{name}」的 type「{ctype}」不是 link_folder 底下的"
            f"資料夾，條目建不出來（會靜默降級成 D_new_candidate）。"
            f"合法值：{'、'.join(valid)}"
        )
    return errors


def _unfileable_candidate_errors(ctx):
    """候選名含斜線偵測——這種名字永遠不可能成為條目檔。

    模型愛用斜線塞「合併名」：利1 的「鳥（斑鳩/雛鴿）」、利11 的「沙番/石獾
    （shaphan）」、出29 的「搖祭/舉祭」。斜線在檔名裡是路徑分隔字元，
    entry_content/<name>.yaml 根本建不出來，於是這個候選必定同時：
    surfaces 連不上任何節、knowledge_nodes 對不上而被丟掉、該條目的本章累積
    永遠不寫入、別的條目 related_entries 指向它而被移除——全部靜默。

    實測全庫（創/出/利 117 章）14 筆全部 find_in_index=not_found，0 誤報；
    利1 的斑鳩/雛鴿與利11 的沙番都已證實真的沒連上。冒號不列入：「信徒作祭司
    （彼前2:5,9）」在檔名裡雖非法，但條目用全形「：」，normalize 後解析得到，
    列入就是誤報。
    """
    payload = ctx.path("link_candidates.yaml")
    if not payload.exists():
        return []
    try:
        data = yaml.safe_load(payload.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return []
    errors = []
    for cand in data.get("candidates") or []:
        if not isinstance(cand, dict):
            continue
        name = str(cand.get("name") or "").strip()
        if not name or not _UNFILEABLE_RE.search(name):
            continue
        parts = [p for p in re.split(r"[/\\]", re.sub(r"[（(].*?[）)]", "", name)) if p.strip()]
        hint = "、".join(parts[:3]) if len(parts) > 1 else name
        errors.append(
            f"link_candidates.yaml: 候選「{name}」含斜線，永遠不可能成為條目檔"
            f"（entry_content/<名稱>.yaml 建不出來），surfaces、knowledge_nodes、"
            f"本章累積會全部靜默失效。一個候選只能對一個條目——"
            f"請拆成多筆（如：{hint}），或改用該條目的真實名稱。"
        )
    return errors


def _table_alias_link_review(ctx):
    """表格列裡帶別名的 wiki-link——Obsidian 會把 | 當成欄位分隔，整列表格裂開。

    `| [[復活盼望|復活信心]] |` 在 Obsidian 裡會被切成兩欄，表格顯示就壞了。
    verify_links 抓不到（md 檔裡連結字面完好、目標也存在），三道閘門全過，
    壞的只有版面。實測創／出／利 117 章共 14 例，全在表格列上。

    修法是把表格格裡的連結改成不帶別名（`[[復活盼望]]`）。因為這是版面問題、
    且渲染器行為隨 Obsidian 版本可能不同，走 manual_review 不擋 build。
    """
    payload = ctx.path("chapter_content.yaml")
    if not payload.exists():
        return []
    try:
        data = yaml.safe_load(payload.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return []
    hits = []
    for lineno, line in enumerate(str(data.get("organization") or "").splitlines(), 1):
        # callout 裡的表格列長成 "> | ... |"，要先剝掉 "> " 前綴才認得出來——
        # 漏掉這一步的話，寫在 callout 裡的表格就檢查不到（利7 實際踩過）。
        s = re.sub(r"^\s*(>\s*)+", "", line).strip()
        if s.startswith("|") and s.endswith("|") and re.search(r"\[\[[^\]\r\n]*\|", s):
            hits.append(f"organization 第 {lineno} 行：{s[:40]}")
    if not hits:
        return []
    return [
        "chapter_content：表格列裡有帶別名的 wiki-link（Obsidian 會把 | 當欄位分隔，"
        "表格會裂開）。請把表格格裡的連結改成不帶別名，例如 [[復活盼望]]。\n      "
        + "\n      ".join(hits[:6])
    ]


_SECTION_VERSE_RE = re.compile(r"[（(]\s*v\s*(\d+)\s*(?:[-–~至]\s*(\d+))?\s*[）)]")


def _verse_coverage_review(ctx):
    """本章整理疑似漏掉整段經文——回報給人工看，不擋流程。

    利1 的整理只寫到 v13，v14-17「若以鳥為燔祭」整段沒寫；利9 更嚴重，
    v22-24「火從耶和華面前出來燒盡燔祭、眾民歡呼俯伏」這個全章高潮不見了。
    三個閘門都過，因為沒有任何一關在看涵蓋率。

    只在 organization 本來就用「### 標題（v3-9）」標號時才算，且只報連續 3 節
    以上的缺漏。這仍是啟發式：出26 第一節標題沒帶節號卻確實寫了 v1-14，就會
    誤報——所以走 manual_review 而不是 error，讓人瞄一眼就好，別擋 build。
    """
    payload = ctx.path("chapter_content.yaml")
    if not payload.exists():
        return []
    try:
        data = yaml.safe_load(payload.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return []
    org = str(data.get("organization") or "")
    headers = re.findall(r"^#{2,4}\s+.*$", org, re.M)
    if not headers:
        return []
    # 有標題卻沒帶節號 → 無從判斷涵蓋，直接放過（出26 即此類）
    if any(not _SECTION_VERSE_RE.search(h) for h in headers):
        return []
    spans = _SECTION_VERSE_RE.findall(org)
    if not spans:
        return []
    try:
        total = len(ctx.raw_verses())
    except FileNotFoundError:
        return []
    if total <= 0:
        return []
    covered = set()
    for start, end in spans:
        s, e = int(start), int(end) if end else int(start)
        if s > e:
            s, e = e, s
        covered |= set(range(s, min(e, total) + 1))
    missing = sorted(set(range(1, total + 1)) - covered)
    if not missing:
        return []
    runs, run = [], [missing[0]]
    for v in missing[1:]:
        if v == run[-1] + 1:
            run.append(v)
        else:
            runs.append(run)
            run = [v]
    runs.append(run)
    big = [r for r in runs if len(r) >= 3]
    if not big:
        return []
    spans_txt = "、".join(f"v{r[0]}-{r[-1]}" for r in big)
    return [
        f"chapter_content：本章整理可能漏掉整段經文（{spans_txt}；本章共 {total} 節）。"
        f"請確認這幾節是否真的沒寫——每段經文都該有對應的整理，不要只寫前面幾段就收尾。"
        f"（若已併入鄰段敘述、只是標題沒帶節號，忽略即可）"
    ]


def validate_step(ctx, written):
    _log("▶ P4 validate：結構驗證中…")
    errors = []
    old_root = vkb.ROOT
    vkb.ROOT = ctx.root
    try:
        for path in written:
            # Chapter files match "第N章.md" pattern, not just starting with "第"
            if re.fullmatch(r"第\d+章\.md", path.name):
                errors.extend(vkb.validate_chapter(path))
                errors.extend(_scripture_tamper_errors(ctx, path))
                errors.extend(_rendered_shape_errors(path))
            else:
                file_errors, _ = vkb.validate_file(path, strict=True)
                errors.extend(file_errors)
    finally:
        vkb.ROOT = old_root
    errors.extend(_split_node_errors(ctx))
    errors.extend(_unfileable_candidate_errors(ctx))
    errors.extend(_unknown_type_candidate_errors(ctx))
    ctx.manual_review.extend(_verse_coverage_review(ctx))
    ctx.manual_review.extend(_table_alias_link_review(ctx))
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
