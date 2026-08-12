#!/usr/bin/env python3
"""程式化產生章節 source_manifest.md，杜絕手寫 manifest 的格式錯誤。

背景：舊流程由 agent 手寫 source_manifest.md。第4欄「raw_data 檔案」若漏寫
`raw_data/` 前綴（裸檔名），`source_excerpts.parse_manifest` 舊版會靜默丟棄整列，
M3/M6 於是拿到空來源、模型只能憑訓練知識杜撰註釋，卻一路通過結構閘門
（申命記 1-6 即此因）。本工具依 `_config/source_catalog.json` 的位址規則產生
四套註釋列，再依 `extract_stepbible.stepbible_filename` 的單一檔名契約加入 STEP
原文資料列；raw_data 路徑一律帶 `raw_data/` 前綴，狀態依檔案是否存在標記。

用法：
    python util/build_source_manifest.py 申命記 6
    python util/build_source_manifest.py 申命記 6 --print      # 只印不寫檔
    python util/build_source_manifest.py 申命記 6 --check      # 驗證既有 manifest 格式正確

四套註釋與位址規則（章號：ccbiblestudy 補零兩位，KC／BibleHub 不補零）：
    CT  https://www.ccbiblestudy.org/Old%20Testament/{cc_folder}/{num}CT{ch:02d}.htm
    GT  https://www.ccbiblestudy.org/Old%20Testament/{cc_folder}/{num}GT{ch:02d}.htm
    KC  https://www.kingcomments.com/en/bible-studies/{kc}/{ch}
    BH  https://biblehub.com/study/{en}/{ch}.htm
raw_data 檔名：ccbiblestudy_CT_{en}_{ch}.txt / ccbiblestudy_GT_{en}_{ch}.txt /
              kingcomments_{en}_{ch}.txt / biblehub_study_{en}_{ch}.txt /
              stepbible_{english_canonical}_{ch}.txt
"""
import argparse
import json
import re
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "_config" / "source_catalog.json"


def _load_catalog():
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if not k.startswith("_")}


def source_specs(book, chapter):
    """回傳四套註釋＋STEP 的 canonical metadata，不查看磁碟狀態。"""
    try:
        from . import book_paths, extract_stepbible
    except ImportError:
        import book_paths
        import extract_stepbible
    catalog = _load_catalog()
    canonical = book_paths.canonical_book_name(book)
    matched_key = None
    for k in catalog:
        if k == book or book_paths.canonical_book_name(k) == canonical:
            matched_key = k
            break
    if not matched_key:
        raise KeyError(
            f"_config/source_catalog.json 沒有「{book}」的位址規則。"
            f"請先在該檔補一列（cc_folder／kc／en），再重新產生 manifest。"
        )
    meta = catalog[matched_key]
    cc_folder = meta["cc_folder"]
    num = "".join(c for c in cc_folder if c.isdigit())  # 01Gen → 01
    kc = meta["kc"]
    en = meta["en"]
    ch = int(chapter)
    base_cc = f"https://www.ccbiblestudy.org/Old%20Testament/{cc_folder}"
    return [
        ("ccbiblestudy CT", "逐節註解", f"{base_cc}/{num}CT{ch:02d}.htm",
         f"ccbiblestudy_CT_{en}_{ch}.txt"),
        ("ccbiblestudy GT", "拾穗", f"{base_cc}/{num}GT{ch:02d}.htm",
         f"ccbiblestudy_GT_{en}_{ch}.txt"),
        ("KingComments", "研經註解", f"https://www.kingcomments.com/en/bible-studies/{kc}/{ch}",
         f"kingcomments_{en}_{ch}.txt"),
        ("BibleHub Study", "研經註解", f"https://biblehub.com/study/{en}/{ch}.htm",
         f"biblehub_study_{en}_{ch}.txt"),
        ("STEP Bible", "原文資料", "https://github.com/STEPBible/STEPBible-Data",
         extract_stepbible.stepbible_filename(canonical, ch)),
    ]


def source_rows(book, chapter, *, root=ROOT):
    """回傳四套註釋＋STEP 原文資料列及其檔案狀態。"""
    rows = []
    for label, kind, url, fname in source_specs(book, chapter):
        rel = f"raw_data/{fname}"
        exists = (Path(root) / rel).exists()
        rows.append((label, kind, url, rel, exists))
    return rows


def _manifest_cells(line: str):
    if not re.match(r"^\s*\|.*\|\s*$", line):
        return None
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    if len(cells) < 5:
        return None
    return cells[:5]


