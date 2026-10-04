import { DB, chapterHref, entryHref, groupOfLaw, groupOfTopic, lawsOfEntry, RELATION_LABEL, refText, relationsOf, topicsOf } from '../data/db';
import type { Evidence, Law, Relation, Topic } from '../data/types';
import { href } from '../router';
import { store } from '../store';
import { ext, h, type Child } from './dom';
import { lbl } from './more';
import { openPeek } from './peek';

/** 條目類型 → CSS 用的英文代號（顏色在 styles.css） */
export const TYPE_KEY: Record<string, string> = {
  人物: 'person', 地點: 'place', 事件: 'event', 主題: 'topic', 神學: 'theology', 背景: 'background',
  文化: 'culture', 歷史: 'history', 原文: 'original', 互文: 'intertext', 解經爭議: 'debate',
};
/** 入門層的白話類型名稱 */
export const TYPE_PLAIN: Record<string, string> = {
  人物: '人物', 地點: '地方', 事件: '事件', 主題: '主題', 神學: '信仰觀念', 背景: '時代背景',
  文化: '當時的文化', 歷史: '歷史', 原文: '原文字詞', 互文: '經文對照', 解經爭議: '各家看法不同',
};
export const typeKey = (title: string) => TYPE_KEY[DB.entries[title]?.type ?? ''] ?? 'topic';
const typeName = (type: string) => lbl(TYPE_PLAIN[type] ?? type, type);

/** 條目小卡：名稱、類型、一句簡介、本站的反查、連到完整條目。不搬條目內容。 */
export function entryPeekContent(title: string): Child[] {
  const info = DB.entries[title];
  const n = lawsOfEntry(title).length;
  return [
    h('div', { class: `lm-peek-type lm-t-${typeKey(title)}` }, typeName(info?.type ?? '')),
    h('h3', { class: 'lm-peek-title' }, title),
    info?.gist ? h('p', { class: 'lm-peek-gist' }, info.gist) : null,
    h('div', { class: 'lm-peek-actions' },
      n ? h('a', { href: href('entry', title) }, `提到它的律法（${n} 條）`) : null,
      ext(entryHref(title), '查看完整條目（另開網頁）')),
  ];
}

/** 條目按鈕：點了開小卡 */
export function entryChip(title: string, label: Child = title): HTMLButtonElement {
  const b = h('button', { type: 'button', class: `lm-chip lm-entry lm-t-${typeKey(title)}` }, label);
  b.addEventListener('click', () => openPeek(b, ...entryPeekContent(title)));
  return b;
}

/** 把文字裡的術語（glossary.yaml）包成可點的虛線字，點了開條目小卡 */
export function glossText(text: string): Child[] {
  if (!DB.glossary.length) return [text];
  const terms = DB.glossary.map((g) => g.term).sort((a, b) => b.length - a.length);
  const re = new RegExp(`(${terms.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})`, 'g');
  return text.split(re).map((part, i) => {
    if (i % 2 === 0) return part;
    const entry = DB.glossary.find((g) => g.term === part)!.entry;
    const b = h('button', { type: 'button', class: 'lm-term' }, part);
    b.addEventListener('click', () => openPeek(b, ...entryPeekContent(entry)));
    return b;
  });
}

export const groupColor = (l: Law) => `var(--g${groupOfLaw(l)?.color ?? 0})`;

export function topicChip(t: Topic): HTMLAnchorElement {
  const g = groupOfTopic(t.id);
  return h('a', { class: 'lm-chip lm-topic', href: href('topic', t.id), style: `--c: var(--g${g?.color ?? 0})` }, lbl(t.plain, t.name));
}

export function lawLink(l: Law, label: Child = l.title): HTMLAnchorElement {
  return h('a', { href: href('law', l.id), class: 'lm-law-link' }, label);
}

/** 條文卡：入門給標題＋白話說明；查經起加上主題與「別卷又說了一次」 */
export function lawCard(l: Law, opts: { showSummary?: boolean } = {}): HTMLElement {
  const rels = relationsOf(l.id);
  return h('article', { class: 'lm-card', style: `--c: ${groupColor(l)}` },
    h('div', { class: 'lm-card-head' }, lawLink(l, h('span', { class: 'lm-card-title' }, l.title)), h('span', { class: 'lm-ref' }, refText(l))),
    opts.showSummary !== false ? h('p', { class: 'lm-card-sum' }, l.summary) : null,
    store.atLeast('study') ? h('div', { class: 'lm-card-meta' }, ...topicsOf(l).map(topicChip)) : null,
    rels.length
      ? h('div', { class: 'lm-card-rels' }, ...rels.map(({ rel, other }) => h('a', { class: `lm-rel lm-rel-${rel.type}`, href: href('law', other.id), title: RELATION_LABEL[rel.type][2] }, '↔ ', refText(other), store.atLeast('study') ? h('span', { class: 'lm-rel-type' }, lbl(...RELATION_LABEL[rel.type])) : null)))
      : null,
  );
}

/** 證據：一句話＋連到出處（條目或章節的公開網頁）；研究層才顯示引句 */
export function evidenceLine(ev: Evidence): HTMLElement {
  const link = ev.kind === 'entry'
    ? ext(entryHref(ev.title), `知識庫條目「${ev.title}」`)
    : ext(chapterHref(ev.book, ev.chapter), `${ev.book}第${ev.chapter}章的本章整理`);
  return h('div', { class: 'lm-evidence' },
    h('span', { class: 'lm-evidence-src' }, '依據：', link),
    store.atLeast('research') ? h('q', { class: 'lm-quote' }, ev.quote) : null);
}

export function relationRow(rel: Relation, other: Law): HTMLElement {
  return h('li', { class: `lm-relrow lm-rel-${rel.type}` },
    h('div', null, h('span', { class: 'lm-rel-type' }, lbl(...RELATION_LABEL[rel.type])), ' ', lawLink(other), ' ', h('span', { class: 'lm-ref' }, refText(other))),
    evidenceLine(rel.evidence));
}
