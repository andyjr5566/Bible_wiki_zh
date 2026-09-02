<!-- candidate_similarity_meta
schema_version: 1
book: 申命記
chapter: 19
candidate_sha256: 029b1403420bdf5f06e4deb7f8296883040be364eb32a0148a63bf13ac111187
candidate_identity_sha256: c286b6b9cd558021b47f4a2b6a7ce419b49b3f76ba1827c8d5b005de24270bf2
embedding_model: nvidia/nemotron-3-embed-1b
embedding_index_fingerprint: 3a7ce6014dad0733
link_index_sha256: 8ba43d45a2f3ccb9fd541d813f0e937439b4043f70945bad47f0a3b138019ea9
homonyms_sha256: b8d042ea4f51253052128b2b289befdcf00b53c88237b67050f3252242c41ab8
rerank_model: nvidia/llama-nemotron-rerank-vl-1b-v2:free
rerank_policy_version: 2026.08.4
calibration_sha256: f63b1218023371bbbece396422aa7a02025bba0da119b49cae75232755734211
rerank_status: success
rerankable_candidates: 4
rerank_attempted: 4
rerank_succeeded: 4
rerank_retrieve_top_k: 20
rerank_score_observed: 0.014-0.417
-->

# 候選語義近鄰報告：申命記 第19章

- 檢索模型：nvidia/nemotron-3-embed-1b｜重排模型：nvidia/llama-nemotron-rerank-vl-1b-v2:free（未校準/保守模式）｜全庫 3017 條
- 規則說明：字面確切匹配直接通過；其餘候選先檢索 Top 20 名再由 Reranker 重排，取前 5 名顯示。
  治理優先：同名歧義（D類）與分類不相容永遠標 ⚠。
  重排模型未校準時，⚠ 由檢索相似度規則（≥0.50 且 top-1 非同實體）決定，重排名次只當附加證據。
  字面解析：列 resolver 實際比對結果——標「請確認」者務必人工核實。

## 逃城（互文）
query:
- 待建立詞：逃城
- 出現位置：申命記 第19章
- 候選類型：互文
- 本章上下文：「這人逃到那些城的一座城，就可以存活」（v5）、「便逃到這些城的一座城」（v11）；本章第1至13節是逃城制度在申命記的正式條文，交代河西那三座。STEP 顯示「逃」是 ya.Nus（H5127，nus: to flee），v3「使誤殺人的都可以逃到那裡去」是 la./Nus。
- 經文用詞：那些城的一座城、這些城的一座城

字面解析：對上既有「逃城」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 逃城 | 0.734 | link_folder/互文/逃城.md |
| 2 | 申19：1-13 | 0.641 | link_folder/互文/申19：1-13.md |
| 3 | 民35：9-34 | 0.638 | link_folder/互文/民35：9-34.md |
| 4 | 摩西分定河東三座逃城（ba.dal） | 0.614 | link_folder/事件/摩西分定河東三座逃城（ba.dal）.md |
| 5 | 書20：1-9 | 0.588 | link_folder/互文/書20：1-9.md |

判定：✅ 建議使用既有條目 [[逃城]]（同名／字面對應）

## 申19：1-13（互文）
query:
- 待建立詞：申19：1-13
- 出現位置：申命記 第19章
- 候選類型：互文
- 本章上下文：本條目名稱所指的整段經文。第8至9節另給一個條件式擴充：耶和華若照向列祖所起的誓擴張境界，且百姓謹守遵行，「就要在這三座城之外，再添三座城」。GT《雷氏研讀本》說這三座城從來沒有加添上去，因為以色列人並沒有佔領應許賜給亞伯拉罕的所有土地；GT《串珠》說即把城的數目由六座增至九座。
- 經文用詞：再添三座城

字面解析：對上既有「申19：1-13」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 申19：1-13 | 0.731 | link_folder/互文/申19：1-13.md |
| 2 | 利未人的四十八座城 | 0.496 | link_folder/主題/利未人的四十八座城.md |
| 3 | 進迦南應許 | 0.488 | link_folder/歷史/進迦南應許.md |
| 4 | 出19：8 | 0.482 | link_folder/互文/出19：8.md |
| 5 | 逃城 | 0.479 | link_folder/互文/逃城.md |

判定：✅ 建議使用既有條目 [[申19：1-13]]（同名／字面對應）

