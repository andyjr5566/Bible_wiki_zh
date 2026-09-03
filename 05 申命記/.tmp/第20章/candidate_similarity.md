<!-- candidate_similarity_meta
schema_version: 1
book: 申命記
chapter: 20
candidate_sha256: 10810c9bb84aecf7ae80e749292ba1d94c63c601231ef4b70122f2c9e0a6e991
candidate_identity_sha256: 601787cc35c53ffac56c72e6a5af9f0055aef8ab4a034c48b013898d0116aac3
embedding_model: nvidia/nemotron-3-embed-1b
embedding_index_fingerprint: 21cc66059f8cd441
link_index_sha256: 11dcc4bf7f30f7b378166bbd6aade5e53004b885839faf1ce6998a3721a18a72
homonyms_sha256: b8d042ea4f51253052128b2b289befdcf00b53c88237b67050f3252242c41ab8
rerank_model: nvidia/llama-nemotron-rerank-vl-1b-v2:free
rerank_policy_version: 2026.08.4
calibration_sha256: f63b1218023371bbbece396422aa7a02025bba0da119b49cae75232755734211
rerank_status: success
rerankable_candidates: 5
rerank_attempted: 5
rerank_succeeded: 5
rerank_retrieve_top_k: 20
rerank_score_observed: 0.002-0.354
-->

# 候選語義近鄰報告：申命記 第20章

- 檢索模型：nvidia/nemotron-3-embed-1b｜重排模型：nvidia/llama-nemotron-rerank-vl-1b-v2:free（未校準/保守模式）｜全庫 3021 條
- 規則說明：字面確切匹配直接通過；其餘候選先檢索 Top 20 名再由 Reranker 重排，取前 5 名顯示。
  治理優先：同名歧義（D類）與分類不相容永遠標 ⚠。
  重排模型未校準時，⚠ 由檢索相似度規則（≥0.50 且 top-1 非同實體）決定，重排名次只當附加證據。
  字面解析：列 resolver 實際比對結果——標「請確認」者務必人工核實。

## 耶和華的爭戰（神學）
query:
- 待建立詞：耶和華的爭戰
- 出現位置：申命記 第20章
- 候選類型：神學
- 本章上下文：「因為耶和華─你們的神與你們同去，要為你們與仇敵爭戰，拯救你們」（v4）。STEP 顯示「爭戰」是 le./hi.la.Chem（H3898A，la.cham: to fight，Niphal），「拯救」是 le./ho.Shi.a'（H3467，ya.sha: to save，Hiphil）。GT《聖經精讀本》：「明確地教導他們,爭戰屬於耶和華神(撒上17:47),其勝負並不為刀槍所左右,乃是憑是否信靠神之全能。」
- 經文用詞：要為你們與仇敵爭戰

字面解析：對上既有「耶和華的爭戰」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 耶和華的爭戰 | 0.702 | link_folder/神學/耶和華的爭戰.md |
| 2 | 耶和華是戰士 | 0.642 | link_folder/神學/耶和華是戰士.md |
| 3 | 在耶和華面前 | 0.563 | link_folder/神學/在耶和華面前.md |
| 4 | 耶和華的得勝 | 0.547 | link_folder/神學/耶和華的得勝.md |
| 5 | 耶和華是我的力量我的詩歌我的拯救 | 0.535 | link_folder/神學/耶和華是我的力量我的詩歌我的拯救.md |

判定：✅ 建議使用既有條目 [[耶和華的爭戰]]（同名／字面對應）

## 神的同在（神學）
query:
- 待建立詞：神的同在
- 出現位置：申命記 第20章
- 候選類型：神學
- 本章上下文：「因為領你出埃及地的耶和華─你神與你同在」（v1）、「因為耶和華─你們的神與你們同去」（v4）。CT〔文意註解〕：「『神與你同在』神的同在是不要怕的原因，無論是攻打或是防守，得勝的秘訣乃在乎神的同在。」STEP 顯示 v1「同在」是介系詞 'i.Ma/kh（H5973A，im: with），v4 是 ha./ho.Lekh 'i.ma./Khem（H1980G，ha.lakh: to go）。
- 經文用詞：與你同在、與你們同去

字面解析：對上既有「神的同在」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 神的同在 | 0.607 | link_folder/神學/神的同在.md |
| 2 | 昂然無懼 | 0.580 | link_folder/原文/昂然無懼.md |
| 3 | 耶和華與約瑟同在 | 0.575 | link_folder/神學/耶和華與約瑟同在.md |
| 4 | 亞伯拉罕的神與我同在 | 0.573 | link_folder/神學/亞伯拉罕的神與我同在.md |
| 5 | 與神同行 | 0.566 | link_folder/神學/與神同行.md |

