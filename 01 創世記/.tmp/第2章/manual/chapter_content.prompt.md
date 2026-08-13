你是聖經研經資料整理員。唯一任務：為 創世記 第2章填寫 chapter_content payload（本章知識節點 + 本章整理）。

【經文】
1. 天地萬物都造齊了。
2. 到第七日，神造物的工已經完畢，就在第七日歇了他一切的工，安息了。
3. 神賜福給第七日，定為聖日；因為在這日，神歇了他一切創造的工，就安息了。
4. 創造天地的來歷，在耶和華神造天地的日子，乃是這樣，
5. 野地還沒有草木，田間的菜蔬還沒有長起來；因為耶和華神還沒有降雨在地上，也沒有人耕地，
6. 但有霧氣從地上騰，滋潤遍地。
7. 耶和華神用地上的塵土造人，將生氣吹在他鼻孔裡，他就成了有靈的活人，名叫亞當。
8. 耶和華神在東方的伊甸立了一個園子，把所造的人安置在那裡。
9. 耶和華神使各樣的樹從地裡長出來，可以悅人的眼目，其上的果子好作食物。園子當中又有生命樹和分別善惡的樹。
10. 有河從伊甸流出來，滋潤那園子，從那裡分為四道：
11. 第一道名叫比遜，就是環繞哈腓拉全地的。在那裡有金子，
12. 並且那地的金子是好的；在那裡又有珍珠和紅瑪瑙。
13. 第二道河名叫基訓，就是環繞古實全地的。
14. 第三道河名叫希底結，流在亞述的東邊。第四道河就是伯拉河。
15. 耶和華神將那人安置在伊甸園，使他修理，看守。
16. 耶和華神吩咐他說：園中各樣樹上的果子，你可以隨意吃，
17. 只是分別善惡樹上的果子，你不可吃，因為你吃的日子必定死！
18. 耶和華神說：那人獨居不好，我要為他造一個配偶幫助他。
19. 耶和華神用土所造成的野地各樣走獸和空中各樣飛鳥都帶到那人面前，看他叫什麼。那人怎樣叫各樣的活物，那就是他的名字。
20. 那人便給一切牲畜和空中飛鳥、野地走獸都起了名；只是那人沒有遇見配偶幫助他。
21. 耶和華神使他沉睡，他就睡了；於是取下他的一條肋骨，又把肉合起來。
22. 耶和華神就用那人身上所取的肋骨造成一個女人，領他到那人跟前。
23. 那人說：這是我骨中的骨，肉中的肉，可以稱他為女人，因為他是從男人身上取出來的。
24. 因此，人要離開父母，與妻子連合，二人成為一體。
25. 當時夫妻二人赤身露體，並不羞恥。

【本章來源 context】
## 本章 Commentary Sources

你已依 manual/sources.md 全文閱讀以下正式 commentary；本 prompt 不重複內嵌原文全文。
- 研經註解（BibleHub Study）
  path: raw_data/biblehub_study_genesis_2.txt
  URL: https://biblehub.com/study/genesis/2.htm
- 研經註解（KingComments）
  path: raw_data/kingcomments_genesis_2.txt
  URL: https://www.kingcomments.com/en/bible-studies/Gen/2
- 逐節註解（ccbiblestudy CT）
  path: raw_data/ccbiblestudy_CT_genesis_2.txt
  URL: https://www.ccbiblestudy.org/Old%20Testament/01Gen/01CT02.htm
- 拾穗（ccbiblestudy GT）
  path: raw_data/ccbiblestudy_GT_genesis_2.txt
  URL: https://www.ccbiblestudy.org/Old%20Testament/01Gen/01GT02.htm

所有 commentary 敘述仍必須忠於上述已全文閱讀來源；不得以摘要或關鍵字 grep 取代全文閱讀。


## STEP Bible task projection
- source: stepbible_genesis_2.txt
- reference: Genesis 2
- selected verses: 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25
- boundary: lexicon 是可能義域，不等於本節語境義；morphology 不自行證明神學結論。

