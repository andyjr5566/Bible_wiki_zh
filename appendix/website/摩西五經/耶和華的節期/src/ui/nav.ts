/**
 * 月份導覽與日數牌。
 * - 桌機右側細直線、手機頂部細橫線，標示正月到七月七個刻度＋一個血紅色的目前位置標記。
 *   有內容的月份可以點；沒有內容的月份顯示為淡色、不可點。
 * - 點擊跳轉：先播約 250ms 的直向刻線抹除遮罩，再 window.scrollTo({ behavior: 'instant' })，再抹開。
 *   不用 smooth scroll、不用 scrollIntoView。
 * - 右上角小日數牌：badge 優先，其次 day（「正月　十五」），再其次 count 拍的「第 n 日」，都沒有就隱藏。
 * - 沒有 month 的章，標記停在前一個位置並改成空心。
 */
import { gsap } from 'gsap';
import { SITE } from '../data/site';
import { story } from '../story/state';
import type { Beat, StoryChapter } from '../data/types';
import type { BeatRef } from './beats';
import { clamp, h } from './dom';
import { dayName } from './text';

const HOLLOW_TITLE = '經文沒有給這個節期月日';

const MONTHS = ['正月', '二月', '三月', '四月', '五月', '六月', '七月'];
const STRIPES = 24;

export interface Nav {
  update(): void;
  /** 跳轉到某個元素的頂端（含刻線抹除轉場） */
  jumpTo(el: HTMLElement): void;
}

