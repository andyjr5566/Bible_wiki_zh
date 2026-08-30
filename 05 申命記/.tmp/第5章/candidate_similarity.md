<!-- candidate_similarity_meta
schema_version: 1
book: 申命記
chapter: 5
candidate_sha256: 233a7de478270610d498b76f09eddb5ece212b501919b9a7bf5f3dd6ab5b611f
embedding_model: nvidia/nemotron-3-embed-1b
embedding_index_fingerprint: ac20a6286e9e117d
link_index_sha256: a1b45445c201829833b02ea20a52a828ca31dada4db73ef47e80e738f36a7fa1
homonyms_sha256: b8d042ea4f51253052128b2b289befdcf00b53c88237b67050f3252242c41ab8
rerank_model: nvidia/llama-nemotron-rerank-vl-1b-v2:free
rerank_policy_version: 2026.08.4
calibration_sha256: f63b1218023371bbbece396422aa7a02025bba0da119b49cae75232755734211
rerank_status: success
rerankable_candidates: 11
rerank_attempted: 11
rerank_succeeded: 11
rerank_retrieve_top_k: 20
rerank_score_observed: 0.002-0.408
-->

# 候選語義近鄰報告：申命記 第5章

- 檢索模型：nvidia/nemotron-3-embed-1b｜重排模型：nvidia/llama-nemotron-rerank-vl-1b-v2:free（未校準/保守模式）｜全庫 2930 條
- 規則說明：字面確切匹配直接通過；其餘候選先檢索 Top 20 名再由 Reranker 重排，取前 5 名顯示。
  治理優先：同名歧義（D類）與分類不相容永遠標 ⚠。
  重排模型未校準時，⚠ 由檢索相似度規則（≥0.50 且 top-1 非同實體）決定，重排名次只當附加證據。
  字面解析：列 resolver 實際比對結果——標「請確認」者務必人工核實。

## 摩西（人物）
query:
- 待建立詞：摩西
- 出現位置：申命記 第5章
- 候選類型：人物
- 本章上下文：第1節「摩西將以色列眾人召了來」；第5節「那時我站在耶和華和你們中間」；KC：Moses calls Israel together. He is a picture of the Lord Jesus as the Teacher who speaks God's Word.

字面解析：對上既有「摩西」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 摩西 | 0.563 | link_folder/人物/摩西.md |
| 2 | 摩西上山見神 | 0.543 | link_folder/事件/摩西上山見神.md |
| 3 | 摩西的呼召與差遣 | 0.531 | link_folder/神學/摩西的呼召與差遣.md |
| 4 | 稱摩西為我主 | 0.527 | link_folder/主題/稱摩西為我主.md |
| 5 | 被拒絕的拯救者摩西 | 0.491 | link_folder/互文/被拒絕的拯救者摩西.md |

判定：✅ 建議使用既有條目 [[摩西]]（同名／字面對應）

## 何烈山（地點）
query:
- 待建立詞：何烈山
- 出現位置：申命記 第5章
- 候選類型：地點
- 本章上下文：第2節「耶和華─我們的神在何烈山與我們立約」；STEP：be./cho.Rev（H2722）；BH：Horeb is another name for Mount Sinai, where Moses received the Ten Commandments.

字面解析：對上既有「何烈山」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 何烈山 | 0.694 | link_folder/地點/何烈山.md |
| 2 | 西乃山 | 0.666 | link_folder/地點/西乃山.md |
| 3 | 何烈 | 0.644 | link_folder/地點/何烈.md |
| 4 | 神的山 | 0.639 | link_folder/地點/神的山.md |
| 5 | 西乃 | 0.569 | link_folder/地點/西乃.md |

判定：✅ 建議使用既有條目 [[何烈山]]（同名／字面對應）

## 西乃之約（神學）
query:
- 待建立詞：西乃之約
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：第2-3節；STEP：ka.Rat（H3772H，簡要詞典義 to cut: make(covenant)）＋be.Rit（H1285）；GT《啟導本》：這是西奈之約的重申，必須成為他們生活的守則、信仰的依憑。
- 經文用詞：與我們立約

字面解析：對上既有「西乃之約」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 西乃之約 | 0.655 | link_folder/神學/西乃之約.md |
| 2 | 西乃山立約 | 0.623 | link_folder/背景/西乃山立約.md |
| 3 | 立約儀式 | 0.611 | link_folder/事件/立約儀式.md |
| 4 | 立約 | 0.570 | link_folder/主題/立約.md |
| 5 | 盟約 | 0.562 | link_folder/主題/盟約.md |

判定：✅ 建議使用既有條目 [[西乃之約]]（同名／字面對應）

## 十誡（神學）
query:
- 待建立詞：十誡
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：第6-21節復述十誡；第22節「這些話是耶和華…大聲曉諭你們全會眾的」；STEP：ha./de.va.Rim（H1697G，字面「這些話」）；GT《精讀本》：十誡是所有律法的核心與本質,並不是單純的律法,乃是神的「約」。
- 經文用詞：這些話

字面解析：對上既有「十誡」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 十誡 | 0.648 | link_folder/神學/十誡.md |
| 2 | 十句話 | 0.645 | link_folder/原文/十句話.md |
| 3 | 盟約 | 0.619 | link_folder/主題/盟約.md |
| 4 | 神頒布十誡 | 0.571 | link_folder/事件/神頒布十誡.md |
| 5 | 我是耶和華你的神 | 0.560 | link_folder/神學/我是耶和華你的神.md |

判定：✅ 建議使用既有條目 [[十誡]]（同名／字面對應）

## 十誡的條分法（神學）
query:
- 待建立詞：十誡的條分法
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：CT 說第五誡「刻在第一塊石頭，與有關神的第一至第四誡同列」；KC 說第16節起是第二塊法版的開始（From this verse begins the second table of the law with six commandments）；GT《啟導本》另按兩兩配對分組。

字面解析：對上既有「十誡的條分法」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 十誡的條分法 | 0.652 | link_folder/神學/十誡的條分法.md |
| 2 | 十誡 | 0.606 | link_folder/神學/十誡.md |
| 3 | 摩西鑿石版（第二次法版） | 0.562 | link_folder/事件/摩西鑿石版（第二次法版）.md |
| 4 | 石版的應許（出24：12） | 0.518 | link_folder/互文/石版的應許（出24：12）.md |
| 5 | 石版 | 0.503 | link_folder/文化/石版.md |

判定：✅ 建議使用既有條目 [[十誡的條分法]]（同名／字面對應）

## 神頒布十誡（事件）
query:
- 待建立詞：神頒布十誡
- 出現位置：申命記 第5章
- 候選類型：事件
- 本章上下文：第4、22節「耶和華在山上，從火中…大聲曉諭你們全會眾的」「他就把這話寫在兩塊石版上」；本章是摩西對新一代重述何烈山頒律當日的情形。

字面解析：對上既有「神頒布十誡」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 神頒布十誡 | 0.660 | link_folder/事件/神頒布十誡.md |
| 2 | 摩西上山領石版 | 0.652 | link_folder/事件/摩西上山領石版.md |
| 3 | 石版的應許（出24：12） | 0.650 | link_folder/互文/石版的應許（出24：12）.md |
| 4 | 十誡 | 0.631 | link_folder/神學/十誡.md |
| 5 | 石版 | 0.610 | link_folder/文化/石版.md |

判定：✅ 建議使用既有條目 [[神頒布十誡]]（同名／字面對應）

## 律例（choq）（原文）
query:
- 待建立詞：律例（choq）
- 出現位置：申命記 第5章
- 候選類型：原文
- 本章上下文：第1、31節「我今日曉諭你們的律例典章」「我要將一切誡命、律例、典章傳給你」；STEP：ha./chu.Kim（H2706G，簡要詞典義 statute: decree）；CT：『律例』指律法，是神向人的要求。
- 經文用詞：律例

字面解析：對上既有「律例（choq）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 律例（choq） | 0.679 | link_folder/原文/律例（choq）.md |
| 2 | 典章 | 0.558 | link_folder/神學/典章.md |
| 3 | 法度（e.dah） | 0.546 | link_folder/原文/法度（e.dah）.md |
| 4 | 講律法（ba.ar） | 0.476 | link_folder/原文/講律法（ba.ar）.md |
| 5 | 約書 | 0.454 | link_folder/神學/約書.md |

判定：✅ 建議使用既有條目 [[律例（choq）]]（同名／字面對應）

## 典章（神學）
query:
- 待建立詞：典章
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：第1、31節與「律例」成對出現；STEP：ha./mish.pa.Tim（H4941G，簡要詞典義 justice: judgement）；CT：『典章』指審判，是神對人是否遵行律法的判定。
- 經文用詞：典章

字面解析：對上既有「典章」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 典章 | 0.683 | link_folder/神學/典章.md |
| 2 | 判斷（mish.pat） | 0.604 | link_folder/原文/判斷（mish.pat）.md |
| 3 | 律例（choq） | 0.549 | link_folder/原文/律例（choq）.md |
| 4 | 律法與公義 | 0.540 | link_folder/主題/律法與公義.md |
| 5 | 審判不可行不義按公義審判 | 0.517 | link_folder/主題/審判不可行不義按公義審判.md |

