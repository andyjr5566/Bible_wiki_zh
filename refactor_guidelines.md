# 聖經書卷內容製作流程「程式主導、模型輔助」重構指導原則

> 本文件是交給執行 agent 的最高指導原則，不含完整實作。
> 執行時以本文件為準；與 `scheme.md`、`agent_start_prompt.md` 現行內容衝突處，代表該處是本次重構要改掉的對象。

## Context（背景與問題診斷）

現行流程由 AI agent 讀取 `agent_start_prompt.md`（32 步 checklist + 27 條禁止事項）與 `scheme.md`（883 行，混合目錄規則、資料格式、模板、流程、驗證規則、禁止清單），然後由模型**自由撰寫整份 markdown 成品**（章節主檔、link_folder 條目）。格式合規完全依賴模型自律，違規只能靠事後驗證工具發現。這是「章節／條目架構經常跳脫規則」的根本原因。

**關鍵觀察**：repo 內已存在正確答案的原型——`util/link_updates.py` 的 `prepare → 模型填 YAML → dry-run → apply` 流程。程式生成骨架（title/path），模型只填 `summary`/`relation` 兩個內容欄位，程式冪等地寫入標記區塊。B 類條目累積因此幾乎不出格式問題。**本重構的核心就是把這個模式推廣到章節主檔與新條目。**

---

## 零、六條最高指導原則

1. **模型不碰結構，程式不碰內容。** 模型的輸出永遠是「資料」（YAML/JSON 欄位值），永遠不是最終 markdown。最終 markdown 一律由 render 程式從模板+資料生成。模型手寫的 markdown 檔案數量目標為零。
2. **每個模型呼叫：單一任務、最小輸入、結構化輸出、可機器驗證、可重試。** 不再有「一個 agent session 跑完 32 步」；每個內容任務是獨立呼叫，只餵它需要的經文段落與 raw text 片段。
3. **驗證左移。** 在 payload（YAML/JSON）層用 schema 擋掉錯誤並自動重試，而不是在成品 markdown 層事後修補。程式生成的結構天生合規，成品驗證只需檢查內容層問題。
4. **規則二分：能寫成 schema／程式檢查的，就從 prompt 移除；留在 prompt 的只剩內容判斷類規則。** 一條規則若同時出現在 prompt 與程式裡，以程式為準並從 prompt 刪除。
5. **判斷題變選擇題。** 需要模型裁量之處（D 類處置、raw text 有效性、分類歸屬），給 enum 選項 + 理由欄位，不給開放式決策。
6. **每一步有明確輸入檔／輸出檔，冪等、可斷點續跑。** orchestrator 依 `.tmp/第x章/` 內的檔案存在狀態決定從哪步繼續，重跑不產生重複變更（`link_updates.py` 已示範此原則）。

---

## 一、架構與內容分離的設計方案

### 1.1 三層架構

```text
┌─ 編排層（程式）orchestrator ──────────────────────────────┐
│  run_chapter.py：把現在的 32 步 checklist 收進程式，        │
│  依序執行；只在「內容任務」節點呼叫模型                       │
├─ 資料層（模型填寫）payloads ─────────────────────────────┤
│  .tmp/第x章/ 內的 YAML/JSON 中介檔，每種有 JSON Schema：    │
│    source_validity.yaml   raw text 有效性判定               │
│    link_candidates.yaml   候選節點（取代手寫 .md）           │
│    verse_links.yaml       經文 wiki-link 標注               │
│    chapter_content.yaml   知識節點篩選 + 本章整理             │
│    entry_content/*.yaml   每個 C/D 類新條目一檔              │
│    link_updates.yaml      （既有，不變）                     │
├─ 呈現層（程式）renderers ────────────────────────────────┤
│  render_chapter.py：經文 + verse_links + chapter_content    │
│                     → 第x章.md（含固定 H2 骨架）             │
│  render_entry.py：entry_content.yaml → 正式/候選條目 .md    │
│                   （frontmatter、H2 順序、accumulation 標記  │
│                    全由程式產生）                             │
└──────────────────────────────────────────────────────────┘
```

