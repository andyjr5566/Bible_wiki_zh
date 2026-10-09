/**
 * 把 SITE.chapters 的每一拍排成一個 <section>：說明框 sticky 停在畫面內。
 * 每個說明框依序是：白話 → 經文（前面一行小字出處）→（互動提示）→「四家怎麼說」「原文」兩顆小按鈕。
 * 按鈕就地展開面板；手機改成從底部升起、覆蓋在說明框上方的面板。
 */
import type { Beat, StoryChapter } from '../data/types';
import { SITE } from '../data/site';
import { h } from './dom';
import type { BakeUI } from './bake';
import type { CountUI } from './count';
import type { HyssopUI } from './hyssop';
import { offeringList } from './offerings';
import type { WaveUI } from './wave';
import { notesPanelBody, wordsPanelBody } from './panels';
import { richText, verseNodes } from './text';

export interface BeatRef {
  chapter: StoryChapter;
  beat: Beat;
  /** 整份故事裡的第幾拍（0 起算） */
  index: number;
  el: HTMLElement;
  box: HTMLElement;
  /** 這一拍的室內分格（場景用 scissor 畫在裡面）；只有 meal 那一拍有 */
  panel?: HTMLElement;
  /** 關掉這一拍展開的面板 */
  closePanel(): void;
  hasPanelOpen(): boolean;
}

/** 說明框左右的固定指定（依 cue）；沒列到的照奇偶交替 */
const FIXED_SIDE: Record<string, 'left' | 'right'> = {
  title: 'right',
  meal: 'right', // 左邊是室內分格
  children: 'left', // 人物在畫面中間偏右，放右邊會蓋住父親的頭
  // 春季：左
  'new-moon': 'left',
  'seven-days': 'left',
  remember: 'left',
  wave: 'left',
  'not-yet': 'left',
  unclean: 'left',
  'second-month': 'left',
  count: 'left',
  'weeks-offerings': 'left',
  corners: 'left',
  // 春季：右
  bake: 'right',
  'no-leaven': 'right',
  'barley-ripe': 'right',
  'lamb-offering': 'right',
  sinai: 'right',
  wait: 'right',
  'two-loaves': 'right',
  rejoice: 'right',
};

/** 各種互動的介面（說明框裡的提示、按鈕、狀態；塗血與搖禾捆另有觸控層） */
export interface InteractionUIs {
  hyssop: HyssopUI;
  bake: BakeUI;
  wave: WaveUI;
  count: CountUI;
}

type Kind = 'notes' | 'words';
const KIND_LABEL: Record<Kind, string> = { notes: '四家怎麼說', words: '原文' };

/** 目前展開中的面板（全頁同時只開一個） */
let openRef: { close(returnFocus: boolean): void } | null = null;

export function closeOpenPanel(returnFocus = false): void {
  openRef?.close(returnFocus);
}
export const anyPanelOpen = (): boolean => openRef !== null;

export function buildBeats(main: HTMLElement, ui: InteractionUIs): BeatRef[] {
  const refs: BeatRef[] = [];
  // 說明框左右交替；有互動的那一拍固定落在左邊（牛膝草把手在畫面右側），其餘照奇偶往前後推
  const flat = SITE.chapters.flatMap((c) => c.beats);
  const interactive = flat.findIndex((b) => b.interaction);
  const offset = interactive >= 0 && interactive % 2 === 1 ? 1 : 0;
  let index = 0;
  for (const chapter of SITE.chapters) {
    chapter.beats.forEach((beat, bi) => {
      const side = FIXED_SIDE[beat.cue] ?? ((index + offset) % 2 === 0 ? 'left' : 'right');
      const ref = buildBeat(chapter, beat, bi, index, side, ui);
      main.append(ref.el);
      refs.push(ref);
      index++;
    });
  }
  return refs;
}

