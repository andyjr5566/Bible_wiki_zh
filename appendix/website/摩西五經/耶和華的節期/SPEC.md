# 耶和華的節期 — 設計與工程規格（第一階段：開場＋逾越節）

給實作的工程子代理看。內容（經文、註釋、原文、敘述文字）一律來自 `data/*.yaml` 與建置腳本產出的 `src/data/site.json`，**工程端不得撰寫或改寫任何研經文字**；需要新文字就留 `TODO(內容)` 並回報。

## 0. 參考畫面

Santioni Spirits（Active Theory，2026-10-05 Awwwards SOTD）的實際截圖在
`C:\Users\ANDYJ_~1\AppData\Local\Temp\claude\c--Obsidian-Hermes-scripture\3fd4e875-dc78-460f-a17c-d874da7b8c25\scratchpad\ref\`
（用 Read 工具看 png）。要學的是：

- 米白紙上的**版畫刻線**（平行線隨明暗變粗變細，線條略帶手刻的抖動），不是網點；網點只當輔助（例如遠景、煙）。
- 角色與物件是 **3D 模型＋刻線著色**（月亮是一顆刻線球）。
- 粗黑邊框的**漫畫分格**，分格會傾斜、互相疊壓，隨捲動滑入。
- 白底粗黑框的**說明框**，一句話裡只有一個關鍵詞是紅色。
- 圓形白底黑框的**互動徽章**（HOLD & MOVE）。
- 右側細細的**進度條**；右下角的**聲音開關**（等化器線條圖示）。
- 轉場用**整片直向刻線**抹過畫面。

不要學的：它的易用性只有 7.54——文字小、純大寫、互動擋住閱讀。我們的讀者是一般大眾，文字一定要好讀。

## 1. Design Read

```yaml
artifact: 單頁長捲軸敘事網站（scrollytelling）
audience: 一般大眾到查經的人；手機與桌機一樣重要
visual-language: 版畫刻線漫畫（engraving comic），紙與墨，限定配色
mode: greenfield
visual-variance: 8
motion-intensity: 8   # 但只有一個招牌高潮；其他轉場要安靜
information-density: 4  # 一拍一段話；深入內容就地展開
asset-dependence: 6   # 程序生成的 3D 幾何＋著色器，不用外部圖檔
brand-fidelity: 2
```

## 2. 設計系統（CSS custom properties，前綴 `--jf-`）

| token | 亮色 | 暗色 | 用途 |
|---|---|---|---|
| `--jf-paper` | `#efeadf` | `#15130f` | 紙、說明框底 |
| `--jf-ink` | `#161412` | `#ece4d2` | 墨、文字、邊框 |
| `--jf-blood` | `#a3231b` | `#cf4334` | 血、關鍵詞（`==…==`） |
| `--jf-ochre` | `#a88758` | `#b8955f` | 泥磚、衣袍、麥穗 |
| `--jf-night` | `#1c2340` | `#0b0e1c` | 夜空平塗 |
| `--jf-glow` | `#f0c46a` | `#f0c46a` | 燈火、月光 |

- 每章另有 `palette`（feasts.yaml），場景依章切換時插值。
- **暗色模式的刻線**：亮色模式是「深墨刻在淺紙上」，線寬＝暗度；暗色模式是「淺墨刻在深紙上」，線寬＝亮度（1−暗度）。這樣夜空在兩種模式都是暗的。血紅、土黃平塗不變。
- 字型（Google Fonts，`display=swap`，離線退回系統襯線／無襯線）：
  - 大標題：`Cactus Classical Serif`（只有 400），字級 clamp(56px, 11vw, 168px)
  - 說明框正文：`Noto Sans TC` 500，17–19px，行高 1.75
  - 經文：`Noto Serif TC` 500，16–18px，行高 1.9
  - 希伯來文：`Noto Serif Hebrew` 500
