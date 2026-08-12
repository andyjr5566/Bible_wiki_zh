# Agent Maintenance Prompt（維護既有章節與 link_folder 條目）

新章製作照 `agent_start_prompt.md` 走。本檔管的是**維護**：章節做完之後，回頭修改
`.tmp/第x章/` 的內容（M3 條目、M6 本章整理、候選、B 類累積），要怎麼把修改正確地
落到渲染後的 `第x章.md` 與 `link_folder/**.md`。

## 你的角色：最後內容把關者

你維護的章節是**其他 agent 先產出的**。你的任務是**勘誤與補充，不是重跑流程**——
舊版對的部分保留、錯的才改，不為改而改。三件工作內容，每章都做：

### 1. 擴充 link_candidates（依 rawdata）

rawdata 裡值得跨章累積、卻沒候選的概念 → 新增候選並補齊 payload 必填欄
（accumulations、sources）。經文裡的關鍵詞沒連結 → 補 surface。常見坑：

- **斜線候選名**建不出 `entry_content/<name>.yaml`，整鏈靜默失效。
- **surface 衝突**（兩候選搶同詞）要判 ambiguous；原文候選拿經文本義詞、主題候選拿詮釋詞。
- **STEP 只觸發有研究／跨章累積／實質內容價值的原文候選**；不可替每個功能詞、詞形或
  Strong 編號批量建頁，Strong 編號不是 wiki ID。
- **type 必須對得上既有資料夾**（動手前先 Glob 確認）；對不上會 fork 重複條目。
- 和合本女性主詞用「他」不用「她」——surface 寫「她」會對不上經文（「未連上任何節」先查這個）。

### 2. 勘誤所有 link 與條目內容

拿舊版每個事實性斷言去 rawdata 對，高風險四類優先查：**數字、全稱詞、來源誤植、
對照類敘述**。要抓的錯型：杜撰引述（掛在某家名下但該家沒說）、被來源明確反駁的說法、
被壓扁的爭議（還原成點名可查的各家並陳）、整段經文缺漏、異章污染（候選從別章照抄）。

- 改候選名／type 後**務必回頭同步 `chapter_content.yaml` 裡的手寫連結**：resolver 認裸名、
  Obsidian 不認——這是「兩閘門全過卻斷鏈」的老坑。改條目名走 `rename_markdown.py`（見情境 B）。
- 找不到出處 → 刪；講反／講過頭 → 改正並在 commit 訊息或 relation 註明勘誤依據，不默默改。

**「勘誤所有 link」包含逐個條目的 md 本體，不只本章整理**——這是最常被跳過的一步：

- 逐個打開本章每個相關條目（`link_folder/**/*.md`），讀 **定義／按書卷累積（本章那筆
  summary＋relation）／來源依據**，對回 rawdata。章整理裡抓到的錯，同型幾乎一定也潛伏在
  條目裡（創1 實例：「把復造說整片掛給 CT/GT」在 organization 與 4 個條目都有；
  「神說出現 8 次」的數字錯在條目）。修完章整理，回頭用同一批判準掃過所有條目。
- **結構完整性 ≠ 內容正確**：`check_existing_links --missing` 零流失、type 對得上資料夾、
  surface 連得上節、候選全 `A_use_directly`——這些**只驗結構**，全過也不代表定義／累積的
  文字沒有杜撰、誤植、壓平、數字錯。內容勘誤要另外逐條讀 md 對 rawdata，不能靠閘門代勞。
- 改法：本章 only、未被他章累積的條目 → 情境 E 直接改 md（render 不重生 A 類條目，
  編輯持久）；已被他章累積 → 定義勘誤直接改 md、累積 summary／relation 走 link_updates。
- 收尾**機械複掃**：改完用 grep 掃全庫同型字串（例：被壓平的來源名 `CT/GT`）確認本卷本章
  清零，但要排除別卷別章的合法用法（來源依據列雙檔、兩家都確實這麼說）。
