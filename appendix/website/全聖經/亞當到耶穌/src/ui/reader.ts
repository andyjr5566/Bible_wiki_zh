import type { ReadingData, ReadingToken, ReadingVerse } from '../data/types';
import type { CanvasApi, ReadingMarks } from './canvas';
import { button, h } from './dom';
import type { SpeechController } from './speech';

/**
 * 帶你讀經：經文一節一節往下讀，讀到誰，大家譜的鏡頭就移到誰；
 * 讀到「生」由父母往子女畫墨線，讀到職稱就蓋一枚朱印。
 * 沒開朗讀時，文字像字幕一樣照速度亮；開了朗讀就跟著聲音走。
 */
export interface ReaderApi {
  panel: HTMLElement;
  stage: HTMLElement;
  open(ref?: string, autoplay?: boolean): void;
  close(): void;
  isOpen(): boolean;
}

interface FlatVerse {
  index: number;
  chapter: number;
  chapterTitle: string;
  verse: ReadingVerse;
  key: string;
}

const CHARS_PER_SECOND = 4.6;
const SPEEDS = [0.75, 1, 1.25, 1.5] as const;
const CHINESE_NUMBERS = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十'];
const chapterName = (n: number) => (n <= 10 ? CHINESE_NUMBERS[n]! : `十${CHINESE_NUMBERS[n - 10]}`);
const storage = {
  get(key: string) { try { return localStorage.getItem(`adam-jesus:reader-${key}`); } catch { return null; } },
  set(key: string, value: string) { try { localStorage.setItem(`adam-jesus:reader-${key}`, value); } catch { /* 私密模式不保存 */ } },
};

