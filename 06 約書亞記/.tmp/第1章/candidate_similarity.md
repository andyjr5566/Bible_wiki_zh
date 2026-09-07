<!-- candidate_similarity_meta
schema_version: 1
book: 約書亞記
chapter: 1
candidate_sha256: 9fa73dc4e3948646f0a3dcac76f0d999ad447ac6c6c8bf4729a6ea80522dca9a
candidate_identity_sha256: 5ef13432dd92f1997e9d9e4f7f1523f242576b5265c6dc95da9a73e0ac17f7dd
embedding_model: nvidia/nemotron-3-embed-1b
embedding_index_fingerprint: 68f90736fd80d73d
link_index_sha256: 1f0b562232bbf32082c7d3b58b0a6f17a6b2c5e26c1ecef047fbe2bd27a3a582
homonyms_sha256: b8d042ea4f51253052128b2b289befdcf00b53c88237b67050f3252242c41ab8
rerank_model: nvidia/llama-nemotron-rerank-vl-1b-v2:free
rerank_policy_version: 2026.08.4
calibration_sha256: f63b1218023371bbbece396422aa7a02025bba0da119b49cae75232755734211
rerank_status: success
rerankable_candidates: 7
rerank_attempted: 7
rerank_succeeded: 7
rerank_retrieve_top_k: 20
rerank_score_observed: 0.002-0.184
-->

# 候選語義近鄰報告：約書亞記 第1章

- 檢索模型：nvidia/nemotron-3-embed-1b｜重排模型：nvidia/llama-nemotron-rerank-vl-1b-v2:free（未校準/保守模式）｜全庫 3130 條
- 規則說明：字面確切匹配直接通過；其餘候選先檢索 Top 20 名再由 Reranker 重排，取前 5 名顯示。
  治理優先：同名歧義（D類）與分類不相容永遠標 ⚠。
  重排模型未校準時，⚠ 由檢索相似度規則（≥0.50 且 top-1 非同實體）決定，重排名次只當附加證據。
  字面解析：列 resolver 實際比對結果——標「請確認」者務必人工核實。

## 約書亞（人物）
query:
- 待建立詞：約書亞
- 出現位置：約書亞記 第1章
- 候選類型：人物
- 本章上下文：第1節「耶和華曉諭摩西的幫手，嫩的兒子約書亞」；第10、12、16節他發令、對河東二支派半說話、接受百姓回應。本章是他正式接任後的第一段記載。

字面解析：對上既有「約書亞」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 約書亞 | 0.622 | link_folder/人物/約書亞.md |
| 2 | 約書亞承接摩西 | 0.618 | link_folder/事件/約書亞承接摩西.md |
| 3 | 摩西與約書亞的權柄差異 | 0.542 | link_folder/主題/摩西與約書亞的權柄差異.md |
| 4 | 分地的十位支派首領 | 0.510 | link_folder/主題/分地的十位支派首領.md |
| 5 | 兩支派半求河東之地為業 | 0.495 | link_folder/事件/兩支派半求河東之地為業.md |

判定：✅ 建議使用既有條目 [[約書亞]]（同名／字面對應）

## 摩西（人物）
query:
- 待建立詞：摩西
- 出現位置：約書亞記 第1章
- 候選類型：人物
- 本章上下文：第1節「耶和華的僕人摩西死了以後」；第3、5、7、14、15、17節反覆以摩西為約書亞權柄與命令的依據。

字面解析：對上既有「摩西」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 摩西 | 0.610 | link_folder/人物/摩西.md |
| 2 | 耶和華的僕人摩西（e.ved 與 al pi） | 0.586 | link_folder/原文/耶和華的僕人摩西（e.ved 與 al pi）.md |
| 3 | 摩西與約書亞的權柄差異 | 0.548 | link_folder/主題/摩西與約書亞的權柄差異.md |
| 4 | 稱摩西為我主 | 0.540 | link_folder/主題/稱摩西為我主.md |
| 5 | 神人（ish ha.e.lo.him） | 0.540 | link_folder/原文/神人（ish ha.e.lo.him）.md |

判定：✅ 建議使用既有條目 [[摩西]]（同名／字面對應）

## 約書亞承接摩西（事件）
query:
- 待建立詞：約書亞承接摩西
- 出現位置：約書亞記 第1章
- 候選類型：事件
- 本章上下文：第1節「摩西的幫手，嫩的兒子約書亞」，第5節「我怎樣與摩西同在，也必照樣與你同在」，第17節百姓說「我們從前在一切事上怎樣聽從摩西，現在也必照樣聽從你」。交接在本章實際生效。
- 經文用詞：嫩的兒子約書亞

字面解析：對上既有「約書亞承接摩西」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 約書亞承接摩西 | 0.700 | link_folder/事件/約書亞承接摩西.md |
| 2 | 約書亞 | 0.644 | link_folder/人物/約書亞.md |
| 3 | 摩西與約書亞的權柄差異 | 0.630 | link_folder/主題/摩西與約書亞的權柄差異.md |
| 4 | 智慧的靈（ru.ach chokh.mah） | 0.588 | link_folder/原文/智慧的靈（ru.ach chokh.mah）.md |
| 5 | 摩西 | 0.562 | link_folder/人物/摩西.md |

