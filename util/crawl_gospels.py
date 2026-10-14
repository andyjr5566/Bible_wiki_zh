#!/usr/bin/env python3
"""批次爬取四福音四套 commentary，輸出到標準 raw_data 檔名。

用法：
    python util/crawl_gospels.py
    python util/crawl_gospels.py --overwrite
    python util/crawl_gospels.py --delay 2.0
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "util"))

import build_source_manifest
import crawl_bible_text

GOSPELS = [
    ("馬太福音", 28),
    ("馬可福音", 16),
    ("路加福音", 24),
    ("約翰福音", 21),
]

def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        reconf = getattr(stream, "reconfigure", None)
        if reconf:
            reconf(encoding="utf-8")

    parser = argparse.ArgumentParser(description="爬取四福音四套 commentary rawdata")
    parser.add_argument("--delay", type=float, default=1.5, help="每次請求間隔秒數 (default: 1.5)")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    raw_data = ROOT / "raw_data"
    raw_data.mkdir(exist_ok=True)

    tasks: list[tuple[str, str]] = []  # (url, dest_fname)
    for book, chapters in GOSPELS:
        for ch in range(1, chapters + 1):
            specs = build_source_manifest.source_specs(book, ch)
            for label, kind, url, fname in specs:
                if label == "STEP Bible":
                    continue
                tasks.append((url, fname))

    total = len(tasks)
    ok = skipped = errors = 0

    for i, (url, fname) in enumerate(tasks):
        dest = raw_data / fname
        if dest.exists() and not args.overwrite:
            print(f"skip  [{i+1}/{total}] {fname} (exists)")
            skipped += 1
            continue

        if i and args.delay > 0:
            time.sleep(args.delay)

        try:
            raw = crawl_bible_text.fetch(url, args.timeout)
            import urllib.error
            source, text = crawl_bible_text.clean_bytes(f"{fname}", raw)
            with dest.open("w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            print(f"ok    [{i+1}/{total}] {fname} [{source}, {len(text):,} chars]")
            ok += 1
        except Exception as exc:
            errors += 1
            print(f"error [{i+1}/{total}] {fname}: {exc}", file=sys.stderr)

    print(f"\n完成：ok={ok}, skipped={skipped}, errors={errors} / total={total}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

