<!-- candidate_similarity_meta
schema_version: 1
book: 申命記
chapter: 25
candidate_sha256: aedbc7295acdc6abd2bd99c030fb471c5c72d947b6f7b80046d31c77f4ff0ebc
candidate_identity_sha256: 32ed5ff2b44e02f2e68c60d82a6d67f652a727c4fe6d5d85e35292d099a9a96b
embedding_model: nvidia/nemotron-3-embed-1b
embedding_index_fingerprint: d1e5c1b2a6d65544
link_index_sha256: ebb7c93a5d747c539bbe859b1c759ec7d3a39983f69016489af8590afb1db03f
homonyms_sha256: b8d042ea4f51253052128b2b289befdcf00b53c88237b67050f3252242c41ab8
rerank_model: nvidia/llama-nemotron-rerank-vl-1b-v2:free
rerank_policy_version: 2026.08.4
calibration_sha256: f63b1218023371bbbece396422aa7a02025bba0da119b49cae75232755734211
rerank_status: success
rerankable_candidates: 8
rerank_attempted: 8
rerank_succeeded: 8
rerank_retrieve_top_k: 20
rerank_score_observed: 0.001-0.410
-->

# 候選語義近鄰報告：申命記 第25章

- 檢索模型：nvidia/nemotron-3-embed-1b｜重排模型：nvidia/llama-nemotron-rerank-vl-1b-v2:free（未校準/保守模式）｜全庫 3048 條
- 規則說明：字面確切匹配直接通過；其餘候選先檢索 Top 20 名再由 Reranker 重排，取前 5 名顯示。
  治理優先：同名歧義（D類）與分類不相容永遠標 ⚠。
  重排模型未校準時，⚠ 由檢索相似度規則（≥0.50 且 top-1 非同實體）決定，重排名次只當附加證據。
  字面解析：列 resolver 實際比對結果——標「請確認」者務必人工核實。

## 審判不可行不義按公義審判（主題）
query:
- 待建立詞：審判不可行不義按公義審判
- 出現位置：申命記 第25章
- 候選類型：主題
- 本章上下文：第1節「審判官就要定義人有理，定惡人有罪」。CT：『義人』指無辜的或被誣告的人；『惡人』指侵權加害別人的人。STEP：v1「定義人有理」是 hitz.Di.ku（H6663 tsa.daq 使役語態，宣告為義），「定惡人有罪」是 hir.Shi.'u（H7561）。
- 經文用詞：定義人有理，定惡人有罪

字面解析：對上既有「審判不可行不義按公義審判」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 審判不可行不義按公義審判 | 0.577 | link_folder/主題/審判不可行不義按公義審判.md |
| 2 | 公義與邪惡的對立 | 0.513 | link_folder/神學/公義與邪惡的對立.md |
| 3 | 司法公義 | 0.510 | link_folder/神學/司法公義.md |
| 4 | 公義與真理 | 0.510 | link_folder/主題/公義與真理.md |
| 5 | 申1：17 | 0.503 | link_folder/互文/申1：17.md |

判定：✅ 建議使用既有條目 [[審判不可行不義按公義審判]]（同名／字面對應）

## 審判官（原文）
query:
- 待建立詞：審判官
- 出現位置：申命記 第25章
- 候選類型：原文
- 本章上下文：第1至2節兩次出現「審判官」。STEP：本章 v2「審判官」是 ha./sho.Fet（H8199 sha.phat），與出21:6 譯作「審判官」的 ha-Elohim（H430）不是同一個字。

字面解析：對上既有「審判官」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 審判官 | 0.672 | link_folder/原文/審判官.md |
| 2 | 出21：6 | 0.594 | link_folder/互文/出21：6.md |
| 3 | 申16：18-20 | 0.568 | link_folder/互文/申16：18-20.md |
| 4 | 申1：17 | 0.557 | link_folder/互文/申1：17.md |
| 5 | 不可看人的外貌（na.khar） | 0.514 | link_folder/原文/不可看人的外貌（na.khar）.md |

判定：✅ 建議使用既有條目 [[審判官]]（同名／字面對應）

## 以色列刑罰的節制與程序保障（背景）
query:
- 待建立詞：以色列刑罰的節制與程序保障
- 出現位置：申命記 第25章
- 候選類型：背景
- 本章上下文：第2至3節規定當面伏在地上、照數責打、不可過數。CT：不要處罰過度，要適當、快速、公平、有節制地處罰。KC：The stripes must be given in the presence of the judge。
- 經文用詞：不可過數

字面解析：對上既有「以色列刑罰的節制與程序保障」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 以色列刑罰的節制與程序保障 | 0.601 | link_folder/背景/以色列刑罰的節制與程序保障.md |
| 2 | 律法與公義 | 0.440 | link_folder/主題/律法與公義.md |
| 3 | 司法公正律例 | 0.435 | link_folder/事件/司法公正律例.md |
| 4 | 古代近東司法制度 | 0.433 | link_folder/背景/古代近東司法制度.md |
| 5 | 石刑 | 0.433 | link_folder/背景/石刑.md |

