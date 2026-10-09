/**
 * 月份導覽與日數牌。
 * - 桌機右側細直線、手機頂部細橫線，標示正月到七月七個刻度＋一個血紅色的目前位置標記。
 *   有內容的月份可以點；沒有內容的月份顯示為淡色、不可點。
 * - 點擊跳轉：先播約 250ms 的直向刻線抹除遮罩，再 window.scrollTo({ behavior: 'instant' })，再抹開。
 *   不用 smooth scroll、不用 scrollIntoView。
 * - 右上角小日數牌「正月　初三」，只在開場章顯示，跟著 story.day 的整數變化。
 */
import { gsap } from 'gsap';
import { SITE } from '../data/site';
import { story } from '../story/state';
import type { BeatRef } from './beats';
import { h } from './dom';
import { dayName } from './text';

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
  let lastDay = -1;
  let lastShow: boolean | null = null;
  let lastP = -1;
  let lastMonth = -1;

  function update() {
    const c = chapters.get(story.chapter);
    const isOpening = c?.kind === 'opening';

    // 日數牌：整數改變才更新文字（避免報讀器一直唸）
    if (isOpening !== lastShow) {
      lastShow = isOpening;
      dayEl.classList.toggle('is-on', isOpening);
      dayEl.setAttribute('aria-hidden', isOpening ? 'false' : 'true');
    }
    if (isOpening) {
      const d = Math.min(14, Math.max(1, Math.round(story.day)));
      if (d !== lastDay) {
        lastDay = d;
        dayEl.textContent = `正月　${dayName(d)}`;
      }
    }

    // 目前位置：開場照 story.day；節期章從節期日起，隨章進度走到隔天
    const month = c ? (c.kind === 'opening' ? 1 : c.month ?? 1) : 1;
    const d = c?.kind === 'opening' ? story.day : (c?.day ?? 1) + story.chapterProgress;
    const pos = ((month - 1) + (d - 1) / 30) / (MONTHS.length - 1);
    const n = Math.round(pos * 10000) / 10000;
    if (n !== lastP) {
      lastP = n;
      marker.style.setProperty('--n', String(n));
    }
    if (month !== lastMonth) {
      lastMonth = month;
      for (const t of ticks) t.li.classList.toggle('is-current', t.month === month);
    }
  }

  return { update, jumpTo };
}
