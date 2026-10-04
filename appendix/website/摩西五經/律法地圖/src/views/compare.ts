import { lawById, lawVerses, refText, relationBetween } from '../data/db';
import type { Law } from '../data/types';
import { charDiff, similarity } from '../lib/diff';
import { href, type Route } from '../router';
import { store } from '../store';
import { evidenceLine, lawLink } from '../ui/cards';
import { h } from '../ui/dom';
import { lbl, more } from '../ui/more';
import { RELATION_LABEL } from '../data/db';

/** 對照頁：2–4 段經文並排。差在哪裡的完整說明在互文條目裡，這裡只放一句關係＋連結。 */
export function compareView(route: Route): HTMLElement {
  const ids = (route.params[0] ?? '').split(',').filter(Boolean);
  const ls = (ids.length ? ids : store.compare).map((id) => lawById.get(id)).filter((l): l is Law => !!l).slice(0, 4);
  if (ls.length < 2) {
    return h('div', { class: 'lm-page' }, h('h1', null, '對照'),
      h('p', null, '在條文頁按「加入對照」，選兩到四條，就可以在這裡並排看。'),
      ls.length ? h('p', null, '目前選了：', lawLink(ls[0])) : null);
  }
  const text = (l: Law) => lawVerses(l).map((v) => v.text).join('');
  const pairs: [Law, Law][] = [];
  for (let i = 0; i < ls.length; i++) for (let j = i + 1; j < ls.length; j++) pairs.push([ls[i], ls[j]]);
  const rels = pairs.map(([a, b]) => ({ a, b, rel: relationBetween(a.id, b.id) })).filter((x) => x.rel);

  return h('div', { class: 'lm-page lm-compare-page' },
    h('h1', null, ls.map((l) => refText(l)).join(' ／ ')),
    rels.length
      ? h('ul', { class: 'lm-rel-list' }, ...rels.map(({ a, b, rel }) => h('li', null,
        `${refText(a)} 與 ${refText(b)}：${lbl(...RELATION_LABEL[rel!.type])}。`, evidenceLine(rel!.evidence))))
      : h('p', { class: 'lm-note' }, '這幾條之間目前沒有有證據的關聯；可能只是同一個主題。'),
    h('div', { class: 'lm-compare-cols', style: `--n: ${ls.length}` }, ...ls.map((l) => h('section', { class: 'lm-compare-col' },
      h('h2', null, lawLink(l), h('small', null, refText(l))),
      h('p', { class: 'lm-card-sum' }, l.summary),
      h('ol', { class: 'lm-verses' }, ...lawVerses(l).map((v) => h('li', { value: String(v.n) }, v.text))),
      h('a', { href: href('compare', ls.filter((x) => x.id !== l.id).map((x) => x.id).join(',')), class: 'lm-muted' }, '從對照移除')))),
    ls.length >= 2 ? more('research', '字面差異（機械比對）', diffBlock(ls[0], ls[1], text)) : null,
  );
}

function diffBlock(a: Law, b: Law, text: (l: Law) => string): HTMLElement {
  const parts = charDiff(text(a), text(b));
  return h('div', null,
    h('p', { class: 'lm-note' }, `逐字比對 ${refText(a)}（刪線）與 ${refText(b)}（底色）。只看字面，不判斷意思；相同字數約佔 ${Math.round(similarity(parts) * 100)}%。`),
    h('p', { class: 'lm-diff' }, ...parts.map((p) => (p.kind === 'same' ? p.text : h(p.kind === 'a' ? 'del' : 'ins', null, p.text)))));
}
