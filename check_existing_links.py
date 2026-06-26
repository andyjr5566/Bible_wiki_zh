#!/usr/bin/env python3
"""
check_existing_links.py (最終確認模式)

掃描指定章節主檔中的所有 wiki-link，比對 link_folder/ 下已有的條目。
這是 link_plan 流程之後的最終安全網，確認所有引用的既有條目：
  - 在本章中已被檢查過
  - 有補充或已明確標記「無新增內容」

用法（3種模式）：
  1. 列出既有條目清單：
     python3 check_existing_links.py 創世記/第13章.md

  2. 檢查某個條目是否已有本章資料：
     python3 check_existing_links.py 創世記/第13章.md --check 條目名

  3. 顯示未確認的既有條目（尚未有本章資料區塊）：
     python3 check_existing_links.py 創世記/第13章.md --missing
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LINK_FOLDER = ROOT / "link_folder"

def extract_links(filepath):
    text = Path(filepath).read_text(encoding="utf-8")
    targets = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', text)
    return list(dict.fromkeys(targets))

def find_existing(targets):
    existing = []
    for t in targets:
        if '/' in t and not t.startswith('link_folder/'):
            continue
        for md in LINK_FOLDER.rglob('*.md'):
            if '_index' in md.parts:
                continue
            if md.stem == t:
                existing.append((t, str(md.relative_to(ROOT))))
                break
    return existing

def has_chapter_data(entry_path, chapter_tag):
    """檢查條目檔案中是否有本章資料區塊"""
    text = Path(entry_path).read_text(encoding='utf-8')
    return chapter_tag in text

def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 check_existing_links.py <章節主檔路徑>")
        print("  python3 check_existing_links.py <章節主檔路徑> --check <條目名>")
        print("  python3 check_existing_links.py <章節主檔路徑> --missing")
        sys.exit(1)
    
    filepath = ROOT / sys.argv[1]
    if not filepath.exists():
        print(f"❌ 檔案不存在: {filepath}")
        sys.exit(1)
    
    # 從檔名推斷章節標籤，如「第13章」
    chapter_tag = filepath.stem  # e.g. 第13章
    
    targets = extract_links(filepath)
    existing = find_existing(targets)
    
    if sys.argv[-1] == '--missing':
        # 模式3：顯示尚未有本章資料的既有條目
        missing = []
        for name, path in existing:
            abs_path = ROOT / path
            if not has_chapter_data(abs_path, chapter_tag):
                missing.append((name, path))
        
        if not missing:
            print(f"✅ 所有 {len(existing)} 個既有條目都已補充第{chapter_tag}章資料。")
        else:
            print(f"⚠️  以下 {len(missing)} 個既有條目尚未補充第{chapter_tag}章資料：\n")
            for name, path in missing:
                print(f"  - [[{name}]] → {path}")
        return
    
    if sys.argv[-1].startswith('--check'):
        target = sys.argv[-1].replace('--check=', '').replace('--check ', '')
        # 模式2：檢查特定條目
        for name, path in existing:
            if name == target:
                status = "✅ 已有" if has_chapter_data(ROOT / path, chapter_tag) else "⚠️ 尚未補充"
                print(f"{status} 第{chapter_tag}章資料在 [[{name}]] → {path}")
                return
        print(f"❌ 未找到條目: {target}")
        return
    
    # 模式1：列出清單
    if not existing:
        print(f"✅ 第{chapter_tag}沒有引用任何既有條目，無需擴充。")
    else:
        print(f"📋 第{chapter_tag}引用了 {len(existing)} 個既有條目：\n")
        for name, path in existing:
            abs_path = ROOT / path
            status = "✅" if has_chapter_data(abs_path, chapter_tag) else "⚠️ 待補充"
            print(f"  {status} [[{name}]] → {path}")
        
        # 統計
        done = sum(1 for n, p in existing if has_chapter_data(ROOT / p, chapter_tag))
        print(f"\n已補充：{done}/{len(existing)}")

if __name__ == "__main__":
    main()