判定：✅ 建議使用既有條目 [[典章]]（同名／字面對應）

## 中保（神學）
query:
- 待建立詞：中保
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：第5節「那時我站在耶和華和你們中間，要將耶和華的話傳給你們」；第27節百姓請摩西代聽；GT《精讀本》：這仲裁者的原理在舊約時代人是不可缺的,預表了新約時代神人之間的惟一中保耶穌基督的事工。
- 經文用詞：站在耶和華和你們中間

字面解析：對上既有「中保」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 中保 | 0.695 | link_folder/神學/中保.md |
| 2 | 提前2：5 | 0.626 | link_folder/互文/提前2：5.md |
| 3 | 耶和華的使者 | 0.537 | link_folder/神學/耶和華的使者.md |
| 4 | 先知 | 0.519 | link_folder/主題/先知.md |
| 5 | 耶和華的話臨到 | 0.517 | link_folder/神學/耶和華的話臨到.md |

判定：✅ 建議使用既有條目 [[中保]]（同名／字面對應）

## 為奴之家（主題）
query:
- 待建立詞：為奴之家
- 出現位置：申命記 第5章
- 候選類型：主題
- 本章上下文：第6節「曾將你從埃及地為奴之家領出來」；STEP：mi./Beit 'a.va.Dim（H1004B＋H5650，字面「奴僕之家」）；BH："House of slavery" refers to the oppressive environment in Egypt.
- 經文用詞：為奴之家

字面解析：對上既有「為奴之家」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 為奴之家 | 0.652 | link_folder/主題/為奴之家.md |
| 2 | 古代近東奴隸制度 | 0.525 | link_folder/背景/古代近東奴隸制度.md |
| 3 | 奴僕 | 0.507 | link_folder/原文/奴僕.md |
| 4 | 波提乏的家 | 0.500 | link_folder/地點/波提乏的家.md |
| 5 | 奴僕與自由 | 0.494 | link_folder/主題/奴僕與自由.md |

判定：✅ 建議使用既有條目 [[為奴之家]]（同名／字面對應）

## 奴僕（原文）
query:
- 待建立詞：奴僕
- 出現位置：申命記 第5章
- 候選類型：原文
- 本章上下文：第15節「你也要記念你在埃及地作過奴僕」；STEP：'E.ved（H5650）；CT：意指應當回想從前那種日以繼夜，不得休息的苦工。
- 經文用詞：作過奴僕

字面解析：對上既有「奴僕」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 為奴之家 | 0.605 | link_folder/主題/為奴之家.md |
| 2 | 奴僕 | 0.533 | link_folder/原文/奴僕.md |
| 3 | 古代近東奴隸制度 | 0.494 | link_folder/背景/古代近東奴隸制度.md |
| 4 | 希伯來奴僕的律例 | 0.492 | link_folder/事件/希伯來奴僕的律例.md |
| 5 | 亞伯拉罕後裔寄居受苦的預言 | 0.492 | link_folder/互文/亞伯拉罕後裔寄居受苦的預言.md |

判定：✅ 建議使用既有條目 [[奴僕]]（同名／字面對應）

## 埃及（地點）
query:
- 待建立詞：埃及
- 出現位置：申命記 第5章
- 候選類型：地點
- 本章上下文：第6節「從埃及地為奴之家領出來」；第15節「你在埃及地作過奴僕」；本章把出埃及同時當作十誡的序言與安息日誡命的理由。

字面解析：對上既有「埃及」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 為奴之家 | 0.671 | link_folder/主題/為奴之家.md |
| 2 | 埃及 | 0.644 | link_folder/地點/埃及.md |
| 3 | 出埃及為要事奉神 | 0.580 | link_folder/神學/出埃及為要事奉神.md |
| 4 | 出埃及 | 0.573 | link_folder/歷史/出埃及.md |
| 5 | 出埃及記一章 | 0.553 | link_folder/互文/出埃及記一章.md |

判定：✅ 建議使用既有條目 [[埃及]]（同名／字面對應）

## 出埃及（歷史）
query:
- 待建立詞：出埃及
- 出現位置：申命記 第5章
- 候選類型：歷史
- 本章上下文：第6、15節；STEP：ho.tze.Ti./kha 與 va/i.yo.Tzi.'a./kha 同為 H3318H（ya.tsa）；GT《精讀本》：在這裡我們要注意授予十誡的耶和華並不是憑著審判者的威嚴,乃是憑著救贖主的慈愛來宣告自己的事實。
- 經文用詞：將你從那裡領出來

字面解析：對上既有「出埃及」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 出埃及 | 0.591 | link_folder/歷史/出埃及.md |
| 2 | 我是耶和華你的神 | 0.579 | link_folder/神學/我是耶和華你的神.md |
| 3 | 出埃及為要事奉神 | 0.547 | link_folder/神學/出埃及為要事奉神.md |
| 4 | 神的拯救 | 0.546 | link_folder/神學/神的拯救.md |
| 5 | 為奴之家 | 0.535 | link_folder/主題/為奴之家.md |

判定：✅ 建議使用既有條目 [[出埃及]]（同名／字面對應）

## 不可為自己雕刻偶像（神學）
query:
- 待建立詞：不可為自己雕刻偶像
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：第8-9節；STEP：fe.sel（H6459，簡要詞典義 idol）；CT：『雕刻』指包括木刻、石雕、泥塑、各種金屬的鑄造，以及繪畫、刺繡、針織、各種手工等。
- 經文用詞：不可為自己雕刻偶像

字面解析：對上既有「不可為自己雕刻偶像」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 不可為自己雕刻偶像 | 0.638 | link_folder/神學/不可為自己雕刻偶像.md |
| 2 | 不能看不能聽不能吃不能聞的神 | 0.527 | link_folder/主題/不能看不能聽不能吃不能聞的神.md |
| 3 | 只聽見聲音卻沒有看見形像（te.mu.nah） | 0.485 | link_folder/神學/只聽見聲音卻沒有看見形像（te.mu.nah）.md |
| 4 | 不可偷盜 | 0.477 | link_folder/神學/不可偷盜.md |
| 5 | 古代近東偶像崇拜 | 0.473 | link_folder/背景/古代近東偶像崇拜.md |

判定：✅ 建議使用既有條目 [[不可為自己雕刻偶像]]（同名／字面對應）

## 只聽見聲音卻沒有看見形像（te.mu.nah）（神學）
query:
- 待建立詞：只聽見聲音卻沒有看見形像（te.mu.nah）
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：第8節「也不可做什麼形像」；STEP：te.mu.Nah（H8544，簡要詞典義 likeness），與申4:12、15-16、23、25 同一個字；KC：God is a spirit and cannot be represented by anything.
- 經文用詞：也不可做什麼形像

字面解析：對上既有「只聽見聲音卻沒有看見形像（te.mu.nah）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 只聽見聲音卻沒有看見形像（te.mu.nah） | 0.699 | link_folder/神學/只聽見聲音卻沒有看見形像（te.mu.nah）.md |
| 2 | 不能看不能聽不能吃不能聞的神 | 0.517 | link_folder/主題/不能看不能聽不能吃不能聞的神.md |
| 3 | 天上事的形狀和影像（來8：5） | 0.452 | link_folder/互文/天上事的形狀和影像（來8：5）.md |
| 4 | 神與摩西面對面明說 | 0.442 | link_folder/神學/神與摩西面對面明說.md |
| 5 | 不可為自己雕刻偶像 | 0.440 | link_folder/神學/不可為自己雕刻偶像.md |

判定：✅ 建議使用既有條目 [[只聽見聲音卻沒有看見形像（te.mu.nah）]]（同名／字面對應）

## 忌邪的神（神學）
query:
- 待建立詞：忌邪的神
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：第9節「因為我耶和華─你的神是忌邪的神」；STEP：'el ka.Na'（H410G＋H7067H，簡要詞典義 jealous）；CT：按原文意指嫉妒的神，表示祂忌恨任何人在祂以外另有別神。

字面解析：對上既有「忌邪的神」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 忌邪的神 | 0.712 | link_folder/神學/忌邪的神.md |
| 2 | 忌邪（嫉妒） | 0.656 | link_folder/原文/忌邪（嫉妒）.md |
| 3 | 除了我以外 | 0.518 | link_folder/原文/除了我以外.md |
| 4 | 除了我以外你不可有別的神 | 0.513 | link_folder/神學/除了我以外你不可有別的神.md |
| 5 | 林後11：2 | 0.496 | link_folder/互文/林後11：2.md |

判定：✅ 建議使用既有條目 [[忌邪的神]]（同名／字面對應）

## 追討罪自父及子直到三四代（神學）
query:
- 待建立詞：追討罪自父及子直到三四代
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：第9節；STEP：Po.ked（H6485I，簡要詞典義 to reckon: visit）、shi.le.Shim（H8029 第三代）、ri.be.'Im（H7256 第四代）；GT《串珠》：這裡不是指過犯的本身，而是指罪惡的後果。
- 經文用詞：自父及子，直到三、四代