- 邊框：說明框與分格 3px 實心墨線，略帶手繪感（用 SVG filter `feTurbulence`+`feDisplacementMap` 輕微抖動，scale ≤ 1.5）；圓角 0。
- 陰影：不用模糊陰影；需要層次時用 6px 偏移的實心墨塊（版畫套印感）。
- 動態：緩動統一 `power3.out`（進場）、`power2.inOut`（轉場）、`none`（scrub）。進場 0.6–0.9s。

## 3. 動線（水流）

1. **一個持續存在的舞台**：`<canvas>` 固定在背景（`position: fixed; inset: 0`），整頁不卸載、不換頁。章與章、拍與拍之間只推動同一條時間軸。
2. **季節當接縫**：開場的夜空與大麥田 → 逾越節的街道。前一拍的結尾畫面就是下一拍的開場畫面；不要硬切。
3. **每拍節奏一樣**：畫面先動 → 說明框滑入（白話＋經文）→ 有互動就出現圓形徽章 → 說明框下方兩顆小按鈕「四家怎麼說」「原文」就地展開。
4. **捲動直接帶動畫面（scrub）**：讀者停下來畫面也停。每拍高度約 120–180vh。pin 的區段不超過 2–3 個螢幕高。
5. **不劫持捲動**：不用 Lenis／smooth scroll，不用 `scrollIntoView`，不在讀者閱讀時自動捲頁。月份導覽被點擊時才 `window.scrollTo({ top, behavior: 'instant' })`，前後加 250ms 的刻線抹除轉場遮住跳動。
6. **文字永遠在 DOM**：canvas 設 `aria-hidden="true"`；所有文字可選取、可放大、可報讀。
7. **互動不擋路**：塗血互動不 pin 住頁面。讀者沒做就捲過去，場景自動補完三處血跡（`story.hyssop.auto = true`），故事照樣接下去。
8. **觸控**：只有在 `scene.interactiveRects()` 回傳的區域（牛膝草把手、門框）攔截觸控（`touch-action: none`），其他地方照常捲動。
9. **只有一個招牌高潮**（第二階段的「七的節奏」漩渦）。第一階段裡最強的時刻是「半夜」：其他轉場都要比它安靜。

## 4. 分鏡（cue → 畫面）

### 開場 `night-moon`（cue：title / month / day-10 / day-14）

- 夜空：大背景平面，`--jf-night` 平塗＋水平刻線，越往天頂越密；星星是刻線上挖掉的小白點。
- 月亮：刻線球體。光源方向由 `story.day`（1–14，連續）決定：初一是細鉤、十四是滿月；黃昏時亮面朝西（畫面右側）。月亮隨捲動從地平線升高。
- 地景：遠方低矮平頂的泥磚房（盒子＋門洞）、椰棗樹（圓柱樹幹＋片狀葉）、地平線。
- `month`：鏡頭下降，穿過前景的**大麥田**（instanced 細葉片＋穗頭，土黃色）；亞筆的字義是「結穗」，鏡頭停在青穗上。麥浪隨風擺動是裝飾性動態（`motionOff` 時停）。
- `day-10`：一家門口拴著一隻羊羔（低面數，刻線）。
- `day-14`：滿月；地平線下緣出現血紅色的黃昏暈染；畫面收在那扇門。
- DOM：大標題「耶和華的節期」與利23:2；右上角一個小日數牌「正月 初一 … 十四」，跟著 `story.day` 變化（`aria-live="polite"`，只在整數改變時更新）。

### 逾越節 `egypt-street`

