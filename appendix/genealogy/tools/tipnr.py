"""離線讀取 STEP Bible TIPNR，產生人物及逐節人名對照。

出處：STEPBible.org，CC BY 4.0，commit bd09545。
只使用 PERSON 原始欄位；不使用 @Brief/@Article 衍生敘述。
"""
from __future__ import annotations

import csv
import io
import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, NamedTuple

if __package__:
    from . import step_names
else:
    import step_names

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "appendix/genealogy"
SOURCE = BASE / "sources/TIPNR.txt"
DATA = ROOT / "appendix/website/全聖經/亞當到耶穌/src/data"
DRAFT = BASE / "亞當到耶穌/對照草稿"
ATTRIBUTION = "# STEP Bible TIPNR（CC BY 4.0, commit bd09545）"

# 已核對 TIPNR 的實際縮寫，包括 Exo/Jos/Jdg/Rut/Ezk/Jol/Nam。
BOOKS = dict(zip(
    "創 出 利 民 申 書 士 得 撒上 撒下 王上 王下 代上 代下 拉 尼 斯 伯 詩 箴 傳 歌 賽 耶 哀 結 但 何 珥 摩 俄 拿 彌 鴻 哈 番 該 亞 瑪 太 可 路 約 徒 羅 林前 林後 加 弗 腓 西 帖前 帖後 提前 提後 多 門 來 雅 彼前 彼後 約一 約二 約三 猶 啟".split(),
    "Gen Exo Lev Num Deu Jos Jdg Rut 1Sa 2Sa 1Ki 2Ki 1Ch 2Ch Ezr Neh Est Job Psa Pro Ecc Sng Isa Jer Lam Ezk Dan Hos Jol Amo Oba Jon Mic Nam Hab Zep Hag Zec Mal Mat Mrk Luk Jhn Act Rom 1Co 2Co Gal Eph Php Col 1Th 2Th 1Ti 2Ti Tit Phm Heb Jas 1Pe 2Pe 1Jn 2Jn 3Jn Jud Rev".split(),
))
BOOK_ORDER = {book: n for n, book in enumerate(BOOKS.values())}
ENDPOINT = re.compile(
    r"(?:(?P<book>[1-3]?[A-Za-z]{2,3})\.)?"
    r"(?:(?P<chapter>\d+)\.)?(?P<verse>\d+)[a-z]?"
)
STRONG = re.compile(r"[HG]\d+[A-Za-z]*")


class TipnrForm(NamedTuple):
    unique_name: str
    dstrong: str
    translated: str
    refs: set[str]


@dataclass
class TipnrPerson:
    unique_name: str
    ustrong: str
    description: str
    parents: str
    siblings: str
    partners: str
    offspring: str
    tribe: str
    summary: str
    sex: str
    forms: list[TipnrForm] = field(default_factory=list)
    refs: set[str] = field(default_factory=set)


def ref_key(ref: str) -> tuple:
    bits = ref.removeprefix("LXX.").split(".")
    return ref.startswith("LXX."), BOOK_ORDER[bits[0]], int(bits[1]), int(bits[2])


