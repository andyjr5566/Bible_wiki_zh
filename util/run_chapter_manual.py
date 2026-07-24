#!/usr/bin/env python3
"""人工模式 wrapper：agent（Claude Code）當模型，整條 run_chapter 流程不打任何 API。

用法（每章三步，依序）：

  python util/run_chapter_manual.py prompts 民數記 5
      P2 resolve ＋ 把 M3/M6 的「實際 prompt」（白名單、字數門檻、來源 URL 對照
      都已代入本章值）落地到 .tmp/第5章/manual/*.prompt.md，並列出來源原檔路徑
      （agent 應讀原檔全文，不要只讀 prompt 內的截斷 excerpt）。不呼叫模型。

  （agent 依 prompt 規格手寫 .tmp/第5章/entry_content/<name>.yaml；條目寫齊後
    重跑 prompts 重生 chapter_content.prompt.md——白名單含實建條目名——再手寫
    chapter_content.yaml，organization 用 YAML | 字面區塊。）

  python util/run_chapter_manual.py check 民數記 5
      對手寫 payload 補跑 fresh 路徑同一套驗證（resume 路徑會繞過 call_model 的
      validate 迴圈，這裡把那道閘門找回來）。

  python util/run_chapter_manual.py run 民數記 5
      原版 orchestrator 跑完 M5/P3/P4 與全部護欄；模型步驟一旦被觸發＝缺 payload，
      guard runner 直接報錯，保證零 API 呼叫。

設計原則：不複製 run_chapter.py 的邏輯——一律 import 原版的步驟與驗證函式，
原版護欄演化時這裡自動跟上。wrapper 只補人工路徑的三個已知缺口：
  1. resume 路徑繞過 call_model 的 validate 迴圈（見 run_chapter.chapter_content_step
     內的注記）→ check 指令對手寫 payload 補跑同一套 validator；
  2. require_sources 空來源護欄只在「要呼叫模型前」觸發，resume 路徑不會跑到
     → prompts／check 都前置明跑（利/民/申全毀的根因，見 memory）；
  3. _invalidate_stale／_invalidate_after_entry 會連鎖刪除手寫 payload
     → 各指令跑前先讀-only 模擬，會刪到手寫產物時擋下並說明修法，不靜默毀工。
"""
import argparse
import json
import sys

import yaml

import run_chapter as rc
from model_client import ModelError, ModelValidationError
from source_excerpts import SourceError

# _batch_entry_prompt 只有重試輪才有的回饋區塊標頭；PromptCapture 據此只收第一輪乾淨版
FEEDBACK_MARKER = "【上一輪這些條目未通過驗證"
CAPTURE_MSG = "（人工模式）prompt 已輸出，等待 agent 手寫 payload"
PROMPT_DIR = "manual"
# 手寫產物節點：被作廢＝毀掉 agent 已寫的內容，刪除前必須明示確認
HAND_NODES = ("entry_content", "chapter_content.yaml")


def _utf8_console():
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")


# --------------------------------------------------------------------------- #
# 讀-only 模擬作廢：與 _invalidate_stale／_invalidate_after_entry 同判準、不動手
# --------------------------------------------------------------------------- #
def simulate_invalidation(ctx):
    """回傳 (stale_removed, after_entry_removed)：實跑時將被刪除的既存節點。

    stale_removed 對應 _invalidate_stale（上游指紋變 → 連鎖作廢下游）；
    after_entry_removed 對應 _invalidate_after_entry（entry_content 與基線不同
    → verse_links／chapter_content 作廢）。人工路徑 entry_content_step 是
    no-op（payload 都已存在），故「現在的指紋」就是屆時比對用的指紋。
    """
    prev = rc._load_pipeline_state(ctx)
    dirty, stale_removed = set(), []
    for out_key, inputs in rc._PIPELINE_STAGES:
        stale = False
        for inp in inputs:
            if inp in dirty:
                stale = True
                break
            if inp in prev and rc._node_fingerprint(rc._node_path(ctx, inp)) != prev[inp]:
                stale = True
                break
        if stale:
            dirty.add(out_key)
            if rc._node_path(ctx, out_key).exists():
                stale_removed.append(out_key)
    after_entry_removed = []
    if "entry_content" in prev and "entry_content" not in dirty:
        if rc._node_fingerprint(rc._node_path(ctx, "entry_content")) != prev["entry_content"]:
            for key in ("verse_links.yaml", "chapter_content.yaml"):
                if key not in dirty and rc._node_path(ctx, key).exists():
                    after_entry_removed.append(key)
    return stale_removed, after_entry_removed