判定：✅ 建議使用既有條目 [[約書亞承接摩西]]（同名／字面對應）

## 耶和華的僕人摩西（e.ved 與 al pi）（原文）
query:
- 待建立詞：耶和華的僕人摩西（e.ved 與 al pi）
- 出現位置：約書亞記 第1章
- 候選類型：原文
- 本章上下文：第1、13、15節三次稱摩西為「耶和華的僕人」；STEP 為 'E.ved（H5650），第2、7節神自稱「我的僕人摩西」（'av.D/i）。
- 經文用詞：耶和華的僕人

字面解析：對上既有「耶和華的僕人摩西（e.ved 與 al pi）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 耶和華的僕人摩西（e.ved 與 al pi） | 0.668 | link_folder/原文/耶和華的僕人摩西（e.ved 與 al pi）.md |
| 2 | 主耶和華（a.do.nai） | 0.571 | link_folder/神學/主耶和華（a.do.nai）.md |
| 3 | 摩西在神全家盡忠（民12：7） | 0.549 | link_folder/互文/摩西在神全家盡忠（民12：7）.md |
| 4 | 稱摩西為我主 | 0.527 | link_folder/主題/稱摩西為我主.md |
| 5 | 耶和華的使者 | 0.504 | link_folder/神學/耶和華的使者.md |

判定：✅ 建議使用既有條目 [[耶和華的僕人摩西（e.ved 與 al pi）]]（同名／字面對應）

## 侍立事奉（a.mad、sha.rat）（原文）
query:
- 待建立詞：侍立事奉（a.mad、sha.rat）
- 出現位置：約書亞記 第1章
- 候選類型：原文
- 本章上下文：第1節「摩西的幫手」，STEP 為 me.sha.Ret（H8334，sha.rat），Piel 分詞。CT 原文字義「幫手」伺候，服事；GT 說原文是「伺候」、「服事」的分詞型態。與利未人「侍立事奉」同一個字根，用在個人助手身上。
- 經文用詞：幫手

字面解析：對上既有「侍立事奉（a.mad、sha.rat）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 侍立事奉（a.mad、sha.rat） | 0.674 | link_folder/原文/侍立事奉（a.mad、sha.rat）.md |
| 2 | 事奉與作奴僕同一字根（a.vad） | 0.543 | link_folder/原文/事奉與作奴僕同一字根（a.vad）.md |
| 3 | 耶和華的僕人摩西（e.ved 與 al pi） | 0.519 | link_folder/原文/耶和華的僕人摩西（e.ved 與 al pi）.md |
| 4 | 擔當（na.sa） | 0.519 | link_folder/原文/擔當（na.sa）.md |
| 5 | 辦事（melakah） | 0.496 | link_folder/原文/辦事（melakah）.md |

判定：✅ 建議使用既有條目 [[侍立事奉（a.mad、sha.rat）]]（同名／字面對應）

## 約但河（地點）
query:
- 待建立詞：約但河
- 出現位置：約書亞記 第1章
- 候選類型：地點
- 本章上下文：第2節「和眾百姓過這約但河」，第11、14、15節四次出現。CT 說明河長、河寬與春汛；GT 說平常寬約25-30公尺，春汛時耶利哥附近可達1000公尺。

字面解析：對上既有「約但河」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 約但河 | 0.571 | link_folder/地點/約但河.md |
| 2 | 雅博渡口 | 0.512 | link_folder/地點/雅博渡口.md |
| 3 | 谷歌大與約巴他 | 0.497 | link_folder/地點/谷歌大與約巴他.md |
| 4 | 耶利哥 | 0.480 | link_folder/地點/耶利哥.md |
| 5 | 「伯拉大河」名稱 | 0.466 | link_folder/原文/「伯拉大河」名稱.md |

判定：✅ 建議使用既有條目 [[約但河]]（同名／字面對應）

## 曠野（地點）
query:
- 待建立詞：曠野
- 出現位置：約書亞記 第1章
- 候選類型：地點
- 本章上下文：第4節「從曠野和這利巴嫩」；各家指這是應許之地的南界旱漠地帶。

字面解析：對上既有「曠野」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 南地 | 0.610 | link_folder/地點/南地.md |
| 2 | 曠野 | 0.596 | link_folder/地點/曠野.md |
| 3 | 應許之地的四至 | 0.559 | link_folder/主題/應許之地的四至.md |
| 4 | 汛的曠野 | 0.531 | link_folder/地點/汛的曠野.md |
| 5 | 迦南四境 | 0.524 | link_folder/主題/迦南四境.md |

判定：✅ 建議使用既有條目 [[曠野]]（同名／字面對應）

## 利巴嫩（地點）
query:
- 待建立詞：利巴嫩
- 出現位置：約書亞記 第1章
- 候選類型：地點
- 本章上下文：第4節「從曠野和這利巴嫩」，各家同指北界山地。

