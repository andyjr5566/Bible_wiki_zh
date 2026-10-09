/**
 * 網站資料契約：scripts/build-data.mjs 讀 data/*.yaml 與 vault，產生 src/data/site.json。
 * 經文、註釋原站網址、STEP 原文欄位都由腳本從 vault 抽出，不在 yaml 手打。
 */

/** 一段經文：「出12:21-28」→ 每節一行，文字只取自 raw_scripture */
export interface VerseBlock {
  ref: string; // 顯示用，例如「出12:21-28」
  book: string; // 出埃及記
  chapter: number;
  from: number;
  to: number;
  lines: { v: number; text: string }[];
}

export type SourceId = 'CT' | 'GT' | 'KC' | 'BH';

/** 一則註釋：逐字引文（quote）和具名轉述（paraphrase）至少有一個 */
export interface CommentaryNote {
  id: string;
  source: SourceId;
  /** 讀者看到的出處名稱，例如「黃迦勒《出埃及記註解》」或「《丁道爾聖經註釋》」 */
  work: string;
  /** 原站名稱，例如「ccbiblestudy 逐節註解」 */
  site: string;
  /** 原站網址：腳本從該章 source_manifest.md 抽出 */
  url: string;
  book: string;
  chapter: number;
  /** 註釋談的是哪一節（顯示用），例如「出12:22」 */
  verse: string;
  /** 逐字引文；英文來源（KC、BH）時是英文原句 */
  quote?: string;
  /** 英文引文的中譯（顯示在引文後的括號裡）；中文來源不填 */
  quoteZh?: string;
  /** 具名轉述（網站自己的話，不加引號） */
  paraphrase?: string;
}

/** 一個原文關鍵字：除了 label 和 note，其餘欄位都由腳本從 STEP raw 抽出 */
export interface StepWord {
  id: string;
  /** 和合本裡的中文字詞，例如「逾越節」 */
  label: string;
  ref: string; // 出12:11
  position: number; // STEP 表格的 #
  hebrew: string; // STEP「原文」欄，逐字照抄（含重音符號）
  translit: string;
  gloss: string; // Context gloss
  strong: string; // Extended Strong
  morph: string; // 詞形代碼
  morphText: string; // 詞形說明（英文，照 STEP）
  lexicon: string; // Brief lexicon
  /** 網站自己的說明：先寫 STEP 能確認的，再寫「部分註釋進一步理解為……」 */
  note: string;
}

export interface EntryLink {
  title: string;
  type: string; // link_folder 的資料夾名，例如「歷史」
  gist: string; // 條目「## 定義」第一句，最多 40 字
}

export type Palette = {
  paper: string; // 紙色
  ink: string; // 主墨（深色）
  accent: string; // 第二色墨（例如血紅）
  glow: string; // 光（月光、燈火）
};

export interface Beat {
  id: string;
  /** 場景提示：場景渲染器據此切換畫面狀態，例如「moon-day-10」「hyssop」「midnight」 */
  cue: string;
  /** 這一拍的主經文（顯示全文），例如「出12:22」 */
  verse?: string;
  /** 網站自己的白話敘述 */
  text: string;
  /** 互動提示文字（有互動的拍才有） */
  prompt?: string;
  interaction?: 'hyssop';
  /** 這一拍就地展開的註釋 id */
  notes?: string[];
  /** 這一拍可點開的原文字 id */
  words?: string[];
  /** 這一拍屬於「經文自己交代的理由」 */
  reason?: boolean;
  /** 開場用：這一拍月亮對應的日子（1–14） */
  day?: number;
}

export interface StoryChapter {
  id: string; // opening、passover……
  kind: 'opening' | 'feast';
  title: string;
  /** 經文給的日期，例如「正月十四日黃昏」 */
  date?: string;
  month?: number;
  day?: number;
  scene: string; // night-moon、egypt-street……
  palette: Palette;
  beats: Beat[];
  /** 主要經文（可展開全文），例如 ["出12:1-14", "利23:5"] */
  passages: string[];
  /** 延伸閱讀的知識庫條目（正式標題） */
  entries: string[];
  /** 新約應驗：卡片底部的一行連結 */
  nt: string[];
  /** 章末的「下一個節期」預告（只放名稱與日期） */
  next?: { title: string; date: string };
}

export interface AudioSource {
  id: string;
  file: string; // public/audio/ 底下的檔名
  title: string;
  author: string;
  license: 'CC0';
  page: string; // 來源頁網址（主要來源）
  /** 混音用到多個來源時，全部來源頁（含 page） */
  pages?: string[];
  downloaded: string; // YYYY-MM-DD
  loop?: boolean;
  /** 做了哪些剪輯（給授權頁） */
  edit?: string;
}

export interface SiteData {
  title: string;
  motto: VerseBlock;
  chapters: StoryChapter[];
  verses: Record<string, VerseBlock>; // key 是 yaml 裡寫的參照字串
  commentary: Record<string, CommentaryNote>;
  step: Record<string, StepWord>;
  entries: Record<string, EntryLink>;
  audio: AudioSource[];
  /** 授權頁：每章用到的來源與網址 */
  sources: { book: string; chapter: number; source: SourceId | 'STEP'; site: string; url: string }[];
}
