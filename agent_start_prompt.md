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
3. 檢查該書卷目錄是否存在
4. 檢查該書卷現有章節主檔與完成進度
5. 執行 `python3 build_link_index.py` 建立最新 link index
6. 檢查 git 狀態
7. 判斷下一個需要處理或修正的章節
8. 不要重做已完成且已通過驗證的章節
9. **讀取經文**：本地 `raw_scripture/{資料夾名}/第{章}.txt`
10. 建立或確認暫存資料夾：`【書名】/.tmp/第x章/`
11. **確認補充資料來源 URL**：ccbiblestudy CT/GT、KingComments、BibleHub Study，或使用者指定來源
12. **使用 `crawl_bible_text.py` 產生 raw text**：
    ```text
    python crawl_bible_text.py "{URL}" --output_path raw_data --output_filename "{source}_{book_slug}_{chapter}"
    ```
    例：
    ```text
    python crawl_bible_text.py "https://biblehub.com/study/daniel/3.htm" --output_path raw_data --output_filename "biblehub_study_daniel_3"
    ```
13. 若 raw text 檔案已存在，預設直接沿用；只有確認內容錯誤或使用者要求時才加 `--overwrite`
14. 讀取這次`crawl_bible_text.py` 產生的 raw text
15. 建立或更新 `【書名】/.tmp/第x章/source_manifest.md`，記錄每個來源的 URL、raw_data 檔案與狀態
16. 讀取所有有效的 `raw_data/*.txt`，檢查是否為本章內容、是否有效、是否有研讀資料
17. 根據經文與有效 raw text 建立 `【書名】/.tmp/第x章/link_candidates.md`
18. 執行 `python3 resolve_link_candidates.py 【書名】 X`，產生 `link_plan.md`
    - 章數 `X` 一律使用阿拉伯數字，不加「第」與「章」
    - 例如：`python3 resolve_link_candidates.py 創世記 13`
19. **根據 link_plan 寫章節主檔**：`【書名】/第x章.md`（經文 + wiki-link + 補充資料）
20. **根據 link_plan 更新 link folder**（B類補充、C類新建、D類候選）
21. 執行 `python3 check_existing_links.py 【書名】/第x章.md --missing`
22. 執行 `python3 build_link_index.py`
23. 執行 `python3 link_quality_check.py 【書名】`
24. 執行 `python3 verify_links.py 【書名】`
25. 修正任何 broken links / invalid refs / unknown links / critical quality warnings
26. 重跑驗證直到全部通過
27. 通過後 git commit + push
28. 最後回報本章完成狀態、更新檔案、補建條目、驗證結果與 commit hash

---

## raw text 原則

- 補充資料不可直接使用網頁內容整理。
- 所有補充資料必須先透過 `crawl_bible_text.py` 存成 `raw_data/*.txt`。
- `crawl_bible_text.py` 的輸入是 URL，輸出是該網站清理後的 raw text。
- `--output_filename` 不必加 `.txt`，程式會自動補上。
- 檔案已存在時不覆蓋；需要覆蓋才加 `--overwrite`。
- 建立 link_candidates.md 時，只能使用經文與已成功取得、已檢查有效的 raw text。
- 無效來源要記錄在 `source_manifest.md`，不可假裝已使用。

---

## 限制

- 禁止用 gbrain 寫入
- 禁止跳過 `scheme.md`
- 禁止跳過 `build_link_index.py`、`resolve_link_candidates.py`
- 禁止跳過 `verify_links.py`、`link_quality_check.py`
- 禁止未驗證就 commit
- 禁止硬猜 URL
- 禁止直接把網頁內容抓進 context 後整理
- 禁止跳過 `crawl_bible_text.py` 直接使用網站資料
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
- 禁止對正式條目的定義/核心摘要/主題發展區塊每章亂改
- 所有輸出使用繁體中文
