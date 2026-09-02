<!-- candidate_similarity_meta
schema_version: 1
book: 申命記
chapter: 18
candidate_sha256: 0fdb7623e6f5f09bb64ba9d262b86a4db9a943e418b5a38b91a39f33e515d33f
candidate_identity_sha256: 5eb5995dcc36f542187a8c35a9cd327247db78e2fdb01bd830a25fb0897cb39b
embedding_model: nvidia/nemotron-3-embed-1b
embedding_index_fingerprint: 59c38954f1eba98b
link_index_sha256: 239037e013e5001354cc1c9a034743a84ef2c45e09e0564131c6fee7a03a00ad
homonyms_sha256: b8d042ea4f51253052128b2b289befdcf00b53c88237b67050f3252242c41ab8
rerank_model: nvidia/llama-nemotron-rerank-vl-1b-v2:free
rerank_policy_version: 2026.08.4
calibration_sha256: f63b1218023371bbbece396422aa7a02025bba0da119b49cae75232755734211
rerank_status: success
rerankable_candidates: 2
rerank_attempted: 2
rerank_succeeded: 2
rerank_retrieve_top_k: 20
rerank_score_observed: 0.012-0.512
-->

# 候選語義近鄰報告：申命記 第18章

- 檢索模型：nvidia/nemotron-3-embed-1b｜重排模型：nvidia/llama-nemotron-rerank-vl-1b-v2:free（未校準/保守模式）｜全庫 3015 條
- 規則說明：字面確切匹配直接通過；其餘候選先檢索 Top 20 名再由 Reranker 重排，取前 5 名顯示。
  治理優先：同名歧義（D類）與分類不相容永遠標 ⚠。
  重排模型未校準時，⚠ 由檢索相似度規則（≥0.50 且 top-1 非同實體）決定，重排名次只當附加證據。
  字面解析：列 resolver 實際比對結果——標「請確認」者務必人工核實。

## 利未支派（人物）
query:
- 待建立詞：利未支派
- 出現位置：申命記 第18章
- 候選類型：人物
- 本章上下文：第1至8節全段的主詞。「祭司利未人和利未全支派必在以色列中無分無業」（v1）；STEP 顯示 v1 是 la./ko.ha.Nim（H3548）ha/l.vi.Yim（H3881）kol- She.vet le.Vi（H7626H＋H3878）。
- 經文用詞：利未全支派、利未人

字面解析：對上既有「利未支派」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 利未支派 | 0.619 | link_folder/人物/利未支派.md |
| 2 | 利未 | 0.562 | link_folder/人物/利未.md |
| 3 | 利未人分散在各支派中 | 0.539 | link_folder/主題/利未人分散在各支派中.md |
| 4 | 利未人受職與祭司受職的差別 | 0.526 | link_folder/主題/利未人受職與祭司受職的差別.md |
| 5 | 利未人的四十八座城 | 0.525 | link_folder/主題/利未人的四十八座城.md |

判定：✅ 建議使用既有條目 [[利未支派]]（同名／字面對應）

## 火祭（isheh）（主題）
query:
- 待建立詞：火祭（isheh）
- 出現位置：申命記 第18章
- 候選類型：主題
- 本章上下文：「他們所吃用的就是獻給耶和華的火祭和一切所捐的」（v1）；STEP 顯示「火祭」是 'i.Shei（H801，簡要詞典義 ish.shah 為 food offering）。GT《串珠》說此處指各類的獻祭。
- 經文用詞：火祭

字面解析：對上既有「火祭（isheh）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 火祭（isheh） | 0.728 | link_folder/主題/火祭（isheh）.md |
| 2 | 獻給神的食物 | 0.611 | link_folder/神學/獻給神的食物.md |
| 3 | 燔祭 | 0.594 | link_folder/神學/燔祭.md |
| 4 | 宰牲與獻祭同一個字（za.vach） | 0.552 | link_folder/原文/宰牲與獻祭同一個字（za.vach）.md |
| 5 | 供物（qorban） | 0.545 | link_folder/原文/供物（qorban）.md |

判定：✅ 建議使用既有條目 [[火祭（isheh）]]（同名／字面對應）

