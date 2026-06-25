#!/usr/bin/env python3
"""
check_existing_links.py
掃描指定章節主檔中的所有 wiki-link，
比對 link_folder/ 下已有的條目，列出需要擴充的既有條目。

用法：
  python3 check_existing_links.py 創世記/第12章.md
"""
import re, sys, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LINK_FOLDER = ROOT / "link_folder"

def extract_links(filepath):
    """從 markdown 檔案中提取所有 wiki-link target"""
    text = Path(filepath).read_text(encoding="utf-8")
    # [[target|alias]] 或 [[target]]
    targets = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', text)
    # 去除路徑前綴（如 創世記/第8章 → 只看條目名）
    return list(dict.fromkeys(targets))  # 去重保序

def find_existing(targets):
    """檢查 link_folder/ 下哪些 target 已存在"""
    existing = []
    for t in targets:
        # 跳過章節連結（如 創世記/第8章）
        if '/' in t and not t.startswith('link_folder/'):
            continue
        # 在 link_folder/ 下遞迴搜尋
        for md in LINK_FOLDER.rglob('*.md'):
            if md.stem == t:
                existing.append((t, str(md.relative_to(ROOT))))
                break
    return existing

def main():
    if len(sys.argv) < 2:
        print("用法: python3 check_existing_links.py <章節主檔路徑>")
        sys.exit(1)
    
    filepath = ROOT / sys.argv[1]
    if not filepath.exists():
        print(f"檔案不存在: {filepath}")
        sys.exit(1)
    
    targets = extract_links(filepath)
    existing = find_existing(targets)
    
    if not existing:
        print("✅ 本章沒有引用任何既有條目，無需擴充。")
    else:
        print(f"📋 本章引用了 {len(existing)} 個既有條目，需要逐一檢查並擴充：\n")
        for name, path in existing:
            print(f"  - [[{name}]] → {path}")

if __name__ == "__main__":
    main()