### Occurrences
format: position | original | transliteration | exact Extended Strong | morphology code | context gloss
#### Gen 2:1
- 1 | וַ/יְכֻלּ֛וּ | va/y.khu.Lu | H3615G | Hc/VPw3mp | and/ they were completed
- 2 | הַ/שָּׁמַ֥יִם | ha./sha.Ma.yim | H8064 | HTd/Ncmpa | the/ heavens
- 3 | וְ/הָ/אָ֖רֶץ | ve./ha./'A.retz | H776G | HC/Td/Ncfsa | and/ the/ earth
- 4 | וְ/כָל\־ | ve./khol | H3605 | HC/Ncmsc | and/ all
- 5 | צְבָאָֽ/ם\׃ | tze.va.'A/m | H6635A | HNcmsc/Sp3mp | host/ their
#### Gen 2:2
- 1 | וַ/יְכַ֤ל | va/y.Khal | H3615G | Hc/Vpw3ms | and/ he completed
- 2 | אֱלֹהִים֙ | 'E.lo.Him | H430G | HNcmpa | God
- 3 | בַּ/יּ֣וֹם | ba/i.Yom | H3117G | HRd/Ncmsa | on the/ day
- 4 | הַ/שְּׁבִיעִ֔י | ha./she.vi.'I | H7637 | HTd/Aomsa | <the>/ seventh
- 5 | מְלַאכְתּ֖/וֹ | me.lakh.T/o | H4399 | HNcfsc/Sp3ms | work/ his
- 6 | אֲשֶׁ֣ר | 'a.Sher | H834A | HTr | which
- 7 | עָשָׂ֑ה | 'a.Sah | H6213A | HVqp3ms | he had done
- 8 | וַ/יִּשְׁבֹּת֙ | va/i.yish.Bot | H7673A | Hc/Vqw3ms | and/ he rested
- 9 | בַּ/יּ֣וֹם | ba/i.Yom | H3117G | HRd/Ncmsa | on the/ day
- 10 | הַ/שְּׁבִיעִ֔י | ha./she.vi.'I | H7637 | HTd/Aomsa | <the>/ seventh
- 11 | מִ/כָּל\־ | mi./kol | H3605 | HR/Ncmsc | from/ all
- 12 | מְלַאכְתּ֖/וֹ | me.lakh.T/o | H4399 | HNcfsc/Sp3ms | work/ his
- 13 | אֲשֶׁ֥ר | 'a.Sher | H834A | HTr | which
- 14 | עָשָֽׂה\׃ | 'a.Sah | H6213A | HVqp3ms | he had done
#### Gen 2:3
- 1 | וַ/יְבָ֤רֶךְ | va/y.Va.rekh | H1288 | Hc/Vpw3ms | and/ he blessed
- 2 | אֱלֹהִים֙ | 'E.lo.Him | H430G | HNcmpa | God
- 3 | אֶת\־ | 'et- | H853 | HTo | <obj.>
- 4 | י֣וֹם | Yom | H3117G | HNcmsc | [the] day
- 5 | הַ/שְּׁבִיעִ֔י | ha./she.vi.'I | H7637 | HTd/Aomsa | <the>/ seventh
- 6 | וַ/יְקַדֵּ֖שׁ | va/y.ka.Desh | H6942G | Hc/Vpw3ms | and/ he set apart as holy
- 7 | אֹת֑/וֹ | 'o.T/o | H853 | HTo/Sp3ms | <obj.>/ it
- 8 | כִּ֣י | ki | H3588A | HTc | for
- 9 | ב֤/וֹ | v/o | H9003 | HRd/Sp3ms | on <the>/ it
- 10 | שָׁבַת֙ | sha.Vat | H7673A | HVqp3ms | he rested
- 11 | מִ/כָּל\־ | mi./kol | H3605 | HR/Ncmsc | from/ all
- 12 | מְלַאכְתּ֔/וֹ | me.lakh.T/o | H4399 | HNcfsc/Sp3ms | work/ his
- 13 | אֲשֶׁר\־ | 'a.Sher- | H834A | HTr | which
- 14 | בָּרָ֥א | ba.Ra' | H1254A | HVqp3ms | he had created
- 15 | אֱלֹהִ֖ים | 'E.lo.Him | H430G | HNcmpa | God
- 16 | לַ/עֲשֽׂוֹת\׃\ \פ | la./'a.Sot | H6213A | HR/Vqcc | to/ make
#### Gen 2:4
- 1 | אֵ֣לֶּה | 'E.leh | H428 | HTm | these
- 2 | תוֹלְד֧וֹת | tol.Dot | H8435 | HNcfpc | [are] [the] accounts of
- 3 | הַ/שָּׁמַ֛יִם | ha./sha.Ma.yim | H8064 | HTd/Ncmpa | the/ heavens
- 4 | וְ/הָ/אָ֖רֶץ | ve./ha./'A.retz | H776G | HC/Td/Ncfsa | and/ the/ earth
- 5 | בְּ/הִבָּֽרְאָ֑/ם | be./hi.ba.re.'A/m | H1254A | HR/VNcc/Sp3mp | when/ were created/ they
- 6 | בְּ/י֗וֹם | be./Yom | H3117G | HR/Ncmsc | on/ [the] day
- 7 | עֲשׂ֛וֹת | a.Sot | H6213H | HVqcc | made
- 8 | יְהוָ֥ה | Yah.weh | H3068G | HNpt | Yahweh
- 9 | אֱלֹהִ֖ים | 'E.lo.Him | H430G | HNcmpa | God
- 10 | אֶ֥רֶץ | 'E.retz | H776G | HNcfsa | earth
- 11 | וְ/שָׁמָֽיִם\׃ | ve./sha.Ma.yim | H8064 | HC/Ncmpa | and/ heaven
#### Gen 2:5
- 1 | וְ/כֹ֣ל\׀ | ve./Khol | H3605 | HC/Ncmsc | and/ any
- 2 | שִׂ֣יחַ | Si.ach | H7880 | HNcmsc | <the> shrub of
- 3 | הַ/שָּׂדֶ֗ה | ha./sa.Deh | H7704G | HTd/Ncmsa | the/ field
- 4 | טֶ֚רֶם | Te.rem | H2962 | HAcbsa | not yet
- 5 | יִֽהְיֶ֣ה | yih.Yeh | H1961 | HVqi3ms | <it> was
- 6 | בָ/אָ֔רֶץ | va./'A.retz | H776G | HRd/Ncfsa | on the/ earth
- 7 | וְ/כָל\־ | ve./khol | H3605 | HC/Ncmsc | and/ any
- 8 | עֵ֥שֶׂב | 'E.sev | H6212 | HNcmsc | <the> vegetation of
- 9 | הַ/שָּׂדֶ֖ה | ha./sa.Deh | H7704G | HTd/Ncmsa | the/ field
- 10 | טֶ֣רֶם | Te.rem | H2962 | HAcbsa | not yet
- 11 | יִצְמָ֑ח | yitz.Mach | H6779 | HVqi3ms | <it> was sprouting
- 12 | כִּי֩ | ki | H3588A | HTc | for
- 13 | לֹ֨א | lo' | H3808 | HTn | not
- 14 | הִמְטִ֜יר | him.Tir | H4305 | HVhp3ms | he had caused rain
- 15 | יְהוָ֤ה | Yah.weh | H3068G | HNpt | Yahweh
- 16 | אֱלֹהִים֙ | 'E.lo.Him | H430G | HNcmpa | God
- 17 | עַל\־ | 'al- | H5921A | HR | on
- 18 | הָ/אָ֔רֶץ | ha./'A.retz | H776G | HTd/Ncfsa | the/ earth
- 19 | וְ/אָדָ֣ם | ve./'a.Dam | H120G | HC/Ncmsa | and/ [was] a human
- 20 | אַ֔יִן | 'A.yin | H369 | HNcmsa | there not
- 21 | לַֽ/עֲבֹ֖ד | la./'a.Vod | H5647I | HR/Vqcc | to/ till
- 22 | אֶת\־ | 'et- | H853 | HTo | <obj.>
- 23 | הָֽ/אֲדָמָֽה\׃ | Ha./'a.da.Mah | H127G | HTd/Ncfsa | the/ ground
#### Gen 2:6
- 1 | וְ/אֵ֖ד | ve./'Ed | H108 | HC/Ncmsa | and/ water
- 2 | יַֽעֲלֶ֣ה | ya.'a.Leh | H5927G | HVqi3ms | <it> came up
- 3 | מִן\־ | min- | H4480A | HR | from
- 4 | הָ/אָ֑רֶץ | ha./'A.retz | H776G | HTd/Ncfsa | the/ earth
- 5 | וְ/הִשְׁקָ֖ה | ve./hish.Kah | H8248G | Hc/Vhq3ms | and/ it watered
- 6 | אֶֽת\־ | 'et- | H853 | HTo | <obj.>
- 7 | כָּל\־ | kol- | H3605 | HNcmsc | all
- 8 | פְּנֵֽי\־ | pe.nei- | H6440J | HNcmpc | [the] surface of
- 9 | הָֽ/אֲדָמָֽה\׃ | Ha./'a.da.Mah | H127G | HTd/Ncfsa | the/ ground
#### Gen 2:7
- 1 | וַ/יִּיצֶר֩ | va/i.yi.Tzer | H3335G | Hc/Vqw3ms | and/ he formed
- 2 | יְהוָ֨ה | Yah.weh | H3068G | HNpt | Yahweh
- 3 | אֱלֹהִ֜ים | 'E.lo.Him | H430G | HNcmpa | God
- 4 | אֶת\־ | 'et- | H853 | HTo | <obj.>
- 5 | הָֽ/אָדָ֗ם | ha./'a.Dam | H120H | HTd/Ncmsa | the/ man
- 6 | עָפָר֙ | 'a.Far | H6083 | HNcmsa | dust
- 7 | מִן\־ | min- | H4480A | HR | from
- 8 | הָ֣/אֲדָמָ֔ה | ha./'a.da.Mah | H127G | HTd/Ncfsa | the/ ground
- 9 | וַ/יִּפַּ֥ח | va/i.yi.Pach | H5301 | Hc/Vqw3ms | and/ he blew
- 10 | בְּ/אַפָּ֖י/ו | be./'a.Pa/v | H639H | HR/Ncmdc/Sp3ms | in/ nostrils/ his
- 11 | נִשְׁמַ֣ת | nish.Mat | H5397 | HNcfsc | [the] breath of
- 12 | חַיִּ֑ים | chai.Yim | H2416E | HNcmpa | life
- 13 | וַֽ/יְהִ֥י | va/y.Hi | H1961 | Hc/Vqw3ms | and/ he became
- 14 | הָֽ/אָדָ֖ם | ha./'a.Dam | H120H | HTd/Ncmsa | the/ man
- 15 | לְ/נֶ֥פֶשׁ | le./Ne.fesh | H5315K | HR/Ncfsa | <into>/ a creature
- 16 | חַיָּֽה\׃ | chai.Yah | H2416A | HAafsa | living
#### Gen 2:8
- 1 | וַ/יִּטַּ֞ע | va/i.yi.Ta' | H5193 | Hc/Vqw3ms | and/ he planted
- 2 | יְהוָ֧ה | Yah.weh | H3068G | HNpt | Yahweh
- 3 | אֱלֹהִ֛ים | 'E.lo.Him | H430G | HNcmpa | God
- 4 | גַּן\־ | gan- | H1588M | HNcbsa | a garden
- 5 | בְ/עֵ֖דֶן | be./'E.den | H5731B | HR/Npl | in/ Eden
- 6 | מִ/קֶּ֑דֶם | mi./Ke.dem | H6924G | HR/Ncmsa | from/ [the] east
- 7 | וַ/יָּ֣שֶׂם | va/i.Ya.sem | H7760H | Hc/Vqw3ms | and/ he put
- 8 | שָׁ֔ם | Sham | H8033G | HD | there
- 9 | אֶת\־ | 'et- | H853 | HTo | <obj.>
- 10 | הָֽ/אָדָ֖ם | ha./'a.Dam | H120H | HTd/Ncmsa | the/ man
- 11 | אֲשֶׁ֥ר | 'a.Sher | H834A | HTr | whom
- 12 | יָצָֽר\׃ | ya.Tzar | H3335G | HVqp3ms | he had formed
#### Gen 2:9
- 1 | וַ/יַּצְמַ֞ח | va/i.yatz.Mach | H6779 | Hc/Vhw3ms | and/ he made sprout
- 2 | יְהוָ֤ה | Yah.weh | H3068G | HNpt | Yahweh
- 3 | אֱלֹהִים֙ | 'E.lo.Him | H430G | HNcmpa | God
- 4 | מִן\־ | min- | H4480A | HR | from
- 5 | הָ֣/אֲדָמָ֔ה | ha./'a.da.Mah | H127G | HTd/Ncfsa | the/ ground
- 6 | כָּל\־ | kol- | H3605 | HNcmsc | every
- 7 | עֵ֛ץ | 'etz | H6086H | HNcmsa | tree
- 8 | נֶחְמָ֥ד | nech.Mad | H2530A | HVNrmsa | desirable
- 9 | לְ/מַרְאֶ֖ה | le./mar.'Eh | H4758 | HR/Ncmsa | to/ appearance
- 10 | וְ/ט֣וֹב | ve./Tov | H2896A | HC/Aamsa | and/ good
- 11 | לְ/מַאֲכָ֑ל | le./ma.'a.Khal | H3978 | HR/Ncmsa | for/ food
- 12 | וְ/עֵ֤ץ | ve./'Etz | H6086H | HC/Ncmsc | and/ [the] tree of
- 13 | הַֽ/חַיִּים֙ | ha./chai.Yim | H2416E | HTd/Ncmpa | <the>/ life
- 14 | בְּ/ת֣וֹךְ | be./Tokh | H8432 | HR/Ncmsc | [was] in/ [the] middle of
- 15 | הַ/גָּ֔ן | ha./Gan | H1588M | HTd/Ncbsa | the/ garden
- 16 | וְ/עֵ֕ץ | ve./'Etz | H6086H | HC/Ncmsc | and/ [the] tree of
- 17 | הַ/דַּ֖עַת | ha./Da.'at | H1847 | HTd/Ncfsc | the/ knowledge
- 18 | ט֥וֹב | Tov | H2896B | HAamsa | good
- 19 | וָ/רָֽע\׃ | va./Ra' | H7451B | HC/Aamsa | and/ evil
#### Gen 2:10
- 1 | וְ/נָהָר֙ | ve./na.Har | H5104H | HC/Ncmsa | and/ a river
- 2 | יֹצֵ֣א | yo.Tze' | H3318L | HVqrmsa | [was] going out
- 3 | מֵ/עֵ֔דֶן | me./'E.den | H5731B | HR/Npl | from/ Eden
- 4 | לְ/הַשְׁק֖וֹת | le./hash.Kot | H8248G | HR/Vhcc | to/ water
- 5 | אֶת\־ | 'et- | H853 | HTo | <obj.>
- 6 | הַ/גָּ֑ן | ha./Gan | H1588M | HTd/Ncbsa | the/ garden
- 7 | וּ/מִ/שָּׁם֙ | u./mi./Sham | H8033G | HC/R/D | and/ from/ there
- 8 | יִפָּרֵ֔ד | yi.pa.Red | H6504 | HVNi3ms | <it> divided
- 9 | וְ/הָיָ֖ה | ve./ha.Yah | H1961 | Hc/Vqq3ms | and/ it became
- 10 | לְ/אַרְבָּעָ֥ה | le./'ar.ba.'Ah | H702 | HR/Acbsa | <into>/ four
- 11 | רָאשִֽׁים\׃ | ra.Shim | H7218J | HNcmpa | heads
#### Gen 2:11
- 1 | שֵׁ֥ם | shem | H8034 | HNcmsc | [the] name of
- 2 | הָֽ/אֶחָ֖ד | ha./'e.Chad | H259 | HTd/Acfsa | the/ one
- 3 | פִּישׁ֑וֹן | pi.Shon | H6376 | HNpl | [is] Pishon
- 4 | ה֣וּא | hu' | H1931 | HPp3ms | it
- 5 | הַ/סֹּבֵ֗ב | ha./so.Vev | H5437G | HTd/Vqrmsa | [is] the/ [one which] goes around
- 6 | אֵ֚ת | 'et | H853 | HTo | <obj.>
- 7 | כָּל\־ | kol- | H3605 | HNcmsc | all
- 8 | אֶ֣רֶץ | 'E.retz | H776G | HNcfsc | [the] land of
- 9 | הַֽ/חֲוִילָ֔ה | ha./cha.vi.Lah | H2341G | HTd/Npl | <the>/ Havilah
- 10 | אֲשֶׁר\־ | 'a.Sher- | H834A | HTr | where
- 11 | שָׁ֖ם | sham | H8033G | HD | [is] there
- 12 | הַ/זָּהָֽב\׃ | ha./za.Hav | H2091 | HTd/Ncmsa | <the>/ gold
#### Gen 2:12
- 1 | וּֽ/זֲהַ֛ב | u./za.Hav | H2091 | HC/Ncmsc | and/ [the] gold of
- 2 | הָ/אָ֥רֶץ | ha./'A.retz | H776G | HTd/Ncfsa | the/ land
- 3 | הַ/הִ֖וא | ha./Hiv' | H1931 | HTd/Pp3fs | <the>/ that
- 4 | ט֑וֹב | Tov | H2896A | HAamsa | [is] good
- 5 | שָׁ֥ם | sham | H8033G | HD | [are] there
- 6 | הַ/בְּדֹ֖לַח | ha./be.Do.lach | H916 | HTd/Ncmsa | <the>/ bdellium
- 7 | וְ/אֶ֥בֶן | ve./'E.ven | H68G | HC/Ncfsc | and/ [the] stone of
- 8 | הַ/שֹּֽׁהַם\׃ | ha./Sho.ham | H7718 | HTd/Ncmsa | <the>/ onyx
#### Gen 2:13
- 1 | וְ/שֵֽׁם\־ | ve./shem- | H8034 | HC/Ncmsc | and/ [the] name of
- 2 | הַ/נָּהָ֥ר | ha./na.Har | H5104H | HTd/Ncmsa | the/ river
- 3 | הַ/שֵּׁנִ֖י | ha./she.Ni | H8145 | HTd/Aomsa | <the>/ second
- 4 | גִּיח֑וֹן | gi.Chon | H1521 | HNpl | [is] Gihon
- 5 | ה֣וּא | hu' | H1931 | HPp3ms | it
- 6 | הַ/סּוֹבֵ֔ב | ha./so.Vev | H5437G | HTd/Vqrmsa | [is] the/ [one which] goes around
- 7 | אֵ֖ת | 'et | H853 | HTo | <obj.>
- 8 | כָּל\־ | kol- | H3605 | HNcmsc | all
- 9 | אֶ֥רֶץ | 'E.retz | H776G | HNcfsc | [the] land of
- 10 | כּֽוּשׁ\׃ | Kush | H3568A | HNpl | Cush
#### Gen 2:14
- 1 | וְ/שֵׁ֨ם | ve./Shem | H8034 | HC/Ncmsc | and/ [the] name of
- 2 | הַ/נָּהָ֤ר | ha./na.Har | H5104H | HTd/Ncmsa | the/ river
- 3 | הַ/שְּׁלִישִׁי֙ | ha./she.li.Shi | H7992 | HTd/Aomsa | <the>/ third
- 4 | חִדֶּ֔קֶל | chi.De.kel | H2313 | HNpl | [is] Tigris
- 5 | ה֥וּא | hu' | H1931 | HPp3ms | it
- 6 | הַֽ/הֹלֵ֖ךְ | ha./ho.Lekh | H1980I | HTd/Vqrmsa | [is] the/ [one which] goes
- 7 | קִדְמַ֣ת | kid.Mat | H6926 | HNcfsc | [the] east of
- 8 | אַשּׁ֑וּר | 'a.Shur | H804G | HNpl | Assyria
- 9 | וְ/הַ/נָּהָ֥ר | ve./ha./na.Har | H5104H | HC/Td/Ncmsa | and/ the/ river
- 10 | הָֽ/רְבִיעִ֖י | ha./re.vi.'I | H7243 | HTd/Aomsa | <the>/ fourth
- 11 | ה֥וּא | hu' | H1931 | HPp3ms | it
- 12 | פְרָֽת\׃ | fe.Rat | H6578 | HNpl | [is the] Euphrates
#### Gen 2:15
- 1 | וַ/יִּקַּ֛ח | va/i.yi.Kach | H3947G | Hc/Vqw3ms | and/ he took
- 2 | יְהוָ֥ה | Yah.weh | H3068G | HNpt | Yahweh
- 3 | אֱלֹהִ֖ים | 'E.lo.Him | H430G | HNcmpa | God
- 4 | אֶת\־ | 'et- | H853 | HTo | <obj.>
- 5 | הָֽ/אָדָ֑ם | ha./'a.Dam | H120H | HTd/Ncmsa | the/ man
- 6 | וַ/יַּנִּחֵ֣/הוּ | va/i.ya.ni.Che./hu | H5117 | Hc/Vhw3ms/Sp3ms | and/ he put/ him
- 7 | בְ/גַן\־ | ve./gan- | H1588M | HR/Ncbsc | in/ [the] garden of
- 8 | עֵ֔דֶן | 'E.den | H5731B | HNpl | Eden
- 9 | לְ/עָבְדָ֖/הּ | le./'a.ve.Da/h | H5647I | HR/Vqcc/Sp3fs | to/ till/ it
- 10 | וּ/לְ/שָׁמְרָֽ/הּ\׃ | u./le./sha.me.Ra/h | H8104H | HC/R/Vqcc/Sp3fs | and/ to/ keep/ it
#### Gen 2:16
- 1 | וַ/יְצַו֙ | va/y.Tzav | H6680 | Hc/Vpw3ms | and/ he commanded
- 2 | יְהוָ֣ה | Yah.weh | H3068G | HNpt | Yahweh
- 3 | אֱלֹהִ֔ים | 'E.lo.Him | H430G | HNcmpa | God
- 4 | עַל\־ | 'al- | H5921A | HR | to
- 5 | הָֽ/אָדָ֖ם | ha./'a.Dam | H120H | HTd/Ncmsa | the/ man
- 6 | לֵ/אמֹ֑ר | le./Mor | H559 | HR/Vqcc | <to>/ saying
- 7 | מִ/כֹּ֥ל | mi./Kol | H3605 | HR/Ncmsc | from/ any
- 8 | עֵֽץ\־ | 'etz- | H6086H | HNcmsc | <the> tree of
- 9 | הַ/גָּ֖ן | ha./Gan | H1588M | HTd/Ncbsa | the/ garden
- 10 | אָכֹ֥ל | 'a.Khol | H398 | HVqaa | certainly <to eat>
- 11 | תֹּאכֵֽל\׃ | to.Khel | H398 | HVqi2ms | you will eat
#### Gen 2:17
- 1 | וּ/מֵ/עֵ֗ץ | u./me./'Etz | H6086H | HC/R/Ncmsc | and/ from/ [the] tree of
- 2 | הַ/דַּ֙עַת֙ | ha./Da.'at | H1847 | HTd/Ncfsc | the/ knowledge
- 3 | ט֣וֹב | Tov | H2896B | HAamsa | good
- 4 | וָ/רָ֔ע | va./Ra' | H7451B | HC/Aamsa | and/ evil
- 5 | לֹ֥א | lo' | H3808 | HTn | not
- 6 | תֹאכַ֖ל | to.Khal | H398 | HVqi2ms | you must eat
- 7 | מִמֶּ֑/נּוּ | mi.Me./nu | H4480A | HRd/Sp3ms | from/ it
- 8 | כִּ֗י | Ki | H3588A | HTc | for
- 9 | בְּ/י֛וֹם | be./Yom | H3117G | HR/Ncmsc | on/ [the] day
- 10 | אֲכָלְ/ךָ֥ | 'a.khal./Kha | H398 | HVqcc/Sp2ms | eating/ you
- 11 | מִמֶּ֖/נּוּ | mi.Me./nu | H4480A | HRd/Sp3ms | from/ it
- 12 | מ֥וֹת | Mot | H4191 | HVqaa | certainly <to die>
- 13 | תָּמֽוּת\׃ | ta.Mut | H4191 | HVqi2ms | you will die
#### Gen 2:18
- 1 | וַ/יֹּ֙אמֶר֙ | va/i.Yo.mer | H559 | Hc/Vqw3ms | and/ he said
- 2 | יְהוָ֣ה | Yah.weh | H3068G | HNpt | Yahweh
- 3 | אֱלֹהִ֔ים | 'E.lo.Him | H430G | HNcmpa | God
- 4 | לֹא\־ | lo'- | H3808 | HTn | not
- 5 | ט֛וֹב | Tov | H2896A | HAamsa | [is] good
- 6 | הֱי֥וֹת | he.Yot | H1961 | HVqcc | to be
- 7 | הָֽ/אָדָ֖ם | ha./'a.Dam | H120H | HTd/Ncmsa | the/ man
- 8 | לְ/בַדּ֑/וֹ | le./va.D/o | H905H | HR/Ncmsc/Sp3ms | to/ only/ him
- 9 | אֶֽעֱשֶׂהּ\־ | 'e.'e.seh- | H6213H | HVqi1cs | I will make
- 10 | לּ֥/וֹ | l/o | H9005 | HRd/Sp3ms | for <the>/ him
- 11 | עֵ֖זֶר | 'E.zer | H5828 | HNcmsa | a helper
- 12 | כְּ/נֶגְדּֽ/וֹ\׃ | ke./neg.D/o | H5048 | HR/Acmsc/Sp3ms | like/ before/ him
#### Gen 2:19
- 1 | וַ/יִּצֶר֩ | va/i.yi.Tzer | H3335G | Hc/Vqw3ms | and/ he formed
- 2 | יְהוָ֨ה | Yah.weh | H3068G | HNpt | Yahweh
- 3 | אֱלֹהִ֜ים | 'E.lo.Him | H430G | HNcmpa | God
- 4 | מִן\־ | min- | H4480A | HR | from
- 5 | הָֽ/אֲדָמָ֗ה | ha./'a.da.Mah | H127G | HTd/Ncfsa | the/ ground
- 6 | כָּל\־ | kol- | H3605 | HNcmsc | every
- 7 | חַיַּ֤ת | chai.Yat | H2416C | HNcfsc | <the> animal of
- 8 | הַ/שָּׂדֶה֙ | ha./sa.Deh | H7704G | HTd/Ncmsa | the/ field
- 9 | וְ/אֵת֙ | ve./'Et | H853 | HC/To | and/ <obj.>
- 10 | כָּל\־ | kol- | H3605 | HNcmsc | every
- 11 | ע֣וֹף | of | H5775 | HNcmsc | <the> bird of
- 12 | הַ/שָּׁמַ֔יִם | ha./sha.Ma.yim | H8064 | HTd/Ncmpa | the/ heavens
- 13 | וַ/יָּבֵא֙ | va/i.ya.Ve' | H935P | Hc/Vhw3ms | and/ he brought [them]
- 14 | אֶל\־ | 'El- | H413 | HR | to
- 15 | הָ֣/אָדָ֔ם | ha./'a.Dam | H120H | HTd/Ncmsa | the/ man
- 16 | לִ/רְא֖וֹת | li/r.'ot | H7200G | HR/Vqcc | to/ see
- 17 | מַה\־ | mah- | H4100 | HPi | what?
- 18 | יִּקְרָא\־ | yik.ra'- | H7121H | HVqi3ms | will he call
- 19 | ל֑/וֹ | l/o | H9005 | HRd/Sp3ms | to <the>/ it
- 20 | וְ/כֹל֩ | ve./Khol | H3605 | HC/Ncmsa | and/ all
- 21 | אֲשֶׁ֨ר | 'a.Sher | H834A | HTr | that
- 22 | יִקְרָא\־ | yik.ra'- | H7121H | HVqi3ms | he called
- 23 | ל֧/וֹ | l/o | H9005 | HRd/Sp3ms | to <the>/ it
- 24 | הָֽ/אָדָ֛ם | ha./'a.Dam | H120H | HTd/Ncmsa | the/ man
- 25 | נֶ֥פֶשׁ | Ne.fesh | H5315K | HNcfsa | a creature
- 26 | חַיָּ֖ה | chai.Yah | H2416A | HAafsa | living
- 27 | ה֥וּא | hu' | H1931 | HPp3ms | it
- 28 | שְׁמֽ/וֹ\׃ | she.M/o | H8034 | HNcmsc/Sp3ms | [was] name/ its
#### Gen 2:20
- 1 | וַ/יִּקְרָ֨א | va/i.yik.Ra' | H7121H | Hc/Vqw3ms | and/ he called
- 2 | הָֽ/אָדָ֜ם | ha./'a.Dam | H120H | HTd/Ncmsa | the/ man
- 3 | שֵׁמ֗וֹת | she.Mot | H8034 | HNcfpa | names
- 4 | לְ/כָל\־ | le./khol | H3605 | HR/Ncmsc | to/ all
- 5 | הַ/בְּהֵמָה֙ | ha./be.he.Mah | H929 | HTd/Ncfsa | the/ livestock
- 6 | וּ/לְ/ע֣וֹף | u./le./'of | H5775 | HC/R/Ncmsc | and/ to/ [the] bird[s] of
- 7 | הַ/שָּׁמַ֔יִם | ha./sha.Ma.yim | H8064 | HTd/Ncmpa | the/ heavens
- 8 | וּ/לְ/כֹ֖ל | u./le./Khol | H3605 | HC/R/Ncmsc | and/ to/ every
- 9 | חַיַּ֣ת | chai.Yat | H2416C | HNcfsc | <the> animal of
- 10 | הַ/שָּׂדֶ֑ה | ha./sa.Deh | H7704G | HTd/Ncmsa | the/ field
- 11 | וּ/לְ/אָדָ֕ם | u./le./'a.Dam | H121G | HC/R/Npm | and/ for/ Adam
- 12 | לֹֽא\־ | lo'- | H3808 | HTn | not
- 13 | מָצָ֥א | ma.Tza' | H4672 | HVqp3ms | he found
- 14 | עֵ֖זֶר | 'E.zer | H5828 | HNcmsa | a helper
- 15 | כְּ/נֶגְדּֽ/וֹ\׃ | ke./neg.D/o | H5048 | HR/Acmsc/Sp3ms | like/ before/ him
#### Gen 2:21
- 1 | וַ/יַּפֵּל֩ | va/i.ya.Pel | H5307G | Hc/Vhw3ms | and/ he made fall
- 2 | יְהוָ֨ה | Yah.weh | H3068G | HNpt | Yahweh
- 3 | אֱלֹהִ֧ים\׀ | 'E.lo.Him | H430G | HNcmpa | God
- 4 | תַּרְדֵּמָ֛ה | tar.de.Mah | H8639 | HNcfsa | a deep sleep
- 5 | עַל\־ | 'al- | H5921A | HR | on
- 6 | הָ/אָדָ֖ם | ha./'a.Dam | H120H | HTd/Ncmsa | the/ man
- 7 | וַ/יִּישָׁ֑ן | va/i.yi.Shan | H3462 | Hc/Vqw3ms | and/ he fell asleep
- 8 | וַ/יִּקַּ֗ח | va/i.yi.Kach | H3947G | Hc/Vqw3ms | and/ he took
- 9 | אַחַת֙ | 'a.Chat | H259 | HAcfsa | one
- 10 | מִ/צַּלְעֹתָ֔י/ו | mi./tzal.'o.Ta/v | H6763 | HR/Ncfpc/Sp3ms | of/ ribs/ his
- 11 | וַ/יִּסְגֹּ֥ר | va/i.yis.Gor | H5462 | Hc/Vqw3ms | and/ he closed up
- 12 | בָּשָׂ֖ר | ba.Sar | H1320 | HNcmsa | flesh
- 13 | תַּחְתֶּֽ/נָּה\׃ | tach.Te./nah | H8478H | HNcmsc/Sp3fs | in place of/ it
#### Gen 2:22
- 1 | וַ/יִּבֶן֩ | va/i.yi.Ven | H1129 | Hc/Vqw3ms | and/ he built
- 2 | יְהוָ֨ה | Yah.weh | H3068G | HNpt | Yahweh
- 3 | אֱלֹהִ֧ים\׀ | 'E.lo.Him | H430G | HNcmpa | God
- 4 | אֶֽת\־ | 'et- | H853 | HTo | <obj.>
- 5 | הַ/צֵּלָ֛ע | ha./tze.La' | H6763 | HTd/Ncfsa | the/ rib
- 6 | אֲשֶׁר\־ | 'a.Sher- | H834A | HTr | which
- 7 | לָקַ֥ח | la.Kach | H3947G | HVqp3ms | he had taken
- 8 | מִן\־ | min- | H4480A | HR | from
- 9 | הָֽ/אָדָ֖ם | ha./'a.Dam | H120H | HTd/Ncmsa | the/ man
- 10 | לְ/אִשָּׁ֑ה | le./'i.Shah | H802G | HR/Ncfsa | into/ a woman
- 11 | וַ/יְבִאֶ֖/הָ | va/y.vi.'E./ha | H935P | Hc/Vhw3ms/Sp3fs | and/ he brought/ her
- 12 | אֶל\־ | 'el- | H413 | HR | to
- 13 | הָֽ/אָדָֽם\׃ | Ha./'a.Dam | H120H | HTd/Ncmsa | the/ man
#### Gen 2:23
- 1 | וַ/יֹּאמֶר֮ | va/i.yo.Mer | H559 | Hc/Vqw3ms | and/ he said
- 2 | הָֽ/אָדָם֒ | ha./'a.Dam | H120H | HTd/Ncmsa | the/ man
- 3 | זֹ֣את | zot | H2063 | HTm | this [one]
- 4 | הַ/פַּ֗עַם | ha./Pa.'am | H6471 | HTd/Ncfsa | this/ time
- 5 | עֶ֚צֶם | 'E.tzem | H6106G | HNcfsa | [is] bone
- 6 | מֵֽ/עֲצָמַ֔/י | me./'a.tza.Ma/i | H6106G | HR/Ncmpc/Sp1bs | from/ bones/ my
- 7 | וּ/בָשָׂ֖ר | u./va.Sar | H1320 | HC/Ncmsa | and/ flesh
- 8 | מִ/בְּשָׂרִ֑/י | mi./be.sa.R/i | H1320 | HR/Ncmsc/Sp1bs | from/ flesh/ my
- 9 | לְ/זֹאת֙ | le./zoT | H2063 | HR/Tm | to/ this [one]
- 10 | יִקָּרֵ֣א | yi.ka.Re' | H7121H | HVNi3ms | <it> will be called
- 11 | אִשָּׁ֔ה | 'i.Shah | H802G | HNcfsa | woman
- 12 | כִּ֥י | ki | H3588A | HTc | for
- 13 | מֵ/אִ֖ישׁ | me./'Ish | H376G | HR/Ncmsa | from/ a man
- 14 | לֻֽקֳחָה\־ | lu.ko.chah- | H3947G | HVPp3fs | she was taken
- 15 | זֹּֽאת\׃ | Zot | H2063 | HTm | this [one]
#### Gen 2:24
- 1 | עַל\־ | 'al- | H5921A | HR | there-
- 2 | כֵּן֙ | ken | H3651C | HD | -fore
- 3 | יַֽעֲזָב\־ | ya.'a.zov- | H5800A | HVqi3ms | he leaves
- 4 | אִ֔ישׁ | 'Ish | H376G | HNcmsa | a man
- 5 | אֶת\־ | 'et- | H853 | HTo | <obj.>
- 6 | אָבִ֖י/ו | 'a.Vi/v | H1G | HNcmsc/Sp3ms | father/ his
- 7 | וְ/אֶת\־ | ve./'Et | H853 | HC/To | and/ <obj.>
- 8 | אִמּ֑/וֹ | 'i.M/o | H517 | HNcfsc/Sp3ms | mother/ his
- 9 | וְ/דָבַ֣ק | ve./da.Vak | H1692 | Hc/Vqq3ms | and/ he cleaves
- 10 | בְּ/אִשְׁתּ֔/וֹ | be./'ish.T/o | H802H | HR/Ncfsc/Sp3ms | to/ wife/ his
- 11 | וְ/הָי֖וּ | ve./ha.Yu | H1961 | Hc/Vqq3cp | and/ they become
- 12 | לְ/בָשָׂ֥ר | le./va.Sar | H1320 | HR/Ncmsa | <into>/ flesh
- 13 | אֶחָֽד\׃ | 'e.Chad | H259 | HAcfsa | one
#### Gen 2:25
- 1 | וַ/יִּֽהְי֤וּ | va/i.yih.Yu | H1961 | Hc/Vqw3mp | and/ they were
- 2 | שְׁנֵי/הֶם֙ | she.nei./Hem | H8147 | HAcbdc/Sp3mp | both of/ them
- 3 | עֲרוּמִּ֔ים | 'a.ru.Mim | H6174 | HAampa | naked
- 4 | הָֽ/אָדָ֖ם | ha./'a.Dam | H120H | HTd/Ncmsa | the/ man
- 5 | וְ/אִשְׁתּ֑/וֹ | ve./'ish.T/o | H802H | HC/Ncfsc/Sp3ms | and/ wife/ his
- 6 | וְ/לֹ֖א | ve./Lo' | H3808 | HC/Tn | and/ not
- 7 | יִתְבֹּשָֽׁשׁוּ\׃ | yit.bo.Sha.shu | H954 | HVti3mp | they were ashamed

