# Book Introduction Scheme

本檔定義書卷級 `Introduction.md` 的設計原則、來源角色、內容編排與 production pipeline。
它與 `scheme.md` 的章節流程並行，但處理的是「整卷書的導論」，不是單章註解。

核心原則仍然是：**模型不碰結構，程式不碰內容。**

Introduction 的目標不是把各網站導論剪貼成百科，也不是做制式的「十點／十二點簡介」。
它要讓一般讀者在開始讀一卷書以前，先知道：

- 這卷書是什麼；
- 它大約在什麼歷史、文學與正典位置上；
- 傳統與研究界如何理解作者、年代與背景；
- 全書最主要在講什麼；
- 為什麼這卷書重要；
- 全書怎麼展開，讀的時候應抓住哪些主線。

---

## 1. 編排基準：學 CT00 的「介紹方法」，不是抄它的欄位數

CCBibleStudy 的 CT00 是本專案書卷導論的**主要編輯參考**。
它最值得沿用的不是「壹、貳、叁……」本身，而是它建立理解的順序：

```text
先讓讀者認識這卷書
→ 再交代作者、年代、受者與背景
→ 接著說明主旨與寫作目的
→ 再回答這卷書為什麼重要、有什麼特色
→ 最後用關鍵經文／主題與全書大綱收束
```

這個順序是**閱讀邏輯**，不是固定欄位。

不同書卷可以省略、合併或增加模組：

- 《創世記》的書名本身很有意義，可以獨立說明 `Bereshith / Genesis`。
- 《馬太福音》不必為了模板硬做「書名」段落。
- 《馬可福音》的「原始受者」特別重要，可以在背景中加重。
- 《詩篇》需要談詩歌體裁、編纂與五卷結構，不能照歷史書的方式寫。
- 書信需要清楚交代收信人、寫信情境與問題。
- 先知書可能需要把先知活動年代、君王、政治背景與信息對象放在前面。

**因此 Introduction 沒有固定 11 點、12 點或固定 H2 數量。**

---

## 2. 三層閱讀邏輯

所有 Introduction 都沿著三個閱讀層次往前，但實際標題依書卷調整。

### A. 先定位這卷書

可用模組：

- 書名與名稱來源（有實際價值時）
- 作者／傳統作者歸屬
- 成書年代與地點
- 原始受者
- 歷史、文化與文學背景
- 故事發生年代與文本成書年代的區分

這一層的功能是回答：**「我現在打開的是什麼書？」**

### B. 再理解這卷書

可用模組：

- 主旨要義
- 寫作目的／寫作動機
- 本書的重要性
- 本書的特色
- 文學設計
- 全書結構／內容大綱
- 關鍵經文、鑰字、重複母題

這一層的功能是回答：**「它到底要帶我看什麼？」**

### C. 最後放回整本聖經

可用模組：

- 與前後書卷的銜接
- 在摩西五經／歷史書／智慧書／先知書／福音書／書信等群組中的位置
- 重要互文與後續發展
- 基督教、猶太教或學術傳統中特別重要的閱讀問題（有需要才出現）

這一層的功能是回答：**「它在整本聖經裡扮演什麼角色？」**

---

## 3. 來源架構

### 3.1 四套既有註釋來源

沿用專案既有四個 commentary 維度：

1. `CT00` — CCBibleStudy 提要
2. `GT00` — CCBibleStudy 導論拾穗
3. `KC0` — KingComments book introduction
4. `BH` — BibleHub book overview / study resources

Introduction 的文章編排以 **CT00 為 editorial anchor**，但這不表示 CT00 在事實爭議上自動擁有最高權威。

換句話說：

> **CT00 決定「怎麼介紹」，不是單獨決定「什麼一定是真的」。**

### 3.2 外部補強層

Prototype 使用：

- `BIBLEPROJECT` — 文學設計、段落推進、整本聖經主線
- `ENTER_THE_BIBLE` — 歷史背景、文類、現代研究與成書議題
- `YALE` — 主流學術閱讀、古代近東背景、來源／編輯研究史