export function createReader(reading: ReadingData, canvas: CanvasApi, options: {
  speech?: SpeechController;
  onOpenChange?(open: boolean): void;
}): ReaderApi {
  const book = reading.book;
  const verses: FlatVerse[] = [];
  for (const chapter of reading.chapters) {
    for (const verse of chapter.verses) {
      verses.push({ index: verses.length, chapter: chapter.n, chapterTitle: chapter.title, verse, key: `${book}${chapter.n}:${verse.v}` });
    }
  }
  const motionOn = () => document.documentElement.dataset.motion !== 'off';

  // ── 狀態 ─────────────────────────────────────────────
  let isOpen = false;
  let at = 0;
  let cursor = 0;
  let fired = 0;
  let playing = false;
  let follow = true;
  let speed = Number(storage.get('speed')) || 1;
  if (!SPEEDS.includes(speed as typeof SPEEDS[number])) speed = 1;
  let voiceOn = false;
  let renderedChapter = 0;
  let pauseUntil = 0;
  let lastFrame = 0;
  let frame = 0;
  let gapTimer = 0;
  let expandedBefore: Set<string> | null = null;
  let marks: ReadingMarks = emptyMarks();
  const lastPersonInSection = new Map<string, string>();

  function emptyMarks(): ReadingMarks {
    return { lit: new Set(), trail: new Set(), current: null, seals: [], ink: [], fresh: new Set() };
  }

  // ── 經文欄 ───────────────────────────────────────────
  const chapterSelect = h('select', { className: 'ag-rd-select', 'aria-label': '選章' },
    ...reading.chapters.map((chapter) => h('option', { value: String(chapter.n) }, `第 ${chapter.n} 章　${chapter.title}`)));
  chapterSelect.addEventListener('change', () => jump(firstVerseOf(Number(chapterSelect.value)), 0, playing));
  const closeButton = button('離開', () => close(), 'ag-rd-close');
  closeButton.setAttribute('aria-label', '離開帶你讀經');
  const scroll = h('div', { className: 'ag-rd-scroll' });
  const playButton = button('播放', () => togglePlay(), 'ag-rd-play');
  const control = (label: string, symbol: string, action: () => void) => {
    const el = button(symbol, action, 'ag-rd-step');
    el.setAttribute('aria-label', label);
    el.title = label;
    return el;
  };
  const speedSelect = h('select', { className: 'ag-rd-select ag-rd-speed', 'aria-label': '速度' },
    ...SPEEDS.map((value) => h('option', { value: String(value), selected: value === speed }, `${value}×`)));
  speedSelect.addEventListener('change', () => {
    speed = Number(speedSelect.value);
    storage.set('speed', String(speed));
    if (playing && voiceOn) speakFromCursor();
  });
  const voiceButton = button('朗讀', () => toggleVoice(), 'ag-rd-voice');
  voiceButton.setAttribute('aria-pressed', 'false');
  const voiceNote = h('p', { className: 'ag-rd-voice-note', hidden: true }, '這台裝置沒有中文語音，可以用文字跟著讀。');
  const panel = h('section', { className: 'ag-rd-panel', role: 'region', 'aria-label': '帶你讀經', hidden: true },
    h('header', { className: 'ag-rd-head' },
      h('div', { className: 'ag-rd-title' }, h('span', { className: 'ag-rd-eyebrow' }, '帶你讀經'), h('strong', {}, reading.bookName)),
      chapterSelect, closeButton),
    scroll,
    h('footer', { className: 'ag-rd-controls' },
      h('div', { className: 'ag-rd-transport' },
        control('上一節', '⇤', () => stepVerse(-1)),
        control('上一個名字', '‹', () => stepName(-1)),
        playButton,
        control('下一個名字', '›', () => stepName(1)),
        control('下一節', '⇥', () => stepVerse(1))),
      h('div', { className: 'ag-rd-options' }, speedSelect, voiceButton),
      voiceNote,
      h('p', { className: 'ag-rd-credit' }, '經文：和合本　讀經字型：霞鶩文楷 TC（SIL Open Font License 1.1）')));
  const returnButton = button('回到朗讀處', () => {
    follow = true;
    returnButton.hidden = true;
    focusCamera(true);
  }, 'ag-rd-return');
  returnButton.hidden = true;
  const chapterCard = h('div', { className: 'ag-rd-chapter-card', 'aria-hidden': 'true' });
  const stage = h('div', { className: 'ag-rd-stage' }, chapterCard, returnButton);

  canvas.onUserCamera(() => {
    if (!isOpen || !follow) return;
    follow = false;
    returnButton.hidden = false;
  });

  function firstVerseOf(chapter: number): number {
    return verses.find((item) => item.chapter === chapter)?.index ?? 0;
  }

  function renderChapter(chapter: number) {
    renderedChapter = chapter;
    chapterSelect.value = String(chapter);
    const info = reading.chapters.find((item) => item.n === chapter)!;
    const article = h('article', { className: 'ag-rd-text' },
      h('h2', { className: 'ag-rd-chapter-head' },
        h('span', { className: 'ag-rd-chapter-no' }, `第${chapterName(chapter)}章`),
        h('span', { className: 'ag-rd-chapter-name' }, info.title)));
    for (const item of verses.filter((entry) => entry.chapter === chapter)) {
      const line = h('span', { className: 'ag-rd-line' });
      let position = 0;
      const text = item.verse.text;
      const segment = (s: number, e: number, token?: ReadingToken, tokenIndex?: number) => {
        const el = h('span', { className: `ag-rd-seg${token ? ` ag-rd-k-${token.k}${token.k === 'p' && token.id ? ' ag-rd-person' : ''}` : ''}`,
          dataset: { s: String(s), e: String(e) } }, text.slice(s, e));
        if (token && token.k === 'p' && token.id && tokenIndex !== undefined) {
          el.setAttribute('role', 'button');
          el.tabIndex = 0;
          const go = () => jump(item.index, token.s, playing);
          el.addEventListener('click', go);
          el.addEventListener('keydown', (event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); go(); } });
        }
        line.append(el);
      };
      item.verse.t.forEach((token, tokenIndex) => {
        if (token.s > position) segment(position, token.s);
        segment(token.s, token.e, token, tokenIndex);
        position = token.e;
      });
      if (position < text.length) segment(position, text.length);
      const number = button(String(item.verse.v), () => jump(item.index, 0, playing), 'ag-rd-vno');
      number.setAttribute('aria-label', `從第 ${item.verse.v} 節讀起`);
      const paragraph = h('p', { className: 'ag-rd-verse', dataset: { i: String(item.index) } }, number, line);
      article.append(paragraph);
      if (item.verse.note !== undefined && reading.notes[item.verse.note]) {
        article.append(h('aside', { className: 'ag-rd-note', dataset: { i: String(item.index) } },
          h('span', { className: 'ag-rd-note-label' }, '讀經提醒'), reading.notes[item.verse.note]!.text));
      }
    }
    scroll.replaceChildren(article);
    scroll.scrollTop = 0;
  }

  // 經文欄只捲動自己，不動整頁
  function scrollToVerse(index: number, smooth: boolean) {
    const paragraph = scroll.querySelector<HTMLElement>(`.ag-rd-verse[data-i="${index}"]`);
    if (!paragraph) return;
    // 每章第一節捲回最上面，章名才看得到
    const inside = paragraph.getBoundingClientRect().top - scroll.getBoundingClientRect().top + scroll.scrollTop;
    const top = verses[index]!.verse.v === 1 ? 0 : inside - scroll.clientHeight * 0.22;
    scroll.scrollTo({ top: Math.max(0, top), behavior: smooth && motionOn() ? 'smooth' : 'auto' });
  }

  function paintText() {
    for (const paragraph of scroll.querySelectorAll<HTMLElement>('.ag-rd-verse')) {
      const index = Number(paragraph.dataset.i);
      paragraph.classList.toggle('is-past', index < at);
      paragraph.classList.toggle('is-now', index === at);
    }
    for (const note of scroll.querySelectorAll<HTMLElement>('.ag-rd-note')) note.classList.toggle('is-shown', Number(note.dataset.i) <= at);
    const paragraph = scroll.querySelector<HTMLElement>(`.ag-rd-verse[data-i="${at}"]`);
    if (!paragraph) return;
    for (const segment of paragraph.querySelectorAll<HTMLElement>('.ag-rd-seg')) {
      const s = Number(segment.dataset.s);
      const e = Number(segment.dataset.e);
      segment.classList.toggle('is-read', e <= cursor);
      segment.classList.toggle('is-now', s <= cursor && cursor < e && segment.classList.contains('ag-rd-person'));
    }
  }

  // ── 鏡頭與標記 ───────────────────────────────────────
  function focusTarget(): string | null {
    if (marks.current) return marks.current;
    const verse = verses[at]!.verse;
    return verse.hold ?? lastPersonInSection.get(verse.sec ?? '') ?? null;
  }
  function focusCamera(animate: boolean) {
    const target = focusTarget();
    if (target) void canvas.flyTo(target, animate);
  }

  function enterVerse(index: number, keepTrail = true, card = true) {
    const previous = marks;
    at = Math.max(0, Math.min(verses.length - 1, index));
    cursor = 0;
    fired = 0;
    const item = verses[at]!;
    const chapterChanged = item.chapter !== renderedChapter;
    if (chapterChanged) {
      renderChapter(item.chapter);
      if (card) showChapterCard(item);
    }
    marks = { ...emptyMarks(), trail: keepTrail ? new Set([...previous.lit]) : new Set() };
    const ids = new Set<string>();
    for (const token of item.verse.t) {
      if (token.id) ids.add(token.id);
      if (token.of) ids.add(token.of);
      for (const from of token.from ?? []) ids.add(from);
      for (const to of token.to ?? []) ids.add(to);
    }
    if (item.verse.hold) ids.add(item.verse.hold);
    canvas.expandMany([...ids]);
    canvas.setReadingMarks(marks);
    const firstPerson = item.verse.t.find((token) => token.k === 'p' && token.id);
    if (!firstPerson && follow) focusCamera(true);
    // 換章的時候，趁章名卡還在，鏡頭先飛到這一章的第一個人
    else if (firstPerson && follow && chapterChanged) void canvas.flyTo(firstPerson.id!, true);
    history.replaceState(null, '', `${location.pathname}${location.search}#read=${encodeURIComponent(item.key)}`);
    storage.set('at', item.key);
    paintText();
    scrollToVerse(at, true);
  }

  /** 讀到 cursor 為止的標記；quiet 時不要落筆動畫（跳讀時用） */
  function fireUpTo(quiet: boolean) {
    const item = verses[at]!;
    const tokens = item.verse.t;
    const fresh = new Set<string>();
    let moved = false;
    while (fired < tokens.length && tokens[fired]!.s <= cursor) {
      const token = tokens[fired]!;
      const key = `${at}:${fired}`;
      if (token.k === 'p' && token.id) {
        marks.lit.add(token.id);
        marks.current = token.id;
        if (item.verse.sec) lastPersonInSection.set(item.verse.sec, token.id);
        for (const from of token.from ?? []) {
          marks.ink.push({ from, to: token.id, key: `${key}:${from}` });
          fresh.add(`${key}:${from}`);
        }
        for (const to of token.to ?? []) {
          marks.ink.push({ from: token.id, to, key: `${key}:>${to}` });
          fresh.add(`${key}:>${to}`);
        }
        moved = true;
      } else if (token.k === 't' && token.of) {
        marks.seals.push({ id: token.of, label: item.verse.text.slice(token.s, token.e), key });
        fresh.add(key);
      }
      fired += 1;
    }
    if (fresh.size || moved) {
      marks = { ...marks, fresh: quiet ? new Set() : fresh };
      canvas.setReadingMarks(marks);
      if (moved && follow) focusCamera(!quiet);
    }
  }

  function jump(index: number, toChar: number, keepPlaying: boolean) {
    stopVoice();
    enterVerse(index, false);
    cursor = toChar;
    fireUpTo(true);
    if (follow) focusCamera(true);
    paintText();
    pauseUntil = performance.now() + 250;
    if (keepPlaying) play(); else pause();
  }

  function stepVerse(direction: -1 | 1) {
    jump(Math.max(0, Math.min(verses.length - 1, at + direction)), 0, playing);
  }

  /** 上一個／下一個人名，可以跨節 */
  function stepName(direction: -1 | 1) {
    const persons = (index: number) => verses[index]!.verse.t.filter((token) => token.k === 'p' && token.id);
    if (direction > 0) {
      const next = persons(at).find((token) => token.s > cursor);
      if (next) { jump(at, next.s, playing); return; }
      for (let index = at + 1; index < verses.length; index += 1) {
        const first = persons(index)[0];
        if (first) { jump(index, first.s, playing); return; }
      }
    } else {
      // 正在讀的是 cursor 之前最後一個名字；往回就是它的前一個
      const list = persons(at);
      let current = -1;
      list.forEach((token, index) => { if (token.s <= cursor) current = index; });
      if (current > 0) { jump(at, list[current - 1]!.s, playing); return; }
      for (let index = at - 1; index >= 0; index -= 1) {
        const list = persons(index);
        if (list.length) { jump(index, list[list.length - 1]!.s, playing); return; }
      }
    }
  }

  // ── 播放 ─────────────────────────────────────────────
  function play() {
    playing = true;
    playButton.textContent = '暫停';
    playButton.classList.add('is-playing');
    lastFrame = performance.now();
    if (voiceOn) speakFromCursor();
    cancelAnimationFrame(frame);
    frame = requestAnimationFrame(tick);
  }
  function pause() {
    playing = false;
    playButton.textContent = '播放';
    playButton.classList.remove('is-playing');
    stopVoice();
    cancelAnimationFrame(frame);
  }
  function togglePlay() { if (playing) pause(); else play(); }

  function endOfVerse() {
    if (at >= verses.length - 1) { pause(); return; }
    enterVerse(at + 1);
    // 換章時讓章名卡停一下
    const gap = verses[at]!.chapter !== verses[at - 1]!.chapter ? 2600 : 520 / speed;
    pauseUntil = performance.now() + gap;
    window.clearTimeout(gapTimer);
    if (voiceOn && playing) gapTimer = window.setTimeout(() => { if (playing && voiceOn) speakFromCursor(); }, gap);
  }

  function tick(now: number) {
    if (!playing) return;
    // 背景分頁回來時不要一口氣跳太多
    const dt = Math.max(0, Math.min(0.25, (now - lastFrame) / 1000));
    lastFrame = now;
    if (!voiceOn && now >= pauseUntil) {
      const text = verses[at]!.verse.text;
      cursor = Math.min(text.length, cursor + dt * CHARS_PER_SECOND * speed);
      fireUpTo(false);
      paintText();
      if (cursor >= text.length) endOfVerse();
    }
    frame = requestAnimationFrame(tick);
  }

  // ── 朗讀 ─────────────────────────────────────────────
  function speakFromCursor() {
    const speech = options.speech;
    if (!speech || !voiceOn) return;
    const item = verses[at]!;
    const start = Math.floor(cursor);
    const index = at;
    speech.speak(item.verse.text, {
      rate: speed,
      startChar: start >= item.verse.text.length ? 0 : start,
      onBoundary(charIndex) {
        if (index !== at || !playing) return;
        cursor = Math.max(cursor, charIndex);
        fireUpTo(false);
        paintText();
      },
      onEnd() {
        if (index !== at || !playing) return;
        cursor = item.verse.text.length;
        fireUpTo(false);
        paintText();
        endOfVerse();
      },
    });
  }
  function stopVoice() {
    window.clearTimeout(gapTimer);
    options.speech?.stop();
  }
  async function toggleVoice() {
    const speech = options.speech;
    if (!voiceOn) {
      const ok = Boolean(speech?.supported()) && Boolean(await speech?.ready());
      voiceNote.hidden = ok;
      if (!ok) return;
      voiceOn = true;
      if (playing) speakFromCursor();
    } else {
      voiceOn = false;
      stopVoice();
      lastFrame = performance.now();
    }
    voiceButton.setAttribute('aria-pressed', String(voiceOn));
    voiceButton.classList.toggle('is-on', voiceOn);
  }

  // ── 章名卡 ───────────────────────────────────────────
  let cardTimer = 0;
  function showChapterCard(item: FlatVerse) {
    window.clearTimeout(cardTimer);
    chapterCard.replaceChildren(
      h('span', { className: 'ag-rd-card-seal' }, reading.bookName),
      h('span', { className: 'ag-rd-card-no' }, `第${chapterName(item.chapter)}章`),
      h('span', { className: 'ag-rd-card-title' }, item.chapterTitle));
    chapterCard.classList.remove('is-on');
    chapterCard.getBoundingClientRect();
    chapterCard.classList.add('is-on');
    cardTimer = window.setTimeout(() => chapterCard.classList.remove('is-on'), 2400);
  }

  // ── 開關 ─────────────────────────────────────────────
  function parse(ref: string): number | null {
    const match = new RegExp(`^${book}(\\d+):(\\d+)$`).exec(ref.trim());
    if (!match) return null;
    const found = verses.find((item) => item.chapter === Number(match[1]) && item.verse.v === Number(match[2]));
    return found ? found.index : null;
  }

  function open(ref?: string, autoplay = true) {
    const index = (ref ? parse(ref) : null) ?? parse(storage.get('at') ?? '') ?? 0;
    if (!isOpen) {
      isOpen = true;
      expandedBefore = canvas.getExpanded();
      panel.hidden = false;
      stage.hidden = false;
      document.documentElement.classList.add('ag-reading');
      canvas.setReading(true);
      options.onOpenChange?.(true);
      document.addEventListener('keydown', onKey);
    }
    follow = true;
    returnButton.hidden = true;
    renderedChapter = 0;
    // 從連結直接打開到章中間的某一節時，不放章名卡
    enterVerse(index, false, verses[index]!.verse.v === 1);
    const firstPerson = verses[index]!.verse.t.find((token) => token.k === 'p' && token.id);
    if (firstPerson && !autoplay) { cursor = firstPerson.s; fireUpTo(true); paintText(); }
    focusCamera(false);
    pauseUntil = performance.now() + (verses[index]!.verse.v === 1 ? 2600 : 400);
    if (autoplay) play(); else pause();
  }

  function close() {
    if (!isOpen) return;
    pause();
    isOpen = false;
    panel.hidden = true;
    stage.hidden = true;
    document.documentElement.classList.remove('ag-reading');
    canvas.setReading(false);
    if (expandedBefore) canvas.setExpanded(expandedBefore);
    expandedBefore = null;
    document.removeEventListener('keydown', onKey);
    if (location.hash.startsWith('#read=')) history.replaceState(null, '', `${location.pathname}${location.search}`);
    options.onOpenChange?.(false);
  }

  function onKey(event: KeyboardEvent) {
    const target = event.target as HTMLElement | null;
    if (target && /^(INPUT|SELECT|TEXTAREA)$/.test(target.tagName)) return;
    if (document.querySelector('.ag-modal-layer:not([hidden])')) return;
    if (event.key === 'ArrowRight') { event.preventDefault(); stepName(1); }
    else if (event.key === 'ArrowLeft') { event.preventDefault(); stepName(-1); }
    // 焦點在按鈕或人名上時，空白鍵是按那個東西，不是播放／暫停
    else if (event.key === ' ' && !target?.closest('button, [role="button"]')) { event.preventDefault(); togglePlay(); }
    else if (event.key === 'Escape') close();
  }

  stage.hidden = true;
  return { panel, stage, open, close, isOpen: () => isOpen };
}
