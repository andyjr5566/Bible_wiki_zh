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
   - 依 `_config/schemas/link_candidates.schema.json`：`{book, chapter, candidates: [{name, type, evidence?, surfaces?}]}`。
   - 只放經文或有效 raw text 明確觸發的候選；分類用 `link_folder/` 現有資料夾名。
   - **一個候選只能對一個條目，`name` 不可含斜線**。斜線在檔名裡是路徑分隔字元，`entry_content/<name>.yaml` 建不出來，該候選必定同時：surfaces 連不上任何節、knowledge_nodes 對不上而被丟掉、本章累積永遠不寫入、別的條目 related_entries 指向它而被移除——而且全部靜默，三個閘門照過。利1 的「鳥（斑鳩/雛鴿）」就是這樣讓 v14 的斑鳩、雛鴿完全沒連結；真實條目是 `文化/斑鳩.md` 與 `文化/雛鴿.md`，要拆成兩筆。想涵蓋多個詞用 `surfaces`，不要塞進 `name`。（validate 會擋）
   - **`type` 只能是 `link_folder/` 底下真的存在的資料夾**：主題、事件、互文、人物、原文、地點、文化、歷史、神學、背景、解經爭議。自己造一個看起來很合理的分類（利10 的「祭禮」、民9 的「儀式」、民10 的「器具」）會靜默失效——resolver 認不得，只把候選降級成 `D_new_candidate` 並附一句 note「未知分類：X」，那是 plan 檔裡的一行字，不是錯誤，跑完照樣印「✅ 完成」，下場與斜線名完全相同。祭祀相關的歸 `主題`（制度）或 `原文`（術語），器物歸 `主題`／`文化`。（validate 會擋）
   - **逐節核對經文用詞**：程式自動比對候選名、條目全名、括號前裸名與 aliases；經文用這些都對不上的簡稱時（「桌子」→陳設餅桌子），為該候選宣告 `surfaces: [桌子]`。同詞在本章多義用 `{phrase, verses}` 限定節次（出26「幔子」v1-13 是幕幔、v31-33 是內幔 → `surfaces: [{phrase: 幔子, verses: [31,32,33]}]`）。
   - **新建候選前先查語義近鄰**：4300+ 條目裡常有「措辭不同、意思相同」的既有條目，字面比對（resolver）看不出來，硬建就是近似重複（利19 的 7 個主題條目就是這樣被合併善後）。打算新建的候選名先跑 `python util/semantic_lookup.py "候選名"`，若高分近鄰是同一概念，改宣告成那個既有條目名（走 B 類累積），不要另開新條目。此為判斷輔助，不是硬規則——名稱雖近但確為不同概念仍照建。
   - 資料驅動判準見 `scheme.md` §3；語義近鄰索引見 `scheme.md` §3.5。

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
   - **看 `link_plan.yaml` 的 `semantic_hint`**：C（新建）與 D（待判斷）候選若程式附上了語義近鄰既有條目（措辭不同、意思相同者），要回頭確認這個候選是不是其實該連到那個既有條目（改走 B 類累積），而非另建近似重複。這是附註線索、不是自動判定；索引或 embedding 端點不可用時該欄位不出現，流程照跑。門檻與原理見 `scheme.md` §3.5。

6. **收尾驗證與提交**
   ```text
   python util/build_fhl_maps.py
   python util/check_existing_links.py 【序號 書名】/第x章.md --missing
   python util/build_link_index.py
   python util/build_embedding_index.py          # 增量更新語義索引（本章新條目要進索引，下一章才查得到）
   python util/validate_knowledge_base.py
   python util/link_quality_check.py 【書名】
   python util/verify_links.py 【書名】
   python util/audit_knowledge_base.py --check-due
   ```
   全 PASS（條件見 `scheme.md` §6）才 commit + push；回報只列結論數字與 D 類決策，不貼完整報告。
   `build_embedding_index.py` 只重嵌新增／變動的條目（沿用其餘），耗時通常幾秒；embedding 端點不可用時整步可略過，不影響 commit gate（語義索引是輔助，非驗證關卡）。

7. **檔案完整性驗證**（commit 前的最後把關）
   ```text
   python util/check_chapter_files.py 【書名】 X
   ```
   依上述 1–6 的流程順序，逐一檢查每步驟該產生的主要檔案是否存在（`source_manifest.md`、
   `link_candidates.yaml`、`link_plan.yaml`、`entry_content/*.yaml`、`verse_links.yaml`、
   `chapter_content.yaml`、`第x章.md`、`link_updates.yaml`、`util/output/` 下的驗證報告）。
   一旦某檔缺失，程式會停在第一個缺檔處並印出「該回到哪個動作續做」的具體指令
   （例：缺 `link_plan.yaml` → 回步驟3重跑 `run_chapter.py`；缺 `link_updates.yaml`
   → 回步驟4跑 `link_updates.py prepare`）；照該指令補完後，再從那一步依序把後面
   的流程走完，直到本檢查全數 PASS 才 commit + push。

## 行為邊界（內容層，程式無法代勞）

- 一切內容由已收集資料驅動：candidates、summary/relation、條目敘述都必須能對回經文或有效 raw text；來源未提的不寫，不憑神學常識外推。
- **英文來源（KingComments、BibleHub）引用時要譯成繁體中文**，不可整段貼英文原文——本檔開頭已訂「所有輸出用繁體中文」。譯文仍要保留引號與出處（KC：「燔祭一切的價值，就彷彿轉到了他、就是獻祭者身上。」），不要因為要翻譯就退回「KC 指出…」的摘要體。只有在原文用字本身就是重點時（如原文區分 'to burn' 與 'to offer up in smoke'）才以括號附註原文。
- 不假裝無效來源有效；不為湊條目而亂搜薄弱資料。
- 檔案改名一律用 `python util/rename_markdown.py <src> <dst> [--dry-run]`（會同步全庫 WikiLink）。
- 已完成且驗證通過的章節不重做。