def parse_refs(text: str, verse_counts: Mapping[tuple[str, int], int] | None = None) -> set[str]:
    """展開完整及省略書卷／章的經節，合併 a/b 次數後綴。

    支援 Gen.4.17a; 18,20-22; 5.1、完整範圍終點、LXX.Est.3.1。
    逗號／分號後沿用上一書卷及章；LXX 保留獨立前綴，避免混入
    希伯來本文。詩篇標題的第 0 節照原樣保留。
    跨章範圍須提供精確章節長度；未知長度、跨書卷、
    ff（無精確終點）一律拋錯，不猜測、不默默略過。實際 PERSON
    子行列出完整出現處，因此不讀含 ff 的 Total 摘要。
    """
    result: set[str] = set()
    context: tuple[str, str, int] | None = None

    def endpoint(value: str, previous: tuple[str, str, int] | None) -> tuple[str, str, int, int]:
        prefix = "LXX." if value.startswith("LXX.") else ""
        if prefix:
            value = value[4:]
        match = ENDPOINT.fullmatch(value)
        if not match:
            raise ValueError(f"無法解析精確經節：{value!r}")
        book, chapter, verse = match.group("book", "chapter", "verse")
        if book:
            if book not in BOOK_ORDER or chapter is None:
                raise ValueError(f"無效書卷／章：{value!r}")
        else:
            if previous is None:
                raise ValueError(f"省略經節缺少上文：{value!r}")
            prefix, book, last_chapter = previous
            chapter = chapter or str(last_chapter)
        c, v = int(chapter), int(verse)
        if c < 1 or v < 0 or (v == 0 and book != "Psa"):
            raise ValueError(f"無效章節：{value!r}")
        return prefix, book, c, v

    for token in re.split(r"[;,；，]", text):
        token = token.strip()
        if not token:
            continue
        limits = re.split(r"\s*[-–—]\s*", token)
        if len(limits) > 2:
            raise ValueError(f"無效經節範圍：{token!r}")
        start = endpoint(limits[0], context)
        end = endpoint(limits[1], start[:3]) if len(limits) == 2 else start
        if start[:2] != end[:2] or start[2:] > end[2:]:
            raise ValueError(f"不支援跨書卷或倒序經節：{token!r}")
        prefix, book, first_chapter, first_verse = start
        last_chapter, last_verse = end[2:]
        for chapter in range(first_chapter, last_chapter + 1):
            first = first_verse if chapter == first_chapter else 1
            if chapter == last_chapter:
                last = last_verse
            elif verse_counts is not None and (book, chapter) in verse_counts:
                last = verse_counts[book, chapter]
            else:
                raise ValueError(f"跨章範圍需要精確章節長度：{book}.{chapter}")
            if last < first:
                raise ValueError(f"範圍超出章節長度：{token!r}")
            if verse_counts is not None and (book, chapter) in verse_counts:
                if last > verse_counts[book, chapter]:
                    raise ValueError(f"範圍超出章節長度：{token!r}")
            result.update(f"{prefix}{book}.{chapter}.{v}" for v in range(first, last + 1))
        context = end[:3]
    return result


def parse_chinese_refs(text: str) -> set[str]:
    """接受人物引用中的多段、重複書名及省略書名／章。"""
    def replace(match: re.Match) -> str:
        name, chapter, verse = match.groups()
        if name not in BOOKS:
            raise ValueError(f"未知書卷簡稱：{name}")
        return f"{BOOKS[name]}.{chapter}.{verse}"

    converted = re.sub(r"([^\W\d_]+)(\d+):(\d+)", replace, text)
    return parse_refs(re.sub(r"\s+", "", converted).replace(":", "."))


def parse_tipnr(text: str) -> list[TipnrPerson]:
    """解析 $ 分隔的 PERSON 紀錄，排除檔頭示範、PLACE 及 OTHER。"""
    persons: list[TipnrPerson] = []
    active = False
    person: TipnrPerson | None = None
    for number, raw_line in enumerate(text.splitlines(), 1):
        line = raw_line.rstrip()
        if line.startswith("$"):
            active = bool(re.match(r"^\$=+\s*PERSON\(s\)\s*$", line))
            person = None
            continue
        if not active or not line:
            continue
        cells = [cell.strip() for cell in line.split("\t")]
        if not line.startswith(("–", "@")) and re.match(r"^[^\t]+@[^\t]+=[HG]\d", cells[0]):
            if len(cells) < 9:
                raise ValueError(f"TIPNR 第 {number} 行主紀錄欄位不足")
            unique_name, ustrong = cells[0].rsplit("=", 1)
            person = TipnrPerson(unique_name, ustrong, *cells[1:9])
            persons.append(person)
        elif person is not None and line.startswith("–") and cells[0] != "– Total":
            if len(cells) < 5 or "@" not in cells[1]:
                raise ValueError(f"TIPNR 第 {number} 行子紀錄欄位不足")
            dstrong = cells[2].split("«", 1)[0].split("=", 1)[0].strip()
            if not STRONG.fullmatch(dstrong):
                raise ValueError(f"TIPNR 第 {number} 行 Strong 無效：{dstrong}")
            # 此版本實際沒有 link 欄，Refs 在 cells[4]。亦支援檔頭宣告的
            # link + Refs 版本；略過明確 URL，不用連結推測出現處。
            ref_column = 5 if len(cells) > 5 and (not cells[4] or cells[4].startswith(("http://", "https://"))) else 4
            # Refs 後的額外欄可能含 @ 註記，不屬於經節。
            ref_text = cells[ref_column]
            try:
                refs = parse_refs(ref_text)
            except ValueError as exc:
                raise ValueError(f"TIPNR 第 {number} 行：{exc}") from exc
            form = TipnrForm(cells[1], dstrong, cells[3], refs)
            person.forms.append(form)
            person.refs.update(refs)
    if len({p.unique_name for p in persons}) != len(persons):
        raise ValueError("TIPNR PERSON 有重複 UniqueName")
    if any(not p.forms for p in persons):
        raise ValueError("TIPNR PERSON 缺少人名子紀錄")
    return persons


