# 交接：耶和華的節期

最後更新：2026-10-09。這份只記「做到哪、接下來做什麼」，其他文件看這裡：

| 想知道 | 看哪裡 |
|---|---|
| 總目標與規則 | `GOAL.md` |
| 第二階段的目標提示詞（使用者用 `/goal` 設定） | `GOAL-2.md` |
| 設計與分鏡 | `SPEC.md` |
| 審查紀錄 | `tools/review-log.md` |

## 進度

| 階段 | 內容 | 狀態 |
|---|---|---|
| 第一階段 | 開場＋逾越節，13 拍 | 已 commit `300746b5`；使用者：「大致上都沒有問題」 |
| 第二階段第一批（春季） | 月朔（併入開場）、無酵節、初熟的禾捆、二月逾越節、七七節，18 拍 | 完成，待使用者驗收 |
| 第二階段第二批（秋季） | 吹角節、贖罪日、住棚節＋第八日；民29 數字檢查 | 未開始 |
| 第二階段第三批（結尾） | 七的節奏（安息日→禧年）、首頁入口卡、律法地圖互連、部署前確認 | 未開始 |

## 第一批（春季）做了什麼

- **內容**（Opus）：
  - 18 拍敘述；
  - 68 則註釋；
  - 8 個原文字；
  - 16 句條目簡介；
  - 4 組獻祭清單：數字由建置腳本從經文解析，不手抄。
  - 註釋讀法：先由 Haiku 的 `tools/raw-index/` 經節行號索引定位，再完整讀相關段落。
- **審查**：Codex 兩輪。
  - 第 1 輪 2 條 finding：BibleHub 一句的中譯被擴大，已修；
  - 第 2 輪 PASS。
- **工程**（Sonnet `jf-engineer` ×2）：
  - 場景：新增 `camp.ts`、`fields.ts`、`home.ts`、`wave.ts`、`geo2.ts`、`props.ts`，`tracks.ts` 改用 cue 名定位時間點；
  - 介面：新增 `src/ui/{offerings,bake,wave,count,fold,place}.ts`；
  - 資料腳本：新欄位、獻祭解析（建置檢查 #5）、GT 標記破折號加寬。
- **新互動**：
  - bake：長按烤餅；
  - wave：拖曳或按鈕搖禾捆；
  - count：捲動數算 7×7 加第 50 日。
  - 三者在桌機與手機、減少動態開與關都實測過。
- **新音效**：`fire`、`field-wind`、`harvest`，都是 CC0，主筆逐頁確認授權。
- **契約新增**：
  - Beat 的 `interaction`（bake／wave／count）、`badge`、`dayTo`、`offerings`、`offeringsLabel`；
  - `SiteData.offerings`；
  - state 的 `month`／`count`／`bake`／`wave`；
  - api 的 `waveAction`、`wave-*` 事件。

## 春季之後的修正（使用者回報）

- **桌機說明框內展開的面板被擠扁**：
  - 原因：敘述、經文、獻祭清單把框的 max-height 用完，面板高度剩 70px 甚至 3px。
  - 修法：框內容改成整框一起捲，面板不再被壓縮；展開時自動捲到面板標題，框底有「往下看」提示。
- **「大部分畫面都是靜止不動的圖片」**：使用者的 Chrome 開著作業系統的減少動態，網站原本因此停掉全部背景動態。使用者決定：
  - 預設一律有動態，標題列有「動態」開關（localStorage `jf-motion`）；
  - `story.motionOff` 只看這個開關，不再看 `prefers-reduced-motion`。
  - 補上四類動態：環境、人物動物小動作、捲動帶動的大動作、運鏡；規格在 SPEC.md「動態規格」。
  - 新增 `src/scene/rig.ts`（可動人物與動物）、`fx.ts`（火星、煙、塵土）。
  - 驗收工具 `tools/check-idle-motion.mjs`：
    - 動態開時，31 拍不捲動也都在動，兩張相隔 1 秒的截圖差異 0.6%–20%；
    - 動態關時全部 0%。
  - 效能：每幀 GPU 7.5–10 ms，三角形最多約 14 萬。
  - 還沒做到的：成群人物不轉頭；two-loaves 的手不夠自然；割麥用「倒下的麥把」表現，不是每刀一個姿勢。
  - `hyssop.ts` 的打擊速度門檻降為 0.4×短邊，因為手機觸控事件頻率低會漏判。

## 已知、可接受的小問題

- 桌機 midnight 拍的說明框壓到那排有血的門上方一小段。
- 讀者跳過塗血、烤餅、搖禾捆時會自動補完，捲回來不能再操作。
- 手機有幾拍主體和說明框稍有重疊（場景用 `MOBILE_K` 統一後退，沒有逐拍微調）。
- weeks-offerings 的祭牲剪影離得遠時，牛羊不易分辨。
- iOS Safari 的音檔解鎖沒有實機驗證。

## 待使用者決定

- 新音效同樣是盲選，請實際聽：火、麥田風、鐮刀。
- 部署：放到現有網站的同一處，部署前須先問使用者。

## 子代理（repo 根目錄 `.claude/agents/`）

- `jf-engineer`：Sonnet 5.5，effort high；
- `jf-collector`：Haiku。
- 兩者都設 `omitClaudeMd: true`。要修改就用 SendMessage 續用同一個代理。

## 工具（`tools/`）

| 檔案 | 用途 |
|---|---|
| `cdp.mjs` | headless Chrome 驅動 |
| `shoot-site.mjs <url> <outDir> [--mobile] [--dark] [--reduced]` | 逐拍截圖＋量 scrollWidth |
| `shoot-fallback.mjs [port]` | 產生靜態插圖（新 cue 要加進 SHOTS） |
| `check-file-url.mjs [png]` | 用 file:// 驗 dist |
| `check-drag.mjs`、`check-wave.mjs`、`check-bake.mjs` | 在整合後的網站上實測三種互動 |
| `record.mjs <url> <out.mp4> [--mobile] [--dark] [--reduced]` | 錄影，會在塗血、烤餅、搖禾捆三拍停下操作 |
| `raw-index/build_index.py <book> <ch> …` | raw 經節行號索引；GT 子來源欄不可靠，以 raw 與建置檢查為準 |
| `fs.mjs` | Freesound 查詢與下載 |
| `codex-review-*.md`、`*.out.md`、`review-log.md` | 審查指令、結果、紀錄 |

注意：這台機器是暗色主題，而且開著減少動態。截圖一律明確設定 `prefers-color-scheme` 與 `prefers-reduced-motion`（腳本已處理）。