字面解析：對上既有「利巴嫩」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 利巴嫩 | 0.648 | link_folder/地點/利巴嫩.md |
| 2 | 北界的何珥山 | 0.545 | link_folder/地點/北界的何珥山.md |
| 3 | 迦南四境的地名考據 | 0.472 | link_folder/背景/迦南四境的地名考據.md |
| 4 | 黑門山 | 0.450 | link_folder/地點/黑門山.md |
| 5 | 應許之地的四至 | 0.440 | link_folder/主題/應許之地的四至.md |

判定：✅ 建議使用既有條目 [[利巴嫩]]（同名／字面對應）

## 伯拉大河（地點）
query:
- 待建立詞：伯拉大河
- 出現位置：約書亞記 第1章
- 候選類型：地點
- 本章上下文：第4節「直到伯拉大河」，STEP 為 ne.har- pe.Rat（H5104H＋H6578），即幼發拉底河，各家同指東界。

字面解析：對上既有「伯拉大河」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 伯拉大河 | 0.644 | link_folder/地點/伯拉大河.md |
| 2 | 「伯拉大河」名稱 | 0.562 | link_folder/原文/「伯拉大河」名稱.md |
| 3 | 伊甸園四河 | 0.466 | link_folder/背景/伊甸園四河.md |
| 4 | 埃及河的地理辨識 | 0.459 | link_folder/解經爭議/埃及河的地理辨識.md |
| 5 | 利河伯（大河邊） | 0.451 | link_folder/地點/利河伯（大河邊）.md |

判定：✅ 建議使用既有條目 [[伯拉大河]]（同名／字面對應）

## 大海（地中海）（地點）
query:
- 待建立詞：大海（地中海）
- 出現位置：約書亞記 第1章
- 候選類型：地點
- 本章上下文：第4節「又到大海日落之處」，STEP 為 hai./Yam ha./ga.Dol me.Vo' ha./Sha.mesh，各家同指西界地中海。

字面解析：對上既有「大海（地中海）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 大海（地中海） | 0.618 | link_folder/地點/大海（地中海）.md |
| 2 | 迦南四境 | 0.421 | link_folder/主題/迦南四境.md |
| 3 | 海（紅海） | 0.396 | link_folder/地點/海（紅海）.md |
| 4 | 紅海指的是哪個海 | 0.373 | link_folder/解經爭議/紅海指的是哪個海.md |
| 5 | 迦南四境的地名考據 | 0.372 | link_folder/背景/迦南四境的地名考據.md |

判定：✅ 建議使用既有條目 [[大海（地中海）]]（同名／字面對應）

## 赫人（人物）
query:
- 待建立詞：赫人
- 出現位置：約書亞記 第1章
- 候選類型：人物
- 本章上下文：第4節「赫人的全地」，STEP 為 ha./chi.Tim（H2850）。各家對這一句的地理指涉有不同說明。

字面解析：對上既有「赫人」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 赫人 | 0.434 | link_folder/人物/赫人.md |
| 2 | 詩歌中的希伯是誰 | 0.363 | link_folder/解經爭議/詩歌中的希伯是誰.md |
| 3 | 希未人稱呼 | 0.353 | link_folder/原文/希未人稱呼.md |
| 4 | 「希伯來人」的意義 | 0.352 | link_folder/原文/「希伯來人」的意義.md |
| 5 | 亞珥歌伯（ar.gov） | 0.352 | link_folder/地點/亞珥歌伯（ar.gov）.md |

判定：✅ 建議使用既有條目 [[赫人]]（同名／字面對應）

## 應許之地的四至（主題）
query:
- 待建立詞：應許之地的四至
- 出現位置：約書亞記 第1章
- 候選類型：主題
- 本章上下文：第4節整節列出曠野、利巴嫩、伯拉大河、赫人全地、大海五個界標，末句「都要作你們的境界」，STEP 的「境界」是 ge.vu.le./Khem（H1366H）。
- 經文用詞：境界

字面解析：對上既有「應許之地的四至」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 應許之地的四至 | 0.683 | link_folder/主題/應許之地的四至.md |
| 2 | 迦南四境 | 0.610 | link_folder/主題/迦南四境.md |
| 3 | 神所定的邊界 | 0.559 | link_folder/神學/神所定的邊界.md |
| 4 | 伯拉大河 | 0.540 | link_folder/地點/伯拉大河.md |
| 5 | 大海（地中海） | 0.522 | link_folder/地點/大海（地中海）.md |

判定：✅ 建議使用既有條目 [[應許之地的四至]]（同名／字面對應）

## 腳掌可踏之處（原文）
query:
- 待建立詞：腳掌可踏之處
- 出現位置：約書亞記 第1章
- 候選類型：原文
- 本章上下文：第3節「凡你們腳掌所踏之地」，STEP 為 tid.Rokh kaf- rag.le./Khem（H1869 da.rakh、H3709H kaph、H7272 re.gel），與申11:24 完全相同的組合；GT 明說申11:24-25 是本段的平行經文。
- 經文用詞：腳掌所踏之地

字面解析：對上既有「腳掌可踏之處」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 腳掌可踏之處 | 0.655 | link_folder/原文/腳掌可踏之處.md |
| 2 | 用腳澆灌 | 0.492 | link_folder/文化/用腳澆灌.md |
| 3 | 眷顧（da.rash） | 0.452 | link_folder/原文/眷顧（da.rash）.md |
| 4 | 伸冤報應在我（na.kam 與 shil.lem） | 0.449 | link_folder/原文/伸冤報應在我（na.kam 與 shil.lem）.md |
| 5 | 神的指頭（路11：20） | 0.442 | link_folder/互文/神的指頭（路11：20）.md |

