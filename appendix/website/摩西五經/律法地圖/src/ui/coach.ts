import { DB, lawById, laws, lawsOfTopic, refText, relationsOf } from '../data/db';
import { go, href, parse, type Route } from '../router';
import { store } from '../store';
import { h } from './dom';

/**
 * 帶路：在真正的網站上，一步一步請讀者自己點。
 * 面板固定在畫面下方（要點的東西在下半部時移到上方），不蓋住頁面、不替讀者捲動。
 * 每一步先說「請你做什麼」，等讀者真的做了，才說明他現在看到的是什麼、對讀經有什麼用。
 * 離開正在做的那一頁，面板會提示並可以一鍵帶回去。
 */
interface Step {
  title: string;
  /** 這一步要在哪一頁做；不在那一頁就提示「帶我過去」 */
  at: (r: Route) => boolean;
  /** 「帶我過去」去哪裡 */
  goHash: string;
  /** 做之前要標出來的東西（CSS 選擇器；同一個選擇器有好幾個時取看得見的第一個） */
  target?: string;
  /** 請讀者做的事；沒有就是只看 */
  ask?: string;
  /** 讀者做了沒有 */
  done?: (r: Route) => boolean;
  /** 做完（或不用做）之後說明：這是什麼、有什麼用 */
  say: string[];
  /** 說明時標出來的東西 */
  sayTarget?: string;
  /** 最後一步 */
  last?: boolean;
}

/** 示範用的律法：第一張問題卡的第一條（出21:2-6），它有別卷記載 */
export const DEMO_LAW = DB.questions[0]?.laws[0] ?? 'ex21-02';
/** 示範「經文給的理由」用的律法 */
export const DEMO_WHY_LAW = 'lev25-39';
/** 示範主題頁 */
export const DEMO_TOPIC = 'slavery';
/** 示範書卷頁 */
export const DEMO_BOOK = '利';

const onLaw = (id?: string) => (r: Route) => r.name === 'law' && (!id || r.params[0] === id);
const anyPage = () => true;
const layerOpen = (key: string) => () => !!document.querySelector<HTMLDetailsElement>(`details[data-layer="${key}"]`)?.open;