判定：✅ 建議使用既有條目 [[神的同在]]（同名／字面對應）

## 以色列人的官長（人物）
query:
- 待建立詞：以色列人的官長
- 出現位置：申命記 第20章
- 候選類型：人物
- 本章上下文：「官長也要對百姓宣告說」（v5）、「官長又要對百姓宣告說」（v8）、「官長對百姓宣告完了，就當派軍長率領他們」（v9）。STEP 顯示「官長」是 ha./sho.te.Rim（H7860，sho.ter: official），「軍長」是 sa.Rei tze.va.'ot（H8269 sar 加 H6635A tsa.va）。CT：「『官長』指奉命徵集士兵的官長，是文官；『軍長』指各級軍隊指揮官，是武官。」
- 經文用詞：官長

字面解析：對上既有「以色列人的官長」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 以色列人的官長 | 0.644 | link_folder/人物/以色列人的官長.md |
| 2 | 車兵長 | 0.550 | link_folder/原文/車兵長.md |
| 3 | 以色列的長老 | 0.531 | link_folder/文化/以色列的長老.md |
| 4 | 以色列的眾長老 | 0.518 | link_folder/人物/以色列的眾長老.md |
| 5 | 十二族長協助數點 | 0.509 | link_folder/事件/十二族長協助數點.md |

判定：✅ 建議使用既有條目 [[以色列人的官長]]（同名／字面對應）

## 心消化（ma.sas）（原文）
query:
- 待建立詞：心消化（ma.sas）
- 出現位置：申命記 第20章
- 候選類型：原文
- 本章上下文：「恐怕他弟兄的心消化，和他一樣」（v8）。STEP 顯示是 yi.Mas（H4549，ma.sas: to melt，Niphal）。BH 說這個融化的比喻傳達了恐懼會傳染、會瓦解群體力量。
- 經文用詞：心消化

字面解析：對上既有「心消化（ma.sas）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 心消化（ma.sas） | 0.688 | link_folder/原文/心消化（ma.sas）.md |
| 2 | 使天下萬民驚恐懼怕 | 0.390 | link_folder/原文/使天下萬民驚恐懼怕.md |
| 3 | 鬆開手與揝著手（pa.tach、qa.phats） | 0.385 | link_folder/原文/鬆開手與揝著手（pa.tach、qa.phats）.md |
| 4 | 來3：8-9 硬著心不可像瑪撒 | 0.380 | link_folder/互文/來3：8-9 硬著心不可像瑪撒.md |
| 5 | 敬畏與可畏同一字根（ya.re） | 0.378 | link_folder/原文/敬畏與可畏同一字根（ya.re）.md |

判定：✅ 建議使用既有條目 [[心消化（ma.sas）]]（同名／字面對應）

## 可憎的物（to.e.vah）（原文）
query:
- 待建立詞：可憎的物（to.e.vah）
- 出現位置：申命記 第20章
- 候選類型：原文
- 本章上下文：「免得他們教導你們學習一切可憎惡的事，就是他們向自己神所行的」（v18）。STEP 顯示是 to.'a.vo.Ta/m（H8441，to.e.vah: abomination）。CT：「他們的信仰風俗習慣已經達到令神極其憎惡的地步。」
- 經文用詞：可憎惡的事

字面解析：對上既有「可憎的物（to.e.vah）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 可憎的物（to.e.vah） | 0.689 | link_folder/原文/可憎的物（to.e.vah）.md |
| 2 | 褻瀆（cha.lal） | 0.517 | link_folder/原文/褻瀆（cha.lal）.md |
| 3 | 不可辱沒女兒使她為娼妓 | 0.491 | link_folder/主題/不可辱沒女兒使她為娼妓.md |
| 4 | 不可照他們那樣事奉耶和華 | 0.491 | link_folder/神學/不可照他們那樣事奉耶和華.md |
| 5 | 行起淫亂（za.nah） | 0.485 | link_folder/原文/行起淫亂（za.nah）.md |

判定：✅ 建議使用既有條目 [[可憎的物（to.e.vah）]]（同名／字面對應）

