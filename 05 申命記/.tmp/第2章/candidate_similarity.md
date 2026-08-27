<!-- candidate_similarity_meta
schema_version: 1
book: 申命記
chapter: 2
candidate_sha256: af07b40a72790e583686299de6c5f616a1bb200c9951aaa85bab5ca215dd9c32
embedding_model: nvidia/nemotron-3-embed-1b
embedding_index_fingerprint: d701a55b5768b76c
link_index_sha256: 4f619b2576f2fa9a6466d3ca640194b9f9d766bfb3517e3e0c4cedae2da63338
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

# 候選語義近鄰報告：申命記 第2章

- 檢索模型：nvidia/nemotron-3-embed-1b｜重排模型：nvidia/llama-nemotron-rerank-vl-1b-v2:free（未校準/保守模式）｜全庫 2887 條
- 規則說明：字面確切匹配直接通過；其餘候選先檢索 Top 20 名再由 Reranker 重排，取前 5 名顯示。
  治理優先：同名歧義（D類）與分類不相容永遠標 ⚠。
  重排模型未校準時，⚠ 由檢索相似度規則（≥0.50 且 top-1 非同實體）決定，重排名次只當附加證據。
  字面解析：列 resolver 實際比對結果——標「請確認」者務必人工核實。

## 海（紅海）（地點）
query:
- 待建立詞：海（紅海）
- 出現位置：申命記 第2章
- 候選類型：地點
- 本章上下文：v1「從紅海的路往曠野去」。CT：「『從紅海的路』指取道阿卡巴灣」；GT《啟導本》：「“紅海”當指阿卡巴灣」；BH：「The Red Sea, or Yam Suph, is significant as it was the site of God's miraculous deliverance of Israel from Egypt」。
- 經文用詞：紅海

字面解析：對上既有「海（紅海）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 海（紅海） | 0.742 | link_folder/地點/海（紅海）.md |
| 2 | 紅海曠野 | 0.697 | link_folder/地點/紅海曠野.md |
| 3 | 紅海指的是哪個海 | 0.669 | link_folder/解經爭議/紅海指的是哪個海.md |
| 4 | 詩一零六9 紅海乾地 | 0.583 | link_folder/互文/詩一零六9 紅海乾地.md |
| 5 | 過紅海 | 0.582 | link_folder/歷史/過紅海.md |

判定：✅ 建議使用既有條目 [[海（紅海）]]（同名／字面對應）

## 西珥山（地點）
query:
- 待建立詞：西珥山
- 出現位置：申命記 第2章
- 候選類型：地點
- 本章上下文：v1「我們在西珥山繞行了許多日子」；v5「因我已將西珥山賜給以掃為業」。CT：「『西珥山』在死海的南邊，屬於以東地」；GT《聖經精讀本》：「西珥山: 在這裡並非指某一特定的山,乃是指整個以東山地」。STEP 顯示 v5 是 har se.'Ir（H2022G＋H8165G），簡要詞典義 (Mount) Seir。

字面解析：對上既有「西珥山」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 西珥山 | 0.765 | link_folder/地點/西珥山.md |
| 2 | 西珥 | 0.647 | link_folder/地點/西珥.md |
| 3 | 西乃山 | 0.549 | link_folder/地點/西乃山.md |
| 4 | 何珥山 | 0.547 | link_folder/地點/何珥山.md |
| 5 | 何烈山 | 0.544 | link_folder/地點/何烈山.md |

判定：✅ 建議使用既有條目 [[西珥山]]（同名／字面對應）

## 曠野飄流四十年（歷史）
query:
- 待建立詞：曠野飄流四十年
- 出現位置：申命記 第2章
- 候選類型：歷史
- 本章上下文：v1「繞行了許多日子」；v7「這四十年，耶和華─你的神常與你同在」；v14「共有三十八年」。GT《聖經精讀本》：「許多日子: 指加低斯巴尼亞探子事件之後的38年」；KC：「in a single sentence, this is indicated: they circled Mountain Seir “for many days” – every day of the thirty-eight years is felt」。STEP 顯示 v7 是 'ar.ba.'Im sha.Nah（H705＋H8141）。

字面解析：對上既有「曠野飄流四十年」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 曠野飄流四十年 | 0.651 | link_folder/歷史/曠野飄流四十年.md |
| 2 | 四十的屬靈意義 | 0.649 | link_folder/原文/四十的屬靈意義.md |
| 3 | 你一無所缺 | 0.606 | link_folder/主題/你一無所缺.md |
| 4 | 三十八年與那世代的兵丁滅盡 | 0.580 | link_folder/歷史/三十八年與那世代的兵丁滅盡.md |
| 5 | 十一天的路程 | 0.577 | link_folder/主題/十一天的路程.md |

判定：✅ 建議使用既有條目 [[曠野飄流四十年]]（同名／字面對應）

## 以掃（人物）
query:
- 待建立詞：以掃
- 出現位置：申命記 第2章
- 候選類型：人物
- 本章上下文：v4「你們弟兄以掃的子孫住在西珥」；v5「因我已將西珥山賜給以掃為業」。CT：「『以掃的子孫』即指以東人(參創三十六8)」；CT 原文字義：「以掃」多毛的；v22 註「以掃」(與「西珥」同義不同字)。STEP 顯示是 le./'e.Sav（H6215H）。

字面解析：對上既有「以掃」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 西珥 | 0.645 | link_folder/地點/西珥.md |
| 2 | 西珥山 | 0.636 | link_folder/地點/西珥山.md |
| 3 | 申命記2章西珥賜給以掃 | 0.633 | link_folder/互文/申命記2章西珥賜給以掃.md |
| 4 | 以東 | 0.609 | link_folder/地點/以東.md |
| 5 | 以掃 | 0.608 | link_folder/人物/以掃.md |

判定：✅ 建議使用既有條目 [[以掃]]（同名／字面對應）

## 以東（地點）
query:
- 待建立詞：以東
- 出現位置：申命記 第2章
- 候選類型：地點
- 本章上下文：v4-8 以色列繞過以掃子孫之地。GT《雷氏研讀本》：「“以掃”的後裔獲賜“西珥山”（整個以東地帶，死海以南的多山地帶；參看創三六6～8）為產業」；BH：「Seir is a mountainous region located southeast of the Dead Sea」。

字面解析：對上既有「以東」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 西珥山 | 0.749 | link_folder/地點/西珥山.md |
| 2 | 西珥 | 0.704 | link_folder/地點/西珥.md |
| 3 | 以東 | 0.671 | link_folder/地點/以東.md |
| 4 | 申命記2章西珥賜給以掃 | 0.590 | link_folder/互文/申命記2章西珥賜給以掃.md |
| 5 | 神對以掃的地業安排 | 0.583 | link_folder/神學/神對以掃的地業安排.md |

判定：✅ 建議使用既有條目 [[以東]]（同名／字面對應）

## 為業（ye.ru.shah）（原文）
query:
- 待建立詞：為業（ye.ru.shah）
- 出現位置：申命記 第2章
- 候選類型：原文
- 本章上下文：v5「因我已將西珥山賜給以掃為業」；v9「因我已將亞珥賜給羅得的子孫為業」（本節出現兩次）；v12「耶和華賜給他為業之地」；v19「亞捫人的地，我不賜給你們為業」。STEP 顯示這幾處是 ye.ru.Shah（H3425），簡要詞典義 possession；v24「得他的地為業」則是動詞 Rash（H3423H ya.rash，簡要詞典義 to possess: take），與名詞同一字根。KC：「God also has His involvement with these other peoples. He also gave the nations land (verses 9,19).」
- 經文用詞：為業

字面解析：對上既有「為業（ye.ru.shah）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 為業（ye.ru.shah） | 0.848 | link_folder/原文/為業（ye.ru.shah）.md |
| 2 | 這地必落給你們為業（na.phal） | 0.581 | link_folder/原文/這地必落給你們為業（na.phal）.md |
| 3 | 業地（a.chuz.zah） | 0.577 | link_folder/原文/業地（a.chuz.zah）.md |
| 4 | 不可擾害也不可爭戰（tsur、garah） | 0.555 | link_folder/原文/不可擾害也不可爭戰（tsur、garah）.md |
| 5 | 起首得那地（cha.lal） | 0.531 | link_folder/原文/起首得那地（cha.lal）.md |

判定：✅ 建議使用既有條目 [[為業（ye.ru.shah）]]（同名／字面對應）