### Lexicon（依 exact Extended Strong 去重）
- H3615G | כָּלָה (ka.lah): to end: finish
- H8064 | שָׁמַיִם (sha.ma.yim): heaven
- H776G | אֶ֫רֶץ (e.rets): land: country/planet
- H3605 | כֹּל (kol): all
- H6635A | צָבָא (tsa.va): army
- H430G | אֱלֹהִים (e.lo.him): God
- H3117G | יוֹם (yom): day
- H7637 | שְׁבִיעִי (she.vi.i): seventh
- H4399 | מְלָאכָה (me.la.khah): work
- H834A | אֲשֶׁר (a.sher): which
- H6213A | עָשָׂה (a.sah): to make: do
- H7673A | שָׁבַת (sha.vat): to cease
- H1288 | בָּרַךְ (ba.rakh): to bless
- H853 | אֵת (et): [Obj.]
- H6942G | קָדַשׁ (qa.dash): to consecrate: consecate
- H3588A | כִּי (ki): for
- H9003 | /ב (b): in/on/with
- H1254A | בָּרָא (ba.ra): to create
- H428 | אֵ֫לֶּה (el.leh): these
- H8435 | תּוֹלֵדוֹת (to.le.dah): generation
- H6213H | עָשָׂה (a.sah): to make
- H3068G | יְהֹוָה (ye.ho.vah): LORD
- H7880 | שִׂיחַ (si.ach): bush
- H7704G | שָׂדֶה (sa.deh): land: country
- H2962 | טֶ֫רֶם (te.rem): before
- H1961 | הָיָה (ha.yah): to be
- H6212 | עֵ֫שֶׂב (e.sev): vegetation
- H6779 | צָמַח (tsa.mach): to spring
- H3808 | לֹא (lo): not
- H4305 | מָטַר (ma.tar): to rain
- H5921A | עַל (al): upon
- H120G | אָדָם (a.dam): man
- H369 | אַ֫יִן (a.yin): nothing
- H5647I | עָבַד (a.vad): to serve: labour
- H127G | אֲדָמָה (a.da.mah): land: soil
- H108 | אֵד (ed): mist
- H5927G | עָלָה (a.lah): to ascend: rise
- H4480A | from
- H8248G | שָׁקָה (sha.qah): to water: watering
- H6440J | פָּנֶה (pa.neh): face: surface
- H3335G | יָצַר (ya.tsar): to form: formed
- H120H | אָדָם (a.dam): the man (Adam)
- H6083 | עָפָר (a.phar): dust
- H5301 | נָפַח (na.phach): to breathe
- H639H | אַף (aph): face: nose
- H5397 | נְשָׁמָה (ne.sha.mah): breath
- H2416E | חַיִּים (chay.yim): life
- H5315K | נֶ֫פֶשׁ (ne.phesh): soul: animal
- H2416A | חַי (chay): alive
- H5193 | נָטַע (na.ta): to plant
- H1588M | גַּן (gan): garden
- H5731B | עֵ֫דֶן (e.den): Eden
- H6924G | קֶ֫דֶם (qe.dem): front: east
- H7760H | שׂוּם (sum): to set: put
- H8033G | שָׁם (sham): there
- H6086H | עֵץ (ets): tree
- H2530A | חָמַד (cha.mad): to desire
- H4758 | מַרְאֶה (mar.eh): appearance
- H2896A | טוֹב (tov): pleasant
- H3978 | מַאֲכָל (ma.a.khal): food
- H8432 | תָּ֫וֶךְ (ta.vekh): midst
- H1847 | דַּ֫עַת (da.at): knowledge
- H2896B | טוֹב (tov): good
- H7451B | רַע (ra): bad: evil
- H5104H | נָהָר (na.har): river
- H3318L | יָצָא (ya.tsa): to come out: issue
- H6504 | פָּרַד (pa.rad): to separate
- H702 | אַרְבַּע (ar.ba): four
- H7218J | רֹאשׁ (rosh): head: first
- H8034 | שֵׁם (shem): name
- H259 | אֶחָד (e.chad): one
- H6376 | פִּישׁוֹן (pi.shon): Pishon
- H1931 | הוּא (hu): he/she/it
- H5437G | סָבַב (sa.vav): to turn: turn
- H2341G | חֲוִילָה (cha.vi.lah): Havilah
- H2091 | זָהָב (za.hav): gold
- H916 | בְּדֹ֫לַח (be.do.lach): bdellium
- H68G | אֶ֫בֶן (e.ven): stone
- H7718 | שֹׁ֫הַם (sho.ham): onyx
- H8145 | שֵׁנִי (she.ni): second
- H1521 | גִּיחוֹן (gi.chon): Gihon
- H3568A | כּוּשׁ (kush): Cush
- H7992 | שְׁלִישִׁי (she.li.shi): third
- H2313 | חִדֶּ֫קֶל (chid.de.qel): Tigris
- H1980I | הָלַךְ (ha.lakh): to go: walk
- H6926 | קִדְמָה (qid.mah): east
- H804G | אַשּׁוּר (ash.shur): Assyria
- H7243 | רְבִיעִי (re.vi.i): fourth
- H6578 | פְּרָת (pe.rat): Euphrates
- H3947G | לָקַח (la.qach): to take: take
- H5117 | נוּחַ (nu.ach): to rest
- H8104H | שָׁמַר (sha.mar): to keep: guard
- H6680 | צָוָה (tsa.vah): to command
- H559 | אָמַר (a.mar): to say
- H398 | אָכַל (a.khal): to eat
- H4191 | מוּת (mut): to die
- H905H | בַּד (bad): alone
- H9005 | /ל (l): to/for
- H5828 | עֵ֫זֶר (e.zer): helper
- H5048 | נֶ֫גֶד (ne.ged): before
- H2416C | חַיָּה (chay.yah): living thing
- H5775 | עוֹף (oph): bird
- H935P | בּוֹא (bo): to come (in): bring
- H413 | אֶל (el): to(wards)
- H7200G | רָאָה (ra.ah): to see: see
- H4100 | מָה (mah): what?
- H7121H | קָרָא (qa.ra): to call: call by
- H929 | בְּהֵמָה (be.he.mah): animal
- H121G | אָדָם (a.dam): Adam
- H4672 | מָצָא (ma.tsa): to find
- H5307G | נָפַל (na.phal): to fall: fall
- H8639 | תַּרְדֵּמָה (tar.de.mah): deep sleep
- H3462 | יָשֵׁן (ya.shen): to sleep
- H6763 | צֵלָע (tse.la): side
- H5462 | סָגַר (sa.gar): to shut
- H1320 | בָּשָׂר (ba.sar): flesh
- H8478H | תַּחַת (ta.chat): underneath: instead
- H1129 | בָּנָה (ba.nah): to build
- H802G | אִשָּׁה (ish.shah): woman
- H2063 | זֹאת (zot): this
- H6471 | פַּ֫עַם (pa.am): beat
- H6106G | עֶ֫צֶם (e.tsem): bone
- H376G | אִישׁ (ish): man
- H3651C | כֵּן (ken): so
- H5800A | עָזַב (a.zav): to leave: forsake
- H1G | אָב (av): father
- H517 | אֵם (em): mother
- H1692 | דָּבַק (da.vaq): to cleave
- H802H | אִשָּׁה (ish.shah): woman: wife
- H8147 | שְׁנַ֫יִם (she.na.yim): two
- H6174 | עָרוֹם (a.rom): naked
- H954 | בּוֹשׁ (bush): be ashamed