def _separator_row(cells) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def preserve_manifest_with_step(
    book,
    chapter,
    existing_text: str,
    *,
    root=ROOT,
    step_exists: bool | None = None,
):
    """只加入／更新 STEP row，逐 byte 語義保留既有 commentary rows。

    Legacy manifests 的標題、欄寬、row 順序與 CT/GT label 並不完全等同目前
    renderer。Phase A 不應把 90 章全部重排；本函式先驗證四個既有 URL/path/
    identity 都仍是 canonical 且 OK，再只處理 STEP 那一列。
    """
    specs = source_specs(book, chapter)
    legacy_kind_by_prefix = {
        "ccbiblestudy_CT_": "CT",
        "ccbiblestudy_GT_": "GT",
        "kingcomments_": "KC",
        "biblehub_study_": "BH",
    }
    expected_commentary = {
        f"raw_data/{fname}": (
            kind,
            url,
            next((legacy for prefix, legacy in legacy_kind_by_prefix.items()
                  if fname.startswith(prefix)), kind),
        )
        for _label, kind, url, fname in specs[:-1]
    }
    step_label, step_kind, step_url, step_filename = specs[-1]
    step_rel = f"raw_data/{step_filename}"
    if step_exists is None:
        step_exists = (Path(root) / step_rel).is_file()
    if not step_exists:
        raise FileNotFoundError(f"STEP source 尚未就緒，拒絕把 manifest 標成 OK：{step_rel}")

    lines = existing_text.splitlines(keepends=True)
    if not lines:
        raise ValueError("source_manifest.md 是空檔")
    row_indexes = []
    actual_commentary = {}
    step_indexes = []
    for index, line in enumerate(lines):
        cells = _manifest_cells(line)
        if cells is None or _separator_row(cells) or cells[0] == "來源":
            continue
        label, kind, url, rel, status = cells
        if rel == step_rel or "stepbible" in rel.casefold() or kind == "原文資料":
            step_indexes.append(index)
            row_indexes.append(index)
            continue
        if rel.startswith("raw_data/"):
            row_indexes.append(index)
            actual_commentary[rel] = (label, kind, url, status)

    if set(actual_commentary) != set(expected_commentary):
        missing = sorted(set(expected_commentary) - set(actual_commentary))
        extra = sorted(set(actual_commentary) - set(expected_commentary))
        raise ValueError(
            "manifest 四大 commentary 路徑不是 canonical 完整集合："
            f"missing={missing}, extra={extra}"
        )
    for rel, (_label, kind, url, status) in actual_commentary.items():
        expected_kind, expected_url, legacy_kind = expected_commentary[rel]
        actual_url = urllib.parse.urlparse(url)
        canonical_url = urllib.parse.urlparse(expected_url)
        same_url = url.rstrip("/").casefold() == expected_url.rstrip("/").casefold()
        # Exodus 9 has two audited historical ccbiblestudy URLs using the old
        # 02Exodus/09CT01 convention rather than the current 02Exo/02CT09 one.
        # Preserve them byte-for-byte, but require the correct source sigil and
        # chapter number so an arbitrary same-domain URL cannot pass.
        ccb_legacy = (
            actual_url.netloc.casefold() == "www.ccbiblestudy.org"
            and canonical_url.netloc.casefold() == "www.ccbiblestudy.org"
            and legacy_kind in {"CT", "GT"}
            and legacy_kind.casefold() in actual_url.path.casefold()
            and f"{int(chapter):02d}" in actual_url.path
        )
        if kind not in {expected_kind, legacy_kind} or not (same_url or ccb_legacy) or "OK" not in status:
            raise ValueError(
                f"manifest commentary row 不符，拒絕重寫：{rel} "
                f"kind={kind!r} url={url!r} status={status!r}"
            )
    if len(step_indexes) > 1:
        raise ValueError("manifest 含多個 STEP rows，拒絕猜測應保留哪一列")

    newline = "\r\n" if "\r\n" in existing_text else "\n"
    step_line = f"| {step_label} | {step_kind} | {step_url} | {step_rel} | OK |"
    if step_indexes:
        index = step_indexes[0]
        ending = "\r\n" if lines[index].endswith("\r\n") else (
            "\n" if lines[index].endswith("\n") else ""
        )
        lines[index] = step_line + ending
    else:
        if not row_indexes:
            raise ValueError("manifest 找不到可定位的 source table rows")
        index = row_indexes[-1] + 1
        if index > 0 and not lines[index - 1].endswith(("\n", "\r")):
            lines[index - 1] += newline
        lines.insert(index, step_line + newline)
    return "".join(lines)


def render_manifest(book, chapter, *, root=ROOT):
    rows = source_rows(book, chapter, root=root)
    lines = [
        "| 來源 | 類型 | URL | raw_data 檔案 | 狀態 |",
        "|------|------|-----|---------------|------|",
    ]
    for label, kind, url, rel, exists in rows:
        if exists:
            status = "OK"
        elif label == "STEP Bible":
            status = "缺檔（需 extract_stepbible.py）"
        else:
            status = "缺檔（需 crawl_bible_text.py）"
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
        print(
            f"⚠ 有 {len(missing)} 個來源 raw_data 尚未準備；"
            "註釋用 crawl_bible_text.py，STEP 原文資料用 extract_stepbible.py，"
            "補齊後再跑 run_chapter。"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
