<!-- candidate_similarity_meta
schema_version: 1
book: 民數記
chapter: 36
candidate_sha256: b88a6254249ceca9b20ce8f98c2cb441493cf12c6f89c3ff03343e24d4520b4f
embedding_model: nvidia/nemotron-3-embed-1b
embedding_index_fingerprint: 6fff3af8c43abaef
link_index_sha256: e24aab27058df0d448efe4faf77c2cb3e4a615c154cd3ba1d4bee0abf90e39ad
homonyms_sha256: b8d042ea4f51253052128b2b289befdcf00b53c88237b67050f3252242c41ab8
rerank_model: nvidia/llama-nemotron-rerank-vl-1b-v2:free
rerank_policy_version: 2026.08.4
calibration_sha256: f63b1218023371bbbece396422aa7a02025bba0da119b49cae75232755734211
rerank_status: not_needed
rerankable_candidates: 0
rerank_attempted: 0
rerank_succeeded: 0
rerank_retrieve_top_k: 20
rerank_score_observed: none
-->

# 候選語義近鄰報告：民數記 第36章

- 檢索模型：nvidia/nemotron-3-embed-1b｜重排模型：nvidia/llama-nemotron-rerank-vl-1b-v2:free（未校準/保守模式）｜全庫 2853 條
- 規則說明：字面確切匹配直接通過；其餘候選先檢索 Top 20 名再由 Reranker 重排，取前 5 名顯示。
  治理優先：同名歧義（D類）與分類不相容永遠標 ⚠。
  重排模型未校準時，⚠ 由檢索相似度規則（≥0.50 且 top-1 非同實體）決定，重排名次只當附加證據。
  字面解析：列 resolver 實際比對結果——標「請確認」者務必人工核實。

## 西羅非哈的女兒（人物）
query:
- 待建立詞：西羅非哈的女兒
- 出現位置：民數記 第36章
- 候選類型：人物
- 本章上下文：v2「將我們兄弟西羅非哈的產業分給他的眾女兒」；v6「論到西羅非哈的眾女兒」；v10-12 她們照吩咐嫁了伯叔的兒子。STEP 顯示五個名字是 mach.Lah（H4244G）、tir.Tzah（H8656G）、cha.ge.Lah（H2295）、mil.Kah（H4435H）、no.'Ah（H5270）。
- 經文用詞：西羅非哈的眾女兒、西羅非哈的女兒

字面解析：對上既有「西羅非哈的女兒」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 西羅非哈的女兒 | 0.720 | link_folder/人物/西羅非哈的女兒.md |
| 2 | 女兒承受產業的條例 | 0.590 | link_folder/主題/女兒承受產業的條例.md |
| 3 | 亞設的女兒西拉 | 0.557 | link_folder/人物/亞設的女兒西拉.md |
| 4 | 同宗支派的兩種解釋 | 0.546 | link_folder/解經爭議/同宗支派的兩種解釋.md |
| 5 | 產業（na.cha.lah） | 0.530 | link_folder/原文/產業（na.cha.lah）.md |

判定：✅ 建議使用既有條目 [[西羅非哈的女兒]]（同名／字面對應）

## 女兒承受產業的條例（主題）
query:
- 待建立詞：女兒承受產業的條例
- 出現位置：民數記 第36章
- 候選類型：主題
- 本章上下文：v2 回顧民27 的判例：「我主也受了耶和華的吩咐將我們兄弟西羅非哈的產業分給他的眾女兒」；v8 把個案推成通則：「凡在以色列支派中得了產業的女子必作同宗支派人的妻」。GT《民數記串珠聖經註釋》：「上次問題的處理原則是：父親的產業不應因無兒子而落入外人手上，應由女兒或近親承受。」
- 經文用詞：得了產業的女子

字面解析：對上既有「女兒承受產業的條例」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 女兒承受產業的條例 | 0.834 | link_folder/主題/女兒承受產業的條例.md |
| 2 | 西羅非哈的女兒 | 0.691 | link_folder/人物/西羅非哈的女兒.md |
| 3 | 產業（na.cha.lah） | 0.613 | link_folder/原文/產業（na.cha.lah）.md |
| 4 | 業地（a.chuz.zah） | 0.587 | link_folder/原文/業地（a.chuz.zah）.md |
| 5 | 同宗支派的兩種解釋 | 0.565 | link_folder/解經爭議/同宗支派的兩種解釋.md |