判定：✅ 建議使用既有條目 [[以色列刑罰的節制與程序保障]]（同名／字面對應）

## 責打不可過四十下的條例（主題）
query:
- 待建立詞：責打不可過四十下的條例
- 出現位置：申命記 第25章
- 候選類型：主題
- 本章上下文：第1至3節。CT〔背景註解〕後來猶太人擔心責打超過四十下，寧可少打一下，保羅受過四十減一的刑罰（林後11:24）。GT《聖經精讀本》：杖打時打到三十九下。BH：flogging was a common form of punishment in the ancient Near East。
- 經文用詞：按著他的罪照數責打

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 以色列刑罰的節制與程序保障 | 0.544 | 0.048 | link_folder/背景/以色列刑罰的節制與程序保障.md |
| 2 | 傷害賠償的律例 | 0.498 | 0.026 | link_folder/事件/傷害賠償的律例.md |
| 3 | 律法與公義 | 0.488 | 0.023 | link_folder/主題/律法與公義.md |
| 4 | 同態復仇法 | 0.501 | 0.022 | link_folder/原文/同態復仇法.md |
| 5 | 以眼還眼 | 0.499 | 0.021 | link_folder/神學/以眼還眼.md |

rerank_margin: 0.022 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=主題 vs 條目=背景），若確為同實體請確認是否改用 [[以色列刑罰的節制與程序保障]]

## 四十的屬靈意義（原文）
query:
- 待建立詞：四十的屬靈意義
- 出現位置：申命記 第25章
- 候選類型：原文
- 本章上下文：第3節「只可打他四十下」。STEP：'ar.ba.'Im（H705）。KC：the number forty stands for a full punishment（Gen 7:12; Num 14:33-34）。CT 話中之光把「四十」讀作徹底。
- 經文用詞：四十下

字面解析：對上既有「四十的屬靈意義」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 四十的屬靈意義 | 0.676 | link_folder/原文/四十的屬靈意義.md |
| 2 | 曠野飄流四十年 | 0.589 | link_folder/歷史/曠野飄流四十年.md |
| 3 | 七十的屬靈意義 | 0.540 | link_folder/原文/七十的屬靈意義.md |
| 4 | 四十天降雨與一百五十天水勢 | 0.529 | link_folder/解經爭議/四十天降雨與一百五十天水勢.md |
| 5 | 四十晝夜 | 0.528 | link_folder/神學/四十晝夜.md |

判定：✅ 建議使用既有條目 [[四十的屬靈意義]]（同名／字面對應）

## 人的尊嚴（主題）
query:
- 待建立詞：人的尊嚴
- 出現位置：申命記 第25章
- 候選類型：主題
- 本章上下文：第3節「若過數，便是輕賤你的弟兄了」。STEP：「輕賤」是 nik.Lah（H7034 qa.lah，蒙羞），後面接「在你眼前」。BH：excessive punishment could lead to public humiliation and a loss of personal honor。
- 經文用詞：輕賤你的弟兄

字面解析：對上既有「人的尊嚴」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 赤身露體與羞恥 | 0.438 | link_folder/神學/赤身露體與羞恥.md |
| 2 | 摩西為人極其謙和（民12：3） | 0.429 | link_folder/神學/摩西為人極其謙和（民12：3）.md |
| 3 | 不可心裡恨弟兄總要指摘鄰舍 | 0.414 | link_folder/主題/不可心裡恨弟兄總要指摘鄰舍.md |
| 4 | 人的尊嚴 | 0.412 | link_folder/主題/人的尊嚴.md |
| 5 | 遮羞 | 0.408 | link_folder/主題/遮羞.md |

判定：✅ 建議使用既有條目 [[人的尊嚴]]（同名／字面對應）

## 不可籠住踹穀之牛的嘴（主題）
query:
- 待建立詞：不可籠住踹穀之牛的嘴
- 出現位置：申命記 第25章
- 候選類型：主題
- 本章上下文：第4節。CT〔背景註解〕農夫把收割下來的麥穗排列在禾場上，讓牛拖著沉重的打穀橇碾過麥穗。GT《聖經精讀本》描述平木板穿孔、附堅硬石頭的打穀機。KC 指出新約兩次引用（林前9:9-10、提前5:17-18）。
- 經文用詞：不可籠住他的嘴

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 不可使異類混雜（牲畜種子衣料） | 0.477 | 0.017 | link_folder/主題/不可使異類混雜（牲畜種子衣料）.md |
| 2 | 拙口笨舌 | 0.472 | 0.015 | link_folder/原文/拙口笨舌.md |
| 3 | 不可咒罵聾子絆倒瞎子 | 0.472 | 0.012 | link_folder/主題/不可咒罵聾子絆倒瞎子.md |
| 4 | 金牛犢事件 | 0.441 | 0.012 | link_folder/事件/金牛犢事件.md |
| 5 | 硬著頸項的百姓 | 0.469 | 0.011 | link_folder/神學/硬著頸項的百姓.md |