【STEP 原文資料使用邊界】
- STEP Bible 是原文證據層，不是第五套 commentary：可直接支持本章詞形、lemma、Strong 編號、morphology、context gloss 與 lexicon 義域等語言事實；不得把它算成CT／GT／KC／BH 的註釋共識票。
- Lexicon 是可能義域，不等於本節必然語境義；morphology 是語法形態，不會自行推出神學結論。語言事實與註釋家的解讀必須分開表述，神學判斷仍須由經文脈絡或註釋來源支持。
- 表達不同層次時要正面分層：先說 STEP 能確認的字形、lemma、Strong、morphology、本節譯義或簡要義域，再說部分註釋如何從整段或其他經文進一步理解。除非原文、Strong、詞形或 lexical identification 確有可驗證衝突，否則不要寫成『這個字不能證明……』『STEP 沒有這個意思』『這只是神學推論』等反駁或裁決語氣。
- STEP 可以觸發原文候選，但只建立有研究價值、跨章累積價值或實質內容的概念；不得因每個功能詞、詞形或 Strong 編號批量建頁，Strong 編號也不是 wiki 條目 ID。

【規則】knowledge_nodes 是「分組→節點清單」的物件，值必須是純字串陣列（既有條目或本章新建條目的完整名稱），不可用巢狀物件或額外欄位，例如：
  神學: [會幕, 神的同在]
  原文: [皂莢木（atzei shittim）]
