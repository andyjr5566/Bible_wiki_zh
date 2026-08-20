<!-- candidate_similarity_meta
schema_version: 1
book: 民數記
chapter: 1
candidate_sha256: 2ef25d8d410c1d232a0e7957df002325d0d45ef29b0e30166cb48489d795984b
embedding_model: nvidia/nemotron-3-embed-1b
embedding_index_fingerprint: c2abf8934419fa2d
link_index_sha256: 63feb9a64e3fb5e516c6e7a6352ff04131187d149984c1f419d4c256c2171684
homonyms_sha256: b8d042ea4f51253052128b2b289befdcf00b53c88237b67050f3252242c41ab8
rerank_model: nvidia/llama-nemotron-rerank-vl-1b-v2:free
rerank_policy_version: 2026.08.4
calibration_sha256: 337500e601e3a204c71a4bbe077172c48c165c2ea9ffe38c5d4425363d899411
rerank_status: not_needed
rerankable_candidates: 0
rerank_attempted: 0
rerank_succeeded: 0
rerank_retrieve_top_k: 20
rerank_score_observed: none
-->

# 候選語義近鄰報告：民數記 第1章

- 檢索模型：nvidia/nemotron-3-embed-1b｜重排模型：nvidia/llama-nemotron-rerank-vl-1b-v2:free（未校準/保守模式）｜全庫 2630 條
- 規則說明：字面確切匹配直接通過；其餘候選先檢索 Top 20 名再由 Reranker 重排，取前 5 名顯示。
  治理優先：同名歧義（D類）與分類不相容永遠標 ⚠。
  重排模型未校準時，⚠ 由檢索相似度規則（≥0.50 且 top-1 非同實體）決定，重排名次只當附加證據。
  字面解析：列 resolver 實際比對結果——標「請確認」者務必人工核實。

## 會幕（帳幕整體）（主題）
query:
- 待建立詞：會幕（帳幕整體）
- 出現位置：民數記 第1章
- 候選類型：主題
- 本章上下文：民1:1「耶和華在西乃的曠野、會幕中曉諭摩西說」；全章以會幕為中心，利未人四圍安營守護（v50-53）。民1:50,53 特別稱「法櫃的帳幕」（tabernacle of the testimony），強調見證的面向——「法櫃」指藏有十誡法版的約櫃（GT啟導本），「法櫃的帳幕」指整個會幕，因法櫃是帳幕中最要緊的聖器（GT丁良才）；「其中的器具」指陳設餅桌、燈檯、燔祭壇等附屬用品（GT精讀本），「屬乎帳幕的」指橛子和繩子等（GT精讀本）。CT：會幕已建立一個月（出40:17），這一個月期間大概就是摩西寫《利未記》的時候；「會幕中」意指神和摩西面對面說話。GT（丁良才）：立會幕後有十一件事依序發生——(1)立會幕（正月初一），(2)神曉諭獻祭禮節（利1-7），(3)摩西膏抹帳幕使之成聖（利8:10），(4)亞倫與子承受聖職七日（利8），(5)祭司初次供職第八天（利9），(6)拿答亞比戶被火焚燒（利10），(7)十二支派首領奉獻禮物（民7），(8)神宣示其餘律例（利11-27），(9)神吩咐守逾越節（民9:1-3），(10)以色列人守逾越節正月十四日（民9:4-5），(11)神命摩西計算民數二月初一日（民1:1）。KC：tabernacle erected one month prior (Exo 40:17); here called "tabernacle of the testimony" — aspect of external testimony; church is pillar and support of truth (1Tim 3:15). BH：Tent of Meeting was central place of worship and God's presence, constructed according to detailed instructions in Exodus 25-31; tabernacle of the Testimony refers to portable sanctuary housing Ark of Covenant containing tablets of the Law; foreshadows Jesus Christ who "tabernacled" among us (John 1:14).
- 經文用詞：法櫃的帳幕、帳幕

字面解析：對上既有「會幕（帳幕整體）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 會幕（帳幕整體） | 0.802 | link_folder/主題/會幕（帳幕整體）.md |
| 2 | 法櫃的帳幕 | 0.745 | link_folder/地點/法櫃的帳幕.md |
| 3 | 摩西的臨時會幕（營外） | 0.697 | link_folder/事件/摩西的臨時會幕（營外）.md |
| 4 | 約櫃 | 0.693 | link_folder/主題/約櫃.md |
| 5 | 法版 | 0.688 | link_folder/原文/法版.md |

判定：✅ 建議使用既有條目 [[會幕（帳幕整體）]]（同名／字面對應）

## 西乃的曠野（地點）
query:
- 待建立詞：西乃的曠野
- 出現位置：民數記 第1章
- 候選類型：地點
- 本章上下文：民1:1「耶和華在西乃的曠野」；民1:19「在西乃的曠野數點他們」。CT：西乃原文字義「多刺的」。GT（背景註釋）：西乃的曠野指以色列安營之山四周的曠野地帶。BH：Wilderness of Sinai is where Israelites camped after leaving Egypt and received the Law.

字面解析：對上既有「西乃的曠野」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 西乃的曠野 | 0.827 | link_folder/地點/西乃的曠野.md |
| 2 | 以色列到達西乃山 | 0.735 | link_folder/事件/以色列到達西乃山.md |
| 3 | 汛的曠野 | 0.725 | link_folder/地點/汛的曠野.md |
| 4 | 西乃 | 0.718 | link_folder/地點/西乃.md |
| 5 | 西乃山 | 0.661 | link_folder/地點/西乃山.md |

判定：✅ 建議使用既有條目 [[西乃的曠野]]（同名／字面對應）

## 摩西（人物）
query:
- 待建立詞：摩西
- 出現位置：民數記 第1章
- 候選類型：人物
- 本章上下文：全章摩西為神諭接收者與數點執行者。民1:1「耶和華…曉諭摩西說」——CT指出「耶和華曉諭摩西」這樣的模式在本書至少記載了八十次以上，任何屬靈領袖必須經常直接從神得著頭手的話語。CT：摩西立刻遵命沒有遲延（v18「當二月初一日招聚全會眾」）；摩西並非擅自數點以色列人（v19），大衛擅自數點民數則有罪（撒下24:10）。GT（丁良才）：摩西兩次數點民數——初次摩西和亞倫（民1），二次摩西和以利亞撒（民26:1）。GT（難解經文）：摩西五經有明言記載是摩西所寫（民1:1, 33:2），新約多次引用民數記且提到是摩西寫的（徒7:13；林前10:2-8；來3:7-16），基督引用民數記證明摩西在曠野怎樣舉蛇（約3:14；民21:9）。KC：Moses and Aaron together picture of Lord Jesus as Apostle and High Priest (Heb 3:1); Moses and Aaron number together, picture of Christ as King-Priest (Zec 6:13). BH：Moses' role as prophet and leader reflects unique relationship with God — LORD spoke to Moses face to face (Exo 33:11).