## 產業（na.cha.lah）（原文）
query:
- 待建立詞：產業（na.cha.lah）
- 出現位置：申命記 第18章
- 候選類型：原文
- 本章上下文：「他們在弟兄中必沒有產業；耶和華是他們的產業」（v2）；STEP 顯示 v1 與 v2 共四次 na.cha.lah（H5159），另 v1「分」是 Che.lek（H2506A）。
- 經文用詞：產業

字面解析：對上既有「產業（na.cha.lah）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 產業（na.cha.lah） | 0.638 | link_folder/原文/產業（na.cha.lah）.md |
| 2 | 耶和華是事奉者的業與分 | 0.550 | link_folder/神學/耶和華是事奉者的業與分.md |
| 3 | 業地（a.chuz.zah） | 0.533 | link_folder/原文/業地（a.chuz.zah）.md |
| 4 | 各守各的產業（da.vaq） | 0.522 | link_folder/原文/各守各的產業（da.vaq）.md |
| 5 | 這地必落給你們為業（na.phal） | 0.502 | link_folder/原文/這地必落給你們為業（na.phal）.md |

判定：✅ 建議使用既有條目 [[產業（na.cha.lah）]]（同名／字面對應）

## 耶和華是事奉者的業與分（神學）
query:
- 待建立詞：耶和華是事奉者的業與分
- 出現位置：申命記 第18章
- 候選類型：神學
- 本章上下文：「他們在弟兄中必沒有產業；耶和華是他們的產業，正如耶和華所應許他們的」（v2）；民18:20 用的是同一對字（Che.lek H2506A 與 na.cha.lah H5159），本章換成第三人稱重述。CT 說神負責利未人的生活問題，凡以色列人奉獻給神的都歸利未人享用。
- 經文用詞：耶和華是他們的產業

字面解析：對上既有「耶和華是事奉者的業與分」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 耶和華是事奉者的業與分 | 0.777 | link_folder/神學/耶和華是事奉者的業與分.md |
| 2 | 利未人的什一奉獻 | 0.568 | link_folder/神學/利未人的什一奉獻.md |
| 3 | 耶和華 | 0.564 | link_folder/神學/耶和華.md |
| 4 | 古代近東以什一奉獻為神職薪酬 | 0.559 | link_folder/文化/古代近東以什一奉獻為神職薪酬.md |
| 5 | 產業（na.cha.lah） | 0.556 | link_folder/原文/產業（na.cha.lah）.md |

判定：✅ 建議使用既有條目 [[耶和華是事奉者的業與分]]（同名／字面對應）

## 利未人的什一奉獻（神學）
query:
- 待建立詞：利未人的什一奉獻
- 出現位置：申命記 第18章
- 候選類型：神學
- 本章上下文：「火祭和一切所捐的」（v1）；CT〔文意註解〕說『一切所捐的』原文「他的產業」，指什一奉獻（參民十八21）。
- 經文用詞：一切所捐的

字面解析：對上既有「利未人的什一奉獻」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 古代近東以什一奉獻為神職薪酬 | 0.619 | link_folder/文化/古代近東以什一奉獻為神職薪酬.md |
| 2 | 火祭（isheh） | 0.614 | link_folder/主題/火祭（isheh）.md |
| 3 | 利未人的什一奉獻 | 0.607 | link_folder/神學/利未人的什一奉獻.md |
| 4 | 供物（qorban） | 0.605 | link_folder/原文/供物（qorban）.md |
| 5 | 葉忒羅獻祭 | 0.580 | link_folder/事件/葉忒羅獻祭.md |

判定：✅ 建議使用既有條目 [[利未人的什一奉獻]]（同名／字面對應）

## 祭司的分（靠祭物養生）（主題）
query:
- 待建立詞：祭司的分（靠祭物養生）
- 出現位置：申命記 第18章
- 候選類型：主題
- 本章上下文：「祭司從百姓所當得的分乃是這樣：凡獻牛或羊為祭的，要把前腿和兩腮並脾胃給祭司」（v3）、「初收的五穀、新酒和油，並初剪的羊毛，也要給他」（v4）；STEP 顯示「當得的分」是 mish.Pat（H4941J），三個部位分別是 ze.Ro.a'（H2220）、le.cha.Ya.yim（H3895H）、ke.Vah（H6896）。
- 經文用詞：祭司從百姓所當得的分

