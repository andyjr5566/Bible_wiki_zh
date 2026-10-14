#!/usr/bin/env python
"""從 STEP Bible 原文證據檔與詞典，為「從亞當到耶穌」的人物抓名字的原文與字義。

做法（只做機械對位，不猜）：
1. 人物記錄的每個「名字＋經節」，到 verses.json（和合本）找該節，數出節中出現的人名（資料集裡所有人物的名字）。
2. 同一節的 STEP 原文檔挑出人名詞（Np m/f，含前綴連寫）。
3. 兩邊個數相同才一一對位，取該位置的 dStrong；個數不同就略過（不硬配）。
4. 用 dStrong 到 TBESH／TBESG 詞典查原文、音譯、字義（「§ 名字 = "字義"」）。
產物：亞當到耶穌/名字字義.yaml（機器產物，不手改）。
STEP Bible 資料：CC BY 4.0（STEPBible.org / Tyndale House）；詞典簡編依 Abridged BDB（Online Bible）。
"""
from __future__ import annotations

import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DATA = HERE / "亞當到耶穌"
SITE_DATA = ROOT / "appendix" / "website" / "全聖經" / "亞當到耶穌" / "src" / "data"
STEP_RAW = ROOT / "raw_data"
LEX_DIR = ROOT / ".stepbible_data" / "Lexicons"

FILE_PREFIX = {
    "創": "genesis", "出": "exodus", "利": "leviticus", "民": "numbers", "申": "deuteronomy",
    "書": "joshua", "士": "judges", "得": "ruth", "撒上": "1_samuel", "撒下": "2_samuel",
    "王上": "1_kings", "王下": "2_kings", "代上": "1_chronicles", "代下": "2_chronicles",
    "拉": "ezra", "尼": "nehemiah", "斯": "esther", "伯": "job", "詩": "psalms", "箴": "proverbs",
    "傳": "ecclesiastes", "歌": "song_of_songs", "賽": "isaiah", "耶": "jeremiah", "哀": "lamentations",
    "結": "ezekiel", "但": "daniel", "何": "hosea", "珥": "joel", "摩": "amos", "俄": "obadiah",
    "拿": "jonah", "彌": "micah", "鴻": "nahum", "哈": "habakkuk", "番": "zephaniah", "該": "haggai",
    "亞": "zechariah", "瑪": "malachi", "太": "matthew", "可": "mark", "路": "luke", "約": "john",
}
BOOK_ORDER = sorted(FILE_PREFIX, key=len, reverse=True)
MEANING_RE = re.compile(r'§\s*(.+?)\s*=\s*"([^"]+)"')
REF_RE = re.compile(r"^([^\d\s]+)\s*(\d+):(\d+)(?:-(?:(\d+):)?(\d+))?$")


FUZZY_MIN = 0.88
ALIGN_MIN = 0.45


def clean_gloss(gloss: str) -> str:
    text = re.sub(r"\[[^\]]*\]|<[^>]*>", " ", gloss.lower())
    text = text.replace("-", "")
    previous = None
    while previous != text:
        previous = text
        text = re.sub(r"^\s*(?:of|to|the|and|from|by|with|for|in|at|into|towards)[/\s]+", "", text)
    return text.strip(" ;,.")


def norm_strong(code: str) -> str:
    m = re.match(r"^([HG])0*(\d+)([A-Z]?)$", code.strip())
    return f"{m.group(1)}{int(m.group(2)):04d}{m.group(3)}" if m else code.strip()


def load_lexicon(path: Path) -> dict[str, dict]:
    entries: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        cols = line.split("\t")
        if len(cols) < 8 or not re.match(r"^[HG]\d{4}", cols[0]):
            continue
        dstrong = norm_strong(cols[1].split("=")[0].strip())
        meaning = MEANING_RE.search(cols[7])
        entries[dstrong] = {
            "orig": cols[3].strip(), "translit": cols[4].strip(), "morph": cols[5].strip(),
            "gloss": cols[6].strip(),
            "name": meaning.group(1).strip() if meaning else "",
            "meaning": meaning.group(2).strip() if meaning else "",
        }
    return entries