def _pending_entries(ctx, plan):
    """尚無對應 payload 的 C 類候選名（比對規則同 entry_content_step 的 done()）。"""
    existing = []
    out_dir = ctx.path("entry_content")
    if out_dir.exists():
        for path in sorted(out_dir.glob("*.yaml")):
            try:
                data = rc._read_yaml(path)
            except yaml.YAMLError:
                continue
            if isinstance(data, dict) and data.get("name"):
                existing.append(str(data["name"]))
    pending, seen = [], set()
    for entry in plan.get("C_new_formal", []) or []:
        if not isinstance(entry, dict) or not entry.get("name"):
            continue
        if entry["name"] in seen:
            continue
        seen.add(entry["name"])
        if rc._created_title(entry, existing) is None:
            pending.append(entry["name"])
    return pending


def _require_sources(ctx):
    """空來源護欄前置（resume 路徑不會自己跑到它）；manifest 無任何 OK 來源也算失敗。"""
    present = rc.source_excerpts.require_sources(ctx.path("source_manifest.md"), ctx.root)
    if not present:
        raise SourceError(
            f"source_manifest.md 沒有任何可用的 OK 來源——空來源下生成＝杜撰內容。"
            f"請先用 util/build_source_manifest.py 產生 manifest。"
            f"\n  manifest：{ctx.path('source_manifest.md')}"
        )
    return present


# --------------------------------------------------------------------------- #
# prompts
# --------------------------------------------------------------------------- #
class PromptCapture:
    """假 runner：prompt 落地成檔後以 ModelValidationError 中止該次呼叫。

    M3 由 _run_entry_batch 的 except ModelValidationError 接住（整批記為失敗、
    續跑下一批）、M6 由 _model_step 接住（記 manual_review、回 None），流程不會炸；
    dump 造成的假性 manual_review 由 cmd_prompts 過濾。重試輪的回饋版 prompt
    （帶 FEEDBACK_MARKER）不落地，每批只留第一輪乾淨版。
    """

    def __init__(self, out_dir, stem):
        self.out_dir = out_dir
        self.stem = stem
        self.written = []

    def __call__(self, prompt):
        if FEEDBACK_MARKER not in prompt:
            self.out_dir.mkdir(parents=True, exist_ok=True)
            if self.stem == "chapter_content":
                path = self.out_dir / "chapter_content.prompt.md"
            else:
                path = self.out_dir / f"{self.stem}_{len(self.written) + 1}.prompt.md"
            path.write_text(prompt, encoding="utf-8")
            if path not in self.written:
                self.written.append(path)
        raise ModelValidationError(CAPTURE_MSG)


