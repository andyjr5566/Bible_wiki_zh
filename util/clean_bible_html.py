#!/usr/bin/env python3
"""Extract useful chapter text from CCBibleStudy, KingComments, and BibleHub.

Examples:
    python util/clean_bible_html.py *.html
    python util/clean_bible_html.py kc_dan_09.html --stdout
    python util/clean_bible_html.py raw_html --output-dir cleaned
"""

from __future__ import annotations

import argparse
import glob
import html
import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable


BLOCK_TAGS = {
    "address", "article", "aside", "blockquote", "br", "div", "dl", "dt",
    "dd", "figcaption", "figure", "footer", "h1", "h2", "h3", "h4", "h5",
    "h6", "header", "hr", "li", "main", "nav", "p", "pre", "section", "td",
    "th", "tr",
}
DROP_TAGS = {"script", "style", "noscript", "svg", "canvas", "template", "iframe"}


@dataclass
class Node:
    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    children: list["Node | str"] = field(default_factory=list)
    parent: "Node | None" = None

    @property
    def classes(self) -> set[str]:
        return set(self.attrs.get("class", "").split())

    def walk(self) -> Iterable["Node"]:
        yield self
        for child in self.children:
            if isinstance(child, Node):
                yield from child.walk()

    def find(self, *, tag: str | None = None, id_: str | None = None,
             class_: str | None = None) -> "Node | None":
        for node in self.walk():
            if tag is not None and node.tag != tag:
                continue
            if id_ is not None and node.attrs.get("id") != id_:
                continue
            if class_ is not None and class_ not in node.classes:
                continue
            return node
        return None


class TreeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("[document]")
        self.current = self.root
        self.drop_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in DROP_TAGS:
            self.drop_depth += 1
            return
        if self.drop_depth:
            return
        node = Node(tag, {k.lower(): v or "" for k, v in attrs}, parent=self.current)
        self.current.children.append(node)
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img",
                       "input", "link", "meta", "param", "source", "track", "wbr"}:
            self.current = node

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in DROP_TAGS:
            if self.drop_depth:
                self.drop_depth -= 1
            return
        if self.drop_depth:
            return
        node = self.current
        while node is not self.root:
            if node.tag == tag:
                self.current = node.parent or self.root
                return
            node = node.parent or self.root

    def handle_data(self, data: str) -> None:
        if not self.drop_depth and data:
            self.current.children.append(data)


def decode_html(raw: bytes) -> str:
    """Decode a page using its BOM/meta declaration, with sensible fallbacks."""
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw.decode("utf-8-sig", errors="replace")
    head = raw[:4096]
    match = re.search(
        br"""charset\s*=\s*["']?\s*([a-zA-Z0-9._-]+)""", head, re.I
    )
    declared = match.group(1).decode("ascii", "ignore") if match else ""
    # cp950 is Microsoft's Big5 superset and is needed by some Word-exported
    # pages that contain extension characters rejected by Python's strict big5.
    aliases = {"big5": "cp950", "utf-8": "utf-8", "utf8": "utf-8",
               "iso-8859-1": "latin-1", "windows-1252": "cp1252"}

    # Some older CCBibleStudy Word exports declare ISO-8859-1 even though their
    # body bytes are Big5. Trusting that declaration produces text such as
    # "¡eªð..." instead of Chinese. Prefer Big5 when it decodes cleanly and
    # yields substantial CJK content.
    if aliases.get(declared.lower(), declared) in {"latin-1", "cp1252"}:
        try:
            big5_text = raw.decode("cp950")
        except UnicodeDecodeError:
            pass
        else:
            cjk_count = sum("\u3400" <= char <= "\u9fff" for char in big5_text)
            if cjk_count >= 20:
                return big5_text

    candidates = [aliases.get(declared.lower(), declared), "utf-8", "cp950", "cp1252"]
    for encoding in dict.fromkeys(filter(None, candidates)):
        try:
            return raw.decode(encoding)
        except (LookupError, UnicodeDecodeError):
            pass
    return raw.decode("utf-8", errors="replace")