字面解析：對上既有「追討罪自父及子直到三四代」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 追討罪自父及子直到三四代 | 0.693 | link_folder/神學/追討罪自父及子直到三四代.md |
| 2 | 禍延三四代 | 0.649 | link_folder/解經爭議/禍延三四代.md |
| 3 | 神公義追討與禍延子孫的釋經探討 | 0.610 | link_folder/解經爭議/神公義追討與禍延子孫的釋經探討.md |
| 4 | 咒罵父母 | 0.499 | link_folder/神學/咒罵父母.md |
| 5 | 你們的罪必追上你們 | 0.493 | link_folder/神學/你們的罪必追上你們.md |

判定：✅ 建議使用既有條目 [[追討罪自父及子直到三四代]]（同名／字面對應）

## 發慈愛直到千代（神學）
query:
- 待建立詞：發慈愛直到千代
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：第10節；STEP：che.sed（H2617A，簡要詞典義 kindness）＋la./'a.la.Fim（H505G，字面「向千」）；CT：『發慈愛』按原文的文法，含有『繼續不斷地傾倒神那絕對的愛』的意思。
- 經文用詞：我必向他們發慈愛，直到千代

字面解析：對上既有「發慈愛直到千代」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 發慈愛直到千代 | 0.729 | link_folder/神學/發慈愛直到千代.md |
| 2 | 神的慈愛引領 | 0.529 | link_folder/神學/神的慈愛引領.md |
| 3 | 慈愛誠實 | 0.529 | link_folder/原文/慈愛誠實.md |
| 4 | 神的憐憫 | 0.507 | link_folder/神學/神的憐憫.md |
| 5 | 神的性情宣告（耶和華有憐憫有恩典） | 0.498 | link_folder/神學/神的性情宣告（耶和華有憐憫有恩典）.md |

判定：✅ 建議使用既有條目 [[發慈愛直到千代]]（同名／字面對應）

## 不可妄稱耶和華你神的名（神學）
query:
- 待建立詞：不可妄稱耶和華你神的名
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：第11節；STEP：ti.Sa'（H5375G，簡要詞典義 to lift: raise）＋la./Shav'（H7723H，簡要詞典義 vanity: vain）；GT《雷氏》：即為了錯誤的目的，如操縱人、行法術，或其它自私的欲望。
- 經文用詞：不可妄稱耶和華─你神的名

字面解析：對上既有「不可妄稱耶和華你神的名」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 不可妄稱耶和華你神的名 | 0.633 | link_folder/神學/不可妄稱耶和華你神的名.md |
| 2 | 妄稱 | 0.613 | link_folder/原文/妄稱.md |
| 3 | 耶和華 | 0.551 | link_folder/神學/耶和華.md |
| 4 | 耶和華聖名的啟示 | 0.528 | link_folder/神學/耶和華聖名的啟示.md |
| 5 | 耶和華神的名字 | 0.528 | link_folder/神學/耶和華神的名字.md |

判定：✅ 建議使用既有條目 [[不可妄稱耶和華你神的名]]（同名／字面對應）

## 安息日（神學）
query:
- 待建立詞：安息日
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：第12-15節；STEP：ha./sha.Bat（H7676）；KC：The sabbath command is the core command of obedience. All other commandments can be understood even by unbelievers.
- 經文用詞：守安息日為聖日

字面解析：對上既有「安息日」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 安息日 | 0.595 | link_folder/神學/安息日.md |
| 2 | 當記念安息日守為聖日 | 0.566 | link_folder/神學/當記念安息日守為聖日.md |
| 3 | 安息日的設立 | 0.535 | link_folder/神學/安息日的設立.md |
| 4 | 安息 | 0.529 | link_folder/神學/安息.md |
| 5 | 安息（第七日的歇息） | 0.514 | link_folder/原文/安息（第七日的歇息）.md |

判定：✅ 建議使用既有條目 [[安息日]]（同名／字面對應）

## 當孝敬父母（神學）
query:
- 待建立詞：當孝敬父母
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：第16節；STEP：ka.Bed（H3513G，簡要詞典義 to honor）；CT：『使你得福』這是十誡中唯一可得福分的應許。
- 經文用詞：孝敬父母

字面解析：對上既有「當孝敬父母」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 當孝敬父母 | 0.594 | link_folder/神學/當孝敬父母.md |
| 2 | 咒罵父母 | 0.506 | link_folder/神學/咒罵父母.md |
| 3 | 弗6：2-3 | 0.486 | link_folder/互文/弗6：2-3.md |
| 4 | 尊敬老人 | 0.479 | link_folder/主題/尊敬老人.md |
| 5 | 箴30：11-14 | 0.463 | link_folder/互文/箴30：11-14.md |

判定：✅ 建議使用既有條目 [[當孝敬父母]]（同名／字面對應）

## 不可殺人（神學）
query:
- 待建立詞：不可殺人
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：第17節；STEP：tre.Tzach（H7523，ra.tsach，簡要詞典義 to murder）；BH：The Hebrew word used here for "murder" is "ratsach," which specifically refers to unlawful killing, distinguishing it from killing in war or capital punishment.

字面解析：對上既有「不可殺人」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 殺人（ratsach） | 0.724 | link_folder/原文/殺人（ratsach）.md |
| 2 | 不可殺人 | 0.594 | link_folder/神學/不可殺人.md |
| 3 | 謀殺與誤殺的區分 | 0.479 | link_folder/神學/謀殺與誤殺的區分.md |
| 4 | 死刑的罪行 | 0.472 | link_folder/神學/死刑的罪行.md |
| 5 | 擾害（tsa.rar） | 0.466 | link_folder/原文/擾害（tsa.rar）.md |

判定：✅ 建議使用既有條目 [[不可殺人]]（同名／字面對應）

## 不可姦淫（神學）
query:
- 待建立詞：不可姦淫
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：第18節；STEP：tne.'Af（H5003，na.aph，簡要詞典義 to commit adultery）；GT《串珠》：先知屢用「淫亂」象徵以色列民對神的不貞。

字面解析：對上既有「不可姦淫」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 姦淫 | 0.624 | link_folder/原文/姦淫.md |
| 2 | 不可姦淫 | 0.575 | link_folder/神學/不可姦淫.md |
| 3 | 不可辱沒女兒使她為娼妓 | 0.528 | link_folder/主題/不可辱沒女兒使她為娼妓.md |
| 4 | 行起淫亂（za.nah） | 0.523 | link_folder/原文/行起淫亂（za.nah）.md |
| 5 | 褻瀆（cha.lal） | 0.518 | link_folder/原文/褻瀆（cha.lal）.md |

判定：✅ 建議使用既有條目 [[不可姦淫]]（同名／字面對應）

## 不可偷盜（神學）
query:
- 待建立詞：不可偷盜
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：第19節；STEP：tge.No（H1589，ga.nav，簡要詞典義 to steal）；KC：Stealing is taking away from another what that other person has received from the Lord and using for ourselves.

字面解析：對上既有「不可偷盜」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 不可偷盜 | 0.601 | link_folder/神學/不可偷盜.md |
| 2 | 創3：19 | 0.511 | link_folder/互文/創3：19.md |
| 3 | 偷 | 0.470 | link_folder/原文/偷.md |
| 4 | 不可貪戀 | 0.451 | link_folder/神學/不可貪戀.md |
| 5 | 出20：15 | 0.427 | link_folder/互文/出20：15.md |

判定：✅ 建議使用既有條目 [[不可偷盜]]（同名／字面對應）

## 不可作假見證陷害人（神學）
query:
- 待建立詞：不可作假見證陷害人
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：第20節；STEP：'ed Shav'（H5707 witness＋H7723G，簡要詞典義 vanity: false）；GT《串珠》：指在法庭上給假口供。

字面解析：對上既有「不可作假見證陷害人」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 不可作假見證陷害人 | 0.535 | link_folder/神學/不可作假見證陷害人.md |
| 2 | 聯手 | 0.477 | link_folder/原文/聯手.md |
| 3 | 出20：16 | 0.459 | link_folder/互文/出20：16.md |
| 4 | 謠言 | 0.445 | link_folder/原文/謠言.md |
| 5 | 箴6：16-19 | 0.434 | link_folder/互文/箴6：16-19.md |

判定：✅ 建議使用既有條目 [[不可作假見證陷害人]]（同名／字面對應）

## 不可貪戀（神學）
query:
- 待建立詞：不可貪戀
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：第21節；STEP：tach.Mod（H2530A）與 tit.'a.Veh（H183）兩個不同的動詞；KC：This commandment lays bare the germ of sin.
- 經文用詞：不可貪戀人的妻子

字面解析：對上既有「不可貪戀」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 不可貪戀 | 0.536 | link_folder/神學/不可貪戀.md |
| 2 | 貪戀 | 0.534 | link_folder/原文/貪戀.md |
| 3 | 不可姦淫 | 0.521 | link_folder/神學/不可姦淫.md |
| 4 | 褻瀆（cha.lal） | 0.499 | link_folder/原文/褻瀆（cha.lal）.md |
| 5 | 無子女而死的刑罰 | 0.492 | link_folder/神學/無子女而死的刑罰.md |

