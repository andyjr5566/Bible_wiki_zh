#!/usr/bin/env python3
"""產生全庫／全卷維護稽核報告；不自動刪除、合併或升級條目。"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

from build_link_index import ROOT, collect_entries, load_resolutions

REPORT_DIR = ROOT / "util" / "output" / "audits"
POLICY_FILE = ROOT / "_config" / "maintenance_policy.yaml"
BOOKS_FILE = ROOT / "_config" / "bible_books.json"


def chapter_files(book=None):
    books = json.loads(BOOKS_FILE.read_text(encoding="utf-8"))
    roots = [ROOT / book] if book else [ROOT / name for name in books]
    files = []
    for directory in roots:
        if not directory.exists():
            continue
        files.extend(
            path for path in directory.glob("第*章.md")
            if re.fullmatch(r"第\d+章", path.stem)
        )
    return sorted(files)


def link_usage():
    counter = Counter()
    pattern = re.compile(r"\[\[([^\]|]+)")
    for md in ROOT.rglob("*.md"):
        if ".git" in md.parts or (ROOT / "util" / "output") in md.parents:
            continue
        try:
            counter.update(pattern.findall(md.read_text(encoding="utf-8")))
        except UnicodeError:
            continue
    return counter


def render_report(scope, files):
    entries, issues = collect_entries()
    usage = link_usage()
    candidates = [e for e in entries if e["status"] == "candidate"]
    orphaned = [e for e in entries if usage[e["title"]] == 0]
    resolutions = load_resolutions()
    lines = [
        f"# 知識庫維護稽核：{scope}\n",
        f"- 已完成章節檔：{len(files)}",
        f"- 正式條目：{sum(e['status'] == 'formal' for e in entries)}",
        f"- 候選條目：{len(candidates)}",
        f"- 未被 wiki-link 引用條目：{len(orphaned)}",
        "",
        "## Alias、分類與重複概念",
        "",
    ]
    if issues:
        lines.extend(f"- {issue}" for issue in issues)
    for title, path in resolutions["titles"].items():
        lines.append(f"- 待合併同名條目：{title}；目前 canonical：`{path}`")
    for alias, target in resolutions["aliases"].items():
        lines.append(f"- 已裁決 alias 衝突：{alias} → {target}")
    if not issues and not resolutions["titles"] and not resolutions["aliases"]:
        lines.append("- 無")

    lines.extend(["", "## 候選條目檢視", ""])
    if candidates:
        for entry in sorted(candidates, key=lambda e: (-usage[e["title"]], e["title"])):
            lines.append(
                f"- [[{entry['title']}]]：引用 {usage[entry['title']]} 次；"
                "是否升級仍須回到已收集資料判斷"
            )
    else:
        lines.append("- 無候選條目")

    lines.extend(["", "## 未被引用條目", ""])
    lines.extend(
        f"- [[{entry['title']}]]（`{entry['path']}`）" for entry in orphaned
    )
    lines.extend([
        "",
        "## 人工決策",
        "",
        "- [ ] 檢查同名條目是否合併",
        "- [ ] 檢查 alias 是否仍正確",
        "- [ ] 依資料決定候選條目的保留、合併或升級",
        "- [ ] 檢查分類錯置與來源不足",
        "",
        "> 本報告只提供稽核線索，不授權自動刪除、合併或升級。",
        "",
    ])
    return "\n".join(lines)


def write_full(interval):
    files = chapter_files()
    REPORT_DIR.mkdir(exist_ok=True)
    output = REPORT_DIR / f"full_audit_{len(files)}.md"
    output.write_text(render_report(f"全庫（每 {interval} 章）", files), encoding="utf-8")
    print(f"✅ 全庫稽核報告：{output}")
    return output


def write_book(book):
    books = json.loads(BOOKS_FILE.read_text(encoding="utf-8"))
    if book not in books:
        raise ValueError(f"未知書卷：{book}")
    files = chapter_files(book)
    REPORT_DIR.mkdir(exist_ok=True)
    output = REPORT_DIR / f"book_audit_{book}.md"
    report = render_report(f"{book}全卷", files)
    report += f"\n## 完整度\n\n- 章節：{len(files)}/{books[book]}\n"
    if len(files) != books[book]:
        report += "- 狀態：尚未完成全卷；本報告為預覽\n"
    else:
        report += "- 狀態：章節數完整，仍須完成上列人工決策\n"
    output.write_text(report, encoding="utf-8")
    print(f"✅ 全卷稽核報告：{output}")
    return output


def check_due():
    policy = yaml.safe_load(POLICY_FILE.read_text(encoding="utf-8"))
    interval = int(policy["full_audit_interval"])
    baseline = int(policy["baseline_completed_chapters"])
    count = len(chapter_files())
    next_due = ((baseline // interval) + 1) * interval
    while next_due <= count:
        matches = list(REPORT_DIR.glob(f"full_audit_{next_due}.md"))
        if not matches:
            print(f"❌ 已完成 {count} 章，缺少第 {next_due} 章里程碑全庫稽核")
            return 1
        next_due += interval

    books = json.loads(BOOKS_FILE.read_text(encoding="utf-8"))
    for book, total in books.items():
        if len(chapter_files(book)) == total:
            report = REPORT_DIR / f"book_audit_{book}.md"
            if not report.exists():
                print(f"❌ {book}已完成全卷，缺少全卷稽核報告")
                return 1
    print(f"✅ 維護稽核未逾期；目前完成 {count} 章")
    return 0


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true")
    group.add_argument("--book")
    group.add_argument("--check-due", action="store_true")
    parser.add_argument("--checkpoint", type=int, default=10)
    args = parser.parse_args()
    try:
        if args.check_due:
            return check_due()
        if args.book:
            write_book(args.book)
        else:
            write_full(args.checkpoint)
    except (OSError, ValueError, yaml.YAMLError, json.JSONDecodeError) as exc:
        print(f"❌ {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
