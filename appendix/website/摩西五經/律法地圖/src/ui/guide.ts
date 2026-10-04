import { lawById, lawWhy, refText } from '../data/db';
import { store } from '../store';
import { h, type Child } from './dom';

/**
 * 導覽：第一次來的人看的七張小圖，講這個網站收了什麼、怎麼點、每一層在哪裡。
 * 圖都是用網站自己的資料畫的示意（不是截圖），所以資料更新後圖也會跟著更新。
 * 用原生 <dialog>：Esc 可以關，不會捲動頁面。頂列的「導覽」可以隨時再打開。
 */
interface Step {
  title: string;
  body: string;
  art: () => HTMLElement;
}

const sample = () => lawById.get('lev25-39')!;

/** 示意用的條文卡 */
function miniCard(): HTMLElement {
  const l = sample();
  return h('div', { class: 'lm-gd-card', 'aria-hidden': 'true' },
    h('span', { class: 'lm-gd-ref' }, refText(l)),
    h('strong', null, l.title),
    h('span', { class: 'lm-gd-sum' }, l.summary));
}

function miniQuestion(): HTMLElement {
  const l = lawById.get('ex21-02')!;
  return h('div', { class: 'lm-gd-stack', 'aria-hidden': 'true' },
    h('div', { class: 'lm-gd-q' }, h('span', null, '買來的希伯來奴僕，要服事幾年？'), h('small', null, `${refText(l)}　看經文怎麼說　＋`)),
    h('div', { class: 'lm-gd-q lm-gd-q-open' }, h('span', null, '放奴僕走的時候，可以讓他空手走嗎？'),
      h('p', null, lawById.get('deut15-12')!.summary),
      h('small', null, '申15:12-18 釋放希伯來弟兄不可空手 →')));
}

function miniLadder(): HTMLElement {
  const row = (name: string, text: string, open = false) => h('div', { class: `lm-gd-row${open ? ' lm-gd-open' : ''}` }, h('b', null, name), h('span', null, text));
  const l = sample();
  return h('div', { class: 'lm-gd-ladder', 'aria-hidden': 'true' },
    row('一句話', l.summary, true),
    row('經文', `${refText(l)}「你的弟兄若在你那裡漸漸窮乏……」 ▾`),
    row('別卷', '出21:2-6、申15:12-18 也記了 ▾'),
    row('出處', '經文裡的人物與觀念、關聯的出處 ▾'));
}

function miniWhy(): HTMLElement {
  const l = sample();
  const w = lawWhy(l)[0];
  return h('div', { class: 'lm-gd-card', 'aria-hidden': 'true' },
    h('strong', null, l.title),
    h('span', { class: 'lm-gd-sum' }, l.summary),
    w ? h('blockquote', { class: 'lm-gd-why' }, h('small', null, '經文給的理由'), h('p', null, w.text), h('cite', null, w.ref)) : null);
}

function miniRibbon(): HTMLElement {
  const cols = [3, 5, 2, 7, 4, 9, 6, 3, 8, 5, 2, 6, 10, 4, 7, 3, 5, 8, 2, 6, 4, 9, 3, 5];
  const colors = ['var(--g1)', 'var(--g2)', 'var(--g3)', 'var(--g4)', 'var(--g5)', 'var(--g6)'];
  return h('div', { class: 'lm-gd-rib', 'aria-hidden': 'true' },
    ...['出埃及記', '利未記', '申命記'].map((bk, r) => h('div', { class: 'lm-gd-rib-row' }, h('small', null, bk),
      h('span', { class: 'lm-gd-rib-cells' }, ...cols.map((n, i) => h('i', { style: `height:${4 + ((n + r * 3 + i) % 9) * 3}px;background:${colors[(i + r) % 6]};opacity:${(i + r) % 4 === 0 ? 1 : 0.35}` }))))));
}

function miniThread(): HTMLElement {
  return h('div', { class: 'lm-gd-thread', 'aria-hidden': 'true' },
    h('strong', null, '希伯來男僕第七年自由'),
    h('span', { class: 'lm-gd-line' },
      h('span', null, h('b', null, '出埃及記'), '出21:2-6'),
      h('span', null, h('b', null, '利未記'), '利25:39-43'),
      h('span', null, h('b', null, '申命記'), '申15:12-18')));
}

