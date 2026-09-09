# 會幕互動導覽網站

以出埃及記的會幕、器物與供職規範為核心的繁體中文3D研讀網站。技術為 Vite、TypeScript、Three.js、Zod。用途為非商業教育與研讀，保留所有第三方素材歸屬。

## 本輪工作入口

整站翻新依 [整站總規格](docs/planning/REVAMP_MASTER.md) 執行；目前 R00–R21 已自驗，R22–R24 仍在收尾。任務狀態只看 [實作進度](docs/planning/REVAMP_PROGRESS.md)，最後由 GPT-6 執行 R24 總控驗收。

本輪涵蓋六件器物、會幕剖面、角色／服飾、六種完整程序、五祭比較、經文與考古證據、手機與鍵盤操作、載入可靠性及效能。所有造型與事實依來源，未知保留未知。

目前程式提供 3D 總覽、五站導覽、六件器物研讀、六種服事程序、五祭比較、來源抽屜、手機抽屜與鍵盤操作。尚未驗證的瀏覽器故障、GPU 與實機效能項目，仍以進度檔和 QA 報告為準；舊工作指示已封存，見 [檔案登記](docs/planning/DOCUMENT_REGISTER.md)。

## 本機啟動

在本目錄執行；首次安裝依 lockfile：

```powershell
npm ci
npm run dev
```

依終端實際網址開啟，預設 `http://127.0.0.1:3001/`。

```powershell
npm run build
npm run preview
```

build 包含 typecheck、tests、architecture、assets。單獨驗證可跑 `npm run verify`。指定 preview 埠遇到 npm/PowerShell 轉傳問題時，直接執行 `npx vite preview --host 127.0.0.1 --port 4173`。

## 原始資料與交付

- 經文字文使用庫根 `raw_scripture/`；本站來源流程依 [證據契約](docs/planning/REVAMP_EVIDENCE.md)。
- 已下載模型與歸屬：[ASSETS](docs/ASSETS.md)、[授權歷史](docs/assets/LICENSE_AUDIT.md)。原source不覆寫，Blender改造另產衍生。
- 使用者研究素材：[REFERENCE_MATERIAL](docs/REFERENCE_MATERIAL.md)；可供查核，不直接當歷史真相。
- 可部署產物是 `dist/`，不是原始 `index.html`。既有建置／匯出方式見 [DEPLOYMENT](docs/DEPLOYMENT.md)，本批只交付本機預覽與產物，不自動發布。