判定：✅ 建議使用既有條目 [[不可貪戀]]（同名／字面對應）

## 石版（文化）
query:
- 待建立詞：石版
- 出現位置：申命記 第5章
- 候選類型：文化
- 本章上下文：第22節「他就把這話寫在兩塊石版上，交給我了」；STEP：she.Nei lu.Chot 'a.va.Nim（H8147＋H3871＋H68G）；GT《精讀本》：對聖經與希伯來人而言,數字「2」意味著證據或確實性。
- 經文用詞：兩塊石版

字面解析：對上既有「石版」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 石版 | 0.662 | link_folder/文化/石版.md |
| 2 | 石版的應許（出24：12） | 0.565 | link_folder/互文/石版的應許（出24：12）.md |
| 3 | 摩西鑿石版（第二次法版） | 0.522 | link_folder/事件/摩西鑿石版（第二次法版）.md |
| 4 | 雙語命名_亞蘭語伊迦爾撒哈杜他_希伯來語迦累得 | 0.517 | link_folder/文化/雙語命名_亞蘭語伊迦爾撒哈杜他_希伯來語迦累得.md |
| 5 | 法版 | 0.499 | link_folder/原文/法版.md |

判定：✅ 建議使用既有條目 [[石版]]（同名／字面對應）

## 密雲（神學）
query:
- 待建立詞：密雲
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：第22節「從火中、雲中、幽暗中」；STEP：he./'a.Nan（H6051，a.nan）；CT：『從火中、雲中、幽暗中』形容聲音出處。
- 經文用詞：雲中

字面解析：對上既有「密雲」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 密雲 | 0.571 | link_folder/神學/密雲.md |
| 2 | 雲彩 | 0.496 | link_folder/原文/雲彩.md |
| 3 | 神住在幽暗中 | 0.476 | link_folder/神學/神住在幽暗中.md |
| 4 | 雲柱火柱 | 0.454 | link_folder/歷史/雲柱火柱.md |
| 5 | 詩97：2 | 0.453 | link_folder/互文/詩97：2.md |

判定：✅ 建議使用既有條目 [[密雲]]（同名／字面對應）

## 神住在幽暗中（神學）
query:
- 待建立詞：神住在幽暗中
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：第22節「幽暗中」；STEP：ve./ha./'a.ra.Fel（H6205，context gloss thick darkness）；CT：『從黑暗中出來』意指神從祂所在的幽暗中發聲。
- 經文用詞：幽暗中

字面解析：對上既有「神住在幽暗中」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 神住在幽暗中 | 0.585 | link_folder/神學/神住在幽暗中.md |
| 2 | 摩西就近幽暗 | 0.524 | link_folder/事件/摩西就近幽暗.md |
| 3 | 詩97：2 | 0.499 | link_folder/互文/詩97：2.md |
| 4 | 神住在人間 | 0.479 | link_folder/神學/神住在人間.md |
| 5 | 約1：14 | 0.476 | link_folder/互文/約1：14.md |

判定：✅ 建議使用既有條目 [[神住在幽暗中]]（同名／字面對應）

## 以色列的長老（文化）
query:
- 待建立詞：以色列的長老
- 出現位置：申命記 第5章
- 候選類型：文化
- 本章上下文：第23節「你們支派中所有的首領和長老都來就近我」；STEP：ra.Shei shiv.tei./Khem（H7218H＋H7626H）與 ve./zik.nei./Khem（H2205G）；GT《精讀本》：首領是各支派的領袖,各有一名,長老則是年高德重之人,為數較多。
- 經文用詞：長老

字面解析：對上既有「以色列的長老」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 以色列的長老 | 0.692 | link_folder/文化/以色列的長老.md |
| 2 | 以色列的眾長老 | 0.627 | link_folder/人物/以色列的眾長老.md |
| 3 | 以色列人的官長 | 0.541 | link_folder/人物/以色列人的官長.md |
| 4 | 十二族長協助數點 | 0.530 | link_folder/事件/十二族長協助數點.md |
| 5 | 七十長老制度起源 | 0.529 | link_folder/歷史/七十長老制度起源.md |

判定：✅ 建議使用既有條目 [[以色列的長老]]（同名／字面對應）

## 耶和華的榮光（神學）
query:
- 待建立詞：耶和華的榮光
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：第24節「耶和華─我們神將他的榮光和他的大能顯給我們看」；STEP：ke.vo.D/o（H3519 ka.vod）與 ga.de.L/o（H1433 go.del）；CT：『祂的榮光』指神顯出祂的榮耀，在此以火光為代表。
- 經文用詞：他的榮光

字面解析：對上既有「耶和華的榮光」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 榮耀 | 0.639 | link_folder/原文/榮耀.md |
| 2 | 耶和華的榮光 | 0.635 | link_folder/神學/耶和華的榮光.md |
| 3 | 神的榮耀 | 0.601 | link_folder/神學/神的榮耀.md |
| 4 | 烈火 | 0.594 | link_folder/原文/烈火.md |
| 5 | 臉光照（神的容面） | 0.532 | link_folder/神學/臉光照（神的容面）.md |

判定：✅ 建議使用既有條目 [[耶和華的榮光]]（同名／字面對應）

## 耶和華永生神（神學）
query:
- 待建立詞：耶和華永生神
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：第26節「曾有何人聽見永生神的聲音從火中出來」；STEP：'E.lo.Him chai.Yim（H430G＋H2416A）；BH：Unlike the idols of surrounding nations, which were lifeless and mute, the God of Israel is living and active.
- 經文用詞：永生神

字面解析：對上既有「耶和華永生神」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 耶和華永生神 | 0.564 | link_folder/神學/耶和華永生神.md |
| 2 | 曾有何民聽見神在火中說話還能存活 | 0.512 | link_folder/主題/曾有何民聽見神在火中說話還能存活.md |
| 3 | 我是自有永有的 | 0.489 | link_folder/原文/我是自有永有的.md |
| 4 | 亞伯拉罕以撒雅各的神是活人的神 | 0.473 | link_folder/互文/亞伯拉罕以撒雅各的神是活人的神.md |
| 5 | 烈火 | 0.473 | link_folder/原文/烈火.md |

判定：✅ 建議使用既有條目 [[耶和華永生神]]（同名／字面對應）

## 寄居身分（神學）
query:
- 待建立詞：寄居身分
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：第14節「並在你城裡寄居的客旅」；STEP：ve./ge.re./Kha（H1616 ger）＋bi/sh.'a.Rei./kha（H8179G sha.ar，字面「在你的城門內」）；BH：The inclusion of foreigners underscores the universal nature of God's covenant.
- 經文用詞：寄居的客旅

字面解析：對上既有「寄居身分」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 寄居的 | 0.625 | link_folder/原文/寄居的.md |
| 2 | 寄居身分 | 0.621 | link_folder/神學/寄居身分.md |
| 3 | 本地人與寄居者同歸一例的律法精神 | 0.573 | link_folder/神學/本地人與寄居者同歸一例的律法精神.md |
| 4 | 寄居者身份 | 0.569 | link_folder/主題/寄居者身份.md |
| 5 | 寄居的與本地人同歸一例 | 0.561 | link_folder/主題/寄居的與本地人同歸一例.md |

判定：✅ 建議使用既有條目 [[寄居身分]]（同名／字面對應）

## 敬畏神（神學）
query:
- 待建立詞：敬畏神
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：第29節「惟願他們存這樣的心敬畏我」；STEP：le./yir.'Ah（H3372H，簡要詞典義 to fear: revere）；BH：This fear is not terror but a recognition of God's power and a commitment to obedience.
- 經文用詞：敬畏我

字面解析：對上既有「敬畏神」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 敬畏神 | 0.643 | link_folder/神學/敬畏神.md |
| 2 | 敬畏耶和華的話 | 0.574 | link_folder/神學/敬畏耶和華的話.md |
| 3 | 敬畏與信服 | 0.551 | link_folder/神學/敬畏與信服.md |
| 4 | 敬畏以撒的神 | 0.541 | link_folder/神學/敬畏以撒的神.md |
| 5 | 尊敬老人 | 0.496 | link_folder/主題/尊敬老人.md |

判定：✅ 建議使用既有條目 [[敬畏神]]（同名／字面對應）

## 大能的手（神學）
query:
- 待建立詞：大能的手
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：第15節「耶和華─你神用大能的手和伸出來的膀臂將你從那裡領出來」；STEP：be./Yad cha.za.Kah（H3027H＋H2389）＋u./vi/z.Ro.a' ne.tu.Yah（H2220＋H5186）。
- 經文用詞：大能的手和伸出來的膀臂

