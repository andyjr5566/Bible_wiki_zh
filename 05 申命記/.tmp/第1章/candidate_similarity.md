<!-- candidate_similarity_meta
schema_version: 1
book: 申命記
chapter: 1
candidate_sha256: f832209d8f6ccf90d7352c9cc5d0e6bd60f1c4434dcfdc4a120ad73fa06b851f
embedding_model: nvidia/nemotron-3-embed-1b
embedding_index_fingerprint: 386bf848ca278714
link_index_sha256: 8546f528f4358d79e2336fb1e1f9ff4ccc2a66fc5982322bc368a72c6a12c0a7
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

# 候選語義近鄰報告：申命記 第1章

- 檢索模型：nvidia/nemotron-3-embed-1b｜重排模型：nvidia/llama-nemotron-rerank-vl-1b-v2:free（未校準/保守模式）｜全庫 2868 條
- 規則說明：字面確切匹配直接通過；其餘候選先檢索 Top 20 名再由 Reranker 重排，取前 5 名顯示。
  治理優先：同名歧義（D類）與分類不相容永遠標 ⚠。
  重排模型未校準時，⚠ 由檢索相似度規則（≥0.50 且 top-1 非同實體）決定，重排名次只當附加證據。
  字面解析：列 resolver 實際比對結果——標「請確認」者務必人工核實。

## 摩西（人物）
query:
- 待建立詞：摩西
- 出現位置：申命記 第1章
- 候選類型：人物
- 本章上下文：v1「以下所記的是摩西⋯向以色列眾人所說的話」；v3「摩西照耶和華藉著他所吩咐以色列人的話都曉諭他們」；v5「摩西在約但河東的摩押地講律法說」。

字面解析：對上既有「摩西」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 摩西 | 0.651 | link_folder/人物/摩西.md |
| 2 | 講律法（ba.ar） | 0.593 | link_folder/原文/講律法（ba.ar）.md |
| 3 | 摩西上山見神 | 0.586 | link_folder/事件/摩西上山見神.md |
| 4 | 摩押平原 | 0.582 | link_folder/地點/摩押平原.md |
| 5 | 摩押地 | 0.566 | link_folder/地點/摩押地.md |

判定：✅ 建議使用既有條目 [[摩西]]（同名／字面對應）

## 約但河（地點）
query:
- 待建立詞：約但河
- 出現位置：申命記 第1章
- 候選類型：地點
- 本章上下文：v1、v5「約但河東」。CT 文意註解：「『約但河東』原文「約但河外」，即今之外約但」。STEP 顯示是 be./'E.ver hai./yar.Den（H5676H＋H3383），簡要詞典義 side: beyond。

字面解析：對上既有「約但河」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 約但河 | 0.556 | link_folder/地點/約但河.md |
| 2 | 往東遷移 | 0.464 | link_folder/主題/往東遷移.md |
| 3 | 東方人之地 | 0.455 | link_folder/地點/東方人之地.md |
| 4 | 河東二支派半最先被擄（代上5：25-26） | 0.449 | link_folder/互文/河東二支派半最先被擄（代上5：25-26）.md |
| 5 | 雅博渡口 | 0.447 | link_folder/地點/雅博渡口.md |

判定：✅ 建議使用既有條目 [[約但河]]（同名／字面對應）

## 亞拉巴（地點）
query:
- 待建立詞：亞拉巴
- 出現位置：申命記 第1章
- 候選類型：地點
- 本章上下文：v1「疏弗對面的亞拉巴」；v7「就是亞拉巴、山地、高原、南地」。CT／GT 同文：「『亞拉巴』指約但河流域從北邊的加利利海到死海南端以迄阿卡巴灣的河谷地帶。今天死海南岸仍叫做亞拉巴（Wady el-Arabah）」。STEP 顯示是 ba./'a.ra.Vah（H6160G），簡要詞典義 Arabah。
- 經文用詞：亞拉巴

字面解析：對上既有「亞拉巴」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 亞拉巴 | 0.796 | link_folder/地點/亞拉巴.md |
| 2 | 應許之地的四至 | 0.600 | link_folder/主題/應許之地的四至.md |
| 3 | 南地 | 0.558 | link_folder/地點/南地.md |
| 4 | 高原（Shephelah） | 0.557 | link_folder/地點/高原（Shephelah）.md |
| 5 | 鹽海 | 0.524 | link_folder/地點/鹽海.md |

判定：✅ 建議使用既有條目 [[亞拉巴]]（同名／字面對應）

## 巴蘭與哈洗錄是否同名不同地（解經爭議）
query:
- 待建立詞：巴蘭與哈洗錄是否同名不同地
- 出現位置：申命記 第1章
- 候選類型：解經爭議
- 本章上下文：v1 列出疏弗、巴蘭、陀弗、拉班、哈洗錄、底撒哈。CT：「這些地方都位於亞拉巴的範圍內，並非南地以南的巴蘭曠野，故巴蘭和哈洗錄同名不同地(參民十二16)」；GT《啟導本》：「疏弗、巴蘭、陀弗、拉班、哈洗錄、底撒哈都是從西奈山北往摩押經過的地方⋯但知巴蘭為介乎加低斯與西奈間的曠野」；BH 亦把 Paran 認作 Numbers 10:12 的曠野、把 Hazeroth 認作 Numbers 11:35 的營地。
- 經文用詞：疏弗、陀弗、底撒哈

字面解析：對上既有「巴蘭與哈洗錄是否同名不同地」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 巴蘭與哈洗錄是否同名不同地 | 0.874 | link_folder/解經爭議/巴蘭與哈洗錄是否同名不同地.md |
| 2 | 巴蘭的曠野 | 0.704 | link_folder/地點/巴蘭的曠野.md |
| 3 | 十二探子自巴蘭或加低斯巴尼亞出發之解經爭議 | 0.679 | link_folder/解經爭議/十二探子自巴蘭或加低斯巴尼亞出發之解經爭議.md |
| 4 | 哈洗錄 | 0.621 | link_folder/地點/哈洗錄.md |
| 5 | 民21 與民33 的站名為何不同 | 0.593 | link_folder/解經爭議/民21 與民33 的站名為何不同.md |

判定：✅ 建議使用既有條目 [[巴蘭與哈洗錄是否同名不同地]]（同名／字面對應）

## 十一天的路程（主題）
query:
- 待建立詞：十一天的路程
- 出現位置：申命記 第1章
- 候選類型：主題
- 本章上下文：v2「（從何烈山經過西珥山到加低斯巴尼亞有十一天的路程。）」CT：「以色列人共花了三十八年的時間」；GT《聖經精讀本》：「這令我們想起以色列竟然為了這麼短的路程而花費了40年」；KC：「The journey could have lasted eleven days⋯Due to unbelief, however, it took them forty years」；BH：「The eleven-day journey serves as a reminder of the consequences of not trusting in God's promises」。
- 經文用詞：十一天的路程

字面解析：對上既有「十一天的路程」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 十一天的路程 | 0.820 | link_folder/主題/十一天的路程.md |
| 2 | 曠野飄流四十年 | 0.573 | link_folder/歷史/曠野飄流四十年.md |
| 3 | 試探神十次 | 0.563 | link_folder/互文/試探神十次.md |
| 4 | 加低斯巴尼亞事件 | 0.559 | link_folder/歷史/加低斯巴尼亞事件.md |
| 5 | 四十的屬靈意義 | 0.538 | link_folder/原文/四十的屬靈意義.md |

判定：✅ 建議使用既有條目 [[十一天的路程]]（同名／字面對應）

## 何烈山（地點）
query:
- 待建立詞：何烈山
- 出現位置：申命記 第1章
- 候選類型：地點
- 本章上下文：v2、v6、v19。CT：「『何烈山』指整條山脈，是磐石出水的地方(參出十七6)，其中一峰稱西乃山，就是神的山」；GT：「何烈山即以色列人領受律法的西奈山（出十九1），一般相信在西乃（今譯西奈）半島南部」。

字面解析：對上既有「何烈山」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 何烈山 | 0.789 | link_folder/地點/何烈山.md |
| 2 | 何烈 | 0.760 | link_folder/地點/何烈.md |
| 3 | 西乃山 | 0.735 | link_folder/地點/西乃山.md |
| 4 | 西乃山的地理 | 0.721 | link_folder/背景/西乃山的地理.md |
| 5 | 神的山 | 0.701 | link_folder/地點/神的山.md |

判定：✅ 建議使用既有條目 [[何烈山]]（同名／字面對應）

## 西珥山（地點）
query:
- 待建立詞：西珥山
- 出現位置：申命記 第1章
- 候選類型：地點
- 本章上下文：v2「經過西珥山」。CT：「『經過西珥山』指繞過以東地的邊緣(參二4)」；GT《串珠》：「「西珥山」：死海以南、亞拉巴東南面的山谷」。