- **development 落後累積成長**：條目的 `definition`／`development`／`related_entries`／`sources`
  只在條目首建那章寫定，之後每章只靠 `link_updates.py` 補「按書卷累積」的逐章區塊，
  不會回頭碰這四欄——累積量隨後續章節持續成長，development 卻可能停在條目剛建立時的舊
  範圍（2026-08 實測：「摩西」累積 49 筆橫跨三卷，development 卻只寫出埃及記第2章）。
  凡是本章要累積進去的既有條目，若累積筆數明顯偏多（`python util/check_development_staleness.py
  <書卷>` 列出候選），要打開來看 development 是不是只覆蓋首建那卷／那章——是的話就依現有
  累積表（已審過、有出處）重新綜整，不是重新套用自動生成；development 只收「跨書卷／跨章的主題
  遞進」，同一段經文內的字義辯論屬於 definition，不要塞錯欄位。`link_updates.py apply` 套用
  時累積跨過門檻會自動印提醒，別忽略。

**別只維護既有候選——要問「rawdata 有沒有值得跨章累積、卻沒有條目的概念」**：勘誤既有的
同時，把 candidate/entry 覆蓋率對 rawdata 重新推導一遍（B/C/D 為空≠已完備，只代表沒人動過）。
高來源密度卻沒有節點的主題（創1 實例：舊約背景註釋整章鋪陳「與古代近東創世神話的對比」
——非爭戰創造、宇宙功用觀、人為受造中心非眾神奴隸、天體去神化——卻無對應條目）就補建
（見工作內容 1 與情境 C 的新增候選＋payload）。

### 3. 從rawdata勘誤並補充本章整理的內容（M6）與條目（M3）的內容與格式

**寫任何內容前，先讀對應的生產 prompt 當規格書**（勘誤補寫的內容必須同樣合格）：

- **M6 本章整理**：以 `util/run_chapter_manual.py prompts` 落地的 chapter_content prompt
  （`你是聖經研經資料整理員…chapter_content payload`）為規格。
- **M3 條目內容**：以同一批 prompts 落地的 entry payload 規格為準。

兩份 prompt 的硬規格摘要（細節以 prompt 為準）：

- **結構**：`### 標題（vX-Y）` 小節數達下限；**散文敘述是主幹（≥ 總字數一半）**，
  表格／callout 只是補充，不可反客為主。
- **內容**：直接引原話「」並標對哪一家（CT／GT／KC／BH 或 GT 內各家），不張冠李戴、
  某家沒說就別替他生一個；矛盾並陳不壓平；英文來源譯成繁中不貼原文；只出自經文與來源。
- **STEP 邊界**：STEP 是原文證據層，不是第五套 commentary；可支持詞形、lemma、Strong、
  morphology、context gloss 與 lexicon 義域，但不算 commentary 共識票。Lexicon 是可能義域，
  不等於本節必然語境義；morphology 也不自行推出神學結論。語言事實與註釋解讀分開寫。
- **圖表優先**：材料是流程／路線／對照／階層／關係／時間軸的形狀 → 對應 mermaid／表格；
  但圖表不折抵散文份量（字數與小節下限先由散文滿足）。
- **格式硬規**：`organization` 用 YAML `|` 字面區塊；mermaid 節點 `A["標籤"]`、圖內不放
  `[[ ]]`；表格內不放帶別名連結（`\|` 斷鏈）；`knowledge_nodes` 寫裸名或 `名稱|小標題`、
  **不自己包 `[[ ]]`**（雙重括號 bug）；wiki-link 白名單＝本章 A/B/C 條目，清單外用純文字；
  禁 `![[]]`／HTML／`#標籤`／參考資料清單。
- **正文不得出現流程註記**：內容是給讀者看的研經材料，不是維護日誌。禁止寫「舊版整段漏掉」
  「舊版把它壓平了」「本次維護補上」「應並陳」這類談論**版本或編輯過程**的句子——勘誤依據
  寫在 commit 訊息或 relation，不寫進 organization／定義／主題發展。要講分歧就直接讓各家並陳
  （「五份來源在這一點上四比一分歧」可以，「舊版未收，應並陳」不行）。
  機械複掃：`grep -rn "舊版\|本次維護\|先前版本" --include=*.md . | grep -v .tmp/`
  應只剩流程文件本身（2026-07-27 實測全庫 10 處污染，創1 與出26-30、33）。
- **M3 額外**：type 是分類不是詞性；音譯與希伯來字母必須在來源實際出現過（護欄會逐字驗、
  查無出處退回）；互文條目 name 用「標題（經文）」；accumulations 是物件陣列含
  book／chapter／summary／relation，至少含本章一筆。

