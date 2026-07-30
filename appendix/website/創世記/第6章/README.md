# 創世記第六章 — 挪亞方舟沉浸式滾動網站

## 簡介

本專案是一個以創世記第六章為主題的沉浸式滾動敘事（scrollytelling）網站，透過 3D 模型、動畫、音效與互動元件，重現挪亞方舟的故事。

## 技術棧

- **React 18** + **Vite 5** — 前端框架與建置工具
- **Three.js** + **@react-three/fiber** + **@react-three/drei** — 3D 方舟模型
- **GSAP** + **ScrollTrigger** — 滾動動畫與釘選區段
- **Framer Motion** — 微互動與浮動動畫
- **Tailwind CSS 3** — 樣式系統
- **Howler.js** — 環境音效
- **Lucide React** — 圖示庫

## 設計色彩

| Token | Hex | 用途 |
|-------|-----|------|
| `wood-dark` | `#1c130b` | 深色背景 |
| `wood-primary` | `#3e2723` | 木材主色 |
| `gold-divine` | `#d4af37` | 神聖金色 |
| `parchment` | `#fcf8f2` | 羊皮紙文字 |
| `deluge-dark` | `#0a1118` | 洪水深色 |

## 六個章節

1. **Hero** — 神聖警告開場
2. **Dimensions** — 3D 方舟視覺化與比例對照
3. **Construction** — 建造藍圖
4. **Boarding** — 橫向滾動登舟
5. **Storm** — 大洪水暴風雨
6. **Peace** — 鴿子與彩虹立約

## 安裝與執行

```bash
cd appendix/website/創世記/第6章
npm install
npm run dev
```

瀏覽器開啟 `http://localhost:5173`

## 建置

```bash
npm run build
npm run preview
```

## 字體

- **Noto Serif TC** — 標題與正文
- **Noto Sans TC** — UI 元素

## 授權

本專案為聖經知識庫附屬網站，供教育用途。
