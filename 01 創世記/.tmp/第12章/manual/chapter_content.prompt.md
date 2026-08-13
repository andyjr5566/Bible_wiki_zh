你是聖經研經資料整理員。唯一任務：為 創世記 第12章填寫 chapter_content payload（本章知識節點 + 本章整理）。

【經文】
1. 耶和華對亞伯蘭說：你要離開本地、本族、父家，往我所要指示你的地去。
2. 我必叫你成為大國。我必賜福給你，叫你的名為大；你也要叫別人得福。
3. 為你祝福的，我必賜福與他；那咒詛你的，我必咒詛他。地上的萬族都要因你得福。
4. 亞伯蘭就照著耶和華的吩咐去了；羅得也和他同去。亞伯蘭出哈蘭的時候年七十五歲。
5. 亞伯蘭將他妻子撒萊和姪兒羅得，連他們在哈蘭所積蓄的財物、所得的人口，都帶往迦南地去。他們就到了迦南地。
6. 亞伯蘭經過那地，到了示劍地方、摩利橡樹那裡。那時迦南人住在那地。
7. 耶和華向亞伯蘭顯現，說：我要把這地賜給你的後裔。亞伯蘭就在那裡為向他顯現的耶和華築了一座壇。
8. 從那裡他又遷到伯特利東邊的山，支搭帳棚；西邊是伯特利，東邊是艾。他在那裡又為耶和華築了一座壇，求告耶和華的名。
9. 後來亞伯蘭又漸漸遷往南地去。
10. 那地遭遇饑荒。因饑荒甚大，亞伯蘭就下埃及去，要在那裡暫居。
11. 將近埃及，就對他妻子撒萊說：我知道你是容貌俊美的婦人。
12. 埃及人看見你必說：這是他的妻子，他們就要殺我，卻叫你存活。
13. 求你說，你是我的妹子，使我因你得平安，我的命也因你存活。
14. 及至亞伯蘭到了埃及，埃及人看見那婦人極其美貌。
15. 法老的臣宰看見了他，就在法老面前誇獎他。那婦人就被帶進法老的宮去。
16. 法老因這婦人就厚待亞伯蘭，亞伯蘭得了許多牛、羊、駱駝、公驢、母驢、僕婢。
17. 耶和華因亞伯蘭妻子撒萊的緣故，降大災與法老和他的全家。
18. 法老就召了亞伯蘭來，說：你這向我做的是什麼事呢？為什麼沒有告訴我他是你的妻子？
19. 為什麼說他是你的妹子，以致我把他取來要作我的妻子？現在你的妻子在這裡，可以帶他走吧。
20. 於是法老吩咐人將亞伯蘭和他妻子，並他所有的都送走了。

【本章來源 context】
## 本章 Commentary Sources

你已依 manual/sources.md 全文閱讀以下正式 commentary；本 prompt 不重複內嵌原文全文。
- 研經註解（BibleHub Study）
  path: raw_data/biblehub_study_genesis_12.txt
  URL: https://biblehub.com/study/genesis/12.htm
- 研經註解（KingComments）
  path: raw_data/kingcomments_genesis_12.txt
  URL: https://www.kingcomments.com/en/bible-studies/Gen/12
- 逐節註解（ccbiblestudy CT）
  path: raw_data/ccbiblestudy_CT_genesis_12.txt
  URL: https://www.ccbiblestudy.org/Old%20Testament/01Gen/01CT12.htm
- 拾穗（ccbiblestudy GT）
  path: raw_data/ccbiblestudy_GT_genesis_12.txt
  URL: https://www.ccbiblestudy.org/Old%20Testament/01Gen/01GT12.htm

所有 commentary 敘述仍必須忠於上述已全文閱讀來源；不得以摘要或關鍵字 grep 取代全文閱讀。


## STEP Bible task projection
- source: stepbible_genesis_12.txt
- reference: Genesis 12
- selected verses: 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20
- boundary: lexicon 是可能義域，不等於本節語境義；morphology 不自行證明神學結論。

