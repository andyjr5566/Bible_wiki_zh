// 開發用的場景實驗室：全螢幕 canvas＋浮動控制列。只在 dev server 使用（scene-lab.html），不進正式建置。
// 網址參數：?cue=midnight&p=0.5&day=14&dark=1&motion=1&ui=0&panel=1&boxes=1&side=left&count=30&bake=0.5
import { SITE } from '../data/site';
import type { Palette } from '../data/types';
import { story } from '../story/state';
import type { SceneEvent, SceneHandle } from './api';
import { createScene } from './index';
import { CUES } from './tracks';

const palettes: Record<string, Palette> = {};
const chapterOf: Record<string, string> = {};
const dayOf: Record<string, number> = {};
for (const ch of SITE.chapters) {
  palettes[ch.id] = ch.palette;
  for (const b of ch.beats) {
    chapterOf[b.cue] = ch.id;
    if (b.day !== undefined) dayOf[b.cue] = b.day;
  }
}

const $ = <T extends HTMLElement>(id: string): T => document.getElementById(id) as T;
const canvas = $<HTMLCanvasElement>('c');
const logEl = $<HTMLPreElement>('lab-log');
const cueSel = $<HTMLSelectElement>('lab-cue');
const chapSel = $<HTMLSelectElement>('lab-chapter');
const pRange = $<HTMLInputElement>('lab-p');
const dRange = $<HTMLInputElement>('lab-day');
const cRange = $<HTMLInputElement>('lab-count');
const bRange = $<HTMLInputElement>('lab-bake');
const darkChk = $<HTMLInputElement>('lab-dark');
const motionChk = $<HTMLInputElement>('lab-motion');
const panel = $<HTMLDivElement>('lab-panel');

for (const id of Object.keys(palettes)) {
  const o = document.createElement('option');
  o.value = id;
  o.textContent = id;
  chapSel.appendChild(o);
}
for (const cu of CUES) {
  const o = document.createElement('option');
  o.value = cu;
  o.textContent = cu;
  cueSel.appendChild(o);
}

const q = new URLSearchParams(location.search);
let forcePanel = q.get('panel') === '1';
if (q.get('ui') === '0') document.body.classList.add('lab-hide');
if (q.get('boxes') === '1') {
  document.getElementById('lab-box')?.classList.add('on');
  document.getElementById('lab-top')?.classList.add('on');
  if (q.get('side') === 'left') document.getElementById('lab-box')?.classList.add('left');
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
  const cue = cueSel.value;
  const idx = CUES.indexOf(cue as (typeof CUES)[number]);
  story.cue = cue;
  story.beat = cue;
  story.prevCue = CUES[Math.max(0, idx - 1)];
  story.chapter = chapterOf[cue] ?? 'opening';
  chapSel.value = story.chapter;
  story.beatProgress = Number(pRange.value);
  story.day = Number(dRange.value);
  story.count = Number(cRange.value);
  story.bake.progress = Number(bRange.value);
  story.bake.done = story.bake.progress >= 1;
  story.dark = darkChk.checked;
  story.motionOff = motionChk.checked;
  $('lab-pv').textContent = story.beatProgress.toFixed(2);
  $('lab-dv').textContent = story.day.toFixed(1);
  $('lab-cv').textContent = story.count.toFixed(1);
  panel.style.display = forcePanel || story.cue === 'meal' ? 'block' : 'none';
}

// 初始值（網址參數）
const cue0 = q.get('cue') ?? 'title';
cueSel.value = (CUES as readonly string[]).includes(cue0) ? cue0 : 'title';
pRange.value = q.get('p') ?? '0.5';
dRange.value = q.get('day') ?? String(dayOf[cueSel.value] ?? 14);
cRange.value = q.get('count') ?? (cueSel.value === 'count' ? '25' : cueSel.value === 'title' ? '0' : '50');
bRange.value = q.get('bake') ?? '0';
darkChk.checked = q.get('dark') === '1';
motionChk.checked = q.get('motion') === '1';
apply();
for (const el of [cueSel, pRange, dRange, cRange, bRange, darkChk, motionChk]) el.addEventListener('input', apply);
cueSel.addEventListener('change', () => {
  if (dayOf[cueSel.value] !== undefined) dRange.value = String(dayOf[cueSel.value]);
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
$('lab-wave').addEventListener('click', () => scene?.waveAction());
const resetWave = () => {
  story.wave.swings = 0;
  story.wave.done = false;
  story.wave.auto = false;
};
$('lab-wave-reset').addEventListener('click', resetWave);

// 供截圖腳本呼叫
(window as unknown as Record<string, unknown>).__lab = {
  set(o: { cue?: string; p?: number; day?: number; dark?: boolean; motion?: boolean; count?: number; bake?: number }) {
    if (o.cue !== undefined) cueSel.value = o.cue;
    if (o.p !== undefined) pRange.value = String(o.p);
    if (o.day !== undefined) dRange.value = String(o.day);
    if (o.count !== undefined) cRange.value = String(o.count);
    if (o.bake !== undefined) bRange.value = String(o.bake);
    if (o.dark !== undefined) darkChk.checked = o.dark;
    if (o.motion !== undefined) motionChk.checked = o.motion;
    apply();
  },
  action: (a: 'dip' | 'lintel' | 'left' | 'right') => scene?.hyssopAction(a),
  wave: () => scene?.waveAction(),
  resetWave,
  rects: () => scene?.interactiveRects().map((r) => [r.x, r.y, r.width, r.height]),
  cam: (v: number[] | null) => (canvas as unknown as { __jfCam?: (v: number[] | null) => void }).__jfCam?.(v),
  info: () => (canvas as unknown as { __jfInfo?: () => unknown }).__jfInfo?.(),
  story,
};
