# Scripture Pipeline — Agent Instructions

處理本專案（聖經章節知識庫）時，一切工作遵循 `agent_start_prompt.md` 的 8 步驟流程。本檔為全專案通用規則，每步都適用。

## 鐵律（違反即重做）

1. **四來源（CT／GT／KC／BH）全部讀完才動筆寫 candidates 或 organization。** GT 夾帶丁良才、啟導本、精讀本、雷氏研讀本、串珠、《舊約聖經背景註釋》等多家，密度最高，不可跳讀。
2. **內容只能出自 rawdata。** 沒有出處的話不准寫，再合理也不行。包括希伯來文音譯／字母——rawdata 沒給就不能寫，即使那是真實存在的聖經常識。
3. **經文一個字都不能改。** surface 對不上就改 surface，不是改經文。
4. **所有輸出用繁體中文。** 英文來源（KC、BH）引用時譯成繁體中文，保留引號與出處。只有原文用字本身是重點時才以括號附註原文。
5. **勘誤是每章固定動作，不是選做。** 閘門全過只代表結構合法，不代表內容對 rawdata 忠實。commit 前必須逐條複核。

## 每章流程速覽

詳見 `agent_start_prompt.md`，此處只列關鍵指令：

| 步驟 | 動作 | 關鍵指令 |
|------|------|----------|
| 1 | 準備來源 | `python util/build_source_manifest.py 【書名】 X`（不可手寫 manifest） |
| 2 | 建 candidates | 讀完四來源 → 寫 `link_candidates.yaml` → `python util/semantic_lookup.py --candidates 【書名】 X` |
| 3 | 跑 orchestrator | `python util/build_link_index.py` → `python util/run_chapter.py 【書名】 X` |
| 4 | B 類累積 | `python util/link_updates.py prepare 【書名】 X` → 填 yaml → `apply --dry-run` → `apply` |
| 5 | 人工決策點 | 處理 `manual_review` 與 D 類衝突 |
| 6 | 勘誤複核 | 逐條核對四來源（見下方「勘誤複核」完整章節） |
| 7 | 收尾驗證 | `build_fhl_maps.py` → `check_existing_links.py` → `build_link_index.py` → `build_embedding_index.py` → `validate_knowledge_base.py` → `link_quality_check.py 【書名】` → `verify_links.py 【書名】` → `audit_knowledge_base.py --check-due` |
| 8 | 檔案完整性 | `python util/check_chapter_files.py 【書名】 X` → `git status` 確認新建條目全進 staging → commit + push |

---

## 步驟 1：準備來源

- **不可手寫 `source_manifest.md`**。一律用 `python util/build_source_manifest.py 【書名】 X`。
- 歷史教訓：利未記、民數記、申命記三卷曾因 manifest 用裸檔名（無 `raw_data/` 前綴）導致 M3/M6 拿到空來源、模型憑空生成。該 bug 已修復（`parse_manifest` 現容忍裸檔名），但不可再手寫 manifest。
- 新書卷需先在 `_config/source_catalog.json` 補一列（cc_folder／kc／en）。
- 經文已在本地：`raw_scripture/{標準書名}/第{章}.txt`。缺檔即停，回報使用者。
- 補充來源用 `python util/crawl_bible_text.py "{URL}" --output_path raw_data --output_filename "{source}_{book_slug}_{chapter}"`。已存在的 raw_data 檔直接沿用，不加 `--overwrite`。

## 步驟 2：Candidates 規則

### 名稱與分類（兩個會靜默毀資料的坑）

1. **`name` 不可含斜線**（`/`）。斜線在檔名裡是路徑分隔字元，`entry_content/<name>.yaml` 建不出來 → 整鏈靜默失效：surfaces 連不上、knowledge_nodes 對不上被丟掉、累積從未寫入、related_entries 指向它而被移除。三個閘門照過。想涵蓋多個詞用 `surfaces`，不要塞進 `name`。

2. **`type` 只能是 `link_folder/` 底下真實存在的資料夾**：主題、事件、互文、人物、原文、地點、文化、歷史、神學、背景、解經爭議。自創分類（如「祭禮」「儀式」「器具」）會被 resolver 降級為 `D_new_candidate` 並附一句「未知分類：X」——那是 plan 檔裡的一行字，不是錯誤，跑完照樣印「✅ 完成」，下場與斜線名完全相同。祭祀相關歸 `主題`（制度）或 `原文`（術語），器物歸 `主題`／`文化`。

3. **一個候選只對一個條目**。`name` 不可含斜線，想涵蓋多個詞用 `surfaces`。