字面解析：對上既有「西珥山」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 西珥山 | 0.648 | link_folder/地點/西珥山.md |
| 2 | 西珥 | 0.565 | link_folder/地點/西珥.md |
| 3 | 北界的何珥山 | 0.527 | link_folder/地點/北界的何珥山.md |
| 4 | 何珥山 | 0.525 | link_folder/地點/何珥山.md |
| 5 | 亞拉巴 | 0.492 | link_folder/地點/亞拉巴.md |

判定：✅ 建議使用既有條目 [[西珥山]]（同名／字面對應）

## 加低斯（地點）
query:
- 待建立詞：加低斯
- 出現位置：申命記 第1章
- 候選類型：地點
- 本章上下文：v2、v19「到了加低斯巴尼亞」；v46「於是你們在加低斯住了許多日子」。GT：「加低斯巴尼亞原名加低斯，又名安密巴（創十四7），位於南地西南，是迦南的南疆入口，距別是巴南約70公里；為曠野中的一個綠洲，水草茂盛。」
- 經文用詞：加低斯巴尼亞、加低斯

字面解析：對上既有「加低斯」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 加低斯 | 0.756 | link_folder/地點/加低斯.md |
| 2 | 安密巴 | 0.661 | link_folder/地點/安密巴.md |
| 3 | 加低斯巴尼亞事件 | 0.647 | link_folder/歷史/加低斯巴尼亞事件.md |
| 4 | 十二探子自巴蘭或加低斯巴尼亞出發之解經爭議 | 0.573 | link_folder/解經爭議/十二探子自巴蘭或加低斯巴尼亞出發之解經爭議.md |
| 5 | 迦南地 | 0.558 | link_folder/地點/迦南地.md |

判定：✅ 建議使用既有條目 [[加低斯]]（同名／字面對應）

## 出埃及第四十年十一月初一日（歷史）
query:
- 待建立詞：出埃及第四十年十一月初一日
- 出現位置：申命記 第1章
- 候選類型：歷史
- 本章上下文：v3。CT：「就是摩西死前大約一個月」；GT《啟導本》：「這是本書唯一記載的日期。兩個月後，百姓進入迦南地（比較書四19）。這期間，他們用了30天來為摩西舉哀（三十四8）」；GT《雷氏研讀本》：「其中兩年停留在西乃山和前往加低斯巴尼亞，其餘三十八年飄流在曠野（二14）」；BH：「The eleventh month, known as Shevat in the Hebrew calendar」。
- 經文用詞：出埃及第四十年十一月初一日

字面解析：對上既有「出埃及第四十年十一月初一日」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 出埃及第四十年十一月初一日 | 0.876 | link_folder/歷史/出埃及第四十年十一月初一日.md |
| 2 | 曠野飄流四十年 | 0.633 | link_folder/歷史/曠野飄流四十年.md |
| 3 | 十一天的路程 | 0.594 | link_folder/主題/十一天的路程.md |
| 4 | 四百三十年 | 0.593 | link_folder/原文/四百三十年.md |
| 5 | 以色列到達西乃山 | 0.585 | link_folder/事件/以色列到達西乃山.md |

判定：✅ 建議使用既有條目 [[出埃及第四十年十一月初一日]]（同名／字面對應）

## 亞摩利人（人物）
query:
- 待建立詞：亞摩利人
- 出現位置：申命記 第1章
- 候選類型：人物
- 本章上下文：v4「亞摩利王西宏」；v7「亞摩利人的山地」；v19、v20、v27、v44。STEP 顯示是 ha./'e.mo.Ri（H567），簡要詞典義 Amorite。CT 原文字義：「亞摩利」山居者。

字面解析：對上既有「亞摩利人」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 亞摩利人 | 0.615 | link_folder/人物/亞摩利人.md |
| 2 | 亞瑪力人 | 0.484 | link_folder/人物/亞瑪力人.md |
| 3 | 亞瑪力 | 0.477 | link_folder/人物/亞瑪力.md |
| 4 | 亞捫人 | 0.458 | link_folder/人物/亞捫人.md |
| 5 | 何利人 | 0.454 | link_folder/人物/何利人.md |

判定：✅ 建議使用既有條目 [[亞摩利人]]（同名／字面對應）

## 希實本（地點）
query:
- 待建立詞：希實本
- 出現位置：申命記 第1章
- 候選類型：地點
- 本章上下文：v4「住希實本的亞摩利王西宏」。CT 原文字義：「希實本」堡壘；GT：「「希實本」為亞摩利人的首邑，距死海北部東岸約20公里」；BH：「Heshbon was the capital city of Sihon⋯Archaeological evidence suggests it was a fortified city」。

字面解析：對上既有「希實本」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 希實本 | 0.743 | link_folder/地點/希實本.md |
| 2 | 亞斯她錄 | 0.499 | link_folder/地點/亞斯她錄.md |
| 3 | 河東城邑的位置考據 | 0.496 | link_folder/背景/河東城邑的位置考據.md |
| 4 | 底本 | 0.481 | link_folder/地點/底本.md |
| 5 | 以色列戰勝亞摩利王西宏互文（申2：24-37；3：1-7；詩135：10-12；136：17-22） | 0.465 | link_folder/互文/以色列戰勝亞摩利王西宏互文（申2：24-37；3：1-7；詩135：10-12；136：17-22）.md |

判定：✅ 建議使用既有條目 [[希實本]]（同名／字面對應）

## 以色列戰勝亞摩利王西宏互文（互文）
query:
- 待建立詞：以色列戰勝亞摩利王西宏互文
- 出現位置：申命記 第1章
- 候選類型：互文
- 本章上下文：v4「他已經擊殺了住希實本的亞摩利王西宏」。CT：「詳情請參閱民數記二十一章21~35節」；KC：「Heshbon is the capital of Moab, but was conquered by Sihon, a king of the Amorites.」
- 經文用詞：西宏

字面解析：對上既有「以色列戰勝亞摩利王西宏互文（申2：24-37；3：1-7；詩135：10-12；136：17-22）」（alias，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 以色列戰勝亞摩利王西宏互文（申2：24-37；3：1-7；詩135：10-12；136：17-22） | 0.762 | link_folder/互文/以色列戰勝亞摩利王西宏互文（申2：24-37；3：1-7；詩135：10-12；136：17-22）.md |
| 2 | 以色列戰勝巴珊王噩互文（申3：1-11；詩135：10-12；136：17-22） | 0.625 | link_folder/互文/以色列戰勝巴珊王噩互文（申3：1-11；詩135：10-12；136：17-22）.md |
| 3 | 希實本 | 0.616 | link_folder/地點/希實本.md |
| 4 | 亞摩利人 | 0.578 | link_folder/人物/亞摩利人.md |
| 5 | 亞捫人 | 0.526 | link_folder/人物/亞捫人.md |

判定：✅ 建議使用既有條目 [[以色列戰勝亞摩利王西宏互文（申2：24-37；3：1-7；詩135：10-12；136：17-22）]]（同名／字面對應）

## 巴珊（地點）
query:
- 待建立詞：巴珊
- 出現位置：申命記 第1章
- 候選類型：地點
- 本章上下文：v4「住以得來、亞斯她錄的巴珊王噩」。CT 原文字義：「巴珊」多結果實的；BH：「Bashan was a fertile and prosperous region」。

字面解析：對上既有「巴珊」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 巴珊 | 0.641 | link_folder/地點/巴珊.md |
| 2 | 以得來 | 0.606 | link_folder/地點/以得來.md |
| 3 | 亞斯她錄 | 0.518 | link_folder/地點/亞斯她錄.md |
| 4 | 以色列戰勝巴珊王噩互文（申3：1-11；詩135：10-12；136：17-22） | 0.441 | link_folder/互文/以色列戰勝巴珊王噩互文（申3：1-11；詩135：10-12；136：17-22）.md |
| 5 | 示拿地 | 0.436 | link_folder/地點/示拿地.md |

判定：✅ 建議使用既有條目 [[巴珊]]（同名／字面對應）

## 以色列戰勝巴珊王噩互文（互文）
query:
- 待建立詞：以色列戰勝巴珊王噩互文
- 出現位置：申命記 第1章
- 候選類型：互文
- 本章上下文：v4「巴珊王噩」。CT 原文字義：「噩」長頸的；BH：「Og, king of Bashan, was another formidable opponent, known for his giant stature (Deuteronomy 3:11)」。
- 經文用詞：噩

字面解析：對上既有「以色列戰勝巴珊王噩互文（申3：1-11；詩135：10-12；136：17-22）」（alias，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 以色列戰勝巴珊王噩互文（申3：1-11；詩135：10-12；136：17-22） | 0.734 | link_folder/互文/以色列戰勝巴珊王噩互文（申3：1-11；詩135：10-12；136：17-22）.md |
| 2 | 巴珊 | 0.594 | link_folder/地點/巴珊.md |
| 3 | 利乏音人 | 0.546 | link_folder/人物/利乏音人.md |
| 4 | 以得來 | 0.542 | link_folder/地點/以得來.md |
| 5 | 以色列戰勝亞摩利王西宏互文（申2：24-37；3：1-7；詩135：10-12；136：17-22） | 0.523 | link_folder/互文/以色列戰勝亞摩利王西宏互文（申2：24-37；3：1-7；詩135：10-12；136：17-22）.md |