## 摩西分定河東三座逃城（ba.dal）（事件）
query:
- 待建立詞：摩西分定河東三座逃城（ba.dal）
- 出現位置：申命記 第19章
- 候選類型：事件
- 本章上下文：「就要在耶和華─你神所賜你為業的地上分定三座城」（v2）、「所以我吩咐你說，要分定三座城」（v7）；STEP 顯示「分定」是 tav.Dil（H914，ba.dal: to separate），與申4:41 摩西在河東分定三座城用的是同一個動詞。GT《啟導本》說這之前摩西已在約但河東為兩個半支派設立了三座。
- 經文用詞：分定三座城

字面解析：對上既有「摩西分定河東三座逃城（ba.dal）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 摩西分定河東三座逃城（ba.dal） | 0.823 | link_folder/事件/摩西分定河東三座逃城（ba.dal）.md |
| 2 | 逃城 | 0.594 | link_folder/互文/逃城.md |
| 3 | 兩支派半求河東之地為業 | 0.559 | link_folder/事件/兩支派半求河東之地為業.md |
| 4 | 申19：1-13 | 0.545 | link_folder/互文/申19：1-13.md |
| 5 | 約但河 | 0.533 | link_folder/地點/約但河.md |

判定：✅ 建議使用既有條目 [[摩西分定河東三座逃城（ba.dal）]]（同名／字面對應）

## 殺人（ratsach）（原文）
query:
- 待建立詞：殺人（ratsach）
- 出現位置：申命記 第19章
- 候選類型：原文
- 本章上下文：「使誤殺人的，都可以逃到那裡去」（v3）、「誤殺人的逃到那裡可以存活」（v4）；STEP 顯示三次都是 ro.Tze.ach（H7523，ra.tsach: to murder），同一個字既涵蓋誤殺也涵蓋 v11 的蓄意殺人。
- 經文用詞：誤殺人的

字面解析：對上既有「殺人（ratsach）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 殺人（ratsach） | 0.729 | link_folder/原文/殺人（ratsach）.md |
| 2 | 謀殺與誤殺的區分 | 0.549 | link_folder/神學/謀殺與誤殺的區分.md |
| 3 | 埋伏 | 0.535 | link_folder/原文/埋伏.md |
| 4 | 不可殺人 | 0.499 | link_folder/神學/不可殺人.md |
| 5 | 古代近東祭壇庇護 | 0.473 | link_folder/背景/古代近東祭壇庇護.md |

判定：✅ 建議使用既有條目 [[殺人（ratsach）]]（同名／字面對應）

## 謀殺與誤殺的區分（神學）
query:
- 待建立詞：謀殺與誤殺的區分
- 出現位置：申命記 第19章
- 候選類型：神學
- 本章上下文：「凡素無仇恨，無心殺了人的」（v4）對照「若有人恨他的鄰舍，埋伏著起來擊殺他」（v11）；STEP 顯示 v4 是 bi/v.li- Da.'at（H1097 加 H1847，da.at: knowledge）與 lo'- so.Ne'（H8130，sa.ne: to hate），v11 是 so.Ne' 加 ve./'A.rav（H693，a.rav: to ambush）。
- 經文用詞：無心殺了人的、埋伏著起來擊殺他

字面解析：對上既有「謀殺與誤殺的區分」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 謀殺與誤殺的區分 | 0.660 | link_folder/神學/謀殺與誤殺的區分.md |
| 2 | 殺人（ratsach） | 0.625 | link_folder/原文/殺人（ratsach）.md |
| 3 | 埋伏 | 0.601 | link_folder/原文/埋伏.md |
| 4 | 不可搬弄是非不可與鄰舍為敵 | 0.541 | link_folder/主題/不可搬弄是非不可與鄰舍為敵.md |
| 5 | 不可心裡恨弟兄總要指摘鄰舍 | 0.538 | link_folder/主題/不可心裡恨弟兄總要指摘鄰舍.md |

判定：✅ 建議使用既有條目 [[謀殺與誤殺的區分]]（同名／字面對應）

## 憑幾個見證人的口（主題）
query:
- 待建立詞：憑幾個見證人的口
- 出現位置：申命記 第19章
- 候選類型：主題
- 本章上下文：「不可憑一個人的口作見證，總要憑兩三個人的口作見證才可定案」（v15）；STEP 顯示「見證人」是 'ed／'e.Dim（H5707），「口」是 pi（H6310I），「定案」是 ya.Kum da.Var（H6965I 加 H1697G）。
- 經文用詞：憑兩三個人的口作見證