判定：✅ 建議使用既有條目 [[腳掌可踏之處]]（同名／字面對應）

## 賜給（na.tan）（原文）
query:
- 待建立詞：賜給（na.tan）
- 出現位置：約書亞記 第1章
- 候選類型：原文
- 本章上下文：GT《約書亞記綜合解讀》：動詞「賜給 נָתַן」在本章中出現了七次(2、3、6、11、13、14、15節)；第3節的「賜給」原文是完成式。STEP 顯示第3節是 ne.ta.Ti/v（HVqp1cs，完成式），第2、11、15節是 no.Ten（分詞）。

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 初熟土產的信仰告白 | 0.453 | 0.018 | link_folder/主題/初熟土產的信仰告白.md |
| 2 | 追隨與臨到（na.sag） | 0.440 | 0.016 | link_folder/原文/追隨與臨到（na.sag）.md |
| 3 | 十一奉獻後的宣告 | 0.449 | 0.016 | link_folder/主題/十一奉獻後的宣告.md |
| 4 | 多多地給不可空手而去（a.naq、re.qam） | 0.462 | 0.015 | link_folder/原文/多多地給不可空手而去（a.naq、re.qam）.md |
| 5 | 十分之一 | 0.444 | 0.014 | link_folder/原文/十分之一.md |

rerank_margin: 0.002 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=原文 vs 條目=主題），若確為同實體請確認是否改用 [[初熟土產的信仰告白]]

## 勉勵他使他膽壯（cha.zaq、a.mats）（原文）
query:
- 待建立詞：勉勵他使他膽壯（cha.zaq、a.mats）
- 出現位置：約書亞記 第1章
- 候選類型：原文
- 本章上下文：第6、7、9節神三次、第18節百姓一次說「剛強壯膽」，STEP 均為 cha.Zak（H2388G）＋ve./'e.Matz（H553），與申31:7、23 同一對命令式。
- 經文用詞：剛強壯膽

字面解析：對上既有「勉勵他使他膽壯（cha.zaq、a.mats）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 勉勵他使他膽壯（cha.zaq、a.mats） | 0.643 | link_folder/原文/勉勵他使他膽壯（cha.zaq、a.mats）.md |
| 2 | 膽壯與大能同一字根（cha.zaq） | 0.600 | link_folder/原文/膽壯與大能同一字根（cha.zaq）.md |
| 3 | 勇士（cha.yil） | 0.507 | link_folder/原文/勇士（cha.yil）.md |
| 4 | 法老心剛硬三字 | 0.506 | link_folder/原文/法老心剛硬三字.md |
| 5 | 殷勤教訓（sha.nan） | 0.489 | link_folder/原文/殷勤教訓（sha.nan）.md |

判定：✅ 建議使用既有條目 [[勉勵他使他膽壯（cha.zaq、a.mats）]]（同名／字面對應）

## 神的同在（神學）
query:
- 待建立詞：神的同在
- 出現位置：約書亞記 第1章
- 候選類型：神學
- 本章上下文：第5節「我怎樣與摩西同在，也必照樣與你同在」，第9節「耶和華─你的神必與你同在」，第17節百姓說「惟願耶和華─你的神與你同在，像與摩西同在一樣」。
- 經文用詞：與你同在

字面解析：對上既有「神的同在」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 神的同在 | 0.648 | link_folder/神學/神的同在.md |
| 2 | 摩西求神同去並蒙應允 | 0.623 | link_folder/事件/摩西求神同去並蒙應允.md |
| 3 | 亞伯拉罕的神與我同在 | 0.595 | link_folder/神學/亞伯拉罕的神與我同在.md |
| 4 | 耶和華與約瑟同在 | 0.591 | link_folder/神學/耶和華與約瑟同在.md |
| 5 | 與神同行 | 0.574 | link_folder/神學/與神同行.md |

判定：✅ 建議使用既有條目 [[神的同在]]（同名／字面對應）

## 必不撇下你，也不丟棄你（ra.phah 與 a.zav）（原文）
query:
- 待建立詞：必不撇下你，也不丟棄你（ra.phah 與 a.zav）
- 出現位置：約書亞記 第1章
- 候選類型：原文
- 本章上下文：第5節「我必不撇下你，也不丟棄你」，STEP 為 'ar.pe./Kha（H7503 ra.phah）與 'e.'ez.Ve./ka（H5800A a.zav），與申31:6、8 同一對動詞。

字面解析：對上既有「必不撇下你，也不丟棄你（ra.phah 與 a.zav）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 必不撇下你，也不丟棄你（ra.phah 與 a.zav） | 0.718 | link_folder/原文/必不撇下你，也不丟棄你（ra.phah 與 a.zav）.md |
| 2 | 你且由著我（ra.phah） | 0.506 | link_folder/原文/你且由著我（ra.phah）.md |
| 3 | 盡弟兄的本分（ya.vam） | 0.486 | link_folder/原文/盡弟兄的本分（ya.vam）.md |
| 4 | 不可擾害也不可爭戰（tsur、garah） | 0.483 | link_folder/原文/不可擾害也不可爭戰（tsur、garah）.md |
| 5 | 擔當（na.sa） | 0.474 | link_folder/原文/擔當（na.sa）.md |

