<!-- candidate_similarity_meta
schema_version: 1
book: 申命記
chapter: 3
candidate_sha256: a01e42baeb1e55864f2062c582d8e963b24097b641b66439ea1bca4ce2a48330
embedding_model: nvidia/nemotron-3-embed-1b
embedding_index_fingerprint: 53fe45478bf047dd
link_index_sha256: a2031773ed74b5e80e7988d593383d34532e0e45f172de7d4f87bc4001473fa4
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

# 候選語義近鄰報告：申命記 第3章

- 檢索模型：nvidia/nemotron-3-embed-1b｜重排模型：nvidia/llama-nemotron-rerank-vl-1b-v2:free（未校準/保守模式）｜全庫 2906 條
- 規則說明：字面確切匹配直接通過；其餘候選先檢索 Top 20 名再由 Reranker 重排，取前 5 名顯示。
  治理優先：同名歧義（D類）與分類不相容永遠標 ⚠。
  重排模型未校準時，⚠ 由檢索相似度規則（≥0.50 且 top-1 非同實體）決定，重排名次只當附加證據。
  字面解析：列 resolver 實際比對結果——標「請確認」者務必人工核實。

## 巴珊（地點）
query:
- 待建立詞：巴珊
- 出現位置：申命記 第3章
- 候選類型：地點
- 本章上下文：v1「以後，我們轉回，向巴珊去」；v10「巴珊全地」；v13「亞珥歌伯全地乃是巴珊全地」。CT：「『巴珊』位於雅博河以北，黑門山以南的高原(即今戈蘭高原)，境內牧草繁茂，盛產牛羊」；GT《串珠》：「「巴珊」：「肥沃」之意。巴珊位於基列之北，以產牛馳名。」；BH：「Bashan was a fertile region east of the Jordan River, known for its rich pastures and strong cities.」。STEP 顯示是 ha./ba.Shan（H1316）。

字面解析：對上既有「巴珊」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 巴珊 | 0.734 | link_folder/地點/巴珊.md |
| 2 | 亞珥歌伯（ar.gov） | 0.559 | link_folder/地點/亞珥歌伯（ar.gov）.md |
| 3 | 以得來 | 0.516 | link_folder/地點/以得來.md |
| 4 | 平原（mi.shor） | 0.506 | link_folder/地點/平原（mi.shor）.md |
| 5 | 撒迦 | 0.496 | link_folder/地點/撒迦.md |

判定：✅ 建議使用既有條目 [[巴珊]]（同名／字面對應）

## 以色列戰勝巴珊王噩互文（申3：1-11；詩135：10-12；136：17-22）（互文）
query:
- 待建立詞：以色列戰勝巴珊王噩互文（申3：1-11；詩135：10-12；136：17-22）
- 出現位置：申命記 第3章
- 候選類型：互文
- 本章上下文：v1-11 是這個互文條目的主要段落，該條目在申1 的累積已寫明「本章只點名，細節留到第三章」。v11「利乏音人所剩下的只有巴珊王噩」。
- 經文用詞：巴珊王噩

字面解析：對上既有「以色列戰勝巴珊王噩互文（申3：1-11；詩135：10-12；136：17-22）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 以色列戰勝巴珊王噩互文（申3：1-11；詩135：10-12；136：17-22） | 0.750 | link_folder/互文/以色列戰勝巴珊王噩互文（申3：1-11；詩135：10-12；136：17-22）.md |
| 2 | 以色列戰勝亞摩利王西宏互文（申2：24-37；3：1-7；詩135：10-12；136：17-22） | 0.586 | link_folder/互文/以色列戰勝亞摩利王西宏互文（申2：24-37；3：1-7；詩135：10-12；136：17-22）.md |
| 3 | 巴珊 | 0.557 | link_folder/地點/巴珊.md |
| 4 | 利乏音人 | 0.535 | link_folder/人物/利乏音人.md |
| 5 | 巴珊王噩的鐵床（e.re.s） | 0.516 | link_folder/原文/巴珊王噩的鐵床（e.re.s）.md |

判定：✅ 建議使用既有條目 [[以色列戰勝巴珊王噩互文（申3：1-11；詩135：10-12；136：17-22）]]（同名／字面對應）

## 以得來（地點）
query:
- 待建立詞：以得來
- 出現位置：申命記 第3章
- 候選類型：地點
- 本章上下文：v1「在以得來與我們交戰」；v10「直到撒迦和以得來」。CT：「『以得來』是巴珊的副都，位於加利利海的東面約一百多公里」；GT《聖經精讀本》：「以得來: 是巴珊王“噩”所居住的王都,與“亞斯他錄”一起是巴珊國兩大首都之一(1:4)」。STEP 顯示 v10 是 've./'ed.Re.'i（H154）。

字面解析：對上既有「以得來」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 以得來 | 0.776 | link_folder/地點/以得來.md |
| 2 | 撒迦 | 0.609 | link_folder/地點/撒迦.md |
| 3 | 亞斯她錄 | 0.574 | link_folder/地點/亞斯她錄.md |
| 4 | 巴珊 | 0.572 | link_folder/地點/巴珊.md |
| 5 | 亞述 | 0.508 | link_folder/地點/亞述.md |

判定：✅ 建議使用既有條目 [[以得來]]（同名／字面對應）

## 以色列戰勝亞摩利王西宏互文（申2：24-37；3：1-7；詩135：10-12；136：17-22）（互文）
query:
- 待建立詞：以色列戰勝亞摩利王西宏互文（申2：24-37；3：1-7；詩135：10-12；136：17-22）
- 出現位置：申命記 第3章
- 候選類型：互文
- 本章上下文：v2「你要待他像從前待住希實本的亞摩利王西宏一樣」；v6「像從前待希實本王西宏一樣」。本章兩次拿西宏之役當作噩之役的先例，KC：「The previous victory, that over Sihon, is cited as evidence.」。
- 經文用詞：亞摩利王西宏、希實本王西宏

字面解析：對上既有「以色列戰勝亞摩利王西宏互文（申2：24-37；3：1-7；詩135：10-12；136：17-22）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 以色列戰勝亞摩利王西宏互文（申2：24-37；3：1-7；詩135：10-12；136：17-22） | 0.770 | link_folder/互文/以色列戰勝亞摩利王西宏互文（申2：24-37；3：1-7；詩135：10-12；136：17-22）.md |
| 2 | 以色列戰勝巴珊王噩互文（申3：1-11；詩135：10-12；136：17-22） | 0.642 | link_folder/互文/以色列戰勝巴珊王噩互文（申3：1-11；詩135：10-12；136：17-22）.md |
| 3 | 希實本 | 0.581 | link_folder/地點/希實本.md |
| 4 | 亞摩利人 | 0.540 | link_folder/人物/亞摩利人.md |
| 5 | 戰勝亞瑪力人 | 0.533 | link_folder/事件/戰勝亞瑪力人.md |

判定：✅ 建議使用既有條目 [[以色列戰勝亞摩利王西宏互文（申2：24-37；3：1-7；詩135：10-12；136：17-22）]]（同名／字面對應）

## 希實本（地點）
query:
- 待建立詞：希實本
- 出現位置：申命記 第3章
- 候選類型：地點
- 本章上下文：v2「住希實本的亞摩利王西宏」。CT：「因為希實本乃是亞摩利的京城(參民二十一27；書九10)」；BH：「Heshbon was the capital city of Sihon, king of the Amorites.」。STEP 顯示 v6 是 chesh.Bon（H2809）。

字面解析：對上既有「希實本」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 希實本 | 0.743 | link_folder/地點/希實本.md |
| 2 | 亞斯她錄 | 0.467 | link_folder/地點/亞斯她錄.md |
| 3 | 以色列戰勝亞摩利王西宏互文（申2：24-37；3：1-7；詩135：10-12；136：17-22） | 0.464 | link_folder/互文/以色列戰勝亞摩利王西宏互文（申2：24-37；3：1-7；詩135：10-12；136：17-22）.md |
| 4 | 亞摩利人 | 0.454 | link_folder/人物/亞摩利人.md |
| 5 | 雅謝 | 0.436 | link_folder/地點/雅謝.md |

判定：✅ 建議使用既有條目 [[希實本]]（同名／字面對應）

## 亞摩利人（人物）
query:
- 待建立詞：亞摩利人
- 出現位置：申命記 第3章
- 候選類型：人物
- 本章上下文：v8「兩個亞摩利王」；v9「亞摩利人稱為示尼珥」。GT《聖經精讀本》：「亞摩利人與當時居住在約但河東的以東、摩押、亞捫人有所不同,是早在亞伯拉罕移居迦南之前已定居在那裡的原住民,也是早已預定被毀滅的迦南七族之一」。
- 經文用詞：亞摩利人、兩個亞摩利王

字面解析：對上既有「亞摩利人」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 亞摩利人 | 0.740 | link_folder/人物/亞摩利人.md |
| 2 | 亞捫人 | 0.649 | link_folder/人物/亞捫人.md |
| 3 | 亞瑪力人 | 0.618 | link_folder/人物/亞瑪力人.md |
| 4 | 迦南地的居民分佈 | 0.609 | link_folder/背景/迦南地的居民分佈.md |
| 5 | 迦南人 | 0.597 | link_folder/人物/迦南人.md |

判定：✅ 建議使用既有條目 [[亞摩利人]]（同名／字面對應）

## 六十座堅固城與無城牆的鄉村（主題）
query:
- 待建立詞：六十座堅固城與無城牆的鄉村
- 出現位置：申命記 第3章
- 候選類型：主題
- 本章上下文：v4「共有六十座，沒有一座城不被我們所奪」；v5「這些城都有堅固的高牆，有門有閂。此外還有許多無城牆的鄉村」。GT《啟導本》：「從《王上》四13所記，這60座城都是有城牆的大城，還有許多鄉村（5節），其地人口必甚多。」；KC：「No less than sixty fortified cities were taken and also “a great many unwalled towns.”」；BH：「The number sixty signifies completeness and totality」。STEP 顯示 v5 「門」是雙數 de.la.Ta.yim（H1817C，Ncfda）、「無城牆的鄉村」是 ha./pe.ra.Zi（H6521，簡要詞典義 villager，context gloss hamlet-dweller）。
- 經文用詞：六十座、堅固的高牆、無城牆的鄉村

