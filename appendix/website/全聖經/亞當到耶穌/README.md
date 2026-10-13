# 從亞當到耶穌

以可縮放、可平移的家譜畫布呈現共同主線、馬太與路加的分線及可展開旁支。人物卡可查看親屬、家譜見證與經節全文；另有兩線對照、年歲時間軸、經文差異和新約家族頁面。網站使用 Vite 5、TypeScript、原生 DOM 與 SVG，d3-hierarchy 只負責旁支樹形排版。

## 本機啟動

```powershell
npm install
npm run dev        # http://127.0.0.1:3051/
npm run build      # 先跑型別檢查與資料閘門，再產生 dist/
npm run preview    # http://127.0.0.1:4201/
```

部署時只需 `dist/`。Vite 使用相對路徑，網站可放在子目錄。`?synthetic=1` 在 dev 模式載入合成壓力測試資料，正式 build 不會啟用。

## 頁面

| 頁面 | 內容 |
| --- | --- |
| 家譜樹 | SVG 主線與旁支；可拖曳、縮放、搜尋、展開，並沿父母或代數不詳的後裔關係往上追溯。 |
| 兩條線對照 | 按資料段落整理各份見證的名字；點名字回到家譜畫布。 |
| 年歲時間軸 | 以創世後年份呈現出生、死亡、生子時間與事件。 |
| 經文不同的地方 | 並列經節、引句、各家說法及來源網址。 |
| 新約家族 | 依 ntFamilies 的人物和親屬資料畫成小型家族圖。 |

## 資料

| 檔案 | 內容 |
| --- | --- |
| `src/data/genealogy.json` | 家譜人物、主線段落、見證、年歲、註記與導覽。 |
| `src/data/verses.json` | 上述家譜所用的經節全文。 |
| `src/data/types.ts` | 匯出 JSON 的 TypeScript 型別。 |
| `src/data/model.ts` | 資料查詢、關係圖、祖先路徑與 dev 合成資料。 |
| `src/data/data.test.ts` | 資料完整度與全展開版面測試；只從網站資料夾讀 JSON。 |

目前 JSON 由 `appendix/genealogy/build_genealogy.py` 的匯出功能產生：

```powershell
python appendix/genealogy/build_genealogy.py 亞當到耶穌 --export-json appendix/website/全聖經/亞當到耶穌/src/data
```

建置不會讀取 vault 其他檔案。更換正式資料時，以 genealogy.json 和 verses.json 為唯一輸入。
