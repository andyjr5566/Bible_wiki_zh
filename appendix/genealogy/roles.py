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

KINDS = {"list", "ring24", "wheel12", "groups"}
RING_SIZE = {"ring24": 24, "wheel12": 12}
CATEGORY_IDS = ("court", "army", "temple", "tribes")


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

    categories = []
    seals: list[dict] = []
    box_ids: set[str] = set()
    seen_ids = {str(c.get("id")) for c in raw.get("categories", []) or []}
    if seen_ids != set(CATEGORY_IDS):
        builder.err(where, f"四類必須是 {'、'.join(CATEGORY_IDS)}")
    for category in raw.get("categories", []) or []:
        boxes = []
        for box in category.get("boxes", []) or []:
            box_id = str(box.get("id", ""))
            at = f"{where}.{box_id}"
            if not box_id or box_id in box_ids:
                builder.err(at, "方塊 id 空白或重複")
            box_ids.add(box_id)
            kind = str(box.get("kind", "list"))
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
                row: dict = {}
                if member.get("id"):
                    pid = str(member["id"])
                    if pid not in builder.people:
                        builder.err(m_at, f"家譜樹上沒有這個人：{pid}")
                    basis_ok(member.get("basis"), m_at)
                    name = str(member.get("name") or display(pid))
                    row["id"] = pid
                    seals.append({"id": pid, "label": str(box.get("seal", "")), "box": box_id, "ref": ref.split(",")[0].strip()})
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
                    row["rid"] = rid
                    for part in [p.strip() for p in ref.split(",") if p.strip()]:
                        if part not in people[rid]["refs"]:
                            people[rid]["refs"].append(part)
                if name and name not in text:
                    builder.err(m_at, f"{ref} 的經文裡沒有「{name}」")
                key = str(member.get("key") or row.get("id") or row.get("rid"))
                if key in keys:
                    builder.err(m_at, f"同一個方塊裡代號重複：{key}")
                keys.add(key)
                row = {"key": key, **row, "name": name, "ref": ref}
                if member.get("d"):
                    row["detail"] = str(member["d"])
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
