<!-- candidate_similarity_meta
schema_version: 1
book: 申命記
chapter: 13
candidate_sha256: 53b00a8399edede41e3d55dae750d28289c85c7501196edfad4f20d4e4de584b
candidate_identity_sha256: ea163e84bf9a7e4c24907484da0a0156599ea3b8d828a7058a00d5b0c87c55a0
embedding_model: nvidia/nemotron-3-embed-1b
embedding_index_fingerprint: d15542f6c35b1da7
link_index_sha256: afc62a77704b182bbdcae4e4b72e2de6fc7bb43dee4cca50cc0e6eed8750ecbd
homonyms_sha256: b8d042ea4f51253052128b2b289befdcf00b53c88237b67050f3252242c41ab8
rerank_model: nvidia/llama-nemotron-rerank-vl-1b-v2:free
rerank_policy_version: 2026.08.4
calibration_sha256: f63b1218023371bbbece396422aa7a02025bba0da119b49cae75232755734211
rerank_status: success
rerankable_candidates: 1
rerank_attempted: 1
rerank_succeeded: 1
rerank_retrieve_top_k: 20
rerank_score_observed: 0.031-0.126
-->

# 候選語義近鄰報告：申命記 第13章

- 檢索模型：nvidia/nemotron-3-embed-1b｜重排模型：nvidia/llama-nemotron-rerank-vl-1b-v2:free（未校準/保守模式）｜全庫 2997 條
- 規則說明：字面確切匹配直接通過；其餘候選先檢索 Top 20 名再由 Reranker 重排，取前 5 名顯示。
  治理優先：同名歧義（D類）與分類不相容永遠標 ⚠。
  重排模型未校準時，⚠ 由檢索相似度規則（≥0.50 且 top-1 非同實體）決定，重排名次只當附加證據。
  字面解析：列 resolver 實際比對結果——標「請確認」者務必人工核實。

## 神蹟奇事不是真先知的憑證（主題）
query:
- 待建立詞：神蹟奇事不是真先知的憑證
- 出現位置：申命記 第13章
- 候選類型：主題
- 本章上下文：v1-3：先知或做夢的顯神蹟奇事、甚至應驗了，仍不可聽。GT《啟導本聖經申命記註釋》說真先知的憑證不是有無行神蹟的能力，而是他的信息和工作是否符合神所啟示的客觀標準；GT《聖經精讀本》說在基督教信仰中神跡奇事本身並不重要，重要的是是否榮耀神；KC 說 It is not the sign or the wonder that is decisive, but the Word of God；BH 引帖後2:9 與太24:24 說行神蹟不自動證明差遣的權柄
- 經文用詞：神蹟奇事

字面解析：對上既有「神蹟奇事不是真先知的憑證」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 神蹟奇事不是真先知的憑證 | 0.814 | link_folder/主題/神蹟奇事不是真先知的憑證.md |
| 2 | 神蹟（miraculous signs） | 0.632 | link_folder/神學/神蹟（miraculous signs）.md |
| 3 | 先知 | 0.592 | link_folder/主題/先知.md |
| 4 | 巴蘭是先知還是術士 | 0.531 | link_folder/解經爭議/巴蘭是先知還是術士.md |
| 5 | 神的權柄與能力 | 0.504 | link_folder/神學/神的權柄與能力.md |

判定：✅ 建議使用既有條目 [[神蹟奇事不是真先知的憑證]]（同名／字面對應）

## 匪類（be.liy.ya.al）（原文）
query:
- 待建立詞：匪類（be.liy.ya.al）
- 出現位置：申命記 第13章
- 候選類型：原文
- 本章上下文：v12「有些匪類從你們中間的一座城出來」，STEP 為 'a.na.Shim be.nei- ve.li.Ya.'al（H582＋H1121H＋H1100G，be.liy.ya.al: Belial）。CT：『匪類』原文是「比列的子孫」，意指魔鬼的兒女；GT《申命記串珠聖經註釋》說該字的希伯來文讀音乃是彼列，原意可能是吞吃，新約用它來形容撒但（林後6:15）；GT《聖經精讀本》引士19:22 與帖後2:3；KC 稱之為 Belials-children
- 經文用詞：匪類

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 把那惡從你們中間除掉（ba.ar） | 0.499 | 0.126 | link_folder/神學/把那惡從你們中間除掉（ba.ar）.md |
| 2 | 敵擋（sa.tan） | 0.494 | 0.084 | link_folder/原文/敵擋（sa.tan）.md |
| 3 | 閒雜人 | 0.537 | 0.081 | link_folder/人物/閒雜人.md |
| 4 | 吃兒女的肉（極端饑荒的咒詛） | 0.491 | 0.073 | link_folder/主題/吃兒女的肉（極端饑荒的咒詛）.md |
| 5 | 不可偏向交鬼行巫術的 | 0.490 | 0.071 | link_folder/主題/不可偏向交鬼行巫術的.md |

