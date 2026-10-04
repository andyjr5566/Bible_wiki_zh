import { DB, lawById, lawVerses, refText, RELATION_LABEL, relationBetween } from '../data/db';
import { href, type Route } from '../router';
import { evidenceLine, glossText, groupColor, lawLink } from '../ui/cards';
import { h } from '../ui/dom';
import { lbl } from '../ui/more';

/** 導覽路線：給初學者，一站一條律法。站與站的關係直接用 relations.yaml 的關聯與證據，不另寫。 */
export function tourView(route: Route): HTMLElement {
  const tour = DB.tours.find((t) => t.id === route.params[0]);
  if (!tour) return h('div', { class: 'lm-page' }, h('h1', null, '找不到這條路線'), h('a', { href: '#/' }, '回總覽'));
  const i = Math.min(Math.max(Number(route.params[1] ?? 0) || 0, 0), tour.stops.length - 1);
  const l = lawById.get(tour.stops[i])!;
  const prev = i > 0 ? lawById.get(tour.stops[i - 1]) : undefined;
  const rel = prev ? relationBetween(prev.id, l.id) : undefined;
  const last = i === tour.stops.length - 1;

  return h('div', { class: 'lm-page lm-tour-page' },
    h('header', { class: 'lm-page-head' },
      h('div', { class: 'lm-kicker' }, '導覽路線'),
      h('h1', null, tour.title),
      i === 0 ? h('p', { class: 'lm-lede' }, ...glossText(tour.intro)) : null,
      h('ol', { class: 'lm-steps', 'aria-label': '路線進度' }, ...tour.stops.map((id, k) => h('li', { 'aria-current': k === i ? 'step' : null },
        h('a', { href: href('tour', tour.id, k) }, refText(lawById.get(id)!)))))),
    h('article', { class: 'lm-stop', style: `--c: ${groupColor(l)}` },
      h('div', { class: 'lm-stop-n' }, `第 ${i + 1} 站，共 ${tour.stops.length} 站`),
      h('h2', null, l.title, h('small', null, refText(l))),
      rel && prev ? h('div', { class: 'lm-stop-rel' }, `和上一站（${refText(prev)}）的關係：${lbl(...RELATION_LABEL[rel.type])}。`, evidenceLine(rel.evidence)) : null,
      h('p', { class: 'lm-summary' }, ...glossText(l.summary)),
      h('ol', { class: 'lm-verses' }, ...lawVerses(l).map((v) => h('li', { value: String(v.n) }, v.text))),
      h('p', null, lawLink(l, '這條律法的詳細資料 →'))),
    h('nav', { class: 'lm-tour-nav' },
      i > 0 ? h('a', { class: 'lm-btn', href: href('tour', tour.id, i - 1) }, '← 上一站') : h('span'),
      last
        ? h('a', { class: 'lm-btn lm-btn-primary', href: href('compare', tour.stops.join(',')) }, '把這幾段並排看 →')
        : h('a', { class: 'lm-btn lm-btn-primary', href: href('tour', tour.id, i + 1) }, '下一站 →')),
    h('p', { class: 'lm-center' }, h('a', { href: '#/' }, '離開路線，自己逛')));
}
