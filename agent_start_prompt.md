# Agent Start Prompt

本次要處理的書卷，請以使用者當前訊息指定的書名為準。

開始前必須先讀取：

```text
C:\Obsidian\Hermes\scripture\scheme.md
```

`scheme.md` 是最高規則。

## 開工流程

請依序執行：

1. 讀取 `scheme.md`
2. 解析使用者指定的書卷名稱與章節需求
3. 執行 `python util/build_link_index.py` 建立最新 link index
4. 檢查 git 狀態
5. 判斷下一個需要處理或修正的章節
6. 不要重做已完成且已通過驗證的章節
7. **讀取經文**：本地 `raw_scripture/{資料夾名}/第{章}.txt`
8. 建立或確認暫存資料夾：`【書名】/.tmp/第x章/`
9. **確認補充資料來源 URL**：ccbiblestudy CT/GT、KingComments、BibleHub Study，或使用者指定來源
10. **使用 `util/crawl_bible_text.py` 產生 raw text**：
    ```text
    python util/crawl_bible_text.py "{URL}" --output_path raw_data --output_filename "{source}_{book_slug}_{chapter}"
    ```
    例：
    ```text
    python util/crawl_bible_text.py "https://biblehub.com/study/daniel/3.htm" --output_path raw_data --output_filename "biblehub_study_daniel_3"
    ```
11. 若 raw text 檔案已存在，預設直接沿用；只有確認內容錯誤或使用者要求時才加 `--overwrite`
12. 讀取這次 `util/crawl_bible_text.py` 產生的 raw text
13. 建立或更新 `【書名】/.tmp/第x章/source_manifest.md`，記錄每個來源的 URL、raw_data 檔案與狀態
14. 讀取所有有效的 `raw_data/*.txt`，檢查是否為本章內容、是否有效、是否有研讀資料
15. 根據經文與有效 raw text 建立 `【書名】/.tmp/第x章/link_candidates.md`
16. 執行 `python util/resolve_link_candidates.py 【書名】 X`，產生 `link_plan.md`
    - 章數 `X` 一律使用阿拉伯數字，不加「第」與「章」
    - 例如：`python util/resolve_link_candidates.py 創世記 13`
17. 檢查 `link_plan.md` 的分類衝突與 alias 歧義；D 類不得自動建立或連結
18. **根據 link_plan 寫章節主檔**：`【書名】/第x章.md`（經文 + wiki-link + 補充資料）
    - 章節檔建立後執行 `python util/build_fhl_maps.py`，由程式將相關地圖同步到經文正文之後
    - 不得手工建立或修改 `fhl-map-links` 管理區塊
19. **根據 link_plan 更新 link folder**：
    - B 類先執行 `python util/link_updates.py prepare 【書名】 X`
    - 回到經文與有效 raw text 填寫 `link_updates.yaml`
    - 執行 `python util/link_updates.py apply 【書名】/.tmp/第x章/link_updates.yaml --dry-run`
    - 確認後執行 `python util/link_updates.py apply 【書名】/.tmp/第x章/link_updates.yaml`
    - 重跑 apply 必須顯示 0 個變更
    - 確認章次位於 `按書卷累積 → ### 書卷名 → #### 第N章`，並依章號排序
    - C 類依來源建立正式條目；D 類人工判斷；E 類不連
20. 執行 `python util/check_existing_links.py 【書名】/第x章.md --missing`
21. 執行 `python util/build_link_index.py`
22. 執行 `python util/validate_knowledge_base.py`
23. 執行 `python util/link_quality_check.py 【書名】`
24. 執行 `python util/verify_links.py 【書名】`
25. 執行 `python util/audit_knowledge_base.py --check-due`
26. 修正任何 schema errors / broken links / invalid refs / unknown links / critical quality warnings
27. 重跑驗證直到全部通過
28. 若累計完成章數到達 10 章里程碑，執行 `python util/audit_knowledge_base.py --all --checkpoint 10` 並人工檢查報告
29. 若完成一卷，執行 `python util/audit_knowledge_base.py --book 【書名】`，清理 alias、候選條目與重複概念
30. 通過後 git commit + push，確認 CI 通過
31. 最後回報本章完成狀態、更新檔案、補建條目、驗證結果與 commit hash