字面解析：對上既有「六十座堅固城與無城牆的鄉村」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 六十座堅固城與無城牆的鄉村 | 0.799 | link_folder/主題/六十座堅固城與無城牆的鄉村.md |
| 2 | 哈倭特睚珥 | 0.541 | link_folder/地點/哈倭特睚珥.md |
| 3 | 沒有一座城高得使我們不能攻取 | 0.483 | link_folder/主題/沒有一座城高得使我們不能攻取.md |
| 4 | 利未人的四十八座城 | 0.451 | link_folder/主題/利未人的四十八座城.md |
| 5 | 郊野（mig.rash） | 0.426 | link_folder/原文/郊野（mig.rash）.md |

判定：✅ 建議使用既有條目 [[六十座堅固城與無城牆的鄉村]]（同名／字面對應）

## 亞珥歌伯（ar.gov）（地點）
query:
- 待建立詞：亞珥歌伯（ar.gov）
- 出現位置：申命記 第3章
- 候選類型：地點
- 本章上下文：v4「這為亞珥歌伯的全境」；v13「亞珥歌伯全地乃是巴珊全地」；v14「睚珥佔了亞珥歌伯全境」。CT 原文字義：「亞珥歌伯」土堆；CT：「『亞珥歌伯』本是巴珊境內東北部多石的一區，此句代表全巴珊」；GT《聖經精讀本》：「此名具有“多石之地”的意思」。STEP 顯示是 'ar.Go（H709G，ar.gov），「全境」是 kol- Che.vel（H2256M che.vel，簡要詞典義 cord）。

字面解析：對上既有「亞珥歌伯（ar.gov）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 亞珥歌伯（ar.gov） | 0.799 | link_folder/地點/亞珥歌伯（ar.gov）.md |
| 2 | 亞珥 | 0.552 | link_folder/地點/亞珥.md |
| 3 | 亞述 | 0.531 | link_folder/地點/亞述.md |
| 4 | 巴珊 | 0.523 | link_folder/地點/巴珊.md |
| 5 | 亞斯她錄 | 0.483 | link_folder/地點/亞斯她錄.md |

判定：✅ 建議使用既有條目 [[亞珥歌伯（ar.gov）]]（同名／字面對應）

## 滅絕（原文）
query:
- 待建立詞：滅絕
- 出現位置：申命記 第3章
- 候選類型：原文
- 本章上下文：v6「我們將這些都毀滅了」。CT 原文字義：「毀滅」完全毀壞。STEP 顯示 v6 用了兩次同一字根 va./na.cha.Rem 與 ha.cha.Rem（H2763A cha.ram，to devote/destroy）。
- 經文用詞：都毀滅了

字面解析：對上既有「滅絕」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 滅絕 | 0.682 | link_folder/原文/滅絕.md |
| 2 | 敗壞與毀滅的文字呼應 | 0.550 | link_folder/原文/敗壞與毀滅的文字呼應.md |
| 3 | 滅絕（herem） | 0.543 | link_folder/神學/滅絕（herem）.md |
| 4 | 人的全面敗壞 | 0.475 | link_folder/神學/人的全面敗壞.md |
| 5 | 毀滅迦南偶像的三道命令 | 0.454 | link_folder/主題/毀滅迦南偶像的三道命令.md |

判定：✅ 建議使用既有條目 [[滅絕]]（同名／字面對應）

## 滅絕（herem）（神學）
query:
- 待建立詞：滅絕（herem）
- 出現位置：申命記 第3章
- 候選類型：神學
- 本章上下文：v6「把有人煙的各城，連女人帶孩子，盡都毀滅」。GT《聖經精讀本》：「以色列的迦南征服戰是基於神命令的耶和華之聖戰,體現了神的公義及保持天國之純潔性」；BH：「This phrase refers to the practice of "herem," a term meaning to devote something to God by completely destroying it.」。
- 經文用詞：盡都毀滅

字面解析：對上既有「滅絕（herem）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 滅絕 | 0.704 | link_folder/原文/滅絕.md |
| 2 | 滅絕（herem） | 0.690 | link_folder/神學/滅絕（herem）.md |
| 3 | 戰勝亞拉得王 | 0.534 | link_folder/歷史/戰勝亞拉得王.md |
| 4 | 迦南人 | 0.534 | link_folder/人物/迦南人.md |
| 5 | 拆毀偶像律例 | 0.532 | link_folder/事件/拆毀偶像律例.md |

判定：✅ 建議使用既有條目 [[滅絕（herem）]]（同名／字面對應）

## 戰利品的分配辦法（主題）
query:
- 待建立詞：戰利品的分配辦法
- 出現位置：申命記 第3章
- 候選類型：主題
- 本章上下文：v7「惟有一切牲畜和城中的財物都取為自己的掠物」。CT〔話中之光〕：「以色列人學會了在得勝以後，先是分別財物，再把財物分別出來歸於神(參民三十一25~54)」。
- 經文用詞：掠物

字面解析：對上既有「戰利品的分配辦法」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 戰利品的分配辦法 | 0.743 | link_folder/主題/戰利品的分配辦法.md |
| 2 | 貢物（Me.khes） | 0.524 | link_folder/原文/貢物（Me.khes）.md |
| 3 | 出埃及時取得埃及財物 | 0.522 | link_folder/解經爭議/出埃及時取得埃及財物.md |
| 4 | 耶和華是事奉者的業與分 | 0.487 | link_folder/神學/耶和華是事奉者的業與分.md |
| 5 | 利未人的什一奉獻 | 0.485 | link_folder/神學/利未人的什一奉獻.md |

判定：✅ 建議使用既有條目 [[戰利品的分配辦法]]（同名／字面對應）

## 亞嫩河（地點）
query:
- 待建立詞：亞嫩河
- 出現位置：申命記 第3章
- 候選類型：地點
- 本章上下文：v8「將亞嫩谷直到黑門山之地奪過來」；v12「從亞嫩谷邊的亞羅珥起」；v16「從基列到亞嫩谷，以谷中為界」。BH：「The Arnon Valley served as a natural boundary between Moab and the Amorite kingdom.」。
- 經文用詞：亞嫩谷

字面解析：對上既有「亞嫩河」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 亞嫩河 | 0.783 | link_folder/地點/亞嫩河.md |
| 2 | 亞羅珥 | 0.675 | link_folder/地點/亞羅珥.md |
| 3 | 亞珥 | 0.597 | link_folder/地點/亞珥.md |
| 4 | 黑門山 | 0.554 | link_folder/地點/黑門山.md |
| 5 | 亞捫人 | 0.550 | link_folder/人物/亞捫人.md |

判定：✅ 建議使用既有條目 [[亞嫩河]]（同名／字面對應）

## 黑門山（地點）
query:
- 待建立詞：黑門山
- 出現位置：申命記 第3章
- 候選類型：地點
- 本章上下文：v8「亞嫩谷直到黑門山之地」；v9「這黑門山，西頓人稱為西連，亞摩利人稱為示尼珥」。CT：「『黑門山』位於利巴嫩之南，南北蜿蜒約達八十公里山脈中的最高峰，約有三千公尺高，長年積雪，峰頂現仍有巴力廟的遺址」；GT 李道生《舊約聖經問題總解》有整段條目；BH：「Mount Hermon marks the northern boundary of the conquered territory.」。STEP 顯示三個名字分別是 cher.Mon（H2768）、sir.Yon（H8303）、se.Nir（H8149），動詞都是 yik.re.'U（H7121H qa.ra）。
- 經文用詞：黑門山、西連、示尼珥

字面解析：對上既有「黑門山」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 黑門山 | 0.883 | link_folder/地點/黑門山.md |
| 2 | 西珥山 | 0.559 | link_folder/地點/西珥山.md |
| 3 | 利巴嫩 | 0.552 | link_folder/地點/利巴嫩.md |
| 4 | 北界的何珥山 | 0.548 | link_folder/地點/北界的何珥山.md |
| 5 | 西乃山的地理 | 0.537 | link_folder/背景/西乃山的地理.md |

判定：✅ 建議使用既有條目 [[黑門山]]（同名／字面對應）

## 平原（mi.shor）（地點）
query:
- 待建立詞：平原（mi.shor）
- 出現位置：申命記 第3章
- 候選類型：地點
- 本章上下文：v10「就是奪了平原的各城」。CT 原文字義：「平原」平地；CT：「『平原的各城』指米底巴平原上諸城(參書十三16)」；GT《啟導本》：「“平原的各城”北起基列，南到亞嫩河」；BH：「The "plateau" refers to the region known as the Mishor, a highland area east of the Jordan River.」。STEP 顯示是 ha./mi.Shor（H4334 mi.shor，簡要詞典義 plain）。
- 經文用詞：平原的各城

字面解析：對上既有「平原（mi.shor）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 平原（mi.shor） | 0.873 | link_folder/地點/平原（mi.shor）.md |
| 2 | 高原（Shephelah） | 0.567 | link_folder/地點/高原（Shephelah）.md |
| 3 | 摩押平原 | 0.542 | link_folder/地點/摩押平原.md |
| 4 | 河東城邑的位置考據 | 0.518 | link_folder/背景/河東城邑的位置考據.md |
| 5 | 應許之地的四至 | 0.480 | link_folder/主題/應許之地的四至.md |

判定：✅ 建議使用既有條目 [[平原（mi.shor）]]（同名／字面對應）

