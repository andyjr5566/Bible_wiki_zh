#!/usr/bin/env python3
"""Fetch book-level introduction sources from a source_manifest.yaml.

Prototype usage (PowerShell):

    python util/crawl_book_introduction.py "raw_data/book_intro/創世記/source_manifest.yaml" --overwrite

By default the crawler writes cleaned text to:

    raw_data/book_intro/<book>/raw/<SOURCE_ID>__NN.txt

Use ``--save-html`` when a reproducible HTML snapshot is also wanted.  The
cleaned text is intended as model input; ``source_notes.yaml`` remains the
human-reviewed normalization layer used to prevent source-role confusion.
"""

import sys
from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import yaml

try:
    from .clean_bible_html import TreeParser, clean_bytes, node_text, normalize_text
except ImportError:
    from clean_bible_html import TreeParser, clean_bytes, node_text, normalize_text

ROOT = Path(__file__).resolve().parent.parent
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36 "
    "BibleWikiBookIntro/0.1"
)


def fetch(url: str, timeout: float) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get("Content-Type", "")
        if "html" not in content_type.lower():
            raise ValueError(f"unexpected Content-Type: {content_type or '(missing)'}")
        return response.read()


def generic_clean(raw: bytes) -> str:
    parser = TreeParser()
    # TreeParser inherits HTMLParser and expects decoded text.  Reuse the same
    # robust decoding path indirectly by trying common encodings first.
    text = None
    for encoding in ("utf-8", "utf-8-sig", "cp1252", "latin1"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        text = raw.decode("utf-8", errors="replace")
    parser.feed(text)
    body = parser.root.find(tag="main") or parser.root.find(tag="article") or parser.root.find(tag="body") or parser.root
    cleaned = normalize_text(node_text(body))
    if len(cleaned) < 100:
        raise ValueError(f"generic extraction unexpectedly short ({len(cleaned)} chars)")
    return cleaned.rstrip() + "\n"


def source_mode(source_id: str, spec: dict) -> str | None:
    family = str(spec.get("family", "")).lower()
    if family == "ccbiblestudy":
        return "ccb"
    if family == "kingcomments":
        return "kingcomments"
    if family == "biblehub":
        return "biblehub"
    return None


def clean(source_id: str, spec: dict, raw: bytes, filename: str) -> tuple[str, str]:
    forced = source_mode(source_id, spec)
    if forced:
        detected, text = clean_bytes(filename, raw, forced)
        return detected, text
    return "generic", generic_clean(raw)


def urls_for(spec: dict) -> list[str]:
    urls = spec.get("urls")
    if isinstance(urls, list):
        return [str(url).strip() for url in urls if str(url).strip()]
    url = str(spec.get("url", "")).strip()
    return [url] if url else []


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def main() -> int:
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8")  # Windows cp1252 保險絲
    parser = argparse.ArgumentParser(description="Fetch book-level introduction sources")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--save-html", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    manifest_path = args.manifest
    if not manifest_path.is_absolute():
        manifest_path = ROOT / manifest_path
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or not isinstance(manifest.get("sources"), dict):
        raise ValueError("manifest.sources must be a mapping")

    book = str(manifest.get("book", "")).strip()
    if not book:
        raise ValueError("manifest.book is required")
    output_dir = args.output_dir or (manifest_path.parent / "raw")
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    receipt = {
        "book": book,
        "manifest": str(manifest_path.relative_to(ROOT)),
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        "sources": [],
    }
    failures = 0

    for source_id, spec in manifest["sources"].items():
        if not isinstance(spec, dict):
            continue
        urls = urls_for(spec)
        for index, url in enumerate(urls, 1):
            stem = f"{source_id}__{index:02d}"
            text_path = output_dir / f"{stem}.txt"
            html_path = output_dir / f"{stem}.html"
            if text_path.exists() and not args.overwrite:
                print(f"skip  {text_path.relative_to(ROOT)}")
                continue
            try:
                raw = fetch(url, args.timeout)
                detected, text = clean(source_id, spec, raw, html_path.name)
                text_path.write_text(text, encoding="utf-8", newline="\n")
                if args.save_html:
                    html_path.write_bytes(raw)
                receipt["sources"].append(
                    {
                        "source_id": source_id,
                        "url": url,
                        "cleaner": detected,
                        "chars": len(text),
                        "raw_sha256": sha256_bytes(raw),
                        "text_path": str(text_path.relative_to(ROOT)),
                        "html_path": str(html_path.relative_to(ROOT)) if args.save_html else None,
                    }
                )
                print(f"ok    {source_id} {index}/{len(urls)} -> {text_path.relative_to(ROOT)}")
            except Exception as exc:  # keep batch fetches inspectable
                failures += 1
                receipt["sources"].append(
                    {"source_id": source_id, "url": url, "error": str(exc)}
                )
                print(f"error {source_id} {url}: {exc}")
            if args.delay > 0:
                time.sleep(args.delay)

    receipt_path = output_dir / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"receipt -> {receipt_path.relative_to(ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
