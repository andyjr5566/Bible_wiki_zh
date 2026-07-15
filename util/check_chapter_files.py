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
            return 1
        print(f"✅ {label}")
    print("✅ 全部主要檔案齊備，流程完整。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