## 基列（地點）
query:
- 待建立詞：基列
- 出現位置：申命記 第3章
- 候選類型：地點
- 本章上下文：v10「基列全地」；v12「基列山地的一半」；v13「其餘的基列地」；v15「我又將基列給了瑪吉」；v16「從基列到亞嫩谷」。CT 原文字義：「基列」多岩之地；CT：「『基列全地』指雅博河以北迄巴珊地南界」；BH：「Gilead is a mountainous region east of the Jordan River, known for its balm, a resin used for medicinal purposes.」。

字面解析：對上既有「基列」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 基列 | 0.772 | link_folder/地點/基列.md |
| 2 | 基列山 | 0.621 | link_folder/地點/基列山.md |
| 3 | 基列胡瑣 | 0.564 | link_folder/地點/基列胡瑣.md |
| 4 | 巴珊 | 0.548 | link_folder/地點/巴珊.md |
| 5 | 基列亞巴 | 0.522 | link_folder/地點/基列亞巴.md |

判定：✅ 建議使用既有條目 [[基列]]（同名／字面對應）

## 撒迦（地點）
query:
- 待建立詞：撒迦
- 出現位置：申命記 第3章
- 候選類型：地點
- 本章上下文：v10「直到撒迦和以得來」。CT 原文字義：「撒迦」遷移；GT《啟導本》：「撒迦位置不詳，或在巴珊最北端（參書十三11）」；GT《串珠》：「「撒迦和以得來」：分別位於巴珊北面和南的邊界」；BH：「Salecah, located on the eastern edge of Bashan, served as a frontier city」。STEP 顯示是 sal.Khah（H5548）。

字面解析：對上既有「撒迦」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 撒迦 | 0.842 | link_folder/地點/撒迦.md |
| 2 | 以得來 | 0.522 | link_folder/地點/以得來.md |
| 3 | 巴珊 | 0.510 | link_folder/地點/巴珊.md |
| 4 | 雅謝 | 0.505 | link_folder/地點/雅謝.md |
| 5 | 撒烈溪 | 0.492 | link_folder/地點/撒烈溪.md |

判定：✅ 建議使用既有條目 [[撒迦]]（同名／字面對應）

## 利乏音人（人物）
query:
- 待建立詞：利乏音人
- 出現位置：申命記 第3章
- 候選類型：人物
- 本章上下文：v11「利乏音人所剩下的只有巴珊王噩」；v13「這叫做利乏音人之地」。CT：「『利乏音人』巨人族(參創十四5)」；GT《雷氏研讀本》：「“噩”。居住在巴勒斯坦的最後一個利乏音人」。STEP 顯示是 ha./re.fa.'Im（H7497B）。

字面解析：對上既有「利乏音人」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 利乏音人 | 0.717 | link_folder/人物/利乏音人.md |
| 2 | 以色列戰勝巴珊王噩互文（申3：1-11；詩135：10-12；136：17-22） | 0.504 | link_folder/互文/以色列戰勝巴珊王噩互文（申3：1-11；詩135：10-12；136：17-22）.md |
| 3 | 散送冥 | 0.501 | link_folder/人物/散送冥.md |
| 4 | 巴珊 | 0.487 | link_folder/地點/巴珊.md |
| 5 | 以米人 | 0.466 | link_folder/人物/以米人.md |

判定：✅ 建議使用既有條目 [[利乏音人]]（同名／字面對應）

## 巴珊王噩的鐵床（e.re.s）（原文）
query:
- 待建立詞：巴珊王噩的鐵床（e.re.s）
- 出現位置：申命記 第3章
- 候選類型：原文
- 本章上下文：v11「他的床是鐵的，長九肘，寬四肘，都是以人肘為度。現今豈不是在亞捫人的拉巴嗎？」。GT《雷氏研讀本》：「他的鐵“床”一直被理解為用鐵來裝飾的石棺材，或準備放在他墓穴中、有鐵裝飾的臥榻，或由玄武岩（含鐵的石）鑿刻的紀念碑」；GT《啟導本》：「“床”可指“棺槨”」；GT《串珠》：「「床」：可能指棺木」；BH：「Iron was a valuable and durable material, suggesting Og's wealth and status.」。STEP 顯示是 ar.S/o 'E.res（H6210 e.re.s），簡要詞典義 bed，context gloss 給 sarcophagus。
- 經文用詞：他的床是鐵的

字面解析：對上既有「巴珊王噩的鐵床（e.re.s）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 巴珊王噩的鐵床（e.re.s） | 0.842 | link_folder/原文/巴珊王噩的鐵床（e.re.s）.md |
| 2 | 以人肘為度 | 0.458 | link_folder/文化/以人肘為度.md |
| 3 | 以色列戰勝巴珊王噩互文（申3：1-11；詩135：10-12；136：17-22） | 0.437 | link_folder/互文/以色列戰勝巴珊王噩互文（申3：1-11；詩135：10-12；136：17-22）.md |
| 4 | 床頭或杖頭 | 0.436 | link_folder/解經爭議/床頭或杖頭.md |
| 5 | 天如鐵地如銅（乾旱咒詛的意象） | 0.399 | link_folder/主題/天如鐵地如銅（乾旱咒詛的意象）.md |

判定：✅ 建議使用既有條目 [[巴珊王噩的鐵床（e.re.s）]]（同名／字面對應）

## 以人肘為度（文化）
query:
- 待建立詞：以人肘為度
- 出現位置：申命記 第3章
- 候選類型：文化
- 本章上下文：v11「長九肘，寬四肘，都是以人肘為度」。CT：「『以人肘為度』指古時以色列人的度量衡以肘為長度單位，一肘相當於一般男子肘至中指尖的長度，約折合零點四五公尺」；GT《啟導本》：「“人肘”指當時通用的量度單位」；GT《串珠》：「「以人肘為度」：即按照通常的尺寸來量度」；BH：「a cubit is approximately 18 inches, making the bed about 13.5 feet long and 6 feet wide」。STEP 顯示是 be./'a.mat- 'Ish（H520A am.mah cubit ＋ H376G ish）。
- 經文用詞：以人肘為度

字面解析：對上既有「以人肘為度」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 以人肘為度 | 0.892 | link_folder/文化/以人肘為度.md |
| 2 | 巴珊王噩的鐵床（e.re.s） | 0.546 | link_folder/原文/巴珊王噩的鐵床（e.re.s）.md |
| 3 | 方舟的尺寸與結構 | 0.464 | link_folder/背景/方舟的尺寸與結構.md |
| 4 | 伊法 | 0.449 | link_folder/原文/伊法.md |
| 5 | 舍客勒 | 0.421 | link_folder/原文/舍客勒.md |

判定：✅ 建議使用既有條目 [[以人肘為度]]（同名／字面對應）

## 亞捫人（人物）
query:
- 待建立詞：亞捫人
- 出現位置：申命記 第3章
- 候選類型：人物
- 本章上下文：v11「現今豈不是在亞捫人的拉巴嗎？」；v16「直到亞捫人交界的雅博河」。CT：「『亞捫人』是亞伯拉罕的侄兒羅得與他次女亂倫所生的子孫(參創十九36，38)，和以色列人有血緣關係；『拉巴』位於雅博河上游支流的北岸，後來劃歸迦得支派」；BH：「Rabbah, the capital of the Ammonites, is modern-day Amman, Jordan.」。

字面解析：對上既有「亞捫人」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 亞捫人 | 0.774 | link_folder/人物/亞捫人.md |
| 2 | 亞蘭人 | 0.580 | link_folder/人物/亞蘭人.md |
| 3 | 摩押人 | 0.576 | link_folder/人物/摩押人.md |
| 4 | 羅得 | 0.573 | link_folder/人物/羅得.md |
| 5 | 摩押 | 0.571 | link_folder/人物/摩押.md |

判定：✅ 建議使用既有條目 [[亞捫人]]（同名／字面對應）

## 亞羅珥（地點）
query:
- 待建立詞：亞羅珥
- 出現位置：申命記 第3章
- 候選類型：地點
- 本章上下文：v12「從亞嫩谷邊的亞羅珥起」。CT：「『亞羅珥』位於死海中部東方約20公里處，亞嫩河北畔的一座城(參二36)」；BH：「Aroer was a city located on the northern edge of the Arnon Valley, which served as a natural boundary.」。

字面解析：對上既有「亞羅珥」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 亞羅珥 | 0.829 | link_folder/地點/亞羅珥.md |
| 2 | 亞嫩河 | 0.610 | link_folder/地點/亞嫩河.md |
| 3 | 亞珥 | 0.564 | link_folder/地點/亞珥.md |
| 4 | 瑣珥 | 0.506 | link_folder/地點/瑣珥.md |
| 5 | 何珥山 | 0.500 | link_folder/地點/何珥山.md |

判定：✅ 建議使用既有條目 [[亞羅珥]]（同名／字面對應）

## 流便（人物）
query:
- 待建立詞：流便
- 出現位置：申命記 第3章
- 候選類型：人物
- 本章上下文：v12「都給了流便人和迦得人」；v16「我給了流便人和迦得人」。BH：「The Reubenites and Gadites were two of the twelve tribes of Israel. Their request for land on the east side of the Jordan was based on its suitability for their large herds and flocks.」。
- 經文用詞：流便人

字面解析：對上既有「流便」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 流便 | 0.588 | link_folder/人物/流便.md |
| 2 | 兩支派半求河東之地為業 | 0.554 | link_folder/事件/兩支派半求河東之地為業.md |
| 3 | 迦得（萬幸） | 0.523 | link_folder/人物/迦得（萬幸）.md |
| 4 | 亞捫人 | 0.493 | link_folder/人物/亞捫人.md |
| 5 | 十二支派起源 | 0.488 | link_folder/神學/十二支派起源.md |

判定：✅ 建議使用既有條目 [[流便]]（同名／字面對應）

## 迦得（萬幸）（人物）
query:
- 待建立詞：迦得（萬幸）
- 出現位置：申命記 第3章
- 候選類型：人物
- 本章上下文：v12、v16「流便人和迦得人」。CT 原文字義：「迦得」軍隊，財富。GT《聖經精讀本》：「將從亞嫩谷邊的亞羅珥起到雅博江之鄉的南部地區賜給流便與迦得支派」。
- 經文用詞：迦得人

