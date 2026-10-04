# 摩西五經的律法

摩西五經律法的互動網站：從生活問題、主題、書卷或經文找到一條律法，再一層一層往下讀經文、別卷的記載與出處。
資料管線、分類與閘門沿用最初的規劃（`C:\Users\andyj_adknr2z\.claude\plans\appendix-website-pasted-content-moonlit-turing.md`），
但**那份規劃裡的「入門／查經／研究」三層切換已經拿掉**（使用者 2026-10-04：太誇張，要一體成型）。以本 README 為準。

**目前狀態：框架完成，內容只有 6 條示範條文。** 所有畫面、資料管線、閘門、測試都能跑；接手的人主要工作是補內容（見「接下來要做的」）。

## 四條原則

1. **不搬知識庫內容。** 條目、互文說明、本章整理只給「名稱＋類型＋最多一句」，然後「查看完整條目（另開網頁）」連到公開網頁（`src/data/links.ts`，作法同民數記 33 章網站）。網站自己的價值是知識庫沒有的東西：分類、反查、跨卷對照、分布。
2. **一體成型，由淺到深。** 沒有閱讀模式、沒有給不同讀者的切換。每條律法固定四層：一句話（永遠開著）→ 經文 → 別卷 → 出處；收合列先預告裡面有什麼（經文開頭幾個字、別卷的出處、條目數）。首頁的順序也是由淺到深：問題卡 → 律法帶 → 別卷又記了一次 → 全部主題；分布表、收錄進度、下載放在「關於」。
3. **不寫 AI 公式文。** 介面文字、問句、路線名稱都平實交代內容：禁「不是…而是」「是…，不是…」、「讓我們／探索／帶你」、「X：Y」口號式標題、空泛昇華句尾。`scripts/build-data.mjs` 的 `BANNED`／`lintCopy` 擋資料，`data.test.ts` 的「介面文字不用公式句」掃 `src/**/*.ts` 的中文字串。閘門擋不到的句型（湊三律排比、模板式導言）要自己讀。
4. **不編造。** 經文只取自 `raw_scripture`；白話說明只重述經文；律法之間的關聯每一條都要有知識庫裡的出處，閘門逐字核對。找不到出處就不連線。

## 指令（一律用 PowerShell 跑，Bash 會被應用程式控制擋 rollup）

```powershell
npm install
npm run data        # data/*.yaml ＋ vault → src/data/explorer.json、appendix-chapters.json、review/summaries.md
npm run seed -- 利未記 1 27   # 從本章整理抽段落草稿到 data/seed/（網站不讀，整理後再搬進 data/laws/）
npm run build       # data:check → tsc → vitest → vite build（單一 dist/index.html，file:// 可直接開）
npm run dev         # http://127.0.0.1:3051
```

改了 `data/*.yaml`、或 vault 裡的經文／verse_links／條目之後，一定要 `npm run data`，否則 build 會因為資料過期而失敗。

## 資料格式（手寫的只有 data/）

| 檔案 | 內容 |
| --- | --- |
| `data/topics.yaml` | 6 大類 × 子題。大類顯示 `name`；子題顯示 `plain`（主題頁標題旁附 `name`）；`entry` 選填，必須是存在的條目 |
| `data/laws/<書名>.yaml` | 章 → 律法段落 → 條文。每章的 `excluded` 寫刻意不收的節與理由 |
| `data/relations.yaml` | 律法之間的關聯，`type`：parallel／supplement／case／cites；`evidence` 必填 |
| `data/questions.yaml` | 首頁的生活問題卡：`q`（≤30 字、問號結尾、只問經文回答得了的事）＋ `laws`（1–3 條）。答案用條文自己的一句話，不另寫 |
| `data/tours.yaml` | 照順序讀的路線（條文 id 的順序）；段與段之間不另寫說明；名稱不用「X：Y」 |
| `data/glossary.yaml` | 術語 → 條目，白話說明裡加虛線底，點了開條目小卡 |

條文欄位：

