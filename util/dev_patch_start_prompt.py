#!/usr/bin/env python3
import re
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "agent_start_prompt.md"
text = PATH.read_text(encoding="utf-8")

step_pattern = re.compile(
    r'5b\. \*\*引句逐字回查（機械，先跑再人工複核）\*\*\n.*?\n6\. \*\*M3/M6 與 B 類內容的勘誤複核（commit 前必做）\*\*',
    re.S,
)
step_replacement = '''5b. **引句字串疑點掃描（review 線索）**
   ```text
   python util/check_quote_fidelity.py 【書名】 X
   ```
   這個工具只用來定位可能需要回查的文字；未命中不等於內容錯誤，也不得為了讓字串比對通過而改寫內容。來源歸屬、翻譯與轉述是否忠實，由 Evidence Reviewer 回到本章正式來源判定。

6. **M3/M6 與 B 類內容的勘誤複核（commit 前必做）**'''

style_pattern = re.compile(
    r'- \*\*英文來源（KingComments、BibleHub）一定要讓中文讀者讀得懂，但「」裡只能放逐字原文。\*\*.*?\n- 不假裝無效來源有效；不為湊條目而亂搜薄弱資料。\n',
    re.S,
)
style_replacement = (
    '- 來源 attribution 必須忠實：標明某一來源時，相關主張必須由該來源支持；翻譯與轉述要保留原意。格式本身不作內容真假的判準。\n'
    '- 不假裝無效來源有效；不為湊條目而亂搜薄弱資料。\n'
)

for label, pattern, replacement in (
    ("step5b", step_pattern, step_replacement),
    ("style", style_pattern, style_replacement),
):
    text, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, got {count}")

PATH.write_text(text, encoding="utf-8")
print("patched agent_start_prompt.md")