判定：✅ 建議使用既有條目 [[以色列戰勝巴珊王噩互文（申3：1-11；詩135：10-12；136：17-22）]]（同名／字面對應）

## 以得來（地點）
query:
- 待建立詞：以得來
- 出現位置：申命記 第1章
- 候選類型：地點
- 本章上下文：v4「住以得來、亞斯她錄的巴珊王噩」。CT 原文字義：「以得來」好的牧草地；GT《啟導本》：「三1說噩住在亞斯他錄；以得來或為離宮所在，位於加利利海東岸45公里處」；BH：「The battle at Edrei was crucial as Bashan was a fertile and prosperous region」。
- 經文用詞：以得來

字面解析：對上既有「以得來」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 以得來 | 0.839 | link_folder/地點/以得來.md |
| 2 | 巴珊 | 0.662 | link_folder/地點/巴珊.md |
| 3 | 亞斯她錄 | 0.590 | link_folder/地點/亞斯她錄.md |
| 4 | 以得臺 | 0.526 | link_folder/地點/以得臺.md |
| 5 | 以倘 | 0.525 | link_folder/地點/以倘.md |

判定：✅ 建議使用既有條目 [[以得來]]（同名／字面對應）

## 亞斯她錄（地點）
query:
- 待建立詞：亞斯她錄
- 出現位置：申命記 第1章
- 候選類型：地點
- 本章上下文：v4。CT 原文字義：「亞斯他錄」星辰；GT《華爾頓申命記背景注釋》：「本節稱亞斯他錄為巴珊的首都。埃及、亞述文獻，和亞馬拿書函，都提到過這個城市⋯它今日稱為亞斯他拉遺址（Tell 'Ashtarah），位於雅穆克河畔，加利利海東面二十五哩左右之處」；BH：「Ashtaroth was one of the principal cities of Og's kingdom and a center of worship for the Canaanite goddess Astarte」。
- 經文用詞：亞斯她錄

字面解析：對上既有「亞斯她錄」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 亞斯她錄 | 0.876 | link_folder/地點/亞斯她錄.md |
| 2 | 亞述 | 0.583 | link_folder/地點/亞述.md |
| 3 | 以得來 | 0.565 | link_folder/地點/以得來.md |
| 4 | 巴珊 | 0.541 | link_folder/地點/巴珊.md |
| 5 | 河東城邑的位置考據 | 0.540 | link_folder/背景/河東城邑的位置考據.md |

判定：✅ 建議使用既有條目 [[亞斯她錄]]（同名／字面對應）

## 摩押地（地點）
query:
- 待建立詞：摩押地
- 出現位置：申命記 第1章
- 候選類型：地點
- 本章上下文：v5「摩西在約但河東的摩押地講律法說」。CT：「『摩押地』即指亞拉巴(參1節)的中南部」；BH：「Moab is a region east of the Dead Sea, named after the descendants of Moab, the son of Lot (Genesis 19:37)」。

字面解析：對上既有「摩押地」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 摩押地 | 0.720 | link_folder/地點/摩押地.md |
| 2 | 摩押 | 0.670 | link_folder/人物/摩押.md |
| 3 | 亞拉巴 | 0.645 | link_folder/地點/亞拉巴.md |
| 4 | 摩押平原 | 0.639 | link_folder/地點/摩押平原.md |
| 5 | 摩押人 | 0.637 | link_folder/人物/摩押人.md |

判定：✅ 建議使用既有條目 [[摩押地]]（同名／字面對應）

## 講律法（ba.ar）（原文）
query:
- 待建立詞：講律法（ba.ar）
- 出現位置：申命記 第1章
- 候選類型：原文
- 本章上下文：v5「摩西在約但河東的摩押地講律法說」。CT 原文字義：「講」解釋，使明白；「律法」指引，教誨。GT《雷氏研讀本》：「「講」。直譯作：解釋」；GT《聖經精讀本》：「講律法說: “講”的希伯來語“baar ”意指“明確地闡明或講解”」；BH：「The Hebrew word for "explain" can also mean "to make clear" or "to expound"」。STEP 顯示是 ho.'Il be.'Er（H2974＋H874），context gloss「he undertook」「he made clear」，簡要詞典義 ba.ar to make plain；「律法」是 ha./to.Rah（H8451），簡要詞典義 instruction。
- 經文用詞：講律法

字面解析：對上既有「講律法（ba.ar）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 講律法（ba.ar） | 0.850 | link_folder/原文/講律法（ba.ar）.md |
| 2 | 亞拉巴 | 0.541 | link_folder/地點/亞拉巴.md |
| 3 | 摩押平原 | 0.526 | link_folder/地點/摩押平原.md |
| 4 | 摩西審判百姓 | 0.522 | link_folder/事件/摩西審判百姓.md |
| 5 | 摩押地 | 0.521 | link_folder/地點/摩押地.md |

判定：✅ 建議使用既有條目 [[講律法（ba.ar）]]（同名／字面對應）

## 應許之地的四至（主題）
query:
- 待建立詞：應許之地的四至
- 出現位置：申命記 第1章
- 候選類型：主題
- 本章上下文：v7「就是亞拉巴、山地、高原、南地，沿海一帶迦南人的地，並利巴嫩山又到伯拉大河」。CT：「『伯拉大河』即今幼發拉底河，是神所應許之地的北方界線」；GT《啟導本》：「本節所描寫的迦南應許地範圍與神當年應許亞伯拉罕、以撒和雅各的符合（創十五18；二十六2～4；三十五11～12）。大衛和所羅門王時代，已見到這塊擴展的版圖」；BH：「The Euphrates River⋯marks the northeastern boundary of the promised land」。
- 經文用詞：利巴嫩山、沿海一帶

字面解析：對上既有「應許之地的四至」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 應許之地的四至 | 0.822 | link_folder/主題/應許之地的四至.md |
| 2 | 伯拉大河 | 0.704 | link_folder/地點/伯拉大河.md |
| 3 | 迦南地 | 0.649 | link_folder/地點/迦南地.md |
| 4 | 「伯拉大河」名稱 | 0.648 | link_folder/原文/「伯拉大河」名稱.md |
| 5 | 四界與亞伯拉罕之約的落差 | 0.624 | link_folder/解經爭議/四界與亞伯拉罕之約的落差.md |

判定：✅ 建議使用既有條目 [[應許之地的四至]]（同名／字面對應）

## 高原（Shephelah）（地點）
query:
- 待建立詞：高原（Shephelah）
- 出現位置：申命記 第1章
- 候選類型：地點
- 本章上下文：v7「亞拉巴、山地、高原、南地」。CT：「『高原』或翻作「低原」、「丘陵」，指迦南地中部「山地」以南，西面與非利士地鄰接，南面與「南地」相接的丘陵地帶」；GT《雷氏研讀本》：「「高原」。位於沿海平原與中央高地之間的低地。此地被稱為Shephelah」；BH：「The foothills, or Shephelah, are the lowlands between the coastal plain and the hill country」。STEP 顯示是 u./va./she.fe.Lah（H8219）。
- 經文用詞：高原

字面解析：對上既有「高原（Shephelah）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 高原（Shephelah） | 0.892 | link_folder/地點/高原（Shephelah）.md |
| 2 | 應許之地的四至 | 0.641 | link_folder/主題/應許之地的四至.md |
| 3 | 南地 | 0.561 | link_folder/地點/南地.md |
| 4 | 亞拉巴 | 0.536 | link_folder/地點/亞拉巴.md |
| 5 | 淨光的高處（she.phi） | 0.532 | link_folder/原文/淨光的高處（she.phi）.md |

判定：✅ 建議使用既有條目 [[高原（Shephelah）]]（同名／字面對應）

## 南地（地點）
query:
- 待建立詞：南地
- 出現位置：申命記 第1章
- 候選類型：地點
- 本章上下文：v7「亞拉巴、山地、高原、南地」。CT：「『南地』指迦南地境內的南部地區，別是巴以南一片貧瘠乾地」；GT《雷氏研讀本》：「「南地」（N e g e v）。位於迦南地南部的曠野地，約有四千五百平方英里（11,650平方公里）」。STEP 顯示是 u./va./Ne.gev（H5045G）。

字面解析：對上既有「南地」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 南地 | 0.792 | link_folder/地點/南地.md |
| 2 | 應許之地的四至 | 0.593 | link_folder/主題/應許之地的四至.md |
| 3 | 南地與希伯崙 | 0.588 | link_folder/地點/南地與希伯崙.md |
| 4 | 高原（Shephelah） | 0.552 | link_folder/地點/高原（Shephelah）.md |
| 5 | 亞拉巴 | 0.549 | link_folder/地點/亞拉巴.md |

判定：✅ 建議使用既有條目 [[南地]]（同名／字面對應）

## 迦南人（人物）
query:
- 待建立詞：迦南人
- 出現位置：申命記 第1章
- 候選類型：人物
- 本章上下文：v7「沿海一帶迦南人的地」。CT 原文字義：「迦南人」熱心的，生意人，商人；BH：「The Canaanites were the primary inhabitants of the land promised to Israel」。