分組名只能用既有分類：主題、事件、互文、人物、原文、地點、文化、歷史、神學、背景、解經爭議——不可自創「儀式」「祭物」「預表」之類的新分組（依各節點所屬條目的實際分類歸組）。
只列值得跨章累積的核心節點，不重列所有經文 link。
※ 條目名本身含逗號時「必須加引號」，例如 - "信徒作祭司（彼前2：5,9）"；不加引號會被 YAML 拆成兩個碎片節點，兩個都對不上條目而被靜靜丟掉，整個節點連同它的章節累積資料就消失了（程式會擋）。
※ 互文分組的節點要帶小標題，讓人一眼知道那節在講什麼：寫 [[出20：16|出20：16 第九誡不可作假見證]]，不要只寫 [[出20：16]]。

organization（本章整理）用「裸 markdown」直接寫在分隔線之後（輸出格式見文末）——不是 YAML 欄位、不用縮排、不用任何跳脫，mermaid／表格／callout 照一般 markdown 寫即可。

【硬規格——程式會驗證，不符會退回重做】
- 依本章段落結構分成至少 3 個小節，每小節以「### 標題（vX-Y）」開頭；最後可加一個跨章脈絡／預表整理的主題小節。
- 全文合計 ≥1000 字，其中散文敘述至少 500 字——沿經文脈絡整合各來源觀點的連貫敘述是主幹，表格、清單、callout 都是它的補充，不可把大半內容包進表格或 callout。
- 這是 Obsidian 筆記庫：行文首次提到本章條目時用 wiki-link 連結，用詞不同寫 [[完整條目名|行文用詞]]，之後再提不必重連；至少要有一個連結，且目標只能取自本章可連條目：安息、安息日、創造（從無到有）、耶和華神的名字、創世記2章與1章關係、創世記2章19節創造次序問題、亞當、夏娃、人、有靈的活人、人的尊嚴與神的形像、地上塵土與生命氣息、配偶幫助者、女人由肋骨造成、配偶與婚姻、婚姻的盟約與次序、基督之新婦（豫表）、伊甸、伊甸園四河、生命樹、分別善惡的樹、神的命令與自由意志、死的三層、骨中的骨，肉中的肉、修理與看守、神命名與主權、赤身露體不羞恥、比遜、哈腓拉、基訓、古實、底格里斯、亞述、伯拉大河、約翰福音5章父與子仍然作工、希伯來書4章神的安息、約翰福音19章肋旁血和水、以弗所書5章基督與教會的婚姻奧祕、馬太福音19章婚姻不可分開、與古代近東創世神話的對比——不可連清單外的目標；清單裡沒有對應條目的概念（vault 裡存在與否都一樣），直接用純文字提及即可，不要加 [[ ]]。
- 所有輸出用繁體中文：引用英文來源（KingComments、BibleHub）時必須譯成繁體中文再以「」直接引，不可整段貼英文原文；只有原文用字本身是重點時，才以括號附註原文詞。
- 內容只能出自上面的經文與來源；整合重點而非搬運來源全文。
- 表格儲存格內不可放帶別名的 wiki-link：[[目標|別名]] 在表格裡要跳脫成 \|，渲染後變成 [[目標\]] 斷鏈（程式會擋）。表格內請用不帶別名的 [[目標]]，或把連結寫在儲存格文字之後：文字（見 [[目標]]）。
- 引述註釋請「直接引原話」並標明是哪一家（CT／GT／KC／BH 或 GT 內的《丁道爾》《舊約背景註釋》《中文聖經註釋》《精讀本》等），不要改寫成「CT指出…」的轉述體，也不可把甲家的話掛到乙家名下——已知實例：《舊約背景註釋》的古代近東材料被誤植為 KC、CT 的靈意註解被誤植為 KC。某一家在某處沒有說法，就不要替他生一個。
STEP 的詞形、Strong、morphology、context gloss 或 lexicon 義域請明標為 STEP語言資料，不要寫成某位註釋家的觀點，也不要把它加入『多家一致』的計數。
- 各家彼此矛盾時要並陳，不要壓平成單一說法——例如出27 的壇，CT 說「表徵耶穌的十字架」，KC 卻明說「不那麼是說到十字架，而是說到主耶穌自己」，這種分歧本身就是重點。
- 不要寫「參考資料」清單——程式會自動附上來源 URL。