字面解析：對上既有「大能的手」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 大能的手 | 0.675 | link_folder/神學/大能的手.md |
| 2 | 大能的手與出埃及神蹟 | 0.614 | link_folder/神學/大能的手與出埃及神蹟.md |
| 3 | 伸出來的膀臂 | 0.597 | link_folder/神學/伸出來的膀臂.md |
| 4 | 神何曾從別的國中將一國的人民領出來 | 0.538 | link_folder/神學/神何曾從別的國中將一國的人民領出來.md |
| 5 | 耶和華的手 | 0.532 | link_folder/神學/耶和華的手.md |

判定：✅ 建議使用既有條目 [[大能的手]]（同名／字面對應）

## 摩西的第二篇講章（背景）
query:
- 待建立詞：摩西的第二篇講章
- 出現位置：申命記 第5章
- 候選類型：背景
- 本章上下文：GT《啟導本》：本章至11章是摩西第二篇談話中關於律法基本原則的講話，為一5「講律法」的開始；GT《串珠》：5:1-11:32 摩西勸勉以色列民：謹守遵行神在何烈山頒佈的訓令。

字面解析：對上既有「摩西的第二篇講章」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 摩西的第二篇講章 | 0.660 | link_folder/背景/摩西的第二篇講章.md |
| 2 | 講律法（ba.ar） | 0.606 | link_folder/原文/講律法（ba.ar）.md |
| 3 | 摩西上山見神 | 0.563 | link_folder/事件/摩西上山見神.md |
| 4 | 約書 | 0.553 | link_folder/神學/約書.md |
| 5 | 十誡 | 0.553 | link_folder/神學/十誡.md |

判定：✅ 建議使用既有條目 [[摩西的第二篇講章]]（同名／字面對應）

## 不可加添也不可刪減（ya.saph、ga.ra）（原文）
query:
- 待建立詞：不可加添也不可刪減（ya.saph、ga.ra）
- 出現位置：申命記 第5章
- 候選類型：原文
- 本章上下文：第22節「此外並沒有添別的話」；STEP：ve./Lo' ya.Saf（H3254H，ya.saph）——與申4:2「不可加添」同一個字根；KC：This word is a complete word to enjoy the blessing, nothing has been added.
- 經文用詞：此外並沒有添別的話

字面解析：對上既有「不可加添也不可刪減（ya.saph、ga.ra）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 不可加添也不可刪減（ya.saph、ga.ra） | 0.712 | link_folder/原文/不可加添也不可刪減（ya.saph、ga.ra）.md |
| 2 | 約瑟（增添／除去） | 0.464 | link_folder/原文/約瑟（增添／除去）.md |
| 3 | 產業減少（ga.ra） | 0.446 | link_folder/原文/產業減少（ga.ra）.md |
| 4 | 亞倫的祝福（祭司祝福） | 0.444 | link_folder/主題/亞倫的祝福（祭司祝福）.md |
| 5 | 敗壞與滅絕同一字根（sha.chat） | 0.439 | link_folder/原文/敗壞與滅絕同一字根（sha.chat）.md |

判定：✅ 建議使用既有條目 [[不可加添也不可刪減（ya.saph、ga.ra）]]（同名／字面對應）

## 主日與安息日的關係之爭（解經爭議）
query:
- 待建立詞：主日與安息日的關係之爭
- 出現位置：申命記 第5章
- 候選類型：解經爭議
- 本章上下文：CT〔問題改正〕列出九點主張新約信徒毋須守安息日；GT 引李道生《舊約聖經問題總解》同向作答；KC 反對把主日當成改頭換面的安息日（The first day of the week is not a disguised sabbath）。

字面解析：對上既有「主日與安息日的關係之爭」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 主日與安息日的關係之爭 | 0.713 | link_folder/解經爭議/主日與安息日的關係之爭.md |
| 2 | 安息日 | 0.507 | link_folder/神學/安息日.md |
| 3 | 當記念安息日守為聖日 | 0.500 | link_folder/神學/當記念安息日守為聖日.md |
| 4 | 七七節安息日算法的兩種解讀之爭 | 0.497 | link_folder/解經爭議/七七節安息日算法的兩種解讀之爭.md |
| 5 | 安息日不可生火 | 0.489 | link_folder/解經爭議/安息日不可生火.md |

判定：✅ 建議使用既有條目 [[主日與安息日的關係之爭]]（同名／字面對應）

## 亞伯拉罕之約（神學）
query:
- 待建立詞：亞伯拉罕之約
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：第3節「這約不是與我們列祖立的」；GT《雷氏》：西乃之約不是賜給列祖的（他們有亞伯拉罕之約；比較四31）；GT《啟導本》：將亞伯拉罕之約中的應許，具體施行在離開埃及奴役後的以色列人身上。

字面解析：對上既有「亞伯拉罕之約」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 亞伯拉罕之約 | 0.683 | link_folder/神學/亞伯拉罕之約.md |
| 2 | 立約 | 0.634 | link_folder/主題/立約.md |
| 3 | 亞伯拉罕之約的應驗 | 0.632 | link_folder/神學/亞伯拉罕之約的應驗.md |
| 4 | 亞伯拉罕 | 0.618 | link_folder/人物/亞伯拉罕.md |
| 5 | 神堅定與亞伯拉罕的約 | 0.612 | link_folder/主題/神堅定與亞伯拉罕的約.md |

判定：✅ 建議使用既有條目 [[亞伯拉罕之約]]（同名／字面對應）

## 律法與恩典（主題）
query:
- 待建立詞：律法與恩典
- 出現位置：申命記 第5章
- 候選類型：主題
- 本章上下文：第6節先講救贖再頒誡命；CT：神乃是先把以色列人從埃及地救出來，然後才將律法賜給他們。因此，律法的本身就是一種愛的表示；GT《精讀本》：在這種意義上,十誡是基於神之慈愛的「慈愛之約」。

字面解析：對上既有「律法與恩典」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 律法與恩典 | 0.733 | link_folder/主題/律法與恩典.md |
| 2 | 我是耶和華你的神 | 0.619 | link_folder/神學/我是耶和華你的神.md |
| 3 | 神的慈愛引領 | 0.572 | link_folder/神學/神的慈愛引領.md |
| 4 | 奴僕與自由 | 0.560 | link_folder/主題/奴僕與自由.md |
| 5 | 十誡 | 0.559 | link_folder/神學/十誡.md |

判定：✅ 建議使用既有條目 [[律法與恩典]]（同名／字面對應）

## 曾有何民聽見神在火中說話還能存活（主題）
query:
- 待建立詞：曾有何民聽見神在火中說話還能存活
- 出現位置：申命記 第5章
- 候選類型：主題
- 本章上下文：第24、26節「今日我們得見神與人說話，人還存活」「像我們聽見還能存活呢？」；STEP：va./Chai 與 va/i.Ye.chi 皆 H2421（cha.yah）。
- 經文用詞：人還存活、還能存活

字面解析：對上既有「曾有何民聽見神在火中說話還能存活」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 曾有何民聽見神在火中說話還能存活 | 0.610 | link_folder/主題/曾有何民聽見神在火中說話還能存活.md |
| 2 | 烈火 | 0.468 | link_folder/原文/烈火.md |
| 3 | 不能看見神的面而存活 | 0.445 | link_folder/神學/不能看見神的面而存活.md |
| 4 | 來12：29 我們的神乃是烈火 | 0.425 | link_folder/互文/來12：29 我們的神乃是烈火.md |
| 5 | 在天上在地下有什麼神能像你 | 0.423 | link_folder/神學/在天上在地下有什麼神能像你.md |

判定：✅ 建議使用既有條目 [[曾有何民聽見神在火中說話還能存活]]（同名／字面對應）

## 面對面見神（神學）
query:
- 待建立詞：面對面見神
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：第4節「耶和華在山上，從火中，面對面與你們說話」；STEP：pa.Nim be./fa.Nim（H6440H 雙同字）；GT《精讀本》：這並不意味著摩西或百姓們曾親眼見過神的容顏,他們只是看見了神的榮耀。
- 經文用詞：面對面

字面解析：對上既有「面對面見神」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 面對面見神 | 0.692 | link_folder/神學/面對面見神.md |
| 2 | 神與摩西面對面明說 | 0.687 | link_folder/神學/神與摩西面對面明說.md |
| 3 | 不能看見神的面而存活 | 0.644 | link_folder/神學/不能看見神的面而存活.md |
| 4 | 看見神 | 0.629 | link_folder/神學/看見神.md |
| 5 | 神的面 | 0.601 | link_folder/神學/神的面.md |

判定：✅ 建議使用既有條目 [[面對面見神]]（同名／字面對應）

## 雷轟即神的聲音（神學）
query:
- 待建立詞：雷轟即神的聲音
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：第22節「大聲曉諭你們全會眾的」；STEP：Kol ga.Dol（H6963A＋H1419A）；CT：『大聲』有如打雷(參約十二29)。
- 經文用詞：大聲

