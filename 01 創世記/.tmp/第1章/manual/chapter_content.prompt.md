你是聖經研經資料整理員。唯一任務：為 創世記 第1章填寫 chapter_content payload（本章知識節點 + 本章整理）。

【經文】
1. 起初，神創造天地。
2. 地是空虛混沌，淵面黑暗；神的靈運行在水面上。
3. 神說：要有光，就有了光。
4. 神看光是好的，就把光暗分開了。
5. 神稱光為晝，稱暗為夜。有晚上，有早晨，這是頭一日。
6. 神說：諸水之間要有空氣，將水分為上下。
7. 神就造出空氣，將空氣以下的水、空氣以上的水分開了。事就這樣成了。
8. 神稱空氣為天。有晚上，有早晨，是第二日。
9. 神說：天下的水要聚在一處，使旱地露出來。事就這樣成了。
10. 神稱旱地為地，稱水的聚處為海。神看著是好的。
11. 神說：地要發生青草和結種子的菜蔬，並結果子的樹木，各從其類，果子都包著核。事就這樣成了。
12. 於是地發生了青草和結種子的菜蔬，各從其類；並結果子的樹木，各從其類；果子都包著核。神看著是好的。
13. 有晚上，有早晨，是第三日。
14. 神說：天上要有光體，可以分晝夜，作記號，定節令、日子、年歲，
15. 並要發光在天空，普照在地上。事就這樣成了。
16. 於是神造了兩個大光，大的管晝，小的管夜，又造眾星，
17. 就把這些光擺列在天空，普照在地上，
18. 管理晝夜，分別明暗。神看著是好的。
19. 有晚上，有早晨，是第四日。
20. 神說：水要多多滋生有生命的物；要有雀鳥飛在地面以上，天空之中。
21. 神就造出大魚和水中所滋生各樣有生命的動物，各從其類；又造出各樣飛鳥，各從其類。神看著是好的。
22. 神就賜福給這一切，說：滋生繁多，充滿海中的水；雀鳥也要多生在地上。
23. 有晚上，有早晨，是第五日。
24. 神說：地要生出活物來，各從其類；牲畜、昆蟲、野獸，各從其類。事就這樣成了。
25. 於是神造出野獸，各從其類；牲畜，各從其類；地上一切昆蟲，各從其類。神看著是好的。
26. 神說：我們要照著我們的形像、按著我們的樣式造人，使他們管理海裡的魚、空中的鳥、地上的牲畜，和全地，並地上所爬的一切昆蟲。
27. 神就照著自己的形像造人，乃是照著他的形像造男造女。
28. 神就賜福給他們，又對他們說：要生養眾多，遍滿地面，治理這地，也要管理海裡的魚、空中的鳥，和地上各樣行動的活物。
29. 神說：看哪，我將遍地上一切結種子的菜蔬和一切樹上所結有核的果子全賜給你們作食物。
30. 至於地上的走獸和空中的飛鳥，並各樣爬在地上有生命的物，我將青草賜給他們作食物。事就這樣成了。
31. 神看著一切所造的都甚好。有晚上，有早晨，是第六日。

【本章來源 context】
## 本章 Commentary Sources

你已依 manual/sources.md 全文閱讀以下正式 commentary；本 prompt 不重複內嵌原文全文。
- 研經註解（BibleHub Study）
  path: raw_data/biblehub_study_genesis_1.txt
  URL: https://biblehub.com/study/genesis/1.htm
- 研經註解（KingComments）
  path: raw_data/kingcomments_genesis_1.txt
  URL: https://www.kingcomments.com/en/bible-studies/Gen/1
- 逐節註解（ccbiblestudy CT）
  path: raw_data/ccbiblestudy_CT_genesis_1.txt
  URL: https://www.ccbiblestudy.org/Old%20Testament/01Gen/01CT01.htm
- 拾穗（ccbiblestudy GT）
  path: raw_data/ccbiblestudy_GT_genesis_1.txt
  URL: https://www.ccbiblestudy.org/Old%20Testament/01Gen/01GT01.htm

所有 commentary 敘述仍必須忠於上述已全文閱讀來源；不得以摘要或關鍵字 grep 取代全文閱讀。


## STEP Bible task projection
- source: stepbible_genesis_1.txt
- reference: Genesis 1
- selected verses: 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31
- boundary: lexicon 是可能義域，不等於本節語境義；morphology 不自行證明神學結論。