這些是**補強維度**，不是第五、六、七個 commentary vote。

未來其他書卷若某一網站沒有對應資料，不需要硬補一個替代來源才能 production；source manifest 必須明確標示 `available / unavailable / optional`。

### 3.3 STEP Bible

STEP 仍維持獨立的原文證據層，只在 Introduction 確實需要時使用，例如：

- 希伯來／希臘書名來自首字或固定稱呼；
- 全書高度重複的關鍵詞；
- 某個「鑰字」的原文需要確認；
- 需要避免中文翻譯造成誤導。

STEP 不加入四套註釋共識票數，也不因詞典義域就自行推出神學結論。

---

## 4. Provenance 與分歧規則

### 4.1 GT00 必須保留子來源

GT00 是導論／研讀資料合輯。若一個觀點只出現在其中某一位作者或某一本研讀本：

- source note 必須保留該子來源名稱；
- 不得寫成「GT00 認為……」或「多數來源一致……」。

### 4.2 BibleHub 是一個來源家族

即使 BibleHub 頁面整合多種底層資源，在專案的四家統計中仍只算 `BH` 一個維度。
若使用其中具名資源（例如某一 study Bible 或 commentary），可在 provenance 中標出，但不能增加票數。

### 4.3 作者與年代不能只剩一個答案

遇到有爭議的作者、年代、編輯與文本形成問題時，至少區分：

```text
故事／事件所描寫的年代
傳統作者歸屬
傳統成書框架
材料傳承或編輯模型（如適用）
現有／最終文本形成的研究觀點（如適用）
```

不是每卷都需要把五層全部寫出來；只有來源確實提出且對一般讀者有幫助時才寫。

寫作上優先使用：

- 「傳統上……」
- 「部分現代研究者則……」
- 「學界對具體年代仍有不同模型……」
- 「這兩種說法回答的問題層次不同……」

避免：

- 「已經證明……」
- 「原文否定……」
- 「現代研究證實傳統錯誤……」
- 把單一學派重建寫成沒有爭議的事實。

---

## 5. 寫作風格

Introduction 面向一般讀者，但不是兒童教材，也不是 AI 導讀文。

### 要

- 像一位熟悉材料的人在正式介紹一卷書；
- 先講清楚，再講深入；
- 段落之間有因果與承接；
- 使用大眾可讀的繁體中文；
- 專有名詞第一次出現時簡單解釋；
- 有來源分歧時自然地放進正文或 callout，不另寫成稽核報告；
- 有必要時用表格、Mermaid、callout 幫讀者一次看懂。

### 不要

- 「如果只記一件事……」「你有沒有想過……」這類密集的 AI 導讀口吻；
- 每段都用問句開頭；
- 為了活潑而過度口語化；
- 把 Introduction 寫成 FAQ；
- 把來源名稱不斷塞進正文；
- 為了對齊模板，硬生出沒有價值的小節；
- 一段一個圖、為了視覺效果而畫圖。

正文應該能在拿掉所有圖表後仍然是一篇完整、連續、可讀的導論。

---

## 6. Obsidian / Markdown 視覺化原則

圖表是「壓縮複雜資訊」的工具，不是裝飾。

### Mermaid 適合

- 全書敘事／論證主線
- 大段落結構
- 時序
- 人物／家族／王朝關係
- 地理移動（只做概念路線，不假裝精確地圖）
- 與前後書卷或正典的銜接

### 表格適合

- 作者／年代不同觀點的並列
- 大綱與章節範圍
- 關鍵經文與其功能
- 書卷群組的對照

### Callout 適合

- 一個必須特別避免混淆的概念
- 學術／傳統觀點的分層
- 閱讀提醒
- 補充背景，但不值得打斷正文主線的內容

### 原則

- 沒有實際降低理解成本，就不用圖。
- Mermaid 一張圖只回答一個問題。
- 不把整段文章原封不動再畫成一次流程圖。
- Introduction 不自行批量建立 `link_folder` 條目。
- wiki-link 只連到已存在且語義確定的條目／章節；不確定就保留純文字。

