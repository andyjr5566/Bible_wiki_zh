# 整站翻新執行進度

計畫版本：2026-09-10。GPT-6 已完成規劃與檔案整理；R00 已由目前 session 執行並完成基線產物。執行介面目前標示為 GPT-5，沒有把這次呼叫冒稱為 GPT-5.6 Luna；後續若使用者切換 Luna，從下一張未完成任務繼續。舊 Blender T0–T5 的完成宣告不轉換為新任務完成。

## 總狀態

- 當前階段：R03 自驗透過，下一張為 R04；R00–R23 尚未宣稱整站完成。
- 實際執行模型：本輪介面標示 GPT-5；GPT-5.6 Luna 尚未由工具實際呼叫確認。
- 最新測試／build：R03 `npm run build` exit 0；typecheck、16 個測試檔／34 個測試、architecture 91 modules、assets 17 assets 均通過；Vite production build 成功。新增來源抽取器 `npm run build:excerpts` 產生 9 段逐節經文。
- Blender：本輪 `get_scene_info` 唯讀呼叫成功，Scene 有 24 個物件、5 個材質，回傳含 `Sketchfab_model`／`Root`。未改場景；儲存／dirty 狀態未由該回應確認，後續依 R07 隔離工作檔規則。
- 網站成熟化：未完成。發布：未執行。
- 前一批缺口：見 [REVAMP_BASELINE](REVAMP_BASELINE.md) B01–B15。

## 任務狀態

| ID | 任務 | 最小相依 | 執行者 | 狀態 | 證據 |
| --- | --- | --- | --- | --- | --- |
| R00 | 工具與基準 | — | 目前 GPT-5 session | 自驗透過 | [BASELINE](../qa/revamp/BASELINE.md)、[資產計量](../qa/revamp/BASELINE_ASSETS.json)、[截圖](../qa/revamp/screenshots/) |
| R01 | 來源臺帳 | R00 | 目前 GPT-5 session | 自驗透過 | [SOURCES](../research/SOURCES.md)、[CLAIMS](../research/CLAIMS.md) |
| R02 | 角色／程序契約 | R01 | 目前 GPT-5 session | 自驗透過 | [RITUAL_STEPS](../research/RITUAL_STEPS.md)、[ROLE_ACCESS](../research/ROLE_ACCESS.md)、[GARMENTS](../research/GARMENTS.md) |
| R03 | 資料與抽取 | R01,R02 | 目前 GPT-5 session | 自驗透過 | [scripture-excerpts](../../src/data/scripture-excerpts.json)、[object-details](../../src/data/object-details.json)、[evidence](../../src/data/evidence.json)、[tours](../../src/data/tours.json)、[ProjectData.test](../../src/data/ProjectData.test.ts) |
| R04 | 入口／狀態 | R03 | 目前 GPT-5 session | 自驗透過 | [UIStateManager](../../src/ui/UIStateManager.ts)、[ModeNavigation](../../src/components/ModeNavigation.ts)、[UIStateManager.test](../../src/ui/UIStateManager.test.ts) |
| R05 | detail生命週期 | R04 | Luna | 待辦 | — |
| R06 | 空間／剖面／取景 | R05 | Luna | 待辦 | — |
| R07 | Blender流程 | R03,R06 | Luna | 待辦 | — |
| R08 | 約櫃修正 | R07,R01 | Luna | 待辦 | — |
| R09 | 完整會幕／照明 | R07,R08 | Luna | 待辦 | — |
| R10 | 五件器物 | R07,R09 | Luna | 待辦 | — |
| R11 | 角色／服飾／牲畜 | R02,R07,R10 | Luna | 待辦 | — |
| R12 | 匯出／資產登記 | R08,R09,R10,R11 | Luna | 待辦 | — |
| R13 | 播放器／洗濯／香 | R04,R05,R06,R12 | Luna | 待辦 | — |
| R14 | 燈／餅程序 | R13 | Luna | 待辦 | — |
| R15 | 燔祭／五祭 | R13,R14 | Luna | 待辦 | — |
| R16 | 贖罪日 | R13,R15 | Luna | 待辦 | — |
| R17 | 空間導覽 | R06,R12,R16 | Luna | 待辦 | — |
| R18 | 器物／來源介面 | R03,R10,R17 | Luna | 待辦 | — |
| R19 | 手機／可及性 | R18 | Luna | 待辦 | — |
| R20 | 效能／診斷 | R19 | Luna | 待辦 | — |
| R21 | 回歸／故障 | R20 | Luna | 待辦 | — |
| R22 | 清理／檔案 | R21 | Luna | 待辦 | — |
| R23 | Production自驗 | R22 | Luna | 待辦 | — |
| R24 | 總控驗收 | R23 | GPT-6 | 待辦 | — |

