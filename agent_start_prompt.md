# Agent Start Prompt

處理書卷章節時，流程由程式主導（`util/run_chapter.py`），你只負責「準備輸入、填內容、處理人工決策點」。設計原則與決策記錄見 `scheme.md`；所有輸出用繁體中文。

## 每章流程

1. **準備來源**（章節的 `.tmp` 資料夾：`【序號 書名】/.tmp/第x章/`）
   - 經文已在本地：`raw_scripture/{標準書名}/第{章}.txt`（缺檔即停，回報使用者）。
   - 每個補充來源（ccbiblestudy CT/GT、KingComments、BibleHub Study）用既有記錄或目錄頁確認 URL（禁止硬猜），執行：
     `python util/crawl_bible_text.py "{URL}" --output_path raw_data --output_filename "{source}_{book_slug}_{chapter}"`
     已存在的 raw_data 檔直接沿用，不加 `--overwrite`。
   - 檢查每份 raw text 是否為本章有效內容（404／目錄頁／亂碼／無關＝無效），寫 `source_manifest.md`（表格欄位：來源｜類型｜URL｜raw_data 檔案｜狀態）。狀態 OK 者才會被程式使用；無效來源照實記錄。

2. **建 link_candidates.yaml**（唯一由你判斷「哪些詞值得成為知識節點」的步驟）
   - 依 `_config/schemas/link_candidates.schema.json`：`{book, chapter, candidates: [{name, type, evidence?}]}`。
   - 只放經文或有效 raw text 明確觸發的候選；分類用 `link_folder/` 現有資料夾名。
   - 資料驅動判準見 `scheme.md` §3。

3. **跑 orchestrator**（結構、渲染、驗證全由程式處理）
   ```text
   python util/build_link_index.py
   python util/run_chapter.py 【書名】 X
   ```
   程式會：解析候選（A–E 類）→ 批量請模型填條目 payload → 程式化標注經文 wiki-link → 模型填本章整理 → 渲染全部 markdown → 結構驗證。模型端點用 `python util/model_client.py list|use|test` 檢查或切換。

4. **B 類累積**（既有條目補本章資料）
   ```text
   python util/link_updates.py prepare 【書名】 X
   ```
   回到經文與有效 raw text 填 `link_updates.yaml` 的 `summary`／`relation`，先 `apply --dry-run` 再 `apply`；重跑 apply 必須 0 變更。

5. **處理人工決策點**：run_chapter 回報的 `manual_review` 項目，與 `link_plan.yaml` 的 D 類（同名衝突、分類衝突）。D 類不得自動建立或連結；判斷後修 candidates 或人工建檔再續跑（run_chapter 可斷點續跑，已完成的步驟不重做）。

6. **收尾驗證與提交**
   ```text
   python util/build_fhl_maps.py
   python util/check_existing_links.py 【序號 書名】/第x章.md --missing
   python util/build_link_index.py
   python util/validate_knowledge_base.py
   python util/link_quality_check.py 【書名】
   python util/verify_links.py 【書名】
   python util/audit_knowledge_base.py --check-due
   ```
   全 PASS（條件見 `scheme.md` §6）才 commit + push；回報只列結論數字與 D 類決策，不貼完整報告。

## 行為邊界（內容層，程式無法代勞）

- 一切內容由已收集資料驅動：candidates、summary/relation、條目敘述都必須能對回經文或有效 raw text；來源未提的不寫，不憑神學常識外推。
- 不假裝無效來源有效；不為湊條目而亂搜薄弱資料。
- 檔案改名一律用 `python util/rename_markdown.py <src> <dst> [--dry-run]`（會同步全庫 WikiLink）。
- 已完成且驗證通過的章節不重做。