rerank_margin: 0.042 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=原文 vs 條目=人物），若確為同實體請確認是否改用 [[閒雜人]]（重排模型 nvidia/llama-nemotron-rerank-vl-1b-v2:free 未校準，上表名次僅供參考）

## 探聽查究細細地訪問（da.rash、cha.qar、sha.al）（原文）
query:
- 待建立詞：探聽查究細細地訪問（da.rash、cha.qar、sha.al）
- 出現位置：申命記 第13章
- 候選類型：原文
- 本章上下文：v14「你就要探聽，查究，細細地訪問」，STEP 為 ve./da.rash.Ta（H1875，da.rash: to seek）、ve./cha.kar.Ta（H2713，cha.qar: to search）、ve./sha.'al.Ta（H7592，sha.al: to ask），後接 hei.Tev（H3190，不定詞絕對式，本節逐字解 thoroughly）。GT《聖經精讀本》說三次重複使用意義相近的動詞是為了強調決不聽信風聞；CT〔原文字義〕逐字給出調查、搜尋、殷勤徹底查問；KC 也把三個動作分開列出
- 經文用詞：探聽，查究，細細地訪問

字面解析：對上既有「探聽查究細細地訪問（da.rash、cha.qar、sha.al）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 探聽查究細細地訪問（da.rash、cha.qar、sha.al） | 0.813 | link_folder/原文/探聽查究細細地訪問（da.rash、cha.qar、sha.al）.md |
| 2 | 求問與訪問同一個字（da.rash） | 0.677 | link_folder/原文/求問與訪問同一個字（da.rash）.md |
| 3 | 盡心盡性尋求（ba.qash、da.rash） | 0.536 | link_folder/原文/盡心盡性尋求（ba.qash、da.rash）.md |
| 4 | 以色列啊你要聽（sha.ma） | 0.522 | link_folder/原文/以色列啊你要聽（sha.ma）.md |
| 5 | 留意聽從與留意謹守（雙同字） | 0.501 | link_folder/原文/留意聽從與留意謹守（雙同字）.md |

判定：✅ 建議使用既有條目 [[探聽查究細細地訪問（da.rash、cha.qar、sha.al）]]（同名／字面對應）

## 把那惡從你們中間除掉（ba.ar）（神學）
query:
- 待建立詞：把那惡從你們中間除掉（ba.ar）
- 出現位置：申命記 第13章
- 候選類型：神學
- 本章上下文：v5「這樣，就把那惡從你們中間除掉」，STEP 為 u./vi.'ar.Ta（H1197I，ba.ar: to burn: purge）＋ha./Ra'（H7451B，ra: bad: evil）。CT〔原文字義〕「除掉(原文雙同字)」消耗，燒盡，並說原文意指用火燒除，含有除惡務盡的意思；GT《啟導本》與《串珠》都把它接到申十七7、十九19、二十一21 等處；KC 數出這道命令在申命記出現九次，並以林前5:13 作新約對應
- 經文用詞：把那惡從你們中間除掉

字面解析：對上既有「把那惡從你們中間除掉（ba.ar）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 把那惡從你們中間除掉（ba.ar） | 0.839 | link_folder/神學/把那惡從你們中間除掉（ba.ar）.md |
| 2 | 林前5：13 | 0.618 | link_folder/互文/林前5：13.md |
| 3 | 除污穢的水 | 0.550 | link_folder/神學/除污穢的水.md |
| 4 | 剪除 | 0.544 | link_folder/原文/剪除.md |
| 5 | 滅絕 | 0.536 | link_folder/原文/滅絕.md |