字面解析：對上既有「憑幾個見證人的口」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 憑幾個見證人的口 | 0.602 | link_folder/主題/憑幾個見證人的口.md |
| 2 | 不可作假見證陷害人 | 0.468 | link_folder/神學/不可作假見證陷害人.md |
| 3 | 法度（e.dah） | 0.434 | link_folder/原文/法度（e.dah）.md |
| 4 | 按手在犯人頭上作見證（利24：14） | 0.418 | link_folder/主題/按手在犯人頭上作見證（利24：14）.md |
| 5 | 呼天喚地作見證（ud） | 0.406 | link_folder/主題/呼天喚地作見證（ud）.md |

判定：✅ 建議使用既有條目 [[憑幾個見證人的口]]（同名／字面對應）

## 不可作假見證陷害人（神學）
query:
- 待建立詞：不可作假見證陷害人
- 出現位置：申命記 第19章
- 候選類型：神學
- 本章上下文：「若見證人果然是作假見證的，以假見證陷害弟兄」（v18）；STEP 顯示是 'ed- she.ker（H5707 加 H8267，she.qer: deception）。KC 說本章詳述的三條誡命之一就是不可作假見證陷害鄰舍。
- 經文用詞：作假見證的

字面解析：對上既有「不可作假見證陷害人」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 不可作假見證陷害人 | 0.690 | link_folder/神學/不可作假見證陷害人.md |
| 2 | 不可搬弄是非不可與鄰舍為敵 | 0.625 | link_folder/主題/不可搬弄是非不可與鄰舍為敵.md |
| 3 | 不可心裡恨弟兄總要指摘鄰舍 | 0.548 | link_folder/主題/不可心裡恨弟兄總要指摘鄰舍.md |
| 4 | 不可妄稱耶和華你神的名 | 0.509 | link_folder/神學/不可妄稱耶和華你神的名.md |
| 5 | 不作見證的罪 | 0.502 | link_folder/神學/不作見證的罪.md |

判定：✅ 建議使用既有條目 [[不可作假見證陷害人]]（同名／字面對應）

## 審判官（原文）
query:
- 待建立詞：審判官
- 出現位置：申命記 第19章
- 候選類型：原文
- 本章上下文：「和當時的祭司，並審判官面前」（v17）、「審判官要細細地查究」（v18）；STEP 顯示是 ha./Sho.fe.Tim（H8199，sha.phat: to judge）。
- 經文用詞：審判官

字面解析：對上既有「審判官」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 審判官 | 0.642 | link_folder/原文/審判官.md |
| 2 | 申1：17 | 0.555 | link_folder/互文/申1：17.md |
| 3 | 申16：18-20 | 0.538 | link_folder/互文/申16：18-20.md |
| 4 | 審判不可行不義按公義審判 | 0.523 | link_folder/主題/審判不可行不義按公義審判.md |
| 5 | 不可看人的外貌（na.khar） | 0.518 | link_folder/原文/不可看人的外貌（na.khar）.md |

判定：✅ 建議使用既有條目 [[審判官]]（同名／字面對應）

## 以色列的長老（文化）
query:
- 待建立詞：以色列的長老
- 出現位置：申命記 第19章
- 候選類型：文化
- 本章上下文：「本城的長老就要打發人去，從那裡帶出他來」（v12）；STEP 顯示是 zik.Nei i.R/o（H2205G 加 H5892B）。CT 說『本城的長老』指那擁有審判權的官長，通常年歲較長。
- 經文用詞：本城的長老

字面解析：對上既有「以色列的長老」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 以色列的長老 | 0.726 | link_folder/文化/以色列的長老.md |
| 2 | 以色列的眾長老 | 0.576 | link_folder/人物/以色列的眾長老.md |
| 3 | 以色列人的官長 | 0.499 | link_folder/人物/以色列人的官長.md |
| 4 | 審判官 | 0.479 | link_folder/原文/審判官.md |
| 5 | 十二族長協助數點 | 0.469 | link_folder/事件/十二族長協助數點.md |

判定：✅ 建議使用既有條目 [[以色列的長老]]（同名／字面對應）

## 立他名的居所（中央聖所）（主題）
query:
- 待建立詞：立他名的居所（中央聖所）
- 出現位置：申命記 第19章
- 候選類型：主題
- 本章上下文：「這兩個爭訟的人就要站在耶和華面前，和當時的祭司，並審判官面前」（v17）；GT《聖經精讀本》說由此可知關於偽證罪或誣告罪的案件是由中央聖所的大法庭來審理（17:8,9）。
- 經文用詞：站在耶和華面前

