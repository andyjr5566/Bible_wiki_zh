# 📖 聖經研讀知識庫 (Bible Wiki ZH)

這是一套**基於 Obsidian 的聖經研讀知識庫系統**，透過結構化的筆記與 wiki-link，建立可逐章累積、跨卷連結的聖經學習網絡。

---

## 🎯 這個專案是什麼？

一套完整的聖經研讀工具，整合：
- 📜 經文內容（來自 cnbible）
- 📚 多來源註解與拾穗（ccbiblestudy、KingComments、BibleHub）
- 🔗 自動化 wiki-link 系統
- 📂 跨章節、跨卷書的知識節點庫
- ✅ 驗證工具（確保連結完整性）

**核心特點**：資料驅動，不臆測 —— 所有 wiki-link 都由實際收集的資料觸發。

---

## 🚀 快速開始（5 分鐘）

### 第 1 步：安裝 Obsidian

#### Windows / macOS / Linux
1. 訪問 [Obsidian 官網](https://obsidian.md)
2. 點選 **Download** → 選擇你的作業系統
3. 安裝完成後打開 Obsidian

---

### 第 2 步：取得本專案檔案

選擇 **其中一種** 方法：

#### 方式 A：使用 Git Clone（推薦程式開發者）

**前置需求**：已安裝 Git

```bash
# 打開終端機（Terminal / PowerShell）
git clone https://github.com/andyjr5566/Bible_wiki_zh.git

# 進入資料夾
cd Bible_wiki_zh
```

**優點**：
- 未來可用 `git pull` 快速更新
- 便於參與開發與貢獻

---

#### 方式 B：直接下載 ZIP（推薦普通使用者）

1. 進入 [GitHub 專案頁面](https://github.com/andyjr5566/Bible_wiki_zh)
2. 點選綠色按鈕 **Code**
3. 點選 **Download ZIP**
4. 解壓到任意位置，例如：
   - Windows: `C:\Users\YourName\Documents\Obsidian\Bible_wiki_zh`
   - macOS: `~/Documents/Obsidian/Bible_wiki_zh`
   - Linux: `~/Documents/Obsidian/Bible_wiki_zh`

**優點**：
- 無需安裝 Git
- 操作簡單直觀

---

### 第 3 步：在 Obsidian 打開本專案

#### A. 打開 Obsidian

Obsidian 啟動時會顯示 Vault 選擇畫面。

#### B. 建立或打開 Vault

| 步驟 | 操作 |
|------|------|
| 1 | 左下角點選 **Open folder as vault** |
| 2 | 選擇你放置 `Bible_wiki_zh` 的資料夾 |
| 3 | 確認後 Obsidian 會掃描並載入所有 markdown 檔案 |

```
選擇資料夾示意：
📁 Obsidian/
 └─ 📁 Bible_wiki_zh/  ← 選這個
    ├── README.md
    ├── scheme.md
    ├── 何西阿書/
    ├── 但以理書/
    ├── link_folder/
    └── ...
```

#### C. 允許 Obsidian 信任此 Vault

- Obsidian 會提示 **"This vault may use plugins and community scripts"**
- 點選 **Trust author and enable plugins**（或 Trust plugin）

---

### 第 4 步：開始使用

現在你可以在 Obsidian 中：

1. **瀏覽聖經書卷**
   - 左側檔案欄 → 何西阿書 → 第1章.md

2. **查看 wiki-link**
   - 點選任何藍色連結（如 `[[何西阿]]`）
   - 自動跳轉至對應條目

3. **查看知識圖譜**
   - 右上方 **圖譜檢視** 可視化所有連結關係

4. **搜尋內容**
   - `Ctrl + P`（Windows）或 `Cmd + P`（macOS）快速搜尋任何檔案或內容

---

## 📚 資料夾結構說明

```
Bible_wiki_zh/
│
├── README.md                    ← 你現在看的檔案
├── scheme.md                    ← 核心規則文檔（必讀）
├── agent_prompt.md              ← AI 助手提示詞（開發用）
│
├── 何西阿書/                     ← 書卷資料夾
│   ├── 全書導論.md
│   ├── 全書綱要.md
│   ├── 第1章.md                ← 整合型章節主檔
│   ├── 第2章.md
│   └── .tmp/                   ← 暫存資料（協作用）
│
├── 但以理書/                     ← 另一個書卷
│   ├── 全書導論.md
│   ├── 全書綱要.md
│   ├── 第1章.md
│   └── ...
│
├── link_folder/                 ← 全域知識節點庫
│   ├── _index/
│   │   └── link_index.json     ← 條目索引
│   ├── 人物/                   ← 聖經人物
│   │   ├── 何西阿.md
│   │   ├── 歌篾.md
│   │   └── ...
│   ├── 地點/                   ← 地理位置
│   ├── 主題/                   ← 神學主題
│   ├── 背景/                   ← 歷史背景
│   ├── 歷史/                   ← 歷史事件
│   ├── 原文/                   ← 原文字義
│   ├── 文化/                   ← 文化習俗
│   ├── 神學/                   ← 神學觀點
│   ├── 互文/                   ← 新舊約連結
│   ├── 解經爭議/                ← 解經爭點
│   └── _待分類/                ← 暫存待分類
│
├── verify_links.py              ← 驗證工具（開發用）
├── link_quality_check.py        ← 品質檢查（開發用）
├── build_link_index.py          ← 索引生成（開發用）
├── _config/                     ← 設定檔
│   └── bible_books.json        ← 聖經書卷章數表
│
└── .git/                        ← Git 版本控制（若用 clone）
```

### 重點資料夾說明

| 資料夾 | 用途 | 對誰重要 |
|--------|------|---------|
| `何西阿書/`、`但以理書/` 等 | 儲存逐章整合筆記 | 所有使用者 |
| `link_folder/` | 跨章累積的知識節點 | 所有使用者 |
| `.tmp/` | 暫存協作檔案 | 開發者 |
| `*.py` | 驗證與維護工具 | 開發者 |
| `_config/` | 系統設定 | 開發者 |

---

## 📖 如何使用

### 1. 閱讀聖經章節

```
1. 左側檔案欄 → 何西阿書 → 第1章.md
2. 看到完整經文 + 註解 + wiki-link
3. 點選任何藍色 [[link]] 查看相關條目
```

### 2. 查閱知識節點

每個條目（如 `link_folder/人物/何西阿.md`）包含：
- 定義與基本資料
- 聖經出現位置
- 與各章節的關聯
- 神學意義
- 相關條目

### 3. 探索知識圖譜

**Obsidian 內置圖譜檢視**（Graph View）：
- 右上角按鈕 → **圖譜檢視**
- 視覺化所有 wiki-link 連結
- 可拖拽、縮放、篩選

### 4. 快速搜尋

| 功能 | 快捷鍵 |
|------|--------|
| 搜尋檔案名稱 | `Ctrl + P`（Windows）/ `Cmd + P`（macOS） |
| 搜尋內容 | `Ctrl + Shift + F` / `Cmd + Shift + F` |
| 開啟快速切換 | `Ctrl + O` / `Cmd + O` |

---

## ❓ 常見問題

### Q1: 我不懂 Git，能用嗎？

**A**: 完全可以。直接下載 ZIP 即可，無需 Git。但如果未來想接收更新，建議學習 `git pull`。

---

### Q2: 資料在哪裡更新？

**A**: 
- 所有聖經內容 → `各書卷資料夾/第X章.md`
- 所有知識節點 → `link_folder/分類/*.md`

你可以在 Obsidian 中直接編輯這些檔案。

---

### Q3: 我能離線使用嗎？

**A**: 是的。本專案是純本地 markdown + Obsidian，無需網路。

---

### Q4: 支援哪些聖經譯本？

**A**: 目前預設為**和合本 (CUV)** 繁體版。其他譯本支援正在規劃。

---

### Q5: 我想參與開發，怎麼開始？

**A**: 
1. Fork 本專案
2. 新建 branch：`git checkout -b feature/your-feature`
3. 遵照 [`scheme.md`](./scheme.md) 規則製作
4. 執行驗證工具
5. 提交 Pull Request

詳見 [貢獻指南](#貢獻指南)

---

## 🤝 貢獻指南

### 貢獻類型

| 類型 | 說明 |
|------|------|
| 📝 新章節 | 新增尚未整理的聖經章節 |
| ✏️ 更新章節 | 補充或修正既有章節 |
| 🔗 新知識節點 | 在 link_folder 建立新條目 |
| 🐛 修復 | 修正破損連結、錯字、格式問題 |
| 📖 文檔 | 改進 README���scheme.md、評論 |

### 提交步驟

```bash
# 1. Fork 本專案（GitHub 網站點擊 Fork）

# 2. Clone 你的 fork
git clone https://github.com/YOUR_USERNAME/Bible_wiki_zh.git
cd Bible_wiki_zh

# 3. 新建分支
git checkout -b feature/add-hosea-chapter-2

# 4. 編輯檔案（在 Obsidian 中編輯內容）

# 5. 執行驗證
python3 verify_links.py
python3 link_quality_check.py

# 6. 提交
git add .
git commit -m "Add Hosea chapter 2 integrated note"

# 7. 推送
git push origin feature/add-hosea-chapter-2

# 8. 在 GitHub 提交 Pull Request
```

### 命名規範

| 對象 | 規範 | 例子 |
|------|------|------|
| Branch | `feature/description` 或 `fix/description` | `feature/add-hosea-chapter-1` |
| Commit message | 英文，述詞開頭 | `Add Hosea chapter 1 note` |
| 檔案名 | 中文（聖經書卷）、英文或數字（系統檔案） | `第1章.md`、`verify_links.py` |

---

## 📞 技術支援

### 遇到問題？

1. **檢查 Obsidian 設定**
   - 確認 Vault 已正確開啟
   - 確認已信任此 Vault（允許外掛與腳本）

2. **檢查檔案編碼**
   - 本專案使用 UTF-8 編碼
   - 若檔案顯示亂碼，嘗試重新開啟

3. **查看驗證工具輸出**
   - 執行 `verify_links.py` 檢查破損連結
   - 執行 `link_quality_check.py` 檢查品質問題

4. **提交 Issue**
   - [GitHub Issues](https://github.com/andyjr5566/Bible_wiki_zh/issues)
   - 詳細描述問題、操作步驟、預期結果

---

## 📄 許可證

本專案採用 **MIT License**。詳見 [LICENSE](./LICENSE) 檔案。

---

## 🙏 致謝

感謝以下資料來源：

- **cnbible.com** — 和合本經文
- **ccbiblestudy.org** — 查經資料大全
- **KingComments** — 聖經批註
- **BibleHub** — 聖經研究工具

感謝所有貢獻者！

---

## 📝 相關檔案

| 檔案 | 說明 |
|------|------|
| [`scheme.md`](./scheme.md) | 完整規則與工作流程文檔（必讀） |
| [`agent_prompt.md`](./agent_prompt.md) | AI 助手提示詞（開發用） |
| `_config/bible_books.json` | 聖經書卷章數配置 |

---

## 🌟 快速連結

- 🏠 [GitHub 專案](https://github.com/andyjr5566/Bible_wiki_zh)
- 📖 [核心規則文檔](./scheme.md)
- 🐛 [報告問題](https://github.com/andyjr5566/Bible_wiki_zh/issues)
- 🔧 [技術討論](https://github.com/andyjr5566/Bible_wiki_zh/discussions)

---

**祝你使用愉快！願聖經研讀之路越走越寬。** 📖✨
