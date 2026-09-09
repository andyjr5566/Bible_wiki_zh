# 會幕互動導覽網站

以出埃及記的會幕、器物與供職規範為核心的繁體中文3D研讀網站。技術為 Vite、TypeScript、Three.js、Zod。用途為非商業教育與研讀，保留所有第三方素材歸屬。

## 本輪工作入口

整站翻新已完成規劃，尚未完成實作。GPT-5.6 Luna 請從 [整站總規格](docs/planning/REVAMP_MASTER.md) 與 [接手提示詞](docs/planning/LUNA_START.md) 開始，依 R00–R23 執行，最後交 GPT-6 執行 R24。狀態只看 [實作進度](docs/planning/REVAMP_PROGRESS.md)。

本輪涵蓋六件器物、會幕剖面、角色／服飾、六種完整程序、五祭比較、經文與考古證據、手機與鍵盤操作、載入可靠性及效能。所有造型與事實依來源，未知保留未知。

目前程式已有3D總覽、五站導覽、器物研讀與自動運鏡，但儀式與證據仍有缺口；詳見 [已核對現況](docs/planning/REVAMP_BASELINE.md)。不要以舊PASS或資料中存在角色／儀式ID推定功能完整。舊工作指示已封存，見 [檔案登記](docs/planning/DOCUMENT_REGISTER.md)。

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
