# Agent Start Prompt

處理書卷章節時，流程由程式主導（`util/run_chapter.py`），你只負責「準備輸入、填內容、處理人工決策點」。設計原則與決策記錄見 `scheme.md`；所有輸出用繁體中文。

## 每章流程

1. **準備來源**（章節的 `.tmp` 資料夾：`【序號 書名】/.tmp/第x章/`）
   - 經文已在本地：`raw_scripture/{標準書名}/第{章}.txt`（缺檔即停，回報使用者）。
   - 每個補充來源（ccbiblestudy CT/GT、KingComments、BibleHub Study）用既有記錄或目錄頁確認 URL（禁止硬猜），執行：
     `python util/crawl_bible_text.py "{URL}" --output_path raw_data --output_filename "{source}_{book_slug}_{chapter}"`
     已存在的 raw_data 檔直接沿用，不加 `--overwrite`。
   - **不要手寫 `source_manifest.md`**，改用：`python util/build_source_manifest.py 【書名】 X`（位址規則在 `_config/source_catalog.json`，新書卷先補一列 cc_folder／kc／en）。它依規則產生四來源、raw_data 路徑一律帶 `raw_data/` 前綴，並依檔案是否存在標 OK／缺檔。標「缺檔」就先 `crawl_bible_text.py` 補爬。
   - run_chapter 的 M3／M6 生成前會檢查來源讀得到；manifest 宣告 OK 卻讀不到任何 raw_data 檔就丟 `SourceError` 中止（防止空來源生成）。照訊息修 manifest 或補 raw_data 再重跑。

2. **建 link_candidates.yaml**（唯一由你判斷「哪些詞值得成為知識節點」的步驟）
   - 依 `_config/schemas/link_candidates.schema.json`：`{book, chapter, candidates: [{name, type, evidence?, surfaces?}]}`。
   - 只放經文或有效 raw text 明確觸發的候選；分類用 `link_folder/` 現有資料夾名。
   - **一個候選只能對一個條目，`name` 不可含斜線**。斜線在檔名裡是路徑分隔字元，`entry_content/<name>.yaml` 建不出來，該候選必定同時：surfaces 連不上任何節、knowledge_nodes 對不上而被丟掉、本章累積永遠不寫入、別的條目 related_entries 指向它而被移除——而且全部靜默，三個閘門照過。想涵蓋多個詞用 `surfaces`，不要塞進 `name`。（validate 會擋）
   - **`type` 只能是 `link_folder/` 底下真的存在的資料夾**：主題、事件、互文、人物、原文、地點、文化、歷史、神學、背景、解經爭議。自己造一個看起來很合理的分類（利10 的「祭禮」、民9 的「儀式」、民10 的「器具」）會靜默失效——resolver 認不得，只把候選降級成 `D_new_candidate` 並附一句 note「未知分類：X」，那是 plan 檔裡的一行字，不是錯誤，跑完照樣印「✅ 完成」，下場與斜線名完全相同。祭祀相關的歸 `主題`（制度）或 `原文`（術語），器物歸 `主題`／`文化`。（validate 會擋）
   - **逐節核對經文用詞**：程式自動比對候選名、條目全名、括號前裸名與 aliases；經文用這些都對不上的簡稱時（「桌子」→陳設餅桌子），為該候選宣告 `surfaces: [桌子]`。同詞在本章多義用 `{phrase, verses}` 限定節次（出26「幔子」v1-13 是幕幔、v31-33 是內幔 → `surfaces: [{phrase: 幔子, verses: [31,32,33]}]`）。
   - **原文類候選名的括號音譯必須是本章來源實際出現過的拼寫**（先 `grep -i` raw_data 確認）；來源沒給音譯就用裸中文名，不可憑聖經工具書常識補配（利2「紀念份（azkarah）」實例：來源只給英文 memorial portion）。希伯來字母寫法同理，且更嚴：P4 validate 對候選檔／entry_content／chapter_content 逐字驗證希伯來字母的出處，查無出處＝error 擋 build（全庫實測抓到創47/出28-30/利1 共 18 筆歷史真陽性、0 誤報）；本章新建原文類名稱的拉丁音譯查無出處＝manual_review 提醒（拼寫變體無法機械排除）。
   - **候選寫齊後跑語義近鄰報告**（候選定稿前必經，check_chapter_files 會驗報告存在）：
     `python util/semantic_lookup.py --candidates 【書名】 X`
     程式把每個候選的「名稱＋分類＋evidence＋surfaces」合成富查詢、一次批量比對全庫索引，寫報告到 `.tmp/第x章/candidate_similarity.md`。報告三種資訊都要看：
     - **字面解析預覽**：resolver 實際會把候選對到哪（同名／裸名／alias／新建）。標「請確認」的多半是 alias 導向不同名條目——alias 登記錯誤會把候選靜默導去錯的條目（實例：安密巴 aliases 誤含以實各谷），這裡是唯一的事前攔截點。
     - **對全庫的 ⚠／ⓘ**：⚠（top-1 高分、字面對不上、分類相容）→ 與候選**同概念**（措辭不同、意思相同）就把候選名改成該既有條目名（resolver 會歸 A/B 走累積），不要另建近似重複；確為不同概念則照建。ⓘ（top-1 高分但分類不相容）→ 常是跨分類的同實體（火柱雲柱[主題]→雲柱火柱[歷史]），確認後連分類一起改用既有條目的。標「resolver 可自動對上」的近鄰不用處理。
     - **候選互查的 ⚠**（本章兩個候選彼此相似 ≥0.8）：新章的條目彼此都還不在索引裡，「兩個候選其實同概念」只有互查抓得到——考慮合併成一個候選（另一個詞用 surfaces 涵蓋），或確認確為兩事再照建。
     報告是分類輔助，不是硬規則；evidence 寫得越具體（含經文引句），近鄰越準。
   - 資料驅動判準見 `scheme.md` §3；語義近鄰索引見 `scheme.md` §3.5。

