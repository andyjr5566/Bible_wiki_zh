# Agent Start Reference — 原因、實例與排錯

`agent_start_prompt.md` 是每章照做的清單；這份收的是清單背後的原因、踩過的坑與排錯細節，
出錯或拿不定時再查。章節代號（§A–§I）對應清單裡的標註。兩份說法若不一致，以清單與
`AGENTS.md` 為準，並回報要修正這一份。

## §A 來源與 manifest

- `build_source_manifest.py` 依 `_config/source_catalog.json` 的四套註釋位址規則與 extractor
  的 66 卷 STEP 檔名契約產生 manifest，raw_data 路徑一律帶 `raw_data/` 前綴。它只看磁碟現況、
  不下載；缺註釋依提示用 crawler，缺 STEP 依提示用 extractor。手寫 manifest 時裸檔名會被靜默
  丟棄，利／民／申整卷就是這樣變成空來源生成。
- `extract_stepbible.py --download` 只下載該書卷需要的 tagged text、lexicon、morphology 到
  gitignored cache，再輸出 canonical `stepbible_*.txt`。
- `run_chapter_manual.py` 的 `prompts`／`check`／`run` 開跑前都會檢查來源讀得到；manifest
  宣告 OK 卻讀不到任何 raw_data 檔就丟 `SourceError` 中止。照訊息修 manifest 或補 raw_data
  再重跑。
- `check_source_read.py` 分兩路：四套 commentary 驗 `read_log.md` 的逐字引句回執；STEP 由正式
  parser 驗 book/chapter、verse coverage、word rows、Strong、morphology、原文字元與 SHA-256，
  receipt 寫入 `step_source_receipt.json`。STEP 不寫人工逐詞引句。

## §B 候選

### B1 斜線名與自造分類的後果

- 斜線在檔名裡是路徑分隔字元，`entry_content/<name>.yaml` 建不出來。該候選的 surfaces
  連不上任何節、knowledge_nodes 對不上而被丟掉、本章累積不寫入、別的條目 related_entries
  指向它也被移除。`run` 的 P4 validate 會報 error，但那時 payload 多半已經寫完。
- 自造分類（利10 的「祭禮」、民9 的「儀式」、民10 的「器具」）resolver 認不得，只把候選降級
  成 `D_new_candidate` 並在 plan 附一句 note「未知分類：X」，條目不會建；P4 validate 會報 error。

### B2 surfaces 範例

- 程式自動比對候選名、條目全名、括號前裸名與 aliases。經文用這些都對不上的簡稱時
  （「桌子」→陳設餅桌子）宣告 `surfaces: [桌子]`。
- 同詞在本章多義：出26「幔子」v1-13 是幕幔、v31-33 是內幔 →
  `surfaces: [{phrase: 幔子, verses: [31,32,33]}]`。
- 和合本女性主詞用「他」不用「她」；surface 寫「她」會對不上經文。

### B3 音譯與希伯來字母

- 括號音譯必須是本章來源實際出現過的拼寫。利2「紀念份（azkarah）」是反例：來源只給英文
  memorial portion。
- P4 validate 對候選檔、entry_content、chapter_content 逐字驗證希伯來字母的出處，查無出處
  ＝error 擋 build。本章新建原文類名稱的拉丁音譯查無出處＝manual_review 提醒（拼寫變體
  無法機械排除）。
- STEP 的使用邊界與正面分層寫法見 `AGENTS.md`「Commentary 與 STEP 的角色區分」。

### B4 存在性掃描

- `check_chapter_files` 步驟2 會驗 `candidate_existence.md`。
- 裸名查不到「X（字義）」型檔名與 alias（民2 差一步建出四個分岔支派條目），所以一律用
  `search_wiki_entries`，不用裸字串 find。
- 措辭不同的同概念實例：承受為業→為業／產業、心都消化→心消化、驚慌與膽氣→使天下萬民驚恐懼怕。

### B5 候選近鄰報告的判讀

- 報告開頭的「摘要：需要判斷的項目」列出所有 ⚠／🆕 候選與候選互查配對；字面直接對上既有
  條目的候選只留一行判定、不附近鄰表。
- **字面解析**：resolver 實際會把候選對到哪（同名／裸名／alias／新建）。標「請確認」的多半
  是 alias 導向不同名條目——alias 登記錯誤會把候選靜默導去錯的條目（安密巴 aliases 誤含
  以實各谷），這裡是唯一的事前攔截點。
