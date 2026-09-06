# Book Introduction Scheme

本檔定義書卷級 `Introduction.md` 的設計原則、來源角色、內容編排與 production pipeline。
它與 `scheme.md` 的章節流程並行，但處理的是「整卷書的導論」，不是單章註解。

核心原則仍然是：**模型不碰結構，程式不碰內容。**

Introduction 的目標不是把各網站導論剪貼成百科，也不是做制式的「十點／十二點簡介」。它要讓一般讀者在開始讀一卷書以前，先知道這卷書是什麼、在什麼背景下形成、主要在講什麼、為什麼重要、全書怎麼展開，以及它在整本聖經裡扮演什麼角色。

---

## 編排基準：學 CT00 的介紹方法，不抄它的欄位數

CCBibleStudy 的 CT00 是本專案書卷導論的**主要編輯參考**。

最值得沿用的不是「壹、貳、叁……」本身，而是它建立理解的順序：

```text
先讓讀者認識這卷書
→ 交代作者、年代、受者與背景
→ 說明主旨與寫作目的
→ 解釋這卷書為什麼重要、有什麼特色
→ 用關鍵經文／主題與全書大綱收束
→ 放回前後書卷與整本聖經
```

這是**閱讀邏輯**，不是固定欄位。

不同書卷可以省略、合併或增加模組：

- 《創世記》的書名本身很有意義，可以說明 `Bereshith / Genesis`。
- 《馬太福音》不必為了模板硬做「書名」段落。
- 《馬可福音》的「原始受者」特別重要，可以在背景中加重。
- 《詩篇》需要談詩歌體裁、編纂與五卷結構，不能照歷史書的方式寫。
- 書信需要清楚交代收信人、寫信情境與問題。
- 先知書常需要把先知活動年代、君王、政治背景與信息對象放在前面。

**因此 Introduction 沒有固定 H2 數量，也沒有固定 11 點或 12 點。**

整體只遵守三層閱讀方向：

```text
定位這卷書
→ 理解這卷書
→ 放回整本聖經
```

「定位」可包含書名、作者、年代、受者與背景；「理解」可包含主旨、目的、重要性、特色、結構與關鍵主題；「放回整本聖經」則處理前後書卷、互文與正典位置。實際公開標題由書卷內容決定，不要求三層名稱直接出現在頁面上。

---

## 來源架構

### 四套既有註釋來源

沿用專案既有四個 commentary 維度：

- `CT00` — CCBibleStudy 提要
- `GT00` — CCBibleStudy 導論拾穗
- `KC0` — KingComments book introduction
- `BH` — BibleHub book overview / study resources

Introduction 的文章編排以 **CT00 為 editorial anchor**，但這不表示 CT00 在事實爭議上自動擁有最高權威。

> **CT00 決定「怎麼介紹」，不是單獨決定「什麼一定是真的」。**

### 外部補強層

《創世記》prototype 使用：

- `BIBLEPROJECT` — 文學設計、段落推進、整本聖經主線
- `ENTER_THE_BIBLE` — 歷史背景、文類、現代研究與成書議題
- `YALE` — 主流學術閱讀、古代近東背景、來源／編輯研究史

這些是**補強維度**，不是第五、六、七個 commentary vote。

未來其他書卷若某一網站沒有對應資料，不需要硬找一個替代來源才能 production；source manifest 應明確標示 `available / unavailable / optional`。

### STEP Bible

STEP 維持獨立的原文證據層，只在 Introduction 確實需要時使用，例如：

- 希伯來／希臘書名來自首字或固定稱呼；
- 全書高度重複的關鍵詞；
- 某個「鑰字」的原文需要確認；
- 需要避免中文翻譯造成誤導。

STEP 不加入四套註釋共識票數，也不因詞典義域就自行推出神學結論。

---

## Provenance 與分歧處理

### GT00 保留子來源

GT00 是導論／研讀資料合輯。若一個觀點只出現在其中某一位作者或某一本研讀本，`source_notes.yaml` 必須保留該子來源名稱；不得把單一子來源寫成「GT00 一致認為」。

### BibleHub 是一個來源家族

即使 BibleHub 頁面整合多種底層資源，在四家統計中仍只算 `BH` 一個維度。若使用其中具名資源，可以在 provenance 中標出，但不能增加票數。

### 作者與年代分層

遇到有爭議的作者、年代、編輯與文本形成問題時，視來源需要區分：

```text
故事／事件所描寫的年代
傳統作者歸屬
傳統成書框架
材料傳承或編輯模型
現有／最終文本形成的研究觀點
```

不是每卷都要把這些層次全部寫出來。只有來源確實提出，而且對一般讀者有幫助時才寫。

寫作上優先使用：「傳統上……」、「部分現代研究者則……」、「學界對具體年代仍有不同模型……」、「這兩種說法回答的問題層次不同……」。避免把單一學派重建寫成沒有爭議的事實，也避免用 STEP 或某一來源去粗暴裁決另一個證據層。

---

## 公開文章的內容結構

### 開頭「一覽」表：可選，但很有價值

在標題與一小段總介之後，可以放一張簡短的 `overview` 表格，讓讀者在十幾秒內先掌握這卷書最基本的定位。

它的作用是**快速掃描**，不是另一套 Introduction，也不是固定欄位模板。欄位依書卷而定；常見可用資料包括位置、章數、原文／通行書名、傳統作者歸屬、傳統成書框架、原始受者、主要時代、全書大分段等，但只放真正有用且來源可確認的項目。

《創世記》prototype 採用：位置、章數、希伯來書名、希臘書名、傳統作者歸屬、傳統成書框架、全書大分段。這不是後續書卷必須照抄的七欄。

