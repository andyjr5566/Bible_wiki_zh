# 從亞當到耶穌

以可縮放、可平移的家譜畫布呈現共同主線、馬太與路加的分線及可展開旁支。資料裡的每一個人都在這張大圖上：經文只把人列在某段名單裡的，掛在名單牌子底下；經文沒有寫家譜的（北國的王、新約裡的一些家庭等），放在同時代主線人物旁邊的區域。人物卡可查看親屬、家譜見證與經節全文；另有兩線對照、年歲時間軸、經文差異，以及「帶你讀經」讀經模式。網站使用 Vite 5、TypeScript、原生 DOM 與 SVG，d3-hierarchy 只負責旁支樹形排版。

## 本機啟動

```powershell
npm install
npm run dev        # http://127.0.0.1:3051/
npm run build      # 先跑型別檢查與資料閘門，再產生 dist/
npm run preview    # http://127.0.0.1:4201/
```

部署時只需 `dist/`。Vite 使用相對路徑，網站可放在子目錄。`?synthetic=1` 在 dev 模式載入合成壓力測試資料，正式 build 不會啟用。建置請用 PowerShell 執行。

## 頁面

| 頁面 | 內容 |
| --- | --- |
| 家譜樹 | SVG 主線與旁支；可拖曳、縮放、搜尋、展開，並沿父母或代數不詳的後裔關係往上追溯。名單牌子（點線）與同時代區域（不畫線）可各自展開收合。 |
| 帶你讀經 | 工具列按鈕打開。一趟從創 4:17 讀到路 3:38（39 段、1,305 節：創世記的家譜、出 6、得 4、撒上 14、撒下 3／5、代上 1–9、代上 11–27 的職位、王上 4、代下 11／21／24、拉 2／7／8／10、尼 3／7／10／11／12、太 1、路 3）。讀到誰鏡頭就移到誰、名字亮起；讀到「生」畫墨線、讀到職稱蓋朱印。畫面跟著經文內容在「家譜樹」「大衛立的職位」「名冊」「城牆」之間自己換（標題卡、角落小地圖、回到朗讀處）。讀拉 2、拉 8、拉 10、尼 7、尼 10 的名單時是名冊：照經文分區，讀到哪寫到哪，人數條跟著朗讀伸長；前面家譜記過的家族蓋「冊上有名」並開子母畫面（家譜樹的一小角），家譜記過的城標「家譜裡有這座城」；只畫經文寫的數字，不算累計。拉 10（娶了外邦女子的人）口氣中性，不加金色；尼 10 的名字像簽名一樣一個個蓋上去。同一個家族（或同一個人）在好幾份名單都出現的，那一行底下一排小籤「也在……」，點了跳到那一節讀。讀尼 3 時是城牆：示意的一圈（不照比例），城門照經文次序排，讀到哪一段亮哪一段、寫上修造的人。讀王上 4 時職位圖捲到「從大衛到所羅門」：大衛時、所羅門時兩欄對照，同一人金框橫跨、換職位的紅框，十二個官吏不編月份。代上 11 的勇士和撒下 23 寫法不同的地方出差異小卡。平行經文寫法不同的地方出差異小卡；歸回的家族連回祖先（祭司二十四班的那一格變紅、族譜尋不著的畫虛線）。可暫停、變速、跳讀、開瀏覽器朗讀；`#read=創5:3`、`#read=代上24:10`、`#read=拉2:61`、`#read=尼3:15` 直接打開到那一節。 |
| 大衛立的職位 | 組織圖：大衛在上，分王的身邊、軍隊、聖殿與利未人、支派與產業四類，加上第五類「從大衛到所羅門」（王上 4 的臣子對照大衛時的官員、十二個官吏）；祭司二十四班與歌唱二十四班畫成環、十二班軍隊畫成十二個月的輪盤、投奔大衛的人依支派分組。點人名看他的每個職位；家譜樹上有的人點了回家譜樹。家譜樹上的人旁邊蓋職位印，點印到這一頁。 |
| 兩條線對照 | 按資料段落整理各份見證的名字；點名字回到家譜畫布。 |
| 年歲時間軸 | 以創世後年份呈現出生、死亡、生子時間與事件。 |
| 經文不同的地方 | 並列經節、引句、各家說法及來源網址。 |

一家人在家譜樹上的排法（`src/data/model.ts` 的 `buildGraph`）：

