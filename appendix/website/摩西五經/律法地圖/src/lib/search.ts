import { DB, laws, lawVerses, refText } from '../data/db';
import type { Law, Topic } from '../data/types';
import { parseQueryRef, refHits } from './refs';

export interface SearchResults {
  ref: { label: string; laws: Law[] } | null;
  laws: Law[];
  topics: Topic[];
  entries: string[];
}

const norm = (s: string) => s.replace(/\s+/g, '').toLowerCase();

/** 全站搜尋：經文參照、條文（標題／說明／經文）、主題、條目 */
export function search(q: string, limit = 8): SearchResults {
  const text = norm(q);
  const empty: SearchResults = { ref: null, laws: [], topics: [], entries: [] };
  if (!text) return empty;
  const r = parseQueryRef(q);
  const ref = r ? { label: `${r.book} ${r.chapter}${r.from ? `:${r.from}${r.to !== r.from ? `-${r.to}` : ''}` : ' 章'}`, laws: laws.filter((l) => refHits(r, l)) } : null;
  const hitLaw = (l: Law) =>
    norm(l.title).includes(text) || norm(l.summary).includes(text) || norm(refText(l)).includes(text) || lawVerses(l).some((v) => v.text.includes(q.trim()));
  return {
    ref,
    laws: r ? [] : laws.filter(hitLaw).slice(0, limit),
    topics: DB.topics.filter((t) => norm(t.name).includes(text) || norm(t.plain).includes(text)).slice(0, limit),
    entries: Object.keys(DB.entries).filter((e) => norm(e).includes(text)).slice(0, limit),
  };
}
