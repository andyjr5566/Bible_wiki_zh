<!-- candidate_similarity_meta
schema_version: 1
book: 申命記
chapter: 22
candidate_sha256: 687a19b2dca5a3f5ec1acb59e84b645710a868031fb168b72b9aa05073a9cafc
candidate_identity_sha256: b3a993257e78cdbf9ba2cd1986e0d57d70f2012623130adf9de00efbc81dcf02
embedding_model: nvidia/nemotron-3-embed-1b
embedding_index_fingerprint: 10e21fa597ffed08
link_index_sha256: fd440dead52fe569b637606b8db0b5b77c7ff234cdb036a5130678aaa98bf388
homonyms_sha256: b8d042ea4f51253052128b2b289befdcf00b53c88237b67050f3252242c41ab8
rerank_model: nvidia/llama-nemotron-rerank-vl-1b-v2:free
rerank_policy_version: 2026.08.4
calibration_sha256: f63b1218023371bbbece396422aa7a02025bba0da119b49cae75232755734211
rerank_status: success
rerankable_candidates: 7
rerank_attempted: 7
rerank_succeeded: 7
rerank_retrieve_top_k: 20
rerank_score_observed: 0.009-0.379
-->

# 候選語義近鄰報告：申命記 第22章

- 檢索模型：nvidia/nemotron-3-embed-1b｜重排模型：nvidia/llama-nemotron-rerank-vl-1b-v2:free（未校準/保守模式）｜全庫 3029 條
- 規則說明：字面確切匹配直接通過；其餘候選先檢索 Top 20 名再由 Reranker 重排，取前 5 名顯示。
  治理優先：同名歧義（D類）與分類不相容永遠標 ⚠。
  重排模型未校準時，⚠ 由檢索相似度規則（≥0.50 且 top-1 非同實體）決定，重排名次只當附加證據。
  字面解析：列 resolver 實際比對結果——標「請確認」者務必人工核實。

## 愛鄰舍與仇敵（主題）
query:
- 待建立詞：愛鄰舍與仇敵
- 出現位置：申命記 第22章
- 候選類型：主題
- 本章上下文：v1-4 三次「不可佯為不見」。CT 話中之光：「『弟兄』指以色列人，但神百姓憐恤的對象不但是弟兄，也包括仇敵(出二十三4-5；太五44)」；GT《啟導本》：「1～4節的例也見《出埃及記》二十三4～5。這是將守望相助的精神推廣擴大到整個社會，連對待仇敵也應如此」；KC：「What applies in the case of an enemy (Exo 23:4), applies all the more to a brother.」
- 經文用詞：不可佯為不見

字面解析：對上既有「愛鄰舍與仇敵」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 愛鄰舍與仇敵 | 0.755 | link_folder/主題/愛鄰舍與仇敵.md |
| 2 | 愛仇敵律例 | 0.728 | link_folder/事件/愛仇敵律例.md |
| 3 | 出23：4-5愛仇敵律例 | 0.702 | link_folder/解經爭議/出23：4-5愛仇敵律例.md |
| 4 | 不可心裡恨弟兄總要指摘鄰舍 | 0.643 | link_folder/主題/不可心裡恨弟兄總要指摘鄰舍.md |
| 5 | 太5：44 | 0.616 | link_folder/互文/太5：44.md |

判定：✅ 建議使用既有條目 [[愛鄰舍與仇敵]]（同名／字面對應）

## 可憎的物（to.e.vah）（原文）
query:
- 待建立詞：可憎的物（to.e.vah）
- 出現位置：申命記 第22章
- 候選類型：原文
- 本章上下文：v5「因為這樣行都是耶和華─你神所憎惡的」。STEP：תוֹעֲבַת to.'a.Vat（H8441，to.e.vah: abomination）。BH：「The use of the word "detestable" indicates the seriousness with which God views the violation of His created order.」
- 經文用詞：所憎惡的

