"""帶你讀經的對照閘門（獨立於建置程式另算一次）：逐段落數三項——位置錯誤、找不到人物、未處理的人名。

用法：python appendix/genealogy/tools/reading_gate.py [網站資料夾]
三項都是 0 才印 PASS，否則 exit 1。
- 位置錯誤：經文和 raw_scripture 不同；標記超出經文、長度為零或互相重疊。
- 找不到人物：人名、職稱歸屬、墨線兩端的人不在家譜樹人物或職位圖人物裡；歸回連結指到不存在的人或格子。
- 未處理的人名：家譜樹人物的名字出處（names[].ref）落在這一段，或職位圖成員的出處落在這一段，
  但出處那幾節都沒有標到這個人。
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BOOKS = {"創": "創世記", "出": "出埃及記", "得": "路得記", "撒上": "撒母耳記上", "撒下": "撒母耳記下", "代上": "歷代志上",
         "代下": "歷代志下", "拉": "以斯拉記", "尼": "尼希米記", "太": "馬太福音", "路": "路加福音"}
site = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "appendix/website/全聖經/亞當到耶穌"
data_dir = site / "src/data"
reading = json.loads((data_dir / "reading.json").read_text(encoding="utf-8"))
genealogy = json.loads((data_dir / "genealogy.json").read_text(encoding="utf-8"))
roles = json.loads((data_dir / "roles.json").read_text(encoding="utf-8"))
persons = {p["id"]: p for p in genealogy["persons"]}
rids = {p["rid"] for p in roles.get("people", [])}
cells = {(box["id"], m["key"]) for c in roles.get("categories", []) for box in c["boxes"] for m in box["members"]}
raw_cache: dict[tuple[str, int], list[str]] = {}


def raw(book: str, chapter: int) -> list[str]:
    key = (book, chapter)
    if key not in raw_cache:
        raw_cache[key] = (ROOT / "raw_scripture" / BOOKS[book] / f"第{chapter}章.txt").read_text(encoding="utf-8").splitlines()
    return raw_cache[key]


def keys_of(ref: str) -> list[str]:
    out = []
    for part in re.split(r"[,，;；、]\s*", str(ref)):
        m = re.match(r"^(\D+?)(\d+):(\d+)(?:-(?:(\d+):)?(\d+))?$", part.strip())
        if not m or m[1] not in BOOKS:
            continue
        book, c1, v1 = m[1], int(m[2]), int(m[3])
        c2 = int(m[4]) if m[4] else c1
        v2 = int(m[5]) if m[5] else v1
        c, v = c1, v1
        while (c, v) <= (c2, v2):
            out.append(f"{book}{c}:{v}")
            v += 1
            if v > len(raw(book, c)):
                c, v = c + 1, 1
    return out


TRIBES = {"以色列", "猶大", "利未", "瑪拿西", "便雅憫", "迦得", "流便", "以薩迦", "亞設", "以法蓮", "西布倫",
          "拿弗他利", "西緬", "但", "約瑟"}
segment_of: dict[str, str] = {}
tagged: set[tuple[str, str]] = set()
rows = []
for segment in reading["segments"]:
    position = missing = 0
    count = 0
    for chapter in segment["chapters"]:
        for verse in chapter["verses"]:
            count += 1
            key = f"{chapter['book']}{chapter['n']}:{verse['v']}"
            segment_of[key] = segment["id"]
            lines = raw(chapter["book"], chapter["n"])
            if verse["v"] > len(lines) or verse["text"] != lines[verse["v"] - 1]:
                position += 1
            end = 0
            for t in verse["t"]:
                if t["s"] < end or t["e"] <= t["s"] or t["e"] > len(verse["text"]):
                    position += 1
                end = t["e"]
                for pid in [t.get("id"), *t.get("from", []), *t.get("to", [])]:
                    if pid and pid not in persons:
                        missing += 1
                if t.get("rid") and t["rid"] not in rids:
                    missing += 1
                if t.get("of") and t["of"] not in persons and t["of"] not in rids:
                    missing += 1
                if t.get("id"):
                    tagged.add((t["id"], key))
                if t.get("rid"):
                    tagged.add(("r:" + t["rid"], key))
    rows.append([segment["id"], segment["title"], count, position, missing, 0])
for link in reading.get("links", []):
    for target in link["to"]:
        if target.get("tree") and target["tree"] not in persons:
            rows[[r[0] for r in rows].index(segment_of.get(link["at"], rows[0][0]))][4] += 1
        if target.get("role") and target.get("member") and (target["role"], target["member"]) not in cells:
            rows[[r[0] for r in rows].index(segment_of.get(link["at"], rows[0][0]))][4] += 1

# 標記的字必須是那個人的名字或別名（家譜樹人物：顯示名＋names[].as；職位圖的人：名字）
forms: dict[str, set[str]] = defaultdict(set)
for pid, person in persons.items():
    forms[pid].add(person.get("name", pid.split("#")[0]))
    forms[pid].update(str(n.get("as")) for n in person.get("names", []) or [] if n.get("as"))
role_names = {p["rid"]: p["name"] for p in roles.get("people", [])}
wrong_name: dict[str, list[str]] = defaultdict(list)
# 裁決檔寫明「只在經文裡亮」的名字（names）：那個位置必須真的有一個沒有連到人的人名標記
import yaml  # noqa: E402

declared: list[tuple[str, str]] = []
decision_dir = ROOT / "appendix/genealogy/亞當到耶穌"
for path in [decision_dir / "讀經.yaml", *sorted((decision_dir / "讀經").glob("*.yaml"))]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    for key, words in (data.get("names") or {}).items():
        declared.extend((str(key), str(word)) for word in words or [])
verse_of: dict[str, dict] = {}
for segment in reading["segments"]:
    for chapter in segment["chapters"]:
        for verse in chapter["verses"]:
            key = f"{chapter['book']}{chapter['n']}:{verse['v']}"
            verse_of[key] = verse
            for t in verse["t"]:
                word = verse["text"][t["s"]:t["e"]]
                if t.get("id") and word not in forms[t["id"]]:
                    wrong_name[segment_of[key]].append(f"{key}「{word}」≠ {t['id']}")
                if t.get("rid") and word != role_names.get(t["rid"]):
                    wrong_name[segment_of[key]].append(f"{key}「{word}」≠ {t['rid']}")
for key, word in declared:
    verse = verse_of.get(key)
    if verse is None:
        continue
    if not any(t["k"] == "p" and not t.get("id") and not t.get("rid") and verse["text"][t["s"]:t["e"]] == word for t in verse["t"]):
        wrong_name[segment_of[key]].append(f"{key}「{word}」裁決說只在經文裡亮，卻沒有標")

# 同一段裡標過的人名，在這一段別的節出現卻完全沒有標記（不是人名、地名，也沒寫明略過）：漏標
for segment in reading["segments"]:
    seg_forms: set[str] = set()
    for chapter in segment["chapters"]:
        for verse in chapter["verses"]:
            for t in verse["t"]:
                if t["k"] == "p" and (t.get("id") or t.get("rid")):
                    seg_forms.add(verse["text"][t["s"]:t["e"]])
    # 支派名（「流便支派」「猶大人」）照第一階段的做法不連到人；宗族名後面接「族」「的子孫」也是指一群人
    all_forms = {f for f in seg_forms if len(f) >= 2} | TRIBES
    seg_forms = {f for f in seg_forms if len(f) >= 2 and f not in TRIBES}
    for chapter in segment["chapters"]:
        for verse in chapter["verses"]:
            key = f"{chapter['book']}{chapter['n']}:{verse['v']}"
            text = verse["text"]
            covered = [(t["s"], t["e"]) for t in verse["t"]]
            longer = [(m.start(), m.end()) for f in all_forms for m in re.finditer(re.escape(f), text)]
            longer += [(t["s"], t["e"]) for t in verse["t"]]
            for form in seg_forms:
                start = text.find(form)
                while start >= 0:
                    end = start + len(form)
                    inside = any(s <= start and end <= e and e - s > end - start for s, e in longer)
                    # 族名、民族的用法：「迦南女子」「米甸人」「哥轄族」「米拉利子孫」「某某的子孫」
                    clan = (text[end:end + 1] in ("族", "人") or text[end:end + 2] in ("女子", "子孫")
                            or text[end:end + 3] == "的子孫")
                    if not inside and not clan and not any(s < end and start < e for s, e in covered):
                        wrong_name[segment["id"]].append(f"{key}「{form}」在這一段別處標過，這裡沒標")
                    start = text.find(form, start + 1)

unhandled: dict[str, list[str]] = defaultdict(list)
for pid, person in persons.items():
    for name in person.get("names", []) or []:
        keys = [k for k in keys_of(name.get("ref", "")) if k in segment_of]
        if keys and not any((pid, k) in tagged for k in keys):
            unhandled[segment_of[keys[0]]].append(f"{pid} {name.get('ref')}")
for category in roles.get("categories", []):
    for box in category["boxes"]:
        for member in box["members"]:
            pid = member.get("id") or ("r:" + member["rid"])
            keys = [k for k in keys_of(member["ref"]) if k in segment_of]
            if keys and not any((pid, k) in tagged for k in keys):
                unhandled[segment_of[keys[0]]].append(f"{member['name']}（{box['title']}）{member['ref']}")
for row in rows:
    row[5] = len(unhandled.get(row[0], []))
    # 名字對不上人、宣告的名字沒標：算在「找不到人物」
    row[4] += len(wrong_name.get(row[0], []))
    for item in wrong_name.get(row[0], [])[:5]:
        unhandled.setdefault(row[0], []).append("名字對不上：" + item)

print("段落\t節數\t位置錯誤\t找不到人物\t未處理的人名")
for seg_id, title, count, position, missing, todo in rows:
    print(f"{title}\t{count}\t{position}\t{missing}\t{todo}")
    for item in unhandled.get(seg_id, [])[:5]:
        print(f"    未處理：{item}")
total = [sum(r[i] for r in rows) for i in (2, 3, 4, 5)]
print(f"合計\t{total[0]}\t{total[1]}\t{total[2]}\t{total[3]}")
ok = total[1] == total[2] == total[3] == 0
print("PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