字面解析：對上既有「迦南人」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 迦南人 | 0.697 | link_folder/人物/迦南人.md |
| 2 | 迦南人與比利洗人 | 0.608 | link_folder/歷史/迦南人與比利洗人.md |
| 3 | 迦南地 | 0.589 | link_folder/地點/迦南地.md |
| 4 | 迦南七族（迦南地原住民） | 0.586 | link_folder/背景/迦南七族（迦南地原住民）.md |
| 5 | 比利洗人 | 0.556 | link_folder/人物/比利洗人.md |

判定：✅ 建議使用既有條目 [[迦南人]]（同名／字面對應）

## 亞伯拉罕（人物）
query:
- 待建立詞：亞伯拉罕
- 出現位置：申命記 第1章
- 候選類型：人物
- 本章上下文：v8「耶和華向你們列祖亞伯拉罕、以撒、雅各起誓應許賜給他們和他們後裔為業之地」。

字面解析：對上既有「亞伯拉罕」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 亞伯拉罕 | 0.663 | link_folder/人物/亞伯拉罕.md |
| 2 | 亞伯蘭 | 0.654 | link_folder/人物/亞伯蘭.md |
| 3 | 亞伯拉罕之約 | 0.644 | link_folder/神學/亞伯拉罕之約.md |
| 4 | 亞伯拉罕之約的應驗 | 0.622 | link_folder/神學/亞伯拉罕之約的應驗.md |
| 5 | 神的信實 | 0.549 | link_folder/神學/神的信實.md |

判定：✅ 建議使用既有條目 [[亞伯拉罕]]（同名／字面對應）

## 以撒（人物）
query:
- 待建立詞：以撒
- 出現位置：申命記 第1章
- 候選類型：人物
- 本章上下文：v8「亞伯拉罕、以撒、雅各」。CT 原文字義：「以撒」他笑。

字面解析：對上既有「以撒」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 「以撒」名字含義 | 0.632 | link_folder/原文/「以撒」名字含義.md |
| 2 | 以撒 | 0.610 | link_folder/人物/以撒.md |
| 3 | 戲笑 | 0.568 | link_folder/原文/戲笑.md |
| 4 | 以撒的豫表 | 0.568 | link_folder/神學/以撒的豫表.md |
| 5 | 亞設（有福） | 0.491 | link_folder/人物/亞設（有福）.md |

判定：✅ 建議使用既有條目 [[以撒]]（同名／字面對應）

## 雅各（人物）
query:
- 待建立詞：雅各
- 出現位置：申命記 第1章
- 候選類型：人物
- 本章上下文：v8「亞伯拉罕、以撒、雅各」。CT 原文字義：「雅各」抓住腳後跟的人，取代者。

字面解析：對上既有「雅各」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 雅各 | 0.602 | link_folder/人物/雅各.md |
| 2 | 雅八 | 0.544 | link_folder/人物/雅八.md |
| 3 | 以色列 | 0.509 | link_folder/原文/以色列.md |
| 4 | 摔跤 | 0.503 | link_folder/原文/摔跤.md |
| 5 | 雅各改名以色列 | 0.501 | link_folder/歷史/雅各改名以色列.md |

判定：✅ 建議使用既有條目 [[雅各]]（同名／字面對應）

## 擔當（na.sa）（原文）
query:
- 待建立詞：擔當（na.sa）
- 出現位置：申命記 第1章
- 候選類型：原文
- 本章上下文：v9「管理你們的重任，我獨自擔當不起」；v12「我獨自一人怎能擔當得起呢」；v31「耶和華─你們的神撫養你們，如同人撫養兒子一般」。CT 原文字義兩處同給「舉起，承擔」（v9「擔當」、v31「撫養」）。STEP 顯示三處同為 H5375H：v9 se.'Et（to bear）、v12 'e.Sa'（will I bear）、v31 ne.sa.'a./Kha（he carried you）與 yi.sa'-（he carries），簡要詞典義 na.sa to lift: bear。KC：「What Moses was not able to do (Num 11:14), God did: He carried them like a man carries his child.」
- 經文用詞：擔當、撫養

字面解析：對上既有「擔當（na.sa）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 擔當（na.sa） | 0.896 | link_folder/原文/擔當（na.sa）.md |
| 2 | 摩西的靈命低谷與重擔求死 | 0.585 | link_folder/神學/摩西的靈命低谷與重擔求死.md |
| 3 | 肩頭抬聖物（哥轄子孫） | 0.523 | link_folder/主題/肩頭抬聖物（哥轄子孫）.md |
| 4 | 擔子 | 0.523 | link_folder/神學/擔子.md |
| 5 | 摩西舉手得勝 | 0.503 | link_folder/事件/摩西舉手得勝.md |

判定：✅ 建議使用既有條目 [[擔當（na.sa）]]（同名／字面對應）

## 敬畏神、誠實、恨不義之財（神學）
query:
- 待建立詞：敬畏神、誠實、恨不義之財
- 出現位置：申命記 第1章
- 候選類型：神學
- 本章上下文：v13「你們要按著各支派選舉有智慧、有見識、為眾人所認識的」。CT：「本節說出領袖三條件：(1)有智慧，較偏重於治事的才幹；(2)有見識，較偏重於分辨的能力；(3)為眾人所認識的，較偏重於經驗和信譽」；GT《啟導本》列出六項並對照出十八21；BH：「Wisdom in the biblical sense often refers to the fear of the Lord⋯These qualities are echoed in the New Testament qualifications for church leaders (1 Timothy 3:1-7)」。STEP 顯示是 cha.kha.Mim（H2450 wise）、u./ne.vo.Nim（H995 bin，Niphal 分詞 understanding）、vi./du.'Im（H3045 yada，Qal 被動分詞 known）。
- 經文用詞：有智慧、有見識、為眾人所認識的

字面解析：對上既有「敬畏神、誠實、恨不義之財」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 敬畏神、誠實、恨不義之財 | 0.799 | link_folder/神學/敬畏神、誠實、恨不義之財.md |
| 2 | 提前3：1-7 監督資格 | 0.638 | link_folder/互文/提前3：1-7 監督資格.md |
| 3 | 徒6：1-7 選立執事 | 0.574 | link_folder/互文/徒6：1-7 選立執事.md |
| 4 | 心裡有智慧 | 0.527 | link_folder/原文/心裡有智慧.md |
| 5 | 彼前5：1-4 牧養群羊 | 0.514 | link_folder/互文/彼前5：1-4 牧養群羊.md |

判定：✅ 建議使用既有條目 [[敬畏神、誠實、恨不義之財]]（同名／字面對應）

## 葉忒羅建議分層治理（事件）
query:
- 待建立詞：葉忒羅建議分層治理
- 出現位置：申命記 第1章
- 候選類型：事件
- 本章上下文：v9-18 回顧何烈山下設立官長。GT《啟導本》：「本節至18節所記的事可參《出埃及記》十八13～26」；GT《聖經精讀本》：「本文講述了摩西在實行岳父葉忒羅之忠告(出18:17-23)的過程中,首先向百姓講明其理由,再得到他們同意的場面」。

字面解析：對上既有「葉忒羅建議分層治理」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 葉忒羅建議分層治理 | 0.772 | link_folder/事件/葉忒羅建議分層治理.md |
| 2 | 摩西立首領 | 0.669 | link_folder/事件/摩西立首領.md |
| 3 | 葉忒羅的建議是不是出於神 | 0.630 | link_folder/解經爭議/葉忒羅的建議是不是出於神.md |
| 4 | 葉忒羅 | 0.627 | link_folder/人物/葉忒羅.md |
| 5 | 葉忒羅來訪 | 0.557 | link_folder/事件/葉忒羅來訪.md |

判定：✅ 建議使用既有條目 [[葉忒羅建議分層治理]]（同名／字面對應）

## 曠野審判制度（背景）
query:
- 待建立詞：曠野審判制度
- 出現位置：申命記 第1章
- 候選類型：背景
- 本章上下文：v15「立他們為官長、千夫長、百夫長、五十夫長、十夫長」。CT：「按所管理的人數，分別設立各級官長(參出十八25)」；GT《聖經精讀本》：「十夫長: 與其它夫長有所不同,他們所擔任的並不是軍事上的統率或司法上的責任,而是負責事務記錄,戶籍管理等行政瑣事」；BH：「This hierarchical structure reflects a military organization」。
- 經文用詞：千夫長、百夫長、五十夫長

字面解析：對上既有「曠野審判制度」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 曠野審判制度 | 0.818 | link_folder/背景/曠野審判制度.md |
| 2 | 摩西立首領 | 0.641 | link_folder/事件/摩西立首領.md |
| 3 | 以色列人的官長 | 0.553 | link_folder/人物/以色列人的官長.md |
| 4 | 葉忒羅建議分層治理 | 0.550 | link_folder/事件/葉忒羅建議分層治理.md |
| 5 | 古代近東司法制度 | 0.537 | link_folder/背景/古代近東司法制度.md |