## 產業（na.cha.lah）（原文）
query:
- 待建立詞：產業（na.cha.lah）
- 出現位置：申命記 第20章
- 候選類型：原文
- 本章上下文：「但這些國民的城，耶和華─你神既賜你為業」（v16）。STEP 顯示「為業」是 na.cha.Lah（H5159，na.cha.lah: inheritance）。BH 指出這份基業是神向亞伯拉罕、以撒、雅各所應許的，不只是territory，也是要按神的律法而活的託付。
- 經文用詞：賜你為業

字面解析：對上既有「產業（na.cha.lah）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 產業（na.cha.lah） | 0.674 | link_folder/原文/產業（na.cha.lah）.md |
| 2 | 業地（a.chuz.zah） | 0.587 | link_folder/原文/業地（a.chuz.zah）.md |
| 3 | 這地必落給你們為業（na.phal） | 0.573 | link_folder/原文/這地必落給你們為業（na.phal）.md |
| 4 | 耶和華是事奉者的業與分 | 0.542 | link_folder/神學/耶和華是事奉者的業與分.md |
| 5 | 為業（ye.ru.shah） | 0.530 | link_folder/原文/為業（ye.ru.shah）.md |

判定：✅ 建議使用既有條目 [[產業（na.cha.lah）]]（同名／字面對應）

## 迦南七族（迦南地原住民）（背景）
query:
- 待建立詞：迦南七族（迦南地原住民）
- 出現位置：申命記 第20章
- 候選類型：背景
- 本章上下文：「只要照耶和華─你神所吩咐的將這赫人、亞摩利人、迦南人、比利洗人、希未人、耶布斯人都滅絕淨盡」（v17）——本章只列六族。CT 逐一交代各族的居地與來歷。
- 經文用詞：赫人、亞摩利人、迦南人、比利洗人、希未人、耶布斯人

字面解析：對上既有「迦南七族（迦南地原住民）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 迦南七族（迦南地原住民） | 0.806 | link_folder/背景/迦南七族（迦南地原住民）.md |
| 2 | 迦南人 | 0.766 | link_folder/人物/迦南人.md |
| 3 | 迦南人與比利洗人 | 0.748 | link_folder/歷史/迦南人與比利洗人.md |
| 4 | 比利洗人 | 0.721 | link_folder/人物/比利洗人.md |
| 5 | 迦南地的居民分佈 | 0.715 | link_folder/背景/迦南地的居民分佈.md |

判定：✅ 建議使用既有條目 [[迦南七族（迦南地原住民）]]（同名／字面對應）

## 迦南滅絕命令的歷史範圍（解經爭議）
query:
- 待建立詞：迦南滅絕命令的歷史範圍
- 出現位置：申命記 第20章
- 候選類型：解經爭議
- 本章上下文：「其中凡有氣息的，一個不可存留」（v16）。GT《串珠》：「有人以為這做法有欠人道，然而此舉正是罪惡滿盈的迦南居民該受的審判（參創15:16），也是保持新興以色列國純正無疵之法（18）。」KC 說本章的和平提議只適用於迦南地以外的城。
- 經文用詞：其中凡有氣息的，一個不可存留

字面解析：對上既有「迦南滅絕命令的歷史範圍」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 迦南滅絕命令的歷史範圍 | 0.671 | link_folder/解經爭議/迦南滅絕命令的歷史範圍.md |
| 2 | 迦南人 | 0.608 | link_folder/人物/迦南人.md |
| 3 | 迦南 | 0.558 | link_folder/人物/迦南.md |
| 4 | 迦南人與比利洗人 | 0.555 | link_folder/歷史/迦南人與比利洗人.md |
| 5 | 迦南地 | 0.554 | link_folder/地點/迦南地.md |

判定：✅ 建議使用既有條目 [[迦南滅絕命令的歷史範圍]]（同名／字面對應）

## 平安（shalom）（原文）
query:
- 待建立詞：平安（shalom）
- 出現位置：申命記 第20章
- 候選類型：原文
- 本章上下文：「先要對城裡的民宣告和睦的話」（v10）、「他們若以和睦的話回答你」（v11）。STEP 顯示兩處都是 sha.Lom（H7965G），v12「和好」則是動詞 tash.Lim（H7999B，sha.lam: to ally，Hiphil）。CT〔話中之光〕：「神希望所有的人都知道神是和睦(原文是平安)的神，是賜平安的神。」
- 經文用詞：和睦的話