字面解析：對上既有「迦得（萬幸）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 迦得（萬幸） | 0.731 | link_folder/人物/迦得（萬幸）.md |
| 2 | 迦得（幸運） | 0.595 | link_folder/原文/迦得（幸運）.md |
| 3 | 迦南人 | 0.560 | link_folder/人物/迦南人.md |
| 4 | 迦勒 | 0.535 | link_folder/人物/迦勒.md |
| 5 | 底本 | 0.532 | link_folder/地點/底本.md |

判定：✅ 建議使用既有條目 [[迦得（萬幸）]]（同名／字面對應）

## 兩支派半求河東之地為業（事件）
query:
- 待建立詞：兩支派半求河東之地為業
- 出現位置：申命記 第3章
- 候選類型：事件
- 本章上下文：v18-20 摩西回顧當年立的約。GT《聖經精讀本》：「當時,流便支派、迦得支派、瑪拿西半個支派向摩西請求將約但河地賜給他們為業。摩西與他們立約條件是他們當在迦南征服戰中作先鋒(民32:16-42)」；KC：「He recalls the two and a half tribes' commitment to help conquer the land first.」。
- 經文用詞：在你們的弟兄以色列人前面過去

字面解析：對上既有「兩支派半求河東之地為業」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 兩支派半求河東之地為業 | 0.794 | link_folder/事件/兩支派半求河東之地為業.md |
| 2 | 河東之地是神的旨意還是神的允許 | 0.650 | link_folder/解經爭議/河東之地是神的旨意還是神的允許.md |
| 3 | 瑪拿西半支派為何留在河東 | 0.624 | link_folder/解經爭議/瑪拿西半支派為何留在河東.md |
| 4 | 摩西是否未求問耶和華就允准 | 0.596 | link_folder/解經爭議/摩西是否未求問耶和華就允准.md |
| 5 | 河東二支派半最先被擄（代上5：25-26） | 0.586 | link_folder/互文/河東二支派半最先被擄（代上5：25-26）.md |

判定：✅ 建議使用既有條目 [[兩支派半求河東之地為業]]（同名／字面對應）

## 河東之地是神的旨意還是神的允許（解經爭議）
query:
- 待建立詞：河東之地是神的旨意還是神的允許
- 出現位置：申命記 第3章
- 候選類型：解經爭議
- 本章上下文：v18「耶和華你們的神已將這地賜給你們為業」。摩西在本章把河東之地直接說成耶和華所賜，是這個爭議在申命記這一端的關鍵敘述。
- 經文用詞：已將這地賜給你們為業

字面解析：對上既有「河東之地是神的旨意還是神的允許」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 河東之地是神的旨意還是神的允許 | 0.774 | link_folder/解經爭議/河東之地是神的旨意還是神的允許.md |
| 2 | 摩西是否未求問耶和華就允准 | 0.651 | link_folder/解經爭議/摩西是否未求問耶和華就允准.md |
| 3 | 兩支派半求河東之地為業 | 0.564 | link_folder/事件/兩支派半求河東之地為業.md |
| 4 | 為業（ye.ru.shah） | 0.528 | link_folder/原文/為業（ye.ru.shah）.md |
| 5 | 窺探迦南起因為神命或民意的解經爭議 | 0.525 | link_folder/解經爭議/窺探迦南起因為神命或民意的解經爭議.md |

判定：✅ 建議使用既有條目 [[河東之地是神的旨意還是神的允許]]（同名／字面對應）

## 瑪拿西（人物）
query:
- 待建立詞：瑪拿西
- 出現位置：申命記 第3章
- 候選類型：人物
- 本章上下文：v14「瑪拿西的子孫睚珥」。BH：「Jair was a prominent figure among the descendants of Manasseh, one of the tribes of Israel.」。
- 經文用詞：瑪拿西的子孫

字面解析：對上既有「瑪拿西」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 瑪拿西 | 0.549 | link_folder/人物/瑪拿西.md |
| 2 | 瑪吉 | 0.544 | link_folder/人物/瑪吉.md |
| 3 | 睚珥 | 0.503 | link_folder/人物/睚珥.md |
| 4 | 瑪拿西支派人數大增 | 0.492 | link_folder/主題/瑪拿西支派人數大增.md |
| 5 | 瑪土撒利 | 0.452 | link_folder/人物/瑪土撒利.md |

判定：✅ 建議使用既有條目 [[瑪拿西]]（同名／字面對應）

## 瑪拿西半支派為何留在河東（解經爭議）
query:
- 待建立詞：瑪拿西半支派為何留在河東
- 出現位置：申命記 第3章
- 候選類型：解經爭議
- 本章上下文：v13「其餘的基列地和巴珊全地，就是噩王的國，我給了瑪拿西半支派」。CT：「『瑪拿西半支派』瑪拿西的子孫共有八個家族⋯瑪吉族和基列族留在約但河東岸」。
- 經文用詞：瑪拿西半支派

字面解析：對上既有「瑪拿西半支派為何留在河東」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 瑪拿西半支派為何留在河東 | 0.810 | link_folder/解經爭議/瑪拿西半支派為何留在河東.md |
| 2 | 瑪吉 | 0.642 | link_folder/人物/瑪吉.md |
| 3 | 瑪拿西 | 0.604 | link_folder/人物/瑪拿西.md |
| 4 | 河東之地是神的旨意還是神的允許 | 0.577 | link_folder/解經爭議/河東之地是神的旨意還是神的允許.md |
| 5 | 兩支派半求河東之地為業 | 0.564 | link_folder/事件/兩支派半求河東之地為業.md |

判定：✅ 建議使用既有條目 [[瑪拿西半支派為何留在河東]]（同名／字面對應）

## 睚珥（人物）
query:
- 待建立詞：睚珥
- 出現位置：申命記 第3章
- 候選類型：人物
- 本章上下文：v14「瑪拿西的子孫睚珥佔了亞珥歌伯全境」。CT：「『睚珥』是猶大支派希斯崙的兒子西割和瑪吉的女兒結婚所生的兒子，歸屬母親家族，故稱瑪拿西的子孫(參民三十二41)」；GT《聖經精讀本》：「若從父系就是猶大的五代子孫,在這裡則從了母系(代上2:3-24)」。

字面解析：對上既有「睚珥」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 睚珥 | 0.774 | link_folder/人物/睚珥.md |
| 2 | 瑪吉 | 0.603 | link_folder/人物/瑪吉.md |
| 3 | 瑪拿西 | 0.568 | link_folder/人物/瑪拿西.md |
| 4 | 摩押 | 0.562 | link_folder/人物/摩押.md |
| 5 | 猶大支派 | 0.547 | link_folder/人物/猶大支派.md |

判定：✅ 建議使用既有條目 [[睚珥]]（同名／字面對應）

## 基述人和瑪迦人（人物）
query:
- 待建立詞：基述人和瑪迦人
- 出現位置：申命記 第3章
- 候選類型：人物
- 本章上下文：v14「直到基述人和瑪迦人的交界」。CT：「『基述人和瑪迦人』指巴珊地的北面，加利利海東面的兩個小邦，基述在南，瑪迦在北，這兩個小邦直到大衛王的時代仍存在(參撒下三3；十6)」；GT《啟導本》：「基述和瑪迦都是位於巴珊北部的小邦。基述在加利利海東岸，瑪迦在基述之北。」；BH：「These groups maintained their distinct identities and were not fully conquered by the Israelites, as noted in other biblical passages (Joshua 13:13).」。STEP 顯示是 ha./ge.shu.Ri（H1651）與 ha./ma.'a.kha.Ti（H4602）。
- 經文用詞：基述人和瑪迦人

字面解析：對上既有「基述人和瑪迦人」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 基述人和瑪迦人 | 0.871 | link_folder/人物/基述人和瑪迦人.md |
| 2 | 基列 | 0.536 | link_folder/地點/基列.md |
| 3 | 巴珊 | 0.523 | link_folder/地點/巴珊.md |
| 4 | 基提（Kittim） | 0.501 | link_folder/地點/基提（Kittim）.md |
| 5 | 撒迦 | 0.496 | link_folder/地點/撒迦.md |

判定：✅ 建議使用既有條目 [[基述人和瑪迦人]]（同名／字面對應）

## 哈倭特睚珥（地點）
query:
- 待建立詞：哈倭特睚珥
- 出現位置：申命記 第3章
- 候選類型：地點
- 本章上下文：v14「就按自己的名稱這巴珊地為哈倭特睚珥，直到今日」。CT：「『哈倭特睚珥』直譯為「睚珥的一切城邑」(參書十三30；士十4；王上四13)，是一些沒有城牆的村落」；BH：「By renaming Bashan as Havvoth-jair, which means "villages of Jair," Jair established his legacy and marked his authority over the region.」。STEP 把整個名字當一個 Strong：cha.Vot ya.'Ir（H2334）。

字面解析：對上既有「哈倭特睚珥」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 哈倭特睚珥 | 0.793 | link_folder/地點/哈倭特睚珥.md |
| 2 | 睚珥 | 0.570 | link_folder/人物/睚珥.md |
| 3 | 亞珥歌伯（ar.gov） | 0.568 | link_folder/地點/亞珥歌伯（ar.gov）.md |
| 4 | 巴珊 | 0.537 | link_folder/地點/巴珊.md |
| 5 | 六十座堅固城與無城牆的鄉村 | 0.524 | link_folder/主題/六十座堅固城與無城牆的鄉村.md |

判定：✅ 建議使用既有條目 [[哈倭特睚珥]]（同名／字面對應）

## 瑪吉（人物）
query:
- 待建立詞：瑪吉
- 出現位置：申命記 第3章
- 候選類型：人物
- 本章上下文：v15「我又將基列給了瑪吉」。CT：「『瑪吉』是瑪拿西唯一的兒子，瑪吉又僅有一個兒子基列」；GT《啟導本》：「瑪姬是約瑟之子瑪拿西的長子，也是基列人的祖先（書十七1）。」；BH：「Machir was the firstborn son of Manasseh, the son of Joseph.」。