判定：✅ 建議使用既有條目 [[把那惡從你們中間除掉（ba.ar）]]（同名／字面對應）

## 荒堆（tel）（原文）
query:
- 待建立詞：荒堆（tel）
- 出現位置：申命記 第13章
- 候選類型：原文
- 本章上下文：v16「那城就永為荒堆，不可再建造」，STEP 為 tel（H8510，tel: mound）。CT〔原文字義〕「荒堆」土堆，並說即指成為一堆廢墟；BH 指出 tel 在考古上有意義，許多被毀的古城後來就成了土丘
- 經文用詞：荒堆

字面解析：對上既有「荒堆（tel）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 荒堆（tel） | 0.779 | link_folder/原文/荒堆（tel）.md |
| 2 | 壘圈（ge.de.rah） | 0.415 | link_folder/原文/壘圈（ge.de.rah）.md |
| 3 | 沒有一座城高得使我們不能攻取 | 0.409 | link_folder/主題/沒有一座城高得使我們不能攻取.md |
| 4 | 迦累得 | 0.401 | link_folder/原文/迦累得.md |
| 5 | 伊迦爾撒哈杜他 | 0.388 | link_folder/原文/伊迦爾撒哈杜他.md |

判定：✅ 建議使用既有條目 [[荒堆（tel）]]（同名／字面對應）

## 滅絕（herem）（神學）
query:
- 待建立詞：滅絕（herem）
- 出現位置：申命記 第13章
- 候選類型：神學
- 本章上下文：v15「都用刀殺盡」STEP 為 ha.cha.Rem（H2763A，cha.ram: to devote/destroy，不定詞絕對式）、v17「那當毀滅的物」為 ha./Che.rem（H2764A，che.rem: devoted thing），正是既有條目所記的動詞與名詞一對。CT〔原文字義〕v15「殺盡」滅絕，完全地毀壞、v17「當毀滅的物」禁忌；GT《申命記串珠聖經註釋》說整座城都該被摧毀，如同迦南地的城邑一樣；BH 說明 herem 指完全歸給神、常以毀滅的方式達成
- 經文用詞：當毀滅的物、殺盡

字面解析：對上既有「滅絕（herem）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 滅絕（herem） | 0.757 | link_folder/神學/滅絕（herem）.md |
| 2 | 滅絕 | 0.718 | link_folder/原文/滅絕.md |
| 3 | 滅盡與除滅的雙同字（sha.mad） | 0.621 | link_folder/原文/滅盡與除滅的雙同字（sha.mad）.md |
| 4 | 荒堆（tel） | 0.600 | link_folder/原文/荒堆（tel）.md |
| 5 | 迦南滅絕命令的歷史範圍 | 0.597 | link_folder/解經爭議/迦南滅絕命令的歷史範圍.md |

判定：✅ 建議使用既有條目 [[滅絕（herem）]]（同名／字面對應）

## 石刑（背景）
query:
- 待建立詞：石刑
- 出現位置：申命記 第13章
- 候選類型：背景
- 本章上下文：v9「你先下手，然後眾民也下手」與 v10「要用石頭打死他」。STEP v9 為 ya.de./Kha ... va./ri.sho.Nah（H3027H 手＋H7223G first）與 ve./Yad kol- ha./'Am ba./'a.cha.ro.Nah（H314 last）。GT《聖經精讀本》說審判制度至少要兩個證人才能定罪，判死刑時證人先舉石打罪人；KC 說第一個見證人必須第一個丟石頭，控告的人不能把執行推給別人；BH 說這是防止誣告的保護機制並接到約8:7；GT《啟導本》另舉拿伯被害（王上21:13）與司提反的例子
- 經文用詞：你先下手、用石頭打死他

字面解析：對上既有「石刑」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 石刑 | 0.678 | link_folder/背景/石刑.md |
| 2 | 死刑的罪行 | 0.591 | link_folder/神學/死刑的罪行.md |
| 3 | 憑幾個見證人的口 | 0.591 | link_folder/主題/憑幾個見證人的口.md |
| 4 | 按手在犯人頭上作見證（利24：14） | 0.584 | link_folder/主題/按手在犯人頭上作見證（利24：14）.md |
| 5 | 褻瀆聖名案例（利未記唯一記載的具體刑罰執行事件） | 0.578 | link_folder/事件/褻瀆聖名案例（利未記唯一記載的具體刑罰執行事件）.md |

