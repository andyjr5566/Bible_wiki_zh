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
| 帶你讀經 | 工具列按鈕打開。代上 1–9 章逐節往下讀，讀到誰鏡頭就移到誰、名字亮起；讀到「生」畫墨線、讀到職稱蓋朱印。可暫停、變速、跳讀、開瀏覽器朗讀；`#read=代上2:4` 直接打開到那一節。 |
| 兩條線對照 | 按資料段落整理各份見證的名字；點名字回到家譜畫布。 |
| 年歲時間軸 | 以創世後年份呈現出生、死亡、生子時間與事件。 |
| 經文不同的地方 | 並列經節、引句、各家說法及來源網址。 |

夫妻與母子在家譜樹上的畫法：

- 有記母親的孩子照母親分開，掛在母親底下（亞伯拉罕 → 夏甲 → 以實瑪利），丈夫到妻子的線標「妻子」。
- 妻子本人排在娘家那一支的（利亞在拉班底下），丈夫旁邊放一張同樣的卡，右上角「↗」；點一下展開孩子，再點跳到娘家本人。程式裡這張卡是 `graph.bornOf`（id 前綴 `所生:`），不算進後代人數。
- 父母本來就排在同一處的（西庇太一家），不放這張卡，直接畫母子線。
- 主線上的孩子：母親在父親或孩子旁邊就畫母子線，否則名字上方標「母親：某某」；沒排在一起的夫妻標「妻子：某某」。點標籤裡的名字會打開那一支並跳過去。

`#p=人物` 打開人物卡；`#family=家族` 打開大圖上的那一家（含新約家族）。

## 資料

| 檔案 | 內容 |
| --- | --- |
| `src/data/genealogy.json` | 家譜人物、主線段落、見證、年歲、註記、導覽，以及大圖安置（`placements`：名單牌子、區域、各家掛在哪裡）。 |
| `src/data/reading.json` | 讀經模式的逐節標記：代上 1–9 章 407 節經文，標出人名、職稱、親屬詞、地名、數字，以及墨線要從誰畫到誰。 |
| `src/data/verses.json` | 上述資料所用的經節全文。 |
| `src/data/speech-fixes.ts` | 朗讀用的多音字替換表（只改送給語音的文字）。 |
| `src/data/types.ts` | 匯出 JSON 的 TypeScript 型別。 |
| `src/data/model.ts` | 資料查詢、關係圖（含大圖安置）、祖先路徑與 dev 合成資料。 |
| `src/data/data.test.ts` | 資料完整度、全展開版面不重疊、每人都有節點、讀經標記位置與人物的閘門；只從網站資料夾讀 JSON。 |
| `src/assets/fonts/` | 讀經模式的楷書字型（霞鶩文楷 TC，SIL OFL 1.1），只留用到的字；`OFL.txt` 是授權全文。 |

JSON 由 `appendix/genealogy/build_genealogy.py` 的匯出功能產生。大圖安置的裁決在 `appendix/genealogy/亞當到耶穌/大圖安置.yaml`，讀經標記的裁決在 `讀經.yaml`（程式在 `appendix/genealogy/reading.py`）：

```powershell
python appendix/genealogy/build_genealogy.py 亞當到耶穌 --export-json appendix/website/全聖經/亞當到耶穌/src/data
```

讀經資料或介面文字有新字時，重做字型子集（字型原檔從 LXGW WenKai TC 的 GitHub release 下載）：

```powershell
python scripts/subset_font.py LXGWWenKaiTC-Regular.ttf LXGWWenKaiTC-Medium.ttf OFL.txt
```

建置不會讀取 vault 其他檔案，也不連網。