## 不可擾害也不可爭戰（tsur、garah）（原文）
query:
- 待建立詞：不可擾害也不可爭戰（tsur、garah）
- 出現位置：申命記 第2章
- 候選類型：原文
- 本章上下文：v5「不可與他們爭戰」；v9「不可擾害摩押人，也不可與他們爭戰」；v19「不可擾害他們，也不可與他們爭戰」。CT 原文字義：「擾害」圍攻，封鎖。STEP 顯示「擾害」是 ta.tzar（H6696B tsur，簡要詞典義 to provoke）、「爭戰」是 tit.ga.Ru／tit.Gar（H1624 ga.rah，簡要詞典義 to stir up，Hithpael），v9、v19、v24 另帶 mil.cha.Mah（H4421 battle）。同一個 ga.rah 在 v24 反過來用成命令：「你要與他爭戰」（ve./hit.Gar）。
- 經文用詞：擾害

字面解析：對上既有「不可擾害也不可爭戰（tsur、garah）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 不可擾害也不可爭戰（tsur、garah） | 0.782 | link_folder/原文/不可擾害也不可爭戰（tsur、garah）.md |
| 2 | 擾害（tsa.rar） | 0.607 | link_folder/原文/擾害（tsa.rar）.md |
| 3 | 咒詛（a.rar 與 qa.vav） | 0.495 | link_folder/原文/咒詛（a.rar 與 qa.vav）.md |
| 4 | 起首得那地（cha.lal） | 0.489 | link_folder/原文/起首得那地（cha.lal）.md |
| 5 | 使天下萬民驚恐懼怕 | 0.481 | link_folder/原文/使天下萬民驚恐懼怕.md |

判定：✅ 建議使用既有條目 [[不可擾害也不可爭戰（tsur、garah）]]（同名／字面對應）

## 腳掌可踏之處（原文）
query:
- 待建立詞：腳掌可踏之處
- 出現位置：申命記 第2章
- 候選類型：原文
- 本章上下文：v5「他們的地，連腳掌可踏之處，我都不給你們」。CT 原文字義：「可踏之處」踏腳之地，踏板；CT：「『腳掌可踏之處』形容寸土之地」；BH：「not even a footprint⋯underscores the absolute nature of God's command」。STEP 顯示是 'ad mid.Rakh kaf- Ra.gel（H4096 mid.rakh「treading」＋H3709H kaph「palm: sole」＋H7272 re.gel「foot」）。
- 經文用詞：連腳掌可踏之處

字面解析：對上既有「腳掌可踏之處」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 腳掌可踏之處 | 0.820 | link_folder/原文/腳掌可踏之處.md |
| 2 | 屬我的子民 | 0.443 | link_folder/神學/屬我的子民.md |
| 3 | 山腳 | 0.438 | link_folder/地點/山腳.md |
| 4 | 連一蹄也不留下 | 0.437 | link_folder/神學/連一蹄也不留下.md |
| 5 | 這地必落給你們為業（na.phal） | 0.432 | link_folder/原文/這地必落給你們為業（na.phal）.md |

判定：✅ 建議使用既有條目 [[腳掌可踏之處]]（同名／字面對應）

## 用錢買糧買水（主題）
query:
- 待建立詞：用錢買糧買水
- 出現位置：申命記 第2章
- 候選類型：主題
- 本章上下文：v6「你們要用錢向他們買糧吃，也要用錢向他們買水喝」；v28「你可以賣糧給我吃，也可以賣水給我喝」。CT 原文字義：「買(首字)」買穀物；「買(次字)」藉交易而獲得；CT：「『用錢…買』意指不可搶奪」；GT《聖經精讀本》：「本節是指以色列在通過以東地時不可像侵略者那樣無禮妄動,乃要像路過的旅人一樣彬彬有禮」；KC：「If Israel were to ask Esau's favor, they should not beg for it, but pay for it.」；BH：「The command to pay in silver reflects a principle of justice and integrity」。
- 經文用詞：用錢

字面解析：對上既有「用錢買糧買水」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 用錢買糧買水 | 0.862 | link_folder/主題/用錢買糧買水.md |
| 2 | 古埃及銀子交易 | 0.538 | link_folder/文化/古埃及銀子交易.md |
| 3 | 出埃及時取得埃及財物 | 0.529 | link_folder/解經爭議/出埃及時取得埃及財物.md |
| 4 | 你一無所缺 | 0.526 | link_folder/主題/你一無所缺.md |
| 5 | 埃及人給以色列人財物 | 0.513 | link_folder/歷史/埃及人給以色列人財物.md |

判定：✅ 建議使用既有條目 [[用錢買糧買水]]（同名／字面對應）

## 你一無所缺（主題）
query:
- 待建立詞：你一無所缺
- 出現位置：申命記 第2章
- 候選類型：主題
- 本章上下文：v7「這四十年，耶和華─你的神常與你同在，故此你一無所缺」。CT：「『一無所缺』指供應生活所需，充分有餘」；GT《聖經精讀本》：「即使是這曠野40年的流浪期是懲罰其叛逆與不信的時期,但這並不是為懲罰,乃是磨練並養育自己百姓」；KC：「In spite of all the grumbling and complaint, God had been with them, and they did not lack anything (Lk 22:35).」STEP 顯示是 lo' cha.Sar.ta da.Var（H2637 cha.ser「to lack」＋H1697I davar「word: thing」），字面是「你未曾缺過一件東西」。

字面解析：對上既有「你一無所缺」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 你一無所缺 | 0.821 | link_folder/主題/你一無所缺.md |
| 2 | 四十的屬靈意義 | 0.530 | link_folder/原文/四十的屬靈意義.md |
| 3 | 神的供應 | 0.530 | link_folder/主題/神的供應.md |
| 4 | 曠野飄流四十年 | 0.527 | link_folder/歷史/曠野飄流四十年.md |
| 5 | 奉獻過剩與節制 | 0.502 | link_folder/神學/奉獻過剩與節制.md |

判定：✅ 建議使用既有條目 [[你一無所缺]]（同名／字面對應）

## 神所定的邊界（神學）
query:
- 待建立詞：神所定的邊界
- 出現位置：申命記 第2章
- 候選類型：神學
- 本章上下文：v5、v9、v19 三次說「我不賜給你們為業，因我已將⋯賜給⋯為業」。KC：「From this they can see that God governs everything and gives each nation its own place to live (Deu 32:8; Acts 17:26).」；GT《聖經精讀本》：「神根據對此三個民族(以東、摩押、亞捫)的祖先,即以掃與羅得的憐恤與應許而保護了他們。由此可知,自在永在者神之應許的不變與信實」；BH：「This highlights God's faithfulness to His promises and His orderly distribution of land」；CT：「神的兒女要知道自己的地界，不能羨慕別人，也不該妒忌別人為甚麼先得了地上的成就」。

字面解析：對上既有「神所定的邊界」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 神所定的邊界 | 0.760 | link_folder/神學/神所定的邊界.md |
| 2 | 為業（ye.ru.shah） | 0.639 | link_folder/原文/為業（ye.ru.shah）.md |
| 3 | 不可擾害也不可爭戰（tsur、garah） | 0.618 | link_folder/原文/不可擾害也不可爭戰（tsur、garah）.md |
| 4 | 屬我的子民 | 0.617 | link_folder/神學/屬我的子民.md |
| 5 | 四界與亞伯拉罕之約的落差 | 0.591 | link_folder/解經爭議/四界與亞伯拉罕之約的落差.md |

判定：✅ 建議使用既有條目 [[神所定的邊界]]（同名／字面對應）

## 亞拉巴（地點）
query:
- 待建立詞：亞拉巴
- 出現位置：申命記 第2章
- 候選類型：地點
- 本章上下文：v8「從亞拉巴的路，經過以拉他、以旬迦別」。CT：「『從亞拉巴的路』另譯「取道低谷」」；GT《啟導本》：「以拉他和以旬迦別為“亞拉巴路”的起點，在阿卡巴灣的頂端。此路始于阿卡巴灣，向北伸延，直到摩押地的東部」；BH：「The Arabah is a desert region extending from the Dead Sea to the Gulf of Aqaba」。

字面解析：對上既有「亞拉巴」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 亞拉巴 | 0.767 | link_folder/地點/亞拉巴.md |
| 2 | 以拉他 | 0.700 | link_folder/地點/以拉他.md |
| 3 | 以旬迦別 | 0.543 | link_folder/地點/以旬迦別.md |
| 4 | 亞羅珥 | 0.519 | link_folder/地點/亞羅珥.md |
| 5 | 鹽海 | 0.503 | link_folder/地點/鹽海.md |

判定：✅ 建議使用既有條目 [[亞拉巴]]（同名／字面對應）