### Occurrences
format: position | original | transliteration | exact Extended Strong | morphology code | context gloss
#### Gen 12:1
- 1 | וַ/יֹּ֤אמֶר | va/i.Yo.mer | H559 | Hc/Vqw3ms | and/ he said
- 2 | יְהוָה֙ | Yah.weh | H3068G | HNpt | Yahweh
- 3 | אֶל\־ | 'el- | H413 | HR | to
- 4 | אַבְרָ֔ם | 'av.Ram | H87 | HNpm | Abram
- 5 | לֶךְ\־ | lekh- | H1980G | HVqv2ms | go
- 6 | לְ/ךָ֛ | le./Kha | H9005 | HRd/Sp2ms | for <the>/ yourself
- 7 | מֵ/אַרְצְ/ךָ֥ | me./'ar.tze./Kha | H776G | HR/Ncfsc/Sp2ms | from/ land/ your
- 8 | וּ/מִ/מּֽוֹלַדְתְּ/ךָ֖ | u./mi./mo.lad.te./Kha | H4138 | HC/R/Ncfsc/Sp2ms | and/ from/ kindred/ your
- 9 | וּ/מִ/בֵּ֣ית | u./mi./Beit | H1004M | HC/R/Ncmsc | and/ from/ [the] household of
- 10 | אָבִ֑י/ךָ | 'a.Vi./kha | H1G | HNcmsc/Sp2ms | father/ your
- 11 | אֶל\־ | 'el- | H413 | HR | to
- 12 | הָ/אָ֖רֶץ | ha./'A.retz | H776G | HTd/Ncfsa | the/ land
- 13 | אֲשֶׁ֥ר | 'a.Sher | H834A | HTr | which
- 14 | אַרְאֶֽ/ךָּ\׃ | 'ar.'E./ka | H7200G | HVhi1cs/Sp2ms | I will show/ you
#### Gen 12:2
- 1 | וְ/אֶֽעֶשְׂ/ךָ֙ | ve./'e.'es./Kha | H6213H | HC/Vqu1cs/Sp2ms | so/ I may make/ you
- 2 | לְ/ג֣וֹי | le./Goy | H1471A | HR/Ncmsa | into/ a nation
- 3 | גָּד֔וֹל | ga.Dol | H1419A | HAamsa | great
- 4 | וַ/אֲבָ֣רֶכְ/ךָ֔ | va./'a.Va.rekh./kha | H1288 | HC/Vpu1cs/Sp2ms | and/ I will bless/ you
- 5 | וַ/אֲגַדְּלָ֖ה | va./'a.ga.de.Lah | H1431 | HC/Vpc1cs | and/ I will make great
- 6 | שְׁמֶ֑/ךָ | she.Me./kha | H8034 | HNcmsc/Sp2ms | name/ your
- 7 | וֶ/הְיֵ֖ה | ve/h.Yeh | H1961 | HC/Vqv2ms | and/ you be
- 8 | בְּרָכָֽה\׃ | be.ra.Khah | H1293 | HNcfsa | a blessing
#### Gen 12:3
- 1 | וַ/אֲבָֽרֲכָה֙ | va./'a.va.ra.Khah | H1288 | HC/Vpc1cs | so/ let me bless
- 2 | מְבָ֣רְכֶ֔י/ךָ | me.Va.re.Khei./kha | H1288 | HVprmpc/Sp2ms | [those who] bless/ you
- 3 | וּ/מְקַלֶּלְ/ךָ֖ | u./me.ka.lel./Cha | H7043 | HC/Vprmsc/Sp2ms | and/ [one who] disdains/ you
- 4 | אָאֹ֑ר | 'a.'Or | H779 | HVqi1cs | I will curse
- 5 | וְ/נִבְרְכ֣וּ | ve./niv.re.Khu | H1288 | Hc/VNq3cp | and/ they will be blessed
- 6 | בְ/ךָ֔ | ve./Kha | H9003 | HRd/Sp2ms | by <the>/ you
- 7 | כֹּ֖ל | kol | H3605 | HNcmsc | all
- 8 | מִשְׁפְּחֹ֥ת | mish.pe.Chot | H4940 | HNcfpc | [the] clans of
- 9 | הָ/אֲדָמָֽה\׃ | ha./'a.da.Mah | H127I | HTd/Ncfsa | the/ earth
#### Gen 12:4
- 1 | וַ/יֵּ֣לֶךְ | va/i.Ye.lekh | H1980G | Hc/Vqw3ms | and/ he went
- 2 | אַבְרָ֗ם | 'av.Ram | H87 | HNpm | Abram
- 3 | כַּ/אֲשֶׁ֨ר | ka./'a.Sher | H834D | HR/Tr | just/ as
- 4 | דִּבֶּ֤ר | di.Ber | H1696G | HVpp3ms | he had said
- 5 | אֵלָי/ו֙ | 'e.La/v | H413 | HRd/Sp3ms | to/ him
- 6 | יְהוָ֔ה | Yah.weh | H3068G | HNpt | Yahweh
- 7 | וַ/יֵּ֥לֶךְ | va/i.Ye.lekh | H1980G | Hc/Vqw3ms | and/ he went
- 8 | אִתּ֖/וֹ | 'i.T/o | H854 | HRd/Sp3ms | with/ him
- 9 | ל֑וֹט | Lot | H3876 | HNpm | Lot
- 10 | וְ/אַבְרָ֗ם | ve./'av.Ram | H87 | HC/Npm | and/ Abram
- 11 | בֶּן\־ | ben- | H1121L | HNcmsc | [was] a son of
- 12 | חָמֵ֤שׁ | cha.Mesh | H2568 | HAcbsa | five
- 13 | שָׁנִים֙ | sha.Nim | H8141 | HNcmpa | years
- 14 | וְ/שִׁבְעִ֣ים | ve./shiv.'Im | H7657 | HC/Acmpa | and/ seventy
- 15 | שָׁנָ֔ה | sha.Nah | H8141 | HNcfsa | year[s]
- 16 | בְּ/צֵאת֖/וֹ | be./tze.T/o | H3318G | HR/Vqcc/Sp3ms | when/ came out/ he
- 17 | מֵ/חָרָֽן\׃ | me./cha.Ran | H2771A | HR/Npl | from/ Haran
#### Gen 12:5
- 1 | וַ/יִּקַּ֣ח | va/i.yi.Kach | H3947G | Hc/Vqw3ms | and/ he took
- 2 | אַבְרָם֩ | 'av.Ram | H87 | HNpm | Abram
- 3 | אֶת\־ | 'et- | H853 | HTo | <obj.>
- 4 | שָׂרַ֨י | sa.Rai | H8297 | HNpf | Sarai
- 5 | אִשְׁתּ֜/וֹ | 'ish.T/o | H802H | HNcfsc/Sp3ms | wife/ his
- 6 | וְ/אֶת\־ | ve./'Et | H853 | HC/To | and/ <obj.>
- 7 | ל֣וֹט | Lot | H3876 | HNpm | Lot
- 8 | בֶּן\־ | ben- | H1121A | HNcmsc | [the] son of
- 9 | אָחִ֗י/ו | 'a.Chi/v | H251G | HNcmsc/Sp3ms | brother/ his
- 10 | וְ/אֶת\־ | ve./'Et | H853 | HC/To | and/ <obj.>
- 11 | כָּל\־ | kol- | H3605 | HNcmsc | all
- 12 | רְכוּשָׁ/ם֙ | re.khu.Sha/m | H7399 | HNcmsc/Sp3mp | possession[s]/ their
- 13 | אֲשֶׁ֣ר | 'a.Sher | H834A | HTr | which
- 14 | רָכָ֔שׁוּ | ra.Kha.shu | H7408 | HVqp3cp | they had accumulated
- 15 | וְ/אֶת\־ | ve./'Et | H853 | HC/To | and/ <obj.>
- 16 | הַ/נֶּ֖פֶשׁ | ha./Ne.fesh | H5315J | HTd/Ncfsa | the/ person[s]
- 17 | אֲשֶׁר\־ | 'a.Sher- | H834A | HTr | whom
- 18 | עָשׂ֣וּ | 'a.Su | H6213I | HVqp3cp | they had acquired
- 19 | בְ/חָרָ֑ן | ve./cha.Ran | H2771A | HR/Npl | in/ Haran
- 20 | וַ/יֵּצְא֗וּ | va/i.ye.tze.'U | H3318G | Hc/Vqw3mp | and/ they went out
- 21 | לָ/לֶ֙כֶת֙ | la./Le.khet | H1980G | HR/Vqcc | to/ go
- 22 | אַ֣רְצָ/ה | 'Ar.tza/h | H776G | HNcfsc/Sd | [the] land of/ towards
- 23 | כְּנַ֔עַן | ke.Na.'an | H3667A | HNpl | Canaan
- 24 | וַ/יָּבֹ֖אוּ | va/i.ya.Vo.'u | H935G | Hc/Vqw3mp | and/ they came
- 25 | אַ֥רְצָ/ה | 'Ar.tza/h | H776G | HNcfsc/Sd | [the] land of/ towards
- 26 | כְּנָֽעַן\׃ | ke.Na.'an | H3667A | HNpl | Canaan
#### Gen 12:6
- 1 | וַ/יַּעֲבֹ֤ר | va/i.ya.'a.Vor | H5674A | Hc/Vqw3ms | and/ he passed
- 2 | אַבְרָם֙ | 'av.Ram | H87 | HNpm | Abram
- 3 | בָּ/אָ֔רֶץ | ba./'A.retz | H776G | HRd/Ncfsa | in the/ land
- 4 | עַ֚ד | 'ad | H5704 | HR | to
- 5 | מְק֣וֹם | me.Kom | H4725 | HNcmsc | [the] place of
- 6 | שְׁכֶ֔ם | she.Khem | H7927G | HNpl | Shechem
- 7 | עַ֖ד | 'ad | H5704 | HR | to
- 8 | אֵל֣וֹן | 'e.Lon | H436H | HNcmsc | [the] great tree of
- 9 | מוֹרֶ֑ה | mo.Reh | H4176G | HNpl | Moreh
- 10 | וְ/הַֽ/כְּנַעֲנִ֖י | ve./ha./ke.na.'a.Ni | H3669A | HC/Td/Ngmsa | and/ the/ Canaanite[s]
- 11 | אָ֥ז | 'az | H227A | HD | then
- 12 | בָּ/אָֽרֶץ\׃ | ba./'A.retz | H776G | HRd/Ncfsa | [was] in the/ land
#### Gen 12:7
- 1 | וַ/יֵּרָ֤א | va/i.ye.Ra' | H7200G | Hc/VNw3ms | and/ he appeared
- 2 | יְהוָה֙ | Yah.weh | H3068G | HNpt | Yahweh
- 3 | אֶל\־ | 'el- | H413 | HR | to
- 4 | אַבְרָ֔ם | 'av.Ram | H87 | HNpm | Abram
- 5 | וַ/יֹּ֕אמֶר | va/i.Yo.mer | H559 | Hc/Vqw3ms | and/ he said
- 6 | לְ/זַ֨רְעֲ/ךָ֔ | le./Zar.'a./kha | H2233H | HR/Ncmsc/Sp2ms | to/ offspring/ your
- 7 | אֶתֵּ֖ן | 'e.Ten | H5414G | HVqi1cs | I will give
- 8 | אֶת\־ | 'et- | H853 | HTo | <obj.>
- 9 | הָ/אָ֣רֶץ | ha./'A.retz | H776G | HTd/Ncfsa | the/ land
- 10 | הַ/זֹּ֑את | ha./Zot | H2063 | HTd/Tm | <the>/ this
- 11 | וַ/יִּ֤בֶן | va/i.Yi.ven | H1129 | Hc/Vqw3ms | and/ he built
- 12 | שָׁם֙ | sham | H8033G | HD | there
- 13 | מִזְבֵּ֔חַ | miz.Be.ach | H4196 | HNcmsa | an altar
- 14 | לַ/יהוָ֖ה | la./Yah.weh | H3068G | HR/Npt | to/ Yahweh
- 15 | הַ/נִּרְאֶ֥ה | ha./nir.'Eh | H7200G | HTd/VNrmsa | who/ had appeared
- 16 | אֵלָֽי/ו\׃ | 'e.La/v | H413 | HRd/Sp3ms | to/ him
#### Gen 12:8
- 1 | וַ/יַּעְתֵּ֨ק | va/i.ya'.Tek | H6275 | Hc/Vhw3ms | and/ he moved on
- 2 | מִ/שָּׁ֜ם | mi./Sham | H8033G | HR/D | from/ there
- 3 | הָ/הָ֗רָ/ה | ha./Ha.ra/h | H2022H | HTd/Ncmsa/Sd | the/ hill country/ towards
- 4 | מִ/קֶּ֛דֶם | mi./Ke.dem | H6924G | HR/Ncmsa | from/ [the] east
- 5 | לְ/בֵֽית\־ | le./veit- | H1008G | HR/Npl | of/ Beth-
- 6 | אֵ֖ל | 'el | H1008G | HNpl | -el
- 7 | וַ/יֵּ֣ט | va/i.Yet | H5186 | Hc/Vqw3ms | and/ he pitched
- 8 | אָהְָל֑/וֹ | 'o.ho.L/o | H168G | HNcmsc/Sp3ms | tent/ his
- 9 | בֵּֽית\־ | beit- | H1008G | HNpl | Beth-
- 10 | אֵ֤ל | 'el | H1008G | HNpl | -el
- 11 | מִ/יָּם֙ | mi./Yam | H3220H | HR/Ncmsa | [was] from/ [the] west
- 12 | וְ/הָ/עַ֣י | ve./ha./'Ai | H5857G | HC/Td/Npl | and/ <the>/ Ai
- 13 | מִ/קֶּ֔דֶם | mi./Ke.dem | H6924G | HR/Ncmsa | [was] from/ [the] east
- 14 | וַ/יִּֽבֶן\־ | va/i.yi.ven- | H1129 | Hc/Vqw3ms | and/ he built
- 15 | שָׁ֤ם | sham | H8033G | HD | there
- 16 | מִזְבֵּ֙חַ֙ | miz.Be.ach | H4196 | HNcmsa | an altar
- 17 | לַֽ/יהוָ֔ה | la./Yah.weh | H3068G | HR/Npt | to/ Yahweh
- 18 | וַ/יִּקְרָ֖א | va/i.yik.Ra' | H7121G | Hc/Vqw3ms | and/ he called
- 19 | בְּ/שֵׁ֥ם | be./Shem | H8034 | HR/Ncmsc | on/ [the] name of
- 20 | יְהוָֽה\׃ | Yah.weh | H3068G | HNpt | Yahweh
#### Gen 12:9
- 1 | וַ/יִּסַּ֣ע | va/i.yi.Sa' | H5265 | Hc/Vqw3ms | and/ he journeyed
- 2 | אַבְרָ֔ם | 'av.Ram | H87 | HNpm | Abram
- 3 | הָל֥וֹךְ | ha.Lokh | H1980L | HVqaa | going
- 4 | וְ/נָס֖וֹעַ | ve./na.So.a' | H5265 | HC/Vqaa | and/ journeying
- 5 | הַ/נֶּֽגְבָּ/ה\׃\ \פ | ha./Neg.ba/h | H5045G | HTd/Npl/Sd | the/ south/ towards
#### Gen 12:10
- 1 | וַ/יְהִ֥י | va/y.Hi | H1961 | Hc/Vqw3ms | and/ it was
- 2 | רָעָ֖ב | ra.'Av | H7458 | HNcmsa | a famine
- 3 | בָּ/אָ֑רֶץ | ba./'A.retz | H776G | HRd/Ncfsa | in the/ land
- 4 | וַ/יֵּ֨רֶד | va/i.Ye.red | H3381 | Hc/Vqw3ms | and/ he went down
- 5 | אַבְרָ֤ם | 'av.Ram | H87 | HNpm | Abram
- 6 | מִצְרַ֙יְמָ/ה֙ | mitz.Ray.ma/h | H4714G | HNpl/Sd | Egypt/ towards
- 7 | לָ/ג֣וּר | la./Gur | H1481A | HR/Vqcc | to/ sojourn
- 8 | שָׁ֔ם | Sham | H8033G | HD | there
- 9 | כִּֽי\־ | ki- | H3588A | HTc | for
- 10 | כָבֵ֥ד | kha.Ved | H3515 | HAamsa | [was] heavy
- 11 | הָ/רָעָ֖ב | ha./ra.'Av | H7458 | HTd/Ncmsa | the/ famine
- 12 | בָּ/אָֽרֶץ\׃ | ba./'A.retz | H776G | HRd/Ncfsa | in the/ land
#### Gen 12:11
- 1 | וַ/יְהִ֕י | va/y.Hi | H1961 | Hc/Vqw3ms | and/ it was
- 2 | כַּ/אֲשֶׁ֥ר | ka./'a.Sher | H834D | HR/Tr | just/ as
- 3 | הִקְרִ֖יב | hik.Riv | H7126G | HVhp3ms | he drew near
- 4 | לָ/ב֣וֹא | la./Vo' | H935G | HR/Vqcc | to/ enter
- 5 | מִצְרָ֑יְמָ/ה | mitz.Ra.ye.ma/h | H4714G | HNpl/Sd | Egypt/ <towards>
- 6 | וַ/יֹּ֙אמֶר֙ | va/i.Yo.mer | H559 | Hc/Vqw3ms | and/ he said
- 7 | אֶל\־ | 'el- | H413 | HR | to
- 8 | שָׂרַ֣י | sa.Rai | H8297 | HNpf | Sarai
- 9 | אִשְׁתּ֔/וֹ | 'ish.T/o | H802H | HNcfsc/Sp3ms | wife/ his
- 10 | הִנֵּה\־ | hi.neh- | H2009 | HTj | here!
- 11 | נָ֣א | na' | H4994 | HTj | please
- 12 | יָדַ֔עְתִּי | ya.Da'.ti | H3045 | HVqp1cs | I know
- 13 | כִּ֛י | ki | H3588A | HTc | that
- 14 | אִשָּׁ֥ה | 'i.Shah | H802G | HNcfsa | [are] a woman
- 15 | יְפַת\־ | ye.fat- | H3303 | HAafsc | beautiful of
- 16 | מַרְאֶ֖ה | mar.'Eh | H4758 | HNcmsa | appearance
- 17 | אָֽתְּ\׃ | 'At | H859C | HPp2fs | you
#### Gen 12:12
- 1 | וְ/הָיָ֗ה | ve./ha.Yah | H1961 | Hc/Vqq3ms | and/ it will be
- 2 | כִּֽי\־ | ki- | H3588A | HTc | that
- 3 | יִרְא֤וּ | yir.'U | H7200G | HVqi3mp | they will see
- 4 | אֹתָ/ךְ֙ | 'o.to/Kh | H853 | HTo/Sp2fs | <obj.>/ you
- 5 | הַ/מִּצְרִ֔ים | ha./mitz.Rim | H4713 | HTd/Ngmpa | the/ Egyptians
- 6 | וְ/אָמְר֖וּ | ve./'a.me.Ru | H559 | Hc/Vqq3cp | and/ they will say
- 7 | אִשְׁתּ֣/וֹ | 'ish.T/o | H802H | HNcfsc/Sp3ms | [is] wife/ his
- 8 | זֹ֑את | Zot | H2063 | HTm | this
- 9 | וְ/הָרְג֥וּ | ve./ha.re.Gu | H2026 | Hc/Vqq3cp | and/ they will kill
- 10 | אֹתִ֖/י | 'o.T/i | H853 | HTo/Sp1bs | <obj.>/ me
- 11 | וְ/אֹתָ֥/ךְ | ve./'o.Ta/kh | H853 | HC/To/Sp2fs | and/ <obj.>/ you
- 12 | יְחַיּֽוּ\׃ | ye.chai.Yu | H2421 | HVpi3mp | they will let live
#### Gen 12:13
- 1 | אִמְרִי\־ | 'im.ri- | H559 | HVqv2fs | say
- 2 | נָ֖א | na' | H4994 | HTj | please
- 3 | אֲחֹ֣תִ/י | 'a.Cho.t/i | H269 | HNcfsc/Sp1bs | [are] sister/ my
- 4 | אָ֑תְּ | 'At | H859C | HPp2fs | you
- 5 | לְמַ֙עַן֙ | le.Ma.'an | H4616 | HTc | so that
- 6 | יִֽיטַב\־ | yi.tav- | H3190 | HVqj3ms | it may go well
- 7 | לִ֣/י | l/i | H9005 | HRd/Sp1bs | for <the>/ me
- 8 | בַ/עֲבוּרֵ֔/ךְ | va./'a.vu.Re/kh | H5668 | HR/Ncmsc/Sp2fs | for/ sake of/ you
- 9 | וְ/חָיְתָ֥ה | ve./cha.ye.Tah | H2421 | Hc/Vqq3fs | and/ it will live
- 10 | נַפְשִׁ֖/י | naf.Sh/i | H5315H | HNcfsc/Sp1bs | life/ my
- 11 | בִּ/גְלָלֵֽ/ךְ\׃ | bi/g.la.Le/kh | H1558 | HR/Ncmsc/Sp2fs | on/ account of/ you
#### Gen 12:14
- 1 | וַ/יְהִ֕י | va/y.Hi | H1961 | Hc/Vqw3ms | and/ it was
- 2 | כְּ/ב֥וֹא | ke./Vo' | H935G | HR/Vqcc | when/ entered
- 3 | אַבְרָ֖ם | 'av.Ram | H87 | HNpm | Abram
- 4 | מִצְרָ֑יְמָ/ה | mitz.Ra.ye.ma/h | H4714G | HNpl/Sd | Egypt/ <towards>
- 5 | וַ/יִּרְא֤וּ | va/i.yir.'U | H7200G | Hc/Vqw3mp | and/ they saw
- 6 | הַ/מִּצְרִים֙ | ha./mitz.Rim | H4713 | HTd/Ngmpa | the/ Egyptians
- 7 | אֶת\־ | 'et- | H853 | HTo | <obj.>
- 8 | הָ֣/אִשָּׁ֔ה | ha./'i.Shah | H802G | HTd/Ncfsa | the/ woman
- 9 | כִּֽי\־ | ki- | H3588A | HTc | that
- 10 | יָפָ֥ה | ya.Fah | H3303 | HAafsa | [was] beautiful
- 11 | הִ֖וא | hi' | H1931 | HPp3fs | she
- 12 | מְאֹֽד\׃ | me.'Od | H3966 | HAcmsa | very
#### Gen 12:15
- 1 | וַ/יִּרְא֤וּ | va/i.yir.'U | H7200G | Hc/Vqw3mp | and/ they saw
- 2 | אֹתָ/הּ֙ | 'o.Ta/h | H853 | HTo/Sp3fs | <obj.>/ her
- 3 | שָׂרֵ֣י | sa.Rei | H8269 | HNcmpc | [the] officials of
- 4 | פַרְעֹ֔ה | far.'Oh | H6547G | HNtmsa | Pharaoh
- 5 | וַ/יְהַֽלְל֥וּ | va/y.ha.Lu | H1984B | Hc/Vpw3mp | and/ they praised
- 6 | אֹתָ֖/הּ | 'o.Ta/h | H853 | HTo/Sp3fs | <obj.>/ her
- 7 | אֶל\־ | 'el- | H413 | HR | to
- 8 | פַּרְעֹ֑ה | par.'Oh | H6547G | HNtmsa | Pharaoh
- 9 | וַ/תֻּקַּ֥ח | va./tu.Kach | H3947G | Hc/VHw3fs | and/ she was taken
- 10 | הָ/אִשָּׁ֖ה | ha./'i.Shah | H802G | HTd/Ncfsa | the/ woman
- 11 | בֵּ֥ית | beit | H1004M | HNcmsc | [the] house of
- 12 | פַּרְעֹֽה\׃ | par.'Oh | H6547G | HNtmsa | Pharaoh
#### Gen 12:16
- 1 | וּ/לְ/אַבְרָ֥ם | u/l./'av.Ram | H87 | HC/R/Npm | and/ to/ Abram
- 2 | הֵיטִ֖יב | hei.Tiv | H3190 | HVhp3ms | he did good
- 3 | בַּ/עֲבוּרָ֑/הּ | ba./'a.vu.Ra/h | H5668 | HR/Ncmsc/Sp3fs | for/ sake of/ her
- 4 | וַֽ/יְהִי\־ | va/y.hi- | H1961 | Hc/Vqw3ms | and/ it be[longed]
- 5 | ל֤/וֹ | l/o | H9005 | HRd/Sp3ms | to <the>/ him
- 6 | צֹאן\־ | tzon- | H6629G | HNcbsa | sheep
- 7 | וּ/בָקָר֙ | u./va.Kar | H1241 | HC/Ncbsa | and/ cattle
- 8 | וַ/חֲמֹרִ֔ים | va./cha.mo.Rim | H2543 | HC/Ncbpa | and/ [male] donkeys
- 9 | וַ/עֲבָדִים֙ | va./'a.va.Dim | H5650 | HC/Ncmpa | and/ [male] servants
- 10 | וּ/שְׁפָחֹ֔ת | u./she.fa.Chot | H8198 | HC/Ncfpa | and/ female servants
- 11 | וַ/אֲתֹנֹ֖ת | va./'a.to.Not | H860 | HC/Ncfpa | and/ female donkeys
- 12 | וּ/גְמַלִּֽים\׃ | u./ge.ma.Lim | H1581 | HC/Ncbpa | and/ camels
#### Gen 12:17
- 1 | וַ/יְנַגַּ֨ע | va/y.na.Ga' | H5060 | Hc/Vpw3ms | and/ he struck
- 2 | יְהוָ֧ה\׀ | Yah.weh | H3068G | HNpt | Yahweh
- 3 | אֶת\־ | 'et- | H853 | HTo | <obj.>
- 4 | פַּרְעֹ֛ה | par.'Oh | H6547G | HNtmsa | Pharaoh
- 5 | נְגָעִ֥ים | ne.ga.'Im | H5061 | HNcmpa | plagues
- 6 | גְּדֹלִ֖ים | ge.do.Lim | H1419A | HAampa | great
- 7 | וְ/אֶת\־ | ve./'Et | H853 | HC/To | and/ <obj.>
- 8 | בֵּית֑/וֹ | bei.T/o | H1004M | HNcmsc/Sp3ms | house/ his
- 9 | עַל\־ | 'al- | H5921A | HR | on
- 10 | דְּבַ֥ר | de.Var | H1697M | HNcmsc | [the] matter of
- 11 | שָׂרַ֖י | sa.Rai | H8297 | HNpf | Sarai
- 12 | אֵ֥שֶׁת | 'E.shet | H802H | HNcfsc | [the] wife of
- 13 | אַבְרָֽם\׃ | 'av.Ram | H87 | HNpm | Abram
#### Gen 12:18
- 1 | וַ/יִּקְרָ֤א | va/i.yik.Ra' | H7121G | Hc/Vqw3ms | and/ he summoned
- 2 | פַרְעֹה֙ | far.'Oh | H6547G | HNtmsa | Pharaoh
- 3 | לְ/אַבְרָ֔ם | le./'av.Ram | H87 | HR/Npm | <to>/ Abram
- 4 | וַ/יֹּ֕אמֶר | va/i.Yo.mer | H559 | Hc/Vqw3ms | and/ he said
- 5 | מַה\־ | mah- | H4100 | HPi | what?
- 6 | זֹּ֖את | zot | H2063 | HTm | this
- 7 | עָשִׂ֣יתָ | 'a.Si.ta | H6213A | HVqp2ms | have you done
- 8 | לִּ֑/י | L/i | H9005 | HRd/Sp1bs | to <the>/ me
- 9 | לָ֚/מָּה | La./mah | H4100 | HR/Pi | <to>/ why?
- 10 | לֹא\־ | lo'- | H3808 | HTn | not
- 11 | הִגַּ֣דְתָּ | hi.Gad.ta | H5046 | HVhp2ms | did you tell
- 12 | לִּ֔/י | L/i | H9005 | HRd/Sp1bs | to <the>/ me
- 13 | כִּ֥י | ki | H3588A | HTc | that
- 14 | אִשְׁתְּ/ךָ֖ | 'ish.te./Kha | H802H | HNcfsc/Sp2ms | [was] wife/ your
- 15 | הִֽוא\׃ | hi' | H1931 | HPp3fs | she
#### Gen 12:19
- 1 | לָ/מָ֤ה | la./Mah | H4100 | HR/Pi | <to>/ why?
- 2 | אָמַ֙רְתָּ֙ | 'a.Mar.ta | H559 | HVqp2ms | did you say
- 3 | אֲחֹ֣תִ/י | 'a.Cho.t/i | H269 | HNcfsc/Sp1bs | [is] sister/ my
- 4 | הִ֔וא | hi' | H1931 | HPp3fs | she
- 5 | וָ/אֶקַּ֥ח | va./'e.Kach | H3947G | Hc/Vqw1cs | and/ I took
- 6 | אֹתָ֛/הּ | 'o.Ta/h | H853 | HTo/Sp3fs | <obj.>/ her
- 7 | לִ֖/י | l/i | H9005 | HRd/Sp1bs | for <the>/ myself
- 8 | לְ/אִשָּׁ֑ה | le./'i.Shah | H802H | HR/Ncfsa | to/ a wife
- 9 | וְ/עַתָּ֕ה | ve./'a.Tah | H6258 | HC/D | and/ now
- 10 | הִנֵּ֥ה | hi.Neh | H2009 | HTj | here!
- 11 | אִשְׁתְּ/ךָ֖ | 'ish.te./Kha | H802H | HNcfsc/Sp2ms | wife/ your
- 12 | קַ֥ח | kach | H3947G | HVqv2ms | take [her]
- 13 | וָ/לֵֽךְ\׃ | va./Lekh | H1980G | HC/Vqv2ms | and/ go
#### Gen 12:20
- 1 | וַ/יְצַ֥ו | va/y.Tzav | H6680 | Hc/Vpw3ms | and/ he commanded
- 2 | עָלָ֛י/ו | 'a.La/v | H5921A | HRd/Sp3ms | on/ him
- 3 | פַּרְעֹ֖ה | par.'Oh | H6547G | HNtmsa | Pharaoh
- 4 | אֲנָשִׁ֑ים | 'a.na.Shim | H582 | HNcmpa | men
- 5 | וַֽ/יְשַׁלְּח֥וּ | va/y.sha.le.Chu | H7971G | Hc/Vpw3mp | and/ they sent away
- 6 | אֹת֛/וֹ | 'o.T/o | H853 | HTo/Sp3ms | <obj.>/ him
- 7 | וְ/אֶת\־ | ve./'Et | H853 | HC/To | and/ <obj.>
- 8 | אִשְׁתּ֖/וֹ | 'ish.T/o | H802H | HNcfsc/Sp3ms | wife/ his
- 9 | וְ/אֶת\־ | ve./'Et | H853 | HC/To | and/ <obj.>
- 10 | כָּל\־ | kol- | H3605 | HNcmsa | all
- 11 | אֲשֶׁר\־ | 'a.Sher- | H834A | HTr | that
- 12 | לֽ/וֹ\׃ | l/o | H9005 | HRd/Sp3ms | [belonged] to <the>/ him

