import './styles.css';
import { bookByAbbr, groupById, lawById, topicById } from './data/db';
import { parse, type Route } from './router';
import { applyQuery, store } from './store';
import { buildChrome } from './ui/chrome';
import { fill, h } from './ui/dom';
import { aboutView } from './views/about';
import { bookView, refView } from './views/book';
import { compareView } from './views/compare';
import { entryView } from './views/entry';
import { lawView } from './views/law';
import { overview } from './views/overview';
import { topicView } from './views/topic';
import { tourView } from './views/tour';

const VIEWS: Record<string, (r: Route) => HTMLElement> = {
  '': overview,
  topic: topicView,
  law: lawView,
  compare: compareView,
  book: bookView,
  ref: refView,
  entry: entryView,
  tour: tourView,
  about: aboutView,
};

/** 足跡列上的名字 */
function trailLabel(r: Route): string {
  const p = r.params[0] ?? '';
  switch (r.name) {
    case 'law': return lawById.get(p)?.title ?? p;
    case 'topic': return topicById.get(p)?.plain ?? groupById.get(p)?.plain ?? p;
    case 'entry': return p;
    case 'book': return bookByAbbr.get(p)?.name ?? p;
    case 'ref': return p;
    case 'tour': return '導覽路線';
    case 'compare': return '對照';
    case 'about': return '關於';
    default: return '總覽';
  }
}

function applyPrefs() {
  const root = document.documentElement;
  if (store.theme === 'auto') delete root.dataset.theme;
  else root.dataset.theme = store.theme;
  root.dataset.big = String(store.big);
  root.dataset.depth = store.depth;
}

const app = document.getElementById('app')!;
const main = h('main', { class: 'lm-main', id: 'main', tabindex: '-1' });
// 網址的 # 給路由用，所以「跳到內容」不能用 #main，改成直接把焦點移過去
const skip = h('a', { class: 'lm-skip', href: '#/', onclick: (e: MouseEvent) => { e.preventDefault(); main.focus(); } }, '跳到內容');
fill(app, skip, buildChrome(), main);

let lastHash = '';
function render() {
  const r = parse();
  applyQuery(r.query);
  const view = VIEWS[r.name] ?? overview;
  fill(main, view(r));
  document.title = r.name ? `${trailLabel(r)}｜摩西五經律法地圖` : '摩西五經律法地圖';
  // 換頁時回到頂端；同一頁因深度或篩選重畫時不動捲動位置
  if (location.hash !== lastHash) {
    window.scrollTo({ top: 0, behavior: 'instant' as ScrollBehavior });
    store.visit({ hash: location.hash || '#/', label: trailLabel(r) });
  }
  lastHash = location.hash;
}

window.addEventListener('hashchange', render);
store.on('depth', () => { applyPrefs(); render(); });
store.on('books', render);
store.on('prefs', applyPrefs);
applyPrefs();
render();
