import { books, DB, entryHref, groupById, lawsOfGroup, lawsOfTopic, relatedTopics, topicById } from '../data/db';
import type { Law } from '../data/types';
import { href, type Route } from '../router';
import { store } from '../store';
import { lawCard, relationRow, topicChip } from '../ui/cards';
import { ext, h } from '../ui/dom';
import { lbl, more } from '../ui/more';

/** 主題頁：id 可以是大類（敬拜與聖所）或子題（安息日） */
export function topicView(route: Route): HTMLElement {
  const id = route.params[0];
  const group = groupById.get(id);
  const topic = topicById.get(id);
  if (!group && !topic) return h('div', { class: 'lm-page' }, h('h1', null, '找不到這個主題'), h('a', { href: '#/' }, '回總覽'));
  const g = group ?? groupById.get(topic!.group)!;
  const all = group ? lawsOfGroup(id) : lawsOfTopic(id);
  const focusBook = route.query.get('book');
  const ls = all.filter((l) => store.bookVisible(l.book) && (!focusBook || l.book === focusBook));
  const name = group ? lbl(group.plain, group.name) : lbl(topic!.plain, topic!.name);
  const formal = group ? group.name : topic!.name;
  const usedBooks = books.filter((b) => ls.some((l) => l.book === b.name));

  return h('div', { class: 'lm-page lm-topic-page', style: `--c: var(--g${g.color})` },
    h('header', { class: 'lm-page-head' },
      h('div', { class: 'lm-kicker' }, group ? '大類' : h('a', { href: href('topic', g.id) }, lbl(g.plain, g.name))),
      h('h1', null, name, name !== formal ? h('small', null, formal) : null),
      h('p', { class: 'lm-lede' }, ls.length
        ? lbl(`這個主題的律法出現在${usedBooks.map((b) => b.name).join('、')}，共 ${ls.length} 條。`, `${usedBooks.length} 卷 · ${ls.length} 條`)
        : '這個主題還沒有收錄條文。'),
      focusBook ? h('p', { class: 'lm-note' }, `只看${focusBook}。`, h('a', { href: href('topic', id) }, '看全部五卷')) : null,
      topic?.entry ? h('p', null, ext(entryHref(topic.entry), `知識庫條目「${topic.entry}」：查看完整條目（另開網頁）`)) : null),

    group ? h('nav', { class: 'lm-subtopics', 'aria-label': '子題' }, ...group.topics.map((t) => topicById.get(t)!).filter((t) => lawsOfTopic(t.id).length).map(topicChip)) : null,

    store.depth === 'basic' ? byBook(ls) : null,
    more('study', lbl('五卷並排看', '五卷泳道'), lanes(ls)),
    !group ? more('research', '常一起出現的主題', relatedList(id)) : null,
    more('research', '這個主題裡的關聯與證據', relationList(ls)),
  );
}

/** 入門：一卷一段，條文卡附白話說明 */
function byBook(ls: Law[]): HTMLElement {
  return h('div', { class: 'lm-bybook' }, ...books.filter((b) => ls.some((l) => l.book === b.name)).map((b) =>
    h('section', null, h('h2', null, b.name), ...ls.filter((l) => l.book === b.name).map((l) => lawCard(l)))));
}

/** 查經：五卷並排，一卷一欄；有證據的關聯以「↔」標在卡片上（待補：欄與欄之間畫連線） */
function lanes(ls: Law[]): HTMLElement {
  const shown = books.filter((b) => store.bookVisible(b.name));
  return h('div', { class: 'lm-lanes', style: `--n: ${shown.length}` }, ...shown.map((b) => {
    const mine = ls.filter((l) => l.book === b.name);
    return h('section', { class: 'lm-lane' }, h('h3', null, b.name, h('span', { class: 'lm-count' }, String(mine.length))),
      ...(mine.length ? mine.map((l) => lawCard(l, { showSummary: store.depth !== 'research' })) : [h('p', { class: 'lm-lane-empty' }, '這一卷沒有')]));
  }));
}

function relatedList(id: string): HTMLElement {
  const rel = relatedTopics(id);
  if (!rel.length) return h('p', { class: 'lm-muted' }, '沒有和其他主題共同標記的條文。');
  return h('ul', { class: 'lm-plain-list' }, ...rel.map(([t, n]) => h('li', null, topicChip(t), ` ${n} 條`)));
}

function relationList(ls: Law[]): HTMLElement {
  const ids = new Set(ls.map((l) => l.id));
  const rels = DB.relations.filter((r) => ids.has(r.from) || ids.has(r.to));
  if (!rels.length) return h('p', { class: 'lm-muted' }, '這個主題的條文目前沒有有證據的跨卷關聯。');
  return h('ul', { class: 'lm-rel-list' }, ...rels.map((r) => {
    const from = ls.find((l) => l.id === r.from) ?? ls.find((l) => l.id === r.to)!;
    const otherId = from.id === r.from ? r.to : r.from;
    const other = DB.laws.find((l) => l.id === otherId)!;
    return h('li', null, h('strong', null, from.title), h('ul', { class: 'lm-rel-list' }, relationRow(r, other)));
  }));
}
