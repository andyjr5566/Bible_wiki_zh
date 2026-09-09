# 整站翻新執行進度

計畫版本：2026-09-10。GPT-6 已完成規劃與檔案整理；R00 已由目前 session 執行並完成基線產物。執行介面目前標示為 GPT-5，沒有把這次呼叫冒稱為 GPT-5.6 Luna；後續若使用者切換 Luna，從下一張未完成任務繼續。舊 Blender T0–T5 的完成宣告不轉換為新任務完成。

## 總狀態

- 當前階段：R13 自驗透過，下一張為 R14；R00–R23 尚未宣稱整站完成。
- 實際執行模型：本輪介面標示 GPT-5；GPT-5.6 Luna 尚未由工具實際呼叫確認。
- 最新測試／build：R13 後 `npm run build` exit 0；typecheck、19 個測試檔／43 個測試、architecture 100 modules、assets 17 assets 均通過；Vite production build 成功。`npm run verify:derived` 逐一讀取 17 件 processed GLB 並寫入 R12 sidecar。
- Blender：R07–R10 隔離工作檔與 stage manifest 已保留；R12 未寫入場景，只用 NodeIO 重新讀取 17 件 processed GLB。R07/R10 的 build/reimport metrics 與 R12 parsed metrics 分開記錄。
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
| R05 | detail生命週期 | R04 | 目前 GPT-5 session | 自驗透過 | [AssetRuntimeManager](../../src/systems/assets/AssetRuntimeManager.ts)、[AssetRuntimeManager.test](../../src/systems/assets/AssetRuntimeManager.test.ts)、[AppShell](../../src/components/AppShell.ts) |
| R06 | 空間／剖面／取景 | R05 | 目前 GPT-5 session | 自驗透過 | [CameraManager](../../src/scene/CameraManager.ts)、[DimensionVisualizer](../../src/scene/DimensionVisualizer.ts)、[asset-parts](../../src/data/asset-parts.json)、[CameraManager.test](../../src/scene/CameraManager.test.ts) |
| R07 | Blender流程 | R03,R06 | 目前 GPT-5 session | 自驗透過 | [README](../../scripts/blender/README.md)、[manifest](../../assets/staging/blender/r07/tabernacle-ark-alternative.r07-manifest.json) |
| R08 | 約櫃修正 | R07,R01 | 目前 GPT-5 session | 自驗透過 | [ARK_PARTS](../research/ARK_PARTS.md)、[assets](../../src/data/assets.json) |
| R09 | 完整會幕／照明 | R07,R08 | 目前 GPT-5 session | 自驗透過 | [R09 policy](../research/R09_LIGHTING_POLICY.md)、[screenshots](../qa/revamp/screenshots/) |
| R10 | 五件器物 | R07,R09 | 目前 GPT-5 session | 自驗透過 | [R10 register](../research/R10_ASSET_REGISTER.md)、[Blender configs](../../scripts/blender/config/) |
| R11 | 角色／服飾／牲畜 | R02,R07,R10 | 目前 GPT-5 session | 自驗透過 | [角色資產登記](../research/R11_CHARACTER_ASSET_REGISTER.md)、[CharacterAppearanceResolver](../../src/characters/CharacterAppearanceResolver.ts)、[截圖](../qa/revamp/screenshots/r11-character-card-desktop.png) |
| R12 | 匯出／資產登記 | R08,R09,R10,R11 | 目前 GPT-5 session | 自驗透過 | [R12 sidecar](../../assets/derived/r12-derived-assets.json)、[驗證器](../../scripts/verify-derived-assets.mjs)、[Blender README](../../scripts/blender/README.md) |
| R13 | 播放器／洗濯／香 | R04,R05,R06,R12 | 目前 GPT-5 session | 自驗透過 | [R13 播放器說明](../research/R13_RITUAL_PLAYER.md)、[RitualPlaybackController](../../src/rituals/RitualPlaybackController.ts)、[截圖](../qa/revamp/screenshots/r13-washing-player-desktop.png) |
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

## R05 執行回執