_step_cache: dict[tuple[str, int], dict[int, list[dict]]] = {}


def step_chapter(book: str, chapter: int) -> dict[int, list[dict]]:
    key = (book, chapter)
    if key in _step_cache:
        return _step_cache[key]
    path = STEP_RAW / f"stepbible_{FILE_PREFIX[book]}_{chapter}.txt"
    verses: dict[int, list[dict]] = {}
    if path.is_file():
        current = 0
        for line in path.read_text(encoding="utf-8").splitlines():
            head = re.match(r"^## .+ \d+:(\d+)\s*$", line)
            if head:
                current = int(head.group(1))
                verses[current] = []
                continue
            if current and line.startswith("|") and not line.startswith("|---") and not line.startswith("| #"):
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if len(cells) >= 7:
                    verses[current].append({"orig": cells[1], "translit": cells[2], "gloss": cells[3], "strong": cells[4], "morph": cells[5]})
    _step_cache[key] = verses
    return verses


def is_person_token(token: dict) -> bool:
    morph = token["morph"].split("—")[0].strip()
    if morph.startswith("H"):
        return any(part in ("Npm", "Npf") for part in morph[1:].split("/")) or bool(re.search(r"Np[mf]", morph))
    return bool(re.match(r"^N-[A-Z]{3}-P(?:\b|$)", morph))


def split_ref(ref: str) -> list[tuple[str, int, int]]:
    out: list[tuple[str, int, int]] = []
    book = ""
    for raw in re.split(r"[,，;；、]", ref):
        part = raw.strip()
        if not part:
            continue
        m = re.match(r"^([^\d\s]+)\s*(.*)$", part)
        if m and m.group(1) in FILE_PREFIX or (m and m.group(1) in BOOK_ORDER):
            book, part = m.group(1), m.group(2)
        m = re.fullmatch(r"(\d+):(\d+)(?:-(?:(\d+):)?(\d+))?", part)
        if not m or not book:
            continue
        c1, v1 = int(m.group(1)), int(m.group(2))
        c2 = int(m.group(3)) if m.group(3) else c1
        v2 = int(m.group(4)) if m.group(4) else v1
        if c2 != c1 or v2 - v1 > 60:
            continue
        out += [(book, c1, v) for v in range(v1, v2 + 1)]
    return out


