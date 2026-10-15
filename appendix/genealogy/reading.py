"""帶你讀經：把經文逐節標出人名、職稱、親屬詞、地名、數字，給網站的讀經模式用。

由 build_genealogy.py 的 LineageBuilder 呼叫（helpers 由它傳入，避免互相匯入）。
裁決寫在 亞當到耶穌/讀經.yaml；程式先依人物資料自動配對，配不出來或有兩種可能的，
必須在裁決檔寫明，否則建置失敗。
"""
from __future__ import annotations

import itertools
import re
from collections import defaultdict
from pathlib import Path

import yaml

RELATION_FIELDS = ("parents", "spouses", "siblings", "kin", "descends")
RELATION_WORDS = ["兒子", "女兒", "子孫", "後裔", "曾孫", "孫子", "玄孫", "長子", "次子", "三子", "四子", "五子",
                  "六子", "七子", "妹子", "姊妹", "弟兄", "兄弟", "父親", "母親", "妻", "妾", "生"]
# 職稱：(樣式, 說明)。「王」只在緊貼人名或「作王」時算數，避免把「王門」「諸王記」標成職稱。
TITLE_PATTERNS = [
    r"大祭司", r"祭司長", r"祭司", r"族長", r"首領", r"先知", r"先見", r"歌唱的", r"守門的", r"文士", r"窯匠",
    r"大能的勇士", r"勇士", r"千夫長", r"百夫長", r"軍長", r"書記", r"長老", r"君王",
]
STOP_CHARS = set("，。；：、的是和與又並及人生有")
NUM_RE = re.compile(r"(?:共)?[零〇一二三四五六七八九十百千萬兩]+(?=人|名|代|歲|年|個|座|城|家|位)")
CLAUSE_RE = re.compile(r"[，。；：！？]")