模板（現在內嵌在 `scheme.md` §3、§6.2、§6.3）移到 `_templates/`，只給 render 程式使用；**模型永遠不看模板**，因此不可能寫錯模板。

### 1.2 Payload schema 範本

**`verse_links.yaml`**（經文 wiki-link 標注——模型只指出「哪節、哪個詞、連到哪」，套用由程式做）：

```yaml
# schema: _config/schemas/verse_links.schema.json
book: 出埃及記
chapter: 26
links:
  - verse: 1                # int, 必須 ≤ 本章節數（程式驗證）
    phrase: 基路伯           # 必須是該節經文的子字串（程式驗證）
    target: 基路伯（keruv）  # 必須存在於 link_plan 的 A/B/C 類（程式驗證）
    occurrence: 1            # 該節第幾次出現，預設 1
```

render 程式將 `phrase` 替換為 `[[target|phrase]]`（target 與 phrase 相同時輸出 `[[target]]`）。alias 格式規則（scheme §4.2）從此不可能違反——程式生成的一定合規。

**`entry_content.yaml`**（C 類新條目——欄位即模板槽位）：

```yaml
# schema: _config/schemas/entry_content.schema.json
name: 施恩座（kapporet）
type: 原文                        # enum: link_folder 現有分類
secondary_types: [神學]
aliases: [施恩座]
status: formal                    # enum: formal | candidate
definition: |
  （模型填寫，僅純文字與合法 wiki-link；程式檢查其中的 [[...]]）
accumulations:
  - book: 出埃及記
    chapter: 26
    summary: ...
    relation: ...
related_entries: [法櫃（aron）, 至聖所]   # 每項必須存在或同批建立（程式驗證）
sources:
  - https://biblehub.com/study/exodus/26.htm
```

`render_entry.py` 據此產出完全符合 §6.2/§6.3 模板的 markdown：H2 順序、必填區塊、accumulation 標記由程式排版。「H2 順序錯」「保護區被改」「模板混用」三類漂移從結構上消失。

**`chapter_content.yaml`**（本章知識節點 + 本章整理）：

```yaml
book: 出埃及記
chapter: 26
knowledge_nodes:                  # key 必須是章節主檔允許的分組
  主題: [會幕作神同在的居所]
  原文／名字: [幔子（parokhet）]
  互文: [來10：19-20]
summary: |
  （本章整理正文，模型撰寫）
references:
  - https://...
```

### 1.3 既有工具的角色變化

| 工具 | 變化 |
|---|---|
| `link_updates.py` | 不變；它就是全流程要複製的模式 |
| `resolve_link_candidates.py` | 輸入改讀 `link_candidates.yaml`（或同時支援舊 .md）；輸出 `link_plan` 增加機器可讀版 `link_plan.yaml`，供後續程式與模型呼叫直接消費 |
| `validate_knowledge_base.py` 等驗證工具 | 保留為最終守門，但預期常態全綠——結構違規已在 payload 層被擋 |
| `normalize_format.py` | 過渡期用於遷移既有成品；長期由 render 程式取代其存在意義 |
| 新增 | `render_chapter.py`、`render_entry.py`、`run_chapter.py`（orchestrator）、`_config/schemas/*.json` |

---

## 二、降低模型跳脫規則的方法

### 2.1 漂移原因分析（對照現行流程）

| # | 原因 | 現行流程中的表現 |
|---|---|---|
| 1 | **指令稀釋**：一次載入 32 步 + 883 行規則，越後面的步驟注意力越弱 | 第 19–20 步（寫主檔、更新條目）恰好在長 context 深處執行，最容易出錯 |
| 2 | **結構與內容同時生成**：格式是模型「順便」產生的，不是被強制的 | 手寫整份章節主檔／條目 markdown |
| 3 | **禁止清單無機器強制**：27+22 條禁止事項全靠自律 | 違規只有跑完驗證才發現，此時 context 已污染，修補又引入新漂移 |
| 4 | **模糊判斷詞**：「值得跨章累積」「資料足夠」「薄弱 stub」 | 模型擴張解釋，每章標準不一 |
| 5 | **單一長 session**：規則漂移隨 context 長度惡化 | 一章一個大 session，重試與修錯讓 context 更亂 |
| 6 | **範例干擾**：規則中的範例是但以理／何西阿 | 處理出埃及記時模仿範例勝過遵守規則；規則衝突時無優先序 |

