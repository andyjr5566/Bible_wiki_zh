# Scripture Knowledge Base Scheme

本檔是 `scripture/` 的設計原則與決策記錄，供人與 agent 理解「為什麼這樣設計」。
操作入口見 `agent_start_prompt.md`；資料結構契約見 `_config/schemas/*.json`；流程本身在 `util/run_chapter.py`。重構緣由與階段記錄見 `refactor_guidelines.md`。

核心一句話：**模型不碰結構，程式不碰內容。** 模型只輸出 YAML payload（資料），所有 markdown 由 render 程式從 payload 生成；格式合規是結構性保證，不靠模型自律。

---

## 1. 架構總覽

```text
編排層（程式）util/run_chapter.py
  resolve → entry_content(模型) → verse_links(程式) → chapter_content(模型) → render → validate
  斷點續跑：.tmp/第x章/ 內檔案存在即跳過；重跑冪等
資料層（模型填寫）.tmp/第x章/*.yaml —— 每種有 JSON Schema
  link_candidates.yaml   候選節點（agent 準備，唯一人工內容輸入）
  link_plan.yaml         A–E 分類（resolver 產生）
  entry_content/*.yaml   C 類新條目 payload（模型批量填寫，每批 5 條）
  verse_links.yaml       經文 wiki-link（程式掃描產生，不呼叫模型）
  chapter_content.yaml   本章知識節點＋本章整理（模型填寫）
  link_updates.yaml      B 類累積（agent 填 summary/relation）
呈現層（程式）render_entry.py / render_chapter.py
  payload → markdown；frontmatter、H2 順序、accumulation 標記、alias 格式全由程式排版
```

模型呼叫規約（`util/model_client.py`）：schema 驗證 + 具體錯誤回饋重試（上限 3 次）+ 失敗標記 manual_review。端點可切換（`_config/model_endpoints.yaml`；CLI `list|use|test`；API key 只放環境變數，經 `api_key_env` 引用，不寫進設定檔）。`tasks:` 把不同任務路由到不同端點與模型：值可為端點名字串，或 `{endpoint, model, kind}` mapping（同一端點依任務換模型）。目前 `entry`（條目，量大逐批）、`chapter`（本章整理，長篇）、`embedding`（語義索引，`kind: embedding`）各自指定。mapping 的 model 只在最終選中的端點就是該設定端點時生效；env 切到別的端點＝用該端點自己的 model。

**決策記錄：模板不設 `_templates/` 資料夾。** 條目與章節的 markdown 結構直接寫在 render 程式內（有 round-trip 測試保證 `render(parse(x)) == x`）；設獨立模板檔會造成兩份真相。模型永遠看不到模板——這才是原則的重點。

---

## 2. 目錄結構

```text
scripture/
├── scheme.md / agent_start_prompt.md / refactor_guidelines.md
├── raw_scripture/{標準書名}/第{章}.txt     # 本地經文，每行一節，不得改寫
├── raw_data/                               # 來源純文字快取（crawl_bible_text.py 產物）
├── _config/                                # bible_books、schemas、homonyms、endpoints、maintenance
├── util/                                   # 全部工具；輸出在 util/output/
├── appendix/fhl_maps/                      # FHL 地圖資料；筆記由 build_fhl_maps.py 生成
├── 【正典序號 書名】/                       # 例 01 創世記/、02 出埃及記/
│   ├── 第x章.md                            # 每章唯一主檔（render_chapter 產物）
│   └── .tmp/第x章/                         # 該章全部中介 payload
└── link_folder/{人物|地點|主題|背景|歷史|原文|文化|神學|互文|解經爭議|事件|...}/
```

- 書卷資料夾負責順讀；`link_folder/` 全域共用，負責跨章累積知識。
- 一條目一主分類；其他性質放 `secondary_types`，不得多資料夾重複建檔。新增分類必須適合跨章累積。
- 章節檔只有 `第x章.md`；不建 `經文/`、`註解/` 等平行資料夾，不為未來章節預建空檔。

---

