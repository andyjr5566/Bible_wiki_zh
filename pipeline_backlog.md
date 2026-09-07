# Pipeline 工程待辦清單

來源：《約書亞記》第1-3章 production（commit `04c748b1` / `b0c908c0` / `d0cf0728` / `920640b5`）過程中浮現的**流程性**問題。
只收「會在下一卷再咬一次」的項目；單章特有的內容問題不列入。

**邊界**：以下 A1-A4、B1、B2、B4、B6、C2、C4 都是 pipeline／護欄／schema 改動。依 `AGENTS.md`「跨層修改邊界」，
內容任務不得順手改這些，必須另開工程任務；反之工程任務也不得順手改 `raw_data/`、`link_folder/` 正文或 `.tmp/` payload 的語意內容。

## 索引

狀態：✅ 已修並有回歸測試　🔷 已修（doc／SOP）　⬜ 未動

| # | 狀態 | 問題 | 主要位置 | 後果 |
| --- | --- | --- | --- | --- |
| A1 | ✅ | 作廢流程直接刪手寫 payload | `util/run_chapter.py` `_invalidate_stale` | 數小時的手寫內容無備份消失 |
| A2 | ✅ | YAML round-trip 失敗把檔案截成 0 byte | 所有 `.tmp/*.yaml` 寫入點 | payload 靜默清空 |
| A3 | ✅ | 記 verdict 前先改檔＝review 額度蒸發 | `util/agent_review.py::record_verdict` | 每 stage 只有 2 次，不可回復 |
| A4 | ✅ | stage hash 涵蓋範圍小於 stage 本身 | `util/agent_review.py` | verdict 掛在錯的 hash 上；曾誘發 reviewer 自行改 gate |
| B1 | ✅ | link_plan 是開工快照，重跑 resolve 會塌回 A 桶 | `util/resolve_link_candidates.py::resolve` | A/B/C 分類全毀，check 才報錯 |
| B2 | ✅ | render 每次吃掉附錄區塊 | `util/run_chapter.py::render_step` | 整段內容消失而四閘門全綠 |
| B3 | ⬜ | 引句閘門門檻 10 字，短偽引句不驗 | `util/check_quote_fidelity.py` | 偽逐字引句常態漏網 |
| B4 | ⬜ | GT 子來源掛名護欄看不懂裸名寫法 | `util/run_chapter.py::_gt_subsource_review` | 護欄在改寫散文 |
| B5 | ⬜ | 主題發展的形狀規則靠 dry-run 拒絕才學到 | link_updates prompt | 每章重撞、浪費往返 |
| B6 | ⬜ | forced_pass 正在變成常態出口 | `util/agent_review.py` | gate 逐漸失去意義 |
| B7 | ⬜ | reviewer finding 不可直接採納 | `agent_evidence_audit_prompt.md` | 依編造的 finding 改動內容 |
| C1 | ⬜ | 重複條目只靠人工判讀擋 | SOP 步驟2 | 條目分岔，閘門不擋 |
| C2 | ⬜ | 正向孤兒沒有全庫掃描 | `util/check_existing_links.py` | 全庫缺漏無人掃 |
| C3 | ⬜ | Windows 環境摩擦 | venv wrapper | 每支指令都要前綴 |
| C4 | ⬜ | `全書目錄及綱要.md` 對每本新書都會缺 | render 的 nav 區塊 | 每章 nav 斷鏈且無閘門捕捉 |

---

## A 級：會靜默毀掉已完成工作

### A1. 作廢流程直接刪除手寫 payload

**症狀**　stale 判定後會刪掉 `.tmp/第x章/entry_content/*.yaml` 與 `chapter_content.yaml`。這是人手寫數小時的產物，
刪除沒有備份、沒有確認清單。第3章實測，只能先 `cp -r` 自保才敢跑。

**位置**　`util/run_chapter.py` 的 `_invalidate_stale` / `_invalidate_after_entry`；
`util/run_chapter_manual.py` 的 `--confirm-stale` 入口；
`util/mcp/server.py::prepare_manual_payload_prompts`（docstring 已警告會刪，但只是警告）。

**解**　刪除改為搬移到 `.tmp/第x章/.trash/<UTC timestamp>/`；真要刪另開 `--delete-payloads`。
prompts / prepare 的回傳值列出被搬移的檔案清單。

**驗收**
- 對一個已寫滿 payload 的章跑 stale 路徑：`entry_content/` 清空，但 `.trash/<ts>/entry_content/` 內容完整。
- 連跑兩次，第二次不覆蓋第一次的 trash。
- 新增測試 `test_run_chapter.py::test_stale_moves_payloads_to_trash`。