字面解析：對上既有「瑪吉」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 瑪吉 | 0.797 | link_folder/人物/瑪吉.md |
| 2 | 瑪拿西 | 0.561 | link_folder/人物/瑪拿西.md |
| 3 | 睚珥 | 0.493 | link_folder/人物/睚珥.md |
| 4 | 瑪拿西半支派為何留在河東 | 0.482 | link_folder/解經爭議/瑪拿西半支派為何留在河東.md |
| 5 | 收納以法蓮與瑪拿西 | 0.479 | link_folder/歷史/收納以法蓮與瑪拿西.md |

判定：✅ 建議使用既有條目 [[瑪吉]]（同名／字面對應）

## 雅博渡口（地點）
query:
- 待建立詞：雅博渡口
- 出現位置：申命記 第3章
- 候選類型：地點
- 本章上下文：v16「直到亞捫人交界的雅博河」。BH：「The Jabbok River, now known as the Zarqa River, was another important boundary marker. It flows into the Jordan River and was the site where Jacob wrestled with God in Genesis 32:22-32」。
- 經文用詞：雅博河

字面解析：對上既有「雅博渡口」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 雅博渡口 | 0.784 | link_folder/地點/雅博渡口.md |
| 2 | 約但河 | 0.585 | link_folder/地點/約但河.md |
| 3 | 雅博渡口經歷 (創32) | 0.549 | link_folder/互文/雅博渡口經歷 (創32).md |
| 4 | 摔跤 | 0.534 | link_folder/原文/摔跤.md |
| 5 | 「伯拉大河」名稱 | 0.520 | link_folder/原文/「伯拉大河」名稱.md |

判定：✅ 建議使用既有條目 [[雅博渡口]]（同名／字面對應）

## 亞拉巴（地點）
query:
- 待建立詞：亞拉巴
- 出現位置：申命記 第3章
- 候選類型：地點
- 本章上下文：v17「又將亞拉巴和靠近約但河之地」。CT：「『亞拉巴』指約但河流域從北邊的加利利海到死海南端以迄阿卡巴灣的河谷地帶」。STEP 顯示是 ha./'a.ra.Vah（H6160G）。

字面解析：對上既有「亞拉巴」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 亞拉巴 | 0.748 | link_folder/地點/亞拉巴.md |
| 2 | 亞羅珥 | 0.551 | link_folder/地點/亞羅珥.md |
| 3 | 應許之地的四至 | 0.549 | link_folder/主題/應許之地的四至.md |
| 4 | 鹽海 | 0.521 | link_folder/地點/鹽海.md |
| 5 | 亞巴琳山 | 0.500 | link_folder/地點/亞巴琳山.md |

判定：✅ 建議使用既有條目 [[亞拉巴]]（同名／字面對應）

## 基尼烈湖（地點）
query:
- 待建立詞：基尼烈湖
- 出現位置：申命記 第3章
- 候選類型：地點
- 本章上下文：v17「從基尼烈直到亞拉巴海」。CT：「『基尼烈』或指加利利海，或指加利利海西北岸的一城」；GT《啟導本》：「“基尼烈”為拿弗他利支派所得的一個城，位於加利利海西北岸（加利利海在舊約時代叫做基尼烈湖，見民三十四11）」。STEP 顯示是 mi./ki.Ne.ret（H3672G）。
- 經文用詞：基尼烈

字面解析：對上既有「基尼烈湖」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 基尼烈湖 | 0.803 | link_folder/地點/基尼烈湖.md |
| 2 | 基尼人 | 0.555 | link_folder/人物/基尼人.md |
| 3 | 挪巴 | 0.531 | link_folder/人物/挪巴.md |
| 4 | 基列 | 0.526 | link_folder/地點/基列.md |
| 5 | 河東城邑的位置考據 | 0.504 | link_folder/背景/河東城邑的位置考據.md |

判定：✅ 建議使用既有條目 [[基尼烈湖]]（同名／字面對應）

## 鹽海（地點）
query:
- 待建立詞：鹽海
- 出現位置：申命記 第3章
- 候選類型：地點
- 本章上下文：v17「從基尼烈直到亞拉巴海，就是鹽海」。GT《啟導本》：「鹽海即死海，舊約中無“死海”之名，主後第一或第二世紀，始名“死海”」。STEP 顯示是 yam ha./'a.ra.Vah 與 yam ha./Me.lach（H3220G＋H6160G／H4417G）。

字面解析：對上既有「鹽海」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 鹽海 | 0.742 | link_folder/地點/鹽海.md |
| 2 | 亞拉巴 | 0.583 | link_folder/地點/亞拉巴.md |
| 3 | 基尼烈湖 | 0.573 | link_folder/地點/基尼烈湖.md |
| 4 | 紅海指的是哪個海 | 0.532 | link_folder/解經爭議/紅海指的是哪個海.md |
| 5 | 海（紅海） | 0.528 | link_folder/地點/海（紅海）.md |

判定：✅ 建議使用既有條目 [[鹽海]]（同名／字面對應）

## 瑣腓田與毘斯迦山頂（地點）
query:
- 待建立詞：瑣腓田與毘斯迦山頂
- 出現位置：申命記 第3章
- 候選類型：地點
- 本章上下文：v17「並毘斯迦山根東邊之地」；v27「你且上毘斯迦山頂去」。CT：「『毘斯迦』亦即摩西所登遠望迦南之山峰，在死海東邊摩押平原的尼波山上」；GT《聖經精讀本》：「毗斯迦山: 是位於耶利哥對面的山,似乎是以尼波山(34:1)為最高峰的亞巴琳山脈(民27:12)的組成部分。」。STEP 顯示 v17「山根」是 'ash.Dot ha./pis.Gah（H798，簡要詞典義 Slopes of Pisgah）。
- 經文用詞：毘斯迦

字面解析：對上既有「瑣腓田與毘斯迦山頂」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 瑣腓田與毘斯迦山頂 | 0.785 | link_folder/地點/瑣腓田與毘斯迦山頂.md |
| 2 | 亞巴琳山 | 0.630 | link_folder/地點/亞巴琳山.md |
| 3 | 毘珥山頂 | 0.596 | link_folder/地點/毘珥山頂.md |
| 4 | 摩押地 | 0.589 | link_folder/地點/摩押地.md |
| 5 | 山頂 | 0.551 | link_folder/地點/山頂.md |

判定：✅ 建議使用既有條目 [[瑣腓田與毘斯迦山頂]]（同名／字面對應）

## 勇士（cha.yil）（原文）
query:
- 待建立詞：勇士（cha.yil）
- 出現位置：申命記 第3章
- 候選類型：原文
- 本章上下文：v18「你們所有的勇士都要帶著兵器」。CT 原文字義：「勇士(原文雙字)」有能力的，武力(首字)；兒子，少壯的(次字)；CT：「『所有的勇士』指可以上戰場的男人」；BH：「The phrase "men of valor" indicates the need for courage and readiness in fulfilling God's commands.」。STEP 顯示是 be.nei- Cha.yil（H1121G ben ＋ H2428G cha.yil，簡要詞典義 strength），「帶著兵器」是 cha.lu.Tzim（H2502B cha.lats，to arm，被動分詞）。
- 經文用詞：勇士

字面解析：對上既有「勇士（cha.yil）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 勇士（cha.yil） | 0.847 | link_folder/原文/勇士（cha.yil）.md |
| 2 | 帶兵器（cha.lats） | 0.638 | link_folder/原文/帶兵器（cha.lats）.md |
| 3 | 以色列人帶兵器 | 0.550 | link_folder/歷史/以色列人帶兵器.md |
| 4 | 耶和華是戰士 | 0.518 | link_folder/神學/耶和華是戰士.md |
| 5 | 昂然無懼 | 0.488 | link_folder/原文/昂然無懼.md |

判定：✅ 建議使用既有條目 [[勇士（cha.yil）]]（同名／字面對應）

## 帶兵器（cha.lats）（原文）
query:
- 待建立詞：帶兵器（cha.lats）
- 出現位置：申命記 第3章
- 候選類型：原文
- 本章上下文：v18「你們所有的勇士都要帶著兵器」。STEP 顯示是 cha.lu.Tzim（H2502B cha.lats，to arm，Vqsmpa 被動分詞），與民32:30、32 完全同形。
- 經文用詞：帶著兵器

字面解析：對上既有「帶兵器（cha.lats）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 帶兵器（cha.lats） | 0.770 | link_folder/原文/帶兵器（cha.lats）.md |
| 2 | 勇士（cha.yil） | 0.655 | link_folder/原文/勇士（cha.yil）.md |
| 3 | 以色列人帶兵器 | 0.568 | link_folder/歷史/以色列人帶兵器.md |
| 4 | 以色列人的軍隊 | 0.435 | link_folder/神學/以色列人的軍隊.md |
| 5 | 以色列人出埃及的軍隊 | 0.427 | link_folder/歷史/以色列人出埃及的軍隊.md |

判定：✅ 建議使用既有條目 [[帶兵器（cha.lats）]]（同名／字面對應）

## 得享平安（nu.ach）（原文）
query:
- 待建立詞：得享平安（nu.ach）
- 出現位置：申命記 第3章
- 候選類型：原文
- 本章上下文：v20「又使他們得享平安，與你們一樣」。CT 原文字義：「平安」休息，安歇；CT：「『得享平安』意指消滅境內任何有組織的敵人」；GT《啟導本》：「以色列人到了迦南之後，在新土上安頓，無仇敵擾害、沒有強國的壓迫與內亂，也免於流浪、饑饉和瘟疫，“得享平安”（參十二9～10；二十五19）」；KC：「If we ourselves have rest, we will seek it for our brothers.」；BH：「The idea of rest is further developed in the New Testament, where it is fulfilled in Jesus Christ, who offers spiritual rest to believers (Matthew 11:28-30, Hebrews 4:1-11).」。STEP 顯示是 ya.Ni.ach（H5117 nu.ach，to rest，Hiphil「he will give rest」）。
- 經文用詞：得享平安