## 以拉他（地點）
query:
- 待建立詞：以拉他
- 出現位置：申命記 第2章
- 候選類型：地點
- 本章上下文：v8「經過以拉他、以旬迦別」。CT 原文字義：「以拉他」高聳的樹叢；GT《聖經精讀本》：「以拉他,以旬迦別: 是位於紅海最北端的兩個港口城市,出了埃及的以色列曾先後三次路經此地,以戰略要地著稱」；BH：「Elath and Ezion-geber were significant port cities at the northern tip of the Gulf of Aqaba, known for trade and commerce」。
- 經文用詞：以拉他

字面解析：對上既有「以拉他」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 以拉他 | 0.827 | link_folder/地點/以拉他.md |
| 2 | 以旬迦別 | 0.642 | link_folder/地點/以旬迦別.md |
| 3 | 海（紅海） | 0.526 | link_folder/地點/海（紅海）.md |
| 4 | 以倘 | 0.521 | link_folder/地點/以倘.md |
| 5 | 亞拉巴 | 0.517 | link_folder/地點/亞拉巴.md |

判定：✅ 建議使用既有條目 [[以拉他]]（同名／字面對應）

## 以旬迦別（地點）
query:
- 待建立詞：以旬迦別
- 出現位置：申命記 第2章
- 候選類型：地點
- 本章上下文：v8「經過以拉他、以旬迦別」。CT 原文字義：「以旬迦別」人的骨幹；GT《聖經精讀本》：「尤其是“以旬迦別”具有“人的背脊之骨”,似乎是因其高低不平的地形而來」。

字面解析：對上既有「以旬迦別」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 以旬迦別 | 0.655 | link_folder/地點/以旬迦別.md |
| 2 | 以拉他 | 0.553 | link_folder/地點/以拉他.md |
| 3 | 西珥 | 0.502 | link_folder/地點/西珥.md |
| 4 | 示劍名字含義 | 0.502 | link_folder/原文/示劍名字含義.md |
| 5 | 高原（Shephelah） | 0.501 | link_folder/地點/高原（Shephelah）.md |

判定：✅ 建議使用既有條目 [[以旬迦別]]（同名／字面對應）

## 摩押地（地點）
query:
- 待建立詞：摩押地
- 出現位置：申命記 第2章
- 候選類型：地點
- 本章上下文：v8「轉向摩押曠野的路去」；v18「你今天要從摩押的境界亞珥經過」。CT：「『摩押曠野的路』摩押曠野是在摩押地的東邊(參民二十一11)」；BH：「The Wilderness of Moab refers to the region east of the Dead Sea, inhabited by the Moabites, descendants of Lot (Genesis 19:37)」。
- 經文用詞：摩押曠野、摩押的境界

字面解析：對上既有「摩押地」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 摩押地 | 0.705 | link_folder/地點/摩押地.md |
| 2 | 摩押 | 0.640 | link_folder/人物/摩押.md |
| 3 | 摩押人 | 0.612 | link_folder/人物/摩押人.md |
| 4 | 摩押平原 | 0.580 | link_folder/地點/摩押平原.md |
| 5 | 曠野 | 0.573 | link_folder/地點/曠野.md |

判定：✅ 建議使用既有條目 [[摩押地]]（同名／字面對應）

## 摩押人（人物）
query:
- 待建立詞：摩押人
- 出現位置：申命記 第2章
- 候選類型：人物
- 本章上下文：v9「不可擾害摩押人」；v11「摩押人稱他們為以米人」；v29「住亞珥的摩押人待我一樣」。CT：「『摩押人』是亞伯拉罕的侄兒羅得與他長女亂倫所生的子孫(參創十九36~37)，和以色列人有血緣關係」；GT《聖經精讀本》：「值得一提的是,日後成為大衛與基督的直系祖先路得是摩押女子(得1:4)」。

字面解析：對上既有「摩押人」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 摩押 | 0.755 | link_folder/人物/摩押.md |
| 2 | 摩押人 | 0.751 | link_folder/人物/摩押人.md |
| 3 | 「摩押」名字含義 | 0.692 | link_folder/原文/「摩押」名字含義.md |
| 4 | 羅得 | 0.642 | link_folder/人物/羅得.md |
| 5 | 亞捫人 | 0.641 | link_folder/人物/亞捫人.md |

判定：✅ 建議使用既有條目 [[摩押人]]（同名／字面對應）

## 羅得（人物）
query:
- 待建立詞：羅得
- 出現位置：申命記 第2章
- 候選類型：人物
- 本章上下文：v9、v19「因我已將⋯賜給羅得的子孫為業」。CT 原文字義：「羅得」遮蓋住；KC：「The LORD reminds of their origin by calling them “the sons of Lot”.」STEP 顯示是 li/v.nei- Lot（H1121G＋H3876）。

字面解析：對上既有「羅得」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 羅得 | 0.650 | link_folder/人物/羅得.md |
| 2 | 便亞米 | 0.501 | link_folder/人物/便亞米.md |
| 3 | 羅得女兒亂倫敘事是否表示贊同 | 0.495 | link_folder/解經爭議/羅得女兒亂倫敘事是否表示贊同.md |
| 4 | 「便亞米」名字含義 | 0.494 | link_folder/原文/「便亞米」名字含義.md |
| 5 | 羅得的兩個女兒 | 0.493 | link_folder/人物/羅得的兩個女兒.md |

判定：✅ 建議使用既有條目 [[羅得]]（同名／字面對應）

## 亞珥（地點）
query:
- 待建立詞：亞珥
- 出現位置：申命記 第2章
- 候選類型：地點
- 本章上下文：v9「因我已將亞珥賜給羅得的子孫為業」；v18「從摩押的境界亞珥經過」；v29「住亞珥的摩押人」。CT 原文字義：「亞珥」城市；CT：「『亞珥』是當時摩押的首邑，用來代表摩押地」；GT《啟導本》：「亞珥當為摩押的首邑（現在用以代表摩押人所居之地）。亞珥稱確切位置不詳。從18節看，其城或在亞嫩河谷」；GT《聖經精讀本》v36 註：「谷中的城: 指位於亞嫩谷(形成摩押與亞捫之界的山谷)中間的摩押之都“亞珥”」。STEP 顯示是 'ar（H6144）。
- 經文用詞：亞珥

字面解析：對上既有「亞珥」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 亞珥 | 0.914 | link_folder/地點/亞珥.md |
| 2 | 亞羅珥 | 0.712 | link_folder/地點/亞羅珥.md |
| 3 | 亞嫩河 | 0.650 | link_folder/地點/亞嫩河.md |
| 4 | 摩押 | 0.635 | link_folder/人物/摩押.md |
| 5 | 摩押地 | 0.625 | link_folder/地點/摩押地.md |

判定：✅ 建議使用既有條目 [[亞珥]]（同名／字面對應）

## 以米人（人物）
query:
- 待建立詞：以米人
- 出現位置：申命記 第2章
- 候選類型：人物
- 本章上下文：v10「先前，有以米人住在那裡，民數眾多，身體高大，像亞衲人一樣」；v11「摩押人稱他們為以米人」。CT 原文字義：「以米」恐怖；GT《聖經精讀本》：「以米人: “以米”具有“可怕”、“可畏”之意,似乎因他們像亞衲族(1:28)一樣身長力壯而來」；GT《啟導本》：「《創世記》十四5說以米人本來住在亞嫩河北摩押地的沙微基列亭」；KC：「The Moabites called the inhabitants “Emim”, which means “terrible” or “frightening”.」

字面解析：對上既有「以米人」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 以米人 | 0.882 | link_folder/人物/以米人.md |
| 2 | 利乏音人 | 0.661 | link_folder/人物/利乏音人.md |
| 3 | 散送冥 | 0.627 | link_folder/人物/散送冥.md |
| 4 | 亞衲族與偉人拿非林 | 0.617 | link_folder/背景/亞衲族與偉人拿非林.md |
| 5 | 摩押人 | 0.591 | link_folder/人物/摩押人.md |

判定：✅ 建議使用既有條目 [[以米人]]（同名／字面對應）

## 利乏音人（人物）
query:
- 待建立詞：利乏音人
- 出現位置：申命記 第2章
- 候選類型：人物
- 本章上下文：v11「也算為利乏音人」；v20「那地也算為利乏音人之地」。CT 原文字義：「利乏音」巨人；GT《啟導本》：「“利乏音人”不是一個民族的稱號，而是以色列人入居迦南前住在巴勒斯坦一帶傳統英雄人物的統稱，其人身材特高且強壯。摩押人稱他們為“以米人”（創十四5）；猶大人稱他們為亞衲人（民十三33；士一20）；亞捫人叫他們做散送冥（20節）」；BH：「The Rephaim were a group of ancient people known for their great size and strength」。

