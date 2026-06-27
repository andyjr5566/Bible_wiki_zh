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

## 📱 手機版 Obsidian + GitHub Sync 設置指南

使用 **GitHub Sync (Multi-Platform)** 外掛，在手機上無縫同步 GitHub 上的筆記。

### 前置準備

#### 1. 準備 GitHub Personal Access Token

**為什麼需要？** GitHub Sync 外掛需要透過 token 存取你的倉庫。

**取得 Token 步驟**：

1. 登入 [GitHub](https://github.com)
2. 點選右上角 **個人頭像** → **Settings**
3. 左側菜單 → **Developer settings**
4. 左側菜單 → **Personal access tokens** → **Tokens (classic)**
5. 2-4 步可以直接點這個連結省略: 🔑 [GitHub Token 生成](https://github.com/settings/tokens)
6. 點選 **Generate new token (classic)**
7. 填寫資訊：
   - **Note**: `Bible Wiki Obsidian Sync`（自訂名稱）
   - **Expiration**: 選擇過期時間（建議 90 days 或 No expiration）
7. **Select scopes** 勾選：
   - ✅ `repo`（完整倉庫存取）
   - ✅ `gist`（如需要）
8. 點選 **Generate token**
9. **複製 token**（只會顯示一次，遺失需重新生成）

**⚠️ 重要**：Token 像密碼一樣，不要分享給他人！

---

### 步驟 1️⃣：下載手機版 Obsidian

#### iOS
- 在 App Store 搜尋 **"Obsidian"**
- 下載官方應用（開發者：Dynalist Inc）

#### Android
- 在 Google Play 搜尋 **"Obsidian"**
- 下載官方應用

---

### 步驟 2️⃣：Create a Vault

#### iOS / Android 操作相同

1. **打開 Obsidian**
2. 點選 **Create new vault**
3. 輸入 Vault 名稱（例如：`Bible Wiki`）
4. 點選 **Create**
5. 等待 Vault 初始化完成

---

### 步驟 3️⃣：安裝 GitHub Sync 外掛（詳細步驟）

#### A. 打開外掛市場

1. 在 Obsidian 主畫面
2. 點選左下角 **設定圖示**（齒輪）
3. 選擇 **Community plugins**（或 **第三方外掛**）
4. 點選 **Browse**（或 **瀏覽**）

#### B. 搜尋 GitHub Sync

1. 搜尋框輸入：`GitHub Sync`
2. 找到 **"GitHub Sync (Multi-Platform)"**
   - 開發者：`Jackpotdever`
   - 圖示：GitHub 標誌

#### C. 安裝外掛

1. 點選該外掛
2. 點選 **Install**
3. 等待安裝完成（通常 5-10 秒）
4. 點選 **Enable**（啟用）
5. 外掛會立即出現在設定中

#### D. 驗證安裝成功

1. 回到主設定頁
2. 確認 **Community plugins** 清單中出現 **GitHub Sync**
3. 右上角應該出現 **GitHub Sync 按鈕**（類似雲端同步圖示）

---

### 步驟 4️⃣：填寫 GitHub 設定

#### A. 打開 GitHub Sync 設定

1. 點選左下角 **設定圖示**（齒輪）
2. 向下滑找到 **"GitHub Sync"** 設定區
3. 或點選右上角 **GitHub Sync 按鈕** → 選擇 **Settings**

#### B. 填寫必要欄位

填寫以下四個欄位：

| 欄位 | 值 | 說明 |
|------|-----|------|
| **Owner** | `andyjr5566` | GitHub 使用者名稱 |
| **Repo** | `Bible_wiki_zh` | GitHub 倉庫名稱 |
| **Branch** | `main` | 分支名稱（預設通常是 main） |
| **Token** | `ghp_xxxxxxxxxxxx...` | 你的 Personal Access Token |

**具體填寫**：

```
Owner: andyjr5566
Repo: Bible_wiki_zh
Branch: main
Token: [貼上你複製的 token]
```

#### C. 驗證設定

1. 填完後點選 **Test Connection**（若有此按鈕）
2. 或直接進行同步測試

---

### 步驟 5️⃣：同步筆記（操作方式）

#### 操作 A：手動同步（最常用）

1. **拉取最新版本**（從 GitHub 下載）
   - 右上角 **GitHub Sync 按鈕** → **Pull**
   - 或 Command Palette（搜尋） → 搜尋 `GitHub Sync: Pull`
   - 等待同步完成（通常 5-30 秒）

2. **上傳你的編輯**（推送到 GitHub）
   - 右上角 **GitHub Sync 按鈕** → **Push**
   - 或 Command Palette → 搜尋 `GitHub Sync: Push`
   - 輸入 commit message（例如：`Update notes from mobile`）
   - 等待上傳完成

#### 操作 B：自動同步（可選）

在 GitHub Sync 設定中：

1. 啟用 **Auto Pull**（自動拉取）
   - 間隔時間：建議 5-10 分鐘
   - 手機會自動從 GitHub 下載最新版本

2. 啟用 **Auto Push**（自動推送）
   - 每次編輯後自動上傳
   - ⚠️ 會產生大量 commit，謹慎使用

#### 操作 C：一鍵同步

某些版本有 **Sync All** 按鈕：
- 同時執行 Pull + Push
- 快速同步最新狀態

---

### 手機版 Obsidian 基本操作

| 功能 | 操作 |
|------|------|
| 打開檔案 | 點左上角 **≡ 菜單** → 瀏覽資料夾 |
| 快速搜尋 | 點搜尋圖示 → 輸入關鍵字 |
| 點擊 wiki-link | 直接點藍色連結 |
| 返回上一頁 | 向右滑動 或 點 **< 返回** |
| 編輯筆記 | 點 **編輯** 按鈕或雙擊 |
| 查看圖譜 | 右上角 **圖譜** 按鈕 |
| 同步 GitHub | 右上角 **GitHub Sync** 按鈕 |

---

## ❓ 常見問題

### Q1: 我不懂 Git，能用嗎？

**A**: 完全可以。使用 GitHub Sync 外掛後，你不需要懂 Git 指令。只需按 **Pull** 和 **Push** 按鈕即可。

---

### Q2: Token 過期了怎麼辦？

**A**: 
1. 重新生成 token（同上面的步驟）
2. 更新 GitHub Sync 設定中的 Token
3. 重新測試連線

---

### Q3: 同步出錯怎麼辦？

**A**:
1. 檢查網路連線
2. 確認 Token 正確且未過期
3. 確認 Owner、Repo、Branch 資訊無誤
4. 嘗試手動 Pull 一次
5. 查看 Obsidian 的錯誤日誌

---

### Q4: 能否自動同步？

**A**: 可以。在 GitHub Sync 設定中啟用 **Auto Pull** 或 **Auto Push**，但建議謹慎使用 Auto Push 以避免過多 commit。

---

### Q5: 手機和電腦編輯同一個文件會有衝突嗎？

**A**: 
- 若同時編輯，先 Push 的版本會被保留，後 Push 的需要手動解決衝突
- 建議：編輯完一個檔案後立即 Push，避免衝突

---

### Q6: 資料在哪裡更新？

**A**: 
- 所有聖經內容 → `各書卷資料夾/第X章.md`
- 所有知識節點 → `link_folder/分類/*.md`

在手機版 Obsidian 中，同樣可以編輯這些檔案。

---

### Q7: 我能離線使用嗎？

**A**: 是的。一旦 Pull 下來，你可以離線閱讀所有筆記。編輯後有網路時再 Push 上傳。

---

## 🤝 貢獻指南

### 貢獻類型

| 類型 | 說明 |
|------|------|
| 📝 新章節 | 新增尚未整理的聖經章節 |
| ✏️ 更新章節 | 補充或修正既有章節 |
| 🔗 新知識節點 | 在 link_folder 建立新條目 |
| 🐛 修復 | 修正破損連結、錯字、格式問題 |
| 📖 文檔 | 改進 README、scheme.md、評論 |

### 提交步驟（電腦版）

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

### 提交步驟（手機版）

1. 在手機 Obsidian 編輯筆記
2. 完成編輯後，點右上角 **GitHub Sync**
3. 點 **Push**
4. 輸入 commit message（例如：`Update from mobile`）
5. 完成上傳

---

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

2. **檢查 GitHub Sync 設定**
   - 確認 Owner、Repo、Branch 正確
   - 確認 Token 未過期
   - 嘗試測試連線

3. **檢查網路連線**
   - 確認手機/電腦已連線網路
   - 檢查防火牆設定

4. **提交 Issue**
   - [GitHub Issues](https://github.com/andyjr5566/Bible_wiki_zh/issues)
   - 詳細描述問題、操作步驟、預期結果

5. **Obsidian 官方支援**
   - 官方文檔：https://help.obsidian.md/
   - 社群論壇：https://forum.obsidian.md/

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

感謝 **GitHub Sync (Multi-Platform)** 外掛開發者！

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
- 📱 [Obsidian 官網](https://obsidian.md/)
- 📚 [Obsidian 官方文檔](https://help.obsidian.md/)
- 🔑 [GitHub Token 生成](https://github.com/settings/tokens)

---

**祝你使用愉快！願聖經研讀之路越走越寬。** 📖✨