- **判定**：`✅ 建議使用既有條目`→確認同概念就改用該條目名（走 A／B 累積）；`⚠`→人工核對
  上下文與經文實體；`🆕 建議建立新條目`→維持 C 類新建。
- **候選互查 ⚠**（本章兩個候選彼此相似 ≥0.8）：新章條目還不在索引裡，只有互查抓得到。
  考慮合併成一個候選（另一個詞用 surfaces），或確認確為兩事再照建。
- evidence 寫得越具體（含經文引句），檢索越準。
- **重排預設關閉**（`_config/model_endpoints.yaml` 的 `tasks.rerank.enabled: false`）：現有
  nvidia 重排模型在本語料上分不出「有／沒有對應條目」（校準紀錄見
  `_config/reranker_calibration.yaml`），判定一直由 embedding 規則決定。`rerank_status:
  disabled` 不會擋任何閘門。要試 Jev 等新模型：加一個 `type: jev` 端點、把 tasks.rerank
  指向它，先用 `util/tests/smoke_reranker_calibration.py` 校準，分得開才把 enabled 改成 true。
- 資料驅動判準見 `scheme.md` §3，門檻與原理見 §3.5。

## §C M6 白名單與 alias

- 本章整理（organization）的 wiki-link 只能連本章 `link_plan.yaml` 的 A／B 類既有條目，或本章
  實際建出的 C 類條目；連到 vault 裡存在但不在本章候選清單的條目會被擋（「wiki-link 目標不在
  本章可連清單」）。要提清單外的既有概念：列成本章候選（走 B 類累積），或用純文字提及。
- 目標是白名單條目的合法 alias（如 [[鹽約]]→立約的鹽）時，程式會自動改寫成 [[全名|原詞]] 再驗。
- M3 的 alias 撞上既有／同批條目時（利2「素祭」配「禮物」），人工路徑的 `check` 會報錯，
  由你從 payload 移除那個 alias（`run_chapter_manual.py` 不會替手寫 payload 刪 alias）。
- `check` 預設會把 organization 裡合法的 `[[alias]]` 改寫成 `[[全名|alias]]` 並回寫檔案；
  MCP 的 `check_manual_payloads` 帶 `--no-rewrite`，只報不寫。
- knowledge_nodes 的互文節點帶小標題，寫成 `出20：16|出20：16 第九誡不可作假見證`，
  不要自己包 `[[ ]]`（渲染時程式會包，自己包會變成雙重括號）。

## §D B 類累積的判準

- `review_evidence.md` 逐條給目標條目的**定義**（400 字以內全文，較長的給首段全文＋其餘段落
  的粗體導語）、**主題發展索引**（有 H3 小標題時只列小標題，否則列段落開頭，上限 8 段）與
  **已累積章清單**（依書卷分組）。最有用的是累積章清單：章號並排＋主題發展空白，就是一條
  沒人寫的跨章線。條目被改過或舊章要補產生：`python util/link_updates.py evidence 【書名】 X`。
- 三個區塊的功能：
  - **定義**：這是誰／什麼、如何辨識、範圍與邊界；只在本章資料改變或澄清穩定身分時更新，
    不寫本章事件摘要。
  - **主題發展**：綜合至少兩個章節（可跨卷），說明推進、轉折、對照或整體意義；不是逐章累積
    的加長版，也不用「民35」這類單章小標題再做一份逐章補充。
  - **逐章累積**：`summary`／`relation` 只記本章明確事實與本章關聯，每章各自成塊。
- `basis`（preview 提出 challenge 而仍選 keep 時才填）：
  - `already_covered`：必須附 `covered_by`，從該區塊現有內容逐字節錄一句，程式會比對；
    引不出來就不是 already_covered。
  - `single_chapter_only`：本章素材形不成跨章綜合。條目自己的累積清單裡已有別章在講同一件事
    時，這個 basis 是假的。
  - `insufficient_evidence`：有欠帳訊號時會被擋（它會把欠帳抹掉）。
  - `standing_debt`：條目本身欠帳（`many_accumulations` 或 `development_blank_with_history`）
    而本章只一句帶過時用。apply 會記進 `util/output/development_debt.json`；日後把主題發展補成
    跨章綜合、填 `development=update`，apply 會自動清除。`python util/link_updates.py debt`
    看目前欠帳。
- `update` 由實際正式區塊 diff 證明。

## §E 短引句裁決

- 常駐閘門（`check_chapter_files` 步驟5 接的 `check_quote_fidelity`）門檻 10 字，4–7 字的偽逐字
  引句完全不驗：自己的措辭套「」、截斷經文補句號、中譯冒充英文原句，幾乎每章都有。