字面解析：對上既有「摩西」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 摩西 | 0.775 | link_folder/人物/摩西.md |
| 2 | 摩西上山見神 | 0.684 | link_folder/事件/摩西上山見神.md |
| 3 | 亞倫 | 0.678 | link_folder/人物/亞倫.md |
| 4 | 耶和華的話臨到 | 0.667 | link_folder/神學/耶和華的話臨到.md |
| 5 | 被拒絕的拯救者摩西 | 0.638 | link_folder/互文/被拒絕的拯救者摩西.md |

判定：✅ 建議使用既有條目 [[摩西]]（同名／字面對應）

## 亞倫（人物）
query:
- 待建立詞：亞倫
- 出現位置：民數記 第1章
- 候選類型：人物
- 本章上下文：民1:3「你和亞倫要照他們的軍隊數點」；v17「摩西、亞倫帶著這些按名指定的人」；v44「是摩西、亞倫…所數點的」。CT：亞倫原文字義「帶來光的人」。GT（丁良才）：拿順是亞倫的妻兄（出6:23），也是大衛的先祖（得4:21-20）。KC：Moses and Aaron number together, picture of Christ as King-Priest (Zec 6:13); together they are picture of Lord Jesus called "Apostle and High Priest of our confession" (Heb 3:1). BH：Aaron as high priest, responsible with Moses for organizing the people; census is divinely ordained task highlighting importance of order and structure.

字面解析：對上既有「亞倫」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 亞倫 | 0.662 | link_folder/人物/亞倫.md |
| 2 | 十二族長協助數點 | 0.589 | link_folder/事件/十二族長協助數點.md |
| 3 | 亞倫的祭司譜系 | 0.573 | link_folder/人物/亞倫的祭司譜系.md |
| 4 | 拿順 | 0.568 | link_folder/人物/拿順.md |
| 5 | 數點民數 | 0.558 | link_folder/事件/數點民數.md |

判定：✅ 建議使用既有條目 [[亞倫]]（同名／字面對應）

## 十二支派起源（神學）
query:
- 待建立詞：十二支派起源
- 出現位置：民數記 第1章
- 候選類型：神學
- 本章上下文：全章按十二支派逐一數點（v20-43）。GT（精讀本）：數點人數使以色列從自然群體形成神權國家體制；以色列百姓所要進行的戰爭是以建立神國度為目的的聖戰，神是以色列的元帥。GT（啟導本）：以法蓮與瑪拿西成為兩個正式支派以補「十二」之數，取代了約瑟和利未——雅各在埃及時曾將約瑟的兩個兒子立為自己的兒子（創48:5），利未支派已蒙揀選在會幕中侍奉不列在十二支派當中。GT（背景註釋）：祭司和利未人營地設於聖所四面，其他支派每邊三個安營在外圍形成方形；猶大為眾支派之首領導最重要的東營（聖幕入口朝東），長子流便領導南營，但支派為北營之首（因為但是妾生眾子最長的一個），拉結眾子的支派位於西面、居首的是被立為約瑟長子的以法蓮。BH：twelve tribes descended from sons of Jacob, each with distinct identity and role.

字面解析：對上既有「十二支派起源」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 十二支派起源 | 0.873 | link_folder/神學/十二支派起源.md |
| 2 | 猶大支派 | 0.670 | link_folder/人物/猶大支派.md |
| 3 | 以法蓮 | 0.668 | link_folder/人物/以法蓮.md |
| 4 | 瑪拿西 | 0.647 | link_folder/人物/瑪拿西.md |
| 5 | 利未支派 | 0.646 | link_folder/人物/利未支派.md |

判定：✅ 建議使用既有條目 [[十二支派起源]]（同名／字面對應）

## 以色列人的軍隊（神學）
query:
- 待建立詞：以色列人的軍隊
- 出現位置：民數記 第1章
- 候選類型：神學
- 本章上下文：民1:3「能出去打仗的，你和亞倫要照他們的軍隊數點」；v16「都是以色列軍中的統領」；v52「要照他們的軍隊，各歸本營」。CT：男丁按原文含有頭顱的意思，意指能夠出去打仗、為國家拋頭顱灑熱血的男子；「從二十歲以外，能出去打仗的」表徵生命必須成熟的信徒才能有分於屬靈戰爭——不單要有兒子的身分，還必須是長成的人；「能出去打仗」首先是認清了爭戰的目的，其次是知道爭戰的法則，再次就是熟練爭戰的方法。GT（精讀本）：以色列百姓所要進行的戰爭是以建立神國度為目的的聖戰，而不是單單以掠奪和領土擴張為目的的戰爭；神是以色列的元帥，以色列百姓只要順服神的命令就能獲得勝利；這預表了新約的教會以耶穌為元首與撒但爭戰（弗6:10-17）。GT（啟導本）：凡是20歲以上的男丁都有參加軍隊的義務，畏縮不前視為大罪（參民14；申20）。KC：militant men, not children or elderly; age of twenty is military service age — spiritually means certain maturity needed to serve as warrior in God's army (1Jn 2:13b-14b; cf. 2Tim 2:3-4); whoever is in service is expected to follow orders without contradicting (Lk 7:8); new testament believer is priest (praising God in sanctuary), Levite (serving church), or warrior (standing up for truth when attacked). BH：census was for military purposes; service in Israel's army tied to being part of God's covenant people; spiritual warfare theme echoed in NT (Eph 6:10-18).

字面解析：對上既有「以色列人的軍隊」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 二十歲以外能打仗的 | 0.811 | link_folder/主題/二十歲以外能打仗的.md |
| 2 | 以色列人的軍隊 | 0.776 | link_folder/神學/以色列人的軍隊.md |
| 3 | 數點民數 | 0.618 | link_folder/事件/數點民數.md |
| 4 | 古代近東的人口統計 | 0.617 | link_folder/背景/古代近東的人口統計.md |
| 5 | 十二族長協助數點 | 0.600 | link_folder/事件/十二族長協助數點.md |

判定：✅ 建議使用既有條目 [[以色列人的軍隊]]（同名／字面對應）

## 猶大支派（人物）
query:
- 待建立詞：猶大支派
- 出現位置：民數記 第1章
- 候選類型：人物
- 本章上下文：民1:26-27 猶大支派 74,600 人，人數最多。CT：猶大支派相當特殊，大衛王和其後的猶大國諸王都出自該支派（太1:3,6），甚至主耶穌也是大衛的後裔（羅1:3）。GT（丁良才）：猶大支派人數最多（創49:8），後來成了為首的支派（民2:3, 7:12）。GT（精讀本）：猶大作為利亞的第四個兒子得到神屬靈的祝福，成了領導以色列的屬靈長子（創49:8-12），後來耶穌基督也誕生在猶大支派（太1:2；啟5:5）。GT（背景註釋）：猶大為眾支派之首，領導最重要的東營（聖幕入口朝東）。KC：Judah 74,600, largest tribe. BH：Judah's prominence — tribe of King David and Jesus Christ, "Lion of the tribe of Judah" (Rev 5:5); territory included Jerusalem.

