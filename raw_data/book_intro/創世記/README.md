# 《創世記》書卷導論 prototype

這個資料夾是書卷級 `Introduction.md` pipeline 的第一個完整 prototype。

整體設計規範見根目錄：`introduction_scheme.md`。

公開頁面：`01 創世記/Introduction.md`  
語意 payload：`01 創世記/.tmp/introduction/introduction_content.yaml`  
JSON Schema：`_config/schemas/introduction_content.schema.json`

---

## Prototype 的目標

不是再做一篇「百科式簡介」，也不是把導論拆成固定十幾點，而是讓一般讀者在開始讀《創世記》以前，先建立一個完整而自然的整卷理解：

- 先用一張簡短「一覽」表快速掌握書卷位置、作者／年代框架與大分段；
- 再理解這卷書的名稱與位置；
- 作者、成書與歷史背景應怎麼理解；
- 它主要在講什麼、為什麼要寫；
- 為什麼這卷書重要；
- 全書怎麼展開；
- 哪些經文、鑰字與主題最能抓住整卷；
- 它如何銜接《出埃及記》與後面的聖經。

公開文章必須像一篇真正的「書卷提要／導論」，不是 FAQ、固定資料卡或 AI 帶讀稿。

---

## 寫作主軸：CT00-led，而不是 CT00-template

本 prototype **不是把七個網站平均混在一起重寫**。

CCBibleStudy `CT00` 提供的是主要的**介紹節奏**：先定位書卷，再交代作者與背景，接著說主旨、目的、重要性與特色，最後用關鍵經文與全書結構收束。

但這不代表把 CT00 的「壹、貳、叁……」原封不動變成固定 schema。

> **CT00 決定「怎麼介紹」；其他來源決定「哪些地方值得補充、校正或標示分歧」。**

因此 schema v3 採用可選模組。像《創世記》的「書名」有實際價值就保留；未來《馬太福音》若沒有必要，就不必為了模板硬做同一節。

---

## 來源分層

### 既有四套註釋來源

| ID | 來源 | 角色 |
| --- | --- | --- |
| `CT00` | CCBibleStudy《創世記提要》 | **editorial anchor**；決定正式書卷提要的閱讀節奏 |
| `GT00` | CCBibleStudy《創世記導論拾穗》 | 多家導論合輯；補充結構、研讀本與作者／成書討論；必須保留子來源 |
| `KC0` | KingComments Genesis Introduction | 保守派書卷導論、傳統作者年代、神學脈絡 |
| `BH` | BibleHub Genesis | overview、audience/purpose、genre、structure、book facts |

這四套才延續章級 pipeline 的「四家註釋」角色。

### 外部補強層

| ID | 來源 | 角色 |
| --- | --- | --- |
| `BIBLEPROJECT` | BibleProject Genesis Guide | 文學設計、全書大故事、主題推進 |
| `ENTER_THE_BIBLE` | Luther Seminary / Enter the Bible | 歷史背景、導論議題、神學主題、現代學術觀點 |
| `YALE` | Yale Bible Study | 文類、古代近東背景、來源研究與歷史閱讀限制 |

這三個來源用來增加維度，**不加入 CT／GT／KC／BH 的四家票數**。

---

## 最重要的 provenance 規則

- `CT00` 是最終 Introduction 的敘事章法基準，但不是唯一事實來源。
- `GT00` 是合輯，不可把其中某一位作者的觀點寫成「GT00 一致認為」。
- BibleHub 即使整合多個底層資源，仍只算一個 `BH` 來源家族。
- BibleProject、Enter the Bible、Yale 是不同功能的補強層，不可變成第五、第六、第七家註釋票。
- 作者／年代有分歧時，分開「故事時代、傳統作者歸屬、傳統成書框架、現代文本形成／編輯研究」。
- 不讓 AI 自己把其中一個框架寫成「已證實」的唯一答案。

---

## v3 payload

### `overview`：可選快速一覽

`overview` 不算正文 module，而是 header 後面的快速掃描區。它只放幾個能幫助讀者立即定位書卷的欄位，欄位依書卷而定，不固定數量。