字面解析：對上既有「利乏音人」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 利乏音人 | 0.827 | link_folder/人物/利乏音人.md |
| 2 | 散送冥 | 0.723 | link_folder/人物/散送冥.md |
| 3 | 以米人 | 0.695 | link_folder/人物/以米人.md |
| 4 | 亞衲族與偉人拿非林 | 0.627 | link_folder/背景/亞衲族與偉人拿非林.md |
| 5 | 亞摩利人 | 0.588 | link_folder/人物/亞摩利人.md |

判定：✅ 建議使用既有條目 [[利乏音人]]（同名／字面對應）

## 亞衲族與偉人拿非林（背景）
query:
- 待建立詞：亞衲族與偉人拿非林
- 出現位置：申命記 第2章
- 候選類型：背景
- 本章上下文：v10、v11、v21「像亞衲人一樣」。CT 原文字義：「亞衲」長頸；CT：「『亞衲人』是身材魁偉的巨人族(參民十三33)」；KC：「Unfortunately, it underscores Israel's cowardice of forty years ago, because even with God's help they were afraid of these enemies (Deu 1:28; Num 13:28,33). Now, however, they get a new opportunity.」
- 經文用詞：亞衲人

字面解析：對上既有「亞衲族與偉人拿非林」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 亞衲族與偉人拿非林 | 0.827 | link_folder/背景/亞衲族與偉人拿非林.md |
| 2 | 利乏音人 | 0.622 | link_folder/人物/利乏音人.md |
| 3 | 偉人 | 0.621 | link_folder/人物/偉人.md |
| 4 | 以米人 | 0.589 | link_folder/人物/以米人.md |
| 5 | 自認如蚱蜢的不信態勢 | 0.583 | link_folder/神學/自認如蚱蜢的不信態勢.md |

判定：✅ 建議使用既有條目 [[亞衲族與偉人拿非林]]（同名／字面對應）

## 何利人（人物）
query:
- 待建立詞：何利人
- 出現位置：申命記 第2章
- 候選類型：人物
- 本章上下文：v12「先前，何利人也住在西珥，但以掃的子孫將他們除滅」；v22。CT 原文字義：「何利」洞穴居民；GT《啟導本》：「過去以為何利人為穴居部落民族，因其希伯來文名中的hor有“穴”的意思，現在已知為主前一千五百年時住在巴勒斯坦北部和敘利亞一帶的強大赫倫人（Hurrians）」；GT《串珠》：「有關他們的生活習俗，可參考古學家所發掘的努斯泥版」；BH：「Archaeological evidence suggests that the Horites were a group of cave-dwellers, as the name "Horite" is derived from a word meaning "cave."」

字面解析：對上既有「何利人」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 何利人 | 0.825 | link_folder/人物/何利人.md |
| 2 | 何利名字含義 | 0.721 | link_folder/原文/何利名字含義.md |
| 3 | 赫人 | 0.625 | link_folder/人物/赫人.md |
| 4 | 西珥（何利人） | 0.601 | link_folder/人物/西珥（何利人）.md |
| 5 | 亞摩利人 | 0.558 | link_folder/人物/亞摩利人.md |

判定：✅ 建議使用既有條目 [[何利人]]（同名／字面對應）

## 撒烈溪（地點）
query:
- 待建立詞：撒烈溪
- 出現位置：申命記 第2章
- 候選類型：地點
- 本章上下文：v13「現在，起來過撒烈溪！於是我們過了撒烈溪」；v14。CT 原文字義：「撒烈」杞柳小溪；CT：「『撒烈溪』以東地與摩押地天然分界，是一條東西向、流入死海東南部的小溪」；GT《啟導本》：「撒烈溪的位置難確定，可能為今天流入死海南端的埃赫沙河（Wadi el-Hesa）」；GT《聖經精讀本》：「撒烈溪: 形成以東與摩押的分界,時有乾涸現象⋯此處就是以色列結束漫長曠野流浪之地」。
- 經文用詞：撒烈溪

字面解析：對上既有「撒烈溪」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 撒烈溪 | 0.885 | link_folder/地點/撒烈溪.md |
| 2 | 加低斯 | 0.575 | link_folder/地點/加低斯.md |
| 3 | 以倘 | 0.562 | link_folder/地點/以倘.md |
| 4 | 書珥 | 0.557 | link_folder/地點/書珥.md |
| 5 | 亞拉巴 | 0.555 | link_folder/地點/亞拉巴.md |

判定：✅ 建議使用既有條目 [[撒烈溪]]（同名／字面對應）

## 加低斯（地點）
query:
- 待建立詞：加低斯
- 出現位置：申命記 第2章
- 候選類型：地點
- 本章上下文：v14「自從離開加低斯巴尼亞，到過了撒烈溪的時候，共有三十八年」。CT：「『加低斯巴尼亞』簡稱加低斯，以色列人從加低斯到加低斯(參民十三26；二十1)，在曠野飄流，將近三十八年」。
- 經文用詞：加低斯巴尼亞

字面解析：對上既有「加低斯」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 加低斯 | 0.726 | link_folder/地點/加低斯.md |
| 2 | 加低斯巴尼亞事件 | 0.672 | link_folder/歷史/加低斯巴尼亞事件.md |
| 3 | 撒烈溪 | 0.671 | link_folder/地點/撒烈溪.md |
| 4 | 三十八年與那世代的兵丁滅盡 | 0.647 | link_folder/歷史/三十八年與那世代的兵丁滅盡.md |
| 5 | 十一天的路程 | 0.597 | link_folder/主題/十一天的路程.md |

判定：✅ 建議使用既有條目 [[加低斯]]（同名／字面對應）

## 三十八年與那世代的兵丁滅盡（歷史）
query:
- 待建立詞：三十八年與那世代的兵丁滅盡
- 出現位置：申命記 第2章
- 候選類型：歷史
- 本章上下文：v14-16「等那世代的兵丁都從營中滅盡，正如耶和華向他們所起的誓」「耶和華的手也攻擊他們」。CT：「『都從營中滅盡』由此可見，那一代人的平均壽命，沒有超過六十歲」；CT 原文字義：「除滅」打亂，使困惑；GT《聖經精讀本》：「那時代的兵丁: 指可以去參戰的所有男子,在第一次人口調查他們都年逾二十(民1:3;14:29)⋯神卻毫無迷戀地除去了他們,將征服迦南的偉業託付給了毫無戰鬥經驗的新世代」；KC：「They had despised His caring hand; therefore, they had to deal with His disciplining hand. When the last one had died, His hand was no more against them.」
- 經文用詞：三十八年

字面解析：對上既有「三十八年與那世代的兵丁滅盡」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 三十八年與那世代的兵丁滅盡 | 0.866 | link_folder/歷史/三十八年與那世代的兵丁滅盡.md |
| 2 | 二十歲以外能打仗的 | 0.605 | link_folder/主題/二十歲以外能打仗的.md |
| 3 | 曠野飄流四十年 | 0.592 | link_folder/歷史/曠野飄流四十年.md |
| 4 | 以色列人的軍隊 | 0.564 | link_folder/神學/以色列人的軍隊.md |
| 5 | 六十萬零三千五百五十人（出38：26） | 0.562 | link_folder/事件/六十萬零三千五百五十人（出38：26）.md |

判定：✅ 建議使用既有條目 [[三十八年與那世代的兵丁滅盡]]（同名／字面對應）

## 亞捫人（人物）
query:
- 待建立詞：亞捫人
- 出現位置：申命記 第2章
- 候選類型：人物
- 本章上下文：v19「走近亞捫人之地，不可擾害他們」；v20、v21、v37。CT 原文字義：「亞捫」部落的；CT：「『亞捫人』是亞伯拉罕的侄兒羅得與他次女亂倫所生的子孫(參創十九36，38)」；GT《聖經精讀本》：「亞捫人居住在約但河對面,即摩押人的東北地區」。

字面解析：對上既有「亞捫人」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 亞捫人 | 0.762 | link_folder/人物/亞捫人.md |
| 2 | 摩押 | 0.649 | link_folder/人物/摩押.md |
| 3 | 摩押人 | 0.631 | link_folder/人物/摩押人.md |
| 4 | 羅得 | 0.603 | link_folder/人物/羅得.md |
| 5 | 亞珥 | 0.590 | link_folder/地點/亞珥.md |

判定：✅ 建議使用既有條目 [[亞捫人]]（同名／字面對應）

