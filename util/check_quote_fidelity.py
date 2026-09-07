#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""引句與交叉引註的逐字回查——把每章現寫的 scratchpad 腳本做成常駐工具。

背景：閘門驗的是結構（檔案在不在、連結解不解得到、格式合不合法），沒有一道驗
「引號裡那句話是不是真的來自本章來源」。申4 這一章實測，M3 payload 有 29 處引句
飄移、B 類 summary/relation 有 6 處、章 md 有 3 處——全部是 scratchpad 腳本抓到的，
六道閘門一個都沒報。飄移的型態幾乎都一樣：截斷後自己補句號、換一種引號、把中文
譯文當成逐字引句、把不相鄰的兩句接成一句。

判定原則（保守，寧可漏報不可誤報）：
  - 語料只放**本章** manifest 宣告為 OK 的來源＋本章經文。相鄰章的 raw 不算，
    否則 CT 民25／民26 那種「同一套註釋相鄰章混引」就驗不出來。
  - 正規化：NFKC、彎引號轉直引號、去掉所有引號（「」『』與直引號：來源用“”、本庫再嵌套時內外層又會互換，引號本身不是內容）、
    去掉 U+2000–U+200B、去掉所有空白、
    把 [[目標|別名]] 還原成別名（章 md 的引句裡會夾 wiki-link）。
  - 語料裡的**經文**放整本聖經（引用別章、別卷的和合本經文都是正當寫法，KC 引提後4:7
    就是實例），**註釋只放本章**——相鄰章註釋混引正是要抓的東西。
  - 引句含 ⋯／… 時視為節錄，拆開後每段各自回查（每段至少 5 字才算數）。
  - 少於 10 字、或含頓線的引句不查：中文用「」兼作強調與並列（「過去／所要去」），
    那不是宣稱逐字引用，硬報只會製造誤報。