判定：✅ 建議使用既有條目 [[石刑]]（同名／字面對應）

## 神蹟（miraculous signs）（神學）
query:
- 待建立詞：神蹟（miraculous signs）
- 出現位置：申命記 第13章
- 候選類型：神學
- 本章上下文：v1-2「向你顯個神蹟奇事」「他所顯的神蹟奇事雖有應驗」，STEP 為 'ot（H226G，ot: sign: miraculous）與 mo.Fet（H4159，mo.phet: wonder）。既有條目收的是神蹟作為差遣憑證的正面用法；本章給的是反例——神蹟即使應驗也可能出自假先知。CT〔原文字義〕「神蹟」神蹟，記號；GT《啟導本》說「神蹟」為指示將來的預兆，「奇事」是證明先知或作夢的確有能力的異事，二詞常用作同義詞。本章經文詞「神蹟奇事」的內文連結裁給新建條目〈神蹟奇事不是真先知的憑證〉，此條目走累積與知識節點

字面解析：對上既有「神蹟（miraculous signs）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 神蹟奇事不是真先知的憑證 | 0.768 | link_folder/主題/神蹟奇事不是真先知的憑證.md |
| 2 | 神蹟（miraculous signs） | 0.687 | link_folder/神學/神蹟（miraculous signs）.md |
| 3 | 先知 | 0.523 | link_folder/主題/先知.md |
| 4 | 手長大痲瘋的神蹟 | 0.507 | link_folder/神學/手長大痲瘋的神蹟.md |
| 5 | 不可行法術觀兆 | 0.494 | link_folder/主題/不可行法術觀兆.md |

判定：✅ 建議使用既有條目 [[神蹟（miraculous signs）]]（同名／字面對應）

## 林前5：13（互文）
query:
- 待建立詞：林前5：13
- 出現位置：申命記 第13章
- 候選類型：互文
- 本章上下文：KC 在 v1-5 把申13:5「把那惡從你們中間除掉」接到新約的對應命令：舊約是把人治死，新約是 Remove the wicked man from among yourselves（林前5:13b）；他並說這道命令在申命記出現九次

字面解析：對上既有「林前5：13」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 林前5：13 | 0.805 | link_folder/互文/林前5：13.md |
| 2 | 把那惡從你們中間除掉（ba.ar） | 0.677 | link_folder/神學/把那惡從你們中間除掉（ba.ar）.md |
| 3 | 出20：13 | 0.513 | link_folder/互文/出20：13.md |
| 4 | 不潔淨被剪除預表拒絕恩典滅亡（來10：26-29） | 0.473 | link_folder/互文/不潔淨被剪除預表拒絕恩典滅亡（來10：26-29）.md |
| 5 | 羅13：1-7 | 0.470 | link_folder/互文/羅13：1-7.md |

判定：✅ 建議使用既有條目 [[林前5：13]]（同名／字面對應）

## 先知（主題）
query:
- 待建立詞：先知
- 出現位置：申命記 第13章
- 候選類型：主題
- 本章上下文：v1、3、5 三次「那先知」。CT〔原文字義〕「先知」先知，發言人，說話者，並說『先知』指為神說話的人、『做夢的』指在睡夢中看見異象向人宣講神旨意者；GT《聖經精讀本》說作夢的指主張自己所作的夢是從神而來的特別啟示
- 經文用詞：先知

字面解析：對上既有「先知」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 先知 | 0.658 | link_folder/主題/先知.md |
| 2 | 神在夢中顯現與引導 | 0.557 | link_folder/神學/神在夢中顯現與引導.md |
| 3 | 神蹟奇事不是真先知的憑證 | 0.547 | link_folder/主題/神蹟奇事不是真先知的憑證.md |
| 4 | 巴蘭是先知還是術士 | 0.520 | link_folder/解經爭議/巴蘭是先知還是術士.md |
| 5 | 古代近東的超脫預言 | 0.503 | link_folder/背景/古代近東的超脫預言.md |

