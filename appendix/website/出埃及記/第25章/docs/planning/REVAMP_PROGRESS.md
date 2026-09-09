# 整站翻新執行進度

計畫版本：2026-09-10。GPT-6 已完成規劃與檔案整理；R00 已由目前 session 執行並完成基線產物。執行介面目前標示為 GPT-5，沒有把這次呼叫冒稱為 GPT-5.6 Luna；後續若使用者切換 Luna，從下一張未完成任務繼續。舊 Blender T0–T5 的完成宣告不轉換為新任務完成。

## 總狀態

- 當前階段：R00 自驗透過，下一張為 R01；R00–R23 尚未宣稱整站完成。
- 實際執行模型：本輪介面標示 GPT-5；GPT-5.6 Luna 尚未由工具實際呼叫確認。
- 最新測試／build：`npm run build` exit 0；typecheck、16 個測試檔／33 個測試、architecture 81 modules、assets 17 assets 均通過；Vite production build 成功。
- Blender：本輪 `get_scene_info` 唯讀呼叫成功，Scene 有 24 個物件、5 個材質，回傳含 `Sketchfab_model`／`Root`。未改場景；儲存／dirty 狀態未由該回應確認，後續依 R07 隔離工作檔規則。
- 網站成熟化：未完成。發布：未執行。
- 前一批缺口：見 [REVAMP_BASELINE](REVAMP_BASELINE.md) B01–B15。

## 任務狀態

| ID | 任務 | 最小相依 | 執行者 | 狀態 | 證據 |
| --- | --- | --- | --- | --- | --- |
| R00 | 工具與基準 | — | 目前 GPT-5 session | 自驗透過 | [BASELINE](../qa/revamp/BASELINE.md)、[資產計量](../qa/revamp/BASELINE_ASSETS.json)、[截圖](../qa/revamp/screenshots/) |
| R01 | 來源臺帳 | R00 | Luna | 待辦 | — |
| R02 | 角色／程序契約 | R01 | Luna | 待辦 | — |
| R03 | 資料與抽取 | R01,R02 | Luna | 待辦 | — |
| R04 | 入口／狀態 | R03 | Luna | 待辦 | — |
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