字面解析：對上既有「可憎的物（to.e.vah）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 可憎的物（to.e.vah） | 0.672 | link_folder/原文/可憎的物（to.e.vah）.md |
| 2 | 忌邪（嫉妒） | 0.501 | link_folder/原文/忌邪（嫉妒）.md |
| 3 | 褻瀆（cha.lal） | 0.493 | link_folder/原文/褻瀆（cha.lal）.md |
| 4 | 神厭惡以色列的難題（利26：30與26：44的張力） | 0.493 | link_folder/解經爭議/神厭惡以色列的難題（利26：30與26：44的張力）.md |
| 5 | 所多瑪罪惡的呼喊 | 0.484 | link_folder/原文/所多瑪罪惡的呼喊.md |

判定：✅ 建議使用既有條目 [[可憎的物（to.e.vah）]]（同名／字面對應）

## 分別為聖（神學）
query:
- 待建立詞：分別為聖
- 出現位置：申命記 第22章
- 候選類型：神學
- 本章上下文：v9「都要充公」。STEP：תִּקְדַּשׁ tik.Dash（H6942I，qa.dash: to consecrate: forfeit）。GT《申命記串珠聖經註釋》：「「充公」：原是「成聖」：指交去聖所。」
- 經文用詞：充公

字面解析：對上既有「分別為聖」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 聖潔 | 0.575 | link_folder/神學/聖潔.md |
| 2 | 分別為聖 | 0.569 | link_folder/神學/分別為聖.md |
| 3 | 褻瀆（cha.lal） | 0.568 | link_folder/原文/褻瀆（cha.lal）.md |
| 4 | 聖物 | 0.566 | link_folder/主題/聖物.md |
| 5 | 你們要聖潔因為我是聖潔的 | 0.563 | link_folder/神學/你們要聖潔因為我是聖潔的.md |

判定：✅ 建議使用既有條目 [[分別為聖]]（同名／字面對應）

## 不可使異類混雜（牲畜種子衣料）（主題）
query:
- 待建立詞：不可使異類混雜（牲畜種子衣料）
- 出現位置：申命記 第22章
- 候選類型：主題
- 本章上下文：v9-11 三道禁令與利19:19 同型。CT：「本段(9~11節)經文的用意，乃在維持信仰的純潔，不可兼容併蓄(參利十九19註解)」；GT《啟導本》：「兩種種子放在一道生長，可破壞品種的純正」；STEP v9：כִּלְאָיִם kil.'A.yim（H3610，kil.a.yim: mixture）。
- 經文用詞：兩樣種子、兩樣攙雜料

字面解析：對上既有「不可使異類混雜（牲畜種子衣料）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 不可使異類混雜（牲畜種子衣料） | 0.797 | link_folder/主題/不可使異類混雜（牲畜種子衣料）.md |
| 2 | 異樣的香與香壇的禁令 | 0.507 | link_folder/主題/異樣的香與香壇的禁令.md |
| 3 | 古代近東人獸性行為 | 0.477 | link_folder/背景/古代近東人獸性行為.md |
| 4 | 奉獻牲畜不可更換條例 | 0.476 | link_folder/主題/奉獻牲畜不可更換條例.md |
| 5 | 言語的混亂 | 0.471 | link_folder/主題/言語的混亂.md |

判定：✅ 建議使用既有條目 [[不可使異類混雜（牲畜種子衣料）]]（同名／字面對應）

## 潔淨與不潔淨（神學）
query:
- 待建立詞：潔淨與不潔淨
- 出現位置：申命記 第22章
- 候選類型：神學
- 本章上下文：v10「不可並用牛、驢耕地」。CT：「牛是潔淨的牲畜，驢是不潔淨的牲畜(參申十四4~8)」；BH：「The ox is a clean animal according to Levitical law (Leviticus 11:3), while the donkey is considered unclean (Leviticus 11:4).」；KC：「An ox is a clean animal and a donkey is an unclean animal.」
- 經文用詞：牛、驢

