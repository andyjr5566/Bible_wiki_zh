# 《創世記》書卷導論 prototype

這個資料夾是書卷級 `Introduction.md` pipeline 的第一個完整 prototype。

## 目標

不是再做一篇「百科式簡介」，而是讓第一次打開《創世記》的普通讀者，在幾分鐘內先看懂：

- 這卷書在講什麼；
- 50 章怎麼分、故事鏡頭怎麼移動；
- 作者與年代有哪些不同層次的問題；
- 原始讀者、歷史文化背景、重要主題與文學特色；
- 它如何接到《出埃及記》與整本聖經；
- 哪些問題是來源間有分歧、不能假裝只有一種答案。

公開頁面：`01 創世記/Introduction.md`

語意 payload：`01 創世記/.tmp/introduction/introduction_content.yaml`

## 來源分層

### 既有四套註釋來源

| ID | 來源 | 角色 |
| --- | --- | --- |
| `CT00` | CCBibleStudy《創世記提要》 | 傳統書卷提要、作者、時地、主旨、大綱 |
| `GT00` | CCBibleStudy《創世記導論拾穗》 | 多家導論合輯；使用時必須保留內部子來源 |
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

## 最重要的 provenance 規則

1. `GT00` 是合輯，不可以把其中某一位作者的觀點寫成「GT00 認為」。
2. BibleHub 即使頁面內部整合多個底層資源，仍只算一個 `BH` 來源家族。
3. BibleProject、Enter the Bible、Yale 是不同功能的補強層，不可以變成第五、第六、第七家註釋票。
4. 作者／年代至少拆成：
   - 故事發生年代；
   - 傳統作者歸屬；
   - 傳統成書框架；
   - 現代文本形成／編輯研究。
5. 有分歧時並列不同框架與證據層級，不讓 AI 自己選一邊寫成「已證實」。

## 檔案角色

- `source_manifest.yaml`：來源 URL、來源角色、預期可抽取欄位與 provenance 規則。
- `source_notes.yaml`：人工可讀的正規化來源筆記與跨來源整理。不是網頁全文鏡像。
- `raw/`：由 crawler 執行時產生的清理後來源文字與 receipt；不應由模型手工杜撰。
- `introduction_content.yaml`：模型負責的語意內容。
- `Introduction.md`：renderer 產生、給一般讀者看的最終頁面。

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

## 呈現原則

公開頁面的調性要跟 repo 現有章文一致：

- 先讓讀者「看懂」，再補學術名詞；
- 能用表格、流程圖、關係圖呈現的，不硬塞成長段落；
- Mermaid 是內容的一部分，不是裝飾；
- 使用 Obsidian callout 把「提醒、爭議、閱讀方法」從正文抽出；
- 保持自然繁體中文，不使用「以下將介紹」「綜上所述」「本節將探討」這類模板式 AI 語氣；
- 不因為資料很多就全部塞進頁面，只留下會改變一般讀者理解方式的資訊；
- 來源與方法收在折疊 callout，避免破壞正文閱讀節奏。

## Prototype 驗收點

- [x] CT00、GT00、KC0、BH 四家來源角色分離
- [x] BibleProject、Enter the Bible、Yale 補強層分離
- [x] 作者／年代分層，不硬裁決
- [x] 1–11／12–50 大結構可視化
- [x] 全書故事焦點移動可視化
- [x] 作者／成書問題可視化
- [x] Obsidian callout 與 wiki-link 導航
- [x] 最終 `Introduction.md` 與原有章文保持同一閱讀調性
- [x] renderer：`introduction_content.yaml -> Introduction.md`
- [x] provenance/render checker
- [ ] 由可連外的本機／CI 實際執行 crawler，產生 `raw/` 與 `receipt.json`

最後一項刻意保留為 runtime 工作：crawler 必須真的向各來源取回頁面後再產生 receipt，不能由模型假造「已抓取成功」。