改完之後照下面「對照表」跑對應指令落地。**流程加固**：同一個錯出現第二次才做成護欄
（機械可證→error、啟發式→manual_review），且加護欄前先懂流程、要全庫實測 0 誤報。

## 先設立 Todo list

**todo 拆到每章三項**（候選擴充／條目勘誤／M6+M3）
內容： 
第X章：讀agent_maintenance_prompt.md 並相關文件, 擴充 link_candidates（依 rawdata）, 勘誤所有 link 與條目內容, 從rawdata勘誤並補充本章整理的內容（M6）與條目（M3）的內容與格式
不要出現這樣的todo list: 第XX-YY章，只能單一章

## 三條前提原則

1. **Source of truth 是 `.tmp/第x章/` 的 yaml，不是渲染出來的 markdown。**
   只改 `第x章.md` 或 `link_folder/**.md` 而不改 yaml，下次重跑 render 就被覆蓋回舊內容
   （申4 鐵爐實測）。唯一例外見下方「既有條目 md 的地位」。
2. **人工重跑**：重跑一律用 `util/run_chapter_manual.py`（`check` → `run`）。它沿用
   原版 orchestrator 的結構護欄與作廢預警；缺少人工 payload 時直接報錯。`link_updates.py`
   照原版用。
3. **內容鐵律不因維護而放鬆**：修改後的文字仍必須能對回經文與本章 manifest 的所有 OK 正式來源
   （`.tmp/第x章/manual/sources.md` 或 `source_manifest.md` 列的 raw_data 檔）；
   新增的引句、經文引註、音譯都要先 grep raw_data 確認出處。

## MCP 輔助（可用時；M3／M6 固定人工內容）

連上 `Hermes-Scripture-MCP` 時，先用 `get_chapter_status` 看管線缺口；用
`read_chapter_artifact` 讀白名單內的 `.tmp` payload／prompt、用 `read_chapter_source`
讀本章經文或 manifest 宣告為 OK 的來源、用 `search_wiki_entries`／`read_wiki_entry` 核對
既有條目與 alias。這些工具有路徑白名單，不能用來讀任意檔案。

本檔引用的 `util/*.py` 也都有 MCP 對應：`extract_stepbible`、`build_source_manifest`、`build_candidate_similarity`、
`sync_link_index`、`sync_embedding_index`、`build_appendix_links`、
`check_existing_links`、`validate_knowledge_base`、`check_link_quality`、`verify_links`、
`audit_knowledge_base`、`check_chapter_files`、`prepare_chapter_link_updates` 與
`rename_markdown`。`check_accumulation_orphans.py`（反向孤兒累積）與
`check_development_staleness.py`（development 落後累積成長候選清單，見上方「勘誤所有
link 與條目內容」一節）目前無 MCP 對應，直接用 Bash 跑。`run_chapter` 這個 MCP 名稱固定走
`run_chapter_manual.py run` 的人工流程；需要寫入的工具仍依 MCP 回傳的確認要求執行。

大型 corpus 呼叫 `run_gates` 時，傳 `timeout_seconds=600..900`，並把 MCP client 的整體
tool-call timeout 設為 `600000–900000` ms；這是 server 內部 timeout 之外的另一層設定。

維護 M3／M6 時，MCP 路徑和本檔的人工模式相同：手寫 yaml 後呼叫
`check_manual_payloads`（唯讀，不會改寫 alias）→ `render_manual_chapter`；改
`entry_content` 且 chapter_content 已同步時才設 `keep_chapter=true`。候選變動前先呼叫
`prepare_manual_payload_prompts(confirm_stale=false)` 看作廢清單，確認後才設為 true。
這些工具實際只會使用 `util/run_chapter_manual.py` 的人工流程。

B 類累積保持既有紀律：`preview_chapter_link_updates` → 人工核對 summary／relation 與
來源 → 將 token 傳給 `apply_chapter_link_updates` → 再 preview 必須 0 變更。MCP 不得用來
跳過本檔要求的逐條內容勘誤、索引同步或收尾驗證。

render 後可用 `scan_unsourced_tokens` 補掃舊 A 類條目從未被 payload 護欄覆蓋的希伯來字母、
拉丁音譯與簡體字。它掃的是**全庫** raw_data：報出是強力刪除線索；未報出不代表該詞來自
本章或該條目實際累積來源，仍要以 manifest／累積章節核對。`run_gates` 只執行部分核心
機械閘門，且 `verify_links` 會更新驗證報告；它不取代本檔的完整收尾驗證。

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
  （原版行為是作廢 verse_links＋chapter_content；人工流程中這代表刪掉你手寫的本章整理）。
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