### 原文類候選的音譯規則

- **括號音譯必須在本章 rawdata 實際出現過**。先 grep 四來源確認拼寫存在：
  ```powershell
  grep -i "<音譯>" raw_data/*<book>_<chapter>*
  ```
  四檔都沒有就是編造，用裸中文名。即使音譯是聖經常識（如 azkarah、tāmîm）也不能寫——鐵律第 2 條。
- 希伯來字母同理，且更嚴：P4 validate 會逐字驗證希伯來字母的出處，查無出處 = error 擋 build。

### 經文用詞對齊

- 逐節核對經文用詞：經文用簡稱而候選名對不上時，宣告 `surfaces`。
- 同詞多義用 `{phrase, verses}` 限定節次（如出26「幔子」v1-13 是幕幔、v31-33 是內幔 → `surfaces: [{phrase: 幔子, verses: [31,32,33]}]`）。

### 語義近鄰報告（必跑）

```powershell
python util/semantic_lookup.py --candidates 【書名】 X
```

報告三種資訊都要看：
- **字面解析預覽**：resolver 實際會把候選對到哪。標「請確認」的多半是 alias 導向不同名條目。
- **⚠（top-1 高分、字面對不上、分類相容）**：與候選同概念 → 改用既有條目名走 B 類累積，不要另建近似重複。
- **候選互查的 ⚠**（本章兩個候選彼此相似 ≥0.8）：考慮合併成一個候選。

### 寫完後自檢

用一行程式列出最終候選數與名稱，跟腦中規劃逐一核對：
```powershell
python -c "import yaml; d=yaml.safe_load(open('.tmp/第X章/link_candidates.yaml',encoding='utf-8')); [print(c['name'], '(', c.get('type',''), ')') for c in d['candidates']]"
```
利7 實例：規劃要放「燔祭」但漏寫，M6 三次重試都因白名單碰壁才發現。

## 步驟 3：跑 Orchestrator

- 開跑前先 test 端點：`python util/model_client.py test`
- 模型端點切換：`python util/model_client.py list|use`
- 不可動 util 程式碼來繞環境問題，用環境變數或 PATH 解決。
- embeddings proxy（localhost:4000）是 repo 外基礎設施；embeddings 突然 404 時查 `C:\Users\andyj_adknr2z\AppData\Local\hermes\litellm\proxy.py` 白名單（搜 `chat/completions", "embeddings"`）。

### 依賴鏈自動作廢

- 改 `link_candidates.yaml` → run_chapter 自動刪 link_plan → entry_content → verse_links → chapter_content 重生。不必手動刪中間檔。
- 改 `entry_content/*.yaml` → 自動刪 verse_links + chapter_content 重生。**注意：這會連帶覆蓋你手動修好的 organization**，修完 entry_content 後要重新檢查 chapter_content。

### M6 白名單機制

- 本章整理（organization）的 wiki-link 只能連到本章 A/B 類既有條目 + C 類本章實建條目。
- 連到清單外的既有條目（即使該條目確實存在於 vault）會被硬擋。
- 跨章背景知識要嘛也列成本章候選，要嘛只能用不帶連結的純文字提及。

## 步驟 4：B 類累積

- `link_updates.yaml` 的 `book` 欄必須是正規書卷名（`利未記`），不可寫資料夾名（`03 利未記`）——後者會生出 `### 03 利未記` 標題，與既有 `### 利未記` 並存互不相認。
- 累積前先讀目標條目完整內容，確認 H2 結構完整：定義→按書卷累積→主題發展→相關條目→來源依據。
- 相關條目只放已存在的條目，不放未來章節才會建的條目（否則 verify_links 報 broken）。
- 順手複查既有條目：若本章累積到的既有條目本身帶著更早期的錯，連同勘誤一併修正，並在 relation 裡註明勘誤依據。
- apply 後重跑必須 0 變更。

## 步驟 5：人工決策點

- 處理 run_chapter 回報的 `manual_review` 項目。
- 處理 `link_plan.yaml` 的 D 類（同名衝突、分類衝突）。D 類不得自動建立或連結。
- 看 `link_plan.yaml` 的 `semantic_hint`：C/D 候選若附上了語義近鄰既有條目，要回頭確認是不是該連到那個既有條目（改走 B 類累積），而非另建近似重複。

## 步驟 6：勘誤複核（每章必做，commit 前最後把關）

閘門全過只代表結構合法，不代表內容對 rawdata 忠實。你必須把新產出的本章整理、新建條目、B 類累積內容，逐條回頭核對四來源原文。

