<!-- candidate_similarity_meta
schema_version: 1
book: 民數記
chapter: 2
candidate_sha256: 736ee8cf8792a6836c2b792ddba12a259161ca95574c38dce952bd568facd138
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

# 候選語義近鄰報告：民數記 第2章

- 檢索模型：nvidia/nemotron-3-embed-1b｜重排模型：nvidia/llama-nemotron-rerank-vl-1b-v2:free（未校準/保守模式）｜全庫 2630 條
- 規則說明：字面確切匹配直接通過；其餘候選先檢索 Top 20 名再由 Reranker 重排，取前 5 名顯示。
  治理優先：同名歧義（D類）與分類不相容永遠標 ⚠。
  重排模型未校準時，⚠ 由檢索相似度規則（≥0.50 且 top-1 非同實體）決定，重排名次只當附加證據。
  字面解析：列 resolver 實際比對結果——標「請確認」者務必人工核實。

## 安營與纛（主題）
query:
- 待建立詞：安營與纛
- 出現位置：民數記 第2章
- 候選類型：主題
- 本章上下文：全章為第1章「安營與纛」原則的具體展開。v2「以色列人要各歸自己的纛下，在本族的旗號那裡，對著會幕的四圍安營」。
CT：各支派各有指定的營地和旗幟；以會幕為中心，表徵以基督為中心，全軍在基督的率領之下；十二支派分作四組各占一個方位圍著會幕安營，形成十字隊形——神藉著這個隊形向人啟示了十字架的生活原則。
GT（啟導本）：以色列民在曠野紮營排列的方式是個正方形，會幕在正中央，祭司在會幕東面，利未三族（米拉利、革順、哥轄）各在北、西、南三面；十二支派分成四組，每組三支派，在利未人與祭司的四圍安營；「對著會幕」也可譯為「與會幕間有相當距離」，《約書亞記》3:4 規定約櫃與支派安營間的距離為二千肘（約一千公尺）。
GT（串珠）：營陣是四方形，會幕在中心，祭司利未人環繞著會幕安營，十二支派也朝向會幕；這陣形象徵神住在子民中間，神子民的生活也以神為核心；這也是聖城的模式，是神永恆的計畫，因此先知以西結（結40章）與使徒約翰（啟21章）所見到的聖城都有類似的結構。
GT（精讀本）：四個纛代表東西南北四個方向——猶大纛（東，獅子綠旗）、流便纛（南，人首紅旗）、以法蓮纛（西，牛犢黃旗）、但纛（北，鷹紅白旗）；這四個支派代表以色列，也暗示著將來要得救的所有被造物（四是被造物的數字）。
GT（背景註釋）：四組支派的排列和他們的母系有很大關係——東營（猶大、以薩迦、西布倫）皆利亞所生；南營（流便、西緬、迦得）利亞所生＋利亞婢女所生；西營（以法蓮、瑪拿西、便雅憫）皆拉結所生/孫；北營（但、亞設、拿弗他利）婢女所生。
KC：Everything in battle revolves around the tabernacle which is the center of the army；每個信徒必須知道自己在神居所周圍的位置（林前12:18）；三個支派在一個纛下聯合，如同地方教會因地理位置而連結；只有一個中心——主耶穌，真正的會幕，祂要將四散的兒女聚集為一；主耶穌如「超乎萬人之上」的纛（歌5:10）。
BH：The Tabernacle was the dwelling place of God among His people, symbolizing His presence and guidance；standards provided organization and identity within the camp；family banners emphasize the importance of family units within the larger community。

四營方位神學——
CT：十二支派分作四組各占一個方位圍著會幕安營，形成十字隊形；東南西北四方位形成十字架，表徵十字架乃防守、禦敵之道。
GT（串珠）：營陣是四方形，會幕在中心，祭司利未人環繞著會幕安營，十二支派也朝向會幕；這陣形象徵神住在子民中間，這也是聖城的模式——先知以西結（結40章）與使徒約翰（啟21章）所見到的聖城都有類似的結構。
GT（精讀本）：四個纛代表東西南北四個方向——猶大纛（東，獅子綠旗）、流便纛（南，人首紅旗）、以法蓮纛（西，牛犢黃旗）、但纛（北，鷹紅白旗）；這四個支派代表以色列，也暗示著將來要得救的所有被造物（四是被造物的數字）。
KC：The four standards lie in four directions from which the influences come from outside；east side — entrance to the tabernacle, sunrise, looking forward to the coming of the Lord Jesus；south side — right side, dignity of position, seated with Christ in heavenly places（弗2:6）；west side — side of the sea, trials and difficulties producing fruit for God；north side — darkest side, hiding, gloomy side of testimony。
- 經文用詞：各歸自己的纛下、本族的旗號、對著會幕的四圍安營、各歸本纛

字面解析：對上既有「安營與纛」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 安營與纛 | 0.864 | link_folder/主題/安營與纛.md |
| 2 | 行軍次序 | 0.706 | link_folder/事件/行軍次序.md |
| 3 | 會幕（帳幕整體） | 0.655 | link_folder/主題/會幕（帳幕整體）.md |
| 4 | 十二支派起源 | 0.646 | link_folder/神學/十二支派起源.md |
| 5 | 但支派 | 0.637 | link_folder/人物/但支派.md |

判定：✅ 建議使用既有條目 [[安營與纛]]（同名／字面對應）