def canonical_strong(strong: str) -> str:
    """STEP 可省略前導零；保留大小寫有意義的個人後綴再比對。"""
    match = re.fullmatch(r"([HG])(\d+)([A-Za-z]*)", strong)
    return f"{match[1]}{int(match[2]):04d}{match[3]}" if match else ""


def base_strong(strong: str) -> str:
    match = re.fullmatch(r"([HG])(\d+)[A-Za-z]*", strong)
    return f"{match[1]}{int(match[2]):04d}" if match else ""


def normalize_name(name: str) -> str:
    return re.sub(r"[-‐‑–—\s]", "", name).casefold()


def form_names(form: TipnrForm) -> set[str]:
    # | 左側是別名、右側是主名；譯名的 = 右側是版本標籤。
    names = form.unique_name.split("@", 1)[0].split("|")
    names.extend(part.split("=", 1)[0].strip() for part in re.split(r"[;/]|\bor\b", form.translated))
    return {normalize_name(name) for name in names if name and name != "[ ]"}


class TipnrIndex:
    def __init__(self, persons: Iterable[TipnrPerson]):
        self.persons = list(persons)
        self.by_dstrong: dict[str, list[TipnrPerson]] = defaultdict(list)
        self.by_ref: dict[str, list[TipnrPerson]] = defaultdict(list)
        self.by_name: dict[str, list[tuple[TipnrPerson, set[str]]]] = defaultdict(list)
        for person in self.persons:
            for strong in sorted({f.dstrong for f in person.forms}):
                self.by_dstrong[strong].append(person)
            for ref in sorted(person.refs, key=ref_key):
                self.by_ref[ref].append(person)
            names: dict[str, set[str]] = defaultdict(set)
            for form in person.forms:
                for name in form_names(form):
                    names[name].update(form.refs)
            for name, refs in names.items():
                self.by_name[name].append((person, refs))

    def match_step(self, strong: str, ref: str) -> list[TipnrPerson]:
        codes = [canonical_strong(code) for code in STRONG.findall(strong)]
        exact = {p.unique_name: p for code in codes for p in self.by_dstrong.get(code, [])}
        if exact:
            return sorted(exact.values(), key=lambda p: p.unique_name)
        bases = {base_strong(code) for code in codes}
        return [p for p in self.by_ref.get(ref, []) if any(
            ref in form.refs and base_strong(form.dstrong) in bases for form in p.forms
        )]


def load_tipnr(path: Path = SOURCE) -> TipnrIndex:
    return TipnrIndex(parse_tipnr(Path(path).read_text(encoding="utf-8-sig")))


def load_english_names(path: Path) -> dict[str, set[str]]:
    names: dict[str, set[str]] = defaultdict(set)
    for row in csv.reader(io.StringIO(path.read_text(encoding="utf-8-sig")), delimiter="\t"):
        if len(row) >= 2 and not row[0].startswith("#"):
            names[row[0].strip()].update(n.strip() for n in row[1].split("/") if n.strip())
    return dict(names)


RELATIONS = ("names", "parents", "spouses", "siblings", "kin", "descends")


@dataclass
class PersonMatch:
    person: dict
    references: list[str]
    english: set[str]
    candidates: dict[str, TipnrPerson]
    evidence: dict[str, set[str]]