字面解析：對上既有「祭司的分（靠祭物養生）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 祭司的分（靠祭物養生） | 0.657 | link_folder/主題/祭司的分（靠祭物養生）.md |
| 2 | 舉祭 | 0.580 | link_folder/原文/舉祭.md |
| 3 | 聖物 | 0.578 | link_folder/主題/聖物.md |
| 4 | 永遠當祭司的職任 | 0.536 | link_folder/神學/永遠當祭司的職任.md |
| 5 | 素祭（minchah） | 0.535 | link_folder/原文/素祭（minchah）.md |

判定：✅ 建議使用既有條目 [[祭司的分（靠祭物養生）]]（同名／字面對應）

## 初熟（原文）
query:
- 待建立詞：初熟
- 出現位置：申命記 第18章
- 候選類型：原文
- 本章上下文：「初收的五穀、新酒和油，並初剪的羊毛，也要給他」（v4）；STEP 顯示兩次 re.Shit（H7225G），另有 gez（H1488，fleece）。
- 經文用詞：初收的五穀

字面解析：對上既有「初熟」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 初熟 | 0.560 | link_folder/原文/初熟.md |
| 2 | 五穀、新酒和油（da.gan、ti.rosh、yits.har） | 0.532 | link_folder/原文/五穀、新酒和油（da.gan、ti.rosh、yits.har）.md |
| 3 | 初熟果子 | 0.521 | link_folder/神學/初熟果子.md |
| 4 | 新素祭 | 0.482 | link_folder/主題/新素祭.md |
| 5 | 七七節（五旬節） | 0.469 | link_folder/歷史/七七節（五旬節）.md |

判定：✅ 建議使用既有條目 [[初熟]]（同名／字面對應）

## 神的揀選（神學）
query:
- 待建立詞：神的揀選
- 出現位置：申命記 第18章
- 候選類型：神學
- 本章上下文：「因為耶和華─你的神從你各支派中將他揀選出來」（v5）；STEP 顯示「揀選」是 ba.Char（H977），與 v6「所選擇的」yiv.Char 是同一個字。
- 經文用詞：將他揀選出來

字面解析：對上既有「神的揀選」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 神的揀選 | 0.643 | link_folder/神學/神的揀選.md |
| 2 | 屬我的子民 | 0.494 | link_folder/神學/屬我的子民.md |
| 3 | 申12：5 | 0.490 | link_folder/互文/申12：5.md |
| 4 | 大的服事小的 | 0.483 | link_folder/主題/大的服事小的.md |
| 5 | 萬人之靈的神 | 0.474 | link_folder/神學/萬人之靈的神.md |

判定：✅ 建議使用既有條目 [[神的揀選]]（同名／字面對應）

## 侍立事奉（a.mad、sha.rat）（原文）
query:
- 待建立詞：侍立事奉（a.mad、sha.rat）
- 出現位置：申命記 第18章
- 候選類型：原文
- 本章上下文：「使他和他子孫永遠奉耶和華的名侍立事奉」（v5）；STEP 顯示是 la./'a.Mod（H5975G）le./sha.Ret（H8334），v7 再出現 ha./'o.me.Dim 與 ve./she.Ret。
- 經文用詞：侍立事奉

字面解析：對上既有「侍立事奉（a.mad、sha.rat）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 侍立事奉（a.mad、sha.rat） | 0.597 | link_folder/原文/侍立事奉（a.mad、sha.rat）.md |
| 2 | 事奉與作奴僕同一字根（a.vad） | 0.509 | link_folder/原文/事奉與作奴僕同一字根（a.vad）.md |
| 3 | 殷勤教訓（sha.nan） | 0.447 | link_folder/原文/殷勤教訓（sha.nan）.md |
| 4 | 學習與教訓同一字根（la.mad） | 0.438 | link_folder/原文/學習與教訓同一字根（la.mad）.md |
| 5 | 褻瀆（cha.lal） | 0.436 | link_folder/原文/褻瀆（cha.lal）.md |

判定：✅ 建議使用既有條目 [[侍立事奉（a.mad、sha.rat）]]（同名／字面對應）