字面解析：對上既有「猶大支派」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 猶大支派 | 0.813 | link_folder/人物/猶大支派.md |
| 2 | 猶大（雅各之子） | 0.656 | link_folder/人物/猶大（雅各之子）.md |
| 3 | 拿順 | 0.599 | link_folder/人物/拿順.md |
| 4 | 十二支派起源 | 0.594 | link_folder/神學/十二支派起源.md |
| 5 | 但支派 | 0.558 | link_folder/人物/但支派.md |

判定：✅ 建議使用既有條目 [[猶大支派]]（同名／字面對應）

## 但支派（人物）
query:
- 待建立詞：但支派
- 出現位置：民數記 第1章
- 候選類型：人物
- 本章上下文：民1:38-39 但支派 62,700 人。GT（丁良才）：但子孫的後代加增甚多——但原來只有一個兒子名戶伸（創46:23；民26:42），若以色列人在埃及共住四百三十年就沒有什麼難處。GT（精讀本）：但支派後來從以色列支派中脫離出去，獨自流離、拜偶像、行惡（士18:1-31），最後從以色列的十二支派中消失了（啟7:5,8），這成就了雅各對但的將來的預言（創49:16-18）。GT（背景註釋）：但支派為北營之首，因為但是妾生眾子最長的一個。BH：Dan's role in encampment was on north side, forming rear guard alongside Asher and Naphtali; Samson most famous member (Judges 13-16); notably absent from list of sealed tribes in Revelation 7:4-8.

字面解析：對上既有「但支派」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 但支派 | 0.751 | link_folder/人物/但支派.md |
| 2 | 但（審判） | 0.640 | link_folder/人物/但（審判）.md |
| 3 | 十二支派起源 | 0.616 | link_folder/神學/十二支派起源.md |
| 4 | 猶大支派 | 0.599 | link_folder/人物/猶大支派.md |
| 5 | 拿弗他利 | 0.564 | link_folder/人物/拿弗他利.md |

判定：✅ 建議使用既有條目 [[但支派]]（同名／字面對應）

## 流便（人物）
query:
- 待建立詞：流便
- 出現位置：民數記 第1章
- 候選類型：人物
- 本章上下文：民1:20-21「以色列的長子，流便子孫的後代」46,500 人。CT：流便因犯淫亂而失去長子的名份，被猶大和約瑟兩人分得。GT（丁良才）：流便因犯罪失了尊榮（創49:3-4），當時流便支派的人數不多。GT（背景註釋）：長子流便領導南營。BH：Reuben was firstborn son of Jacob and Leah; lost birthright due to indiscretion with Bilhah (Gen 35:22, 49:3-4); tribe settled east of Jordan in pasturelands (Num 32:1-5); often struggled with maintaining prominence.

字面解析：對上既有「流便」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 流便 | 0.774 | link_folder/人物/流便.md |
| 2 | 流便失去長子名分 | 0.695 | link_folder/神學/流便失去長子名分.md |
| 3 | 流便與辟拉同寢的性質 | 0.622 | link_folder/解經爭議/流便與辟拉同寢的性質.md |
| 4 | 便雅憫 | 0.612 | link_folder/人物/便雅憫.md |
| 5 | 十二支派起源 | 0.603 | link_folder/神學/十二支派起源.md |

判定：✅ 建議使用既有條目 [[流便]]（同名／字面對應）

## 以法蓮（人物）
query:
- 待建立詞：以法蓮
- 出現位置：民數記 第1章
- 候選類型：人物
- 本章上下文：民1:32-33 以法蓮 40,500 人。CT：約書亞的祖父以利沙瑪為以法蓮族長。GT（丁良才）：以利沙瑪是約書亞的祖父（代上7:26-27）；瑪拿西雖是約瑟的長子，以法蓮支派的名字卻被列在先（創48:19-20），人數也多（申33:16）；在曠野飄流的時候這支派的人數卻減少了八千名（民26:37）。GT（精讀本）：在約瑟的兩個兒子中小兒子以法蓮列在哥哥瑪拿西前，在行軍和安營時成為中心，是因為以法蓮是神主權性的揀選，得到了比瑪拿西更大的祝福（創48:13-14,17-19）。GT（背景註釋）：拉結眾子的支派位於西面，居首的是被立為約瑟長子的以法蓮。BH：Ephraim younger son of Joseph received greater blessing from Jacob (Gen 48:19); tribe became one of most prominent in Israel, often representing northern kingdom in prophetic literature.

字面解析：對上既有「以法蓮」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 以法蓮 | 0.822 | link_folder/人物/以法蓮.md |
| 2 | 以法蓮在瑪拿西以上 | 0.668 | link_folder/神學/以法蓮在瑪拿西以上.md |
| 3 | 瑪拿西 | 0.661 | link_folder/人物/瑪拿西.md |
| 4 | 收納以法蓮與瑪拿西 | 0.634 | link_folder/歷史/收納以法蓮與瑪拿西.md |
| 5 | 十二支派起源 | 0.615 | link_folder/神學/十二支派起源.md |

判定：✅ 建議使用既有條目 [[以法蓮]]（同名／字面對應）

## 瑪拿西（人物）
query:
- 待建立詞：瑪拿西
- 出現位置：民數記 第1章
- 候選類型：人物
- 本章上下文：民1:34-35 瑪拿西 32,200 人。GT（丁良才）：當時瑪拿西的人數是最少的（創48:19），在曠野的時候這支派中卻加增了二萬零五百名（民26:34，參伯12:23）。GT（精讀本）：神超越人的意思成就自己的工作，在神揀選的工作面前人應該謙卑讚美神的旨意（羅9:18-29）。BH：Manasseh split into two half-tribes east and west of Jordan; tribe's inheritance was large reflecting blessing Jacob gave to Joseph's sons (Gen 48:19).

字面解析：對上既有「瑪拿西」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 瑪拿西 | 0.727 | link_folder/人物/瑪拿西.md |
| 2 | 以法蓮 | 0.561 | link_folder/人物/以法蓮.md |
| 3 | 以法蓮在瑪拿西以上 | 0.553 | link_folder/神學/以法蓮在瑪拿西以上.md |
| 4 | 十二支派起源 | 0.542 | link_folder/神學/十二支派起源.md |
| 5 | 收納以法蓮與瑪拿西 | 0.524 | link_folder/歷史/收納以法蓮與瑪拿西.md |

判定：✅ 建議使用既有條目 [[瑪拿西]]（同名／字面對應）

