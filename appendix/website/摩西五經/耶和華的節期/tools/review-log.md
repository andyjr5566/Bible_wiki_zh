# 內容審查紀錄（第一階段：開場＋逾越節）

審查者：Codex CLI 0.161.0，`codex exec --sandbox read-only`（唯讀）。每輪審完都跑 `git status util/`，兩輪都沒有變動。
預算：最多 2 輪；第 2 輪之後由主筆做最後修正，不再叫第 3 次審查（AGENTS.md）。

## 第 1 輪（2026-10-09）

- 指令：`tools/codex-review-1.md`。
- 範圍：story.yaml、commentary.yaml、step.yaml 全部。
- 結果：`VERDICT: PASS`，無 finding。

## 第 2 輪（2026-10-09，最後一輪）

- 指令：`tools/codex-review-2.md`。
- 範圍：第 1 輪之後的改動，包括：
  - `entry_gists` 11 句；
  - hyssop 拍加掛 `gt-tyndale-basin`；
  - 介面上涉及經文內容的字句。
- 結果：`VERDICT: CHANGES_REQUIRED`，1 條 finding。
  - `gt-tyndale-basin` 的轉述在 GT raw 第 404 行，但這一段本身沒有出處標記；第 406 行的「──《丁道爾聖經註釋》」屬於下一段，不能證明第 404 行也是丁道爾。

### 主筆查證

- 第 404 行之後是空行，第 406 行才是另一段，屬實。
- 專案正式護欄 `util/run_chapter.py` 的 `_nearest_gt_marker` 是「往後找最近的標記」，不看段落；照它判，第 404 行會算丁道爾。
- 第 404 行的音譯寫法（sap{）在全庫 GT raw 約九成出現在丁道爾段落，但也出現在其他子來源。
- 結論：證據傾向丁道爾，但沒有明確標記。網站公開掛名採較嚴的判準：**引文或轉述所在的那一段，結尾必須有該子來源的標記**。

### 依同一判準全面複查後的最後修正

同一型（本段無標記，靠下一段的標記掛名）共找到 4 處，第 1 輪都沒抓到：

| 位置 | GT raw | 處理 |
|---|---|---|
| `gt-tyndale-basin`（盆／門檻） | 第 404 行 | 刪除這則註釋；step.yaml 的 `saph` 說明改用 STEP 欄位＋黃迦勒（CT 第 112 行）＋KingComments（KC 第 89 行） |
| step.yaml `ezov`（墨角蘭、不合約19:29） | 第 404 行 | 改用《舊約聖經背景註釋》（第 412 行，有標記） |
| `gt-tyndale-fullmoon`（當是月圓） | 第 83 行 | 刪除；full-moon 拍只留《舊約聖經背景註釋》（第 140 行，有標記），highlight 改在「滿月」 |
| `gt-tyndale-pesach`（本節是對節期名稱唯一的解釋；越過／跳過） | 第 263 行（之後是 14～20 節的段落標題） | 刪除；midnight 拍改掛 `kc-passover-word`（KC 第 69 行）；step.yaml `pasach` 改用黃迦勒的原文字義（CT 第 222 行「越過」略過，跳過） |

### 機械防線

- `scripts/checks.mjs` 的 `attributionAfter` 改成只在引文所在段落裡找標記，遇空行就停。
- `scripts/checks.test.mjs` 加了反例測試。
- 現在網站的 GT 註釋 9 則都有逐字引文，全部通過這道段落級檢查。
- STEP 說明裡提到 GT 子來源的 6 處由主筆逐一回查，標記都在同一段：
  - 串珠第 132 行；
  - 丁道爾第 138、225、267 行；
  - 背景註釋第 176、227、412 行；
  - 丁良才第 390–391 行。

---

# 第二階段第一批（春季：月朔、無酵節、初熟的禾捆、二月逾越節、七七節）

## 第 1 輪（2026-10-09）

- 指令：`tools/codex-review-3.md`。
- 範圍：本批新增的內容，包括 story.yaml 18 拍、commentary.yaml 68 則、step.yaml 8 字、條目簡介 16 句。
- 結果：`VERDICT: CHANGES_REQUIRED`，2 條 finding，見 `tools/codex-review-3.out.md`。兩條同一個問題：BibleHub 利23:17「Unlike other offerings that required unleavened bread」被譯成「別的祭都要用無酵餅」，擴大了來源的說法。
- 主筆回查 `raw_data/biblehub_study_leviticus_23.txt` 第 251 行，屬實。已修 `bh-leaven-unlike` 的中譯和 `chamets` 的說明。
- Codex 另外說明：
  - 67 則逐字引文都在指定 raw 找到；
  - GT 引文都有本段標記；
  - STEP、敘述、條目簡介都核過。
- 審查前後 `git status util/` 無變動。

## 第 2 輪（2026-10-09，最後一輪）

- 指令：`tools/codex-review-4.md`，只複核上述兩處。
- 結果：`VERDICT: PASS`，無 finding，見 `tools/codex-review-4.out.md`。
- 審查前後 `git status util/` 無變動。