## 利未支派（人物）
query:
- 待建立詞：利未支派
- 出現位置：民數記 第2章
- 候選類型：人物
- 本章上下文：v17「隨後，會幕要往前行，有利未營在諸營中間。他們怎樣安營就怎樣往前行，各按本位，各歸本纛」。
v33「惟獨利未人沒有數在以色列人中，是照耶和華所吩咐摩西的」。
CT：利未營在諸營中間，會幕和利未支派構成全軍的中心。
GT（丁良才）：有利未營在諸營中間——就是哥轄族（民10:17註）；「他們怎樣安營，就怎樣往前行」（民10:11-28），這樣神的住處常在選民中間（參詩46:5）。
GT（精讀本）：指哥轄子孫抬著聖物往前行（民10:21）；帳幕中的聖物與帳幕分開，佔據了以色列所有支派中最中心的位置；神就是這樣讓以色列百姓即使在行軍中也維持以神為中心的信仰生活。
KC：The tent of meeting is the center of the people；both in worship and approaching God（camp）as well as in defense and protection（set out）it is about the relationship of God with His people；Levites have their own specific task, inseparable from both services.
BH：Levites were not numbered among the sons of Israel, just as the LORD had commanded Moses；their role was spiritual rather than military.

會幕在諸營中間（v17）——
GT（丁良才）：有利未營在諸營中間——就是哥轄族（民10:17註）；「他們怎樣安營，就怎樣往前行」（民10:11-28），這樣神的住處常在選民中間（參詩46:5）。
GT（精讀本）：指哥轄子孫抬著聖物往前行（民10:21）；帳幕中的聖物與帳幕分開，佔據了以色列所有支派中最中心的位置；神就是這樣讓以色列百姓即使在行軍中也維持以神為中心的信仰生活；神向以色列百姓所要求的是隨時隨地時刻都以神為中心。
KC：The tent of meeting is the center of the people, from there come their marching orders；both in worship and approaching God as well as in defense and protection it is about the relationship of God with His people.
BH：The central positioning reflects the need for God to be the focal point in the lives of believers（太6:33）。
- 經文用詞：利未營在諸營中間、利未人沒有數在以色列人中

字面解析：對上既有「利未支派」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 利未支派 | 0.749 | link_folder/人物/利未支派.md |
| 2 | 行軍次序 | 0.670 | link_folder/事件/行軍次序.md |
| 3 | 安營與纛 | 0.662 | link_folder/主題/安營與纛.md |
| 4 | 摩西的臨時會幕（營外） | 0.625 | link_folder/事件/摩西的臨時會幕（營外）.md |
| 5 | 會幕（帳幕整體） | 0.615 | link_folder/主題/會幕（帳幕整體）.md |

判定：✅ 建議使用既有條目 [[利未支派]]（同名／字面對應）

## 會幕（帳幕整體）（主題）
query:
- 待建立詞：會幕（帳幕整體）
- 出現位置：民數記 第2章
- 候選類型：主題
- 本章上下文：v2「對著會幕的四圍安營」；v17「隨後，會幕要往前行，有利未營在諸營中間」。
全章以會幕為絕對中心，四營環繞，利未人緊鄰會幕安營。
CT：以會幕為中心，就是以主為中心；人的難處是以自己為中心，若中心從自己的身上轉移到主身上，人所有的難處就全可以解決了。
GT（精讀本）：神以會幕為中心安置以色列各支派的營，這象徵神作為以色列真正的統治者，臨在於他們的生活中；人存在的價值和意義，是把神迎接在自己的生活中心裡。
GT（丁良才）：會幕在以色列人當中，有三樣教訓——（一）神與人同在，（二）都當倚靠神，（三）都可親近神。
KC：The tent of meeting is the center of the people, from there come their marching orders.
BH：The Tabernacle was the dwelling place of God among His people, symbolizing His presence and guidance；central positioning reflects the need for God to be the focal point in the lives of believers（太6:33）。

會幕在諸營中間（v17）——
GT（丁良才）：有利未營在諸營中間——就是哥轄族（民10:17註）；「他們怎樣安營，就怎樣往前行」（民10:11-28），這樣神的住處常在選民中間（參詩46:5）。
GT（精讀本）：帳幕中的聖物與帳幕分開，佔據了以色列所有支派中最中心的位置；神就是這樣讓以色列百姓即使在行軍中也維持以神為中心的信仰生活。
- 經文用詞：會幕要往前行

字面解析：對上既有「會幕（帳幕整體）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 會幕（帳幕整體） | 0.714 | link_folder/主題/會幕（帳幕整體）.md |
| 2 | 安營與纛 | 0.679 | link_folder/主題/安營與纛.md |
| 3 | 神的同在 | 0.678 | link_folder/神學/神的同在.md |
| 4 | 行軍次序 | 0.668 | link_folder/事件/行軍次序.md |
| 5 | 摩西的臨時會幕（營外） | 0.663 | link_folder/事件/摩西的臨時會幕（營外）.md |

判定：✅ 建議使用既有條目 [[會幕（帳幕整體）]]（同名／字面對應）