任務ID／起訖日期：R05／2026-09-10 03:20–03:45（Asia/Taipei）
執行模型／工具實測：目前 session 標示 GPT-5；以 AssetRuntimeManager 單元測試、production build 與 Browser preview 實測，未宣稱 GPT-5.6 Luna。
開始時工作樹或基準hash：R04 commit `aea22c51`，分支 `feat/appendix-exodus25-revamp`。
已讀輸入與核准claim IDs：R03 typed object IDs／asset manifest、R04 playback owner；沒有新增經文 claim。detail 資產仍沿用既有授權與 source hash。
變更檔案：`AssetRuntimeManager.ts` 增加 detail generation／request guard、profile 切換失效化與 runtime diagnostics；`AssetRuntimeState` 增加 selected／pending 診斷；`AppKernel.ts` 由器物選取自動切至 structural profile 並要求對應 detail，加入 selection generation；`AppShell.ts` 將產品狀態改為可讀數量並把技術診斷放 data attributes；`AssetRuntimeManager.test.ts` 新增延遲 A→B 快切負例。
Blender工作檔／recipe／source與derived hashes：沒有寫入 Blender、source GLB 或 processed GLB。
驗收QA IDs：R05 detail 真載入、A→B late response、profile revision、錯誤狀態與產品面板不洩露技術名詞。
命令、exit code、log路徑：`npm run build` exit 0（含 typecheck、36 tests、architecture 91 modules、assets 17 assets）；Browser preview 點選「器物與經文 → 約櫃」後 `data-runtime-profile=desktop-structural`、`data-active-asset-count=2`、`data-selected-asset=tabernacle-ark-alternative`，textContent 為「已就緒 · 已載入 2 項模型」；dev logs 0。
畫面與activeAssetIds／profile／viewport證據：Browser production preview 預設 desktop viewport；DOM 診斷確認 framework + ark detail 兩項 active 資產，學習面板顯示約櫃 typed detail；尚未宣稱手機取景或 GPU 指標。
未驗證項目／限制／需總控判定：GLTF loader 的跨 consumer 共享取消仍沿用既有 promise cache；完整錯誤重試 UI 與 R21 故障演練尚待後續；detail 是否完全隔離於每個 GLB 的部件邊界待 R06/R12 實測。
結論（自驗／總控分開）：R05 自驗透過；點選器物會真實觸發 detail pipeline，late response 不會覆蓋新選取，尚未交 GPT-6 R24。
下一張任務ID、可直接執行的下一步：R06；統一世界、部件 bounds、剖面取景與尺寸資料的座標契約。

## R06 執行回執

任務ID／起訖日期：R06／2026-09-10 03:45–04:05（Asia/Taipei）
執行模型／工具實測：目前 session 標示 GPT-5；以 CameraManager／資料契約測試、Vite build 與既有 Browser preview 驗證，未宣稱 GPT-5.6 Luna。
開始時工作樹或基準hash：R05 commit `66ef8b52`，分支 `feat/appendix-exodus25-revamp`。
已讀輸入與核准claim IDs：R03 尺寸與 evidence、R05 detail 資產 manifest、現有 WorldAlignment／CameraManager；未新增歷史 claim。
變更檔案：新增 `src/data/asset-parts.json`、`src/types/assetParts.ts`、`src/data/schemas/assetParts.ts` 並納入 loader；`DimensionVisualizer.ts` 維持只讀 typed dimension specs，未詳載尺寸不產生尺線；`CameraManager.ts` 改由 dimension specs 推導器物取景並補 ritual rig；`SceneBootstrap.ts` 傳入同一份 specs；更新 `CameraManager.test.ts` 與 `ProjectData.test.ts`。
Blender工作檔／recipe／source與derived hashes：沒有寫入 Blender、source GLB 或 processed GLB；用 GLB JSON chunk 讀取現有 detail node 名稱，未將未能確認的約櫃節點冒稱 verified。
驗收QA IDs：R06 世界 Y-up／東 +Z／至聖所 -Z、typed 尺寸、未知尺寸不數值化、asset part map、器物取景。
命令、exit code、log路徑：`npm run build` exit 0；typecheck、16 檔／36 tests、architecture 93 modules、assets 17 assets 均通過；CameraManager 測試確認取景由 specs 推導；`git diff --check` 無內容錯誤。
畫面與activeAssetIds／profile／viewport證據：未新增截圖；R05 Browser detail DOM 證據仍有效。未宣稱旋轉後、390×844 或各 GLB 可見部件已完成驗收。
未驗證項目／限制／需總控判定：現有相機仍以規則推導，尚未依每個 GLB 實際 bounds 做 R12 校準；約櫃、香壇與桌的部分節點名稱仍 unresolved；剖面恢復迴圈與門檻避障留待 R09/R17。
結論（自驗／總控分開）：R06 自驗透過；世界／取景／尺寸／部件資料已同源，未知部件維持 unresolved，尚未交 GPT-6 R24。
下一張任務ID、可直接執行的下一步：R07；建立安全可重現的 Blender 隔離工作檔與 staging 匯出流程。