def main() -> int:
    persons = json.loads((SITE_DATA / "genealogy.json").read_text(encoding="utf-8"))["persons"]
    verses = json.loads((SITE_DATA / "verses.json").read_text(encoding="utf-8"))
    hebrew = load_lexicon(LEX_DIR / "TBESH - Translators Brief lexicon of Extended Strongs for Hebrew - STEPBible.org CC BY.txt")
    greek = load_lexicon(LEX_DIR / "TBESG - Translators Brief lexicon of Extended Strongs for Greek - STEPBible.org CC BY.txt")

    all_names = sorted({n for p in persons for n in [p["name"], *[x["as"] for x in p.get("names", []) if x.get("as")]] if n}, key=len, reverse=True)
    name_re = re.compile("|".join(re.escape(n) for n in all_names))
    english: dict[str, list[str]] = {}
    for line in (DATA / "名字英文對照.tsv").read_text(encoding="utf-8").splitlines():
        if line.strip() and "	" in line:
            zh, en = line.split("	", 1)
            english[zh.strip()] = [x for x in en.strip().split("/") if x]

    def norm(text: str) -> str:
        return re.sub(r"[^a-z]", "", text.lower())

    mentioned: dict[str, list[str]] = {}
    for other in persons:
        for field in ("parents", "spouses", "siblings", "kin", "descends"):
            for relation in other.get(field, []):
                if relation.get("ref") and relation.get("id"):
                    mentioned.setdefault(relation["id"], []).append(relation["ref"])
    result: dict[str, dict] = {}
    stats = {"person": len(persons), "no_english": 0, "no_match": 0, "ambiguous": 0, "no_lexicon": 0, "no_meaning": 0, "ok": 0}
    for person in persons:
        keys = {norm(x) for x in english.get(person["name"], [])}
        forms = {person["name"], *[x["as"] for x in person.get("names", []) if x.get("as")]}
        if not keys:
            stats["no_english"] += 1
            continue
        refs = [x["ref"] for x in person.get("names", []) if x.get("ref")]
        for relation in person.get("parents", []):
            if relation.get("ref"):
                refs.append(relation["ref"])
        refs += mentioned.get(person["id"], [])
        status = "no_match"
        found = None
        for fuzzy in (False, True, "aligned"):
            for ref in dict.fromkeys(refs):
                for book, chapter, verse in split_ref(ref):
                    if book not in FILE_PREFIX:
                        continue
                    hits: dict[str, tuple] = {}
                    step_tokens = [t for t in step_chapter(book, chapter).get(verse, []) if is_person_token(t)]
                    if fuzzy == "aligned":
                        text = verses.get(f"{book}{chapter}:{verse}") or ""
                        spans = [m.group(0) for m in name_re.finditer(text)]
                        mine = [i for i, name in enumerate(spans) if name in forms]
                        if len(spans) == len(step_tokens) and len(mine) == 1:
                            token = step_tokens[mine[0]]
                            strong = norm_strong(token["strong"])
                            lexicon = hebrew if strong.startswith("H") else greek
                            entry = lexicon.get(strong) or lexicon.get(re.sub(r"[A-Z]$", "", strong)) or {}
                            gloss_norm = norm(clean_gloss(token["gloss"]))
                            def score(tok: dict) -> float:
                                gloss = norm(clean_gloss(tok["gloss"]))
                                return max((SequenceMatcher(None, k, gloss).ratio() for k in keys), default=0)
                            best = max(score(tok) for tok in step_tokens)
                            # 位置對上、字形也要相近；而且這個詞不能有別的詞比它更像（避免希伯來文與中文語序不同時配錯）
                            if score(token) >= ALIGN_MIN and score(token) >= best - 1e-9:
                                found = (book, chapter, verse, token, entry, "aligned")
                                break
                        continue
                    for token in step_tokens:
                        strong = norm_strong(token["strong"])
                        lexicon = hebrew if strong.startswith("H") else greek
                        entry = lexicon.get(strong) or lexicon.get(re.sub(r"[A-Z]$", "", strong)) or {}
                        names = {norm(clean_gloss(token["gloss"]))} | {norm(x) for x in re.split(r"\s+or\s+", entry.get("name", "")) if x}
                        if keys & names:
                            hits[strong] = (token, entry, "exact")
                        elif fuzzy and any(form in (verses.get(f"{book}{chapter}:{verse}") or "") for form in forms):
                            score = max((SequenceMatcher(None, k, n).ratio() for k in keys for n in names if n), default=0)
                            if score >= FUZZY_MIN:
                                hits.setdefault(strong, (token, entry, "fuzzy"))
                    if len(hits) == 1:
                        token, entry, kind = next(iter(hits.values()))
                        found = (book, chapter, verse, token, entry, kind)
                        break
                    if len(hits) > 1:
                        status = "ambiguous"
                if found:
                    break
            if found:
                break
        if not found:
            stats[status] += 1
            continue
        book, chapter, verse, token, entry, kind = found
        record = {"ref": f"{book}{chapter}:{verse}", "strong": norm_strong(token["strong"]), "orig": entry.get("orig") or token["orig"],
                  "translit": entry.get("translit") or token["translit"], "name_en": entry.get("name") or clean_gloss(token["gloss"]).title(),
                  "meaning_en": entry.get("meaning", ""), "match": kind}
        if not record["meaning_en"]:
            stats["no_meaning"] += 1
        stats["ok"] += 1
        result[person["id"]] = record
    out = DATA / "名字字義.yaml"
    out.write_text("# 機器產物：extract_name_meanings.py 依 STEP Bible 對位產生，不手改。\n# 來源：STEP Bible / STEPBible-Data（CC BY 4.0）；詞典簡編依 Abridged BDB。\n"
                   + yaml.safe_dump(result, allow_unicode=True, sort_keys=True, width=1000), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
