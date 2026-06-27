#!/usr/bin/env python3
"""
resolve_link_candidates.py — 將 link_candidates.md 與 link_index.json 比對

比對優先順序（加強版，支援 YAML aliases）：
  1. 完全同名檔案
  2. YAML aliases 完全命中 → 指向主條目
  3. 常見同義詞命中
  4. fuzzy match 候選 → D 類
  5. 不同資料夾中的同名條目（使用既有條目）
  6. 書卷名與人物名衝突
  7. 經文原詞與條目完整名稱不同 → 確認 alias 格式

產生 link_plan.md（A/B/C/D/E 五類）

用法：
  python3 resolve_link_candidates.py <書卷名> <章>

範例：
  python3 resolve_link_candidates.py 創世記 13
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX_FILE = ROOT / "link_folder" / "_index" / "link_index.json"

# 同一人物不同階段/命名的 mapping（不納入 link_index，只供比對 fallback）
SAME_PERSON_MAP = {
    "亞伯拉罕": "亞伯蘭",   # 創17章前後改名
    "撒拉": "撒萊",         # 取消炎改名
    "亞伯蘭": "亞伯拉罕",   # 反向
    "撒萊": "撒拉",         # 反向
}

# 書卷名→人物名映射（用於衝突檢測）
PERSON_TO_BOOK = {
    "何西阿": "何西阿書", "約珥": "約珥書", "阿摩司": "阿摩司書",
    "俄巴底亞": "俄巴底亞書", "約拿": "約拿書", "彌迦": "彌迦書",
    "那鴻": "那鴻書", "哈巴谷": "哈巴谷書", "西番雅": "西番雅書",
    "哈該": "哈該書", "撒迦利亞": "撒迦利亞書", "瑪拉基": "瑪拉基書",
    "馬太": "馬太福音", "馬可": "馬可福音", "路加": "路加福音",
    "約翰": "約翰福音", "雅各": "雅各書", "彼得": "彼得前書",
    "猶大": "猶大書",
}


def load_index():
    if not INDEX_FILE.exists():
        print(f"❌ link index 不存在，請先執行 build_link_index.py")
        return {}
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_candidates(book, chapter):
    path = ROOT / book / ".tmp" / f"第{chapter}章" / "link_candidates.md"
    if not path.exists():
        print(f"❌ link_candidates.md 不存在: {path}")
        return []
    text = path.read_text(encoding='utf-8')
    candidates = []
    current_category = None

    for line in text.split('\n'):
        # 偵測類別標題
        m_cat = re.match(r'^##\s+(.*)', line)
        if m_cat:
            current_category = m_cat.group(1).strip()
            continue

        # 格式: - 條目名 → 類別
        m_item = re.match(r'^\s*-\s+(.+?)\s*→\s*(.+)$', line)
        if m_item:
            candidates.append({
                "name": m_item.group(1).strip(),
                "suggested_type": m_item.group(2).strip(),
                "section": current_category
            })
        # 懶人格式: - 條目名
        elif re.match(r'^\s*-\s+(.+)', line) and current_category:
            name = re.match(r'^\s*-\s+(.+)', line).group(1).split('—')[0].strip()
            if name and name not in ['', '不建立']:
                candidates.append({
                    "name": name,
                    "suggested_type": current_category,
                    "section": current_category
                })

    return candidates


def find_in_index(candidate_name, index):
    """
    在 link_index 中尋找 candidate。
    
    回傳 (match_type, matched_entry_dict_or_None)
    
    match_type:
      "exact"       — 完全匹配 index key
      "alias"       — 命中某條目的 aliases 列表
      "conflict"    — 同名但存在多個可能性
      "not_found"   — 未找到
    """
    # 1. 完全匹配
    if candidate_name in index:
        entry = index[candidate_name]
        if "alias_of" in entry:
            # 是別名，指向正式條目
            return ("alias", index.get(entry["alias_of"], entry))
        return ("exact", entry)

    # 2. 檢查 YAML aliases（遍歷 index 中每個條目的 aliases 列表）
    for key, entry in index.items():
        if isinstance(entry, dict) and "alias_of" not in entry:
            aliases = entry.get("aliases", [])
            if isinstance(aliases, str):
                aliases = [aliases]
            if candidate_name in aliases:
                # Candidate 是某條目的 alias → 指向主條目
                return ("alias", entry)

    # 3. 檢查 SAME_PERSON_MAP（同一人物不同命名階段）
    mapped = SAME_PERSON_MAP.get(candidate_name)
    if mapped and mapped in index:
        entry = index[mapped]
        if "alias_of" not in entry:
            return ("exact", entry)

    # 4. 檢查書卷名衝突
    for person, book in PERSON_TO_BOOK.items():
        if candidate_name == person or candidate_name == book:
            # 檢查 index 中是否有對應人物條目
            if person in index:
                return ("conflict", index[person])
            if book in index:
                return ("conflict", index[book])

    return ("not_found", None)


VALID_TYPES = {'人物', '地點', '神學', '主題', '原文', '背景',
               '歷史', '文化', '互文', '解經爭議', '文學結構',
               '節期', '祭祀', '王朝', '預言應驗', '新約引用',
               '聖經神學', '制度'}


def resolve(candidates, index, book, chapter):
    plan = {
        "A_use_directly": [],   # 已存在，直接使用
        "B_needs_update": [],    # 已存在，需要補充
        "C_new_formal": [],      # 不存在，建立正式條目
        "D_new_candidate": [],   # 不存在，建立候選條目
        "E_skip": []             # 不建立
    }

    for c in candidates:
        name_raw = c["name"]
        suggested_type = c["suggested_type"]

        # Step 1: 去除 candidates 中的英文括號註釋
        #   亞伯拉罕（Abraham）→ 亞伯拉罕
        #   亞蘭（Aram/Aramean）→ 亞蘭
        name = re.sub(r'[（(][^）)]*[）)]', '', name_raw).strip()

        # 若去除後為空，保留原始（如條目本身是英文）
        if not name:
            name = name_raw

        c["clean_name"] = name

        # 跳過標記為「不建立」的項目
        if name.startswith('不建立') or name == '暫不建立':
            plan["E_skip"].append(c)
            continue

        # 比對
        match_type, matched = find_in_index(name, index)

        if match_type == "exact":
            # 已存在，需要補充本章資料
            plan["B_needs_update"].append({
                **c,
                "existing_path": matched["path"],
                "existing_title": matched.get("title", name),
                "match_type": "exact"
            })

        elif match_type == "alias":
            # 命中別名 → 指向主條目，需要補充資料
            plan["B_needs_update"].append({
                **c,
                "existing_path": matched["path"],
                "existing_title": matched.get("title", matched.get("name", name)),
                "match_type": "alias",
                "original_candidate": name
            })

        elif match_type == "conflict":
            # 有衝突，放入 D 類讓 Agent 判斷
            plan["D_new_candidate"].append({
                **c,
                "match_type": "conflict",
                "note": f"可能與人物「{name}」或書卷「{PERSON_TO_BOOK.get(name, '?')}」衝突"
            })

        elif match_type == "not_found":
            # 不存在
            if suggested_type.startswith('暫不') or suggested_type == '普通詞':
                plan["E_skip"].append(c)
            elif suggested_type in VALID_TYPES:
                plan["C_new_formal"].append(c)
            else:
                plan["D_new_candidate"].append(c)

    return plan


def write_plan(plan, book, chapter):
    out_dir = ROOT / book / ".tmp" / f"第{chapter}章"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "link_plan.md"

    lines = [f"# 第{chapter}章 link plan\n"]

    if plan["A_use_directly"]:
        lines.append("## A. 使用既有條目（無需更新）\n")
        for c in plan["A_use_directly"]:
            lines.append(f"- [[{c['name']}]] — 已存在，直接使用\n")
        lines.append("")

    if plan["B_needs_update"]:
        lines.append("## B. 需更新既有條目\n")
        for c in plan["B_needs_update"]:
            match_label = ""
            if c.get("match_type") == "alias":
                match_label = f"（由 alias [{c.get('original_candidate', c['name'])}] → {c.get('existing_title', c.get('clean_name', c['name']))}）"
            path = c.get('existing_path', '')
            link_name = c.get('clean_name', c['name'])
            lines.append(f"- [[{link_name}]] → {path}{match_label}\n")
            lines.append(f"  - 動作：補充第{chapter}章資料（{c['suggested_type']}）\n")
        lines.append("")

    if plan["C_new_formal"]:
        lines.append("## C. 新增正式條目\n")
        for c in plan["C_new_formal"]:
            lines.append(f"- [[{c['name']}]] → link_folder/{c['suggested_type']}/{c['name']}.md\n")
        lines.append("")

    if plan["D_new_candidate"]:
        lines.append("## D. 新增候選條目\n")
        for c in plan["D_new_candidate"]:
            note = c.get('note', '')
            if note:
                lines.append(f"- [[{c['name']}]] — {note}\n")
            else:
                lines.append(f"- [[{c['name']}]] — 待確認分類和內容\n")
        lines.append("")

    if plan["E_skip"]:
        lines.append("## E. 不建立 link\n")
        for c in plan["E_skip"]:
            lines.append(f"- {c['name']} — 純文字（{c.get('suggested_type', '')}）\n")
        lines.append("")

    out_file.write_text(''.join(lines), encoding='utf-8')
    print(f"✅ link plan 已建立: {out_file}")

    # 摘要
    print(f"\n📋 摘要：")
    print(f"   A. 已存在直接使用：{len(plan['A_use_directly'])} 條")
    print(f"   B. 需更新既有條目：{len(plan['B_needs_update'])} 條")
    print(f"   C. 新增正式條目：{len(plan['C_new_formal'])} 條")
    print(f"   D. 新增候選條目：{len(plan['D_new_candidate'])} 條")
    print(f"   E. 不建立 link：{len(plan['E_skip'])} 條")

    # B 類詳細
    b_alias = [c for c in plan["B_needs_update"] if c.get("match_type") == "alias"]
    if b_alias:
        print(f"\n📌 注意：以下條目通過 alias 匹配到既有條目：")
        for c in b_alias:
            print(f"   「{c.get('original_candidate', '?')}」→「{c.get('existing_title', '?')}」({c.get('existing_path', '')})")


def main():
    if len(sys.argv) < 3:
        print("用法: python3 resolve_link_candidates.py <書卷名> <章>")
        print("範例: python3 resolve_link_candidates.py 創世記 13")
        sys.exit(1)

    book = sys.argv[1]
    chapter = sys.argv[2]

    index = load_index()
    if not index:
        sys.exit(1)

    candidates = load_candidates(book, chapter)
    if not candidates:
        sys.exit(1)

    print(f"📋 link_candidates 共 {len(candidates)} 條")
    print(f"📋 link_index 共 {len(index)} 條（含別名）")

    plan = resolve(candidates, index, book, chapter)
    write_plan(plan, book, chapter)


if __name__ == "__main__":
    main()
