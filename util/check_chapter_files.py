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
import sys
from pathlib import Path

try:
    from .book_paths import book_directory, canonical_book_name
    from .console import utf8_stdio
except ImportError:
    from book_paths import book_directory, canonical_book_name
    from console import utf8_stdio

import yaml

ROOT = Path(__file__).resolve().parent.parent

_ACCUM_RE = re.compile(r"<!-- accumulation:([^:]+):(\d+):start -->")


def _git_lines_z(root, *args):
    """跑 git 並以 NUL 分隔解析輸出（避開 core.quotepath 對中文路徑的轉義）。

    呼叫端須自行把 -z 放在 pathspec（--）之前——放在 args 尾端會被 git
    當成檔名（實測踩過：三個注入測試檔全數漏抓）。
    """
    try:
        proc = subprocess.run(
            ["git", *args], cwd=root, capture_output=True, check=True
        )
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
    """embedding 索引是否與條目庫同步（純雜湊比對，不打網路）。

    回傳 (ok, 說明)。這是機械可證的同步檢查：漏跑 build_embedding_index
    的下場是「下一章的候選近鄰報告查不到本章新條目」，靜默且延後爆發，
    所以在此硬擋。與相似度判斷（不可證、只附註）分屬兩事。
    """
    try:
        try:
            from .build_embedding_index import stale_summary
        except ImportError:
            from build_embedding_index import stale_summary
    except Exception as exc:  # numpy 未裝等環境問題也要能給出可讀訊息
        return False, f"無法載入 build_embedding_index：{exc}"
    summary = stale_summary(root)
    if summary is None:
        return False, "索引不存在（首次請跑 python util/build_embedding_index.py 全量建立）"
    changed, removed = summary["changed"], summary["removed"]
    if changed or removed:
        return False, f"{len(changed)} 條未入索引或已變更、{len(removed)} 條已刪除"
    return True, ""


def build_checks(book, chapter, root=ROOT):
    canonical = canonical_book_name(book)
    book_dir = book_directory(root, book)
    tmp = book_dir / ".tmp" / f"第{chapter}章"
    raw_scripture = root / "raw_scripture" / canonical / f"第{chapter}章.txt"
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
    run_chapter_cmd = f"python util/run_chapter.py {canonical} {chapter}"
    embedding_ok, embedding_detail = _embedding_index_synced(root)

    return [
        (
            "步驟1｜經文本地檔",
            raw_scripture.exists(),
            f"從步驟1「準備來源」開始：確認 {raw_scripture} 是否存在——"
            "這一步缺檔不可由程式代補，需回報使用者確認經文來源。",
        ),
        (
            "步驟1｜source_manifest.md",
            (tmp / "source_manifest.md").exists(),
            "從步驟1「準備來源」繼續：對每個補充來源（CT/GT/KC/BH）以既有記錄或目錄頁確認 URL 後跑 "
            "crawl_bible_text.py 抓 raw_data，查核每份 raw text 是否為本章有效內容，寫 "
            f"{tmp / 'source_manifest.md'}。",
        ),
        (
            "步驟2｜link_candidates.yaml",
            (tmp / "link_candidates.yaml").exists(),
            "從步驟2「建 link_candidates.yaml」開始：依 _config/schemas/link_candidates.schema.json "
            f"逐節核對經文與有效 raw text，寫 {tmp / 'link_candidates.yaml'}。",
        ),
        (
            "步驟2｜candidate_similarity.md（候選語義近鄰報告）",
            (tmp / "candidate_similarity.md").exists(),
            f"從步驟2後半續做：python util/semantic_lookup.py --candidates {canonical} {chapter}，"
            "依報告檢視 ⚠ 高相似候選是否改用既有條目名（走 B 類累積），再進步驟3。",
        ),
        (
            "步驟3｜link_plan.yaml（P2 resolve）",
            plan_path.exists(),
            f"從步驟3「跑 orchestrator」開始：python util/build_link_index.py && {run_chapter_cmd}",
        ),
        (
            f"步驟3｜entry_content/*.yaml（M3，計畫需 {entries_expected} 個）",
            entry_content_ok,
            f"重跑步驟3：{run_chapter_cmd}（可斷點續跑，只補未完成的條目 payload）。",
        ),
        (
            "步驟3｜verse_links.yaml（M5）",
            (tmp / "verse_links.yaml").exists(),
            f"重跑步驟3：{run_chapter_cmd}（entry_content 全數完成後才會產生此檔）。",
        ),
        (
            "步驟3｜chapter_content.yaml（M6）",
            (tmp / "chapter_content.yaml").exists(),
            f"重跑步驟3：{run_chapter_cmd}（模型填本章整理 payload）。",
        ),
        (
            f"步驟3｜{chapter_md.name}（P3 render）",
            chapter_md.exists(),
            f"重跑步驟3：{run_chapter_cmd}；若 manual_review 顯示 knowledge_nodes 閉合後全空，"
            "先處理步驟5的人工決策點（修 candidates 或人工建檔）再重跑。",
        ),
        (
            f"步驟4｜link_updates.yaml（B 類累積，計畫需 {updates_expected} 筆）",
            link_updates_ok,
            f"從步驟4「B 類累積」開始：python util/link_updates.py prepare {canonical} {chapter}，"
            "回經文與有效 raw text 填 summary/relation，先 apply --dry-run 再 apply。",
        ),
        (
            "步驟6｜util/output/link_index.json",
            (output_dir / "link_index.json").exists(),
            "從步驟6「收尾驗證」開始：python util/build_fhl_maps.py && python util/check_existing_links.py "
            f"{book_dir.name}/第{chapter}章.md --missing && python util/build_link_index.py",
        ),
        (
            "步驟6｜util/output/link_quality_report.json",
            (output_dir / "link_quality_report.json").exists(),
            f"從步驟6繼續：python util/validate_knowledge_base.py && python util/link_quality_check.py {canonical}",
        ),
        (
            "步驟6｜util/output/verify_report.json ＋ verify_result.txt",
            (output_dir / "verify_report.json").exists() and (output_dir / "verify_result.txt").exists(),
            f"從步驟6繼續：python util/verify_links.py {canonical} && python util/audit_knowledge_base.py --check-due",
        ),
        (
            "步驟6｜embedding 語義索引同步",
            embedding_ok,
            f"（{embedding_detail}）從步驟6續做：python util/build_link_index.py，"
            "再 python util/build_embedding_index.py（增量，通常數秒）——"
            "本章新條目沒進索引，下一章的候選近鄰報告就查不到它們。",
        ),
    ]


def main():
    utf8_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("book")
    parser.add_argument("chapter", type=int)
    args = parser.parse_args()

    try:
        checks = build_checks(args.book, args.chapter)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"❌ {exc}")
        return 1

    for label, ok, resume_hint in checks:
        if not ok:
            print(f"❌ 缺檔：{label}")
            print(f"   → 請從此動作續做：{resume_hint}")
            print("   完成後依 agent_start_prompt.md 流程順序繼續往下一步，直到本檢查全數通過。")
            print("結論：FAIL（缺口見上）")
            return 1
        print(f"✅ {label}")

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
