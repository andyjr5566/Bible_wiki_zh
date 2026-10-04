import { cooccurring, lawById, lawEntries, lawsOfEntry, relationsOf, topicsOf } from '../data/db';
import { href } from '../router';
import { h, s } from './dom';

/**
 * 關係圖：以目前的律法或條目為中心，一圈畫出直接相連的主題、律法與條目。
 * 版面是確定性的放射狀（同一個中心每次長得一樣），不用力導向，避免一團亂線。
 * 點任何一點就換它當中心（就是換頁，所以也會進足跡）。
 */
type Kind = 'law' | 'topic' | 'entry';
interface GNode { kind: Kind; label: string; target: string }

const MAX = 24;
const short = (t: string, n = 8) => ([...t].length > n ? `${[...t].slice(0, n - 1).join('')}…` : t);

function neighbors(kind: 'law' | 'entry', id: string): GNode[] {
  if (kind === 'law') {
    const l = lawById.get(id)!;
    return [
      ...topicsOf(l).map((t) => ({ kind: 'topic' as const, label: t.plain, target: href('topic', t.id) })),
      ...relationsOf(id).map(({ other }) => ({ kind: 'law' as const, label: other.title, target: href('law', other.id) })),
      ...[...new Set([...l.entries, ...lawEntries(l)])].map((e) => ({ kind: 'entry' as const, label: e, target: href('entry', e) })),
    ].slice(0, MAX);
  }
  return [
    ...lawsOfEntry(id).map((l) => ({ kind: 'law' as const, label: l.title, target: href('law', l.id) })),
    ...cooccurring(id, 12).map(([e]) => ({ kind: 'entry' as const, label: e, target: href('entry', e) })),
  ].slice(0, MAX);
}

export function egoGraph(kind: 'law' | 'entry', id: string, centerLabel: string): HTMLElement {
  const ns = neighbors(kind, id);
  const W = 520;
  const C = W / 2;
  const R = 190;
  const svg = s('svg', { viewBox: `0 0 ${W} ${W}`, class: 'lm-graph-svg', role: 'img', 'aria-label': `${centerLabel}的關係圖` });
  const pos = ns.map((_, i) => {
    const a = (i / Math.max(ns.length, 1)) * Math.PI * 2 - Math.PI / 2;
    return [C + R * Math.cos(a), C + R * Math.sin(a)] as const;
  });
  ns.forEach((_, i) => svg.append(s('line', { x1: C, y1: C, x2: pos[i][0], y2: pos[i][1], class: 'lm-g-edge' })));
  svg.append(s('circle', { cx: C, cy: C, r: 34, class: `lm-g-node lm-g-${kind} lm-g-center` }), s('text', { x: C, y: C + 5, 'text-anchor': 'middle', class: 'lm-g-label lm-g-center-label' }, short(centerLabel, 7)));
  ns.forEach((n, i) => {
    const [x, y] = pos[i];
    const a = s('a', { href: n.target, class: 'lm-g-link' },
      s('title', {}, n.label),
      s('circle', { cx: x, cy: y, r: 10, class: `lm-g-node lm-g-${n.kind}` }),
      s('text', { x, y: y + (y < C ? -16 : 26), 'text-anchor': 'middle', class: 'lm-g-label' }, short(n.label)));
    svg.append(a);
  });
  return h('figure', { class: 'lm-graph' }, svg,
    h('figcaption', null, h('span', { class: 'lm-g-key lm-g-topic' }, '主題'), h('span', { class: 'lm-g-key lm-g-law' }, '律法'), h('span', { class: 'lm-g-key lm-g-entry' }, '知識條目'), ns.length >= MAX ? `（只畫前 ${MAX} 個）` : ''));
}