## 立他名的居所（中央聖所）（主題）
query:
- 待建立詞：立他名的居所（中央聖所）
- 出現位置：申命記 第18章
- 候選類型：主題
- 本章上下文：「一心願意到耶和華所選擇的地方」（v6）；STEP 顯示是 ha./ma.Kom（H4725）'a.Sher yiv.Char（H977）。
- 經文用詞：耶和華所選擇的地方

字面解析：對上既有「立他名的居所（中央聖所）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 立他名的居所（中央聖所） | 0.635 | link_folder/主題/立他名的居所（中央聖所）.md |
| 2 | 申12：5 | 0.551 | link_folder/互文/申12：5.md |
| 3 | 神的聖所 | 0.494 | link_folder/神學/神的聖所.md |
| 4 | 神住在人間 | 0.464 | link_folder/神學/神住在人間.md |
| 5 | 神的揀選 | 0.457 | link_folder/神學/神的揀選.md |

判定：✅ 建議使用既有條目 [[立他名的居所（中央聖所）]]（同名／字面對應）

## 寄居的（原文）
query:
- 待建立詞：寄居的
- 出現位置：申命記 第18章
- 候選類型：原文
- 本章上下文：「利未人無論寄居在以色列中的哪一座城」（v6）；STEP 顯示「寄居」是 gar（H1481A，簡要詞典義 gur 為 to sojourn），主詞是利未人自己。
- 經文用詞：寄居

字面解析：對上既有「寄居的」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 寄居身分 | 0.554 | link_folder/神學/寄居身分.md |
| 2 | 寄居的 | 0.550 | link_folder/原文/寄居的.md |
| 3 | 利未人的四十八座城 | 0.532 | link_folder/主題/利未人的四十八座城.md |
| 4 | 林後6：16 | 0.514 | link_folder/互文/林後6：16.md |
| 5 | 利未人分散在各支派中 | 0.507 | link_folder/主題/利未人分散在各支派中.md |

判定：✅ 建議使用既有條目 [[寄居的]]（同名／字面對應）

## 利未人自願上中央聖所事奉（主題）
query:
- 待建立詞：利未人自願上中央聖所事奉
- 出現位置：申命記 第18章
- 候選類型：主題
- 本章上下文：「就要奉耶和華─他神的名事奉，像他眾弟兄利未人侍立在耶和華面前事奉一樣。除了他賣祖父產業所得的以外，還要得一分祭物與他們同吃」（v7-8）；STEP 顯示 v8 是 Che.lek ke./Che.lek yo.Khe.lu（H2506A 兩次加 H398）。
- 經文用詞：還要得一分祭物與他們同吃

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 利未人的什一奉獻 | 0.573 | 0.088 | link_folder/神學/利未人的什一奉獻.md |
| 2 | 在耶和華面前歡樂 | 0.548 | 0.080 | link_folder/主題/在耶和華面前歡樂.md |
| 3 | 立他名的居所（中央聖所） | 0.520 | 0.066 | link_folder/主題/立他名的居所（中央聖所）.md |
| 4 | 祭司的分（靠祭物養生） | 0.547 | 0.053 | link_folder/主題/祭司的分（靠祭物養生）.md |
| 5 | 宰牲與獻祭同一個字（za.vach） | 0.516 | 0.052 | link_folder/原文/宰牲與獻祭同一個字（za.vach）.md |

rerank_margin: 0.008 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=主題 vs 條目=神學），若確為同實體請確認是否改用 [[利未人的什一奉獻]]

## 可憎的物（to.e.vah）（原文）
query:
- 待建立詞：可憎的物（to.e.vah）
- 出現位置：申命記 第18章
- 候選類型：原文
- 本章上下文：「那些國民所行可憎惡的事，你不可學著行」（v9）、「凡行這些事的都為耶和華所憎惡」（v12）；STEP 顯示本章三次 H8441（ke./to.'a.Vot、to.'a.Vat、ha./to.'e.Vot）。
- 經文用詞：可憎惡的事