字面解析：對上既有「立他名的居所（中央聖所）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 立他名的居所（中央聖所） | 0.575 | link_folder/主題/立他名的居所（中央聖所）.md |
| 2 | 難斷的案件上訴到中央聖所 | 0.556 | link_folder/主題/難斷的案件上訴到中央聖所.md |
| 3 | 審判官 | 0.500 | link_folder/原文/審判官.md |
| 4 | 神的聖所 | 0.480 | link_folder/神學/神的聖所.md |
| 5 | 聖所 | 0.473 | link_folder/地點/聖所.md |

判定：✅ 建議使用既有條目 [[立他名的居所（中央聖所）]]（同名／字面對應）

## 把那惡從你們中間除掉（ba.ar）（神學）
query:
- 待建立詞：把那惡從你們中間除掉（ba.ar）
- 出現位置：申命記 第19章
- 候選類型：神學
- 本章上下文：「這樣，就把那惡從你們中間除掉」（v19）；STEP 顯示是 u./vi.'ar.Ta ha./Ra' mi./kir.Be./cha（H1197I 加 H7451B 加 H7130G），與申13:5、17:7 是同一個公式；第13節「除掉流無辜血的罪」用的也是 u./vi.'ar.Ta。
- 經文用詞：把那惡從你們中間除掉

字面解析：對上既有「把那惡從你們中間除掉（ba.ar）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 把那惡從你們中間除掉（ba.ar） | 0.776 | link_folder/神學/把那惡從你們中間除掉（ba.ar）.md |
| 2 | 林前5：13 | 0.540 | link_folder/互文/林前5：13.md |
| 3 | 除污穢的水 | 0.522 | link_folder/神學/除污穢的水.md |
| 4 | 未見雅各中有罪孽 | 0.517 | link_folder/神學/未見雅各中有罪孽.md |
| 5 | 匪類（be.liy.ya.al） | 0.512 | link_folder/原文/匪類（be.liy.ya.al）.md |

判定：✅ 建議使用既有條目 [[把那惡從你們中間除掉（ba.ar）]]（同名／字面對應）

## 求問與訪問同一個字（da.rash）（原文）
query:
- 待建立詞：求問與訪問同一個字（da.rash）
- 出現位置：申命記 第19章
- 候選類型：原文
- 本章上下文：「審判官要細細地查究」（v18）；STEP 顯示是 ve./da.re.Shu（H1875，da.rash）加 hei.Tev（H3190，ya.tav: be good），是這個動詞在申命記的又一種對象——查案。
- 經文用詞：細細地查究

字面解析：對上既有「求問與訪問同一個字（da.rash）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 求問與訪問同一個字（da.rash） | 0.722 | link_folder/原文/求問與訪問同一個字（da.rash）.md |
| 2 | 探聽查究細細地訪問（da.rash、cha.qar、sha.al） | 0.688 | link_folder/原文/探聽查究細細地訪問（da.rash、cha.qar、sha.al）.md |
| 3 | 審判官 | 0.513 | link_folder/原文/審判官.md |
| 4 | 盡心盡性尋求（ba.qash、da.rash） | 0.499 | link_folder/原文/盡心盡性尋求（ba.qash、da.rash）.md |
| 5 | 眷顧（da.rash） | 0.473 | link_folder/原文/眷顧（da.rash）.md |

判定：✅ 建議使用既有條目 [[求問與訪問同一個字（da.rash）]]（同名／字面對應）

## 產業（na.cha.lah）（原文）
query:
- 待建立詞：產業（na.cha.lah）
- 出現位置：申命記 第19章
- 候選類型：原文
- 本章上下文：「在耶和華─你神所賜你承受為業之地，不可挪移你鄰舍的地界」（v14）；STEP 顯示是 be./na.cha.la.te./Kha（H5159）加 tin.Chal（H5157，na.chal: to inherit），名詞與同源動詞在同一節連用。
- 經文用詞：承受為業之地