## 數點民數（事件）
query:
- 待建立詞：數點民數
- 出現位置：民數記 第1章
- 候選類型：事件
- 本章上下文：全章核心事件——第一次人口普查。民1:2-3「你要按以色列全會眾的家室、宗族、人名的數目計算所有的男丁…從二十歲以外，能出去打仗的」。CT：此次數點是為著準備打仗；男丁按原文含有頭顱的意思，意指能夠出去打仗、為國家拋頭顱灑熱血的男子。GT（丁良才）：摩西兩次數點民數——初次在西奈曠野（出埃及後第二年，民1），二次在摩押平原（出埃及後第四十年，民26）；這種按宗族家室登記的數點法有四層益處：(1)好修成可靠的家譜，(2)得詳知各支派的人數，(3)能分佈各支派應占的位置，(4)可規定出發的次序；摩西兩次數點比較表——初次在西奈曠野、出埃及後第二年、出埃及的那一代、603,550人；二次在摩押平原、出埃及後第四十年、進迦南的那一代、601,730人。GT（啟導本）：第一次在建造會幕前為收銀子建會幕向二十歲以上男丁收取半舍客勒銀子（出30:11-16; 38:25-26），第二次即本章為組成軍隊；603,550人中除了迦勒和約書亞二人，全都在曠野的旅程中死去（民14,20）；若連婦孺及利未人總人口當在二百萬左右。GT（串珠）：民1與民26比較——西緬從59,300暴跌至22,200（可能因民25瘟疫），瑪拿西從32,200增至52,700，總數相差不遠。GT（難解經文）：出38和民1兩次普查目的不同——第一次為宗教目的（收集帳幕獻金），第二次為軍事目的（核定能打仗男丁）；兩次核定人數接近相符因日期相近不遠。GT（精讀本）：被數的意味著蒙神揀選成了居住在神榮耀中的人——領受征服迦南使命、為老弱婦孺爭戰、被呼召成為神手中的器皿；在這個世界上最大的祝福是被數點為神的百姓。KC：Numbering is proof of ownership; being numbered for heaven, knowing our names are recorded there, is something to be happy for (Lk 10:20b); God knows every single one, every person is important to Him; all numbered here except Joshua and Caleb will fall in wilderness (Num 14:29); those numbered in Num 26 form a new generation; the journey to the land should only take eleven days but became forty years due to unfaithfulness. BH：census served both practical and spiritual purposes, organizing people for military and religious duties; reflects God's promise to Abraham to make descendants as numerous as stars (Gen 15:5); total 603,550 underscores strength and potential of Israelite nation.
- 經文用詞：計算所有的男丁、數點、被數的

字面解析：對上既有「數點民數」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 數點民數 | 0.892 | link_folder/事件/數點民數.md |
| 2 | 六十萬零三千五百五十人（出38：26） | 0.815 | link_folder/事件/六十萬零三千五百五十人（出38：26）.md |
| 3 | 兩次普查的關係 | 0.775 | link_folder/解經爭議/兩次普查的關係.md |
| 4 | 古代近東的人口統計 | 0.774 | link_folder/背景/古代近東的人口統計.md |
| 5 | 家室與宗族 | 0.695 | link_folder/主題/家室與宗族.md |

判定：✅ 建議使用既有條目 [[數點民數]]（同名／字面對應）

## 利未支派（人物）
query:
- 待建立詞：利未支派
- 出現位置：民數記 第1章
- 候選類型：人物
- 本章上下文：民1:47-53 利未支派不數點在軍隊中，專責管理法櫃的帳幕。v49「惟獨利未支派你不可數點」；v50「只要派利未人管法櫃的帳幕和其中的器具」；v53「利未人要在法櫃帳幕的四圍安營，免得忿怒臨到以色列會眾」。CT：利未人因供聖職不在計算之列；利未支派不可算在軍隊之內，但他們另行數點以代替以色列人頭生的（民3:39-46）；利未人從一個月以外的男子就被數點（不像十二支派從二十歲以外）；利未人雖早已在敬拜金牛犢之人受罰之事上為耶和華熱心（出32:26-29；申33:8-9），也曾幫助祭司（出38:21），到這時候方被分派襄辦帳幕的事。GT（丁良才）：利未人不列在十二支派中因為要辦理會幕的事；利未三子：革順、哥轄和米拉利（創46:11），摩西和亞倫都是哥轄的子孫（出6:16-20；民3:14-24；代上6:1-48）。GT（啟導本）：以色列人的祭司必須是亞倫的後裔（亞倫的祭司體系）；利未人被揀選擔任會幕拆卸運輸支搭及聖殿侍奉；他們沒有分得迦南的地業，分住在各支派的城邑中（書21）；早期利未人侍奉年歲為三十至五十歲，後來降到二十歲（代下31:7）；律法對祭司的要求比對利未人嚴格；不久前利未人曾協助摩西剿滅拜金牛者所以被選為侍奉神的人（出32:27）。GT（精讀本）：利未支派是獻給神的支派，免去服兵役義務；利未人代替以色列的長子獻給神（民3:12; 8:9-15; 18:3-7; 出13:2,13）；信徒在靈裡應不斷與撒但爭戰，盡心事奉神並在神裡面享受安息（太11:28; 約4:24; 羅1:9; 來4:1-11）。KC：Levites not among warriors; take care of tabernacle and camp right around it; tabernacle here called "tabernacle of the testimony" — aspect of external testimony; church has to uphold testimony of truth in world, creates resistance and requires struggle; new testament believer is priest (praising God in sanctuary), Levite (serving church), or warrior (standing up for truth when attacked). BH：Levites were set apart for religious duties, exempt from military census; their role primarily spiritual, serving in Tabernacle and later Temple; Levites' separation can be seen as type of Christ set apart for ultimate priestly role; Levites' encampment around tabernacle serves as type of church called to be holy community set apart for God's purposes.
- 經文用詞：利未人、利未支派

字面解析：對上既有「利未支派」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 利未支派 | 0.899 | link_folder/人物/利未支派.md |
| 2 | 利未 | 0.718 | link_folder/人物/利未.md |
| 3 | 利未三族分工 | 0.693 | link_folder/事件/利未三族分工.md |
| 4 | 利未人代替長子 | 0.683 | link_folder/神學/利未人代替長子.md |
| 5 | 利未人受聖職討罪 | 0.677 | link_folder/事件/利未人受聖職討罪.md |

判定：✅ 建議使用既有條目 [[利未支派]]（同名／字面對應）

## 家室與宗族（主題）
query:
- 待建立詞：家室與宗族
- 出現位置：民數記 第1章
- 候選類型：主題
- 本章上下文：民1:2「按以色列全會眾的家室、宗族、人名的數目」；v18「會眾就照他們的家室、宗族、人名的數目…都述說自己的家譜」。CT：家室指略大於家庭的家族，宗族指介於支派和家族之間的部族；以色列人相當重視家譜，甚至根據家譜來斷定是以色列人不是（尼7:5,61）；家譜是各以色列人生命來源的記錄，教會也應該重視生命來源的見證——教會不是人的組織，不是看屬地的財富身分才幹，而是看屬天的生命。GT（丁良才）：這種數點法有四層益處——好修成可靠的家譜、得詳知各支派人數、能分佈各支派應占位置、可規定出發次序；古時候的以色列人以他們的家譜為重要，這樣辦為將來之救主的家譜使後人有法考察。GT（精讀本）：家室指親屬，宗族是父親、族長和家、家族的組合詞，指各支派；這樣按家室和宗族計算人數是為了讓人記住自己的出身，也是為了讓各個支派明確選民意識和歷史意識，好使他們協調一致完成神的神聖計畫。KC：every member must know his origin and where he belongs; every believer must know his place in Christ, know he is a child of God and what his spiritual family is; must declare pedigrees — declaring goes beyond inner conviction, must testify for others of his faith and not be ashamed (2Tim 1:8,12); declaration necessary because of "mixed multitude" (Exo 12:38; Num 11:4) among them — people who joined company of Christians but do not have life from God. BH：organization by clans and families highlights tribal structure crucial for identity and inheritance rights; listing every man by name signifies value of individual within community; one by one emphasizes thoroughness and precision — God's attention to detail and care for each member.
- 經文用詞：家室、宗族、家譜