## 3. 內容決策規則（模型／agent 的判斷邊界）

### 3.1 資料驅動 link 判準

建 link 前兩問：**此詞是否由本章經文或有效 raw text 明確觸發？是否有足夠資料支撐一個條目？** 任一為否就不建。

- 可建：經文明確出現的人物／地點／事件；來源明確解釋的概念、原文、象徵、互文、神學。
- 不建：AI 覺得重要但來源未提；只靠神學常識聯想；只能寫 2–3 行 stub；普通名詞而來源未賦義；為了讓庫看起來豐富。
- 普通詞不 link；來源賦予特殊意義時 link 完整概念短語（`[[屬靈淫亂]]` 而非 `[[淫亂]]`）。
- 新條目內出現的新詞不自動長出第二層條目，仍須各自通過上述判準。
- 不設每章條目數上限，也不因人物看似普通而先驗排除——只由已收集資料決定。

### 3.2 命名與 alias 語義

- `link target = 條目檔名`、`alias = 經文原詞`：`[[條目完整名稱|經文原詞]]`。
- 原文類條目名用「中文（音譯）」如 `皂莢木（atzei shittim）`；互文類用「簡短標題（經文）」如 `天上真聖所（來9：23-24）`——讀者要能從名稱知道在講什麼。冒號一律全形 `：`（半形 `:` 是 Windows 檔名非法字元，程式會自動正規化）。
- **同名不同實體必須分檔且全部加最小穩定限定詞**（`示劍（城）`／`示劍（哈抹之子）`），不得讓任一個獨占裸名；登記於 `_config/link_homonyms.yaml`，resolver 遇裸名列入 D 類。限定詞用長期可辨識的關係／職分／類型，不用流水號。
- 同一實體多性質＝一檔＋`secondary_types`，不是同名詞。歧義裸名不得放進 YAML `aliases`。
- 跨章引用寫完整路徑 `[[28 何西阿書/第1章|何西阿書 第1章]]`，不寫 `[[第1章]]`。

### 3.3 A–E 類語義（link_plan）

| 類 | 意義 | 動作 |
|---|---|---|
| A | 既有條目已含本書卷本章累積 | 直接用（verse_links 連 existing_title） |
| B | 既有條目，本章尚未累積 | `link_updates.py` 安全累積（人填 summary/relation） |
| C | 不存在且資料足夠 | orchestrator 批量請模型建正式條目 |
| D | 同名／分類衝突、資料不足 | 人工判斷，不得自動建立或連結 |
| E | 不應建 link | 純文字 |

resolver 比對序：完全同名 → aliases → 音譯基名（裸名「皂莢木」命中「皂莢木（atzei shittim）」）→ 同名映射；歧義一律進 D。命中後核對分類相容（type 或 secondary_types），不相容進 D。此序純字面，抓不到「措辭不同、意思相同」的近似重複——該缺口由 §3.5 語義近鄰索引以附註補上（不改分類，僅供人工判斷）。

### 3.4 條目內容原則

- 定義要完整說明原文、字義與本章用法，不吝嗇篇幅；一切陳述可對回來源。
- 來源依據每項格式「標籤: 位置說明（URL）」，URL 取自本章 source_manifest 的 OK 來源（程式驗證）。
- 相關條目只能指向已存在或同批建立的條目完整名稱；渲染前由程式閉合——裸經文引用（創3:24）改寫為對應互文條目全名，無對應者移除並回報。
- 正式條目的 `定義`／`主題發展` 是保護區：每章任務只累積，不重寫（除非使用者要求）。
- 候選條目（status: candidate）每卷完成後清理：多次引用者升級、重複者合併、長期無支撐者處置。

### 3.5 語義近鄰索引（近似重複的防線）

**要解決的問題**：字面比對（§3.3 resolver 比對序）只認得同名／alias／音譯基名，看不出「措辭不同、意思相同」。4300+ 條目下這是靜默坑——agent 把「不可搶奪鄰舍」當新候選，其實已有「不可欺壓鄰舍搶奪與雇工工價不過夜」，兩個閘門全過卻建出近似重複（利19 的 7 個主題條目即是善後案例）。