狀態用「待辦／進行中／自驗透過／受阻／待總控驗收／總控透過」。自驗透過的依賴可讓 Luna 繼續；歷史PASS或僅建立檔案不可當功能自驗透過。來源爭議要記具體受影響工作，停在該邊界，不停掉其他已授權獨立工作。

## 每張任務完成時追加

```text
任務ID／起訖日期：
執行模型／工具實測：
開始時工作樹或基準hash：
已讀輸入與核准claim IDs：
變更檔案（含刪除/原因）：
Blender工作檔／recipe／source與derived hashes（適用時）：
驗收QA IDs：
命令、exit code、log路徑：
畫面與activeAssetIds／profile／viewport證據：
未驗證項目／限制／需總控判定：
結論（自驗／總控分開）：
下一張任務ID、可直接執行的下一步：
```

## unresolved 登記

初始無本輪已裁定問題；B07約櫃包金修正為已確定任務，B11競態為待受控重現的工程風險。接手後新增表格，每項填：ID、來源/檔案位置、衝突內容、影響R/QA、已嘗試查核、可行選項、總控結論。不得用空白表代表全部已解決。

## 規劃交付的證據

- 本組總規格／25任務／18 QA／證據規格已落地，當前所有實作卡待辦。
- 舊指令與當前入口分離；封存清單及hash見 [DOCUMENT_REGISTER.md](DOCUMENT_REGISTER.md)。

## R00 執行回執

任務ID／起訖日期：R00／2026-09-10 01:35–01:45（Asia/Taipei）
執行模型／工具實測：目前 session 標示 GPT-5；Node/npm、Browser、Blender MCP 均實測；命令列 `blender` 不在 PATH。
開始時工作樹或基準hash：`feat/appendix-exodus25-revamp`、`c0aefae8`；本站 tracked 差異為 0。
已讀輸入與核准claim IDs：LUNA_START、REVAMP_MASTER、REVAMP_TASKS R00、package.json、vite.config.ts；R00 只做工程／工具基線，未新增內容 claim。
變更檔案：`docs/qa/revamp/BASELINE.md`、`BASELINE_ASSETS.json`、`screenshots/r00-*.png`、本進度檔。未改 runtime、GLB、source GLB、raw_scripture 或 Blender 場景。
Blender工作檔／recipe／source與derived hashes：未寫入 Blender；processed 17 GLB 的 bytes／三角面／材質／貼圖／local bounds 見 `BASELINE_ASSETS.json`。
驗收QA IDs：R00 基線驗收；桌面 1920×945、手機 390×844；未把 DOM 名稱當成 detail 載入證據。
命令、exit code、log路徑：`npm run build` exit 0；`npx vite preview --host 127.0.0.1 --port 4173` 成功；Browser console warning/error 0；原始命令輸出保留於本次工作回執。
畫面與activeAssetIds／profile／viewport證據：五張截圖連結於 BASELINE；Browser 未暴露 activeAssetIds／profile 診斷，標為未驗證。
未驗證項目／限制／需總控判定：獨立 detail 實際 GLB 請求、GPU frame 指標、Blender dirty／檔名、六種完整服事、角色與來源內容均未在 R00 判定。
結論（自驗／總控分開）：R00 自驗透過；尚未交 GPT-6 R24，網站成熟化仍未完成。
下一張任務ID、可直接執行的下一步：R01；建立來源／主張臺帳，先隔離無依據的尺寸、原文、角色與特效內容。

## R01 執行回執