**狀態**　✅ 完成。`run_chapter.py` 新增 `_retire_node`／`_trash_node`／`_trash_session_dir`：
`_invalidate_stale` 與 `_invalidate_edges`（涵蓋 after_plan／after_entry 三輪）改走 `_retire_node`，
預設搬到 `.tmp/第x章/.trash/<UTC ts>[-N]/` 並保留相對結構，同秒重跑補序號不覆蓋。
`ChapterContext(delete_payloads=)` ／ `run_chapter(delete_payloads=)` ／ CLI `--delete-payloads` 才真刪。
搬移清單透過 `ctx.notes`（`回收（未刪除）：` 前綴）回報，`run` 與 `prompts` 都會印；
MCP `prepare_manual_payload_prompts` 的 stdout 一併帶出。`.gitignore` 排除 `**/.tmp/**/.trash/`。
測試：`test_stale_moves_payloads_to_trash`、`test_delete_payloads_flag_skips_trash`。

### A2. YAML round-trip 失敗會把 payload 截成 0 byte

**症狀**　`open(path, 'w')` 已清空檔案後 dump 才丟例外，結果是 0 byte。
另外 round-trip 會把 literal block 攤成引號式、在表格列之間插空行，破壞已通過 gate 的排版。

**位置**　所有寫 `.tmp/第x章/*.yaml` 的地方：`util/run_chapter.py` 的 payload 寫入、
`util/link_updates.py`、`util/resolve_link_candidates.py::build_plan_document`。

**解**　統一走一個 `write_yaml_atomic(path, data)`：先寫 `path.tmp` → `os.replace`。

**驗收**
- 注入一個會在 dump 中途丟例外的物件：原檔內容完全不變，暫存檔被清掉。
- 確認沒有其他地方直接 `open(..., 'w')` 寫 yaml。

**狀態**　✅ 完成。新增 `util/yaml_io.py::write_yaml_atomic(path, data, **dump_kwargs)`：
先 `safe_dump`（失敗不動原檔）→ 寫 `<name>.<pid>.tmp` → `os.replace` 換上；任何錯誤刪暫存檔並 re-raise。
改接的四個 payload 寫入點：`run_chapter._write_yaml`、`resolve_link_candidates.write_plan_yaml`、
`link_updates`（`link_update_review_baseline.yaml` ＋ `link_updates.yaml`，後者保留 `default_style='"'`）、
`agent_review._write_state`（`agent_review.yaml`）。其餘 `yaml.safe_dump` 只用於 md frontmatter／manifest
列印，不在 `.tmp/*.yaml` 範圍。round-trip 把 literal block 攤平／表格插空行是 `safe_dump` 本質，
仍以「小改用純文字 replace」為人工紀律，不在本次程式範圍。
測試：`util/tests/test_yaml_io.py`（4 項）。

### A3. 記 verdict 前先改檔＝該次 review 額度蒸發

**症狀**　`record_verdict` 用當前內容 hash 驗證，所以順序必須是「先記 verdict → 再修」。
第1章 m6 搞反過一次，SHA 對不上，那次 attempt 直接消失——而每個 stage 只有 2 次，不可回復。

**位置**　`util/agent_review.py::record_verdict`、`_review_attempts`。

**解**　`verdict` 加 `--observed-sha`，允許對 reviewer 當時實際看到的 hash 補記，
寫進 `review_history` 並標 `late_recorded: true`。
現況不符時給明確錯誤訊息（列出 observed / current 兩個 sha 與可用的補救指令），而不是靜默拒絕。

**驗收**
- 改檔後仍能用 `--observed-sha` 補記，`review_attempts` 正確 +1。
- 補記不改變當前 hash 的 gate 判定。
- 未帶 `--observed-sha` 時的錯誤訊息包含可直接複製的補救指令。

**狀態**　✅ 完成。`record_verdict` 加 `observed_sha=`（CLI `--observed-sha`，須等於 `--sha`）：
sha 對不上時不再靜默丟棄，而是報出 observed／recorded／current 三個 sha ＋可複製的補救指令；
帶旗標則把該次 attempt 照算、history 標 `late_recorded`，並把 verdict 掛在
`record["verdict_sha"]`（reviewer 當時看過的 sha）而非目前內容。`require_pass` 新增
`verdict_sha == current` 檢查（`forced_pass` 例外、缺欄位 fallback 到 `sha256` → v1 receipt 照舊可讀），
補記過的舊版本不會被當成對目前內容的 PASS。`agent_evidence_audit_prompt.md` 補上補記指令範例。
測試：`test_late_recorded_verdict_credits_attempt_without_blessing_current`、
`test_late_recorded_pass_does_not_pass_gate_for_new_bytes`、`test_observed_sha_must_equal_sha`。

