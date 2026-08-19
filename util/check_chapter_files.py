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
        extract_report_metadata,
        RERANK_POLICY_VERSION,
        CALIBRATION_FILE_REL,
    )
    from .build_embedding_index import compute_index_fingerprint, stale_summary
    from .model_client import select_endpoint
    from . import source_excerpts
    from . import check_source_read
except ImportError:
    from book_paths import book_directory, canonical_book_name
    from console import utf8_stdio
    from semantic_lookup import (
        _file_sha256,
        extract_report_metadata,
        RERANK_POLICY_VERSION,
        CALIBRATION_FILE_REL,
    )
    from build_embedding_index import compute_index_fingerprint, stale_summary
    from model_client import select_endpoint
    import source_excerpts
    import check_source_read

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
    changed, removed = summary["changed"], summary["removed"]
    if changed or removed:
        return False, f"{len(changed)} 條未入索引或已變更、{len(removed)} 條已刪除"
    return True, ""


def check_candidate_similarity_freshness(book, chapter, root=ROOT):
    """檢查 candidate_similarity.md 是否存在且符合 multi-factor freshness。

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

    cur_cand_sha = _file_sha256(candidates_path)
    if meta.get("candidate_sha256") != cur_cand_sha:
        return False, f"候選檔已變更（報告 hash {meta.get('candidate_sha256', '')[:8]} vs 目前 {cur_cand_sha[:8]}），需重跑 semantic_lookup.py", ""

    cur_link_sha = _file_sha256(root / "util" / "output" / "link_index.json")
    if cur_link_sha == "missing" or meta.get("link_index_sha256") != cur_link_sha:
        return False, "既有條目索引 link_index.json 缺失或已變更，需重跑 semantic_lookup.py", ""

    cur_homo_sha = _file_sha256(root / "_config" / "link_homonyms.yaml")
    if cur_homo_sha == "missing" or meta.get("homonyms_sha256") != cur_homo_sha:
        return False, "同名詞設定 link_homonyms.yaml 缺失或已變更，需重跑 semantic_lookup.py", ""

    if meta.get("rerank_policy_version") != RERANK_POLICY_VERSION:
        return False, f"判定規則版本已升級（報告 {meta.get('rerank_policy_version')} vs 目前 {RERANK_POLICY_VERSION}），需重跑 semantic_lookup.py", ""

    cur_calib_sha = _file_sha256(root / CALIBRATION_FILE_REL)
    if meta.get("calibration_sha256") != cur_calib_sha:
        return False, "校準設定檔 reranker_calibration.yaml 已變更，需重跑 semantic_lookup.py", ""

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
    if meta.get("embedding_index_fingerprint") != cur_fp:
        return False, "embedding 向量索引指紋已變更，需重跑 semantic_lookup.py", ""

    status = meta.get("rerank_status")
    if not status or status not in VALID_RERANK_STATUS:
        return False, f"rerank_status '{status}' 無效或缺失（必須為 {VALID_RERANK_STATUS}）", ""

    for req_field in ["rerankable_candidates", "rerank_attempted", "rerank_succeeded"]:
        if req_field not in meta:
            return False, f"元資料缺少運作統計欄位 {req_field}", status

    # 檢查 Rerank 模型設定一致性
    if status != "disabled":
        try:
            cur_rerank_model = select_endpoint(task="rerank").get("model")
        except Exception:
            cur_rerank_model = None
        if cur_rerank_model and meta.get("rerank_model") != cur_rerank_model:
            return False, f"rerank 模型已變更（報告 {meta.get('rerank_model')} vs 目前 {cur_rerank_model}），需重跑 semantic_lookup.py", status

    return True, "", status


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
    link_updates_ok = updates_expected == 0 or (tmp / "link_updates.yaml").exists()
    prompts_cmd = f"python util/run_chapter_manual.py prompts {canonical} {chapter}"
    check_cmd = f"python util/run_chapter_manual.py check {canonical} {chapter}"
    run_cmd = f"python util/run_chapter_manual.py run {canonical} {chapter}"

    embedding_ok, embedding_detail = _embedding_index_synced(root)
    sim_fresh, sim_reason, sim_status = check_candidate_similarity_freshness(canonical, chapter, root=root)

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

    # 候選相似度與 Preflight Readiness 檢查
    sim_check_ok = sim_fresh
    sim_check_hint = ""
    sim_check_warning = ""

    if not sim_fresh:
        sim_check_hint = f"從步驟2後半續做：python util/semantic_lookup.py --candidates {canonical} {chapter}（{sim_reason}）"
    else:
        if preflight and sim_status == "disabled":
            sim_check_ok = False
            sim_check_hint = "正式交接前置包禁止 rerank_status: disabled（--no-rerank 僅供診斷）；請配置 Reranker 並重跑 semantic_lookup.py"
        elif sim_status in {"partial", "degraded"}:
            sim_check_warning = f"candidate_similarity fresh，但 Reranker 狀態為 {sim_status}，本次使用降級結果"
        else:
            sim_check_hint = "依報告檢視 ⚠ 高相似候選是否改用既有條目名（走 B 類累積），再進步驟3。"

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
            "步驟2｜candidate_similarity.md（候選語義近鄰報告與 freshness）",
            sim_check_ok,
            sim_check_hint,
            warning=sim_check_warning,
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