判定：✅ 建議使用既有條目 [[先知]]（同名／字面對應）

## 你要盡心盡性盡力愛耶和華（a.hav）（原文）
query:
- 待建立詞：你要盡心盡性盡力愛耶和華（a.hav）
- 出現位置：申命記 第13章
- 候選類型：原文
- 本章上下文：v3「要知道你們是盡心盡性愛耶和華─你們的神不是」，STEP 為 'o.ha.Vim（H157G，a.hav: to love）＋be./khol le.vav./Khem（H3824，le.vav: heart）＋naf.she./Khem（H5315G，ne.phesh: soul）。CT 說『盡心盡性』原文是「全心全魂」；BH 明指這句呼應申6:4-5 的示馬，並說耶穌在太22:37-38 稱之為最大的誡命。本章比申6 少了「盡力」一項
- 經文用詞：盡心盡性愛耶和華

字面解析：對上既有「你要盡心盡性盡力愛耶和華（a.hav）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 你要盡心盡性盡力愛耶和華（a.hav） | 0.789 | link_folder/原文/你要盡心盡性盡力愛耶和華（a.hav）.md |
| 2 | 太22：36-39 | 0.650 | link_folder/互文/太22：36-39.md |
| 3 | 盡心盡性尋求（ba.qash、da.rash） | 0.634 | link_folder/原文/盡心盡性尋求（ba.qash、da.rash）.md |
| 4 | 耶和華向你所要的是什麼呢 | 0.571 | link_folder/主題/耶和華向你所要的是什麼呢.md |
| 5 | 甘心樂意的奉獻 | 0.532 | link_folder/神學/甘心樂意的奉獻.md |

判定：✅ 建議使用既有條目 [[你要盡心盡性盡力愛耶和華（a.hav）]]（同名／字面對應）

## 神的試驗（神學）
query:
- 待建立詞：神的試驗
- 出現位置：申命記 第13章
- 候選類型：神學
- 本章上下文：v3「因為這是耶和華─你們的神試驗你們」。CT 說『試驗你們』指驗明人的存心所在，並強調這並非說神主動利用假先知行神蹟奇事，而是神容許假先知行騙以顯明人的存心；GT《申命記串珠聖經註釋》要讀者參米該雅的預言與事蹟（王上22章）
- 經文用詞：試驗你們

字面解析：對上既有「神的試驗」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 神的試驗 | 0.724 | link_folder/神學/神的試驗.md |
| 2 | 神蹟奇事不是真先知的憑證 | 0.671 | link_folder/主題/神蹟奇事不是真先知的憑證.md |
| 3 | 神試驗亞伯拉罕 | 0.653 | link_folder/神學/神試驗亞伯拉罕.md |
| 4 | 試探的本質 | 0.575 | link_folder/神學/試探的本質.md |
| 5 | 苦煉（a.nah） | 0.543 | link_folder/原文/苦煉（a.nah）.md |

判定：✅ 建議使用既有條目 [[神的試驗]]（同名／字面對應）

## 試探的本質（神學）
query:
- 待建立詞：試探的本質
- 出現位置：申命記 第13章
- 候選類型：神學
- 本章上下文：GT《聖經精讀本》在 v3 把兩者分開：神的試驗與撒但的試探全然不同，撒但的試探在人的內心勾起犯罪的衝動、目的在於誘惑人使其陷入網羅，神試驗人則是熬煉自己百姓的愛之教育過程

字面解析：對上既有「試探的本質」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 試探的本質 | 0.681 | link_folder/神學/試探的本質.md |
| 2 | 神的試驗 | 0.677 | link_folder/神學/神的試驗.md |
| 3 | 神試驗亞伯拉罕 | 0.629 | link_folder/神學/神試驗亞伯拉罕.md |
| 4 | 撒但 | 0.495 | link_folder/神學/撒但.md |
| 5 | 苦煉（a.nah） | 0.491 | link_folder/原文/苦煉（a.nah）.md |

判定：✅ 建議使用既有條目 [[試探的本質]]（同名／字面對應）