rerank_margin: 0.003 (Top1 - Top2)
判定：🆕 建議建立新條目（最相似條目僅 0.477 < 0.50）（重排模型 nvidia/llama-nemotron-rerank-vl-1b-v2:free 未校準，上表名次僅供參考）

## 工價與雇約（文化）
query:
- 待建立詞：工價與雇約
- 出現位置：申命記 第25章
- 候選類型：文化
- 本章上下文：第4節被四套註釋一致讀成作工者當得供養的原則。CT：本節所述條例，後來轉用來說明「工人得工價是應當的」。KC：so the laborer is worthy of his wages。

字面解析：對上既有「工價與雇約」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 不可欺壓鄰舍雇工工價不可過夜 | 0.479 | link_folder/主題/不可欺壓鄰舍雇工工價不可過夜.md |
| 2 | 工價與雇約 | 0.473 | link_folder/文化/工價與雇約.md |
| 3 | 四百舍客勒 | 0.403 | link_folder/文化/四百舍客勒.md |
| 4 | 沒有窮人與窮人永不斷絕（ev.yon） | 0.355 | link_folder/解經爭議/沒有窮人與窮人永不斷絕（ev.yon）.md |
| 5 | 一切的工（me.la.khah） | 0.354 | link_folder/原文/一切的工（me.la.khah）.md |

判定：✅ 建議使用既有條目 [[工價與雇約]]（同名／字面對應）

## 叔嫂婚姻（文化）
query:
- 待建立詞：叔嫂婚姻
- 出現位置：申命記 第25章
- 候選類型：文化
- 本章上下文：第5至10節。CT〔背景註解〕叔嫂婚姻（levirate marriage）是古代中東和中亞許多民族的習俗，古代赫人和亞述人都有相似的習俗。GT《聖經精讀本》列出繼代結婚的三個目的。
- 經文用詞：死人的妻不可出嫁外人

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 弟續兄孀制度 | 0.511 | 0.021 | link_folder/文化/弟續兄孀制度.md |
| 2 | 申25：5-10 | 0.543 | 0.019 | link_folder/互文/申25：5-10.md |
| 3 | 古代近東婚姻習俗 | 0.596 | 0.019 | link_folder/歷史/古代近東婚姻習俗.md |
| 4 | 申命記7_3-4 禁止與迦南人通婚 | 0.529 | 0.015 | link_folder/互文/申命記7_3-4 禁止與迦南人通婚.md |
| 5 | 不可姦淫 | 0.493 | 0.015 | link_folder/神學/不可姦淫.md |

rerank_margin: 0.002 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=文化 vs 條目=歷史），若確為同實體請確認是否改用 [[古代近東婚姻習俗]]（重排模型 nvidia/llama-nemotron-rerank-vl-1b-v2:free 未校準，上表名次僅供參考）

## 古代近東婚姻習俗（歷史）
query:
- 待建立詞：古代近東婚姻習俗
- 出現位置：申命記 第25章
- 候選類型：歷史
- 本章上下文：CT〔背景註解〕：叔嫂婚姻是古代中東和中亞許多民族的習俗，古代赫人和亞述人都有相似的習俗；文意註解另說「中東一帶地方，多有此風俗習慣」。GT《聖經精讀本》：這繼代結婚的風俗早在摩西時代的很久以前就遠傳於以色列社會與古代近東社會。

字面解析：對上既有「古代近東婚姻習俗」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 古代近東婚姻習俗 | 0.727 | link_folder/歷史/古代近東婚姻習俗.md |
| 2 | 古代近東同父異母婚姻 | 0.581 | link_folder/背景/古代近東同父異母婚姻.md |
| 3 | 古代近東聘禮制度 | 0.578 | link_folder/背景/古代近東聘禮制度.md |
| 4 | 古代近東的性禁忌與獻兒女為祭 | 0.563 | link_folder/背景/古代近東的性禁忌與獻兒女為祭.md |
| 5 | 送婢女為嫁妝 | 0.547 | link_folder/文化/送婢女為嫁妝.md |

判定：✅ 建議使用既有條目 [[古代近東婚姻習俗]]（同名／字面對應）