## R07 ????

??ID??????R07?2026-09-10 04:05?04:55?Asia/Taipei?
???????????? session ?? GPT-5?Blender CLI `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe` ?????Blender 5.2.1 LTS?MCP addon ??? protocol 5 up-to-date?????????????????? MCP ??????
?????????hash?R06 commit `8e30f9f0`???????? Blender ????? `.blend1` ?????
???????claim IDs?R03/R06 asset manifest?`REVAMP_TASKS` R07??? `build_ark_detail.py`?`process-sketchfab-assets.mjs`???????????? R06 part map??????? claim?
??????? `scripts/blender/build_ark_detail.py`?????????? `clear_scene`??? config?owned collection?inspect?build?staging export?glTF Transform optimize?reimport check??? promotion??? `scripts/blender/config/ark.json`?`scripts/blender/README.md`??? staging `.blend`?staged?optimized GLB?manifest ??? before?after PNG?
Blender????recipe?source?derived hashes??? `ark_of_the_covenant_alternative.glb` SHA-256 `d8be215800501c9e39d7dc48b0552db75b3a86d11e73216d374aa47ef327e50a`?4,183,752 bytes?manifest ?? Blender 5.2.1?METRIC scale 1?-Z?Y ????????????staging optimized GLB ?? promotion ? public??? R08 ????????
??QA IDs?R07 ?? collection??? blend??????????????????source hash ???reimport metrics?????????
???exit code?log????? `blender --background --factory-startup --python scripts/blender/build_ark_detail.py -- --config scripts/blender/config/ark.json` ? exit 0???? log ?? `%TEMP%\ex25-r07-run2-final.log`?`npm run build` exit 0?16 ??36 tests?architecture 93?assets 17???? staging blend ???scene `EX25_R07_Work`?owned objects 9????? 2?
???activeAssetIds?profile?viewport???`assets/staging/blender/r07/previews/` ? before?after Front?Side?Top?Close ? 8 ???? metrics ?????model objects 4?meshes 3?triangles 41380?bounds size `[9.0, 2.1461100578308105, 1.8546199798583984]`??? `ArkAcaciaWoodImproved`?`ArkGoldImproved`?
???????????????????? optimized GLB promotion ? public??? framing ?? R12 ?? GLB ?? bounds ???MCP ?????????? addon ????????????
????????????R07 ????????? Blender ??????????????? GPT-6 R24?
?????ID???????????R08????????????????????????? mapping??????? promotion?

## R08 ????

??ID??????R08?2026-09-10 04:55?05:20?Asia/Taipei?
???????????? session ?? GPT-5??? Blender 5.2.1 CLI?glTF Transform?Vite preview ? Browser????? GPT-5.6 Luna?
?????????hash?R07 commit `903b9dc0`?R07 source hash `d8be215800501c9e39d7dc48b0552db75b3a86d11e73216d374aa47ef327e50a`?
???????claim IDs?R01 `CLAIMS.md`?R06 `asset-parts.json`?R07 manifest?config??25:10?22??37:1?9?? claim `C-EX25-ARK-SPEC`?`C-EX25-ARK-CHERUB`?????????????
?????`scripts/blender/config/ark.json` ?????? bounds region ????????????????????????????? source ???? unresolved??? `docs/research/ARK_PARTS.md`??? parts ???????? `src/data/assets.json` ? `public/models/manifest.json` revision?? R07 ????????? promotion ? processed/public?
Blender????recipe?source?derived hashes?source SHA-256 ?? `d8be215800501c9e39d7dc48b0552db75b3a86d11e73216d374aa47ef327e50a`?optimized?processed?public ?? GLB SHA-256 `3298d4c9ae45b1bb9c45239b55a4b698d1a3e6fa5507891b4815125a3b324dcf`?manifest ???? `ArkGoldImproved`?baseColor `[0.8,0.45,0.08]`?metallic 0.28?roughness 0.34???????roughness 0.72??
??QA IDs?R08 ??? mapping??????????????????????source?derived hash?R05 detail ????
???exit code?log???Blender `--promote` exit 0?log `%TEMP%\ex25-r08-final2-promote.log`??`npx gltf-transform inspect public/models/ark-alternative.glb` ?? 1 scene?3 meshes?2 materials?KHR_mesh_quantization?`npm run build` exit 0?16 ??36 tests?architecture 93?assets 17??Browser preview URL revision `20260910-r08-gold-1`??? detail DOM `data-selected-asset=tabernacle-ark-alternative`?`data-runtime-profile=desktop-structural`?`data-active-asset-count=2`?console logs 0?
???activeAssetIds?profile?viewport???`docs/qa/revamp/screenshots/r08-ark-detail-desktop.png`????????????????????? 2.5?1.5?1.5 ????????????????????
???????????????source GLB ????????????????? unresolved????????????? R12 ?????R07 staging blend ? Blender ??????????????? `.001`???????????????
????????????R08 ???????????????????? mapping ????????????? GPT-6 R24?
?????ID???????????R09?? R07 ????????????????????? zones?court?camp ??????
## R09 執行回執