判定：✅ 建議使用既有條目 [[必不撇下你，也不丟棄你（ra.phah 與 a.zav）]]（同名／字面對應）

## 律法書放在約櫃旁（主題）
query:
- 待建立詞：律法書放在約櫃旁
- 出現位置：約書亞記 第1章
- 候選類型：主題
- 本章上下文：第8節「這律法書不可離開你的口」，STEP 為 se.Fer ha./to.Rah（H5612H＋H8451）。GT《啟導本》說「這律法書」指神藉摩西所傳的一切律法。

字面解析：對上既有「律法書放在約櫃旁」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 律法書放在約櫃旁 | 0.651 | link_folder/主題/律法書放在約櫃旁.md |
| 2 | 法版 | 0.565 | link_folder/原文/法版.md |
| 3 | 講律法（ba.ar） | 0.523 | link_folder/原文/講律法（ba.ar）.md |
| 4 | 約書 | 0.514 | link_folder/神學/約書.md |
| 5 | 約櫃 | 0.506 | link_folder/主題/約櫃.md |

判定：✅ 建議使用既有條目 [[律法書放在約櫃旁]]（同名／字面對應）

## 晝夜思想（ha.gah）（原文）
query:
- 待建立詞：晝夜思想（ha.gah）
- 出現位置：約書亞記 第1章
- 候選類型：原文
- 本章上下文：第8節「總要晝夜思想」，STEP 為 ve./ha.Gi.ta（H1897，簡要詞典義 ha.gah: to mutter）加 yo.Mam va./Lay.lah。CT 原文字義「思想」默想，沉思；GT《雷氏研讀本》說包括大聲朗讀和反複誦讀；BH 詳述聖經式默想。

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 殷勤教訓（sha.nan） | 0.378 | 0.010 | link_folder/原文/殷勤教訓（sha.nan）.md |
| 2 | 你且由著我（ra.phah） | 0.350 | 0.006 | link_folder/原文/你且由著我（ra.phah）.md |
| 3 | 各人行自己眼中看為正的事 | 0.348 | 0.006 | link_folder/主題/各人行自己眼中看為正的事.md |
| 4 | 稱頌（ba.rakh） | 0.345 | 0.005 | link_folder/原文/稱頌（ba.rakh）.md |
| 5 | 心高氣傲（rum） | 0.366 | 0.005 | link_folder/原文/心高氣傲（rum）.md |

rerank_margin: 0.004 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=原文 vs 條目=神學），若確為同實體請確認是否改用 [[聖靈]]（重排模型 nvidia/llama-nemotron-rerank-vl-1b-v2:free 未校準，上表名次僅供參考）

## 亨通與順利（tsa.lech 與 sa.khal）（原文）
query:
- 待建立詞：亨通與順利（tsa.lech 與 sa.khal）
- 出現位置：約書亞記 第1章
- 候選類型：原文
- 本章上下文：第8節「你的道路就可以亨通，凡事順利」，STEP 為 tatz.Li.ach（H6743B tsa.lech）與 tas.Kil（H7919A sa.khal）；第7節末「都可以順利」也是 sa.khal。CT 原文字義「亨通」奔騰，昌盛；「順利」興盛，成功。
- 經文用詞：亨通、順利

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 殷勤教訓（sha.nan） | 0.372 | 0.157 | link_folder/原文/殷勤教訓（sha.nan）.md |
| 2 | 他的道（de.rekh） | 0.390 | 0.132 | link_folder/原文/他的道（de.rekh）.md |
| 3 | 河、泉、源（na.chal、a.yin、te.hom） | 0.374 | 0.113 | link_folder/原文/河、泉、源（na.chal、a.yin、te.hom）.md |
| 4 | 七次回轉（shuv） | 0.364 | 0.107 | link_folder/原文/七次回轉（shuv）.md |
| 5 | 六組祝福與六組咒詛的對稱 | 0.387 | 0.105 | link_folder/主題/六組祝福與六組咒詛的對稱.md |

rerank_margin: 0.025 (Top1 - Top2)
判定：🆕 建議建立新條目（最相似條目僅 0.424 < 0.50）（重排模型 nvidia/llama-nemotron-rerank-vl-1b-v2:free 未校準，上表名次僅供參考）

## 以色列人的官長（人物）
query:
- 待建立詞：以色列人的官長
- 出現位置：約書亞記 第1章
- 候選類型：人物
- 本章上下文：第10節「約書亞吩咐百姓的官長」，GT《啟導本》說當為摩西在各支派中所立的千夫長、百夫長等；GT《聖經精讀本》說官長的作用是把領袖指示傳達給百姓或召集戰鬥人員。