**新增一個全新條目（rawdata 有值得累積、卻沒節點的概念）——完整流程與兩個坑：**

1. `link_candidates.yaml` 加候選（`name`／`type`／`evidence`）。**主題節點可不給 surface**
   （像「六日復造的結構」「三位一體…」），只在 knowledge_nodes 與 organization 連結、不動
   verse_links——這是最低風險做法；要連經文特定詞才給 surface。
2. `prompts 【書名】 X --confirm-stale` → resolve 把新候選分類為 `C_new_formal`。
3. 手寫 `entry_content/<name>.yaml`（欄位照 `_ENTRY_EXAMPLE`：name／type／status／definition／
   development／accumulations〔含本章一筆〕／related_entries〔限本章條目〕／sources；
   原文類 name 用「中文（音譯）」且音譯要在來源出現過）。**不必再重跑 prompts**——白名單
   驗證（`_reconstruct_allowed_links`）直接讀 `entry_content/*.yaml`，payload 在就認得。
4. 重寫 `chapter_content.yaml`：加 knowledge_node（歸對分組）＋在 organization 首次提及處
   加 `[[新條目名|行文詞]]`。
5. **坑一（會刪掉你剛寫的 payload）**：若該章之前 `run` 過，`pipeline_state.json` 存的是
   舊 baseline；`run` 開頭的 `_invalidate_stale` 會判 link_candidates 變了 → 連鎖刪除
   link_plan／entry_content／chapter_content。**對策：`run` 前先刪 `pipeline_state.json`**
   （它只是作廢比對基線，`run` 結尾會重建）——刪掉後「無基線＝視為乾淨」，run 直接用磁碟
   現有產物 render，不會毀掉手寫 payload。先 `check`（唯讀、安全）確認 payload 合格，再刪
   state、`run`。
6. **坑二（新增條目後索引沒跟上）**：`run` 完務必依序
   `python util/build_link_index.py` → `python util/build_embedding_index.py`（見收尾驗證；
   embedding 需 local-4000 proxy 的 `/v1/embeddings`，會靜默失效，跑完看有無「已嵌入 N/N」）。
7. 閘門：`check_existing_links --missing`（條目數應+新增數）、`validate_knowledge_base`、
   `verify_links 【書名】`。

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
`check_accumulation_orphans.py` 要帶書卷名（或 `--all`）；`check_existing_links.py` 帶
`第x章.md` 路徑＋`--missing`（回報「N 個既有條目都有本章資料」＝零流失）。

## 實戰要點（開場先讀，少走冤枉路）

這節是把已踩過的坑落成 checklist。逐章維護的實際順序建議：**四套 OK commentary 全讀＋STEP machine gate → 機械掃描（下 A）
→ 逐條目讀＋高風險四類勘誤 → 覆蓋率重推（下 B）→ 驗 M6 → 閘門 → 分兩 commit（勘誤／覆蓋）**。

### A0. 開工第一件事：commentary 全讀＋STEP machine gate（沒過不准動任何檔）

**歷史事故（當時仍是四來源且尚未加閘門）：**「四來源全讀」曾是規格裡唯一沒有閘門的硬規格，所以最先縮水。2026-08-03 實測：
創48 的 BH、創49 的 KC 與 BH、創50 的 GT 後半／KC／BH 只做了關鍵字 grep 就往下寫，
漏掉整批材料（KC 創49 把中間六支派讀成一條連續的末世預言線、GT 創50 丁良才的約瑟預表
基督對照表、BH 創48 的猶太祝福傳統），而四道閘門每章全綠。

因此加了機械閘門，**順序不可調換**：

1. 讀完 `source_manifest.md` 中四套 OK prose commentary 的**原檔全文**（不是 prompt 摘要、不是 grep）。
2. 寫 `.tmp/第x章/read_log.md`：每個 commentary 登記行數與**三段逐字引句**，其中**至少一段必須出自該檔後三分之一**。STEP 不做人工逐詞引句；完整 raw 檔由 formal parser machine-validate，receipt 寫 `step_source_receipt.json`。
3. `python util/check_source_read.py 【書名】 X` 要同時回報 commentary receipt 與 STEP machine validation PASS。它已掛進
   `run_chapter_manual.py` 的 `check`——沒過就擋下，render 跑不了。
