你正在接續「聖經研讀資料整理」專案。

本次要處理的書卷，請以使用者當前訊息指定的書名為準。

開始前必須先讀取：

```text
C:\Obsidian\Hermes\scripture\scheme.md
```

`scheme.md` 是最高規則。  
本 prompt 不重複規則細節；凡涉及資料夾結構、URL 模式、檔案模板、wiki-link、條目建立、驗證流程、commit 規則，全部以 `scheme.md` 為準。

請照以下開工流程執行：

1. 讀取 `scheme.md`
2. 解析使用者指定的書卷名稱
3. 檢查該書卷目錄與現有進度
4. 檢查 git 狀態
5. 判斷下一個需要處理的章節
6. 不要重做已完成且已通過驗證的章節
7. 只在缺資料時，依 `scheme.md` 指定來源與 URL 規則抓取資料
8. 建立或更新該章的經文、註解、拾穗、解說檔
9. 撰寫時依 `scheme.md` 建立 wiki-link
10. 所有 wiki-link 必須閉合到本地 markdown 檔案
11. 缺失條目依 `scheme.md` 建立正式條目或候選條目
12. 執行 `verify_links.py`
13. 修正缺失連結並重新驗證
14. 直到 0 破損連結
15. 驗證通過後 commit + push
16. 最後回報本章完成狀態、更新檔案、補建條目、verify 結果與 commit hash

限制：

- 禁止用 gbrain 寫入
- 禁止跳過 `verify_links.py`
- 禁止未驗證就 commit
- 禁止硬猜 URL
- 禁止把 `scheme.md` 已規定的細節改成自己的做法
- 禁止為了補條目而亂搜薄弱資料
- 禁止重做已完成且已驗證通過的章節
- 所有輸出使用繁體中文