任務ID／起訖日期：R01／2026-09-10 01:50–02:10（Asia/Taipei）
執行模型／工具實測：目前 session 標示 GPT-5；本機 raw_scripture、使用者 PDF/PPTX、既有資產授權文件與指定研究 URL 已實測讀取。Tel Aviv University 研究入口後一次請求為 internal error，已標 `unverified`。
開始時工作樹或基準hash：R00 commit `2a4fc00a`，分支 `feat/appendix-exodus25-revamp`。
已讀輸入與核准claim IDs：REVAMP_EVIDENCE、REVAMP_TASKS R01、S-EX25/26/27/28/30/35–40、S-LV01–08/16/24、S-NM03/04/18、S-EX16、S-NM17、S-HB09；目前未把原有 hard-coded UI 事實直接核准。
變更檔案：`docs/research/SOURCES.md`、`docs/research/CLAIMS.md`、本進度檔。沒有修改 raw_scripture、raw_data、研經 production、runtime 或模型。
驗收QA IDs：R01 來源／主張臺帳驗收；所有列含定位、狀態、界線與待驗證項目。
命令、exit code、log路徑：PowerShell SHA-256／行數核對 exit 0；Python pypdf 逐頁讀兩份 PDF；PPTX ZIP/XML 確認 18 張投影片；PLOS 原始研究摘要／考古脈絡／方法與指定比較 URL 已開啟。
畫面與activeAssetIds／profile／viewport證據：沿用 R00 截圖作為現行主張觀察；R01 不宣稱新增視覺功能。
未驗證項目／限制／需總控判定：Tel Aviv 入口內容待穩定讀取；TheTorah 僅 interpretive；使用者 PDF/PPTX 僅 reference-only；肘換算、燈臺未載尺寸、營地配置、未回查原文拼寫均 unresolved 或 rejected。
結論（自驗／總控分開）：R01 自驗透過；只有 `verified` 且有精確定位的 claim 可進 R03 typed evidence，未交 GPT-6 R24。
下一張任務ID、可直接執行的下一步：R02；依臺帳編排六個核心程序、利未記五祭分支、角色權限與兩套服裝狀態。

## R02 執行回執

任務ID／起訖日期：R02／2026-09-10 02:10–02:35（Asia/Taipei）
執行模型／工具實測：目前 session 標示 GPT-5；依 R01 已核准的 raw_scripture claims 編排資料，沒有啟動動畫或 Blender 寫入。
開始時工作樹或基準hash：R01 commit `872283f9`，分支 `feat/appendix-exodus25-revamp`。
已讀輸入與核准claim IDs：RITUAL_STEPS 輸入規格、S-EX25/26/27/28/30/37/40、S-LV01–07/16/24、S-NM03/04/18；另逐行核對利5、利7、利16與出28。
變更檔案：`docs/research/RITUAL_STEPS.md`、`ROLE_ACCESS.md`、`GARMENTS.md`、本進度檔。沒有修改 runtime JSON、schema、raw_scripture 或模型。
驗收QA IDs：R02 程序／角色／服裝驗收；六核心程序均拆成可停步驟，燔祭有牛／羊／鳥分支，五祭保留材料與處置差異，贖罪日含香、血、活羊、換衣、營外與排他狀態。
命令、exit code、log路徑：Node claim ID 交叉檢查 missing=0；PowerShell 搜尋 TODO／placeholder／待補=0；`git diff --check` 無錯誤。
畫面與activeAssetIds／profile／viewport證據：R02 是語義與資料契約，不宣稱有新畫面；R00 截圖只作現況對照。
未驗證項目／限制／需總控判定：R03 尚未把契約接到 typed data／schema；角色 mesh 與動畫仍未實作；actor-unspecified、阿撒瀉勒解釋、未詳載服裝外觀保留未知。
結論（自驗／總控分開）：R02 自驗透過；所有程序列都有 claim IDs、來源定位與未知界線，尚未交 GPT-6 R24。
下一張任務ID、可直接執行的下一步：R03；建立 evidence／object-details／tours 與擴充 ritual schema，並由庫根 raw_scripture 產生可驗證 excerpts。

## R03 執行回執