function buildBeat(chapter: StoryChapter, beat: Beat, bi: number, index: number, side: 'left' | 'right', ui: InteractionUIs): BeatRef {
  const el = h('section', {
    class: 'jf-beat',
    id: `jf-beat-${chapter.id}-${beat.id}`,
    'data-chapter': chapter.id,
    'data-beat': beat.id,
    'data-cue': beat.cue,
    'data-side': side,
    'data-len': index === 0 || beat.interaction ? 'long' : 'normal',
  });

  // 開場第一拍：大標題；其他章的第一拍：章標題
  if (index === 0) {
    el.append(
      h('header', { class: 'jf-hero' },
        h('h1', { class: 'jf-plate jf-title' }, SITE.title),
        h('p', { class: 'jf-hero-ref' }, SITE.motto.ref)),
    );
  } else if (bi === 0 && chapter.kind === 'feast') {
    el.append(
      h('header', { class: 'jf-chaphead' },
        h('h2', { class: 'jf-plate jf-chaptitle' }, chapter.title),
        chapter.date ? h('p', { class: 'jf-chapdate' }, chapter.date) : null),
    );
  }

  const boxId = `jf-box-${chapter.id}-${beat.id}`;
  const box = h('article', { class: 'jf-box', id: boxId, 'data-compact': beat.interaction ? 'true' : null, 'data-offers': beat.offerings?.length ?? null });
  if (beat.reason) box.append(h('p', { class: 'jf-reason' }, '經文自己說的理由'));
  box.append(h('p', { class: 'jf-text' }, richText(beat.text)));

  const block = beat.verse ? SITE.verses[beat.verse] : undefined;
  if (block) {
    box.append(
      h('figure', { class: 'jf-verse' },
        h('figcaption', { class: 'jf-verse-ref' }, block.ref),
        h('blockquote', { class: 'jf-verse-text' }, verseNodes(block))),
    );
  }

  const offers = offeringList(beat.offerings, beat.offeringsLabel);
  if (offers) box.append(offers);

  if (beat.prompt) {
    if (beat.interaction === 'hyssop') box.append(ui.hyssop.controls(beat.prompt));
    else if (beat.interaction === 'bake') box.append(ui.bake.controls(beat.prompt));
    else if (beat.interaction === 'wave') box.append(ui.wave.controls(beat.prompt));
    else if (beat.interaction === 'count') box.append(ui.count.controls(beat.prompt));
  }

  // ---- 就地展開 ----
  const hasNotes = !!beat.notes?.length;
  const hasWords = !!beat.words?.length;
  const parts: Partial<Record<Kind, { chip: HTMLButtonElement; more: HTMLElement; closeBtn: HTMLButtonElement }>> = {};
  let current: Kind | null = null;

  const handle = {
    close(returnFocus: boolean) {
      const k = current;
      setOpen(null);
      if (returnFocus && k) parts[k]?.chip.focus();
    },
  };

  function setOpen(kind: Kind | null) {
    current = kind;
    for (const k of ['notes', 'words'] as Kind[]) {
      const p = parts[k];
      if (!p) continue;
      const on = k === kind;
      p.more.hidden = !on;
      p.chip.setAttribute('aria-expanded', on ? 'true' : 'false');
    }
    box.dataset.open = kind ?? '';
    if (kind) openRef = handle;
    else if (openRef === handle) openRef = null;
  }

  function addPart(kind: Kind, body: HTMLElement) {
    const moreId = `${boxId}-${kind}`;
    const closeBtn = h('button', { type: 'button', class: 'jf-more-x', 'aria-label': `關閉「${KIND_LABEL[kind]}」`, onclick: () => handle.close(true) }, '關閉');
    const more = h('div', { class: 'jf-more', id: moreId, role: 'region', 'aria-label': KIND_LABEL[kind], hidden: true },
      h('div', { class: 'jf-more-head' }, h('span', { class: 'jf-more-title' }, KIND_LABEL[kind]), closeBtn),
      h('div', { class: 'jf-more-body' }, body));
    const chip = h('button', {
      type: 'button',
      class: 'jf-chip',
      'aria-expanded': 'false',
      'aria-controls': moreId,
      onclick: () => {
        if (current === kind) {
          setOpen(null);
        } else {
          closeOpenPanel(false);
          setOpen(kind);
          // 手機的面板蓋在說明框上方：把焦點帶進去，讀報讀器的人才知道面板開了
          if (window.matchMedia('(max-width: 720px)').matches) closeBtn.focus({ preventScroll: true });
        }
      },
    }, KIND_LABEL[kind]);
    parts[kind] = { chip, more, closeBtn };
  }

  if (hasNotes) addPart('notes', notesPanelBody(beat.notes!));
  if (hasWords) addPart('words', wordsPanelBody(beat.words!));

  if (parts.notes || parts.words) {
    box.append(h('div', { class: 'jf-actions' }, parts.notes?.chip, parts.words?.chip));
    for (const k of ['notes', 'words'] as Kind[]) if (parts[k]) box.append(parts[k]!.more);
  }

  // 說明框的 sticky 範圍限在 .jf-pin 裡，所以開場大標題、章標題那一段不會被說明框蓋住
  // meal：室內分格。DOM 只給外框與位置（背景透明，canvas 透出來），場景找到它之後用 scissor 畫在框內。
  // 一開始是 hidden；進入這一拍才顯示（見 setPanelOn），離開就隱藏，場景量到 0×0 就不畫。
  const panel = beat.cue === 'meal'
    ? h('div', { class: 'jf-panel', 'data-jf-panel': 'meal', 'aria-hidden': 'true', hidden: true })
    : undefined;
  el.append(h('div', { class: 'jf-pin' }, panel, box));
  return {
    chapter,
    beat,
    index,
    el,
    box,
    panel,
    closePanel: () => handle.close(false),
    hasPanelOpen: () => current !== null,
  };
}

/** 顯示或隱藏室內分格：進入時從下方滑入＋淡入（約 0.5s，減少動態時只淡入，見 CSS）；離開就收起來 */
export function setPanelOn(panel: HTMLElement, on: boolean): void {
  if (on) {
    if (!panel.hidden && panel.classList.contains('is-on')) return;
    panel.hidden = false;
    void panel.offsetWidth; // 先讓瀏覽器量一次，transition 才會從起點開始
    panel.classList.add('is-on');
  } else {
    panel.classList.remove('is-on');
    panel.hidden = true;
  }
}