字面解析：對上既有「得享平安（nu.ach）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 得享平安（nu.ach） | 0.873 | link_folder/原文/得享平安（nu.ach）.md |
| 2 | 平安（shalom） | 0.647 | link_folder/原文/平安（shalom）.md |
| 3 | 希伯來書4章神的安息 | 0.582 | link_folder/互文/希伯來書4章神的安息.md |
| 4 | 平安的約 | 0.564 | link_folder/主題/平安的約.md |
| 5 | 平安祭 | 0.544 | link_folder/神學/平安祭.md |

判定：✅ 建議使用既有條目 [[得享平安（nu.ach）]]（同名／字面對應）

## 為業（ye.ru.shah）（原文）
query:
- 待建立詞：為業（ye.ru.shah）
- 出現位置：申命記 第3章
- 候選類型：原文
- 本章上下文：v20「你們才可以回到我所賜給你們為業之地」。STEP 顯示是 li./ru.sha.T/o（H3425 ye.rush.shah，簡要詞典義 possession），與申2 同一個 Extended Strong；同章 v18「賜給你們為業」用的是動詞 le./rish.Ta/h（H3423H ya.rash）。
- 經文用詞：為業之地

字面解析：對上既有「為業（ye.ru.shah）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 為業（ye.ru.shah） | 0.719 | link_folder/原文/為業（ye.ru.shah）.md |
| 2 | 這地必落給你們為業（na.phal） | 0.571 | link_folder/原文/這地必落給你們為業（na.phal）.md |
| 3 | 業地（a.chuz.zah） | 0.527 | link_folder/原文/業地（a.chuz.zah）.md |
| 4 | 耶和華是事奉者的業與分 | 0.490 | link_folder/神學/耶和華是事奉者的業與分.md |
| 5 | 得享平安（nu.ach） | 0.490 | link_folder/原文/得享平安（nu.ach）.md |

判定：✅ 建議使用既有條目 [[為業（ye.ru.shah）]]（同名／字面對應）

## 約書亞（人物）
query:
- 待建立詞：約書亞
- 出現位置：申命記 第3章
- 候選類型：人物
- 本章上下文：v21「那時我吩咐約書亞說」；v28「你卻要囑咐約書亞」。GT《串珠》：「這位顯赫一時的軍事領袖（出17:9），曾被稱為摩西的幫手和摩西所揀選的一個人（參出24:13; 民11:28），現被神立為摩西的接棒人乃眾望所歸的事（詳情見民27:15-23）」。STEP 顯示是 ye.ho.Shu.a'（H3091G）。

字面解析：對上既有「約書亞」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 約書亞 | 0.677 | link_folder/人物/約書亞.md |
| 2 | 約書亞承接摩西 | 0.670 | link_folder/事件/約書亞承接摩西.md |
| 3 | 摩西與約書亞的權柄差異 | 0.614 | link_folder/主題/摩西與約書亞的權柄差異.md |
| 4 | 勉勵他使他膽壯（cha.zaq、a.mats） | 0.604 | link_folder/原文/勉勵他使他膽壯（cha.zaq、a.mats）.md |
| 5 | 何西阿與約書亞改名時機與字意之解經爭議 | 0.550 | link_folder/解經爭議/何西阿與約書亞改名時機與字意之解經爭議.md |

判定：✅ 建議使用既有條目 [[約書亞]]（同名／字面對應）

## 你親眼看見了（主題）
query:
- 待建立詞：你親眼看見了
- 出現位置：申命記 第3章
- 候選類型：主題
- 本章上下文：v21「你親眼看見了耶和華你神向這二王所行的」。CT：「『你親眼看見』直譯為「你自己的眼睛，就是看見一切的眼睛」」；KC：「Seeing something with one's own eyes makes God's acts of salvation toward His people actual for every generation. Moses uses this expression more often in this book (Deu 4:3,9; 7:19; 9:17; 10:21; 11:12; 34:4).」；BH：「The phrase emphasizes the importance of eyewitness testimony in establishing faith and confidence in God's promises.」。STEP 顯示是 'ei.Nei./kha ha./ro.'Ot（H5869A a.yin ＋ H7200G ra.ah，帶冠詞的陰性複數分詞）。
- 經文用詞：你親眼看見了

字面解析：對上既有「你親眼看見了」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 你親眼看見了 | 0.828 | link_folder/主題/你親眼看見了.md |
| 2 | 信心與眼見 | 0.574 | link_folder/神學/信心與眼見.md |
| 3 | 不隨從己心眼目行邪淫與成為聖潔 | 0.538 | link_folder/神學/不隨從己心眼目行邪淫與成為聖潔.md |
| 4 | 你與你們的單複數交替 | 0.529 | link_folder/原文/你與你們的單複數交替.md |
| 5 | 眼目明亮（ga.lah） | 0.528 | link_folder/原文/眼目明亮（ga.lah）.md |

判定：✅ 建議使用既有條目 [[你親眼看見了]]（同名／字面對應）

## 耶和華的爭戰（神學）
query:
- 待建立詞：耶和華的爭戰
- 出現位置：申命記 第3章
- 候選類型：神學
- 本章上下文：v22「你不要怕他們，因那為你爭戰的是耶和華你的神」。GT《聖經精讀本》：「因為約書亞在聽此番話時,心中必想起在與西宏和噩的爭戰中,在紅海海岸為了以色列的緣故親自與法老的軍隊爭戰的那位神(出14:13-31)」；BH：「The concept of God as a warrior is prevalent in the Old Testament, portraying Him as one who actively participates in the battles of His people.」。STEP 顯示是 ha./nil.Cham（H3898A la.cham，to fight，Niphal 分詞）。
- 經文用詞：爭戰

字面解析：對上既有「耶和華的爭戰」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 耶和華的爭戰 | 0.790 | link_folder/神學/耶和華的爭戰.md |
| 2 | 耶和華是戰士 | 0.695 | link_folder/神學/耶和華是戰士.md |
| 3 | 在耶和華面前 | 0.597 | link_folder/神學/在耶和華面前.md |
| 4 | 耶和華 | 0.543 | link_folder/神學/耶和華.md |
| 5 | 戰勝亞瑪力人 | 0.536 | link_folder/事件/戰勝亞瑪力人.md |

判定：✅ 建議使用既有條目 [[耶和華的爭戰]]（同名／字面對應）

## 懇求（cha.nan）（原文）
query:
- 待建立詞：懇求（cha.nan）
- 出現位置：申命記 第3章
- 候選類型：原文
- 本章上下文：v23「那時，我懇求耶和華說」。CT 原文字義：「懇求」求恩，憐憫；BH：「The Hebrew word used here can imply a sense of desperation or urgency, highlighting Moses' strong desire for God's favor.」；KC：「He did not speak his question in rebellion.」。STEP 顯示是 va./'et.cha.Nan（H2603A cha.nan，簡要詞典義 be gracious，Hitpael 未完成敘述式）。
- 經文用詞：懇求

字面解析：對上既有「懇求（cha.nan）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 懇求（cha.nan） | 0.831 | link_folder/原文/懇求（cha.nan）.md |
| 2 | 罷了（rav） | 0.600 | link_folder/原文/罷了（rav）.md |
| 3 | 摩西的代求 | 0.556 | link_folder/神學/摩西的代求.md |
| 4 | 摩西代求與神的豐盛慈愛 | 0.541 | link_folder/神學/摩西代求與神的豐盛慈愛.md |
| 5 | 代求 | 0.513 | link_folder/神學/代求.md |

判定：✅ 建議使用既有條目 [[懇求（cha.nan）]]（同名／字面對應）

## 主耶和華（a.do.nai）（神學）
query:
- 待建立詞：主耶和華（a.do.nai）
- 出現位置：申命記 第3章
- 候選類型：神學
- 本章上下文：v24「主耶和華啊，你已將你的大力大能顯給僕人看」。GT《串珠》思想問題：「「主耶和華」一詞（24）在申命記中只出現兩次（另一處在9:26），都是摩西祈禱時對神的稱呼，與亞伯拉罕對神的稱呼相同（見創15:2, 8）」。STEP 顯示是 'a.do.Nai（H136 a.do.nai）加 Yah.weh（H3069），與本章其他各處的 Yah.weh（H3068G）不是同一個 Extended Strong。
- 經文用詞：主耶和華

字面解析：對上既有「主耶和華（a.do.nai）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 主耶和華（a.do.nai） | 0.842 | link_folder/神學/主耶和華（a.do.nai）.md |
| 2 | 耶和華 | 0.595 | link_folder/神學/耶和華.md |
| 3 | 在天上在地下有什麼神能像你 | 0.568 | link_folder/神學/在天上在地下有什麼神能像你.md |
| 4 | 稱摩西為我主 | 0.560 | link_folder/主題/稱摩西為我主.md |
| 5 | 耶和華聖名的啟示 | 0.554 | link_folder/神學/耶和華聖名的啟示.md |

判定：✅ 建議使用既有條目 [[主耶和華（a.do.nai）]]（同名／字面對應）

## 大能的手（神學）
query:
- 待建立詞：大能的手
- 出現位置：申命記 第3章
- 候選類型：神學
- 本章上下文：v24「你已將你的大力大能顯給僕人看」。CT 原文字義：「大力」偉大，高大；「大能(原文雙字)」手(首字)；強壯的，堅固的(次字)；CT：「『大能』按原文另譯「大能的手」」。STEP 顯示是 ga.de.le./Kha（H1433 go.del）＋ ya.de./Kha ha./cha.za.Kah（H3027H yad ＋ H2389 cha.zaq），同節的「大能的作為」則是另一個字 ge.vu.ro.Te./kha（H1369 ge.vu.rah）。
- 經文用詞：大力大能