判定：✅ 建議使用既有條目 [[曠野審判制度]]（同名／字面對應）

## 審判官（原文）
query:
- 待建立詞：審判官
- 出現位置：申命記 第1章
- 候選類型：原文
- 本章上下文：v16「當時，我囑咐你們的審判官說」。CT 原文字義：「審判官」判斷，治理。STEP 顯示是 sho.fe.tei./Khem（H8199 shaphat），同節「按公義判斷」的動詞 u./she.fa.Tem 同為 H8199，「公義」是 Tze.dek（H6664G）。

字面解析：對上既有「審判官」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 審判官 | 0.677 | link_folder/原文/審判官.md |
| 2 | 申16：18-20 | 0.593 | link_folder/互文/申16：18-20.md |
| 3 | 審判不可行不義按公義審判 | 0.580 | link_folder/主題/審判不可行不義按公義審判.md |
| 4 | 申1：17 | 0.573 | link_folder/互文/申1：17.md |
| 5 | 司法公義 | 0.538 | link_folder/神學/司法公義.md |

判定：✅ 建議使用既有條目 [[審判官]]（同名／字面對應）

## 寄居的（原文）
query:
- 待建立詞：寄居的
- 出現位置：申命記 第1章
- 候選類型：原文
- 本章上下文：v16「是與同居的外人爭訟，都要按公義判斷」。CT：「『外人』指皈依猶太教的非希伯來人」；BH：「Including "a foreign resident" highlights the inclusivity of God's justice system」。STEP 顯示是 ge.R/o（H1616），簡要詞典義 ger sojourner。
- 經文用詞：同居的外人

字面解析：對上既有「寄居的」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 寄居的 | 0.669 | link_folder/原文/寄居的.md |
| 2 | 寄居的與本地人同歸一例 | 0.631 | link_folder/主題/寄居的與本地人同歸一例.md |
| 3 | 善待寄居的外人愛他如己 | 0.602 | link_folder/主題/善待寄居的外人愛他如己.md |
| 4 | 本地人與寄居者同歸一例的律法精神 | 0.593 | link_folder/神學/本地人與寄居者同歸一例的律法精神.md |
| 5 | 寄居身分 | 0.561 | link_folder/神學/寄居身分.md |

判定：✅ 建議使用既有條目 [[寄居的]]（同名／字面對應）

## 不可看人的外貌（na.khar）（原文）
query:
- 待建立詞：不可看人的外貌（na.khar）
- 出現位置：申命記 第1章
- 候選類型：原文
- 本章上下文：v17「審判的時候，不可看人的外貌；聽訟不可分貴賤，不可懼怕人」。CT 原文字義：「外貌」面，臉；「貴」巨大的；「賤」小的，低微的。STEP 顯示是 lo'- ta.Ki.ru fa.Nim（H5234A na.khar「to recognize」＋H6440N pa.neh「faces」），字面是「不可認臉」；同節「不可懼怕人」是 lo' ta.Gu.ru mi./pe.nei- 'Ish（H1481C gur「to dread」），再次用 pa.neh。BH：「Partiality, or favoritism, is condemned throughout Scripture (e.g., Leviticus 19:15, James 2:1-9)」。
- 經文用詞：不可看人的外貌

字面解析：對上既有「不可看人的外貌（na.khar）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 不可看人的外貌（na.khar） | 0.825 | link_folder/原文/不可看人的外貌（na.khar）.md |
| 2 | 申1：17 | 0.617 | link_folder/互文/申1：17.md |
| 3 | 審判不可行不義按公義審判 | 0.595 | link_folder/主題/審判不可行不義按公義審判.md |
| 4 | 不可咒罵聾子絆倒瞎子 | 0.487 | link_folder/主題/不可咒罵聾子絆倒瞎子.md |
| 5 | 司法公義 | 0.478 | link_folder/神學/司法公義.md |

判定：✅ 建議使用既有條目 [[不可看人的外貌（na.khar）]]（同名／字面對應）

## 申1：17（互文）
query:
- 待建立詞：申1：17
- 出現位置：申命記 第1章
- 候選類型：互文
- 本章上下文：v17「因為審判是屬乎神的。若有難斷的案件，可以呈到我這裡，我就判斷」。CT：「『審判是屬乎神的』指審判是經過神的授權，代表神而為，故毋須顧慮「人」的因素」；GT《聖經精讀本》：「掌管神之律法的審判官作為神的代言人,也當持有以神的權威與名義審判的意識」；KC 列為審判官四條件之三；BH：「Judges serve as God's representatives, administering His justice on earth (Psalm 82:1-4)」。STEP 顯示「審判」是 ha./mish.Pat（H4941G）、「難斷的案件」是 ha./da.Var 'a.Sher yik.Sheh（H1697L davar「word: case」＋H7185 qashah「to harden」）。
- 經文用詞：審判是屬乎神的

字面解析：對上既有「申1：17」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 申1：17 | 0.771 | link_folder/互文/申1：17.md |
| 2 | 審判官 | 0.655 | link_folder/原文/審判官.md |
| 3 | 不可看人的外貌（na.khar） | 0.624 | link_folder/原文/不可看人的外貌（na.khar）.md |
| 4 | 審判不可行不義按公義審判 | 0.566 | link_folder/主題/審判不可行不義按公義審判.md |
| 5 | 申16：18-20 | 0.555 | link_folder/互文/申16：18-20.md |

判定：✅ 建議使用既有條目 [[申1：17]]（同名／字面對應）

## 古代近東司法制度（背景）
query:
- 待建立詞：古代近東司法制度
- 出現位置：申命記 第1章
- 候選類型：背景
- 本章上下文：v16-17。GT《華爾頓申命記背景注釋》：「接近這個時代的埃及和赫人記錄，亦同樣顯示司法系統是等級性的。赫人的《軍官及司令指南》（Instructions to Officers and Commanders）甚至與第13節相同，讓軍官擔任法官⋯陪審團並不存在，但長老有時也會集體判案⋯律師也不存在，大部分人在法庭上都是充任自己的律師」。

字面解析：對上既有「古代近東司法制度」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 古代近東司法制度 | 0.764 | link_folder/背景/古代近東司法制度.md |
| 2 | 曠野審判制度 | 0.567 | link_folder/背景/曠野審判制度.md |
| 3 | 古代近東法典 | 0.520 | link_folder/背景/古代近東法典.md |
| 4 | 古代近東的祭司 | 0.476 | link_folder/背景/古代近東的祭司.md |
| 5 | 申16：18-20 | 0.473 | link_folder/互文/申16：18-20.md |

判定：✅ 建議使用既有條目 [[古代近東司法制度]]（同名／字面對應）

## 曠野飄流四十年（歷史）
query:
- 待建立詞：曠野飄流四十年
- 出現位置：申命記 第1章
- 候選類型：歷史
- 本章上下文：v19「經過你們所看見那大而可怕的曠野」；v46「於是你們在加低斯住了許多日子」。GT《聖經精讀本》：「大而可怕的曠野: 指阿拉伯曠野的西部,即形成北部西奈半島的荒涼沙漠地帶⋯山脈如同被火燒,只有尖岩陡石和荒沙遍滿全地」；KC：「The great and terrible wilderness served to create a longing for the land.」

字面解析：對上既有「曠野飄流四十年」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 曠野飄流四十年 | 0.672 | link_folder/歷史/曠野飄流四十年.md |
| 2 | 西乃的曠野 | 0.619 | link_folder/地點/西乃的曠野.md |
| 3 | 汛的曠野 | 0.603 | link_folder/地點/汛的曠野.md |
| 4 | 曠野 | 0.602 | link_folder/地點/曠野.md |
| 5 | 以色列到達西乃山 | 0.595 | link_folder/事件/以色列到達西乃山.md |

判定：✅ 建議使用既有條目 [[曠野飄流四十年]]（同名／字面對應）

## 你與你們的單複數交替（原文）
query:
- 待建立詞：你與你們的單複數交替
- 出現位置：申命記 第1章
- 候選類型：原文
- 本章上下文：v21、v31 在原文是第二人稱單數，與全章通用的複數不同。GT《啟導本》：「本節的“你”為第二人稱單數，與全章通用的多數“你們”不同。有人因此指出本節為後加的。31節經文中的“你們”原文也是單數，《和合本》為求統一，改譯為“你們”」。STEP morphology 逐字證實：v21 Re.'eh（Vqv2ms）、'e.lo.Hei./kha（Sp2ms）、'a.Leh（Vqv2ms）、Resh（Vqv2ms）、ti.Ra'（Vqj2ms）、te.Chat（VNj2ms）全為單數；v31 ra.'I.ta（Vqp2ms）、ne.sa.'a./Kha（Sp2ms）亦為單數。

字面解析：對上既有「你與你們的單複數交替」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 你與你們的單複數交替 | 0.831 | link_folder/原文/你與你們的單複數交替.md |
| 2 | 出35-40 逐字複述出25-31 | 0.421 | link_folder/主題/出35-40 逐字複述出25-31.md |
| 3 | 報仇（na.qam 與 nik.mah） | 0.419 | link_folder/原文/報仇（na.qam 與 nik.mah）.md |
| 4 | 行事與我反對（qe.ri） | 0.419 | link_folder/原文/行事與我反對（qe.ri）.md |
| 5 | 三位一體在創造中的隱現 | 0.419 | link_folder/神學/三位一體在創造中的隱現.md |