```yaml
- id: ex21-02                 # 書卷英文簡寫＋章＋起始節，全站唯一
  title: 希伯來男僕第七年自由  # ≤30 字
  refs: ["2-6"]               # 同一章內的節範圍，可多段；跨章的重述另立一條再用關聯連
  topics: [slavery]           # topics.yaml 的子題 id，至少一個
  summary: 買來的希伯來男僕服事六年，第七年可以白白地出去；……   # 只重述經文，≤90 字
  basis: [2, 5, 6]            # 說明依據哪幾節，必須在 refs 內
  entries: [希伯來奴僕的律例]  # 選填：庫裡已有的這條律法的條目
```

關聯證據二選一，引句必須**逐字**出現在出處裡，而且「條目標題＋引句」解析出的經文參照要同時蓋到兩條律法：

```yaml
evidence: { entry: 申15：12-18, quote: 申命記15章補充了出21:2-6的希伯來奴僕釋放條例 }
evidence: { chapter: 申命記/第15章, quote: ……本章整理裡的一句…… }   # 該章本身算一端
```

參照解析支援 `出21:2-6`、`出21：2`、`出二十一2～6`、`《出埃及記》二十一2`、`申命記15章`（`scripts/lib.mjs` 的 `extractRefs`）。

## 閘門（`npm run data` 與 vitest）

- 經文範圍在章內、`basis` ⊆ `refs`、每條有子題與說明、id 不重複。
- 白話說明 lint：長度；禁「不是…而是」、象徵／預表／體現／意味著等解釋性字眼；禁「她」；禁 CT／GT／KC／BH／STEP 與 Strong 編號。
- 說明與依據經文的字詞重疊率 < 40% 會警告（可能說了經文沒說的事）。**寫完一定要讀 `review/summaries.md` 逐條對照經文**，閘門只擋得住明顯的錯。
- 條目、主題、術語、證據都要解得到；verse_links 的片語要在經文裡找得到。
- 條目簡介 ≤ 40 字、不含原文字母與 Strong 編號；連結不得是 `obsidian://`。
- 覆蓋率：每章還沒處理（既不在條文也不在 `excluded`）的節，`npm run data` 會列出來。一卷完成的標準是只剩 `excluded`。

## 掛到章節附錄

`appendix-chapters.json` 由 `npm run data` 自動產生（有條文的章）。`appendix/website/build.py` 已支援跨卷的「書名/第N章」寫法，且不會為 `摩西五經` 這個非書卷資料夾產生自己的 key。

順序固定：**先 `npm run build`（要有 dist/index.html），再** `python util/build_appendix_links.py`——dist 不在時同步會把連結刪掉。之後跑 `check_chapter_files`、`validate_knowledge_base`（base 傳 git revision）、`verify_links`。

> 目前**還沒有掛上去**：只有 6 條示範條文，等 Phase 1 內容補齊再掛。`--check` 已確認會更新出20、出21、利25、申5、申15 與三卷全書目錄，共 8 個檔。

## 程式結構

```
scripts/lib.mjs            讀 vault：經文、verse_links、條目（掃 link_folder）、本章整理、全書目錄；經文參照解析
scripts/build-data.mjs     接資料、跑閘門、寫輸出；export buildAll() 給測試用
scripts/seed-sections.mjs  段落草稿
src/data/                  types.ts（explorer.json 形狀）、db.ts（索引與查詢）、links.ts（公開網址）
src/lib/                   refs（搜尋框參照）、search、diff（字面差異）、csv
src/ui/                    dom、peek（原地小卡）、cards（條文卡、經文、條目小卡）、chrome（頂列）、searchbox、
                           ribbon（五經律法帶：首頁大的、各頁頂端細的；任何 data-laws="id id" 的元素滑過或聚焦就亮出那幾條）、graph（關係圖）
src/views/                 home、law（四層梯子）、topic（各卷一欄＋連線）、compare、book（含 #/ref/出21）、entry、tour、about
```

路由：`#/`、`#/topic/<子題或大類 id>`、`#/law/<id>`、`#/compare/<id,id>`、`#/book/<簡稱>`、`#/ref/出21`、`#/entry/<條目>`、`#/tour/<id>/<段>`、`#/about`。

條文頁記住讀者打開過「經文」「別卷」（localStorage `lawmap:layers`），換到下一條時沿用；「出處」不沿用。

