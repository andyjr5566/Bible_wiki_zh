"""帶你讀經：把讀經路線上的經文逐節標出人名、職稱、親屬詞、地名、數字，給網站的讀經模式用。

由 build_genealogy.py 的 LineageBuilder 呼叫（helpers 由它傳入，避免互相匯入）。
- 路線寫在 亞當到耶穌/讀經路線.yaml（一串段落，從創 4:17 讀到路 3:38）。
- 裁決寫在 亞當到耶穌/讀經.yaml（代上 1–9）和 亞當到耶穌/讀經/*.yaml（其餘段落）。
- 大衛立的職位寫在 亞當到耶穌/職位.yaml；平行經文差異小卡寫在 差異.yaml；歸回的家族連回祖先寫在 歸回.yaml。
程式先依人物資料自動配對，配不出來或有兩種可能的，必須在裁決檔寫明，否則建置失敗。
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
# 兩個人名中間的字，寫明前一位是後一位的父親或母親
STATED_FORWARD = re.compile(r"(的?(兒子|女兒|長子|次子|三子|四子|五子|六子|七子)(原?是|名叫)?|(又)?生(了)?(長子)?|所生的(兒子|長子)是?)")
# 「後一位是前一位的兒子」的後半
STATED_BACKWARD = re.compile(r"的(兒子|女兒|長子|次子)")
ROLE_PREFIX = "r:"
STAGES = ("tree", "roles", "roster", "wall")


def load_yaml(path: Path, builder, where: str, default):
    if not path.is_file():
        return default
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        builder.err(where, f"無法讀取：{exc}")
        return default
    return default if value is None else value


def range_label(ranges: str) -> str:
    """「創29:31-30:24, 創35:16-18」→「創 29:31–30:24、35:16–18」（讀者看的經文範圍）。"""
    out, last_book = [], None
    for part in re.split(r"[,，;；]\s*", str(ranges).strip()):
        m = re.match(r"^([^\d\s]+)\s*(.*)$", part)
        if not m:
            continue
        book, rest = m.group(1), m.group(2).replace("-", "–")
        out.append(rest if book == last_book else f"{book} {rest}")
        last_book = book
    return "、".join(out)


def build_reading(builder, helpers: dict) -> dict | None:
    """回傳 reading.json 的內容；錯誤寫進 builder.err。"""
    parse_refs, prefix_book, display, abbr_of = (helpers["parse_refs"], helpers["prefix_book"],
                                                  helpers["display"], helpers["FULL_TO_ABBR"])
    root: Path = helpers["ROOT"]
    path = builder.dir / "讀經.yaml"
    if not path.is_file():
        return None
    where = "讀經.yaml"
    spec = load_yaml(path, builder, where, {})
    chr_abbr, chr_book = str(spec.get("book", "代上")), str(spec.get("book_full", "歷代志上"))
    chr_first, chr_last = [int(x) for x in spec.get("chapters", [1, 9])]
    source = yaml.safe_load((builder.dir / str(spec["genealogy"])).read_text(encoding="utf-8"))
    chapter_titles = {int(k): str(v) for k, v in (source.get("chapters") or {}).items()}

    # ── 裁決：讀經.yaml＋讀經/*.yaml 合併（經節都帶書卷簡稱，不會互相蓋掉） ──
    decisions: dict[str, list] = {}
    title_of: dict[str, dict] = {}
    names_of: dict[str, list] = {}
    places: set[str] = set()
    decision_files = [(where, spec)] + [(f"讀經/{p.name}", load_yaml(p, builder, f"讀經/{p.name}", {}))
                                         for p in sorted((builder.dir / "讀經").glob("*.yaml"))]
    for file_where, data in decision_files:
        places.update(str(p) for p in data.get("places", []) or [])
        for field, target in (("decide", decisions), ("title_of", title_of), ("names", names_of)):
            for k, value in (data.get(field, {}) or {}).items():
                if str(k) in target:
                    builder.err(f"{file_where}.{field}", f"{k} 在兩個裁決檔都有寫")
                target[str(k)] = value

    # ── 路線 ──
    route_spec = load_yaml(builder.dir / "讀經路線.yaml", builder, "讀經路線.yaml", None)
    if route_spec is None:
        route_spec = {"start": f"{chr_abbr}{chr_first}:1", "segments": [
            {"id": "chr1-9", "title": "歷代志上的族譜", "group": "歷代志上的族譜",
             "ranges": f"{chr_abbr}{chr_first}:1-{chr_last}:{len(builder.sc.chapter(chr_book, chr_last))}",
             "stage": "tree", "chronicles": True}]}

    def key(book: str, c: int, v: int) -> str:
        return f"{abbr_of.get(book, book)}{c}:{v}"

    def verses_of(ref: str) -> list[str]:
        """經節字串 → 經節 key（不限路線範圍）。"""
        try:
            parsed = parse_refs(str(ref), "", builder.sc)
        except ValueError:
            return []
        return [key(b, c, v) for b, c, v in parsed]

    segments_in: list[tuple[dict, list[tuple[str, int, int]]]] = []
    for index, segment in enumerate(route_spec.get("segments", []) or []):
        seg_where = f"讀經路線.yaml.segments[{index}]"
        try:
            parsed = parse_refs(str(segment.get("ranges", "")), "", builder.sc)
        except ValueError as exc:
            builder.err(seg_where, str(exc))
            continue
        if not parsed:
            builder.err(seg_where, "經文範圍是空的")
            continue
        if segment.get("stage") not in STAGES:
            builder.err(seg_where, f"stage 必須是 {'／'.join(STAGES)}")
        for field in ("id", "title", "group"):
            if not segment.get(field):
                builder.err(seg_where, f"{field} 不能空白")
        segments_in.append((segment, parsed))
    route_order: list[str] = [key(*item) for _, parsed in segments_in for item in parsed]
    route_keys = set(route_order)
    if len(route_keys) != len(route_order):
        builder.err("讀經路線.yaml", "有經節在路線上出現兩次")
    start = str(route_spec.get("start", ""))
    if route_order and start not in route_keys:
        builder.err("讀經路線.yaml.start", f"起點不在路線上：{start}")
    stage_override: dict[str, str] = {}
    for segment, _ in segments_in:
        for ref, stage in (segment.get("stages", {}) or {}).items():
            if stage not in STAGES:
                builder.err(f"讀經路線.yaml.{segment.get('id')}.stages", f"{ref}：stage 必須是 {'／'.join(STAGES)}")
            for k in verses_of(str(ref)):
                if k not in route_keys:
                    builder.err(f"讀經路線.yaml.{segment.get('id')}.stages", f"{k} 不在路線上")
                stage_override[k] = str(stage)

    # ── 大衛立的職位：只在職位圖上的人也是候選人（內部用 r: 開頭，和家譜樹人物分開） ──
    roles = getattr(builder, "roles_data", None) or {}
    role_people = {str(item.get("rid")): item for item in roles.get("people", []) or []}
    people = builder.people
    surfaces: dict[str, set[str]] = defaultdict(set)
    for pid, person in people.items():
        surfaces[pid].add(display(pid))
        for name in person.get("names", []) or []:
            if name.get("as"):
                surfaces[pid].add(str(name["as"]))
    for rid, item in role_people.items():
        surfaces[ROLE_PREFIX + rid].add(str(item.get("name", display(rid))))
        for alias in item.get("aliases", []) or []:
            surfaces[ROLE_PREFIX + rid].add(str(alias))

    def known(pid: str) -> bool:
        return pid in people or (pid.startswith(ROLE_PREFIX) and pid[len(ROLE_PREFIX):] in role_people)

    # 每一節提到誰：名字的出處（一定要在經文裡找到）和關係的出處（找得到就標）
    named: dict[str, set[str]] = defaultdict(set)
    mentioned: dict[str, set[str]] = defaultdict(set)
    name_ranges: list[tuple[str, str, list[str]]] = []
    for pid, person in people.items():
        for name in person.get("names", []) or []:
            verses = verses_of(str(name.get("ref", "")))
            in_route = [k for k in verses if k in route_keys]
            if in_route:
                name_ranges.append((pid, str(name.get("as", "")), in_route))
            for k in verses:
                named[k].add(pid)
        for field in RELATION_FIELDS:
            for relation in person.get(field, []) or []:
                for k in verses_of(str(relation.get("ref", ""))):
                    mentioned[k].add(pid)
                    if relation.get("id") in people:
                        mentioned[k].add(str(relation["id"]))
    # 職位圖的成員：成員出處那幾節就是他的名字出處
    for category in roles.get("categories", []) or []:
        for box in category.get("boxes", []) or []:
            for member in box.get("members", []) or []:
                pid = (ROLE_PREFIX + str(member["rid"])) if member.get("rid") else str(member.get("id", ""))
                if not known(pid):
                    continue
                verses = verses_of(str(member.get("ref", "")))
                in_route = [k for k in verses if k in route_keys]
                if in_route and member.get("rid"):
                    name_ranges.append((pid, str(member.get("name", "")), in_route))
                for k in verses:
                    named[k].add(pid)

    # 代上族譜資料逐句記的人（同一份名單重複出現時，人物資料只記第一次的出處）
    def statement_ids(statement: dict) -> list[str]:
        ids = []
        for field in ("chain", "children", "roots"):
            for item in statement.get(field, []) or []:
                ids.append(str(item.get("id") if isinstance(item, dict) else item))
        if statement.get("parent"):
            ids.append(str(statement["parent"]))
        return [pid for pid in ids if pid in people]
    # 族譜逐句記的父子（「甲生乙」的鏈、某人的兒女）：記在這一句的經節，墨線就可以在那裡畫
    statement_pairs: list[tuple[str, str, list[str]]] = []
    for section in source.get("sections", []) or []:
        for statement in section.get("statements", []) or []:
            keys = verses_of(prefix_book(str(statement.get("ref", "")), chr_abbr))
            for k in keys:
                mentioned[k].update(statement_ids(statement))
            chain = [str(item.get("id") if isinstance(item, dict) else item) for item in statement.get("chain", []) or []]
            for parent, child in zip(chain, chain[1:]):
                statement_pairs.append((child, parent, keys))
            if statement.get("parent"):
                for item in statement.get("children", []) or []:
                    statement_pairs.append((str(item.get("id") if isinstance(item, dict) else item), str(statement["parent"]), keys))
    parents_of: dict[str, set[str]] = defaultdict(set)
    relation_verses: dict[tuple[str, str], set[str]] = defaultdict(set)
    related: dict[str, set[str]] = defaultdict(set)
    for pid, person in people.items():
        for field in ("parents", "descends"):
            for relation in person.get(field, []) or []:
                parents_of[pid].add(str(relation.get("id", "")))
                # 這條父子／後代關係記在哪幾節：墨線只畫這一節（或同一句話）經文本身寫明的關係
                for vk in verses_of(str(relation.get("ref", ""))):
                    relation_verses[(pid, str(relation.get("id", "")))].add(vk)
        for field in RELATION_FIELDS:
            for relation in person.get(field, []) or []:
                other = str(relation.get("id", ""))
                if other in people and other != pid:
                    related[pid].add(other)
                    related[other].add(pid)
    for child, parent, keys in statement_pairs:
        if child in people and parent in people and parent in parents_of[child]:
            relation_verses[(child, parent)].update(keys)

    # 地名詞庫：知識庫的地點條目＋代上族譜裡的城邑清單＋裁決檔補的
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

    used_decisions: set[tuple[str, str]] = set()
    used_titles: set[tuple[str, str]] = set()
    used_names: set[str] = set()

    def inside_longer(text: str, s: int, e: int, exclude: set[str]) -> bool:
        """這段字是不是另一個更長名字的一部分（例如「以利」在「以利加拿」裡）。"""
        for length in lengths:
            if length <= e - s:
                break
            for begin in range(max(0, e - length), s + 1):
                word = text[begin:begin + length]
                if len(word) == length and word in global_names and word not in exclude and begin <= s and begin + length >= e:
                    return True
        return False

    def occurrences(text: str, word: str) -> list[int]:
        out, i = [], text.find(word)
        while i >= 0:
            out.append(i)
            i = text.find(word, i + 1)
        return out

    # ── 代上 1–9：附錄的小段、讀經提醒、名單牌子 ──
    chr_sections = []
    for section in source.get("sections", []) or []:
        verses = verses_of(prefix_book(str(section.get("range", "")), chr_abbr))
        chr_sections.append((section, verses))
    section_of = {k: section for section, verses in chr_sections for k in verses}
    section_verses = {str(section.get("title", "")): verses for section, verses in chr_sections}
    hold_by_anchor = {str(item.get("anchor")): f"名單:{item.get('title')}"
                      for item in (builder.placement_data.get("lists", []) or [])}
    notes = []
    note_of: dict[str, int] = {}
    for section, _ in chr_sections:
        for note in section.get("notes", []) or []:
            verses = verses_of(prefix_book(str(note.get("refs", "")), chr_abbr))
            if not verses:
                continue
            # 讀經提醒也會提到別卷的經節（例如創 10:23），那幾節的經文一併收進網站
            for k in verses:
                found = parse_refs(k, "", builder.sc)
                text = builder.sc.verse(*found[0]) if found else None
                if text is not None:
                    builder.refs_used[k] = text
            notes.append({"text": str(note.get("text", "")).strip(), "verses": verses})
            note_of.setdefault(verses[0], len(notes) - 1)

    # ── 職位圖的方塊：沒有人名的節，鏡頭停在這一節所屬的方塊 ──
    box_of: dict[str, str] = {}
    for category in roles.get("categories", []) or []:
        for box in category.get("boxes", []) or []:
            for k in verses_of(str(box.get("verses", "") or "")):
                box_of.setdefault(k, str(box.get("id")))

    # ── 平行經文差異小卡 ──
    diffs_spec = load_yaml(builder.dir / "差異.yaml", builder, "差異.yaml", []) or []
    diffs = []
    diff_of: dict[str, list[int]] = defaultdict(list)
    for index, item in enumerate(diffs_spec):
        d_where = f"差異.yaml[{index}]"
        sides = []
        for side in item.get("sides", []) or []:
            ref, text = str(side.get("ref", "")), str(side.get("text", ""))
            joined = "".join(builder.sc.verse(*p) or "" for p in parse_refs(ref, "", builder.sc)) if ref else ""
            if not text or text not in joined:
                builder.err(d_where, f"{ref} 的經文裡沒有「{text}」")
            for k in verses_of(ref):
                builder.refs_used[k] = builder.sc.verse(*parse_refs(k, "", builder.sc)[0]) or ""
            sides.append({"ref": ref, "text": text})
        if len(sides) < 2 or not item.get("title"):
            builder.err(d_where, "至少要兩處寫法和一個標題")
        at_keys = verses_of(str(item.get("at", "")))
        if not at_keys or any(k not in route_keys for k in at_keys):
            builder.err(d_where, f"出現的位置不在路線上：{item.get('at')}")
        diffs.append({"title": str(item.get("title", "")), "sides": sides})
        for k in at_keys:
            diff_of[k].append(len(diffs) - 1)

    # ── 歸回的家族連回祖先 ──
    links_spec = load_yaml(builder.dir / "歸回.yaml", builder, "歸回.yaml", {}) or {}
    role_members = {(str(box.get("id")), str(member.get("key"))) for category in roles.get("categories", []) or []
                    for box in category.get("boxes", []) or [] for member in box.get("members", []) or []}
    role_boxes = {str(box.get("id")) for category in roles.get("categories", []) or [] for box in category.get("boxes", []) or []}
    links = []
    links_at: dict[str, list[tuple[str, int]]] = defaultdict(list)
    check_basis = helpers.get("check_basis")
    for index, item in enumerate(links_spec.get("links", []) or []):
        l_where = f"歸回.yaml.links[{index}]"
        at = str(item.get("at", ""))
        if at not in route_keys:
            builder.err(l_where, f"位置不在路線上：{at}")
        targets = []
        for target in item.get("to", []) or []:
            if target.get("tree") and str(target["tree"]) not in people:
                builder.err(l_where, f"家譜樹上沒有這個人：{target['tree']}")
            if target.get("role") and (str(target["role"]) not in role_boxes or (
                    target.get("member") and (str(target["role"]), str(target["member"])) not in role_members)):
                builder.err(l_where, f"職位圖上沒有：{target.get('role')} {target.get('member', '')}")
            targets.append({k: str(v) for k, v in target.items() if k in ("tree", "role", "member")})
        if item.get("effect") not in ("returned", "lost", "link", "town"):
            builder.err(l_where, "effect 必須是 returned／lost／link／town")
        if check_basis:
            for message in check_basis(item.get("basis"), l_where, root):
                builder.err(l_where, message)
        refs = [str(r) for r in item.get("refs", []) or []]
        # 小卡裡「」內的字必須逐字出現在 refs 的某一節經文
        ref_texts = [builder.sc.verse(*p) or "" for ref in refs for p in (parse_refs(ref, "", builder.sc) if verses_of(ref) else [])]
        for quote in re.findall(r"「([^「」]+)」", str(item.get("card", ""))):
            if not any(quote in verse_text for verse_text in ref_texts):
                builder.err(l_where, f"小卡的引句不在 refs 的經文裡：「{quote}」")
        for ref in refs:
            if not verses_of(ref):
                builder.err(l_where, f"經節格式錯誤：{ref}")
            for k in verses_of(ref):
                found = parse_refs(k, "", builder.sc)
                text = builder.sc.verse(*found[0]) if found else None
                if text is None:
                    builder.err(l_where, f"經節不存在：{k}")
                else:
                    builder.refs_used[k] = text
        # 子母畫面標題裡的名字（「伯利恆之祖薩瑪」）：必須逐字出現在 refs 的經文裡
        if item.get("pip") and not any(str(item["pip"]) in verse_text for verse_text in ref_texts):
            builder.err(l_where, f"pip 不在 refs 的經文裡：{item['pip']}")
        links.append({"at": at, "word": str(item.get("word", "")), "to": targets, "effect": str(item.get("effect", "")),
                      **({"card": str(item["card"]).strip()} if item.get("card") else {}), "refs": refs,
                      **({"pip": str(item["pip"])} if item.get("pip") else {})})
        links_at[at].append((str(item.get("word", "")), len(links) - 1))

    segments_out = []
    found_names: set[tuple[str, str]] = set()
    review: list[str] = []
    for segment, parsed in segments_in:
        chronicles = bool(segment.get("chronicles"))
        seg_keys = [key(*item) for item in parsed]
        seg_pool_keys = seg_keys + [k for ref in [segment.get("parallel")] if ref for k in verses_of(str(ref))]
        # 職位章同名的人很多，「同段自動配」容易配錯：auto_pool: false 的段只用 people 明列的人
        seg_pool = set()
        if segment.get("auto_pool", True) and seg_pool_keys:
            seg_pool = set().union(*(named[x] | mentioned[x] for x in seg_pool_keys))
        # 這一段反覆提到、但出處記在別卷的人（例如職位章裡的大衛、約押）：名字只對得上一個人才標
        for pid in segment.get("people", []) or []:
            if str(pid) not in people:
                builder.err(f"讀經路線.yaml.{segment.get('id')}.people", f"人物不存在：{pid}")
            seg_pool.add(str(pid))
        seg_stage = str(segment.get("stage", "tree"))
        chapters: list[dict] = []
        previous_last: tuple[str, str] | None = None
        previous_section = None
        previous_key: tuple[str, int, int] | None = None
        carry: list[str] = []
        carry_keys: list[str] = []
        for book, c, v in parsed:
            k = key(book, c, v)
            abbr = abbr_of.get(book, book)
            if not chapters or chapters[-1]["book"] != abbr or chapters[-1]["n"] != c:
                title = chapter_titles.get(c, "") if chronicles and book == chr_book else str(segment.get("title", ""))
                chapters.append({"book": abbr, "bookName": book, "n": c, "title": title, "verses": []})
            # 不相連的兩段之間，句子不會接下去
            if previous_key is None or previous_key[:2] != (book, c) or previous_key[2] + 1 != v:
                if not (previous_key and previous_key[0] == book and previous_key[1] + 1 == c and v == 1):
                    carry, carry_keys = [], []
            previous_key = (book, c, v)
            text = builder.sc.verse(book, c, v)
            if text is None:
                builder.err("讀經路線.yaml", f"經節不存在：{k}")
                continue
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
            # 歸回連結指到的家族名，也是裁決過的位置
            link_spans: dict[tuple[int, int], int] = {}
            for at, link_index in links_at.get(k, []):
                word, _, number = at.rpartition("@")
                hits = occurrences(text, word)
                if not word or not number.isdigit() or int(number) > len(hits):
                    builder.err(f"歸回.yaml.links[{link_index}]", f"{k} 找不到「{at}」")
                    continue
                s = hits[int(number) - 1]
                link_spans[(s, s + len(word))] = link_index
                if (s, s + len(word)) not in forced:
                    forced[(s, s + len(word))] = {"link": link_index}
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
                    elif "link" in decision and links[decision["link"]]["effect"] == "town":
                        # 家譜裡記過的城（伯利恆人）：照樣是地名，只帶著連結
                        assignment[span] = None
                        place_spans.add(span)
                    elif "link" in decision:
                        # 歸回連結指到家譜樹上的祖先（亞薩、沙龍、所羅門……）：名字同時連到那個人
                        tree = [t["tree"] for t in links[decision["link"]]["to"] if t.get("tree")]
                        assignment[span] = tree[0] if len(tree) == 1 else None
                    elif decision.get("skip"):
                        assignment[span] = None
                    else:
                        pid = str(decision.get("rid") and ROLE_PREFIX + str(decision["rid"]) or decision.get("id", ""))
                        if not known(pid):
                            builder.err(f"讀經.decide.{k}", f"人物不存在：{pid}")
                        elif text[span[0]:span[1]] not in surfaces[pid]:
                            # 裁決只能指定「名字對得上」的人；寫法不同的要先在人物資料加 names 別名（附出處）
                            builder.err(f"讀經.decide.{k}", f"「{text[span[0]:span[1]]}」不是 {pid} 的名字或別名")
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
                    builder.err("讀經.decide", f"{k} 同名太多，請直接裁決：" + "、".join(label(*s) for s in open_spans))
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
                    builder.err("讀經.decide", f"{k} 無法自動判斷，請裁決：" + "；".join(
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
            section = section_of.get(k) if chronicles else None
            if section is not None:
                pool = set().union(*(named[x] | mentioned[x] for x in section_verses[str(section.get("title", ""))]))
                add_unique(pool - candidates, "同段")
            elif not chronicles:
                add_unique(seg_pool - candidates, "同段")
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
                if span in place_spans:
                    token = {"s": span[0], "e": span[1], "k": "l"}
                    if span in link_spans:
                        token["link"] = link_spans[span]
                else:
                    token = {"s": span[0], "e": span[1], "k": "p"}
                    if pid and pid.startswith(ROLE_PREFIX):
                        token["rid"] = pid[len(ROLE_PREFIX):]
                    elif pid:
                        token["id"] = pid
                    if span in link_spans:
                        token["link"] = link_spans[span]
                tokens.append(token)
                taken.append(span)
                if pid:
                    found_names.add((pid, k))
            # 經文裡的名字，但不是資料裡的人物（例如迦勒的妻子以法他）：只在經文裡亮
            for word in names_of.get(k, []) or []:
                used_names.add(k)
                hits = [s for s in occurrences(text, str(word)) if all(s + len(str(word)) <= a or s >= b for a, b in taken)]
                if not hits:
                    builder.err(f"讀經.names.{k}", f"這一節沒有這個名字：{word}")
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
            if chronicles and (section_of.get(k) is None or previous_section != section_of.get(k).get("title")):
                carry = []
                carry_keys = []
            for index, token in enumerate(persons):
                earlier = carry + [other["id"] for other in persons[:index]]
                sentence = set(carry_keys) | {k}
                sources = [pid for pid in earlier if pid in parents_of[token["id"]] and relation_verses[(token["id"], pid)] & sentence]
                children = [pid for pid in earlier if token["id"] in parents_of[pid] and pid not in sources and relation_verses[(pid, token["id"])] & sentence]
                # 這一節字面上就寫明的父子（「比珥的兒子比拉」「亞伯拉罕生以撒」「西番雅是他哈的兒子」），
                # 資料把關係記在別卷經文時也算
                if index:
                    before = persons[index - 1]
                    between = text[before["e"]:token["s"]]
                    after = text[token["e"]:token["e"] + 4]
                    if STATED_FORWARD.fullmatch(between) and before["id"] in parents_of[token["id"]] and before["id"] not in sources:
                        sources.append(before["id"])
                    if between == "是" and STATED_BACKWARD.match(after) and token["id"] in parents_of[before["id"]] and before["id"] not in children:
                        children.append(before["id"])
                if sources:
                    token["from"] = list(dict.fromkeys(sources))
                # 倒著往上數的家譜（「希幔是約珥的兒子」）：讀到父親時，畫到前面已經讀過的兒子
                if children:
                    token["to"] = list(dict.fromkeys(children))
            # 職稱屬於誰：裁決檔寫明的優先；否則緊貼在後的人名，再來是同一句前面最近的人
            manual = {str(word): str(pid) for word, pid in (title_of.get(k) or {}).items()}
            owners = [t for t in tokens if t["k"] == "p" and (t.get("id") or t.get("rid"))]
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
                    target = manual[chosen]
                    if target in people or target in role_people:
                        token["of"] = target
                    else:
                        builder.err(f"讀經.title_of.{k}", f"人物不存在：{target}")
                    continue
                clause = len(CLAUSE_RE.findall(text[:token["s"]]))
                after = next((p for p in owners if p["s"] == token["e"]), None)
                before = [p for p in owners if p["e"] <= token["s"] and len(CLAUSE_RE.findall(text[:p["s"]])) == clause]
                owner = after or (before[-1] if before else None)
                if owner:
                    token["of"] = owner.get("id") or owner.get("rid")
            row = {"v": v, "text": text, "t": tokens}
            stage = stage_override.get(k, seg_stage)
            if stage != seg_stage:
                row["stage"] = stage
            if chronicles:
                section = section_of.get(k)
                if section is not None:
                    row["sec"] = str(section.get("title", ""))
                    hold = hold_by_anchor.get(str(section.get("title", "")))
                    if hold:
                        row["hold"] = hold
                if k in note_of:
                    row["note"] = note_of[k]
            if k in diff_of:
                row["diff"] = diff_of[k]
            if k in box_of:
                row["box"] = box_of[k]
            chapters[-1]["verses"].append(row)
            review.append(f"{k} {annotate(text, tokens, display)}{auto_note}")
            if persons:
                previous_last = (text[persons[-1]["s"]:persons[-1]["e"]], persons[-1]["id"])
            continues = not re.search(r"[。！？）]\s*$", text)
            carry = (carry + [p["id"] for p in persons]) if continues else []
            carry_keys = (carry_keys + [k]) if continues else []
            previous_section = section_of.get(k).get("title") if chronicles and section_of.get(k) is not None else None
        segments_out.append({"id": str(segment.get("id")), "title": str(segment.get("title")), "group": str(segment.get("group")),
                             "range": range_label(str(segment.get("ranges", ""))), "stage": seg_stage, "chapters": chapters})
        if chronicles:
            count = sum(len(chapter["verses"]) for chapter in chapters)
            expected = int(spec.get("verse_count", 0) or 0)
            if expected and count != expected:
                builder.err(where, f"應有 {expected} 節，實際 {count} 節")

    for pid, form, verses in name_ranges:
        if not any((pid, k) in found_names for k in verses):
            builder.err("讀經", f"{display(pid)}（{pid}）的名字「{form}」在 {verses[0]}{'…' if len(verses) > 1 else ''} 沒有對上經文")
    for k, items in decisions.items():
        for item in items or []:
            if (str(k), str(item.get("at"))) not in used_decisions:
                builder.err(f"讀經.decide.{k}", f"找不到要裁決的位置：{item.get('at')}")
    for k, words in title_of.items():
        for word in words or {}:
            if (str(k), str(word)) not in used_titles:
                builder.err(f"讀經.title_of.{k}", f"這一節沒有這個職稱：{word}")
    for k in names_of:
        if k not in used_names:
            builder.err(f"讀經.names.{k}", "這一節不在讀經路線上")
    builder.reading_review = review
    return {"start": start, "segments": segments_out, "notes": notes, "diffs": diffs, "links": links}


def annotate(text: str, tokens: list[dict], display) -> str:
    out, at = [], 0
    for token in tokens:
        out.append(text[at:token["s"]])
        word = text[token["s"]:token["e"]]
        if token["k"] == "p":
            tag = token.get("id") or (("職:" + token["rid"]) if token.get("rid") else "？")
            tag = word if tag == word else f"{word}={tag}"
            if token.get("from"):
                tag += "←" + "/".join(display(x) for x in token["from"])
            if token.get("to"):
                tag += "→" + "/".join(display(x) for x in token["to"])
            if "link" in token:
                tag += f"⇢連結{token['link']}"
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