字面解析：對上既有「以色列人的官長」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 以色列人的官長 | 0.622 | link_folder/人物/以色列人的官長.md |
| 2 | 摩西立首領 | 0.613 | link_folder/事件/摩西立首領.md |
| 3 | 曠野審判制度 | 0.602 | link_folder/背景/曠野審判制度.md |
| 4 | 以色列的長老 | 0.584 | link_folder/文化/以色列的長老.md |
| 5 | 以色列的眾長老 | 0.575 | link_folder/人物/以色列的眾長老.md |

判定：✅ 建議使用既有條目 [[以色列人的官長]]（同名／字面對應）

## 過河前當預備食物（主題）
query:
- 待建立詞：過河前當預備食物
- 出現位置：約書亞記 第1章
- 候選類型：主題
- 本章上下文：第11節「當預備食物」，STEP 為 ha.Khi.nu（H3559A kun）加 tzei.Dah（H6720）。GT《綜合解讀》把它與出埃及時不必預備乾糧對比；KC 說這份食物不是官長給的，百姓自己要預備；BH 說嗎哪雖然仍降，百姓仍要為眼前的過河預備。
- 經文用詞：預備食物

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 五穀、新酒和油（da.gan、ti.rosh、yits.har） | 0.444 | 0.037 | link_folder/原文/五穀、新酒和油（da.gan、ti.rosh、yits.har）.md |
| 2 | 逾越節的吃法 | 0.476 | 0.036 | link_folder/歷史/逾越節的吃法.md |
| 3 | 嗎哪 | 0.494 | 0.034 | link_folder/主題/嗎哪.md |
| 4 | 過河的四萬人與留守的七萬人 | 0.449 | 0.031 | link_folder/主題/過河的四萬人與留守的七萬人.md |
| 5 | 「除了自己所吃的飯」含義 | 0.444 | 0.028 | link_folder/解經爭議/「除了自己所吃的飯」含義.md |

rerank_margin: 0.001 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=主題 vs 條目=原文），若確為同實體請確認是否改用 [[五穀、新酒和油（da.gan、ti.rosh、yits.har）]]

## 三日之內與差派探子的先後之爭（解經爭議）
query:
- 待建立詞：三日之內與差派探子的先後之爭
- 出現位置：約書亞記 第1章
- 候選類型：解經爭議
- 本章上下文：第11節「三日之內你們要過這約但河」。CT 說顯然約書亞已經接到探子的消息（參書二22~23；三2）；GT《雷氏研讀本》說探子的差遣顯然在約書亞發出這準備的命令之前；GT《串珠》說「三日之內」只是約數，很可能在1:12-15 之後起算；GT《啟導本》說或指三2 所說的三天；GT《綜合解讀》說原文是「再三日」，表明約書亞立即行動。
- 經文用詞：三日之內

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 三天 | 0.516 | 0.184 | link_folder/原文/三天.md |
| 2 | 第三日 | 0.490 | 0.102 | link_folder/神學/第三日.md |
| 3 | 十二探子窺探迦南地 | 0.515 | 0.096 | link_folder/事件/十二探子窺探迦南地.md |
| 4 | 窺探迦南起因為神命或民意的解經爭議 | 0.532 | 0.075 | link_folder/解經爭議/窺探迦南起因為神命或民意的解經爭議.md |
| 5 | 十一天的路程 | 0.471 | 0.057 | link_folder/主題/十一天的路程.md |

rerank_margin: 0.083 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=解經爭議 vs 條目=原文），若確為同實體請確認是否改用 [[三天]]

## 流便（人物）
query:
- 待建立詞：流便
- 出現位置：約書亞記 第1章
- 候選類型：人物
- 本章上下文：第12節「約書亞對流便人、迦得人，和瑪拿西半支派的人說」。

字面解析：對上既有「流便」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 流便 | 0.559 | link_folder/人物/流便.md |
| 2 | 十二支派起源 | 0.529 | link_folder/神學/十二支派起源.md |
| 3 | 兩支派半求河東之地為業 | 0.518 | link_folder/事件/兩支派半求河東之地為業.md |
| 4 | 瑪拿西 | 0.485 | link_folder/人物/瑪拿西.md |
| 5 | 分地的十位支派首領 | 0.485 | link_folder/主題/分地的十位支派首領.md |

判定：✅ 建議使用既有條目 [[流便]]（同名／字面對應）

## 迦得（萬幸）（人物）
query:
- 待建立詞：迦得（萬幸）
- 出現位置：約書亞記 第1章
- 候選類型：人物
- 本章上下文：第12節「迦得人」；GT 說迦得字義是「侵略者」、「軍隊」、「財富」，是利亞的使女悉帕所生。

字面解析：對上既有「迦得（萬幸）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 迦得（萬幸） | 0.668 | link_folder/人物/迦得（萬幸）.md |
| 2 | 迦得（幸運） | 0.657 | link_folder/原文/迦得（幸運）.md |
| 3 | 悉帕 | 0.509 | link_folder/人物/悉帕.md |
| 4 | 迦勒 | 0.479 | link_folder/人物/迦勒.md |
| 5 | 迦南人 | 0.475 | link_folder/人物/迦南人.md |

判定：✅ 建議使用既有條目 [[迦得（萬幸）]]（同名／字面對應）