## 散送冥（人物）
query:
- 待建立詞：散送冥
- 出現位置：申命記 第2章
- 候選類型：人物
- 本章上下文：v20「亞捫人稱他們為散送冥」。CT 原文字義：「散送冥」陰謀者；CT：「『散送冥』聖經中僅在此處出現一次，原文字義「陰謀者」，可能指對外族人很不友善」；GT《聖經精讀本》：「散送冥: 具有“熙嚷挑剔的宗族”之意,是亞捫人對巨人族利乏音人的稱呼」；BH：「The term "Zamzummites" could imply a particular characteristic or reputation, possibly related to their strength or the fear they inspired」。
- 經文用詞：散送冥

字面解析：對上既有「散送冥」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 散送冥 | 0.841 | link_folder/人物/散送冥.md |
| 2 | 利乏音人 | 0.577 | link_folder/人物/利乏音人.md |
| 3 | 亞衲族與偉人拿非林 | 0.545 | link_folder/背景/亞衲族與偉人拿非林.md |
| 4 | 亞捫人 | 0.521 | link_folder/人物/亞捫人.md |
| 5 | 亞瑪力 | 0.517 | link_folder/人物/亞瑪力.md |

判定：✅ 建議使用既有條目 [[散送冥]]（同名／字面對應）

## 非利士人（地點）
query:
- 待建立詞：非利士人
- 出現位置：申命記 第2章
- 候選類型：地點
- 本章上下文：v23「從迦斐託出來的迦斐託人將先前住在鄉村直到迦薩的亞衛人除滅」。CT 原文字義：「迦斐托」一個冠冕；CT：「『迦斐托』即革哩底(參多一12)；『迦斐托人』又稱非利士人」；GT《聖經精讀本》：「從迦斐托出來的迦斐托人: 指非利士人(耶47:4;摩9:7),其土著地為愛琴海沿岸地區的Crete。“非利士”本身具有“移民”(immigrant)之意」；BH：「The Caphtorites are believed to be related to the Philistines, often associated with the island of Crete or the broader Aegean region」。
- 經文用詞：迦斐託人、迦斐託

字面解析：對上既有「非利士人」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 非利士人出自迦斯路希或迦斐託 | 0.812 | link_folder/解經爭議/非利士人出自迦斯路希或迦斐託.md |
| 2 | 非利士人 | 0.767 | link_folder/地點/非利士人.md |
| 3 | 亞衛人 | 0.707 | link_folder/人物/亞衛人.md |
| 4 | 迦薩 | 0.685 | link_folder/地點/迦薩.md |
| 5 | 非利士地 | 0.653 | link_folder/地點/非利士地.md |

判定：✅ 建議使用既有條目 [[非利士人]]（同名／字面對應）

## 非利士人出自迦斯路希或迦斐託（解經爭議）
query:
- 待建立詞：非利士人出自迦斯路希或迦斐託
- 出現位置：申命記 第2章
- 候選類型：解經爭議
- 本章上下文：v23 把非利士人的來源指向迦斐託。GT《啟導本》：「迦斐托為今天的克里特島非利士人可能來自此島（參創十14；耶四十七4；摩九7）」；BH：「Caphtor is traditionally identified with Crete, though some scholars suggest it could refer to other locations in the Aegean or eastern Mediterranean」。

字面解析：對上既有「非利士人出自迦斯路希或迦斐託」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 非利士人出自迦斯路希或迦斐託 | 0.893 | link_folder/解經爭議/非利士人出自迦斯路希或迦斐託.md |
| 2 | 非利士人 | 0.672 | link_folder/地點/非利士人.md |
| 3 | 亞伯拉罕時代是否已有非利士人 | 0.611 | link_folder/解經爭議/亞伯拉罕時代是否已有非利士人.md |
| 4 | 非利士地 | 0.587 | link_folder/地點/非利士地.md |
| 5 | 迦薩 | 0.546 | link_folder/地點/迦薩.md |

判定：✅ 建議使用既有條目 [[非利士人出自迦斯路希或迦斐託]]（同名／字面對應）

## 亞衛人（人物）
query:
- 待建立詞：亞衛人
- 出現位置：申命記 第2章
- 候選類型：人物
- 本章上下文：v23「先前住在鄉村直到迦薩的亞衛人」。CT 原文字義：「亞衛」毀滅；CT：「『亞衛人』迦薩地區的原住民」；GT《啟導本》：「“亞衛人”只在此處和《約書亞記》十三3中提到，當為巴勒斯坦西南的原來居民」；GT《串珠》：「「亞衛人」：指地中海沿岸原來的居民」；BH：「The Avvim's presence in villages suggests a settled, agrarian lifestyle」。
- 經文用詞：亞衛人

字面解析：對上既有「亞衛人」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 亞衛人 | 0.849 | link_folder/人物/亞衛人.md |
| 2 | 迦薩 | 0.673 | link_folder/地點/迦薩.md |
| 3 | 非利士人 | 0.555 | link_folder/地點/非利士人.md |
| 4 | 亞捫人 | 0.546 | link_folder/人物/亞捫人.md |
| 5 | 迦南人 | 0.533 | link_folder/人物/迦南人.md |

判定：✅ 建議使用既有條目 [[亞衛人]]（同名／字面對應）

## 迦薩（地點）
query:
- 待建立詞：迦薩
- 出現位置：申命記 第2章
- 候選類型：地點
- 本章上下文：v23「住在鄉村直到迦薩」。CT 原文字義：「迦薩」強壯；CT：「『迦薩』非利士人五個首領之一的管區(參書十三3)，位於最南部沿海一處狹窄的地區」；BH：「Gaza, a major city in the region, was a strategic location due to its position on trade routes」。
- 經文用詞：迦薩

字面解析：對上既有「迦薩」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 迦薩 | 0.806 | link_folder/地點/迦薩.md |
| 2 | 加低斯 | 0.524 | link_folder/地點/加低斯.md |
| 3 | 亞衛人 | 0.524 | link_folder/人物/亞衛人.md |
| 4 | 迦南地 | 0.515 | link_folder/地點/迦南地.md |
| 5 | 非利士地 | 0.499 | link_folder/地點/非利士地.md |

判定：✅ 建議使用既有條目 [[迦薩]]（同名／字面對應）

## 亞嫩河（地點）
query:
- 待建立詞：亞嫩河
- 出現位置：申命記 第2章
- 候選類型：地點
- 本章上下文：v24「你們起來前往，過亞嫩谷」；v36「從亞嫩谷邊的亞羅珥和谷中的城」。CT：「『亞嫩谷』指亞嫩河谷，是一條從摩押高原流入死海中部的河，河谷深約五百公尺，寬約三公里，形成小型的峽谷(參民二十一13)」；GT《聖經精讀本》：「亞嫩谷: 與“亞嫩河”相一致,因為不下雨的季節河床會乾涸成谷。亞嫩谷是摩押與亞摩利人的分界線(民21:13)」；BH：「identified with the modern Wadi Mujib in Jordan」。
- 經文用詞：亞嫩谷

字面解析：對上既有「亞嫩河」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 亞嫩河 | 0.807 | link_folder/地點/亞嫩河.md |
| 2 | 亞羅珥 | 0.686 | link_folder/地點/亞羅珥.md |
| 3 | 亞珥 | 0.624 | link_folder/地點/亞珥.md |
| 4 | 亞拉巴 | 0.610 | link_folder/地點/亞拉巴.md |
| 5 | 撒烈溪 | 0.588 | link_folder/地點/撒烈溪.md |

判定：✅ 建議使用既有條目 [[亞嫩河]]（同名／字面對應）

## 接連的山谷（na.chal）（原文）
query:
- 待建立詞：接連的山谷（na.chal）
- 出現位置：申命記 第2章
- 候選類型：原文
- 本章上下文：v24「過亞嫩谷」、v36「亞嫩谷邊」「谷中的城」。STEP 顯示這三處的「谷」都是 Na.chal（H5158N），簡要詞典義 torrent: valley，context gloss 作「wadi」——與 GT《聖經精讀本》所說「不下雨的季節河床會乾涸成谷」的旱溪一致。

字面解析：對上既有「接連的山谷（na.chal）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 接連的山谷（na.chal） | 0.771 | link_folder/原文/接連的山谷（na.chal）.md |
| 2 | 亞嫩河 | 0.514 | link_folder/地點/亞嫩河.md |
| 3 | 亞羅珥 | 0.501 | link_folder/地點/亞羅珥.md |
| 4 | 溫泉或騾子（創36：24） | 0.464 | link_folder/原文/溫泉或騾子（創36：24）.md |
| 5 | 亞珥 | 0.464 | link_folder/地點/亞珥.md |

判定：✅ 建議使用既有條目 [[接連的山谷（na.chal）]]（同名／字面對應）

