#!/usr/bin/env python3
"""
check_chapter_files.py — 章節管線檔案完整性檢查

依 agent_start_prompt.md 的步驟順序，逐一檢查每步驟該產生的主要檔案是否存在。
從第一個缺檔處停止並回報「該回到哪個動作續做」——後面步驟的產物都依賴
前面步驟，缺檔時再往下查只會洗出一串連鎖缺檔訊息，沒有意義。全數存在才 PASS。

Usage:
  python util/check_chapter_files.py 【書名】 X
"""
import argparse
import re
import subprocess
import json
import sys
from pathlib import Path

try:
    from .book_paths import book_directory, canonical_book_name
    from .console import utf8_stdio
    from .semantic_lookup import (
        _file_sha256,
        candidate_identity_sha256,
        extract_report_metadata,
        RERANK_POLICY_VERSION,
        CALIBRATION_FILE_REL,
    )
    from .build_embedding_index import compute_index_fingerprint, stale_summary
    from .model_client import select_endpoint
    from . import source_excerpts
    from . import check_source_read
    from . import check_quote_fidelity
    from . import link_updates
    from . import build_appendix_links
    from .render_chapter import APPENDIX_BLOCK_START
except ImportError:
    from book_paths import book_directory, canonical_book_name
    from console import utf8_stdio
    from semantic_lookup import (
        _file_sha256,
        candidate_identity_sha256,
        extract_report_metadata,
        RERANK_POLICY_VERSION,
        CALIBRATION_FILE_REL,
    )
    from build_embedding_index import compute_index_fingerprint, stale_summary
    from model_client import select_endpoint
    import source_excerpts
    import check_source_read
    import check_quote_fidelity
    import link_updates
    import build_appendix_links
    from render_chapter import APPENDIX_BLOCK_START

from collections import Counter
import yaml

ROOT = Path(__file__).resolve().parent.parent

_ACCUM_RE = re.compile(r"<!-- accumulation:([^:]+):(\d+):start -->")
VALID_RERANK_STATUS = {"success", "partial", "degraded", "disabled", "not_needed"}


class CheckResult:
    """檢查結果封裝；支援 tuple (label, ok, resume_hint) 解構並附帶 warning 屬性。"""

    def __init__(self, label, ok, resume_hint="", warning=""):
        self.label = label
        self.ok = ok
        self.resume_hint = resume_hint
        self.warning = warning

    def __iter__(self):
        return iter((self.label, self.ok, self.resume_hint))

    def __repr__(self):
        return f"CheckResult(label={self.label!r}, ok={self.ok!r}, warning={self.warning!r})"


# git 無限期阻塞時的上限。本模組被 MCP server 以函式庫方式呼叫
# （`build_checks`），而該 server 跑在不允許建立子行程的 host 上：沒有
# timeout 的 `subprocess.run` 不是失敗而是永遠不回來（實測 get_chapter_status
# 卡滿 1800 秒被 client 中止，同一支 CLI 在 shell 只要 2 秒）。逾時與
# 「不是 repo」同樣視為 git 不可用，照既有契約回 None、不誤擋。
_GIT_TIMEOUT_SECONDS = 20
_git_disabled_reason = None


def disable_git(reason):
    """關掉本模組的 git 呼叫；長駐 host 已知不能 spawn 時先行宣告。

    沒有這個開關，這種 host 每次呼叫都要再付一次 `_GIT_TIMEOUT_SECONDS`。
    """
    global _git_disabled_reason
    _git_disabled_reason = reason


def git_disabled_reason():
    """git 目前被判為不可用的原因；可用時回 None。"""
    return _git_disabled_reason