### 高風險四類（優先查）

1. **數字**：出25 舊版「照山上的樣式出現七次」→ CT 說四次（七次是 KC 講「耶和華曉諭摩西說」的次數，被混進來了）。
2. **全稱詞**（唯一／所有／從不／適用於所有人）：出21 舊版「同態復仇法適用於所有人」→ 三處來源都說不適用於僕人。
3. **來源誤植**：模型把 GT 子來源（丁良才／啟導本／背景註釋）互相搞混，或整批誤植給 BH／KC。複核時要確認引句存在的是「模型講的那一家」，GT 尤其要往下細分是丁良才／啟導本／背景註釋哪一段。
4. **對照類敘述**（X 法典 vs 以色列、指示 vs 建造）：最容易被簡化成錯的。

### 模型常見編造（逐條查，含具體 grep 指令）

#### A. 查無出處的交叉引註

模型會編造來源沒出現過的經文引註（來10:14、西1:20、林後8:9 等）。每個引註都要 grep 四來源確認：
```powershell
grep -in "來10:14\|來10：14" raw_data/*<book>_<chapter>*
grep -in "西1:20\|西1：20" raw_data/*<book>_<chapter>*
```
四檔都沒有 → 編造，刪除或替換成 grep 到的正確引註。

#### B. 查無出處的希伯來音譯／字母（三種位置都會犯）

1. **候選名括號**（如「紀念份（azkarah）」）：
   ```powershell
   grep -in "azkarah" raw_data/*<book>_<chapter>*
   ```
   四檔都沒有 → 用裸中文名。

2. **entry definition 的希伯來字母**（如 `מִנְחָה`）：
   ```powershell
   grep -in "מִנְחָה" raw_data/*<book>_<chapter>*
   ```
   四檔都沒有 → 刪除字母，只留音譯（如果音譯有出處）。

3. **chapter_content 自由文字／表格裡的音譯**（如 `*chatta't*`、`*qodesh qodashim*`）：
   ```powershell
   grep -in "chatta" raw_data/*<book>_<chapter>*
   grep -in "qodesh" raw_data/*<book>_<chapter>*
   ```
   四檔都沒有 → 刪除。注意：每次 M6 重新生成都可能在新位置再犯，改完 entry_content 導致 chapter_content 重生後，複核清單要整份重跑。

#### C. 發明不存在的來源標籤

模型可能把 ccbiblestudy.org 網域名和來源標籤搞混，生出「CCB」等假標籤。核對時確認每個來源標籤都是四家之一（CT/GT/KC/BH）。P4 的 `_unknown_source_label_review` 會抓全大寫 2-4 字母的假標籤，但人工複核仍是主力。

#### D. M6 knowledge_nodes 大規模自由發揮

模型可能自行生成超出候選清單十倍以上的假節點（利9 實例：80+ 個虛構條目，含 36 個純 Hebrew 音譯、10 個虛構互文條目、50+ 個自創分類）。每個 knowledge_node 都要確認對應真實條目存在。多數會被 P4 自動剔除，但有些因巧合命中既有 vault 條目的別名而被自動改寫成 wiki-link——這種連結繞過了白名單設計。

#### E. 英文未譯

KC／BH 引句若仍為英文，譯成繁體中文。掃描法：
```powershell
# 在 chapter_content.yaml 和 entry_content/*.yaml 中搜尋英文段落
grep -in "[a-zA-Z]{20,}" .tmp/第X章/chapter_content.yaml
```

#### F. GT 子來源誤植（最隱蔽的坑）

GT 是多家合訂本（丁良才、啟導本、聖經精讀本、雷氏研讀本、串珠、《舊約聖經背景註釋》），模型會把裡面的子來源互相搞混，或整批誤植給 BH。複核時不能只看「引句是否存在於某來源」，要確認引句存在的是「模型講的那一家」。P4 的 `_gt_subsource_review` 只在模型明確用《》點名 GT 子來源時才有著力點；模型常只寫「GT 指出」不點名子來源，那種仍要靠人工複核細分。

### 勘誤修正要改 yaml 源頭，不是 .md

- `chapter_content.yaml`（organization）與 `entry_content/*.yaml`（definition／development）才是 source of truth。
- 只改渲染後的 `第x章.md`／`link_folder/**.md`，下次任何重跑都會被 render 覆蓋回錯的舊內容。
- **改 `entry_content/*.yaml` 會連帶作廢 `chapter_content.yaml`**：run_chapter 偵測到 entry_content 變動就會自動重生 verse_links 與 chapter_content（模型重新生成），手動修好的 organization 會被整段覆蓋。修完 entry_content 後要重新檢查 chapter_content。
- B 類累積在 `link_updates.yaml`，改完要重跑 `link_updates.py apply`（不是 run_chapter）。

