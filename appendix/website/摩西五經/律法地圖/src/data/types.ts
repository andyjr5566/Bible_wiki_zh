/** src/data/explorer.json 的形狀（由 scripts/build-data.mjs 產生，不手改） */

export type Range = [number, number];
export type RelationType = 'parallel' | 'supplement' | 'case' | 'cites';
export type Depth = 'basic' | 'study' | 'research';

export interface Book {
  abbr: string;
  name: string;
  num: number;
  chapters: number;
  /** 全書目錄的法典段落，例「聖潔法典（17-27 章）」 */
  codes: { title: string; from: number; to: number }[];
}

export interface Group {
  id: string;
  name: string;
  plain: string;
  color: number;
  topics: string[];
}

export interface Topic {
  id: string;
  name: string;
  plain: string;
  group: string;
  entry?: string;
}

export interface Section {
  id: string;
  book: string;
  chapter: number;
  title: string;
  from: number;
  to: number;
  code?: string;
  laws: string[];
}

export interface Law {
  id: string;
  title: string;
  book: string;
  chapter: number;
  refs: Range[];
  topics: string[];
  summary: string;
  basis: number[];
  entries: string[];
  section: string;
}

export interface VerseLink {
  /** 片語在該節經文裡的起訖字元位置 */
  s: number;
  e: number;
  target: string;
}

export interface EntryInfo {
  type: string;
  /** 條目定義的第一句（≤40 字），只用來簡單提一下 */
  gist: string;
}

export type Evidence =
  | { kind: 'entry'; title: string; quote: string }
  | { kind: 'chapter'; book: string; chapter: number; quote: string };

export interface Relation {
  from: string;
  to: string;
  type: RelationType;
  evidence: Evidence;
}

export interface Tour {
  id: string;
  title: string;
  intro: string;
  stops: string[];
}

export interface Coverage {
  book: string;
  chapter: number;
  total: number;
  covered: number;
  excluded: number;
  missing: Range[];
}

export interface Explorer {
  version: number;
  books: Book[];
  groups: Group[];
  topics: Topic[];
  sections: Section[];
  laws: Law[];
  /** key：「出21:2」 */
  verses: Record<string, string>;
  links: Record<string, VerseLink[]>;
  entries: Record<string, EntryInfo>;
  relations: Relation[];
  tours: Tour[];
  glossary: { term: string; entry: string }[];
  coverage: Coverage[];
}