字面解析：對上既有「潔淨與不潔淨」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 潔淨與不潔淨 | 0.676 | link_folder/神學/潔淨與不潔淨.md |
| 2 | 分蹄倒嚼（潔淨走獸的判準） | 0.606 | link_folder/主題/分蹄倒嚼（潔淨走獸的判準）.md |
| 3 | 潔淨與不潔淨的早期區分 | 0.601 | link_folder/主題/潔淨與不潔淨的早期區分.md |
| 4 | 公牛犢 | 0.585 | link_folder/主題/公牛犢.md |
| 5 | 驢用羊羔代贖 | 0.579 | link_folder/原文/驢用羊羔代贖.md |

判定：✅ 建議使用既有條目 [[潔淨與不潔淨]]（同名／字面對應）

## 衣服邊的繸子與藍細帶子（文化）
query:
- 待建立詞：衣服邊的繸子與藍細帶子
- 出現位置：申命記 第22章
- 候選類型：文化
- 本章上下文：v12「你要在所披的外衣上四圍做繸子」。STEP：גְּדִלִים ge.di.Lim（H1434，ge.dil: tassel）。GT《啟導本》：「在外衣上作“繸子”，有提醒穿的人常守律法的作用(民十五38～39)，也是民族服裝的一個特色。」BH 把這做法追到民15:37-41。
- 經文用詞：繸子

字面解析：對上既有「衣服邊的繸子與藍細帶子」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 衣服邊的繸子與藍細帶子 | 0.789 | link_folder/文化/衣服邊的繸子與藍細帶子.md |
| 2 | 外袍（以弗得的外袍） | 0.520 | link_folder/主題/外袍（以弗得的外袍）.md |
| 3 | 腰帶（繡花腰帶） | 0.517 | link_folder/主題/腰帶（繡花腰帶）.md |
| 4 | 藍色鈕扣 | 0.496 | link_folder/主題/藍色鈕扣.md |
| 5 | 記號與經文 | 0.483 | link_folder/原文/記號與經文.md |

判定：✅ 建議使用既有條目 [[衣服邊的繸子與藍細帶子]]（同名／字面對應）

## 流無辜血的罪（神學）
query:
- 待建立詞：流無辜血的罪
- 出現位置：申命記 第22章
- 候選類型：神學
- 本章上下文：v8「免得有人從房上掉下來，流血的罪就歸於你家」。STEP：דָּמִים da.Mim（H1818，dam: blood，複數）。BH：「Bloodguilt refers to the responsibility for shedding innocent blood, a serious offense in biblical law.」GT《啟導本》：「“流血的罪”看十九9；二十一1注。」
- 經文用詞：流血的罪

字面解析：對上既有「流無辜血的罪」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 流無辜血的罪 | 0.667 | link_folder/神學/流無辜血的罪.md |
| 2 | 血 | 0.603 | link_folder/主題/血.md |
| 3 | 他的血要歸到他身上 | 0.596 | link_folder/原文/他的血要歸到他身上.md |
| 4 | 來9：18-22 | 0.572 | link_folder/互文/來9：18-22.md |
| 5 | 血的尊重 | 0.552 | link_folder/神學/血的尊重.md |

判定：✅ 建議使用既有條目 [[流無辜血的罪]]（同名／字面對應）

## 當孝敬父母（神學）
query:
- 待建立詞：當孝敬父母
- 出現位置：申命記 第22章
- 候選類型：神學
- 本章上下文：v7「這樣你就可以享福，日子得以長久」。KC：「By the addition "that it may be well with you and that you may prolong your days", there is a connection between this regulation and the fifth commandment, that of honoring father and mother. A similar addition is given to the fifth commandment (Deu 5:16).」BH：「It is reminiscent of the fifth commandment in Exodus 20:12, which promises long life for honoring one's parents.」
- 經文用詞：日子得以長久

