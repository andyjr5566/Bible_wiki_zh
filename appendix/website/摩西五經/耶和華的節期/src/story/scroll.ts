/**
 * 捲動綁定：用 ScrollTrigger 把每個 <section>（一拍）的捲動進度寫進共享的 story 物件。
 * - 捲動直接帶動畫面（進度與捲動位置一對一，沒有時間差），讀者停下來畫面也停。
 * - 不用 Lenis／smooth scroll，不用 scrollIntoView，不自動捲頁。
 * - 「目前這一拍」＝畫面 60% 高度的那條線正落在哪個 section 裡，所以下一個說明框滑入時畫面就開始轉場。
 */
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { story } from './state';
import { clamp } from '../ui/dom';

gsap.registerPlugin(ScrollTrigger);
// 手機網址列收合造成的高度變化不要整頁重算，避免捲動位置跳動
ScrollTrigger.config({ ignoreMobileResize: true });

export interface BeatInfo {
  chapterId: string;
  chapterKind: 'opening' | 'feast';
  beatId: string;
  cue: string;
  /** 開場用：這一拍月亮對應的日子 */
  day?: number;
  el: HTMLElement;
  box: HTMLElement;
}

export interface ScrollController {
  /** 目前所在的拍（0 起算） */
  index(): number;
  refresh(): void;
}

/** 畫面上的這條線（視窗高度的比例）決定「目前這一拍」 */
const LINE = 0.6;

/** 系統偏好：暗色、減少動態。每次變化都即時寫進 story。 */
export function bindPreferences(): void {
  const dark = window.matchMedia('(prefers-color-scheme: dark)');
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  story.dark = dark.matches;
  story.motionOff = reduce.matches;
  const on = (mq: MediaQueryList, fn: (m: boolean) => void) => {
    if (mq.addEventListener) mq.addEventListener('change', (e) => fn(e.matches));
    else (mq as MediaQueryList).addListener((e) => fn(e.matches));
  };
  on(dark, (m) => {
    story.dark = m;
  });
  on(reduce, (m) => {
    story.motionOff = m;
  });
}

export function initScroll(beats: BeatInfo[], onBeat: (index: number, prev: number) => void): ScrollController {
  const n = beats.length;
  const triggers: ScrollTrigger[] = [];
  const starts = new Array<number>(n).fill(0);
  const ends = new Array<number>(n).fill(1);
  let current = -1;

  // 開場月亮的日子：每一拍在 0.3–0.7 的區間停在自己的日子，拍與拍之間連續內插
  const dayPts: { s: number; d: number }[] = [];
  beats.forEach((b, i) => {
    if (b.day === undefined) return;
    dayPts.push({ s: i + 0.3, d: b.day }, { s: i + 0.7, d: b.day });
  });
  function dayAt(i: number, p: number): number {
    if (!dayPts.length) return story.day;
    const s = i + p;
    if (s <= dayPts[0].s) return dayPts[0].d;
    const last = dayPts[dayPts.length - 1];
    if (s >= last.s) return last.d;
    let k = 0;
    while (k < dayPts.length - 2 && s > dayPts[k + 1].s) k++;
    const a = dayPts[k];
    const b = dayPts[k + 1];
    return a.d + ((b.d - a.d) * (s - a.s)) / (b.s - a.s);
  }

  // 每章的起訖拍
  const chapterSpan = new Map<string, { first: number; last: number }>();
  beats.forEach((b, i) => {
    const c = chapterSpan.get(b.chapterId);
    if (c) c.last = i;
    else chapterSpan.set(b.chapterId, { first: i, last: i });
  });

  function recompute() {
    for (let i = 0; i < n; i++) {
      const st = triggers[i];
      if (!st) continue;
      starts[i] = i === 0 ? 0 : st.start;
      ends[i] = st.end;
    }
  }

  function sync(y: number) {
    let i = 0;
    while (i < n - 1 && y >= starts[i + 1]) i++;
    const span = Math.max(1, ends[i] - starts[i]);
    const p = clamp((y - starts[i]) / span);
    const b = beats[i];
    if (i !== current) {
      const prev = current;
      current = i;
      story.chapter = b.chapterId;
      story.beat = b.beatId;
      story.cue = b.cue;
      story.prevCue = i > 0 ? beats[i - 1].cue : b.cue;
      onBeat(i, prev);
    }
    story.beatProgress = p;
    const cs = chapterSpan.get(b.chapterId)!;
    const c0 = starts[cs.first];
    const c1 = ends[cs.last];
    story.chapterProgress = clamp((y - c0) / Math.max(1, c1 - c0));
    story.pageProgress = clamp(y / Math.max(1, ScrollTrigger.maxScroll(window)));
    story.day = dayAt(i, p);
  }

  beats.forEach((b, i) => {
    const st = ScrollTrigger.create({
      trigger: b.el,
      start: () => (i === 0 ? 0 : `top ${LINE * 100}%`),
      end: () => `bottom ${LINE * 100}%`,
      onRefresh: () => {
        recompute();
        sync(window.scrollY);
      },
      onUpdate: (self) => sync(self.scroll()),
      onLeave: (self) => {
        // 最後一拍之後（章末、頁尾）：進度停在 1
        if (i === n - 1) sync(self.scroll());
      },
    });
    triggers.push(st);

    // 說明框進場：捲進來時淡入並從下方滑上來（減少動態時只淡入，見 CSS）
    ScrollTrigger.create({
      trigger: b.el,
      start: 'top 80%',
      end: 'bottom 15%',
      toggleClass: { targets: b.box, className: 'jf-in' },
    });
  });

  // 整頁進度：最後一拍之後（章末、頁尾）也要繼續走到 1
  ScrollTrigger.create({
    start: 0,
    end: 'max',
    onUpdate: (self) => {
      story.pageProgress = self.progress;
    },
  });

  recompute();
  sync(window.scrollY);
  // 平時不另外起迴圈；ScrollTrigger 在捲動時會呼叫 onUpdate

  return {
    index: () => Math.max(0, current),
    refresh: () => ScrollTrigger.refresh(),
  };
}