### Occurrences
format: position | original | transliteration | exact Extended Strong | morphology code | context gloss
#### Gen 1:1
- 1 | בְּ/רֵאשִׁ֖ית | be./re.Shit | H7225G | HR/Ncfsa | in/ beginning
- 2 | בָּרָ֣א | ba.Ra' | H1254A | HVqp3ms | he created
- 3 | אֱלֹהִ֑ים | 'E.lo.Him | H430G | HNcmpa | God
- 4 | אֵ֥ת | 'et | H853 | HTo | <obj.>
- 5 | הַ/שָּׁמַ֖יִם | ha./sha.Ma.yim | H8064 | HTd/Ncmpa | the/ heavens
- 6 | וְ/אֵ֥ת | ve./'Et | H853 | HC/To | and/ <obj.>
- 7 | הָ/אָֽרֶץ\׃ | ha./'A.retz | H776G | HTd/Ncfsa | the/ earth
#### Gen 1:2
- 1 | וְ/הָ/אָ֗רֶץ | ve./ha./'A.retz | H776G | HC/Td/Ncfsa | and/ the/ earth
- 2 | הָיְתָ֥ה | ha.ye.Tah | H1961 | HVqp3fs | <it> was
- 3 | תֹ֙הוּ֙ | to.hu | H8414 | HNcmsa | formlessness
- 4 | וָ/בֹ֔הוּ | va./Vo.hu | H922 | HC/Ncmsa | and/ emptiness
- 5 | וְ/חֹ֖שֶׁךְ | ve./Cho.shekh | H2822 | HC/Ncmsa | and/ darkness
- 6 | עַל\־ | 'al- | H5921A | HR | [was] over
- 7 | פְּנֵ֣י | pe.Nei | H6440J | HNcmpc | [the] surface of
- 8 | תְה֑וֹם | te.Hom | H8415 | HNcfsa | [the] deep
- 9 | וְ/ר֣וּחַ | ve./Ru.ach | H7307G | HC/Ncfsc | and/ [the] spirit of
- 10 | אֱלֹהִ֔ים | 'E.lo.Him | H430G | HNcmpa | God
- 11 | מְרַחֶ֖פֶת | me.ra.Che.fet | H7363B | HVprfsa | [was] hovering
- 12 | עַל\־ | 'al- | H5921A | HR | over
- 13 | פְּנֵ֥י | pe.Nei | H6440J | HNcmpc | [the] surface of
- 14 | הַ/מָּֽיִם\׃ | ha./Ma.yim | H4325G | HTd/Ncmpa | the/ waters
#### Gen 1:3
- 1 | וַ/יֹּ֥אמֶר | va/i.Yo.mer | H559 | Hc/Vqw3ms | and/ he said
- 2 | אֱלֹהִ֖ים | 'E.lo.Him | H430G | HNcmpa | God
- 3 | יְהִ֣י | ye.Hi | H1961 | HVqj3ms | let it be
- 4 | א֑וֹר | 'or | H216 | HNcfsa | light
- 5 | וַֽ/יְהִי\־ | va/y.hi- | H1961 | Hc/Vqw3ms | and/ there was
- 6 | אֽוֹר\׃ | 'or | H216 | HNcfsa | light
#### Gen 1:4
- 1 | וַ/יַּ֧רְא | va/i.Yar' | H7200G | Hc/Vqw3ms | and/ he saw
- 2 | אֱלֹהִ֛ים | 'E.lo.Him | H430G | HNcmpa | God
- 3 | אֶת\־ | 'et- | H853 | HTo | <obj.>
- 4 | הָ/א֖וֹר | ha./'Or | H216 | HTd/Ncfsa | the/ light
- 5 | כִּי\־ | ki- | H3588A | HTc | that
- 6 | ט֑וֹב | Tov | H2895 | HVqp3ms | [it was] good
- 7 | וַ/יַּבְדֵּ֣ל | va/i.yav.Del | H914 | Hc/Vhw3ms | and/ he separated
- 8 | אֱלֹהִ֔ים | 'E.lo.Him | H430G | HNcmpa | God
- 9 | בֵּ֥ין | bein | H996G | HAcmsc | between
- 10 | הָ/א֖וֹר | ha./'Or | H216 | HTd/Ncfsa | the/ light
- 11 | וּ/בֵ֥ין | u./Vein | H996G | HC/Acmsc | and/ between
- 12 | הַ/חֹֽשֶׁךְ\׃ | ha./Cho.shekh | H2822 | HTd/Ncmsa | the/ darkness
#### Gen 1:5
- 1 | וַ/יִּקְרָ֨א | va/i.yik.Ra' | H7121H | Hc/Vqw3ms | and/ he called
- 2 | אֱלֹהִ֤ים\׀ | 'E.lo.Him | H430G | HNcmpa | God
- 3 | לָ/אוֹר֙ | la./'Or | H216 | HRd/Ncfsa | <to> the/ light
- 4 | י֔וֹם | Yom | H3117G | HNcmsa | day
- 5 | וְ/לַ/חֹ֖שֶׁךְ | ve./la./Cho.shekh | H2822 | HC/Rd/Ncmsa | and/ <to> the/ darkness
- 6 | קָ֣רָא | Ka.ra' | H7121H | HVqp3ms | he called
- 7 | לָ֑יְלָה | Lai.lah | H3915 | HNcmsa | night
- 8 | וַֽ/יְהִי\־ | va/y.hi- | H1961 | Hc/Vqw3ms | and/ there was
- 9 | עֶ֥רֶב | 'E.rev | H6153 | HNcmsa | evening
- 10 | וַֽ/יְהִי\־ | va/y.hi- | H1961 | Hc/Vqw3ms | and/ there was
- 11 | בֹ֖קֶר | Vo.ker | H1242 | HNcmsa | morning
- 12 | י֥וֹם | Yom | H3117G | HNcmsa | day
- 13 | אֶחָֽד\׃\ \פ | 'e.Chad | H259 | HAcfsa | one
#### Gen 1:6
- 1 | וַ/יֹּ֣אמֶר | va/i.Yo.mer | H559 | Hc/Vqw3ms | and/ he said
- 2 | אֱלֹהִ֔ים | 'E.lo.Him | H430G | HNcmpa | God
- 3 | יְהִ֥י | ye.Hi | H1961 | HVqj3ms | let it be
- 4 | רָקִ֖יעַ | ra.Ki.a' | H7549 | HNcmsa | a firmament
- 5 | בְּ/ת֣וֹךְ | be./Tokh | H8432 | HR/Ncmsc | in/ [the] middle of
- 6 | הַ/מָּ֑יִם | ha./Ma.yim | H4325G | HTd/Ncmpa | the/ waters
- 7 | וִ/יהִ֣י | vi./Hi | H1961 | HC/Vqj3ms | and/ let it be
- 8 | מַבְדִּ֔יל | mav.Dil | H914 | HVhrmsa | separating
- 9 | בֵּ֥ין | bein | H996G | HAcmsc | between
- 10 | מַ֖יִם | Ma.yim | H4325G | HNcmpa | waters
- 11 | לָ/מָֽיִם\׃ | la./Ma.yim | H4325G | HR/Ncmpa | to/ waters
#### Gen 1:7
- 1 | וַ/יַּ֣עַשׂ | va/i.Ya.'as | H6213H | Hc/Vqw3ms | and/ he made
- 2 | אֱלֹהִים֮ | 'E.lo.Him | H430G | HNcmpa | God
- 3 | אֶת\־ | 'et- | H853 | HTo | <obj.>
- 4 | הָ/רָקִיעַ֒ | ha./ra.ki.a' | H7549 | HTd/Ncmsa | the/ firmament
- 5 | וַ/יַּבְדֵּ֗ל | va/i.yav.Del | H914 | Hc/Vhw3ms | and/ he separated
- 6 | בֵּ֤ין | bein | H996G | HAcmsc | between
- 7 | הַ/מַּ֙יִם֙ | ha./Ma.yim | H4325G | HTd/Ncmpa | the/ waters
- 8 | אֲשֶׁר֙ | 'a.Sher | H834A | HTr | which
- 9 | מִ/תַּ֣חַת | mi./Ta.chat | H8478G | HR/Ncmsc | [were] from/ under
- 10 | לָ/רָקִ֔יעַ | la./ra.Ki.a' | H7549 | HRd/Ncmsa | to the/ firmament
- 11 | וּ/בֵ֣ין | u./Vein | H996G | HC/Acmsc | and/ between
- 12 | הַ/מַּ֔יִם | ha./Ma.yim | H4325G | HTd/Ncmpa | the/ waters
- 13 | אֲשֶׁ֖ר | 'a.Sher | H834A | HTr | which
- 14 | מֵ/עַ֣ל | me./'Al | H5921A | HR/R | [were] from/ <above>
- 15 | לָ/רָקִ֑יעַ | la./ra.Ki.a' | H7549 | HRd/Ncmsa | <to> the/ firmament
- 16 | וַֽ/יְהִי\־ | va/y.hi- | H1961 | Hc/Vqw3ms | and/ it was
- 17 | כֵֽן\׃ | Khen | H3651C | HD | so
#### Gen 1:8
- 1 | וַ/יִּקְרָ֧א | va/i.yik.Ra' | H7121H | Hc/Vqw3ms | and/ he called
- 2 | אֱלֹהִ֛ים | 'E.lo.Him | H430G | HNcmpa | God
- 3 | לָֽ/רָקִ֖יעַ | la./ra.Ki.a' | H7549 | HRd/Ncmsa | <to> the/ firmament
- 4 | שָׁמָ֑יִם | sha.Ma.yim | H8064 | HNcmpa | heaven
- 5 | וַֽ/יְהִי\־ | va/y.hi- | H1961 | Hc/Vqw3ms | and/ there was
- 6 | עֶ֥רֶב | 'E.rev | H6153 | HNcmsa | evening
- 7 | וַֽ/יְהִי\־ | va/y.hi- | H1961 | Hc/Vqw3ms | and/ there was
- 8 | בֹ֖קֶר | Vo.ker | H1242 | HNcmsa | morning
- 9 | י֥וֹם | Yom | H3117G | HNcmsa | a day
- 10 | שֵׁנִֽי\׃\ \פ | she.Ni | H8145 | HAomsa | second
#### Gen 1:9
- 1 | וַ/יֹּ֣אמֶר | va/i.Yo.mer | H559 | Hc/Vqw3ms | and/ he said
- 2 | אֱלֹהִ֗ים | 'E.lo.Him | H430G | HNcmpa | God
- 3 | יִקָּו֨וּ | yi.ka.Vu | H6960B | HVNi3mp | let them gather
- 4 | הַ/מַּ֜יִם | ha./Ma.yim | H4325G | HTd/Ncmpa | the/ waters
- 5 | מִ/תַּ֤חַת | mi./Ta.chat | H8478G | HR/Ncmsc | from/ under
- 6 | הַ/שָּׁמַ֙יִם֙ | ha./sha.Ma.yim | H8064 | HTd/Ncmpa | the/ heavens
- 7 | אֶל\־ | 'El- | H413 | HR | to
- 8 | מָק֣וֹם | ma.Kom | H4725 | HNcmsa | a place
- 9 | אֶחָ֔ד | 'e.Chad | H259 | HAcfsa | one
- 10 | וְ/תֵרָאֶ֖ה | ve./te.ra.'Eh | H7200G | HC/VNu3fs | and/ let it appear
- 11 | הַ/יַּבָּשָׁ֑ה | hai./ya.ba.Shah | H3004 | HTd/Ncfsa | the/ dry ground
- 12 | וַֽ/יְהִי\־ | va/y.hi- | H1961 | Hc/Vqw3ms | and/ it was
- 13 | כֵֽן\׃ | Khen | H3651C | HD | so
#### Gen 1:10
- 1 | וַ/יִּקְרָ֨א | va/i.yik.Ra' | H7121H | Hc/Vqw3ms | and/ he called
- 2 | אֱלֹהִ֤ים\׀ | 'E.lo.Him | H430G | HNcmpa | God
- 3 | לַ/יַּבָּשָׁה֙ | la/i.ya.ba.Shah | H3004 | HRd/Ncfsa | <to> the/ dry ground
- 4 | אֶ֔רֶץ | 'E.retz | H776G | HNcfsa | earth
- 5 | וּ/לְ/מִקְוֵ֥ה | u./le./mik.Veh | H4723C | HC/R/Ncmsc | and/ <to>/ [the] collection of
- 6 | הַ/מַּ֖יִם | ha./Ma.yim | H4325G | HTd/Ncmpa | the/ waters
- 7 | קָרָ֣א | ka.Ra' | H7121H | HVqp3ms | he called
- 8 | יַמִּ֑ים | ya.Mim | H3220G | HNcmpa | seas
- 9 | וַ/יַּ֥רְא | va/i.Yar' | H7200G | Hc/Vqw3ms | and/ he saw
- 10 | אֱלֹהִ֖ים | 'E.lo.Him | H430G | HNcmpa | God
- 11 | כִּי\־ | ki- | H3588A | HTc | that
- 12 | טֽוֹב\׃ | Tov | H2895 | HVqp3ms | [it was] good
#### Gen 1:11
- 1 | וַ/יֹּ֣אמֶר | va/i.Yo.mer | H559 | Hc/Vqw3ms | and/ he said
- 2 | אֱלֹהִ֗ים | 'E.lo.Him | H430G | HNcmpa | God
- 3 | תַּֽדְשֵׁ֤א | tad.She' | H1876 | HVhj3fs | let it sprout
- 4 | הָ/אָ֙רֶץ֙ | ha./'A.retz | H776G | HTd/Ncfsa | the/ earth
- 5 | דֶּ֔שֶׁא | De.she' | H1877 | HNcmsa | vegetation
- 6 | עֵ֚שֶׂב | 'E.sev | H6212 | HNcmsa | plant[s]
- 7 | מַזְרִ֣יעַ | maz.Ri.a' | H2232 | HVhrmsa | [which] bears seed
- 8 | זֶ֔רַע | Ze.ra' | H2233G | HNcmsa | seed
- 9 | עֵ֣ץ | 'etz | H6086H | HNcmsc | tree[s] of
- 10 | פְּרִ֞י | pe.Ri | H6529 | HNcmsa | fruit
- 11 | עֹ֤שֶׂה | 'O.seh | H6213H | HVqrmsa | producing
- 12 | פְּרִי֙ | pe.Ri | H6529 | HNcmsa | fruit
- 13 | לְ/מִינ֔/וֹ | le./mi.N/o | H4327 | HR/Ncmsc/Sp3ms | to/ kind/ its
- 14 | אֲשֶׁ֥ר | 'a.Sher | H834A | HTr | which
- 15 | זַרְע/וֹ\־ | zar.'o/v- | H2233G | HNcmsc/Sp3ms | seed/ its
- 16 | ב֖/וֹ | v/o | H9003 | HRd/Sp3ms | [is] in <the>/ it
- 17 | עַל\־ | 'al- | H5921A | HR | on
- 18 | הָ/אָ֑רֶץ | ha./'A.retz | H776G | HTd/Ncfsa | the/ earth
- 19 | וַֽ/יְהִי\־ | va/y.hi- | H1961 | Hc/Vqw3ms | and/ it was
- 20 | כֵֽן\׃ | Khen | H3651C | HD | so
#### Gen 1:12
- 1 | וַ/תּוֹצֵ֨א | va./to.Tze' | H3318M | Hc/Vhw3fs | and/ <it> brought forth
- 2 | הָ/אָ֜רֶץ | ha./'A.retz | H776G | HTd/Ncfsa | the/ earth
- 3 | דֶּ֠שֶׁא | De.she' | H1877 | HNcmsa | vegetation
- 4 | עֵ֣שֶׂב | 'E.sev | H6212 | HNcmsa | plant[s]
- 5 | מַזְרִ֤יעַ | maz.Ri.a' | H2232 | HVhrmsa | [which] bears seed
- 6 | זֶ֙רַע֙ | ze.ra' | H2233G | HNcmsa | seed
- 7 | לְ/מִינֵ֔/הוּ | le./mi.Ne./hu | H4327 | HR/Ncmsc/Sp3ms | to/ kind/ its
- 8 | וְ/עֵ֧ץ | ve./'Etz | H6086H | HC/Ncmsa | and/ tree[s]
- 9 | עֹֽשֶׂה\־ | 'o.seh- | H6213H | HVqrmsa | producing
- 10 | פְּרִ֛י | pe.Ri | H6529 | HNcmsa | fruit
- 11 | אֲשֶׁ֥ר | 'a.Sher | H834A | HTr | which
- 12 | זַרְע/וֹ\־ | zar.'o/v- | H2233G | HNcmsc/Sp3ms | seed/ its
- 13 | ב֖/וֹ | v/o | H9003 | HRd/Sp3ms | [was] in <the>/ it
- 14 | לְ/מִינֵ֑/הוּ | le./mi.Ne./hu | H4327 | HR/Ncmsc/Sp3ms | to/ kind/ its
- 15 | וַ/יַּ֥רְא | va/i.Yar' | H7200G | Hc/Vqw3ms | and/ he saw
- 16 | אֱלֹהִ֖ים | 'E.lo.Him | H430G | HNcmpa | God
- 17 | כִּי\־ | ki- | H3588A | HTc | that
- 18 | טֽוֹב\׃ | Tov | H2895 | HVqp3ms | [it was] good
#### Gen 1:13
- 1 | וַֽ/יְהִי\־ | va/y.hi- | H1961 | Hc/Vqw3ms | and/ there was
- 2 | עֶ֥רֶב | 'E.rev | H6153 | HNcmsa | evening
- 3 | וַֽ/יְהִי\־ | va/y.hi- | H1961 | Hc/Vqw3ms | and/ there was
- 4 | בֹ֖קֶר | Vo.ker | H1242 | HNcmsa | morning
- 5 | י֥וֹם | Yom | H3117G | HNcmsa | a day
- 6 | שְׁלִישִֽׁי\׃\ \פ | she.li.Shi | H7992 | HAomsa | third
#### Gen 1:14
- 1 | וַ/יֹּ֣אמֶר | va/i.Yo.mer | H559 | Hc/Vqw3ms | and/ he said
- 2 | אֱלֹהִ֗ים | 'E.lo.Him | H430G | HNcmpa | God
- 3 | יְהִ֤י | ye.Hi | H1961 | HVqj3ms | let it be
- 4 | מְאֹרֹת֙ | me.'o.Rot | H3974 | HNcmpa | luminaries
- 5 | בִּ/רְקִ֣יעַ | bi/r.Ki.a' | H7549 | HR/Ncmsc | in/ [the] firmament of
- 6 | הַ/שָּׁמַ֔יִם | ha./sha.Ma.yim | H8064 | HTd/Ncmpa | the/ heavens
- 7 | לְ/הַבְדִּ֕יל | le./hav.Dil | H914 | HR/Vhcc | to/ separate
- 8 | בֵּ֥ין | bein | H996G | HAcmsc | between
- 9 | הַ/יּ֖וֹם | hai./Yom | H3117G | HTd/Ncmsa | the/ day
- 10 | וּ/בֵ֣ין | u./Vein | H996G | HC/Acmsc | and/ between
- 11 | הַ/לָּ֑יְלָה | ha./La.ye.lah | H3915 | HTd/Ncmsa | the/ night
- 12 | וְ/הָי֤וּ | ve./ha.Yu | H1961 | Hc/Vqq3cp | and/ they will become
- 13 | לְ/אֹתֹת֙ | le./'o.Tot | H226H | HR/Ncfpa | <into>/ signs
- 14 | וּ/לְ/מ֣וֹעֲדִ֔ים | u./le./Mo.'a.Dim | H4150G | HC/R/Ncmpa | and/ <into>/ appointed times
- 15 | וּ/לְ/יָמִ֖ים | u./le./ya.Mim | H3117G | HC/R/Ncmpa | and/ <into>/ days
- 16 | וְ/שָׁנִֽים\׃ | ve./sha.Nim | H8141 | HC/Ncmpa | and/ years
#### Gen 1:15
- 1 | וְ/הָי֤וּ | ve./ha.Yu | H1961 | Hc/Vqq3cp | and/ they will become
- 2 | לִ/מְאוֹרֹת֙ | li/m.'o.Rot | H3974 | HR/Ncmpa | <into>/ luminaries
- 3 | בִּ/רְקִ֣יעַ | bi/r.Ki.a' | H7549 | HR/Ncmsc | in/ [the] firmament of
- 4 | הַ/שָּׁמַ֔יִם | ha./sha.Ma.yim | H8064 | HTd/Ncmpa | the/ heavens
- 5 | לְ/הָאִ֖יר | le./ha.'Ir | H215 | HR/Vhcc | to/ give light
- 6 | עַל\־ | 'al- | H5921A | HR | on
- 7 | הָ/אָ֑רֶץ | ha./'A.retz | H776G | HTd/Ncfsa | the/ earth
- 8 | וַֽ/יְהִי\־ | va/y.hi- | H1961 | Hc/Vqw3ms | and/ it was
- 9 | כֵֽן\׃ | Khen | H3651C | HD | so
#### Gen 1:16
- 1 | וַ/יַּ֣עַשׂ | va/i.Ya.'as | H6213H | Hc/Vqw3ms | and/ he made
- 2 | אֱלֹהִ֔ים | 'E.lo.Him | H430G | HNcmpa | God
- 3 | אֶת\־ | 'et- | H853 | HTo | <obj.>
- 4 | שְׁנֵ֥י | she.Nei | H8147 | HAcbdc | [the] two
- 5 | הַ/מְּאֹרֹ֖ת | ha./me.'o.Rot | H3974 | HTd/Ncmpa | the/ luminaries
- 6 | הַ/גְּדֹלִ֑ים | ha./ge.do.Lim | H1419A | HTd/Aampa | <the>/ great
- 7 | אֶת\־ | 'et- | H853 | HTo | <obj.>
- 8 | הַ/מָּא֤וֹר | ha./ma.'or | H3974 | HTd/Ncmsa | the/ luminary
- 9 | הַ/גָּדֹל֙ | ha./ga.Dol | H1419A | HTd/Aamsa | <the>/ great
- 10 | לְ/מֶמְשֶׁ֣לֶת | le./mem.She.let | H4475 | HR/Ncfsc | for/ [the] dominion of
- 11 | הַ/יּ֔וֹם | hai./Yom | H3117G | HTd/Ncmsa | the/ day
- 12 | וְ/אֶת\־ | ve./'Et | H853 | HC/To | and/ <obj.>
- 13 | הַ/מָּא֤וֹר | ha./ma.'or | H3974 | HTd/Ncmsa | the/ luminary
- 14 | הַ/קָּטֹן֙ | ha./ka.Ton | H6996B | HTd/Aamsa | <the>/ small
- 15 | לְ/מֶמְשֶׁ֣לֶת | le./mem.She.let | H4475 | HR/Ncfsc | for/ [the] dominion of
- 16 | הַ/לַּ֔יְלָה | ha./Lay.lah | H3915 | HTd/Ncmsa | the/ night
- 17 | וְ/אֵ֖ת | ve./'Et | H853 | HC/To | and/ <obj.>
- 18 | הַ/כּוֹכָבִֽים\׃ | ha./ko.kha.Vim | H3556 | HTd/Ncmpa | the/ stars
#### Gen 1:17
- 1 | וַ/יִּתֵּ֥ן | va/i.yi.Ten | H5414H | Hc/Vqw3ms | and/ he set
- 2 | אֹתָ֛/ם | 'o.Ta/m | H853 | HTo/Sp3mp | <obj.>/ them
- 3 | אֱלֹהִ֖ים | 'E.lo.Him | H430G | HNcmpa | God
- 4 | בִּ/רְקִ֣יעַ | bi/r.Ki.a' | H7549 | HR/Ncmsc | in/ [the] firmament of
- 5 | הַ/שָּׁמָ֑יִם | ha./sha.Ma.yim | H8064 | HTd/Ncmpa | the/ heavens
- 6 | לְ/הָאִ֖יר | le./ha.'Ir | H215 | HR/Vhcc | to/ give light
- 7 | עַל\־ | 'al- | H5921A | HR | on
- 8 | הָ/אָֽרֶץ\׃ | ha./'A.retz | H776G | HTd/Ncfsa | the/ earth
#### Gen 1:18
- 1 | וְ/לִ/מְשֹׁל֙ | ve./li/m.Shol | H4910 | HC/R/Vqcc | and/ to/ rule
- 2 | בַּ/יּ֣וֹם | ba/i.Yom | H3117G | HRd/Ncmsa | over the/ day
- 3 | וּ/בַ/לַּ֔יְלָה | u./va./Lay.lah | H3915 | HC/Rd/Ncmsa | and/ over the/ night
- 4 | וּֽ/לֲ/הַבְדִּ֔יל | u./la./hav.Dil | H914 | HC/R/Vhcc | and/ to/ separate
- 5 | בֵּ֥ין | bein | H996G | HAcmsc | between
- 6 | הָ/א֖וֹר | ha./'Or | H216 | HTd/Ncfsa | the/ light
- 7 | וּ/בֵ֣ין | u./Vein | H996G | HC/Acmsc | and/ between
- 8 | הַ/חֹ֑שֶׁךְ | ha./Cho.shekh | H2822 | HTd/Ncmsa | the/ darkness
- 9 | וַ/יַּ֥רְא | va/i.Yar' | H7200G | Hc/Vqw3ms | and/ he saw
- 10 | אֱלֹהִ֖ים | 'E.lo.Him | H430G | HNcmpa | God
- 11 | כִּי\־ | ki- | H3588A | HTc | that
- 12 | טֽוֹב\׃ | Tov | H2895 | HVqp3ms | [it was] good
#### Gen 1:19
- 1 | וַֽ/יְהִי\־ | va/y.hi- | H1961 | Hc/Vqw3ms | and/ there was
- 2 | עֶ֥רֶב | 'E.rev | H6153 | HNcmsa | evening
- 3 | וַֽ/יְהִי\־ | va/y.hi- | H1961 | Hc/Vqw3ms | and/ there was
- 4 | בֹ֖קֶר | Vo.ker | H1242 | HNcmsa | morning
- 5 | י֥וֹם | Yom | H3117G | HNcmsa | a day
- 6 | רְבִיעִֽי\׃\ \פ | re.vi.'I | H7243 | HAomsa | fourth
#### Gen 1:20
- 1 | וַ/יֹּ֣אמֶר | va/i.Yo.mer | H559 | Hc/Vqw3ms | and/ he said
- 2 | אֱלֹהִ֔ים | 'E.lo.Him | H430G | HNcmpa | God
- 3 | יִשְׁרְצ֣וּ | yish.re.Tzu | H8317 | HVqi3mp | let them swarm
- 4 | הַ/מַּ֔יִם | ha./Ma.yim | H4325G | HTd/Ncmpa | the/ waters
- 5 | שֶׁ֖רֶץ | She.retz | H8318 | HNcmsc | swarming thing[s]
- 6 | נֶ֣פֶשׁ | Ne.fesh | H5315K | HNcfsa | creature[s]
- 7 | חַיָּ֑ה | chai.Yah | H2416A | HAafsa | living
- 8 | וְ/עוֹף֙ | ve./'Of | H5775 | HC/Ncmsa | and/ bird[s]
- 9 | יְעוֹפֵ֣ף | ye.'o.Fef | H5774A | HVpi3ms | let it fly
- 10 | עַל\־ | 'al- | H5921A | HR | above
- 11 | הָ/אָ֔רֶץ | ha./'A.retz | H776G | HTd/Ncfsa | the/ earth
- 12 | עַל\־ | 'al- | H5921A | HR | on
- 13 | פְּנֵ֖י | pe.Nei | H6440J | HNcmpc | [the] surface of
- 14 | רְקִ֥יעַ | re.Ki.a' | H7549 | HNcmsc | [the] firmament of
- 15 | הַ/שָּׁמָֽיִם\׃ | ha./sha.Ma.yim | H8064 | HTd/Ncmpa | the/ heavens
#### Gen 1:21
- 1 | וַ/יִּבְרָ֣א | va/i.yiv.Ra' | H1254A | Hc/Vqw3ms | and/ he created
- 2 | אֱלֹהִ֔ים | 'E.lo.Him | H430G | HNcmpa | God
- 3 | אֶת\־ | 'et- | H853 | HTo | <obj.>
- 4 | הַ/תַּנִּינִ֖ם | ha./ta.ni.Nim | H8577N | HTd/Ncmpa | the/ sea monsters
- 5 | הַ/גְּדֹלִ֑ים | ha./ge.do.Lim | H1419A | HTd/Aampa | <the>/ great
- 6 | וְ/אֵ֣ת | ve./'Et | H853 | HC/To | and/ <obj.>
- 7 | כָּל\־ | kol- | H3605 | HNcmsc | every
- 8 | נֶ֣פֶשׁ | Ne.fesh | H5315K | HNcfsa | creature
- 9 | הַֽ/חַיָּ֣ה\׀ | ha./chai.Yah | H2416A | HTd/Aafsa | <the>/ living
- 10 | הָֽ/רֹמֶ֡שֶׂת | ha./ro.Me.set | H7430 | HTd/Vqrfsa | which/ creeps
- 11 | אֲשֶׁר֩ | 'a.Sher | H834A | HTr | which
- 12 | שָׁרְצ֨וּ | sha.re.Tzu | H8317 | HVqp3cp | they swarmed
- 13 | הַ/מַּ֜יִם | ha./Ma.yim | H4325G | HTd/Ncmpa | the/ waters
- 14 | לְ/מִֽינֵ/הֶ֗ם | le./mi.ne./Hem | H4327 | HR/Ncmsc/Sp3mp | to/ kind/ their
- 15 | וְ/אֵ֨ת | ve./'Et | H853 | HC/To | and/ <obj.>
- 16 | כָּל\־ | kol- | H3605 | HNcmsc | every
- 17 | ע֤וֹף | of | H5775 | HNcmsc | bird of
- 18 | כָּנָף֙ | ka.Naf | H3671 | HNcfsa | wing
- 19 | לְ/מִינֵ֔/הוּ | le./mi.Ne./hu | H4327 | HR/Ncmsc/Sp3ms | to/ kind/ its
- 20 | וַ/יַּ֥רְא | va/i.Yar' | H7200G | Hc/Vqw3ms | and/ he saw
- 21 | אֱלֹהִ֖ים | 'E.lo.Him | H430G | HNcmpa | God
- 22 | כִּי\־ | ki- | H3588A | HTc | that
- 23 | טֽוֹב\׃ | Tov | H2895 | HVqp3ms | [it was] good
#### Gen 1:22
- 1 | וַ/יְבָ֧רֶךְ | va/y.Va.rekh | H1288 | Hc/Vpw3ms | and/ he blessed
- 2 | אֹתָ֛/ם | 'o.Ta/m | H853 | HTo/Sp3mp | <obj.>/ them
- 3 | אֱלֹהִ֖ים | 'E.lo.Him | H430G | HNcmpa | God
- 4 | לֵ/אמֹ֑ר | le./Mor | H559 | HR/Vqcc | <to>/ saying
- 5 | פְּר֣וּ | pe.Ru | H6509 | HVqv2mp | be fruitful
- 6 | וּ/רְב֗וּ | u./re.Vu | H7235A | HC/Vqv2mp | and/ multiply
- 7 | וּ/מִלְא֤וּ | u./mil.'U | H4390 | HC/Vqv2mp | and/ fill
- 8 | אֶת\־ | 'et- | H853 | HTo | <obj.>
- 9 | הַ/מַּ֙יִם֙ | ha./Ma.yim | H4325G | HTd/Ncmpa | the/ waters
- 10 | בַּ/יַּמִּ֔ים | ba/i.ya.Mim | H3220G | HRd/Ncmpa | in the/ seas
- 11 | וְ/הָ/ע֖וֹף | ve./ha./'of | H5775 | HC/Td/Ncmsa | and/ the/ bird[s]
- 12 | יִ֥רֶב | Yi.rev | H7235A | HVqj3ms | let it multiply
- 13 | בָּ/אָֽרֶץ\׃ | ba./'A.retz | H776G | HRd/Ncfsa | on the/ earth
#### Gen 1:23
- 1 | וַֽ/יְהִי\־ | va/y.hi- | H1961 | Hc/Vqw3ms | and/ there was
- 2 | עֶ֥רֶב | 'E.rev | H6153 | HNcmsa | evening
- 3 | וַֽ/יְהִי\־ | va/y.hi- | H1961 | Hc/Vqw3ms | and/ there was
- 4 | בֹ֖קֶר | Vo.ker | H1242 | HNcmsa | morning
- 5 | י֥וֹם | Yom | H3117G | HNcmsa | a day
- 6 | חֲמִישִֽׁי\׃\ \פ | cha.mi.Shi | H2549 | HAomsa | fifth
#### Gen 1:24
- 1 | וַ/יֹּ֣אמֶר | va/i.Yo.mer | H559 | Hc/Vqw3ms | and/ he said
- 2 | אֱלֹהִ֗ים | 'E.lo.Him | H430G | HNcmpa | God
- 3 | תּוֹצֵ֨א | to.Tze' | H3318M | HVhj3fs | let it produce
- 4 | הָ/אָ֜רֶץ | ha./'A.retz | H776H | HTd/Ncfsa | the/ earth
- 5 | נֶ֤פֶשׁ | Ne.fesh | H5315K | HNcfsa | creature[s]
- 6 | חַיָּה֙ | chai.Yah | H2416A | HAafsa | living
- 7 | לְ/מִינָ֔/הּ | le./mi.Na/h | H4327 | HR/Ncmsc/Sp3fs | to/ kind/ its
- 8 | בְּהֵמָ֥ה | be.he.Mah | H929 | HNcfsa | livestock
- 9 | וָ/רֶ֛מֶשׂ | va./Re.mes | H7431 | HC/Ncmsa | and/ creeping thing[s]
- 10 | וְ/חַֽיְתוֹ\־ | ve./chay.tov- | H2416C | HC/Ncfsc | and/ animal[s] of
- 11 | אֶ֖רֶץ | 'E.retz | H776H | HNcfsa | [the] earth
- 12 | לְ/מִינָ֑/הּ | le./mi.Na/h | H4327 | HR/Ncmsc/Sp3fs | to/ kind/ its
- 13 | וַֽ/יְהִי\־ | va/y.hi- | H1961 | Hc/Vqw3ms | and/ it was
- 14 | כֵֽן\׃ | Khen | H3651C | HD | so
#### Gen 1:25
- 1 | וַ/יַּ֣עַשׂ | va/i.Ya.'as | H6213H | Hc/Vqw3ms | and/ he made
- 2 | אֱלֹהִים֩ | 'E.lo.Him | H430G | HNcmpa | God
- 3 | אֶת\־ | 'et- | H853 | HTo | <obj.>
- 4 | חַיַּ֨ת | chai.Yat | H2416C | HNcfsc | [the] animal[s] of
- 5 | הָ/אָ֜רֶץ | ha./'A.retz | H776G | HTd/Ncfsa | the/ earth
- 6 | לְ/מִינָ֗/הּ | le./mi.Na/h | H4327 | HR/Ncmsc/Sp3fs | to/ kind/ its
- 7 | וְ/אֶת\־ | ve./'Et | H853 | HC/To | and/ <obj.>
- 8 | הַ/בְּהֵמָה֙ | ha./be.he.Mah | H929 | HTd/Ncfsa | the/ livestock
- 9 | לְ/מִינָ֔/הּ | le./mi.Na/h | H4327 | HR/Ncmsc/Sp3fs | to/ kind/ its
- 10 | וְ/אֵ֛ת | ve./'Et | H853 | HC/To | and/ <obj.>
- 11 | כָּל\־ | kol- | H3605 | HNcmsc | every
- 12 | רֶ֥מֶשׂ | Re.mes | H7431 | HNcmsc | <the> creeping thing of
- 13 | הָֽ/אֲדָמָ֖ה | ha./'a.da.Mah | H127G | HTd/Ncfsa | the/ ground
- 14 | לְ/מִינֵ֑/הוּ | le./mi.Ne./hu | H4327 | HR/Ncmsc/Sp3ms | to/ kind/ its
- 15 | וַ/יַּ֥רְא | va/i.Yar' | H7200G | Hc/Vqw3ms | and/ he saw
- 16 | אֱלֹהִ֖ים | 'E.lo.Him | H430G | HNcmpa | God
- 17 | כִּי\־ | ki- | H3588A | HTc | that
- 18 | טֽוֹב\׃ | Tov | H2895 | HVqp3ms | [it was] good
#### Gen 1:26
- 1 | וַ/יֹּ֣אמֶר | va/i.Yo.mer | H559 | Hc/Vqw3ms | and/ he said
- 2 | אֱלֹהִ֔ים | 'E.lo.Him | H430G | HNcmpa | God
- 3 | נַֽעֲשֶׂ֥ה | na.'a.Seh | H6213H | HVqi1cp | let us make
- 4 | אָדָ֛ם | 'a.Dam | H120G | HNcmsa | humankind
- 5 | בְּ/צַלְמֵ֖/נוּ | be./tzal.Me./nu | H6754 | HR/Ncmsc/Sp1bp | in/ image/ our
- 6 | כִּ/דְמוּתֵ֑/נוּ | ki/d.mu.Te./nu | H1823 | HR/Ncfsc/Sp1bp | according to/ likeness/ our
- 7 | וְ/יִרְדּוּ֩ | ve./yir.Du | H7287A | HC/Vqu3mp | and/ they may rule
- 8 | בִ/דְגַ֨ת | vi/d.Gat | H1710 | HR/Ncfsc | over/ [the] fish of
- 9 | הַ/יָּ֜ם | hai./Yam | H3220G | HTd/Ncmsa | the/ sea
- 10 | וּ/בְ/ע֣וֹף | u./ve./'of | H5775 | HC/R/Ncmsc | and/ over/ [the] bird[s] of
- 11 | הַ/שָּׁמַ֗יִם | ha./sha.Ma.yim | H8064 | HTd/Ncmpa | the/ heavens
- 12 | וּ/בַ/בְּהֵמָה֙ | u./va./be.he.Mah | H929 | HC/Rd/Ncfsa | and/ over the/ livestock
- 13 | וּ/בְ/כָל\־ | u./ve./Khol- | H3605 | HC/R/Ncmsc | and/ over/ all
- 14 | הָ/אָ֔רֶץ | ha./'A.retz | H776G | HTd/Ncfsa | the/ earth
- 15 | וּ/בְ/כָל\־ | u./ve./Khol- | H3605 | HC/R/Ncmsc | and/ over/ every
- 16 | הָ/רֶ֖מֶשׂ | ha./Re.mes | H7431 | HTd/Ncmsa | <the>/ creeping thing
- 17 | הָֽ/רֹמֵ֥שׂ | ha./ro.Mes | H7430 | HTd/Vqrmsa | which/ creeps
- 18 | עַל\־ | 'al- | H5921A | HR | on
- 19 | הָ/אָֽרֶץ\׃ | ha./'A.retz | H776H | HTd/Ncfsa | the/ earth
#### Gen 1:27
- 1 | וַ/יִּבְרָ֨א | va/i.yiv.Ra' | H1254A | Hc/Vqw3ms | and/ he created
- 2 | אֱלֹהִ֤ים\׀ | 'E.lo.Him | H430G | HNcmpa | God
- 3 | אֶת\־ | 'et- | H853 | HTo | <obj.>
- 4 | הָֽ/אָדָם֙ | ha./'a.Dam | H120G | HTd/Ncmsa | <the>/ humankind
- 5 | בְּ/צַלְמ֔/וֹ | be./tzal.M/o | H6754 | HR/Ncmsc/Sp3ms | in/ own image/ his
- 6 | בְּ/צֶ֥לֶם | be./Tze.lem | H6754 | HR/Ncmsc | in/ [the] image of
- 7 | אֱלֹהִ֖ים | 'E.lo.Him | H430G | HNcmpa | God
- 8 | בָּרָ֣א | ba.Ra' | H1254A | HVqp3ms | he created
- 9 | אֹת֑/וֹ | 'o.T/o | H853 | HTo/Sp3ms | <obj.>/ it
- 10 | זָכָ֥ר | za.Khar | H2145 | HAamsa | male
- 11 | וּ/נְקֵבָ֖ה | u./ne.ke.Vah | H5347 | HC/Aafsa | and/ female
- 12 | בָּרָ֥א | ba.Ra' | H1254A | HVqp3ms | he created
- 13 | אֹתָֽ/ם\׃ | 'o.Ta/m | H853 | HTo/Sp3mp | <obj.>/ them
#### Gen 1:28
- 1 | וַ/יְבָ֣רֶךְ | va/y.Va.rekh | H1288 | Hc/Vpw3ms | and/ he blessed
- 2 | אֹתָ/ם֮ | 'o.Ta/m | H853 | HTo/Sp3mp | <obj.>/ them
- 3 | אֱלֹהִים֒ | 'E.lo.Him | H430G | HNcmpa | God
- 4 | וַ/יֹּ֨אמֶר | va/i.Yo.mer | H559 | Hc/Vqw3ms | and/ he said
- 5 | לָ/הֶ֜ם | la./Hem | H9005 | HRd/Sp3mp | to <the>/ them
- 6 | אֱלֹהִ֗ים | 'E.lo.Him | H430G | HNcmpa | God
- 7 | פְּר֥וּ | pe.Ru | H6509 | HVqv2mp | be fruitful
- 8 | וּ/רְב֛וּ | u./re.Vu | H7235A | HC/Vqv2mp | and/ multiply
- 9 | וּ/מִלְא֥וּ | u./mil.'U | H4390 | HC/Vqv2mp | and/ fill
- 10 | אֶת\־ | 'et- | H853 | HTo | <obj.>
- 11 | הָ/אָ֖רֶץ | ha./'A.retz | H776G | HTd/Ncfsa | the/ earth
- 12 | וְ/כִבְשֻׁ֑/הָ | ve./khiv.Shu./ha | H3533 | HC/Vqv2mp/Sp3fs | and/ subdue/ it
- 13 | וּ/רְד֞וּ | u./re.Du | H7287A | HC/Vqv2mp | and/ rule
- 14 | בִּ/דְגַ֤ת | bi/d.Gat | H1710 | HR/Ncfsc | over/ [the] fish of
- 15 | הַ/יָּם֙ | hai./Yam | H3220G | HTd/Ncmsa | the/ sea
- 16 | וּ/בְ/ע֣וֹף | u./ve./'of | H5775 | HC/R/Ncmsc | and/ over/ [the] bird[s] of
- 17 | הַ/שָּׁמַ֔יִם | ha./sha.Ma.yim | H8064 | HTd/Ncmpa | the/ heavens
- 18 | וּ/בְ/כָל\־ | u./ve./Khol- | H3605 | HC/R/Ncmsc | and/ over/ every
- 19 | חַיָּ֖ה | chai.Yah | H2416A | HNcfsa | animal
- 20 | הָֽ/רֹמֶ֥שֶׂת | ha./ro.Me.set | H7430 | HTd/Vqrfsa | which/ creeps
- 21 | עַל\־ | 'al- | H5921A | HR | on
- 22 | הָ/אָֽרֶץ\׃ | ha./'A.retz | H776H | HTd/Ncfsa | the/ earth
#### Gen 1:29
- 1 | וַ/יֹּ֣אמֶר | va/i.Yo.mer | H559 | Hc/Vqw3ms | and/ he said
- 2 | אֱלֹהִ֗ים | 'E.lo.Him | H430G | HNcmpa | God
- 3 | הִנֵּה֩ | hi.Neh | H2009 | HTj | here!
- 4 | נָתַ֨תִּי | na.Ta.ti | H5414G | HVqp1cs | I give
- 5 | לָ/כֶ֜ם | la./Khem | H9005 | HRd/Sp2mp | to <the>/ you
- 6 | אֶת\־ | 'et- | H853 | HTo | <obj.>
- 7 | כָּל\־ | kol- | H3605 | HNcmsc | every
- 8 | עֵ֣שֶׂב\׀ | 'E.sev | H6212 | HNcmsa | plant
- 9 | זֹרֵ֣עַ | zo.Re.a' | H2232 | HVqrmsa | [which] bears seed
- 10 | זֶ֗רַע | Ze.ra' | H2233G | HNcmsa | seed
- 11 | אֲשֶׁר֙ | 'a.Sher | H834A | HTr | which
- 12 | עַל\־ | 'al- | H5921A | HR | [is] on
- 13 | פְּנֵ֣י | pe.Nei | H6440J | HNcmpc | [the] surface of
- 14 | כָל\־ | khol- | H3605 | HNcmsc | all
- 15 | הָ/אָ֔רֶץ | ha./'A.retz | H776G | HTd/Ncfsa | the/ earth
- 16 | וְ/אֶת\־ | ve./'Et | H853 | HC/To | and/ <obj.>
- 17 | כָּל\־ | kol- | H3605 | HNcmsc | every
- 18 | הָ/עֵ֛ץ | ha./'Etz | H6086H | HTd/Ncmsa | <the>/ tree
- 19 | אֲשֶׁר\־ | 'a.Sher- | H834A | HTr | which
- 20 | בּ֥/וֹ | b/o | H9003 | HRd/Sp3ms | in <the>/ it
- 21 | פְרִי\־ | fe.ri- | H6529 | HNcmsc | [is the] fruit of
- 22 | עֵ֖ץ | 'etz | H6086H | HNcmsa | a tree
- 23 | זֹרֵ֣עַ | zo.Re.a' | H2232 | HVqrmsa | [which] bears seed
- 24 | זָ֑רַע | Za.ra' | H2233G | HNcmsa | seed
- 25 | לָ/כֶ֥ם | la./Khem | H9005 | HRd/Sp2mp | to <the>/ you
- 26 | יִֽהְיֶ֖ה | yih.Yeh | H1961 | HVqi3ms | <it> will be[long]
- 27 | לְ/אָכְלָֽה\׃ | le./'okh.Lah | H402 | HR/Ncfsa | to/ food
#### Gen 1:30
- 1 | וּֽ/לְ/כָל\־ | u./le./khol- | H3605 | HC/R/Ncmsc | and/ to/ every
- 2 | חַיַּ֣ת | chai.Yat | H2416C | HNcfsc | <the> animal of
- 3 | הָ֠/אָרֶץ | Ha./'a.retz | H776H | HTd/Ncfsa | the/ earth
- 4 | וּ/לְ/כָל\־ | u./le./khol- | H3605 | HC/R/Ncmsc | and/ to/ every
- 5 | ע֨וֹף | of | H5775 | HNcmsc | <the> bird of
- 6 | הַ/שָּׁמַ֜יִם | ha./sha.Ma.yim | H8064 | HTd/Ncmpa | the/ heavens
- 7 | וּ/לְ/כֹ֣ל\׀ | u./le./Khol | H3605 | HC/R/Ncmsc | and/ to/ every
- 8 | רוֹמֵ֣שׂ | ro.Mes | H7430 | HVqrmsa | creeping [thing]
- 9 | עַל\־ | 'al- | H5921A | HR | on
- 10 | הָ/אָ֗רֶץ | ha./'A.retz | H776H | HTd/Ncfsa | the/ earth
- 11 | אֲשֶׁר\־ | 'a.Sher- | H834A | HTr | which
- 12 | בּ/וֹ֙ | b/o | H9003 | HRd/Sp3ms | [is] in <the>/ it
- 13 | נֶ֣פֶשׁ | Ne.fesh | H5315H | HNcfsa | life
- 14 | חַיָּ֔ה | chai.Yah | H2416A | HAafsa | living
- 15 | אֶת\־ | 'et- | H853 | HTo | <obj.>
- 16 | כָּל\־ | kol- | H3605 | HNcmsc | all
- 17 | יֶ֥רֶק | Ye.rek | H3418 | HNcmsc | greenery of
- 18 | עֵ֖שֶׂב | 'E.sev | H6212 | HNcmsa | plant[s]
- 19 | לְ/אָכְלָ֑ה | le./'okh.Lah | H402 | HR/Ncfsa | to/ food
- 20 | וַֽ/יְהִי\־ | va/y.hi- | H1961 | Hc/Vqw3ms | and/ it was
- 21 | כֵֽן\׃ | Khen | H3651C | HD | so
#### Gen 1:31
- 1 | וַ/יַּ֤רְא | va/i.Yar' | H7200G | Hc/Vqw3ms | and/ he saw
- 2 | אֱלֹהִים֙ | 'E.lo.Him | H430G | HNcmpa | God
- 3 | אֶת\־ | 'et- | H853 | HTo | <obj.>
- 4 | כָּל\־ | kol- | H3605 | HNcmsa | all
- 5 | אֲשֶׁ֣ר | 'a.Sher | H834A | HTr | that
- 6 | עָשָׂ֔ה | 'a.Sah | H6213H | HVqp3ms | he had made
- 7 | וְ/הִנֵּה\־ | ve./hi.neh- | H2009 | HC/Tj | and/ there!
- 8 | ט֖וֹב | Tov | H2896A | HAamsa | [it was] good
- 9 | מְאֹ֑ד | me.'Od | H3966 | HAcmsa | very
- 10 | וַֽ/יְהִי\־ | va/y.hi- | H1961 | Hc/Vqw3ms | and/ there was
- 11 | עֶ֥רֶב | 'E.rev | H6153 | HNcmsa | evening
- 12 | וַֽ/יְהִי\־ | va/y.hi- | H1961 | Hc/Vqw3ms | and/ there was
- 13 | בֹ֖קֶר | Vo.ker | H1242 | HNcmsa | morning
- 14 | י֥וֹם | Yom | H3117G | HNcmsc | [the] day
- 15 | הַ/שִּׁשִּֽׁי\׃\ \פ | ha./shi.Shi | H8345 | HTd/Aomsa | <the>/ sixth