## 瑪拿西（人物）
query:
- 待建立詞：瑪拿西
- 出現位置：約書亞記 第1章
- 候選類型：人物
- 本章上下文：第12節「瑪拿西半支派的人」；GT 說瑪拿西字義是「導致遺忘」，是約瑟的長子。

字面解析：對上既有「瑪拿西」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 瑪拿西 | 0.702 | link_folder/人物/瑪拿西.md |
| 2 | 瑪拿西（使之忘了） | 0.643 | link_folder/原文/瑪拿西（使之忘了）.md |
| 3 | 瑪吉 | 0.519 | link_folder/人物/瑪吉.md |
| 4 | 收納以法蓮與瑪拿西 | 0.512 | link_folder/歷史/收納以法蓮與瑪拿西.md |
| 5 | 瑪拿西半支派為何留在河東 | 0.482 | link_folder/解經爭議/瑪拿西半支派為何留在河東.md |

判定：✅ 建議使用既有條目 [[瑪拿西]]（同名／字面對應）

## 兩支派半求河東之地為業（事件）
query:
- 待建立詞：兩支派半求河東之地為業
- 出現位置：約書亞記 第1章
- 候選類型：事件
- 本章上下文：第12至15節約書亞要他們「追念耶和華的僕人摩西所吩咐你們的話」，並重申妻子孩子牲畜留在河東、勇士先過河的條件；各家都回指民32 與申3:18-20 的約定。
- 經文用詞：半支派

字面解析：對上既有「兩支派半求河東之地為業」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 兩支派半求河東之地為業 | 0.694 | link_folder/事件/兩支派半求河東之地為業.md |
| 2 | 瑪拿西半支派為何留在河東 | 0.603 | link_folder/解經爭議/瑪拿西半支派為何留在河東.md |
| 3 | 過河的四萬人與留守的七萬人 | 0.557 | link_folder/主題/過河的四萬人與留守的七萬人.md |
| 4 | 河東之地是神的旨意還是神的允許 | 0.550 | link_folder/解經爭議/河東之地是神的旨意還是神的允許.md |
| 5 | 勇士（cha.yil） | 0.549 | link_folder/原文/勇士（cha.yil）.md |

判定：✅ 建議使用既有條目 [[兩支派半求河東之地為業]]（同名／字面對應）

## 得享平安（nu.ach）（原文）
query:
- 待建立詞：得享平安（nu.ach）
- 出現位置：約書亞記 第1章
- 候選類型：原文
- 本章上下文：第13節「使你們得享平安」與第15節「像你們一樣得享平安」，STEP 第13節為 me.Ni.ach（H5117 nu.ach，Hiphil 分詞）。GT 說原文作「休息」，型態是單數陽性分詞，並說「得享平安」原文是「得享安息」。

字面解析：對上既有「得享平安（nu.ach）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 得享平安（nu.ach） | 0.659 | link_folder/原文/得享平安（nu.ach）.md |
| 2 | 平安（shalom） | 0.486 | link_folder/原文/平安（shalom）.md |
| 3 | 安息（第七日的歇息） | 0.459 | link_folder/原文/安息（第七日的歇息）.md |
| 4 | 平安的約 | 0.441 | link_folder/主題/平安的約.md |
| 5 | 安慰與安息 | 0.438 | link_folder/主題/安慰與安息.md |

判定：✅ 建議使用既有條目 [[得享平安（nu.ach）]]（同名／字面對應）

## 勇士（cha.yil）（原文）
query:
- 待建立詞：勇士（cha.yil）
- 出現位置：約書亞記 第1章
- 候選類型：原文
- 本章上下文：第14節「一切大能的勇士」，STEP 為 gi.bo.Rei ha./Cha.yil（H1368 gib.bor＋H2428G cha.yil）。GT 說原文是「強壯的軍隊」；GT《啟導本》說是年滿20歲能使用兵器英勇作戰的人。
- 經文用詞：大能的勇士

字面解析：對上既有「勇士（cha.yil）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 勇士（cha.yil） | 0.612 | link_folder/原文/勇士（cha.yil）.md |
| 2 | 二十歲以外能打仗的 | 0.516 | link_folder/主題/二十歲以外能打仗的.md |
| 3 | 帶兵器（cha.lats） | 0.477 | link_folder/原文/帶兵器（cha.lats）.md |
| 4 | 耶和華是戰士 | 0.470 | link_folder/神學/耶和華是戰士.md |
| 5 | 膽壯與大能同一字根（cha.zaq） | 0.468 | link_folder/原文/膽壯與大能同一字根（cha.zaq）.md |

判定：✅ 建議使用既有條目 [[勇士（cha.yil）]]（同名／字面對應）

## 帶著兵器（cha.mush）（原文）
query:
- 待建立詞：帶著兵器（cha.mush）
- 出現位置：約書亞記 第1章
- 候選類型：原文
- 本章上下文：第14節「都要帶著兵器」，STEP 為 cha.mu.Shim（H2571，簡要詞典義 cha.mush: armed，本節譯義 arrayed for battle）。GT《綜合解讀》說「帶著兵器 חָמַשׁ」原文的字根是「第五 חֹמֶשׁ」，可能當時採五人一組的戰鬥隊形；GT《聖經精讀本》同樣說派生於指數字五的詞根，含有「準備參戰」之意。

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 以色列人帶兵器 | 0.575 | 0.069 | link_folder/歷史/以色列人帶兵器.md |
| 2 | 帶兵器（cha.lats） | 0.605 | 0.054 | link_folder/原文/帶兵器（cha.lats）.md |
| 3 | 勇士（cha.yil） | 0.548 | 0.025 | link_folder/原文/勇士（cha.yil）.md |
| 4 | 車兵長 | 0.456 | 0.017 | link_folder/原文/車兵長.md |
| 5 | 以色列人的軍隊 | 0.510 | 0.016 | link_folder/神學/以色列人的軍隊.md |