字面解析：對上既有「平安（shalom）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 平安（shalom） | 0.693 | link_folder/原文/平安（shalom）.md |
| 2 | 平安的約 | 0.613 | link_folder/主題/平安的約.md |
| 3 | 得享平安（nu.ach） | 0.587 | link_folder/原文/得享平安（nu.ach）.md |
| 4 | 平安祭 | 0.547 | link_folder/神學/平安祭.md |
| 5 | 「撒冷」名字含義 | 0.519 | link_folder/原文/「撒冷」名字含義.md |

判定：✅ 建議使用既有條目 [[平安（shalom）]]（同名／字面對應）

## 滅絕（herem）（神學）
query:
- 待建立詞：滅絕（herem）
- 出現位置：申命記 第20章
- 候選類型：神學
- 本章上下文：「都滅絕淨盡」（v17）。STEP 顯示是 ha.cha.Rem ta.cha.ri.Me/m（H2763A，cha.ram: to devote/destroy，不定詞絕對式加未完成式）。GT《舊約背景註釋》：「這習慣希伯來語稱為赫倫，軍事策略中十分罕見。」BH 也稱之為 herem。
- 經文用詞：滅絕淨盡

字面解析：對上既有「滅絕（herem）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 滅絕（herem） | 0.696 | link_folder/神學/滅絕（herem）.md |
| 2 | 滅絕 | 0.653 | link_folder/原文/滅絕.md |
| 3 | 滅盡與除滅的雙同字（sha.mad） | 0.531 | link_folder/原文/滅盡與除滅的雙同字（sha.mad）.md |
| 4 | 迦南滅絕命令的歷史範圍 | 0.520 | link_folder/解經爭議/迦南滅絕命令的歷史範圍.md |
| 5 | 荒堆（tel） | 0.514 | link_folder/原文/荒堆（tel）.md |

判定：✅ 建議使用既有條目 [[滅絕（herem）]]（同名／字面對應）

## 戰利品的分配辦法（主題）
query:
- 待建立詞：戰利品的分配辦法
- 出現位置：申命記 第20章
- 候選類型：主題
- 本章上下文：「惟有婦女、孩子、牲畜，和城內一切的財物，你可以取為自己的掠物」（v14）。STEP 顯示「掠物」是 she.la.La/h／she.Lal（H7998，sha.lal: spoil），動詞是 ta.Voz（H962，ba.zaz: to plunder）。GT《舊約背景註釋》說古代近東不發糧餉，而從攻取村鎮的戰利品中分配一部分給士兵。
- 經文用詞：掠物

字面解析：對上既有「戰利品的分配辦法」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 戰利品的分配辦法 | 0.644 | link_folder/主題/戰利品的分配辦法.md |
| 2 | 出埃及時取得埃及財物 | 0.529 | link_folder/解經爭議/出埃及時取得埃及財物.md |
| 3 | 古代近東以什一奉獻為神職薪酬 | 0.518 | link_folder/文化/古代近東以什一奉獻為神職薪酬.md |
| 4 | 古代近東偷竊賠償法 | 0.514 | link_folder/背景/古代近東偷竊賠償法.md |
| 5 | 拈鬮分地（go.ral） | 0.491 | link_folder/主題/拈鬮分地（go.ral）.md |

判定：✅ 建議使用既有條目 [[戰利品的分配辦法]]（同名／字面對應）

## 迦南地栽種果樹頭三年果子如未受割禮的條例（主題）
query:
- 待建立詞：迦南地栽種果樹頭三年果子如未受割禮的條例
- 出現位置：申命記 第20章
- 候選類型：主題
- 本章上下文：「誰種葡萄園，尚未用所結的果子」（v6）。CT：「新種的果樹，頭三年所結的果子，主人不能享用；第四年所結的果子，要當作初熟的果子獻給神；第五年以後所結的果子，才可以享用(參利十九23~25)。」GT《串珠》：「「尚未用所結的果子」：即種葡萄園不足五年」。
- 經文用詞：尚未用所結的果子

字面解析：對上既有「迦南地栽種果樹頭三年果子如未受割禮的條例」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 迦南地栽種果樹頭三年果子如未受割禮的條例 | 0.807 | link_folder/主題/迦南地栽種果樹頭三年果子如未受割禮的條例.md |
| 2 | 初熟果子 | 0.554 | link_folder/神學/初熟果子.md |
| 3 | 古代近東初熟果子奉獻 | 0.535 | link_folder/背景/古代近東初熟果子奉獻.md |
| 4 | 迦南地的七樣出產 | 0.525 | link_folder/主題/迦南地的七樣出產.md |
| 5 | 初熟 | 0.513 | link_folder/原文/初熟.md |