### A4. stage hash 的涵蓋範圍小於 stage 本身

**症狀**　hash 只涵蓋 `entry_content`，但 m6 與 link_updates 的 verdict 也掛在同一套機制上。
之前 reviewer 就是因為 hash 對不上，自行在 `util/agent_review.py` 加了 `--allow-same-sha` 旗標讓自己過關。

**位置**　`util/agent_review.py` 的 stage hash 計算。

**解**　每個 stage 定義自己的檔案集合，且只涵蓋該 stage 被審的檔案：

| stage | hash 輸入 |
| --- | --- |
| m3 | `entry_content/*.yaml` |
| m6 | `chapter_content.yaml`（＋已核准 m3 的 hash 當 parent） |
| link_updates | `link_updates.yaml` |

hash 的輸入檔案清單寫進 receipt，事後可稽核。

**驗收**
- 只改 `chapter_content.yaml` 時，m6 hash 改變而 m3 hash 不變。
- receipt 裡看得到每個 stage 實際涵蓋了哪些檔案。
- 不存在 `--allow-same-sha` 這類旁路旗標。

**狀態**　✅ 完成。stage 的每-stage 檔案集合本來就已是分離的（m3=`entry_content/*.yaml`、
m6=`chapter_content.yaml`＋m3 parent、link_updates=`link_updates.yaml`＋m3/m6 parent），
且已無 `--allow-same-sha`。本次補上**稽核面**：抽出 `_stage_parts` 同時產生 digest 與人可讀
涵蓋清單，`submit`／forced-pass 都把 `hash_inputs` 寫進 receipt，`submit` 輸出也印「hash 涵蓋：…」。
docstring 明列「刻意不留 --allow-same-sha 旁路」。測試：`test_m6_hash_isolates_from_m3`、
`test_receipt_records_hash_inputs_per_stage`、`test_no_allow_same_sha_bypass_flag`。

**附帶**　reviewer 對 `util/` 應該是硬性 read-only。目前只靠 sandbox 設定＋我每輪人工 `git status util/` 確認。（未處理——屬 sandbox／權限設定，非本檔程式碼範圍。）

---

## B 級：會靜默降低內容品質

### B1. link_plan 是開工快照，apply 後重跑 resolve 會塌回 A 桶

**症狀**　第3章收尾後重跑 resolve，34 個候選全部跑回 `A_use_directly`，
接著 `check` 才報「對不上任何 C 類候選」，只能手工還原 A=2 / B=24 / C=8。

**位置**　`util/resolve_link_candidates.py::resolve`、`build_plan_document`；`util/run_chapter_manual.py::_plan_after_run`。

**解**　M3 gate PASS 時在 `link_plan.yaml` 寫入 `locked_at` 與當時的 buckets hash；
`resolve` 遇到 locked 直接拒寫並提示 `--force-replan`。

**驗收**
- gate PASS 後重跑 resolve：不改檔，回非零退出碼。
- `--force-replan` 可覆寫，且會清掉 `locked_at`。

**狀態**　✅ 完成。實作為 sidecar 記號（`.tmp/第x章/link_plan.lock`，比只寫 `locked_at` 欄位更耐
「手動 rm link_plan.yaml」）：
- `resolve_link_candidates.py`：`lock_plan`／`unlock_plan`／`plan_is_locked`／`bucket_digest`／
  `PlanLockedError`；`write_plan`＋`write_plan_yaml` 有 lock 就拒寫（`PlanLockedError` → `main` 回非零），
  `--force-replan` 先 `unlock_plan` 再重寫；`lock_plan` 同時在 `link_plan.yaml` 補 `locked_at` 欄位。
- `agent_review.py gate ... m3` PASS 後自動 `lock_plan`（失敗不擋 gate）。
- `run_chapter.resolve_step`：plan 檔不見但 lock 還在＝拒絕靜默重生，指向 `--force-replan`。
- `run_chapter._invalidate_stale`：candidates 正式改動而 `link_plan.yaml` 被作廢時，一併作廢 lock
  （維護加候選的正規流程照常重算）。`agent_maintenance_prompt.md` 情境坑一／坑二補上 lock 說明。
測試：`test_resolve_candidate_formats.PlanLockTests`（4）＋`test_run_chapter` 2 項。