**機制**：`build_embedding_index.py` 把每個條目的「標題＋分類＋別名＋定義＋主題發展＋相關條目＋累積摘要」嵌成向量存 `util/output/embedding_index.{npz,meta.json}`（增量更新，只重嵌變動條目）。`semantic_lookup.py` 以詞查最相似的既有條目。resolve 後程式自動對 C／D 候選查近鄰，寫進 `link_plan.yaml` 的 `semantic_hint`。

**邊界（與整體原則一致：機械不可證者只提示、不裁決）**：

- **純附註，不是閘門**：只加 `semantic_hint` 欄位供人工判斷，不改分類、不自動建立或連結、不擋 commit。相似度非機械可證，不升級為 error（呼應「加護欄前先全庫實測」的教訓）。
- **降級不中斷**：索引缺失、模型不符、端點不通時整步靜默略過，主流程照跑。語義索引是輔助工具，不是資料流必要環節。
- **與 embedding 模型綁定**：向量跨模型不可比，混用後相似度看似合理實為垃圾。meta 記錄模型名與維度，載入端比對現行設定，不符即拒用並要求 `--rebuild`（此為機械可證，故可硬擋）。
- **門檻經全庫校準**：現用 `nvidia/nemotron-3-embed-1b`，query／passage 為非對稱向量空間（同句兩空間 cos≈0.6，故完全命中的絕對分也只 ~0.47）。實測噪音上限≈0.24、真近似落 0.42–0.57，取門檻 0.40（`resolve_link_candidates.SEMANTIC_HINT_THRESHOLD`）。換模型後此數失效須重新校準。索引一律用 `input_type=passage`、查詢用 `query`，不可混。

---

## 4. 資料流契約

```text
raw_scripture + 有效 raw_data
→ link_candidates.yaml（agent 判斷）
→ build_link_index.py → resolve → link_plan.yaml（程式分類 A–E）
→ run_chapter.py：entry payloads（模型）→ verse_links（程式掃描）→ chapter_content（模型）
→ render_entry / render_chapter（程式渲染全部 markdown）
→ link_updates.py（B 類，人填內容、程式冪等寫入標記區）
→ 驗證鏈 → commit
```

- `link_plan` 只決定「用哪個條目、放哪、什麼類別」；寫內容一律回到 raw text 與經文，不得依 plan 編內容。
- 本章整理（organization）是「### 小節（vX-Y）」分段的整合性散文並標明出處（CT指出…），份量門檻隨章節長度由程式驗證；章節「參考資料」由程式從 source_manifest 注入 OK 來源 URL，模型不手寫。
- 經文本文只取自 `raw_scripture`，render_chapter 逐字對齊；wiki-link 由程式掃描已知詞彙套用（子字串保證、長詞優先、目標閉合），模型不再手寫經文區。已知詞彙＝候選名＋條目全名＋括號前裸名＋條目 aliases（A/B 取全庫索引、C 取本章 payload）＋候選宣告的 `surfaces`——經文用條目全名與 aliases 都對不上的簡稱時（桌子→陳設餅桌子），在 link_candidates 為該候選宣告 surfaces；同詞在本章多義用 `{phrase, verses}` 限定節次（出26「幔子」v1-13 幕幔、v31-33 內幔）。同一詞推導出多個條目＝歧義，整詞不連並記 manual_review（宣告的 surfaces 優先於推導，可用來裁決）。
- 來源全文直接餵給模型（不切片）；超大章節由程式等比截斷（§7）。
- 累積標記 `<!-- accumulation:{書}:{章}:start/end -->` 由程式生成與定位；同書卷一個 `### 標題`、章次依序排列，重跑冪等。

---

## 5. 程式強制界線

以下規則已由程式結構性保證，agent 無需（也不得）手工替代：