## 盡弟兄的本分（ya.vam）（原文）
query:
- 待建立詞：盡弟兄的本分（ya.vam）
- 出現位置：申命記 第25章
- 候選類型：原文
- 本章上下文：第5節「當盡弟兄的本分」、第7節「不給我盡弟兄的本分」。STEP：v5「他丈夫的兄弟」是 ye.va.Ma/h（H2993 名詞），「盡弟兄的本分」是 ve./yi.be.Ma/h（H2992 動詞），v7、v9「他哥哥的妻」是 ye.vim.T/o（H2994）——同一組字根的三個詞。

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 骨肉原文作弟兄 | 0.482 | 0.031 | link_folder/原文/骨肉原文作弟兄.md |
| 2 | 申25：5-10 | 0.435 | 0.031 | link_folder/互文/申25：5-10.md |
| 3 | 殷勤教訓（sha.nan） | 0.413 | 0.029 | link_folder/原文/殷勤教訓（sha.nan）.md |
| 4 | 事奉與作奴僕同一字根（a.vad） | 0.403 | 0.026 | link_folder/原文/事奉與作奴僕同一字根（a.vad）.md |
| 5 | 帶到他弟兄那裡去是什麼意思 | 0.423 | 0.025 | link_folder/解經爭議/帶到他弟兄那裡去是什麼意思.md |

rerank_margin: 0.000 (Top1 - Top2)
判定：🆕 建議建立新條目（最相似條目僅 0.482 < 0.50）（重排模型 nvidia/llama-nemotron-rerank-vl-1b-v2:free 未校準，上表名次僅供參考）

## 猶大與他瑪事件（歷史）
query:
- 待建立詞：猶大與他瑪事件
- 出現位置：申命記 第25章
- 候選類型：歷史
- 本章上下文：四套來源都以創38:8 為本條例的先例。CT：使哥哥的產業有兒子可以繼承（參創三十八8）。GT《啟導本》：兄弟續弟兄遺孀的婚姻風俗自古流行，視為天經地義（創三十八章）。KC：This use, now enacted as law, has been known for some time (Gen 38:8)。

字面解析：對上既有「猶大與他瑪事件」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 猶大與他瑪事件 | 0.575 | link_folder/歷史/猶大與他瑪事件.md |
| 2 | 弟續兄孀制度 | 0.534 | link_folder/文化/弟續兄孀制度.md |
| 3 | 他瑪被判燒死的刑罰問題 | 0.524 | link_folder/解經爭議/他瑪被判燒死的刑罰問題.md |
| 4 | 他瑪（創38） | 0.524 | link_folder/人物/他瑪（創38）.md |
| 5 | 猶大（雅各之子） | 0.507 | link_folder/人物/猶大（雅各之子）.md |

判定：✅ 建議使用既有條目 [[猶大與他瑪事件]]（同名／字面對應）

## 救贖goel（神學）
query:
- 待建立詞：救贖goel
- 出現位置：申命記 第25章
- 候選類型：神學
- 本章上下文：第5至10節。KC：Boaz must become both the redeemer and the one who performs the duty of a husband's brother。BH：This law is also seen in the story of Ruth and Boaz, where Boaz acts as a kinsman-redeemer。

字面解析：對上既有「救贖goel」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 救贖goel | 0.538 | link_folder/神學/救贖goel.md |
| 2 | 以色列人賣給外人的贖回條例 | 0.467 | link_folder/主題/以色列人賣給外人的贖回條例.md |
| 3 | 救贖 | 0.453 | link_folder/神學/救贖.md |
| 4 | 申25：5-10 | 0.440 | link_folder/互文/申25：5-10.md |
| 5 | 救贖歷史的進程 | 0.424 | link_folder/神學/救贖歷史的進程.md |

判定：✅ 建議使用既有條目 [[救贖goel]]（同名／字面對應）

## 路得記4章法勒斯家譜（互文）
query:
- 待建立詞：路得記4章法勒斯家譜
- 出現位置：申命記 第25章
- 候選類型：互文
- 本章上下文：CT 話中之光：主耶穌基督和大衛王的祖先俄備得，就是波阿斯和路得透過「叔嫂婚姻」所生的長子（太一5；得四17）。GT《啟導本》：後來這條例擴大，死者若無兄弟，他的最近親屬也須負此義務（得四章）。

字面解析：對上既有「路得記4章法勒斯家譜」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 路得記4章法勒斯家譜 | 0.681 | link_folder/互文/路得記4章法勒斯家譜.md |
| 2 | 珥和俄南死在迦南地（創38：6-10） | 0.575 | link_folder/互文/珥和俄南死在迦南地（創38：6-10）.md |
| 3 | 法勒斯 | 0.509 | link_folder/人物/法勒斯.md |
| 4 | 利未的族譜（出六14-27） | 0.478 | link_folder/歷史/利未的族譜（出六14-27）.md |
| 5 | 古代近東同父異母婚姻 | 0.464 | link_folder/背景/古代近東同父異母婚姻.md |

判定：✅ 建議使用既有條目 [[路得記4章法勒斯家譜]]（同名／字面對應）