## 專靠（da.veq）（原文）
query:
- 待建立詞：專靠（da.veq）
- 出現位置：申命記 第13章
- 候選類型：原文
- 本章上下文：v4「專靠他」STEP 為 tid.ba.Ku/n（H1692，da.vaq: to cleave）；v17「不可粘你的手」是同一個字根的 yid.Bak（H1692）。CT〔原文字義〕在 v4 註「專靠」附著，黏住，緊靠，在 v17 註「粘」附著，黏住，緊靠，兩處字義完全相同
- 經文用詞：專靠

字面解析：對上既有「專靠（da.veq）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 專靠（da.veq） | 0.734 | link_folder/原文/專靠（da.veq）.md |
| 2 | 各守各的產業（da.vaq） | 0.438 | link_folder/原文/各守各的產業（da.vaq）.md |
| 3 | 敬畏與可畏同一字根（ya.re） | 0.401 | link_folder/原文/敬畏與可畏同一字根（ya.re）.md |
| 4 | 擾害（tsa.rar） | 0.399 | link_folder/原文/擾害（tsa.rar）.md |
| 5 | 你且由著我（ra.phah） | 0.398 | link_folder/原文/你且由著我（ra.phah）.md |

判定：✅ 建議使用既有條目 [[專靠（da.veq）]]（同名／字面對應）

## 敬畏神（神學）
query:
- 待建立詞：敬畏神
- 出現位置：申命記 第13章
- 候選類型：神學
- 本章上下文：v4「敬畏他」STEP 為 ti.Ra.'u（H3372H，ya.re: to fear: revere）。CT 說『敬畏祂』指害怕惹祂不喜悅、發怒；GT《啟導本》說考驗一個人靈性的標準在他是否遵從神的話、侍奉祂、倚靠祂
- 經文用詞：敬畏他

字面解析：對上既有「敬畏神」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 敬畏神 | 0.662 | link_folder/神學/敬畏神.md |
| 2 | 敬畏與可畏同一字根（ya.re） | 0.618 | link_folder/原文/敬畏與可畏同一字根（ya.re）.md |
| 3 | 敬畏耶和華的話 | 0.580 | link_folder/神學/敬畏耶和華的話.md |
| 4 | 敬畏以撒的神 | 0.578 | link_folder/神學/敬畏以撒的神.md |
| 5 | 敬畏與信服 | 0.575 | link_folder/神學/敬畏與信服.md |

判定：✅ 建議使用既有條目 [[敬畏神]]（同名／字面對應）

## 事奉與作奴僕同一字根（a.vad）（原文）
query:
- 待建立詞：事奉與作奴僕同一字根（a.vad）
- 出現位置：申命記 第13章
- 候選類型：原文
- 本章上下文：v2「事奉他吧」、v4「事奉他」STEP 為 ta.'a.Vo.du（H5647H）、v12「事奉你們素來所不認識的別神」為 ve./na.'av.Dah（H5647H，a.vad: to serve: minister）；同一個動詞同時用在事奉真神與事奉別神兩邊
- 經文用詞：事奉他

字面解析：對上既有「事奉與作奴僕同一字根（a.vad）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 事奉與作奴僕同一字根（a.vad） | 0.686 | link_folder/原文/事奉與作奴僕同一字根（a.vad）.md |
| 2 | 侍立事奉（a.mad、sha.rat） | 0.546 | link_folder/原文/侍立事奉（a.mad、sha.rat）.md |
| 3 | 不可照他們那樣事奉耶和華 | 0.530 | link_folder/神學/不可照他們那樣事奉耶和華.md |
| 4 | 他的道（de.rekh） | 0.480 | link_folder/原文/他的道（de.rekh）.md |
| 5 | 奴僕 | 0.468 | link_folder/原文/奴僕.md |

判定：✅ 建議使用既有條目 [[事奉與作奴僕同一字根（a.vad）]]（同名／字面對應）

## 為奴之家（主題）
query:
- 待建立詞：為奴之家
- 出現位置：申命記 第13章
- 候選類型：主題
- 本章上下文：v5「救贖你脫離為奴之家」STEP 為 mi./Beit（H1004B）＋'a.va.Dim（H5650，e.ved: servant/slave），「救贖」是 ve./ha./po.de./Kha（H6299，pa.dah: to ransom）；v10 再說一次。KC 說呼籲人去事奉別神是對神的直接侮辱，也是否認救贖是祂而不是偶像成就的
- 經文用詞：為奴之家