判定：✅ 建議使用既有條目 [[你與你們的單複數交替]]（同名／字面對應）

## 十二探子窺探迦南地（事件）
query:
- 待建立詞：十二探子窺探迦南地
- 出現位置：申命記 第1章
- 候選類型：事件
- 本章上下文：v22-25「我們要先打發人去，為我們窺探那地」；v23「就從你們中間選了十二個人，每支派一人」。KC：「In Numbers it says that God commands spies to be sent out (Num 13:1-2), while here we learn that the people wanted it.」

字面解析：對上既有「十二探子窺探迦南地」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 十二探子窺探迦南地 | 0.754 | link_folder/事件/十二探子窺探迦南地.md |
| 2 | 窺探迦南起因為神命或民意的解經爭議 | 0.669 | link_folder/解經爭議/窺探迦南起因為神命或民意的解經爭議.md |
| 3 | 加低斯巴尼亞事件 | 0.548 | link_folder/歷史/加低斯巴尼亞事件.md |
| 4 | 迦南地 | 0.523 | link_folder/地點/迦南地.md |
| 5 | 兩支派半求河東之地為業 | 0.511 | link_folder/事件/兩支派半求河東之地為業.md |

判定：✅ 建議使用既有條目 [[十二探子窺探迦南地]]（同名／字面對應）

## 以實各谷的一掛葡萄（主題）
query:
- 待建立詞：以實各谷的一掛葡萄
- 出現位置：申命記 第1章
- 候選類型：主題
- 本章上下文：v24「到以實各谷，窺探那地」；v25「他們手裡拿著那地的果子下來」。CT 原文字義：「以實各」串束；GT《啟導本》：「“以實各”有果實累累之意，表示其地異常肥沃。此谷近希伯侖（參民十三22）」。

字面解析：對上既有「以實各谷的一掛葡萄」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 以實各谷的一掛葡萄 | 0.786 | link_folder/主題/以實各谷的一掛葡萄.md |
| 2 | 流奶與蜜之地 | 0.558 | link_folder/神學/流奶與蜜之地.md |
| 3 | 以實各 | 0.530 | link_folder/人物/以實各.md |
| 4 | 葡萄樹與真葡萄樹_約15_1 | 0.524 | link_folder/互文/葡萄樹與真葡萄樹_約15_1.md |
| 5 | 接連的山谷（na.chal） | 0.522 | link_folder/原文/接連的山谷（na.chal）.md |

判定：✅ 建議使用既有條目 [[以實各谷的一掛葡萄]]（同名／字面對應）

## 美地（主題）
query:
- 待建立詞：美地
- 出現位置：申命記 第1章
- 候選類型：主題
- 本章上下文：v25「耶和華─我們的神所賜給我們的是美地」；v35「連一個也不得見我起誓應許賜給你們列祖的美地」。CT：「『美地』又稱流奶與蜜之地(參民十三27)，乃形容物產豐富，適宜居住生活」；KC：「They have also recognized that the land God gives is "a good (or: fair) land", an expression that appears ten times in this book (Deu 1:25,35; 3:25; 4:21,22; 6:18; 8:7,10; 9:6; 11:17).」STEP 顯示是 to.Vah ha./'A.retz（H2896A tov「pleasant」）。
- 經文用詞：美地

字面解析：對上既有「美地」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 美地 | 0.843 | link_folder/主題/美地.md |
| 2 | 流奶與蜜之地 | 0.701 | link_folder/神學/流奶與蜜之地.md |
| 3 | 迦南地 | 0.529 | link_folder/地點/迦南地.md |
| 4 | 應許之地的四至 | 0.517 | link_folder/主題/應許之地的四至.md |
| 5 | 業地（a.chuz.zah） | 0.509 | link_folder/原文/業地（a.chuz.zah）.md |

判定：✅ 建議使用既有條目 [[美地]]（同名／字面對應）

## 流奶與蜜之地（神學）
query:
- 待建立詞：流奶與蜜之地
- 出現位置：申命記 第1章
- 候選類型：神學
- 本章上下文：v25「所賜給我們的是美地」。CT：「『美地』又稱流奶與蜜之地(參民十三27)」；GT《聖經精讀本》：「早在摩西蒙召時(出3:8,17),神就描繪那地為“流奶與蜜之地”(11:9)」。

字面解析：對上既有「流奶與蜜之地」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 流奶與蜜之地 | 0.783 | link_folder/神學/流奶與蜜之地.md |
| 2 | 美地 | 0.707 | link_folder/主題/美地.md |
| 3 | 進迦南應許 | 0.562 | link_folder/歷史/進迦南應許.md |
| 4 | 神的聖所 | 0.519 | link_folder/神學/神的聖所.md |
| 5 | 米甸地 | 0.515 | link_folder/地點/米甸地.md |

判定：✅ 建議使用既有條目 [[流奶與蜜之地]]（同名／字面對應）

## 越過耶和華的口（peh）（原文）
query:
- 待建立詞：越過耶和華的口（peh）
- 出現位置：申命記 第1章
- 候選類型：原文
- 本章上下文：v26「竟違背了耶和華─你們神的命令」；v43「竟違背耶和華的命令，擅自上山地去了」。GT《聖經精讀本》：「違背了耶和華你們神的命令: 在這裡意指誡命的“命令”(希伯來語, peh)的字面意思是“口”。即,出自神之口的話就是誡命」。STEP 兩節同為 va./tam.Ru 'et- pi Yah.weh（H4784 marah「to rebel」＋H6310I peh「lip: word」）；相對地 v45「耶和華卻不聽你們的聲音」用的是 be./Ko.le./Khem（H6963A qol「voice」）。
- 經文用詞：命令

字面解析：對上既有「越過耶和華的口（peh）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 越過耶和華的口（peh） | 0.728 | link_folder/原文/越過耶和華的口（peh）.md |
| 2 | 爭先與擅自 | 0.563 | link_folder/原文/爭先與擅自.md |
| 3 | 遵著耶和華的吩咐記載路程 | 0.511 | link_folder/主題/遵著耶和華的吩咐記載路程.md |
| 4 | 擅敢行事與褻瀆耶和華的剪除處分 | 0.491 | link_folder/神學/擅敢行事與褻瀆耶和華的剪除處分.md |
| 5 | 不聽從神的五層漸進懲罰（利26：14-39） | 0.482 | link_folder/主題/不聽從神的五層漸進懲罰（利26：14-39）.md |

判定：✅ 建議使用既有條目 [[越過耶和華的口（peh）]]（同名／字面對應）

## 心消化（ma.sas）（原文）
query:
- 待建立詞：心消化（ma.sas）
- 出現位置：申命記 第1章
- 候選類型：原文
- 本章上下文：v28「我們的弟兄使我們的心消化」。CT 原文字義：「消化」溶化，溶解；GT《聖經精讀本》：「使我們的心消化: 原文的字面意義是“使心消融並淌流”」；BH：「The phrase "hearts melt" is a vivid expression of fear and loss of courage」。STEP 顯示是 he.Ma.su 'et- le.va.Ve./nu（H4549 ma.sas「to melt」，Hiphil 使役），簡要詞典義 to melt。
- 經文用詞：心消化

字面解析：對上既有「心消化（ma.sas）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 心消化（ma.sas） | 0.789 | link_folder/原文/心消化（ma.sas）.md |
| 2 | 未受割禮的心若謙卑（認罪悔改的條件） | 0.417 | link_folder/神學/未受割禮的心若謙卑（認罪悔改的條件）.md |
| 3 | 不可心裡恨弟兄總要指摘鄰舍 | 0.412 | link_folder/主題/不可心裡恨弟兄總要指摘鄰舍.md |
| 4 | 來3：8-9 硬著心不可像瑪撒 | 0.398 | link_folder/互文/來3：8-9 硬著心不可像瑪撒.md |
| 5 | 為定與廢去（qum 與 pa.rar） | 0.390 | link_folder/原文/為定與廢去（qum 與 pa.rar）.md |

判定：✅ 建議使用既有條目 [[心消化（ma.sas）]]（同名／字面對應）

## 亞衲族與偉人拿非林（背景）
query:
- 待建立詞：亞衲族與偉人拿非林
- 出現位置：申命記 第1章
- 候選類型：背景
- 本章上下文：v28「並且我們在那裡看見亞衲族的人」。CT 原文字義：「亞衲」頸項；GT《啟導本》：「“亞衲族”為迦南早期居民，以身材高大著稱⋯但所居地的城牆，據考古學家發現，只有10至15公尺高。探子說“高得頂天”的確過甚其詞」；GT 李道生：「亞衲－－意即巨人，此族的人身體強壯高大」。STEP 顯示是 be.Nei 'a.na.Kim（H6062）。