## 塗抹（ma.chah）（原文）
query:
- 待建立詞：塗抹（ma.chah）
- 出現位置：申命記 第25章
- 候選類型：原文
- 本章上下文：第6節「免得他的名在以色列中塗抹了」與第19節「將亞瑪力的名號從天下塗抹了」。STEP：兩處是同一個動詞 ma.chah（H4229A），v6 是被動語態 yi.ma.Cheh，v19 是命令以色列去做的 tim.Cheh。

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 申25：17-19 記念亞瑪力 | 0.516 | 0.017 | link_folder/互文/申25：17-19 記念亞瑪力.md |
| 2 | 亞瑪力 | 0.491 | 0.015 | link_folder/人物/亞瑪力.md |
| 3 | 把那惡從你們中間除掉（ba.ar） | 0.448 | 0.013 | link_folder/神學/把那惡從你們中間除掉（ba.ar）.md |
| 4 | 滅絕（herem） | 0.432 | 0.013 | link_folder/神學/滅絕（herem）.md |
| 5 | 你且由著我（ra.phah） | 0.433 | 0.012 | link_folder/原文/你且由著我（ra.phah）.md |

rerank_margin: 0.002 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=原文 vs 條目=互文），若確為同實體請確認是否改用 [[申25：17-19 記念亞瑪力]]

## 以色列的長老（文化）
query:
- 待建立詞：以色列的長老
- 出現位置：申命記 第25章
- 候選類型：文化
- 本章上下文：第7至9節，寡嫂到城門長老那裡，長老召那人來問，脫鞋吐唾沫在長老面前進行。BH：The elders were respected leaders and judges within the community。
- 經文用詞：長老

字面解析：對上既有「以色列的長老」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 以色列的長老 | 0.656 | link_folder/文化/以色列的長老.md |
| 2 | 以色列的眾長老 | 0.626 | link_folder/人物/以色列的眾長老.md |
| 3 | 尊敬老人 | 0.528 | link_folder/主題/尊敬老人.md |
| 4 | 七十長老制度起源 | 0.510 | link_folder/歷史/七十長老制度起源.md |
| 5 | 城門口公共場合 | 0.493 | link_folder/歷史/城門口公共場合.md |

判定：✅ 建議使用既有條目 [[以色列的長老]]（同名／字面對應）

## 城門口公共場合（歷史）
query:
- 待建立詞：城門口公共場合
- 出現位置：申命記 第25章
- 候選類型：歷史
- 本章上下文：第7節「就要到城門長老那裡」。CT：『城門』指城門洞兩側的小房間，是以色列人處理交易和訴訟的公共會所（參得四1）。BH：The city gate was the center of civic life in ancient Israel。
- 經文用詞：城門

字面解析：對上既有「城門口公共場合」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 城門口公共場合 | 0.730 | link_folder/歷史/城門口公共場合.md |
| 2 | 城門口交易 | 0.609 | link_folder/文化/城門口交易.md |
| 3 | 會幕門口 | 0.469 | link_folder/地點/會幕門口.md |
| 4 | 基督是門（約10：7） | 0.461 | link_folder/互文/基督是門（約10：7）.md |
| 5 | 以色列的長老 | 0.439 | link_folder/文化/以色列的長老.md |

判定：✅ 建議使用既有條目 [[城門口公共場合]]（同名／字面對應）

## 脫鞋之家（文化）
query:
- 待建立詞：脫鞋之家
- 出現位置：申命記 第25章
- 候選類型：文化
- 本章上下文：第9至10節。CT〔背景註解〕「鞋」原文指古代中東人常穿的涼鞋，鞋子被古代以色列人作為交易的憑證（得四7）。GT《啟導本》：古代腳踏田地為依法取得土地所有權的象徵，脫去所穿之鞋象徵放棄權利。KC：Pulling off the shoe speaks of the opposite and means abandoning a given thing。

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 脫鞋與聖地 | 0.476 | 0.007 | link_folder/文化/脫鞋與聖地.md |
| 2 | 地不可永賣（地權屬神） | 0.435 | 0.003 | link_folder/神學/地不可永賣（地權屬神）.md |
| 3 | 田角拾穗顧念窮人的條例 | 0.424 | 0.003 | link_folder/主題/田角拾穗顧念窮人的條例.md |
| 4 | 四百舍客勒 | 0.421 | 0.003 | link_folder/文化/四百舍客勒.md |
| 5 | 腳掌可踏之處 | 0.456 | 0.003 | link_folder/原文/腳掌可踏之處.md |

rerank_margin: 0.004 (Top1 - Top2)
判定：🆕 建議建立新條目（最相似條目僅 0.476 < 0.50）（重排模型 nvidia/llama-nemotron-rerank-vl-1b-v2:free 未校準，上表名次僅供參考）

