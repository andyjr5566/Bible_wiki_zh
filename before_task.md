你要完成【{書名} 第{X}章】知識連結流程的前半段——只做到 link_candidates.yaml
定稿＋語義近鄰報告，不要往下跑 run_chapter.py（步驟3以後留給下一手）。

治理規範：完整讀 C:\Obsidian\Hermes\scripture\agent_start_prompt.md 步驟1–2，一切照它走；
所有輸出用繁體中文（英文來源 KC/BH 引用要譯不要貼原文）。

## 步驟1：準備來源
- 經文本地應已有：raw_scripture/{標準書名}/第{X}章.txt（缺檔就停，回報使用者，不要自己編）
- 四來源（ccbiblestudy CT/GT、KingComments、BibleHub Study）用既有記錄或目錄頁確認 URL
  （禁止硬猜），缺檔才用 crawl_bible_text.py 補爬；已存在的 raw_data 直接沿用。
- manifest 一律用程式產生，不要手寫：
    python util/build_source_manifest.py 【{書名}】 {X}
  標「缺檔」的來源要先補爬再重跑，直到四來源都 OK。

## 步驟2：建 link_candidates.yaml（這是你唯一要做判斷的地方）
- 四來源全部讀完才動筆，只放經文或有效 raw text 明確觸發的候選。
- 格式依 _config/schemas/link_candidates.schema.json；分類 type 只能用
  link_folder/ 底下真實存在的資料夾名（主題、事件、互文、人物、原文、地點、
  文化、歷史、神學、背景、解經爭議）——自己造分類會靜默失效，不是報錯。
- name 不可含斜線；一個候選只能對一個條目，涵蓋多詞用 surfaces，不要塞進 name。
- 逐節核對經文用詞：經文用簡稱/裸名時要宣告 surfaces；同詞多義要用
  {phrase, verses} 限定節次。
- 原文類候選的括號音譯／希伯來字母，必須是本章來源實際出現過的拼寫
  （grep -i raw_data 確認），來源沒給就用裸中文名，不可憑常識補配。

候選寫齊後，定稿前必跑語義近鄰報告：
    python util/semantic_lookup.py --candidates 【{書名}】 {X}
輸出寫到 .tmp/第{X}章/candidate_similarity.md，三種資訊都要看並回頭修候選：
  - 字面解析預覽：標「請確認」的多半是 alias 導向錯條目，要核實。
  - 對全庫 ⚠（同概念但字面不對）→ 候選名改成既有條目名，不要另建近似重複；
    ⓘ（分類不相容的同實體）→ 連分類一起改用既有條目的。
  - 候選互查 ⚠（本章內兩候選相似 ≥0.8）→ 考慮合併成一個候選（另一詞用 surfaces）。

## 收尾自檢（做完再回報，不要往下跑 run_chapter）
    python util/check_chapter_files.py {書名} {X}
確認 source_manifest.md／link_candidates.yaml／candidate_similarity.md 三者存在
且無缺檔警告，即代表前置包（交接包）備齊，可以交給下一手跑步驟3–8。
回報只列：候選數量、有沒有觸發 ⚠/ⓘ 需要你確認的項目、以及自檢結果。