任務ID／起訖日期：R09／2026-09-10 03:05–03:25（Asia/Taipei）
執行模型／工具實測：目前 session 標示 GPT-5；TypeScript、Vitest、Vite preview 與 Browser 實測；本卡沒有 Blender 寫入，沿用 R07/R08 已驗證的 GLB。
開始時工作樹或基準 hash：R08 commit `99df79d8`；分支 `feat/appendix-exodus25-revamp`。
已讀輸入與核准 claim IDs：R09 `REVAMP_TASKS.md`；R07/R08 Blender manifest、R08 `ARK_PARTS.md`；未新增經文 claim。
變更檔案（含刪除／原因）：`ParticleEffects.ts` 移除 Shekinah 光球／光柱、夜間火柱與粗錐體祭壇火；新增 `ParticleCue` opt-in 閘門與分組名稱，煙／燈火只在 cue 啟用且非學習細節焦點時顯示。`DesertEnvironment.ts` 將 midday 設為明確預設，降低三種氣氛的局部燈強度、背景山脊／地形飽和度、營地 instance（每組 24→12，合計 36）與營火亮度。`SceneBootstrap.ts` 曝光改為 0.98。`SettingsModal.ts` 移除「火柱」文案，改成已校準時間光影說明。新增 `ParticleEffects.test.ts` 與 `R09_LIGHTING_POLICY.md`。
Blender工作檔／recipe／source與derived hashes（適用時）：無；R08 公共 GLB hash 維持 `3298d4c9ae45b1bb9c45239b55a4b698d1a3e6fa5507891b4815125a3b324dcf`。
驗收QA IDs：R09 光照基線、無預設神聖光柱／粗錐體、cue 預設隱藏、遠景低干擾、總覽→器物細節可辨金材質。
命令、exit code、log路徑：`npm run typecheck` exit 0；`npm test` exit 0（17 檔／37 tests）；`npm run verify:architecture` exit 0（94 modules）；`npm run verify:assets` exit 0（17 assets）；`npm run build` exit 0；Browser preview console logs 0。
畫面與activeAssetIds／profile／viewport證據：`docs/qa/revamp/screenshots/r09-before-ark-detail-desktop.png`、`r09-ark-detail-desktop.png`、`r09-overview-desktop.png`；desktop preview 器物面板顯示「約櫃」，GLB 金材質與輪廓可辨，總覽無預設光柱。
未驗證項目／限制／需總控判定：R13–R15 尚未把程序 cue 接到播放器；營地與山脊仍是中性 reconstructed 背景，不能當歷史配置；R12 尚未逐一以 GLB bounds 校準所有器物。
結論（自驗／總控分開）：R09 自驗透過；已完成場景閱讀基線與 cue 邊界，尚未交 GPT-6 R24。
下一張任務ID、可直接執行的下一步：R10；依 R09 背景與 cue 邊界補齊五件器物的資料、分件與細節資產。
## R10 執行回執