字面解析：對上既有「大能的手」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 大能的手 | 0.694 | link_folder/神學/大能的手.md |
| 2 | 大能的手與出埃及神蹟 | 0.580 | link_folder/神學/大能的手與出埃及神蹟.md |
| 3 | 在天上在地下有什麼神能像你 | 0.537 | link_folder/神學/在天上在地下有什麼神能像你.md |
| 4 | 伸出來的膀臂 | 0.517 | link_folder/神學/伸出來的膀臂.md |
| 5 | 神的右手 | 0.503 | link_folder/神學/神的右手.md |

判定：✅ 建議使用既有條目 [[大能的手]]（同名／字面對應）

## 起首得那地（cha.lal）（原文）
query:
- 待建立詞：起首得那地（cha.lal）
- 出現位置：申命記 第3章
- 候選類型：原文
- 本章上下文：v24「你已將你的大力大能顯給僕人看」的「已」。STEP 顯示是 ha.chi.Lo.ta（H2490C，簡要詞典義 to profane/begin: begin，context gloss「you have begun」），與申2:24-25「起首得那地」同一個 base Strong H2490。BH：「Moses is speaking here, recognizing that God has only just begun to reveal His full might and majesty.」。
- 經文用詞：你已將

字面解析：對上既有「起首得那地（cha.lal）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 起首得那地（cha.lal） | 0.767 | link_folder/原文/起首得那地（cha.lal）.md |
| 2 | 在天上在地下有什麼神能像你 | 0.548 | link_folder/神學/在天上在地下有什麼神能像你.md |
| 3 | 主耶和華（a.do.nai） | 0.516 | link_folder/神學/主耶和華（a.do.nai）.md |
| 4 | 罷了（rav） | 0.475 | link_folder/原文/罷了（rav）.md |
| 5 | 大能的手 | 0.458 | link_folder/神學/大能的手.md |

判定：✅ 建議使用既有條目 [[起首得那地（cha.lal）]]（同名／字面對應）

## 在天上在地下有什麼神能像你（神學）
query:
- 待建立詞：在天上在地下有什麼神能像你
- 出現位置：申命記 第3章
- 候選類型：神學
- 本章上下文：v24「在天上，在地下，有什麼神能像你行事、像你有大能的作為呢？」。CT：「『有什麼神』其實，除祂以外，別無真神」；GT《聖經精讀本》：「在天上、在地下,有什麼神: 摩西的此番話並不是承認其它神存在,乃是為了更加強調神的全能。」；BH：「In the ancient Near Eastern context, many cultures worshiped a pantheon of gods, each with limited power and domain. Moses contrasts these with the one true God, who reigns supreme over all creation.」。
- 經文用詞：有什麼神能像你行事

字面解析：對上既有「在天上在地下有什麼神能像你」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 在天上在地下有什麼神能像你 | 0.869 | link_folder/神學/在天上在地下有什麼神能像你.md |
| 2 | 普天下沒有像我的 | 0.597 | link_folder/神學/普天下沒有像我的.md |
| 3 | 至高的神 | 0.578 | link_folder/神學/至高的神.md |
| 4 | 耶和華 | 0.561 | link_folder/神學/耶和華.md |
| 5 | 除了我以外你不可有別的神 | 0.557 | link_folder/神學/除了我以外你不可有別的神.md |

判定：✅ 建議使用既有條目 [[在天上在地下有什麼神能像你]]（同名／字面對應）

## 過去與發怒同一字根（a.var）（原文）
query:
- 待建立詞：過去與發怒同一字根（a.var）
- 出現位置：申命記 第3章
- 候選類型：原文
- 本章上下文：v25「求你容我過去」；v26「但耶和華因你們的緣故向我發怒」；v27「你必不能過這約但河」；v28「他必在這百姓前面過去」。CT 原文字義：「發怒」離開，消逝。STEP 顯示 v25 'e'.be.rah、v27 ta.'a.Vor、v28 ya.'a.Vor、v18 ta.'av.Ru、v21 'o.Ver 都是 H5674A（a.var，to pass），而 v26「發怒」是 va/i.yit.'a.Ber（H5674B，同一個 base Strong，簡要詞典義 be angry）。
- 經文用詞：向我發怒、容我過去

字面解析：對上既有「過去與發怒同一字根（a.var）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 過去與發怒同一字根（a.var） | 0.792 | link_folder/原文/過去與發怒同一字根（a.var）.md |
| 2 | 氣忿忿 | 0.519 | link_folder/原文/氣忿忿.md |
| 3 | 連合（tsa.mad） | 0.494 | link_folder/原文/連合（tsa.mad）.md |
| 4 | 罷了（rav） | 0.481 | link_folder/原文/罷了（rav）.md |
| 5 | 咒詛（a.rar 與 qa.vav） | 0.477 | link_folder/原文/咒詛（a.rar 與 qa.vav）.md |

判定：✅ 建議使用既有條目 [[過去與發怒同一字根（a.var）]]（同名／字面對應）

## 約但河（地點）
query:
- 待建立詞：約但河
- 出現位置：申命記 第3章
- 候選類型：地點
- 本章上下文：v8「約但河東」；v17「靠近約但河之地」；v20「約但河那邊」；v25「約但河那邊的美地」。BH：「Crossing the Jordan represents a transition from the wilderness wanderings to the inheritance of the Promised Land.」。STEP 顯示 v20、v25「那邊」是 be./'E.ver（H5676H e.ver，簡要詞典義 side: beyond）。

字面解析：對上既有「約但河」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 約但河 | 0.609 | link_folder/地點/約但河.md |
| 2 | 過去與發怒同一字根（a.var） | 0.545 | link_folder/原文/過去與發怒同一字根（a.var）.md |
| 3 | 以色列人經過還是繞過以東境界 | 0.510 | link_folder/解經爭議/以色列人經過還是繞過以東境界.md |
| 4 | 雅博渡口 | 0.496 | link_folder/地點/雅博渡口.md |
| 5 | 應許之地的四至 | 0.495 | link_folder/主題/應許之地的四至.md |

判定：✅ 建議使用既有條目 [[約但河]]（同名／字面對應）

## 美地（主題）
query:
- 待建立詞：美地
- 出現位置：申命記 第3章
- 候選類型：主題
- 本章上下文：v25「求你容我過去，看約但河那邊的美地，就是那佳美的山地和利巴嫩」。CT 原文字義：「美」好的，令人愉悅的；「佳美的」(原文和「美」同字)。STEP 證實兩處都是 H2896A（ha./to.Vah、ha./Tov）。KC：「He spoke with great admiration about the inheritance that the LORD has prepared for His people and called it "the fair land" and "that good hill country".」。
- 經文用詞：美地、佳美的山地

字面解析：對上既有「美地」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 美地 | 0.751 | link_folder/主題/美地.md |
| 2 | 利巴嫩 | 0.608 | link_folder/地點/利巴嫩.md |
| 3 | 流奶與蜜之地 | 0.568 | link_folder/神學/流奶與蜜之地.md |
| 4 | 應許之地的四至 | 0.517 | link_folder/主題/應許之地的四至.md |
| 5 | 迦南地 | 0.469 | link_folder/地點/迦南地.md |

判定：✅ 建議使用既有條目 [[美地]]（同名／字面對應）

## 利巴嫩（地點）
query:
- 待建立詞：利巴嫩
- 出現位置：申命記 第3章
- 候選類型：地點
- 本章上下文：v25「就是那佳美的山地和利巴嫩」。CT 原文字義：「利巴嫩」潔白；GT《啟導本》：「其中黑門山峰高三千公尺，為黎巴嫩境內最壯觀的一座大山」；BH：「Lebanon, known for its majestic cedar trees, was located to the north of Israel. It was renowned for its natural beauty and resources, often symbolizing strength and majesty in biblical literature (Psalm 92:12).」。STEP 顯示是 ve./ha./le.va.Non（H3844G）。

字面解析：對上既有「利巴嫩」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 利巴嫩 | 0.829 | link_folder/地點/利巴嫩.md |
| 2 | 黑門山 | 0.568 | link_folder/地點/黑門山.md |
| 3 | 美地 | 0.482 | link_folder/主題/美地.md |
| 4 | 香柏木（潔淨儀式用） | 0.472 | link_folder/文化/香柏木（潔淨儀式用）.md |
| 5 | 北界的何珥山 | 0.463 | link_folder/地點/北界的何珥山.md |

判定：✅ 建議使用既有條目 [[利巴嫩]]（同名／字面對應）

## 在米利巴未將耶和華尊為聖（神學）
query:
- 待建立詞：在米利巴未將耶和華尊為聖
- 出現位置：申命記 第3章
- 候選類型：神學
- 本章上下文：v26「但耶和華因你們的緣故向我發怒」。CT：「『因你們的緣故』表面是因以色列人爭鬧求水喝，實際是因摩西違背神的命令，用杖擊打磐石兩下(參民二十11~13)」；GT《串珠》：「摩西發怒得罪神，乃由百姓激怒所引起（民20:1-13; 27:12-14）」。
- 經文用詞：因你們的緣故

字面解析：對上既有「在米利巴未將耶和華尊為聖」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 在米利巴未將耶和華尊為聖 | 0.802 | link_folder/神學/在米利巴未將耶和華尊為聖.md |
| 2 | 摩西擊打磐石兩下 | 0.674 | link_folder/事件/摩西擊打磐石兩下.md |
| 3 | 米利巴（Meribah） | 0.639 | link_folder/原文/米利巴（Meribah）.md |
| 4 | 摩西不得進入應許之地 | 0.613 | link_folder/事件/摩西不得進入應許之地.md |
| 5 | 氣忿忿 | 0.611 | link_folder/原文/氣忿忿.md |

判定：✅ 建議使用既有條目 [[在米利巴未將耶和華尊為聖]]（同名／字面對應）