def build_reading(builder, helpers: dict) -> dict | None:
    """回傳 reading.json 的內容；錯誤寫進 builder.err。"""
    parse_refs, prefix_book, display, abbr_of = (helpers["parse_refs"], helpers["prefix_book"],
                                                  helpers["display"], helpers["FULL_TO_ABBR"])
    root: Path = helpers["ROOT"]
    path = builder.dir / "讀經.yaml"
    if not path.is_file():
        return None
    where = "讀經.yaml"
    try:
        spec = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        builder.err(where, f"無法讀取：{exc}")
        return None
    abbr, book = str(spec.get("book", "代上")), str(spec.get("book_full", "歷代志上"))
    first, last = [int(x) for x in spec.get("chapters", [1, 9])]
    source = yaml.safe_load((builder.dir / str(spec["genealogy"])).read_text(encoding="utf-8"))
    chapter_titles = {int(k): str(v) for k, v in (source.get("chapters") or {}).items()}

    def key(c: int, v: int) -> str:
        return f"{abbr}{c}:{v}"

    def verses_of(ref: str) -> list[str]:
        try:
            parsed = parse_refs(str(ref), "", builder.sc)
        except ValueError:
            return []
        return [key(c, v) for b, c, v in parsed if b == book and first <= c <= last]

    people = builder.people
    surfaces: dict[str, set[str]] = defaultdict(set)
    for pid, person in people.items():
        surfaces[pid].add(display(pid))
        for name in person.get("names", []) or []:
            if name.get("as"):
                surfaces[pid].add(str(name["as"]))
    # 每一節提到誰：名字的出處（一定要在經文裡找到）和關係的出處（找得到就標）
    named: dict[str, set[str]] = defaultdict(set)
    mentioned: dict[str, set[str]] = defaultdict(set)
    name_ranges: list[tuple[str, str, list[str]]] = []
    for pid, person in people.items():
        for name in person.get("names", []) or []:
            verses = verses_of(str(name.get("ref", "")))
            if verses:
                name_ranges.append((pid, str(name.get("as", "")), verses))
            for k in verses:
                named[k].add(pid)
        for field in RELATION_FIELDS:
            for relation in person.get(field, []) or []:
                for k in verses_of(str(relation.get("ref", ""))):
                    mentioned[k].add(pid)
                    if relation.get("id") in people:
                        mentioned[k].add(str(relation["id"]))
    # 代上族譜資料逐句記的人（同一份名單重複出現時，人物資料只記第一次的出處）
    def statement_ids(statement: dict) -> list[str]:
        ids = []
        for field in ("chain", "children", "roots"):
            for item in statement.get(field, []) or []:
                ids.append(str(item.get("id") if isinstance(item, dict) else item))
        if statement.get("parent"):
            ids.append(str(statement["parent"]))
        return [pid for pid in ids if pid in people]
    for section in source.get("sections", []) or []:
        for statement in section.get("statements", []) or []:
            for k in verses_of(prefix_book(str(statement.get("ref", "")), abbr)):
                mentioned[k].update(statement_ids(statement))
    parents_of: dict[str, set[str]] = defaultdict(set)
    related: dict[str, set[str]] = defaultdict(set)
    for pid, person in people.items():
        for field in ("parents", "descends"):
            for relation in person.get(field, []) or []:
                parents_of[pid].add(str(relation.get("id", "")))
        for field in RELATION_FIELDS:
            for relation in person.get(field, []) or []:
                other = str(relation.get("id", ""))
                if other in people and other != pid:
                    related[pid].add(other)
                    related[other].add(pid)

    # 地名詞庫：知識庫的地點條目＋代上族譜裡的城邑清單＋裁決檔補的
    places: set[str] = set(str(p) for p in spec.get("places", []) or [])
    for entry in (root / "link_folder" / "地點").glob("*.md"):
        base = re.sub(r"（.*?）|\(.*?\)", "", entry.stem).strip()
        if len(base) >= 2:
            places.add(base)
    for section in source.get("sections", []) or []:
        for statement in section.get("statements", []) or []:
            places.update(str(p) for p in statement.get("places", []) or [])
    global_names = set(places)
    for forms in surfaces.values():
        global_names.update(f for f in forms if len(f) >= 2)
    lengths = sorted({len(w) for w in global_names}, reverse=True)

    decisions = spec.get("decide", {}) or {}
    title_of = spec.get("title_of", {}) or {}
    used_decisions: set[tuple[str, str]] = set()
    used_titles: set[tuple[str, str]] = set()

    def inside_longer(text: str, s: int, e: int, exclude: set[str]) -> bool:
        """這段字是不是另一個更長名字的一部分（例如「以利」在「以利加拿」裡）。"""
        for length in lengths:
            if length <= e - s:
                break
            for start in range(max(0, e - length), s + 1):
                word = text[start:start + length]
                if len(word) == length and word in global_names and word not in exclude and start <= s and start + length >= e:
                    return True
        return False

    def occurrences(text: str, word: str) -> list[int]:
        out, i = [], text.find(word)
        while i >= 0:
            out.append(i)
            i = text.find(word, i + 1)
        return out

    sections = []
    for section in source.get("sections", []) or []:
        verses = verses_of(prefix_book(str(section.get("range", "")), abbr))
        sections.append((section, verses))
    section_of = {k: section for section, verses in sections for k in verses}
    section_verses = {str(section.get("title", "")): verses for section, verses in sections}
    hold_by_anchor = {str(item.get("anchor")): f"名單:{item.get('title')}"
                      for item in (builder.placement_data.get("lists", []) or [])}
    notes = []
    note_of: dict[str, int] = {}
    for section, _ in sections:
        for note in section.get("notes", []) or []:
            verses = verses_of(prefix_book(str(note.get("refs", "")), abbr))
            if not verses:
                continue
            notes.append({"text": str(note.get("text", "")).strip(), "verses": verses})
            note_of.setdefault(verses[0], len(notes) - 1)

    chapters = []
    found_names: set[tuple[str, str]] = set()
    review: list[str] = []
    previous_last: tuple[str, str] | None = None
    previous_section = None
    carry: list[str] = []
    for c in range(first, last + 1):
        chapter = {"n": c, "title": chapter_titles.get(c, ""), "verses": []}
        v = 0
        while True:
            v += 1
            text = builder.sc.verse(book, c, v)
            if text is None:
                break
            k = key(c, v)
            builder.refs_used[k] = text
            candidates = named[k] | mentioned[k]
            by_surface: dict[str, set[str]] = defaultdict(set)
            for pid in candidates:
                for form in surfaces[pid]:
                    by_surface[form].add(pid)

            def label(s: int, e: int) -> str:
                """「以利加拿@2」＝這一節第二個「以利加拿」（照經文裡出現的次序數）。"""
                word = text[s:e]
                return f"{word}@{occurrences(text, word).index(s) + 1}"
            # 裁決檔寫明的位置先放；其餘找出候選名字出現的位置，同一處有更長的名字就讓給長的
            verse_decisions = {str(d.get("at")): d for d in decisions.get(k, []) or []}
            forced: dict[tuple[int, int], dict] = {}
            for at, decision in verse_decisions.items():
                word, _, number = at.rpartition("@")
                hits = occurrences(text, word)
                if not word or not number.isdigit() or int(number) > len(hits):
                    continue
                s = hits[int(number) - 1]
                forced[(s, s + len(word))] = decision
                used_decisions.add((k, at))
            spans: dict[tuple[int, int], set[str]] = defaultdict(set)
            for form, pids in by_surface.items():
                for s in occurrences(text, form):
                    if not inside_longer(text, s, s + len(form), set()):
                        spans[(s, s + len(form))].update(pids)
            kept: list[tuple[int, int]] = sorted(forced)
            for span in sorted(spans, key=lambda span: (span[0], -(span[1] - span[0]))):
                if all(span[1] <= a or span[0] >= b for a, b in kept):
                    kept.append(span)
            kept.sort()
            assignment: dict[tuple[int, int], str | None] = {}
            place_spans: set[tuple[int, int]] = set()
            open_spans = []
            for span in kept:
                decision = forced.get(span)
                if decision is not None:
                    if decision.get("place"):
                        assignment[span] = None
                        place_spans.add(span)
                    elif decision.get("skip"):
                        assignment[span] = None
                    else:
                        pid = str(decision.get("id", ""))
                        if pid not in people:
                            builder.err(f"{where}.decide.{k}", f"人物不存在：{pid}")
                        assignment[span] = pid
                elif len(spans[span]) == 1:
                    assignment[span] = next(iter(spans[span]))
                else:
                    open_spans.append(span)
            notes_for_review = []
            if open_spans:
                # 同一節有同名的人：試所有配法，挑「同一句裡父子關係對得上最多」的那一種
                choices = [sorted(spans[span]) for span in open_spans]
                total = 1
                for options in choices:
                    total *= len(options)
                if total > 50000:
                    builder.err(f"{where}.decide", f"{k} 同名太多，請直接裁決：" + "、".join(label(*s) for s in open_spans))
                    continue
                clause_of = {span: len(CLAUSE_RE.findall(text[:span[0]])) for span in kept}

                def score(combo) -> tuple[int, int]:
                    trial = dict(assignment)
                    trial.update(dict(zip(open_spans, combo)))
                    pairs = 0
                    items = [(span, pid) for span, pid in sorted(trial.items()) if pid]
                    for (a, pa), (b, pb) in itertools.combinations(items, 2):
                        if clause_of[a] == clause_of[b] and (pa in parents_of[pb] or pb in parents_of[pa]):
                            pairs += 1
                        # 「X生Y；Y生Z」：前後兩句接著寫的同一個名字是同一個人
                        if clause_of[b] == clause_of[a] + 1 and text[a[0]:a[1]] == text[b[0]:b[1]] and pa == pb:
                            pairs += 1
                    # 上一節最後一個人名，這一節開頭又寫一次，也是同一個人
                    if items and previous_last and text[items[0][0][0]:items[0][0][1]] == previous_last[0] and items[0][1] == previous_last[1]:
                        pairs += 1
                    covered = len({pid for _, pid in items} & named[k])
                    return (pairs, covered)
                scored = sorted(((score(combo), combo) for combo in itertools.product(*choices)), key=lambda item: item[0], reverse=True)
                if len(scored) > 1 and scored[0][0] == scored[1][0]:
                    builder.err(f"{where}.decide", f"{k} 無法自動判斷，請裁決：" + "；".join(
                        f"{label(*s)}＝{'或'.join(choices[i])}" for i, s in enumerate(open_spans)))
                    continue
                for span, pid in zip(open_spans, scored[0][1]):
                    assignment[span] = pid
                notes_for_review.append("自動判斷同名")

            # 這一節沒記到、但同一段經文記到的人；或和這一節已標的人有經文記載關係的人：
            # 名字出現在經文裡、而且只對得上一個人，才標上去
            def add_unique(pool: set[str], why: str) -> bool:
                pool_surface: dict[str, set[str]] = defaultdict(set)
                for pid in pool:
                    for form in surfaces[pid]:
                        if len(form) >= 2:
                            pool_surface[form].add(pid)
                added = False
                for form, pids in sorted(pool_surface.items(), key=lambda item: -len(item[0])):
                    if len(pids) != 1:
                        continue
                    for s in occurrences(text, form):
                        span = (s, s + len(form))
                        if inside_longer(text, s, s + len(form), set()) or not all(span[1] <= a or span[0] >= b for a, b in kept):
                            continue
                        kept.append(span)
                        assignment[span] = next(iter(pids))
                        notes_for_review.append(f"{form}＝{why}")
                        added = True
                return added
            section = section_of.get(k)
            if section is not None:
                pool = set().union(*(named[x] | mentioned[x] for x in section_verses[str(section.get("title", ""))]))
                add_unique(pool - candidates, "同段")
            for _ in range(3):
                linked = {pid for pid in assignment.values() if pid}
                pool = set().union(*(related[pid] for pid in linked)) if linked else set()
                if not add_unique(pool - linked, "有關係"):
                    break
            kept.sort()
            tokens = []
            taken = []
            for span in kept:
                pid = assignment.get(span)
                tokens.append({"s": span[0], "e": span[1], "k": "l"} if span in place_spans
                              else {"s": span[0], "e": span[1], "k": "p", **({"id": pid} if pid else {})})
                taken.append(span)
                if pid:
                    found_names.add((pid, k))
            # 經文裡的名字，但不是資料裡的人物（例如迦勒的妻子以法他）：只在經文裡亮
            for word in (spec.get("names", {}) or {}).get(k, []) or []:
                hits = [s for s in occurrences(text, str(word)) if all(s + len(str(word)) <= a or s >= b for a, b in taken)]
                if not hits:
                    builder.err(f"{where}.names.{k}", f"這一節沒有這個名字：{word}")
                for s in hits:
                    tokens.append({"s": s, "e": s + len(str(word)), "k": "p"})
                    taken.append((s, s + len(str(word))))
            auto_note = f"（{'；'.join(notes_for_review)}）" if notes_for_review else ""

            def free(s: int, e: int) -> bool:
                return all(e <= a or s >= b for a, b in taken)
            # 職稱、親屬詞、數字、地名
            for pattern in TITLE_PATTERNS:
                for match in re.finditer(pattern, text):
                    if free(match.start(), match.end()):
                        tokens.append({"s": match.start(), "e": match.end(), "k": "t"})
                        taken.append((match.start(), match.end()))
            # 「某地之祖」：往前收到標點、「的」或別的標記為止，最多五個字
            for i in occurrences(text, "之祖"):
                j = i
                while j > 0 and i - j < 5 and text[j - 1] not in STOP_CHARS and free(j - 1, j):
                    j -= 1
                if j < i and free(j, i + 2):
                    tokens.append({"s": j, "e": i + 2, "k": "t"})
                    taken.append((j, i + 2))
            for match in re.finditer("王", text):
                s, e = match.start(), match.end()
                adjacent = any(t["k"] == "p" and (t["s"] == e or t["e"] == s) for t in tokens) or text[max(0, s - 1):s] == "作"
                if adjacent and free(s, e):
                    tokens.append({"s": s, "e": e, "k": "t"})
                    taken.append((s, e))
            for match in NUM_RE.finditer(text):
                if free(match.start(), match.end()):
                    tokens.append({"s": match.start(), "e": match.end(), "k": "n"})
                    taken.append((match.start(), match.end()))
            for word in sorted(places, key=len, reverse=True):
                for s in occurrences(text, word):
                    if free(s, s + len(word)):
                        tokens.append({"s": s, "e": s + len(word), "k": "l"})
                        taken.append((s, s + len(word)))
            for word in RELATION_WORDS:
                for s in occurrences(text, word):
                    if free(s, s + len(word)):
                        tokens.append({"s": s, "e": s + len(word), "k": "r"})
                        taken.append((s, s + len(word)))
            tokens.sort(key=lambda t: t["s"])
            persons = [t for t in tokens if t["k"] == "p" and t.get("id")]
            # 墨線：排在他前面、經文記載是他父母或祖先的人（一句話跨到下一節時，上一節的人也算）
            if section_of.get(k) is None or previous_section != section_of.get(k).get("title"):
                carry = []
            for index, token in enumerate(persons):
                earlier = carry + [other["id"] for other in persons[:index]]
                sources = [pid for pid in earlier if pid in parents_of[token["id"]]]
                if sources:
                    token["from"] = list(dict.fromkeys(sources))
                # 倒著往上數的家譜（「希幔是約珥的兒子」）：讀到父親時，畫到前面已經讀過的兒子
                children = [pid for pid in earlier if token["id"] in parents_of[pid] and pid not in sources]
                if children:
                    token["to"] = list(dict.fromkeys(children))
            # 職稱屬於誰：裁決檔寫明的優先；否則緊貼在後的人名，再來是同一句前面最近的人
            manual = {str(word): str(pid) for word, pid in (title_of.get(k) or {}).items()}
            for token in tokens:
                if token["k"] != "t":
                    continue
                word = text[token["s"]:token["e"]]
                # 裁決可以寫「族長」（這一節每個「族長」）或「族長@2」（第二個）
                keyed = f"{word}@{occurrences(text, word).index(token['s']) + 1}"
                chosen = keyed if keyed in manual else word if word in manual else None
                if chosen:
                    used_titles.add((k, chosen))
                    if manual[chosen] == "-":
                        continue
                    if manual[chosen] not in people:
                        builder.err(f"{where}.title_of.{k}", f"人物不存在：{manual[chosen]}")
                    else:
                        token["of"] = manual[chosen]
                    continue
                clause = len(CLAUSE_RE.findall(text[:token["s"]]))
                after = next((p for p in persons if p["s"] == token["e"]), None)
                before = [p for p in persons if p["e"] <= token["s"] and len(CLAUSE_RE.findall(text[:p["s"]])) == clause]
                owner = after or (before[-1] if before else None)
                if owner:
                    token["of"] = owner["id"]
            row = {"v": v, "text": text, "t": tokens}
            section = section_of.get(k)
            if section is not None:
                row["sec"] = str(section.get("title", ""))
                hold = hold_by_anchor.get(str(section.get("title", "")))
                if hold:
                    row["hold"] = hold
            if k in note_of:
                row["note"] = note_of[k]
            chapter["verses"].append(row)
            review.append(f"{k} {annotate(text, tokens, display)}{auto_note}")
            if persons:
                previous_last = (text[persons[-1]["s"]:persons[-1]["e"]], persons[-1]["id"])
            continues = not re.search(r"[。！？）]\s*$", text)
            carry = (carry + [p["id"] for p in persons]) if continues else []
            previous_section = section.get("title") if section is not None else None
        chapters.append(chapter)

    for pid, form, verses in name_ranges:
        if not any((pid, k) in found_names for k in verses):
            builder.err(where, f"{display(pid)}（{pid}）的名字「{form}」在 {verses[0]}{'…' if len(verses) > 1 else ''} 沒有對上經文")
    for k, items in decisions.items():
        for item in items or []:
            if (str(k), str(item.get("at"))) not in used_decisions:
                builder.err(f"{where}.decide.{k}", f"找不到要裁決的位置：{item.get('at')}")
    for k, words in title_of.items():
        for word in words or {}:
            if (str(k), str(word)) not in used_titles:
                builder.err(f"{where}.title_of.{k}", f"這一節沒有這個職稱：{word}")
    count = sum(len(chapter["verses"]) for chapter in chapters)
    expected = int(spec.get("verse_count", 0) or 0)
    if expected and count != expected:
        builder.err(where, f"應有 {expected} 節，實際 {count} 節")
    builder.reading_review = review
    return {"book": abbr, "bookName": book, "chapters": chapters, "notes": notes}


def annotate(text: str, tokens: list[dict], display) -> str:
    out, at = [], 0
    for token in tokens:
        out.append(text[at:token["s"]])
        word = text[token["s"]:token["e"]]
        if token["k"] == "p":
            tag = token.get("id", "？")
            tag = word if tag == word else f"{word}={tag}"
            if token.get("from"):
                tag += "←" + "/".join(display(x) for x in token["from"])
            if token.get("to"):
                tag += "→" + "/".join(display(x) for x in token["to"])
            out.append(f"〔{tag}〕")
        elif token["k"] == "t":
            out.append(f"《{word}→{display(token['of']) if token.get('of') else '？'}》")
        elif token["k"] == "l":
            out.append(f"⟨{word}⟩")
        elif token["k"] == "n":
            out.append(f"#{word}#")
        else:
            out.append(f"_{word}_")
        at = token["e"]
    out.append(text[at:])
    return "".join(out)