3. **跑 orchestrator**（結構、渲染、驗證全由程式處理）
   ```text
   python util/build_link_index.py
   python util/run_chapter.py 【書名】 X
   ```
   程式會：解析候選（A–E 類）→ 批量請模型填條目 payload → 程式化標注經文 wiki-link → 模型填本章整理 → 渲染全部 markdown → 結構驗證。模型端點用 `python util/model_client.py list|use|test` 檢查或切換。
   - **本章整理（organization）的 wiki-link 有白名單限制**：只能連到本章 `link_plan.yaml` 的 A／B 類既有條目，或本章實際建出的 C 類條目；連到 vault 裡真實存在、但不在本章候選清單內的其他條目一律被擋（錯誤：「wiki-link 目標不在本章可連清單」），模型會反覆重試到放棄。想在本章整理提到清單外的既有概念，要嘛把它也列成本章候選（走 B 類累積），要嘛只能用不帶連結的純文字提及，不要嘗試連結。目標若是白名單條目的合法 alias（如 [[鹽約]]→立約的鹽），程式會自動改寫成 [[全名|原詞]] 再驗，不再退回模型重試。
   - **M3 的 alias 撞名不再硬失敗**：模型配的 alias 撞上既有／同批條目時（利2「素祭」配「禮物」實例），程式直接剔除該 alias 並記 manual_review「已自動移除（僅通知）」，不再把整個條目退回模型重做——實測錯誤回饋重試兩輪模型照配不誤，只會白燒呼叫。

4. **B 類累積**（既有條目補本章資料）
   ```text
   python util/link_updates.py prepare 【書名】 X
   ```
   回到經文與有效 raw text 填 `link_updates.yaml` 的 `summary`／`relation`，然後：
   ```text
   python util/link_updates.py apply 【書名】 X --dry-run
   python util/link_updates.py apply 【書名】 X
   ```
   重跑 apply 必須 0 變更。

5. **處理人工決策點**：run_chapter 回報的 `manual_review` 項目，與 `link_plan.yaml` 的 D 類（同名衝突、分類衝突）。D 類不得自動建立或連結；判斷後修 candidates 或人工建檔再續跑（run_chapter 可斷點續跑，已完成的步驟不重做）。
   - **看 `link_plan.yaml` 的 `semantic_hint`**：C（新建）與 D（待判斷）候選若程式附上了語義近鄰既有條目（措辭不同、意思相同者），要回頭確認這個候選是不是其實該連到那個既有條目（改走 B 類累積），而非另建近似重複。這是附註線索、不是自動判定；索引或 embedding 端點不可用時該欄位不出現，流程照跑。門檻與原理見 `scheme.md` §3.5。

