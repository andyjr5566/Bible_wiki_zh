# Agent Maintenance Prompt（維護既有章節與 link_folder 條目）

新章製作照 `agent_start_prompt.md` 走。本檔管的是**維護**：章節做完之後，回頭修改
`.tmp/第x章/` 的內容（M3 條目、M6 本章整理、候選、B 類累積），要怎麼把修改正確地
落到渲染後的 `第x章.md` 與 `link_folder/**.md`。

## 三條前提原則

1. **Source of truth 是 `.tmp/第x章/` 的 yaml，不是渲染出來的 markdown。**
   只改 `第x章.md` 或 `link_folder/**.md` 而不改 yaml，下次重跑 render 就被覆蓋回舊內容
   （申4 鐵爐實測）。唯一例外見下方「既有條目 md 的地位」。
2. **零 API**：重跑一律用 `util/run_chapter_manual.py`（`check` → `run`），不用
   `run_chapter.py`——manual 版是原版 orchestrator 加 guard runner（模型步驟被觸發＝
   直接報錯）與作廢預警，護欄完全相同。`link_updates.py` 本來就不呼叫模型，照原版用。
3. **內容鐵律不因維護而放鬆**：修改後的文字仍必須能對回經文與本章四來源
   （`.tmp/第x章/manual/sources.md` 或 `source_manifest.md` 列的 raw_data 檔）；
   新增的引句、經文引註、音譯都要先 grep raw_data 確認出處。

## 對照表：改了什麼 → 跑什麼

| 修改的檔案 | 之後跑 | 說明 |
| --- | --- | --- |
| `chapter_content.yaml`（M6 本章整理／knowledge_nodes） | `check` → `run` | 最單純：不觸發任何作廢，render 每跑必重寫 `第x章.md` |
| `entry_content/*.yaml`（M3 條目內容） | `check` → `run --keep-chapter` | run 會偵測 entry 變動要作廢 chapter_content；`--keep-chapter` 保住本章整理、只重生 verse_links |
| `link_candidates.yaml`（候選／surfaces） | `prompts --confirm-stale` → 補 payload → `check` → `run` | **會連鎖刪除手寫 payload**，見下方專節 |
| `link_updates.yaml`（B 類累積 summary/relation） | `link_updates.py apply ... --dry-run` → `apply` | 不歸 run_chapter 管；重跑 apply 必須 0 變更 |
| 既有條目 md（帶其他章累積標記者） | 直接改 md（見下方） | render 對這類檔有覆寫保護，不會打回 |

指令都是 `python util/run_chapter_manual.py <子指令> 【書名】 X`；
`link_updates.py` 用法同 `agent_start_prompt.md` 步驟4。

## 各情境細節

### A. 改 M6（chapter_content.yaml）

最常見的維護（勘誤本章整理、補小節、修圖表）。注意：

- `organization` 用 YAML `|` 字面區塊；mermaid 圖內**不可**有 `[[ ]]`（節點一律
  `A["標籤"]`）；表格格內不可放帶別名連結；knowledge_nodes 項目寫裸名或
  `名稱|小標題`，**不要**自己包 `[[ ]]`。
- wiki-link 白名單＝本章 A/B 既有條目＋C 實建條目；清單外的概念用純文字。
  `check` 會擋，且會把 `[[alias]]` 機械改寫成 `[[全名|alias]]` 並回寫。
- 改完：`check` → `run`。

### B. 改 M3（entry_content/*.yaml）

修條目的 definition／development／accumulations／sources 等欄位：

- 改完：`check` → `run --keep-chapter`。不帶 `--keep-chapter` 時 run 會擋下並說明
  （原版行為是作廢 verse_links＋chapter_content 重找模型生成；人工模式沒有模型，
  作廢＝刪掉你手寫的本章整理）。
- `--keep-chapter` 的前提是「本章整理不受這次條目修改影響」——若改了條目**名稱**或
  **aliases**，chapter_content 的 knowledge_nodes／organization 連結可能跟著要改，
  先改好再 `check`（白名單驗證會抓）。