字面解析：對上既有「為奴之家」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 為奴之家 | 0.701 | link_folder/主題/為奴之家.md |
| 2 | 事奉與作奴僕同一字根（a.vad） | 0.604 | link_folder/原文/事奉與作奴僕同一字根（a.vad）.md |
| 3 | 出埃及為要事奉神 | 0.547 | link_folder/神學/出埃及為要事奉神.md |
| 4 | 基督為奴僕 | 0.533 | link_folder/主題/基督為奴僕.md |
| 5 | 奴僕 | 0.518 | link_folder/原文/奴僕.md |

判定：✅ 建議使用既有條目 [[為奴之家]]（同名／字面對應）

## 出埃及（歷史）
query:
- 待建立詞：出埃及
- 出現位置：申命記 第13章
- 候選類型：歷史
- 本章上下文：v5「那領你們出埃及地」與 v10「那領你出埃及地為奴之家的耶和華」。BH 說出埃及是以色列歷史的根基事件，背棄神不只是拒絕祂的律法，也是否認祂的救贖作為
- 經文用詞：出埃及地

字面解析：對上既有「出埃及」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 出埃及 | 0.680 | link_folder/歷史/出埃及.md |
| 2 | 為奴之家 | 0.643 | link_folder/主題/為奴之家.md |
| 3 | 出埃及為要事奉神 | 0.625 | link_folder/神學/出埃及為要事奉神.md |
| 4 | 救贖 | 0.591 | link_folder/神學/救贖.md |
| 5 | 埃及 | 0.589 | link_folder/地點/埃及.md |

判定：✅ 建議使用既有條目 [[出埃及]]（同名／字面對應）

## 專一敬拜（神學）
query:
- 待建立詞：專一敬拜
- 出現位置：申命記 第13章
- 候選類型：神學
- 本章上下文：全章三段都在處理同一件事——被引誘去事奉別神時該怎麼辦。GT《聖經精讀本》說本章分三個類型訓戒虛假宗教的誘惑：來自假先知的、來自家人與親戚的、來自群眾的；KC 說拜偶像是對神以及祂與百姓關係的本質性攻擊

字面解析：對上既有「專一敬拜」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 專一敬拜 | 0.693 | link_folder/神學/專一敬拜.md |
| 2 | 敬畏神與專一事奉 | 0.589 | link_folder/主題/敬畏神與專一事奉.md |
| 3 | 專一事奉 | 0.577 | link_folder/神學/專一事奉.md |
| 4 | 敬拜 | 0.565 | link_folder/主題/敬拜.md |
| 5 | 不可照他們那樣事奉耶和華 | 0.563 | link_folder/神學/不可照他們那樣事奉耶和華.md |

判定：✅ 建議使用既有條目 [[專一敬拜]]（同名／字面對應）

## 各人行自己眼中看為正的事（主題）
query:
- 待建立詞：各人行自己眼中看為正的事
- 出現位置：申命記 第13章
- 候選類型：主題
- 本章上下文：v17「行耶和華─你神眼中看為正的事」，與申12:8 的「各人行自己眼中看為正的事」、申12:25、28 的「耶和華眼中看為正」是同一組用語；本章把它放在處置拜偶像之城的收尾
- 經文用詞：眼中看為正的事

字面解析：對上既有「各人行自己眼中看為正的事」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 各人行自己眼中看為正的事 | 0.724 | link_folder/主題/各人行自己眼中看為正的事.md |
| 2 | 不隨從己心眼目行邪淫與成為聖潔 | 0.517 | link_folder/神學/不隨從己心眼目行邪淫與成為聖潔.md |
| 3 | 遵行 | 0.504 | link_folder/原文/遵行.md |
| 4 | 不能看不能聽不能吃不能聞的神 | 0.491 | link_folder/主題/不能看不能聽不能吃不能聞的神.md |
| 5 | 不以貌取人 | 0.491 | link_folder/原文/不以貌取人.md |

判定：✅ 建議使用既有條目 [[各人行自己眼中看為正的事]]（同名／字面對應）

