# HANDOFF：Gemini 額度用完時，由 Claude 子代理接手

使用者 2026-10-25 決定：Gemini 4 Argon 額度用完時，由總監（Claude）派子代理從目前磁碟狀態接手，不重做。

## 接手的人先讀

1. `GOAL.md`（含 0.1 分工調整：3D 先做、蒐集成果在 `collect/`）
2. `Claude.md`（設計定案）
3. `PLAN.md`（拍表、契約檔、閘門）
4. `進度.md` 最後一節（Gemini 做到哪裡）
5. `git status`、`git diff --stat` 看本站資料夾目前的改動；`npm run build`（PowerShell）看現在能不能建置

## 規則

- GOAL.md 的權限、內容規則、網站規則全部照舊；只寫本站資料夾。
- 不重寫 Gemini 已完成且建置通過的部分；從 `進度.md` 記的下一步接著做。
- 若建置是壞的，先修到 `npm run build` 通過再往下做。
- 每做完一段，照 GOAL.md 第 9 節格式在 `進度.md` 加一節，標明「接手者：Claude 子代理」。

## 待套用的蒐集成果

- `collect/dem/`：三張高程圖（示劍山谷 zoom 13、迦南、廣域），格式見各 `*_meta.json` 與 README；署名照 README。
- `collect/audio/`：`audio-candidates.md`；後製版本在 `processed/`（人群低語、人群聲浪、大河、海水合攏、石頭落地）。
- `collect/places/位置考證.md`、`survey.json`：要改的地方——
  1. 大河：`places.yaml` 的 overrideLon/Lat 41.2、35.4 離河道約 74 公里，改用報告建議的河道代表點；
  2. 埃及：說明寫歌珊一帶但座標是全國代表點，改用報告建議的歌珊點（與民數記33章網站的蘭塞一致）；
  3. 曠野路線：`scripts/build-geodata.mjs` 把加低斯排在以旬迦別前面，民33 是以旬迦別（第32站）在前、加低斯（第33站）在後，改正並加閘門；
  4. 證壇、迦實山、非尼哈的小山、基列米斯巴改標位置不詳；
  5. 有爭議的 9 處：地圖用報告建議的最可信說法，其他說法放資訊卡的補充說明。
- `collect/refs/`：建模參考圖與 `refs.md`（Codex 蒐集中，可能還沒到）。