- **結構**：frontmatter、H2 順序、模板、alias 格式、標記區——render 程式產物必然合規；結構驗證出錯＝程式 bug，修程式而非叫模型重寫。
- **安全**：覆寫保護（含其他章累積的既有條目拒絕覆寫）、檔名安全字元、`rename_markdown.py` 同步全庫連結、`link_updates` 只動標記區。
- **正確性**：verse_links 的 phrase 必為經文子字串且 target 閉合；related_entries 渲染前閉合（無對應條目者移除並回報）；條目 sources 與章節參考資料的 URL 以 source_manifest 為唯一事實來源；本章整理份量門檻依章節長度驗證；book/chapter 以程式認定為準；驗證左移（payload 層擋錯＋錯誤回饋重試）。
- 舊成品格式遷移用 `normalize_format.py --scope all --dry-run` → 套用 → 再 dry-run 必須 0 變更。

---

## 6. 驗證與 commit gate

```text
check_existing_links.py 【序號 書名】/第x章.md --missing   # 章節連結完整
build_link_index.py                                        # 索引可重現（CI 用 --check）
validate_knowledge_base.py                                 # ERRORS=0（新增檔違規為 blocking）
link_quality_check.py 【書名】                              # CRITICAL=0
verify_links.py 【書名】                                    # BROKEN=0, INVALID=0, UNKNOWN=0（PENDING_SCRIPTURE_REFS 可存在）
audit_knowledge_base.py --check-due                        # PASS
python -m unittest discover -s util/tests                  # 工具測試（CI 必跑）
```

全部成立才 commit + push；CI 為最終守門。回報只列結論數字（errors/critical/broken 計數）與需人工決策的項目，不貼完整報告。

---

## 7. 來源規約

- 來源：ccbiblestudy（CT 註解／GT 拾穗）、KingComments（KC）、BibleHub Study（BH）、使用者指定。
- 一律先 `crawl_bible_text.py` 轉 `raw_data/*.txt` 再讀本地檔；禁止直接抓網頁進 context 整理、禁止硬猜 URL、已存在不 `--overwrite`。
- URL 模式：
  `https://www.ccbiblestudy.org/{Old|New}%20Testament/{卷代碼}/{卷號}{CT|GT}{章2位}.htm`
  `https://www.kingcomments.com/en/bible-studies/{KC_slug}/{章}`
  `https://biblehub.com/study/{book_slug}/{章}.htm`
- ccbiblestudy CT/GT:
	https://www.ccbiblestudy.org/{Old|New}%20Testament/{卷代碼}/{卷號}{CT|GT}{章2位}.htm
	例：27Daniel/27CT03.htm, 27Daniel/27GT03.htm, 28Hosea/28CT01.htm, 28Hosea/28GT01.htm, 01Gen/01CT01.htm, 40Matt/40CT01.htm
- KingComments:
	https://www.kingcomments.com/en/bible-studies/{KC_slug}/{章}
	例：Dan/3, Hos/1, Gen/1, 1Sam/1, Song/1
- BibleHub Study:
	https://biblehub.com/study/{book_slug}/{章}.htm
	例：daniel/3.htm, hosea/1.htm, 1_samuel/1.htm
- 有效性：404、目錄頁、導覽列、亂碼、與本章無關、過短無料＝無效；只記錄於 manifest，不得作依據。
- 大章節（>60 節或來源單檔 >120KB／合計 >250KB）：程式自動等比截斷來源餵入（`util/source_excerpts.py`）；不再有人工三階段分段流程。

---

## 8. 維護

- 每累計 10 章：`audit_knowledge_base.py --all --checkpoint 10`；每卷完成：`--book 【書名】`。報告只是人工決策線索，不自動刪併升級。間隔記錄在 `_config/maintenance_policy.yaml`，`--check-due` 阻止漏檢。
- FHL 地圖：`build_fhl_maps.py` 生成與同步（`--check` 驗證）；章內 `fhl-map-links` 標記區由程式管理，render_chapter 原樣保留（passthrough），人工補充放 `fhl-map-manual` 標記後。
- 每卷完成後清理 `_待分類/` 與候選條目。