## 猶大支派（人物）
query:
- 待建立詞：猶大支派
- 出現位置：民數記 第2章
- 候選類型：人物
- 本章上下文：v3「在東邊，向日出之地，照著軍隊安營的是猶大營的纛」；v9「凡屬猶大營…共有十八萬六千四百名，要作第一隊往前行」。
CT：東邊向日出之地——會幕門口即面向東邊（出27:13,16），摩西和亞倫也安營在東邊的內層，可見是最重要的方位；猶大支派相當特殊，大衛王和其後的猶大國諸王都出自該支派（太1:3,6），甚至主耶穌也是大衛的後裔（羅1:3）。
GT（精讀本）：猶大支派站在行軍行列的前面，預表耶穌作為全人類的救主和君王，站在全人類的前面，把人引到永遠的國度裡（約10:4）；耶穌是藉著猶大支派的血統道成了肉身（太1:3-16）。
GT（背景註釋）：東邊向日出之地——會幕前面的方向（民3:38），在神面前是榮耀的位置；成就了雅各對猶大的預言（創49:10），在大衛時期展開（撒下2:4-7; 5:1-3），並通過耶穌基督得以成就（來7:14）。
KC：Judah means 'praise' — the spirit of praise is the spirit of power（代下20:22）；the main purpose of the meeting of the church is to praise and worship God；Judah becomes the royal line from whom the Messiah will be born（創49:10; 得4:18-22）；拿順列在主耶穌的家譜中（太1:4）。
BH：Judah's position at the forefront of the camp signifies their role as leaders and protectors；the east side holds significant symbolism — new beginnings, hope, divine presence；Judah's prominence points to the future coming of the Messiah, "Lion of the tribe of Judah"（啟5:5）。
- 經文用詞：猶大營的纛

字面解析：對上既有「猶大支派」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 猶大支派 | 0.832 | link_folder/人物/猶大支派.md |
| 2 | 拿順 | 0.642 | link_folder/人物/拿順.md |
| 3 | 猶大（雅各之子） | 0.638 | link_folder/人物/猶大（雅各之子）.md |
| 4 | 行軍次序 | 0.608 | link_folder/事件/行軍次序.md |
| 5 | 但支派 | 0.579 | link_folder/人物/但支派.md |

判定：✅ 建議使用既有條目 [[猶大支派]]（同名／字面對應）

## 流便（人物）
query:
- 待建立詞：流便
- 出現位置：民數記 第2章
- 候選類型：人物
- 本章上下文：v10「在南邊，按著軍隊是流便營的纛」；v16「凡屬流便營…共有十五萬一千四百五十名，要作第二隊往前行」。
CT：南邊——流便雖為長子，因犯罪失去長子名分，在此仍被安排為南營之首。
GT（精讀本）：南邊按行軍的方向來看指右邊，對希伯來人來講右邊意味著「力量」和「祝福」，可以理解為對以色列的長子流便的特殊照顧（出15:6; 傳10:2）。
GT（丁良才）：南邊有流便、西緬支派（就是利亞之長子和次子的後裔，這樣就使他們少生嫉妒猶大支派的心）並迦得支派（就是利亞之婢女悉帕之長子的後裔）。
KC：South side is literally 'the right side' — speaks in the Scriptures of dignity of position；主耶穌「坐在高天至大者的右邊」（來1:3; 8:1; 10:12; 12:2）；Reuben means 'see, a son' — believers come together who know that they are sons of God.
BH：Reuben was the firstborn of Jacob and Leah, yet his tribe is positioned on the south rather than the east, reflecting the loss of his birthright（創35:22, 49:3-4）。
- 經文用詞：流便營的纛

字面解析：對上既有「流便」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 流便 | 0.723 | link_folder/人物/流便.md |
| 2 | 便雅憫 | 0.632 | link_folder/人物/便雅憫.md |
| 3 | 迦得（萬幸） | 0.626 | link_folder/人物/迦得（萬幸）.md |
| 4 | 行軍次序 | 0.610 | link_folder/事件/行軍次序.md |
| 5 | 十二支派起源 | 0.607 | link_folder/神學/十二支派起源.md |

判定：✅ 建議使用既有條目 [[流便]]（同名／字面對應）

## 以法蓮（人物）
query:
- 待建立詞：以法蓮
- 出現位置：民數記 第2章
- 候選類型：人物
- 本章上下文：v18「在西邊，按著軍隊是以法蓮營的纛」；v24「凡屬以法蓮營…共有十萬零八千一百名，要作第三隊往前行」。
CT：西邊——以法蓮、瑪拿西、便雅憫都是同一個祖母（拉結）的子孫，他們在法櫃後行走（詩80:1-2）。
GT（精讀本）：西邊是帳幕的後邊，瑪拿西、便雅憫支派以以法蓮支派為中心安營；他們是拉結的子孫。
GT（丁良才）：以法蓮、瑪拿西、便雅憫都是同一個祖母（拉結）的子孫，他們在法櫃後行走；此處可解明詩80:1-2的話，這些支派所得的地都相連接。
KC：West side is literally 'side of the sea' — speaks of trials and difficulties in the life of the believer；in those trials they produce fruit for God（創1:20-23）；Ephraim means 'double fertility', an appropriate standard-bearer for the west side.
BH：Ephraim, younger son of Joseph, received greater blessing from Jacob（創48:19）；positioned on the west side alongside Manasseh and Benjamin, all descendants of Rachel.
- 經文用詞：以法蓮營的纛

字面解析：對上既有「以法蓮」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 以法蓮 | 0.793 | link_folder/人物/以法蓮.md |
| 2 | 瑪拿西 | 0.631 | link_folder/人物/瑪拿西.md |
| 3 | 十二支派起源 | 0.608 | link_folder/神學/十二支派起源.md |
| 4 | 便雅憫 | 0.607 | link_folder/人物/便雅憫.md |
| 5 | 西布倫（同住） | 0.592 | link_folder/人物/西布倫（同住）.md |

判定：✅ 建議使用既有條目 [[以法蓮]]（同名／字面對應）