字面解析：對上既有「家室與宗族」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 家室與宗族 | 0.832 | link_folder/主題/家室與宗族.md |
| 2 | 利未的族譜（出六14-27） | 0.601 | link_folder/歷史/利未的族譜（出六14-27）.md |
| 3 | 十二族長協助數點 | 0.595 | link_folder/事件/十二族長協助數點.md |
| 4 | 十二支派起源 | 0.576 | link_folder/神學/十二支派起源.md |
| 5 | 列國表 | 0.573 | link_folder/背景/列國表.md |

判定：✅ 建議使用既有條目 [[家室與宗族]]（同名／字面對應）

## 二十歲以外能打仗的（主題）
query:
- 待建立詞：二十歲以外能打仗的
- 出現位置：民數記 第1章
- 候選類型：主題
- 本章上下文：民1:3「凡以色列中，從二十歲以外，能出去打仗的」；全章每支派重複此條件（v20,22,24,26,28,30,32,34,36,38,40,42）。CT：二十歲以外表徵生命必須成熟的信徒才能有分於屬靈戰爭——不單要有兒子的身分，還必須是長成的人；「能出去打仗」首先是認清了爭戰的目的，其次是知道爭戰的法則，再次就是熟練爭戰的方法；近世的基督教趨向以工作來代替生命的追求，只會使幼小的生命萎縮；沒有長成的生命，神不能接受這人參加進爭戰的隊伍中。GT（啟導本）：凡是20歲以上的男丁都有參加軍隊的義務，畏縮不前視為大罪（參民14；申20）。GT（丁良才）：以下五等人都不在數點之內——凡二十歲以內的男丁、婦女、外邦人、利未人、年老不能上陣的人。KC：age of twenty is military service age in many countries; spiritually means certain maturity needed to serve as warrior in God's army (1Jn 2:13b-14b; cf. 2Tim 2:3-4); a baby in faith is not expected to be a warrior — it is expected of a young man in faith; once someone is in active service he renounces personal interests and makes his time and strength available; effectiveness depends on listening to superiors, following orders without contradicting (Lk 7:8). BH：age of twenty marks transition to adulthood and eligibility for military service; consistent throughout Pentateuch (Exo 30:14, Num 14:29); highlights readiness and responsibility expected of young men to defend and uphold community's values.
- 經文用詞：從二十歲以外

字面解析：對上既有「二十歲以外能打仗的」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 二十歲以外能打仗的 | 0.859 | link_folder/主題/二十歲以外能打仗的.md |
| 2 | 以色列人的軍隊 | 0.671 | link_folder/神學/以色列人的軍隊.md |
| 3 | 數點民數 | 0.545 | link_folder/事件/數點民數.md |
| 4 | 古代近東的人口統計 | 0.538 | link_folder/背景/古代近東的人口統計.md |
| 5 | 三十歲直到五十歲（利未人任職年齡） | 0.537 | link_folder/主題/三十歲直到五十歲（利未人任職年齡）.md |

判定：✅ 建議使用既有條目 [[二十歲以外能打仗的]]（同名／字面對應）

## 安營與纛（主題）
query:
- 待建立詞：安營與纛
- 出現位置：民數記 第1章
- 候選類型：主題
- 本章上下文：民1:52「以色列人支搭帳棚，要照他們的軍隊，各歸本營，各歸本纛」。CT：各支派各有指定的營地和旗幟。GT（丁良才）：共分四營四纛（民2:1-34）。GT（精讀本）：以會幕為中心支搭自己的帳幕（民2:1-34），表示他們應過以神為中心的生活。GT（背景註釋）：祭司和利未人營地設於聖所四面，其他支派每邊三個安營在外圍形成方形——軍營呈方形是這時代埃及的慣例，主前九世紀亞述藝術也顯示君王位居受保護的中央；猶大為眾支派之首領導最重要的東營（聖幕入口朝東），長子流便領導南營，但支派為北營之首（因為但是妾生眾子最長的一個），拉結眾子的支派位於西面居首的是被立為約瑟長子的以法蓮；埃及軍兵每個部隊以神祇為名、旗幟之上都有所屬神祇的標記，因此假定每個支派都有象徵該支派事物在其纛上是理所當然的事；但另一方面亦有釋經家將「纛」解作軍兵的單位而非旗幟。BH：standard refers to banner or flag representing each tribe, rallying point and symbol of identity; foreshadows believers rallying under banner of Christ (Heb 12:1-2); echoes prophetic vision in Isaiah 11:10 where root of Jesse stands as banner for peoples drawing all nations to Him.
- 經文用詞：各歸本營、各歸本纛

字面解析：對上既有「安營與纛」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 安營與纛 | 0.884 | link_folder/主題/安營與纛.md |
| 2 | 行軍次序 | 0.660 | link_folder/事件/行軍次序.md |
| 3 | 耶和華尼西 | 0.628 | link_folder/神學/耶和華尼西.md |
| 4 | 會幕（帳幕整體） | 0.610 | link_folder/主題/會幕（帳幕整體）.md |
| 5 | 十二支派起源 | 0.605 | link_folder/神學/十二支派起源.md |

判定：✅ 建議使用既有條目 [[安營與纛]]（同名／字面對應）

## 外人近前來必被治死（主題）
query:
- 待建立詞：外人近前來必被治死
- 出現位置：民數記 第1章
- 候選類型：主題
- 本章上下文：民1:51「近前來的外人必被治死」。CT：「外人」意指非利未人，包括以色列其他支派和外族人；利未人的營在神的百姓中作為一條界線，讓百姓在每天的生活中學習尊神為大，不越過神的界限，免得引來死亡——這是見證嚴肅的一面，人的天性是喜歡越過神的，神從各方面的安排來提醒人，讓人時刻去學習尊重神。GT（丁良才）：「外人」就是外族人（參民16:40；利22:12）。GT（啟導本）：「外人」指非利未人，包括一切非利未人的以色列人——從會幕的侍奉來說這些人都是外人（參出29:33；利22:12）。GT（精讀本）：利未人擔當著護衛神聖潔的任務，神以死亡刑罰無視並破壞神聖潔的人（撒上5章）。BH：severe warning highlights holiness of tabernacle and seriousness of approaching God's presence without authorization; restriction serves as reminder of separation between God and humanity due to sin, ultimately bridged by Jesus Christ (Heb 10:19-22); echoes incident with Nadab and Abihu (Lev 10:1-2) where improper worship led to immediate judgment.
- 經文用詞：近前來的外人必被治死