判定：✅ 建議使用既有條目 [[迦南地栽種果樹頭三年果子如未受割禮的條例]]（同名／字面對應）

## 爭戰前受膏祭司的宣告（主題）
query:
- 待建立詞：爭戰前受膏祭司的宣告
- 出現位置：申命記 第20章
- 候選類型：主題
- 本章上下文：「你們將要上陣的時候，祭司要到百姓面前宣告」（v2），宣告內容見 v3-4。CT：「『祭司』非指一般祭司，乃是指像非尼哈那樣的隨軍祭司(參民三十一6)，其地位僅次於大祭司，KJV另加說明the anointed of war，即指「為戰爭受膏的祭司」」；GT《聖經精讀本》說猶太拉比稱他們為特地「為爭戰而受膏之人」。STEP 顯示 v3 用四個動詞：ye.Rakh（H7401 ra.khakh）、ti.re.'U（H3372G ya.re）、tach.pe.Zu（H2648 cha.phaz）、ta.'ar.Tzu（H6206 a.rats）。
- 經文用詞：祭司要到百姓面前宣告

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 在耶和華面前 | 0.509 | 0.354 | link_folder/神學/在耶和華面前.md |
| 2 | 受膏的祭司 | 0.517 | 0.324 | link_folder/人物/受膏的祭司.md |
| 3 | 約櫃前行與停住的宣告 | 0.449 | 0.296 | link_folder/神學/約櫃前行與停住的宣告.md |
| 4 | 亞倫和他兒子（祭司） | 0.462 | 0.223 | link_folder/人物/亞倫和他兒子（祭司）.md |
| 5 | 古代近東的祭司 | 0.461 | 0.216 | link_folder/背景/古代近東的祭司.md |

rerank_margin: 0.030 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=主題 vs 條目=神學），若確為同實體請確認是否改用 [[在耶和華面前]]

## 免服兵役的四種人（主題）
query:
- 待建立詞：免服兵役的四種人
- 出現位置：申命記 第20章
- 候選類型：主題
- 本章上下文：「誰建造房屋，尚未奉獻」（v5）、「誰種葡萄園，尚未用所結的果子」（v6）、「誰聘定了妻，尚未迎娶」（v7）、「誰懼怕膽怯」（v8），四次都是「他可以回家去」。STEP 顯示 v5「奉獻」是 cha.na.Kh/o（H2596，cha.nakh: to dedicate），v7「聘定」是 'e.Ras（H781，a.ra.s: to betroth）。GT《聖經精讀本》：「不論數位的多寡,以色列軍隊皆由完全自願的人組成。」
- 經文用詞：他可以回家去

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 二十歲以外能打仗的 | 0.521 | 0.012 | link_folder/主題/二十歲以外能打仗的.md |
| 2 | 拿細耳人（nazir） | 0.512 | 0.008 | link_folder/原文/拿細耳人（nazir）.md |
| 3 | 五種必須償還的願 | 0.482 | 0.006 | link_folder/主題/五種必須償還的願.md |
| 4 | 永遠服事的奴僕 | 0.491 | 0.006 | link_folder/神學/永遠服事的奴僕.md |
| 5 | 以色列人的軍隊 | 0.485 | 0.006 | link_folder/神學/以色列人的軍隊.md |

rerank_margin: 0.004 (Top1 - Top2)
判定：⚠ 相似度居中（0.50 ≤ 0.521 < 0.70），最近鄰為 [[二十歲以外能打仗的]]——此區間真對應與無對應分數重疊，需逐一人工判斷（重排模型 nvidia/llama-nemotron-rerank-vl-1b-v2:free 未校準，上表名次僅供參考）

## 遠方城的招降條例（主題）
query:
- 待建立詞：遠方城的招降條例
- 出現位置：申命記 第20章
- 候選類型：主題
- 本章上下文：「離你甚遠的各城，不是這些國民的城，你都要這樣待他」（v15）總結 v10-14 的程序：先宣告和睦的話、開城則全城服勞役、拒絕則圍困、殺盡男丁、婦孺牲畜財物取為掠物。STEP 顯示 v11「效勞」是 la./Mas（H4522，mas: taskworker），「服事」是 va./'a.va.Du./kha（H5647G，a.vad: to serve）。
- 經文用詞：離你甚遠的各城

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 寄居的 | 0.454 | 0.015 | link_folder/原文/寄居的.md |
| 2 | 侍立事奉（a.mad、sha.rat） | 0.429 | 0.013 | link_folder/原文/侍立事奉（a.mad、sha.rat）.md |
| 3 | 匪類（be.liy.ya.al） | 0.471 | 0.013 | link_folder/原文/匪類（be.liy.ya.al）.md |
| 4 | 六十座堅固城與無城牆的鄉村 | 0.445 | 0.013 | link_folder/主題/六十座堅固城與無城牆的鄉村.md |
| 5 | 心消化（ma.sas） | 0.436 | 0.013 | link_folder/原文/心消化（ma.sas）.md |

