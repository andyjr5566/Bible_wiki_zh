你要完成【{書名} 第{X}章】知識連結流程的前半段——只做到 link_candidates.yaml
定稿＋語義近鄰報告，不要往下跑 run_chapter_manual.py（步驟3以後留給下一手）。

治理規範：完整讀 C:\Obsidian\Hermes\scripture\agent_start_prompt.md 步驟1–2，一切照它走；
所有輸出用繁體中文（英文來源 KC/BH 引用要譯不要貼原文）。

## 步驟1：準備來源
- 經文本地應已有：raw_scripture/{標準書名}/第{X}章.txt（缺檔就停，回報使用者，不要自己編）
- 四套註釋（ccbiblestudy CT/GT、KingComments、BibleHub Study）用既有記錄或目錄頁確認 URL
  （禁止硬猜），缺檔才用 crawl_bible_text.py 補爬；已存在的 raw_data 直接沿用。
- STEP 原文資料缺檔時執行：
    python util/extract_stepbible.py "【{書名}】 {X}" --data_path .stepbible_data --output_path raw_data --download
  STEP 是原文證據層，不是第五套註釋；lexicon 義域／morphology 不可直接當語境義／神學結論。
- manifest 一律用程式產生，不要手寫：
    python util/build_source_manifest.py 【{書名}】 {X}
  標「缺檔」的來源先依狀態提示補 `crawl` 或 `extract` 再重跑，直到五個正式來源都 OK。
- 來源 gate 依 kind 分流：四套 commentary 全文閱讀並在 `.tmp/第{X}章/read_log.md` 留三段逐字引句（至少一段在後 1/3）；STEP 全 raw 由 `python util/check_source_read.py 【{書名}】 {X}` deterministic parser 驗證並留 machine receipt，不做人工逐詞回執。需要原文細節用 `python util/step_context.py 【{書名}】 {X} --verses ...`。

## 步驟2：建 link_candidates.yaml（這是你唯一要做判斷的地方）
- manifest 中四套 OK commentary 全部讀完、STEP machine gate PASS 後才動筆，只放經文或有效 raw text 明確觸發的候選。
- 格式依 _config/schemas/link_candidates.schema.json；分類 type 只能用
  link_folder/ 底下真實存在的資料夾名（主題、事件、互文、人物、原文、地點、
  文化、歷史、神學、背景、解經爭議）——自己造分類會靜默失效，不是報錯。
- name 不可含斜線；一個候選只能對一個條目，涵蓋多詞用 surfaces，不要塞進 name。
- 逐節核對經文用詞：經文用簡稱/裸名時要宣告 surfaces；同詞多義要用
  {phrase, verses} 限定節次。
- 原文類候選的括號音譯／希伯來字母，必須是本章來源實際出現過的拼寫
  （grep -i raw_data 確認），來源沒給就用裸中文名，不可憑常識補配。
- STEP 可觸發原文候選，但仍須有研究／跨章累積／實質內容價值；不得替每個功能詞、詞形或
  Strong 編號批量建頁，Strong 編號不是 wiki ID。四套註釋的共識計數不得把 STEP 算一票。

候選寫齊後，定稿前必跑語義近鄰與重排報告：
    python util/semantic_lookup.py --candidates 【{書名}】 {X}
輸出寫到 .tmp/第{X}章/candidate_similarity.md，資訊都要看並回頭修候選：
  - 字面解析：標「請確認」的多半是 alias 導向錯條目或同名詞歧義（D類），務必人工核實。
  - 治理優先與重排裁判：
    - `✅ 建議使用既有條目 [[條目]]`（確切命中或經校準模型判定高可信且分類相容）→ 若確認為同概念改用既有條目名（走 B 類累積），不要另建近似重複。
    - `⚠ 需 Agent / 人工判斷`（未校準模型、候選相近、分數差距過小、同名歧義或分類不相容）→ 需人工核對上下文判定。
    - `🆕 建議建立新條目`（相關度低）→ 維持 C 類新建。
  - 候選互查 ⚠（本章內兩候選相似 ≥0.8）→ 考慮合併成一個候選（另一詞用 surfaces）。

## 收尾自檢（做完再回報，不要往下跑 run_chapter）
    python util/check_chapter_files.py {書名} {X} --preflight
確認經文、source_manifest.md、link_candidates.yaml、candidate_similarity.md 與 freshness 檢查全數 PASS，
即代表前置包（交接包）備齊，可以交給下一手跑步驟3–8。
回報只列：候選數量、有沒有觸發 ⚠/ⓘ 需要你確認的項目、以及自檢結果。