## 亞摩利人（人物）
query:
- 待建立詞：亞摩利人
- 出現位置：申命記 第2章
- 候選類型：人物
- 本章上下文：v24「我已將亞摩利人希實本王西宏和他的地交在你手中」。GT《雷氏研讀本》：「亞摩利人是一個與以色列人無關的異族，他們散佈在約但河的東面。由於他們沉溺於偶像膜拜，所以神吩咐以色列人把他們毀滅」；GT《啟導本》：「以色列人可以攻取約但河以東亞摩利人的土地，西宏與噩都是亞摩利人的王，屬迦南族」。

字面解析：對上既有「亞摩利人」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 亞摩利人 | 0.780 | link_folder/人物/亞摩利人.md |
| 2 | 亞捫人 | 0.687 | link_folder/人物/亞捫人.md |
| 3 | 以色列戰勝亞摩利王西宏互文（申2：24-37；3：1-7；詩135：10-12；136：17-22） | 0.644 | link_folder/互文/以色列戰勝亞摩利王西宏互文（申2：24-37；3：1-7；詩135：10-12；136：17-22）.md |
| 4 | 亞瑪力人 | 0.629 | link_folder/人物/亞瑪力人.md |
| 5 | 亞瑪力 | 0.623 | link_folder/人物/亞瑪力.md |

判定：✅ 建議使用既有條目 [[亞摩利人]]（同名／字面對應）

## 希實本（地點）
query:
- 待建立詞：希實本
- 出現位置：申命記 第2章
- 候選類型：地點
- 本章上下文：v24、v26、v30「希實本王西宏」。CT 原文字義：「希實本」堡壘；CT：「希實本乃是亞摩利的京城(參民二十一27；書九10)」；KC：「Heshbon originally belonged to the Moabites, but the Amorites had conquered it (Num 21:26-29) and expelled the Moabites.」

字面解析：對上既有「希實本」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 希實本 | 0.793 | link_folder/地點/希實本.md |
| 2 | 以色列戰勝亞摩利王西宏互文（申2：24-37；3：1-7；詩135：10-12；136：17-22） | 0.578 | link_folder/互文/以色列戰勝亞摩利王西宏互文（申2：24-37；3：1-7；詩135：10-12；136：17-22）.md |
| 3 | 亞摩利人 | 0.556 | link_folder/人物/亞摩利人.md |
| 4 | 雅雜 | 0.528 | link_folder/地點/雅雜.md |
| 5 | 亞捫人 | 0.514 | link_folder/人物/亞捫人.md |

判定：✅ 建議使用既有條目 [[希實本]]（同名／字面對應）

## 以色列戰勝亞摩利王西宏互文（互文）
query:
- 待建立詞：以色列戰勝亞摩利王西宏互文
- 出現位置：申命記 第2章
- 候選類型：互文
- 本章上下文：v24-36 整段。GT《串珠》：「以色列民擊敗希實本王（見民21:21-32）」；GT《聖經精讀本》：「此次爭戰是以色列在開展迦南征服戰之前的序幕戰,以色列得勝的消息傳遍了迦南全地」；BH：「This victory is later celebrated in Israel's history (Psalm 135:10-12).」
- 經文用詞：西宏

字面解析：對上既有「以色列戰勝亞摩利王西宏互文（申2：24-37；3：1-7；詩135：10-12；136：17-22）」（alias，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 以色列戰勝亞摩利王西宏互文（申2：24-37；3：1-7；詩135：10-12；136：17-22） | 0.817 | link_folder/互文/以色列戰勝亞摩利王西宏互文（申2：24-37；3：1-7；詩135：10-12；136：17-22）.md |
| 2 | 以色列戰勝巴珊王噩互文（申3：1-11；詩135：10-12；136：17-22） | 0.662 | link_folder/互文/以色列戰勝巴珊王噩互文（申3：1-11；詩135：10-12；136：17-22）.md |
| 3 | 希實本 | 0.591 | link_folder/地點/希實本.md |
| 4 | 亞摩利人 | 0.578 | link_folder/人物/亞摩利人.md |
| 5 | 雅雜 | 0.576 | link_folder/地點/雅雜.md |

判定：✅ 建議使用既有條目 [[以色列戰勝亞摩利王西宏互文（申2：24-37；3：1-7；詩135：10-12；136：17-22）]]（同名／字面對應）

## 起首得那地（cha.lal）（原文）
query:
- 待建立詞：起首得那地（cha.lal）
- 出現位置：申命記 第2章
- 候選類型：原文
- 本章上下文：v24「你要與他爭戰，得他的地為業」（原文帶「起首」）；v25「從今日起」；v31「從此起首，我要將西宏和他的地交給你」。CT 原文字義 v31：「從此起首」(原文無此詞)。STEP 顯示 v24 是 ha.Chel（H2490C）、v25 是 'a.Chel（H2490C），簡要詞典義 cha.lal「to profane/begin: begin」。KC：「Therefore the LORD says in verse 24 and in verse 31: “Begin to take possession” and “begin to occupy”.」
- 經文用詞：從此起首

字面解析：對上既有「起首得那地（cha.lal）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 起首得那地（cha.lal） | 0.842 | link_folder/原文/起首得那地（cha.lal）.md |
| 2 | 使天下萬民驚恐懼怕 | 0.491 | link_folder/原文/使天下萬民驚恐懼怕.md |
| 3 | 為業（ye.ru.shah） | 0.488 | link_folder/原文/為業（ye.ru.shah）.md |
| 4 | 褻瀆（cha.lal） | 0.471 | link_folder/原文/褻瀆（cha.lal）.md |
| 5 | 行起淫亂（za.nah） | 0.468 | link_folder/原文/行起淫亂（za.nah）.md |

判定：✅ 建議使用既有條目 [[起首得那地（cha.lal）]]（同名／字面對應）

## 使天下萬民驚恐懼怕（原文）
query:
- 待建立詞：使天下萬民驚恐懼怕
- 出現位置：申命記 第2章
- 候選類型：原文
- 本章上下文：v25「我要使天下萬民聽見你的名聲都驚恐懼怕，且因你發顫傷慟」。CT 原文字義：「萬民(原文雙字)」面，臉(首字)；國家，百姓(次字)；「驚恐」恐懼；「懼怕」害怕，不安；「發顫」發抖，震動；「傷慟」扭曲，扭動。STEP 逐字證實：「萬民」是 pe.Nei ha./'a.Mim（H6440H panim＋H5971A am）、「驚恐懼怕」是 pach.de./Kha ve./yir.'A.te./kha（H6343 pa.chad「dread」＋H3374 yir.ah「fear」）、「發顫傷慟」是 ve./ra.ge.Zu ve./cha.Lu（H7264 ra.gaz「to tremble」＋H2342I chul「to twist: writh in pain」）。BH：「The reaction of trembling and anguish signifies a deep, visceral fear.」
- 經文用詞：驚恐懼怕

字面解析：對上既有「使天下萬民驚恐懼怕」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 使天下萬民驚恐懼怕 | 0.838 | link_folder/原文/使天下萬民驚恐懼怕.md |
| 2 | 百姓懼怕神的顯現 | 0.573 | link_folder/事件/百姓懼怕神的顯現.md |
| 3 | 敬畏神 | 0.503 | link_folder/神學/敬畏神.md |
| 4 | 敬畏與信服 | 0.491 | link_folder/神學/敬畏與信服.md |
| 5 | 賽6：5 | 0.483 | link_folder/互文/賽6：5.md |

判定：✅ 建議使用既有條目 [[使天下萬民驚恐懼怕]]（同名／字面對應）

## 基底莫（地點）
query:
- 待建立詞：基底莫
- 出現位置：申命記 第2章
- 候選類型：地點
- 本章上下文：v26「我從基底莫的曠野差遣使者去見希實本王西宏」。CT 原文字義：「基底莫」東方的；CT：「『基底莫的曠野』確實位置不詳，大概在亞嫩河以北、接近希實本王疆土的東界」；GT《啟導本》：「基底莫確切位置不詳，只知後來為流便支派居住的一城（書十三18）」。
- 經文用詞：基底莫

字面解析：對上既有「基底莫」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 基底莫 | 0.823 | link_folder/地點/基底莫.md |
| 2 | 希實本 | 0.561 | link_folder/地點/希實本.md |
| 3 | 底本 | 0.558 | link_folder/地點/底本.md |
| 4 | 河東城邑的位置考據 | 0.557 | link_folder/背景/河東城邑的位置考據.md |
| 5 | 以倘 | 0.527 | link_folder/地點/以倘.md |

判定：✅ 建議使用既有條目 [[基底莫]]（同名／字面對應）

