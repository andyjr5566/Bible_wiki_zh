# Scripture Knowledge Base Scheme

本檔是 `C:\Obsidian\Hermes\scripture\` 的最高規則。所有輸出用繁體中文。不得跳過本檔、驗證流程、資料驅動 link 流程。

核心：每章一個整合型章節主檔；書卷資料夾負責順讀，全域 `link_folder/` 負責跨章累積知識；wiki-link 必須由已收集資料明確觸發，不由 AI 憑感覺建立。

---

## 1. 目錄結構

```text
scripture/
├── scheme.md
├── agent_start_prompt.md
├── raw_scripture/              # 本地經文
├── raw_data/                   # 網站來源純文字快取
├── _config/
│   ├── bible_books.json
│   ├── link_conflict_resolutions.yaml
│   └── link_homonyms.yaml
├── util/
│   ├── crawl_bible_text.py
│   ├── clean_bible_html.py
│   ├── build_link_index.py
│   ├── resolve_link_candidates.py
│   ├── link_updates.py
│   ├── normalize_format.py
│   ├── rename_markdown.py
│   ├── validate_knowledge_base.py
│   ├── audit_knowledge_base.py
│   ├── check_existing_links.py
│   ├── link_quality_check.py
│   ├── verify_links.py
│   ├── tests/
│   └── output/
│       ├── link_index.json
│       ├── verify_report.json
│       ├── verify_result.txt
│       ├── link_quality_report.json
│       └── audits/
├── .github/workflows/knowledge-base.yml
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
```

規則：
- 根目錄只保留專案文件、設定與經文／知識資料；所有工具 script 放在 `util/`，其索引、驗證與巡檢輸出放在 `util/output/`。
- `raw_data/` 是來源快取，不是工具報告，因此維持原位。
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

`{標準書卷名}` 必須與 `_config/bible_books.json` 一致。經文檔每行一節；除非使用者明確要求，經文不透過 `util/crawl_bible_text.py` 抓取。

### 2.2 補充資料

目前主要來源：
1. ccbiblestudy.org
	1. 註解（CT）
	2. 拾穗（GT）
2. KingComments（KC）
3. BibleHub Study（BH）
4. 使用者指定且可轉成純文字的其他網站

補充資料**不得直接讀網頁後整理**。必須先用 `util/crawl_bible_text.py` 轉成 `raw_data/*.txt`，再讀本地 raw text。

標準命令：

```text
python util/crawl_bible_text.py "{URL}" --output_path raw_data --output_filename "{source}_{book_slug}_{chapter}"
```

例：

```text
python util/crawl_bible_text.py "https://biblehub.com/study/daniel/3.htm" --output_path raw_data --output_filename "biblehub_study_daniel_3"
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

### 2.6 FHL 聖經地圖

FHL 地圖原始資料固定放在 `appendix/fhl_maps/`，其中包含 `metadata.json`、
`images/` 與 `texts/`。地圖筆記、總索引與經文對照一律由程式產生：

```powershell
python util/build_fhl_maps.py
```

規則：
- 每張地圖各有一個 `maps/{gid}.md`，整合圖片、解說、相關經文、相關地圖及來源。
- 經文引用只在對應章節檔已存在時建立 wiki-link；未完成章節保留普通文字。
- 每次新增或完成章節後執行 `python util/build_fhl_maps.py`。
- 章內「相關地圖」固定放在經文正文之後、第一條分隔線之前，由 `fhl-map-links` 標記管理。
- `fhl-map-manual` 標記以下為人工補充區，程式重建時必須保留。
- 可用 `python util/build_fhl_maps.py --check` 驗證是否需要同步。
- 圖片格式由 `appendix/fhl_maps/image_optimization.json` 決定；不得手工改寫副檔名。
- 批次壓縮使用 `python util/optimize_fhl_map_images.py`；JPEG 固定採
  `yuvj444p`，只有容量至少縮小 10% 才取代 GIF。

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

## 參考資料
<url>
<url>
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

- 合法但尚未建立的聖經章節引用交給 `util/verify_links.py` 分為 `PENDING_SCRIPTURE_REFS`，不得為未來章節預建空檔。

### 4.5 合法同名詞與消歧義

`folder` 只表示主分類，不能用來區分全庫同名 target。不同實體共用同一表面名稱時，全部正式檔名都必須加入最小且穩定的限定詞：

```md
[[示劍（城）|示劍]]
[[示劍（哈抹之子）|示劍]]
[[示劍人（城中居民）|示劍人]]
```

規則：
- 不同實體必須分檔；人物、地點、族群不得因同名而合併。
- 同一實體兼具多種性質時只建一檔，以主分類加 `secondary_types` 表示；不得誤當同名詞拆檔。
- 同名組所有正式檔名都要加限定詞，包含最常見者；不得讓其中一個獨占裸名。
- 限定詞優先使用可長期辨識身分的關係、職分或地點類型，例如「哈抹之子」、「城」；不得使用容易失效的流水號。
- 經文原詞只放在 WikiLink alias 顯示位置，不得把歧義裸名加入任何條目的 YAML `aliases`。
- 合法同名組登記於 `_config/link_homonyms.yaml`。`resolve_link_candidates.py` 遇到登記裸名必須列入 D 類人工判斷；`validate_knowledge_base.py` 必須阻擋裸 WikiLink。
- `_config/link_conflict_resolutions.yaml` 只處理待清理的錯誤重複或 alias 衝突，不得用來替合法同名實體選定單一勝者。
- 資料尚不足時不得為可能存在的同名人物或族群預建 stub。

---

## 5. link candidate → link plan 流程

正式寫入 wiki-link 前，必須完成：

```text
raw_scripture + 有效 raw_data
→ link_candidates.md
→ util/build_link_index.py
→ util/resolve_link_candidates.py
→ link_plan.md
→ 章節主檔 wiki-link
→ link_folder 建立／更新
```

### 5.1 util/build_link_index.py

每章處理前執行：

```text
python util/build_link_index.py
```

掃描 `link_folder/`，產生 `util/output/link_index.json`。每個條目讀取 YAML frontmatter：

```yaml
type: 主分類
secondary_types: [文化, 歷史]
aliases: [別名1, 別名2]
status: formal | candidate
```

Index 必須支援：條目名 → path/type/aliases/status；alias → alias_of。Aliases 是比對核心。

索引穩定性規則：
- `secondary_types` 只表示次分類，**不得**建立為 alias。
- 同名條目、alias 多重指向、alias 與正式名稱衝突不得由掃描順序靜默決定。
- 合法同名實體必須使用帶限定詞的全域唯一正式名稱，並登記在 `_config/link_homonyms.yaml`。
- 已人工確認但尚待全卷清理的舊衝突，記錄在 `_config/link_conflict_resolutions.yaml`；未登記的新衝突必須阻擋建索引。
- 名稱正規化只可處理 Unicode 與空白差異，不得刪除括號內容或其他可能帶有語義的文字。
- CI 使用 `python util/build_link_index.py --check` 確認索引可重現且已是最新。

### 5.2 link_candidates.md

位置：

```text
【書名】/.tmp/第x章/link_candidates.md
```

只放由經文與有效 raw text 明確觸發的候選節點；不得放 AI 憑感覺認為重要的詞。

正式格式以第 26 章的精簡格式為準：

```md
# 創世記 第26章 — Link Candidates

## 人物
- 以撒 → 人物
- 利百加 → 人物

## 地點
- 基拉耳 → 地點
- 別是巴 → 地點

## 神學主題
- 亞伯拉罕之約 → 神學
- 神的同在 → 神學
```

每一列的欄位固定為：

```text
- 條目完整名稱 → 主分類
```

- `##` 標題用於人類閱讀與分組，可以是「神學主題」、「名字含義」等整理名稱，不必等於實際主分類。
- `→` 右側只放主分類，必須使用 `link_folder/` 的合法分類名稱，不得把經節、說明或括號註解混入分類。
- 每個候選必須使用 `- ` 項目符號。空行與 `#` 標題不視為候選。
- 候選必須由經文或有效 raw text 觸發，但通常不必在每一列重複列出來源，以節省 token；詳細依據由 `source_manifest.md`、raw text 與後續整理保留。
- 候選名稱中禁止使用 `/`、`\`、`<`、`>`、`：`、`"`、`|`、`?`、`*` 等檔案系統不安全字元

候選名稱可能有歧義、分類理由不直觀，或需要留下稽核線索時，才選擇性加入 `— 觸發依據`：

```md
- 天梯 → 神學 — CT/GT/KC/BH 討論基督預表與天地交通
- 埃色（相爭） → 原文 — 名字含義
```

解析時，`→` 與 `—` 必須分開：`→` 後是主分類，`—` 後是選填說明。不得寫成沒有 `→ 主分類` 的 `條目名稱 — 說明`。

### 5.3 util/resolve_link_candidates.py

執行：

```text
python util/resolve_link_candidates.py 【書名】 X
```

`X` 一律為阿拉伯數字，不加「第／章」。例：

```text
python util/resolve_link_candidates.py 創世記 13
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

## util/resolve_link_candidates.py 比對邏輯

`util/resolve_link_candidates.py` 必須將本章 link_candidates.md 與 `util/output/link_index.json` 比對。

比對優先順序：
1. **完全同名檔案** — 條目名稱完全匹配 index key
2. **YAML aliases 完全命中** — candidate 名稱命中某條目的 aliases 列表
3. **常見同義詞命中** — 預設同義詞表比對
4. **fuzzy match 候選** — 相似但非精確匹配，放入 D 類
5. **不同資料夾中的同名條目** — 若候選名稱與某 index key 相同但分類不同，使用既有條目
6. **書卷名與人物名衝突** — 檢查 `PERSON_TO_BOOK` 映射
7. **經文原詞與條目完整名稱不同** — 確認 alias 格式正確

附加規則：
- 精確比對必須先使用完整候選名稱；例如「全能的神（El Shaddai）」不可先刪除括號再搜尋。
- 命中既有條目後，必須核對候選主分類是否等於既有 `type`，或包含於其 `secondary_types`。
- 分類不相容時不得自動連結或新建同名條目，必須列入 D 類人工判斷。
- A 類表示既有條目已含「同一書卷＋同一章」累積；B 類表示條目存在但尚未累積本章。不得只搜尋「第x章」字串。
### Alias 比對規則
若命中 alias，必須指向 alias 所屬的主條目檔案，不可另建新條目。
例如：
```yaml
# link_folder/主題/屬靈淫亂.md
aliases:
  - 屬靈姦淫
  - 拜偶像如淫亂
  - 以色列的淫亂
```
若本章 candidate 出現「屬靈姦淫」，應解析為：
```md
[[屬靈淫亂|屬靈姦淫]]
```
不可新增：
```text
link_folder/主題/屬靈姦淫.md
```
### 歧義處理
若有歧義（同一名稱指向多個既有條目，或書卷人物衝突），
不要自動建立新條目，放入 link_plan 的 D 類（候選條目）或 E 類（不建立）。
### 5.4 link_plan 不是資料來源

`link_plan.md` 只決定「用哪個條目、建在哪裡、A-E 類別、由哪些來源觸發」。寫章節內容或條目內容時必須回到：`raw_data/*.txt`、`source_manifest.md`、`.tmp/` 暫存、章節主檔；不得根據 link_plan 直接編內容。

### 5.5 link_plan 回報節省 token

Agent 回報 `link_plan.md` 時，不得把完整 `link_plan.md` 貼回對話。預設只回報：
- D 類待人工判斷項目。
- C 類新增正式條目的摘要與數量。
- 分類衝突、alias 歧義、書卷／人物同名等需要使用者決策的點。

若沒有 D 類或衝突，只需簡短說明 resolver 已產生、C/B 類數量與下一步動作。需要完整細節時，讀本地 `【書名】/.tmp/第x章/link_plan.md`，不要在對話中展開。

---

## 6. link_folder 條目規則

不要吝嗇文字使用量，越詳細越好，把資料的細節精隨整理出來
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

## 按書卷累積

### 但以理書
<!-- accumulation:但以理書:3:start -->
#### 第3章
- 本章重點：
- 與本章關聯：
<!-- accumulation:但以理書:3:end -->

## 主題發展
（保護區）

## 相關條目

## 來源依據
<url>

```

`定義` 同時承擔條目辨識與核心摘要，不另設內容容易重複的「核心摘要」區。Agent 只能在以下累積區新增：`按書卷累積`、`相關條目`、`來源依據`。除非使用者明確要求，不得大改 `定義`、`主題發展`。

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

既有條目也必須由本章資料觸發才更新。可補：聖經出現、與本章關聯、神學意義、相關條目。不得加入本章來源未提內容，不得重複貼相同內容。

### 6.5 B 類安全累積流程

B 類條目預設使用：

```text
python util/link_updates.py prepare 【書名】 X
```

產生：

```text
【書名】/.tmp/第x章/link_updates.yaml
```

Agent 必須回到本章經文與有效 raw text，逐項填入：
- `summary`：本章重點
- `relation`：與本章關聯

`sources`、`source_files` 等內部追蹤欄位不得寫入 `link_folder` 條目；條目只保留有閱讀價值的內容，不顯示 raw_data 檔案路徑。

先預覽，再套用：

```text
python util/link_updates.py apply 【書名】/.tmp/第x章/link_updates.yaml --dry-run
python util/link_updates.py apply 【書名】/.tmp/第x章/link_updates.yaml
```

累積區使用穩定標記：

```md
### 創世記
<!-- accumulation:創世記:28:start -->
#### 第28章
...
<!-- accumulation:創世記:28:end -->
```

規則：
- 同一書卷只保留一個 `### 書卷名`；各章以 `#### 第N章` 表示，依正典書卷順序及阿拉伯章號排序。
- 每個章次區塊都必須位於所屬書卷標題下並由穩定標記包住；不得把章次追加到 `主題發展`、`相關條目` 或 `來源依據`。
- 工具只負責安全寫入，內容仍由經文與 raw text 驅動。
- 重跑必須冪等，不得重複新增同一章。
- 工具只可改累積標記區，不得改正式條目的保護區。
- manifest 缺少摘要或關聯時不得套用。

### 6.6 防止條目爆炸

新條目內出現的新詞，不自動生成第二層、第三層條目。每個新 link 仍須通過資料驅動、必要性、已存在檔案、普通詞、候選條目等判斷。

不得設定每章正式條目數量上限，也不得因人物看似普通而先驗排除；是否建立條目只由已收集資料、跨章累積需要與內容充分性決定。

### 6.7 Markdown 安全改名

任何既有 Markdown 檔案改名或移動時，一律使用：

```text
python util/rename_markdown.py "目前檔案路徑.md" "改名後檔案路徑.md" --dry-run
python util/rename_markdown.py "目前檔案路徑.md" "改名後檔案路徑.md"
```

工具會先確認目標檔名未與全庫任何 Markdown 檔案同名，再同步更新所有指向原檔案的 Obsidian WikiLink target；alias、標題錨點與嵌入語法必須保留。撞名或連結指向不明時必須拒絕執行，不得直接用檔案系統命令改名。

---

## 7. 驗證規則

最終順序：

```text
python util/check_existing_links.py 【書名】/第x章.md --missing
python util/build_link_index.py
python util/validate_knowledge_base.py
python util/link_quality_check.py 【書名】
python util/verify_links.py 【書名】
python util/audit_knowledge_base.py --check-due
```

`util/check_existing_links.py --missing` 必須核對書卷與章數；有缺漏時回傳非零狀態。

`util/validate_knowledge_base.py` 檢查 YAML、分類、alias、重複累積標記、合法同名詞、歧義裸 WikiLink、正式條目結構與保護區。既有技術債可列 warning；本次新增或更新檔案若違規則為 blocking。

既有成品需要統一格式時，使用：

```text
python util/normalize_format.py --scope all --dry-run
python util/normalize_format.py --scope all
python util/normalize_format.py --scope all --dry-run --verify-base HEAD
```

正規化必須區分章節主檔、正式條目與候選條目三種模板；不得把三者改成相同格式。套用後第二次 dry-run 必須為 0，正文保存驗證、schema、quality 與 verify 必須全部通過。

單元測試：

```text
python -m unittest discover -s util/tests -v
```

CI 每次 push／pull request 必須執行單元測試、index check、結構驗證、quality、verify 與巡檢到期檢查。

### 7.1 util/verify_links.py

Found links 分類：

| 類別 | 說明 | blocking |
|---|---|---|
| BROKEN_LINKS | 目標不存在於 link_folder、不是章節檔、不是合法聖經引用 | 是 |
| PENDING_SCRIPTURE_REFS | 書卷存在且章數合法，但本地章節未建 | 否 |
| INVALID_SCRIPTURE_REFS | 書卷存在但章數超出範圍 | 是 |
| UNKNOWN_LINKS | 非 link_folder、非章節檔、非合法聖經引用 | 是 |

PASS 條件：`BROKEN_LINKS=0`、`INVALID_SCRIPTURE_REFS=0`、`UNKNOWN_LINKS=0`。`PENDING_SCRIPTURE_REFS` 可存在。

合法未來章節引用例：`[[啟示錄13]]`、`[[撒母耳記下5]]`、`[[啟示錄/第13章|啟示錄13章]]`。章數以 `_config/bible_books.json` 判斷，別名在 `BOOK_ALIASES` 維護。

### 7.2 util/link_quality_check.py

檢查書卷/人物錯連、alias 格式錯誤、短詞過度 link、`[[何西阿]]書` 類後綴錯連、同 alias 指向多 target、target 不在 index、冗長 alias 等。

PASS 條件：`CRITICAL=0`。WARNING 必須回報並人工判斷是否修。

### 7.3 驗證回報節省 token

驗證工具的完整輸出不得預設貼回對話。成功時只回報結論欄位：
- `validate_knowledge_base.py`：errors / warnings 數量。
- `link_quality_check.py`：critical / warning 數量。
- `verify_links.py`：broken / invalid / unknown 數量；`pending scripture refs` 只回報數量，不列清單。
- `audit_knowledge_base.py --check-due`：PASS / FAIL。

只有驗證失敗、需要修正時，才展開 blocking 錯誤細節；非 blocking 的長清單與報告路徑不必完整貼出。最終完成回報也遵守此摘要格式。

---

## 8. 一般章節流程

1. 讀取 `scheme.md`。
2. 確認書卷與章節。
3. 檢查書卷資料夾、現有章節檔、完成狀態；已完成且通過驗證者不重做。
4. 讀取經文：`raw_scripture/{書名}/第{章}.txt`。
5. 建立 `【書名】/.tmp/第x章/`。
6. 確認 CT/GT/KC/BH/使用者指定來源 URL；不可硬猜。
7. 對每個已確認 URL 執行 `util/crawl_bible_text.py` 產生或沿用 `raw_data/*.txt`。
8. 建立／更新 `source_manifest.md`。
9. 讀取並檢查有效 raw text。
10. 執行 `python util/build_link_index.py`。
11. 根據經文與有效 raw text 建 `link_candidates.md`。
12. 執行 `python util/resolve_link_candidates.py 【書名】 X` 產生 `link_plan.md`。
13. 根據 `link_plan.md` 寫 `第x章.md`：經文 + wiki-link + 本章知識節點 + 本章整理。
14. 根據 `link_plan.md` 建立／更新 link_folder：B 預設經 `link_updates.yaml` 安全累積；C 正式、D 人工判斷、E 不連。
15. 對 B 類執行 `util/link_updates.py prepare`，回到來源填寫 manifest，dry-run 後 apply；重跑確認 0 個重複變更。
16. 執行最終驗證順序，修到結構驗證無 error、verify 無 blocking、quality 無 critical。
17. 執行 `util/audit_knowledge_base.py --check-due`；到達巡檢里程碑時先產生並人工檢查報告。
18. git status → commit → push；由 CI 作最終守門。
19. 回報完成狀態、更新檔案、link、條目、驗證結果、commit hash。

---

## 9. 超長章節流程

符合任一條件即超長：經文超過 60 節；任一 raw text 超過 120KB；來源合計估計超過 250KB；Agent 判斷 context 可能爆。

超長章節三階段：

### 9.1 來源暫存

1. 讀完整經文並建立章節骨架。
2. 建 `.tmp/第x章/`。
3. 確認 URL，用 `util/crawl_bible_text.py` 產生完整 `raw_data/*.txt`。
4. 建 `source_manifest.md`。
5. 檢查 raw text；無效來源不得進後續。
6. 依自然段落切分有效來源：`001-008_CT.md`、`001-008_GT.md`、`001-008_KC.md`、`001-008_BH.md`。
7. 第一階段只做暫存與切分；不得整合寫主檔或更新 link_folder。

分段優先按文體自然結構：詩歌詩節／字母段，家譜世代，敘事事件，預言神諭，福音事件，書信論證；無明顯結構才每 20 節切。

### 9.2 分段整合

逐段讀同一範圍所有來源暫存檔，跨來源比較後整合進章節主檔，並更新 `link_queue.md`。整合必須由暫存資料支撐，不得過度推論。

### 9.3 link queue 處理

所有分段完成後，彙整 `link_queue.md` → `link_candidates.md` → `util/resolve_link_candidates.py` → `link_plan.md`，再統一寫 wiki-link 與更新 link_folder。最後完整跑 quality + verify。

---

## 10. commit 與回報

只有以下條件全部成立才能 commit + push：

```text
util/verify_links.py: BROKEN_LINKS=0, INVALID_SCRIPTURE_REFS=0, UNKNOWN_LINKS=0
util/link_quality_check.py: CRITICAL=0
util/validate_knowledge_base.py: ERRORS=0
util/audit_knowledge_base.py --check-due: PASS
所有新建 link_folder 條目有 YAML frontmatter
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
```

---

## 11. 禁止事項

嚴禁：
1. 跳過 `scheme.md`、`util/build_link_index.py`、`util/resolve_link_candidates.py`、`util/check_existing_links.py`、`util/link_quality_check.py`、`util/verify_links.py`。
2. 使用 gbrain 寫入。
3. 補充資料跳過 `util/crawl_bible_text.py`，直接用網頁內容整理。
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
19. 把 `secondary_types` 當 alias，或讓同名／alias 衝突由掃描順序自動決定。
20. 以刪除括號內容的方式正規化候選名稱。
21. 只用「第x章」字串判斷條目已累積，而未核對書卷。
22. 手工大量附加 B 類資料而跳過可用的 `link_updates.yaml` 安全流程。

---

## 12. 定期維護

### 12.1 每 10 章全庫巡檢

預設每累計完成 10 章執行：

```text
python util/audit_knowledge_base.py --all --checkpoint 10
```

巡檢 alias、候選條目、同名與重複概念、孤立條目、分類及來源問題。報告只提供人工決策線索，不自動刪除、合併、移動或升級。

### 12.2 每卷完成巡檢

完成一卷後執行：

```text
python util/audit_knowledge_base.py --book 【書名】
```

必須人工檢查 alias、一卷內候選條目、重複概念、分類與來源完整度，再決定保留、升級或合併。新正式條目數量不設上限，所有決定仍由資料驅動。

`_config/maintenance_policy.yaml` 記錄巡檢間隔與導入基準；`util/audit_knowledge_base.py --check-due` 阻止漏掉應執行的巡檢。

---

## 13. 最短總原則

```text
先讀 scheme → 讀本地經文 → 確認 URL → crawl 成 raw_data → 檢查 raw text
→ build index → link_candidates → resolve → link_plan
→ 寫章節主檔 → link_updates 安全累積／更新 link_folder
→ schema + quality + verify + audit due 到 PASS → commit → CI → push 到 repo
```

所有 link 必須由已收集資料觸發；所有內容必須能回到 raw text 或本章經文；所有 wiki-link 必須閉合到本地 markdown；所有正式條目的保護區不可被每章任務亂改。