## 抓住下體要砍手的條例（主題）
query:
- 待建立詞：抓住下體要砍手的條例
- 出現位置：申命記 第25章
- 候選類型：主題
- 本章上下文：第11至12節。GT《啟導本》：這是聖經中「以命償命」之外，唯一斫斷肢體的刑罰。KC：The physical mutilation that should be used here as a punishment is the only example given in the law。STEP：v12「手」是 ka.Pa/h（H3709G 手掌），與 v11 伸出的 ya.Da/h（H3027G）不同字。
- 經文用詞：就要砍斷婦人的手

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 傷害孕婦的律例 | 0.439 | 0.009 | link_folder/事件/傷害孕婦的律例.md |
| 2 | 以眼還眼 | 0.457 | 0.007 | link_folder/神學/以眼還眼.md |
| 3 | 娶被擄女子為妻的條例 | 0.456 | 0.006 | link_folder/主題/娶被擄女子為妻的條例.md |
| 4 | 婢女行淫的贖愆祭條例 | 0.440 | 0.005 | link_folder/主題/婢女行淫的贖愆祭條例.md |
| 5 | 傷害賠償的律例 | 0.425 | 0.005 | link_folder/事件/傷害賠償的律例.md |

rerank_margin: 0.003 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=主題 vs 條目=事件），若確為同實體請確認是否改用 [[傷害孕婦的律例]]

## 公道天平法碼升斗（主題）
query:
- 待建立詞：公道天平法碼升斗
- 出現位置：申命記 第25章
- 候選類型：主題
- 本章上下文：第13至16節。GT《啟導本》指向利19:35 及注。KC：The bad merchant has a large measure for the purchase and a small measure for the sale。STEP：v15「對準公平」是 she.le.Mah（H8003 完整）配 Tze.dek（H6664G 公義），兩樣器具各配一次。
- 經文用詞：法碼

字面解析：對上既有「公道天平法碼升斗」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 公道天平法碼升斗 | 0.660 | link_folder/主題/公道天平法碼升斗.md |
| 2 | 審判不可行不義按公義審判 | 0.468 | link_folder/主題/審判不可行不義按公義審判.md |
| 3 | 律法與公義 | 0.444 | link_folder/主題/律法與公義.md |
| 4 | 利19：15 | 0.430 | link_folder/互文/利19：15.md |
| 5 | 公義與真理 | 0.428 | link_folder/主題/公義與真理.md |

判定：✅ 建議使用既有條目 [[公道天平法碼升斗]]（同名／字面對應）

## 伊法（原文）
query:
- 待建立詞：伊法
- 出現位置：申命記 第25章
- 候選類型：原文
- 本章上下文：第14至15節的「升斗」。CT〔原文字義〕「兩樣的升斗（原文雙同字）」伊法，升斗。STEP：v14、v15 都是 'ei.Fah（H374）。
- 經文用詞：升斗

字面解析：對上既有「伊法」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 心高氣傲（rum） | 0.389 | link_folder/原文/心高氣傲（rum）.md |
| 2 | 你且由著我（ra.phah） | 0.388 | link_folder/原文/你且由著我（ra.phah）.md |
| 3 | 耶和華的爭戰 | 0.382 | link_folder/神學/耶和華的爭戰.md |
| 4 | 監_坑_地牢_dungeon | 0.374 | link_folder/原文/監_坑_地牢_dungeon.md |
| 5 | 公道天平法碼升斗 | 0.373 | link_folder/主題/公道天平法碼升斗.md |

判定：✅ 建議使用既有條目 [[伊法]]（同名／字面對應）

## 可憎的物（to.e.vah）（原文）
query:
- 待建立詞：可憎的物（to.e.vah）
- 出現位置：申命記 第25章
- 候選類型：原文
- 本章上下文：第16節「因為行非義之事的人都是耶和華─你神所憎惡的」。STEP：to.'a.Vat（H8441 to.e.vah）；「非義之事」是 'A.vel（H5766A）。KC：such a conduct of ambivalence is an abomination。
- 經文用詞：所憎惡的

字面解析：對上既有「可憎的物（to.e.vah）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 可憎的物（to.e.vah） | 0.619 | link_folder/原文/可憎的物（to.e.vah）.md |
| 2 | 荒堆（tel） | 0.479 | link_folder/原文/荒堆（tel）.md |
| 3 | 心中受迷惑（pa.tah） | 0.471 | link_folder/原文/心中受迷惑（pa.tah）.md |
| 4 | 匪類（be.liy.ya.al） | 0.469 | link_folder/原文/匪類（be.liy.ya.al）.md |
| 5 | 神厭惡以色列的難題（利26：30與26：44的張力） | 0.469 | link_folder/解經爭議/神厭惡以色列的難題（利26：30與26：44的張力）.md |

判定：✅ 建議使用既有條目 [[可憎的物（to.e.vah）]]（同名／字面對應）

## 神的記念（神學）
query:
- 待建立詞：神的記念
- 出現位置：申命記 第25章
- 候選類型：神學
- 本章上下文：第17節「你要記念你們出埃及的時候」。STEP：za.Khor（H2142 zakhar 不定詞絕對形），與第19節要塗抹的「名號」ze.kher（H2143）同一字根。CT 靈訓把全章讀成神的紀念與追討。
- 經文用詞：記念