字面解析：對上既有「外人近前來必被治死」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 外人近前來必被治死 | 0.883 | link_folder/主題/外人近前來必被治死.md |
| 2 | 凡擅進靠近耶和華會棚與祭事場者必定蒙誅死亡 | 0.603 | link_folder/神學/凡擅進靠近耶和華會棚與祭事場者必定蒙誅死亡.md |
| 3 | 不可親近 | 0.601 | link_folder/神學/不可親近.md |
| 4 | 褻瀆聖名案例（利未記唯一記載的具體刑罰執行事件） | 0.596 | link_folder/事件/褻瀆聖名案例（利未記唯一記載的具體刑罰執行事件）.md |
| 5 | 剪除 | 0.596 | link_folder/原文/剪除.md |

判定：✅ 建議使用既有條目 [[外人近前來必被治死]]（同名／字面對應）

## 十二族長協助數點（事件）
query:
- 待建立詞：十二族長協助數點
- 出現位置：民數記 第1章
- 候選類型：事件
- 本章上下文：民1:4「每支派中必有一人作本支派的族長，幫助你們」；v5-15 十二族長名單；v16「這都是從會中選召的，各作本支派的首領，都是以色列軍中的統領」。CT：選立意為才能出眾被神按名指定（v17）；首領指官長平時治理本支派的事務，統領指將領戰時統帥本支派的軍士；十二個首領在摩西和亞倫的監督下數點各自支派的人數。GT（丁良才）：這些族長大概是摩西先前所分派的首領（參出18:21-26）；各支派的名字不是完全照長幼的次序排列，而是按著他們所屬之營排列的——迦得的名字列在流便西緬之後因為這三支派在一營之中。GT（精讀本）：各支派的首領都是以色列軍中統領，暗示著他們在以色列中擔負大事的人；他們與長老不同——長老是屬靈方面的領袖（出4:29; 24:9），而他們是在行政方面的領袖；數點人數的工作能在一天內結束是因為以前次的數點為基礎（出30:11-12）所以較為容易，且他們擁有對耶和華的信仰具有明確的使命意識。KC：names of heads also found in Num 2,7,10; in most names 'El' (God) resounds — Israelites did not forget God during stay in Egypt, in names they gave their children they kept memory of God; twelve names with meanings — Elizur=「my God is a rock」, Shelumiel=「in peace with God」, Nahshon=「prophet」, Nethanel=「gift of God」, Eliab=「my God is Father」, Elishama=「my God has heard」, Gamaliel=「God is a rewarder」, Abidan=「my Father is Judge」, Ahiezer=「brother of help」, Pagiel=「God has met me」, Eliasaph=「God has added」, Ahira=「brother of evil」; Timothy is one of those 'numbered' by older brothers (Acts 16:1-2). BH：leaders were not only chosen from congregation but representatives of respective tribes; appointment from within congregation underscores importance of communal involvement in leadership selection; reflects theocratic nature of Israelite society where God directed Moses to choose leaders already recognized by the people.
- 經文用詞：族長、首領、統領

字面解析：對上既有「十二族長協助數點」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 十二族長協助數點 | 0.900 | link_folder/事件/十二族長協助數點.md |
| 2 | 以色列的眾長老 | 0.688 | link_folder/人物/以色列的眾長老.md |
| 3 | 摩西立首領 | 0.663 | link_folder/事件/摩西立首領.md |
| 4 | 以色列人的官長 | 0.660 | link_folder/人物/以色列人的官長.md |
| 5 | 以色列的長老 | 0.657 | link_folder/文化/以色列的長老.md |

判定：✅ 建議使用既有條目 [[十二族長協助數點]]（同名／字面對應）

## 拿順（人物）
query:
- 待建立詞：拿順
- 出現位置：民數記 第1章
- 候選類型：人物
- 本章上下文：民1:7「屬猶大的，有亞米拿達的兒子拿順」，猶大支派首領兼軍中統領（v16）。CT 原文字義作「男巫」。GT 丁良才：「拿順是亞倫的妻兄（出六23），也是大衛的先祖（得四21-20）。」KC 依 Grant《Numerical Bible》給的字義是 prophet（先知），父名亞米拿達為 people of the willing Giver。BH：拿順列在馬太福音一4、路加福音三32 耶穌的家譜中；猶太傳統高度推崇拿順，常把信心之舉歸給他，例如紅海分開之前第一個踏進海中的就是他。同一人再見於民2:3、7:12、10:14。
- 經文用詞：拿順

字面解析：對上既有「拿順」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 拿順 | 0.814 | link_folder/人物/拿順.md |
| 2 | 十二族長協助數點 | 0.612 | link_folder/事件/十二族長協助數點.md |
| 3 | 拿弗他利 | 0.587 | link_folder/人物/拿弗他利.md |
| 4 | 拿鶴 | 0.582 | link_folder/人物/拿鶴.md |
| 5 | 拿答 | 0.574 | link_folder/人物/拿答.md |

判定：✅ 建議使用既有條目 [[拿順]]（同名／字面對應）

## 六十萬零三千五百五十人（出38：26）（事件）
query:
- 待建立詞：六十萬零三千五百五十人（出38：26）
- 出現位置：民數記 第1章
- 候選類型：事件
- 本章上下文：民1:46「凡以色列人中被數的……共有六十萬零三千五百五十名」，與出38:26 收贖命銀時所點的總數完全相同。GT 丁良才據此主張兩次計算「是相連的」，並給四層理由（數點民數不是三五日可完的事；五六個月之內神未必使摩西數點民數兩次；兩次都沒有數點利未人；民26:64 只提兩次數點）。GT《啟導本》：全部可以作戰的男丁總數為603,550（46節），與第一次人口統計的總數一樣（出三十八26）。KC：This number corresponds to a previous census, about nine months earlier (Exo 38:25-26)；在那次普查中每個被數的人要付半舍客勒銀子作贖價。BH：這個總數不含利未人，是神向亞伯拉罕應許後裔如同星辰的應驗（創15:5）。

字面解析：對上既有「六十萬零三千五百五十人（出38：26）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 六十萬零三千五百五十人（出38：26） | 0.858 | link_folder/事件/六十萬零三千五百五十人（出38：26）.md |
| 2 | 兩次普查的關係 | 0.801 | link_folder/解經爭議/兩次普查的關係.md |
| 3 | 數點民數 | 0.754 | link_folder/事件/數點民數.md |
| 4 | 六十萬人的數目 | 0.664 | link_folder/解經爭議/六十萬人的數目.md |
| 5 | 古代近東的人口統計 | 0.657 | link_folder/背景/古代近東的人口統計.md |

判定：✅ 建議使用既有條目 [[六十萬零三千五百五十人（出38：26）]]（同名／字面對應）