字面解析：對上既有「雷轟即神的聲音」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 雷轟即神的聲音 | 0.622 | link_folder/神學/雷轟即神的聲音.md |
| 2 | 角聲 | 0.499 | link_folder/神學/角聲.md |
| 3 | 二基路伯中間說話的聲音 | 0.471 | link_folder/神學/二基路伯中間說話的聲音.md |
| 4 | 歡呼王的聲音（te.ru.ah） | 0.462 | link_folder/原文/歡呼王的聲音（te.ru.ah）.md |
| 5 | 神的降臨 | 0.457 | link_folder/神學/神的降臨.md |

判定：✅ 建議使用既有條目 [[雷轟即神的聲音]]（同名／字面對應）

## 烈火（原文）
query:
- 待建立詞：烈火
- 出現位置：申命記 第5章
- 候選類型：原文
- 本章上下文：第25節「現在這大火將要燒滅我們」；STEP：to.khe.Le./nu（H398，a.khal，簡要詞典義 to eat）＋ha./'Esh ha./ge.do.Lah——與申4:24「烈火」（'esh 'o.khe.Lah）同樣是「火」加「吞吃」兩個字。
- 經文用詞：大火

字面解析：對上既有「烈火」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 烈火 | 0.640 | link_folder/原文/烈火.md |
| 2 | 來12：29 我們的神乃是烈火 | 0.531 | link_folder/互文/來12：29 我們的神乃是烈火.md |
| 3 | 娶妻並娶其母用火焚燒的大惡條例 | 0.512 | link_folder/主題/娶妻並娶其母用火焚燒的大惡條例.md |
| 4 | 耶和華的烈火將兩百五十個拿香爐者徹底毀滅 | 0.501 | link_folder/事件/耶和華的烈火將兩百五十個拿香爐者徹底毀滅.md |
| 5 | 滅盡與除滅的雙同字（sha.mad） | 0.499 | link_folder/原文/滅盡與除滅的雙同字（sha.mad）.md |

判定：✅ 建議使用既有條目 [[烈火]]（同名／字面對應）

## 這約是與哪一代人立的（解經爭議）
query:
- 待建立詞：這約是與哪一代人立的
- 出現位置：申命記 第5章
- 候選類型：解經爭議
- 本章上下文：第3節「這約不是與我們列祖立的，乃是與我們今日在這裡存活之人立的」；GT《雷氏》給出兩種讀法（列祖＝西乃山那一代／列祖＝族長）；GT《啟導本》與 KC 各採一種。

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 立約 | 0.532 | 0.022 | link_folder/主題/立約.md |
| 2 | 西乃之約 | 0.482 | 0.019 | link_folder/神學/西乃之約.md |
| 3 | 西乃山立約 | 0.475 | 0.016 | link_folder/背景/西乃山立約.md |
| 4 | 古代近東立約 | 0.460 | 0.013 | link_folder/背景/古代近東立約.md |
| 5 | 出19 的來源批判與擬人法之爭 | 0.475 | 0.011 | link_folder/解經爭議/出19 的來源批判與擬人法之爭.md |

rerank_margin: 0.003 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=解經爭議 vs 條目=主題），若確為同實體請確認是否改用 [[立約]]

## 事奉與作奴僕同一字根（a.vad）（原文）
query:
- 待建立詞：事奉與作奴僕同一字根（a.vad）
- 出現位置：申命記 第5章
- 候選類型：原文
- 本章上下文：第9節「事奉」ta.'a.ve.De/m（H5647H）、第13節「勞碌」ta.'a.Vod（H5647I）、第6節「為奴」'a.va.Dim（H5650）、第14節「僕婢」'av.de./kha（H5650）、第15節「作過奴僕」'E.ved（H5650）——STEP 顯示同一個 a.vad 字根貫穿本章。

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 奴僕與自由 | 0.443 | 0.041 | link_folder/主題/奴僕與自由.md |
| 2 | 奴僕 | 0.475 | 0.038 | link_folder/原文/奴僕.md |
| 3 | 古代近東奴隸制度 | 0.424 | 0.035 | link_folder/背景/古代近東奴隸制度.md |
| 4 | 潔淨 | 0.419 | 0.031 | link_folder/神學/潔淨.md |
| 5 | 勞碌的工（a.vo.dah） | 0.486 | 0.030 | link_folder/原文/勞碌的工（a.vo.dah）.md |

rerank_margin: 0.003 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=原文 vs 條目=主題），若確為同實體請確認是否改用 [[奴僕與自由]]

## 學習與教訓同一字根（la.mad）（原文）
query:
- 待建立詞：學習與教訓同一字根（la.mad）
- 出現位置：申命記 第5章
- 候選類型：原文
- 本章上下文：第1節「可以學習」u./le.mad.Tem（H3925H）與第31節「你要教訓他們」te.la.me.De/m（H3925G）；CT：在這裏，摩西列舉了教育法則：聽，是教育的開始。

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 律例（choq） | 0.442 | 0.009 | link_folder/原文/律例（choq）.md |
| 2 | 起首得那地（cha.lal） | 0.446 | 0.007 | link_folder/原文/起首得那地（cha.lal）.md |
| 3 | 滅盡與除滅的雙同字（sha.mad） | 0.383 | 0.005 | link_folder/原文/滅盡與除滅的雙同字（sha.mad）.md |
| 4 | 敗壞與滅絕同一字根（sha.chat） | 0.419 | 0.005 | link_folder/原文/敗壞與滅絕同一字根（sha.chat）.md |
| 5 | 你與你們的單複數交替 | 0.404 | 0.005 | link_folder/原文/你與你們的單複數交替.md |

rerank_margin: 0.002 (Top1 - Top2)
判定：🆕 建議建立新條目（最相似條目僅 0.446 < 0.50）（重排模型 nvidia/llama-nemotron-rerank-vl-1b-v2:free 未校準，上表名次僅供參考）

## 得福（ya.tav）（原文）
query:
- 待建立詞：得福（ya.tav）
- 出現位置：申命記 第5章
- 候選類型：原文
- 本章上下文：第16節「使你得福」Yi.tav、第28節「他們所說的都是」hei.Ti.vu、第29節「使他們…得福」yi.Tav，STEP 皆 H3190（ya.tav，簡要詞典義 be good）；CT〔原文字義〕「都是」美好，喜歡，令人滿意。

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 亞設（有福） | 0.378 | 0.013 | link_folder/人物/亞設（有福）.md |
| 2 | 得享平安（nu.ach） | 0.403 | 0.012 | link_folder/原文/得享平安（nu.ach）.md |
| 3 | 祝福與咒詛 | 0.400 | 0.009 | link_folder/主題/祝福與咒詛.md |
| 4 | 亞倫的祝福（祭司祝福） | 0.454 | 0.009 | link_folder/主題/亞倫的祝福（祭司祝福）.md |
| 5 | 心消化（ma.sas） | 0.376 | 0.008 | link_folder/原文/心消化（ma.sas）.md |

rerank_margin: 0.002 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=原文 vs 條目=人物），若確為同實體請確認是否改用 [[亞設（有福）]]

## 惟願（mi yi.ten）（原文）
query:
- 待建立詞：惟願（mi yi.ten）
- 出現位置：申命記 第5章
- 候選類型：原文
- 本章上下文：第29節「惟願他們存這樣的心敬畏我」；STEP：mi-（H4310 who?）＋yi.Ten（H5414Q，簡要詞典義 to give: if only!），字面是「誰會給」；CT：『這樣的心』指害怕惹神發怒的心。

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 使天下萬民驚恐懼怕 | 0.445 | 0.015 | link_folder/原文/使天下萬民驚恐懼怕.md |
| 2 | 忌邪（嫉妒） | 0.430 | 0.011 | link_folder/原文/忌邪（嫉妒）.md |
| 3 | 甘心樂意的奉獻 | 0.452 | 0.011 | link_folder/神學/甘心樂意的奉獻.md |
| 4 | 忌邪的神 | 0.411 | 0.010 | link_folder/神學/忌邪的神.md |
| 5 | 許願 | 0.435 | 0.010 | link_folder/文化/許願.md |

rerank_margin: 0.003 (Top1 - Top2)
判定：⚠ 相似度居中（0.50 ≤ 0.505 < 0.70），最近鄰為 [[盡心盡性尋求（ba.qash、da.rash）]]——此區間真對應與無對應分數重疊，需逐一人工判斷（重排模型 nvidia/llama-nemotron-rerank-vl-1b-v2:free 未校準，上表名次僅供參考）

## 幽暗與黑暗的兩個字（a.ra.phel、cho.shekh）（原文）
query:
- 待建立詞：幽暗與黑暗的兩個字（a.ra.phel、cho.shekh）
- 出現位置：申命記 第5章
- 候選類型：原文
- 本章上下文：第22節「幽暗」ve./ha./'a.ra.Fel（H6205）與第23節「黑暗」ha./Cho.shekh（H2822）在 STEP 是兩個不同的字；CT〔原文字義〕「幽暗」漆黑，烏黑；「黑暗」黑暗，隱密處。

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 神住在幽暗中 | 0.470 | 0.039 | link_folder/神學/神住在幽暗中.md |
| 2 | 摸得著的黑暗 | 0.481 | 0.034 | link_folder/原文/摸得著的黑暗.md |
| 3 | 古實 | 0.375 | 0.026 | link_folder/地點/古實.md |
| 4 | 使天下萬民驚恐懼怕 | 0.344 | 0.024 | link_folder/原文/使天下萬民驚恐懼怕.md |
| 5 | 黑暗之災 | 0.367 | 0.022 | link_folder/歷史/黑暗之災.md |

