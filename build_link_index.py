#!/usr/bin/env python3
"""
build_link_index.py
掃描全域 link_folder/，產生 link_folder/_index/link_index.json

用法：
  python3 build_link_index.py

輸出：
  link_folder/_index/link_index.json
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LINK_FOLDER = ROOT / "link_folder"
INDEX_DIR = LINK_FOLDER / "_index"
INDEX_FILE = INDEX_DIR / "link_index.json"

def parse_frontmatter(text):
    """簡易 frontmatter parser"""
    fm = {}
    m = re.match(r'^---\s*\n(.*?)\n---', text, re.DOTALL)
    if m:
        for line in m.group(1).split('\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                fm[key.strip()] = val.strip()
    return fm

def build_index():
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    
    index = {}
    for md in sorted(LINK_FOLDER.rglob('*.md')):
        if '_index' in md.parts:
            continue
        text = md.read_text(encoding='utf-8')
        fm = parse_frontmatter(text)
        
        relative = md.relative_to(ROOT)
        category = md.parent.name  # e.g. 人物, 神學
        
        entry = {
            "path": str(relative).replace('\\', '/'),
            "type": category,
            "title": md.stem,
            "status": fm.get("status", "candidate"),
            "aliases": []
        }
        
        # 從 frontmatter 提取別名（如果有 alias 欄位）
        if "aliases" in fm:
            aliases = fm["aliases"].strip().strip('[]').replace('"', '').replace("'", '')
            entry["aliases"] = [a.strip() for a in aliases.split(',') if a.strip()]
        
        # 同時用完整名稱和別名作為 key
        index[md.stem] = entry
        for alias in entry["aliases"]:
            if alias not in index:
                index[alias] = {"alias_of": md.stem}
    
    INDEX_FILE.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"✅ link index 已建立: {INDEX_FILE}")
    print(f"   共 {len(index)} 個條目（含別名）")

if __name__ == "__main__":
    build_index()
