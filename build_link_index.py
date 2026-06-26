#!/usr/bin/env python3
"""
build_link_index.py — 掃描全域 link_folder/，產生 link_folder/_index/link_index.json

掃描時讀取每個 markdown 檔案的 YAML frontmatter，提取：
  - type: 主分類
  - secondary_types: 次分類（可選，列表）
  - aliases: 別名（可選，列表）
  - status: formal 或 candidate

輸出：
  link_folder/_index/link_index.json

用法：
  python3 build_link_index.py
"""
import json
import yaml
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LINK_FOLDER = ROOT / "link_folder"
INDEX_DIR = LINK_FOLDER / "_index"
INDEX_FILE = INDEX_DIR / "link_index.json"


def extract_frontmatter(text):
    """完整解析 YAML frontmatter，回傳 dict；無 frontmatter 回傳空 dict"""
    m = re.match(r'^---\s*\n(.*?)\n---', text, re.DOTALL)
    if not m:
        return {}
    try:
        fm = yaml.safe_load(m.group(1))
        if isinstance(fm, dict):
            return fm
        return {}
    except yaml.YAMLError:
        return {}


def build_index():
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    index = {}

    # 排除檔案
    EXCLUDE_PARTS = {'_index', '_管理', '_待分類', '_template'}

    for md in sorted(LINK_FOLDER.rglob('*.md')):
        # 跳過管理/模板/暫存
        if EXCLUDE_PARTS & set(md.parts):
            continue

        text = md.read_text(encoding='utf-8')
        fm = extract_frontmatter(text)

        relative = md.relative_to(ROOT)
        category = md.parent.name  # 人物, 神學, 主題 ...

        # --- 主要條目 ---
        entry = {
            "path": str(relative).replace('\\', '/'),
            "type": fm.get("type", category),           # frontmatter type 優先，否則用資料夾名
            "secondary_types": fm.get("secondary_types", []),
            "title": md.stem,
            "status": fm.get("status", "candidate"),     # 預設 candidate
            "aliases": fm.get("aliases", []),
        }

        # 確保 aliases 是 list
        if isinstance(entry["aliases"], str):
            entry["aliases"] = [entry["aliases"]]
        if isinstance(entry["secondary_types"], str):
            entry["secondary_types"] = [entry["secondary_types"]]

        index[md.stem] = entry

        # --- 別名指向主條目 ---
        for alias in entry["aliases"]:
            if alias and alias not in index:
                index[alias] = {"alias_of": md.stem}

        # --- secondary_types 也建立指向 ---
        for st in entry["secondary_types"]:
            if st and st not in index:
                index[st] = {"alias_of": md.stem, "via_secondary_type": True}

    # 寫入
    INDEX_FILE.write_text(
        json.dumps(index, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )

    # 統計
    formal_count = sum(
        1 for v in index.values()
        if isinstance(v, dict) and v.get("status") == "formal"
    )
    candidate_count = sum(
        1 for v in index.values()
        if isinstance(v, dict) and v.get("status") == "candidate"
    )
    alias_count = sum(
        1 for v in index.values()
        if isinstance(v, dict) and "alias_of" in v
    )

    print(f"✅ link index 已建立: {INDEX_FILE}")
    print(f"   共 {len(index)} 條（含別名）")
    print(f"   ├─ 正式條目: {formal_count}")
    print(f"   ├─ 候選條目: {candidate_count}")
    print(f"   └─ 別名指向: {alias_count}")


if __name__ == "__main__":
    build_index()