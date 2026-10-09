// 開發用的場景實驗室：全螢幕 canvas＋浮動控制列。只在 dev server 使用（scene-lab.html），不進正式建置。
// 網址參數：?cue=midnight&p=0.5&day=14&dark=1&motion=1&ui=0&panel=1
import type { Palette } from '../data/types';
import { story } from '../story/state';
import type { SceneEvent, SceneHandle } from './api';
import { createScene } from './index';
import { CUES } from './tracks';

const palettes: Record<string, Palette> = {
  opening: { paper: '#efe5cf', ink: '#1a2342', accent: '#b9832e', glow: '#f7efd8' },
  passover: { paper: '#eadfc8', ink: '#131a33', accent: '#a3231b', glow: '#f0c46a' },
};

const $ = <T extends HTMLElement>(id: string): T => document.getElementById(id) as T;
const canvas = $<HTMLCanvasElement>('c');
const logEl = $<HTMLPreElement>('lab-log');
const cueSel = $<HTMLSelectElement>('lab-cue');
const chapSel = $<HTMLSelectElement>('lab-chapter');
const pRange = $<HTMLInputElement>('lab-p');
const dRange = $<HTMLInputElement>('lab-day');
const darkChk = $<HTMLInputElement>('lab-dark');
const motionChk = $<HTMLInputElement>('lab-motion');
const panel = $<HTMLDivElement>('lab-panel');

const DAY_OF: Record<string, number> = { title: 1, month: 3, 'day-10': 10, 'day-14': 14 };
for (const c of CUES) {
  const o = document.createElement('option');
  o.value = c;
  o.textContent = c;
  cueSel.appendChild(o);
}

const q = new URLSearchParams(location.search);
let forcePanel = q.get('panel') === '1';
if (q.get('ui') === '0') document.body.classList.add('lab-hide');
if (q.get('boxes') === '1') {
  document.getElementById('lab-box')?.classList.add('on');
  document.getElementById('lab-top')?.classList.add('on');
}

const lines: string[] = [];
const log = (e: SceneEvent) => {
  lines.push(`${(performance.now() / 1000).toFixed(1)}s ${e.type}${'part' in e ? ' ' + e.part : ''}${'auto' in e ? ' auto=' + e.auto : ''}`);
  if (lines.length > 12) lines.shift();
  logEl.textContent = lines.join('\n');
  (window as unknown as { __events: SceneEvent[] }).__events.push(e);
};
(window as unknown as { __events: SceneEvent[] }).__events = [];

function apply(): void {
  story.cue = cueSel.value;
  story.beat = cueSel.value;
  story.prevCue = CUES[Math.max(0, CUES.indexOf(cueSel.value as (typeof CUES)[number]) - 1)];
  story.chapter = CUES.indexOf(cueSel.value as (typeof CUES)[number]) >= 4 ? 'passover' : 'opening';
  chapSel.value = story.chapter;
  story.beatProgress = Number(pRange.value);
  story.day = Number(dRange.value);
  story.dark = darkChk.checked;
  story.motionOff = motionChk.checked;
  $('lab-pv').textContent = story.beatProgress.toFixed(2);
  $('lab-dv').textContent = story.day.toFixed(1);
  panel.style.display = forcePanel || story.cue === 'meal' ? 'block' : 'none';
}

// 初始值（網址參數）
const cue0 = q.get('cue') ?? 'title';
cueSel.value = (CUES as readonly string[]).includes(cue0) ? cue0 : 'title';
pRange.value = q.get('p') ?? '0.5';
dRange.value = q.get('day') ?? String(DAY_OF[cueSel.value] ?? 14);
darkChk.checked = q.get('dark') === '1';
motionChk.checked = q.get('motion') === '1';
apply();
for (const el of [cueSel, pRange, dRange, darkChk, motionChk]) el.addEventListener('input', apply);
cueSel.addEventListener('change', () => {
  if (DAY_OF[cueSel.value] !== undefined) dRange.value = String(DAY_OF[cueSel.value]);
  apply();
});

let scene: SceneHandle | null = null;
const fit = () => scene?.resize(window.innerWidth, window.innerHeight, window.devicePixelRatio || 1);
scene = createScene({ canvas, story, palettes, onEvent: log });
if (!scene) {
  logEl.textContent = '此環境不支援 WebGL2，createScene 回傳 null';
} else {
  fit();
  window.addEventListener('resize', fit);
}

document.querySelectorAll<HTMLButtonElement>('button[data-act]').forEach((b) =>
  b.addEventListener('click', () => scene?.hyssopAction(b.dataset.act as 'dip' | 'lintel' | 'left' | 'right')),
);
$('lab-reset').addEventListener('click', () => {
  story.hyssop.dipped = false;
  story.hyssop.marks = { lintel: false, left: false, right: false };
  story.hyssop.done = false;
  story.hyssop.auto = false;
});

// 供截圖腳本呼叫
(window as unknown as Record<string, unknown>).__lab = {
  set(o: { cue?: string; p?: number; day?: number; dark?: boolean; motion?: boolean }) {
    if (o.cue !== undefined) cueSel.value = o.cue;
    if (o.p !== undefined) pRange.value = String(o.p);
    if (o.day !== undefined) dRange.value = String(o.day);
    if (o.dark !== undefined) darkChk.checked = o.dark;
    if (o.motion !== undefined) motionChk.checked = o.motion;
    apply();
  },
  action: (a: 'dip' | 'lintel' | 'left' | 'right') => scene?.hyssopAction(a),
  rects: () => scene?.interactiveRects().map((r) => [r.x, r.y, r.width, r.height]),
  cam: (v: number[] | null) => (canvas as unknown as { __jfCam?: (v: number[] | null) => void }).__jfCam?.(v),
  info: () => (canvas as unknown as { __jfInfo?: () => unknown }).__jfInfo?.(),
  story,
};


