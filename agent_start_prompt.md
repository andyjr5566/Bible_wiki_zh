# Agent Start Prompt — 新章製作清單

寫作方式必須是要讓一般大眾看得懂；所有輸出用繁體中文。

這份是每章照做的操作清單。規則背後的原因、實例與排錯細節在 `agent_start_reference.md`
（清單裡標 §A–§I 的地方），出錯或拿不定時再查。共通規則（來源、STEP 邊界、寫作要求、
review 預算）以 `AGENTS.md` 為準，這裡不重抄；架構與設計判斷見 `scheme.md`。M3／M6 的寫作格式
以本章 `run_chapter_manual.py prompts` 落地的 prompt 為最終規格。

## 核心規則

1. M3／M6 一律人工手寫 payload，不用任何模型 API 自動生成。
2. 四套 Commentary 各自全文閱讀一次。STEP 全 raw 由 machine validation 驗證，寫作時讀
   projection，需要時用 MCP 精確 query；不猜、不 dump 全 raw、不查網路 STEP。
3. M3、M6、B 類寫完各過一道 reviewer gate（步驟 3），gate 沒過不往下。
4. `.tmp/第x章/` 的 yaml 是 source of truth，不手改渲染出來的 markdown。
5. 閘門全綠只代表結構合法；步驟 6 的內容勘誤每章都要做。

## MCP（可用時）

工具表與用法見 `util/mcp/README.md`。要點：

- M3／M6 經 MCP 也只走人工路：`prepare_manual_payload_prompts` → 手寫 → `check_manual_payloads`
  → `render_manual_chapter`。
- B 類只走 `preview_chapter_link_updates` → token → `apply_chapter_link_updates` → 再 preview
  必須 0 變更。
- `check_chapter_files` 會呼叫 git，在 MCP 下可能卡到 180 秒逾時，照步驟 8 在 shell 執行。
  `link_updates.py evidence`／`debt` 與網站 build 沒有 MCP 對應。
- `run_gates` 只包部分閘門（`timeout_seconds=600..900`，client timeout 600000–900000 ms），
  不取代步驟 7–8。
- `scan_unsourced_tokens` 比對的是全庫 raw_data：報出＝強力刪除線索，沒報出不代表出自本章。

## 每章流程

1. **準備來源**（`【序號 書名】/.tmp/第x章/`）
   - 經文：`raw_scripture/{標準書名}/第{章}.txt`，缺檔即停，回報使用者。
   - 四套註釋：用既有記錄或目錄頁確認 URL（禁止硬猜）；已存在的 raw_data 直接沿用，不加
     `--overwrite`。
     `python util/crawl_bible_text.py "{URL}" --output_path raw_data --output_filename "{source}_{book_slug}_{chapter}"`
   - STEP：`python util/extract_stepbible.py "【書名】 X" --data_path .stepbible_data --output_path raw_data --download`
   - manifest 不可手寫：`python util/build_source_manifest.py 【書名】 X`，缺檔依提示補 crawl／extract。
   - 全文讀四套 Commentary，在 `read_log.md` 各留三段逐字引句（至少一段出自後 1/3），再跑
     `python util/check_source_read.py 【書名】 X`；commentary 回執與 STEP machine receipt 都 PASS
     才動內容。（§A）

2. **建 link_candidates.yaml**（唯一由你判斷「哪些詞值得成為知識節點」的步驟）
   - 格式依 `_config/schemas/link_candidates.schema.json`；只放經文或有效 raw text 明確觸發的候選。
   - 一個候選對一個條目，`name` 不可含斜線；多個詞用 `surfaces`。（§B1）
   - `type` 只能是 `link_folder/` 下的資料夾：主題、事件、互文、人物、原文、地點、文化、歷史、
     神學、背景、解經爭議。祭祀制度歸 `主題`、術語歸 `原文`，器物歸 `主題`／`文化`。（§B1）
   - 經文用詞對不上候選名時宣告 `surfaces`；同詞多義用 `{phrase, verses}` 限定節次。（§B2）
   - 原文類候選的括號音譯、希伯來字母必須在本章來源出現過（先 `grep -i` raw_data），沒有就用
     裸中文名。（§B3）
   - STEP 可觸發原文候選，但只收有研究或跨章累積價值的；Strong 編號不是 wiki ID。
   - 存在性掃描：整章候選名一次丟給 `search_wiki_entries(queries=[...])`，把 `unmatched` 寫進
     `candidate_existence.md`。有 match 的確認是不是同概念，是就改用既有條目名。（§B4）
   - 近鄰報告：`python util/semantic_lookup.py --candidates 【書名】 X`。先讀開頭的「摘要：
     需要判斷的項目」，只細看列出的候選：✅ 確認同概念就改用既有條目名，⚠ 人工判斷，🆕 照建；
     候選互查 ⚠ 考慮合併。（§B5）