任務ID／起訖日期：R10／2026-09-10 03:25–03:45（Asia/Taipei）
執行模型／工具實測：目前 session 標示 GPT-5；Blender 5.2.1 CLI、glTF Transform 4.4.2、TypeScript、Vitest、Vite preview 與 Browser 實測；五件 Blender 寫入嚴格逐件執行。
開始時工作樹或基準 hash：R09 commit `bc996b77`；分支 `feat/appendix-exodus25-revamp`。
已讀輸入與核准 claim IDs：R01/R03 資產規格、R06 part map、R07 pipeline、R09 lighting policy；C-EX27-BURNT-ALTAR、C-EX30-LAVER、C-EX30-INCENSE、C-EX25-MENORAH、C-LV24-LAMP、C-EX25-TABLE、C-LV24-BREAD。
變更檔案（含刪除／原因）：擴充 `build_ark_detail.py` 的 `autoCameras` 與 `stageId`，建立五個 R10 config；五件各自輸出 blend、staging GLB、optimized GLB、r10 manifest 與八張前後預覽；更新五個 runtime URL revision 與 public processing metadata；新增 `R10_ASSET_REGISTER.md`；README 補上多資產重跑規則。未改 raw_scripture 或來源 GLB。
Blender工作檔／recipe／source與derived hashes：五件 source SHA 分別為燔祭壇 `cfce6b18f5467ddecf325e0883f8aa6400bcd7cd99ab1a5640a84a8918bdd14b`、洗濯盆 `e50a5b0d54d39bab61abbbdad24dd00a731089eea218197ae45d376b0c7c15f3`、香壇 `03b8863c97c51c007ea02268fcd1b3de5f31df927e1f25acd2bed64e6b2028fb`、金燈臺 `eebae6562001cf9470e15d09da96061050da4f435d07401d1e8d4a81ff2252a8`、陳設餅桌 `3568f0a6208701a1fe34d7a43e691474037e5025496d35de65969ae9fbbb0160`；processed/public 已逐件 hash 相等，完整 derived hash 見 R10 register。
驗收QA IDs：五件各通過 source inspect、四視角預覽、材質／bounds、staging export、glTF Transform optimize、reimport metrics；來源節點不足的餅堆、水面與香壇部位保持 unresolved 或 source-node。
命令、exit code、log路徑：五次 `blender --background --factory-startup --python scripts/blender/build_ark_detail.py -- --config scripts/blender/config/r10-*.json --promote` 均 exit 0；`npm run verify:assets` exit 0（17 assets）；Browser 依序點選五個器物後 active detail 與 profile 正確，console logs 0。
畫面與activeAssetIds／profile／viewport證據：每件八張預覽位於 `assets/staging/blender/r10/<asset-id>/previews/`；Browser desktop preview 五件依序回報 `data-runtime-profile=desktop-structural`、active asset count 2，selected asset 分別為 `tabernacle-burnt-altar-detail`、`tabernacle-laver-detail`、`tabernacle-incense-altar-detail`、`tabernacle-menorah-detail`、`tabernacle-table-shewbread-detail`。
未驗證項目／限制／需總控判定：五件來源材質與幾何仍屬 reconstructed 資產；尺寸真值與 R14 餅／燈程序要由後續資料任務處理；R12 尚未完成全資產 GPU／bounds 統整。
結論（自驗／總控分開）：R10 自驗透過；五件 detail 資產已可獨立載入與重建，尚未交 GPT-6 R24。
下一張任務ID、可直接執行的下一步：R11；先檢查可合法複用的人物 rig，再建立角色／服飾／必要牲畜資源。

## R11 執行回執