4. **回執通過以前，不要動任何 yaml／md。** 邊讀邊寫就是抄近路發生的縫隙。

只 grep 幾個關鍵字湊不出 commentary 後段引句，這正是本閘門要擋的東西。引句要逐字抄（實測即抓到兩處「差不多但不精確」的轉錄）。STEP 改驗證方式而非免驗；寫作時讀 task-aware projection，細查用 `step_context.py`／MCP `query_step_context`。

### A. 每章開場的機械掃描——查無出處的希伯來字母／音譯（work item 2 最有效的第一刀）

**護欄（`_unsourced_hebrew_errors`）只掃 `.tmp` 的 payload，從不掃已渲染的 `link_folder/**.md`。**
舊版→新版遷移的舊條目被判 A 類原樣保留、沒有 entry_content、護欄一次都沒驗過——遷移前塞的
希伯來字母全數潛伏至今。創2 實測：39 條目中 **14 條**定義帶希伯來字母（安息 שבת／亞當 אדם／
五條地名等），去 niqqud 後比對**整個 raw_data 語料**確認一個都不在任何來源（拼寫多正確，仍照
鐵律拔除）。

- 掃法：Python 抽 `[֐-׿]+`、去 niqqud（U+0591–U+05C7）後在整個 `raw_data/*.txt`
  子字串比對；查無出處＝拔希伯來字母，**保留來源實際出現的拉丁音譯**（KC/BH/GT 給的
  Pishon/Havilah/shabbat/bara/nephesh/ezer/kenegdo… 要留；查無出處的 avad/shamar/qadesh/
  tov va-ra/perat 連拉丁一起拔、改用來源給的中文字義）。
- 拉丁音譯要用**詞界** grep：`grep -oiE "\b(token)\b" raw_data/*.txt`——子字串比對會把 `perat`
  誤配 cooperation/temperate 而假放行。音譯可能出處在別章（Chavah 在 BH 創3、qadesh 只在
  出12），要對「該條目實際累積的章」判斷，不是只看本章。
- **坑：`grep -oP '[\x{0590}-\x{05FF}]'` 在本環境 Git Bash 回傳假 0，一定要用 Python 掃**。
  可複用腳本在 scratchpad：`heb_scan.py`（列哪些條目有希伯來）／`heb_source_check.py`（每條
  Hebrew 對全語料查出處＋列該條目累積哪些章）／`translit_scan.py`（抽 `*斜體*` 拉丁音譯查語料）。

### B. 覆蓋率重推——把「高來源密度卻沒節點」的主題補成既有條目的新章累積（B 類）

情境 C 講的是「新增全新條目」；更常見的是**既有條目要吃本章的新累積**（例：ch1 建的
「與古代近東創世神話的對比」，ch2 的《舊約背景註釋》又有造人／安息／生命樹的近東對比高密度
材料）。既有條目＋新章累積，resolve 會判 **B_needs_update**（不是 A）；M6 白名單含 A＋B，可在
本章整理連結。完整命令序列與兩個坑：

1. `link_candidates.yaml` 加候選（`name`／`type`／`evidence`；主題／背景節點**不給 surface**，
   風險最低）。
2. **坑一：`resolve_step` 若 `link_plan.yaml` 已存在就直接回傳、不重算**（見
   `util/run_chapter_manual.py` 所使用的 resolver 實作）
   ——只刪 `pipeline_state.json` 不夠，新候選不會進 plan。要**同時刪 `link_plan.yaml`**。
3. **坑二：保住手寫的 M6**——`_invalidate_stale` 見 link_candidates 變了會連鎖刪
   chapter_content。對策同情境 C 步驟5：**先刪 `pipeline_state.json`（無基線＝視為乾淨、不作廢）**，
   再刪 `link_plan.yaml`，再 `prompts`。prompts 會重生 link_plan（新候選落 B_needs_update）、
   但因無基線不動 chapter_content。動前先確認 `.tmp` 已 commit（那就是備份）。
4. 改 `chapter_content.yaml`：加 knowledge_node（歸對分組）＋在 organization 首次提及處加
   `[[條目名｜行文詞]]`（連結目標要在 A/B 白名單內，check 會驗）。
