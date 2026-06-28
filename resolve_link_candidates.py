#!/usr/bin/env python3
"""將資料驅動的 link candidates 與全域 index 比對並產生 link plan。"""
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX_FILE = ROOT / "link_folder" / "_index" / "link_index.json"

SAME_PERSON_MAP = {
    "亞伯拉罕": "亞伯蘭", "亞伯蘭": "亞伯拉罕",
    "撒拉": "撒萊", "撒萊": "撒拉",
}
PERSON_TO_BOOK = {
    "何西阿": "何西阿書", "約珥": "約珥書", "阿摩司": "阿摩司書",
    "俄巴底亞": "俄巴底亞書", "約拿": "約拿書", "彌迦": "彌迦書",
    "那鴻": "那鴻書", "哈巴谷": "哈巴谷書", "西番雅": "西番雅書",
    "哈該": "哈該書", "撒迦利亞": "撒迦利亞書", "瑪拉基": "瑪拉基書",
    "馬太": "馬太福音", "馬可": "馬可福音", "路加": "路加福音",
    "約翰": "約翰福音", "雅各": "雅各書", "彼得": "彼得前書", "猶大": "猶大書",
}
VALID_TYPES = {
    "人物", "地點", "神學", "主題", "原文", "背景", "歷史", "文化", "互文",
    "解經爭議", "文學結構", "節期", "祭祀", "王朝", "預言應驗", "新約引用",
    "聖經神學", "制度",
}


def normalize_name(value):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", value)).strip()


def load_index(index_file=INDEX_FILE):
    if not index_file.exists():
        raise FileNotFoundError("link index 不存在，請先執行 build_link_index.py")
    return json.loads(index_file.read_text(encoding="utf-8"))


def load_candidates(book, chapter, root=ROOT):
    path = root / book / ".tmp" / f"第{chapter}章" / "link_candidates.md"
    if not path.exists():
        raise FileNotFoundError(f"link_candidates.md 不存在：{path}")
    candidates = []
    current_section = None
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        section = re.match(r"^##\s+(.+)", line)
        if section:
            current_section = section.group(1).strip()
            continue
        item = re.match(r"^\s*-\s+(.+?)\s*→\s*([^—]+?)(?:\s*—\s*(.+))?\s*$", line)
        if item:
            candidates.append({
                "name": item.group(1).strip(),
                "suggested_type": item.group(2).strip(),
                "evidence": (item.group(3) or "").strip(),
                "section": current_section,
                "line_number": line_number,
            })
        elif re.match(r"^\s*-\s+\S", line):
            print(f"⚠️ 無法解析候選（第 {line_number} 行）：{line.strip()}")
    return candidates


def _canonical_entry(entry, index):
    if "alias_of" in entry:
        return index.get(entry["alias_of"]), entry["alias_of"]
    return entry, entry.get("title")


def find_in_index(candidate_name, index):
    """回傳 match_type、entry、實際 title；不做破壞語義的名稱裁切。"""
    if candidate_name in index:
        entry, title = _canonical_entry(index[candidate_name], index)
        return ("alias" if candidate_name != title else "exact", entry, title)

    normalized = normalize_name(candidate_name)
    matches = []
    for key, value in index.items():
        if normalize_name(key) == normalized:
            entry, title = _canonical_entry(value, index)
            matches.append((entry, title, "alias" if key != title else "normalized"))
    unique = {(m[1], m[0].get("path", "")): m for m in matches if m[0]}
    if len(unique) == 1:
        entry, title, kind = next(iter(unique.values()))
        return kind, entry, title
    if len(unique) > 1:
        return "conflict", None, None

    mapped = SAME_PERSON_MAP.get(candidate_name)
    if mapped and mapped in index:
        entry, title = _canonical_entry(index[mapped], index)
        return "alias", entry, title
    return "not_found", None, None


def type_compatible(suggested_type, entry):
    return suggested_type == entry.get("type") or suggested_type in entry.get("secondary_types", [])


def has_book_chapter_data(entry_path, book, chapter, root=ROOT):
    text = (root / entry_path).read_text(encoding="utf-8")
    marker = f"<!-- accumulation:{book}:{chapter}:start -->"
    if marker in text:
        return True
    direct = re.compile(rf"^###\s+{re.escape(book)}\s*第{re.escape(str(chapter))}章\s*$", re.M)
    nested = re.compile(
        rf"^###\s+{re.escape(book)}\s*$[\s\S]*?^####\s+第{re.escape(str(chapter))}章\s*$",
        re.M,
    )
    return bool(direct.search(text) or nested.search(text))