字面解析：對上既有「產業（na.cha.lah）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 產業（na.cha.lah） | 0.746 | link_folder/原文/產業（na.cha.lah）.md |
| 2 | 業地（a.chuz.zah） | 0.620 | link_folder/原文/業地（a.chuz.zah）.md |
| 3 | 這地必落給你們為業（na.phal） | 0.591 | link_folder/原文/這地必落給你們為業（na.phal）.md |
| 4 | 為業（ye.ru.shah） | 0.535 | link_folder/原文/為業（ye.ru.shah）.md |
| 5 | 各守各的產業（da.vaq） | 0.533 | link_folder/原文/各守各的產業（da.vaq）.md |

判定：✅ 建議使用既有條目 [[產業（na.cha.lah）]]（同名／字面對應）

## 以眼還眼（神學）
query:
- 待建立詞：以眼還眼
- 出現位置：申命記 第19章
- 候選類型：神學
- 本章上下文：「你眼不可顧惜，要以命償命，以眼還眼，以牙還牙，以手還手，以腳還腳」（v21）；STEP 顯示是 Ne.fesh be./Ne.fesh、'A.yin be./'A.yin、shen be./Shen、yad be./Yad、Re.gel be./Ra.gel 五組同字對舉。
- 經文用詞：以眼還眼

字面解析：對上既有「以眼還眼」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 以眼還眼 | 0.716 | link_folder/神學/以眼還眼.md |
| 2 | 申19：21 | 0.627 | link_folder/互文/申19：21.md |
| 3 | 太5：38-39 | 0.588 | link_folder/互文/太5：38-39.md |
| 4 | 同態復仇法 | 0.585 | link_folder/原文/同態復仇法.md |
| 5 | 以眼還眼的適用範圍 | 0.578 | link_folder/解經爭議/以眼還眼的適用範圍.md |

判定：✅ 建議使用既有條目 [[以眼還眼]]（同名／字面對應）

## 以眼還眼的適用範圍（解經爭議）
query:
- 待建立詞：以眼還眼的適用範圍
- 出現位置：申命記 第19章
- 候選類型：解經爭議
- 本章上下文：第21節在本章的位置很特別：它不是判傷害案，而是判作假見證的人。GT《聖經精讀本》說這絕不是個人性的復仇方法，而只是說明了由司法機關執行刑罰；CT 也說這一節所定的原則是給審判官使用的，並不適用於個人的報復。KC 則說主耶穌沒有廢掉這條律法，只是宣告它不適用於個人恩怨。
- 經文用詞：以命償命

字面解析：對上既有「以眼還眼的適用範圍」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 以眼還眼的適用範圍 | 0.794 | link_folder/解經爭議/以眼還眼的適用範圍.md |
| 2 | 以眼還眼 | 0.723 | link_folder/神學/以眼還眼.md |
| 3 | 同態復仇法 | 0.677 | link_folder/原文/同態復仇法.md |
| 4 | 打死人與打死牲畜的賠償原則 | 0.656 | link_folder/主題/打死人與打死牲畜的賠償原則.md |
| 5 | 申19：21 | 0.654 | link_folder/互文/申19：21.md |

判定：✅ 建議使用既有條目 [[以眼還眼的適用範圍]]（同名／字面對應）

## 報血仇的（ga.al）（原文）
query:
- 待建立詞：報血仇的（ga.al）
- 出現位置：申命記 第19章
- 候選類型：原文
- 本章上下文：「免得報血仇的，心中火熱追趕他」（v6）、「交在報血仇的手中，將他治死」（v12）；STEP 顯示是 go.'El ha./Dam（H1350H，ga.al: to redeem: avenge 加 H1818 dam: blood）。CT 說指死者的至近親屬；GT《聖經精讀本》說含有償還、賠償之意，可翻譯為償還者、報仇者。
- 經文用詞：報血仇的

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 古代近東血仇制度 | 0.554 | 0.417 | link_folder/背景/古代近東血仇制度.md |
| 2 | 報仇（na.qam 與 nik.mah） | 0.605 | 0.346 | link_folder/原文/報仇（na.qam 與 nik.mah）.md |
| 3 | 救贖goel | 0.680 | 0.293 | link_folder/神學/救贖goel.md |
| 4 | 殺人（ratsach） | 0.527 | 0.188 | link_folder/原文/殺人（ratsach）.md |
| 5 | 亞伯的血哀告 | 0.495 | 0.157 | link_folder/神學/亞伯的血哀告.md |

rerank_margin: 0.070 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=原文 vs 條目=背景），若確為同實體請確認是否改用 [[古代近東血仇制度]]