## 但支派（人物）
query:
- 待建立詞：但支派
- 出現位置：民數記 第2章
- 候選類型：人物
- 本章上下文：v25「在北邊，按著軍隊是但營的纛」；v31「凡但營被數的，共有十五萬七千六百名，要歸本纛作末隊往前行」。
CT：北邊——但、亞設、拿弗他利三個支派殿後。
GT（精讀本）：北邊是在帳幕的周圍安置以色列各支派的陣營時最後提到的地方；除了猶大以外被數點的人數最多的但支派是勇敢的人群，擔負著守衛以色列陣營後方的重要任務。
GT（丁良才）：北邊——但支派是從拉結的婢女辟拉所生之長子的後裔，亞設支派是悉帕的後裔，拿弗他利是辟拉的後裔。
KC：The north side is the darkest side, furthest from the sun；north is literally 'hiding' — represents the gloomy side of the testimony of God on earth；Dan is called "a serpent" by Jacob（創49:17）；Danites have the doubtful honor of being first to introduce idolatry in Israel（士18:30）。
BH：Dan's role was on the north side, forming rear guard alongside Asher and Naphtali；Samson most famous member（士13-16）；notably absent from list of sealed tribes in Revelation 7:4-8.
- 經文用詞：但營的纛

字面解析：對上既有「但支派」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 但支派 | 0.763 | link_folder/人物/但支派.md |
| 2 | 但（審判） | 0.591 | link_folder/人物/但（審判）.md |
| 3 | 拿弗他利 | 0.578 | link_folder/人物/拿弗他利.md |
| 4 | 猶大支派 | 0.576 | link_folder/人物/猶大支派.md |
| 5 | 行軍次序 | 0.568 | link_folder/事件/行軍次序.md |

判定：✅ 建議使用既有條目 [[但支派]]（同名／字面對應）

## 以色列人的軍隊（神學）
query:
- 待建立詞：以色列人的軍隊
- 出現位置：民數記 第2章
- 候選類型：神學
- 本章上下文：全章按軍隊編排四營，每營三支派，各有首領、人數、行軍次序。
v9「要作第一隊往前行」；v16「要作第二隊往前行」；v24「要作第三隊往前行」；v31「要歸本纛作末隊往前行」。
CT：十二支派分作四組各占一個方位圍著會幕安營，形成十字隊形——十字架乃防守、禦敵之道，無懈可擊；會幕裡面的內容是十字架，安營的隊形也是十字架，裡外都是十字架。
GT（精讀本）：以色列百姓所要進行的戰爭是以建立神國度為目的的聖戰，而不是單單以掠奪和領土擴張為目的的戰爭；神是以色列的元帥，以色列百姓只要順服神的命令就能獲得勝利。
GT（串珠）：數以百萬計的以色列民，能夠有條不紊地安營和起行，在曠野中生活了四十年而蒙保守，都是因為神起初匠心的組織和編排；當神的子民以神為中心，按次序而行時（林前14:40），便能夠克服很多環境和人事的問題。
KC：The tribes must camp in relation to the tabernacle according to the wind directions；the four standards lie in four directions from which the influences come from outside and which the people of God must face in the power of Him Who dwells in their midst.
BH：The organization of the tribes around the Tabernacle has theological significance, symbolizing God's presence at the center of the Israelite community；each tribe's position and number were divinely ordained, emphasizing order and obedience.
- 經文用詞：照著軍隊安營、按著軍隊被數的

字面解析：對上既有「以色列人的軍隊」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 行軍次序 | 0.779 | link_folder/事件/行軍次序.md |
| 2 | 以色列人的軍隊 | 0.730 | link_folder/神學/以色列人的軍隊.md |
| 3 | 安營與纛 | 0.717 | link_folder/主題/安營與纛.md |
| 4 | 神的軍兵 | 0.603 | link_folder/神學/神的軍兵.md |
| 5 | 以色列人帶兵器 | 0.589 | link_folder/歷史/以色列人帶兵器.md |

判定：✅ 建議使用既有條目 [[以色列人的軍隊]]（同名／字面對應）

## 十二支派起源（神學）
query:
- 待建立詞：十二支派起源
- 出現位置：民數記 第2章
- 候選類型：神學
- 本章上下文：四營分組反映母系結構：東營（猶大、以薩迦、西布倫）皆利亞所生；南營（流便、西緬、迦得）利亞所生＋利亞婢女悉帕所生；西營（以法蓮、瑪拿西、便雅憫）皆拉結所生/孫；北營（但、亞設、拿弗他利）婢女所生（但、拿弗他利為拉結婢女辟拉所生，亞設為利亞婢女悉帕所生）。
GT（啟導本）：四組支派的排列和他們的母系有很大關係。
GT（丁良才）：南邊有流便、西緬支派（利亞之長子和次子的後裔，這樣就使他們少生嫉妒猶大支派的心）並迦得支派（利亞之婢女悉帕之長子的後裔）。
KC：Reuben and Simeon are the oldest sons of Leah；Levi is not numbered, in his place comes Gad, the first son of Zilpa, the maid of Leah；Ephraim, Manasseh, Benjamin are descendants of Rachel, Joseph represented by his two sons；Dan, Asher, Naphtali are all three sons of maids.
BH：The twelve tribes descended from sons of Jacob, each with distinct identity and role.