3. **手寫 M3／M6，逐段過 reviewer gate**
   ```text
   python util/build_link_index.py
   python util/run_chapter_manual.py prompts 【書名】 X
   ```
   - 讀 M3 prompt 與 STEP projection，手寫 `entry_content/<name>.yaml`（每個條目一個檔）。
   - M3 gate 通過後重跑 `prompts` 取得正式 M6 prompt，手寫 `chapter_content.yaml`，過 M6 gate。
   - 接著 `python util/run_chapter_manual.py check 【書名】 X`，再 `run`。`run` 缺 payload 會直接
     報錯，不會自動產生內容。
   - 本章整理的 wiki-link 只能連本章可連清單（A／B 既有條目＋本章實建 C 條目），清單外的概念用
     純文字。M3 的 alias 撞名由 `check` 報出，自己從 payload 移除。（§C）
   - **Reviewer gate**（M3、M6、B 類各一道）：
     1. `python util/agent_review.py submit 【書名】 X m3`（M6 用 `m6`，B 類用 `link_updates`）。
     2. 請另一個 agent 唯讀審查：預設 Codex（`--sandbox read-only`），不能用時改 Antigravity
        （`agent_antigravity_orchestrator_prompt.md`）。同一章延續同一個 thread（Codex `--resume`、
        agy `--conversation`）。只給書卷、章、stage、目前 sha，請它依
        `agent_evidence_audit_prompt.md` 審查，不另寫審查標準。
     3. 依 reviewer 的 footer 代記：
        `python util/agent_review.py verdict 【書名】 X m3 <pass|changes_required|blocked> --sha <REVIEW_SHA256> --reviewer <codex|antigravity> --findings-count N`
     4. 有 findings 就修 `.tmp` 的 yaml 再 submit。採納前先對 raw_data `grep -F` 核對它引的原文，
        查不到的不採納。
     5. `python util/agent_review.py gate 【書名】 X m3` 通過才往下。
     - 每個 stage 最多兩次審查；第二次仍要改時，修完再 submit 會自動記 FORCED PASS，不開第三次。
     - 已過關的 stage 只因上游修改而 hash 變動（例如 M6 過後又改了 M3）時，submit 會標成差異複核：
       請 reviewer 只確認上游修改有沒有波及本 stage，這次不耗額度。
     - Codex 與 Antigravity 都不能用時，改記
       `python util/agent_review.py skip 【書名】 X m3 --reason "無可用 reviewer"`，gate 會以
       SKIPPED 放行。commit 訊息要註明，日後用 `python util/agent_review.py summary` 找出來補審。
     - 寫作者不審自己的稿、不自己記 PASS；不得為了過關改 `util/agent_review.py` 或任何 gate 腳本
       （每輪審查後 `git status util/`）。

4. **B 類累積**（既有條目補本章資料）
   ```text
   python util/link_updates.py prepare 【書名】 X
   ```
   - 先讀 `review_evidence.md`；判斷不是單純 keep，或要引逐字內容時，才開條目原檔。
   - `summary`／`relation` 只記本章明確事實與本章關聯。
   - `overview_review` 的 `definition`、`development` 各選 `keep` 或 `update`。keep 是正常結果；
     只有明確的新定義或跨章發展才 update，不為了顯得有做事而硬湊。
   - preview 提出 challenge 而仍選 keep 時才填 `basis`；`already_covered` 要附 `covered_by`
     逐字節錄；條目欠帳而本章只一句帶過時填 `standing_debt`。（§D）
   - `development=update` 要在 `synthesis_scope` 列本章與至少另一章，並先改條目的
     `## 主題發展`；不可把本章 summary／relation 換句話說貼進定義或主題發展。
   - 過 `link_updates` gate 後才 apply，重跑 apply 必須 0 變更：
     ```text
     python util/link_updates.py apply 【書名】 X --dry-run
     python util/link_updates.py apply 【書名】 X
     ```