字面解析：對上既有「可憎的物（to.e.vah）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 可憎的物（to.e.vah） | 0.664 | link_folder/原文/可憎的物（to.e.vah）.md |
| 2 | 匪類（be.liy.ya.al） | 0.511 | link_folder/原文/匪類（be.liy.ya.al）.md |
| 3 | 褻瀆（cha.lal） | 0.494 | link_folder/原文/褻瀆（cha.lal）.md |
| 4 | 咒詛（a.rar 與 qa.vav） | 0.493 | link_folder/原文/咒詛（a.rar 與 qa.vav）.md |
| 5 | 神厭惡以色列的難題（利26：30與26：44的張力） | 0.485 | link_folder/解經爭議/神厭惡以色列的難題（利26：30與26：44的張力）.md |

判定：✅ 建議使用既有條目 [[可憎的物（to.e.vah）]]（同名／字面對應）

## 不可使兒女經火歸摩洛（主題）
query:
- 待建立詞：不可使兒女經火歸摩洛
- 出現位置：申命記 第18章
- 候選類型：主題
- 本章上下文：「你們中間不可有人使兒女經火」（v10）；STEP 顯示是 ma.'a.Vir（H5674A）be.no/v u./vi.T/o ba./'Esh（H784）。
- 經文用詞：使兒女經火

字面解析：對上既有「不可使兒女經火歸摩洛」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 不可使兒女經火歸摩洛 | 0.568 | link_folder/主題/不可使兒女經火歸摩洛.md |
| 2 | 摩洛（Molech）身分之爭 | 0.523 | link_folder/解經爭議/摩洛（Molech）身分之爭.md |
| 3 | 摩洛獻兒女治死條例（含知情連坐） | 0.489 | link_folder/主題/摩洛獻兒女治死條例（含知情連坐）.md |
| 4 | 利18：21 | 0.458 | link_folder/互文/利18：21.md |
| 5 | 歸給耶和華 | 0.452 | link_folder/原文/歸給耶和華.md |

判定：✅ 建議使用既有條目 [[不可使兒女經火歸摩洛]]（同名／字面對應）

## 卦金（qe.sem）（原文）
query:
- 待建立詞：卦金（qe.sem）
- 出現位置：申命記 第18章
- 候選類型：原文
- 本章上下文：「也不可有占卜的」（v10）、「都聽信觀兆的和占卜的」（v14）；STEP 顯示是 ko.Sem ke.sa.Mim（H7080 qa.sam 加 H7081 qe.sem），CT〔原文字義〕註「占卜(原文雙字)」行占卜(首字)；占卜(次字)。
- 經文用詞：占卜的

字面解析：對上既有「卦金（qe.sem）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 卦金（qe.sem） | 0.675 | link_folder/原文/卦金（qe.sem）.md |
| 2 | 斷沒有法術可以害雅各 | 0.504 | link_folder/神學/斷沒有法術可以害雅各.md |
| 3 | 不可行法術觀兆 | 0.494 | link_folder/主題/不可行法術觀兆.md |
| 4 | 銀杯與杯占術 | 0.462 | link_folder/解經爭議/銀杯與杯占術.md |
| 5 | 咒詛（a.rar 與 qa.vav） | 0.431 | link_folder/原文/咒詛（a.rar 與 qa.vav）.md |

判定：✅ 建議使用既有條目 [[卦金（qe.sem）]]（同名／字面對應）

## 不可行法術觀兆（主題）
query:
- 待建立詞：不可行法術觀兆
- 出現位置：申命記 第18章
- 候選類型：主題
- 本章上下文：「觀兆的、用法術的」（v10）、「都聽信觀兆的和占卜的」（v14）；STEP 顯示「觀兆」是 me.'o.Nen（H6049B，a.nan）、「用法術」是 me.na.Chesh（H5172，na.chash）。
- 經文用詞：觀兆的、用法術的

字面解析：對上既有「不可行法術觀兆」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 不可行法術觀兆 | 0.647 | link_folder/主題/不可行法術觀兆.md |
| 2 | 斷沒有法術可以害雅各 | 0.475 | link_folder/神學/斷沒有法術可以害雅各.md |
| 3 | 不可偏向交鬼行巫術的 | 0.443 | link_folder/主題/不可偏向交鬼行巫術的.md |
| 4 | 神蹟奇事不是真先知的憑證 | 0.427 | link_folder/主題/神蹟奇事不是真先知的憑證.md |
| 5 | 卦金（qe.sem） | 0.424 | link_folder/原文/卦金（qe.sem）.md |