function buildSteps(): Step[] {
  const demo = lawById.get(DEMO_LAW)!;
  const whyLaw = lawById.get(DEMO_WHY_LAW)!;
  const firstQ = DB.questions[0];
  const topicN = lawsOfTopic(DEMO_TOPIC).length;
  const otherRefs = relationsOf(DEMO_LAW).map((r) => refText(r.other)).join('、');
  return [
    {
      title: '先看這個網站收了什麼',
      at: (r) => r.name === '',
      goHash: '#/',
      say: [
        '讀利未記、申命記的時候，字都看得懂，卻常常不知道這一條在講什麼，為什麼要這樣規定，別卷是不是也說過。',
        `這個網站把五經的律法拆成一條一條，目前有 ${laws.length} 條，涵蓋創世記到申命記的每一章。每一條都整理成同樣的幾層，所以從任何一條都可以看懂它。`,
        '接下來請你自己點幾下。每點一下，我說明你看到的是什麼、對讀經有什麼用。大約三分鐘，隨時可以結束。',
      ],
    },
    {
      title: '從一個問題開始',
      at: (r) => r.name === '',
      goHash: '#/',
      target: '.lm-qgrid .lm-q:first-child .lm-q-btn',
      ask: `請點第一張問題卡：「${firstQ?.q ?? ''}」`,
      done: () => document.querySelector('.lm-qgrid .lm-q:first-child .lm-q-btn')?.getAttribute('aria-expanded') === 'true',
      say: [
        `翻開的這一句，是把${refText(demo)}整理成一句話。只說經文說了什麼，沒有加解釋。`,
        '這是網站的基本單位：一條律法，配一句話。聖經裡一長串規定擺在一起，很難看出每一條在講什麼。先看這一句，就知道這段在講什麼。',
        '往下捲到「律法在五經的哪裡」，剛才這條律法所在的章已經亮起來。一格是一章，整個五經的律法分布，一眼就看完。',
      ],
      sayTarget: '.lm-qgrid .lm-q:first-child',
    },
    {
      title: '進到這條律法',
      at: (r) => r.name === '',
      goHash: '#/',
      target: '.lm-qgrid .lm-q:first-child .lm-q-go',
      ask: '請點答案下面的連結，進到這條律法自己的頁面。',
      done: onLaw(),
      say: [
        '這是一條律法的頁面。最上面的「一句話」，就是剛才那一句。',
        '往下有三層：經文、別卷、出處。越往下越細，不想看就不用打開。',
        '頁面最上方的細帶是整個五經，一格一章。亮起來的格子，是這條律法所在的章，和別卷重述它的章。點任何一格，可以看那一章收了哪些律法。',
      ],
      sayTarget: '.lm-top-rib',
    },
    {
      title: '看經文原文',
      at: onLaw(),
      goHash: href('law', DEMO_LAW),
      target: 'details[data-layer="text"] > summary',
      ask: '請打開「經文」這一層（點那一列）。',
      done: layerOpen('text'),
      say: [
        '這是和合本原文，一個字都沒有改。上面那一句話有沒有說錯，可以自己對照。',
        '劃底線的字是人物、地方或觀念。點一下會跳出一小張簡介，再按「查看完整條目」，就能到知識庫讀完整的說明。',
        '底色淡的節，是上面那一句話的依據。',
      ],
      sayTarget: 'details[data-layer="text"]',
    },
    {
      title: '看別卷怎麼說',
      at: onLaw(),
      goHash: href('law', DEMO_LAW),
      target: 'details[data-layer="others"] > summary',
      ask: '請打開「別卷」這一層。',
      done: layerOpen('others'),
      say: [
        `出埃及記、利未記、申命記常常把同一件事各記一次，說法不完全一樣。這一層列出別卷的記載（${otherRefs}），每一條都附上知識庫裡的出處，找不到出處的，網站不連。`,
        '讀到申命記15章的時候，可以馬上看到出埃及記21章怎麼說，不用自己翻。',
      ],
      sayTarget: 'details[data-layer="others"]',
    },
    {
      title: '三段經文並排看',
      at: onLaw(),
      goHash: href('law', DEMO_LAW),
      target: 'details[data-layer="others"] .lm-btn',
      ask: '請按「這幾段並排，逐字比較」。',
      done: (r) => r.name === 'compare',
      say: [
        '三段經文並排。最下面的逐字比較，有刪除線的字只在前一段有，有底色的字只在後一段有。',
        '看一個例子：出埃及記21章講用錐子穿耳朵，申命記15章同一件事又寫到要多給羊群、禾場、酒醡出產。這種差別，單讀一卷很容易漏掉。',
      ],
      sayTarget: '.lm-compare-cols',
    },
    {
      title: '經文自己說的理由',
      at: (r) => r.name === 'compare',
      goHash: href('compare', [DEMO_LAW, DEMO_WHY_LAW, 'deut15-12'].join(',')),
      target: `.lm-compare-cols a[href="${href('law', DEMO_WHY_LAW)}"]`,
      ask: `請點中間那一欄的標題「${whyLaw.title}」，進到利未記的這一條。`,
      done: onLaw(DEMO_WHY_LAW),
      say: [
        '在「一句話」下面多了一塊「經文給的理由」，那是經文自己寫的原句，網站只是把那一節標出來。',
        '律法在希伯來文叫妥拉，字義是指引、教導。很多律法旁邊，經文自己就交代了為什麼這樣吩咐。網站不替經文解釋，只把經文給的理由放在規定旁邊。',
        '讀規定的時候順便讀它的理由，就比較看得出神為什麼這樣吩咐，是對誰說的。',
      ],
      sayTarget: '.lm-why',
    },
    {
      title: '同一個主題的律法放在一起',
      at: onLaw(DEMO_WHY_LAW),
      goHash: href('law', DEMO_WHY_LAW),
      target: '.lm-law-meta .lm-topic',
      ask: '請點這條律法的第一個主題標籤。',
      done: (r) => r.name === 'topic',
      say: [
        `這一頁把五經裡同一個主題的 ${topicN} 條律法排在一起，分成出埃及記、利未記、申命記三欄。想知道聖經對這件事怎麼規定，一頁就能從頭讀到尾。`,
        '用虛線連起來的卡片，是別卷又記了一次的同一件事。',
        `全站的律法分成 ${DB.groups.length} 大類、${DB.topics.length} 個主題，首頁最下面可以看到全部。`,
      ],
      sayTarget: '.lm-lanes-box',
    },
    {
      title: '用搜尋找',
      at: anyPage,
      goHash: '#/',
      target: '.lm-search-input',
      ask: '請在搜尋框打「安息日」。',
      done: () => [...document.querySelectorAll<HTMLInputElement>('.lm-search-input')].some((i) => i.offsetParent !== null && i.value.trim().length >= 2),
      say: [
        '搜尋會同時找條文、主題、人物地方和經文出處。標題有這個詞的條文排在前面，有「經文給的理由」的，會在標題下面多一行。',
        '讀聖經讀到某一章看不懂，可以直接打章節，例如「利25」或「申15:12」，就會列出那一節所在的律法。',
      ],
      sayTarget: '.lm-search-results:not([hidden])',
    },
    {
      title: '照書卷、照章來看',
      at: anyPage,
      goHash: '#/',
      target: `a.lm-rib-name[href="${href('book', DEMO_BOOK)}"]`,
      ask: '請點律法帶左邊的「利」，進到整卷利未記。',
      done: (r) => r.name === 'book',
      say: [
        '這一頁是整卷利未記，照全書目錄的段落（獻祭條例、潔淨條例等）和章排好。每一章可以點開，看那一章收了哪幾條律法。',
        '讀到利未記哪一章，就在這裡展開那一章，不用從頭翻。五卷書都是這樣。',
      ],
      sayTarget: '.lm-book-tools',
    },
    {
      title: '之後讀經可以這樣用',
      at: anyPage,
      goHash: '#/',
      say: [
        '有一個疑問，從首頁的問題卡開始。',
        '想看一個主題在五經怎麼說，進主題頁。',
        '讀到某一章看不懂，搜章節，或進書卷頁展開那一章。',
        '每一條律法都有一句話、經文、別卷、出處四層，有些還有經文自己給的理由。先看一句話，需要再往下打開。',
      ],
      last: true,
    },
  ];
}