### Lexicon（依 exact Extended Strong 去重）
- H559 | אָמַר (a.mar): to say
- H3068G | יְהֹוָה (ye.ho.vah): LORD
- H413 | אֶל (el): to(wards)
- H87 | אַבְרָם (av.ram): Abram
- H1980G | הָלַךְ (ha.lakh): to go: went
- H9005 | /ל (l): to/for
- H776G | אֶ֫רֶץ (e.rets): land: country/planet
- H4138 | מוֹלֶ֫דֶת (mo.le.det): relatives
- H1004M | בַּ֫יִת (ba.yit): house: household
- H1G | אָב (av): father
- H834A | אֲשֶׁר (a.sher): which
- H7200G | רָאָה (ra.ah): to see: see
- H6213H | עָשָׂה (a.sah): to make
- H1471A | גּוֹי (goy): nation
- H1419A | גָּדוֹל (ga.dol): great: large
- H1288 | בָּרַךְ (ba.rakh): to bless
- H1431 | גָּדַל (ga.dal): to magnify
- H8034 | שֵׁם (shem): name
- H1961 | הָיָה (ha.yah): to be
- H1293 | בְּרָכָה (be.ra.khah): blessing
- H7043 | קָלַל (qa.lal): to lighten
- H779 | אָרַר (a.rar): to curse
- H9003 | /ב (b): in/on/with
- H3605 | כֹּל (kol): all
- H4940 | מִשְׁפָּחָה (mish.pa.chah): family
- H127I | אֲדָמָה (a.da.mah): land: planet
- H834D | כַּאֲשֶׁר (ka.a.sher): as which
- H1696G | דָבַר (da.var): to speak: speak
- H854 | אֵת (et): with
- H3876 | לוֹט (lot): Lot
- H1121L | בֵּן (ben): son: aged
- H2568 | חָמֵשׁ (cha.mesh): five
- H8141 | שָׁנָה (sha.neh): year
- H7657 | שִׁבְעִים (shiv.im): seventy
- H3318G | יָצָא (ya.tsa): to come out: come
- H2771A | חָרָן (cha.ran): Haran
- H3947G | לָקַח (la.qach): to take: take
- H853 | אֵת (et): [Obj.]
- H8297 | שָׂרַי (sa.ray): Sarai
- H802H | אִשָּׁה (ish.shah): woman: wife
- H1121A | בֵּן (ben): son: child
- H251G | אָח (ach): brother: male-sibling
- H7399 | רְכוּשׁ (re.khush): property
- H7408 | רָכַשׁ (ra.khash): to gather
- H5315J | נֶ֫פֶשׁ (ne.phesh): soul: person
- H6213I | עָשָׂה (a.sah): to make: offer
- H3667A | כְּנַ֫עַן (ke.na.an): Canaan
- H935G | בּוֹא (bo): to come (in): come
- H5674A | עָבַר (a.var): to pass
- H5704 | עַד (ad): till
- H4725 | מָקוֹם (ma.qom): place
- H7927G | שְׁכֶם (she.khem): Shechem
- H436H | אֵלוֹן (e.lon): terebinth
- H4176G | מוֹרֶה (mo.reh): Moreh
- H3669A | כְּנַעֲנִי (ke.na.a.ni): Canaanite
- H227A | אָז (az): then
- H2233H | זֶ֫רַע (ze.ra): seed: children
- H5414G | נָתַן (na.tan): to give: give
- H2063 | זֹאת (zot): this
- H1129 | בָּנָה (ba.nah): to build
- H8033G | שָׁם (sham): there
- H4196 | מִזְבֵּחַ (miz.be.ach): altar
- H6275 | עָתַק (a.taq): to proceed
- H2022H | הַר (har): mountain: hill country
- H6924G | קֶ֫דֶם (qe.dem): front: east
- H1008G | בֵּֽיתְ־אֵל (bet-el): Bethel
- H5186 | נָטָה (na.tah): to stretch
- H168G | אֹ֫הֶל (o.hel): tent
- H3220H | יָם (yam): sea: west
- H5857G | עַי (ay): Ai
- H7121G | קָרָא (qa.ra): to call: call to
- H5265 | נָסַע (na.sa): to set out
- H1980L | הָלַךְ (ha.lakh): to go: continue
- H5045G | נֶ֫גֶב (ne.gev): Negeb
- H7458 | רָעָב (ra.av): famine
- H3381 | יָרַד (ya.rad): to go down
- H4714G | מִצְרַ֫יִם (mits.ra.yim): Egypt
- H1481A | גּוּר (gur): to sojourn
- H3588A | כִּי (ki): for
- H3515 | כָּבֵד (ka.ved): heavy
- H7126G | קָרַב (qa.rav): to present: come
- H2009 | הִנֵּה (hin.neh): behold
- H4994 | נָא (na): please
- H3045 | יָדַע (ya.da): to know
- H802G | אִשָּׁה (ish.shah): woman
- H3303 | יָפֶה (ya.pheh): beautiful
- H4758 | מַרְאֶה (mar.eh): appearance
- H859C | אַתְּ (at.te): you(f.s.)
- H4713 | מִצְרִי (mits.ri): Egyptian
- H2026 | הָרַג (ha.rag): to kill
- H2421 | חָיָה (cha.yah): to live
- H269 | אָחוֹת (a.chot): sister
- H4616 | מַ֫עַן (ma.an): because
- H3190 | יָטַב (ya.tav): be good
- H5668 | עָבוּר (a.vur): for the sake of
- H5315H | נֶ֫פֶשׁ (ne.phesh): soul: life
- H1558 | גָּלָל (ga.lal): because of
- H1931 | הוּא (hu): he/she/it
- H3966 | מְאֹד (me.od): much
- H8269 | שַׂר (sar): ruler
- H6547G | פַּרְעֹה (par.oh): Pharaoh
- H1984B | הָלַל (ha.lal): to boast: praise
- H6629G | צֹאן (tson): flock
- H1241 | בָּקָר (ba.qar): cattle
- H2543 | חֲמוֹר (cha.mor): donkey
- H5650 | עֶ֫בֶד (e.ved): servant/slave
- H8198 | שִׁפְחָה (shiph.chah): maidservant
- H860 | אָתוֹן (a.ton): she-ass
- H1581 | גָּמָל (ga.mal): camel
- H5060 | נָגַע (na.ga): to touch
- H5061 | נֶ֫גַע (ne.ga): plague
- H5921A | עַל (al): upon
- H1697M | דָּבָר (da.var): word: because
- H4100 | מָה (mah): what?
- H6213A | עָשָׂה (a.sah): to make: do
- H3808 | לֹא (lo): not
- H5046 | נָגַד (na.gad): to tell
- H6258 | עַתָּ֫ה (at.tah): now
- H6680 | צָוָה (tsa.vah): to command
- H582 | אֱנוֹשׁ (e.nosh): human
- H7971G | שָׁלַח (sha.lach): to send: depart


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
- 全文合計 ≥800 字，其中散文敘述至少 400 字——沿經文脈絡整合各來源觀點的連貫敘述是主幹，表格、清單、callout 都是它的補充，不可把大半內容包進表格或 callout。
- 這是 Obsidian 筆記庫：行文首次提到本章條目時用 wiki-link 連結，用詞不同寫 [[完整條目名|行文用詞]]，之後再提不必重連；至少要有一個連結，且目標只能取自本章可連條目：亞伯拉罕之約、信心的本質、羅得、哈蘭、亞伯蘭、撒萊、迦南地、示劍（城）、帳棚與祭壇、伯特利、漸漸的墮落、亞伯蘭下埃及是否出於不信、亞伯蘭稱撒萊為妹子的性質、亞伯蘭下埃及與出埃及——不可連清單外的目標；清單裡沒有對應條目的概念（vault 裡存在與否都一樣），直接用純文字提及即可，不要加 [[ ]]。
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
chapter: 12
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