def repair_mojibake(text: str) -> str:
    """Repair common UTF-8-as-Windows-1252 sequences without harming CJK text."""
    def repair_big5_as_latin1(candidate: str) -> str | None:
        big5_markers = ("¡", "¤", "ª", "¦", "§", "¨", "«", "¬", "­", "®", "°", "±")
        if not any(ord(char) > 127 for char in candidate):
            return None
        try:
            repaired = candidate.encode("latin-1").decode("cp950")
        except (UnicodeEncodeError, UnicodeDecodeError):
            return None
        old_cjk = sum("\u3400" <= char <= "\u9fff" for char in candidate)
        new_cjk = sum("\u3400" <= char <= "\u9fff" for char in repaired)
        old_markers = sum(candidate.count(marker) for marker in big5_markers)
        new_markers = sum(repaired.count(marker) for marker in big5_markers)
        if new_cjk >= max(4, old_cjk * 2 + 4) and new_markers <= old_markers:
            return repaired
        return None

    repaired_text = repair_big5_as_latin1(text)
    if repaired_text is not None:
        text = repaired_text
    else:
        lines: list[str] = []
        changed = False
        for line in text.splitlines(keepends=True):
            body = line.rstrip("\r\n")
            ending = line[len(body):]
            repaired_line = repair_big5_as_latin1(body)
            if repaired_line is not None:
                lines.append(repaired_line + ending)
                changed = True
            else:
                lines.append(line)
        if changed:
            text = "".join(lines)

    markers = ("â€", "â€™", "â€œ", "â€”", "Ã", "Â©", "Â ")
    if not any(marker in text for marker in markers):
        return text
    try:
        repaired = text.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        lines = []
        changed = False
        for line in text.splitlines(keepends=True):
            body = line.rstrip("\r\n")
            ending = line[len(body):]
            if not any(marker in body for marker in markers):
                lines.append(line)
                continue
            try:
                repaired_line = body.encode("cp1252").decode("utf-8")
            except (UnicodeEncodeError, UnicodeDecodeError):
                lines.append(line)
                continue
            old_score = sum(body.count(m) for m in markers)
            new_score = sum(repaired_line.count(m) for m in markers)
            if new_score < old_score:
                lines.append(repaired_line + ending)
                changed = True
            else:
                lines.append(line)
        return "".join(lines) if changed else text
    old_score = sum(text.count(m) for m in markers)
    new_score = sum(repaired.count(m) for m in markers)
    return repaired if new_score < old_score else text


def node_text(node: Node) -> str:
    parts: list[str] = []

    def visit(item: Node | str) -> None:
        if isinstance(item, str):
            parts.append(item)
            return
        if item.tag in DROP_TAGS:
            return
        if item.tag in BLOCK_TAGS:
            parts.append("\n")
        for child in item.children:
            visit(child)
        if item.tag in BLOCK_TAGS:
            parts.append("\n")

    visit(node)
    return "".join(parts)