- **改條目名是高風險操作**：渲染過的舊 md 會殘留在 link_folder、全庫手寫連結會斷。
  正確作法：先 `python util/rename_markdown.py <舊md> <新md>`（同步全庫 WikiLink），
  再把 `.tmp` 內出現舊名的地方（candidates、entry yaml 的 name＋檔名、
  chapter_content 的節點與連結）全改成新名，然後照情境 C 走。

### C. 改候選（link_candidates.yaml）

**這條會連鎖作廢下游**（link_plan → entry_content → verse_links／chapter_content），
包括你手寫的 payload。紀律：

1. 動手前先確認 `.tmp` 已 commit（`.tmp` 有進 git——這就是備份）。
2. `prompts 【書名】 X` 會先擋下並列出將被刪除的手寫產物；確認後加 `--confirm-stale`。
3. 作廢後，**內容不受這次候選改動影響的 payload 可以用 git 挑著還原**
   （例：只改了某候選的 surfaces → 其他條目的 yaml、甚至該條目的 yaml 本身都可
   `git checkout -- <路徑>` 還原；改了名稱／type 的候選對應 payload 就要重寫）。
4. 缺的 payload 依 `manual/*.prompt.md` 補寫 → `check` → `run`。
5. 候選改名後記得同步 `chapter_content.yaml` 裡的手寫連結（resolver 認得裸名，
   Obsidian 不認——這是「兩閘門全過卻斷鏈」的老坑）。
6. 候選有實質增刪時，照 `agent_start_prompt.md` 步驟2 重跑
   `python util/semantic_lookup.py --candidates 【書名】 X` 更新近鄰報告。

### D. 改 B 類累積（link_updates.yaml）

- 改 `summary`／`relation` 後：`python util/link_updates.py apply 【書名】 X --dry-run`
  確認 diff → 去掉 `--dry-run` 實跑 → **再跑一次 apply 必須 0 變更**。
- 累積標記的書卷名必須是正規全名（`accumulation:民數記:4`，不可用簡稱）。
- 收累積孤兒（條目有累積、章卻沒連回）用 `python util/check_accumulation_orphans.py`。

### E. 既有條目 md 的地位（link_folder/**.md）

- **本章新建（C 類）、且尚未被其他章累積**：md 是 render 產物，修內容一律回
  `entry_content/*.yaml` 改（情境 B）。
- **已被其他章累積**（md 內有其他章的 `accumulation:` 標記）：render 有覆寫保護
  （`_would_destroy_data`），不會再碰這個檔——此時 **md 本身就是活文件**：
  - 補累積：走 link_updates（情境 D），不要手貼區塊。
  - 修定義區的錯字／勘誤：直接改 md，commit 訊息註明勘誤依據。
- 改名／移分類資料夾一律 `python util/rename_markdown.py <src> <dst> [--dry-run]`。

## 收尾驗證（每次維護後，量力裁剪但不省核心）

```text
python util/validate_knowledge_base.py
python util/verify_links.py 【書名】
```

另視改動加跑：

- 動了條目名／aliases／新增刪除條目 → `python util/build_link_index.py` 與
  `python util/build_embedding_index.py`（順序不可反），再補
  `python util/check_existing_links.py 【序號 書名】/第x章.md --missing`。
- 動了累積 → `python util/check_accumulation_orphans.py`。
- 大改（等同重做該章）→ 照 `agent_start_prompt.md` 步驟7–8 全套閘門。

閘門吃**書卷名不是路徑**（`verify_links.py 民數記`）；別用 `grep -c` 判斷通過。

## 提交

- 一次維護一 commit，訊息寫清楚改了什麼、依據哪個來源；staging 用明確檔名
  （`.tmp` 的 yaml ＋ 渲染出的 md 一起進），不要整目錄 `git add link_folder`。
- 修改屬勘誤性質時，不默默改：commit 訊息或 relation 註明勘誤依據。