任務ID／起訖日期：R11／2026-09-10 03:40–03:55（Asia/Taipei）
執行模型／工具實測：目前 session 標示 GPT-5；以 TypeScript／Zod／Vitest、Vite production build 與 Browser preview 實測。未把本輪呼叫冒稱為 GPT-5.6 Luna；沒有新增 Blender 寫入，沿用 R07–R10 已驗證的 Blender／GLB 產物。
開始時工作樹或基準hash：R10 commit `940c5ae4`；保留既有未追蹤 `.blend1` 復原備份。
已讀輸入與核准claim IDs：R02 `GARMENTS.md`、`ROLE_ACCESS.md`、R01 `CLAIMS.md`、R07–R10 資產臺帳；新增資料只使用 `C-EX28-ROLE-GARMENT`、`C-LV16-DAY`、`C-EX30-LAVER`、`C-EX30-INCENSE`、`C-LV24-LAMP`、`C-LV01-BRANCHES`、`C-NM-ROLES`。
變更檔案（含刪除／原因）：新增 `src/types/garment` 相關角色與服飾型別、`src/types/offerings.ts`、`src/data/garments.json`、`role-costumes.json`、`offerings.json` 及 Zod schemas；角色資料補上技術基底、職責、預設服裝與 disclosure；新增 `CharacterAppearanceResolver` 與測試；獻香角色修正為供職祭司，避免把普通祭司職責誤標成大祭司；研讀面板新增人物／服飾考據卡與必要樣式；新增 `R11_CHARACTER_ASSET_REGISTER.md`。
Blender工作檔／recipe／source與derived hashes（適用時）：本任務沒有寫入場景或重新匯出 GLB；角色模型維持 `priest-basic-human-library`、`priest-arab-man-library` 的 technical-base metadata，服飾專用 `assetId` 全部維持 `null`。
驗收QA IDs：角色職責分離、普通祭司／大祭司／贖罪日細麻衣三狀態、非法角色服裝組合 fail-closed、利未人角色位置示意、牛／羊／山羊／鳥分支與公牛性別要求、cow 候選不被分支引用、每個部件與 claim 可追溯。
命令、exit code、log路徑：`npm run typecheck` exit 0；`npm test` exit 0（18 檔／41 tests）；`npm run verify:architecture` exit 0（99 modules）；`npm run verify:assets` exit 0（17 assets）；`npm run build` exit 0；Browser preview `?r11=1` runtime errors 0、warnings 0。
畫面與activeAssetIds／profile／viewport證據：`docs/qa/revamp/screenshots/r11-character-study-desktop.png`、`r11-character-card-desktop.png`；學習面板顯示供職祭司、普通祭司日常聖衣、四個可追溯部件與技術基底 disclosure；本卡未宣稱角色 GLB 已載入世界場景。
未驗證項目／限制／需總控判定：R13–R16 尚未把角色 appearance 與播放器每一 step 的場景骨架、動作與贖罪日完整路徑接起來；服飾 mesh、山羊／鳥 mesh 沒有核准來源，維持文字／符號；角色位置仍是資料與面板展示，不是歷史實況動畫。
結論（自驗／總控分開）：R11 自驗透過；角色身份、職責、服裝狀態與供物分支已進入 typed data，技術基底與歷史服飾界線明示，尚未交 GPT-6 R24。
下一張任務ID、可直接執行的下一步：R12；依序檢查本批全部資產的 source／derived hash、重匯入、manifest 與重現流程，維持 source hash 語義不變。

## R12 執行回執

任務ID／起訖日期：R12／2026-09-10 04:00–04:15（Asia/Taipei）
執行模型／工具實測：目前 session 標示 GPT-5；Node.js `@gltf-transform/core`＋KHRONOS extensions 實測重新讀取全部 17 件 processed GLB，未把本輪呼叫冒稱為 GPT-5.6 Luna。沒有新增 Blender 寫入。
開始時工作樹或基準hash：R11 commit `37f15c17`；R07/R10 staging blend、manifest 與既有 `.blend1` 備份保留。
已讀輸入與核准claim IDs：`src/data/assets.json`、`public/models/manifest.json`、R00 `BASELINE_ASSETS.json`、R07/R10 stage manifests、`verify-assets.mjs`；本卡不新增經文 claim。
變更檔案（含刪除／原因）：新增 `scripts/verify-derived-assets.mjs` 與 `npm run verify:derived`；新增 `assets/derived/r12-derived-assets.json`、`public/models/derived-manifest.json`；typed/public asset manifest 增加 `derivedHash`／`derivedBytes` 與 sidecar 路徑；型別／schema同步；README 補上全資產重現說明。沒有刪除來源、processed 或 public runtime 資產。
Blender工作檔／recipe／source與derived hashes：17 件 source SHA 全部與 typed manifest 相同；17 件 processed/runtime SHA 逐件相同；R07/R10 stage optimized SHA 與 processed 對應。完整 source／derived／runtime hashes、bytes、bounds、materials、textures、animations 與 stage metrics 見 `assets/derived/r12-derived-assets.json`。
驗收QA IDs：source hash 語義不變、processed/runtime 對應、NodeIO reimport 可讀、mesh／三角面計數、材質／貼圖／動畫數量、軸向／單位、bounds、GPU upload conservative estimate、nodeMap／工具版本、R07/R10 instanced mesh 計數差異明示。
命令、exit code、log路徑：`npm run verify:derived` exit 0（17 assets）；`npm run verify:assets` exit 0（17 assets）；`npm run typecheck` exit 0；完整 `npm run build` 將在本階段收尾重跑。
畫面與activeAssetIds／profile／viewport證據：R12 為資產與部署資料驗收，未新增畫面；R10 Browser 逐件 detail 證據與 R11 角色面板截圖維持有效。
未驗證項目／限制／需總控判定：GPU 實際上傳量與 frame-time 沒有 profiler 證據，sidecar 只記錄 processed bytes 的保守估計；未重跑未修改資產的 Blender recipe，只重新解析 processed GLB；R13 尚未把角色／服飾接入播放器。
結論（自驗／總控分開）：R12 自驗透過；source hash、derived hash、runtime 對應、17 件 GLB 重新讀取與 manifest/sidecar 均完成，尚未交 GPT-6 R24。
下一張任務ID、可直接執行的下一步：R13；以 R04–R06 的單一 owner 與 R11 appearance 資料建立通用程序播放器，先完成洗濯與日常獻香的逐步可回復流程。

