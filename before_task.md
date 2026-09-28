你要完成【{書名} 第{X}章】知識連結流程的前半段：只做到 link_candidates.yaml 定稿與候選近鄰報告，
不往下跑 run_chapter_manual.py（步驟3以後留給下一手）。

照 `agent_start_prompt.md` 的步驟1–2 做；原因與排錯細節查 `agent_start_reference.md`，共通規則以
`AGENTS.md` 為準（已自動載入的話不必重讀）。所有輸出用繁體中文。

做完後自檢：

    python util/check_chapter_files.py {書名} {X} --preflight

步驟1–2 的檢查全數 PASS，就代表交接包備齊，可以交給下一手跑步驟3–9。

回報只列：候選數量、`candidate_similarity.md` 開頭摘要裡需要確認的項目、自檢結果。