5. 改 `link_updates.yaml`：加該條目一筆 `title/path/summary/relation`（summary/relation 逐句
   對回 manifest 正式來源；若陳述 commentary 共識，只計 CT／GT／KC／BH，不計 STEP）。
6. `check` → `run`（render 出 `第x章.md`）→ `python util/link_updates.py apply 【書名】 x --dry-run`
   確認**只動這一個新條目檔**（其餘冪等）→ 去 `--dry-run` 實跑 → 再 apply 一次必須 0 變更。
7. 閘門：`check_existing_links 第x章.md --missing`（條目數應 +1）、`validate_knowledge_base`、
   `verify_links 【書名】`、`check_accumulation_orphans 【書名】`。
8. **正常現象**：`run` 會把手寫的 organization `|` 字面區塊 re-dump 成單引號折行式——渲染輸出
   相同、內容不變，不用回改。

### C. 重跑 render 前先驗「chapter_content 節點 vs 已渲染 md 節點」是否失步（遷移遺留 bug）

`render_knowledge_nodes` **只讀 chapter_content.yaml 的 knowledge_nodes**，不做累積反查。遷移遺留
的坑：不少章的 `第x章.md` 節點清單比 yaml 多出幾個節點——這些節點是「已被本章累積（entry 有
`accumulation:書卷:x`）、且已在 md 連回」的合法條目，但 yaml 漏列。**現況閘門會過**（md 有回連），
可是**一旦為別的原因重跑 render，這些節點會連同 md 回連一起被刪 → 立刻變成等量的累積孤兒**（創3
實測 4 個：彌賽亞／亞當作舊造元首／耶和華神的名字／神的命令與自由意志）。

- 重跑 render 前先比對：`grep '^- \[\[' 第x章.md`（本章知識節點區）與 chapter_content.yaml 的
  knowledge_nodes；md 有、yaml 無的，逐一確認該 entry 是否真有本章累積（合法）——是就**補進
  yaml 對應分組**（位置對回 md）再 render，別讓它們掉。
- 這些節點常「有累積、卻不在 link_candidates／link_updates」（累積是更早的流程或手寫留下的）；
  補進 knowledge_nodes 即可（節點清單不吃白名單，不必硬做成候選），link_updates.py apply 不會動
  它們（apply 只碰 link_updates.yaml 內的條目）。
- **注意**：補進 knowledge_nodes ≠ 可以在 organization 連 `[[ ]]`。節點清單不吃白名單，
  organization 吃。這類節點在散文裡要用純文字（創12 實測：補了 7 個節點，其中 4 個一寫成
  `[[ ]]` 就被 check 擋）。
- **規模是可以量出來的，別憑印象**：創世記全卷掃描（2026-07-27）13-50章有 **28 章失步、
  共漏列 105 個節點**，最嚴重的創14 漏 15 個（麥基洗德的豫表、什一奉獻的起源、耶路撒冷、
  死海……）、創17 漏 8、創34 漏 8。已一次補平並 commit。**新書卷開工時先跑一次全卷掃描**，
  比逐章才發現省事得多。scratchpad 兩支可複用腳本：`node_desync.py <書卷資料夾> [起] [迄]`
  只報告；`sync_nodes.py <書卷資料夾> <起> <迄> [--apply]` 依 md 現況把節點與分組寫回 yaml
  （只改 knowledge_nodes 區塊，organization 的折行風格不動；先 dry-run 看有沒有
  「yaml 有而 md 無」的反向差異，有的話要手動判斷再決定）。
- **失步有第二種型態，上面的掃描抓不到**：部分章在「本章知識節點」段落的 `---` 分隔線
  **之後**還掛著落單的 `### 群組`（創16 的 `### 互文 / - [[羅馬書九章]]` 即是）。
  `node_desync.py`／`sync_nodes.py` 都只讀到第一個 `---` 為止，**掃描結果會顯示乾淨**，
  一旦重跑 render 這些節點就永久消失，而且要等 `check_accumulation_orphans` 才會被抓到
  （創16 實測：render 後才報「羅馬書九章宣告創16累積、卻沒有連回」）。
  全卷掃描（2026-07-27）：創世記另有 **10 章、23 個節點**藏在分隔線之後
  （創23／24／28／29／30／37／40／42／43／49），已一次補平。
  scratchpad `sync_stray.py <書卷資料夾> [--apply]` 專掃這一型：讀 `---` 到 `## 本章整理`
  之間的殘留群組，併回 yaml 對應分組（分組不存在就新建）。**每個書卷開工時兩支都要跑。**