## 求問與訪問同一個字（da.rash）（原文）
query:
- 待建立詞：求問與訪問同一個字（da.rash）
- 出現位置：申命記 第13章
- 候選類型：原文
- 本章上下文：v14「探聽」STEP 為 ve./da.rash.Ta（H1875，da.rash: to seek），與申12:5「求問」tid.re.Shu、申12:30「訪問」tid.Rosh 同一個字；申12 那兩處是向神求問與向偶像打聽的對比，本章則是查證傳聞的第一個動作

字面解析：對上既有「求問與訪問同一個字（da.rash）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 求問與訪問同一個字（da.rash） | 0.804 | link_folder/原文/求問與訪問同一個字（da.rash）.md |
| 2 | 探聽查究細細地訪問（da.rash、cha.qar、sha.al） | 0.696 | link_folder/原文/探聽查究細細地訪問（da.rash、cha.qar、sha.al）.md |
| 3 | 盡心盡性尋求（ba.qash、da.rash） | 0.496 | link_folder/原文/盡心盡性尋求（ba.qash、da.rash）.md |
| 4 | 眷顧（da.rash） | 0.492 | link_folder/原文/眷顧（da.rash）.md |
| 5 | 以色列啊你要聽（sha.ma） | 0.478 | link_folder/原文/以色列啊你要聽（sha.ma）.md |

判定：✅ 建議使用既有條目 [[求問與訪問同一個字（da.rash）]]（同名／字面對應）

## 殺盡米甸人的道德難題（解經爭議）
query:
- 待建立詞：殺盡米甸人的道德難題
- 出現位置：申命記 第13章
- 候選類型：解經爭議
- 本章上下文：v15-17 命令用刀殺盡拜偶像之城的居民與牲畜、燒盡財物。GT《申命記串珠聖經註釋》說整座城都該被摧毀，如同迦南地的城邑一樣；GT《聖經精讀本》說這樣的規定表明離棄神而追隨偶像是何等可怕的罪惡，並說在預表天國的迦南決不容忍任何罪的因素存在

字面解析：對上既有「殺盡米甸人的道德難題」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 殺盡米甸人的道德難題 | 0.728 | link_folder/解經爭議/殺盡米甸人的道德難題.md |
| 2 | 迦南滅絕命令的歷史範圍 | 0.592 | link_folder/解經爭議/迦南滅絕命令的歷史範圍.md |
| 3 | 滅絕 | 0.592 | link_folder/原文/滅絕.md |
| 4 | 拆毀偶像律例 | 0.577 | link_folder/事件/拆毀偶像律例.md |
| 5 | 米甸人為何被追討而摩押人沒有 | 0.576 | link_folder/解經爭議/米甸人為何被追討而摩押人沒有.md |

判定：✅ 建議使用既有條目 [[殺盡米甸人的道德難題]]（同名／字面對應）

## 亞伯拉罕之約（神學）
query:
- 待建立詞：亞伯拉罕之約
- 出現位置：申命記 第13章
- 候選類型：神學
- 本章上下文：v17「照他向你列祖所起的誓使你人數增多」，STEP 為 ve./hir.Be./kha（H7235A，ra.vah: to multiply）＋nish.Ba'（H7650，sha.va: to swear）。BH 把這句接回神應許亞伯拉罕後裔繁多（創12:2、15:5）；KC 說滅城會損失人口，但這個順服的舉動連著神必再使他們增多的應許

字面解析：對上既有「亞伯拉罕之約」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 亞伯拉罕之約 | 0.650 | link_folder/神學/亞伯拉罕之約.md |
| 2 | 神堅定與亞伯拉罕的約 | 0.637 | link_folder/主題/神堅定與亞伯拉罕的約.md |
| 3 | 亞伯拉罕 | 0.626 | link_folder/人物/亞伯拉罕.md |
| 4 | 亞伯拉罕之約的應驗 | 0.622 | link_folder/神學/亞伯拉罕之約的應驗.md |
| 5 | 指著自己起誓 | 0.598 | link_folder/神學/指著自己起誓.md |

判定：✅ 建議使用既有條目 [[亞伯拉罕之約]]（同名／字面對應）

## 候選互查（本章內部，⚠＝彼此相似 ≥ 0.8）
（無 ≥ 門檻的配對）