字面解析：對上既有「當孝敬父母」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 當孝敬父母 | 0.700 | link_folder/神學/當孝敬父母.md |
| 2 | 出20：12 | 0.594 | link_folder/互文/出20：12.md |
| 3 | 弗6：2-3 | 0.553 | link_folder/互文/弗6：2-3.md |
| 4 | 十誡中的兩條正面誡命 | 0.529 | link_folder/主題/十誡中的兩條正面誡命.md |
| 5 | 尊敬老人 | 0.523 | link_folder/主題/尊敬老人.md |

判定：✅ 建議使用既有條目 [[當孝敬父母]]（同名／字面對應）

## 以色列的長老（文化）
query:
- 待建立詞：以色列的長老
- 出現位置：申命記 第22章
- 候選類型：文化
- 本章上下文：v15-18 長老受理貞潔憑據的訴訟並執行懲治。BH：「The city elders were respected leaders and judges within the community, often sitting at the city gate to conduct legal and civic matters.」GT《啟導本》：「在希伯來人社會中，女子的爭訟都由父親或丈夫出面擔負責任。」
- 經文用詞：長老

字面解析：對上既有「以色列的長老」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 以色列的長老 | 0.664 | link_folder/文化/以色列的長老.md |
| 2 | 以色列的眾長老 | 0.605 | link_folder/人物/以色列的眾長老.md |
| 3 | 城門口公共場合 | 0.538 | link_folder/歷史/城門口公共場合.md |
| 4 | 曠野審判制度 | 0.521 | link_folder/背景/曠野審判制度.md |
| 5 | 女子在以色列社會的法律地位 | 0.510 | link_folder/背景/女子在以色列社會的法律地位.md |

判定：✅ 建議使用既有條目 [[以色列的長老]]（同名／字面對應）

## 城門口公共場合（歷史）
query:
- 待建立詞：城門口公共場合
- 出現位置：申命記 第22章
- 候選類型：歷史
- 本章上下文：v15「帶到本城門長老那裡」、v24「把這二人帶到本城門」。BH：「The city gate was not only a physical entry point but also a central place for public gatherings, legal proceedings, and commerce.」並引 得4:1-2、箴31:23。
- 經文用詞：本城門

字面解析：對上既有「城門口公共場合」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 城門口公共場合 | 0.691 | link_folder/歷史/城門口公共場合.md |
| 2 | 城門口交易 | 0.568 | link_folder/文化/城門口交易.md |
| 3 | 會幕門口 | 0.446 | link_folder/地點/會幕門口.md |
| 4 | 基督是門（約10：7） | 0.436 | link_folder/互文/基督是門（約10：7）.md |
| 5 | 帳幕門簾 | 0.416 | link_folder/主題/帳幕門簾.md |

判定：✅ 建議使用既有條目 [[城門口公共場合]]（同名／字面對應）

## 舍客勒（原文）
query:
- 待建立詞：舍客勒
- 出現位置：申命記 第22章
- 候選類型：原文
- 本章上下文：v19「罰他一百舍客勒銀子」、v29「拿五十舍客勒銀子」。CT：「罰款一百舍客勒銀子(參19節)，約折合1150公克重，是女子聘禮身價的兩倍(參29節)」、「『五十舍客勒』約折合575公克」；GT《雷氏研讀本》：「罰款約相等於四十八安士(1.1千克)的銀子。」
- 經文用詞：舍客勒

字面解析：對上既有「舍客勒」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 舍客勒 | 0.683 | link_folder/原文/舍客勒.md |
| 2 | 會幕金銀銅重量的換算分歧 | 0.582 | link_folder/解經爭議/會幕金銀銅重量的換算分歧.md |
| 3 | 聖所的平（捨客勒標準） | 0.577 | link_folder/文化/聖所的平（捨客勒標準）.md |
| 4 | 贖銀五舍客勒 | 0.562 | link_folder/文化/贖銀五舍客勒.md |
| 5 | 半舍客勒（贖罪銀） | 0.560 | link_folder/原文/半舍客勒（贖罪銀）.md |