@dataclass
class Comparison:
    matches: dict[str, PersonMatch]
    a: list[PersonMatch]
    b: dict[str, list[PersonMatch]]
    c: list[PersonMatch]
    d: list[PersonMatch]


def compare_people(persons: list[dict], english_names: dict[str, set[str]], index: TipnrIndex) -> Comparison:
    matches: dict[str, PersonMatch] = {}
    inverse: dict[str, list[PersonMatch]] = defaultdict(list)
    for person in persons:
        references = sorted({row["ref"] for key in RELATIONS for row in person.get(key, []) if row.get("ref")})
        refs: set[str] = set()
        for reference in references:
            try:
                refs.update(parse_chinese_refs(reference))
            except ValueError as exc:
                raise ValueError(f"人物 {person['id']} 引用 {reference!r}：{exc}") from exc
        chinese = {person["name"], *(row["as"] for row in person.get("names", []) if row.get("as"))}
        english = {name for word in chinese for name in english_names.get(word, set())}
        candidates: dict[str, TipnrPerson] = {}
        evidence: dict[str, set[str]] = defaultdict(set)
        for name in sorted({normalize_name(name) for name in english}):
            for candidate, name_refs in index.by_name.get(name, []):
                common = refs & name_refs
                if common:
                    candidates[candidate.unique_name] = candidate
                    evidence[candidate.unique_name].update(common)
        match = PersonMatch(person, references, english, dict(sorted(candidates.items())), dict(evidence))
        if person["id"] in matches:
            raise ValueError(f"重複人物 id：{person['id']}")
        matches[person["id"]] = match
        for unique in candidates:
            inverse[unique].append(match)
    a = [m for m in matches.values() if len(m.candidates) == 1 and len(inverse[next(iter(m.candidates))]) == 1]
    b = {unique: rows for unique, rows in sorted(inverse.items()) if len(rows) > 1}
    c = [m for m in matches.values() if len(m.candidates) > 1]
    d = [m for m in matches.values() if not m.candidates]
    return Comparison(matches, a, b, c, d)


def summarize_refs(refs: Iterable[str], limit: int | None = 16) -> str:
    ordered = sorted(set(refs), key=ref_key)
    shown = ordered if limit is None else ordered[:limit]
    groups: dict[tuple[str, str], list[int]] = defaultdict(list)
    for ref in shown:
        stem, verse = ref.rsplit(".", 1)
        book, chapter = stem.rsplit(".", 1)
        groups[book, chapter].append(int(verse))
    pieces = []
    for (book, chapter), verses in groups.items():
        runs = []
        start = end = verses[0]
        for verse in verses[1:]:
            if verse == end + 1:
                end = verse
            else:
                runs.append(str(start) if start == end else f"{start}-{end}")
                start = end = verse
        runs.append(str(start) if start == end else f"{start}-{end}")
        pieces.append(f"{book}.{chapter}." + ",".join(runs))
    suffix = f"；等共 {len(ordered)} 節" if len(shown) < len(ordered) else ""
    return "; ".join(pieces) + suffix