- `--min-chars 2` 誤報偏多、要人工裁決，不能機械刪，所以不降硬閘門門檻，改成必跑一輪並逐條
  寫裁決。來源歸屬、翻譯與轉述是否忠實，仍由 Evidence Reviewer 回到正式來源判定。

## §F 內容勘誤

### 高風險四類的實例

1. **數字**：出25 舊版「照山上的樣式出現七次」，CT 說四次（七次是 KC 講「耶和華曉諭摩西說」的次數）。
2. **全稱詞**（唯一／所有／從不）：出21 舊版「同態復仇法適用於所有人」，三處來源都說不適用於僕人。
3. **來源誤植**：GT 是多家合訂本（丁良才、啟導本、聖經精讀本、雷氏研讀本、串珠、《舊約聖經
   背景註釋》），子來源常被互相搞混或整批誤植給 BH／KC。要確認引句存在的是「文中講的那一家」，
   GT 要細分到子來源。
4. **對照類敘述**（X 法典 vs 以色列、指示 vs 建造）最容易被簡化成錯的。

### P4 的 manual_review 提醒（只提醒不擋 build，人工複核仍是主力）

1. 本章整理行文／表格裡查無出處的拉丁音譯。改 entry_content 之後本章整理若重寫，要整份重查。
2. 引句掛名來源查無、卻在別家 raw 檔逐字找到＝誤植嫌疑。兩邊都查無的引句多半是英文來源的
   中譯，機器不可驗，仍要人工比對。
3. 解經爭議類條目的主題發展／定義被塞進查無出處的解經史（利12／利13：`type=解經爭議` 且
   evidence 描述雙方交鋒時，容易寫出來源沒提的解經史分期）。判準是條目含具名學者／經典／
   分期用語，但該詞在本章正式來源與經文查無出處。

另有一道 error 級護欄：knowledge_nodes 單一清單項用頓號把兩個條目名黏成一項（利11「摩西、
亞倫和他兒子（祭司）」），整項對不上任何條目會被丟棄。判準是整項對不上、拆開後 ≥2 段各自
對得上真實條目；名字本身帶頓號的合法條目不受影響。

### 常見編造的查法（`<book>_<chapter>` 換成本章，例如 joshua_12）

- **查無出處的交叉引註**：每個引註都 grep 四來源，阿拉伯數字、全形冒號兩種寫法都要試：
  `grep -in "來10:14\|來10：14" raw_data/*<book>_<chapter>*`。四檔都沒有＝編造。
- **查無出處的音譯／希伯來字母**：候選名括號、entry definition、本章整理行文三個位置都會犯，
  各自 `grep -in "<拼寫>" raw_data/*<book>_<chapter>*`。
- **假來源標籤**：來源標籤只能是 CT／GT／KC／BH 四家（加 STEP 語言資料）；P4 的
  `_unknown_source_label_review` 會抓全大寫 2–4 字母的假標籤。
- **knowledge_nodes 自由發揮**：每個節點都要對應真實條目（利9 曾出現 80 多個虛構節點）。
  多數會被 P4 移除，但巧合命中既有 alias 的會被改寫成連結、繞過白名單。
- **英文引句沒附中譯**：`grep -in "[a-zA-Z]{20,}" .tmp/第X章/chapter_content.yaml`，逐條看
  「」裡的英文後面是否有（）中譯。
- **GT 子來源誤植**：P4 的 `_gt_subsource_review` 只在文中用《》點名子來源時才有著力點；只寫
  「GT 指出」的要人工細分。

### 修正方式

- `chapter_content.yaml`（organization）與 `entry_content/*.yaml` 才是 source of truth；只改
  `第x章.md`／`link_folder/**.md` 的話，下次 render 會覆蓋回舊內容。
- B 類累積在 `link_updates.yaml`，改完重跑 `link_updates.py apply`。
- 勘誤依據寫在 relation 或 commit 訊息，正文不寫流程／版本註記（`AGENTS.md`「寫作要求」）。

## §G 收尾驗證

- `build_embedding_index.py` 只重嵌新增／變動的條目，通常幾秒。略過它，本章新條目就不在索引裡，
  下一章的候選近鄰報告靜默查不到它們；`check_chapter_files` 會用雜湊比對驗證同步，
  `build_embedding_index.py --check` 可單獨驗、不打網路。