判定：✅ 建議使用既有條目 [[女兒承受產業的條例]]（同名／字面對應）

## 產業（na.cha.lah）（原文）
query:
- 待建立詞：產業（na.cha.lah）
- 出現位置：民數記 第36章
- 候選類型：原文
- 本章上下文：本章 12 次出現。STEP 顯示 v2 是 be./na.cha.Lah（H5159）、v3-4 是 na.cha.la.Ta/n 與 mi./na.cha.Lat、v7 是 be./na.cha.Lat、v9 是 be./Na.cha.la.T/o。CT 原文字義給「產業，基業，地業」。
- 經文用詞：產業

字面解析：對上既有「產業（na.cha.lah）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 產業（na.cha.lah） | 0.625 | link_folder/原文/產業（na.cha.lah）.md |
| 2 | 業地（a.chuz.zah） | 0.540 | link_folder/原文/業地（a.chuz.zah）.md |
| 3 | 這地必落給你們為業（na.phal） | 0.462 | link_folder/原文/這地必落給你們為業（na.phal）.md |
| 4 | 各守各的產業（da.vaq） | 0.455 | link_folder/原文/各守各的產業（da.vaq）.md |
| 5 | 產業減少（ga.ra） | 0.387 | link_folder/原文/產業減少（ga.ra）.md |

判定：✅ 建議使用既有條目 [[產業（na.cha.lah）]]（同名／字面對應）

## 拈鬮分地（go.ral）（主題）
query:
- 待建立詞：拈鬮分地（go.ral）
- 出現位置：民數記 第36章
- 候選類型：主題
- 本章上下文：v2「耶和華曾吩咐我主拈鬮分地給以色列人為業」；v3「我們拈鬮所得的產業就要減少了」。STEP 顯示是 be./go.Ral 與 u./mi./go.Ral（H1486），簡要詞典義 allotted；CT 原文字義給「鬮，卵石」。
- 經文用詞：拈鬮

字面解析：對上既有「拈鬮分地（go.ral）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 拈鬮分地（go.ral） | 0.639 | link_folder/主題/拈鬮分地（go.ral）.md |
| 2 | 這地必落給你們為業（na.phal） | 0.605 | link_folder/原文/這地必落給你們為業（na.phal）.md |
| 3 | 耶和華是事奉者的業與分 | 0.519 | link_folder/神學/耶和華是事奉者的業與分.md |
| 4 | 產業（na.cha.lah） | 0.512 | link_folder/原文/產業（na.cha.lah）.md |
| 5 | 各守各的產業（da.vaq） | 0.509 | link_folder/原文/各守各的產業（da.vaq）.md |

判定：✅ 建議使用既有條目 [[拈鬮分地（go.ral）]]（同名／字面對應）

## 禧年（第五十年）（原文）
query:
- 待建立詞：禧年（第五十年）
- 出現位置：民數記 第36章
- 候選類型：原文
- 本章上下文：v4「到了以色列人的禧年，這女兒的產業就必加在他們丈夫支派的產業上」。STEP 顯示是 hai./yo.Vel（H3104），簡要詞典義 jubilee/horn；CT 原文字義給「第五十年，號角」。
- 經文用詞：禧年

字面解析：對上既有「禧年（第五十年）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 禧年（第五十年） | 0.688 | link_folder/原文/禧年（第五十年）.md |
| 2 | 禧年宣告自由與地業歸還 | 0.596 | link_folder/神學/禧年宣告自由與地業歸還.md |
| 3 | 產業減少（ga.ra） | 0.540 | link_folder/原文/產業減少（ga.ra）.md |
| 4 | 七年豐收七年饑荒與安息年-禧年 | 0.479 | link_folder/互文/七年豐收七年饑荒與安息年-禧年.md |
| 5 | 奉獻田地的複雜計算（承受之地與買來之地的差別） | 0.455 | link_folder/主題/奉獻田地的複雜計算（承受之地與買來之地的差別）.md |

判定：✅ 建議使用既有條目 [[禧年（第五十年）]]（同名／字面對應）

