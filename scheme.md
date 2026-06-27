# Scripture Knowledge Base Scheme

本檔是 `C:\Obsidian\Hermes\scripture\` 的最高規則。所有輸出用繁體中文。不得跳過本檔、驗證流程、資料驅動 link 流程。

核心：每章一個整合型章節主檔；書卷資料夾負責順讀，全域 `link_folder/` 負責跨章累積知識；wiki-link 必須由已收集資料明確觸發，不由 AI 憑感覺建立。

---

## 1. 目錄結構

```text
scripture/
├── scheme.md
├── agent_start_prompt.md
├── crawl_bible_text.py
├── raw_scripture/              # 本地經文
├── raw_data/                   # 網站來源純文字快取
├── _config/bible_books.json
├── build_link_index.py
├── resolve_link_candidates.py
├── check_existing_links.py
├── link_quality_check.py
├── verify_links.py
├── 何西阿書/
│   ├── 全書導論.md
│   ├── 全書綱要.md
│   ├── 第1章.md
│   ├── 第2章.md
│   └── ...
├── 但以理書/
│   ├── 全書導論.md
│   ├── 全書綱要.md
│   ├── 第1章.md
│   └── .tmp/第3章/
│       ├── source_manifest.md
│       ├── link_candidates.md
│       ├── link_plan.md
│       └── link_queue.md       # 僅超長章節需要
├── link_folder/
│   ├── 人物/
│   ├── 地點/
│   ├── 主題/
│   ├── 背景/
│   ├── 歷史/
│   ├── 原文/
│   ├── 文化/
│   ├── 神學/
│   ├── 互文/
│   └── 解經爭議/
    └── _index/link_index.json