## R13 執行回執

任務ID／起訖日期：R13／2026-09-10 04:20–04:45（Asia/Taipei）
執行模型／工具實測：目前 session 標示 GPT-5；TypeScript／Vitest、Vite production build 與 Browser preview 實測，沒有把本輪呼叫冒稱為 GPT-5.6 Luna。未寫入 Blender。
開始時工作樹或基準hash：R12 commit `2a8976d8`；R07–R12 資產與 sidecar 保持原狀。
已讀輸入與核准claim IDs：R02 `RITUAL_STEPS.md`、`ROLE_ACCESS.md`、`GARMENTS.md`，R09 cue policy、R11 appearance data；C-EX30-LAVER、C-EX30-INCENSE。
變更檔案（含刪除／原因）：洗濯與日常獻香各由單步改為三步資料鏈，補齊 actor／character／garment／object／location／source／displayCue／unresolved；`RitualPlaybackController` 新增依 `nextStepIds` 前進、上一部、seek、replay 與越界 fail；`RitualVisualSystem` 依 step 隱藏獻香界線煙霧；`ParticleEffects` 增加清除 narrative cues；AppKernel 將 step 與 cue、角色服飾同步並在退出清理；程序面板加入進度、上一／下一步、暫停／重播／退出與未知項目；新增 R13 controller／visual tests、說明文件與截圖。
Blender工作檔／recipe／source與derived hashes（適用時）：沒有 Blender 寫入或 GLB 變更；沿用 R12 verified asset hashes。
驗收QA IDs：洗濯「走近→洗手洗腳→前往服事」；獻香「早晨→黃昏→日常界線」；nextStep graph、previous、pause/resume、replay、seek、complete、idle／越界錯誤、角色與 daily-priest 狀態、日常煙霧 cue 與 boundary 隱藏。
命令、exit code、log路徑：`npm run typecheck` exit 0；`npm test` exit 0（19 檔／43 tests）；`npm run verify:architecture` exit 0（100 modules）；`npm run verify:assets` exit 0（17 assets）；`npm run build` exit 0；Browser `?r13-final=1` console/runtime errors 0、warnings 0；畫面為真實 WebGL preview，非 DOM-only 模擬。
畫面與activeAssetIds／profile／viewport證據：`docs/qa/revamp/screenshots/r13-washing-player-desktop.png` 顯示服事程序、1/3 進度、洗濯盆高亮與操作列；先前 `r13-incense-boundary-desktop.png` 顯示獻香界線資料。R13 未更換 detail asset，active detail 仍依 R10/R12 證據。
未驗證項目／限制／需總控判定：R14 尚未接燈臺與陳設餅完整資料；洗濯與獻香目前只接 R02 兩程序，燔祭分支與贖罪日仍待 R15/R16；角色 mesh 仍為技術基底，位置與動作以標籤／高亮示意。
結論（自驗／總控分開）：R13 自驗透過；兩個程序共用可回復播放器並同步角色／服飾／器物／來源，未宣稱未載的寫實動作或永久特效，尚未交 GPT-6 R24。
下一張任務ID、可直接執行的下一步：R14；沿用同一播放器接入燈臺與陳設餅的計數、時段與 cue，建立完整 step snapshots。