// ---- 面板 ----
let steps: Step[] = [];
let idx = 0;
let panel: HTMLElement | null = null;
let doneSet = new Set<number>();
let marked: Element | null = null;
let pending = 0;
let lastSig = '';

const visible = (el: Element) => (el as HTMLElement).getClientRects().length > 0 && !(el as HTMLElement).closest('[hidden]');
function find(sel?: string): HTMLElement | null {
  if (!sel) return null;
  for (const el of document.querySelectorAll<HTMLElement>(sel)) if (visible(el)) return el;
  return null;
}

function mark(el: HTMLElement | null) {
  if (marked === el) return;
  marked?.classList.remove('lm-coach-hl');
  marked = el;
  el?.classList.add('lm-coach-hl');
}

export function coachActive(): boolean {
  return !!panel;
}

export function startCoach(from = 0) {
  if (panel) return;
  steps = buildSteps();
  idx = Math.min(Math.max(from, 0), steps.length - 1);
  doneSet = new Set();
  lastSig = '';
  // 讓「經文」「別卷」兩層一開始是收著的，才看得到打開的那一下
  store.setLayer('text', false);
  store.setLayer('others', false);
  panel = h('aside', { class: 'lm-coach', role: 'region', 'aria-label': '帶路' });
  document.body.append(panel);
  for (const ev of ['click', 'input', 'toggle'] as const) document.addEventListener(ev, schedule, true);
  window.addEventListener('resize', schedule);
  window.addEventListener('scroll', schedule, { passive: true });
  if (parse().name !== '') go('#/');
  update();
}

export function stopCoach() {
  if (!panel) return;
  for (const ev of ['click', 'input', 'toggle'] as const) document.removeEventListener(ev, schedule, true);
  window.removeEventListener('resize', schedule);
  window.removeEventListener('scroll', schedule);
  mark(null);
  panel.remove();
  panel = null;
  store.setGuided(true);
}

