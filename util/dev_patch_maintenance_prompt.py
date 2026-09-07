#!/usr/bin/env python3
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "agent_maintenance_prompt.md"
text = path.read_text(encoding="utf-8")
old = '''- **內容**：直接引原話「」並標對哪一家（CT／GT／KC／BH 或 GT 內各家），不張冠李戴、
  某家沒說就別替他生一個；矛盾並陳不壓平；英文來源譯成繁中不貼原文；只出自經文與來源。
'''
new = '''- **內容**：所有主張都要能回查經文或正式來源；標明某一家時不可張冠李戴，來源未提就不要歸給它；
  有分歧時忠實並陳，不把彼此不同的解讀壓成同一說法。
'''
if text.count(old) != 1:
    raise SystemExit(f"expected exactly one match, got {text.count(old)}")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
print("patched agent_maintenance_prompt.md")