### 2.2 對策（依效果排序）

1. **結構化輸出取代自由 markdown**（治本）：所有模型輸出走 JSON Schema 約束（API 的 structured output / tool-use forced schema，或 Claude Code Agent SDK 的 StructuredOutput）。模型「無法」輸出不合 schema 的東西。
2. **schema 驗證 + 自動重試迴圈**：程式收到 payload 先跑 schema 與語義檢查（phrase 是否為經文子字串、target 是否在 link_plan 內、分類是否合法 enum）。不合格時把**具體錯誤訊息**連同原輸出回給模型重試，上限 3 次，超過則標記人工處理。
3. **最小 context 原則**：每個呼叫只給該任務需要的資料。填「施恩座」條目時，給的是 link_plan 中該條目的觸發來源 + 從 raw text 摘出的相關段落，**不是**整份 scheme + 四份完整 raw text。
4. **逐條目、逐段處理**：一個 C 類條目一次呼叫；經文 wiki-link 標注每 10–20 節一批。呼叫之間無共享 context，前一項的錯誤不會傳染。
5. **判斷題選擇題化**：例如 raw text 有效性任務輸出 `{status: OK|INVALID|IRRELEVANT, reason: string}`；D 類處置輸出 `{action: create_candidate|link_existing|skip, reason}`。
6. **每種 payload 附 1–2 個黃金範例（few-shot）**：放在 `_templates/examples/`，由程式注入 prompt，與規則分離、隨任務更換書卷以免範例干擾。
7. **模糊詞量化**：「資料足夠」→「至少 2 個來源提及，或單一來源 ≥ 3 句實質說明」；「薄弱 stub」→「definition < 80 字且 accumulation 為空」。量化後移入程式檢查。

### 2.3 內容任務 prompt 範本（step-scoped，由 orchestrator 注入）

```text
你是聖經研經資料整理員。本次唯一任務：為條目「{name}」（分類：{type}）填寫內容。

【輸入】
1. 觸發經文（出埃及記 26 章，節錄）：{verses}
2. 相關來源摘錄：{source_excerpts}   ← 程式從 raw_data 依關鍵詞切出的段落

【規則】（僅內容層規則，結構由程式處理）
- 所有陳述必須能對應到上述輸入；輸入未提及的內容不得寫入。
- definition 需完整說明該詞的原文、字義與本章用法，不吝嗇篇幅。
- related_entries 只能從此清單選擇：{allowed_entries}

【輸出】
只輸出符合下列 schema 的 YAML，不輸出任何其他文字：
{schema}

【範例】
{golden_example}
```

注意：這個 prompt **不含** 32 步流程、不含目錄結構、不含驗證命令——那些都不再是模型的事。

---

## 三、`scheme.md` 與 `agent_start_prompt.md` 的重劃

### 3.1 現況缺漏

- `scheme.md` 五種身分混居：人讀原則、機器格式規範、操作手冊、模板庫、禁止清單。模型每次全文載入，多數內容與當下任務無關（→ 指令稀釋）。
- `agent_start_prompt.md` 是流程引擎的偽裝：32 步含大量純機械步驟（跑命令、建資料夾、檢查檔案存在），這些交給模型執行本身就是漂移源——模型可能跳步、換序、自創變體。
- 兩檔規則互相重複（raw text 原則、禁止清單各出現兩次），且無「衝突時以何者為準」的優先序。

### 3.2 目標職責分工

