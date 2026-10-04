import { books, DB, groupOfLaw, laws, lawsOfGroup, lawsOfTopic, refText, relationClusters, topicById } from '../data/db';
import type { Law } from '../data/types';
import { href } from '../router';
import { store } from '../store';
import { h } from '../ui/dom';
import { lbl, more } from '../ui/more';

const visible = (ls: Law[]) => ls.filter((l) => store.bookVisible(l.book));

/** 總覽：入門從「從這裡開始」讀起，查經起看矩陣與律法帶，研究層看覆蓋率 */
export function overview(): HTMLElement {
  const total = visible(laws).length;
  return h('div', { class: 'lm-page lm-overview' },
    h('section', { class: 'lm-hero' },
      h('h1', null, '摩西五經的律法地圖'),
      h('p', { class: 'lm-lede' }, lbl(
        `五經裡的律法散在出埃及記、利未記、民數記、申命記好幾十章。這裡把它們依主題排好，同一條律法在別卷又說了一次的，也連在一起。目前收了 ${total} 條。`,
        `依主題、書卷與彼此的關聯走讀五經律法。目前收錄 ${total} 條條文。`,
      ))),
    start(),
    more('study', `主題 × 書卷：每一類律法分布在哪幾卷`, matrix()),
    more('study', '五經律法帶：律法集中在哪些章', ribbon()),
    restated(),
    more('research', '收錄進度：每章收了幾節、還有哪些節沒處理', coverage()),
  );
}

function start(): HTMLElement {
  return h('section', { class: 'lm-start' },
    h('h2', null, lbl('從這裡開始', '導覽路線與六大類')),
    DB.tours.length
      ? h('div', { class: 'lm-tours' }, ...DB.tours.map((t) => h('a', { class: 'lm-tour-card', href: href('tour', t.id, 0) },
        h('span', { class: 'lm-tour-kicker' }, `導覽路線 · ${t.stops.length} 站`),
        h('strong', null, t.title),
        h('span', null, t.intro),
        h('span', { class: 'lm-go' }, '開始 →'))))
      : null,
    h('div', { class: 'lm-groups' }, ...DB.groups.map((g) => {
      const n = visible(lawsOfGroup(g.id)).length;
      return h('a', { class: 'lm-group-card', href: href('topic', g.id), style: `--c: var(--g${g.color})` },
        h('strong', null, lbl(g.plain, g.name)),
        store.depth === 'basic' ? h('span', { class: 'lm-muted' }, g.name) : null,
        h('span', { class: 'lm-count' }, n ? `${n} 條` : '還沒收錄'));
    })));
}

function matrix(): HTMLElement {
  const shown = books.filter((b) => store.bookVisible(b.name));
  const max = Math.max(1, ...DB.groups.flatMap((g) => shown.map((b) => lawsOfGroup(g.id).filter((l) => l.book === b.name).length)));
  const cell = (ls: Law[], topic: string, book: string) => {
    const n = ls.filter((l) => l.book === book).length;
    if (!n) return h('td', { class: 'lm-cell lm-cell-empty' }, '·');
    const size = 10 + Math.round((n / max) * 22);
    return h('td', { class: 'lm-cell' }, h('a', { href: `${href('topic', topic)}?book=${encodeURIComponent(book)}`, title: `${n} 條` },
      h('span', { class: 'lm-dot', style: `width:${size}px;height:${size}px` }), h('span', { class: 'lm-cell-n' }, String(n))));
  };
  const rows: HTMLElement[] = [];
  for (const g of DB.groups) {
    rows.push(h('tr', { class: 'lm-mrow-group', style: `--c: var(--g${g.color})` }, h('th', { scope: 'row' }, h('a', { href: href('topic', g.id) }, lbl(g.plain, g.name))), ...shown.map((b) => cell(lawsOfGroup(g.id), g.id, b.name))));
    if (store.atLeast('research')) {
      for (const tid of g.topics) {
        const ls = lawsOfTopic(tid);
        if (!ls.length) continue;
        rows.push(h('tr', { class: 'lm-mrow-topic' }, h('th', { scope: 'row' }, h('a', { href: href('topic', tid) }, topicById.get(tid)!.name)), ...shown.map((b) => cell(ls, tid, b.name))));
      }
    }
  }
  return h('div', { class: 'lm-matrix-wrap' },
    h('table', { class: 'lm-matrix' },
      h('thead', null, h('tr', null, h('th', null, ''), ...shown.map((b) => h('th', { scope: 'col' }, b.name)))),
      h('tbody', null, ...rows)),
    h('p', { class: 'lm-note' }, '圓點越大，這一類在那一卷收的條文越多。一條律法可以同時屬於好幾類。'));
}

function ribbon(): HTMLElement {
  return h('div', { class: 'lm-ribbon' }, ...books.filter((b) => store.bookVisible(b.name)).map((b) => {
    const cells: HTMLElement[] = [];
    for (let c = 1; c <= b.chapters; c++) {
      const ls = laws.filter((l) => l.book === b.name && l.chapter === c);
      const g = ls.length ? groupOfLaw(ls[0]) : undefined;
      cells.push(ls.length
        ? h('a', { class: 'lm-rib-cell', href: href('ref', `${b.abbr}${c}`), title: `${b.abbr}${c}：${ls.length} 條`, style: `--c: var(--g${g?.color ?? 0})` })
        : h('span', { class: 'lm-rib-cell lm-rib-empty', title: `${b.abbr}${c}` }));
    }
    return h('div', { class: 'lm-rib-row' }, h('a', { class: 'lm-rib-book', href: href('book', b.abbr) }, b.name), h('div', { class: 'lm-rib-cells' }, ...cells));
  }), h('p', { class: 'lm-note' }, '一格是一章，有顏色的章收了律法，顏色是那一章第一條律法的大類。'));
}

function restated(): HTMLElement | null {
  const clusters = relationClusters().filter((c) => c.some((l) => store.bookVisible(l.book)));
  if (!clusters.length) return null;
  return more('basic', lbl(`同一條律法在別卷又說了一次（${clusters.length} 組）`, `跨卷重述的律法（${clusters.length} 組）`),
    h('ul', { class: 'lm-clusters' }, ...clusters.map((c) => h('li', null,
      h('strong', null, c[0].title),
      h('span', { class: 'lm-cluster-refs' }, ...c.map((l) => h('a', { href: href('law', l.id) }, refText(l)))),
      h('a', { class: 'lm-go', href: href('compare', c.map((l) => l.id).join(',')) }, '並排看 →')))));
}

function coverage(): HTMLElement {
  return h('table', { class: 'lm-table' },
    h('thead', null, h('tr', null, ...['章', '節數', '已收', '不收', '還沒處理'].map((t) => h('th', null, t)))),
    h('tbody', null, ...DB.coverage.map((c) => h('tr', null,
      h('td', null, h('a', { href: href('ref', `${books.find((b) => b.name === c.book)!.abbr}${c.chapter}`) }, `${c.book} ${c.chapter}`)),
      h('td', null, String(c.total)), h('td', null, String(c.covered)), h('td', null, String(c.excluded)),
      h('td', null, c.missing.map(([a, b]) => (a === b ? `${a}` : `${a}-${b}`)).join('、') || '—')))));
}