rerank_margin: 0.001 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=主題 vs 條目=原文），若確為同實體請確認是否改用 [[寄居的]]

## 圍城不可砍伐果樹的條例（主題）
query:
- 待建立詞：圍城不可砍伐果樹的條例
- 出現位置：申命記 第20章
- 候選類型：主題
- 本章上下文：「就不可舉斧子砍壞樹木；因為你可以吃那樹上的果子，不可砍伐。田間的樹木豈是人，叫你蹧蹋嗎？」（v19）、「惟獨你所知道不是結果子的樹木可以毀壞、砍伐」（v20）。STEP 顯示「砍壞」是 tash.Chit（H7843，sha.chat: to ruin），「斧子」是 gar.Zen（H1631），v20「不是結果子的樹木」直譯是不是食物之樹（'etz ma.'a.Khal，H3978）。GT《串珠》：「不要把樹木當作那應遭毀滅的敵人而把它們砍掉。」
- 經文用詞：不可舉斧子砍壞樹木

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 流無辜血的罪 | 0.433 | 0.155 | link_folder/神學/流無辜血的罪.md |
| 2 | 迦南地栽種果樹頭三年果子如未受割禮的條例 | 0.547 | 0.095 | link_folder/主題/迦南地栽種果樹頭三年果子如未受割禮的條例.md |
| 3 | 不可挪移地界（ge.vul） | 0.440 | 0.079 | link_folder/主題/不可挪移地界（ge.vul）.md |
| 4 | 樹木 | 0.435 | 0.077 | link_folder/主題/樹木.md |
| 5 | 殺人（ratsach） | 0.467 | 0.072 | link_folder/原文/殺人（ratsach）.md |

rerank_margin: 0.060 (Top1 - Top2)
判定：⚠ 相似度居中（0.50 ≤ 0.547 < 0.70），最近鄰為 [[迦南地栽種果樹頭三年果子如未受割禮的條例]]——此區間真對應與無對應分數重疊，需逐一人工判斷（重排模型 nvidia/llama-nemotron-rerank-vl-1b-v2:free 未校準，上表名次僅供參考）

## 古代近東的圍城戰與營壘（背景）
query:
- 待建立詞：古代近東的圍城戰與營壘
- 出現位置：申命記 第20章
- 候選類型：背景
- 本章上下文：「用以修築營壘，攻擊那與你打仗的城，直到攻塌了」（v20）。STEP 顯示「營壘」是 ma.Tzor（H4692，ma.tsor: siege），v12、v19「圍困」是 tzar.Ta／ta.Tzur（H6696A，tsur: to confine）。GT《靈修版》：「考古學家在迦南地發掘出許多堅固城邑的遺跡。有些城牆有九公尺高，有堡壘、壕溝與瞭望樓。」BH 提到拉吉與夏瑣遺址留下攻城坡道與撞城錘的痕跡。
- 經文用詞：修築營壘

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 古代近東祭壇 | 0.495 | 0.035 | link_folder/背景/古代近東祭壇.md |
| 2 | 壘圈（ge.de.rah） | 0.530 | 0.024 | link_folder/原文/壘圈（ge.de.rah）.md |
| 3 | 古代近東偶像崇拜 | 0.475 | 0.023 | link_folder/背景/古代近東偶像崇拜.md |
| 4 | 密奪 | 0.497 | 0.020 | link_folder/地點/密奪.md |
| 5 | 巴珊 | 0.477 | 0.020 | link_folder/地點/巴珊.md |

rerank_margin: 0.011 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=背景 vs 條目=主題），若確為同實體請確認是否改用 [[六十座堅固城與無城牆的鄉村]]（重排模型 nvidia/llama-nemotron-rerank-vl-1b-v2:free 未校準，上表名次僅供參考）

## 候選互查（本章內部，⚠＝彼此相似 ≥ 0.8）
（無 ≥ 門檻的配對）