## 不可挪移地界（ge.vul）（主題）
query:
- 待建立詞：不可挪移地界（ge.vul）
- 出現位置：申命記 第19章
- 候選類型：主題
- 本章上下文：「在耶和華─你神所賜你承受為業之地，不可挪移你鄰舍的地界，那是先人所定的」（v14）；STEP 顯示「挪移」是 ta.Sig（H5253，na.sag: to remove），「地界」是 ge.Vul（H1366G，ge.vul: border: boundary），「先人所定的」是 ga.ve.Lu ri.sho.Nim（H1379 加 H7223H）。
- 經文用詞：不可挪移你鄰舍的地界

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 不可搬弄是非不可與鄰舍為敵 | 0.444 | 0.322 | link_folder/主題/不可搬弄是非不可與鄰舍為敵.md |
| 2 | 山的界限 | 0.463 | 0.202 | link_folder/神學/山的界限.md |
| 3 | 神所定的邊界 | 0.571 | 0.193 | link_folder/神學/神所定的邊界.md |
| 4 | 以色列人經過還是繞過以東境界 | 0.438 | 0.188 | link_folder/解經爭議/以色列人經過還是繞過以東境界.md |
| 5 | 產業（na.cha.lah） | 0.460 | 0.175 | link_folder/原文/產業（na.cha.lah）.md |

rerank_margin: 0.120 (Top1 - Top2)
判定：⚠ 相似度居中（0.50 ≤ 0.571 < 0.70），最近鄰為 [[神所定的邊界]]——此區間真對應與無對應分數重疊，需逐一人工判斷（重排模型 nvidia/llama-nemotron-rerank-vl-1b-v2:free 未校準，上表名次僅供參考）

## 預備往逃城的道路（主題）
query:
- 待建立詞：預備往逃城的道路
- 出現位置：申命記 第19章
- 候選類型：主題
- 本章上下文：「又要預備道路，使誤殺人的，都可以逃到那裡去」（v3）；STEP 顯示是 ta.Khin（H3559K，kun: to establish）加 ha./de.reKh（H1870K，de.rekh: way: road），並以 ve./shi.lash.Ta（H8027，sha.lash: to do three）把地分為三段。CT、GT《聖經精讀本》與 KC 各自記下猶太傳統對這條路的規格。
- 經文用詞：預備道路

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 申19：1-13 | 0.500 | 0.135 | link_folder/互文/申19：1-13.md |
| 2 | 逃城 | 0.558 | 0.098 | link_folder/互文/逃城.md |
| 3 | 摩西分定河東三座逃城（ba.dal） | 0.504 | 0.066 | link_folder/事件/摩西分定河東三座逃城（ba.dal）.md |
| 4 | 民35：9-34 | 0.484 | 0.057 | link_folder/互文/民35：9-34.md |
| 5 | 書20：1-9 | 0.453 | 0.049 | link_folder/互文/書20：1-9.md |

rerank_margin: 0.038 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=主題 vs 條目=互文），若確為同實體請確認是否改用 [[申19：1-13]]

## 流無辜血的罪（神學）
query:
- 待建立詞：流無辜血的罪
- 出現位置：申命記 第19章
- 候選類型：神學
- 本章上下文：「免得無辜之人的血流在耶和華─你神所賜你為業的地上，流血的罪就歸於你」（v10）、「卻要從以色列中除掉流無辜血的罪」（v13）；STEP 顯示「無辜」是 ha./na.Ki（H5355A，na.qi: innocent），「血」是 dam（H1818）。
- 經文用詞：流血的罪、流無辜血的罪

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 血 | 0.583 | 0.221 | link_folder/主題/血.md |
| 2 | 把那惡從你們中間除掉（ba.ar） | 0.520 | 0.181 | link_folder/神學/把那惡從你們中間除掉（ba.ar）.md |
| 3 | 他的血要歸到他身上 | 0.556 | 0.174 | link_folder/原文/他的血要歸到他身上.md |
| 4 | 亞伯的血哀告 | 0.590 | 0.168 | link_folder/神學/亞伯的血哀告.md |
| 5 | 那地不得潔淨（ki.pher） | 0.604 | 0.161 | link_folder/原文/那地不得潔淨（ki.pher）.md |

rerank_margin: 0.040 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=神學 vs 條目=主題），若確為同實體請確認是否改用 [[血]]

## 候選互查（本章內部，⚠＝彼此相似 ≥ 0.8）
（無 ≥ 門檻的配對）
