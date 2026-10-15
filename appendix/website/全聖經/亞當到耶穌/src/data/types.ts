export type LineName = 'common' | '馬太' | '路加' | string;

export interface Relation {
  id: string;
  ref?: string;
  qualifier?: string;
  idQualifier?: string;
  who_ref?: string;
  role?: string;
  type?: string;
  rel?: string;
  note?: string;
  source?: string;
  [key: string]: unknown;
}

export interface NameForm {
  as: string;
  ref?: string;
  [key: string]: unknown;
}

export interface PersonMark {
  witness?: string;
  label: string;
  [key: string]: unknown;
}

export interface MaybeSamePerson {
  id: string;
  refs: string[];
}

export interface NameMeaning {
  orig: string;
  translit: string;
  strong: string;
  nameEn: string;
  meaningEn: string;
  meaningZh: string;
  via?: string;
  ref: string;
  scripture: Array<{ ref: string; quote: string }>;
}

export interface Person {
  id: string;
  name: string;
  qualifier?: string;
  sex?: string | null;
  kind?: string;
  names?: NameForm[];
  parents?: Relation[];
  spouses?: Relation[];
  siblings?: Relation[];
  kin?: Relation[];
  descends?: Relation[];
  maybeSame?: MaybeSamePerson[];
  desc?: string | null;
  note?: string | null;
  entry?: string | null;
  entryGloss?: string;
  mother_name?: string | null;
  gen?: Record<string, number>;
  lines?: LineName[];
  marks?: PersonMark[];
  notes?: string[];
  imported?: unknown;
  anchor?: string | null;
  nameMeaning?: NameMeaning | null;
  [key: string]: unknown;
}

export interface SpineSegment {
  id: string;
  title: string;
  lines: Record<string, string[]>;
}

export interface Spine {
  segments: SpineSegment[];
  lines: Record<string, string[]>;
}

export interface WitnessEntry {
  id?: string;
  name?: string;
  as?: string;
  ref?: string;
  qualifier?: string;
  [key: string]: unknown;
}

export interface Witness {
  id: string;
  title: string;
  ref?: string;
  line?: string;
  direction?: string;
  marks?: Record<string, string>;
  entries?: WitnessEntry[];
  [key: string]: unknown;
}

export interface AgePerson {
  id: string;
  born: number;
  died: number;
  total?: number;
  refs?: string[];
  [key: string]: unknown;
}

export interface Ages {
  people: AgePerson[];
  events: Array<Record<string, unknown>>;
  notes: Array<string | Record<string, unknown>>;
}

export interface NoteScripture {
  ref: string;
  quote?: string;
  [key: string]: unknown;
}

export interface NoteView {
  source?: string;
  quote?: string;
  translation?: string;
  paraphrase?: string;
  url?: string;
  [key: string]: unknown;
}

export interface GenealogyNote {
  id: string;
  title: string;
  attach?: string[];
  scripture?: NoteScripture[];
  text?: string;
  views?: NoteView[];
  [key: string]: unknown;
}

export interface TourStop {
  id: string;
  title: string;
  focus: string[];
  sequence?: string[];
  refs: string | string[];
  text: string;
}

export interface Family {
  id: string;
  title: string;
  roots?: string[];
  members?: string[];
  count?: number;
  intro?: string;
  imported?: unknown;
  [key: string]: unknown;
}

/** 大圖上的名單牌子（list）、同時代區域（region）、區域裡各家的牌子（family）。 */
export interface PlacementNode {
  id: string;
  kind: 'list' | 'region' | 'family';
  title: string;
  ref: string;
  under: string;
  basis: string;
  family?: string;
}

/** 主線往下接不到的一家，掛在哪裡；via 是畫在圖上的那條經文關係。 */
export interface PlacementItem {
  root: string;
  under: string;
  via: { from: string; to: string; kind: 'parent' | 'mother' | 'spouse' | 'sibling' | 'kin' | 'descends' } | null;
  side: 'same' | 'opposite';
}

export interface Placements {
  nodes: PlacementNode[];
  items: PlacementItem[];
}

export interface GenealogyData {
  persons: Person[];
  placements?: Placements;
  spine: Spine;
  witnesses: Witness[];
  ages: Ages;
  notes: GenealogyNote[];
  tour: TourStop[];
  families: Family[];
  ntFamilies: Family[];
  sources?: Array<Record<string, unknown>>;
}

export type VerseMap = Record<string, string>;

/**
 * 讀經模式的逐節標記。s/e 是經文裡的字元位置（左閉右開）。
 * k：p 人名（id 是人物；沒有 id 表示經文沒交代是哪一位，只在經文裡亮）、t 職稱（of 是屬於誰）、
 *    r 親屬詞、l 地名、n 數字。from：讀到這個人名時，從哪些人畫墨線過來（經文記載的父母或祖先）。
 */
export interface ReadingToken {
  s: number;
  e: number;
  k: 'p' | 't' | 'r' | 'l' | 'n';
  id?: string;
  of?: string;
  from?: string[];
  /** 倒著數的家譜：讀到這位父親時，畫到前面已經讀過的兒子 */
  to?: string[];
}

export interface ReadingVerse {
  v: number;
  text: string;
  t: ReadingToken[];
  /** 所屬段落的標題 */
  sec?: string;
  /** 這段經文是一塊名單牌子：沒有人名的節，鏡頭停在牌子上 */
  hold?: string;
  /** 讀經提醒（notes 的索引） */
  note?: number;
}

export interface ReadingChapter {
  n: number;
  title: string;
  verses: ReadingVerse[];
}

export interface ReadingData {
  book: string;
  bookName: string;
  chapters: ReadingChapter[];
  notes: Array<{ text: string; verses: string[] }>;
}