字面解析：對上既有「神的記念」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 「記念」與「守」 | 0.609 | link_folder/原文/「記念」與「守」.md |
| 2 | 神的記念 | 0.594 | link_folder/神學/神的記念.md |
| 3 | 記念我的約 | 0.585 | link_folder/神學/記念我的約.md |
| 4 | 忘記（sha.khach） | 0.541 | link_folder/原文/忘記（sha.khach）.md |
| 5 | 紀念份 | 0.533 | link_folder/原文/紀念份.md |

判定：✅ 建議使用既有條目 [[神的記念]]（同名／字面對應）

## 亞瑪力人（人物）
query:
- 待建立詞：亞瑪力人
- 出現位置：申命記 第25章
- 候選類型：人物
- 本章上下文：第17至18節。CT：『亞瑪力人』是以掃的子孫（創卅六12），是以色列人的世仇。GT《雷氏研讀本》：亞瑪力人也許是迦南人中最殘忍野蠻的一族。

字面解析：對上既有「亞瑪力人」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 亞瑪力人 | 0.687 | link_folder/人物/亞瑪力人.md |
| 2 | 亞瑪力 | 0.685 | link_folder/人物/亞瑪力.md |
| 3 | 出埃及記17章亞瑪力攻擊以色列 | 0.656 | link_folder/互文/出埃及記17章亞瑪力攻擊以色列.md |
| 4 | 亞摩利人 | 0.579 | link_folder/人物/亞摩利人.md |
| 5 | 申25：17-19 記念亞瑪力 | 0.577 | link_folder/互文/申25：17-19 記念亞瑪力.md |

判定：✅ 建議使用既有條目 [[亞瑪力人]]（同名／字面對應）

## 出埃及記17章亞瑪力攻擊以色列（互文）
query:
- 待建立詞：出埃及記17章亞瑪力攻擊以色列
- 出現位置：申命記 第25章
- 候選類型：互文
- 本章上下文：GT《串珠》「在路上怎樣待你」：見出17:8-16; 民14:39-45。GT《聖經精讀本》：指出埃及第一年二月底左右，以色列抵達何烈山附近的利非訂之時。

字面解析：對上既有「出埃及記17章亞瑪力攻擊以色列」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 出埃及記17章亞瑪力攻擊以色列 | 0.612 | link_folder/互文/出埃及記17章亞瑪力攻擊以色列.md |
| 2 | 申25：17-19 記念亞瑪力 | 0.601 | link_folder/互文/申25：17-19 記念亞瑪力.md |
| 3 | 亞瑪力人 | 0.600 | link_folder/人物/亞瑪力人.md |
| 4 | 出埃及的年代 | 0.583 | link_folder/解經爭議/出埃及的年代.md |
| 5 | 利非訂 | 0.578 | link_folder/地點/利非訂.md |

判定：✅ 建議使用既有條目 [[出埃及記17章亞瑪力攻擊以色列]]（同名／字面對應）

## 儘後邊軟弱的人（za.nav）（原文）
query:
- 待建立詞：儘後邊軟弱的人（za.nav）
- 出現位置：申命記 第25章
- 候選類型：原文
- 本章上下文：第18節「趁你疲乏困倦擊殺你儘後邊軟弱的人」。STEP：動詞 va/y.za.Nev（H2179 za.nav，字根與「尾巴」相關），受詞是 ha./ne.che.sha.Lim（H2826 cha.shal，軟弱），「疲乏」是 'a.Yef（H5889），「困倦」是 ya.Ge.a'（H3023）。
- 經文用詞：儘後邊軟弱的人

字面解析：無字面對應 → 新建（C）

| Rank | Candidate | Similarity | Rerank | Path |
|---|---|---:|---:|---|
| 1 | 古代近東社會弱勢群體 | 0.431 | 0.410 | link_folder/背景/古代近東社會弱勢群體.md |
| 2 | 申25：17-19 記念亞瑪力 | 0.409 | 0.288 | link_folder/互文/申25：17-19 記念亞瑪力.md |
| 3 | 保護弱勢 | 0.430 | 0.193 | link_folder/主題/保護弱勢.md |
| 4 | 保護弱者的律例 | 0.402 | 0.172 | link_folder/事件/保護弱者的律例.md |
| 5 | 摩西的靈命低谷與重擔求死 | 0.408 | 0.152 | link_folder/神學/摩西的靈命低谷與重擔求死.md |

rerank_margin: 0.122 (Top1 - Top2)
判定：⚠ 近鄰分類不相容（候選=原文 vs 條目=背景），若確為同實體請確認是否改用 [[古代近東社會弱勢群體]]

