# Agent Start Prompt

你正在接續「聖經研讀資料整理」專案。

本次要處理的書卷，請以使用者當前訊息指定的書名為準。

開始前必須先讀取：

```text
C:\Obsidian\Hermes\scripture\scheme.md
```

`scheme.md` 是最高規則。  
## 開工流程

請依序執行：

1. 讀取 `scheme.md`
2. 解析使用者指定的書卷名稱
3. 檢查該書卷目錄是否存在
4. 檢查該書卷現有章節主檔與完成進度
5. 執行 `python3 build_link_index.py` 建立最新 link index
6. 檢查 git 狀態
7. 判斷下一個需要處理或修正的章節
8. 不要重做已完成且已通過驗證的章節
9. 只在缺資料時，依 `scheme.md` 指定來源與 URL 規則抓取資料
10. 抓取後清理來源，根據來源內容建立 `【書名】/.tmp/第x章/link_candidates.md`
11. 執行 `python3 resolve_link_candidates.py 【書名】 X，產生 `link_plan.md`
		例如:`python3 resolve_link_candidates.py 創世記 13`
12. **根據 link_plan 寫章節主檔**：`【書名】/第x章.md`（經文 + wiki-link + 補充資料）
13. **根據 link_plan 更新 link folder**（B類補充、C類新建、D類候選）
14. 執行 `python3 check_existing_links.py 【書名】/第x章.md --missing`
15. 執行 `python3 link_quality_check.py 〖書名〗`
16. 執行 `python3 verify_links.py 〖書名〗`
17. 修正任何 broken links / invalid refs / critical quality warnings
18. 重跑驗證直到全部通過
19. 通過後 git commit + push
20. 最後回報本章完成狀態、更新檔案、補建條目、驗證結果與 commit hash

---

## 限制

- 禁止用 gbrain 寫入
- 禁止跳過 `scheme.md`
- 禁止跳過 `build_link_index.py`、`resolve_link_candidates.py`
- 禁止跳過 `verify_links.py`、`link_quality_check.py`
- 禁止未驗證就 commit
- 禁止硬猜 URL
- 禁止把 `scheme.md` 已規定的細節改成自己的做法
- 禁止為了補條目而亂搜薄弱資料
- 禁止建立只有 2-3 行的薄弱 stub
- 禁止重做已完成且已驗證通過的章節
- 禁止再建立舊架構的 `經文/`、`註解/`、`拾穗/`、`解說/` 平行章節檔
- 禁止把四大來源硬分配到固定資料夾；應依內容性質判斷放入章節主檔或適合的 link folder
- 禁止同一個條目在多個 link folder 重複建立
- 禁止根據 link_plan.md 直接撰寫條目內容而不回到來源資料
- 禁止為未來章節預先建立空白章節檔
- 禁止對正式條目的定義/核心摘要/主題發展區塊每章亂改
- 所有輸出使用繁體中文