《創世記》目前使用：位置、章數、希伯來書名、希臘書名、**傳統作者歸屬、傳統成書框架**、全書大分段。

有爭議的欄位必須明確標籤，例如寫「傳統作者歸屬」，不能只寫「作者」就把爭議抹掉；完整分歧仍由 `authorship_context` 解釋。

### 內容 modules

Renderer 只接受 `introduction_scheme.md` 定義的允許模組：

```text
identity
authorship_context
message_purpose
importance_features
structure
key_texts_themes
canonical_relationship
```

這些是**內部 module ID**，不是公開頁面的固定七點。

- Renderer 決定模組順序。
- 沒有價值的模組可以省略。
- 公開標題可以依書卷自然調整。
- `authorship_context`、`message_purpose`、`structure` 是一篇可用 Introduction 的最低核心。

---

## 檔案角色

- `source_manifest.yaml`：來源 URL、來源角色、預期資料與 provenance 規則。
- `source_notes.yaml`：人工可讀的正規化來源筆記與跨來源整理；不是網頁全文鏡像。
- `raw/`：crawler 實際執行時產生的清理後來源文字與 receipt；不可由模型手工杜撰。
- `introduction_content.yaml`：跨來源整合完成的語意內容，包含可選 `overview` 與正文 modules。
- `Introduction.md`：renderer 產生、給一般讀者看的最終頁面。
- `_config/schemas/introduction_content.schema.json`：v3 payload 的結構契約。

---

## 執行順序

```powershell
python util/crawl_book_introduction.py "raw_data/book_intro/創世記/source_manifest.yaml" --overwrite

python util/render_book_introduction.py `
  "01 創世記/.tmp/introduction/introduction_content.yaml" `
  --output "01 創世記/Introduction.md" `
  --write --force

python util/check_book_introduction.py `
  "01 創世記/.tmp/introduction/introduction_content.yaml" `
  --manifest "raw_data/book_intro/創世記/source_manifest.yaml" `
  --rendered "01 創世記/Introduction.md"
```

---

## 呈現原則

公開頁面的調性要跟 repo 現有章文一致，同時保留 CT00 那種「正式書卷提要」的閱讀感：

- 開頭可用簡短 `overview` 表讓讀者快速掌握基本資料，但它不能取代正文；
- 正文以連續、自然的導論敘述為主，不寫成聊天式帶讀稿；
- 不大量使用「如果只記一件事」「你可以問自己」「鏡頭拉近」等 AI 常見導讀句型；
- 圖表是輔助，不主導文章章法；
- Mermaid 只在能真正壓縮時間、結構、主線或書卷關係時使用；
- 表格用來快速掃描基本資料、並列不同年代／作者框架、大綱或關鍵經文；
- Obsidian callout 收納容易混淆的概念、爭議層次與補充背景；
- 使用大眾看得懂的繁體中文，不寫成論文，也避免「以下將介紹」「綜上所述」「本節將探討」這類制式 AI 語氣；
- 來源與方法收在折疊 callout，避免破壞正文閱讀節奏。

---

## Prototype 驗收狀態

- [x] CT00 從「固定欄位模板」改為「editorial rhythm」
- [x] schema v3 改為可選模組，不綁固定點數
- [x] 恢復可選的開頭 `overview` 一覽表，且不把欄位固定成模板
- [x] CT00、GT00、KC0、BH 四家來源角色分離
- [x] BibleProject、Enter the Bible、Yale 補強層分離
- [x] 作者／年代分層，不硬裁決
- [x] 全書主旨、結構與正典關係視覺化
- [x] Obsidian callout 與 wiki-link 導航
- [x] `introduction_content.yaml -> Introduction.md` renderer
- [x] provenance / style / deterministic render checker
- [x] `_config/schemas/introduction_content.schema.json`
- [ ] 由可連外的本機／CI 實際執行 crawler，產生 `raw/` 與 `receipt.json`

最後一項刻意保留為 runtime 工作：crawler 必須真的向各來源取回頁面後再產生 receipt，不能由模型假造「已抓取成功」。
