## vexp <!-- vexp v1.3.11 -->

**MANDATORY: use `run_pipeline` — do NOT grep or glob the codebase.**
vexp returns pre-indexed, graph-ranked context in a single call.

### Workflow
1. `run_pipeline` with your task description — ALWAYS FIRST (replaces all other tools)
2. Make targeted changes based on the context returned
3. `run_pipeline` again only if you need more context

### Available MCP tools
- `run_pipeline` — **PRIMARY TOOL**. Runs capsule + impact + memory in 1 call.
  Auto-detects intent. Includes file content. Example: `run_pipeline({ "task": "fix auth bug" })`
- `get_context_capsule` — lightweight, for simple questions only
- `get_impact_graph` — impact analysis of a specific symbol
- `search_logic_flow` — execution paths between functions
- `get_skeleton` — compact file structure
- `index_status` — indexing status
- `get_session_context` — recall observations from sessions
- `search_memory` — cross-session search
- `save_observation` — persist insights (prefer run_pipeline's observation param)

### Agentic search
- Do NOT use built-in file search, grep, or codebase indexing — always call `run_pipeline` first
- If you spawn sub-agents or background tasks, pass them the context from `run_pipeline`
  rather than letting them search the codebase independently

### Smart Features
Intent auto-detection, hybrid ranking, session memory, auto-expanding budget.

### Multi-Repo
`run_pipeline` auto-queries all indexed repos. Use `repos: ["alias"]` to scope. Run `index_status` to see aliases.
<!-- /vexp -->

# Hermes Scripture — 共享 Agent 憲法

本檔是 Claude Code、Codex CLI、Antigravity CLI 共用的專案核心規則與流程索引。
上方 vexp 區塊管程式碼導航；本區塊以下管**這個聖經知識庫本身的內容紀律**。
完整 SOP 不複製進來——各節末尾指到權威文件。
## 規則權威範圍

- `AGENTS.md`：跨任務共同遵守的 evidence、source、licensing、validation 與 production invariants。
- `agent_start_prompt.md`：新章 production 的具體 workflow。
- `agent_maintenance_prompt.md`：已完成章節勘誤／補充的具體 workflow。
- `scheme.md`：架構、來源與設計決策。
- 當次 `util/run_chapter_manual.py prompts`：只對該次 M3／M6 的 payload schema、欄位要求、輸入範圍與寫作格式具有最高權威。
- 若權威文件之間出現真正衝突，不自行選擇其中一方覆蓋其他規則；標記 `unresolved` 並交人工裁決。

## 專案定位

- `scripture/` 是繁體中文聖經研經知識庫：書卷資料夾負責逐章順讀（每章唯一主檔 `【序號 書名】/第x章.md`），`link_folder/` 全域共用、負責跨章累積的知識條目。
- Production 章節主檔與由 payload 管理的內容，原則上由 render 程式從
  `.tmp/第x章/*.yaml` 生成，不直接手改渲染結果。
- `link_folder/` 既有條目的維護方式依 `agent_maintenance_prompt.md`：
  可直接修正其允許直接維護的欄位；跨章 accumulation 則走
  preview → token → apply 流程。
- 不得繞過正式 workflow 直接修改由 renderer / accumulator 管理的結構。
- 資料層（人／agent 手寫，每種有 JSON Schema：`_config/schemas/*.json`）與呈現層（render 程式）分離。

## 來源架構

- 每章 production 使用**四套 commentary**（ccbiblestudy CT、ccbiblestudy GT、KingComments KC、BibleHub Study BH）＋**一份 STEP Bible 原文證據檔**。
- 準備：commentary 用 `util/crawl_bible_text.py` → `raw_data/*.txt`；STEP 用 `util/extract_stepbible.py "書名 章" --data_path .stepbible_data --output_path raw_data --download`；再用 `util/build_source_manifest.py` 重建 manifest。
- `build_source_manifest.py` 純依磁碟現況產生，不下載。**絕不手寫 `source_manifest.md`**（裸檔名會被靜默丟棄，是利／民／申整卷損毀的根因）。
- 禁止硬猜來源 URL；`raw_data` 已存在不覆寫（MCP 正式覆寫需明確 `overwrite=true`）。
- `raw_data/stepbible_*.txt` 衍生自 STEP Bible / STEPBible-Data，依 CC BY 4.0，必須保留歸屬；本庫自己的 Apache-2.0 不取代該上游授權。
- 一條目一主分類（其他性質放 `secondary_types`，不得多資料夾重複建檔）；同名不同實體必須分檔並各加最小穩定限定詞，登記 `_config/link_homonyms.yaml`。

## Commentary 與 STEP 的角色區分

- 四套 commentary 是**散文解讀層**：統計共識或分歧時，只計 CT／GT／KC／BH。
- STEP 是**原文證據層，不是第五套 commentary，永遠不算一票**。
- STEP 可支持：詞形、lemma、Strong、Extended Strong、morphology、context gloss、lexicon 義域。**lexicon 是可能義域，不是本節自動語境義；morphology 不自行證明神學結論。**
- **STEP absence 不是證據**：STEP 未在 projection 出現、或 brief lexicon 未列某義，不等於「STEP 否定該義」或「原文查無此義」，不得用來否定 commentary 的解經延伸。
- **正面分層寫法**：先寫 STEP 能確認的字形／lemma／Strong／morphology／本節譯義與簡要義域，再寫「部分註釋進一步理解為……」。除非 STEP 與 commentary 在 Hebrew／Strong／morphology／lexical identification 上有明確可驗證衝突，否則不要寫成「這個字並不證明」「原文沒有這個意思」「不能從中文譯名倒推」。
- Strong 編號是資料欄位，不是 wiki ID；不為功能詞、詞形或 Strong 批量建頁。

## M3／M6：一律人工 payload

- M3／M6 一律**人工手寫 payload**；外部模型／API 自動生成路徑已停用。
- 正式流程是 `util/run_chapter_manual.py`（`prompts` → 手寫 → `check` → `run`）。MCP 的 `run_chapter`、`render_manual_chapter`、`prepare_manual_payload_prompts` 等名稱固定走這條人工路，不得偷換成自動生成。
- **實際 M3／M6 寫作格式，以當次 `run_chapter_manual.py prompts` 落地的 prompt 為最終規格**，優先於本檔與 SOP 的任何摘要。
- `lint_chapter_content` 只是格式提示；結構閘門是 `check_manual_payloads` / `check`。

## Commentary 全文閱讀

- 每章四套 prose commentary **各自全文閱讀一次**（不是 prompt 摘要、不是 grep 關鍵字）。

- 在 `.tmp/第x章/read_log.md` 每套登記行數＋**三段逐字引句，至少一段出自該檔後三分之一**。

- `source_manifest.md` 與 `read_log.md` 是 read gate 本身需要先建立／更新的驗證產物；它們不受「PASS 前不得動 production 內容」限制。`source_manifest.md` 仍必須由 `build_source_manifest.py` 產生，不得手寫。

- `python util/check_source_read.py 書名 章` 必須同時回報 commentary receipt 與 STEP machine validation PASS。**未 PASS 前，不得修改 M3／M6 payload、link payload 或渲染後的 production markdown。**

- M3／M6 prompt 不重複內嵌 commentary 全文，這是避免重讀，不是允許摘要或降低閱讀要求。

## STEP machine validation／projection／query 邊界

- STEP full raw 由 formal parser 確定性驗證（book/chapter、verse coverage、word/Strong/morphology/原文字元、SHA-256 receipt 寫 `step_source_receipt.json`）；**不要求人工逐詞閱讀，不寫 434 列人工回執**。
- M3 只接收 candidate-matched STEP evidence（evidence／surfaces／verses 只是搜尋範圍，不是整節或整章輸入）；M6 只用 selected HIGH／MEDIUM evidence，不用 LOW 填預算。
- 單一 candidate 無法定位或 evidence=全章 → 只讓該 candidate fail-small，不影響同 batch 其他 candidate；**絕不 fallback 成整節或整章 STEP raw**。
- STEP 不足時用 MCP 精確查詢（`query_step_context` 查 verses／exact Strong／base Strong／word；`find_step_candidates` 探候選；`find_step_occurrences` bounded 查相鄰章）——**不猜測、不 dump full raw、不查網路 STEP**。
- `read_chapter_source` 不得讀取 structured STEP raw 全文。
- STEP 是否可用一律以**當章 manifest ＋ machine validation 結果**為準，不依賴過去某次 Phase A 書卷清單。

## 不得猜測來源或原文資料

- 一切內容必須可對回經文或有效 raw text；來源未提的不寫，不憑神學常識外推。

- **Commentary 引述、來源 attribution、音譯、希伯來／希臘字母與其他原文資料**：回查本章 manifest 宣告的有效 `raw_data/` 來源。

- **經文本文與經文交叉引註**：回查 `raw_scripture/` 的正式經文；不得把 commentary raw 當成經文本文的權威來源。

- 原文類條目名的括號音譯／希伯來字母**必須是本章來源實際出現過的拼寫**；查無出處的希伯來字母是 P4 error（擋 build），查無出處的新建拉丁音譯是 manual_review。

- **「」是逐字宣告，不是強調或術語記號。** Reader-facing production 內容遇英文 commentary 時，預設用**具名的繁體中文轉述，不加「」且不貼英文原文**；若正式 prompt／驗證產物明確要求 verbatim quote（例如 `read_log.md`），才保留英文原句作逐字引句。中文翻譯不得放進「」冒充英文來源的逐字原話。

- STEP 逐詞的中文字面直譯、自己對經文結構的概括，都不加引號。

- 不假裝無效來源有效；不為湊條目而亂搜薄弱資料。

## 已完成章節 vs 新章

- **新章** → 照 `agent_start_prompt.md` 全套流程。

- **已完成且驗證通過的章節不重做**。維護＝**勘誤與補充，不是重跑流程**：舊版對的保留、錯的才改，不為改而改。維護紀律見 `agent_maintenance_prompt.md`。

- 已完成章節的 STEP-only 遷移用 `util/backfill_step_sources.py`（冪等）；`util/audit_original_language.py` 只出報告，**永不修改 production 內容**。

- 已完成章節不得因 STEP infrastructure migration 自動重新開啟 production lifecycle；migration 本身不代表要重跑 M3／M6／render／links／commentary reading／proofreading。

- 目前哪些章節已完成 migration，必須依當前 project status、manifest 與 receipts 判定，不依賴本檔中的歷史 Phase 清單。

## 寫作要求

- **所有輸出用繁體中文，寫給一般大眾看得懂**：先講白話結論，段落要短，多家並陳拆分點，原文編號不寫進句子中間。
- **散文敘述是主幹（≥ 總字數一半）**，表格／mermaid／callout 只是補充，不可反客為主；材料若是流程／路線／對照／階層／時間軸的形狀就用對應圖表，但圖表不折抵散文份量。
- 拒絕 AI 腔：禁「不是X而是Y」對仗轉折、假掉書袋開場、導覽口吻、空泛昇華句尾、湊三律排比。
- **正文不得出現流程／版本註記**（「舊版漏掉」「本次維護補上」「應並陳」）——勘誤依據寫在 commit 訊息或 relation。要講分歧就直接讓各家並陳。
- 粗體節制；`==高亮==` 每段最多一處。和合本女性主詞用「他」不用「她」。

## 不為「更完整」而重寫既有正確內容

- 正式條目的 `## 定義`／`## 主題發展` 預設視為保護區：
  不因本章新增資料就順手重寫。
- 但若來源複核確認 definition 有事實錯誤、來源錯配、過度推論，
  或 development 已明顯落後既有跨章累積範圍，則應依
  `agent_maintenance_prompt.md` 的規則做必要的點狀修正或重新綜整。
- 不得只為了「更完整」「更漂亮」而重寫。
- 不 100% 相信舊版（全稱詞、對照類敘述最容易錯），但勘誤是**點狀修正**，不是整段重寫。
- 不因為想顯得更完整／更嚴謹而重寫來源支撐無誤的內容。

## MCP／Hermes Scripture 使用原則

- `Hermes-Scripture-MCP` 工具（`get_chapter_status`、`search_wiki_entries`／`read_wiki_entry`、`read_chapter_artifact`／`read_chapter_source`、STEP 查詢工具）減少找檔與誤連；**不取代候選判斷、來源複核與收尾閘門**。

- SOP 中**已有 MCP 對應的工作**優先走 MCP；累積類工作依 `preview` → token → `apply` → 再 `preview` 必須 0 變更。不要假設每個 `util/*.py` 都有 MCP 對應；例如 maintenance SOP 明列 `check_accumulation_orphans.py`、`check_development_staleness.py` 目前需直接執行 script。

- 大型 corpus 呼叫 `run_gates`：`timeout_seconds=600..900`，MCP client tool-call timeout 設 `600000–900000` ms。

- 改名一律 `python util/rename_markdown.py <src> <dst> [--dry-run]`（同步全庫 WikiLink；預設 dry-run，正式執行須明確確認）。

## vexp 使用要求

- 程式碼／pipeline／resolver／schema 導航：照上方 vexp 區塊——`run_pipeline` 優先，vexp daemon 執行時 PreToolUse hook 會擋 Grep／Glob。

- **內容核對例外**：SOP 明確要求的定向 grep／Glob 不屬於「探索 codebase」。這包括對 `raw_data/`、`raw_scripture/`、`link_folder/` 與既有 production `.md` 做來源出處、type／路徑、污染字串、md-vs-yaml 一致性等核對。

- 這個例外只適用於**已知目標、已知驗證目的**的內容／產物核對；不得拿它繞過 vexp 去自由搜尋 Python／程式碼結構。若 built-in Grep／Glob 被 hook 擋，改用 SOP 指定的 script／MCP／精確 shell command 完成該項核對，不做廣泛 code search。

- 四套 commentary 的全文閱讀不能用 `get_skeleton`／pipeline 取代。

- 直接 `Read` 具名的 production 文件（本檔、三份 SOP、`.tmp` payload、章 md、`link_folder` 條目）不受限制。

## Validation／完工定義

- **新章 production／等同重做某章的大改**：完整收尾順序與參數以 `agent_start_prompt.md` 步驟 7–8 為準。共享憲法不重抄整套 ordered commands，避免與 SOP 漂移；其中包含 `build_appendix_links.py`，且 embedding index 必須執行實際增量更新，不能用 `--check` 取代更新步驟。

- **既有章節 maintenance**：完工定義以 `agent_maintenance_prompt.md` 為準。核心至少包含 `validate_knowledge_base` 與 `verify_links`，其餘 gate 依實際改動範圍追加；只有大改到等同重做該章時才升級為新章完整收尾。
- Gate 的參數不是一體適用：例如 `check_existing_links.py --missing` 需要章節 markdown 路徑；以書卷名為參數的 corpus／book-level 工具則傳標準書卷名。**不得把「閘門吃書卷名不是路徑」當成所有 gate 的通則。**

- `verify_links` 的正式通過條件是 BROKEN=0、INVALID=0、UNKNOWN=0；`PENDING_SCRIPTURE_REFS` 可依 `scheme.md` 的正式規則存在，不應被誤判成同類失敗。

- **適用於本次任務的 gates 全部 PASS 才可 commit。** CI 是最終機械守門。

- **閘門全綠 = 結構／機械驗證通過，不代表內容對 rawdata 忠實。** 新建條目、B 類累積、本章整理與事實性斷言仍必須逐條回查 manifest 正式來源／`raw_scripture`；語意勘誤是獨立人工步驟。

- 回報只列結論數字（errors／critical／broken 等）與需人工決策項，不貼完整報告。

## Workflow Router

| 情境 | 權威文件 |
| --- | --- |
| 新章 production | `agent_start_prompt.md` |
| Codex 主導新章協作 | `agent_codex_orchestrator_prompt.md`（角色／review/fallback；實際步驟仍以 `agent_start_prompt.md` 為準） |
| Codex 額度耗盡後 Antigravity 接手 | `agent_antigravity_orchestrator_prompt.md` |
| Evidence review | `agent_evidence_audit_prompt.md` |
| 已完成章節勘誤／補充 | `agent_maintenance_prompt.md` |
| 架構、來源與設計判斷 | `scheme.md` |
| 實際 M3／M6 payload 規格 | 當次 `util/run_chapter_manual.py prompts` 輸出（最高優先，蓋過上述文件的摘要） |
| 資料結構契約 | `_config/schemas/*.json` |

## Multi-Agent Collaboration

`agent_start_prompt.md` 仍是新章 production **唯一正式流程**。Orchestrator prompt 只決定誰推流程、誰寫內容、誰 review；不得另造第二套 SOP。

預設：**Codex 總控／QA → Claude Opus 主筆 → Codex 落地前 audit → Claude 修 → Codex gate/render/apply/final gates**。Codex quota／service unavailable 時，**Antigravity 從同一磁碟 checkpoint 接手總控與 reviewer**，不重做、不重置 review 預算。

### Codex：Primary Orchestrator + Evidence Reviewer

- Codex 是新章預設 host，先讀 `agent_codex_orchestrator_prompt.md`。
- 負責 source/manifest/STEP machine validation、similarity/resolver/prompts、review receipt、check、run/render、B prepare/preview/apply、final gates、commit。
- Claude交稿後依 `agent_evidence_audit_prompt.md` 查核；audit 對 Claude-authored content read-only，findings 退 Claude 修。
- M3 必查已寫內容與 **missing entry candidate**；candidate 根因要退回 `link_candidates.yaml`，再重跑 deterministic steps。
- Codex 不做第一次語意作者；否則會自己寫、自己審。

### Claude：研經內容作者

- 完整讀四套 Commentary、完成 `read_log.md`、做 candidate 語意判斷、手寫 M3/M6/B 類內容，依 reviewer findings 修 source-of-truth payload。
- 固定 `model=opus`、`effort=max`；同一章優先沿用同一 `session_id`。
- 不得靜默 fallback Sonnet/Haiku；Opus 不可用就 `BLOCKED`，除非使用者另允許。
- Claude 不主導 run/render/apply/final gates/commit，也不得替 reviewer 宣告 PASS。

### Antigravity：Codex quota fallback + 可選總編輯

- Codex 因 quota/rate-limit/service unavailable 無法繼續時，Antigravity 依 `agent_antigravity_orchestrator_prompt.md` 從當前 disk state 接手 **orchestrator + Evidence Reviewer**。
- Antigravity fallback 使用 `agy models` 中最新一代 **High** tier Gemini；目前指定 `gemini-3.7-flash-high`（Gemini 3.7 Flash High）。不要把舊 `gemini-3.1-pro-high` 當預設 fallback。
- Antigravity 的 High reasoning 由 model tier/slug 表達；若 live catalog 出現更新一代 High，改用更新者。
- 它接手後仍把 prose 任務交給 Claude Opus/max；自己只做流程與 QA。
- Codex 已用掉的 `review_attempts` 照算，**換 reviewer 不重置**。
- Codex 可用時，Antigravity 仍可在複雜章節／數章／整卷完成後做高層 editorial consistency review，但不重做逐句 evidence audit。

### Review budget / receipt（硬限制）

- 每章每個 stage（`m3`、`m6`、`link_updates`）最多 **2 次 substantive reviewer attempt**，由 `util/agent_review.py` 強制執行。
- Attempt 1/2：完整 audit，一次列齊 material findings；M3 一定含條目完整度。
- Claude 修後 Attempt 2/2：最後一次 reviewer 機會，只複核上一輪、修改處與直接波及範圍，並一次列齊所有剩餘 material findings。
- 不把 review quota 浪費在文風偏好、可有可無的「更完整」建議。
- Attempt 2 若仍 `CHANGES_REQUIRED`：Claude做**最後修正**；下一次 `submit` 若 hash 改變，程式直接對新 hash 記 `forced_pass: true` + `reviewer_status: pass`。**禁止第三次 reviewer call。**
- `BLOCKED` 不算 substantive attempt；因此 Codex quota block 後可由 Antigravity接同一 hash，不額外消耗機會。
- 兩次預算屬於 stage，不屬於 agent/session；換 Codex session、換 Antigravity、重開 IDE 都不能歸零。
- `forced_pass` 是流程上可跨 gate 的 PASS，但不是「reviewer 確認零問題」；final mechanical/semantic sanity gates 仍全部照 SOP 跑。
- v1 舊 receipt 的 `codex: pass` 仍可讀；新 receipt 使用 `reviewer_status` / `reviewer_agent` / `review_attempts` / `review_history`。

### Pre-landing gates

- **M3**：Claude寫 M3 → orchestrator `submit m3` → reviewer attempt（含 missing-entry）→ Claude修 → 最多第二次 reviewer → 必要時 Claude最後修 + forced pass → `gate m3` PASS；之後才生成正式最新 M6 prompt。
- **M6**：Claude寫 M6 → `submit m6` → reviewer 查 M6 + 已核准 M3 consistency → 同樣最多兩次 → `gate m6` PASS；未過不得 run/render。
- **B 類**：orchestrator prepare → Claude填 `link_updates.yaml` → `submit link_updates` → 最多兩次 reviewer → `gate link_updates` PASS → 才 apply。
- render/apply 後照 `agent_start_prompt.md` 做 post-landing sanity + steps 7–8 final gates；這不是第三輪 evidence audit。

### 預設內容工作流

```text
Codex 準備來源／machine gates
→ Claude(Opus,max) 全文 Commentary + read_log + candidates
→ Codex similarity / resolve / prompts
→ Claude M3
→ reviewer attempt 1 → Claude修
→ reviewer attempt 2（若需要）→ Claude最後修 → 必要時 FORCED PASS
→ M3 gate
→ 最新 M6 prompt → Claude M6 → 同樣最多兩次 review → M6 gate
→ check → run/render
→ B prepare → Claude B → 同樣最多兩次 review → B gate → preview/apply
→ post-landing sanity + final gates → commit

若 Codex 額度耗盡：
Codex current disk checkpoint → Antigravity(latest High) 接手 → 不重置 review_attempts → 繼續同一流程
```

- 同一章 Claude 優先維持一個 session；多章一章完整完成、一章一 commit。
- Agent 之間不靠多數決；來源事實回到可驗證 evidence。

### 跨層修改邊界

- Orchestrator 可以執行正式 pipeline／schema-aware scripts，但不得因此成為研經內容作者。
- Evidence audit 對 Claude-authored M3/M6/B read-only；內容修正由 Claude做。
- Claude 內容任務不得順手改 pipeline、schema、resolver 或 MCP server；工程缺陷另開工程任務。
- 程式工程任務不得順手改寫經文、`link_folder/` 正文、`raw_data/` 或 `.tmp/` production payload 的語意內容。
- 跨層契約修正要明確指出兩層並各自 validation。
- 經文本文只取自 `raw_scripture/`，不得由模型改寫。

## 多 Agent 意見不一致時

- **不採多數決。**
- 回到 `source_manifest` / `raw_data` / STEP evidence / 正式 project rules。
- 要求各方指出可驗證證據（raw 行號、STEP receipt、schema、gate output）。
- Antigravity 作為 editor 時可整理分歧，但不能以「第三票」取代證據。
- 無法確認就標 `unresolved`，不得猜測，交人工裁決。
