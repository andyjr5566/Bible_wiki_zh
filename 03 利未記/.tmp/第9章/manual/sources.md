# Source reading plan

所有正式來源都完整保留於 raw_data，並納入 provenance／validation。

## 必須由 Agent 全文閱讀

### 逐節註解（ccbiblestudy CT）
- path: raw_data/ccbiblestudy_CT_leviticus_9.txt
- url: https://www.ccbiblestudy.org/Old%20Testament/03Lev/03CT09.htm
- validation: human/agent full-read receipt（3 段逐字引句，至少 1 段在後 1/3）

### 拾穗（ccbiblestudy GT）
- path: raw_data/ccbiblestudy_GT_leviticus_9.txt
- url: https://www.ccbiblestudy.org/Old%20Testament/03Lev/03GT09.htm
- validation: human/agent full-read receipt（3 段逐字引句，至少 1 段在後 1/3）

### 研經註解（KingComments）
- path: raw_data/kingcomments_leviticus_9.txt
- url: https://www.kingcomments.com/en/bible-studies/Lev/9
- validation: human/agent full-read receipt（3 段逐字引句，至少 1 段在後 1/3）

### 研經註解（BibleHub Study）
- path: raw_data/biblehub_study_leviticus_9.txt
- url: https://biblehub.com/study/leviticus/9.htm
- validation: human/agent full-read receipt（3 段逐字引句，至少 1 段在後 1/3）

## Structured original-language source

### 原文資料（STEP Bible）
- path: raw_data/stepbible_leviticus_9.txt
- url: https://github.com/STEPBible/STEPBible-Data
- validation: deterministic machine gate（解析、book/chapter、verse coverage、word/Strong/morphology/original script、SHA-256）
- 使用方式: M3/M6 prompt 會提供 task-aware compact projection；需要更多細節時執行 `python util/step_context.py 書名 章 --verses 範圍`。
- 不要求 Agent 為 read receipt 人工逐詞通讀完整 STEP rows；完整 raw source 仍須通過 machine validation。