字面解析：對上既有「十二支派起源」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 十二支派起源 | 0.839 | link_folder/神學/十二支派起源.md |
| 2 | 利亞 | 0.664 | link_folder/人物/利亞.md |
| 3 | 拿弗他利 | 0.651 | link_folder/人物/拿弗他利.md |
| 4 | 猶大支派 | 0.642 | link_folder/人物/猶大支派.md |
| 5 | 利未 | 0.640 | link_folder/人物/利未.md |

判定：✅ 建議使用既有條目 [[十二支派起源]]（同名／字面對應）

## 十二族長協助數點（事件）
query:
- 待建立詞：十二族長協助數點
- 出現位置：民數記 第2章
- 候選類型：事件
- 本章上下文：本章重複第1章的十二族長名單，但按營盤方位分組排列（而非第1章的支派次序）。
v3-31 每支派均列出首領名字：拿順（猶大）、拿坦業（以薩迦）、以利押（西布倫）、以利蓿（流便）、示路蔑（西緬）、以利雅薩（迦得）、以利沙瑪（以法蓮）、迦瑪列（瑪拿西）、亞比但（便雅憫）、亞希以謝（但）、帕結（亞設）、亞希拉（拿弗他利）。
GT（精讀本）：首領名單與第1章相同，但排列次序按營盤方位而非出生順序。
KC：The leaders are the same as in Numbers 1, now arranged by camp positions.
- 經文用詞：作猶大人的首領、作以薩迦人的首領

字面解析：對上既有「十二族長協助數點」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 十二族長協助數點 | 0.755 | link_folder/事件/十二族長協助數點.md |
| 2 | 拿順 | 0.659 | link_folder/人物/拿順.md |
| 3 | 十二支派起源 | 0.658 | link_folder/神學/十二支派起源.md |
| 4 | 行軍次序 | 0.628 | link_folder/事件/行軍次序.md |
| 5 | 猶大支派 | 0.603 | link_folder/人物/猶大支派.md |

判定：✅ 建議使用既有條目 [[十二族長協助數點]]（同名／字面對應）

## 行軍次序（事件）
query:
- 待建立詞：行軍次序
- 出現位置：民數記 第2章
- 候選類型：事件
- 本章上下文：全章規定以色列全軍起行的先後次序。
v9「要作第一隊往前行」（猶大營：猶大、以薩迦、西布倫，186,400人）；
v16「要作第二隊往前行」（流便營：流便、西緬、迦得，151,450人）；
v17「隨後，會幕要往前行，有利未營在諸營中間」；
v24「要作第三隊往前行」（以法蓮營：以法蓮、瑪拿西、便雅憫，108,100人）；
v31「要歸本纛作末隊往前行」（但營：但、亞設、拿弗他利，157,600人）。
CT：猶大營擔任以色列全軍的開路先鋒，正面迎敵時首當其衝。
GT（精讀本）：猶大支派站在行軍行列的前面，預表耶穌作為全人類的救主和君王站在全人類的前面（約10:4）；屬於流便營的行進之前，革順的子孫和米拉利的子孫抬著帳幕往前行（民10:17-20）；屬於以法蓮營的在實際行軍時跟在抬聖物的利未人哥轄子孫的後面（民10:21）；但營擔負著守衛以色列陣營後方的重要任務。
GT（丁良才）：有利未營在諸營中間——就是哥轄族（民10:17註）；「他們怎樣安營，就怎樣往前行」（民10:11-28），這樣神的住處常在選民中間（參詩46:5）。
KC：First we talk about "camp", then "set out", but both actions take place in agreement with each other；both in worship and approaching God（camp）as well as in defense and protection（set out）it is about the relationship of God with His people.
BH：Judah's position as the first to set out underscores its leadership and preeminence among the tribes；being first implies a role of guidance and protection for the other tribes.
- 經文用詞：第一隊往前行、第二隊往前行、第三隊往前行、末隊往前行、安營起行

字面解析：對上既有「行軍次序」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 行軍次序 | 0.848 | link_folder/事件/行軍次序.md |
| 2 | 猶大支派 | 0.661 | link_folder/人物/猶大支派.md |
| 3 | 拔營起行 | 0.660 | link_folder/歷史/拔營起行.md |
| 4 | 安營與纛 | 0.652 | link_folder/主題/安營與纛.md |
| 5 | 以色列人的軍隊 | 0.640 | link_folder/神學/以色列人的軍隊.md |

判定：✅ 建議使用既有條目 [[行軍次序]]（同名／字面對應）

## 以薩迦（價值）（人物）
query:
- 待建立詞：以薩迦（價值）
- 出現位置：民數記 第2章
- 候選類型：人物
- 本章上下文：民2:5「挨著他安營的是以薩迦支派。有蘇押的兒子拿坦業作以薩迦人的首領」，v6 其軍隊54,400 名，隸屬東邊猶大營。CT 原文字義：「以薩迦」有價值；「蘇押」渺小；「拿坦業」神的賜予。CT 並指出猶大、以薩迦和西布倫三人都是同母兄弟，利亞所生（創35:23），三個支派在軍隊編組裡同屬最先起行的一組。BH 指出以薩迦以「通達時務」著稱（代上12:32），其地業在肥沃的耶斯列平原，並在士師記第五章支持底波拉與巴拉。

字面解析：對上既有「以薩迦（價值）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 以薩迦（價值） | 0.826 | link_folder/人物/以薩迦（價值）.md |
| 2 | 以薩迦（報酬） | 0.621 | link_folder/原文/以薩迦（報酬）.md |
| 3 | 西布倫（同住） | 0.609 | link_folder/人物/西布倫（同住）.md |
| 4 | 拿順 | 0.584 | link_folder/人物/拿順.md |
| 5 | 猶大支派 | 0.577 | link_folder/人物/猶大支派.md |