## 摩西（人物）
query:
- 待建立詞：摩西
- 出現位置：民數記 第36章
- 候選類型：人物
- 本章上下文：v1 族長們來到摩西面前；v5「摩西照耶和華的話吩咐以色列人」；v10、13 兩次「耶和華⋯⋯吩咐摩西」。CT 註 v5：顯然摩西曾將此問題求問神，得到神的答覆（參二十七5~6）。
- 經文用詞：摩西

字面解析：對上既有「摩西」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 稱摩西為我主 | 0.716 | link_folder/主題/稱摩西為我主.md |
| 2 | 摩西 | 0.656 | link_folder/人物/摩西.md |
| 3 | 耶和華的話臨到 | 0.609 | link_folder/神學/耶和華的話臨到.md |
| 4 | 摩西審判百姓 | 0.601 | link_folder/事件/摩西審判百姓.md |
| 5 | 摩西上山見神 | 0.590 | link_folder/事件/摩西上山見神.md |

判定：✅ 建議使用既有條目 [[摩西]]（同名／字面對應）

## 瑪吉（人物）
query:
- 待建立詞：瑪吉
- 出現位置：民數記 第36章
- 候選類型：人物
- 本章上下文：v1「瑪拿西的孫子，瑪吉的兒子基列」。CT 背景註解：「瑪拿西僅有一個兒子瑪吉，瑪吉又僅有一個兒子基列，而基列有六個兒子(參二十六29~32)。」
- 經文用詞：瑪吉

字面解析：對上既有「瑪吉」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 瑪吉 | 0.754 | link_folder/人物/瑪吉.md |
| 2 | 瑪拿西 | 0.541 | link_folder/人物/瑪拿西.md |
| 3 | 睚珥 | 0.519 | link_folder/人物/睚珥.md |
| 4 | 基土拉 | 0.472 | link_folder/人物/基土拉.md |
| 5 | 基列 | 0.468 | link_folder/地點/基列.md |

判定：✅ 建議使用既有條目 [[瑪吉]]（同名／字面對應）

## 瑪拿西（人物）
query:
- 待建立詞：瑪拿西
- 出現位置：民數記 第36章
- 候選類型：人物
- 本章上下文：v1「瑪拿西的孫子」；v12「他們嫁入約瑟兒子、瑪拿西子孫的族中」。STEP 顯示是 me.na.Sheh（H4519G）。
- 經文用詞：瑪拿西

字面解析：對上既有「瑪拿西」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 瑪拿西 | 0.575 | link_folder/人物/瑪拿西.md |
| 2 | 瑪拿西（使之忘了） | 0.529 | link_folder/原文/瑪拿西（使之忘了）.md |
| 3 | 瑪吉 | 0.528 | link_folder/人物/瑪吉.md |
| 4 | 亞西納 | 0.476 | link_folder/人物/亞西納.md |
| 5 | 瑪拿西支派人數大增 | 0.475 | link_folder/主題/瑪拿西支派人數大增.md |

判定：✅ 建議使用既有條目 [[瑪拿西]]（同名／字面對應）

## 約瑟（人物）
query:
- 待建立詞：約瑟
- 出現位置：民數記 第36章
- 候選類型：人物
- 本章上下文：v1「約瑟的後裔」；v5「約瑟支派的人說得有理」；v12「約瑟兒子、瑪拿西子孫的族中」。GT 丁良才註 v5：「約瑟支派，就是以法蓮、瑪拿西支派。但在此處摩西特指基列人。」
- 經文用詞：約瑟

字面解析：對上既有「約瑟」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 瑪拿西 | 0.623 | link_folder/人物/瑪拿西.md |
| 2 | 約瑟 | 0.623 | link_folder/人物/約瑟.md |
| 3 | 收納以法蓮與瑪拿西 | 0.620 | link_folder/歷史/收納以法蓮與瑪拿西.md |
| 4 | 十二支派起源 | 0.589 | link_folder/神學/十二支派起源.md |
| 5 | 以法蓮 | 0.582 | link_folder/人物/以法蓮.md |

判定：✅ 建議使用既有條目 [[約瑟]]（同名／字面對應）

## 瑪拿西半支派為何留在河東（解經爭議）
query:
- 待建立詞：瑪拿西半支派為何留在河東
- 出現位置：民數記 第36章
- 候選類型：解經爭議
- 本章上下文：CT 註 v1：「瑪吉族和基列族的產業分配在約但河東，而此次的問題與這兩族無關，故可能他們的族長可能缺席。」GT 丁良才同樣說：「瑪姬人的族長不在其內，因為他們在約旦河東已經得了基業。」