def cmd_prompts(args):
    ctx = rc.ChapterContext(args.book, args.chapter)
    stale_removed, _ = simulate_invalidation(ctx)
    hand_hit = [k for k in stale_removed if k in HAND_NODES]
    if hand_hit and not args.confirm_stale:
        print("⚠️ 上游（link_candidates 等）已改動，重跑會作廢並刪除下列產物：")
        for key in stale_removed:
            print(f"   - {key}" + ("（手寫，刪了要重寫）" if key in HAND_NODES else ""))
        print("確認要作廢請加 --confirm-stale；不想作廢就先還原上游改動。")
        return 1
    _require_sources(ctx)
    rc._invalidate_stale(ctx)
    plan = rc.resolve_step(ctx)  # runner 尚未注入 → 語義附註照常嘗試（端點不通自動略過）

    manual_dir = ctx.path(PROMPT_DIR)
    if manual_dir.exists():
        for old in manual_dir.glob("*.prompt.md"):
            old.unlink()
    manual_dir.mkdir(parents=True, exist_ok=True)
    # 來源原檔路徑：prompt 內的 sources_text 對大章節會等比截斷，agent 要讀原檔全文
    (manual_dir / "sources.md").write_text(
        "agent 應讀下列來源「原檔全文」（prompt 內嵌的版本對大章節會截斷）：\n\n"
        + "\n".join(f"- {label}：{path}" for label, path in ctx.sources())
        + "\n",
        encoding="utf-8",
    )

    cap_entry = PromptCapture(manual_dir, "entry_batch")
    ctx.runner = cap_entry
    rc.entry_content_step(ctx, plan)
    cap_chapter = PromptCapture(manual_dir, "chapter_content")
    ctx.runner = cap_chapter
    rc.chapter_content_step(ctx, plan)

    # dump 過程的假性 manual_review（批次「失敗」與 M6 的 CAPTURE_MSG）不是真問題
    leftovers = [
        item for item in ctx.manual_review
        if CAPTURE_MSG not in item and "批量重做後仍不合格" not in item
    ]
    pending = _pending_entries(ctx, plan)
    chapter_done = ctx.path("chapter_content.yaml").exists()

    print(f"✅ prompts 完成：{ctx.book} 第{ctx.chapter}章")
    print(f"   來源清單：{manual_dir / 'sources.md'}")
    for path in cap_entry.written + cap_chapter.written:
        print(f"   prompt：{path}")
    if pending:
        print(f"   待寫條目 payload（{len(pending)} 個）→ {ctx.path('entry_content')}\\<name>.yaml：")
        for name in pending:
            print(f"     - {name}")
    else:
        print("   條目 payload 已齊（無待寫 C 類候選）")
    if chapter_done:
        print("   chapter_content.yaml 已存在（要重寫請先手動刪除再重跑 prompts）")
    elif pending:
        print("   ⚠️ chapter_content.prompt.md 的可連白名單「不含尚未寫的條目」——"
              "條目寫齊後重跑 prompts 重生它，再寫本章整理")
    else:
        print(f"   待寫 chapter_content.yaml → {ctx.path('chapter_content.yaml')}"
              "（organization 用 YAML | 字面區塊；knowledge_nodes 不要預包 [[ ]]）")
    for item in leftovers:
        print(f"   ⚠️ {item}")
    print(f"   下一步：寫完 payload 後 python util/run_chapter_manual.py check {args.book} {args.chapter}")
    return 0


# --------------------------------------------------------------------------- #
# check：fresh 路徑同一套驗證，補 resume 路徑繞過的閘門
# --------------------------------------------------------------------------- #
def _check_entries(ctx, plan, problems, warnings):
    known = ctx.known_types()
    source_urls = rc.source_excerpts.manifest_kind_urls(ctx.path("source_manifest.md"))
    allowed_urls = [url for _, url in source_urls]
    url_kinds = {url: kind for kind, url in source_urls}

    payload_list = []
    out_dir = ctx.path("entry_content")
    if out_dir.exists():
        for path in sorted(out_dir.glob("*.yaml")):
            try:
                data = rc._read_yaml(path)
            except yaml.YAMLError as exc:
                problems.append(f"{path.name}: YAML 解析失敗（{exc}）")
                continue
            if not isinstance(data, dict) or not data.get("name"):
                problems.append(f"{path.name}: 必須是含 name 的物件 payload")
                continue
            name = str(data["name"])
            if rc.render_entry.safe_name(name) != name:
                problems.append(
                    f"{path.name}: name「{name}」含需正規化的字元（如半形冒號），"
                    f"請直接寫正規形（fresh 路徑會 safe_name 後才落檔）"
                )
            if path.stem != name:
                warnings.append(f"{path.name}: 檔名與 name「{name}」不一致（慣例：檔名＝name）")
            payload_list.append(data)

    seen = set()
    c_entries = []
    for entry in plan.get("C_new_formal", []) or []:
        if isinstance(entry, dict) and entry.get("name") and entry["name"] not in seen:
            seen.add(entry["name"])
            c_entries.append(entry)
    index = rc.resolver.load_index()
    planned_names = {rc.render_entry.safe_name(e["name"]) for e in c_entries}
    owners = rc._alias_owners(index, planned_names, {})
    matched_ids, pending = set(), []
    for entry in c_entries:
        payload = rc._match_payload(entry, payload_list)
        if payload is None:
            pending.append(entry["name"])
            continue
        matched_ids.add(id(payload))
        errs = rc.render_entry.validate_payload(payload, known_types=known)
        errs.extend(rc._entry_source_errors(payload, allowed_urls, url_kinds))
        # fresh 路徑對撞名 alias 是自動剔除＋通知；人工路徑報出來讓 agent 自己改
        errs.extend(rc._entry_alias_errors(entry, payload, owners))
        if errs:
            for err in errs:
                problems.append(f"entry_content/{payload['name']}: {err}")
        else:
            rc._register_alias_owner(owners, payload)
    for payload in payload_list:
        if id(payload) not in matched_ids:
            problems.append(
                f"entry_content/{payload['name']}: 對不上任何 C 類候選"
                f"（payload name 必須能對回 link_plan 的候選名，否則整鏈靜默失效）"
            )
    if pending:
        warnings.append("尚缺 payload 的 C 類候選：" + "、".join(pending))