- 構圖：前景是以色列人住的一排泥磚房（側視略帶角度），中間那間是主角的家：木門框（兩根門柱＋門楣）、門口地上一個盆、門邊一把牛膝草。遠處隔著田野是埃及人的城和山丘上的法老宮殿剪影，宮殿有火把。
- `dusk-street`：黃昏，門口有人影（剪影，不畫五官）。
- `hyssop`（**招牌互動**）：鏡頭推近正面看門。讀者按住牛膝草（一束細莖小葉，3D）拖動：拖進盆裡＝蘸血（葉尖變血紅、`hyssop-dip`）；拖到門楣／左門柱／右門柱並「打」上去（指標速度超過門檻或放開時在區域內）＝留下血跡（程序生成的潑濺貼圖，`hyssop-strike`）。三處都打過 → `hyssop-done`，鄰家的門框也陸續出現血跡。沒蘸血就打 → `hyssop-miss`（輕微抖動，不扣分）。互動徽章文字「按住拖曳」。
- `door-shut`：門關上（門板轉動）；門縫透出燈光（`--jf-glow`）。
- `meal`：一格室內分格（DOM 外框＋同一張 canvas 的另一個鏡頭，用 scissor 畫在分格範圍內）：一家人站著吃，腰間束帶、手拿杖；桌上有餅和一盤菜。人物一律剪影。
- `midnight`（**本階段最強的時刻**）：鏡頭拉遠到整條街，月亮在天頂。一片會流動的黑暗（噪聲遮罩）從畫面一側掃過整個大地；掃到有血的門時從門上方分開、繞過去。經文沒有描寫滅命的樣子：**不要畫成人形或天使**，只畫黑暗本身的移動。
- `wailing`：遠處埃及人的城一扇一扇窗熄燈；宮殿的火把熄滅。近景一扇亮著的窗裡，一個人影俯身在床邊。哀號聲（音效）。克制，不加血腥細節。
- `depart`：月光下，長長的人群隊伍（instanced 剪影，肩上扛著用布包著的摶麵盆）帶著羊群牛群往畫面左方走。走路照「長距離走路」規則：起步、到達用正常速度，中間的捲動段落加速。
- `vigil`：鏡頭仰起看天，月亮與星；隊伍在地平線上變成一條細線。
- `children`：直向刻線抹除轉場到「日後」：白天、應許之地的屋子，一個孩子拉著父親的衣角，指著門框。章末顯示「下一個節期：無酵節（正月十五日起，共七日）」。

## 5. 程式結構與分工

```
data/                 內容（主筆維護，工程端唯讀）
scripts/              建置腳本（資料子代理）
src/data/             types.ts（契約，主筆維護）、site.json（產物）、site.ts、links.ts
src/story/            state.ts（契約，主筆維護）、scroll.ts（介面子代理）
src/scene/            api.ts（契約，主筆維護）、其餘全部（場景子代理）
src/ui/、src/audio/、src/styles/、src/main.ts、index.html   介面子代理
public/audio/         CC0 音檔（主筆放）
public/fallback/      WebGL 不可用時的靜態插圖（之後由主筆用截圖腳本產生）
```

- 契約檔（`types.ts`、`state.ts`、`api.ts`）不得改；確實需要改就回報理由。
- 同一個檔案只屬於一個子代理。

## 6. 硬性規則（所有子代理）

- CSS class 一律 `jf-` 前綴。
- 不用 `scrollIntoView`；不做自動捲頁；不用 smooth-scroll 函式庫。
- `prefers-reduced-motion`：`story.motionOff = true` 時停掉風、紙紋閃動、鏡頭漂移、進場位移（改成淡入）；讀者觸發的動作（打門框、關門）照常完整播放。所有用到的 `dt` 夾在 `[0, 0.1]`。
- 建置一律用 PowerShell 跑 npm（Bash 跑 vite 會被應用程式控制擋住 rollup 原生模組）。
- 單一檔案輸出（vite-plugin-singlefile）。不在執行期 fetch 本機檔案（file:// 會被擋）；音檔用 `<audio>` 元素。
- 效能：DPR 上限 1.75（手機 1.5）；場景三角形數 < 150k；每幀不配置新物件；`document.hidden` 時停 render loop。
- 不得修改 `raw_data/`、`raw_scripture/`、`link_folder/`、`.tmp/`、`util/`，以及本專案以外的任何檔案。
- 交回時附：改了哪些檔案、`npm run typecheck`／`npm test` 的輸出、（場景與介面）headless Chrome 截圖路徑。截圖工具：scratchpad 的 `cdp.mjs`（`launch({ gpu: true })`、`shot()`、`evaluate()`），手機截圖要量 `[innerWidth, document.documentElement.scrollWidth]`。只關自己開的 Chrome（user-data-dir 前綴 `jfshoot-`）。