## 兩次普查的關係（解經爭議）
query:
- 待建立詞：兩次普查的關係
- 出現位置：民數記 第1章
- 候選類型：解經爭議
- 本章上下文：出38:25-26 的贖命銀普查與民1 的軍籍普查總數同為603,550，兩者關係諸家不同。GT 丁良才主張兩次計算「是相連的」，列四層理由。GT 賈斯樂郝威《聖經難解經文詮釋手冊》命題3 主張是兩次不同目的的普查：「第一次的人數核定（出卅八章）是為了宗教的目的，第二次人數核定是為了軍事目的……兩次核定人數的數目接近相符，因為核定的日期相近不遠。」GT《民數記串珠聖經註釋》：「這次統計很可能沿用數月前作過的統計資料（出30:12-16; 38:25-26），但目的卻是不同。」KC 給的間隔則是九個月：「This number corresponds to a previous census, about nine months earlier」。GT《啟導本》另指這是以色列人進入曠野後舉行的第二次人口調查。

字面解析：對上既有「兩次普查的關係」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 兩次普查的關係 | 0.871 | link_folder/解經爭議/兩次普查的關係.md |
| 2 | 六十萬零三千五百五十人（出38：26） | 0.706 | link_folder/事件/六十萬零三千五百五十人（出38：26）.md |
| 3 | 數點民數 | 0.689 | link_folder/事件/數點民數.md |
| 4 | 古代近東的人口統計 | 0.637 | link_folder/背景/古代近東的人口統計.md |
| 5 | 六十萬人的數目 | 0.583 | link_folder/解經爭議/六十萬人的數目.md |

判定：✅ 建議使用既有條目 [[兩次普查的關係]]（同名／字面對應）

## 古代近東的人口統計（背景）
query:
- 待建立詞：古代近東的人口統計
- 出現位置：民數記 第1章
- 候選類型：背景
- 本章上下文：GT《舊約聖經背景註釋》【民一2 人口統計的目的】：「古代的人口統計是為徵召壯丁而設的，召來的男丁有時得服兵役，有時要參與官方的建築工程。政府往往同時課取人頭稅，人頭稅有時甚至是人口統計的動機。這次統計的目的雖是徵召軍兵，與出埃及記三十11～16（參註釋）為收取殿稅而作的統計，卻不無關係。」BH：二十歲的役齡門檻在古代近東文化中通行——「In ancient Near Eastern cultures, this age was commonly associated with the ability to bear arms and participate in communal defense」；並指出點名造冊（census）在古代近東是行政與軍事的慣常做法。本章與出30:11-16 的殿稅統計互為表裡。

字面解析：對上既有「古代近東的人口統計」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 古代近東的人口統計 | 0.838 | link_folder/背景/古代近東的人口統計.md |
| 2 | 數點民數 | 0.672 | link_folder/事件/數點民數.md |
| 3 | 二十歲以外能打仗的 | 0.645 | link_folder/主題/二十歲以外能打仗的.md |
| 4 | 六十萬零三千五百五十人（出38：26） | 0.589 | link_folder/事件/六十萬零三千五百五十人（出38：26）.md |
| 5 | 兩次普查的關係 | 0.567 | link_folder/解經爭議/兩次普查的關係.md |

判定：✅ 建議使用既有條目 [[古代近東的人口統計]]（同名／字面對應）

## 六十萬人的數目（解經爭議）
query:
- 待建立詞：六十萬人的數目
- 出現位置：民數記 第1章
- 候選類型：解經爭議
- 本章上下文：民1:46 的603,550 是二十歲以上男丁，換算全體人口引起長期爭議。GT《啟導本》：「這裡的總數只限20歲以上的男丁，若連婦孺及利未人，總人口當在二百萬左右。不少史家為此龐大數字作出種種解釋，認為按當時地理、資源等等，決不可能養活……龐大人口。」GT 丁良才：「連婦女、孩子，統共有二百四十余萬，可見是神的保護。」GT《聖經精讀本》從神蹟角度回應：「以色列百姓的數目,第四代或第五代(約430年)只有男丁(二十歲以外)已達到六十萬,若靠自然能力這是不可能的,只有靠神超自然的恩典和能力才有可能。」GT《舊約聖經背景註釋》【民一46 人口的數目】把討論指回出埃及記十二37 的註釋。

字面解析：對上既有「六十萬人的數目」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 六十萬人的數目 | 0.783 | link_folder/解經爭議/六十萬人的數目.md |
| 2 | 六十萬零三千五百五十人（出38：26） | 0.647 | link_folder/事件/六十萬零三千五百五十人（出38：26）.md |
| 3 | 數點民數 | 0.608 | link_folder/事件/數點民數.md |
| 4 | 兩次普查的關係 | 0.597 | link_folder/解經爭議/兩次普查的關係.md |
| 5 | 古代近東的人口統計 | 0.573 | link_folder/背景/古代近東的人口統計.md |

判定：✅ 建議使用既有條目 [[六十萬人的數目]]（同名／字面對應）

## 西緬（人物）
query:
- 待建立詞：西緬
- 出現位置：民數記 第1章
- 候選類型：人物
- 本章上下文：民1:22-23 西緬子孫59,300 名。CT 指出西緬經常與利未相提並論（創49:5），但此次數點漏過利未，因利未支派專供聖職不在數點之列。GT《聖經精讀本》指出西緬是利亞的第二個兒子（創29:33）。GT《民數記串珠聖經註釋》的兩章對照表顯示西緬是減幅最大的支派：民1 的59,300 到民26 只剩22,200。BH 指出西緬的地業落在猶大境內（書19:1-9），並提到創49:5-7 雅各對西緬與利未「分散在以色列」的預言。

字面解析：對上既有「西緬」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 西緬 | 0.734 | link_folder/人物/西緬.md |
| 2 | 西布倫（同住） | 0.621 | link_folder/人物/西布倫（同住）.md |
| 3 | 利未 | 0.602 | link_folder/人物/利未.md |
| 4 | 西緬利未受咒詛 (創49_5-7) | 0.596 | link_folder/互文/西緬利未受咒詛 (創49_5-7).md |
| 5 | 「西緬」名字含義 | 0.582 | link_folder/原文/「西緬」名字含義.md |

判定：✅ 建議使用既有條目 [[西緬]]（同名／字面對應）

## 以薩迦（價值）（人物）
query:
- 待建立詞：以薩迦（價值）
- 出現位置：民數記 第1章
- 候選類型：人物
- 本章上下文：民1:28-29 以薩迦子孫54,400 名。CT 指出猶大、以薩迦和西布倫三人都是同母兄弟，利亞所生（創35:23），「這三個支派在軍隊的編組裡同屬最先起行的一組」。GT《聖經精讀本》指出以薩迦和西布倫是利亞的第五和第六個兒子（創30:17-20）。BH 指出以薩迦以「通達時務」著稱（代上12:32），地業在肥沃的耶斯列平原。

字面解析：對上既有「以薩迦（價值）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 以薩迦（價值） | 0.814 | link_folder/人物/以薩迦（價值）.md |
| 2 | 以薩迦（報酬） | 0.659 | link_folder/原文/以薩迦（報酬）.md |
| 3 | 西布倫（同住） | 0.635 | link_folder/人物/西布倫（同住）.md |
| 4 | 利亞 | 0.592 | link_folder/人物/利亞.md |
| 5 | 亞設（有福） | 0.576 | link_folder/人物/亞設（有福）.md |