字面解析：對上既有「瑪拿西半支派為何留在河東」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 瑪拿西半支派為何留在河東 | 0.805 | link_folder/解經爭議/瑪拿西半支派為何留在河東.md |
| 2 | 瑪吉 | 0.651 | link_folder/人物/瑪吉.md |
| 3 | 兩支派半求河東之地為業 | 0.573 | link_folder/事件/兩支派半求河東之地為業.md |
| 4 | 河東之地是神的旨意還是神的允許 | 0.568 | link_folder/解經爭議/河東之地是神的旨意還是神的允許.md |
| 5 | 瑪拿西 | 0.562 | link_folder/人物/瑪拿西.md |

判定：✅ 建議使用既有條目 [[瑪拿西半支派為何留在河東]]（同名／字面對應）

## 典章（神學）
query:
- 待建立詞：典章
- 出現位置：民數記 第36章
- 候選類型：神學
- 本章上下文：v13「這是耶和華⋯⋯藉著摩西所吩咐以色列人的命令典章」。STEP 顯示是 ha./mish.pa.Tim（H4941G），簡要詞典義 justice: judgement；CT 原文字義給「審判，律例，公義」。
- 經文用詞：典章

字面解析：對上既有「典章」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 典章 | 0.681 | link_folder/神學/典章.md |
| 2 | 判斷（mish.pat） | 0.638 | link_folder/原文/判斷（mish.pat）.md |
| 3 | 民數記的結語 | 0.612 | link_folder/主題/民數記的結語.md |
| 4 | 摩西審判百姓 | 0.550 | link_folder/事件/摩西審判百姓.md |
| 5 | 律法與公義 | 0.549 | link_folder/主題/律法與公義.md |

判定：✅ 建議使用既有條目 [[典章]]（同名／字面對應）

## 摩押平原（地點）
query:
- 待建立詞：摩押平原
- 出現位置：民數記 第36章
- 候選類型：地點
- 本章上下文：v13「這是耶和華在摩押平原─約但河邊、耶利哥對面─藉著摩西所吩咐以色列人的命令典章」。STEP 顯示是 be./'ar.Vot mo.'Av（H6160I 加 H4124I）。
- 經文用詞：摩押平原

字面解析：對上既有「摩押平原」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 摩押平原 | 0.764 | link_folder/地點/摩押平原.md |
| 2 | 耶利哥 | 0.644 | link_folder/地點/耶利哥.md |
| 3 | 民數記的結語 | 0.631 | link_folder/主題/民數記的結語.md |
| 4 | 摩押地 | 0.565 | link_folder/地點/摩押地.md |
| 5 | 摩西錄 | 0.532 | link_folder/地點/摩西錄.md |

判定：✅ 建議使用既有條目 [[摩押平原]]（同名／字面對應）

## 約但河（地點）
query:
- 待建立詞：約但河
- 出現位置：民數記 第36章
- 候選類型：地點
- 本章上下文：v13「摩押平原─約但河邊」。GT《啟導本聖經註釋》：「本書以『約但河邊、耶利哥對面』作結，說明以色列人此際遠望隔岸美地，已為定居作好準備。」
- 經文用詞：約但河

字面解析：對上既有「約但河」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 約但河 | 0.651 | link_folder/地點/約但河.md |
| 2 | 摩押平原 | 0.649 | link_folder/地點/摩押平原.md |
| 3 | 耶利哥 | 0.648 | link_folder/地點/耶利哥.md |
| 4 | 亞嫩河 | 0.561 | link_folder/地點/亞嫩河.md |
| 5 | 民數記的結語 | 0.555 | link_folder/主題/民數記的結語.md |

判定：✅ 建議使用既有條目 [[約但河]]（同名／字面對應）

## 耶利哥（地點）
query:
- 待建立詞：耶利哥
- 出現位置：民數記 第36章
- 候選類型：地點
- 本章上下文：v13「耶利哥對面」。STEP 顯示是 ye.re.Cho（H3405G）。
- 經文用詞：耶利哥