- 全 PASS 的條件見 `scheme.md` §6。
- 閘門常見錯誤：
  - 多數閘門吃「書卷名」不是路徑：`verify_links.py 利未記` 對，傳 `"03 利未記/第13章.md"` 會
    crash。`check_existing_links.py ... --missing` 例外，它要章節 md 路徑。
  - 不要用 `grep -c` 判斷通過：程式 crash 時數到 0 會假裝通過。看 PASS／FAIL 與 exit code。
- 同時修改 `appendix/website/**` 的互動網站時，先在 repo 根目錄跑網站自己的 production build，
  再同步附錄索引：
  ```text
  python appendix/website/build.py --build --deploy-dir .tmp/website-deploy
  python util/build_appendix_links.py
  ```
  `build_appendix_links.py` 動態載入網站 plugin 的 `scan_all_entries()`，只讀已產生的
  `dist/index.html` 與靜態 HTML，不會自行執行 npm。Vite 章節的根目錄 `index.html` 是開發入口，
  附錄連結應指向 `dist/index.html`；部署目錄只供靜態主機發布。靜態 HTML 章節維持原檔案入口。
  plugin 模組若宣告 `BOOK_INDEX_HEADING`（`appendix/website/build.py` 已宣告），同一支程式也會依章號
  順序把該類連結整理進該卷 `全書目錄及綱要.md` 的 `appendix-index:<plugin>` 標記區塊（放在「🎬」
  影片段之前）；該卷沒有入口時清掉舊區塊，目錄頁其餘手寫內容不動。不想進目錄頁就刪掉那個宣告。

## §H check_chapter_files 還驗什麼

- 依步驟順序檢查每步的主要檔案：`source_manifest.md`、`link_candidates.yaml`、
  `candidate_existence.md`、`candidate_similarity.md`、`link_plan.yaml`、`entry_content/*.yaml`、
  `verse_links.yaml`、`chapter_content.yaml`、`quote_adjudication.md`、`第x章.md`、
  `link_updates.yaml`、`util/output/` 的驗證報告，最後以雜湊比對 embedding 索引與條目庫同步。
  停在第一個缺檔處並印出續做指令（缺 `link_plan.yaml`→回步驟3重跑 prompts；缺
  `link_updates.yaml`→回步驟4跑 prepare）。
- **內容涵蓋**：`verse_links.yaml` 有沒有涵蓋 `link_plan.yaml` 自己宣告的經文詞。
  `verse_links_step` 是「輸出檔存在就沿用」，擋在前面的作廢機制只在 `pipeline_state.json` 有
  基線時生效——基線被刪就整套失效，改過 candidates／plan／entry_content 後重跑會靜默沿用舊的
  `verse_links.yaml`（民20：30 個候選只渲染出 4 個內文連結，其他閘門全 PASS，因為它們驗「連出去
  的對不對」，不驗「該連的有沒有連」）。要讓某一步重生，直接刪那一步的輸出檔。
- **作廢機制**比對的是下游真正讀到的那一面：`entry_content` 只跟 plan 的 C 類名單走，
  `chapter_content.yaml` 只跟可連白名單與條目名／aliases 走，`verse_links.yaml` 才吃 plan 全檔
  （surfaces 在裡面）。所以只改 surfaces，或只改條目的定義／主題發展正文，都不會作廢手寫
  payload，直接重跑即可；新增／刪除候選或改動條目 aliases 會作廢下游。`prompts` 跑完會把
  candidates 與 plan 的基線一起前推。
- **未追蹤檔案**：最後掃 git 未追蹤的 `link_folder/**.md`（利3／利4 曾漏 git add 新建條目、
  commit 訊息還寫「新建條目：0個」）。「本章待 git add」的要一併加入；「屬已 commit 章節」的
  是先前漏提交＝FAIL，驗證內容後補提交。

## §I 新建條目與流程加固

- 新建條目前用 `search_wiki_entries` 確認名稱與 aliases 不與既有條目衝突。
- 互文檔名用全形冒號「：」（半形 `:` `?` `\` `/` 在 Windows 是非法字元）。
- 條目 H2 順序依 scheme：定義→按書卷累積→主題發展→相關條目→來源依據。
- 新建條目一次寫齊 payload 必填欄（accumulations、sources）。
- 同一個錯出現第二次，就做成 pipeline 護欄，不逐章人工抓：機械可證的列 error（擋 build），
  啟發式的列 manual_review（提醒不擋）。加護欄前要全庫實測：注入已知真錯抓得到，且 0 誤報。