判定：✅ 建議使用既有條目 [[舍客勒]]（同名／字面對應）

## 不可姦淫（神學）
query:
- 待建立詞：不可姦淫
- 出現位置：申命記 第22章
- 候選類型：神學
- 本章上下文：v22「就要將姦夫淫婦一併治死」。GT《啟導本》：「希伯來人執行“不可姦淫”(出二十14)的誡命，只適用於男子與有夫之婦或與已受聘(訂婚)的女子行淫(利二十10；申二十二22～24,28～29)。」BH 也把本節接回出20:14。
- 經文用詞：姦夫淫婦

字面解析：對上既有「不可姦淫」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 不可姦淫 | 0.714 | link_folder/神學/不可姦淫.md |
| 2 | 姦淫 | 0.677 | link_folder/原文/姦淫.md |
| 3 | 出20：14 | 0.672 | link_folder/互文/出20：14.md |
| 4 | 不可與男人苟合可憎惡的事 | 0.616 | link_folder/主題/不可與男人苟合可憎惡的事.md |
| 5 | 不可辱沒女兒使她為娼妓 | 0.596 | link_folder/主題/不可辱沒女兒使她為娼妓.md |

判定：✅ 建議使用既有條目 [[不可姦淫]]（同名／字面對應）

## 引誘處女的律例（事件）
query:
- 待建立詞：引誘處女的律例
- 出現位置：申命記 第22章
- 候選類型：事件
- 本章上下文：v28-29 與出22:16-17 是同一組案例的兩面。CT 話中之光：「男子沒有不娶的權力，但女子卻有拒絕的權力(出二十二16-17)」；GT《啟導本》列出污辱未許配女子的三項後果並註「女家若不許女兒嫁他，不可索還聘禮(出二十二16～17)」；KC 也整段引出22:16-17 作補充。
- 經文用詞：沒有許配人的處女

字面解析：對上既有「引誘處女的律例」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 引誘處女的律例 | 0.751 | link_folder/事件/引誘處女的律例.md |
| 2 | 申22：28-29 | 0.647 | link_folder/互文/申22：28-29.md |
| 3 | 出20：14 | 0.640 | link_folder/互文/出20：14.md |
| 4 | 申22：23-24 | 0.597 | link_folder/互文/申22：23-24.md |
| 5 | 聘禮（mohar） | 0.593 | link_folder/原文/聘禮（mohar）.md |

判定：✅ 建議使用既有條目 [[引誘處女的律例]]（同名／字面對應）

## 不可同日宰母和子（主題）
query:
- 待建立詞：不可同日宰母和子
- 出現位置：申命記 第22章
- 候選類型：主題
- 本章上下文：v6「母鳥伏在雛上或在蛋上」。GT《聖經精讀本──申命記註解》註本節時把根據放在同一組律例上：「雖然律法賦予人掌管自然界的特權,但人總要根據神的慈愛與憐憫、維持、保護自然界(出23:19;利22:28)。」利22:28 正是不可同日宰母和子的條例。
- 經文用詞：母鳥

字面解析：對上既有「不可同日宰母和子」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 不可同日宰母和子 | 0.726 | link_folder/主題/不可同日宰母和子.md |
| 2 | 耶5：28 | 0.502 | link_folder/互文/耶5：28.md |
| 3 | 出23：19不可用山羊羔母奶煮山羊羔 | 0.498 | link_folder/解經爭議/出23：19不可用山羊羔母奶煮山羊羔.md |
| 4 | 申22：8 | 0.487 | link_folder/互文/申22：8.md |
| 5 | 生養眾多與治理 | 0.487 | link_folder/主題/生養眾多與治理.md |