字面解析：對上既有「亞衲族與偉人拿非林」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 亞衲族與偉人拿非林 | 0.813 | link_folder/背景/亞衲族與偉人拿非林.md |
| 2 | 偉人 | 0.593 | link_folder/人物/偉人.md |
| 3 | 迦南地的居民分佈 | 0.590 | link_folder/背景/迦南地的居民分佈.md |
| 4 | 利乏音人 | 0.552 | link_folder/人物/利乏音人.md |
| 5 | 亞捫人 | 0.541 | link_folder/人物/亞捫人.md |

判定：✅ 建議使用既有條目 [[亞衲族與偉人拿非林]]（同名／字面對應）

## 耶和華的爭戰（神學）
query:
- 待建立詞：耶和華的爭戰
- 出現位置：申命記 第1章
- 候選類型：神學
- 本章上下文：v30「在你們前面行的耶和華─你們的神必為你們爭戰」；v41「情願照耶和華─我們神一切所吩咐的上去爭戰」；v42「不要上去，也不要爭戰」。STEP 顯示 v30 是 hu' yi.la.Chem la./Khem（H3898A lacham，Niphal）。
- 經文用詞：爭戰

字面解析：對上既有「耶和華的爭戰」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 耶和華的爭戰 | 0.683 | link_folder/神學/耶和華的爭戰.md |
| 2 | 在耶和華面前 | 0.568 | link_folder/神學/在耶和華面前.md |
| 3 | 耶和華是戰士 | 0.565 | link_folder/神學/耶和華是戰士.md |
| 4 | 爭先與擅自 | 0.522 | link_folder/原文/爭先與擅自.md |
| 5 | 報仇（na.qam 與 nik.mah） | 0.465 | link_folder/原文/報仇（na.qam 與 nik.mah）.md |

判定：✅ 建議使用既有條目 [[耶和華的爭戰]]（同名／字面對應）

## 雲柱火柱（歷史）
query:
- 待建立詞：雲柱火柱
- 出現位置：申命記 第1章
- 候選類型：歷史
- 本章上下文：v33「夜間在火柱裡，日間在雲柱裡，指示你們所當行的路」。GT《啟導本》：「在曠野中，神的約櫃走在百姓前面，為他們開路，找安營的地方。神在會幕的雲彩中，用火柱、雲柱引領他們行經曠野（參出十三21）」。

字面解析：對上既有「雲柱火柱」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 雲柱火柱 | 0.763 | link_folder/歷史/雲柱火柱.md |
| 2 | 雲彩 | 0.580 | link_folder/原文/雲彩.md |
| 3 | 法櫃的帳幕 | 0.539 | link_folder/地點/法櫃的帳幕.md |
| 4 | 耶和華的榮光 | 0.525 | link_folder/神學/耶和華的榮光.md |
| 5 | 摩西的臨時會幕（營外） | 0.499 | link_folder/事件/摩西的臨時會幕（營外）.md |

判定：✅ 建議使用既有條目 [[雲柱火柱]]（同名／字面對應）

## 加低斯巴尼亞事件（歷史）
query:
- 待建立詞：加低斯巴尼亞事件
- 出現位置：申命記 第1章
- 候選類型：歷史
- 本章上下文：v19-46 整段回顧。GT《聖經精讀本》：「回顧加低斯巴尼亞事件:本文回顧了38年前加低斯巴尼亞所發生的以色列舊世代苦澀的叛逆事件(民13:1-14:45)」。

字面解析：對上既有「加低斯巴尼亞事件」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 加低斯巴尼亞事件 | 0.652 | link_folder/歷史/加低斯巴尼亞事件.md |
| 2 | 加低斯 | 0.517 | link_folder/地點/加低斯.md |
| 3 | 十一天的路程 | 0.515 | link_folder/主題/十一天的路程.md |
| 4 | 神的回顧只記進度不記背叛 | 0.495 | link_folder/神學/神的回顧只記進度不記背叛.md |
| 5 | 曠野飄流四十年 | 0.487 | link_folder/歷史/曠野飄流四十年.md |

判定：✅ 建議使用既有條目 [[加低斯巴尼亞事件]]（同名／字面對應）

## 迦勒（人物）
query:
- 待建立詞：迦勒
- 出現位置：申命記 第1章
- 候選類型：人物
- 本章上下文：v36「惟有耶孚尼的兒子迦勒必得看見⋯因為他專心跟從我」。CT 原文字義：「耶孚尼」他將被面對；「迦勒」有才能的，勇敢，全心的；BH：「His father, Jephunneh, is identified as a Kenizzite」。STEP 顯示是 ka.Lev ben- ye.fu.Neh（H3612G＋H3312G）。

字面解析：對上既有「迦勒」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 迦勒 | 0.675 | link_folder/人物/迦勒.md |
| 2 | 專心跟從主與另一個心志 | 0.580 | link_folder/神學/專心跟從主與另一個心志.md |
| 3 | 迦得（萬幸） | 0.498 | link_folder/人物/迦得（萬幸）.md |
| 4 | 基尼洗人 | 0.482 | link_folder/人物/基尼洗人.md |
| 5 | 迦累得 | 0.461 | link_folder/原文/迦累得.md |

判定：✅ 建議使用既有條目 [[迦勒]]（同名／字面對應）

## 專心跟從主與另一個心志（神學）
query:
- 待建立詞：專心跟從主與另一個心志
- 出現位置：申命記 第1章
- 候選類型：神學
- 本章上下文：v36「因為他專心跟從我」。CT：「『專心跟從我』字面的意思是『完全跟在我後面』，意指一心一意跟從神，不受任何外在因素的影響(參民三十二12)」；KC：「His name means 'wholeheartedly'.」STEP 顯示是 mi.Le' 'a.cha.Rei Yah.weh（H4390 ma.le「to fill」Piel＋H310A a.char「after」），字面是「他填滿了跟在耶和華後面」。
- 經文用詞：專心跟從

字面解析：對上既有「專心跟從主與另一個心志」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 專心跟從主與另一個心志 | 0.747 | link_folder/神學/專心跟從主與另一個心志.md |
| 2 | 不隨從己心眼目行邪淫與成為聖潔 | 0.513 | link_folder/神學/不隨從己心眼目行邪淫與成為聖潔.md |
| 3 | 甘心樂意的奉獻 | 0.483 | link_folder/神學/甘心樂意的奉獻.md |
| 4 | 與神同行 | 0.478 | link_folder/神學/與神同行.md |
| 5 | 忌邪（嫉妒） | 0.470 | link_folder/原文/忌邪（嫉妒）.md |

判定：✅ 建議使用既有條目 [[專心跟從主與另一個心志]]（同名／字面對應）

## 摩西不得進入應許之地（事件）
query:
- 待建立詞：摩西不得進入應許之地
- 出現位置：申命記 第1章
- 候選類型：事件
- 本章上下文：v37「耶和華為你的緣故也向我發怒，說：你必不得進入那地」。CT：「『為你們的緣故』指以色列百姓惹動摩西氣憤失態，杖打磐石兩次，結果遭受神的懲罰(參民二十11~12)」；GT《雷氏研讀本》：「雖然拒絕摩西進入應許地的決定，在以色列人於加低斯被拒絕的三十八年後才宣佈出來，但兩個決定的原因是相同的——不信」。

字面解析：對上既有「摩西不得進入應許之地」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 摩西不得進入應許之地 | 0.753 | link_folder/事件/摩西不得進入應許之地.md |
| 2 | 加低斯巴尼亞事件 | 0.605 | link_folder/歷史/加低斯巴尼亞事件.md |
| 3 | 在米利巴未將耶和華尊為聖 | 0.603 | link_folder/神學/在米利巴未將耶和華尊為聖.md |
| 4 | 摩西擊打磐石兩下 | 0.601 | link_folder/事件/摩西擊打磐石兩下.md |
| 5 | 摩西 | 0.592 | link_folder/人物/摩西.md |

判定：✅ 建議使用既有條目 [[摩西不得進入應許之地]]（同名／字面對應）

## 約書亞（人物）
query:
- 待建立詞：約書亞
- 出現位置：申命記 第1章
- 候選類型：人物
- 本章上下文：v38「伺候你、嫩的兒子約書亞，他必得進入那地；你要勉勵他」。CT 原文字義：「嫩」魚，後裔；「勉勵」兼顧，加強；BH：「His name, originally Hoshea, was changed by Moses to Joshua, meaning "The LORD is salvation"」。

字面解析：對上既有「約書亞」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 約書亞 | 0.693 | link_folder/人物/約書亞.md |
| 2 | 何西阿與約書亞改名時機與字意之解經爭議 | 0.631 | link_folder/解經爭議/何西阿與約書亞改名時機與字意之解經爭議.md |
| 3 | 約書亞承接摩西 | 0.518 | link_folder/事件/約書亞承接摩西.md |
| 4 | 迦勒 | 0.511 | link_folder/人物/迦勒.md |
| 5 | 以色列 | 0.492 | link_folder/原文/以色列.md |

判定：✅ 建議使用既有條目 [[約書亞]]（同名／字面對應）