def _check_chapter(ctx, problems, warnings):
    cc_path = ctx.path("chapter_content.yaml")
    if not cc_path.exists():
        warnings.append("chapter_content.yaml 尚未撰寫")
        return
    try:
        payload = rc._read_yaml(cc_path)
    except yaml.YAMLError as exc:
        problems.append(f"chapter_content.yaml: YAML 解析失敗（{exc}）")
        return
    if not isinstance(payload, dict):
        problems.append("chapter_content.yaml: 頂層必須是物件")
        return
    if payload.get("book") != ctx.book or payload.get("chapter") != ctx.chapter:
        problems.append(
            f"chapter_content.yaml: book/chapter 必須是 {ctx.book}/{ctx.chapter}"
            f"（目前 {payload.get('book')}/{payload.get('chapter')}）"
        )
    allowed_links = rc._reconstruct_allowed_links(ctx)
    alias_map = rc._allowed_alias_map(ctx, allowed_links)
    validator = rc._chapter_payload_validator(len(ctx.raw_verses()), allowed_links, alias_map)
    before = payload.get("organization")
    for err in validator(payload):
        problems.append(f"chapter_content.yaml: {err}")
    if payload.get("organization") != before:
        # validator 內的 _rewrite_alias_links 把 [[alias]] 機械改寫成 [[全名|alias]]
        # ——fresh 路徑會把改寫後版本落檔，這裡比照回寫
        rc._write_yaml(cc_path, payload)
        warnings.append("organization 的 [[alias]] 已機械改寫為 [[全名|alias]] 並回寫檔案")
    for err in rc._split_node_errors(ctx) + rc._merged_node_errors(ctx):
        problems.append(err)


def cmd_check(args):
    ctx = rc.ChapterContext(args.book, args.chapter)
    problems, warnings = [], []
    stale_removed, after_removed = simulate_invalidation(ctx)
    if stale_removed or after_removed:
        warnings.append(
            "上游已改動，下列產物屬過期、實跑（prompts/run）會被作廢："
            + "、".join(stale_removed + after_removed)
        )
    try:
        _require_sources(ctx)
    except SourceError as exc:
        problems.append(str(exc))
    plan_path = ctx.path("link_plan.yaml")
    if not plan_path.exists():
        print("❌ 尚無 link_plan.yaml——先跑 prompts")
        return 1
    plan = rc._read_yaml(plan_path) or {}
    _check_entries(ctx, plan, problems, warnings)
    _check_chapter(ctx, problems, warnings)
    # 高風險早篩：查無出處的希伯來字母（P4 也會擋）與音譯複核（P4 也會提醒）
    problems.extend(rc._unsourced_hebrew_errors(ctx))
    warnings.extend(rc._transliteration_review(ctx))

    for item in warnings:
        print(f"⚠️ {item}")
    if problems:
        print(f"❌ check 未過（{len(problems)} 項）：")
        for item in problems:
            print(f"   - {item}")
        return 1
    print(f"✅ check 通過：{ctx.book} 第{ctx.chapter}章 手寫 payload 合格")
    print(f"   下一步：python util/run_chapter_manual.py run {args.book} {args.chapter}")
    return 0