| 檔案 | 職責 | 讀者 |
|---|---|---|
| `_config/schemas/*.json` | 全部資料結構定義（payload schema、分類 enum、檔名規則） | 程式（驗證）、模型（經 prompt 注入片段） |
| `_templates/*.md` + `_templates/examples/` | markdown 模板與黃金範例 | render 程式 |
| `util/run_chapter.py` | 流程本身（現 32 步）＋每步的 prompt 組裝 | 程式 |
| `scheme.md` | 縮減為人讀的設計原則與決策記錄：為什麼資料驅動、為什麼同名要限定詞、A–E 類語義。指向 schema 與 orchestrator，不再重複其內容 | 人、維護者 |
| `agent_start_prompt.md` | 退化為入口說明：「執行 `python util/run_chapter.py 【書名】 X`，處理程式回報的人工決策點」＋內容任務的行為邊界（資料驅動、不外推）。目標 < 50 行 | 啟動用 agent |

**規則遷移判準**（逐條處理現有 27+22 條禁止事項）：
- 可程式強制 → 寫進 orchestrator／schema／validator，從 prompt 刪除（估 80%：跳步類、格式類、命令類、覆蓋類）。
- 純內容判斷 → 留在對應內容任務的 step-scoped prompt（估 20%：資料驅動、不憑感覺建 link、不外推）。
- 兩者皆非 → 刪除。

### 3.3 過渡期原則

在 orchestrator 完成前的過渡期，至少先做：模板與範例抽出到 `_templates/`；`agent_start_prompt.md` 每步標注「機械步驟（照抄命令）」vs「內容步驟（需判斷）」；禁止清單去重並標注哪些已有工具強制。

---

## 四、端到端工作流程重構

### 4.1 流程總圖

```text
run_chapter.py 【書名】 X
│
├─ P1 準備（純程式，模型 0 次）
│    build_link_index → 讀 raw_scripture → 依 source_manifest/URL 規則
│    crawl raw_data → 自動生成 source_manifest.md 骨架
│
├─ M1 來源有效性（模型 × 來源數；每來源一呼叫）
│    輸入：單一 raw text 的前 N 行＋抽樣段
│    輸出：{status: OK|INVALID|IRRELEVANT, reason}  → 程式回填 manifest
│
├─ M2 候選抽取（模型 × 分段數；經文+來源每段一呼叫）
│    輸出：link_candidates.yaml 條目（name, type, trigger）
│    程式合併、去重、檢查非法字元與分類 enum
│
├─ P2 解析（純程式）
│    resolve_link_candidates → link_plan.yaml（A/B/C/D/E）
│    D 類與衝突 → 匯總為人工決策點，暫停或標記後續
│
├─ M3 條目內容（模型 × C 類條目數；每條目一呼叫）
│    輸入：該條目觸發經文 + 程式切出的來源摘錄
│    輸出：entry_content/{name}.yaml → schema 驗證 → 不合格自動重試 ≤3
│
├─ M4 B 類累積（既有流程：prepare → 模型填 link_updates.yaml → 程式 apply）
│
├─ M5 經文標注（模型 × 節數/批；每 10–20 節一呼叫）
│    輸出：verse_links.yaml → 程式驗證 phrase 子字串與 target 閉合
│
├─ M6 章整理（模型 × 1）
│    輸出：chapter_content.yaml（knowledge_nodes + summary + references）
│
├─ P3 渲染（純程式）
│    render_entry × N → link_folder/*.md
│    render_chapter → 第x章.md → build_fhl_maps 同步
│
├─ P4 驗證（純程式）
│    check_existing_links → validate → quality → verify → audit --check-due
│    結構錯誤＝render 程式的 bug（修程式，非叫模型重寫）
│    內容錯誤 → 定位到對應 payload，只重跑該項的 M 步驟
│
└─ P5 提交（程式 + 人工 gate）
     全綠 → 產出完成回報（程式套模板）→ commit/push
```

**職責劃分口訣**：P 步驟（程式）負責*何時、何地、什麼格式*；M 步驟（模型）負責*寫什麼*。資料交接點一律是 `.tmp/第x章/` 內有 schema 的檔案。

### 4.2 orchestrator 虛擬碼