樣式：所有 class 用 `lm-` 前綴；顏色是 `:root` 的變數（深淺色各一組）；大類色 `--g1…--g6`、條目類型色 `--t-*`。互動守則：點擊不捲動頁面（用 peek 小卡）、不用 `scrollIntoView`、手機單欄寫 `minmax(0, 1fr)`。

## 驗證

用 headless Chrome 以 `file://` 開 `dist/index.html` 截圖（PowerShell `Start-Process` 開 chrome 的 remote debugging，再用 CDP 腳本）。每次要看：首頁（問題卡打開、滑過圖例時律法帶亮起）、條文頁四層全收與全開、主題頁連線、桌機 1280 與手機 390（手機 `scrollWidth` 必須是 390）、深色模式、console 無錯誤、打開一層與點經文片語前後 `scrollY` 不變。
**收尾只關自己開的 Chrome**（用獨立 `--user-data-dir`，再依命令列找出那幾個行程關掉）；不要 `Get-Process chrome | Stop-Process`，那會連使用者正在用的瀏覽器一起關掉。

## 接下來要做的

**Phase 1：出20–23 ＋ 平行經文**（框架已就緒，只差內容）
- [ ] `npm run seed -- 出埃及記 20 23` 已產生草稿 `data/seed/出埃及記.yaml`；整理成條文（約 70 條）搬進 `data/laws/出埃及記.yaml`，勸勉段落（如出23:20-33）寫進 `excluded`。
- [ ] 平行經文只收有關聯的條文：申5（十誡）、申15:12-18、利25:39-55、申19／民35（逃城）、利25:1-7、出34／利23／申16（節期）、申22:28-29、申24:10-13、利25:35-37、申23:19-20、申22:1-4、利24:17-22、申14:21。已確認有互文條目可當證據的：申5:6-21、利25:39-43、民35:9-34、申19:1-13、利25:1-7、申22:28-29、申24:10-13、利25:35-37、申23:19-20；出34:18、申22:1-4、利24:17、申14:21 沒有，要到本章整理找。
- [ ] 第三條照順序讀的路線（寄居的、孤兒寡婦、窮人），名稱平實，不用「X：Y」。
- [ ] `data/questions.yaml` 隨條文補問題卡：只問經文回答得了的事。
- [ ] 逐條讀 `review/summaries.md`。
- [ ] build → 截圖驗證 → `build_appendix_links` 掛上 → KB 閘門。

**框架上還可以細磨的**（2026-10-04 改版後；含 gpt-5.6-luna 審查的建議）
- [ ] 主題頁到 600 條時：欄會很長、連線會變毛線團。建議每欄依章分段可收合；平常只淡淡畫線，點選一張卡才把它的線與對面的卡亮起，並出現「這兩段並排」。
- [ ] 首頁問題卡：維持人工挑 8–12 張，前 6 張先顯示（`FIRST_QUESTIONS`），其餘按「再看 N 個問題」。每個大類至少一張。
- [ ] 律法帶在手機上：大帶一列 50 格約 6px，點不準。可改成點一卷放大成那一卷的章格，或可橫向捲動（只能捲容器，不可捲頁面）。
- [ ] 律法帶的「定位尺」：點了問題卡或主題後保留亮起狀態（現在主要靠滑過，手機只有聚焦時有）。
- [ ] 「全部主題」到內容滿了以後改成可篩選。
- [ ] 章節附錄連結帶 `#/ref/出21`，讓從某章點進來直接落在那一章（要先確認 Obsidian 會不會保留 `.html#…`）。
- [ ] 書卷篩選目前存在 localStorage，規劃是也寫進網址（`?b=出申`）以便分享。
- [ ] 字面差異目前只比前兩欄。
- [ ] 視覺設計再細磨（首頁主視覺、矩陣、律法帶）。

**Phase 2 以後**：利未記 → 申命記 → 民數記 → 創世記與出埃及記其餘章，一卷一 commit；出25–31（會幕規格）只收到段落層。

## 授權

經文為和合本。本站僅供非商業的教育與聖經研讀使用。