判定：✅ 建議使用既有條目 [[不可同日宰母和子]]（同名／字面對應）

## 男女不可易服的條例（主題）
query:
- 待建立詞：男女不可易服的條例
- 出現位置：申命記 第22章
- 候選類型：主題
- 本章上下文：v5「婦女不可穿戴男子所穿戴的，男子也不可穿婦女的衣服」。STEP：כְלִי khe.li（H3627，ke.li: article/utensil）與 שִׂמְלַת sim.Lat（H8071，sim.lah: mantle）。GT 艾基斯《舊約聖經難題彙編》整篇討論 keli 與 simlah 的字義範圍；GT《雷氏研讀本》：「在當時的社會，男性和女性的服裝十分相似」；GT《啟導本》講迦南異教儀式男女易服；KC 談創造次序與公開的表現。
- 經文用詞：婦女不可穿戴男子所穿戴的

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 古代近東人獸性行為 | 0.453 | 0.145 | link_folder/背景/古代近東人獸性行為.md |
| 2 | 女人行經的不潔條例 | 0.477 | 0.108 | link_folder/主題/女人行經的不潔條例.md |
| 3 | 不可辱沒女兒使她為娼妓 | 0.472 | 0.098 | link_folder/主題/不可辱沒女兒使她為娼妓.md |
| 4 | 不可使異類混雜（牲畜種子衣料） | 0.529 | 0.092 | link_folder/主題/不可使異類混雜（牲畜種子衣料）.md |
| 5 | 不可效法外邦喪儀習俗（剃髮劃身刺花紋） | 0.462 | 0.087 | link_folder/主題/不可效法外邦喪儀習俗（剃髮劃身刺花紋）.md |

rerank_margin: 0.037 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=主題 vs 條目=背景），若確為同實體請確認是否改用 [[古代近東人獸性行為]]

## 放母取雛的鳥窩條例（主題）
query:
- 待建立詞：放母取雛的鳥窩條例
- 出現位置：申命記 第22章
- 候選類型：主題
- 本章上下文：v6-7「不可連母帶雛一併取去。總要放母，只可取雛」。STEP：קַן kan（H7064，qen: nest）、צִפּוֹר tzi.Por（H6833，tsip.por: bird）、שַׁלֵּחַ תְּשַׁלַּח sha.Le.ach te.sha.Lach（H7971H，不定詞加強式）。CT：「取雛不取母，使生命可以延續」；GT《串珠》：「人不可以滅絕神在自然界中所造之物，須保護自然資源」；KC 從母性感情讀；BH 講永續與憐憫。
- 經文用詞：不可連母帶雛一併取去、總要放母

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 不可同日宰母和子 | 0.547 | 0.379 | link_folder/主題/不可同日宰母和子.md |
| 2 | 雛鴿 | 0.430 | 0.290 | link_folder/主題/雛鴿.md |
| 3 | 保護弱者的律例 | 0.422 | 0.274 | link_folder/事件/保護弱者的律例.md |
| 4 | 田角拾穗顧念窮人的條例 | 0.421 | 0.268 | link_folder/主題/田角拾穗顧念窮人的條例.md |
| 5 | 才生祭牲七天當跟母第八天蒙悅納 | 0.416 | 0.256 | link_folder/主題/才生祭牲七天當跟母第八天蒙悅納.md |

rerank_margin: 0.089 (Top1 - Top2)
判定：⚠ 相似度居中（0.50 ≤ 0.547 < 0.70），最近鄰為 [[不可同日宰母和子]]——此區間真對應與無對應分數重疊，需逐一人工判斷（重排模型 nvidia/llama-nemotron-rerank-vl-1b-v2:free 未校準，上表名次僅供參考）