字面解析：對上既有「耶利哥」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 耶利哥 | 0.593 | link_folder/地點/耶利哥.md |
| 2 | 雅謝 | 0.385 | link_folder/地點/雅謝.md |
| 3 | 行事與我反對（qe.ri） | 0.380 | link_folder/原文/行事與我反對（qe.ri）.md |
| 4 | 雅博渡口 | 0.370 | link_folder/地點/雅博渡口.md |
| 5 | 迦累得 | 0.365 | link_folder/原文/迦累得.md |

判定：✅ 建議使用既有條目 [[耶利哥]]（同名／字面對應）

## 各守各的產業（da.vaq）（原文）
query:
- 待建立詞：各守各的產業（da.vaq）
- 出現位置：民數記 第36章
- 候選類型：原文
- 本章上下文：v7「因為以色列人要各守各祖宗支派的產業」；v9「因為以色列支派的人要各守各的產業」。STEP 顯示動詞是 yid.be.Ku（H1692，詞典形 da.vaq），簡要詞典義 to cleave；CT 原文字義給「附著，黏住，緊靠」。
- 經文用詞：各守各

字面解析：對上既有「各守各的產業（da.vaq）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 各守各的產業（da.vaq） | 0.756 | link_folder/原文/各守各的產業（da.vaq）.md |
| 2 | 產業（na.cha.lah） | 0.502 | link_folder/原文/產業（na.cha.lah）.md |
| 3 | 業地（a.chuz.zah） | 0.483 | link_folder/原文/業地（a.chuz.zah）.md |
| 4 | 這地必落給你們為業（na.phal） | 0.445 | link_folder/原文/這地必落給你們為業（na.phal）.md |
| 5 | 為定與廢去（qum 與 pa.rar） | 0.434 | link_folder/原文/為定與廢去（qum 與 pa.rar）.md |

判定：✅ 建議使用既有條目 [[各守各的產業（da.vaq）]]（同名／字面對應）

## 家室與宗族（主題）
query:
- 待建立詞：家室與宗族
- 出現位置：民數記 第36章
- 候選類型：主題
- 本章上下文：v1、v12 兩次用「族」指瑪拿西下面的單位；v6「同宗支派」。STEP 顯示 v1 是 le./mish.Pa.chat 與 mi./mish.pe.Chot、v6 是 le./mish.Pa.chat ma.Teh 'a.vi./Hem、v12 是 mi./mish.pe.Chot 與 mish.Pa.chat（H4940，簡要詞典義 family），與 H4294H ma.Teh（tribe）並列。

字面解析：對上既有「家室與宗族」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 家室與宗族 | 0.564 | link_folder/主題/家室與宗族.md |
| 2 | 同宗支派的兩種解釋 | 0.503 | link_folder/解經爭議/同宗支派的兩種解釋.md |
| 3 | 宗族方言地土地與邦國 | 0.397 | link_folder/主題/宗族方言地土地與邦國.md |
| 4 | 利未的族譜（出六14-27） | 0.352 | link_folder/歷史/利未的族譜（出六14-27）.md |
| 5 | 以實瑪利十二族 | 0.346 | link_folder/主題/以實瑪利十二族.md |

判定：✅ 建議使用既有條目 [[家室與宗族]]（同名／字面對應）

## 同宗支派的兩種解釋（解經爭議）
query:
- 待建立詞：同宗支派的兩種解釋
- 出現位置：民數記 第36章
- 候選類型：解經爭議
- 本章上下文：v6「只是要嫁同宗支派的人」。CT 在備註中列出兩種解釋：指同一支派，或指同一支派內的同一宗族。GT 丁良才同樣列出兩個解法並偏向宗族說。STEP 顯示原文是 le./mish.Pa.chat ma.Teh 'a.vi./Hem（H4940 加 H4294H 加 H1G）。
- 經文用詞：同宗支派

字面解析：對上既有「同宗支派的兩種解釋」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 同宗支派的兩種解釋 | 0.781 | link_folder/解經爭議/同宗支派的兩種解釋.md |
| 2 | 家室與宗族 | 0.512 | link_folder/主題/家室與宗族.md |
| 3 | 民30：6-8 是已出嫁還是被聘未嫁 | 0.502 | link_folder/解經爭議/民30：6-8 是已出嫁還是被聘未嫁.md |
| 4 | 摩西娶古實女子的解經爭議 | 0.493 | link_folder/解經爭議/摩西娶古實女子的解經爭議.md |
| 5 | 林後6：14 | 0.468 | link_folder/互文/林後6：14.md |