def _git_lines_z(root, *args):
    """跑 git 並以 NUL 分隔解析輸出（避開 core.quotepath 對中文路徑的轉義）。

    呼叫端須自行把 -z 放在 pathspec（--）之前——放在 args 尾端會被 git
    當成檔名（實測踩過：三個注入測試檔全數漏抓）。
    """
    if _git_disabled_reason is not None:
        return None
    try:
        proc = subprocess.run(
            ["git", *args], cwd=root, capture_output=True, check=True,
            timeout=_GIT_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        # 這台機器上 git 起不來。latch 起來，後續呼叫不必再各付一次逾時。
        disable_git(f"git 逾時（{_GIT_TIMEOUT_SECONDS} 秒），本行程不再呼叫 git")
        return None
    except (OSError, subprocess.CalledProcessError):
        return None
    return [p for p in proc.stdout.decode("utf-8", "replace").split("\0") if p]


def untracked_entry_findings(root, book, chapter):
    """git 未追蹤的 link_folder 條目檔——「commit 漏了 git add」的攔截網。

    利3／4 實例：run_chapter 實建的新條目 .md 沒進當時的 commit（訊息還寫
    「新建條目：0個」），以未追蹤狀態晾了兩天才被發現。判準機械可證，
    以條目檔內的 accumulation 標記歸屬章節：
    - 標記指向的章節已 commit（該章 第N章.md 已被 git 追蹤）→ 該章 commit
      漏了它 = error（回傳 errors）
    - 標記只含本章 → 本章工作產物，commit 時必須一併 git add（回傳 pending）
    - 標記只含其他未 commit 章節 → 可能是他 agent 進行中的工作，僅提示（notes）
    - 無任何標記 → 無法歸屬 = error（正常管線產的條目一定有建立章的標記）
    回傳 (errors, pending, notes)；git 不可用（非 repo 等）時全部回空，不誤擋。
    """
    canonical = canonical_book_name(book)
    untracked = _git_lines_z(root, "status", "--porcelain", "--untracked-files=all",
                             "-z", "--", "link_folder")
    if untracked is None:
        return [], [], []
    paths = [line[3:] for line in untracked
             if line.startswith("?? ") and line.endswith(".md")]
    if not paths:
        return [], [], []
    tracked = set(_git_lines_z(root, "ls-files", "-z") or [])
    errors, pending, notes = [], [], []
    for rel in sorted(paths):
        try:
            text = (root / rel).read_text(encoding="utf-8")
        except OSError:
            errors.append(f"{rel}：讀不到檔案內容，請人工確認")
            continue
        refs = {(b, int(c)) for b, c in _ACCUM_RE.findall(text)}
        if not refs:
            errors.append(f"{rel}：無累積標記、無法歸屬章節，請人工確認來源後補 git add 或移除")
            continue
        committed_elsewhere = []
        for b, c in sorted(refs):
            if (b, c) == (canonical, chapter):
                continue
            try:
                ch_md = book_directory(root, b) / f"第{c}章.md"
            except (OSError, ValueError):
                continue
            rel_md = ch_md.relative_to(root).as_posix()
            if rel_md in tracked:
                committed_elsewhere.append(f"{b}第{c}章")
        if committed_elsewhere:
            errors.append(
                f"{rel}：屬已 commit 的 {'、'.join(committed_elsewhere)}，"
                f"當時的 commit 漏了 git add 此檔——驗證內容後補提交"
            )
        elif (canonical, chapter) in refs:
            pending.append(rel)
        else:
            notes.append(f"{rel}：屬其他進行中章節（{'、'.join(f'{b}第{c}章' for b, c in sorted(refs))}），不擋本章")
    return errors, pending, notes


def _load_yaml(path):
    if not path.exists():
        return None
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return None


def _plan_count(plan, key):
    if not isinstance(plan, dict):
        return 0
    return len(plan.get(key) or [])


def _plan_unique_name_count(plan, key):
    """C_new_formal 計畫可能同名重複（run_chapter.py 建 entry 前會去重）。"""
    if not isinstance(plan, dict):
        return 0
    return len({e["name"] for e in plan.get(key) or [] if isinstance(e, dict) and e.get("name")})


def _embedding_index_synced(root):
    """embedding 索引是否與條目庫同步（純雜湊比對，不打網路）。"""
    summary = stale_summary(root)
    if summary is None:
        return False, "索引不存在（首次請跑 python util/build_embedding_index.py 全量建立）"
    if summary.get("legacy_schema"):
        return False, "索引為 legacy schema，請跑 python util/build_embedding_index.py --rebuild"
    try:
        cur_embed_model = select_endpoint(task="embedding", root=root).get("model")
    except Exception as exc:
        return False, f"目前 embedding 端點設定無法解析：{exc}"
    if not cur_embed_model:
        return False, "目前 embedding model 未設定"
    if summary.get("model") != cur_embed_model:
        return False, f"索引模型（{summary.get('model')}）與目前設定（{cur_embed_model}）不符，請跑 python util/build_embedding_index.py --rebuild"
    changed, removed = summary["changed"], summary["removed"]
    if changed or removed:
        return False, f"{len(changed)} 條未入索引或已變更、{len(removed)} 條已刪除"
    return True, ""


class _AlreadyApplied(Exception):
    """內部訊號：本章 B 類累積已套用，審查判斷轉為歷史紀錄。"""


def check_candidate_similarity_freshness(book, chapter, root=ROOT):
    """檢查 candidate_similarity.md 是否存在且符合 multi-factor freshness（11 因子 Fail-Closed 驗證）。

    回傳 (fresh: bool, reason: str, status: str)
    """
    root = Path(root)
    canonical = canonical_book_name(book)
    book_dir = book_directory(root, canonical)
    tmp = book_dir / ".tmp" / f"第{chapter}章"
    report_path = tmp / "candidate_similarity.md"
    candidates_path = tmp / "link_candidates.yaml"

    if not report_path.is_file():
        return False, "候選近鄰報告 candidate_similarity.md 不存在", ""
    if not candidates_path.is_file():
        return False, "候選檔 link_candidates.yaml 不存在", ""

    meta = extract_report_metadata(report_path)
    if not meta:
        return False, "candidate_similarity.md 缺少機器元資料標頭（<!-- candidate_similarity_meta -->）", ""

    if meta.get("schema_version") != "1":
        return False, f"元資料 schema_version 不符（報告 {meta.get('schema_version')} vs 預期 1）", ""
    if meta.get("book") != canonical:
        return False, f"元資料書名不符（報告 {meta.get('book')} vs 目前 {canonical}）", ""
    if str(meta.get("chapter")) != str(chapter):
        return False, f"元資料章節不符（報告 {meta.get('chapter')} vs 目前 {chapter}）", ""

    # 裁決是否已被消化（M3／M6 payload 已寫齊）——下面兩處綁定的鬆緊都取決於它。
    #
    # 判準要對著 link_plan 宣告的 C 類數量，不能只問「有沒有任何一個 entry」：
    # - 全章沒有新建條目（C=0）時 entry_content 永遠是空的，用 any() 會讓這一段
    #   判斷永遠是 False，放寬形同不存在；
    # - 反過來，5 個 C 只寫了 1 個就算「已消化」，剩下 4 個候選的 evidence 被改
    #   動時會被誤放行，而那幾筆裁決根本還沒做。
    # 判準與本檔 entries_expected 那一段一致。
    plan_for_review = _load_yaml(tmp / "link_plan.yaml")
    entry_dir = tmp / "entry_content"
    written_entries = len(list(entry_dir.glob("*.yaml"))) if entry_dir.is_dir() else 0
    if isinstance(plan_for_review, dict):
        expected_entries = _plan_unique_name_count(plan_for_review, "C_new_formal")
        adjudication_consumed = (
            (tmp / "chapter_content.yaml").is_file()
            and written_entries >= expected_entries
        )
    else:
        # 沒有 plan 就數不出應有的 C 類數量，退回舊的啟發式：payload 在就算已消化。
        # 正式流程不會走到這裡（payload 必然產在 resolve 之後），保留只是不改動
        # 既有契約。
        adjudication_consumed = (
            (tmp / "chapter_content.yaml").is_file() and written_entries > 0
        )

    cur_cand_sha = _file_sha256(candidates_path)
    if meta.get("candidate_sha256") != cur_cand_sha:
        # 裁決已消化之後，只有「候選集本身增刪」才需要重新裁決。evidence／surfaces
        # 是送進 embedding／rerank 的查詢文字，裁決前照舊整檔綁定；但修掉一個被長
        # 別名蓋住的死 surface 必然發生在 payload 寫完之後的 run 階段，那時逼出一
        # 次整套 rerank 重跑既沒有判斷可做，報告本身也已因條目入庫而失去診斷值。
        report_identity = meta.get("candidate_identity_sha256")
        cur_identity = candidate_identity_sha256(candidates_path)
        relaxed = (
            adjudication_consumed
            and report_identity                      # 舊報告沒這個欄位 → 退回整檔比對
            and cur_identity not in ("missing", "error")
            and report_identity == cur_identity
        )
        if not relaxed:
            return False, f"候選檔已變更（報告 hash {meta.get('candidate_sha256', '')[:8]} vs 目前 {cur_cand_sha[:8]}），需重跑 semantic_lookup.py", ""

    # 索引類因子只在「裁決尚未被消化」時才綁定。
    #
    # 這份報告的用途是在寫 payload 以前裁決「候選該連既有條目還是新建」。M3/M6 手寫
    # 完成之後，那個裁決已經被寫進 payload，而報告本身變成當時的紀錄；此後條目庫每
    # 長一點（本章 render 出的新條目、下一章新增的條目）都會讓指紋變動，逼出一次沒有
    # 任何判斷可做的重跑——申4 一章重跑四次，申3 完工後再檢查也照樣卡住。
    #
    # 更糟的是 render 之後重跑會讓本章 C 類候選對到自己而變成高可信，報告的診斷值歸零
    # （全庫 127 份報告回溯：3929 個候選只有 14 個真的送過重排）。所以這裡不是放寬，
    # 是把索引綁定放回它真正有意義的時點：payload 寫出來以前。
    if not adjudication_consumed:
        cur_link_sha = _file_sha256(root / "util" / "output" / "link_index.json")
        if cur_link_sha == "missing" or meta.get("link_index_sha256") != cur_link_sha:
            return False, "既有條目索引 link_index.json 缺失或已變更，需重跑 semantic_lookup.py", ""

    cur_homo_sha = _file_sha256(root / "_config" / "link_homonyms.yaml")
    if cur_homo_sha == "missing" or meta.get("homonyms_sha256") != cur_homo_sha:
        return False, "同名詞設定 link_homonyms.yaml 缺失或已變更，需重跑 semantic_lookup.py", ""

    if meta.get("rerank_policy_version") != RERANK_POLICY_VERSION:
        return False, f"判定規則版本已升級（報告 {meta.get('rerank_policy_version')} vs 目前 {RERANK_POLICY_VERSION}），需重跑 semantic_lookup.py", ""

    calib_path = root / CALIBRATION_FILE_REL
    if not calib_path.is_file():
        return False, "校準設定檔 reranker_calibration.yaml 不存在，需先建立", ""
    try:
        calib_data = yaml.safe_load(calib_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, f"校準設定檔 reranker_calibration.yaml 損壞無法解析（{exc}）", ""
    if not isinstance(calib_data, dict) or not isinstance(calib_data.get("models"), dict):
        return False, "校準設定檔 reranker_calibration.yaml 格式非預期（需包含 models mapping）", ""

    cur_calib_sha = _file_sha256(calib_path)
    if cur_calib_sha == "missing" or meta.get("calibration_sha256") != cur_calib_sha:
        return False, "校準設定檔 reranker_calibration.yaml 缺失或已變更，需重跑 semantic_lookup.py", ""

    meta_path = root / "util" / "output" / "embedding_index.meta.json"
    if not meta_path.is_file():
        return False, "embedding 索引 meta 檔不存在，需先建立索引", ""
    try:
        cur_embed_meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, f"embedding 索引 meta 檔損壞（{exc}），需 --rebuild", ""

    cur_fp = compute_index_fingerprint(cur_embed_meta)
    if cur_fp == "legacy_stale":
        return False, "embedding 索引為 legacy schema，需執行 build_embedding_index.py --rebuild", ""
    if not adjudication_consumed and meta.get("embedding_index_fingerprint") != cur_fp:
        return False, "embedding 向量索引指紋已變更，需重跑 semantic_lookup.py", ""

    # 檢查 Embedding 模型設定一致性（Fail-closed）
    try:
        cur_embed_model = select_endpoint(task="embedding", root=root).get("model")
    except Exception as exc:
        return False, f"目前 embedding route 無法解析：{exc}", ""
    if not cur_embed_model:
        return False, "目前 embedding model 未設定", ""
    if meta.get("embedding_model") != cur_embed_model:
        return False, f"embedding 模型已變更（報告 {meta.get('embedding_model')} vs 目前 {cur_embed_model}），需重跑 semantic_lookup.py", ""

    # 檢查 Embedding 索引是否與條目庫即時同步（防範跨章新詞未入索引漏查）
    embedding_synced, sync_reason = _embedding_index_synced(root)
    if not adjudication_consumed and not embedding_synced:
        return False, f"embedding 語義索引未與目前條目庫同步（{sync_reason}），需先更新 embedding index 再重跑 semantic_lookup.py", ""

    status = meta.get("rerank_status")
    if not status or status not in VALID_RERANK_STATUS:
        return False, f"rerank_status '{status}' 無效或缺失（必須為 {VALID_RERANK_STATUS}）", ""

    for req_field in ["rerankable_candidates", "rerank_attempted", "rerank_succeeded"]:
        if req_field not in meta:
            return False, f"元資料缺少運作統計欄位 {req_field}", status

    # 檢查 Rerank 模型設定一致性（Fail-closed）
    if status != "disabled":
        try:
            cur_rerank_model = select_endpoint(task="rerank", root=root).get("model")
        except Exception as exc:
            return False, f"目前 rerank route 無法解析：{exc}", status
        if not cur_rerank_model:
            return False, "目前 rerank model 未設定", status
        if meta.get("rerank_model") != cur_rerank_model:
            return False, f"rerank 模型已變更（報告 {meta.get('rerank_model')} vs 目前 {cur_rerank_model}），需重跑 semantic_lookup.py", status

    return True, "", status


def check_candidate_similarity_readiness(book, chapter, root=ROOT, production=True):
    """統一的前置與生產就緒檢查閘門。

    回傳 (ok: bool, hint: str, status: str, warning: str | None)
    """
    fresh, reason, status = check_candidate_similarity_freshness(book, chapter, root=root)
    canonical = canonical_book_name(book)
    if not fresh:
        return (
            False,
            f"從步驟2後半續做：python util/semantic_lookup.py --candidates {canonical} {chapter}（{reason}）",
            status,
            None,
        )
    if production and status == "disabled":
        return (
            False,
            "正式生產流程禁止 rerank_status: disabled（--no-rerank 僅供診斷/除錯）；請配置 Reranker 並重跑 semantic_lookup.py",
            status,
            None,
        )
    if status in {"partial", "degraded"}:
        warning = f"candidate_similarity fresh，但 Reranker 狀態為 {status}，本次使用降級結果"
        hint = "依報告檢視 ⚠ 高相似候選是否改用既有條目名（走 B 類累積），再進步驟3。"
        return True, hint, status, warning
    hint = "依報告檢視 ⚠ 高相似候選是否改用既有條目名（走 B 類累積），再進步驟3。"
    return True, hint, status, None


def verse_link_coverage_gaps(book, chapter, root=ROOT):
    """M5 重生失效偵測：本章 plan 自己宣告的詞出現在經文，verse_links 卻沒連上它。

    `verse_links_step` 開頭就是「輸出檔存在就沿用」，而擋在前面的作廢機制
    (`_invalidate_stale`) 只在 `pipeline_state.json` 有基線時生效——基線一旦被刪，
    改過 `link_plan.yaml`／`entry_content` 之後重跑會**靜默**沿用上一輪的
    `verse_links.yaml`。民20 實測整章 30 個候選只渲染出 4 個內文連結，而
    validate_knowledge_base／verify_links／link_quality_check／check_existing_links
    全部 PASS：它們驗的是「連出去的對不對」，沒有一道驗「該連的有沒有連」。

    只報**本章自己凍結得住的詞彙**：候選宣告的 surfaces、候選名、條目全名與括號前
    裸名、本章 entry_content payload 的 aliases。全庫索引的 aliases 不列入回報，因為
    它隨後續章節成長，拿它當基準會把「語料自然變多」誤判成缺口。

    但**位置競爭仍用完整索引**（含那些 aliases）：M5 是長詞優先、同節不重疊，把索引
    aliases 抽掉會讓短詞搶到本來屬於長詞的位置而生誤報（創40 實例：v1 的「埃及」其實
    被 alias「埃及王的酒政」整個蓋住，抽掉 alias 後「埃及」就被誤報成漏連）。
    因此掃描用完整 surface map，只在「勝出的詞是本章自己宣告的」時才回報。

    比對規則直接沿用 `build_surface_map` 與 `verse_links_step` 本體（含歧義不連、
    長詞優先、同節不重疊），所以報出來的每一筆都是同一套程式在同一份 plan 上會連、
    而現檔沒有的。
    """
    try:
        from . import run_chapter
    except ImportError:
        import run_chapter

    tmp = book_directory(root, book) / ".tmp" / f"第{chapter}章"
    plan = _load_yaml(tmp / "link_plan.yaml")
    payload = _load_yaml(tmp / "verse_links.yaml")
    if not isinstance(plan, dict) or not isinstance(payload, dict) or not plan:
        return []

    entry_dir = tmp / "entry_content"
    created = sorted(path.stem for path in entry_dir.glob("*.yaml")) if entry_dir.is_dir() else []

    def _surfaces(index):
        ctx = run_chapter.ChapterContext(book, chapter, root=root, index=index)
        ctx.created_entry_names = list(created)
        return ctx, run_chapter.build_surface_map(ctx, plan)

    index_path = root / "util" / "output" / "link_index.json"
    try:
        # 明確從 root 讀索引；resolver.load_index() 綁死在真實 repo 路徑，交給它會讓
        # 其他 root（測試、MCP 工作區）比對到錯的索引。
        full_index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.is_file() else {}
        if not isinstance(full_index, dict):
            full_index = {}
        _, own_map = _surfaces({})              # 本章自己宣告的詞（回報範圍）
        ctx, surface_map = _surfaces(full_index)  # 完整索引（位置競爭，避免短詞搶位誤報）
        verses = ctx.raw_verses()
    except (OSError, ValueError, KeyError):
        return []
    own = set(own_map)

    linked = {link.get("target") for link in (payload.get("links") or [])}
    # plan 的候選名可能落後於改名（出12 實例：plan 仍指「寄居的（ger）」，實際條目
    # 早已改名為「寄居的」，經文其實連得好好的）。目標條目檔不存在＝那是改名漂移，
    # 不是 verse_links 過期，不報。
    entry_stems = {path.stem for path in (root / "link_folder").rglob("*.md")}
    gaps = {}
    for vnum, verse in enumerate(verses, 1):
        spans = []
        for surface, info in surface_map.items():
            if info["verses"] is not None and vnum not in info["verses"]:
                continue
            idx = verse.find(surface)
            if idx != -1:
                spans.append((idx, idx + len(surface), surface))
        spans.sort(key=lambda s: (s[0], -(s[1] - s[0])))
        last_end = -1
        for start, end, surface in spans:
            if start >= last_end:
                target = surface_map[surface]["target"]
                if surface in own and target not in linked and target in entry_stems:
                    gaps.setdefault(target, []).append(f"第{vnum}節「{surface}」")
                last_end = end
    return sorted(gaps.items())


def build_checks(book, chapter, root=ROOT, preflight=False):
    canonical = canonical_book_name(book)
    book_dir = book_directory(root, book)
    tmp = book_dir / ".tmp" / f"第{chapter}章"
    raw_scripture = root / "raw_scripture" / canonical / f"第{chapter}章.txt"
    manifest_path = tmp / "source_manifest.md"
    plan_path = tmp / "link_plan.yaml"
    entry_dir = tmp / "entry_content"
    chapter_md = book_dir / f"第{chapter}章.md"
    output_dir = root / "util" / "output"

    plan = _load_yaml(plan_path)
    entries_expected = _plan_unique_name_count(plan, "C_new_formal")
    updates_expected = _plan_count(plan, "B_needs_update")

    entry_content_ok = entries_expected == 0 or (
        entry_dir.is_dir() and len(list(entry_dir.glob("*.yaml"))) >= entries_expected
    )
    link_updates_path = tmp / "link_updates.yaml"
    link_updates_ok = updates_expected == 0 or link_updates_path.exists()
    link_review_ok = updates_expected == 0
    link_review_detail = ""
    link_review_warning = ""
    if updates_expected and link_updates_path.is_file():
        try:
            update_manifest = _load_yaml(link_updates_path)
            # 已套用的章節不再重驗審查判斷，只驗累積區塊在不在。
            #
            # preview_updates 會拿條目「現在」的定義／主題發展去對本章 prepare 當時的
            # 基線。等到後面的章節合法更新了同一個條目（申4 補了美地與約但河的主題發展），
            # 申1-3 的舊 manifest 就會突然報「選了 keep 但區塊已被修改」——完工章節被
            # 後來的章節追溯性弄壞，而且條目越常被累積壞得越快。
            # 章節進行中（尚未套用）仍然全驗：那時基線比對正是用來擋「說 keep 卻改了區塊」。
            marker = f"<!-- accumulation:{canonical}:{chapter}:start -->"
            targets = [update.get("path") for update in (update_manifest.get("updates") or [])
                       if isinstance(update, dict) and update.get("path")]
            applied = bool(targets) and all(
                (root / str(path)).is_file()
                and marker in (root / str(path)).read_text(encoding="utf-8")
                for path in targets
            )
            if applied:
                link_review_ok = True
                link_review_detail = (
                    f"{len(targets)} 個條目的本章累積區塊齊備；"
                    "審查判斷為當時紀錄，不再與條目現況重比（後續章節可合法改動同一區塊）"
                )
                raise _AlreadyApplied
            link_updates.preview_updates(link_updates_path, root=root)
            link_review_ok = True
            if update_manifest.get("review_schema_version") is None:
                link_review_warning = (
                    "此章是 overview_review 上線前的 legacy link_updates.yaml，僅為相容而放行；"
                    "未宣稱 agent 當時已完成定義／主題發展判斷。未來由 prepare 產生的新 manifest "
                    "會強制逐條 keep/update。"
                )
        except _AlreadyApplied:
            pass
        except (OSError, ValueError, yaml.YAMLError) as exc:
            link_review_detail = str(exc)
    prompts_cmd = f"python util/run_chapter_manual.py prompts {canonical} {chapter}"
    check_cmd = f"python util/run_chapter_manual.py check {canonical} {chapter}"
    run_cmd = f"python util/run_chapter_manual.py run {canonical} {chapter}"

    embedding_ok, embedding_detail = _embedding_index_synced(root)

    verse_links_path = tmp / "verse_links.yaml"
    verse_gaps = (
        verse_link_coverage_gaps(canonical, chapter, root=root)
        if verse_links_path.is_file() and plan_path.is_file()
        else []
    )

    # 來源完整性與閱讀回執驗證
    sources_declared_ok = False
    sources_declared_detail = ""
    sources_read_ok = False
    sources_read_detail = ""

    if manifest_path.is_file():
        try:
            identities = source_excerpts.manifest_source_identities(manifest_path, root)
            counts = Counter(identity.key for identity in identities)
            expected = Counter({"CT": 1, "GT": 1, "KC": 1, "BH": 1, "STEP": 1})
            if counts == expected:
                sources_declared_ok = True
            else:
                sources_declared_detail = f"來源宣告不符合正好五套（CT/GT/KC/BH/STEP 各一筆）：目前為 {dict(counts)}"
        except Exception as exc:
            sources_declared_detail = f"無法解析來源清單：{exc}"

        if sources_declared_ok:
            try:
                source_problems = check_source_read.check(canonical, chapter, root=root)
                if not source_problems:
                    sources_read_ok = True
                else:
                    sources_read_detail = "；".join(source_problems)
            except Exception as exc:
                sources_read_detail = f"來源閱讀檢查失敗：{exc}"
    else:
        sources_declared_detail = f"來源清單 {manifest_path} 不存在"

    # 引句字串掃描只提供 reviewer 定位線索，不做內容正確性的硬判決。
    quote_fidelity_ok, quote_fidelity_detail, quote_fidelity_warning = True, "", ""
    if (tmp / "chapter_content.yaml").exists():
        try:
            quote_total, quote_misses, _names = check_quote_fidelity.check_quotes(
                canonical, chapter, root=root
            )
            if quote_misses:
                preview = "；".join(f"{label}：{quote[:28]}" for label, quote in quote_misses[:3])
                quote_fidelity_detail = (
                    f"引句 {quote_total} 處，字串回查未命中 {len(quote_misses)} 處——{preview}"
                    + ("⋯" if len(quote_misses) > 3 else "")
                )
                quote_fidelity_warning = (
                    f"{quote_fidelity_detail}。這些只作為 evidence review 的定位線索；"
                    "不可僅因字串未命中就判內容錯誤或要求改寫。"
                )
            else:
                quote_fidelity_detail = f"引句 {quote_total} 處全數命中"
        except Exception as exc:
            quote_fidelity_detail = f"引句字串掃描失敗：{exc}"
            quote_fidelity_warning = (
                f"{quote_fidelity_detail}；此掃描不擋 production，內容忠實度仍由 evidence review 判定。"
            )

    # 候選相似度與 Preflight / Production Readiness 檢查
    sim_ok, sim_hint, sim_status, sim_warning = check_candidate_similarity_readiness(
        canonical, chapter, root=root, production=True
    )

    # 附錄資源區塊一致性：render_step 每次重跑都會把舊檔的附錄區塊 passthrough，
    # 但若曾用未修正版 render 過、或 build_appendix_links 沒補跑，區塊就會整段消失
    # 而其他閘門全綠。索引有本章資源卻沒有區塊 = FAIL。
    appendix_block_ok = True
    appendix_block_detail = ""
    # 附錄 plugin（appendix/*）是 repo-global、非 per-vault：只有對真正的庫根跑才有意義。
    if chapter_md.is_file() and Path(root).resolve() == ROOT.resolve():
        try:
            sections = build_appendix_links.collect_all_appendix_sections(build_indexes=False)
            ch_sections = sections.get(f"{canonical}/第{chapter}章") or []
            has_block = APPENDIX_BLOCK_START in chapter_md.read_text(encoding="utf-8")
            if ch_sections and not has_block:
                appendix_block_ok = False
                appendix_block_detail = (
                    f"附錄索引有本章 {len(ch_sections)} 段資源，但 {chapter_md.name} 沒有附錄區塊"
                    "——多半是重 render 後沒補跑 build_appendix_links.py。"
                )
        except Exception as exc:  # noqa: BLE001 — infra 問題不擋 production
            appendix_block_detail = f"附錄一致性檢查略過：{exc}"

    # 短偽引句裁決紀錄：常駐引句閘門門檻 10 字，4-7 字的偽逐字引句（自己的措辭
    # 套「」、截斷經文補句號、中譯冒充英文原句）完全不驗。降門檻會噪音爆量、且
    # 這一型需人工裁決不能機械刪，所以改成 SOP 必跑一輪 `--min-chars 2` 並把裁決
    # 寫進 quote_adjudication.md；缺這份紀錄＝這一輪沒做（B3）。
    quote_adjudication = tmp / "quote_adjudication.md"
    quote_adjudication_ok = (
        not chapter_md.is_file() or quote_adjudication.is_file()
    )

    # markdown 相對路徑連結指向不存在的檔案：所有既有連結檢查都只看 wiki-link，
    # `[回目錄](…/全書目錄及綱要.md)` 這種在整卷做完前一直是斷的、完全靜默（C4）。
    # 豁免會逐步補齊的 `第N章.md`（導覽前後章）；`全書目錄及綱要.md` 整卷做完才有，
    # 修正版 render 已不再輸出該連結，仍出現＝舊版 render 的殘留 → 只警告、提示重跑；
    # 其餘（多半是 organization 裡打錯的跨檔連結）＝FAIL。
    md_link_ok = True
    md_link_detail = ""
    md_link_warning = ""
    if chapter_md.is_file():
        broken_hard, broken_catalog = [], []
        for target in re.findall(r"\]\(([^)\s]+\.md)\)", chapter_md.read_text(encoding="utf-8")):
            name = target.split("/")[-1]
            if re.fullmatch(r"第\d+章\.md", name):
                continue
            resolved = (chapter_md.parent / target.replace("%20", " ")).resolve()
            if resolved.is_file():
                continue
            (broken_catalog if name == "全書目錄及綱要.md" else broken_hard).append(target)
        if broken_hard:
            md_link_ok = False
            md_link_detail = "、".join(dict.fromkeys(broken_hard))
        elif broken_catalog:
            md_link_warning = (
                f"{chapter_md.name} 還有指向未建立的 全書目錄及綱要.md 的連結"
                "（舊版 render 殘留；修正版不再輸出）——整卷完成後重跑 render 即消失。"
            )

    # 候選存在性掃描紀錄：resolver 只靠字面比對，「承受為業→為業／產業」「心都消化
    # →心消化」這種近似重複要由人把候選從新建 C 改成累積既有 B，閘門完全不擋（庫已
    # 3000+ 條）。開章固定跑 search_wiki_entries(queries=[整章候選]) 把 unmatched
    # 存成 candidate_existence.md；缺這份＝這一步沒做（C1）。
    candidate_existence = tmp / "candidate_existence.md"
    candidate_existence_ok = (
        not (tmp / "link_candidates.yaml").exists() or candidate_existence.is_file()
    )

    checks = [
        CheckResult(
            "步驟1｜經文本地檔",
            raw_scripture.exists(),
            f"從步驟1「準備來源」開始：確認 {raw_scripture} 是否存在——"
            "這一步缺檔不可由程式代補，需回報使用者確認經文來源。",
        ),
        CheckResult(
            "步驟1｜source_manifest.md 完整五來源宣告",
            sources_declared_ok,
            "從步驟1「準備來源」繼續：必須包含 CT、GT、KC、BH、STEP 剛好各一筆有效來源。"
            + (f"（{sources_declared_detail}）" if sources_declared_detail else ""),
        ),
        CheckResult(
            "步驟1｜來源閱讀回執與 STEP 驗證",
            sources_read_ok,
            "從步驟1「準備來源」繼續：四套 commentary 必須有完整 read_log 逐字引句且 STEP 通過機器驗證。"
            + (f"（{sources_read_detail}）" if sources_read_detail else ""),
        ),
        CheckResult(
            "步驟2｜link_candidates.yaml",
            (tmp / "link_candidates.yaml").exists(),
            "從步驟2「建 link_candidates.yaml」開始：依 _config/schemas/link_candidates.schema.json "
            f"逐節核對經文與有效 raw text，寫 {tmp / 'link_candidates.yaml'}。",
        ),
        CheckResult(
            "步驟2｜候選存在性掃描紀錄（candidate_existence.md）",
            candidate_existence_ok,
            "resolver 只做字面比對，近似重複（承受為業→為業／產業、心都消化→心消化）"
            "要人把候選從新建 C 改成累積既有 B，閘門不擋。開章一次掃完整章候選："
            f"search_wiki_entries(queries=[整章候選名])，把 unmatched 清單寫入 {candidate_existence}。",
        ),
        CheckResult(
            "步驟2｜candidate_similarity.md（候選語義近鄰報告與 freshness）",
            sim_ok,
            sim_hint,
            warning=sim_warning,
        ),
    ]

    if preflight:
        return checks

    checks.extend([
        CheckResult(
            "步驟3｜link_plan.yaml（P2 resolve）",
            plan_path.exists(),
            f"從步驟3「跑 orchestrator」開始：python util/build_link_index.py && {prompts_cmd}",
        ),
        CheckResult(
            f"步驟3｜entry_content/*.yaml（M3，計畫需 {entries_expected} 個）",
            entry_content_ok,
            f"重跑步驟3：{check_cmd} 或 {prompts_cmd}（補未完成的條目 payload）。",
        ),
        CheckResult(
            "步驟3｜verse_links.yaml（M5）",
            (tmp / "verse_links.yaml").exists(),
            f"重跑步驟3：{check_cmd}（entry_content 全數完成後才會產生此檔）。",
        ),
        CheckResult(
            "步驟3｜verse_links.yaml 涵蓋本章 plan 宣告的經文詞",
            not verse_gaps,
            "verse_links.yaml 是上一輪的舊檔：M5 有檔就跳過，而刪掉 pipeline_state.json "
            "會關掉作廢機制、讓改過的 link_plan／entry_content 無法連鎖重生。"
            f'強制重生：rm "{verse_links_path}" 再跑 {run_cmd}'
            "（不要改用刪 pipeline_state.json；要改 link_plan 就自己把新 sha256 寫回去）。"
            "漏連：" + "；".join(
                f"{target}（{'、'.join(where[:3])}{'…' if len(where) > 3 else ''}）"
                for target, where in verse_gaps[:8]
            ) + ("…等 %d 個" % len(verse_gaps) if len(verse_gaps) > 8 else ""),
        ),
        CheckResult(
            "步驟3｜chapter_content.yaml（M6）",
            (tmp / "chapter_content.yaml").exists(),
            f"重跑步驟3：{check_cmd}（模型填本章整理 payload）。",
        ),
        CheckResult(
            f"步驟3｜{chapter_md.name}（P3 render）",
            chapter_md.exists(),
            f"重跑步驟3：{run_cmd}；若 manual_review 顯示 knowledge_nodes 閉合後全空，"
            "先處理步驟5的人工決策點（修 candidates 或人工建檔）再重跑。",
        ),
        CheckResult(
            f"步驟4｜link_updates.yaml（B 類累積，計畫需 {updates_expected} 筆）",
            link_updates_ok,
            f"從步驟4「B 類累積」開始：python util/link_updates.py prepare {canonical} {chapter}，"
            "回經文與有效 raw text 填 summary/relation，先 apply --dry-run 再 apply。",
        ),
        CheckResult(
            "步驟4｜overview_review 已逐條判斷定義／主題發展且與實際區塊一致",
            link_review_ok,
            "先完整讀取 link_updates.yaml 每筆 path 指向條目的定義、全部按書卷累積與主題發展；"
            "再完成 overview_review：definition/development 各選 keep 或 "
            "update；keep 合法。只有程式提出 challenge 而仍 keep 時才填受控 basis。"
            "定義只處理穩定身分，主題發展只做跨章綜合，"
            "不可把 summary/relation 換句話說貼入。development=update 要列本章＋另一章的 "
            f"synthesis_scope，再重跑 apply --dry-run。檢查訊息：{link_review_detail}",
            warning=link_review_warning,
        ),
        CheckResult(
            "步驟5｜引句字串疑點掃描（review 線索）",
            quote_fidelity_ok,
            "",
            warning=quote_fidelity_warning,
        ),
        CheckResult(
            "步驟6｜util/output/link_index.json",
            (output_dir / "link_index.json").exists(),
            "從步驟6「收尾驗證」開始：python util/build_appendix_links.py && python util/check_existing_links.py "
            f"{book_dir.name}/第{chapter}章.md --missing && python util/build_link_index.py",
        ),
        CheckResult(
            "步驟6｜util/output/link_quality_report.json",
            (output_dir / "link_quality_report.json").exists(),
            f"從步驟6繼續：python util/validate_knowledge_base.py && python util/link_quality_check.py {canonical}",
        ),
        CheckResult(
            "步驟6｜util/output/verify_report.json ＋ verify_result.txt",
            (output_dir / "verify_report.json").exists() and (output_dir / "verify_result.txt").exists(),
            f"從步驟6繼續：python util/verify_links.py {canonical} && python util/audit_knowledge_base.py --check-due",
        ),
        CheckResult(
            "步驟6｜embedding 語義索引同步",
            embedding_ok,
            f"（{embedding_detail}）從步驟6續做：python util/build_link_index.py，"
            "再 python util/build_embedding_index.py（增量，通常數秒）——"
            "本章新條目沒進索引，下一章的候選近鄰報告就查不到它們。",
        ),
        CheckResult(
            "步驟6｜附錄資源區塊未被 render 吃掉",
            appendix_block_ok,
            "重 render 會 passthrough 舊檔的附錄區塊；仍缺代表該章從未補跑或曾被舊版吃掉。"
            f"補跑：python util/build_appendix_links.py（{appendix_block_detail}）",
        ),
        CheckResult(
            "步驟5｜短偽引句裁決紀錄（--min-chars 2）",
            quote_adjudication_ok,
            "常駐引句閘門門檻 10 字，4-7 字的偽逐字引句不驗。必跑一輪並把裁決寫進紀錄："
            f"python util/check_quote_fidelity.py {canonical} {chapter} --min-chars 2，"
            f"逐條裁決（逐字命中／已改為轉述／已補全截斷／中譯已移出「」／確為強調用法保留）"
            f"寫入 {quote_adjudication}。",
        ),
        CheckResult(
            "步驟6｜章 md 的 markdown 路徑連結目標存在",
            md_link_ok,
            "章 md 有指向不存在檔案的 [文字](相對路徑.md) 連結（wiki-link 檢查看不到這一型）："
            f"{md_link_detail}——請修 chapter_content.yaml 的 organization 或確認目標檔。",
            warning=md_link_warning,
        ),
    ])
    return checks


def main():
    utf8_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("book")
    parser.add_argument("chapter", type=int)
    parser.add_argument("--preflight", action="store_true", help="只驗證前置包（步驟1與步驟2）完備性")
    args = parser.parse_args()

    try:
        checks = build_checks(args.book, args.chapter, preflight=args.preflight)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"❌ {exc}")
        return 1

    for res in checks:
        if not res.ok:
            print(f"❌ 缺檔：{res.label}")
            print(f"   → 請從此動作續做：{res.resume_hint}")
            print("   完成後依 agent_start_prompt.md 流程順序繼續往下一步，直到本檢查全數通過。")
            print("結論：FAIL（缺口見上）")
            return 1
        if getattr(res, "warning", None):
            print(f"⚠️ {res.warning}")
        else:
            print(f"✅ {res.label}")

    if args.preflight:
        print("✅ 前置交接包主要檔案、來源閱讀回執與 freshness 齊備。")
        print("結論：PASS")
        return 0

    canonical = canonical_book_name(args.book)
    errors, pending, notes = untracked_entry_findings(ROOT, args.book, args.chapter)
    for note in notes:
        print(f"ℹ️ {note}")
    if pending:
        print(f"📋 本章產出、commit 時必須一併 git add 的未追蹤條目檔（{len(pending)} 個）：")
        for rel in pending:
            print(f"   {rel}")
    if errors:
        print("❌ 發現漏提交的條目檔（先前章節 commit 時漏了 git add）：")
        for err in errors:
            print(f"   {err}")
        print("結論：FAIL（漏提交檔案見上）")
        return 1
    print("✅ 全部主要檔案齊備，流程完整。")
    print("結論：PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