- 有記妻子（或孩子的母親）的人，往外排成三欄：他 → 妻子欄 → 兒女欄。兒女接在自己的母親底下；經文沒寫母親的，接在妻子欄最後的「母親未記載」底下。妻子卡上緣標「妻子」，經文沒記成夫妻的標「生母」。
- 妻子本人的卡：本來就在丈夫旁邊、或和丈夫在同一處（西庇太一家）的，直接用本人。娘家只有一條祖先線、而且掛在這一家裡面的（瑪迦的祖父亞米忽、父親達買），本人搬進妻子欄，祖先疊在他上面（亞米忽 → 達買 → 瑪迦）；記了兩個名字的父親並排（拔示巴上面的以連、亞米利），另一位丈夫放在他下面（烏利亞）。娘家是另外一大支的（利亞、拉結在拉班底下），妻子欄放一張「↗」卡，第二行寫「拉班的女兒」，點了跳到本人。
- 主線上的兒女（猶大、所羅門）不能搬家，在母親的兒女欄放一張「↗」卡，點了跳到主線上。
- 程式裡：`graph.wifeSlots`（妻子欄每張卡）、`graph.bornOf`（妻子的「↗」卡，id 前綴 `所生:`）、`graph.childRefs`（主線兒女的「↗」卡，前綴 `主線:`）、`graph.noMother`（「母親未記載」，前綴 `未記母親:`）、`graph.ancestry`、`graph.otherHusbands`。標示卡不算進後代人數（主線兒女的「↗」卡算）。
- 主線分成馬太、路加兩欄的地方（大衛），妻子欄整組推到那一欄外面，線不交叉。其他排在兩處的父母、夫妻不拉長線，在名字上方標「母親：某某」「妻子：某某」，點名字打開那一支並跳過去。
`#p=人物` 打開人物卡；`#family=家族` 打開大圖上的那一家（含新約家族）。

## 資料

| 檔案 | 內容 |
| --- | --- |
| `src/data/genealogy.json` | 家譜人物、主線段落、見證、年歲、註記、導覽，以及大圖安置（`placements`：名單牌子、區域、各家掛在哪裡）。 |
| `src/data/reading.json` | 讀經路線：39 段、1,305 節經文的逐節標記（人名、職稱、親屬詞、地名、數字、墨線、這一節用哪個畫面），加上讀經提醒、平行經文差異小卡（`diffs`）、歸回的家族連回祖先（`links`）。 |
| `src/data/roles.json` | 大衛立的職位：五類（含從大衛到所羅門的兩欄對照 `rows`、十二個官吏）、各職位方塊與成員、只在職位圖上的人。分頁打開或讀經讀到時才載入。 |
| `src/data/roster.json` | 名冊（拉 2、拉 8、拉 10、尼 7、尼 10）：分區、每一行的字與人數在經文裡的位置、尼 7 和拉 2 不同的行、行裡的歸回連結、口氣（`tone`）、簽名蓋印（`seal`）、家族軌跡（`families`、行與名字上的 `fam`）。讀經讀到時才載入。 |
| `src/data/wall.json` | 尼 3 修城牆的人：照經文次序繞一圈的門、樓、每一段修造的人與家族軌跡。讀經讀到時才載入。 |
| `src/data/verses.json` | 上述資料所用的經節全文。 |
| `src/data/speech-fixes.ts` | 朗讀用的多音字替換表（只改送給語音的文字）。 |
| `src/data/types.ts` | 匯出 JSON 的 TypeScript 型別。 |
| `src/data/model.ts` | 資料查詢、關係圖（含大圖安置）、祖先路徑與 dev 合成資料。 |
| `src/data/data.test.ts` | 資料完整度、全展開版面不重疊、每人都有節點、讀經標記位置與人物的閘門；只從網站資料夾讀 JSON。 |
| `src/data/roster.test.ts`、`chinese-number.ts` | 名冊的字在經文的位置逐字核對、人數等於經文的中文數字。 |
| `src/assets/fonts/` | 讀經模式的楷書字型（霞鶩文楷 TC，SIL OFL 1.1），只留用到的字；`OFL.txt` 是授權全文。 |

JSON 由 `appendix/genealogy/build_genealogy.py` 的匯出功能產生。資料都在 `appendix/genealogy/亞當到耶穌/`：

