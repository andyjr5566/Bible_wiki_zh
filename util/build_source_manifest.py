#!/usr/bin/env python3
"""程式化產生章節 source_manifest.md，杜絕手寫 manifest 的格式錯誤。

背景：舊流程由 agent 手寫 source_manifest.md。第4欄「raw_data 檔案」若漏寫
`raw_data/` 前綴（裸檔名），`source_excerpts.parse_manifest` 舊版會靜默丟棄整列，
M3/M6 於是拿到空來源、模型只能憑訓練知識杜撰註釋，卻一路通過結構閘門
（申命記 1-6 即此因）。本工具依 `_config/source_catalog.json` 的位址規則產生
四來源列，raw_data 路徑一律帶 `raw_data/` 前綴，狀態依 raw_data 檔是否存在標記。

用法：
    python util/build_source_manifest.py 申命記 6
    python util/build_source_manifest.py 申命記 6 --print      # 只印不寫檔
    python util/build_source_manifest.py 申命記 6 --check      # 驗證既有 manifest 格式正確

四來源與位址規則（章號：ccbiblestudy 補零兩位，KC／BibleHub 不補零）：
    CT  https://www.ccbiblestudy.org/Old%20Testament/{cc_folder}/{num}CT{ch:02d}.htm
    GT  https://www.ccbiblestudy.org/Old%20Testament/{cc_folder}/{num}GT{ch:02d}.htm
    KC  https://www.kingcomments.com/en/bible-studies/{kc}/{ch}
    BH  https://biblehub.com/study/{en}/{ch}.htm
raw_data 檔名：ccbiblestudy_CT_{en}_{ch}.txt / ccbiblestudy_GT_{en}_{ch}.txt /
              kingcomments_{en}_{ch}.txt / biblehub_study_{en}_{ch}.txt
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "_config" / "source_catalog.json"


def _load_catalog():
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if not k.startswith("_")}


def source_rows(book, chapter, *, root=ROOT):
    """回傳四來源列 [(來源, 類型, URL, raw_data 相對路徑, 檔案是否存在)]。"""
    catalog = _load_catalog()
    if book not in catalog:
        raise KeyError(
            f"_config/source_catalog.json 沒有「{book}」的位址規則。"
            f"請先在該檔補一列（cc_folder／kc／en），再重新產生 manifest。"
        )
    meta = catalog[book]
    cc_folder = meta["cc_folder"]
    num = "".join(c for c in cc_folder if c.isdigit())  # 01Gen → 01
    kc = meta["kc"]
    en = meta["en"]
    ch = int(chapter)
    base_cc = f"https://www.ccbiblestudy.org/Old%20Testament/{cc_folder}"
    specs = [
        ("ccbiblestudy CT", "逐節註解", f"{base_cc}/{num}CT{ch:02d}.htm",
         f"ccbiblestudy_CT_{en}_{ch}.txt"),
        ("ccbiblestudy GT", "拾穗", f"{base_cc}/{num}GT{ch:02d}.htm",
         f"ccbiblestudy_GT_{en}_{ch}.txt"),
        ("KingComments", "研經註解", f"https://www.kingcomments.com/en/bible-studies/{kc}/{ch}",
         f"kingcomments_{en}_{ch}.txt"),
        ("BibleHub Study", "研經註解", f"https://biblehub.com/study/{en}/{ch}.htm",
         f"biblehub_study_{en}_{ch}.txt"),
    ]
    rows = []
    for label, kind, url, fname in specs:
        rel = f"raw_data/{fname}"
        exists = (Path(root) / rel).exists()
        rows.append((label, kind, url, rel, exists))
    return rows


def render_manifest(book, chapter, *, root=ROOT):
    rows = source_rows(book, chapter, root=root)
    lines = [
        "| 來源 | 類型 | URL | raw_data 檔案 | 狀態 |",
        "|------|------|-----|---------------|------|",
    ]
    for label, kind, url, rel, exists in rows:
        status = "OK" if exists else "缺檔（raw_data 未爬取）"
        lines.append(f"| {label} | {kind} | {url} | {rel} | {status} |")
    return "\n".join(lines) + "\n"


def manifest_path_for(book, chapter, root=ROOT):
    # 與 run_chapter.ChapterContext 相同：【NN 書名】/.tmp/第x章/source_manifest.md
    import book_paths  # noqa: local import 避免循環
    return book_paths.book_directory(Path(root), book) / ".tmp" / f"第{int(chapter)}章" / "source_manifest.md"


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="程式化產生章節 source_manifest.md")
    parser.add_argument("book")
    parser.add_argument("chapter", type=int)
    parser.add_argument("--print", dest="only_print", action="store_true",
                        help="只印出內容，不寫檔")
    parser.add_argument("--check", action="store_true",
                        help="驗證既有 manifest 是否與程式化版本一致（不寫檔）")
    args = parser.parse_args(argv)

    content = render_manifest(args.book, args.chapter)

    if args.only_print:
        sys.stdout.write(content)
        return 0

    out = manifest_path_for(args.book, args.chapter)
    if args.check:
        if not out.exists():
            print(f"✗ 缺 manifest：{out}")
            return 1
        import source_excerpts
        try:
            present = source_excerpts.require_sources(out, ROOT)
        except source_excerpts.SourceError as exc:
            print(f"✗ manifest 來源讀不到：\n{exc}")
            return 1
        print(f"✓ manifest 的 {len(present)} 個 OK 來源全部讀得到：{out}")
        return 0

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    n_ok = content.count("| OK |")
    print(f"✅ 已產生 {out}")
    missing = [line for line in content.splitlines() if "缺檔" in line]
    if missing:
        print(f"⚠ 有 {len(missing)} 個來源 raw_data 尚未爬取，請先 crawl_bible_text.py 再跑 run_chapter。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