【設計空間——你是本章筆記的設計者，圖表優先】
硬規格之內體裁自由，但預設立場是「能用圖表就用圖表」：動筆前先讀完材料，逐段判斷資訊的形狀；凡材料是流程、路線、對照、階層、關係、時間軸的形狀，一律用對應的 mermaid／表格呈現——只有純敘事、純解經論述這類沒有結構形狀的材料才整段散文。一章寫完若一張圖表都沒有，幾乎可以肯定是漏判了材料形狀，回頭重新檢查。
※ 但圖表不折抵份量：硬規格的總字數與散文主幹下限必須先由連貫的散文敘述滿足（小節數也一樣），圖表是加在主幹之上的呈現層——正確做法是「散文寫足整合敘述＋同一材料的結構面另以圖表呈現」，不是「用圖表代替散文」。
- 理解與整合（沿經文脈絡串起各來源解讀）→ 散文，這是主幹。
- 比較與對照（多項並列、新舊呼應、尺寸規格、來源間差異、重複模式）→ markdown 表格或短編號清單。
- 流程與因果（獻祭步驟、制度建立、事件因果鏈）→ mermaid flowchart。
- 時間與發展（事件推進、跨章年代脈絡）→ mermaid timeline。
- 分類與階層（神學概念展開、支派分組、家譜樹）→ mermaid mindmap 或 flowchart 樹狀。
- 關係與空間（人物關係網、行程路線、空間配置）→ mermaid graph／flowchart。
- 對答與往返（人與神的對話交涉、代求）→ mermaid sequenceDiagram。
- 補充與旁註 → callout：[!quote] 收來源關鍵引句、[!note]／[!info] 標「這是來源解讀、非經文明言」的分辨、[!important] 突顯本章樞紐、[!question] 留懸而未決的問題；補充性長內容可用可摺疊的「> [!example]- 標題」預設收合。
- 關鍵詞句可用 ==高亮==。
mermaid 技術規格：圖型限 flowchart、graph、timeline、mindmap、sequenceDiagram；節點標籤一律用雙引號包住（如 A["燔祭壇"]）以免特殊字元破圖；圖內放不了 wiki-link，關鍵詞仍要在行文中連結；圖旁配散文說明，不可只丟一張圖。
唯一原則：形式服務材料——用某個手法是因為材料是那個形狀，不是為了裝飾；本章若沒有合適形狀的材料，整段散文完全正當。
【禁用】![[]] 嵌入、mermaid 以外的程式碼區塊、#標籤、HTML——會重複條目內文、破壞頁面或污染 vault。

【輸出格式，極重要】輸出分成兩段，中間用單獨一行「===ORGANIZATION===」隔開：
第一段：只含 book/chapter/knowledge_nodes 的 YAML（可放 ```yaml 圍欄內），不可多包一層 key，也不要放 organization。
第二段：本章整理的 markdown 原文，從分隔線下一行直接開始——不是 YAML、不用縮排或跳脫，可自由使用 mermaid 圍欄、表格、callout；不要把整段再包進任何程式碼圍欄。範例：
```yaml
book: 創世記
chapter: 2
knowledge_nodes:
  神學: [山上的樣式]
  原文: [皂莢木（atzei shittim）]
```
===ORGANIZATION===
### 標題一（v1-6）
文字…神吩咐用 [[皂莢木（atzei shittim）|皂莢木]] 做櫃…

### 標題二（v7-13）
文字…

payload 欄位：book, chapter, knowledge_nodes, organization, references。詳見 _config/schemas/chapter_content.schema.json。