### Lexicon（依 exact Extended Strong 去重）
- H7225G | רֵאשִׁית (re.shit): first: beginning
- H1254A | בָּרָא (ba.ra): to create
- H430G | אֱלֹהִים (e.lo.him): God
- H853 | אֵת (et): [Obj.]
- H8064 | שָׁמַיִם (sha.ma.yim): heaven
- H776G | אֶ֫רֶץ (e.rets): land: country/planet
- H1961 | הָיָה (ha.yah): to be
- H8414 | תֹּ֫הוּ (to.hu): formlessness
- H922 | בֹּהוּ (bo.hu): void
- H2822 | חֹ֫שֶׁךְ (cho.shekh): darkness
- H5921A | עַל (al): upon
- H6440J | פָּנֶה (pa.neh): face: surface
- H8415 | תְּהוֹם (te.hom): abyss
- H7307G | רוּחַ (ru.ach): spirit
- H7363B | רָחַף (ra.chaph): to hover
- H4325G | מַי (ma.yim): water
- H559 | אָמַר (a.mar): to say
- H216 | אוֹר (or): light
- H7200G | רָאָה (ra.ah): to see: see
- H3588A | כִּי (ki): for
- H2895 | טוֹב (tov): be pleasing
- H914 | בָּדַל (ba.dal): to separate
- H996G | בַּ֫יִן (ba.yin): between
- H7121H | קָרָא (qa.ra): to call: call by
- H3117G | יוֹם (yom): day
- H3915 | לַ֫יְלָה (lay.lah): night
- H6153 | עֶ֫רֶב (e.rev): evening
- H1242 | בֹּ֫קֶר (bo.qer): morning
- H259 | אֶחָד (e.chad): one
- H7549 | רָקִיעַ (ra.qi.a): expanse
- H8432 | תָּ֫וֶךְ (ta.vekh): midst
- H6213H | עָשָׂה (a.sah): to make
- H834A | אֲשֶׁר (a.sher): which
- H8478G | תַּחַת (ta.chat): underneath: under
- H3651C | כֵּן (ken): so
- H8145 | שֵׁנִי (she.ni): second
- H6960B | קָוָה (qa.vah): to collect
- H413 | אֶל (el): to(wards)
- H4725 | מָקוֹם (ma.qom): place
- H3004 | יַבָּשָׁה (yab.ba.shah): dry land
- H4723C | מִקְוֶה (miq.veh): collection
- H3220G | יָם (yam): sea
- H1876 | דָּשָׁא (da.sah): to sprout
- H1877 | דֶּ֫שֶׁא (de.she): grass
- H6212 | עֵ֫שֶׂב (e.sev): vegetation
- H2232 | זָרַע (za.ra): to sow
- H2233G | זֶ֫רַע (ze.ra): seed
- H6086H | עֵץ (ets): tree
- H6529 | פְּרִי (pe.ri): fruit
- H4327 | מִין (min): kind
- H9003 | /ב (b): in/on/with
- H3318M | יָצָא (ya.tsa): to come out: produce
- H7992 | שְׁלִישִׁי (she.li.shi): third
- H3974 | מָאוֹר (ma.or): light
- H226H | אוֹת (ot): sign: indicator
- H4150G | מוֹעֵד (mo.ed): meeting: time appointed
- H8141 | שָׁנָה (sha.neh): year
- H215 | אוֹר (or): to light
- H8147 | שְׁנַ֫יִם (she.na.yim): two
- H1419A | גָּדוֹל (ga.dol): great: large
- H4475 | מֶמְשָׁלָה (mem.sha.lah): dominion
- H6996B | קָטֹן (qa.ton): small
- H3556 | כּוֹכָב (ko.khav): star
- H5414H | נָתַן (na.tan): to give: put
- H4910 | מָשַׁל (ma.shal): to rule
- H7243 | רְבִיעִי (re.vi.i): fourth
- H8317 | שָׁרַץ (sha.rats): to swarm
- H8318 | שֶׁ֫רֶץ (she.rets): swarm
- H5315K | נֶ֫פֶשׁ (ne.phesh): soul: animal
- H2416A | חַי (chay): alive
- H5775 | עוֹף (oph): bird
- H5774A | עוּף (uph): to fly
- H8577N | תַּנִּין (tan.nin): serpent: monster
- H3605 | כֹּל (kol): all
- H7430 | רָמַשׂ (ra.ma.s): to creep
- H3671 | כָּנָף (ka.naph): wing
- H1288 | בָּרַךְ (ba.rakh): to bless
- H6509 | פָּרָה (pa.rah): be fruitful
- H7235A | רָבָה (ra.vah): to multiply
- H4390 | מָלֵא (ma.le): to fill
- H2549 | חֲמִישִׁי (cha.mi.shi): fifth
- H776H | אֶ֫רֶץ (e.rets): land: soil
- H929 | בְּהֵמָה (be.he.mah): animal
- H7431 | רֶ֫מֶשׂ (re.me.s): creeping
- H2416C | חַיָּה (chay.yah): living thing
- H127G | אֲדָמָה (a.da.mah): land: soil
- H120G | אָדָם (a.dam): man
- H6754 | צֶ֫לֶם (tse.lem): image
- H1823 | דְּמוּת (de.mut): likeness
- H7287A | רָדָה (ra.dah): to rule
- H1710 | דָּגָה (da.gah): fish
- H2145 | זָכָר (za.khar): male
- H5347 | נְקֵבָה (ne.qe.vah): female
- H9005 | /ל (l): to/for
- H3533 | כָּבַשׁ (ka.vash): to subdue
- H2009 | הִנֵּה (hin.neh): behold
- H5414G | נָתַן (na.tan): to give: give
- H402 | אׇכְלָה (okh.lah): food
- H5315H | נֶ֫פֶשׁ (ne.phesh): soul: life
- H3418 | יֶ֫רֶק (ye.req): green
- H2896A | טוֹב (tov): pleasant
- H3966 | מְאֹד (me.od): much
- H8345 | שִׁשִּׁי (shish.shi): sixth


