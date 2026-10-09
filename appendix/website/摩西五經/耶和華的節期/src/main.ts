import './styles/tokens.css';
import './styles/base.css';
import './styles/story.css';
import './styles/chrome.css';
import './styles/end.css';

import { SITE } from './data/site';
import { createAudio } from './audio/audio';
import { bindPreferences, initScroll, type BeatInfo } from './story/scroll';
import { story } from './story/state';
import { anyPanelOpen, buildBeats, closeOpenPanel, setPanelOn } from './ui/beats';
import { createChrome } from './ui/chrome';
import { createCoach } from './ui/coach';
import { h } from './ui/dom';
import { buildCredits, buildEndings } from './ui/ending';
import { createHeadFade } from './ui/headfade';
import { createHyssopUI } from './ui/hyssop';
import { createNav } from './ui/nav';
import { createStage, type Stage } from './ui/stage';

function boot() {
  const root = document.documentElement;
  const app = document.getElementById('jf-app')!;
  const canvas = document.getElementById('jf-canvas') as HTMLCanvasElement;
  const fallback = document.getElementById('jf-fallback')!;
  const loading = document.getElementById('jf-loading');

  bindPreferences();

  // ---- 版面：每一拍一個 section ----
  const hyssop = createHyssopUI(canvas, app);
  const main = h('main', { class: 'jf-story', id: 'jf-story' });
  const beats = buildBeats(main, hyssop);
  app.append(main);
  for (const end of buildEndings()) {
    const cid = end.getAttribute('data-chapter');
    const lastOfChapter = [...beats].reverse().find((b) => b.chapter.id === cid);
    if (lastOfChapter) lastOfChapter.el.after(end);
    else main.append(end);
  }
  app.append(buildCredits());

  // ---- 場景、聲音、導覽 ----
  let stage: Stage | null = null;
  const audio = createAudio(SITE.audio, beats.map((b) => b.beat.cue), () => !!stage?.scene);
  stage = createStage(
    canvas,
    fallback,
    (e) => {
      audio.onSceneEvent(e);
      hyssop.onEvent(e);
    },
    (scene) => hyssop.setScene(scene),
  );
  const nav = createNav(app, beats);
  const coach = createCoach(app);
  createChrome(app, audio, () => coach.open());
  const mobileQ = window.matchMedia('(max-width: 720px)');
  const headFade = createHeadFade(mobileQ);

  // ---- 捲動 ----
  const infos: BeatInfo[] = beats.map((b) => ({
    chapterId: b.chapter.id,
    chapterKind: b.chapter.kind,
    beatId: b.beat.id,
    cue: b.beat.cue,
    day: b.beat.day,
    el: b.el,
    box: b.box,
  }));
  const hyssopRef = beats.find((b) => b.beat.interaction === 'hyssop');
  let sideLocked = false;
  const mealRef = beats.find((b) => b.panel);

  const scroll = initScroll(infos, (index) => {
    audio.onBeat(index);
    stage?.setCue(story.cue);
    // 手機的面板蓋在說明框上方：離開那一拍就收起來
    if (mobileQ.matches && anyPanelOpen()) {
      const open = beats.find((b) => b.hasPanelOpen());
      if (open && open.index !== index) closeOpenPanel(false);
    }
    sideLocked = false;
    // 室內分格：進入那一拍才顯示
    for (const b of beats) if (b.panel) setPanelOn(b.panel, b.index === index);
  });
  stage.setCue(story.cue);

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && anyPanelOpen() && !document.querySelector('dialog[open]')) closeOpenPanel(true);
  });
  window.addEventListener('resize', () => {
    sideLocked = false;
  });

  // 桌機：說明框放在畫面左或右，挑跟可互動區域重疊較少的那一邊（把手最重、盆次之、門框區最輕）
  const RECT_WEIGHT = [4, 2, 0.5];
  function pickSide(rects: DOMRect[]): 'left' | 'right' {
    const box = hyssopRef!.box;
    const bw = box.offsetWidth;
    const bh = box.offsetHeight;
    const vw = window.innerWidth;
    const top = parseFloat(getComputedStyle(box).top) || 120;
    const xs = {
      left: Math.min(96, Math.max(24, vw * 0.06)),
      right: vw - Math.min(150, Math.max(100, vw * 0.09)) - bw,
    };
    const cost = (x0: number) => {
      let c = 0;
      rects.forEach((r, i) => {
        const w = Math.max(0, Math.min(x0 + bw, r.right) - Math.max(x0, r.left));
        const hh = Math.max(0, Math.min(top + bh, r.bottom) - Math.max(top, r.top));
        c += w * hh * (RECT_WEIGHT[i] ?? 1);
      });
      return c;
    };
    return cost(xs.left) <= cost(xs.right) ? 'left' : 'right';
  }

  const firstEnd = document.querySelector('.jf-end');

  // 徽章要避開的固定介面：標題列、月份導覽、聲音鈕、日數牌（顯示時）、往下捲提示，再加上說明框
  const fixedUi = [...document.querySelectorAll<HTMLElement>('.jf-brand, .jf-bar .jf-btn, .jf-months, .jf-day, .jf-scrollcue')];
  const avoidRects: DOMRect[] = [];
  function collectAvoid(box: HTMLElement): DOMRect[] {
    avoidRects.length = 0;
    for (const el of fixedUi) {
      if (el.classList.contains('jf-day') && !el.classList.contains('is-on')) continue;
      avoidRects.push(el.getBoundingClientRect());
    }
    avoidRects.push(box.getBoundingClientRect());
    return avoidRects;
  }

  /** 手機：分格的高度不能碰到下方貼底的說明框頂端，碰到就縮（最矮 120px） */
  function fitMealPanel() {
    if (!mealRef?.panel) return;
    if (!mobileQ.matches) {
      mealRef.panel.style.removeProperty('--jf-panel-h');
      return;
    }
    const H = window.innerHeight;
    const base = Math.min(290, Math.max(200, H * 0.34));
    const top = mealRef.panel.getBoundingClientRect().top;
    const boxTop = H - 8 - mealRef.box.offsetHeight;
    const h = Math.min(base, Math.max(120, boxTop - top - 12));
    mealRef.panel.style.setProperty('--jf-panel-h', `${Math.round(h)}px`);
  }

  // ---- 每幀：只做便宜的事（導覽標記、日數牌、觸控層與徽章的位置） ----
  const tick = () => {
    requestAnimationFrame(tick);
    if (document.hidden) return;
    nav.update();
    headFade.update();
    root.classList.toggle('jf-at-top', window.scrollY < 40);
    if (firstEnd) root.classList.toggle('jf-past-story', firstEnd.getBoundingClientRect().top < 110);
    const onHyssop = story.cue === 'hyssop';
    const rects = hyssop.update(onHyssop, onHyssop && hyssopRef ? collectAvoid(hyssopRef.box) : []);
    if (story.cue === 'meal') fitMealPanel();
    if (onHyssop && hyssopRef && !sideLocked && rects && rects.length && !mobileQ.matches) {
      hyssopRef.el.dataset.side = pickSide(rects);
      sideLocked = true;
    }
  };
  tick();

  // ---- 載入畫面：資料就緒（字型與場景）後淡出，不做假進度條 ----
  const fonts = (document as Document & { fonts?: FontFaceSet }).fonts;
  const fontsReady = fonts ? fonts.ready.then(() => undefined) : Promise.resolve();
  const timeout = new Promise<void>((r) => window.setTimeout(r, 2500));
  Promise.race([Promise.all([fontsReady, stage.whenReady()]).then(() => undefined), timeout]).then(() => {
    root.classList.add('jf-ready');
    loading?.classList.add('is-gone');
    window.setTimeout(() => loading?.remove(), 700);
    scroll.refresh();
    coach.openIfFirstVisit();
  });
  fontsReady.then(() => scroll.refresh());
}

boot();