判定：✅ 建議使用既有條目 [[同宗支派的兩種解釋]]（同名／字面對應）

## 產業減少（ga.ra）（原文）
query:
- 待建立詞：產業減少（ga.ra）
- 出現位置：民數記 第36章
- 候選類型：原文
- 本章上下文：v3「這樣，我們拈鬮所得的產業就要減少了」；v4「我們祖宗支派的產業就減少了」。STEP 顯示動詞是 ve./nig.re.'Ah 與 yi.ga.Re.a'（H1639，詞典形 ga.ra），Niphal 形；相對的「加在」是 ve./no.Saf 與 ve./nos.Fah（H3254H，詞典形 ya.saph），同樣是 Niphal。CT 原文字義給「減少，限制，撤回」與「增加」。
- 經文用詞：減少

字面解析：對上既有「產業減少（ga.ra）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 產業減少（ga.ra） | 0.656 | link_folder/原文/產業減少（ga.ra）.md |
| 2 | 各守各的產業（da.vaq） | 0.484 | link_folder/原文/各守各的產業（da.vaq）.md |
| 3 | 產業（na.cha.lah） | 0.437 | link_folder/原文/產業（na.cha.lah）.md |
| 4 | 這地必落給你們為業（na.phal） | 0.427 | link_folder/原文/這地必落給你們為業（na.phal）.md |
| 5 | 業地（a.chuz.zah） | 0.425 | link_folder/原文/業地（a.chuz.zah）.md |

判定：✅ 建議使用既有條目 [[產業減少（ga.ra）]]（同名／字面對應）

## 稱摩西為我主（主題）
query:
- 待建立詞：稱摩西為我主
- 出現位置：民數記 第36章
- 候選類型：主題
- 本章上下文：v2 族長們兩次稱摩西「我主」。GT 丁良才：「當時的以色列人，比前輩的人對於摩西更加恭敬。按聖書上所記，唯獨亞倫和約書亞曾稱摩西為主。」STEP 顯示是 'a.do.N/i（H113，簡要詞典義 lord）。
- 經文用詞：我主

字面解析：對上既有「稱摩西為我主」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 稱摩西為我主 | 0.786 | link_folder/主題/稱摩西為我主.md |
| 2 | 摩西 | 0.541 | link_folder/人物/摩西.md |
| 3 | 在米利巴未將耶和華尊為聖 | 0.540 | link_folder/神學/在米利巴未將耶和華尊為聖.md |
| 4 | 摩西看為極大 | 0.539 | link_folder/人物/摩西看為極大.md |
| 5 | 摩西上山見神 | 0.538 | link_folder/事件/摩西上山見神.md |

判定：✅ 建議使用既有條目 [[稱摩西為我主]]（同名／字面對應）

## 民數記的結語（主題）
query:
- 待建立詞：民數記的結語
- 出現位置：民數記 第36章
- 候選類型：主題
- 本章上下文：v13「這是耶和華在摩押平原─約但河邊、耶利哥對面─藉著摩西所吩咐以色列人的命令典章」。GT 丁良才：「本節是民數記的總結；將神在摩押平原，和在西奈山所吩咐的命令典章，列為平等（參利二十六46，二十七34）。」KingComments 也說最後這一句是對耶和華所說之話的總結與強調。

字面解析：對上既有「民數記的結語」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 民數記的結語 | 0.851 | link_folder/主題/民數記的結語.md |
| 2 | 摩押平原 | 0.691 | link_folder/地點/摩押平原.md |
| 3 | 摩西最後的任務 | 0.548 | link_folder/主題/摩西最後的任務.md |
| 4 | 摩西上山見神 | 0.546 | link_folder/事件/摩西上山見神.md |
| 5 | 摩西不得進入應許之地 | 0.534 | link_folder/事件/摩西不得進入應許之地.md |

判定：✅ 建議使用既有條目 [[民數記的結語]]（同名／字面對應）

## 候選互查（本章內部，⚠＝彼此相似 ≥ 0.8）
（無 ≥ 門檻的配對）