若某欄本身有重大爭議，`overview` 只能用清楚限定過的簡短寫法，例如「**傳統作者歸屬：摩西**」，不能把學術分歧壓成一個沒有標籤的答案。完整的傳統／現代研究分層仍放在 `authorship_context` 正文與詳細表格中。

換句話說：

> **一覽表回答「先讓我快速知道這卷書是什麼」；正文回答「這些資料應該怎麼理解」。**

### 內容模組

`introduction_content.yaml` 使用**固定允許模組、彈性出現**的方式。Renderer 決定模組順序；沒有資料價值的模組可以完全省略。

允許模組：

```text
identity                # 書名／位置；可省略
authorship_context      # 作者、年代、受者、歷史與文學背景
message_purpose         # 主旨與寫作目的
importance_features     # 重要性與特色
structure               # 全書結構／內容大綱
key_texts_themes        # 鑰節、鑰字、核心主題
canonical_relationship  # 與其他書卷／整本聖經的關係；可省略
```

這些是**內部 module ID**，不是要求公開頁面出現七個制式標題。

例如 `authorship_context` 在《創世記》可顯示成「作者、成書與背景」；在保羅書信可以自然呈現為「作者、收信人與寫作處境」；在《詩篇》可能改成「作者、編纂與詩篇集的形成」。

**`overview` 不算內容 module。** 它固定出現在 header 後、第一個正文 module 前；沒有適合的快速資料時可以完全省略。

**module 順序由 renderer 決定，model/agent 不得自行重排。**

---

## 寫作與視覺風格

Introduction 面向一般讀者，但不是兒童教材，也不是 AI 導讀文。

正文應像一位熟悉材料的人在正式介紹一卷書：先講清楚，再講深入；段落有承接；使用自然的繁體中文；專有名詞第一次出現時簡單解釋；有來源分歧時自然地放進正文或 callout，不另寫成稽核報告。

避免密集使用「如果只記一件事……」「你有沒有想過……」等 AI 導讀句型，不把 Introduction 寫成 FAQ，也不要為了活潑而過度口語化。

### Obsidian / Markdown

圖表是**壓縮複雜資訊**的工具，不是裝飾。

Mermaid 適合：

- 全書敘事／論證主線
- 大段落結構
- 時序
- 人物／家族／王朝關係
- 地理移動的概念路線
- 與前後書卷或正典的銜接

表格適合：

- 開頭的書卷基本資料一覽
- 作者／年代不同觀點的並列
- 大綱與章節範圍
- 關鍵經文與其功能
- 書卷群組的對照

Callout 適合：

- 容易混淆的概念
- 傳統／學術觀點的分層
- 閱讀提醒
- 不值得打斷正文主線的補充背景

原則：

- 沒有實際降低理解成本，就不用圖。
- Mermaid 一張圖只回答一個問題。
- 不把整段文章原封不動再畫成流程圖。
- 正文拿掉所有圖表後，仍必須是一篇完整、連續、可讀的導論。
- Introduction 不自行批量建立 `link_folder` 條目；wiki-link 只連到已存在且語義確定的條目／章節。

---

## Production pipeline

```text
canonical book registry
→ 建立 book-level source_manifest.yaml
→ crawl_book_introduction.py 抓取可用來源
→ raw/*.txt + receipt.json
→ Agent 全文閱讀，產出 source_notes.yaml
→ provenance / role check
→ Agent 依 introduction prompt 填 introduction_content.yaml
→ check_book_introduction.py 檢查來源 ID、角色、爭議分層與 payload
→ render_book_introduction.py
→ Introduction.md
→ deterministic rendered equality check
→ 人工 review（內容、文風、圖表）
→ 通過後才 merge / 推進下一卷
```

### `source_manifest.yaml`

記錄來源 URL、role、availability、是否為 editorial anchor，以及 GT00 / BH 等特殊 provenance 規則。外部補強網址未必能靠固定 slug 推導，因此由 canonical registry 或 per-book override 管理，不讓 crawler 猜網址。

### `source_notes.yaml`

保存各來源實際說了什麼、可核對事實、來源特有觀點、分歧、GT00 子來源 provenance，以及可供 final article 使用的背景資訊。它不是公開文章。

### `introduction_content.yaml`

保存已完成跨來源整合的 public-facing 內容，以及 overview、每段、表格、圖表對應的 `source_ids`。它不負責 Markdown 排版。

### `Introduction.md`

只負責給讀者閱讀，不承擔 research log。它必須由 renderer deterministic 產生。

---

## Gate 與 rollout

每卷至少確認：

- manifest 的 URL 與 role 合法；
- content 使用的 source ID 全部存在；
- 四家 commentary 與外部補強來源沒有混票；
- GT00 合輯觀點沒有失去子來源；
- 作者／年代等重大分歧沒有被硬壓成單一結論；
- 若有 `overview`，其中爭議資料必須帶有「傳統／研究」等必要限定，不冒充單一確定答案；
- `Introduction.md` 可由 payload deterministic render；
- 文章沒有被固定點數模板綁死；
- 視覺元素真的降低理解成本；不強制每卷一定有 Mermaid；
- wiki-link 指向已存在目標；
- 人工確認文風不是 AI FAQ／清單式導讀。

《創世記》是第一階段唯一 prototype。在它的文章、圖表、provenance 與 schema 都確認後，再用同一套 scheme 測試一卷**不同文類**的書；建議下一個測《詩篇》或《馬可福音》。若這兩種文類也能自然套用，再考慮批量推進其他書卷。
