# 交接：耶和華的節期（第一階段：開場＋逾越節）

最後更新：2026-10-09。目標與規則看 `GOAL.md`（使用者已用 `/goal` 設為本工作的目標），設計與分鏡看 `SPEC.md`。這份只記「做到哪、接下來做什麼」。

## 第一階段狀態：完成，待使用者驗收

- **內容**（Opus）：
  - `data/feasts.yaml`、`data/story.yaml`（開場 4 拍＋逾越節 9 拍）；
  - `data/commentary.yaml`（29 則，四家都有）；
  - `data/step.yaml`（10 個原文字）。
- **審查**：Codex 唯讀兩輪已用完。
  - 第 1 輪 PASS；
  - 第 2 輪 1 條 finding（GT 段落沒標出處卻掛名丁道爾）。主筆依同一判準全面複查，共修 4 處，做最後修正。
  - 不再有第 3 輪。細節見 `tools/review-log.md`。
- **工程**（Sonnet 兩個子代理＋主筆整合）：
  - 場景 `src/scene/**`＋`scene-lab.html`；
  - 介面 `index.html`、`src/main.ts`、`src/story/scroll.ts`、`src/ui/**`、`src/audio/**`、`src/styles/**`；
  - 資料腳本 `scripts/**`。GT 歸屬檢查已改成段落級。
- **檢查**：
  - `npm run build` 全過：data:check、typecheck、56 項測試；`dist/index.html` 約 736 kB 單檔，`dist/audio` 7 個檔，`dist/fallback` 13 張。
  - `file://` 打開正常：13 拍、場景、插圖、音檔都能載入，console 無錯誤。
  - 桌機 1440×900、手機 390×844，亮色與暗色，13 拍全部截圖看過；手機 scrollWidth 都是 390。
- **WebGL 不可用時的插圖**：`public/fallback/<cue>.webp`，13 張共約 3.4 MB，用 `tools/shoot-fallback.mjs` 從 lab 頁截。
- **錄影與截圖**：交件用的在 `review/`（已列入 .gitignore，不 commit）。
  - 4 支影片：桌機亮、桌機暗、手機亮、手機減少動態；
  - 13 拍總覽圖 4 張：桌機／手機 × 亮／暗。
- **主筆驗收時抓到並修好的**：
  - meal 室內分格：介面沒建框，場景畫不出來；
  - 徽章壓到月份導覽；
  - 章標題被標題列壓住；
  - 手機構圖被說明框蓋住；
  - 父親像帳篷；
  - **減少動態開著時拖曳牛膝草不跟手**：場景閒置跳幀沒被 pointer 事件叫醒。已在 `src/scene/index.ts` 修。
  - 以上用 `tools/check-drag.mjs` 與 scratchpad 的 `site-drag*.mjs` 驗過：滑鼠、觸控、減少動態開或關，甩到三處停住都能打上。

## 待使用者決定（交件時已問）

- 音效是盲選的（無法試聽），請使用者實際聽過，尤其「群眾哀號」與「打門框」。
- 畫風依實際看過 Santioni 後改為「刻線為主、網點為輔」（GOAL.md §1 已註記），請使用者確認。
- 這個資料夾還沒 commit（使用者沒要求）。
- 部署：要放到現有網站的同一處，部署前須先問使用者。

## 已知、可接受的小問題

- 桌機 midnight 拍的說明框壓到那排有血的門上方一小段。
- 讀者跳過塗血時，場景會自動補上三處的血（狀態列寫「已替你補上三處的血」）。之後捲回這一拍不能再操作。
- iOS Safari 的音檔解鎖沒有實機驗證。

## 下一步（使用者同意後）

第二階段才做其他節日。這次 GOAL.md 明定垂直切片做完就停。

## 工具（`tools/`）

| 檔案 | 用途 |
|---|---|
| `cdp.mjs` | headless Chrome 驅動 |
| `shoot-site.mjs <url> <outDir> [--mobile] [--dark] [--reduced]` | 逐拍截圖＋量 scrollWidth |
| `shoot-fallback.mjs [port]` | 產生靜態插圖 |
| `check-file-url.mjs [png]` | 用 file:// 驗 dist |
| `check-drag.mjs <url> [--mobile] [outDir]` | 在整合後的網站上用滑鼠或觸控拖曳塗血 |
| `record.mjs <url> <out.mp4> [--mobile] [--dark] [--reduced]` | 錄影 |
| `fs.mjs` | Freesound 查詢與下載 |
| `codex-review-1.md`、`codex-review-2.md` | 審查指令 |
| `codex-review-2.out.md` | 第 2 輪結果 |
| `review-log.md` | 審查紀錄 |

注意：這台機器的系統是暗色主題，截亮色圖要明確用 `Emulation.setEmulatedMedia` 設 `prefers-color-scheme: light`（腳本已處理）。