### 勘誤要寫進 commit message

不默默改。用 `> [!note]` 標明修正依據。

## 步驟 7：收尾驗證（閘門）

### 閘門指令（全 PASS 才 commit）

```powershell
python util/build_fhl_maps.py
python util/check_existing_links.py "【序號 書名】/第x章.md" --missing
python util/build_link_index.py
python util/build_embedding_index.py          # 必須在 build_link_index.py 之後跑
python util/validate_knowledge_base.py
python util/link_quality_check.py 【書名】
python util/verify_links.py 【書名】
python util/audit_knowledge_base.py --check-due
```

### 閘門常見錯誤

1. **閘門吃「書卷名」不是路徑**：
   - ✅ `verify_links.py 利未記`
   - ❌ `verify_links.py "03 利未記/第13章.md"` → KeyError crash

2. **別用 `grep -c` 判斷通過**：程式 crash 時 grep 數不到關鍵字就回 0，假裝通過。看 `Result: PASS/FAIL` 或檢查 exit code。

3. **`build_embedding_index.py` 必須在 `build_link_index.py` 之後跑**，不可略過——本章新條目沒進索引，下一章候選近鄰報告查不到它們（靜默失效）。

4. **收工前用 `git status` 對照 `check_chapter_files.py` 的未追蹤清單**，確認新建 link_folder 條目全部進了 staging。不可只信 commit 訊息上的數字（利4 實例：訊息寫「新建條目：0個」但實際新建了 9 個）。

## 步驟 8：檔案完整性驗證

```powershell
python util/check_chapter_files.py 【書名】 X
```

依步驟 1-6 的流程順序，逐一檢查每步驟該產生的主要檔案是否存在。一旦某檔缺失，程式會停在第一個缺檔處並印出「該回到哪個動作續做」的具體指令。照該指令補完後，再從那一步依序把後面的流程走完，直到本檢查全數 PASS 才 commit + push。

## 內容格式規範

### 視覺形式（材料決定形狀）

- 對照／清單 → 表格；流程因果 → flowchart；時間 → timeline；階層 → mindmap；對話 → sequenceDiagram
- 散文敘述是主幹（至少一半），表格/callout 是補充，不可反客為主
- mermaid 節點標籤加雙引號（`A["燔祭壇"]`），圖旁必須配散文說明
- YAML 的 organization 一律用 `|` 字面區塊（單引號 scalar 會把 mermaid／表格／callout 全折成一行）

### 排版

- 粗體節制，不可整段包 `**`；`==高亮==` 每段最多一處
- 引句用直接引「」並標對哪一家，不可張冠李戴；某家沒說就不要替他生一個
- 矛盾要並陳不壓平
- 互文節點必須帶小標題：`[[出20：16|出20：16 第九誡不可作假見證]]`，不可裸引用
- 表格內不可放帶別名連結（`[[X|Y]]` 的 `|` 會斷表格）
- 禁 HTML／#標籤／`![[]]`／參考資料清單

### 重複段落只寫差異

如出25-31（指示）vs 出35-40（建造）是同一批東西兩遍，建造段只寫「什麼變了、什麼一字不差照做」。

## 新建條目（C 類）

- 建條目前先 grep 全庫確認 alias 不與既有條目衝突：
  ```powershell
  grep -r "aliases:" link_folder/ | grep "新alias"
  ```
- 互文檔名用全形冒號 `：`（Windows 非法字元：半形 `:` `?` `\` `/`）。
- 嚴格按 scheme H2 順序：定義→按書卷累積→主題發展→相關條目→來源依據。
- 新建條目要一次寫齊 payload 必填欄（accumulations、sources）。
- 檔案改名一律用 `python util/rename_markdown.py <src> <dst> [--dry-run]`（同步全庫 WikiLink）。

## 流程加固原則

同一個錯出現第二次 → 做成護欄修進 pipeline，不逐章人工抓。
- 機械可證 → error 級（擋 build）
- 啟發式 → manual_review 級（提醒不擋）
- 加護欄前必須全庫實測：①注入已知真錯抓得到 ②0 誤報

## 參考檔案

- 完整流程：`agent_start_prompt.md`
- 設計原則：`scheme.md`
- 索引規範：`scheme_index.md`
- 重構指南：`refactor_guidelines.md`
- 設定檔：`_config/` 目錄下各 yaml/json