```

規則：
- 每卷書一個資料夾；章節檔只用 `第x章.md`，不得再建立 `經文/`、`註解/`、`拾穗/`、`解說/` 等平行章節資料夾。
- `link_folder/` 是全域共用，可依資料自然新增分類；新增分類必須適合跨章／跨卷累積，禁止為單一零散詞開新資料夾。
- 同一條目只允許一個主分類；其他性質用 `secondary_types` 表示，不得在多個 folder 重複建檔。

---

## 2. 資料來源與 raw text 快取

### 2.1 經文

經文固定讀取本地檔：

```text
raw_scripture/{標準書卷名}/第{章}.txt
```

`{標準書卷名}` 必須與 `_config/bible_books.json` 一致。經文檔每行一節；除非使用者明確要求，經文不透過 `crawl_bible_text.py` 抓取。

### 2.2 補充資料

目前主要來源：
1. ccbiblestudy.org
	1. 註解（CT）
	2. 拾穗（GT）
2. KingComments（KC）
3. BibleHub Study（BH）
4. 使用者指定且可轉成純文字的其他網站

補充資料**不得直接讀網頁後整理**。必須先用 `crawl_bible_text.py` 轉成 `raw_data/*.txt`，再讀本地 raw text。

標準命令：

```text
python crawl_bible_text.py "{URL}" --output_path raw_data --output_filename "{source}_{book_slug}_{chapter}"
```

例：

```text
python crawl_bible_text.py "https://biblehub.com/study/daniel/3.htm" --output_path raw_data --output_filename "biblehub_study_daniel_3"
```

結果：`raw_data/biblehub_study_daniel_3.txt`。檔名不用加 `.txt`；已存在時不覆蓋，只有確認舊檔錯誤或使用者要求時才加 `--overwrite`。

建議命名：

```text
raw_data/biblehub_study_daniel_3.txt
raw_data/kingcomments_daniel_3.txt
raw_data/ccbiblestudy_CT_daniel_3.txt
raw_data/ccbiblestudy_GT_daniel_3.txt
```

### 2.3 URL 模式與限制

只可使用已確認 URL；來源優先順序：使用者指定 URL、既有 `source_manifest.md`、既有可靠記錄、來源目錄頁。禁止硬猜 URL。

```text
ccbiblestudy CT/GT:
https://www.ccbiblestudy.org/{Old|New}%20Testament/{卷代碼}/{卷號}{CT|GT}{章2位}.htm
例：27Daniel/27CT03.htm, 27Daniel/27GT03.htm, 28Hosea/28CT01.htm, 28Hosea/28GT01.htm, 01Gen/01CT01.htm, 40Matt/40CT01.htm

KingComments:
https://www.kingcomments.com/en/bible-studies/{KC_slug}/{章}
例：Dan/3, Hos/1, Gen/1, 1Sam/1, Song/1

BibleHub Study:
https://biblehub.com/study/{book_slug}/{章}.htm
例：daniel/3.htm, hosea/1.htm, 1_samuel/1.htm
```

`卷代碼`、`KC_slug`、`book_slug` 必須以實際網站或既有可靠記錄為準。

### 2.4 source_manifest.md

每章建立：

```text
【書名】/.tmp/第x章/source_manifest.md
```

格式：

```md
# 但以理書 第3章 source manifest

| 來源 | 類型 | URL | raw_data 檔案 | 狀態 |
|---|---|---|---|---|
| BibleHub Study | BH | https://biblehub.com/study/daniel/3.htm | raw_data/biblehub_study_daniel_3.txt | OK |
| KingComments | KC | ... | raw_data/kingcomments_daniel_3.txt | OK |
| ccbiblestudy | CT | ... | raw_data/ccbiblestudy_CT_daniel_3.txt | OK |
| ccbiblestudy | GT | ... | raw_data/ccbiblestudy_GT_daniel_3.txt | OK |
```

狀態可用：`OK`、`MISSING`、`FAILED`、`INVALID`、`SKIPPED`。失敗來源可記錄，但不可假裝已使用。

### 2.5 raw text 有效性

讀取 `raw_data/*.txt` 後必須檢查。以下不得作為 link 或內容依據：404、目錄頁、網站錯誤頁、純導覽列、頁首頁尾、廣告、重複版權、亂碼、HTML 殘留、與本章無關、過短且無可整理資料。無效來源只記錄在 manifest。

---

## 3. 章節主檔格式

檔名：`【書名】/第x章.md`。

```md
# 何西阿書 第1章

1. 當[[烏西亞]]、[[約坦]]、[[亞哈斯]]、[[希西家]]作[[猶大]]王，[[約阿施]]的兒子[[耶羅波安二世|耶羅波安]]作[[以色列]]王的時候，[[耶和華的話臨到]][[備利]]的兒子[[何西阿]]。
2. [[耶和華]]初次與[[何西阿]]說話，對他說：「你去娶淫婦為妻，也收那從淫亂所生的兒女；因為這地大行[[屬靈淫亂|淫亂]]，離棄[[耶和華]]。」
3. ...

---

## 本章知識節點

### 主題

- [[屬靈淫亂]]
- [[婚姻作為盟約隱喻]]
- [[審判後的復興]]

### 歷史／背景

- [[北國以色列滅亡]]
- [[耶戶王朝]]
- [[亞述入侵]]

### 原文／名字

- [[耶斯列的雙關]]
- [[羅路哈瑪]]
- [[羅阿米]]

### 互文

- [[非我民到神的兒子]]
- [[外邦人得救]]

---

## 本章整理
```

規則：
- 經文保留完整內容，wiki-link 直接加在經文上。
- 「本章知識節點」只列來源補充後顯明、值得跨章累積的核心節點；不要重列所有經文 link。
- 「本章整理」整合來源重點，不大量搬運 CT/GT/KC/BH 全文。
- 過多資料應沉澱到 `link_folder/` 或暫存在 `.tmp/`，章節主檔不是資料倉庫。

---

## 4. wiki-link 建立規則

### 4.1 資料驅動原則

建立任何 link 前先問：

```text
此 link 是否由目前經文或已收集 raw text 明確觸發？
此 link 是否有資料可支撐本地 markdown 條目？
```

任一答案為否，就不建立。

可建立條件：
- 經文本身明確出現，且是人物、地點、國家、群體、書卷、重要事件。
- raw text 明確解釋該詞、概念、背景、原文、象徵、互文、爭議、神學或歷史意義。
- 來源提供足夠內容，可整理到 `link_folder/`。
- 該概念與本章解釋直接相關。

禁止建立：
- AI 覺得可能重要，但來源未提。
- 只靠一般神學常識聯想。
- 沒有可整理內容或只能寫空泛 stub。
- 普通名詞且來源未賦予特殊意義。
- 為了讓知識庫看起來豐富。
- 需要另行外搜才有內容。

### 4.2 link target 與 alias

核心：`link target = 條目檔名`，`alias = 經文原詞`。

```md
[[條目完整名稱|經文原詞]]
[[條目完整名稱]]       # 經文原詞與條目名完全相同時可用
```

例：

```md
[[神的話（創造媒介）|神說]]
[[形像與樣式|形像]]
[[屬靈淫亂|淫亂]]
```

禁止用短詞誤當 target，例如來源討論的是「神的話（創造媒介）」，不得建 `[[神說]]`。

### 4.3 普通詞與主題詞

普通詞不直接 link。若來源明確賦予神學、象徵、審判、盟約、救恩等意義，link 完整概念短語：

```md
不要：[[弓]]        可：[[折斷以色列的弓]]
不要：[[海沙]]      可：[[亞伯拉罕之約的海沙應許]]
不要：[[淫亂]]      可：[[屬靈淫亂]]
```

主題型 link 如 `[[神的公義與慈愛]]`、`[[耶和華的話臨到]]`，也必須由本章來源明確討論才可建立。

### 4.4 書卷、人物、章節連結

- 書卷與人物同名要分清：`[[何西阿]]` 是人物，`[[何西阿書]]` 是書卷；禁止 `[[何西阿]]書`。
- 跨章／跨卷引用不可寫 `[[第1章]]`，必須寫完整路徑：

```md
[[何西阿書/第1章|何西阿書 第1章]]
[[但以理書/第3章|但以理書 第3章]]
```

- 合法但尚未建立的聖經章節引用交給 `verify_links.py` 分為 `PENDING_SCRIPTURE_REFS`，不得為未來章節預建空檔。

---

## 5. link candidate → link plan 流程

正式寫入 wiki-link 前，必須完成：

```text
raw_scripture + 有效 raw_data
→ link_candidates.md
→ build_link_index.py
→ resolve_link_candidates.py
→ link_plan.md
→ 章節主檔 wiki-link
→ link_folder 建立／更新
```

### 5.1 build_link_index.py

每章處理前執行：

```text
python3 build_link_index.py
```

掃描 `link_folder/`，產生 `link_folder/_index/link_index.json`。每個條目讀取 YAML frontmatter：

```yaml
type: 主分類
secondary_types: [文化, 歷史]
aliases: [別名1, 別名2]
status: formal | candidate
```

Index 必須支援：條目名 → path/type/aliases/status；alias → alias_of。Aliases 是比對核心。

### 5.2 link_candidates.md

位置：

```text
【書名】/.tmp/第x章/link_candidates.md
```

只放由經文與有效 raw text 明確觸發的候選節點；不得放 AI 憑感覺認為重要的詞。

### 5.3 resolve_link_candidates.py

執行：

```text
python3 resolve_link_candidates.py 【書名】 X
```

`X` 一律為阿拉伯數字，不加「第／章」。例：

```text
python3 resolve_link_candidates.py 創世記 13
```

輸出：

```text
【書名】/.tmp/第x章/link_plan.md
```

link_plan 類別：

| 類別 | 動作 |
|---|---|
| A | 已存在，直接使用 |
| B | 已存在，補充本章資料 |
| C | 不存在，資料足夠，建正式條目 |
| D | 不存在，資料不足，建候選條目或待分類 |
| E | 不應建立 link，改純文字 |

比對優先序：完全同名 → YAML aliases → 同義詞表 → fuzzy 候選 → 同名不同分類 → 書卷/人物衝突 → alias 格式確認。歧義不得自動新建，放 D 或 E。

### 5.4 link_plan 不是資料來源

`link_plan.md` 只決定「用哪個條目、建在哪裡、A-E 類別、由哪些來源觸發」。寫章節內容或條目內容時必須回到：`raw_data/*.txt`、`source_manifest.md`、`.tmp/` 暫存、章節主檔；不得根據 link_plan 直接編內容。

---

## 6. link_folder 條目規則

### 6.1 分類

條目依主要性質放入一個主分類；其他性質放 `secondary_types`。分類不確定先放 `link_folder/_待分類/`，每卷完成後清理。

### 6.2 正式條目模板

```md
---
type: 主題
secondary_types: [神學]
aliases: []
status: formal
source_scope: collected_only
---

# 條目名稱

## 定義
（保護區）

## 核心摘要
（保護區）

## 按書卷累積

### 但以理書
#### 第3章
- 觸發來源：BH/KC/CT/GT
- 本章重點：
- 與本章關聯：

## 主題發展
（保護區）

## 相關條目

## 來源依據

## 待確認事項
```

Agent 只能在以下累積區新增：`按書卷累積`、`相關條目`、`來源依據`、`待確認事項`。除非使用者明確要求，不得大改 `定義`、`核心摘要`、`主題發展`。

### 6.3 候選條目模板

```md
---
type: 主題
secondary_types: []
aliases: []
status: candidate
created_from: 但以理書 第3章
source_scope: collected_only
---

# 條目名稱

## 類型

## 觸發來源
- [[但以理書/第3章|但以理書 第3章]]：

## 目前資料
- 根據目前已收集資料整理。

## 相關條目

## 待補充
- 目前資料不足，日後再擴充或合併。
```

候選條目不能變成垃圾堆；每卷完成後檢查：多次引用者升級、資料足夠者升級、重複者合併、分類錯者移動、長期無支撐者保留或移除 link。

### 6.4 更新既有條目

既有條目也必須由本章資料觸發才更新。可補：觸發來源、聖經出現、與本章關聯、神學意義、相關條目、待確認事項。不得加入本章來源未提內容，不得重複貼相同內容。

### 6.5 防止條目爆炸

新條目內出現的新詞，不自動生成第二層、第三層條目。每個新 link 仍須通過資料驅動、必要性、已存在檔案、普通詞、候選條目等判斷。

---

## 7. 驗證規則

最終順序：

```text
python3 check_existing_links.py 【書名】/第x章.md --missing
python3 build_link_index.py
python3 link_quality_check.py 【書名】
python3 verify_links.py 【書名】
```

### 7.1 verify_links.py

Found links 分類：

| 類別 | 說明 | blocking |
|---|---|---|
| BROKEN_LINKS | 目標不存在於 link_folder、不是章節檔、不是合法聖經引用 | 是 |
| PENDING_SCRIPTURE_REFS | 書卷存在且章數合法，但本地章節未建 | 否 |
| INVALID_SCRIPTURE_REFS | 書卷存在但章數超出範圍 | 是 |
| UNKNOWN_LINKS | 非 link_folder、非章節檔、非合法聖經引用 | 是 |

PASS 條件：`BROKEN_LINKS=0`、`INVALID_SCRIPTURE_REFS=0`、`UNKNOWN_LINKS=0`。`PENDING_SCRIPTURE_REFS` 可存在。

合法未來章節引用例：`[[啟示錄13]]`、`[[撒母耳記下5]]`、`[[啟示錄/第13章|啟示錄13章]]`。章數以 `_config/bible_books.json` 判斷，別名在 `BOOK_ALIASES` 維護。

### 7.2 link_quality_check.py

檢查書卷/人物錯連、alias 格式錯誤、短詞過度 link、`[[何西阿]]書` 類後綴錯連、同 alias 指向多 target、target 不在 index、冗長 alias 等。

PASS 條件：`CRITICAL=0`。WARNING 必須回報並人工判斷是否修。

---

## 8. 一般章節流程

1. 讀取 `scheme.md`。
2. 確認書卷與章節。
3. 檢查書卷資料夾、現有章節檔、完成狀態；已完成且通過驗證者不重做。
4. 讀取經文：`raw_scripture/{書名}/第{章}.txt`。
5. 建立 `【書名】/.tmp/第x章/`。
6. 確認 CT/GT/KC/BH/使用者指定來源 URL；不可硬猜。
7. 對每個已確認 URL 執行 `crawl_bible_text.py` 產生或沿用 `raw_data/*.txt`。
8. 建立／更新 `source_manifest.md`。
9. 讀取並檢查有效 raw text。
10. 執行 `python3 build_link_index.py`。
11. 根據經文與有效 raw text 建 `link_candidates.md`。
12. 執行 `python3 resolve_link_candidates.py 【書名】 X` 產生 `link_plan.md`。
13. 根據 `link_plan.md` 寫 `第x章.md`：經文 + wiki-link + 本章知識節點 + 本章整理。
14. 根據 `link_plan.md` 建立／更新 link_folder：B 補充、C 正式、D 候選、E 不連。
15. 執行最終驗證順序，修到 verify 無 blocking、quality 無 critical。
16. git status → commit → push。
17. 回報完成狀態、更新檔案、link、條目、驗證結果、commit hash、待確認事項。

---

## 9. 超長章節流程

符合任一條件即超長：經文超過 60 節；任一 raw text 超過 60KB；來源合計估計超過 100KB；Agent 判斷 context 可能爆。

超長章節三階段：

### 9.1 來源暫存

1. 讀完整經文並建立章節骨架。
2. 建 `.tmp/第x章/`。
3. 確認 URL，用 `crawl_bible_text.py` 產生完整 `raw_data/*.txt`。
4. 建 `source_manifest.md`。
5. 檢查 raw text；無效來源不得進後續。
6. 依自然段落切分有效來源：`001-008_CT.md`、`001-008_GT.md`、`001-008_KC.md`、`001-008_BH.md`。
7. 第一階段只做暫存與切分；不得整合寫主檔或更新 link_folder。

分段優先按文體自然結構：詩歌詩節／字母段，家譜世代，敘事事件，預言神諭，福音事件，書信論證；無明顯結構才每 10–20 節切。

### 9.2 分段整合

逐段讀同一範圍所有來源暫存檔，跨來源比較後整合進章節主檔，並更新 `link_queue.md`。整合必須由暫存資料支撐，不得過度推論。

### 9.3 link queue 處理

所有分段完成後，彙整 `link_queue.md` → `link_candidates.md` → `resolve_link_candidates.py` → `link_plan.md`，再統一寫 wiki-link 與更新 link_folder。最後完整跑 quality + verify。

---

## 10. commit 與回報

只有以下條件全部成立才能 commit + push：

```text
verify_links.py: BROKEN_LINKS=0, INVALID_SCRIPTURE_REFS=0, UNKNOWN_LINKS=0
link_quality_check.py: CRITICAL=0
所有新建 link_folder 條目有 YAML frontmatter
所有新建／更新內容有觸發來源
```

建議 commit message：

```text
Add Daniel chapter 3 integrated study note
Update Daniel chapter 3 links and knowledge nodes
```

完成回報格式：

```md
## 完成回報

- 本次完成章節：
- 建立／更新檔案：
- 新增 wiki-link：
- 新增 link folder 條目：
- 新增候選條目：
- 補充既有條目：
- verify_links.py 結果：
- link_quality_check.py 結果：
- git commit hash：
- 待確認事項：
```

---

## 11. 禁止事項

嚴禁：
1. 跳過 `scheme.md`、`build_link_index.py`、`resolve_link_candidates.py`、`check_existing_links.py`、`link_quality_check.py`、`verify_links.py`。
2. 使用 gbrain 寫入。
3. 補充資料跳過 `crawl_bible_text.py`，直接用網頁內容整理。
4. 未確認 URL 就硬猜；抓到 404、目錄、空內容、亂碼、導覽列仍硬用。
5. raw_data 已存在且未確認錯誤時任意 `--overwrite`。
6. 未產生 `link_plan.md` 就把 wiki-link 寫入章節主檔。
7. 根據 `link_plan.md` 直接編內容而不回 raw text。
8. 只靠 AI 記憶、常識、感覺建立 link。
9. 建立無本地 markdown 檔案閉合的 wiki-link。
10. 建立資料不足、只有 2–3 行的薄弱 stub。
11. 普通名詞大量誤連；短詞當 target；書卷錯連人物；章節寫 `[[第1章]]`。
12. 同一條目在多個 link folder 重複建立。
13. 為單一零散概念開新 link folder。
14. 為未來章節預建空章節檔。
15. 把 CT/GT/KC/BH 大量全文塞進章節主檔。
16. 已完成且通過驗證的章節未檢查就重做。
17. 驗證未通過就 commit。
18. 超長章節一次塞滿 context、跳過分段整合、跳過最終整章 verify/quality。

---

## 12. 最短總原則

```text
先讀 scheme → 讀本地經文 → 確認 URL → crawl 成 raw_data → 檢查 raw text
→ build index → link_candidates → resolve → link_plan
→ 寫章節主檔 → 更新 link_folder → quality + verify 到 PASS → commit
```

所有 link 必須由已收集資料觸發；所有內容必須能回到 raw text 或本章經文；所有 wiki-link 必須閉合到本地 markdown；所有正式條目的保護區不可被每章任務亂改。
