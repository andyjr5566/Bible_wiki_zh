"""大衛立的職位：讀 亞當到耶穌/職位.yaml，檢查後整理成網站的 roles.json 與家譜樹上的職位印。

由 build_genealogy.py 的 LineageBuilder 呼叫（helpers 由它傳入，避免互相匯入）。
檢查：
- 每個成員的名字逐字出現在他的出處經文裡；
- 家譜樹上的人（id）必須寫 basis，而且根據檢查器通過；people 裡定義的人（出現在好幾處）也要寫 basis；
- 照經文寫的人數（figures.count）逐字出現在該節；
- 二十四班、十二月的序號在範圍內；方塊與成員代號不重複。
"""
from __future__ import annotations

from collections import OrderedDict
from pathlib import Path

KINDS = {"list", "ring24", "wheel12", "groups", "compare", "tiles"}
RING_SIZE = {"ring24": 24, "wheel12": 12}
CATEGORY_IDS = ("court", "army", "temple", "tribes", "solomon")


def build_roles(builder, raw: dict, helpers: dict) -> tuple[dict, list[dict]]:
    """回傳 (roles.json 的內容, 家譜樹職位印)。錯誤寫進 builder.err。"""
    if not raw:
        return {}, []
    parse_refs, display = helpers["parse_refs"], helpers["display"]
    check_basis = helpers.get("check_basis")
    root: Path = helpers["ROOT"]
    where = "職位.yaml"

    def text_of(ref: str, at: str) -> str:
        try:
            parsed = parse_refs(str(ref), "", builder.sc)
        except ValueError as exc:
            builder.err(at, str(exc))
            return ""
        if not parsed:
            builder.err(at, f"經節是空的：{ref}")
        out = []
        for item in parsed:
            verse = builder.sc.verse(*item)
            if verse is None:
                builder.err(at, f"經節不存在：{ref}")
            else:
                out.append(verse)
        return "".join(out)

    def basis_ok(items, at: str) -> None:
        if check_basis is None:
            builder.err(at, "找不到根據檢查器 check_basis.py")
            return
        for message in check_basis(items, at, root):
            builder.err(at, message)

    people: OrderedDict[str, dict] = OrderedDict()
    for rid, item in (raw.get("people") or {}).items():
        at = f"{where}.people.{rid}"
        if not item.get("name"):
            builder.err(at, "name 不能空白")
        basis_ok(item.get("basis"), at)
        people[str(rid)] = {"rid": str(rid), "name": str(item.get("name", "")), "qualifier": str(item.get("q", "") or ""),
                            "refs": [], "aliases": [str(a) for a in item.get("aliases", []) or []]}
    declared = set(people)
    used_declared: set[str] = set()
    people_definitions = raw.get("people") or {}

    def raw_entity(item):
        if not isinstance(item, dict):
            return "", ("", "")
        if item.get("id"):
            pid = str(item["id"])
            return str(item.get("name") or display(pid)), ("id", pid)
        if item.get("rid"):
            rid = str(item["rid"])
            person = people_definitions.get(rid, {})
            return str(person.get("name", "")), ("rid", rid)
        if item.get("n"):
            name = str(item["n"])
            q = str(item.get("q", "") or "")
            rid = f"{name}#{q}" if q else name
            if item.get("qid") is not None:
                rid += f"#{item['qid']}"
            return name, ("rid", rid)
        return "", ("", "")

    solomon_entities = []
    for category_spec in raw.get("categories", []) or []:
        if not isinstance(category_spec, dict) or category_spec.get("id") != "solomon":
            continue
        for box_spec in category_spec.get("boxes", []) or []:
            if not isinstance(box_spec, dict):
                continue
            for member_spec in box_spec.get("members", []) or []:
                entity_name, identity = raw_entity(member_spec)
                solomon_entities.append((member_spec, entity_name, identity))
            for row_spec in box_spec.get("rows", []) or []:
                if not isinstance(row_spec, dict):
                    continue
                for david_spec in row_spec.get("david", []) or []:
                    entity_name, identity = raw_entity(david_spec)
                    solomon_entities.append((david_spec, entity_name, identity))

    # 其他類別的職位成員、家譜樹上的人也算同名（以拉的兒子示每 vs 拉瑪人示每、家譜樹上的示每）
    other_entities = []
    for category_spec in raw.get("categories", []) or []:
        if not isinstance(category_spec, dict) or category_spec.get("id") == "solomon":
            continue
        for box_spec in category_spec.get("boxes", []) or []:
            for member_spec in (box_spec.get("members", []) or []) if isinstance(box_spec, dict) else []:
                entity_name, identity = raw_entity(member_spec)
                other_entities.append((member_spec, entity_name, identity))
    tree_names = {display(pid) for pid in builder.people}

    def name_conflicts(member, name: str, rid: str) -> bool:
        if name in tree_names:
            return True
        for other_source, other_name, identity in other_entities:
            if other_name == name and identity != ("rid", rid):
                return True
        for other_rid, person in people_definitions.items():
            if (str(other_rid) != rid and isinstance(person, dict)
                    and str(person.get("name", "")) == name):
                return True
        for other_source, other_name, identity in solomon_entities:
            if other_source is not member and other_name == name and identity != ("rid", rid):
                return True
        return False

    def compare_rows(box: dict, keys: set[str], people: dict, at: str) -> list[dict]:
        """「從大衛到所羅門」：一個職位一列，左欄大衛時、右欄所羅門時。"""
        rows = []
        used: set[str] = set()
        for r_index, row in enumerate(box.get("rows", []) or []):
            r_at = f"{at}.rows[{r_index}]"
            office = str(row.get("office", ""))
            if not office:
                builder.err(r_at, "office 不能空白")
            david = []
            for d_index, item in enumerate(row.get("david", []) or []):
                d_at = f"{r_at}.david[{d_index}]"
                ref = str(item.get("ref", ""))
                text = text_of(ref, d_at)
                entry: dict = {"ref": ref}
                if item.get("id"):
                    pid = str(item["id"])
                    if pid not in builder.people:
                        builder.err(d_at, f"家譜樹上沒有這個人：{pid}")
                    entry.update({"id": pid, "name": display(pid)})
                elif item.get("rid"):
                    rid = str(item["rid"])
                    if rid not in people:
                        builder.err(d_at, f"people 沒有定義：{rid}")
                        continue
                    entry.update({"rid": rid, "name": people[rid]["name"]})
                elif item.get("n"):
                    entry["name"] = str(item["n"])
                else:
                    builder.err(d_at, "id／rid／n 必須寫一個")
                    continue
                if not any(form in text for form in [entry["name"]] + (people[entry["rid"]]["aliases"] if entry.get("rid") else [])):
                    builder.err(d_at, f"{ref} 的經文裡沒有「{entry['name']}」")
                if item.get("d"):
                    entry["detail"] = str(item["d"])
                david.append(entry)
            solomon = [str(k) for k in row.get("solomon", []) or []]
            for key in solomon:
                if key not in keys:
                    builder.err(r_at, f"members 裡沒有這個人：{key}")
            out_row: dict = {"office": office, "david": david, "solomon": solomon}
            if row.get("same"):
                same = str(row["same"])
                # 合併成同一人（金框橫跨兩欄）：必須是 people 定義過、寫了根據（basis）的人
                if same not in keys:
                    builder.err(r_at, f"members 裡沒有這個人：{same}")
                if same not in declared:
                    builder.err(r_at, f"同一人（same）必須在 people 定義並寫根據：{same}")
                out_row["same"] = same
            if row.get("moved"):
                moved = row["moved"]
                key, origin = str(moved.get("key", "")), str(moved.get("from", ""))
                if key not in solomon:
                    builder.err(r_at, f"moved 的人必須在這一列的所羅門時：{key}")
                if not origin:
                    builder.err(r_at, "moved 要寫原本的職位（from）")
                out_row["moved"] = {"key": key, "from": origin}
            used.update(solomon)
            if row.get("same"):
                used.add(str(row["same"]))
            rows.append(out_row)
        for key in sorted(keys - used):
            builder.err(at, f"這個人沒有排進任何一列：{key}")
        return rows

    categories = []
    seals: list[dict] = []
    box_ids: set[str] = set()
    seen_ids = {str(c.get("id")) for c in raw.get("categories", []) or []}
    if seen_ids != set(CATEGORY_IDS):
        builder.err(where, f"類別必須是 {'、'.join(CATEGORY_IDS)}")
    for category in raw.get("categories", []) or []:
        boxes = []
        for box in category.get("boxes", []) or []:
            box_id = str(box.get("id", ""))
            at = f"{where}.{box_id}"
            if not box_id or box_id in box_ids:
                builder.err(at, "方塊 id 空白或重複")
            box_ids.add(box_id)
            kind = str(box.get("kind", "list"))
            is_officials = box_id == "solomon-officials"
            if is_officials and kind != "tiles":
                builder.err(at, "solomon-officials 的 kind 必須是 tiles")
            if kind not in KINDS:
                builder.err(at, f"kind 必須是 {'／'.join(sorted(KINDS))}")
            for field in ("title", "ref", "seal"):
                if not box.get(field):
                    builder.err(at, f"{field} 不能空白")
            members = []
            keys: set[str] = set()
            for index, member in enumerate(box.get("members", []) or []):
                m_at = f"{at}.members[{index}]"
                kinds = [k for k in ("id", "rid", "n") if member.get(k)]
                if len(kinds) != 1:
                    builder.err(m_at, "id／rid／n 必須恰好寫一個")
                    continue
                ref = str(member.get("ref", ""))
                text = text_of(ref, m_at)
                q = str(member.get("q", "") or "")
                if category.get("id") == "solomon" and q and not _is_ref(q) and q not in text:
                    builder.err(m_at, f"限定詞「{q}」沒有逐字出現在 {ref} 的經文裡")
                row: dict = {}
                if member.get("id"):
                    pid = str(member["id"])
                    if pid not in builder.people:
                        builder.err(m_at, f"家譜樹上沒有這個人：{pid}")
                    basis_ok(member.get("basis"), m_at)
                    name = str(member.get("name") or display(pid))
                    row["id"] = pid
                    # 成員可以有自己的印（「從大衛到所羅門」裡撒督的兒子亞撒利雅是「祭司」）
                    seals.append({"id": pid, "label": str(member.get("seal") or box.get("seal", "")), "box": box_id,
                                  "ref": ref.split(",")[0].strip()})
                else:
                    if member.get("rid"):
                        rid = str(member["rid"])
                        if rid not in people:
                            builder.err(m_at, f"people 沒有定義：{rid}")
                            continue
                        used_declared.add(rid)
                    else:
                        q = str(member.get("q", "") or "")
                        rid = f"{member['n']}#{q}" if q else str(member["n"])
                        # qid：同一處經文裡同名、限定詞也一樣的兩個人（例如瑪拿西人約撒拔有兩個），只用來分開，不給讀者看
                        if member.get("qid") is not None:
                            rid += f"#{member['qid']}"
                        if rid in declared:
                            builder.err(m_at, f"{rid} 在 people 定義過，請改寫 rid")
                        people.setdefault(rid, {"rid": rid, "name": str(member["n"]), "qualifier": q if not _is_ref(q) else "",
                                                "refs": [], "aliases": []})
                    name = people[rid]["name"]
                    if member.get("n"):
                        conflict = category.get("id") == "solomon" and name_conflicts(
                            member, name, rid
                        )
                        if conflict and not member.get("basis"):
                            builder.err(m_at, "同名不同人的分開要寫根據")
                        if conflict or "basis" in member:
                            basis_ok(member.get("basis"), m_at)
                    row["rid"] = rid
                    for part in [p.strip() for p in ref.split(",") if p.strip()]:
                        if part not in people[rid]["refs"]:
                            people[rid]["refs"].append(part)
                # 別寫（亞多蘭／亞多尼蘭）：名字或任一個別寫出現在經文裡就算
                forms = [name] + (people[row["rid"]]["aliases"] if row.get("rid") else [])
                if name and not any(form in text for form in forms):
                    builder.err(m_at, f"{ref} 的經文裡沒有「{name}」")
                key = str(member.get("key") or row.get("id") or row.get("rid"))
                if key in keys:
                    builder.err(m_at, f"同一個方塊裡代號重複：{key}")
                keys.add(key)
                row = {"key": key, **row, "name": name, "ref": ref}
                if member.get("d"):
                    row["detail"] = str(member["d"])
                # 十二個官吏裡娶了所羅門女兒的兩位：名牌連到家譜樹上的妻子（名字必須在出處經文裡）
                if member.get("spouse"):
                    spouse = str(member["spouse"])
                    if spouse not in builder.people:
                        builder.err(m_at, f"家譜樹上沒有這個人：{spouse}")
                    elif display(spouse) not in text:
                        builder.err(m_at, f"{ref} 的經文裡沒有「{display(spouse)}」")
                    row["spouse"] = {"id": spouse, "name": display(spouse)}
                if member.get("order") is not None:
                    order = int(member["order"])
                    if kind in RING_SIZE and not 1 <= order <= RING_SIZE[kind]:
                        builder.err(m_at, f"序號超出範圍：{order}")
                    row["order"] = order
                members.append(row)
            if kind in RING_SIZE:
                orders = {m.get("order") for m in members}
                if orders != set(range(1, RING_SIZE[kind] + 1)):
                    builder.err(at, f"{RING_SIZE[kind]} 格沒有排滿：缺 {sorted(set(range(1, RING_SIZE[kind] + 1)) - orders)}")
            out = {"id": box_id, "title": str(box.get("title", "")), "ref": str(box.get("ref", "")), "kind": kind,
                   "seal": str(box.get("seal", "")), "members": members}
            if box.get("verses"):
                out["verses"] = str(box["verses"])
                text_of(str(box["verses"]), f"{at}.verses")
            if box.get("note"):
                out["note"] = str(box["note"])
            figures = []
            for f_index, figure in enumerate(box.get("figures", []) or []):
                f_at = f"{at}.figures[{f_index}]"
                count, ref = str(figure.get("count", "")), str(figure.get("ref", ""))
                if not count or count not in text_of(ref, f_at):
                    builder.err(f_at, f"{ref} 的經文裡沒有「{count}」")
                figures.append({"label": str(figure.get("label", "")), "count": count, "ref": ref})
            if figures:
                out["figures"] = figures
            if kind == "compare":
                out["rows"] = compare_rows(box, keys, people, at)
            if box.get("quote"):
                quote = box["quote"]
                q_ref, q_text = str(quote.get("ref", "")), str(quote.get("text", ""))
                if not q_text or q_text not in text_of(q_ref, f"{at}.quote"):
                    builder.err(f"{at}.quote", f"{q_ref} 的經文裡沒有「{q_text}」")
                out["quote"] = {"ref": q_ref, "text": q_text}
            if is_officials:
                if any("order" in m or "month" in m for m in box.get("members", []) or []):
                    builder.err(at, "十二個官吏不得有 order（序號）或 month（月份）")
                if len(members) != 12:
                    builder.err(at, f"十二個官吏應有 12 位，現在 {len(members)} 位")
            elif kind == "tiles":
                if any("order" in m or "month" in m for m in box.get("members", []) or []):
                    builder.err(at, "方塊 tiles 不得有 order（序號）或 month（月份）")
                if len(members) != 12:
                    builder.err(at, f"tiles 應有 12 位，現在 {len(members)} 位")
            if box.get("groups"):
                groups = []
                for g_index, group in enumerate(box["groups"]):
                    try:
                        verses = {(c, v) for _, c, v in parse_refs(str(group.get("ref", "")), "", builder.sc)}
                    except ValueError as exc:
                        builder.err(f"{at}.groups[{g_index}]", str(exc))
                        verses = set()
                    keys_in = [m["key"] for m in members
                               if any((c, v) in verses for _, c, v in _safe(parse_refs, m["ref"], builder))]
                    groups.append({"title": str(group.get("title", "")), "ref": str(group.get("ref", "")), "keys": keys_in})
                out["groups"] = groups
            boxes.append(out)
        categories.append({"id": str(category.get("id")), "title": str(category.get("title", "")), "boxes": boxes})
    for rid in declared - used_declared:
        builder.err(f"{where}.people.{rid}", "定義了卻沒有用到")
    for person in people.values():
        if not person["refs"]:
            builder.err(f"{where}.people.{person['rid']}", "沒有出處")
    # 同一個人在同一個職位只蓋一枚印
    unique_seals, seen = [], set()
    for seal in seals:
        mark = (seal["id"], seal["label"])
        if mark not in seen:
            seen.add(mark)
            unique_seals.append(seal)
    return {"categories": categories, "people": list(people.values())}, unique_seals


def _is_ref(text: str) -> bool:
    """q 寫經節（只為了區分同名、沒有更好的限定詞）時，不給讀者看。"""
    return bool(text) and text[0] in "創出利民申書士得撒王代拉尼斯太可路約徒" and ":" in text


def _safe(parse_refs, ref: str, builder):
    try:
        return parse_refs(str(ref), "", builder.sc)
    except ValueError:
        return []