| 檔案 | 內容 |
| --- | --- |
| `大圖安置.yaml` | 接不上主線的家族掛在大圖哪裡。 |
| `讀經路線.yaml` | 讀經的 39 段：經文範圍、標題、分組、預設畫面（家譜樹、職位圖、名冊、城牆）、段內換畫面的地方。 |
| `讀經.yaml`、`讀經/*.yaml` | 逐節裁決：名字是誰、職稱屬於誰、只在經文裡亮的名字、地名（程式在 `appendix/genealogy/reading.py`）。 |
| `職位.yaml` | 大衛立的職位與從大衛到所羅門（程式在 `appendix/genealogy/roles.py`）；家譜樹上的人、合併成同一人的要寫根據；十二個官吏不准編月份（建置檢查）。 |
| `歸回.yaml` | 歸回的家族連回祖先、名冊上的「冊上有名」與「家譜裡有這座城」，每一筆都寫根據。 |
| `名冊.yaml` | 名冊：照經文分區的每一行（程式在 `appendix/genealogy/roster.py`，逐字、數字與量詞（含沒寫量詞的）、涵蓋每一節都由建置檢查；`tone: plain` 的名冊不准有冊上有名的連結）。 |
| `城牆.yaml` | 尼 3 的城牆一圈：門、樓、每一節修造的人（程式在 `appendix/genealogy/wall.py`，逐字、次序、涵蓋每一節、繞回羊門都由建置檢查）。 |
| `家族.yaml` | 家族軌跡：同一個家族在六份名單出現的位置與根據（程式在 `appendix/genealogy/family.py`；每一處的中文寫法要在 `forms`、第幾次出現要對到 STEP 那一個詞、原文編號要屬於 `tipnr` 那一條。這個檢查要讀本機的 `appendix/genealogy/sources/TIPNR.txt`，它不進版控，下載方法見同資料夾的 README）。 |
| `差異.yaml` | 平行經文差異小卡：只寫兩處各自的寫法和經節（含撒下 23 對代上 11 的勇士名單）。 |
| `people/06_大衛立的職位.yaml` | 職位章裡經文寫明父親、而父親已在家譜樹上的人。 |

**資料根據的順序**（每一個連結都寫 `basis:`，建置時由 `appendix/genealogy/check_basis.py` 逐字檢查）：
1. 經文（`raw_scripture/`，和合本）：人物關係、職位、誰是誰的兒子，只取自這裡；前後文能判斷的以前後文為準。
2. 原文證據（STEP Bible，`raw_data/stepbible_*.txt`）：同名的人常用不同的擴充 Strong 編號區分。
3. 四套註釋（`raw_data/` 的 CT、GT、KC、BH）：只能支持經文已經指向的連結，引句逐字比對原檔。
4. TIPNR（STEPBible-Data，CC BY 4.0，見 `appendix/genealogy/sources/README.md`）：交叉檢查同名的人。不引維基百科；外部資料和經文衝突時以經文為準。

**連結規則：有根據且沒人反對才連。** 「是不是同一人／同一家／同一座城」：STEP 原文編號（含字母）相同而且 TIPNR 是同一條，或四套註釋有一句話明說；而且沒有任何一方反對。STEP／TIPNR 把它們分成不同的人（分條），或有註釋說不是、可能只是同名，就算反對；同一條 TIPNR 裡只是寫法不同（約薩達／約薩答、亞多蘭／亞多尼蘭）不算反對。各說各話、都沒根據的，不連、照讀。

Python 閘門的單元測試（含突變測試）：

```powershell
python -m unittest appendix.genealogy.tests_roster appendix.genealogy.tests_wall appendix.genealogy.tests_family appendix.genealogy.tests_roles_solomon appendix.genealogy.tests_check_basis util.tests.test_genealogy_pages
```

檢查工具在 `appendix/genealogy/tools/`：`reading_gate.py`（逐段三項閘門：位置錯誤、找不到人物、未處理的人名）、`step_names.py`（每節原文人名，`audit` 列出標記數對不上的節）、`align_parallels.py`（平行名單逐名對齊）、`tipnr.py`（TIPNR 對照表）。朗讀多音字用 `scripts/polyphone_cases.py` 產生候選、`scripts/tts_polyphone.py` 比對語音波形（說明見 `scripts/README.md`）。

```powershell
python appendix/genealogy/build_genealogy.py 亞當到耶穌 --export-json appendix/website/全聖經/亞當到耶穌/src/data
python appendix/genealogy/tools/reading_gate.py
```

（舊說明）大圖安置的裁決在 `大圖安置.yaml`，讀經標記的裁決在 `讀經.yaml`：

```powershell
python appendix/genealogy/build_genealogy.py 亞當到耶穌 --export-json appendix/website/全聖經/亞當到耶穌/src/data
```

讀經資料或介面文字有新字時，重做字型子集（字型原檔從 LXGW WenKai TC 的 GitHub release 下載）：

```powershell
python scripts/subset_font.py LXGWWenKaiTC-Regular.ttf LXGWWenKaiTC-Medium.ttf OFL.txt
```

建置不會讀取 vault 其他檔案，也不連網。