6. **模型產出後的勘誤複核（run_chapter／link_updates 跑完、commit 前必做）**：`run_chapter.py` 的 M3（entry_content）與 M6（chapter_content 本章整理）、以及 `link_updates.py` 填的 summary／relation，都是模型依 prompt 一次生成，不是人工逐句核對過的——**閘門全過只代表結構合法，不代表內容對 rawdata 忠實**。你必須把新產出的本章整理、新建條目、B 類累積內容，逐條回頭核對四來源原文：
   - 抓法同 §「內容勘誤」四類高風險：模型是否把某來源沒說的話講成是它說的（來源誤植）、把「常見」講成「罕見」或反過來（全稱詞／方向性誤讀）、引了 rawdata 沒有出現過的經文交叉引註（憑常識腦補書卷章節）、或編出聽起來合理但查無出處的格言式總結句。
   - 發現有誤：**source of truth 是 `.tmp/第x章/` 裡的 yaml，不是渲染出來的 markdown**。改 `chapter_content.yaml`（本章整理）或 `entry_content/*.yaml`（新建條目，注意是 `definition`／`development` 欄，不是 `.md` 的段落）裡的文字後，重跑 `python util/run_chapter.py 【書名】 X` 讓 render 重新產出 markdown——**只改渲染後的 `第x章.md`／`link_folder/**.md` 而不改 yaml，下次任何重跑都會被 render 覆蓋回錯的舊內容**（實測踩過：申4 鐵爐條目只改了 `.md` 沒改 yaml，重跑就打回原形）。唯一例外是 `link_updates.yaml` 的 B 類累積——它是 `link_updates.py apply` 寫進既有條目 `.md`，改完 yaml 要重跑 `apply`（不是 run_chapter）。
   - `run_chapter.py` 已會在改動 `link_candidates.yaml` 時**自動作廢並重生下游**（link_plan／entry_content／verse_links／chapter_content），不必再手動刪中間檔；但改 `entry_content/*.yaml`／`chapter_content.yaml` 本身後，直接重跑即可讓 render 帶出新內容。
   - **改 `entry_content/*.yaml` 會連帶作廢 `chapter_content.yaml`**：即使只是修一兩句勘誤，`run_chapter.py` 偵測到 entry_content 變動就會自動作廢並重新生成 `verse_links.yaml` 與 `chapter_content.yaml`——包含你已經手動改好的本章整理，也會被模型重新生成的版本整段覆蓋掉（利1實測踩過：改一個 entry_content 的錯誤引註，手動修好的 organization 被整段換掉兩次）。修完 entry_content 後，要重新檢查（甚至可能要重寫或重新複核）`chapter_content.yaml`，不能假設它沒受影響。
   - 順手複查既有條目：本章若累積到的既有條目本身帶著更早期的錯（例如某地名被錯記成同音異義的另一地名），連同勘誤一併修正，並在 relation 裡註明勘誤依據，不要默默改。
   - 這一步做完才進入下一步收尾驗證；驗證閘門不會幫你抓這類語意錯誤。

7. **收尾驗證與提交**
   ```text
   python util/build_fhl_maps.py
   python util/check_existing_links.py 【序號 書名】/第x章.md --missing
   python util/build_link_index.py
   python util/build_embedding_index.py          # 增量更新語義索引（本章新條目要進索引，下一章才查得到）
   python util/validate_knowledge_base.py
   python util/link_quality_check.py 【書名】
   python util/verify_links.py 【書名】
   python util/audit_knowledge_base.py --check-due
   ```
   全 PASS（條件見 `scheme.md` §6）才 commit + push；回報只列結論數字與 D 類決策，不貼完整報告。
   `build_embedding_index.py` 必須在 `build_link_index.py` 之後跑：它只重嵌新增／變動的條目（沿用其餘），耗時通常幾秒。**這步不可略過**——本章新條目沒進索引，下一章的候選近鄰報告就查不到它們，而且是靜默失效；步驟7 的 check_chapter_files 會用雜湊比對驗證索引同步（`build_embedding_index.py --check` 可單獨驗，不打網路）。

8. **檔案完整性驗證**（commit 前的最後把關）
   ```text
   python util/check_chapter_files.py 【書名】 X
   ```
   依上述 1–6 的流程順序，逐一檢查每步驟該產生的主要檔案是否存在（`source_manifest.md`、
   `link_candidates.yaml`、`candidate_similarity.md`、`link_plan.yaml`、`entry_content/*.yaml`、
   `verse_links.yaml`、`chapter_content.yaml`、`第x章.md`、`link_updates.yaml`、
   `util/output/` 下的驗證報告），最後以雜湊比對驗證 embedding 語義索引與條目庫同步。
   一旦某檔缺失，程式會停在第一個缺檔處並印出「該回到哪個動作續做」的具體指令
   （例：缺 `link_plan.yaml` → 回步驟3重跑 `run_chapter.py`；缺 `link_updates.yaml`
   → 回步驟4跑 `link_updates.py prepare`）；照該指令補完後，再從那一步依序把後面
   的流程走完，直到本檢查全數 PASS 才 commit + push。

## 行為邊界（內容層，程式無法代勞）

- 一切內容由已收集資料驅動：candidates、summary/relation、條目敘述都必須能對回經文或有效 raw text；來源未提的不寫，不憑神學常識外推。
- **run_chapter／link_updates 產出後，agent 必須以四來源為基準逐條複核，不可假設模型一次生成的內容已經對** ——見步驟6。這不是選做，是每章都要做的固定動作。
- **英文來源（KingComments、BibleHub）引用時要譯成繁體中文**，不可整段貼英文原文——本檔開頭已訂「所有輸出用繁體中文」。譯文仍要保留引號與出處（KC：「燔祭一切的價值，就彷彿轉到了他、就是獻祭者身上。」），不要因為要翻譯就退回「KC 指出…」的摘要體。只有在原文用字本身就是重點時（如原文區分 'to burn' 與 'to offer up in smoke'）才以括號附註原文。
- 不假裝無效來源有效；不為湊條目而亂搜薄弱資料。
- 檔案改名一律用 `python util/rename_markdown.py <src> <dst> [--dry-run]`（會同步全庫 WikiLink）。
- 已完成且驗證通過的章節不重做。
