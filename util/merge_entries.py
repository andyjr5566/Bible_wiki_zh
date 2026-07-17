#!/usr/bin/env python3
"""安全合併兩個重複條目：併內容、全庫重導連結、刪舊檔，不製造 missing link。

用途：清 embedding_dup_report.py 找出的「已存在近似重複」。近似 ≠ 重複，
本工具不自動判斷該不該合併——由人指定 loser／winner，工具只負責安全執行。

合併語義（winner 為保留檔，loser 併入後刪除）：
  - 按書卷累積：兩邊聯集（render_entry 依 (書卷,章) 自動去重合併，不漏章）
  - aliases／secondary_types／related_entries／sources：去重聯集
  - 定義／主題發展：保留 winner 的；loser 有而 winner 缺才補；兩邊都有且不同
    會警告，交人工確認（不靜默覆蓋既有內容——定義是保護區）
連結安全：先刪 winner 檔騰位，再用 rename_markdown 把 loser 檔改名成 winner
（同步把全庫 [[loser]] 重導成 [[winner]]），最後寫回合併內容。故所有原本指向
loser 或 winner 的連結，合併後都指向存在的 winner，不會斷。

  python util/merge_entries.py <loser.md> <winner.md> --dry-run
  python util/merge_entries.py <loser.md> <winner.md>          # 實際執行
  python util/merge_entries.py --batch pairs.json --dry-run    # 批次

批次 JSON：[{"loser": "link_folder/主題/A.md", "winner": "link_folder/主題/B.md"}, ...]
執行後務必跑 build_link_index.py 與 verify_links.py 驗證。
"""
import argparse
import json
import sys
from pathlib import Path

try:
    from . import rename_markdown
    from .render_entry import parse_entry, render_entry, safe_name
except ImportError:
    import rename_markdown
    from render_entry import parse_entry, render_entry, safe_name

ROOT = Path(__file__).resolve().parent.parent


class MergeError(RuntimeError):
    pass


def _dedup(seq):
    seen, out = set(), []
    for item in seq:
        key = str(item).strip()
        if key and key not in seen:
            seen.add(key)
            out.append(key)
    return out


def build_merged_payload(loser, winner, *, keep_loser_alias=True,
                         keep_definition="winner"):
    """把 loser 併進 winner，回傳 (merged_payload, warnings)。

    keep_definition: 定義／主題發展兩邊都有且不同時，保留哪邊（winner 預設，
    或 loser——當 loser 內容較豐富、winner 只是命名較好的殼時用）。
    """
    if loser.get("status") != "formal" or winner.get("status") != "formal":
        raise MergeError("目前只支援 formal 條目合併（candidate 請人工處理）")
    if keep_definition not in ("winner", "loser"):
        raise MergeError("keep_definition 只能是 winner 或 loser")
    warnings = []
    merged = dict(winner)

    merged["accumulations"] = (winner.get("accumulations") or []) + (
        loser.get("accumulations") or []
    )
    aliases = list(winner.get("aliases") or []) + list(loser.get("aliases") or [])
    if keep_loser_alias:
        aliases.append(loser["name"])
    # winner 自己的名字不當自己的 alias
    merged["aliases"] = [a for a in _dedup(aliases) if a != winner["name"]]
    merged["secondary_types"] = _dedup(
        list(winner.get("secondary_types") or []) + list(loser.get("secondary_types") or [])
    )
    names = {winner["name"], loser["name"]}
    merged["related_entries"] = [
        r for r in _dedup(
            list(winner.get("related_entries") or []) + list(loser.get("related_entries") or [])
        ) if r not in names
    ]
    merged["sources"] = _dedup(
        list(winner.get("sources") or []) + list(loser.get("sources") or [])
    )

    # 定義／主題發展：保護區，不靜默覆蓋
    for field, label in (("definition", "定義"), ("development", "主題發展")):
        w = str(winner.get(field, "")).strip()
        l = str(loser.get(field, "")).strip()
        if not w and l:
            merged[field] = l
            warnings.append(f"winner 缺{label}，已補入 loser 的{label}")
        elif w and l and w != l:
            if keep_definition == "loser":
                merged[field] = l
                warnings.append(f"兩邊{label}不同，依指定保留 loser 的；winner 的{label}已捨棄")
            else:
                warnings.append(
                    f"兩邊{label}不同，保留 winner 的；loser 的{label}未併入，請人工確認是否有獨有內容"
                )
    return merged, warnings


def _load_entry(path):
    path = Path(path)
    if not path.is_file():
        raise MergeError(f"條目不存在：{path}")
    return parse_entry(path.read_text(encoding="utf-8"))


