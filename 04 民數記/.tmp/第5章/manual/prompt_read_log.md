# Prompt 讀取回執：民數記 第5章

## manual/entry_batch_1.prompt.md
- 引句：你是聖經研經資料整理員，並且輸出以繁體中文為主。任務：一次為以下 7 個 link_folder 條目各填一份 entry_content payload。
- 引句：- status 一律 formal。accumulations 是「物件陣列」，每項含 book、chapter、summary、relation 四欄，且至少含本章（民數記 第5章）一筆、同章只給一筆。
- 引句：- 互文類條目 name 不可只有經文引用，須用「簡短標題（經文）」，例如「天上真聖所（來9：23-24）」；括號內保留原經文、冒號用全形「：」。

## manual/chapter_content.prompt.md
- 引句：你是聖經研經資料整理員。唯一任務：為 民數記 第5章填寫 chapter_content payload（本章知識節點 + 本章整理）。
- 引句：第二段：本章整理的 markdown 原文，從分隔線下一行直接開始
- 引句：payload 欄位：book, chapter, knowledge_nodes, organization, references。詳見 _config/schemas/chapter_content.schema.json。