### D. 舊章的 chapter_content.yaml 可能藏著「check 會擋」的白名單外連結

遷移／舊版產出的章從沒跑過現行 `check`。創9 實測：organization 裡有
`[[洪水範圍的爭論|第7章洪水地理範圍]]`，該條目不在本章 A/B/C 白名單 →
一跑 `check` 就 FAIL。**修法不是直接刪連結**：先看該條目有沒有本章累積
（`grep 'accumulation:書卷:x:start' <該條目.md>`）——

- **有累積**（創9 就是）→ 把它補進 `knowledge_nodes` 的對應分組。節點清單不吃
  白名單，補進去 md 就會連回，`check` 過、`check_accumulation_orphans` 也過。
  只把散文連結改成純文字而不補節點，會立刻多一個孤兒累積（實測 0→1→0）。
- **沒累積** → 才是真的斷鏈／跨章連結，改純文字。

順序上這是 A（機械掃描）之後、`run` 之前就該做的一步：**每章第一次 `check`
必然會把這類舊帳一次吐出來，不要以為是自己剛改壞的**。

### E. GT 掛名護欄的兩種假報，先判型再動手

`_gt_subsource_review` 與 `_quote_attribution_review` 都可能誤報，動筆改掛名前先
`grep` raw 確認正主（見 memory `gt-subsource-guard-dash-codepoints`）：

- `_QUOTE_ATTR_RE` 抓的是標籤後 **25 字內的第一個「」**。若行文在真引句之前先引了
  一段經文、或前一句剛提過別家標籤，護欄會抓錯配對。對策是讓「GT《X》」後緊接的
  第一個「」就是該家的引句，或把前一個標籤推到 25 字之外。
- `_GT_MARKER_RE` 的破折號字元類原本漏 U+2015／U+2014（2026-07-27 已修）；若日後
  又見「掛名正確卻被判誤植」，先查 raw 段末標記用的是哪個碼位。

### F. 範圍縮水是本流程最大的失效模式——它會靜靜地發生（2026-07-27 實測 36 章）

創世記維護實跑中，第 9–12、16–47 章**連續 36 章只做了工作內容 3 的 M6 那一半**，
工作內容 1（擴充候選）與 2（逐條目 md 勘誤）零執行，而四道閘門每章全綠、commit
訊息每章漂亮。成因與對策都要記住，因為這是流程層的錯，換一卷會原樣復發：

- **閘門會發亮，工作內容 1、2 不會。** 閘門只驗結構，卻是每章唯一明確的「完成」訊號，
  於是注意力自動流向它。→ **閘門全綠不是完工判準，只是可以開始檢查內容的前提。**
- **可 grep 的排擠必須通讀的。** M6 補充可塌縮成 `grep 舊約背景註釋` 一道指令，
  條目勘誤沒有這種入口。→ 每章**先做工作內容 2（逐個開 `link_folder/**.md`）再做 M6**，
  順序反過來就會做不完。
- **零改動必須主動聲明。** 一章的 commit 若 `link_folder/` 改動數為 0，
  訊息或回報要明寫「本章 N 個條目全部讀過、無錯可改」。
  **沒有這句話＝沒做**，把沉默從預設合格改成預設不合格——這是工作內容 2 唯一會留下的痕跡。
- **不要批次多章一 commit。** 每章成本下降通常不是熟練，是做的事變少了；
  批次化是徵兆不是效率。
- **每章開頭重讀本檔的三件工作**，不要拿上一章當模板。連續自主作業沒有外部校正，
  以前一輪為基準的漂移只會單調變小、不會自己回彈。

## 提交

- 一次維護一 commit，訊息寫清楚改了什麼、依據哪個來源；staging 用明確檔名
  （`.tmp` 的 yaml ＋ 渲染出的 md 一起進），不要整目錄 `git add link_folder`。
- 修改屬勘誤性質時，不默默改：commit 訊息或 relation 註明勘誤依據。
- 訊息要能讓人看出**三件工作各自的狀態**，不能只寫做過的那件（見實戰要點 F）。