def _count_redirects(loser_path, winner_path, root):
    """數出「若把 [[loser]] 全數重導到 [[winner]]」會改幾個連結、幾個檔。

    不呼叫 rename_markdown()（它的 validate_paths 會因 winner 已存在而擋下）；
    只借用其 resolver 與 update_wikilinks 做計數，不動任何檔案。
    """
    markdown_files = rename_markdown.collect_markdown_files(root)
    resolver = rename_markdown.WikiLinkResolver(root, markdown_files)
    changed_links = changed_files = 0
    for path in markdown_files:
        _, text, _ = rename_markdown.decode_markdown(path)
        _, count = rename_markdown.update_wikilinks(
            text, loser_path, winner_path, resolver, path
        )
        if count:
            changed_links += count
            changed_files += 1
    return changed_links, changed_files


def merge_entries(loser_path, winner_path, *, root=ROOT, dry_run=False,
                  keep_loser_alias=True, keep_definition="winner"):
    root = Path(root).resolve()
    loser_path = rename_markdown.resolve_in_root(loser_path, root)
    winner_path = rename_markdown.resolve_in_root(winner_path, root)
    if loser_path == winner_path:
        raise MergeError("loser 與 winner 相同")

    loser = _load_entry(loser_path)
    winner = _load_entry(winner_path)
    merged, warnings = build_merged_payload(
        loser, winner, keep_loser_alias=keep_loser_alias,
        keep_definition=keep_definition,
    )
    # 先驗證合併後 payload 可渲染（驗證左移；不合格就別動檔案）
    merged_markdown = render_entry(merged)

    # 預檢：會重導幾個連結（winner 已存在，不能用 rename 的 dry_run，自行計數）
    changed_links, changed_files = _count_redirects(loser_path, winner_path, root)

    report = {
        "loser": str(loser_path.relative_to(root)),
        "winner": str(winner_path.relative_to(root)),
        "accumulations": f"{len(winner.get('accumulations') or [])}+{len(loser.get('accumulations') or [])}",
        "aliases_after": merged["aliases"],
        "links_redirected": changed_links,
        "files_touched": changed_files,
        "warnings": warnings,
        "dry_run": dry_run,
    }
    if dry_run:
        return report

    # 執行：刪 winner 騰位 → rename loser→winner（重導全庫連結）→ 寫回合併內容
    winner_backup = winner_path.read_bytes()
    winner_path.unlink()
    try:
        rename_markdown.rename_markdown(loser_path, winner_path, root=root)
    except Exception:
        winner_path.write_bytes(winner_backup)  # 復原 winner，loser 未動
        raise
    winner_path.write_text(merged_markdown, encoding="utf-8")
    return report


def _print_report(report):
    mark = "（dry-run）" if report["dry_run"] else "✅"
    print(f"{mark} {report['loser']}  →  {report['winner']}")
    print(f"    累積 {report['accumulations']}（自動依書卷章去重）"
          f"｜重導連結 {report['links_redirected']} 個（{report['files_touched']} 檔）")
    print(f"    合併後 aliases：{report['aliases_after']}")
    for w in report["warnings"]:
        print(f"    ⚠ {w}")


def main():
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="安全合併重複條目")
    parser.add_argument("loser", nargs="?", help="要併入並刪除的條目 .md")
    parser.add_argument("winner", nargs="?", help="保留的條目 .md")
    parser.add_argument("--batch", type=Path, help="批次 JSON（loser/winner 陣列）")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--no-keep-alias", action="store_true",
        help="不把 loser 名加進 winner 的 aliases（錯字類合併適用）",
    )
    parser.add_argument(
        "--keep-definition", choices=("winner", "loser"), default="winner",
        help="兩邊定義／主題發展不同時保留哪邊（loser＝loser 內容較豐富時）",
    )
    args = parser.parse_args()

    jobs = []
    if args.batch:
        data = json.loads(args.batch.read_text(encoding="utf-8"))
        jobs = [(j["loser"], j["winner"]) for j in data]
    elif args.loser and args.winner:
        jobs = [(args.loser, args.winner)]
    else:
        parser.error("需提供 loser 與 winner，或用 --batch")

    failed = 0
    for loser, winner in jobs:
        try:
            report = merge_entries(
                loser, winner, dry_run=args.dry_run,
                keep_loser_alias=not args.no_keep_alias,
                keep_definition=args.keep_definition,
            )
            _print_report(report)
        except (MergeError, rename_markdown.RenameError, ValueError) as exc:
            print(f"❌ {loser} → {winner}：{exc}")
            failed += 1
    if not args.dry_run and jobs:
        print("\n提醒：跑 build_link_index.py 與 verify_links.py 驗證連結完整。")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
