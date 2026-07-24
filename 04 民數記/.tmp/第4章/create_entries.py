import os
import sys
import yaml

sys.stdout.reconfigure(encoding='utf-8')

out_dir = r"C:\Obsidian\Hermes\scripture\04 民數記\.tmp\第4章\entry_content"
os.makedirs(out_dir, exist_ok=True)

entries = [
    {
        'name': '哥轄子孫',
        'type': '人物',
        'secondary_types': [],
        'aliases': [],
        'status': 'formal',
        'definition': '哥轄（Kohath，意為「集會」）為利未次子，其子孫在利未三大家族中處於首要與特出的地位（CT、GT）。哥轄子孫在會幕曠野行軍與搬運事工中，專責搬運至聖所與聖所內的「至聖之物」（包括約櫃、陳設餅桌子、金燈臺、金香壇、銅壇及其屬壇器具與聖所器皿）（v4-14）。摩西與亞倫亦出自哥轄家族，因而此族在事奉上享有最崇高與神聖的職責（GT）。然而，哥轄子孫在搬運至聖物時，嚴禁親自觸摸或觀看未包紮的聖物，違者必遭擊殺（v15, 20）；必須等候亞倫及其兒子（祭司）先將聖物以幔子、海狗皮與各式顏色毯子完全包裹後，方能扛抬移動（CT、KC）。',
        'accumulations': [
            {
                'book': '民數記',
                'chapter': 4,
                'summary': '本章記載哥轄子孫30歲至50歲在前來任職、在會幕裡辦事的男丁共有2,750名（v36）；詳細規定祭司包紮至聖物與哥轄子孫搬運抬載的嚴格規範與懲戒警告（v1-20, 34-37）。',
                'relation': '確立哥轄子孫作為至聖物搬運者的特別職掌與事奉邊界，展現神聖潔要求與嚴密秩序。'
            }
        ],
        'related_entries': ['利未三族分工', '利未支派', '摩西', '亞倫', '以利亞撒', '約櫃', '不可摸聖物'],
        'sources': [
            '逐節註解: 民數記第四章註解（https://www.ccbiblestudy.org/Old%20Testament/04Num/04CT04.htm）',
            '拾穗: 民數記第四章拾穗（https://www.ccbiblestudy.org/Old%20Testament/04Num/04GT04.htm）',
            '研經註解: KingComments Numbers 4（https://www.kingcomments.com/en/bible-studies/Num/4）',
            '研經註解: BibleHub Study Numbers 4（https://biblehub.com/study/numbers/4.htm）'
        ]
    },
    {
        'name': '革順子孫',
        'type': '人物',
        'secondary_types': [],
        'aliases': [],
        'status': 'formal',
        'definition': '革順（Gershon，意為「流亡」）為利未長子，其子孫負責會幕織物與覆蓋結構的拆卸、搬運與保管事工（CT、GT）。在起營移動時，革順子孫負責扛抬與經理帳幕的最內層十幅幔子、會幕罩棚、公羊皮蓋與海狗皮頂蓋、會幕門簾、院子圍繞四圍的帷子與門簾，以及相關繩子與器具（v24-26）。在搬運工具上，革順子孫獲分配兩輛牛車與四隻牛進行運輸（民7:7；GT）。革順子孫的一切抬物與辦事，皆在祭司亞倫之子以他瑪的指揮與監督下進行（v28；CT、BH）。',
        'accumulations': [
            {
                'book': '民數記',
                'chapter': 4,
                'summary': '本章記載革順子孫30歲至50歲在會幕任職辦事的男丁共有2,630名（v39-40）；詳細分派其抬運會幕幔子、門簾、帷子與繩索等織物事事（v21-28, 38-41）。',
                'relation': '呈現革順子孫在會幕外部保護與見證結構上的特別職責，彰顯肢體分工與順服祭司權柄原則。'
            }
        ],
        'related_entries': ['利未三族分工', '利未支派', '以他瑪', '海狗皮頂蓋', '內幔（隔聖所至聖所的幔子）', '藍色、紫色、朱紅色線（tekhelet, argaman, tola\'at shani）'],
        'sources': [
            '逐節註解: 民數記第四章註解（https://www.ccbiblestudy.org/Old%20Testament/04Num/04CT04.htm）',
            '拾穗: 民數記第四章拾穗（https://www.ccbiblestudy.org/Old%20Testament/04Num/04GT04.htm）',
            '研經註解: KingComments Numbers 4（https://www.kingcomments.com/en/bible-studies/Num/4）',
            '研經註解: BibleHub Study Numbers 4（https://biblehub.com/study/numbers/4.htm）'
        ]
    },
    {
        'name': '米拉利子孫',
        'type': '人物',
        'secondary_types': [],
        'aliases': [],
        'status': 'formal',
        'definition': '米拉利（Merari，意為「苦味」）為利未幼子，其子孫負責會幕整體硬體骨架與建築結構的拆卸、搬運與架設事工（CT、GT）。米拉利子孫所抬負的物件最為粗重，包括帳幕的豎板、閂、柱子與帶卯的座，以及院子四圍的柱子、帶卯的座、橛子、繩子與一切使用器具（v31-32）。因所搬運的物件體積龐大且重量極沈（含金、銀、銅與重木），米拉利子孫在諸族中獲分配最多的四輛牛車與八隻牛（民7:8；GT）。此外，摩西與亞倫特別吩咐對米拉利子孫所抬的器具必須「按名指定」（v32），防範細小件遺失並維持嚴密秩序。其事工同在祭司以他瑪手下督理（v33；CT）。',
        'accumulations': [
            {
                'book': '民數記',
                'chapter': 4,
                'summary': '本章記載米拉利子孫30歲至50歲在會幕任職辦事的男丁共有3,200名（v43-44）；詳細列明其抬負會幕板閂柱座等骨架器具並實施按名指定（v29-33, 42-45）。',
                'relation': '展現米拉利子孫承擔會幕穩固基石與骨架事工的忠心，證明暗中扶持與粗重事務在神眼中同等尊貴。'
            }
        ],
        'related_entries': ['利未三族分工', '利未支派', '以他瑪', '按名指定', '會幕（帳幕整體）'],
        'sources': [
            '逐節註解: 民數記第四章註解（https://www.ccbiblestudy.org/Old%20Testament/04Num/04CT04.htm）',
            '拾穗: 民數記第四章拾穗（https://www.ccbiblestudy.org/Old%20Testament/04Num/04GT04.htm）',
            '研經註解: KingComments Numbers 4（https://www.kingcomments.com/en/bible-studies/Num/4）',
            '研經註解: BibleHub Study Numbers 4（https://biblehub.com/study/numbers/4.htm）'
        ]
    },
    {
        'name': '數點利未任職男子',
        'type': '事件',
        'secondary_types': [],
        'aliases': [],
        'status': 'formal',
        'definition': '數點利未任職男子是指摩西、亞倫與以色列會眾的諸首領，依耶和華命令對利未支派哥轄、革順、米拉利三大家族中「從三十歲直到五十歲」凡前來任職、在會幕裡做抬物與辦事之工的男丁進行第二次精確普查（v1-3, 34-49；CT、GT）。本次數點與民數記3章按月齡（一月以上男丁代贖長子）的統計不同，專為實際扛抬與經營會幕聖事之體力與成熟度作準備。統計總數為8,580名（哥轄2,750名、革順2,630名、米拉利3,200名），占利未一月以上總男丁（22,000名）約三分之一強（GT、KC）。此數點確保會幕起營移動時人手充沛、權責明確，展現神管理神的百姓具有周密計畫與清淅分配（GT）。',
        'accumulations': [
            {
                'book': '民數記',
                'chapter': 4,
                'summary': '本章記載摩西、亞倫與諸首領詳細登記三族30至50歲任職男子，最終總結全體利未任職人員共計8,580名（v34-49）。',
                'relation': '標誌著利未人從身份登記進步到具體聖職與負重事奉的執行階段。'
            }
        ],
        'related_entries': ['利未三族分工', '利未支派', '三十歲直到五十歲（利未人任職年齡）', '摩西', '亞倫'],
        'sources': [
            '逐節註解: 民數記第四章註解（https://www.ccbiblestudy.org/Old%20Testament/04Num/04CT04.htm）',
            '拾穗: 民數記第四章拾穗（https://www.ccbiblestudy.org/Old%20Testament/04Num/04GT04.htm）',
            '研經註解: KingComments Numbers 4（https://www.kingcomments.com/en/bible-studies/Num/4）',
            '研經註解: BibleHub Study Numbers 4（https://biblehub.com/study/numbers/4.htm）'
        ]
    },
    {
        'name': '三十歲直到五十歲（利未人任職年齡）',
        'type': '主題',
        'secondary_types': [],
        'aliases': [],
        'status': 'formal',
        'definition': '「從三十歲直到五十歲」是神為利未人在曠野時期正式任職、在會幕裡辦理繁重搬運與聖物事工所訂定的年齡門檻（v3, 23, 30, 35, 39, 43, 47；CT、GT）。此年齡層代表人生最成熟、精力最充沛的壯年時期：30歲象徵生命長大成熟、具備靈性經驗與體力能力；50歲則防止身心衰老受損或無力承擔重負（CT、GT）。主耶穌在地上開始傳道亦在三十歲左右（路3:23），符合聖經事奉要求的屬靈原則（CT、GT）。此門檻與民數記8:24規定的25歲（學徒受訓期）以及大衛與歸回時期（代上23:24、拉3:8）的20歲（聖殿建成無須搬運會幕）形成完美的歷史遞進與制度調和（GT、KC）。',
        'accumulations': [
            {
                'book': '民數記',
                'chapter': 4,
                'summary': '本章七次反覆強調「從三十歲直到五十歲」為前來任職在會幕辦事的嚴格條件，並按此年齡段統計出8,580名合格利未工人（v3, 23, 30, 35, 39, 43, 47）。',
                'relation': '彰顯神要求事奉者將最成熟、最健壯的黃金歲月獻給神，且事奉必須經過生命成長與鍛鍊。'
            }
        ],
        'related_entries': ['數點利未任職男子', '利未人任職年齡的差異', '辦事（melakah）', '工作（baabodath）'],
        'sources': [
            '逐節註解: 民數記第四章註解（https://www.ccbiblestudy.org/Old%20Testament/04Num/04CT04.htm）',
            '拾穗: 民數記第四章拾穗（https://www.ccbiblestudy.org/Old%20Testament/04Num/04GT04.htm）',
            '研經註解: KingComments Numbers 4（https://www.kingcomments.com/en/bible-studies/Num/4）',
            '研經註解: BibleHub Study Numbers 4（https://biblehub.com/study/numbers/4.htm）'
        ]
    },
    {
        'name': '按名指定',
        'type': '主題',
        'secondary_types': [],
        'aliases': [],
        'status': 'formal',
        'definition': '「按名指定」（assign by name）是摩西與亞倫在分派米拉利子孫搬運會幕硬體骨架（板、閂、柱子、帶卯的座、橛子、繩子等）時所執行的嚴格分工管理命令（v32；CT、GT）。由於米拉利族所負責的物件數量極多且多屬零散小型組件，若無精確指派極易造成隨意挑選、輕重不均或遺失破損（GT、串珠）。祭司亞倫與以他瑪逐一按物件名稱與工人姓名進行一對一清點與指定，確保每位利未人都清楚自身具體責任。這展現了神事工管理的細緻入微與高度秩序，預表新約教會中肢體按恩賜各盡其職、井然有序地建立基督身體（GT、BH）。',
        'accumulations': [
            {
                'book': '民數記',
                'chapter': 4,
                'summary': '本章第32節命令祭司對米拉利子孫所抬的一切器具實施按名指定，防止雜亂與遺失。',
                'relation': '體現神對聖所事工管理精確與公平分擔原則，強調個體在團體事奉中的明確定位。'
            }
        ],
        'related_entries': ['米拉利子孫', '以他瑪', '祭司統轄事奉'],
        'sources': [
            '逐節註解: 民數記第四章註解（https://www.ccbiblestudy.org/Old%20Testament/04Num/04CT04.htm）',
            '拾穗: 民數記第四章拾穗（https://www.ccbiblestudy.org/Old%20Testament/04Num/04GT04.htm）',
            '研經註解: KingComments Numbers 4（https://www.kingcomments.com/en/bible-studies/Num/4）',
            '研經註解: BibleHub Study Numbers 4（https://biblehub.com/study/numbers/4.htm）'
        ]
    },
    {
        'name': '抬架（會幕器具搬運）',
        'type': '主題',
        'secondary_types': [],
        'aliases': [],
        'status': 'formal',
        'definition': '抬架（carrying frame / bars，原文指槓或專用攜帶架）是會幕起營搬運時，專用於承載無法直接穿槓搬運之聖所器具（如金燈檯及其一切剪子盤子油器、金香壇相關器具、聖所一切使用器具，以及祭壇遮蓋後的附屬器皿）的專用搬運工具（v10, 12, 15；CT、GT）。聖所中至聖物件除約櫃、桌子、兩座壇設有固有環槓外，其餘精緻聖器皆須先經祭司以藍布與海狗皮嚴密包裹後，放置於抬架之上由哥轄子孫肩抬（CT、GT）。這確保一切聖物絕不直接接觸人的雙手或曠野地面，維護神絕對的聖潔規範與尊榮（BH）。',
        'accumulations': [
            {
                'book': '民數記',
                'chapter': 4,
                'summary': '本章第10、12、15節記載金燈檯與聖所各樣器具包裹海狗皮後，均須放置於抬架上由哥轄子孫扛抬。',
                'relation': '補充會幕聖器運輸的具體安全裝置，凸顯對聖物嚴禁直接觸摸的保護措施。'
            }
        ],
        'related_entries': ['哥轄子孫', '金燈臺', '不可摸聖物'],
        'sources': [
            '逐節註解: 民數記第四章註解（https://www.ccbiblestudy.org/Old%20Testament/04Num/04CT04.htm）',
            '拾穗: 民數記第四章拾穗（https://www.ccbiblestudy.org/Old%20Testament/04Num/04GT04.htm）',
            '研經註解: KingComments Numbers 4（https://www.kingcomments.com/en/bible-studies/Num/4）',
            '研經註解: BibleHub Study Numbers 4（https://biblehub.com/study/numbers/4.htm）'
        ]
    },
    {
        'name': '不可摸聖物',
        'type': '神學',
        'secondary_types': [],
        'aliases': [],
        'status': 'formal',
        'definition': '「不可摸聖物，免得他們死亡」（v15）是神給予搬運至聖物之哥轄子孫的嚴厲警示與聖潔禁令（CT、GT）。至聖物（約櫃、陳設餅桌、燈檯、香壇、祭壇）已被膏立分別為聖，充滿神的屬靈權威與榮耀臨在；未經膏立的哥轄子孫雖獲選為搬運人員，但若直接親手觸摸聖物，即屬褻瀆神的聖潔，必定招致死亡懲罰（GT、BH）。此禁令確立了「祭司負責包裹、利未人僅負責肩抬」的嚴格權限邊界（CT）。後世大衛時代烏撒因手扶約櫃而被神擊殺（撒下6:6-7），即為違背此禁令的經典歷史教訓（GT、KC）。靈意上，警示信徒事奉時不可越分干涉或憑肉體私意「觸摸」神的聖事，當存敬畏順服的心（CT）。',
        'accumulations': [
            {
                'book': '民數記',
                'chapter': 4,
                'summary': '本章第15節嚴禁哥轄子孫在搬運會幕物件時觸摸聖物，違者必死，並規定必須由亞倫父子遮蓋完畢後始得肩抬。',
                'relation': '確立聖物不可侵犯之屬靈原則，劃清祭司與利未人事奉權責的分水嶺。'
            }
        ],
        'related_entries': ['哥轄子孫', '不可摸約櫃（撒下6：6-7）', '不可觀看聖所', '約櫃'],
        'sources': [
            '逐節註解: 民數記第四章註解（https://www.ccbiblestudy.org/Old%20Testament/04Num/04CT04.htm）',
            '拾穗: 民數記第四章拾穗（https://www.ccbiblestudy.org/Old%20Testament/04Num/04GT04.htm）',
            '研經註解: KingComments Numbers 4（https://www.kingcomments.com/en/bible-studies/Num/4）',
            '研經註解: BibleHub Study Numbers 4（https://biblehub.com/study/numbers/4.htm）'
        ]
    },
    {
        'name': '不可觀看聖所',
        'type': '神學',
        'secondary_types': [],
        'aliases': [],
        'status': 'formal',
        'definition': '「只是他們連片時不可進去觀看聖所，免得他們死亡」（v20）是神對哥轄子孫發出的另一道極其嚴肅的防護戒命（CT、GT）。「片時」指轉瞬之間或一會兒；「觀看聖所」指窺視或注視未經幔子遮蓋的至聖所與至聖器具（CT）。神臨在的至聖榮耀無比聖潔，墮落罪人若擅自窺探神的至聖權能，必立刻招致滅亡（出33:20、賽6:5；GT、BH）。神吩咐亞倫父子必須先進去將至聖物件以幔子與海狗皮完全覆蓋遮掩，哥轄子孫始可進去扛抬，此乃神因著慈愛為保護哥轄家族不被神聖榮耀擊殺所設立的安全屏障（v18-19；GT、KC）。新約時代因基督肉身裂開，信徒始得坦然進入至聖所（來10:19-20；GT）。',
        'accumulations': [
            {
                'book': '民數記',
                'chapter': 4,
                'summary': '本章第18-20節吩咐摩西亞倫務要派定哥轄人的工作，嚴禁他們連片時進去觀看至聖物，免得哥轄支派從利未人中剪除。',
                'relation': '揭示神對罪人的憐憫保護與聖潔不可冒犯之張力，強調敬畏與遵循神定規導引的重要性。'
            }
        ],
        'related_entries': ['哥轄子孫', '不可摸聖物', '內幔（隔聖所至聖所的幔子）', '亞倫'],
        'sources': [
            '逐節註解: 民數記第四章註解（https://www.ccbiblestudy.org/Old%20Testament/04Num/04CT04.htm）',
            '拾穗: 民數記第四章拾穗（https://www.ccbiblestudy.org/Old%20Testament/04Num/04GT04.htm）',
            '研經註解: KingComments Numbers 4（https://www.kingcomments.com/en/bible-studies/Num/4）',
            '研經註解: BibleHub Study Numbers 4（https://biblehub.com/study/numbers/4.htm）'
        ]
    },
    {
        'name': '祭司統轄事奉',
        'type': '神學',
        'secondary_types': [],
        'aliases': [],
        'status': 'formal',
        'definition': '祭司統轄事奉是指利未全支派的所有服事與搬運工作，均必須嚴格在祭司（亞倫及其兒子以利亞撒、以他瑪）的權柄、吩咐與監督之下執行的神學原則（v16, 27, 28, 33；CT、GT）。其中亞倫長子以利亞撒統轄至聖所器具與哥轄子孫，並親自看守點燈油、香料、常獻素祭與膏油（v16；GT）；亞倫幼子以他瑪則專責督理革順子孫與米拉利子孫的搬運與看守（v28, 33）。利未人不可自行決定事奉內容或私自選擇崗位，必須完全順服祭司的分派（CT）。這彰顯了神家事奉層次分明、權責清晰的秩序，預表在新約教會中一切事奉皆須順服基督為大祭司與元首的權柄（KC、BH）。',
        'accumulations': [
            {
                'book': '民數記',
                'chapter': 4,
                'summary': '本章多處明確規定革順與米拉利子孫在以他瑪手下辦事（v28, 33），哥轄子孫由以利亞撒監督（v16），一切抬物辦事均憑祭司吩咐（v27）。',
                'relation': '奠定聖所事奉中「權柄與順服」的核心架構，確保團體運作不致混亂。'
            }
        ],
        'related_entries': ['以利亞撒', '以他瑪', '利未三族分工', '按名指定'],
        'sources': [
            '逐節註解: 民數記第四章註解（https://www.ccbiblestudy.org/Old%20Testament/04Num/04CT04.htm）',
            '拾穗: 民數記第四章拾穗（https://www.ccbiblestudy.org/Old%20Testament/04Num/04GT04.htm）',
            '研經註解: KingComments Numbers 4（https://www.kingcomments.com/en/bible-studies/Num/4）',
            '研經註解: BibleHub Study Numbers 4（https://biblehub.com/study/numbers/4.htm）'
        ]
    },
    {
        'name': '利未人任職年齡的差異',
        'type': '解經爭議',
        'secondary_types': [],
        'aliases': [],
        'status': 'formal',
        'definition': '聖經關於利未人開始在會幕或聖殿任職的年齡記載存在顯著差異：民數記4:3規定為「三十歲」，民數記8:24規定為「二十五歲」，而以斯拉記3:8與歷代志上23:24則記載為「二十歲」（GT）。傳統解經與學者解經提供合理的制度調和與歷史發展解釋：(1) 民數記4:3的30歲是專指在曠野漂泊時期正式負擔「會幕搬運與負重（melakah）」的成熟壯年要求；(2) 民數記8:24的25歲則是利未人進入會幕擔任「學徒與見習訓練（baabodath）」的年齡，經過5年實務學習與觀察，至30歲始正式獨立接管重任（GT艾基斯、賈斯樂）；(3) 大衛與被擄歸回時期調降至20歲，係因聖殿建成立後會幕已無拆卸搬運之苦勞，且歸回時期利未人人數極為稀少（僅74名），故降低門檻以應建殿與督理之急需（GT）。三處經文並無矛盾，實反映不同時代背景與職務性質的彈性調整（GT）。',
        'accumulations': [
            {
                'book': '民數記',
                'chapter': 4,
                'summary': '本章第3節記錄利未人搬運會幕的任職年齡為30歲至50歲，引發與民8:24（25歲）及拉3:8（20歲）年齡差異的解經討論。',
                'relation': '澄清舊約儀文律法在歷史演變與職務階梯中的完美和諧，消除表面經文對立。'
            }
        ],
        'related_entries': ['三十歲直到五十歲（利未人任職年齡）', '辦事（melakah）', '工作（baabodath）', '數點利未任職男子'],
        'sources': [
            '逐節註解: 民數記第四章註解（https://www.ccbiblestudy.org/Old%20Testament/04Num/04CT04.htm）',
            '拾穗: 民數記第四章拾穗（https://www.ccbiblestudy.org/Old%20Testament/04Num/04GT04.htm）',
            '研經註解: KingComments Numbers 4（https://www.kingcomments.com/en/bible-studies/Num/4）',
            '研經註解: BibleHub Study Numbers 4（https://biblehub.com/study/numbers/4.htm）'
        ]
    },
    {
        'name': '抬約櫃的槓是否可抽出來',
        'type': '解經爭議',
        'secondary_types': [],
        'aliases': [],
        'status': 'formal',
        'definition': '出埃及記25:15明確命令「這槓要常在櫃的環內，不可抽出來」，然而民數記4:6在記載起營包裹約櫃時卻寫道「把槓穿上」（insert its poles），產生條例規範上的解經疑義（GT）。解經學者指出，希伯來文「穿上」（sam/sim）字義極廣，包含放置、裝置、調整、轉動或繫緊（adjust and fasten）等動詞意涵（GT賈斯樂）。在實務操作上，約櫃的槓平日始終留在金環之內未曾完全抽出；當起營要依次包裹內幔、海狗皮與純藍色毯子時，祭司必須暫時拉動或調整槓的位置以便將三層覆蓋物順暢蒙蓋，隨後再將槓重新推入、整理並固定緊實（adjust and fasten），稱為「把槓穿上」（GT、KC）。因此兩處指示在原則與操作上完全一致，並無衝突。',
        'accumulations': [
            {
                'book': '民數記',
                'chapter': 4,
                'summary': '本章第6節記載起營包裹約櫃後「把槓穿上」，引出與出25:15「槓不可抽出來」之對比與語義解析。',
                'relation': '解釋會幕起營搬運操作細節，證實神的話語精密不阿與文意協調。'
            }
        ],
        'related_entries': ['約櫃', '哥轄子孫', '海狗皮頂蓋'],
        'sources': [
            '逐節註解: 民數記第四章註解（https://www.ccbiblestudy.org/Old%20Testament/04Num/04CT04.htm）',
            '拾穗: 民數記第四章拾穗（https://www.ccbiblestudy.org/Old%20Testament/04Num/04GT04.htm）',
            '研經註解: KingComments Numbers 4（https://www.kingcomments.com/en/bible-studies/Num/4）',
            '研經註解: BibleHub Study Numbers 4（https://biblehub.com/study/numbers/4.htm）'
        ]
    },
    {
        'name': '辦事（melakah）',
        'type': '原文',
        'secondary_types': [],
        'aliases': [],
        'status': 'formal',
        'definition': '「辦事」（melakah / melakhah，希伯來文 מְלָאכָה）在民數記4:3中專指利未人到達三十歲 mature 年齡後，正式進入會幕所擔負的聖職、管理與至聖物搬運事工（GT）。與一般性的體力勞作不同，melakah 強調具有制度化、責任重大且直接關乎神聖所運作的最高等級職務（GT難解經文）。此字在民數記4章中多次與軍事服役（zaba）並用，表明在會幕裡「辦事」本質上是一場嚴肅的屬靈爭戰與神聖事奉（CT、GT）。',
        'accumulations': [
            {
                'book': '民數記',
                'chapter': 4,
                'summary': '本章第3節使用 melakah 指稱30至50歲利未人在會幕裡所辦理的至聖聖工。',
                'relation': '確立「辦事」作為成熟利未人正式聖職事奉的希伯來原文術語。'
            }
        ],
        'related_entries': ['三十歲直到五十歲（利未人任職年齡）', '工作（baabodath）', '利未人任職年齡的差異'],
        'sources': [
            '逐節註解: 民數記第四章註解（https://www.ccbiblestudy.org/Old%20Testament/04Num/04CT04.htm）',
            '拾穗: 民數記第四章拾穗（https://www.ccbiblestudy.org/Old%20Testament/04Num/04GT04.htm）',
            '研經註解: KingComments Numbers 4（https://www.kingcomments.com/en/bible-studies/Num/4）',
            '研經註解: BibleHub Study Numbers 4（https://biblehub.com/study/numbers/4.htm）'
        ]
    },
    {
        'name': '工作（baabodath）',
        'type': '原文',
        'secondary_types': [],
        'aliases': [],
        'status': 'formal',
        'definition': '「工作」（baabodath / abodah，希伯來文 בַּעֲבֹדָה）在民數記8:24中指利未人從二十五歲開始進入會幕所從事的輔助性勞作、雜務或學徒訓練（GT）。與民數記4:3專指三十歲正式獨立任職的「辦事（melakah）」有所區別，baabodath 著重於體力付出、服侍與學習過程（GT難解經文）。年輕利未人在這5年訓練期中觀察年長者如何拆卸包紮器具、清理地坪與協助獻祭，為日後30歲承擔 melakah 重任奠定堅實基礎（GT）。',
        'accumulations': [
            {
                'book': '民數記',
                'chapter': 4,
                'summary': '本章第3節在解析任職年齡時，對比民8:24的 baabodath（學徒期勞作工作）與民4:3的 melakah（正式辦事）。',
                'relation': '提供分析利未人職務階梯與學徒制度的原文基礎。'
            }
        ],
        'related_entries': ['辦事（melakah）', '三十歲直到五十歲（利未人任職年齡）', '利未人任職年齡的差異'],
        'sources': [
            '逐節註解: 民數記第四章註解（https://www.ccbiblestudy.org/Old%20Testament/04Num/04CT04.htm）',
            '拾穗: 民數記第四章拾穗（https://www.ccbiblestudy.org/Old%20Testament/04Num/04GT04.htm）',
            '研經註解: KingComments Numbers 4（https://www.kingcomments.com/en/bible-studies/Num/4）',
            '研經註解: BibleHub Study Numbers 4（https://biblehub.com/study/numbers/4.htm）'
        ]
    }
]

for e in entries:
    fname = os.path.join(out_dir, f"{e['name']}.yaml")
    with open(fname, 'w', encoding='utf-8') as f:
        yaml.dump(e, f, allow_unicode=True, sort_keys=False)