判定：✅ 建議使用既有條目 [[以薩迦（價值）]]（同名／字面對應）

## 西布倫（同住）（人物）
query:
- 待建立詞：西布倫（同住）
- 出現位置：民數記 第2章
- 候選類型：人物
- 本章上下文：民2:7「又有西布倫支派。希倫的兒子以利押作西布倫人的首領」，v8 其軍隊57,400 名，隸屬東邊猶大營。CT 原文字義：「西布倫」高貴的；「希倫」力量；「以利押」神是父。BH 指出西布倫的地業靠海、便於貿易，應驗雅各的預言「西布倫必住在海口，必成為停船的海口」（創49:13），並在士師記第四、五章出兵支持底波拉與巴拉。

字面解析：對上既有「西布倫（同住）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 西布倫（同住） | 0.798 | link_folder/人物/西布倫（同住）.md |
| 2 | 以法蓮 | 0.546 | link_folder/人物/以法蓮.md |
| 3 | 猶大支派 | 0.543 | link_folder/人物/猶大支派.md |
| 4 | 西珥 | 0.527 | link_folder/地點/西珥.md |
| 5 | 以東 | 0.525 | link_folder/地點/以東.md |

判定：✅ 建議使用既有條目 [[西布倫（同住）]]（同名／字面對應）

## 迦得（萬幸）（人物）
query:
- 待建立詞：迦得（萬幸）
- 出現位置：民數記 第2章
- 候選類型：人物
- 本章上下文：民2:14「又有迦得支派。丟珥的兒子以利雅薩作迦得人的首領」，v15 其軍隊45,650 名，隸屬南邊流便營。CT 原文字義：「迦得」軍隊；「丟珥」他們認識神；「以利雅薩」神已加添。CT 指出迦得和亞設同為悉帕所生（創35:26），卻在軍隊編組中分列不同的組。GT 丁良才說明南營的組成：流便、西緬是利亞之長子和次子的後裔，「這樣就使他們少生嫉妒猶大支派的心」，迦得則是利亞之婢女悉帕之長子的後裔。BH 指出迦得之名意為 fortune 或 troop，地業在約但河東的基列，以善戰著稱。

字面解析：對上既有「迦得（萬幸）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 迦得（萬幸） | 0.865 | link_folder/人物/迦得（萬幸）.md |
| 2 | 迦得（幸運） | 0.664 | link_folder/原文/迦得（幸運）.md |
| 3 | 亞設（有福） | 0.631 | link_folder/人物/亞設（有福）.md |
| 4 | 便雅憫 | 0.584 | link_folder/人物/便雅憫.md |
| 5 | 猶大支派 | 0.582 | link_folder/人物/猶大支派.md |

判定：✅ 建議使用既有條目 [[迦得（萬幸）]]（同名／字面對應）

## 亞設（有福）（人物）
query:
- 待建立詞：亞設（有福）
- 出現位置：民數記 第2章
- 候選類型：人物
- 本章上下文：民2:27「挨著他安營的是亞設支派。俄蘭的兒子帕結作亞設人的首領」，v28 其軍隊41,500 名，隸屬北邊但營。CT 原文字義：「亞設」快樂的；「俄蘭」憂慮的；「帕結」神的事件。CT 指出亞設和迦得同為悉帕所生，卻分列不同營。GT 丁良才說北營三支派中「亞設支派，是悉帕的後裔」。BH 指出亞設之名意為 happy／blessed，地業沿地中海岸富庶，應驗雅各的預言「亞設之地必出肥美的糧，且出君王的美味」（創49:20）。

字面解析：對上既有「亞設（有福）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 亞設（有福） | 0.827 | link_folder/人物/亞設（有福）.md |
| 2 | 迦得（萬幸） | 0.602 | link_folder/人物/迦得（萬幸）.md |
| 3 | 以法蓮 | 0.583 | link_folder/人物/以法蓮.md |
| 4 | 拿弗他利 | 0.548 | link_folder/人物/拿弗他利.md |
| 5 | 瑪拿西 | 0.546 | link_folder/人物/瑪拿西.md |

判定：✅ 建議使用既有條目 [[亞設（有福）]]（同名／字面對應）

## 瑪拿西（人物）
query:
- 待建立詞：瑪拿西
- 出現位置：民數記 第2章
- 候選類型：人物
- 本章上下文：民2:20「挨著他的是瑪拿西支派。比大蓿的兒子迦瑪列作瑪拿西人的首領」，v21 其軍隊32,200 名，隸屬西邊以法蓮營。CT 原文字義：「瑪拿西」導致遺忘；「比大蓿」磐石已贖回；「迦瑪列」神的獎勵；並指出以法蓮和瑪拿西同為約瑟的兒子，因約瑟得到長子雙份的特權，故同被升格成為兩個支派。GT《聖經精讀本》指出西邊是帳幕的後邊，瑪拿西、便雅憫支派以以法蓮支派為中心安營，他們是拉結的子孫。BH 指出迦瑪列之名意為「神是我的獎賞」，父名比大蓿意為「磐石已贖回」。