## 使者（原文）
query:
- 待建立詞：使者
- 出現位置：申命記 第2章
- 候選類型：原文
- 本章上下文：v26「我從基底莫的曠野差遣使者去見希實本王西宏，用和睦的話說」。BH：「Sending messengers was a common diplomatic practice in the ancient Near East. It reflects a desire for peaceful negotiation rather than immediate conflict.」

字面解析：對上既有「使者」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 使者 | 0.610 | link_folder/原文/使者.md |
| 2 | 基底莫 | 0.593 | link_folder/地點/基底莫.md |
| 3 | 耶和華的使者是否為神顯現 | 0.438 | link_folder/解經爭議/耶和華的使者是否為神顯現.md |
| 4 | 耶和華的使者 | 0.430 | link_folder/神學/耶和華的使者.md |
| 5 | 古代近東岳父禮儀 | 0.399 | link_folder/背景/古代近東岳父禮儀.md |

判定：✅ 建議使用既有條目 [[使者]]（同名／字面對應）

## 大道（原文作王道）（文化）
query:
- 待建立詞：大道（原文作王道）
- 出現位置：申命記 第2章
- 候選類型：文化
- 本章上下文：v27「求你容我從你的地經過，只走大道，不偏左右」。CT 原文字義：「大道(原文雙同字)」道路，路程；CT：「『只走大道，不偏左右』指不侵犯住宅區、民房、田地等」；GT《聖經精讀本》：「只走大道: 具有“只走道,只走道”的意思,強調了會一直沿著大道而行,概不侵犯其它所有地方。此道與民21:22的“王道”(Kings Highway)是同一道路,是古代東方幾個主要國際道路之一」；BH：「The main road, or "King's Highway," was a major trade route in the ancient Near East, running from the Gulf of Aqaba in the south to Damascus in the north」。
- 經文用詞：只走大道，不偏左右

字面解析：對上既有「大道（原文作王道）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 大道（原文作王道） | 0.816 | link_folder/文化/大道（原文作王道）.md |
| 2 | 沿海大道（Via Maris） | 0.550 | link_folder/地點/沿海大道（Via Maris）.md |
| 3 | 以東王拒絕以色列人假道 | 0.495 | link_folder/歷史/以東王拒絕以色列人假道.md |
| 4 | 認識神的道 | 0.459 | link_folder/主題/認識神的道.md |
| 5 | 非利士地 | 0.454 | link_folder/地點/非利士地.md |

判定：✅ 建議使用既有條目 [[大道（原文作王道）]]（同名／字面對應）

## 約但河（地點）
query:
- 待建立詞：約但河
- 出現位置：申命記 第2章
- 候選類型：地點
- 本章上下文：v29「等我過了約但河，好進入耶和華─我們神所賜給我們的地」。CT 原文字義：「約但」下降；CT：「『約但河』就在死海的北邊流入死海，而約但河的東岸屬於亞摩利人、西岸屬於迦南人，故須從亞摩利人的境內渡河到迦南地」。

字面解析：對上既有「約但河」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 約但河 | 0.690 | link_folder/地點/約但河.md |
| 2 | 雅博渡口 | 0.596 | link_folder/地點/雅博渡口.md |
| 3 | 亞捫人 | 0.582 | link_folder/人物/亞捫人.md |
| 4 | 亞嫩河 | 0.582 | link_folder/地點/亞嫩河.md |
| 5 | 迦南地的居民分佈 | 0.575 | link_folder/背景/迦南地的居民分佈.md |

判定：✅ 建議使用既有條目 [[約但河]]（同名／字面對應）

## 法老心剛硬三字（原文）
query:
- 待建立詞：法老心剛硬三字
- 出現位置：申命記 第2章
- 候選類型：原文
- 本章上下文：v30「因為耶和華─你的神使他心中剛硬，性情頑梗」。CT 原文字義：「心中」靈，氣，風；「剛硬」固執，頑固；「性情」內心；「頑梗」堅強，堅固。STEP 逐字證實：「使他心中剛硬」是 hik.Shah 'et- ru.Ch/o（H7185 qa.shah「to harden」＋H7307G ru.ach「spirit」）、「性情頑梗」是 ve./'i.Metz 'et- le.va.V/o（H553 a.mats「to strengthen」＋H3824 le.vav「heart」）——和合本譯作「心中」的其實是 ruach（靈），譯作「性情」的才是 levav（心）。GT《串珠》：「按神的計畫，希實本王西宏使自己的心剛硬；因他立定心志敵擋神，這種抗拒的態度便使他的心逐步剛硬。故此，人不可忽視自己的行動，因神的預定與人的責任是不能分割的（參出7:3, 14，有關法老的心剛硬）」。
- 經文用詞：剛硬

字面解析：對上既有「法老心剛硬三字」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 法老心剛硬三字 | 0.850 | link_folder/原文/法老心剛硬三字.md |
| 2 | 神使西宏心中剛硬與人的責任 | 0.814 | link_folder/解經爭議/神使西宏心中剛硬與人的責任.md |
| 3 | 法老的心剛硬 | 0.757 | link_folder/神學/法老的心剛硬.md |
| 4 | 法老心剛硬 | 0.751 | link_folder/神學/法老心剛硬.md |
| 5 | 耶和華使法老的心剛硬 | 0.695 | link_folder/神學/耶和華使法老的心剛硬.md |

判定：✅ 建議使用既有條目 [[法老心剛硬三字]]（同名／字面對應）

## 神使西宏心中剛硬與人的責任（解經爭議）
query:
- 待建立詞：神使西宏心中剛硬與人的責任
- 出現位置：申命記 第2章
- 候選類型：解經爭議
- 本章上下文：v30「因為耶和華─你的神使他心中剛硬，性情頑梗，為要將他交在你手中」。GT《雷氏研讀本》：「“心中剛硬，性情頑梗”。雖然是西宏自己作出決定，但摩西從神控制歷史的希伯來人觀點而說出這句話（民二一23）」；GT《聖經精讀本》：「使他心中剛硬: 並不是指敵意使原本善良的希實本王西宏變得頑梗 ,乃是指任他持有剛硬的心」；KC：「The hardening of his heart by the LORD only confirms the already present inflexible attitude.」；BH：「It underscores the belief that God can influence the decisions of rulers to fulfill His purposes.」

字面解析：對上既有「神使西宏心中剛硬與人的責任」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 神使西宏心中剛硬與人的責任 | 0.859 | link_folder/解經爭議/神使西宏心中剛硬與人的責任.md |
| 2 | 法老的心剛硬 | 0.619 | link_folder/神學/法老的心剛硬.md |
| 3 | 法老心剛硬 | 0.612 | link_folder/神學/法老心剛硬.md |
| 4 | 法老心剛硬三字 | 0.590 | link_folder/原文/法老心剛硬三字.md |
| 5 | 耶和華使法老的心剛硬 | 0.589 | link_folder/神學/耶和華使法老的心剛硬.md |

判定：✅ 建議使用既有條目 [[神使西宏心中剛硬與人的責任]]（同名／字面對應）

## 雅雜（地點）
query:
- 待建立詞：雅雜
- 出現位置：申命記 第2章
- 候選類型：地點
- 本章上下文：v32「那時，西宏和他的眾民出來攻擊我們，在雅雜與我們交戰」。CT 原文字義：「雅雜」踩踏；CT：「『雅雜』位於亞嫩河北面，屬於亞摩利境內的一處地方(參民二十一13，23)」；GT《串珠》：「「雅雜」：地點不詳。主前九世紀中葉的摩押碑文指出這城日後為摩押人管轄」。
- 經文用詞：雅雜

字面解析：對上既有「雅雜」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 雅雜 | 0.861 | link_folder/地點/雅雜.md |
| 2 | 雅謝 | 0.620 | link_folder/地點/雅謝.md |
| 3 | 亞珥 | 0.612 | link_folder/地點/亞珥.md |
| 4 | 希實本 | 0.560 | link_folder/地點/希實本.md |
| 5 | 以色列戰勝亞摩利王西宏互文（申2：24-37；3：1-7；詩135：10-12；136：17-22） | 0.558 | link_folder/互文/以色列戰勝亞摩利王西宏互文（申2：24-37；3：1-7；詩135：10-12；136：17-22）.md |

判定：✅ 建議使用既有條目 [[雅雜]]（同名／字面對應）