def tsv(rows: Iterable[Iterable[object]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, delimiter="\t", lineterminator="\n")
    for row in rows:
        writer.writerow(re.sub(r"[\t\r\n]+", " ", str(cell)) for cell in row)
    return buffer.getvalue()


def concordance_tsv(comparison: Comparison) -> str:
    rows = [["人物id", "UniqueName", "dStrong", "描述"]]
    for match in comparison.a:
        person = next(iter(match.candidates.values()))
        rows.append([match.person["id"], person.unique_name,
                     ", ".join(sorted({f.dstrong for f in person.forms})), person.description])
    return ATTRIBUTION + "\n" + tsv(rows)


def reading_tsv(reading: dict, index: TipnrIndex) -> tuple[str, dict[str, int]]:
    rows = [["經節", "序", "translit", "dStrong", "TIPNR UniqueName", "描述", "父母", "兒女",
             "同一節我們標的人物 id（依 s 順序列出）"]]
    stats = {"verses": 0, "words": 0, "unmatched": 0, "multiple": 0, "unidentified_markers": 0}
    for segment in reading["segments"]:
        for chapter in segment["chapters"]:
            book, number = chapter.get("book", segment.get("book")), int(chapter["n"])
            words_by_verse = step_names.load_chapter(book, number)
            for verse in chapter["verses"]:
                v = int(verse["v"])
                if v not in words_by_verse:
                    raise ValueError(f"STEP 缺少讀經經節：{book}{number}:{v}")
                stats["verses"] += 1
                ref = f"{BOOKS[book]}.{number}.{v}"
                markers = sorted((t for t in verse.get("t", []) if t.get("k") == "p"), key=lambda t: t["s"])
                # 部分 p 標記只有字面、沒有 id；只列來源實際提供的 id，不推測。
                stats["unidentified_markers"] += sum(not t.get("id") for t in markers)
                marked_ids = ", ".join(t["id"] for t in markers if t.get("id"))
                for word in step_names.proper_nouns(book, number, v, kinds=step_names.PERSON_KINDS):
                    people = index.match_step(word.strong, ref)
                    stats["words"] += 1
                    stats["unmatched"] += not people
                    stats["multiple"] += len(people) > 1
                    # 序保留 STEP 本節原始詞序，同一人的重複標記不去重。
                    rows.append([f"{book}{number}:{v}", word.index, word.translit, word.strong,
                                 " ; ".join(p.unique_name for p in people),
                                 " ; ".join(p.description for p in people),
                                 " ; ".join(p.parents for p in people),
                                 " ; ".join(p.offspring for p in people), marked_ids])
    return ATTRIBUTION + "\n" + tsv(rows), stats


# E 的別寫來自任務指定查找名，只用於同名名單，不補寫 A–D 的字典。
FOCUS = {
    "耶何耶大": "Jehoiada", "比拿雅": "Benaiah", "撒督": "Zadok", "亞比亞他": "Abiathar",
    "亞希米勒": "Ahimelech", "約拿單": "Jonathan", "亞薩": "Asaph", "希幔": "Heman",
    "耶杜頓": "Jeduthun", "以探": "Ethan", "俄別以東": "Obed-edom", "亞瑪撒": "Amasa/Amasai",
    "以利戶": "Elihu", "押尼珥": "Abner", "雅西業": "Jaasiel", "示每": "Shimei",
    "拉但": "Ladan", "耶利雅": "Jeriah", "哈沙比雅": "Hashabiah", "示利米雅": "Shelemiah/Meshelemiah",
    "米施利米雅": "Meshelemiah", "撒迦利亞": "Zechariah", "耶大雅": "Jedaiah", "哈琳": "Harim",
    "音麥": "Immer", "哈歌斯": "Hakkoz/Koz", "巴西萊": "Barzillai", "沙龍": "Shallum",
    "亞谷": "Akkub", "達們": "Talmon", "亞希突": "Ahitub", "以利亞撒": "Eleazar",
    "朵多": "Dodo/Dodai", "雅朔班": "Jashobeam", "以拉": "Ira", "伊勒哈難": "Elhanan", "沙瑪": "Shammah",
}


def in_focus(ref: str) -> bool:
    if ref.startswith("LXX."):
        return False
    book, chapter, _ = ref.split(".")
    c = int(chapter)
    return ((book == "1Ch" and 10 <= c <= 29) or (book == "2Sa" and c in (8, 20, 23))
            or (book == "Ezr" and c == 2) or (book == "Neh" and c in (7, 11, 12)))


def focus_people(chinese: str, english: str, english_names: dict[str, set[str]], index: TipnrIndex) -> list[TipnrPerson]:
    # 以拉在字典作 Elah，在指定勇士名單作 Ira。E 保留兩個查找名，
    # 再依指定章節篩選；不擅自修改既有中英對照。
    names = english_names.get(chinese, set()) | set(english.split("/"))
    people = {p.unique_name: p for name in names for p, _ in index.by_name.get(normalize_name(name), [])
              if p.sex in ("Male", "Female") and any(in_focus(ref) for ref in p.refs)}
    return sorted(people.values(), key=lambda p: p.unique_name)


def md_cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def comparison_markdown(comparison: Comparison, english_names: dict[str, set[str]], index: TipnrIndex) -> str:
    lines = ["# TIPNR 人物對照", "", "出處：STEP Bible（STEPBible.org），CC BY 4.0，commit bd09545。", "",
             "人物依姓名及所引經節交叉比對；英文別寫忽略大小寫、連字號與空格。"
             "以下列出相符的紀錄，供並讀經文時參考。", "",
             "## A. 一對一", "", f"共 {len(comparison.a)} 人。", "",
             "## B. 多位人物共用同一筆 TIPNR 紀錄", "",
             f"共 {len(comparison.b)} 組，涉及 {len({m.person['id'] for rows in comparison.b.values() for m in rows})} 位人物。", "",
             "每組依 TIPNR 紀錄列出；同一位人物也可能出現在 C。", ""]
    for unique, matches in comparison.b.items():
        person = matches[0].candidates[unique]
        lines.extend([f"### {unique}", "", f"描述：{person.description}", "",
                      f"經節摘要：{summarize_refs(person.refs)}", ""])
        for match in matches:
            lines.append(f"- {match.person['id']}：{'；'.join(match.references)}。相符經節：{summarize_refs(match.evidence[unique], None)}")
        lines.append("")
    lines.extend(["## C. 一位人物對應多筆 TIPNR 紀錄", "", f"共 {len(comparison.c)} 人。", ""])
    for match in comparison.c:
        lines.extend([f"### {match.person['id']}", "", f"所引經節：{'；'.join(match.references)}", ""])
        for unique, person in match.candidates.items():
            lines.extend([f"- {unique}：{person.description}。父母：{person.parents}。",
                          f"  相符經節：{summarize_refs(match.evidence[unique], None)}；經節摘要：{summarize_refs(person.refs)}"])
        lines.append("")
    lines.extend(["## D. 沒有相符紀錄", "", f"共 {len(comparison.d)} 人。前 {min(50, len(comparison.d))} 位：", "",
                  "、".join(m.person["id"] for m in comparison.d[:50]), "",
                  "## E. 同名人物並列", "",
                  "以下按查找名列出曾出現在代上10–29、撒下8／20／23、拉2、尼7／11–12的個人；經節摘要限於這些章。", ""])
    for chinese, english in FOCUS.items():
        people = focus_people(chinese, english, english_names, index)
        lines.extend([f"### {chinese}（{english}）", ""])
        if not people:
            lines.extend(["目前沒有相符人物。", ""])
            continue
        lines.extend(["| UniqueName | 描述 | 父母 | 經節摘要 |", "| --- | --- | --- | --- |"])
        for person in people:
            values = [person.unique_name, person.description, person.parents,
                      summarize_refs((ref for ref in person.refs if in_focus(ref)), None)]
            lines.append("| " + " | ".join(md_cell(v) for v in values) + " |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    index = load_tipnr()
    persons = json.loads((DATA / "genealogy.json").read_text(encoding="utf-8-sig"))["persons"]
    reading = json.loads((DATA / "reading.json").read_text(encoding="utf-8-sig"))
    english = load_english_names(BASE / "亞當到耶穌/名字英文對照.tsv")
    comparison = compare_people(persons, english, index)
    verses, stats = reading_tsv(reading, index)
    # 完成解析與比對後才落地。固定三個輸出，不觸碰來源或網站資料。
    outputs = {
        BASE / "sources/tipnr_對照.tsv": concordance_tsv(comparison),
        DRAFT / "TIPNR_人物對照.md": comparison_markdown(comparison, english, index),
        DRAFT / "TIPNR_經節人名.tsv": verses,
    }
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8", newline="\n")
    print(f"PERSON：{len(index.persons)}；A：{len(comparison.a)} 人；B：{len(comparison.b)} 組；"
          f"C：{len(comparison.c)} 人；D：{len(comparison.d)} 人")
    print(f"讀經：{stats['verses']} 節；STEP 人名：{stats['words']} 詞；"
          f"未匹配：{stats['unmatched']} 詞；多重候選：{stats['multiple']} 詞；"
          f"未附人物 id 的人名標記：{stats['unidentified_markers']} 處")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
