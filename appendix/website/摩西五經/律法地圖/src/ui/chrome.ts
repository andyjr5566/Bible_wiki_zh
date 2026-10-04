import { books, refText } from '../data/db';
import { search } from '../lib/search';
import { go, href } from '../router';
import { DEPTHS, DEPTH_LABEL, store } from '../store';
import { fill, h } from './dom';

const DEPTH_HELP = {
  basic: '入門：先給一句話看懂，其他收起來',
  study: '查經：展開經文、相關律法與各卷對照',
  research: '研究：再展開證據出處、分布數字與資料下載',
};

/** 頂列：品牌、搜尋、閱讀深度、書卷篩選、對照、偏好；下面一列是足跡 */
export function buildChrome(): HTMLElement {
  const results = h('div', { class: 'lm-search-results', hidden: true, role: 'listbox' });
  const input = h('input', { class: 'lm-search-input', type: 'search', placeholder: '找經文、主題或人物（例：申15:12、安息日）', 'aria-label': '搜尋' });
  const close = () => { results.hidden = true; };
  const render = () => {
    const r = search(input.value);
    const rows: HTMLElement[] = [];
    const row = (label: string, sub: string, target: string) => rows.push(h('a', { class: 'lm-sr', href: target, role: 'option', onclick: close }, h('span', null, label), h('small', null, sub)));
    if (r.ref) {
      if (r.ref.laws.length) r.ref.laws.forEach((l) => row(l.title, refText(l), href('law', l.id)));
      else rows.push(h('div', { class: 'lm-sr lm-sr-none' }, `${r.ref.label}：這裡還沒有收錄律法`));
    }
    r.laws.forEach((l) => row(l.title, `條文 · ${refText(l)}`, href('law', l.id)));
    r.topics.forEach((t) => row(t.plain === t.name ? t.name : `${t.plain}（${t.name}）`, '主題', href('topic', t.id)));
    r.entries.forEach((e) => row(e, '知識條目', href('entry', e)));
    fill(results, ...(rows.length ? rows : [h('div', { class: 'lm-sr lm-sr-none' }, '找不到')]));
    results.hidden = !input.value.trim();
  };
  input.addEventListener('input', render);
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      const first = results.querySelector<HTMLAnchorElement>('a.lm-sr');
      if (first) { go(first.getAttribute('href')!); close(); input.blur(); }
    }
    if (e.key === 'Escape') { close(); input.blur(); }
  });
  input.addEventListener('blur', () => setTimeout(close, 150));
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); input.focus(); }
  });

  const depth = h('div', { class: 'lm-depth', role: 'radiogroup', 'aria-label': '閱讀深度' });
  const renderDepth = () => fill(depth, ...DEPTHS.map((d) => h('button', { type: 'button', role: 'radio', 'aria-checked': String(store.depth === d), title: DEPTH_HELP[d], onclick: () => store.setDepth(d) }, DEPTH_LABEL[d])));

  const bookBar = h('div', { class: 'lm-books', 'aria-label': '只看這幾卷' });
  const renderBooks = () => fill(bookBar,
    ...books.map((b) => h('button', { type: 'button', 'aria-pressed': String(store.books.has(b.name)), title: `只看${b.name}（可多選）`, onclick: () => store.toggleBook(b.name) }, b.abbr)),
    store.books.size ? h('button', { type: 'button', class: 'lm-books-clear', onclick: () => store.clearBooks() }, '全部') : null);

  const compare = h('a', { class: 'lm-compare-link', href: '#/compare' });
  const renderCompare = () => {
    fill(compare, '對照', store.compare.length ? h('span', { class: 'lm-badge' }, String(store.compare.length)) : null);
    compare.setAttribute('href', store.compare.length ? href('compare', store.compare.join(',')) : '#/compare');
  };

  const prefs = h('div', { class: 'lm-prefs' });
  const renderPrefs = () => fill(prefs,
    h('button', { type: 'button', title: '深淺色', onclick: () => store.setTheme(store.theme === 'auto' ? 'dark' : store.theme === 'dark' ? 'light' : 'auto') }, store.theme === 'auto' ? '◐ 自動' : store.theme === 'dark' ? '● 深色' : '○ 淺色'),
    h('button', { type: 'button', 'aria-pressed': String(store.big), onclick: () => store.setBig(!store.big) }, '大字'));

  const trail = h('nav', { class: 'lm-trail', 'aria-label': '足跡' });
  const renderTrail = () => fill(trail, store.trail.length > 1 ? h('span', { class: 'lm-trail-label' }, '剛走過：') : null, ...store.trail.slice(1).map((t) => h('a', { href: t.hash }, t.label)));

  store.on('depth', renderDepth);
  store.on('books', renderBooks);
  store.on('compare', renderCompare);
  store.on('prefs', renderPrefs);
  store.on('trail', renderTrail);
  renderDepth(); renderBooks(); renderCompare(); renderPrefs(); renderTrail();

  return h('header', { class: 'lm-top' },
    h('div', { class: 'lm-top-row' },
      h('a', { class: 'lm-brand', href: '#/' }, h('span', { class: 'lm-brand-mark', 'aria-hidden': 'true' }), '律法地圖'),
      h('div', { class: 'lm-search' }, input, results),
      depth),
    h('div', { class: 'lm-top-row lm-top-sub' }, bookBar, compare, h('a', { href: '#/about' }, '關於'), prefs),
    trail);
}