字面解析：對上既有「瑪拿西」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 瑪拿西 | 0.824 | link_folder/人物/瑪拿西.md |
| 2 | 以法蓮 | 0.685 | link_folder/人物/以法蓮.md |
| 3 | 十二支派起源 | 0.613 | link_folder/神學/十二支派起源.md |
| 4 | 收納以法蓮與瑪拿西 | 0.609 | link_folder/歷史/收納以法蓮與瑪拿西.md |
| 5 | 迦得（萬幸） | 0.600 | link_folder/人物/迦得（萬幸）.md |

判定：✅ 建議使用既有條目 [[瑪拿西]]（同名／字面對應）

## 便雅憫（人物）
query:
- 待建立詞：便雅憫
- 出現位置：民數記 第2章
- 候選類型：人物
- 本章上下文：民2:22「又有便雅憫支派。基多尼的兒子亞比但作便雅憫人的首領」，v23 其軍隊35,400 名，隸屬西邊以法蓮營。CT 原文字義：「便雅憫」右手之子；「基多尼」我的砍伐者；「亞比但」我父是公義；並指出便雅憫與以法蓮和瑪拿西同為拉結所出（創35:24）。GT 丁良才指出以法蓮、瑪拿西、便雅憫都是同一個祖母拉結的子孫，「他們在法櫃後行走」，此處可解明詩80:1-2 的話，而這些支派所得的地都相連接。BH 指出便雅憫日後出了以色列的第一位王掃羅（撒上9:1-2）與使徒保羅（腓3:5）。

字面解析：對上既有「便雅憫」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 便雅憫 | 0.774 | link_folder/人物/便雅憫.md |
| 2 | 以法蓮 | 0.627 | link_folder/人物/以法蓮.md |
| 3 | 十二支派起源 | 0.625 | link_folder/神學/十二支派起源.md |
| 4 | 猶大支派 | 0.608 | link_folder/人物/猶大支派.md |
| 5 | 迦得（萬幸） | 0.587 | link_folder/人物/迦得（萬幸）.md |

判定：✅ 建議使用既有條目 [[便雅憫]]（同名／字面對應）

## 西緬（人物）
query:
- 待建立詞：西緬
- 出現位置：民數記 第2章
- 候選類型：人物
- 本章上下文：民2:12「挨著他安營的是西緬支派。蘇利沙代的兒子示路蔑作西緬人的首領」，v13 其軍隊59,300 名，隸屬南邊流便營。CT 原文字義：「西緬」聽見；「蘇利沙代」我的磐石是全能的；「示路蔑」神的朋友；並指出西緬是雅各的次子，與流便同為母親利亞所生。BH 給示路蔑的字義是「神的朋友」或「與神和好」，父名蘇利沙代意為「我的磐石是全能者」；並指出西緬支派的地業落在猶大境內（書19:1-9），後來逐漸併入猶大。

字面解析：對上既有「西緬」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 西緬 | 0.679 | link_folder/人物/西緬.md |
| 2 | 西布倫（同住） | 0.624 | link_folder/人物/西布倫（同住）.md |
| 3 | 「西緬」名字含義 | 0.599 | link_folder/原文/「西緬」名字含義.md |
| 4 | 猶大支派 | 0.565 | link_folder/人物/猶大支派.md |
| 5 | 迦得（萬幸） | 0.565 | link_folder/人物/迦得（萬幸）.md |

判定：✅ 建議使用既有條目 [[西緬]]（同名／字面對應）

## 拿弗他利（人物）
query:
- 待建立詞：拿弗他利
- 出現位置：民數記 第2章
- 候選類型：人物
- 本章上下文：民2:29「又有拿弗他利支派。以南的兒子亞希拉作拿弗他利人的首領」，v30 其軍隊53,400 名，隸屬北邊但營。CT 原文字義：「拿弗他利」摔角；「以南」有眼睛；「亞希拉」我兄弟是惡毒的；並指出拿弗他利和但兩兄弟為同母辟拉所生（創35:25）。GT 丁良才指出北營中「拿弗他利是辟拉的後裔」。BH 指出拿弗他利的地業在迦南北部靠加利利海，日後正是耶穌大部分傳道工作所在，應驗以賽亞書9:1-2 的預言。

字面解析：對上既有「拿弗他利」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 拿弗他利 | 0.796 | link_folder/人物/拿弗他利.md |
| 2 | 但支派 | 0.592 | link_folder/人物/但支派.md |
| 3 | 拿鶴 | 0.562 | link_folder/人物/拿鶴.md |
| 4 | 拿順 | 0.560 | link_folder/人物/拿順.md |
| 5 | 以法蓮 | 0.551 | link_folder/人物/以法蓮.md |

判定：✅ 建議使用既有條目 [[拿弗他利]]（同名／字面對應）

## 拿順（人物）
query:
- 待建立詞：拿順
- 出現位置：民數記 第2章
- 候選類型：人物
- 本章上下文：民2:3「有亞米拿達的兒子拿順作猶大人的首領」，猶大營居東、作第一隊往前行。CT 原文字義作「男巫」，並指出拿順是亞倫的妻兄（出6:23），也是大衛的先祖。KC 指出在馬太福音第一章的家譜裡，這位支派首領拿順被列在主耶穌的祖先之中（太1:4）。BH 補上一層姻親關係：亞米拿達的女兒以利沙巴嫁給了首任大祭司亞倫，因此拿順這一支同時牽著王室與祭司兩條線，最終在基督身上合一——祂既是君王也是大祭司。STEP 顯示本節的「首領」是 נָשִׂיא（na.si，H5387A，詞典義 leader）。
- 經文用詞：拿順