判定：✅ 建議使用既有條目 [[以薩迦（價值）]]（同名／字面對應）

## 西布倫（同住）（人物）
query:
- 待建立詞：西布倫（同住）
- 出現位置：民數記 第1章
- 候選類型：人物
- 本章上下文：民1:30-31 西布倫子孫57,400 名。CT 在民一9 直接指回第8節註解：猶大、以薩迦和西布倫同為利亞所生，同屬最先起行的一組。GT《聖經精讀本》指出西布倫是利亞的第六個兒子（創30:17-20）。BH 指出雅各預言西布倫必住在海口、成為停船的海口（創49:13），其地業近加利利海、便於貿易，並在士師記4:6 與歷代志上12:33 出兵。

字面解析：對上既有「西布倫（同住）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 西布倫（同住） | 0.839 | link_folder/人物/西布倫（同住）.md |
| 2 | 西緬 | 0.584 | link_folder/人物/西緬.md |
| 3 | 西珥 | 0.556 | link_folder/地點/西珥.md |
| 4 | 利亞 | 0.555 | link_folder/人物/利亞.md |
| 5 | 以薩迦（價值） | 0.546 | link_folder/人物/以薩迦（價值）.md |

判定：✅ 建議使用既有條目 [[西布倫（同住）]]（同名／字面對應）

## 迦得（萬幸）（人物）
query:
- 待建立詞：迦得（萬幸）
- 出現位置：民數記 第1章
- 候選類型：人物
- 本章上下文：民1:24-25 迦得子孫45,650 名——本章唯一沒有以「百」收尾的數字。GT 丁良才記下兩件事：「迦得的名字列在此處大概是因這支派和流便西緬支派在一營之中」；以及「除了迦得支派以外，十二支派都是記整數，沒有記零數，有人以為這一次的計算，是為預備打仗，所以只記五十個以上的整數」。CT 指出迦得和亞設同為悉帕所生（創35:26），卻在軍隊編組中分列不同的組。GT《聖經精讀本》指出迦得是利亞的婢女悉帕的第一個兒子（創30:10-11），神把相近的親族安排在一個行列中，「是為了消除人為的矛盾和磨擦，這是神的智慧」。BH 指出迦得以善戰著稱（代上12:8）。

字面解析：對上既有「迦得（萬幸）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 迦得（萬幸） | 0.838 | link_folder/人物/迦得（萬幸）.md |
| 2 | 迦得（幸運） | 0.635 | link_folder/原文/迦得（幸運）.md |
| 3 | 亞設（有福） | 0.609 | link_folder/人物/亞設（有福）.md |
| 4 | 十二支派起源 | 0.600 | link_folder/神學/十二支派起源.md |
| 5 | 拿弗他利 | 0.582 | link_folder/人物/拿弗他利.md |

判定：✅ 建議使用既有條目 [[迦得（萬幸）]]（同名／字面對應）

## 亞設（有福）（人物）
query:
- 待建立詞：亞設（有福）
- 出現位置：民數記 第1章
- 候選類型：人物
- 本章上下文：民1:40-41 亞設子孫41,500 名。CT 指出亞設和迦得同為悉帕所生（創35:26），卻在軍隊的編組中分列不同的組——「亞設與但、拿弗他利同組（參二25~31），迦得則與流便、西緬同組（參二10~16）」。GT《聖經精讀本》指出亞設是悉帕最小的兒子（創30:12-13）。BH 指出亞設之名意為快樂或有福，地業沿地中海岸富庶，應驗創49:20 的祝福，申33:24 另提到亞設的橄欖油。

字面解析：對上既有「亞設（有福）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 亞設（有福） | 0.815 | link_folder/人物/亞設（有福）.md |
| 2 | 迦得（萬幸） | 0.613 | link_folder/人物/迦得（萬幸）.md |
| 3 | 以薩迦（價值） | 0.545 | link_folder/人物/以薩迦（價值）.md |
| 4 | 以法蓮 | 0.542 | link_folder/人物/以法蓮.md |
| 5 | 亞捫人 | 0.540 | link_folder/人物/亞捫人.md |

判定：✅ 建議使用既有條目 [[亞設（有福）]]（同名／字面對應）

## 拿弗他利（人物）
query:
- 待建立詞：拿弗他利
- 出現位置：民數記 第1章
- 候選類型：人物
- 本章上下文：民1:42-43 拿弗他利子孫53,400 名。CT 指出但和拿弗他利兩兄弟為同母辟拉所生（創35:25），「他們兩支派加上亞設支派在軍隊的編組中同屬殿後的一組」。GT《聖經精讀本》指出拿弗他利是辟拉最小的兒子（創30:7-8）。BH 指出拿弗他利地業在迦南北部靠加利利海，日後是耶穌大部分傳道工作所在，應驗以賽亞書9:1-2 的預言。

字面解析：對上既有「拿弗他利」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 拿弗他利 | 0.786 | link_folder/人物/拿弗他利.md |
| 2 | 拿鶴 | 0.611 | link_folder/人物/拿鶴.md |
| 3 | 辟拉 | 0.550 | link_folder/人物/辟拉.md |
| 4 | 但支派 | 0.547 | link_folder/人物/但支派.md |
| 5 | 迦南 | 0.543 | link_folder/人物/迦南.md |

判定：✅ 建議使用既有條目 [[拿弗他利]]（同名／字面對應）

## 便雅憫（人物）
query:
- 待建立詞：便雅憫
- 出現位置：民數記 第1章
- 候選類型：人物
- 本章上下文：民1:36-37 便雅憫子孫35,400 名。CT 指出在軍隊的編組中，以法蓮、瑪拿西和便雅憫同屬一組，「他們都是拉結的後裔」（民2:18-24；創35:24）。BH 指出便雅憫雖是較小的支派，卻以善用機弦的勇士著稱（士20:16），日後出了以色列的第一位王掃羅，以及使徒保羅。

字面解析：對上既有「便雅憫」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 便雅憫 | 0.720 | link_folder/人物/便雅憫.md |
| 2 | 迦得（萬幸） | 0.561 | link_folder/人物/迦得（萬幸）.md |
| 3 | 十二支派起源 | 0.549 | link_folder/神學/十二支派起源.md |
| 4 | 猶大支派 | 0.545 | link_folder/人物/猶大支派.md |
| 5 | 以法蓮 | 0.540 | link_folder/人物/以法蓮.md |

判定：✅ 建議使用既有條目 [[便雅憫]]（同名／字面對應）

## 候選互查（本章內部，⚠＝彼此相似 ≥ 0.8）
兩個候選可能是同一概念——考慮合併成一個候選（另一個用 surfaces 涵蓋），
或確認確為兩個條目再照建：
- 0.840 ⚠ 以色列人的軍隊 ↔ 二十歲以外能打仗的