# --------------------------------------------------------------------------- #
# run：原版 orchestrator ＋ guard runner（零 API 保證）
# --------------------------------------------------------------------------- #
def cmd_run(args):
    ctx = rc.ChapterContext(args.book, args.chapter)
    stale_removed, after_removed = simulate_invalidation(ctx)
    if "link_plan.yaml" in stale_removed or any(k in HAND_NODES for k in stale_removed):
        print("❌ 上游已改動，實跑會作廢：" + "、".join(stale_removed))
        print("   請改跑 prompts（它會執行作廢並重出提示），補齊 payload 後再 run。")
        return 1
    if "chapter_content.yaml" in after_removed and not args.keep_chapter:
        print("❌ entry_content 與基線不同：實跑會作廢 verse_links 與「手寫的 chapter_content.yaml」。")
        print("   若本章整理已反映最新條目（先跑 check 確認白名單仍過），加 --keep-chapter：")
        print("   保留 chapter_content、只重生 verse_links。否則請重跑 prompts 重寫本章整理。")
        return 1
    if after_removed and args.keep_chapter:
        # 條目定稿在後、本章整理寫於其後——更新基線宣告 chapter_content 已是新的；
        # verse_links 仍要重生（條目 aliases 可能已變，surface 詞彙表跟著變）
        state = rc._load_pipeline_state(ctx)
        state["entry_content"] = rc._node_fingerprint(rc._node_path(ctx, "entry_content"))
        ctx.path(rc._PIPELINE_STATE_FILE).write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        verse_links = ctx.path("verse_links.yaml")
        if verse_links.exists():
            verse_links.unlink()
        print("⟳ 已更新 entry_content 基線並作廢 verse_links.yaml（將重生）；chapter_content.yaml 保留")

    plan_path = ctx.path("link_plan.yaml")
    if not plan_path.exists():
        print("❌ 尚無 link_plan.yaml——先跑 prompts")
        return 1
    plan = rc._read_yaml(plan_path) or {}
    pending = _pending_entries(ctx, plan)
    missing = [f"entry_content/{name}.yaml" for name in pending]
    if not ctx.path("chapter_content.yaml").exists():
        missing.append("chapter_content.yaml")
    if missing:
        print("❌ payload 未齊，缺：")
        for item in missing:
            print(f"   - {item}")
        print("   跑 prompts 取得對應 prompt 檔，手寫後先 check 再 run。")
        return 1

    def guard(prompt):
        raise ModelError(
            "人工模式不呼叫 API——模型步驟被觸發表示 payload 缺漏或中途被作廢，"
            "請重跑 prompts → 手寫 → check 後再 run"
        )

    result = rc.run_chapter(args.book, args.chapter, runner=guard)
    print(f"✅ 完成：寫入 {len(result['written'])} 檔，新增條目 {result['entry_count']}")
    if result["manual_review"]:
        print("⚠️ 需人工處理：")
        for item in result["manual_review"]:
            print(f"   - {item}")
        rc.remediation.print_fix_hints(
            rc._manual_review_hints(result["manual_review"], args.book, args.chapter)
        )
    if result["errors"]:
        print("❌ 結構驗證未過：")
        for item in result["errors"]:
            print(f"   - {item}")
        return 1
    return 0


def main():
    _utf8_console()
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)
    p_prompts = sub.add_parser("prompts", help="產出 M3/M6 實際 prompt 檔（不呼叫模型）")
    p_prompts.add_argument("--confirm-stale", action="store_true",
                           help="上游改動會刪手寫 payload 時，確認照刪")
    p_check = sub.add_parser("check", help="以 fresh 路徑同套驗證檢查手寫 payload")
    p_run = sub.add_parser("run", help="跑原版 orchestrator（M5/P3/P4）；缺 payload 即報錯")
    p_run.add_argument("--keep-chapter", action="store_true",
                       help="entry_content 變動後保留手寫 chapter_content，只重生 verse_links")
    for p in (p_prompts, p_check, p_run):
        p.add_argument("book")
        p.add_argument("chapter", type=int)
    args = parser.parse_args()
    handler = {"prompts": cmd_prompts, "check": cmd_check, "run": cmd_run}[args.command]
    try:
        return handler(args)
    except (OSError, ValueError, yaml.YAMLError, SourceError, ModelError) as exc:
        print(f"❌ {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