export function createNav(host: HTMLElement, beats: BeatRef[]): Nav {
  // 每個月份第一個有內容的拍
  const target = new Map<number, HTMLElement>();
  for (const ref of beats) {
    const m = ref.chapter.kind === 'opening' ? 1 : ref.chapter.month;
    if (m && !target.has(m)) target.set(m, ref.el);
  }

  // ---- 刻線抹除遮罩 ----
  const stripes: HTMLElement[] = [];
  const wipeEl = h('div', { class: 'jf-wipe', 'aria-hidden': 'true' });
  for (let i = 0; i < STRIPES; i++) {
    const st = h('i', { class: 'jf-wipe-stripe' });
    stripes.push(st);
    wipeEl.append(st);
  }
  let busy = false;

  function wipe(mid: () => void) {
    if (busy) return;
    busy = true;
    wipeEl.style.display = 'flex';
    const done = () => {
      wipeEl.style.display = 'none';
      busy = false;
    };
    if (story.motionOff) {
      // 減少動態：不做刻線，改成短短的淡入淡出，跳轉時不會突然閃一下
      gsap.set(stripes, { scaleY: 1, transformOrigin: '50% 0%' });
      gsap
        .timeline({ onComplete: done })
        .fromTo(wipeEl, { opacity: 0 }, { opacity: 1, duration: 0.12, ease: 'none' })
        .add(mid)
        .to(wipeEl, { opacity: 0, duration: 0.14, ease: 'none' });
      return;
    }
    gsap.set(wipeEl, { opacity: 1 });
    gsap
      .timeline({ onComplete: done })
      .fromTo(stripes, { scaleY: 0, transformOrigin: '50% 0%' }, { scaleY: 1, duration: 0.16, ease: 'power2.inOut', stagger: { amount: 0.09, from: 'random' } })
      .add(mid)
      .set(stripes, { transformOrigin: '50% 100%' })
      .to(stripes, { scaleY: 0, duration: 0.16, ease: 'power2.inOut', stagger: { amount: 0.09, from: 'random' } });
  }

  function jumpTo(el: HTMLElement) {
    const top = Math.max(0, window.scrollY + el.getBoundingClientRect().top);
    wipe(() => window.scrollTo({ top, behavior: 'instant' }));
  }

  // ---- 月份刻度 ----
  const marker = h('li', { class: 'jf-marker', 'aria-hidden': 'true' });
  const ticks: { month: number; li: HTMLElement }[] = [];
  const rail = h('ol', { class: 'jf-rail' });
  MONTHS.forEach((name, i) => {
    const month = i + 1;
    const el = target.get(month);
    const li = h('li', { class: 'jf-tick', style: `--n:${(i / (MONTHS.length - 1)).toFixed(5)}` },
      el
        ? h('button', { type: 'button', class: 'jf-m', onclick: () => jumpTo(el), 'aria-label': `跳到${name}` }, h('span', { class: 'jf-m-label' }, name))
        : h('button', { type: 'button', class: 'jf-m is-off', disabled: true }, h('span', { class: 'jf-m-label' }, name)));
    ticks.push({ month, li });
    rail.append(li);
  });
  rail.append(marker);
  const nav = h('nav', { class: 'jf-months', 'aria-label': '月份導覽' }, rail);

  // ---- 日數牌 ----
  const dayEl = h('div', { class: 'jf-day', role: 'status', 'aria-live': 'polite', 'aria-atomic': 'true' });
  host.append(nav, dayEl, wipeEl);

  const chapters = new Map(SITE.chapters.map((c) => [c.id, c]));
  const beatByKey = new Map(beats.map((r) => [`${r.chapter.id}/${r.beat.id}`, r.beat]));
  const span = MONTHS.length - 1;
  const posOf = (month: number, day: number) => Math.round((((month - 1) + (day - 1) / 30) / span) * 10000) / 10000;

  // 沒有 month 的章：標記停在前一個有月份的章的章末位置
  const holdPos = new Map<string, number>();
  {
    let prev = posOf(1, 14);
    for (const c of SITE.chapters) {
      if (c.kind === 'opening') prev = posOf(1, 14);
      else if (c.month) prev = posOf(c.month, (c.day ?? 1) + 1);
      else holdPos.set(c.id, prev);
    }
  }

  let lastText: string | null | undefined;
  let lastP = -1;
  let lastMonth = -1;
  let lastHollow: boolean | null = null;

  function dayText(c: StoryChapter | undefined, b: Beat | undefined): string | null {
    if (!c || !b) return null;
    if (b.badge) return b.badge;
    const month = c.kind === 'opening' ? 1 : c.month;
    if (b.day !== undefined && month) return `${MONTHS[month - 1] ?? `${month}月`}　${dayName(story.day)}`;
    if (b.interaction === 'count') return `第 ${clamp(Math.ceil(story.count), 1, 50)} 日`;
    return null;
  }

  function update() {
    const c = chapters.get(story.chapter);
    const b = beatByKey.get(`${story.chapter}/${story.beat}`);

    // 日數牌：文字改變才更新（避免報讀器一直唸）
    const text = dayText(c, b);
    if (text !== lastText) {
      lastText = text;
      dayEl.classList.toggle('is-on', text !== null);
      dayEl.setAttribute('aria-hidden', text !== null ? 'false' : 'true');
      if (text !== null) dayEl.textContent = text;
    }

    // 目前位置：開場照 story.day；有月份的節期章從節期日起，隨章進度走到隔天；沒有月份的章停在前一個位置
    const hollow = !!c && c.kind === 'feast' && !c.month;
    let n: number;
    if (hollow) n = holdPos.get(c!.id) ?? 0;
    else if (c?.kind === 'opening') n = posOf(1, story.day);
    else n = posOf(c?.month ?? 1, (c?.day ?? 1) + story.chapterProgress);
    if (n !== lastP) {
      lastP = n;
      marker.style.setProperty('--n', String(n));
    }
    if (hollow !== lastHollow) {
      lastHollow = hollow;
      marker.classList.toggle('is-hollow', hollow);
      if (hollow) marker.setAttribute('title', HOLLOW_TITLE);
      else marker.removeAttribute('title');
    }
    if (story.month !== lastMonth) {
      lastMonth = story.month;
      for (const t of ticks) t.li.classList.toggle('is-current', t.month === story.month);
    }
  }

  return { update, jumpTo };
}