rerank_margin: 0.004 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=原文 vs 條目=神學），若確為同實體請確認是否改用 [[神住在幽暗中]]

## 凡屬血氣的（ba.sar）（原文）
query:
- 待建立詞：凡屬血氣的（ba.sar）
- 出現位置：申命記 第5章
- 候選類型：原文
- 本章上下文：第26節「凡屬血氣的，曾有何人聽見永生神的聲音」；STEP：khol- ba.Sar（H3605＋H1320，簡要詞典義 flesh）；BH："All flesh" refers to all humanity。
- 經文用詞：凡屬血氣的

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 血的尊重 | 0.386 | 0.066 | link_folder/神學/血的尊重.md |
| 2 | 亞伯的血哀告 | 0.352 | 0.064 | link_folder/神學/亞伯的血哀告.md |
| 3 | 人的全面敗壞 | 0.355 | 0.054 | link_folder/神學/人的全面敗壞.md |
| 4 | 全會眾 | 0.357 | 0.054 | link_folder/人物/全會眾.md |
| 5 | 地上塵土與生命氣息 | 0.382 | 0.052 | link_folder/原文/地上塵土與生命氣息.md |

rerank_margin: 0.002 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=原文 vs 條目=神學），若確為同實體請確認是否改用 [[血的尊重]]

## 以色列啊你要聽（sha.ma）（原文）
query:
- 待建立詞：以色列啊你要聽（sha.ma）
- 出現位置：申命記 第5章
- 候選類型：原文
- 本章上下文：第1節「以色列人哪，我今日曉諭你們的律例典章，你們要聽」；STEP：she.Ma'（H8085G，命令式）；BH：This phrase echoes the Shema (Deuteronomy 6:4), a central declaration of faith in Judaism.
- 經文用詞：你們要聽

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 律例（choq） | 0.452 | 0.033 | link_folder/原文/律例（choq）.md |
| 2 | 智慧與聰明（chokh.mah、bi.nah） | 0.418 | 0.032 | link_folder/原文/智慧與聰明（chokh.mah、bi.nah）.md |
| 3 | 只聽見聲音卻沒有看見形像（te.mu.nah） | 0.424 | 0.029 | link_folder/神學/只聽見聲音卻沒有看見形像（te.mu.nah）.md |
| 4 | 傳於後代 | 0.416 | 0.025 | link_folder/神學/傳於後代.md |
| 5 | 十句話 | 0.410 | 0.024 | link_folder/原文/十句話.md |

rerank_margin: 0.001 (Top1 - Top2)
判定：🆕 建議建立新條目（最相似條目僅 0.463 < 0.50）（重排模型 nvidia/llama-nemotron-rerank-vl-1b-v2:free 未校準，上表名次僅供參考）

## 不可偏離左右（主題）
query:
- 待建立詞：不可偏離左右
- 出現位置：申命記 第5章
- 候選類型：主題
- 本章上下文：第32節「不可偏離左右」；STEP：ta.Su.ru（H5493I，簡要詞典義 to turn aside）＋ya.Min（H3225G 右）＋u./se.Mol（H8040G 左）；GT《精讀本》：指要正直走在神所吩咐的律法之路。
- 經文用詞：不可偏離左右

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 大道（原文作王道） | 0.422 | 0.198 | link_folder/文化/大道（原文作王道）.md |
| 2 | 審判不可行不義按公義審判 | 0.456 | 0.180 | link_folder/主題/審判不可行不義按公義審判.md |
| 3 | 以東王拒絕以色列人假道 | 0.425 | 0.153 | link_folder/歷史/以東王拒絕以色列人假道.md |
| 4 | 公義與真理 | 0.416 | 0.148 | link_folder/主題/公義與真理.md |
| 5 | 面東定向的左右方位 | 0.427 | 0.141 | link_folder/背景/面東定向的左右方位.md |

rerank_margin: 0.018 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=主題 vs 條目=文化），若確為同實體請確認是否改用 [[大道（原文作王道）]]

## 十誡的解釋原理（神學）
query:
- 待建立詞：十誡的解釋原理
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：GT《精讀本》在第7-21節列出解釋十誡的原理：動機性原理、對偶原理、代表的原理、連線性原理，並說這些原理可擴大適用於其它所有律法。

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 十誡 | 0.535 | 0.408 | link_folder/神學/十誡.md |
| 2 | 倫理十誡 | 0.499 | 0.142 | link_folder/神學/倫理十誡.md |
| 3 | 定言式法律 | 0.475 | 0.121 | link_folder/神學/定言式法律.md |
| 4 | 十誡的條分法 | 0.491 | 0.118 | link_folder/神學/十誡的條分法.md |
| 5 | 我是耶和華你的神 | 0.427 | 0.101 | link_folder/神學/我是耶和華你的神.md |

rerank_margin: 0.266 (Top1 - Top2)
判定：⚠ 相似度居中（0.50 ≤ 0.535 < 0.70），最近鄰為 [[十誡]]——此區間真對應與無對應分數重疊，需逐一人工判斷（重排模型 nvidia/llama-nemotron-rerank-vl-1b-v2:free 未校準，上表名次僅供參考）

## 我是耶和華你的神（神學）
query:
- 待建立詞：我是耶和華你的神
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：第6節「我是耶和華─你的神，曾將你從埃及地為奴之家領出來」；GT《精讀本》：在立約或立法之前首先宣佈了立法者的稱呼及資格,這是為了對後面的契約或律法賦予牢不可破的權威和價值；CT：『耶和華』的希伯來文是雅威(Yehweh)，意思是那自有永有的。
- 經文用詞：我是耶和華─你的神

字面解析：對上既有「我是耶和華你的神」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 耶和華我是 | 0.756 | link_folder/神學/耶和華我是.md |
| 2 | 耶和華 | 0.675 | link_folder/神學/耶和華.md |
| 3 | 我是耶和華你的神 | 0.672 | link_folder/神學/我是耶和華你的神.md |
| 4 | 耶和華聖名的啟示 | 0.645 | link_folder/神學/耶和華聖名的啟示.md |
| 5 | 我是自有永有的 | 0.610 | link_folder/原文/我是自有永有的.md |

判定：✅ 建議使用既有條目 [[我是耶和華你的神]]（同名／字面對應）

## 妄稱（原文）
query:
- 待建立詞：妄稱
- 出現位置：申命記 第5章
- 候選類型：原文
- 本章上下文：第11節；STEP：ti.Sa'（H5375G）＋la./Shav'（H7723H）；CT〔原文字義〕「妄稱(原文雙字)」舉起，承擔；本章第20節的「假見證」（'ed Shav'，H7723G）用的是同一個 shav。
- 經文用詞：妄稱耶和華名的

字面解析：對上既有「妄稱」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 妄稱 | 0.612 | link_folder/原文/妄稱.md |
| 2 | 不可妄稱耶和華你神的名 | 0.518 | link_folder/神學/不可妄稱耶和華你神的名.md |
| 3 | 出20：7 | 0.488 | link_folder/互文/出20：7.md |
| 4 | 褻瀆聖名（na.qav） | 0.483 | link_folder/原文/褻瀆聖名（na.qav）.md |
| 5 | 滅絕 | 0.470 | link_folder/原文/滅絕.md |

判定：✅ 建議使用既有條目 [[妄稱]]（同名／字面對應）

## 貪戀（原文）
query:
- 待建立詞：貪戀
- 出現位置：申命記 第5章
- 候選類型：原文
- 本章上下文：第21節「不可貪戀人的妻子」tach.Mod（H2530A）與「也不可貪圖人的房屋」tit.'a.Veh（H183）是兩個不同的動詞；GT 引艾基斯：在申命記五21，「房屋」之前也用了一個與出埃及記不同的動詞「妄想」（即tit'awweh取代了tahmod)。
- 經文用詞：貪圖

字面解析：對上既有「貪戀」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 貪戀 | 0.613 | link_folder/原文/貪戀.md |
| 2 | 不可貪戀 | 0.536 | link_folder/神學/不可貪戀.md |
| 3 | 忌邪（嫉妒） | 0.529 | link_folder/原文/忌邪（嫉妒）.md |
| 4 | 姦淫 | 0.503 | link_folder/原文/姦淫.md |
| 5 | 疑恨條例 | 0.486 | link_folder/事件/疑恨條例.md |

判定：✅ 建議使用既有條目 [[貪戀]]（同名／字面對應）

## 申5：6-21（互文）
query:
- 待建立詞：申5：6-21
- 出現位置：申命記 第5章
- 候選類型：互文
- 本章上下文：本章第6-21節就是這段十誡本身；GT 引艾基斯《舊約聖經難題彙編》整段處理它與出二十2-17 的字句差異；KC：What we will see in verses 6-21, is not just a repetition of the Ten Commandments from Exodus 20.