## 房上安欄杆的條例（主題）
query:
- 待建立詞：房上安欄杆的條例
- 出現位置：申命記 第22章
- 候選類型：主題
- 本章上下文：v8「你若建造房屋，要在房上的四圍安欄杆」。STEP：מַעֲקֶה ma.'a.Keh（H4624，ma.a.qeh: parapet）、גַּג ga.Ge（H1406，gag: roof）。CT：「古時以色列人的房頂是平的，屋外有梯階可上房頂，供人休憩(參書二6)」；GT《精讀本》：「據猶大傳承,此時欄杆的高度當約有1米左右」；KC 讀成對新人的照顧；BH 講 bloodguilt。
- 經文用詞：安欄杆

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 申22：8 | 0.527 | 0.103 | link_folder/互文/申22：8.md |
| 2 | 房屋大痲瘋的診斷與潔淨條例 | 0.433 | 0.035 | link_folder/主題/房屋大痲瘋的診斷與潔淨條例.md |
| 3 | 古代近東的圍城戰與營壘 | 0.431 | 0.033 | link_folder/背景/古代近東的圍城戰與營壘.md |
| 4 | 田角拾穗顧念窮人的條例 | 0.431 | 0.027 | link_folder/主題/田角拾穗顧念窮人的條例.md |
| 5 | 免服兵役的四種人 | 0.440 | 0.023 | link_folder/主題/免服兵役的四種人.md |

rerank_margin: 0.068 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=主題 vs 條目=互文），若確為同實體請確認是否改用 [[申22：8]]

## 貞潔的憑據（文化）
query:
- 待建立詞：貞潔的憑據
- 出現位置：申命記 第22章
- 候選類型：文化
- 本章上下文：v14-20 反覆出現「貞潔的憑據」。STEP：בְּתוּלִים be.tu.Lim（H1331，be.tu.lim: virginity，複數）。GT《啟導本》給了兩種說法：「“貞潔的憑據”可指初夜的落紅。也有人說是指結婚前仍有月事，以證明結婚時並未懷孕，確屬童貞」；GT《精讀本》：「就古代猶大的風俗而言,這是女子可證明其貞潔的唯一證據」；BH：「a cloth with bloodstains from the wedding night, which was kept as evidence of the bride's virginity」。
- 經文用詞：貞潔的憑據

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 聘禮（mohar） | 0.449 | 0.302 | link_folder/原文/聘禮（mohar）.md |
| 2 | 古代近東婚姻習俗 | 0.445 | 0.242 | link_folder/歷史/古代近東婚姻習俗.md |
| 3 | 自潔 | 0.457 | 0.241 | link_folder/神學/自潔.md |
| 4 | 古代近東聘禮制度 | 0.455 | 0.237 | link_folder/背景/古代近東聘禮制度.md |
| 5 | 女人行經的不潔條例 | 0.499 | 0.224 | link_folder/主題/女人行經的不潔條例.md |

rerank_margin: 0.059 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=文化 vs 條目=原文），若確為同實體請確認是否改用 [[聘禮（mohar）]]

## 誣告妻子不貞的三種懲罰（主題）
query:
- 待建立詞：誣告妻子不貞的三種懲罰
- 出現位置：申命記 第22章
- 候選類型：主題
- 本章上下文：v18-19。GT《精讀本》：「記錄了誣告妻子尚未出嫁時有失貞潔的丈夫所要受到的三種刑罰」，即公開杖刑、罰一百舍客勒、終身剝奪休妻權；CT 逐項列同樣三點；GT《雷氏研讀本》：「“懲治他”的方法是鞭打他四十下(比較二五3)」；BH：「This lifelong commitment was a safeguard against further injustice.」
- 經文用詞：將醜名加在他身上、終身不可休他

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 引誘處女的律例 | 0.472 | 0.040 | link_folder/事件/引誘處女的律例.md |
| 2 | 疑恨條例 | 0.471 | 0.033 | link_folder/事件/疑恨條例.md |
| 3 | 祭司不可娶被玷污的婦人為妻 | 0.469 | 0.028 | link_folder/主題/祭司不可娶被玷污的婦人為妻.md |
| 4 | 以色列刑罰的節制與程序保障 | 0.477 | 0.026 | link_folder/背景/以色列刑罰的節制與程序保障.md |
| 5 | 婢女行淫的贖愆祭條例 | 0.530 | 0.026 | link_folder/主題/婢女行淫的贖愆祭條例.md |