def normalize_text(text: str) -> str:
    text = html.unescape(text).replace("\xa0", " ").replace("\u3000", " ")
    text = repair_mojibake(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines: list[str] = []
    seen_adjacent = ""
    for raw_line in text.splitlines():
        line = re.sub(r"[ \t\f\v]+", " ", raw_line).strip()
        line = re.sub(r" *([，。；：！？、]) *", r"\1", line)
        if not line:
            if lines and lines[-1] != "":
                lines.append("")
            continue
        # Drop exact adjacent duplicates introduced by malformed/exported HTML.
        key = re.sub(r"\s+", " ", line).casefold()
        if key == seen_adjacent:
            continue
        seen_adjacent = key
        lines.append(line)
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def extract_ccb(root: Node) -> str:
    content = root.find(class_="WordSection1") or root.find(tag="body") or root
    text = normalize_text(node_text(content))
    lines = text.splitlines()
    while lines and (
        not lines[0].strip()
        or "返回首頁" in lines[0]
        or "返回本書目錄" in lines[0]
        or "返回講道資料總索引" in lines[0]
    ):
        lines.pop(0)
    footer_patterns = ("返回首頁 | 返回本書目錄", "返回首頁｜", "Top of Page")
    for index, line in enumerate(lines):
        if any(pattern in line for pattern in footer_patterns):
            lines = lines[:index]
            break
    return normalize_text("\n".join(lines))


def extract_kingcomments(root: Node) -> str:
    main = root.find(tag="main", id_="main-container")
    if main is None:
        raise ValueError("KingComments main content was not found")

    title_parts: list[str] = []
    for node in main.walk():
        if node.tag in {"h1", "h2"}:
            value = normalize_text(node_text(node))
            if value and value not in title_parts:
                title_parts.append(value)

    page_content = None
    for child in main.children:
        if isinstance(child, Node) and child.tag == "div" and child.classes == {"content"}:
            page_content = child
            break
    if page_content is None:
        raise ValueError("KingComments chapter body was not found")

    # The top jump buttons repeat every section heading, so omit them.
    for node in list(page_content.walk()):
        if "goto-title" in node.classes and node.parent:
            node.parent.children.remove(node)

    body = normalize_text(node_text(page_content))
    return normalize_text("\n\n".join(title_parts + [body]))


def extract_biblehub(root: Node) -> str:
    content = root.find(tag="div", class_="chap")
    if content is None:
        raise ValueError("BibleHub .chap content was not found")
    return normalize_text(node_text(content))


def detect_source(path: Path, root: Node, source: str) -> str:
    if source != "auto":
        return source
    name = path.name.lower()
    if name.startswith("ccb_") or root.find(class_="WordSection1"):
        return "ccb"
    if name.startswith("kc_") or root.find(tag="main", id_="main-container"):
        return "kingcomments"
    if name.startswith("bh_") or root.find(tag="div", class_="chap"):
        return "biblehub"
    raise ValueError("source could not be detected; use --source")


def clean_file(path: Path, source: str = "auto") -> tuple[str, str]:
    return clean_bytes(path.name, path.read_bytes(), source)


def clean_bytes(name: str, raw: bytes, source: str = "auto") -> tuple[str, str]:
    """Clean HTML bytes obtained from a file, requests, urllib, or another crawler."""
    parser = TreeParser()
    parser.feed(decode_html(raw))
    detected = detect_source(Path(name), parser.root, source)
    extractors = {
        "ccb": extract_ccb,
        "kingcomments": extract_kingcomments,
        "biblehub": extract_biblehub,
    }
    text = extractors[detected](parser.root)
    if len(text) < 100:
        raise ValueError(f"extracted text is unexpectedly short ({len(text)} characters)")
    return detected, text + "\n"


def expand_inputs(values: list[str], output_dir: Path) -> list[Path]:
    paths: list[Path] = []
    for value in values:
        matches = [Path(p) for p in glob.glob(value)]
        if not matches:
            matches = [Path(value)]
        for path in matches:
            if path.is_dir():
                paths.extend(sorted(path.glob("*.html")))
            elif path.is_file() and path.suffix.lower() in {".htm", ".html"}:
                paths.append(path)
    unique: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        resolved = path.resolve()
        if resolved not in seen and output_dir.resolve() not in resolved.parents:
            seen.add(resolved)
            unique.append(path)
    return unique


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract chapter text from downloaded Bible-study HTML files."
    )
    parser.add_argument("inputs", nargs="+", help="HTML file, directory, or glob")
    parser.add_argument("-o", "--output-dir", type=Path, default=Path("cleaned"),
                        help="output directory (default: cleaned)")
    parser.add_argument("--source", default="auto",
                        choices=("auto", "ccb", "kingcomments", "biblehub"),
                        help="force a source extractor")
    parser.add_argument("--stdout", action="store_true",
                        help="print one input to stdout instead of writing a file")
    parser.add_argument("--overwrite", action="store_true",
                        help="replace existing output files")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = expand_inputs(args.inputs, args.output_dir)
    if not paths:
        print("error: no HTML input files found", file=sys.stderr)
        return 2
    if args.stdout and len(paths) != 1:
        print("error: --stdout requires exactly one input file", file=sys.stderr)
        return 2

    if not args.stdout:
        args.output_dir.mkdir(parents=True, exist_ok=True)

    failures = 0
    for path in paths:
        try:
            source, text = clean_file(path, args.source)
            if args.stdout:
                sys.stdout.write(text)
                continue
            output = args.output_dir / f"{path.stem}.txt"
            if output.exists() and not args.overwrite:
                print(f"skip  {output} (exists; use --overwrite)")
                continue
            output.write_text(text, encoding="utf-8", newline="\n")
            print(f"ok    {path.name} -> {output} [{source}, {len(text):,} chars]")
        except Exception as exc:
            failures += 1
            print(f"error {path}: {exc}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