```python
def run_chapter(book, ch):
    ctx = load_or_resume(f"{book_dir(book)}/.tmp/第{ch}章/")   # 斷點續跑
    if not ctx.done("P1"): prepare_sources(book, ch)
    for src in ctx.sources:
        if not ctx.done(f"M1:{src}"):
            result = call_model("source_validity", inputs=excerpt(src),
                                schema=SCHEMAS.validity, retries=3)
            ctx.manifest.update(src, result)
    ...
    for entry in ctx.link_plan.category("C"):
        if not ctx.done(f"M3:{entry.name}"):
            payload = call_model("entry_content",
                                 inputs=slice_sources_for(entry),
                                 schema=SCHEMAS.entry, retries=3)
            semantic_check(payload, ctx)        # target 閉合、enum、量化門檻
            save(ctx.tmp / f"entry_content/{entry.name}.yaml", payload)
    ...
    render_all(ctx)          # P3：模板+payload → markdown
    report = run_validators(ctx)               # P4
    dispatch_fixes(report, ctx)                # 內容錯→重跑對應 M；結構錯→raise
```

`call_model` 的實作可以是 Anthropic API 直呼（structured output）、Claude Code headless（`claude -p` + `--output-format json`）或 Agent SDK subagent——指導原則不綁定；關鍵是 **schema 強制 + 重試迴圈 + 最小輸入** 三件事不可省。

### 4.3 分批與 context 控制

- **逐條目**是預設粒度，不是超長章節的特例。現行 scheme §9 的「超長章節三階段」在新流程下自然消失——每個 M 呼叫本來就只載入一小片，60 節與 20 節的差別只是批次數。
- 每個 M 呼叫是**全新 context**：無前章記憶、無修錯殘留，規則漂移無從累積。
- 來源摘錄由程式切片（依條目關鍵詞 grep 前後段落），而非把整份 raw text 丟給模型自己找——這同時省 token 與降低「順手引用了規則外內容」的機率。

### 4.4 人工決策點

程式在以下節點暫停並輸出決策清單，其餘全自動：D 類與同名／alias 衝突（現有設計，保留）、M 步驟重試 3 次仍不合格、驗證後定位不到 payload 的內容錯誤、10 章／整卷巡檢報告。

---

## 五、漸進導入路線（交給執行 agent 的階段任務）

按「漂移最大處先做」排序，每階段獨立可用、可驗收：

| 階段 | 內容 | 驗收 |
|---|---|---|
| 1 | `_config/schemas/` + `render_entry.py`：C 類條目改為「模型填 entry_content.yaml → 程式渲染」 | 用既有某章的 C 類條目重跑，`validate_knowledge_base.py` 0 error、diff 僅內容差異 |
| 2 | `verse_links.yaml` + `render_chapter.py`：章節主檔改程式生成 | 對既有章節做 round-trip（成品→payload→重渲染）diff ≈ 0 |
| 3 | `link_candidates.yaml` 取代手寫 .md；`resolve_link_candidates.py` 雙格式支援 | resolver 對新舊格式輸出相同 link_plan |
| 4 | `run_chapter.py` orchestrator：收編 32 步、實作 call_model 重試迴圈與斷點續跑 | 新章節端到端跑通，模型手寫 markdown 檔案數 = 0 |
| 5 | 縮編 `scheme.md`／`agent_start_prompt.md`，規則遷移（§3.2 判準），模板入 `_templates/` | prompt 總量下降 ≥ 70%；CI 全綠 |

每階段完成後跑完整驗證鏈與 `python -m unittest discover -s util/tests -v`；render 程式必須有 round-trip 測試（golden payload → 渲染 → validate 通過）。

---

## 六、驗收標準（重構是否成功）

1. 模型輸出的檔案全部是 `.tmp/` 內有 schema 的 YAML/JSON；`link_folder/` 與章節主檔全部由程式寫入。
2. 結構類驗證錯誤（H2 順序、frontmatter、標記區、alias 格式）常態為 0——若出現即為 render 程式 bug。
3. 任一內容錯誤可定位到單一 payload 並單獨重跑，不需重做整章。
4. 中斷後 `run_chapter.py` 可從斷點續跑，重跑冪等（0 重複變更）。
5. 給模型的 prompt 中不再包含流程步驟與可程式強制的禁止事項。