rerank_margin: 0.006 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=主題 vs 條目=事件），若確為同實體請確認是否改用 [[引誘處女的律例]]

## 城裡與田野對強姦案的判定（主題）
query:
- 待建立詞：城裡與田野對強姦案的判定
- 出現位置：申命記 第22章
- 候選類型：主題
- 本章上下文：v23-27。GT《精讀本》：「此律例規定了若已許配人的女子遭到強姦時,可根據是在城內(23,24節)還是在城外(25-27節)來判斷是有罪還是無罪」；CT：「『在城裡』指人煙眾多的場所；『沒有喊叫』指默許事情發生」；KC：「In the city, someone who is engaged is not in as great a danger.」；BH 把 v26 的類比讀成「This comparison to murder underscores the severity of the crime and the innocence of the victim.」
- 經文用詞：雖在城裡卻沒有喊叫、在田野遇見

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 無主命案的折頸母牛犢條例 | 0.432 | 0.125 | link_folder/主題/無主命案的折頸母牛犢條例.md |
| 2 | 城門口公共場合 | 0.424 | 0.053 | link_folder/歷史/城門口公共場合.md |
| 3 | 謀殺與誤殺的區分 | 0.435 | 0.052 | link_folder/神學/謀殺與誤殺的區分.md |
| 4 | 司法公義 | 0.401 | 0.049 | link_folder/神學/司法公義.md |
| 5 | 埋伏 | 0.421 | 0.048 | link_folder/原文/埋伏.md |

rerank_margin: 0.072 (Top1 - Top2)
判定：🆕 建議建立新條目（最相似條目僅 0.460 < 0.50）（重排模型 nvidia/llama-nemotron-rerank-vl-1b-v2:free 未校準，上表名次僅供參考）

## 衣襟（ka.naph）（原文）
query:
- 待建立詞：衣襟（ka.naph）
- 出現位置：申命記 第22章
- 候選類型：原文
- 本章上下文：v30「不可掀開他父親的衣襟」與 v12「外衣上四圍」在 STEP 是同一個字：כְּנַף ke.Naf 與 כַּנְפוֹת kan.Fot，都是 H3671（ka.naph: wing）。CT：「『掀開他父親的衣襟』指侵犯父親的婚姻關係(參得三9)」；GT《啟導本》：「男子把衣襟覆在女子身上象徵婚姻關係(得三9；結十六8)」。
- 經文用詞：衣襟、四圍

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 衣裳（外袍） | 0.516 | 0.055 | link_folder/原文/衣裳（外袍）.md |
| 2 | 彩衣 | 0.524 | 0.050 | link_folder/文化/彩衣.md |
| 3 | 不可使異類混雜（牲畜種子衣料） | 0.452 | 0.044 | link_folder/主題/不可使異類混雜（牲畜種子衣料）.md |
| 4 | 古代近東當頭制度 | 0.444 | 0.040 | link_folder/背景/古代近東當頭制度.md |
| 5 | 聖衣（祭司聖服） | 0.471 | 0.038 | link_folder/主題/聖衣（祭司聖服）.md |

rerank_margin: 0.005 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=原文 vs 條目=文化），若確為同實體請確認是否改用 [[彩衣]]（重排模型 nvidia/llama-nemotron-rerank-vl-1b-v2:free 未校準，上表名次僅供參考）

## 候選互查（本章內部，⚠＝彼此相似 ≥ 0.8）
（無 ≥ 門檻的配對）