任務ID／起訖日期：R03／2026-09-10 02:35–03:00（Asia/Taipei）
執行模型／工具實測：目前 session 標示 GPT-5；未宣稱 GPT-5.6 Luna。使用 Node 來源抽取器、TypeScript／Zod、Vitest、Vite preview 與瀏覽器驗證；Blender 僅維持既有 read-only 檢查結果。
開始時工作樹或基準hash：R02 commit `019ae859`，分支 `feat/appendix-exodus25-revamp`。
已讀輸入與核准claim IDs：R01 `SOURCES.md`／`CLAIMS.md`、R02 `RITUAL_STEPS.md`／`ROLE_ACCESS.md`／`GARMENTS.md`；runtime claim IDs 涵蓋 C-EX25-ARK-SPEC、C-EX25-ARK-CHERUB、C-EX25-TABLE、C-LV24-BREAD、C-EX25-MENORAH、C-LV24-LAMP、C-EX27-BURNT-ALTAR、C-EX30-LAVER、C-EX30-INCENSE、C-EX26-ZONES、C-EX27-COURT、C-LV01-BRANCHES、C-LV02-07-FIVE、C-LV16-DAY、C-EX40-CLOUD-FIRE；工程與拒絕項保持 unresolved／rejected。
變更檔案：新增 `src/types/{evidence,objectDetails,tours,scriptureEvidence,dimensions}.ts`、對應 Zod schemas、`evidence.json`、`object-details.json`、`tours.json`、`dimensions.json`、`scripture-excerpt-specs.json`、生成的 `scripture-excerpts.json` 與 `scripts/build-scripture-excerpts.mjs`；更新 `loadProjectData.ts`、`rituals.json`／schema／type、`locations.json`、`ExperiencePanel.ts`、`CinematicTourController.ts`、`DimensionVisualizer.ts`、`SceneBootstrap.ts`、`AppKernel.ts`、`ProjectData.test.ts`、`package.json`。
Blender工作檔／recipe／source與derived hashes：沒有寫入 Blender；本任務只從庫根 `raw_scripture/` 讀取來源，抽取器在每段 excerpt 記錄 sourcePath 與 SHA-256。
驗收QA IDs：R03 資料單一來源、schema 解析、cross-reference、重複 ID／缺 claim fail-closed、導覽字幕無省略號、尺寸未詳狀態。
命令、exit code、log路徑：`npm run build:excerpts` exit 0（9 段）；`npm run typecheck` exit 0；`npm test` exit 0（16 檔／34 tests）；`npm run verify:architecture` exit 0（91 modules）；`npm run verify:assets` exit 0（17 assets）；`npm run build` exit 0；瀏覽器 console logs 0；截圖 `docs/qa/revamp/screenshots/r03-cinematic-excerpts-desktop.png`。
畫面與activeAssetIds／profile／viewport證據：瀏覽器 desktop preview 可見器物面板由 `availableObjects`／`detail` 顯示，導覽顯示 1/8 與出27:9–19 全段文字，逐幕字幕顯示同一 excerpts；目前沒有對 `activeAssetIds` 做新宣稱。
未驗證項目／限制／需總控判定：肘換算仍是 unresolved 工程假設；燈臺與洗濯盆尺寸不顯示數值；營地三個位置是 reconstructed 示意，不能當歷史配置；R02 詳細六程序分支尚待 R13–R16 完整落地；仍未修改 Blender 場景。
結論（自驗／總控分開）：R03 自驗透過；typed data、schema、抽取器與現有 consumers 已接合，尚未交 GPT-6 R24。
下一張任務ID、可直接執行的下一步：R04；建立入口／狀態契約與載入失敗的 fail-closed 行為，先處理資料載入與 UI 狀態邊界。

## R04 執行回執

任務ID／起訖日期：R04／2026-09-10 03:00–03:20（Asia/Taipei）
執行模型／工具實測：目前 session 標示 GPT-5；以 TypeScript／Vitest 與 Browser preview 實測，未宣稱 GPT-5.6 Luna。
開始時工作樹或基準hash：R03 commit `17975847`，分支 `feat/appendix-exodus25-revamp`。
已讀輸入與核准claim IDs：R03 typed data／schemas、`AppKernel`、`UIStateManager`、`ModeNavigation`、`ExperiencePanel`、`CinematicOverlay`；本卡沒有新增經文 claim。
變更檔案：`src/types/ui.ts` 新增 ritual／overlay／playback-owner 狀態；`UIStateManager.ts` 新增儀式選取、overlay 與 owner 單一寫入方法；`ModeNavigation.ts` 增加服事程序入口；`AppKernel.ts` 統一 cinematic／ritual 搶佔、重設與返回；`ExperiencePanel.ts` 支援 ritual mode；`AppShell.ts`／`CinematicOverlay.ts` 移除重複電影級入口文案；`UIStateManager.test.ts` 增加 ritual 返回測試。
Blender工作檔／recipe／source與derived hashes：沒有寫入 Blender 或資產。
驗收QA IDs：R04 四入口、單一 playbackOwner、ritual 開始／關閉、模式轉換無殘留播放器、aria 入口文案。
命令、exit code、log路徑：`npm run typecheck` exit 0；`npm test` exit 0（16 檔／35 tests）；`npm run build` exit 0（Vite production）；Browser preview 顯示四個模式按鈕「場景總覽／五站導覽／器物與經文／服事程序」，服事程序自動載入祭司洗濯並可關閉返回，dev logs 0。
畫面與activeAssetIds／profile／viewport證據：Browser desktop preview、預設 viewport；四入口與 ritual panel DOM 實測；未對 activeAssetIds 做新宣稱。
未驗證項目／限制／需總控判定：相機 pose、profile 與 overlay 尚未序列化成深連結或瀏覽器 history；R05 才處理 detail 非同步生命週期；R04 沒有 Blender 寫入。
結論（自驗／總控分開）：R04 自驗透過；四入口與播放所有權已納入狀態契約，尚未交 GPT-6 R24。
下一張任務ID、可直接執行的下一步：R05；修復六器物 detail 的真實非同步載入、generation/token 與錯誤恢復。