function miniSource(): HTMLElement {
  return h('div', { class: 'lm-gd-card', 'aria-hidden': 'true' },
    h('span', { class: 'lm-gd-ref' }, '知識庫條目'),
    h('strong', null, '禧年'),
    h('span', { class: 'lm-gd-sum' }, '名稱加一句簡介，完整內容另開網頁。'),
    h('span', { class: 'lm-gd-link' }, '查看完整條目（另開網頁）↗'));
}

const STEPS: Step[] = [
  { title: '這個網站收了什麼', art: miniCard,
    body: '摩西五經（創世記到申命記）裡神吩咐的律法，一條一條整理在這裡。每一條都附上和合本經文，還有一句話說它在講什麼。' },
  { title: '從一個問題開始', art: miniQuestion,
    body: '首頁的問題卡，點一下就在原地翻出經文怎麼回答，不會換頁。想找別的，用最上面的搜尋框，打主題、經文或人物都可以。' },
  { title: '一條律法分四層', art: miniLadder,
    body: '點進一條律法，由上往下是一句話、經文、別卷、出處。後三層先收起來，每一列寫著裡面有什麼，要看再點開。' },
  { title: '經文自己交代的理由', art: miniWhy,
    body: '很多律法旁邊跟著一句原因。網站把這一節的和合本原文標出來，放在一句話下面，不加自己的解釋。首頁也有一區集中列出這些原句。' },
  { title: '五經律法帶', art: miniRibbon,
    body: '首頁和每一頁上面的帶子，一格是一章，顏色是律法的類別，柱子越高，那一章收的律法越多。滑鼠移到問題卡、主題或顏色上，就亮出那些律法在哪幾章。' },
  { title: '別卷又記了一次', art: miniThread,
    body: '同一件事常在出埃及記、利未記、申命記各記一次，說法不完全一樣。點進去可以把幾段經文並排，逐字比較。每一條連線都有知識庫裡的出處。' },
  { title: '資料從哪裡來', art: miniSource,
    body: '經文用和合本，照錄不改寫。人物、地方和觀念連到知識庫的條目，這裡只放名稱和一句簡介，完整內容按「查看完整條目」另開網頁讀。收錄進度、分布表和下載在「關於」。' },
];

let dlg: HTMLDialogElement | null = null;

export function openGuide(from = 0): void {
  if (dlg) return;
  let i = Math.min(Math.max(from, 0), STEPS.length - 1);
  const art = h('div', { class: 'lm-gd-art' });
  const title = h('h2', { id: 'lm-gd-title' });
  const body = h('p', { class: 'lm-gd-body' });
  const count = h('span', { class: 'lm-gd-count' });
  const dots = h('span', { class: 'lm-gd-dots', 'aria-hidden': 'true' }, ...STEPS.map(() => h('i')));
  const prev = h('button', { type: 'button', class: 'lm-btn', onclick: () => go(i - 1) }, '上一張');
  const next = h('button', { type: 'button', class: 'lm-btn lm-btn-primary', onclick: () => (i === STEPS.length - 1 ? close() : go(i + 1)) });
  const closeBtn = h('button', { type: 'button', class: 'lm-gd-x', 'aria-label': '關閉導覽', onclick: () => close() }, '×');

  const d = h('dialog', { class: 'lm-guide', 'aria-labelledby': 'lm-gd-title' },
    h('div', { class: 'lm-gd-head' }, count, closeBtn),
    art, title, body,
    h('div', { class: 'lm-gd-foot' }, prev, dots, next));

  function go(n: number) {
    i = Math.min(Math.max(n, 0), STEPS.length - 1);
    const s = STEPS[i];
    art.replaceChildren(s.art());
    title.textContent = s.title;
    body.textContent = s.body;
    count.textContent = `${i + 1} / ${STEPS.length}`;
    prev.style.visibility = i === 0 ? 'hidden' : 'visible';
    next.textContent = i === STEPS.length - 1 ? '開始逛' : '下一張';
    [...dots.children].forEach((el, k) => el.classList.toggle('lm-on', k === i));
  }
  function close() {
    d.close();
  }
  d.addEventListener('close', () => {
    store.setGuided(true);
    d.remove();
    dlg = null;
  });
  // 點到對話框外面（背景）也關
  d.addEventListener('click', (e: MouseEvent) => {
    if (e.target === d) close();
  });
  document.body.append(d);
  dlg = d;
  go(i);
  d.showModal();
  next.focus();
}

/** 第一次來到首頁時自動打開一次；之後只有按頂列的「導覽」才會出現 */
export function offerGuide(isHome: boolean): void {
  if (isHome && !store.guided) openGuide();
}

export type { Child };