---

## raw text 原則

- 補充資料不可直接使用網頁內容整理。
- 所有補充資料必須先透過 `util/crawl_bible_text.py` 存成 `raw_data/*.txt`。
- `util/crawl_bible_text.py` 的輸入是 URL，輸出是該網站清理後的 raw text。
- `--output_filename` 不必加 `.txt`，程式會自動補上。
- 檔案已存在時不覆蓋；需要覆蓋才加 `--overwrite`。
- 建立 link_candidates.md 時，只能使用經文與已成功取得、已檢查有效的 raw text。
- 無效來源要記錄在 `source_manifest.md`，不可假裝已使用。
- 不設定每章正式條目數量上限，也不因人物看似普通而先驗排除；建立與否只由已收集資料決定。
- B 類的 `link_updates.yaml` 必須記錄實際 `sources` 與 `source_files`，不得用工具生成無來源內容。

---

## 限制

- 禁止用 gbrain 寫入
- 禁止跳過 `scheme.md`
- 禁止跳過 `util/build_link_index.py`、`util/resolve_link_candidates.py`
- 禁止跳過 `util/link_updates.py`（有 B 類時）、`util/validate_knowledge_base.py`、`util/verify_links.py`、`util/link_quality_check.py`、`util/audit_knowledge_base.py --check-due`
- 禁止未驗證就 commit
- 禁止硬猜 URL
- 禁止直接把網頁內容抓進 context 後整理
- 禁止跳過 `util/crawl_bible_text.py` 直接使用網站資料
- 禁止在 raw_data 檔案已存在且未確認錯誤時任意使用 `--overwrite`
- 禁止把無效 raw text 當作有效來源
- 禁止把 `scheme.md` 已規定的細節改成自己的做法
- 禁止為了補條目而亂搜薄弱資料
- 禁止建立只有 2-3 行的薄弱 stub
- 禁止重做已完成且已驗證通過的章節
- 禁止再建立舊架構的 `經文/`、`註解/`、`拾穗/`、`解說/` 平行章節檔
- 禁止把五大來源硬分配到固定資料夾；應依內容性質判斷放入章節主檔或適合的 link folder
- 禁止同一個條目在多個 link folder 重複建立
- 禁止根據 link_plan.md 直接撰寫條目內容而不回到來源資料
- 禁止為未來章節預先建立空白章節檔
- 禁止對正式條目的定義/主題發展區塊每章亂改；正式條目不另建容易與定義重複的核心摘要區
- 禁止把章次累積附加到主題發展、相關條目或來源依據之後
- 禁止把 `secondary_types` 當 alias
- 禁止忽略分類衝突、alias 多重指向或同名條目衝突
- 禁止為比對方便而刪除候選名稱中的括號內容
- 禁止只用「第x章」字串判斷累積完成，必須同時核對書卷與章數
- 禁止自動刪除、合併、移動或升級巡檢報告列出的條目；必須人工判斷並回到來源
- 既有格式需要遷移時，先執行 `python util/normalize_format.py --scope all --dry-run`；套用後必須重跑確認 0 變更，並用 `--verify-base` 確認條目正文未遺失
- 所有輸出使用繁體中文

---

## debug

- 若python util/verify_links.py 沒過
	1. 確認主章的link 有沒有寫完
	2. 若是有，應該是主要章節沒寫好,先讀在檢查link 寫法是否有誤 (90% 問題出在這)
    3. 若是依然沒過,檢查 broken link 在 link folder 的所在檔案, link 寫法是否有錯
    4. 若是沒過，在考慮這個是不是不用設link