### B2. render 每次都吃掉附錄區塊

**症狀**　這次為了修 review findings 重 render 第3章，地圖附錄整段消失，而四道閘門全綠。
必須人工記得補跑 `build_appendix_links.py`。這是每次重 render 都會發生的固定損失。

**位置**　`util/run_chapter.py::render_step`（產生章 md 時未保留 `<!-- appendix-links:start/end -->`）；
`util/build_appendix_links.py`。

**解**　二選一——render 收尾自動呼叫 build_appendix_links，或 render 保留既有 appendix 區塊。
另外 `check_chapter_files` 加一條：該章在附錄索引中有對應資源但 md 無區塊 = FAIL。

**驗收**
- 對已有附錄的章重 render 後區塊仍在，`build_appendix_links --check` 回報 0 stale。
- 手工刪掉區塊後 `check_chapter_files` 會 FAIL。

**狀態**　✅ 完成（兩路都做）。
render 保留：`render_chapter` 新增 `APPENDIX_BLOCK_RE`／constants，`parse_chapter` 先拆附錄區塊
（否則被吞進 organization）；`run_chapter.render_step` 比照 `map_block` 從舊檔擷取 `appendix_block`
一併 passthrough 給 `render_chapter(appendix_block=)`（本就支援、但沒人傳）。
閘門：`build_appendix_links.collect_all_appendix_sections(build_indexes=False)` 唯讀掃描；
`check_chapter_files` 加「步驟6｜附錄資源區塊未被 render 吃掉」——索引有本章資源但 md 無區塊＝FAIL
（只對真正庫根跑，plugin 是 repo-global）。測試：`test_appendix_block_is_preserved_and_placed_after_organization`、
`test_rerender_preserves_appendix_links_block`、`test_appendix_block_missing_when_index_has_resources_fails`。

### B3. 引句閘門門檻 10 字，4-7 字的偽逐字引句完全不驗

**症狀**　常駐閘門 PASS，但另跑 `--min-chars 2` 每章都抓到東西：
自己的措辭套上「」、截斷經文補句號、中譯冒充英文原句。而這一步不在 SOP 的 ordered commands 裡，靠人記得。

**位置**　`util/check_quote_fidelity.py` 的 `MIN_QUOTE_CHARS`；`agent_start_prompt.md` 步驟 7-8。

**解**　不動硬閘門門檻（降門檻會噪音爆量，且這一型需要人工裁決不能機械刪）。
改成在 SOP 明列必跑一輪 `--min-chars 2`，裁決紀錄寫進 `.tmp/第x章/quote_adjudication.md`。

**驗收**
- 缺 `quote_adjudication.md` 時 `check_chapter_files` FAIL。
- SOP 步驟含該指令與裁決紀錄格式。

### B4. GT 子來源掛名護欄看不懂裸名寫法

**症狀**　護欄只認 `《》` 包起來的子來源；`── 約書亞記研經資料(蔡哲民等)` 這種寫法會被判成掛名誤植。
第1、2章都為了讓護欄閉嘴而改寫掛名方式——**是護欄在改寫散文，不是來源在決定掛名**。
長期會累積出一批「為了過機器而扭曲的 attribution」。

**位置**　`util/run_chapter.py::_gt_subsource_review`；同型的 `_quote_attribution_review` 一起看。

**解**　子來源辨識補上「`──` / `—` / `―` ＋裸名」形式（U+2015/U+2014 的碼位問題之前修過一次，同一個地方）；
比對前把子來源名正規化（去書名號、全半形括號、空白）。

**驗收**
- 全庫掃描誤報降到 0。
- 原本能抓到的真陽性（利6 那組跨家誤植）仍然被抓到——兩邊都要有回歸測試。

### B5. 主題發展的形狀規則靠 dry-run 拒絕才學到

**症狀**　「development 不能寫成本章摘要的加長版」這條規則 prompt 裡沒寫，
第3章 `自潔`、`雲柱火柱` 各撞一次才知道正解是「從前幾章講起、本章當終點，本章引句留在 summary 不要重複」。

**位置**　link_updates prompt 產生處（`util/link_updates.py`，prepare 階段寫出的 prompt 與 `review_evidence.md`）；
拒絕點在 `util/link_updates.py::_v2_verdict`。

**解**　把該規則寫進 prompt，並在拒絕訊息裡附一行正確形狀的範例。

**驗收**
- prompt 文字含該規則。
- 踩到時的錯誤訊息可直接照著改，不需回頭查 SOP。

### B6. forced_pass 正在變成常態出口