判定：✅ 建議使用既有條目 [[不可行法術觀兆]]（同名／字面對應）

## 不可偏向交鬼行巫術的（主題）
query:
- 待建立詞：不可偏向交鬼行巫術的
- 出現位置：申命記 第18章
- 候選類型：主題
- 本章上下文：「交鬼的、行巫術的」（v11）；STEP 顯示是 sho.'El 'Ov（H7592 加 H178）與 yi.de.'o.Ni（H3049）。
- 經文用詞：交鬼的、行巫術的

字面解析：對上既有「不可偏向交鬼行巫術的」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 不可偏向交鬼行巫術的 | 0.565 | link_folder/主題/不可偏向交鬼行巫術的.md |
| 2 | 申18：10-12 | 0.443 | link_folder/互文/申18：10-12.md |
| 3 | 古代近東行邪術 | 0.433 | link_folder/背景/古代近東行邪術.md |
| 4 | 撒上28：3,9 | 0.417 | link_folder/互文/撒上28：3,9.md |
| 5 | 不可行法術觀兆 | 0.416 | link_folder/主題/不可行法術觀兆.md |

判定：✅ 建議使用既有條目 [[不可偏向交鬼行巫術的]]（同名／字面對應）

## 申18：10-12（互文）
query:
- 待建立詞：申18：10-12
- 出現位置：申命記 第18章
- 候選類型：互文
- 本章上下文：第10至11節一口氣列出九項：使兒女經火、占卜的、觀兆的、用法術的、行邪術的、用迷術的、交鬼的、行巫術的、過陰的；第12節總結「凡行這些事的都為耶和華所憎惡」。STEP 顯示九項各有不同字根，其中「行邪術的」是 me.kha.Shef（H3784，ka.shaph）、「用迷術的」是 cho.Ver Cha.ver（H2266 加 H2267）。
- 經文用詞：凡行這些事的、用迷術的

字面解析：對上既有「申18：10-12」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 申18：10-12 | 0.708 | link_folder/互文/申18：10-12.md |
| 2 | 不可行法術觀兆 | 0.604 | link_folder/主題/不可行法術觀兆.md |
| 3 | 不可偏向交鬼行巫術的 | 0.590 | link_folder/主題/不可偏向交鬼行巫術的.md |
| 4 | 行邪術的女人 | 0.584 | link_folder/原文/行邪術的女人.md |
| 5 | 古代近東行邪術 | 0.576 | link_folder/背景/古代近東行邪術.md |

判定：✅ 建議使用既有條目 [[申18：10-12]]（同名／字面對應）

## 求問與訪問同一個字（da.rash）（原文）
query:
- 待建立詞：求問與訪問同一個字（da.rash）
- 出現位置：申命記 第18章
- 候選類型：原文
- 本章上下文：「過陰的」（v11）；STEP 顯示是 do.Resh（H1875，da.rash）'el- ha./me.Tim（H4191），CT〔原文字義〕註「過陰(原文雙字)」尋求(首字)；死人(次字)。
- 經文用詞：過陰的

字面解析：對上既有「求問與訪問同一個字（da.rash）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 求問與訪問同一個字（da.rash） | 0.582 | link_folder/原文/求問與訪問同一個字（da.rash）.md |
| 2 | 探聽查究細細地訪問（da.rash、cha.qar、sha.al） | 0.483 | link_folder/原文/探聽查究細細地訪問（da.rash、cha.qar、sha.al）.md |
| 3 | 眷顧（da.rash） | 0.454 | link_folder/原文/眷顧（da.rash）.md |
| 4 | 盡心盡性尋求（ba.qash、da.rash） | 0.454 | link_folder/原文/盡心盡性尋求（ba.qash、da.rash）.md |
| 5 | 逾越（Pesach） | 0.381 | link_folder/原文/逾越（Pesach）.md |

判定：✅ 建議使用既有條目 [[求問與訪問同一個字（da.rash）]]（同名／字面對應）

## 義人與完全人（神學）
query:
- 待建立詞：義人與完全人
- 出現位置：申命記 第18章
- 候選類型：神學
- 本章上下文：「你要在耶和華─你的神面前作完全人」（v13）；STEP 顯示是 ta.Mim（H8549H，簡要詞典義 ta.mim 為 unblemished: blameless），BH 直接寫出 tamim 並說它含完整、真誠、無瑕之意。
- 經文用詞：完全人