## 敬畏神（神學）
query:
- 待建立詞：敬畏神
- 出現位置：申命記 第25章
- 候選類型：神學
- 本章上下文：第18節「並不敬畏神」。CT：換句話說，敬畏神的人不會欺負弱小者。BH：In biblical terms, the fear of God is associated with wisdom and righteousness。

字面解析：對上既有「敬畏神」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 敬畏神 | 0.615 | link_folder/神學/敬畏神.md |
| 2 | 敬畏與可畏同一字根（ya.re） | 0.548 | link_folder/原文/敬畏與可畏同一字根（ya.re）.md |
| 3 | 箴9：10 | 0.542 | link_folder/互文/箴9：10.md |
| 4 | 敬畏耶和華的話 | 0.537 | link_folder/神學/敬畏耶和華的話.md |
| 5 | 箴16：6 | 0.528 | link_folder/互文/箴16：6.md |

判定：✅ 建議使用既有條目 [[敬畏神]]（同名／字面對應）

## 亞瑪力（人物）
query:
- 待建立詞：亞瑪力
- 出現位置：申命記 第25章
- 候選類型：人物
- 本章上下文：第19節「你要將亞瑪力的名號從天下塗抹了」。STEP：'a.ma.Lek（H6002G），「名號」是 Ze.kher（H2143）。
- 經文用詞：亞瑪力的名號

字面解析：對上既有「亞瑪力」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 亞瑪力 | 0.555 | link_folder/人物/亞瑪力.md |
| 2 | 申25：17-19 記念亞瑪力 | 0.484 | link_folder/互文/申25：17-19 記念亞瑪力.md |
| 3 | 亞瑪力人 | 0.446 | link_folder/人物/亞瑪力人.md |
| 4 | 亞甲是人名還是王朝稱號 | 0.443 | link_folder/解經爭議/亞甲是人名還是王朝稱號.md |
| 5 | 亞摩利人 | 0.407 | link_folder/人物/亞摩利人.md |

判定：✅ 建議使用既有條目 [[亞瑪力]]（同名／字面對應）

## 申25：17-19 記念亞瑪力（互文）
query:
- 待建立詞：申25：17-19 記念亞瑪力
- 出現位置：申命記 第25章
- 候選類型：互文
- 本章上下文：本段是出17 亞瑪力之役的回顧與命令，補上出17:8 沒有交代的攻擊方式。CT：神這個除滅亞瑪力人的命令，要等到希西家王年間才由西緬支派的人實現（參代上四41~43）。

字面解析：對上既有「申25：17-19 記念亞瑪力」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 申25：17-19 記念亞瑪力 | 0.758 | link_folder/互文/申25：17-19 記念亞瑪力.md |
| 2 | 亞瑪力 | 0.619 | link_folder/人物/亞瑪力.md |
| 3 | 亞瑪力人 | 0.579 | link_folder/人物/亞瑪力人.md |
| 4 | 以色列戰勝亞摩利王西宏互文（申2：24-37；3：1-7；詩135：10-12；136：17-22） | 0.573 | link_folder/互文/以色列戰勝亞摩利王西宏互文（申2：24-37；3：1-7；詩135：10-12；136：17-22）.md |
| 5 | 出埃及記17章亞瑪力攻擊以色列 | 0.569 | link_folder/互文/出埃及記17章亞瑪力攻擊以色列.md |

判定：✅ 建議使用既有條目 [[申25：17-19 記念亞瑪力]]（同名／字面對應）

## 掃羅擊殺亞甲（撒上15：8）（互文）
query:
- 待建立詞：掃羅擊殺亞甲（撒上15：8）
- 出現位置：申命記 第25章
- 候選類型：互文
- 本章上下文：CT：最後，神命令掃羅王除滅亞瑪力人（參撒上十五2~3），但他沒有徹底執行。KC：Saul is commissioned to blot out Amalek, but fails by disobedience (1Sam 15:1-3,18-19)。

字面解析：對上既有「掃羅擊殺亞甲（撒上15：8）」（exact，將歸 A/B 累積）

| Rank | Candidate | Similarity | Path |
|---|---|---:|---|
| 1 | 掃羅擊殺亞甲（撒上15：8） | 0.679 | link_folder/互文/掃羅擊殺亞甲（撒上15：8）.md |
| 2 | 申25：17-19 記念亞瑪力 | 0.533 | link_folder/互文/申25：17-19 記念亞瑪力.md |
| 3 | 亞瑪力 | 0.526 | link_folder/人物/亞瑪力.md |
| 4 | 戰勝亞瑪力人 | 0.486 | link_folder/事件/戰勝亞瑪力人.md |
| 5 | 亞瑪力人 | 0.485 | link_folder/人物/亞瑪力人.md |

判定：✅ 建議使用既有條目 [[掃羅擊殺亞甲（撒上15：8）]]（同名／字面對應）

## 候選互查（本章內部，⚠＝彼此相似 ≥ 0.8）
（無 ≥ 門檻的配對）