## 海（紅海）（地點）
query:
- 待建立詞：海（紅海）
- 出現位置：申命記 第1章
- 候選類型：地點
- 本章上下文：v40「至於你們，要轉回，從紅海的路往曠野去」。GT《啟導本》：「“紅海”原文為“蘆葦海”，當日很多湖泊都用此名（參出十四21注）。此處指阿卡巴灣」；GT《串珠》：「「紅海的路」：應作「蘆葦海的路」（參出13:18注）。這路經過加低斯東面」。
- 經文用詞：紅海

字面解析：對上既有「海（紅海）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 海（紅海） | 0.793 | link_folder/地點/海（紅海）.md |
| 2 | 紅海曠野 | 0.733 | link_folder/地點/紅海曠野.md |
| 3 | 紅海指的是哪個海 | 0.723 | link_folder/解經爭議/紅海指的是哪個海.md |
| 4 | 紅海分開 | 0.576 | link_folder/歷史/紅海分開.md |
| 5 | 過紅海 | 0.558 | link_folder/歷史/過紅海.md |

判定：✅ 建議使用既有條目 [[海（紅海）]]（同名／字面對應）

## 得罪神（神學）
query:
- 待建立詞：得罪神
- 出現位置：申命記 第1章
- 候選類型：神學
- 本章上下文：v41「我們得罪了耶和華」。CT 原文字義：「得罪」錯過目標，出差錯，犯罪。STEP 顯示是 cha.ta.Nu（H2398 chata），簡要詞典義 to sin。KC：「If the confession "we have sinned" sounds from their mouths, it is only by rote with no real meaning.」
- 經文用詞：得罪

字面解析：對上既有「得罪神」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 得罪神 | 0.663 | link_folder/神學/得罪神.md |
| 2 | 你們的罪必追上你們 | 0.505 | link_folder/神學/你們的罪必追上你們.md |
| 3 | 未見雅各中有罪孽 | 0.504 | link_folder/神學/未見雅各中有罪孽.md |
| 4 | 誤犯 | 0.489 | link_folder/神學/誤犯.md |
| 5 | 罪伏在門前 | 0.489 | link_folder/神學/罪伏在門前.md |

判定：✅ 建議使用既有條目 [[得罪神]]（同名／字面對應）

## 爭先與擅自（原文）
query:
- 待建立詞：爭先與擅自
- 出現位置：申命記 第1章
- 候選類型：原文
- 本章上下文：v41「於是你們各人帶著兵器，爭先上山地去了」；v43「竟違背耶和華的命令，擅自上山地去了」。CT 原文字義：「爭先」認為容易，輕鬆以待；「擅自」傲慢，無禮。GT《聖經精讀本》：「擅自: “無禮”或“妄自尊大”」。STEP 顯示 v41 是 va./ta.Hi.nu（H1951 hun，context gloss「you regarded as easy」）、v43 是 va./ta.Zi.du（H2102 zud，簡要詞典義「to boil」，context gloss「you acted presumptuously」）。BH：「thinking it easy to go up into the hill country⋯reveals their misunderstanding of the situation and underestimation of the enemy」。
- 經文用詞：爭先、擅自

字面解析：對上既有「爭先與擅自」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 爭先與擅自 | 0.867 | link_folder/原文/爭先與擅自.md |
| 2 | 假意悔改與冒死擅自作戰 | 0.543 | link_folder/事件/假意悔改與冒死擅自作戰.md |
| 3 | 擅敢行事與褻瀆耶和華的剪除處分 | 0.498 | link_folder/神學/擅敢行事與褻瀆耶和華的剪除處分.md |
| 4 | 耶和華的爭戰 | 0.488 | link_folder/神學/耶和華的爭戰.md |
| 5 | 自認如蚱蜢的不信態勢 | 0.484 | link_folder/神學/自認如蚱蜢的不信態勢.md |

判定：✅ 建議使用既有條目 [[爭先與擅自]]（同名／字面對應）

## 迦南大敗直到何珥瑪（歷史）
query:
- 待建立詞：迦南大敗直到何珥瑪
- 出現位置：申命記 第1章
- 候選類型：歷史
- 本章上下文：v44「住那山地的亞摩利人就出來攻擊你們，追趕你們，如蜂擁一般，在西珥殺退你們，直到何珥瑪」。CT：「『何珥瑪』是雙關語，原本是可以得到『庇護』的地理用詞，現在轉用來成為『完全毀滅』的所在」；CT 原文字義：「殺退」打碎。STEP 顯示「如蜂擁一般」是 ka.'a.Sher ta.'a.Sei.nah ha./de.vo.Rim（H1682 devorah「bee」）、「殺退」是 va/i.ya.ke.Tu（H3807 katat「to crush」）。

字面解析：對上既有「迦南大敗直到何珥瑪」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 迦南大敗直到何珥瑪 | 0.798 | link_folder/歷史/迦南大敗直到何珥瑪.md |
| 2 | 戰勝亞拉得王 | 0.611 | link_folder/歷史/戰勝亞拉得王.md |
| 3 | 亞摩利人 | 0.570 | link_folder/人物/亞摩利人.md |
| 4 | 西珥山 | 0.545 | link_folder/地點/西珥山.md |
| 5 | 迦南人 | 0.541 | link_folder/人物/迦南人.md |

判定：✅ 建議使用既有條目 [[迦南大敗直到何珥瑪]]（同名／字面對應）

## 宗主條約（背景）
query:
- 待建立詞：宗主條約
- 出現位置：申命記 第1章
- 候選類型：背景
- 本章上下文：GT《聖經精讀本》：「摩西的第一篇講章:整卷書都依照當時施行於古代近東的宗主權盟約的傳統形式進行記錄。其結構如下:①前言;②歷史性序論;③立約;④保存並公開頒佈;⑤證人的名單;⑥根據是否遵守所立之約而賜下的祝福與咒詛。如此來看,本文當屬前言與歷史性序論部分。因為,本文是構成本書的三篇講章(1:6-4:43;4:44-26:19;27:1-30:20)中第一篇」。

字面解析：對上既有「宗主條約」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 宗主條約 | 0.740 | link_folder/背景/宗主條約.md |
| 2 | 盟約 | 0.614 | link_folder/主題/盟約.md |
| 3 | 約書 | 0.611 | link_folder/神學/約書.md |
| 4 | 西乃之約 | 0.594 | link_folder/神學/西乃之約.md |
| 5 | 古代近東立約 | 0.593 | link_folder/背景/古代近東立約.md |

判定：✅ 建議使用既有條目 [[宗主條約]]（同名／字面對應）

## 伯拉大河（地點）
query:
- 待建立詞：伯拉大河
- 出現位置：申命記 第1章
- 候選類型：地點
- 本章上下文：v7「並利巴嫩山又到伯拉大河」。CT：「『伯拉大河』即今幼發拉底河，是神所應許之地的北方界線」；CT 原文字義：「伯拉」豐收；BH：「The Euphrates River, one of the longest rivers in Western Asia, marks the northeastern boundary of the promised land」。STEP 顯示是 ne.har- pe.Rat（H5104H na.har「river」＋H6578）。

字面解析：對上既有「伯拉大河」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 伯拉大河 | 0.822 | link_folder/地點/伯拉大河.md |
| 2 | 「伯拉大河」名稱 | 0.706 | link_folder/原文/「伯拉大河」名稱.md |
| 3 | 應許之地的四至 | 0.597 | link_folder/主題/應許之地的四至.md |
| 4 | 埃及河的地理辨識 | 0.552 | link_folder/解經爭議/埃及河的地理辨識.md |
| 5 | 伊甸園四河 | 0.527 | link_folder/背景/伊甸園四河.md |

判定：✅ 建議使用既有條目 [[伯拉大河]]（同名／字面對應）

## 摩西立首領（事件）
query:
- 待建立詞：摩西立首領
- 出現位置：申命記 第1章
- 候選類型：事件
- 本章上下文：v13-15「你們要按著各支派選舉⋯我立他們為你們的首領」「我便將你們各支派的首領⋯立他們為官長、千夫長、百夫長、五十夫長、十夫長」。CT：「本節又說出領袖人物如何產生：(1)選舉──為眾人所舉薦；(2)設立──為成熟的既任領袖所認可」；GT《啟導本》：「本節至18節所記的事可參《出埃及記》十八13～26」。

字面解析：對上既有「摩西立首領」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 摩西立首領 | 0.825 | link_folder/事件/摩西立首領.md |
| 2 | 曠野審判制度 | 0.618 | link_folder/背景/曠野審判制度.md |
| 3 | 以色列的長老 | 0.605 | link_folder/文化/以色列的長老.md |
| 4 | 以色列人的官長 | 0.597 | link_folder/人物/以色列人的官長.md |
| 5 | 葉忒羅建議分層治理 | 0.589 | link_folder/事件/葉忒羅建議分層治理.md |

判定：✅ 建議使用既有條目 [[摩西立首領]]（同名／字面對應）

## 候選互查（本章內部，⚠＝彼此相似 ≥ 0.8）
（無 ≥ 門檻的配對）