字面解析：對上既有「義人與完全人」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 義人與完全人 | 0.592 | link_folder/神學/義人與完全人.md |
| 2 | 無殘疾（tamim） | 0.474 | link_folder/主題/無殘疾（tamim）.md |
| 3 | 聖潔 | 0.450 | link_folder/神學/聖潔.md |
| 4 | 耶和華向你所要的是什麼呢 | 0.444 | link_folder/主題/耶和華向你所要的是什麼呢.md |
| 5 | 沒有殘疾的祭牲 | 0.442 | link_folder/神學/沒有殘疾的祭牲.md |

判定：✅ 建議使用既有條目 [[義人與完全人]]（同名／字面對應）

## 先知（主題）
query:
- 待建立詞：先知
- 出現位置：申命記 第18章
- 候選類型：主題
- 本章上下文：第15至22節六次出現「先知」；STEP 顯示都是 na.Vi'（H5030）。v18「我要將當說的話傳給他」是 ve./na.ta.Ti de.va.Ra/i be./Fi/v（H5414H 加 H1697G 加 H6310G），字面是我要把我的話放在他口中。
- 經文用詞：先知

字面解析：對上既有「先知」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 先知 | 0.589 | link_folder/主題/先知.md |
| 2 | 拿單 | 0.480 | link_folder/人物/拿單.md |
| 3 | 越過耶和華的口（peh） | 0.463 | link_folder/原文/越過耶和華的口（peh）.md |
| 4 | 神蹟奇事不是真先知的憑證 | 0.459 | link_folder/主題/神蹟奇事不是真先知的憑證.md |
| 5 | 耶和華的話臨到 | 0.457 | link_folder/神學/耶和華的話臨到.md |

判定：✅ 建議使用既有條目 [[先知]]（同名／字面對應）

## 興起一位先知像我（神學）
query:
- 待建立詞：興起一位先知像我
- 出現位置：申命記 第18章
- 候選類型：神學
- 本章上下文：「耶和華─你的神要從你們弟兄中間給你興起一位先知像我，你們要聽從他」（v15）、「我必在他們弟兄中間給他們興起一位先知像你」（v18）；STEP 顯示「興起」是 ya.Kim 與 'a.Kim（H6965I，qum: to arise: establish），「弟兄」是 'a.Chei./kha（H251I）。
- 經文用詞：興起一位先知像我

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 先知 | 0.478 | 0.512 | link_folder/主題/先知.md |
| 2 | 神蹟奇事不是真先知的憑證 | 0.445 | 0.331 | link_folder/主題/神蹟奇事不是真先知的憑證.md |
| 3 | 羅馬書 9-17（神興起法老） | 0.405 | 0.274 | link_folder/互文/羅馬書 9-17（神興起法老）.md |
| 4 | 古代近東的超脫預言 | 0.403 | 0.250 | link_folder/背景/古代近東的超脫預言.md |
| 5 | 彌賽亞 | 0.410 | 0.241 | link_folder/神學/彌賽亞.md |

rerank_margin: 0.182 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=神學 vs 條目=主題），若確為同實體請確認是否改用 [[先知]]

## 何烈山（地點）
query:
- 待建立詞：何烈山
- 出現位置：申命記 第18章
- 候選類型：地點
- 本章上下文：「正如你在何烈山大會的日子求耶和華─你神一切的話」（v16）；GT《聖經精讀本》說大會的日子指以色列百姓為了領受十誡聚集在西奈山腳下的那一日。
- 經文用詞：何烈山

字面解析：對上既有「何烈山」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 何烈山 | 0.728 | link_folder/地點/何烈山.md |
| 2 | 大會的日子（qa.hal） | 0.700 | link_folder/原文/大會的日子（qa.hal）.md |
| 3 | 神的山 | 0.669 | link_folder/地點/神的山.md |
| 4 | 西乃山 | 0.666 | link_folder/地點/西乃山.md |
| 5 | 何烈 | 0.635 | link_folder/地點/何烈.md |

