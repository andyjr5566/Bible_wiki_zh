import { books, cooccurring, DB, entryHref, lawsOfEntry, topicById } from '../data/db';
import type { Law } from '../data/types';
import { type Route } from '../router';
import { store } from '../store';
import { entryChip, lawCard, TYPE_PLAIN } from '../ui/cards';
import { ext, h } from '../ui/dom';
import { egoGraph } from '../ui/graph';
import { lbl, more } from '../ui/more';

/**
 * 知識節點頁：條目本身只給名稱、類型、一句簡介和連結；
 * 主體是知識庫本身沒有的東西——五經律法裡哪些條文提到它。
 */
export function entryView(route: Route): HTMLElement {
  const title = route.params[0];
  const info = DB.entries[title];
  if (!info) return h('div', { class: 'lm-page' }, h('h1', null, title), h('p', null, '本站的律法裡沒有提到這個條目。'), h('a', { href: '#/' }, '回總覽'));
  const ls = lawsOfEntry(title).filter((l) => store.bookVisible(l.book));
  return h('div', { class: 'lm-page lm-entry-page' },
    h('header', { class: 'lm-page-head' },
      h('div', { class: 'lm-kicker' }, lbl(TYPE_PLAIN[info.type] ?? info.type, info.type)),
      h('h1', null, title),
      info.gist ? h('p', { class: 'lm-lede' }, info.gist) : null,
      h('p', null, ext(entryHref(title), '查看完整條目（另開網頁）'))),
    h('section', null,
      h('h2', null, lbl(`有 ${ls.length} 條律法提到它`, `提到它的律法（${ls.length}）`)),
      ...books.filter((b) => ls.some((l) => l.book === b.name)).map((b) => h('section', { class: 'lm-bybook' }, h('h3', null, b.name), ...ls.filter((l) => l.book === b.name).map((l) => lawCard(l))))),
    more('research', '依主題分組', byTopic(ls)),
    more('research', '在律法裡常和它一起出現的條目', cooc(title)),
    more('research', '關係圖', egoGraph('entry', title, title)),
  );
}

function byTopic(ls: Law[]): HTMLElement {
  const m = new Map<string, Law[]>();
  for (const l of ls) for (const t of l.topics) m.set(t, [...(m.get(t) ?? []), l]);
  return h('ul', { class: 'lm-plain-list' }, ...[...m.entries()].map(([t, list]) => h('li', null, h('strong', null, topicById.get(t)?.name ?? t), `：${list.map((l) => l.title).join('、')}`)));
}

function cooc(title: string): HTMLElement {
  const list = cooccurring(title);
  if (!list.length) return h('p', { class: 'lm-muted' }, '沒有。');
  return h('div', { class: 'lm-chips' }, ...list.map(([e, n]) => entryChip(e, `${e}（${n}）`)));
}
