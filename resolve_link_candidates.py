#!/usr/bin/env python3
"""
resolve_link_candidates.py
將 link_candidates.md 與 link_index.json 比對，
產生 link_plan.md

用法：
  python3 resolve_link_candidates.py <書卷名> <章>

例如：
  python3 resolve_link_candidates.py 創世記 13

流程：
  1. 讀取 link_folder/_index/link_index.json
  2. 讀取 .tmp/第x章/link_candidates.md
  3. 逐條比對，分為五類：
     A. 已存在 → 直接使用
     B. 已存在 → 需要補充本章資料
     C. 不存在 → 建立正式條目
     D. 不存在 → 建立候選條目
     E. 不應建立 link → 純文字
  4. 寫入 .tmp/第x章/link_plan.md
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX_FILE = ROOT / "link_folder" / "_index" / "link_index.json"

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
        
        # 偵測條目 - 格式: - 條目名 → 類別
        m_item = re.match(r'^\s*-\s+(.+?)\s*→\s*(.+)$', line)
        if m_item:
            candidates.append({
                "name": m_item.group(1).strip(),
                "suggested_type": m_item.group(2).strip(),
                "section": current_category
            })
        # 懶人格式: - 條目名（不帶箭頭時推斷為前一個類別）
        elif re.match(r'^\s*-\s+(.+)', line) and current_category:
            name = re.match(r'^\s*-\s+(.+)', line).group(1).split('—')[0].strip()
            if name and name not in ['', '不建立']:
                candidates.append({
                    "name": name,
                    "suggested_type": current_category,
                    "section": current_category
                })
    
    return candidates

def resolve(candidates, index, book, chapter):
    plan = {
        "A_use_directly": [],      # 已存在，直接使用
        "B_needs_update": [],       # 已存在，需要補充
        "C_new_formal": [],         # 不存在，建立正式條目
        "D_new_candidate": [],      # 不存在，建立候選條目
        "E_skip": []                # 不建立
    }
    
    for c in candidates:
        name = c["name"]
        suggested_type = c["suggested_type"]
        
        # 跳過標記為「不建立」的項目
        if name.startswith('不建立') or name == '暫不建立':
            plan["E_skip"].append(c)
            continue
        
        # 完全匹配
        if name in index:
            entry = index[name]
            if "alias_of" in entry:
                # 是別名，指向正式名稱
                plan["B_needs_update"].append({
                    **c,
                    "existing_path": index[entry["alias_of"]]["path"],
                    "existing_title": entry["alias_of"]
                })
            else:
                plan["B_needs_update"].append({
                    **c,
                    "existing_path": entry["path"],
                    "existing_title": entry.get("title", name)
                })
        else:
            # 不存在
            if suggested_type.startswith('暫不') or suggested_type == '普通詞':
                plan["E_skip"].append(c)
            elif suggested_type in ('人物', '地點', '神學', '主題', '原文', '背景', '歷史', '文化', '互文', '解經爭議'):
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
        lines.append("## 使用既有條目（無需更新）\n")
        for c in plan["A_use_directly"]:
            lines.append(f"- [[{c['name']}]] — 已存在，直接使用\n")
        lines.append("")
    
    if plan["B_needs_update"]:
        lines.append("## 更新既有條目\n")
        for c in plan["B_needs_update"]:
            links = c.get('existing_path', '')
            lines.append(f"- [[{c['name']}]] → {links}\n")
            lines.append(f"  - 動作：補充第{chapter}章資料（{c['suggested_type']}）\n")
        lines.append("")
    
    if plan["C_new_formal"]:
        lines.append("## 新增正式條目\n")
        for c in plan["C_new_formal"]:
            lines.append(f"- [[{c['name']}]] → link_folder/{c['suggested_type']}/{c['name']}.md\n")
        lines.append("")
    
    if plan["D_new_candidate"]:
        lines.append("## 新增候選條目\n")
        for c in plan["D_new_candidate"]:
            lines.append(f"- [[{c['name']}]] — 待確認分類和內容\n")
        lines.append("")
    
    if plan["E_skip"]:
        lines.append("## 不建立 link\n")
        for c in plan["E_skip"]:
            lines.append(f"- {c['name']} — 純文字（{c.get('suggested_type', '')}）\n")
        lines.append("")
    
    out_file.write_text(''.join(lines), encoding='utf-8')
    print(f"✅ link plan 已建立: {out_file}")
    
    # 同時顯示摘要
    print(f"\n📋 摘要：")
    print(f"   A. 已存在直接使用：{len(plan['A_use_directly'])} 條")
    print(f"   B. 需更新既有條目：{len(plan['B_needs_update'])} 條")
    print(f"   C. 新增正式條目：{len(plan['C_new_formal'])} 條")
    print(f"   D. 新增候選條目：{len(plan['D_new_candidate'])} 條")
    print(f"   E. 不建立 link：{len(plan['E_skip'])} 條")

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
    print(f"📋 link_index 共 {len(index)} 條")
    
    plan = resolve(candidates, index, book, chapter)
    write_plan(plan, book, chapter)

if __name__ == "__main__":
    main()