import { abbrOf, bookByName, chapterHref, DB, entryHref, lawById, lawEntries, laws, lawVerses, refText, relationsOf, sectionOf, topicsOf } from '../data/db';
import type { Law } from '../data/types';
import { href, type Route } from '../router';
import { store } from '../store';
import { entryChip, entryPeekContent, glossText, groupColor, relationRow, TYPE_PLAIN, topicChip, typeKey } from '../ui/cards';
import { ext, h, type Child } from '../ui/dom';
import { egoGraph } from '../ui/graph';
import { at, lbl, more } from '../ui/more';
import { openPeek } from '../ui/peek';

export function lawView(route: Route): HTMLElement {
  const l = lawById.get(route.params[0]);
  if (!l) return h('div', { class: 'lm-page' }, h('h1', null, '找不到這條律法'), h('a', { href: '#/' }, '回總覽'));
  const sec = sectionOf(l);
  const book = bookByName.get(l.book)!;
  const ents = lawEntries(l);
  const rels = relationsOf(l.id);
  const inCompare = store.compare.includes(l.id);

  return h('div', { class: 'lm-page lm-law-page', style: `--c: ${groupColor(l)}` },
    h('nav', { class: 'lm-crumbs', 'aria-label': '位置' },
      h('a', { href: href('book', book.abbr) }, l.book),
      at('study', sec?.code ? h('span', null, sec.code) : null),
      h('a', { href: href('ref', `${book.abbr}${l.chapter}`) }, `第${l.chapter}章`),
      sec ? h('span', null, sec.title) : null),
    h('header', { class: 'lm-page-head' },
      h('h1', null, l.title),
      h('div', { class: 'lm-law-meta' }, h('span', { class: 'lm-ref lm-ref-big' }, refText(l)), ...topicsOf(l).map(topicChip))),

    // 第一層：一句話看懂
    h('section', { class: 'lm-summary' },
      h('p', null, ...glossText(l.summary)),
      at('study', h('p', { class: 'lm-basis' }, `這句話依據第 ${l.basis.join('、')} 節。`))),

    // 第二層：經文與連結
    more('study', lbl(`讀經文（${refText(l)}）`, `經文 ${refText(l)}`), scripture(l)),
    ents.length || l.entries.length
      ? more('study', lbl(`經文裡提到 ${ents.length} 個人物、地方與觀念`, `經文連到的知識條目（${ents.length}）`), entryGroups(l, ents))
      : null,
    rels.length
      ? more('basic', lbl(rels.length === 1 ? '這條律法在別卷也出現 →' : `這條律法在別卷也出現（${rels.length} 處）→`, `相關律法（${rels.length}）`),
        h('ul', { class: 'lm-rel-list' }, ...rels.map(({ rel, other }) => relationRow(rel, other))),
        h('a', { class: 'lm-btn', href: href('compare', [l.id, ...rels.map((r) => r.other.id)].join(',')) }, '把這幾段經文並排看'))
      : null,

    h('div', { class: 'lm-actions' },
      h('button', {
        type: 'button', class: 'lm-btn', 'aria-pressed': String(inCompare),
        onclick: (e: MouseEvent) => {
          store.toggleCompare(l.id);
          const on = store.compare.includes(l.id);
          const b = e.currentTarget as HTMLButtonElement;
          b.setAttribute('aria-pressed', String(on));
          b.textContent = on ? '已加入對照' : '加入對照';
        },
      }, inCompare ? '已加入對照' : '加入對照'),
      ext(chapterHref(l.book, l.chapter), `讀${l.book}第${l.chapter}章的本章整理（另開網頁）`)),

    neighbors(l),

    // 第三層：資料與證據
    more('research', '關係圖', egoGraph('law', l.id, l.title)),
    more('research', '資料', h('dl', { class: 'lm-dl' },
      h('dt', null, '條文代號'), h('dd', null, l.id),
      sec?.code ? [h('dt', null, '法典段落'), h('dd', null, `${sec.code}（取自${l.book}全書目錄）`)] : null,
      sec ? [h('dt', null, '律法段落'), h('dd', null, `${sec.title}（v${sec.from}-${sec.to}）`)] : null,
      h('dt', null, '依據節'), h('dd', null, l.basis.join('、')),
      coverageLine(l))),
  );
}

/** 經文：verse_links 的片語劃線，點了開條目小卡 */
function scripture(l: Law): HTMLElement {
  return h('ol', { class: 'lm-verses' }, ...lawVerses(l).map((v) => {
    const parts: Child[] = [];
    let at0 = 0;
    for (const k of v.links) {
      if (k.s > at0) parts.push(v.text.slice(at0, k.s));
      const b = h('button', { type: 'button', class: `lm-phrase lm-t-${typeKey(k.target)}`, title: k.target }, v.text.slice(k.s, k.e));
      b.addEventListener('click', () => openPeek(b, ...entryPeekContent(k.target)));
      parts.push(b);
      at0 = k.e;
    }
    parts.push(v.text.slice(at0));
    const isBasis = l.basis.includes(v.n);
    return h('li', { value: String(v.n), class: isBasis && store.atLeast('research') ? 'lm-basis-verse' : null }, ...parts);
  }), h('p', { class: 'lm-note' }, '經文：和合本。劃線的字連到知識庫條目，點了看簡介。'));
}

function entryGroups(l: Law, ents: string[]): HTMLElement {
  const byType = new Map<string, string[]>();
  for (const e of ents) {
    const t = DB.entries[e]?.type ?? '其他';
    byType.set(t, [...(byType.get(t) ?? []), e]);
  }
  return h('div', { class: 'lm-entry-groups' },
    l.entries.length ? h('div', { class: 'lm-entry-group' }, h('h4', null, '這條律法的知識庫條目'), ...l.entries.map((e) => ext(entryHref(e), e))) : null,
    ...[...byType.entries()].map(([type, list]) => h('div', { class: 'lm-entry-group' }, h('h4', null, lbl(TYPE_PLAIN[type] ?? type, type)), ...list.map((e) => entryChip(e)))));
}

/** 同一章的前後條文 */
function neighbors(l: Law): HTMLElement | null {
  const same = laws.filter((x) => x.book === l.book);
  const i = same.findIndex((x) => x.id === l.id);
  const prev = same[i - 1];
  const next = same[i + 1];
  if (!prev && !next) return null;
  return h('nav', { class: 'lm-prevnext', 'aria-label': '前後條文' },
    prev ? h('a', { href: href('law', prev.id) }, h('span', null, '← ', prev.title), h('small', null, refText(prev))) : h('span'),
    next ? h('a', { href: href('law', next.id) }, h('span', null, next.title, ' →'), h('small', null, refText(next))) : h('span'));
}

function coverageLine(l: Law): Child {
  const c = DB.coverage.find((x) => x.book === l.book && x.chapter === l.chapter);
  if (!c) return null;
  return [h('dt', null, '本章收錄'), h('dd', null, `${abbrOf(l.book)}${l.chapter} 共 ${c.total} 節，已收 ${c.covered} 節，不收 ${c.excluded} 節${c.missing.length ? `，還沒處理 ${c.missing.map(([a, b]) => (a === b ? a : `${a}-${b}`)).join('、')}` : ''}`)];
}
