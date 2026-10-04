import { bookByAbbr, chapterHref, DB, lawById } from '../data/db';
import type { Book, Section } from '../data/types';
import { href, type Route } from '../router';
import { lawCard } from '../ui/cards';
import { ext, h } from '../ui/dom';
import { lbl } from '../ui/more';

/** #/book/出：依法典段落 → 章 → 律法段落 → 條文 */
export function bookView(route: Route): HTMLElement {
  const b = bookByAbbr.get(route.params[0]);
  if (!b) return notFound();
  return h('div', { class: 'lm-page lm-book-page' },
    h('header', { class: 'lm-page-head' }, h('h1', null, b.name), h('p', { class: 'lm-lede' }, lbl('這一卷收錄的律法，依段落排列。', '依全書目錄的法典段落、章、律法段落排列。'))),
    ...codesOf(b).map(({ title, sections }) => h('section', { class: 'lm-code' },
      title ? h('h2', null, title) : null,
      ...chapters(sections).map(([ch, secs]) => h('section', { class: 'lm-chapter' },
        h('h3', null, h('a', { href: href('ref', `${b.abbr}${ch}`) }, `第${ch}章`)),
        ...secs.map(sectionBlock))))),
    DB.sections.some((s) => s.book === b.name) ? null : h('p', { class: 'lm-muted' }, '這一卷還沒有收錄條文。'));
}

/** #/ref/出21：從章節附錄連過來時落在這裡 */
export function refView(route: Route): HTMLElement {
  const m = /^(創|出|利|民|申)(\d+)$/.exec(route.params[0] ?? '');
  const b = m ? bookByAbbr.get(m[1]) : undefined;
  if (!m || !b) return notFound();
  const ch = Number(m[2]);
  const secs = DB.sections.filter((s) => s.book === b.name && s.chapter === ch);
  return h('div', { class: 'lm-page lm-book-page' },
    h('nav', { class: 'lm-crumbs' }, h('a', { href: href('book', b.abbr) }, b.name), h('span', null, `第${ch}章`)),
    h('h1', null, `${b.name} 第${ch}章的律法`),
    secs.length ? secs.map(sectionBlock) : h('p', null, '這一章還沒有收錄律法。'),
    h('p', null, ext(chapterHref(b.name, ch), `讀${b.name}第${ch}章的經文與本章整理（另開網頁）`)));
}

function sectionBlock(s: Section): HTMLElement {
  return h('section', { class: 'lm-section' }, h('h4', null, s.title, h('small', null, ` v${s.from}-${s.to}`)),
    ...s.laws.map((id) => lawById.get(id)!).map((l) => lawCard(l)),
    s.laws.length ? null : h('p', { class: 'lm-muted' }, '還沒有整理成條文。'));
}

function codesOf(b: Book): { title: string | null; sections: Section[] }[] {
  const secs = DB.sections.filter((s) => s.book === b.name).sort((x, y) => x.chapter - y.chapter || x.from - y.from);
  const out: { title: string | null; sections: Section[] }[] = [];
  for (const s of secs) {
    const title = s.code ?? null;
    const last = out[out.length - 1];
    if (last && last.title === title) last.sections.push(s);
    else out.push({ title, sections: [s] });
  }
  return out;
}

function chapters(secs: Section[]): [number, Section[]][] {
  const m = new Map<number, Section[]>();
  for (const s of secs) m.set(s.chapter, [...(m.get(s.chapter) ?? []), s]);
  return [...m.entries()];
}

const notFound = () => h('div', { class: 'lm-page' }, h('h1', null, '找不到這一卷或這一章'), h('a', { href: '#/' }, '回總覽'));
