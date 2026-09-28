worker 開工前，這一章要先備齊前置包（`agent_start_prompt.md` 步驟1–2 的產物）：

| 檔案 | 誰產的 | 狀態要求 |
|---|---|---|
| raw_data 四套註釋＋`stepbible_{book}_{chapter}.txt` | crawl_bible_text.py／extract_stepbible.py | source_manifest 都標 OK |
| `.tmp/第x章/source_manifest.md` | build_source_manifest.py | 不可手寫 |
| `.tmp/第x章/read_log.md`＋STEP receipt | 全文閱讀／check_source_read.py | 兩路都 PASS |
| `.tmp/第x章/link_candidates.yaml`、`candidate_existence.md` | 上游判斷定稿 | 候選名無斜線、type 是真實資料夾 |
| `.tmp/第x章/candidate_similarity.md` | semantic_lookup.py --candidates | 候選定稿後才跑，且 fresh |

一行驗證前置包（缺哪步它會指回哪裡）：

    python util/check_chapter_files.py {書名} {X} --preflight

如果它說缺 candidates 或 similarity，代表前置包沒備齊。候選是上游的判斷工作，worker 不自己補。

## Worker 起手 prompt（換 {書名}/{X} 直接貼）

你要接手【{書名} 第{X}章】的知識連結流程。link_candidates.yaml 已由上游定稿，不要重做候選。
照 `agent_start_prompt.md` 的步驟3–9 把這章做完並驗證通過；原因與排錯細節查
`agent_start_reference.md`，共通規則以 `AGENTS.md` 為準（已自動載入的話不必重讀）。
所有輸出用繁體中文。

開工前先跑 `python util/check_chapter_files.py {書名} {X} --preflight`；若缺 candidates 或
similarity，停下回報上游。