**症狀**　第3章 link_updates 兩次用完後 forced pass。規則上它可以過 gate，
但它不等於 reviewer 確認零問題。若不看著，往後每章都會漂到這個出口。

**位置**　`util/agent_review.py` 的 `forced_pass` 設定點與 `review_history`。

**解**
- receipt 記錄每 stage 的 forced_pass 次數；加一支彙總（或併進 `audit_knowledge_base`）在卷末報告 forced_pass 比例。
- Attempt 1 的 reviewer prompt 加強制 scope checklist（M3 必含條目完整度），避免額度被花在文風偏好上。

**驗收**
- 一行指令可查出某書卷各 stage 的 forced_pass 率。
- `agent_evidence_audit_prompt.md` 的 attempt 1 有 checklist。

### B7. reviewer finding 不可直接採納

**症狀**　本次全局 review 三項觀察：1 項真（STEP 節號掛錯，`yi.Ka.re.Tu/n` 在書3:13 不在 3:16）、
1 項該修但它自己放行（書3:12 整節沒寫）、1 項誤報（說「相關條目」該連結，但那兩個名字庫裡根本不存在）；
它連資料夾名都寫錯（地理 vs 地點）。之前也有整條編造引句的紀錄。

**位置**　`AGENTS.md`「多 Agent 意見不一致時」、`agent_evidence_audit_prompt.md`。

**解**　規則已有，但要把「missing 類 finding 動手前每條引句 `grep -F` 打一遍」寫成明確步驟；
reviewer 輸出格式強制附 raw 檔名＋行號＋逐字內容（本次全局 review 的 prompt 有要求，應收進正式 prompt 檔）。

**驗收**　`agent_evidence_audit_prompt.md` 含舉證格式的硬性要求。

---

## C 級：每章都在磨，不致命

### C1. 重複條目只靠人工判讀擋

**症狀**　這三章從 similarity 報告把 6 個候選由「新建 C」改成「累積進既有條目 B」
（承受為業→為業／產業、心都消化→心消化、驚慌與膽氣→使天下萬民驚恐懼怕⋯）。閘門完全不擋這一型。庫已 3152 條。

**解**　開章固定跑 `search_wiki_entries(queries=[整章候選])`，
`unmatched` 清單存成 `.tmp/第x章/candidate_existence.md`，列進 `check_chapter_files` 步驟2。

**驗收**　缺該檔時 FAIL。

### C2. 正向孤兒沒有全庫掃描

**症狀**　反向有 `check_accumulation_orphans --all`，正向 `check_existing_links` 只吃單章 markdown 路徑。
所以「章節該連而沒連既有條目」這個方向，全庫從來沒被掃過。

**位置**　`util/check_existing_links.py`。

**解**　加 `--book` / `--all`。

**驗收**　全庫跑得動，輸出可讀的缺漏清單。

### C3. Windows 環境摩擦

**症狀**　每支 python 都要前綴 `PYTHONIOENCODING=utf-8`，否則 cp1252 炸掉。
（Bash heredoc 吃反斜線是 agent 端的問題，用 `chr(92)` 繞開即可，不列入工程項。）

**解**　`PYTHONIOENCODING=utf-8` 設進 venv 啟動 wrapper 或 `.env`。

**驗收**　不帶前綴直接跑任一 util 腳本不炸。

### C4. `全書目錄及綱要.md` 對每本新書都會缺

**症狀**　不是約書亞記特有：任何新書的第1章一 render，導覽列就指向一個要到全卷做完才存在的檔案。
因為它是 markdown 路徑連結而非 wiki-link，`verify_links` 不會報（本次 BROKEN=0），完全靜默。

**位置**　render 的 `<!-- chapter-navigation -->` 區塊產生處（`util/run_chapter.py::render_step`）。

**解**　目標檔不存在時 nav 不輸出該連結；或 render 時產生一份只列已完成章節的漸進式目錄。

**驗收**
- 新書第1章 render 後 nav 無斷鏈。
- 加一條檢查：章 md 內的 markdown 相對路徑連結指向不存在的檔案 = FAIL（目前所有連結檢查都只看 wiki-link）。

---

## 建議處理順序

1. **A1、A3、B2**——前兩件是不可回復的損失，第三件是每次重 render 都靜默掉一段內容而閘門全綠。
2. **A2、A4**——資料完整性與 gate 可信度的地基。
3. **B1、B4**——每章都會踩，且 B4 正在反向污染內容。
4. 其餘依卷別排程；C 級可在任一次工程回合順手做掉。
