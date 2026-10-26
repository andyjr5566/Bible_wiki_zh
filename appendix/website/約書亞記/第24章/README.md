# 至於我和我家

約書亞記 24 章的互動研經網站，包含順讀故事、整理區、經文、註釋、原文與地圖。

## 開發

在 PowerShell 進入本站資料夾後執行：

```powershell
npm ci
npm run dev
npm run build
```

開發伺服器位於 `http://127.0.0.1:3024/`。`npm run build` 會先跑資料一致性、字體、型別、Vitest 與人物透明度檢查，再輸出 `dist/index.html` 與 `dist/assets/`。部署時必須複製整個 `dist/`，保留相對路徑；素材、字體、音效、模型與資料均使用帶雜湊的檔名。

## 開啟與部署

```powershell
npm run preview
# http://127.0.0.1:4224/
```

也可用 `python -m http.server 4225 --bind 127.0.0.1 --directory dist`，開啟 `http://127.0.0.1:4225/`。公開部署支援子目錄；共用 `appendix/website/build.py --build --deploy-dir <資料夾>` 會複製整個 `dist/`。

直接雙擊 `dist/index.html` 的 `file://` 開法已不支援：瀏覽器會限制 ES module 與本地資料請求，請使用本機 HTTP 伺服器。既有 Node 截圖工具已改由 `tools/site-server.mjs` 自動啟動僅監聽本機的伺服器，預設驗收已建置的 `dist/`；設定 `JOS_URL` 可改驗 preview 或部署後的子目錄。`acceptance-final.ps1` 預設使用 4224，執行前先啟動 preview。

## 素材載入

開場只下載序幕與第一幕的晨曦全景、人物圖集、橡樹、石材、模型與山谷高程。第二幕第一站在第一幕尾段預載；其後每讀到一站，就預載下一站。地圖暈渲到接近第二幕才下載。示劍其他時段在接近該時段時預載，跳讀會直接補載當前需要的素材。

站圖解碼完成前顯示柔和底色，完成後以 450ms 淡入；尚未載好的全景沿用已載好的畫面，再以 600ms 淡入。透明貼圖先使用透明底，石材先使用柔和底色。整理區的地圖底圖也接近視窗才載入。音效保持靜默，按下聲音開關後才下載。

經文優先預載本地芫荽子集，搭配 `font-display: block`；掛載最多等候 1.2 秒，失敗或逾時仍可使用後備字體閱讀。一般介面使用既有的系統字體後備順序，移除 Google Fonts 外部連線，避免額外下載整套字體。完整字型與授權仍留在來源資料夾；部署只包含子集。

冷快取實測首屏 **2,957,052 bytes（2.96 MB）**，完整讀完故事與整理區 **8,948,740 bytes（8.95 MB）**，開啟聲音後 **9,385,396 bytes（9.39 MB）**。這些是本機 gzip 伺服器的實際傳輸量，包含 HTTP 回應標頭；MB 以 1,000,000 bytes 計。量測採一般 WebGL 閱讀，包含逐站及所有整理區段；兩張只供無 WebGL 備援的石頭圖不在這條閱讀路線內。整個 `dist/` 共 99 檔、11,068,696 bytes。

WebP、MP3、WOFF2 與 GLB 使用原檔，HTML／JS／CSS／JSON 使用 gzip。公開主機必須啟用文字資源壓縮，才能重現首屏 ≤3 MB 的結果；未壓縮首屏素材合計約 4.03 MB，靜態伺服器仍可正常使用。主機的標頭與壓縮設定不同，傳輸量會有小幅差異。

完整數字與逐請求清單見 `.tmp-shots/loading/report.json`；桌機、手機延遲 1.8 秒的底色／淡入檢查與三種入口結果見 `checks.json`，部署檔案雜湊比對見 `deploy.json`。

## 資料與素材

- `data/*.yaml` 是本站手寫資料；`scripts/` 將故事、題卡與研經資料整理成 `src/data/` 的建置輸入。更新生成資料時執行 `npm run data`；只檢查一致性用 `npm run data:check`。`npm run data` 需要知識庫來源檔，獨立建置只使用已提交的 `src/data/`。
- Blender 場景與圖層在 `collect/`、`lab/`。`key_layers.py` 匯出命名圖層，`slice_sheet.py` 把圖層切成透明素材；第二幕站播放器依 `src/data/stations.json` 排列素材，重新輸出站圖執行 `npm run stations`。
- `素材來源.md` 記錄經文、註釋、地理、地形、插圖、3D 場景與音效的出處及授權。音效尚缺逐檔原始頁連結，補齊前需由維護者逐一核對。

## 驗收閘門

`npm run build` 包含 `npm run data:check`、`npm run font:check`、`npm run typecheck`、`npm run test`、`npm run alpha:check` 及 Vite 生產建置。字體閘門會檢查 WOFF2 實際字碼表是否包含故事經文用字；Vitest 同時檢查逐拍版位、十一站節奏及經文／短註互斥。

說書式經文的專項驗收：先建置，再執行 `powershell -NoProfile -File tools/storyteller.ps1 -Phase after`，最後執行 `python -I tools/analyze-storyteller.py`。截圖、60 秒自動播放抽樣、兩秒泡泡位移、節奏前後對照及像素對比分析均存於 `.tmp-shots/storyteller/`。`before.json` 是改動前保留的實測；不要用新版成品重新跑 `-Phase before` 覆蓋它。

完整網站另有 `powershell -NoProfile -File tools/acceptance-final.ps1`，用 headless Chrome 驗收桌機與手機的 36 拍、捲動穩定、直式轉向提示、目錄與新手教學；每種尺寸各 30 拍檢查實際像素動態比例，6 拍家人對話則檢查泡泡可見、文字與位置穩定。另檢查無 WebGL 靜止剪影及讀者可見文字。第二幕另有 `tools/shoot-act2.ps1` 的站點畫面檢查。瀏覽器驗收請逐套執行，避免多個 Chrome 同時取樣干擾時間間隔。

分檔部署與載入驗收：

```powershell
# 複製本站及所需依賴到 %TEMP%，不含 vault；共用建置程式保持原檔。
python -I tools/validate-deploy.py --prepare-only
$fixture = Get-Content -Raw -Encoding UTF8 .tmp-shots/loading/ci-prepared.json | ConvertFrom-Json
[IO.File]::WriteAllText((Join-Path $fixture.root 'package.json'), '{"type":"module","private":true}')
Push-Location $fixture.root
python -I $fixture.builder --build --deploy-dir $fixture.deploy
Pop-Location
python -I tools/validate-deploy.py --finish $fixture.root

# 先啟動 npm run preview；以下兩項依序執行。
powershell -NoProfile -File tools/measure-loading.ps1
powershell -NoProfile -File tools/measure-loading.ps1 -Script tools/check-loading.mjs
```

隔離建置使用複製的既有 `node_modules`，已驗證不依賴 vault；這項檢查不代表重新從網路執行過 `npm ci`。受限環境若拒絕工具向上搜尋使用者目錄，請在同一個 PowerShell 工作階段執行上述命令。所有正式程式修改仍僅在本站；TEMP 中的建置、部署與索引為隔離驗收副本。