## 滅絕（原文）
query:
- 待建立詞：滅絕
- 出現位置：申命記 第2章
- 候選類型：原文
- 本章上下文：v34「我們奪了他的一切城邑，將有人煙的各城，連女人帶孩子，盡都毀滅，沒有留下一個」。CT 原文字義：「人煙」男人；「毀滅」完全毀壞；CT：「『盡都毀滅』意指不留一個活口，通常只有在聖戰的指令下才這樣作，例如在耶利哥城(參書六17)」；GT《啟導本》：「“毀滅”的希伯來原文作（），為一專用字，指在為神而作的聖戰中，將所有戰俘、擄物完全殲滅，當作對神的奉獻」（該處原文字形在來源檔中缺漏）。STEP 補上了缺漏的字形：v34 是 va./na.cha.Rem（H2763A cha.ram，Hiphil，簡要詞典義 to devote/destroy）；同節「有人煙的各城」是 'ir me.Tim（H4962 mat「man」）、「沒有留下一個」是 lo' hish.'Ar.nu sa.Rid（H7604 sha.ar「to remain」＋H8300 sa.rid「survivor」）。
- 經文用詞：盡都毀滅

字面解析：對上既有「滅絕」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 滅絕 | 0.754 | link_folder/原文/滅絕.md |
| 2 | 滅絕（herem） | 0.653 | link_folder/神學/滅絕（herem）.md |
| 3 | 戰勝亞拉得王 | 0.540 | link_folder/歷史/戰勝亞拉得王.md |
| 4 | 拆毀偶像律例 | 0.538 | link_folder/事件/拆毀偶像律例.md |
| 5 | 使天下萬民驚恐懼怕 | 0.536 | link_folder/原文/使天下萬民驚恐懼怕.md |

判定：✅ 建議使用既有條目 [[滅絕]]（同名／字面對應）

## 亞羅珥（地點）
query:
- 待建立詞：亞羅珥
- 出現位置：申命記 第2章
- 候選類型：地點
- 本章上下文：v36「從亞嫩谷邊的亞羅珥和谷中的城」。CT 原文字義：「亞羅珥」毀滅；CT：「『亞羅珥』位於死海中部東方約20公里處，亞嫩河北畔的一座城」；GT《啟導本》：「“亞羅珥”：不只一個地方叫此名字。此處的亞羅珥或為死海東南20公里亞嫩河畔的一個城」；BH：「Aroer was a city located on the northern edge of the Arnon Valley」。STEP 顯示是 me./'a.ro.'Er（H6177H）。
- 經文用詞：亞羅珥

字面解析：對上既有「亞羅珥」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 亞羅珥 | 0.871 | link_folder/地點/亞羅珥.md |
| 2 | 亞珥 | 0.638 | link_folder/地點/亞珥.md |
| 3 | 亞嫩河 | 0.596 | link_folder/地點/亞嫩河.md |
| 4 | 戰勝亞拉得王 | 0.574 | link_folder/歷史/戰勝亞拉得王.md |
| 5 | 瑣珥 | 0.570 | link_folder/地點/瑣珥.md |

判定：✅ 建議使用既有條目 [[亞羅珥]]（同名／字面對應）

## 基列（地點）
query:
- 待建立詞：基列
- 出現位置：申命記 第2章
- 候選類型：地點
- 本章上下文：v36「直到基列，耶和華─我們的神都交給我們了」。CT：「『基列』廣義泛指約但河東以色列人所佔領之地(參三十四1)，狹義僅指雅博河以北包括巴珊地區在內，本處應指狹義的基列」；GT《啟導本》：「基列在加利利海東南，土地肥沃（參創三十一21）」；GT《串珠》：「「基列」：約但河東的山區」。

字面解析：對上既有「基列」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 基列 | 0.806 | link_folder/地點/基列.md |
| 2 | 基列山 | 0.680 | link_folder/地點/基列山.md |
| 3 | 巴珊 | 0.606 | link_folder/地點/巴珊.md |
| 4 | 基列亞巴 | 0.598 | link_folder/地點/基列亞巴.md |
| 5 | 基尼烈湖 | 0.575 | link_folder/地點/基尼烈湖.md |

判定：✅ 建議使用既有條目 [[基列]]（同名／字面對應）

## 沒有一座城高得使我們不能攻取（主題）
query:
- 待建立詞：沒有一座城高得使我們不能攻取
- 出現位置：申命記 第2章
- 候選類型：主題
- 本章上下文：v36「沒有一座城高得使我們不能攻取的」。CT 原文字義：「高得」高到難以接近；「攻取」(原文無此字)；GT《雷氏研讀本》：「“高得使我們不能攻取”。高高的城牆把以色列人嚇壞了（一28）」；KC：「In this way we too can continue in spiritual strength in the awareness that no spiritual city is too high for us (verse 36).」；BH：「This phrase highlights the miraculous nature of Israel's victories, as fortified cities with high walls were typically difficult to conquer.」STEP 證實 CT 的「(原文無此字)」：原文只有 lo' ha.ye.Tah kir.Yah 'a.Sher sa.ge.Vah mi.Me./nu（H7151 qir.yah「town」＋H7682 sa.gav「to exalt」），沒有對應「攻取」的動詞。
- 經文用詞：沒有一座城高得使我們不能攻取的

字面解析：對上既有「沒有一座城高得使我們不能攻取」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 沒有一座城高得使我們不能攻取 | 0.884 | link_folder/主題/沒有一座城高得使我們不能攻取.md |
| 2 | 心消化（ma.sas） | 0.553 | link_folder/原文/心消化（ma.sas）.md |
| 3 | 使天下萬民驚恐懼怕 | 0.523 | link_folder/原文/使天下萬民驚恐懼怕.md |
| 4 | 昂然無懼 | 0.512 | link_folder/原文/昂然無懼.md |
| 5 | 戰勝亞拉得王 | 0.506 | link_folder/歷史/戰勝亞拉得王.md |

判定：✅ 建議使用既有條目 [[沒有一座城高得使我們不能攻取]]（同名／字面對應）

## 雅博渡口（地點）
query:
- 待建立詞：雅博渡口
- 出現位置：申命記 第2章
- 候選類型：地點
- 本章上下文：v37「凡靠近雅博河的地」。CT 原文字義：「雅博」倒空；GT《啟導本》：「雅博河在外約但，自東北向西南流，在死海北約30公里處流入約但河」；GT《串珠》：「「雅博河」：約但河東部的支流，在死海以北六十四公里（四十英里）流入約但河；昔日雅各曾在此與天使摔跤（參串）」；BH：「The Jabbok River, known today as the Zarqa River, was a significant geographical boundary.」
- 經文用詞：雅博河

字面解析：對上既有「雅博渡口」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 雅博渡口 | 0.812 | link_folder/地點/雅博渡口.md |
| 2 | 約但河 | 0.628 | link_folder/地點/約但河.md |
| 3 | 「伯拉大河」名稱 | 0.550 | link_folder/原文/「伯拉大河」名稱.md |
| 4 | 雅雜 | 0.536 | link_folder/地點/雅雜.md |
| 5 | 撒烈溪 | 0.535 | link_folder/地點/撒烈溪.md |

判定：✅ 建議使用既有條目 [[雅博渡口]]（同名／字面對應）

## 滅絕（herem）（神學）
query:
- 待建立詞：滅絕（herem）
- 出現位置：申命記 第2章
- 候選類型：神學
- 本章上下文：v34「將有人煙的各城，連女人帶孩子，盡都毀滅，沒有留下一個」。GT《啟導本》：「“毀滅”的希伯來原文作（），為一專用字，指在為神而作的聖戰中，將所有戰俘、擄物完全殲滅，當作對神的奉獻」（該處字形在來源檔中缺漏，STEP 補為 va./na.cha.Rem，H2763A）；CT：「『盡都毀滅』意指不留一個活口，通常只有在聖戰的指令下才這樣作，例如在耶利哥城(參書六17)」；GT《聖經精讀本》：「尤其是“毀滅”這一詞意指殺盡母親與孩子。」

字面解析：對上既有「滅絕（herem）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 滅絕 | 0.742 | link_folder/原文/滅絕.md |
| 2 | 滅絕（herem） | 0.701 | link_folder/神學/滅絕（herem）.md |
| 3 | 拆毀偶像律例 | 0.528 | link_folder/事件/拆毀偶像律例.md |
| 4 | 滅命的 | 0.520 | link_folder/神學/滅命的.md |
| 5 | 戰勝亞拉得王 | 0.513 | link_folder/歷史/戰勝亞拉得王.md |

判定：✅ 建議使用既有條目 [[滅絕（herem）]]（同名／字面對應）

## 候選互查（本章內部，⚠＝彼此相似 ≥ 0.8）
兩個候選可能是同一概念——考慮合併成一個候選（另一個用 surfaces 涵蓋），
或確認確為兩個條目再照建：
- 0.900 ⚠ 滅絕 ↔ 滅絕（herem）
- 0.801 ⚠ 非利士人 ↔ 非利士人出自迦斯路希或迦斐託