字面解析：對上既有「申5：6-21」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 申5：6-21 | 0.726 | link_folder/互文/申5：6-21.md |
| 2 | 本章是否另有一套十誡 | 0.584 | link_folder/解經爭議/本章是否另有一套十誡.md |
| 3 | 十誡 | 0.560 | link_folder/神學/十誡.md |
| 4 | 十句話 | 0.550 | link_folder/原文/十句話.md |
| 5 | 申21：18-21 | 0.533 | link_folder/互文/申21：18-21.md |

判定：✅ 建議使用既有條目 [[申5：6-21]]（同名／字面對應）

## 當記念安息日守為聖日（神學）
query:
- 待建立詞：當記念安息日守為聖日
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：第12-15節第四誡；GT《精讀本》：在出20:11中,聖守安息日的誡命是以神在創造天地萬物之後第七日休息的事實為根據,而本書則以以色列民族從埃及得到解放的歷史性救贖事件為根據；BH：In the ancient Near Eastern context, this command was countercultural, as most societies did not have a regular day of rest.
- 經文用詞：吩咐你守安息日

字面解析：對上既有「當記念安息日守為聖日」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 當記念安息日守為聖日 | 0.775 | link_folder/神學/當記念安息日守為聖日.md |
| 2 | 安息日 | 0.708 | link_folder/神學/安息日.md |
| 3 | 「記念」與「守」 | 0.645 | link_folder/原文/「記念」與「守」.md |
| 4 | 古代近東安息日 | 0.641 | link_folder/背景/古代近東安息日.md |
| 5 | 安息日的設立 | 0.633 | link_folder/神學/安息日的設立.md |

判定：✅ 建議使用既有條目 [[當記念安息日守為聖日]]（同名／字面對應）

## 「記念」與「守」（原文）
query:
- 待建立詞：「記念」與「守」
- 出現位置：申命記 第5章
- 候選類型：原文
- 本章上下文：第12節「當照耶和華─你神所吩咐的守安息日為聖日」用 sha.Mor（H8104G，簡要詞典義 to keep）起頭；第15節「你也要記念你在埃及地作過奴僕」才用 ve./za.khar.Ta（H2142，za.khar）——本章的「記念」掛在埃及為奴，不在安息日誡命本身。
- 經文用詞：記念

字面解析：對上既有「「記念」與「守」」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 「記念」與「守」 | 0.723 | link_folder/原文/「記念」與「守」.md |
| 2 | 當記念安息日守為聖日 | 0.576 | link_folder/神學/當記念安息日守為聖日.md |
| 3 | 為奴之家 | 0.567 | link_folder/主題/為奴之家.md |
| 4 | 記念我的約 | 0.546 | link_folder/神學/記念我的約.md |
| 5 | 守節 | 0.516 | link_folder/原文/守節.md |

判定：✅ 建議使用既有條目 [[「記念」與「守」]]（同名／字面對應）

## 安息（第七日的歇息）（原文）
query:
- 待建立詞：安息（第七日的歇息）
- 出現位置：申命記 第5章
- 候選類型：原文
- 本章上下文：第14節「使你的僕婢可以和你一樣安息」；STEP：ya.Nu.ach（H5117，nu.ach，簡要詞典義 to rest），與「安息日」（sha.bat，H7676）不是同一個字；GT《啟導本》：在神面前人人平等，從祂規定僕婢也應休息看出。
- 經文用詞：可以和你一樣安息

字面解析：對上既有「安息（第七日的歇息）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 安息（第七日的歇息） | 0.637 | link_folder/原文/安息（第七日的歇息）.md |
| 2 | 得享平安（nu.ach） | 0.601 | link_folder/原文/得享平安（nu.ach）.md |
| 3 | 希伯來書4章神的安息 | 0.593 | link_folder/互文/希伯來書4章神的安息.md |
| 4 | 安息 | 0.590 | link_folder/神學/安息.md |
| 5 | 安息日律例 | 0.577 | link_folder/事件/安息日律例.md |

判定：✅ 建議使用既有條目 [[安息（第七日的歇息）]]（同名／字面對應）

## 遵行（原文）
query:
- 待建立詞：遵行
- 出現位置：申命記 第5章
- 候選類型：原文
- 本章上下文：第1、32節「你們要聽，可以學習，謹守遵行」；STEP：u./she.mar.Tem（H8104J，簡要詞典義 to keep: careful）＋la./'a.so.Ta/m（H6213A，a.sah）；CT：『謹守』重在指思想觀念的贊同和一致；『遵行』重在指行為上的遵照和實施。
- 經文用詞：謹守遵行

字面解析：對上既有「遵行」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 遵行 | 0.609 | link_folder/原文/遵行.md |
| 2 | 尊敬老人 | 0.478 | link_folder/主題/尊敬老人.md |
| 3 | 遵著耶和華的吩咐記載路程 | 0.454 | link_folder/主題/遵著耶和華的吩咐記載路程.md |
| 4 | 擅敢行事與褻瀆耶和華的剪除處分 | 0.453 | link_folder/神學/擅敢行事與褻瀆耶和華的剪除處分.md |
| 5 | 不隨從己心眼目行邪淫與成為聖潔 | 0.445 | link_folder/神學/不隨從己心眼目行邪淫與成為聖潔.md |

判定：✅ 建議使用既有條目 [[遵行]]（同名／字面對應）

## 定言式法律（神學）
query:
- 待建立詞：定言式法律
- 出現位置：申命記 第5章
- 候選類型：神學
- 本章上下文：第7-21節十條誡命全用「不可……」或「當……」的絕對句式；GT《精讀本》：第一,十誡的體裁是,即「當……」或「不可……」。

字面解析：對上既有「定言式法律」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 定言式法律 | 0.705 | link_folder/神學/定言式法律.md |
| 2 | 十句話 | 0.561 | link_folder/原文/十句話.md |
| 3 | 十誡 | 0.548 | link_folder/神學/十誡.md |
| 4 | 十誡的條分法 | 0.527 | link_folder/神學/十誡的條分法.md |
| 5 | 敬拜十守則 | 0.491 | link_folder/神學/敬拜十守則.md |

判定：✅ 建議使用既有條目 [[定言式法律]]（同名／字面對應）

## 百姓懼怕神的顯現（事件）
query:
- 待建立詞：百姓懼怕神的顯現
- 出現位置：申命記 第5章
- 候選類型：事件
- 本章上下文：第5節「因為你們懼怕那火，沒有上山」；第23-27節首領和長老求摩西代聽；第25節「現在這大火將要燒滅我們，我們何必冒死呢？」
- 經文用詞：懼怕那火、求你近前去

字面解析：對上既有「百姓懼怕神的顯現」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 百姓懼怕神的顯現 | 0.668 | link_folder/事件/百姓懼怕神的顯現.md |
| 2 | 使天下萬民驚恐懼怕 | 0.546 | link_folder/原文/使天下萬民驚恐懼怕.md |
| 3 | 摩西就近幽暗 | 0.543 | link_folder/事件/摩西就近幽暗.md |
| 4 | 曾有何民聽見神在火中說話還能存活 | 0.540 | link_folder/主題/曾有何民聽見神在火中說話還能存活.md |
| 5 | 神的降臨 | 0.532 | link_folder/神學/神的降臨.md |

判定：✅ 建議使用既有條目 [[百姓懼怕神的顯現]]（同名／字面對應）

## 十誡中的兩條正面誡命（主題）
query:
- 待建立詞：十誡中的兩條正面誡命
- 出現位置：申命記 第5章
- 候選類型：主題
- 本章上下文：第12、16節；STEP：ka./'a.Sher tzi.ve./Kha（H834D＋H6680）；GT《啟導本》：此誡和下一條孝敬父母之誡，為十誡中唯一兩條用正面語氣提出的誡命（其他都用「不可」），並且用「照耶和華神所吩咐」開頭，旨在說明十誡為神親自頒佈。
- 經文用詞：照耶和華─你神所吩咐的

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 十誡 | 0.606 | 0.401 | link_folder/神學/十誡.md |
| 2 | 神頒布十誡 | 0.520 | 0.207 | link_folder/事件/神頒布十誡.md |
| 3 | 十誡的條分法 | 0.485 | 0.149 | link_folder/神學/十誡的條分法.md |
| 4 | 敬拜十守則 | 0.534 | 0.134 | link_folder/神學/敬拜十守則.md |
| 5 | 倫理十誡 | 0.521 | 0.129 | link_folder/神學/倫理十誡.md |

rerank_margin: 0.194 (Top1 - Top2)
判定：⚠ 相似度居中（0.50 ≤ 0.607 < 0.70），最近鄰為 [[當孝敬父母]]——此區間真對應與無對應分數重疊，需逐一人工判斷（重排模型 nvidia/llama-nemotron-rerank-vl-1b-v2:free 未校準，上表名次僅供參考）

## 候選互查（本章內部，⚠＝彼此相似 ≥ 0.8）
（無 ≥ 門檻的配對）