/** 第一次來到首頁時主動問一次 */
export function offerCoach(isHome: boolean) {
  if (isHome && !store.guided) startCoach();
}

/** 換頁後、或讀者做了什麼之後，重新判斷這一步的狀態 */
export function coachSync() {
  if (panel) update();
}

function schedule() {
  if (!panel || pending) return;
  pending = window.setTimeout(() => {
    pending = 0;
    update();
  }, 60);
}

function move(n: number) {
  idx = Math.min(Math.max(n, 0), steps.length - 1);
  update();
}

function update() {
  if (!panel) return;
  const s = steps[idx];
  const r = parse();
  // 「做到了」要看整個畫面的狀態（有的步驟做完就換頁，所以不限定在原來那一頁）
  if (s.ask && !doneSet.has(idx) && s.done?.(r)) doneSet.add(idx);
  const onPage = doneSet.has(idx) || s.at(r);
  const done = !s.ask || doneSet.has(idx);

  // 標出該標的東西
  const sel = !onPage ? undefined : done ? s.sayTarget : s.target;
  const el = find(sel);
  mark(el);

  // 面板放上面還是下面：要點的東西在下半部就放上面
  const rect = el?.getBoundingClientRect();
  const top = !!rect && rect.top > window.innerHeight * 0.42 && rect.top < window.innerHeight;
  const where = rect ? (rect.top >= window.innerHeight ? '下方' : rect.bottom <= 0 ? '上方' : '') : '';

  // 狀態沒變就不重畫，免得讀者用鍵盤移動時焦點被洗掉
  const sig = [idx, onPage, done, top, where, !!el, sel ?? ''].join('|');
  if (sig === lastSig) return;
  lastSig = sig;

  const body: HTMLElement[] = [];
  if (!onPage) {
    body.push(h('p', { class: 'lm-coach-ask' }, `這一步要回到對應的頁面做。`));
  } else if (!done) {
    body.push(h('p', { class: 'lm-coach-ask' }, s.ask!));
    if (sel && !el) body.push(h('p', { class: 'lm-coach-hint' }, '畫面上暫時找不到要點的地方，可以按「帶我過去」。'));
    else if (where) body.push(h('p', { class: 'lm-coach-hint' }, `要點的地方在畫面${where}，往${where === '下方' ? '下' : '上'}捲就看得到。`));
  } else {
    if (s.ask) body.push(h('p', { class: 'lm-coach-ok' }, '做到了。'));
    body.push(...s.say.map((t) => h('p', null, t)));
  }

  const needGo = !onPage || (!done && sel && !el);
  const lastDone = s.last && done;
  const nextBtn = lastDone
    ? h('button', { type: 'button', class: 'lm-btn lm-btn-primary', onclick: () => { stopCoach(); go('#/'); } }, '回首頁自己逛')
    : h('button', { type: 'button', class: `lm-btn ${done ? 'lm-btn-primary' : ''}`, onclick: () => move(idx + 1) }, done ? '下一步' : '跳過這一步');

  panel.className = `lm-coach${top ? ' lm-coach-top' : ''}`;
  panel.replaceChildren(
    h('div', { class: 'lm-coach-head' },
      h('span', { class: 'lm-coach-count' }, `帶路　第 ${idx + 1} 步 / ${steps.length} 步`),
      h('button', { type: 'button', class: 'lm-coach-x', 'aria-label': '結束帶路', onclick: () => stopCoach() }, '×')),
    h('h2', { class: 'lm-coach-title' }, s.title),
    h('div', { class: 'lm-coach-body', 'aria-live': 'polite' }, ...body),
    h('div', { class: 'lm-coach-foot' },
      idx > 0 ? h('button', { type: 'button', class: 'lm-btn', onclick: () => move(idx - 1) }, '上一步') : h('span'),
      needGo ? h('button', { type: 'button', class: 'lm-btn', onclick: () => { go(s.goHash); } }, '帶我過去') : null,
      nextBtn));
}

export type { Step };