## 罷了（rav）（原文）
query:
- 待建立詞：罷了（rav）
- 出現位置：申命記 第3章
- 候選類型：原文
- 本章上下文：v26「罷了！你不要向我再提這事」。CT 原文字義：「罷了」夠了。GT《聖經精讀本》：「罷了: 令我們聯想到神對保羅三次懇求挪去肉中刺的禱告所作出的回答(林後12:9)」；KC：「He received an answer similar to the one Moses received: "My grace is sufficient for you" (2Cor 12:9).」。STEP 顯示是 rav- La/kh（H7227A rav，簡要詞典義 many）。
- 經文用詞：罷了

字面解析：對上既有「罷了（rav）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 罷了（rav） | 0.816 | link_folder/原文/罷了（rav）.md |
| 2 | 懇求（cha.nan） | 0.481 | link_folder/原文/懇求（cha.nan）.md |
| 3 | 行事與我反對（qe.ri） | 0.473 | link_folder/原文/行事與我反對（qe.ri）.md |
| 4 | 過去與發怒同一字根（a.var） | 0.470 | link_folder/原文/過去與發怒同一字根（a.var）.md |
| 5 | 摩西的靈命低谷與重擔求死 | 0.469 | link_folder/神學/摩西的靈命低谷與重擔求死.md |

判定：✅ 建議使用既有條目 [[罷了（rav）]]（同名／字面對應）

## 摩西不得進入應許之地（事件）
query:
- 待建立詞：摩西不得進入應許之地
- 出現位置：申命記 第3章
- 候選類型：事件
- 本章上下文：v26-27「不應允我⋯因為你必不能過這約但河」。GT《聖經精讀本》：「摩西曾在埃及宮廷居住了40年,在米甸曠野生活了40年,共經過80年的錘煉之後蒙神呼召成為以色列的領袖⋯儘管如此,在本文中神還是不允許他進入迦南」；KC：「God allowed him to stand in a place from where he could see the whole land in its length and breadth」。
- 經文用詞：你必不能過這約但河

字面解析：對上既有「摩西不得進入應許之地」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 摩西不得進入應許之地 | 0.721 | link_folder/事件/摩西不得進入應許之地.md |
| 2 | 摩西 | 0.591 | link_folder/人物/摩西.md |
| 3 | 摩西八十歲 | 0.580 | link_folder/互文/摩西八十歲.md |
| 4 | 罷了（rav） | 0.575 | link_folder/原文/罷了（rav）.md |
| 5 | 加低斯巴尼亞事件 | 0.569 | link_folder/歷史/加低斯巴尼亞事件.md |

判定：✅ 建議使用既有條目 [[摩西不得進入應許之地]]（同名／字面對應）

## 面東定向的左右方位（背景）
query:
- 待建立詞：面東定向的左右方位
- 出現位置：申命記 第3章
- 候選類型：背景
- 本章上下文：v27「向東、西、南、北舉目觀望」。該條目已收創13:14 神叫亞伯蘭「向東西南北觀看」，本節是同一套方位語言的第二次出現。STEP 顯示四個方位詞分別是 Ya.ma/h（H3220H yam，簡要詞典義 sea: west）、tza.Fo.na/h（H6828G north）、tei.Ma.na/h（H8486 te.man，south）、miz.Ra.cha/h（H4217H east）。
- 經文用詞：向東、西、南、北

字面解析：對上既有「面東定向的左右方位」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 面東定向的左右方位 | 0.699 | link_folder/背景/面東定向的左右方位.md |
| 2 | 東方人之地 | 0.494 | link_folder/地點/東方人之地.md |
| 3 | 迦南四境 | 0.471 | link_folder/主題/迦南四境.md |
| 4 | 東風與西風 | 0.461 | link_folder/原文/東風與西風.md |
| 5 | 大東風 | 0.444 | link_folder/原文/大東風.md |

判定：✅ 建議使用既有條目 [[面東定向的左右方位]]（同名／字面對應）

## 擔當（na.sa）（原文）
query:
- 待建立詞：擔當（na.sa）
- 出現位置：申命記 第3章
- 候選類型：原文
- 本章上下文：v27「舉目觀望」。CT 原文字義：「觀望(原文雙字)」覺察，凝視(首字)；眼睛(次字)。STEP 顯示「舉」是 ve./Sa'（H5375M na.sa，簡要詞典義 to lift: look），與申1「擔當」同一個 base Strong H5375。
- 經文用詞：舉目

字面解析：對上既有「擔當（na.sa）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 擔當（na.sa） | 0.620 | link_folder/原文/擔當（na.sa）.md |
| 2 | 眼目明亮（ga.lah） | 0.412 | link_folder/原文/眼目明亮（ga.lah）.md |
| 3 | 使天下萬民驚恐懼怕 | 0.381 | link_folder/原文/使天下萬民驚恐懼怕.md |
| 4 | 眼目閉住還是睜開（sha.tam） | 0.380 | link_folder/原文/眼目閉住還是睜開（sha.tam）.md |
| 5 | 連合（tsa.mad） | 0.375 | link_folder/原文/連合（tsa.mad）.md |

判定：✅ 建議使用既有條目 [[擔當（na.sa）]]（同名／字面對應）

## 勉勵他使他膽壯（cha.zaq、a.mats）（原文）
query:
- 待建立詞：勉勵他使他膽壯（cha.zaq、a.mats）
- 出現位置：申命記 第3章
- 候選類型：原文
- 本章上下文：v28「你卻要囑咐約書亞，勉勵他，使他膽壯」。CT 原文字義：「勉勵」加強，堅定；「膽壯」勇敢，大膽；CT：「神命令摩西作好交棒：(1)『囑咐(charge)』指交代任務；(2)『勉勵(encourage)』指免除畏懼；(3)『膽壯』(strengthen)指加強勇氣」；BH：「The call to strengthen Joshua echoes the biblical theme of God empowering His chosen leaders, as seen with figures like Gideon (Judges 6:14) and David (1 Samuel 30:6).」。STEP 顯示三個動詞是 ve./Tzav（H6680 tsa.vah）、ve./cha.ze.Ke./hu（H2388G cha.zaq）、ve./'a.me.Tze./hu（H553 a.mats），後兩個就是約書亞記反覆出現的「剛強壯膽」組合。
- 經文用詞：勉勵他，使他膽壯

字面解析：對上既有「勉勵他使他膽壯（cha.zaq、a.mats）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 勉勵他使他膽壯（cha.zaq、a.mats） | 0.892 | link_folder/原文/勉勵他使他膽壯（cha.zaq、a.mats）.md |
| 2 | 勇士（cha.yil） | 0.595 | link_folder/原文/勇士（cha.yil）.md |
| 3 | 約書亞承接摩西 | 0.567 | link_folder/事件/約書亞承接摩西.md |
| 4 | 約書亞 | 0.544 | link_folder/人物/約書亞.md |
| 5 | 心消化（ma.sas） | 0.520 | link_folder/原文/心消化（ma.sas）.md |

判定：✅ 建議使用既有條目 [[勉勵他使他膽壯（cha.zaq、a.mats）]]（同名／字面對應）

## 約書亞承接摩西（事件）
query:
- 待建立詞：約書亞承接摩西
- 出現位置：申命記 第3章
- 候選類型：事件
- 本章上下文：v21「那時我吩咐約書亞說」；v28「你卻要囑咐約書亞⋯因為他必在這百姓前面過去」。KC：「This is already the third time that the transfer of the leadership from Moses to Joshua is discussed (Deu 1:38; 3:21-22).」；GT《啟導本》：「神要摩西把領導權交付約書亞。這位年青一代的新領袖要負起兩個責任：1，征服新土（帶領這百姓過河）；2，把土地分配給百姓（“承受你所要觀看之地”）。」。
- 經文用詞：你卻要囑咐約書亞

字面解析：對上既有「約書亞承接摩西」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 約書亞承接摩西 | 0.804 | link_folder/事件/約書亞承接摩西.md |
| 2 | 勉勵他使他膽壯（cha.zaq、a.mats） | 0.664 | link_folder/原文/勉勵他使他膽壯（cha.zaq、a.mats）.md |
| 3 | 摩西與約書亞的權柄差異 | 0.660 | link_folder/主題/摩西與約書亞的權柄差異.md |
| 4 | 約書亞 | 0.633 | link_folder/人物/約書亞.md |
| 5 | 你親眼看見了 | 0.588 | link_folder/主題/你親眼看見了.md |

判定：✅ 建議使用既有條目 [[約書亞承接摩西]]（同名／字面對應）

## 伯毘珥（地點）
query:
- 待建立詞：伯毘珥
- 出現位置：申命記 第3章
- 候選類型：地點
- 本章上下文：v29「於是我們住在伯毘珥對面的谷中」。CT：「『伯毗珥』原為摩押人城鎮，在分配應許之地時，分給了流便支派(參書十三20)」；GT《啟導本》：「“伯毗珥”的意思是“毗珥的居所”，可能就是以色列人曾拜過巴力毗珥的地方（參民二十三28；二十五3）」；GT《串珠》：「「伯毗珥」：即毗珥的殿；以色列民曾在這裡崇拜巴力偶像、行淫亂，陷入極大的罪中（參民25章）」；GT《聖經精讀本》：「伯毗珥對面的谷中: 是摩西作告別佈道的地點,也是死後被葬之地(34:5,6)」。
- 經文用詞：伯毘珥

字面解析：對上既有「伯毘珥」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 伯毘珥 | 0.890 | link_folder/地點/伯毘珥.md |
| 2 | 毘珥山頂 | 0.658 | link_folder/地點/毘珥山頂.md |
| 3 | 巴力毘珥 | 0.624 | link_folder/背景/巴力毘珥.md |
| 4 | 摩押地 | 0.604 | link_folder/地點/摩押地.md |
| 5 | 伯特利 | 0.597 | link_folder/地點/伯特利.md |

判定：✅ 建議使用既有條目 [[伯毘珥]]（同名／字面對應）

## 候選互查（本章內部，⚠＝彼此相似 ≥ 0.8）
（無 ≥ 門檻的配對）