【STEP 原文資料使用邊界】
- STEP Bible 是原文證據層，不是第五套 commentary：可直接支持本章詞形、lemma、Strong 編號、morphology、context gloss 與 lexicon 義域等語言事實；不得把它算成CT／GT／KC／BH 的註釋共識票。
- Lexicon 是可能義域，不等於本節必然語境義；morphology 是語法形態，不會自行推出神學結論。語言事實與註釋家的解讀必須分開表述，神學判斷仍須由經文脈絡或註釋來源支持。
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
- 全文合計 ≥1240 字，其中散文敘述至少 620 字——沿經文脈絡整合各來源觀點的連貫敘述是主幹，表格、清單、callout 都是它的補充，不可把大半內容包進表格或 callout。
- 這是 Obsidian 筆記庫：行文首次提到本章條目時用 wiki-link 連結，用詞不同寫 [[完整條目名|行文用詞]]，之後再提不必重連；至少要有一個連結，且目標只能取自本章可連條目：創造（從無到有）、神的靈的角色、神的話（創造媒介）、三位一體在創造中的隱現、形像與樣式、人的尊嚴與神的形像、光與黑暗的分別、人、空虛混沌的原意、六日復造的結構、光體作記號定節令、創造日長度問題、創世記1章第1-2節間隔問題、各從其類、治理與管理、神命名與主權、生養眾多與治理、神看為好（甚好）、原初素食與受造界和平、六日創造與信徒重生經歷、詩篇33篇神話語創造、約翰福音1章道與創造、詩篇8篇人的治理權柄、創世記9章洪水後准吃肉、與古代近東創世神話的對比、穹蒼（raqia）——不可連清單外的目標；清單裡沒有對應條目的概念（vault 裡存在與否都一樣），直接用純文字提及即可，不要加 [[ ]]。
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
chapter: 1
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