判定：✅ 建議使用既有條目 [[何烈山]]（同名／字面對應）

## 大會的日子（qa.hal）（原文）
query:
- 待建立詞：大會的日子（qa.hal）
- 出現位置：申命記 第18章
- 候選類型：原文
- 本章上下文：「正如你在何烈山大會的日子求耶和華─你神一切的話」（v16）；GT《聖經精讀本》說大會的日子指以色列百姓為了從神領受十誡，經過兩天的潔淨期之後，聚集在西奈山腳下的那一日。
- 經文用詞：大會的日子

字面解析：對上既有「大會的日子（qa.hal）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 大會的日子（qa.hal） | 0.810 | link_folder/原文/大會的日子（qa.hal）.md |
| 2 | 聖會 | 0.590 | link_folder/文化/聖會.md |
| 3 | 大贖罪日（Yom Kippur）條例 | 0.553 | link_folder/歷史/大贖罪日（Yom Kippur）條例.md |
| 4 | 何烈山 | 0.544 | link_folder/地點/何烈山.md |
| 5 | 神的山 | 0.530 | link_folder/地點/神的山.md |

判定：✅ 建議使用既有條目 [[大會的日子（qa.hal）]]（同名／字面對應）

## 擅敢行事與褻瀆耶和華的剪除處分（神學）
query:
- 待建立詞：擅敢行事與褻瀆耶和華的剪除處分
- 出現位置：申命記 第18章
- 候選類型：神學
- 本章上下文：「若有先知擅敢託我的名說我所未曾吩咐他說的話」（v20）、「是那先知擅自說的」（v22）；STEP 顯示 v20 是 ya.Zid（H2102，zud）、v22 是 be./za.dOn（H2087，za.don: arrogance），後者與申17:12 的 ve./za.Don 是同一個 Extended Strong。
- 經文用詞：擅敢託我的名、擅自說的

字面解析：對上既有「擅敢行事與褻瀆耶和華的剪除處分」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 擅敢行事與褻瀆耶和華的剪除處分 | 0.636 | link_folder/神學/擅敢行事與褻瀆耶和華的剪除處分.md |
| 2 | 爭先與擅自 | 0.520 | link_folder/原文/爭先與擅自.md |
| 3 | 敬畏與可畏同一字根（ya.re） | 0.520 | link_folder/原文/敬畏與可畏同一字根（ya.re）.md |
| 4 | 在米利巴未將耶和華尊為聖 | 0.494 | link_folder/神學/在米利巴未將耶和華尊為聖.md |
| 5 | 先知 | 0.491 | link_folder/主題/先知.md |

判定：✅ 建議使用既有條目 [[擅敢行事與褻瀆耶和華的剪除處分]]（同名／字面對應）

## 神蹟奇事不是真先知的憑證（主題）
query:
- 待建立詞：神蹟奇事不是真先知的憑證
- 出現位置：申命記 第18章
- 候選類型：主題
- 本章上下文：「先知託耶和華的名說話，所說的若不成就，也無效驗，這就是耶和華所未曾吩咐的」（v22）；GT《啟導本》在申13 已把應驗列為另一項測驗並註明十八22，本章給出這條測驗本身。
- 經文用詞：也無效驗

字面解析：對上既有「神蹟奇事不是真先知的憑證」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 神蹟奇事不是真先知的憑證 | 0.733 | link_folder/主題/神蹟奇事不是真先知的憑證.md |
| 2 | 先知 | 0.539 | link_folder/主題/先知.md |
| 3 | 神蹟（miraculous signs） | 0.528 | link_folder/神學/神蹟（miraculous signs）.md |
| 4 | 神的試驗 | 0.506 | link_folder/神學/神的試驗.md |
| 5 | 巴蘭是先知還是術士 | 0.502 | link_folder/解經爭議/巴蘭是先知還是術士.md |

判定：✅ 建議使用既有條目 [[神蹟奇事不是真先知的憑證]]（同名／字面對應）

## 候選互查（本章內部，⚠＝彼此相似 ≥ 0.8）
兩個候選可能是同一概念——考慮合併成一個候選（另一個用 surfaces 涵蓋），
或確認確為兩個條目再照建：
- 0.836 ⚠ 何烈山 ↔ 大會的日子（qa.hal）