條目模式（--entry）：`link_folder/**.md` 是維護回合實際動筆的地方（情境 E 的活文件），
章節模式從不掃它，於是寫進定義／主題發展的引句一道閘門都沒有。條目模式改以「該條目
自己宣告累積過的每一章」為語料——那正好就是它有權引用的來源集合。
本工具只出報告，不改檔；報出＝強力線索，未報出不等於內容忠實。
"""
from __future__ import annotations

import argparse
import glob
import re
import sys
import unicodedata
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from util import console  # noqa: E402
from util.book_paths import book_directory, canonical_book_name  # noqa: E402
from util.source_excerpts import parse_manifest  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

MIN_QUOTE_CHARS = 10
MIN_FRAGMENT_CHARS = 5
# 巢狀引號：「…『某詞』…」的外層若用 [^「」『』] 比對會整段漏掉，而外層才是宣稱
# 逐字引用的那一層（memory: nested-quotes-escape-the-quote-checker）。
QUOTE_PATTERNS = (
    re.compile(r"「((?:[^「」]|『[^『』]*』)+?)」"),
    re.compile(r"『([^『』]+?)』"),
)
ELLIPSIS_RE = re.compile(r"[⋯…]+")
WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
MARKDOWN_EMPHASIS_RE = re.compile(r"\*+|=={2,}|==")
CHAPTER_ORGANIZATION_HEADING = "## 本章整理"

_CN_DIGITS = "一二三四五六七八九"


def _strip_wikilinks(text: str) -> str:
    return WIKILINK_RE.sub(lambda m: m.group(2) or m.group(1), text)


def normalize(text) -> str:
    text = unicodedata.normalize("NFKC", str(text))
    text = _strip_wikilinks(text)
    for src, dst in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"')):
        text = text.replace(src, dst)
    text = "".join(c for c in text if not 0x2000 <= ord(c) <= 0x200B)
    # 引號本身不算內容：把來源的引句再嵌進自己的「」時，內層一律要換成『』
    # （中文排版慣例），逐字比對必須看穿這一層，否則每章會多出二十幾筆假陽性。
    text = text.translate({ord(c): None for c in "「」『』\"'"})
    # markdown 的強調記號不是內容：引句裡寫 **可能** 是排版，不是改了來源的字。
    text = MARKDOWN_EMPHASIS_RE.sub("", text)
    return "".join(text.split())


def chapter_corpus(book: str, chapter: int, root: Path = ROOT) -> tuple[str, list[str]]:
    """本章語料＝manifest 的 OK 來源＋本章經文；回傳 (正規化語料, 檔名清單)。"""
    base = book_directory(root, book) / ".tmp" / f"第{chapter}章"
    manifest = base / "source_manifest.md"
    if not manifest.is_file():
        raise FileNotFoundError(f"找不到 {manifest}")
    paths = [path for _label, path in parse_manifest(manifest, root)]
    # 經文放整本聖經：引用別章甚至別卷的和合本經文都是正當寫法（申3 的累積引申1:4 的
    # 巴珊王噩；KC 申2 引提後4:7「那美好的仗我已經打過了」）。本地 raw_scripture 有全部
    # 66 卷，限制成本卷只會把正當的跨卷引用報成查無出處。
    # 註釋只放本章：相鄰章註釋混引（CT 民25／民26）正是要抓的那一型。
    paths.extend(sorted((root / "raw_scripture").glob("*/第*章.txt")))
    parts, names, scripture = [], [], 0
    for path in paths:
        path = Path(path)
        if not path.is_file():
            continue
        parts.append(normalize(path.read_text(encoding="utf-8", errors="ignore")))
        if path.parent.parent.name == "raw_scripture":
            scripture += 1
        else:
            names.append(path.name)
    if scripture:
        names.append(f"和合本經文 {scripture} 章")
    return "".join(parts), names


ACCUM_META_RE = re.compile(r"<!-- accumulation:([^:]+):(\d+):start -->")


def entry_corpus(entry_path: Path, root: Path = ROOT) -> tuple[str, list[str]]:
    """條目語料＝它累積過的每一章的 OK 來源＋全本聖經。

    條目引用的正當範圍就是它自己累積過的章節；拿全庫 raw_data 當語料會放過
    「引了別章註釋卻沒有該章累積」這一型，拿單章當語料又會把正當的跨章引用報成
    查無出處。
    """
    text = entry_path.read_text(encoding="utf-8")
    parts, names = [], []
    seen = set()
    for book, chapter in ACCUM_META_RE.findall(text):
        book = canonical_book_name(book)
        manifest = book_directory(root, book) / ".tmp" / f"第{chapter}章" / "source_manifest.md"
        if not manifest.is_file():
            names.append(f"（缺 manifest：{book}{chapter}）")
            continue
        for _label, path in parse_manifest(manifest, root):
            path = Path(path)
            if path in seen or not path.is_file():
                continue
            seen.add(path)
            parts.append(normalize(path.read_text(encoding="utf-8", errors="ignore")))
        names.append(f"{book}{chapter}")
    scripture = 0
    for path in sorted((root / "raw_scripture").glob("*/第*章.txt")):
        parts.append(normalize(path.read_text(encoding="utf-8", errors="ignore")))
        scripture += 1
    if scripture:
        names.append(f"和合本經文 {scripture} 章")
    return "".join(parts), names


def entry_targets(entry_path: Path):
    """條目裡由維護者寫出來的部分：定義與主題發展（逐章累積另有章節模式在驗）。"""
    text = entry_path.read_text(encoding="utf-8")
    out = []
    for heading in ("定義", "主題發展"):
        start = text.find(f"## {heading}")
        if start < 0:
            continue
        end = text.find("\n## ", start + 4)
        out.append((heading, text[start:end if end > start else len(text)]))
    return out


def check_entry_quotes(entry_path: Path, root: Path = ROOT, min_chars: int = MIN_QUOTE_CHARS):
    corpus, names = entry_corpus(Path(entry_path), root)
    total, misses = 0, []
    for label, text in entry_targets(Path(entry_path)):
        seen = set()
        for pattern in QUOTE_PATTERNS:
            for match in pattern.finditer(text):
                quote = match.group(1).strip()
                if len(quote) < min_chars or quote in seen:
                    continue
                if "／" in quote or "/" in quote:
                    continue
                seen.add(quote)
                total += 1
                if normalize(quote) in corpus:
                    continue
                if ELLIPSIS_RE.search(quote):
                    pieces = [f.strip() for f in ELLIPSIS_RE.split(quote) if f.strip()]
                    fragments = [f for f in pieces if len(f) >= MIN_FRAGMENT_CHARS] or pieces
                    if fragments and all(normalize(f) in corpus for f in fragments):
                        continue
                misses.append((label, quote))
    return total, misses, names


def _organization_section(markdown: str) -> str:
    """章 md 只查『本章整理』：知識節點清單引的是別章來源，不在本章語料裡。"""
    index = markdown.find(CHAPTER_ORGANIZATION_HEADING)
    return markdown[index:] if index >= 0 else ""


def _yaml_strings(node, fields=None, inside=False):
    """走訪 yaml 取出字串值。

    一定要解析 yaml，不能對原始文字做正則：safe_dump 的折行會在長句中插入反斜線
    與續行縮排，正則抓到的引句會夾著那些標記而整批誤判為查無出處（申3 實測 16 筆
    誤報裡有 6 筆是這一型）。
    """
    out = []
    if isinstance(node, dict):
        for key, value in node.items():
            hit = fields is None or key in fields
            out.extend(_yaml_strings(value, fields, inside or hit))
    elif isinstance(node, list):
        for item in node:
            out.extend(_yaml_strings(item, fields, inside))
    elif isinstance(node, str) and (fields is None or inside):
        out.append(node)
    return out


def _yaml_text(path: Path, fields=None) -> str:
    return "\n".join(_yaml_strings(yaml.safe_load(path.read_text(encoding="utf-8")), fields))


def collect_targets(book: str, chapter: int, root: Path = ROOT):
    """回傳 [(標籤, 待查文字)]；每一項只取真正由本章寫出來的部分。"""
    base = book_directory(root, book) / ".tmp" / f"第{chapter}章"
    targets = []
    for path in sorted(glob.glob(str(base / "entry_content" / "*.yaml"))):
        targets.append((f"entry_content/{Path(path).name}", _yaml_text(Path(path))))
    chapter_yaml = base / "chapter_content.yaml"
    if chapter_yaml.is_file():
        targets.append(("chapter_content.yaml", _yaml_text(chapter_yaml)))
    updates = base / "link_updates.yaml"
    if updates.is_file():
        targets.append(("link_updates.yaml（summary／relation）",
                        _yaml_text(updates, {"summary", "relation"})))
    rendered = book_directory(root, book) / f"第{chapter}章.md"
    if rendered.is_file():
        section = _organization_section(rendered.read_text(encoding="utf-8"))
        if section:
            targets.append((f"第{chapter}章.md（本章整理）", section))
    return targets


def check_quotes(book: str, chapter: int, root: Path = ROOT, min_chars: int = MIN_QUOTE_CHARS):
    corpus, source_names = chapter_corpus(book, chapter, root)
    total, misses = 0, []
    for label, text in collect_targets(book, chapter, root):
        seen = set()
        for pattern in QUOTE_PATTERNS:
            for match in pattern.finditer(text):
                quote = match.group(1).strip()
                if len(quote) < min_chars or quote in seen:
                    continue
                if "／" in quote or "/" in quote:
                    continue  # 並列用法，不是宣稱逐字引用
                seen.add(quote)
                total += 1
                if normalize(quote) in corpus:
                    continue
                if ELLIPSIS_RE.search(quote):
                    # 判準是「有沒有節錄記號」，不是「切出幾段」：以 ⋯ 結尾的引句
                    # 只切得出一段（申4「…並大可畏的事⋯」），用段數判會整句漏掉。
                    pieces = [f.strip() for f in ELLIPSIS_RE.split(quote) if f.strip()]
                    # 節錄逐段查。碎片全都短於門檻時（「因我已將⋯賜給⋯為業」這種句型
                    # 抽象），過濾後會空掉；空清單不代表查無出處，代表無從判斷——改成
                    # 每一段都要在語料裡，比直接報出來誠實。
                    fragments = [f for f in pieces if len(f) >= MIN_FRAGMENT_CHARS] or pieces
                    if fragments and all(normalize(f) in corpus for f in fragments):
                        continue
                misses.append((label, quote))
    return total, misses, source_names


def _chinese_number(value: int) -> str:
    if value <= 0:
        return str(value)
    if value < 10:
        return _CN_DIGITS[value - 1]
    if value == 10:
        return "十"
    if value < 20:
        return "十" + _CN_DIGITS[value - 11]
    if value < 100:
        tens, ones = divmod(value, 10)
        return _CN_DIGITS[tens - 1] + "十" + ("" if ones == 0 else _CN_DIGITS[ones - 1])
    return str(value)


REFERENCE_RE = re.compile(
    r"(?<![一-鿿])([一-鿿]{1,4}(?:福音|前書|後書|一書|二書|三書)?)"
    r"\s*(\d{1,3})\s*[:：]\s*(\d{1,3})"
)


def check_references(book: str, chapter: int, root: Path = ROOT):
    """交叉引註回查：阿拉伯／中文數字兩型都找不到才報（英文書卷名交給引句那一關）。"""
    corpus, _names = chapter_corpus(book, chapter, root)
    seen: dict[tuple[str, str, str], set[str]] = {}
    for label, text in collect_targets(book, chapter, root):
        for match in REFERENCE_RE.finditer(text):
            book_name, ref_chapter, verse = match.groups()
            if book_name.endswith(("第", "節", "章")):
                continue
            seen.setdefault((book_name, ref_chapter, verse), set()).add(label)
    misses = []
    for (book_name, ref_chapter, verse), labels in sorted(seen.items()):
        variants = {ref_chapter}
        if ref_chapter.isdigit():
            variants.add(_chinese_number(int(ref_chapter)))
        forms = set()
        for variant in variants:
            for joiner in (":", "：", ""):
                forms.add(normalize(f"{book_name}{variant}{joiner}{verse}"))
        if not any(form in corpus for form in forms):
            misses.append((f"{book_name}{ref_chapter}:{verse}", sorted(labels)))
    return len(seen), misses


def main() -> int:
    console.utf8_stdio()
    parser = argparse.ArgumentParser(description="引句與交叉引註逐字回查（只出報告）")
    parser.add_argument("book", nargs="?")
    parser.add_argument("chapter", type=int, nargs="?")
    parser.add_argument("--entry", help="改驗單一 link_folder 條目的定義與主題發展")
    parser.add_argument("--references", action="store_true",
                        help="同時回查交叉引註（誤報較多，預設關閉）")
    parser.add_argument("--min-chars", type=int, default=MIN_QUOTE_CHARS, metavar="N",
                        help=f"引句長度下限（預設 {MIN_QUOTE_CHARS}）。調低到 2~4 可掃出"
                             "「」被當強調記號用的短引句——那是常駐閘門驗不到的一型，"
                             "但誤報也會變多，報出的每一條都要人工裁決")
    args = parser.parse_args()
    if args.min_chars < 1:
        parser.error("--min-chars 至少要 1")
    if args.entry:
        path = Path(args.entry)
        if not path.is_absolute():
            path = ROOT / args.entry
        total, misses, names = check_entry_quotes(path, min_chars=args.min_chars)
        print(f"語料：{path.name} 累積過的 {'、'.join(names)}")
        print(f"引句 {total} 處，回查不到 {len(misses)} 處")
        for label, quote in misses:
            print(f"   ✗ {label}：{quote[:80]}")
        if misses:
            print("結論：FAIL（條目只能引用它自己累積過的那些章的來源）")
            return 1
        print("結論：PASS")
        return 0
    if not args.book or args.chapter is None:
        parser.error("要嘛給「書名 章」，要嘛給 --entry <條目路徑>")
    book = canonical_book_name(args.book)

    total, misses, source_names = check_quotes(book, args.chapter, min_chars=args.min_chars)
    print(f"語料：{'、'.join(source_names)}")
    print(f"引句 {total} 處，回查不到 {len(misses)} 處")
    for label, quote in misses:
        print(f"   ✗ {label}：{quote[:80]}")

    ref_misses = []
    if args.references:
        ref_total, ref_misses = check_references(book, args.chapter)
        print(f"交叉引註 {ref_total} 組，回查不到 {len(ref_misses)} 組")
        for reference, labels in ref_misses:
            print(f"   ✗ {reference}　← {'、'.join(labels)}")

    if misses or ref_misses:
        print("結論：FAIL（報出＝強力線索：多半是截斷補句號、換引號、"
              "把中文譯文當逐字引句，或把不相鄰的兩句接起來）")
        return 1
    print("結論：PASS（未報出不等於內容忠實，仍須依 manifest 人工核對）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