rerank_margin: 0.016 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=原文 vs 條目=歷史），若確為同實體請確認是否改用 [[以色列人帶兵器]]

## 違背命令（ma.rah）（原文）
query:
- 待建立詞：違背命令（ma.rah）
- 出現位置：約書亞記 第1章
- 候選類型：原文
- 本章上下文：第18節「無論什麼人違背你的命令」，STEP 為 yam.Reh（H4784 ma.rah，Hiphil）。GT《丁道爾聖經注釋》說動詞違背(希伯來：yamreh)在約書亞記只出現過這一次，申命記則用它描述加低斯巴尼亞的背叛與忤逆之子。
- 經文用詞：違背

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 加低斯巴尼亞事件 | 0.484 | 0.093 | link_folder/歷史/加低斯巴尼亞事件.md |
| 2 | 惹 | 0.505 | 0.076 | link_folder/原文/惹.md |
| 3 | 咒詛擾亂責罰（me.e.rah、me.hu.mah、mig.e.ret） | 0.533 | 0.042 | link_folder/原文/咒詛擾亂責罰（me.e.rah、me.hu.mah、mig.e.ret）.md |
| 4 | 迦南滅絕命令的歷史範圍 | 0.481 | 0.042 | link_folder/解經爭議/迦南滅絕命令的歷史範圍.md |
| 5 | 越過耶和華的口（peh） | 0.529 | 0.039 | link_folder/原文/越過耶和華的口（peh）.md |

rerank_margin: 0.017 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=原文 vs 條目=歷史），若確為同實體請確認是否改用 [[加低斯巴尼亞事件]]

## 為業（ye.ru.shah）（原文）
query:
- 待建立詞：為業（ye.ru.shah）
- 出現位置：約書亞記 第1章
- 候選類型：原文
- 本章上下文：第11節「進去得耶和華─你們神賜你們為業之地」與第15節「得著耶和華─你們神所賜他們為業之地，那時才可以回你們所得之地，承受為業」。STEP 顯示第11節兩次、第15節兩次都是動詞 la./Re.shet、le./rish.Ta/h、ve./ya.re.Shu、vi./rish.Tem（H3423H，簡要詞典義 ya.rash: to possess: take），與申2:24、申3:18 同一個 Extended Strong。GT 指出整章出現四次「得、繼承[03423]」。

字面解析：對上既有「為業（ye.ru.shah）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 為業（ye.ru.shah） | 0.692 | link_folder/原文/為業（ye.ru.shah）.md |
| 2 | 這地必落給你們為業（na.phal） | 0.591 | link_folder/原文/這地必落給你們為業（na.phal）.md |
| 3 | 產業（na.cha.lah） | 0.576 | link_folder/原文/產業（na.cha.lah）.md |
| 4 | 業地（a.chuz.zah） | 0.558 | link_folder/原文/業地（a.chuz.zah）.md |
| 5 | 眷顧（da.rash） | 0.537 | link_folder/原文/眷顧（da.rash）.md |

判定：✅ 建議使用既有條目 [[為業（ye.ru.shah）]]（同名／字面對應）

## 產業（na.cha.lah）（原文）
query:
- 待建立詞：產業（na.cha.lah）
- 出現位置：約書亞記 第1章
- 候選類型：原文
- 本章上下文：第6節「因為你必使這百姓承受那地為業」，STEP 為 tan.Chil（H5157，簡要詞典義 na.chal: to inherit，Hiphil）——使役語態，動作者是約書亞。GT 譯作「使這百姓繼承」。與第11、15節的 ya.rash 屬不同字根。
- 經文用詞：承受那地為業

字面解析：對上既有「產業（na.cha.lah）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 產業（na.cha.lah） | 0.650 | link_folder/原文/產業（na.cha.lah）.md |
| 2 | 這地必落給你們為業（na.phal） | 0.561 | link_folder/原文/這地必落給你們為業（na.phal）.md |
| 3 | 業地（a.chuz.zah） | 0.549 | link_folder/原文/業地（a.chuz.zah）.md |
| 4 | 為業（ye.ru.shah） | 0.511 | link_folder/原文/為業（ye.ru.shah）.md |
| 5 | 必不撇下你，也不丟棄你（ra.phah 與 a.zav） | 0.507 | link_folder/原文/必不撇下你，也不丟棄你（ra.phah 與 a.zav）.md |

判定：✅ 建議使用既有條目 [[產業（na.cha.lah）]]（同名／字面對應）

## 候選互查（本章內部，⚠＝彼此相似 ≥ 0.8）
（無 ≥ 門檻的配對）