5. **人工決策點**：處理 `manual_review` 項目與 `link_plan.yaml` 的 D 類（同名、分類衝突）。D 類
   不得自動建立或連結；判斷後修 candidates 或人工建檔再續跑。C／D 候選附有 `semantic_hint` 時，
   確認是不是該改走 B 類累積。

5b. **短引句裁決**
   ```text
   python util/check_quote_fidelity.py 【書名】 X
   python util/check_quote_fidelity.py 【書名】 X --min-chars 2
   ```
   第二行必跑，每一條未命中都要裁決並寫進 `quote_adjudication.md`（缺這份會被
   `check_chapter_files` 擋）。字串沒命中不等於內容錯，不要為了讓比對通過而改寫內容。（§E）
   ```markdown
   # 第X章 短引句裁決（--min-chars 2）

   本輪共 N 處未命中，逐條裁決：
   - [CT] 「⋯⋯」→ 逐字命中（工具因標點差異誤報）
   - [KC] 「⋯⋯」→ 已改為具名轉述，去「」
   - [經文] 「⋯⋯」→ 已補全截斷、與 raw_scripture 一致
   - [BH] 「⋯⋯」→ 英文原句移入「」、中譯移到（）
   - [—] 「⋯⋯」→ 確為強調用法（非逐字宣告），保留
   ```

6. **內容勘誤（commit 前必做）**：把新寫的本章整理、新建條目、B 類累積逐條對回 manifest 正式來源，
   優先查四類：來源誤植、全稱詞／方向性誤讀、rawdata 沒出現過的經文交叉引註、查無出處的格言式
   總結句。（實例與 grep 查法 §F）
   - 解經爭議類條目只陳述四套註釋實際記載的立場，不可自編解經史。
   - knowledge_nodes 一項只放一個條目名，不要用頓號把兩個條目名黏成一項。
   - 發現錯誤就改 `.tmp` 的 yaml，再 `check` → `run`；B 類改 `link_updates.yaml` 後重跑 apply；
     改了 `link_candidates.yaml` 要重跑 `prompts`。
   - 本章累積到的既有條目若帶著舊錯，一併修正，勘誤依據寫在 relation 或 commit 訊息。

7. **收尾驗證**
   ```text
   python util/build_appendix_links.py
   python util/check_existing_links.py 【序號 書名】/第x章.md --missing
   python util/build_link_index.py
   python util/build_embedding_index.py
   python util/validate_knowledge_base.py
   python util/link_quality_check.py 【書名】
   python util/verify_links.py 【書名】
   python util/audit_knowledge_base.py --check-due
   ```
   - `build_embedding_index.py` 一定要在 `build_link_index.py` 之後跑，不可略過。
   - 閘門吃書卷名，不是路徑（`check_existing_links.py` 例外，要章節 md 路徑）。看 PASS／FAIL 與
     exit code，不要用 grep 計數判斷通過。
   - 有改 `appendix/website/**` 時另見 §G。

8. **檔案完整性驗證**
   ```text
   python util/check_chapter_files.py 【書名】 X
   ```
   - 缺檔時照它印的指令回到那一步，依序做完再重跑，直到全數 PASS。（§H）
   - 它列為「本章待 git add」的 `link_folder/**.md` 要一併 staging，staging 後用 `git status` 對照。

9. **全局 review 與 commit**
   - commit 前請 Antigravity 做一次唯讀全局 review：重大遺漏、內容失衡、M3／M6 或跨章條目不一致；
     wording 偏好不改。有實質問題就修 yaml、重跑受影響的驗證。
   - Antigravity 不能用時跳過，commit 訊息註明「全局 review：略過（無 reviewer）」。
   - 全部 PASS 後 commit + push，一章一個 commit。回報只列結論數字與需要人工決定的項目，不貼完整報告。

## 行為邊界

- 一切內容對得回經文或有效 raw text；來源未提的不寫，不憑神學常識外推。
- 來源 attribution 必須忠實，翻譯與轉述保留原意；格式本身不作內容真假的判準。
- 不假裝無效來源有效；不為湊條目亂搜薄弱資料。
- 改名一律 `python util/rename_markdown.py <src> <dst> [--dry-run]`（會同步全庫 WikiLink）。
- 已完成且驗證通過的章節不重做；維護見 `agent_maintenance_prompt.md`。新建條目的規則見 §I。