字面解析：對上既有「拿順」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 拿順 | 0.857 | link_folder/人物/拿順.md |
| 2 | 亞倫的祭司譜系 | 0.626 | link_folder/人物/亞倫的祭司譜系.md |
| 3 | 十二族長協助數點 | 0.598 | link_folder/事件/十二族長協助數點.md |
| 4 | 猶大支派 | 0.583 | link_folder/人物/猶大支派.md |
| 5 | 以利亞撒 | 0.575 | link_folder/人物/以利亞撒.md |

判定：✅ 建議使用既有條目 [[拿順]]（同名／字面對應）

## 神的同在（神學）
query:
- 待建立詞：神的同在
- 出現位置：民數記 第2章
- 候選類型：神學
- 本章上下文：民2:2「對著會幕的四圍安營」、v17「隨後，會幕要往前行，有利未營在諸營中間」——全營以會幕為幾何與屬靈中心。CT〔靈意註解〕：「以會幕為中心，表徵以基督為中心，全軍在基督的率領之下」，並說「神以會幕為中心安置以色列各支派的營，這象徵神作為以色列真正的統治者，臨在於他們的生活中」。GT《聖經精讀本》同語：人存在的價值和意義「是把神迎接在自己的生活中心裡」。GT 丁良才在 v34 歸納會幕在以色列人當中的三樣教訓：「（一）神與人同在，（二）都當倚靠神，（三）都可親近神。」KC：戰事的一切都圍繞著會幕，它是軍隊的中心。BH 指出會幕居中意味著神的同在對每個支派同樣可及。

字面解析：對上既有「神的同在」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 神的同在 | 0.720 | link_folder/神學/神的同在.md |
| 2 | 神住在人間 | 0.682 | link_folder/神學/神住在人間.md |
| 3 | 會幕（帳幕整體） | 0.660 | link_folder/主題/會幕（帳幕整體）.md |
| 4 | 安營與纛 | 0.647 | link_folder/主題/安營與纛.md |
| 5 | 舍吉拿（shekinah） | 0.616 | link_folder/原文/舍吉拿（shekinah）.md |

判定：✅ 建議使用既有條目 [[神的同在]]（同名／字面對應）

## 六十萬人的數目（解經爭議）
query:
- 待建立詞：六十萬人的數目
- 出現位置：民數記 第2章
- 候選類型：解經爭議
- 本章上下文：民2:32 重述總數603,550。GT《舊約聖經背景註釋》在【民二3～32 統計的人數】給出本章特有的一種讀法：「由於希伯來語的「千」字（'lp）的寫法和譯作「軍事部隊」的字眼相同，「七萬四千六百名」（4節）也可譯作「七十四個部隊，（共）六百人」。第32節的總數，本來則是五百九十八個部隊（'lp），五千（'lp）五百人。經文在抄寫傳遞之時，這兩個字可能發生混淆，加在一起成為「六百零三千」（即六十萬三千）。這解釋若對，則以色列出埃及的人數大約有二萬。」這是把本章逐營數字當成論證材料的具體算法。

字面解析：對上既有「六十萬人的數目」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 六十萬人的數目 | 0.733 | link_folder/解經爭議/六十萬人的數目.md |
| 2 | 六十萬零三千五百五十人（出38：26） | 0.646 | link_folder/事件/六十萬零三千五百五十人（出38：26）.md |
| 3 | 出埃及 | 0.599 | link_folder/歷史/出埃及.md |
| 4 | 兩次普查的關係 | 0.583 | link_folder/解經爭議/兩次普查的關係.md |
| 5 | 數點民數 | 0.568 | link_folder/事件/數點民數.md |

判定：✅ 建議使用既有條目 [[六十萬人的數目]]（同名／字面對應）

## 六十萬零三千五百五十人（出38：26）（事件）
query:
- 待建立詞：六十萬零三千五百五十人（出38：26）
- 出現位置：民數記 第2章
- 候選類型：事件
- 本章上下文：民2:32「這些以色列人，照他們的宗族，按他們的軍隊，在諸營中被數的，共有六十萬零三千五百五十名」——與民1:46 及出38:26 同數。CT 指出這是四個營加起來的總數（參9、16、24、31節），而「宗族」指十二支派、「軍隊」指猶大、流便、以法蓮、但四個營。KC 指出民數記第一章提到的戰士數目在此重複，並且與各支派相符：每個戰士都在自己的支派裡就了位，每個支派也都按神所指定的纛在會幕前站定了自己的位置。

字面解析：對上既有「六十萬零三千五百五十人（出38：26）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 六十萬零三千五百五十人（出38：26） | 0.759 | link_folder/事件/六十萬零三千五百五十人（出38：26）.md |
| 2 | 以色列人的軍隊 | 0.641 | link_folder/神學/以色列人的軍隊.md |
| 3 | 數點民數 | 0.637 | link_folder/事件/數點民數.md |
| 4 | 行軍次序 | 0.626 | link_folder/事件/行軍次序.md |
| 5 | 六十萬人的數目 | 0.619 | link_folder/解經爭議/六十萬人的數目.md |

判定：✅ 建議使用既有條目 [[六十萬零三千五百五十人（出38：26）]]（同名／字面對應）

## 候選互查（本章內部，⚠＝彼此相似 ≥ 0.8）
兩個候選可能是同一概念——考慮合併成一個候選（另一個用 surfaces 涵蓋），
或確認確為兩個條目再照建：
- 0.870 ⚠ 利未支派 ↔ 會幕（帳幕整體）
- 0.844 ⚠ 會幕（帳幕整體） ↔ 神的同在