---

## 7. 內容 payload：固定模組、彈性出現

`introduction_content.yaml` 不再用「十二個固定 section」思維。
Renderer 只認得一組**允許模組**，並由程式決定順序；沒有資料價值的模組可以省略。

推薦允許模組：

```text
identity                # 書名／位置；可省略
authorship_context      # 作者、年代、受者、歷史與文學背景
message_purpose         # 主旨與寫作目的
importance_features     # 重要性與特色
structure               # 全書結構／內容大綱
key_texts_themes        # 鑰節、鑰字、核心主題
canonical_relationship  # 與其他書卷／整本聖經的關係；可省略
```

這些是內部 module ID，不要求公開頁面呈現成七個制式標題。
Renderer 可依書卷設定自然標題，並在沒有內容時完全不 render 該模組。

**重要：module 順序由 renderer 決定，model/agent 不得自行重排。**

---

## 8. 每卷 production pipeline

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
→ round-trip / rendered equality check
→ 人工 review（內容、文風、圖表）
→ 通過後才 merge / 推進下一卷
```

Prototype 階段以《創世記》完成整套流程；在《創世記》未確認前，不批量產生其他 65 卷。

---

## 9. 每卷 source manifest 應記什麼

至少包含：

```yaml
book: 創世記
book_folder: 01 創世記
sources:
  CT00:
    role: commentary
    editorial_anchor: true
    url: ...
  GT00:
    role: commentary
    provenance_mode: anthology
    url: ...
  KC0:
    role: commentary
    url: ...
  BH:
    role: commentary
    family_vote: BH
    url: ...
  BIBLEPROJECT:
    role: literary_design
    optional: true
    url: ...
  ENTER_THE_BIBLE:
    role: academic_context
    optional: true
    urls: [...]
  YALE:
    role: academic_context
    optional: true
    url: ...
```

外部補強網址未必能靠固定 slug 推導，所以應由 canonical registry / per-book override 管理，不讓 crawler 猜 URL。

---

## 10. Source notes 與 final content 的責任分離

### `source_notes.yaml`

保存：

- 各來源實際說了什麼；
- 可核對的事實；
- 來源特有觀點；
- 分歧；
- GT00 子來源 provenance；
- 可供 final article 使用的背景資訊。

它不是公開文章。

### `introduction_content.yaml`

保存：

- 已完成跨來源整合的 public-facing 內容；
- 每一段／表格／圖表對應的 `source_ids`；
- 遇到分歧時已分層處理的文字。

它也不是公開文章；最終由 renderer 生成 Markdown。

### `Introduction.md`

只負責給讀者閱讀，不承擔原始 research log。

---

## 11. Gate

每卷至少通過：

1. `source_manifest` 中的 URL 與 role 合法；
2. content 使用的所有 source ID 都存在；
3. 四家 commentary 與外部補強來源沒有混票；
4. GT00 合輯觀點沒有失去子來源；
5. 作者／年代等重大分歧沒有被硬壓成單一結論；
6. `Introduction.md` 可由 payload deterministic render；
7. 文章不是固定點數模板；
8. 至少一個視覺元素確實降低理解成本，但不強制每卷一定有 Mermaid；
9. 所有 wiki-link 都指向已存在目標；
10. 人工確認文風不是 AI FAQ／清單式導讀。

---

## 12. Prototype 決策

《創世記》是唯一的第一階段 prototype。

在使用者確認以下項目以前，不把流程批量套到其他書卷：

- 文章讀起來像真正的「書卷提要／導論」；
- CT00 的介紹節奏被保留，但沒有照抄其所有神學判斷；
- 外部學術來源有補強，而沒有搶走文章主體；
- 圖表實際好用；
- source provenance 清楚；
- schema 對不同文類足夠彈性。

確認後才進入下一階段：用同一套 scheme 測試一卷**不同文類**的書（建議《詩篇》或《馬可福音》），再決定是否擴到 66 卷。
