#!/usr/bin/env python3
"""抓取聖經研讀網頁，並立即輸出清理過的純文字。

使用方式（PowerShell）：

1. 抓取一個網址，輸出至預設的 ``cleaned`` 資料夾：
   python crawl_bible_text.py "https://biblehub.com/study/daniel/3.htm"

2. 指定純文字輸出資料夾：
   python crawl_bible_text.py "https://biblehub.com/study/daniel/3.htm" --output_path "D:\\BibleText"

3. 指定單一 URL 的輸出檔名（省略 .txt 時會自動補上）：
   python crawl_bible_text.py "https://biblehub.com/study/daniel/3.htm" --output_path cleaned --output_filename "但以理書第3章"

4. 從文字檔批次讀取網址（每行一個 URL）：
   python crawl_bible_text.py --url-file urls.txt --output_path cleaned --delay 1

5. 同時保留抓取到的原始 HTML：
   python crawl_bible_text.py --url-file urls.txt --output_path cleaned --save-html raw

6. 覆蓋已存在的輸出檔案：
   python crawl_bible_text.py --url-file urls.txt --output_path cleaned --overwrite

``--output_path`` 是選填參數；未指定時會儲存至目前目錄下的 ``cleaned``。
它與既有的 ``-o``、``--output-dir`` 是相同參數的不同寫法。
``--output_filename`` 只適用於一次抓取一個 URL。

本爬蟲只處理明確提供的 URL，不會自行遍歷整個網站，以控制抓取範圍及頻率。
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from clean_bible_html import clean_bytes


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36 "
    "BibleTextCleaner/1.0"
)


def safe_stem(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    host = parsed.netloc.lower().removeprefix("www.").split(".")[0]
    pieces = [p for p in parsed.path.split("/") if p]
    tail = "_".join(pieces[-3:]) or "index"
    if "." in tail:
        tail = tail.rsplit(".", 1)[0]
    stem = "".join(c if c.isalnum() or c in "_-" else "_" for c in f"{host}_{tail}")
    stem = "_".join(filter(None, stem.split("_")))
    if len(stem) > 100:
        digest = hashlib.sha1(url.encode()).hexdigest()[:10]
        stem = f"{stem[:85]}_{digest}"
    return stem


def fetch(url: str, timeout: float) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.7",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get("Content-Type", "")
        if "html" not in content_type.lower():
            raise ValueError(f"unexpected Content-Type: {content_type or '(missing)'}")
        return response.read()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch explicit Bible-study URLs and write cleaned UTF-8 text."
    )
    parser.add_argument("urls", nargs="*", help="one or more http(s) URLs")
    parser.add_argument("--url-file", type=Path,
                        help="UTF-8 file containing one URL per line (# comments allowed)")
    parser.add_argument("-o", "--output-dir", "--output_path",
                        dest="output_dir", type=Path, default=Path("cleaned"),
                        help="text output directory (default: cleaned)")
    parser.add_argument("--output_filename", "--output-filename",
                        dest="output_filename",
                        help="output filename for exactly one URL (.txt is optional)")
    parser.add_argument("--save-html", type=Path, metavar="DIR",
                        help="also preserve fetched HTML bytes in this directory")
    parser.add_argument("--delay", type=float, default=1.0,
                        help="seconds between requests (default: 1.0)")
    parser.add_argument("--timeout", type=float, default=30.0,
                        help="request timeout in seconds (default: 30)")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    urls = list(args.urls)
    if args.url_file:
        urls.extend(
            line.strip() for line in args.url_file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )
    urls = list(dict.fromkeys(urls))
    invalid = [u for u in urls if urllib.parse.urlparse(u).scheme not in {"http", "https"}]
    if not urls or invalid:
        if invalid:
            print(f"error: invalid URL: {invalid[0]}", file=sys.stderr)
        else:
            print("error: provide URLs or --url-file", file=sys.stderr)
        return 2
    if args.output_filename and len(urls) != 1:
        print("error: --output_filename requires exactly one URL", file=sys.stderr)
        return 2
    if args.output_filename:
        filename = Path(args.output_filename)
        if filename.name != args.output_filename or filename.name in {"", ".", ".."}:
            print("error: --output_filename must be a filename, not a path", file=sys.stderr)
            return 2
        if filename.suffix.lower() != ".txt":
            filename = filename.with_name(filename.name + ".txt")
        args.output_filename = filename.name

    args.output_dir.mkdir(parents=True, exist_ok=True)
    if args.save_html:
        args.save_html.mkdir(parents=True, exist_ok=True)

    failures = 0
    for index, url in enumerate(urls):
        if index and args.delay > 0:
            time.sleep(args.delay)
        stem = safe_stem(url)
        output = args.output_dir / (
            args.output_filename if args.output_filename else f"{stem}.txt"
        )
        if output.exists() and not args.overwrite:
            print(f"skip  {url} -> {output} (exists; use --overwrite)")
            continue
        try:
            raw = fetch(url, args.timeout)
            if args.save_html:
                (args.save_html / f"{stem}.html").write_bytes(raw)
            source, text = clean_bytes(f"{stem}.html", raw)
            output.write_text(text, encoding="utf-8", newline="\n")
            print(f"ok    {url} -> {output} [{source}, {len(text):,} chars]")
        except (OSError, ValueError, urllib.error.URLError) as exc:
            failures += 1
            print(f"error {url}: {exc}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