def resolve(candidates, index, book, chapter, root=ROOT):
    plan = {key: [] for key in (
        "A_use_directly", "B_needs_update", "C_new_formal", "D_new_candidate", "E_skip"
    )}
    for original in candidates:
        candidate = dict(original)
        name = candidate["name"].strip()
        suggested = candidate["suggested_type"]
        candidate["clean_name"] = name

        if name.startswith("不建立") or name == "暫不建立" or suggested in {"普通詞"}:
            plan["E_skip"].append(candidate)
            continue
        if suggested not in VALID_TYPES:
            candidate["note"] = f"未知分類：{suggested}"
            plan["D_new_candidate"].append(candidate)
            continue

        match_type, matched, title = find_in_index(name, index)
        if match_type == "conflict":
            candidate["note"] = "名稱或 alias 有多重指向"
            plan["D_new_candidate"].append(candidate)
        elif matched:
            if not type_compatible(suggested, matched):
                candidate.update({
                    "match_type": "type_conflict",
                    "existing_path": matched.get("path", ""),
                    "existing_title": title,
                    "note": (
                        f"分類衝突：候選={suggested}，既有={matched.get('type')}，"
                        f"secondary={matched.get('secondary_types', [])}"
                    ),
                })
                plan["D_new_candidate"].append(candidate)
                continue
            candidate.update({
                "match_type": match_type,
                "existing_path": matched["path"],
                "existing_title": title,
                "original_candidate": name,
            })
            bucket = (
                "A_use_directly"
                if has_book_chapter_data(matched["path"], book, chapter, root)
                else "B_needs_update"
            )
            plan[bucket].append(candidate)
        elif name in PERSON_TO_BOOK or name in PERSON_TO_BOOK.values():
            candidate["note"] = "人物與書卷可能同名，需人工確認"
            plan["D_new_candidate"].append(candidate)
        else:
            plan["C_new_formal"].append(candidate)
    return plan


def write_plan(plan, book, chapter, root=ROOT):
    output_dir = root / book / ".tmp" / f"第{chapter}章"
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "link_plan.md"
    lines = [f"# 第{chapter}章 link plan\n\n"]
    sections = [
        ("A_use_directly", "A. 使用既有條目（本章資料已存在）"),
        ("B_needs_update", "B. 需更新既有條目"),
        ("C_new_formal", "C. 新增正式條目"),
        ("D_new_candidate", "D. 待人工判斷"),
        ("E_skip", "E. 不建立 link"),
    ]
    for key, heading in sections:
        if not plan[key]:
            continue
        lines.append(f"## {heading}\n\n")
        for item in plan[key]:
            evidence = f"；依據：{item['evidence']}" if item.get("evidence") else ""
            if key in {"A_use_directly", "B_needs_update"}:
                lines.append(
                    f"- [[{item['existing_title']}]] → {item['existing_path']}"
                    f"（{item['match_type']}；候選分類={item['suggested_type']}；"
                    f"實際分類已核對；來源行={item['line_number']}{evidence}）\n"
                )
            elif key == "C_new_formal":
                lines.append(
                    f"- [[{item['name']}]] → link_folder/{item['suggested_type']}/{item['name']}.md"
                    f"（來源行={item['line_number']}{evidence}）\n"
                )
            elif key == "D_new_candidate":
                lines.append(f"- {item['name']} — {item.get('note', '待確認')}{evidence}\n")
            else:
                lines.append(f"- {item['name']} — 純文字\n")
        lines.append("\n")
    output.write_text("".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"✅ link plan 已建立：{output}")
    for key, _ in sections:
        print(f"   {key}: {len(plan[key])}")
    return output


def main():
    if len(sys.argv) != 3:
        print("用法：python resolve_link_candidates.py <書卷名> <章>")
        return 2
    book, chapter = sys.argv[1], sys.argv[2]
    try:
        index = load_index()
        candidates = load_candidates(book, chapter)
        plan = resolve(candidates, index, book, chapter)
        write_plan(plan, book, chapter)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"❌ {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
