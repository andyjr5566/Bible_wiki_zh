// 手機橫擺、CPU 降速下甩動捲動，量重排與樣式重算次數、每幀間隔（比較兩份建置用）。
import { launch, sleep } from './cdp.mjs';
import { fileURLToPath } from 'node:url';
import { serveDist } from './site-server.mjs';
const root = process.argv[2] ?? 'dist';
const { url } = await serveDist(fileURLToPath(new URL(`../${root}/`, import.meta.url)));
const c = await launch({ width: 844, height: 390, mobile: true, dpr: 2, port: 9496 });
const ka = setInterval(() => {}, 1000);
try {
  await c.send('Page.navigate', { url });
  for (let i = 0; i < 60; i++) { if (await c.evaluate('!!window.__josState')) break; await sleep(500); }
  await sleep(2500);
  // 從第三幕開始（示劍 3D＋藝術字經文）
  await c.evaluate(`(()=>{const e=document.querySelector('section[data-beat-id="beat-13-now"]');scrollTo({top:scrollY+e.getBoundingClientRect().top,behavior:'instant'})})()`);
  await sleep(1500);
  await c.send('Performance.enable');
  await c.send('Emulation.setCPUThrottlingRate', { rate: 4 });
  const m0 = Object.fromEntries((await c.send('Performance.getMetrics')).metrics.map(m => [m.name, m.value]));
  await c.evaluate(`window.__ft=[];window.__on=true;let l=performance.now();(function f(n){if(!window.__on)return;window.__ft.push(n-l);l=n;requestAnimationFrame(f)})(performance.now())`);
  for (let k = 0; k < 10; k++) {
    await c.send('Input.synthesizeScrollGesture', { x: 422, y: 270, yDistance: -500, speed: 1200, repeatCount: 1 });
    await sleep(400);
  }
  await c.evaluate('window.__on=false');
  const m1 = Object.fromEntries((await c.send('Performance.getMetrics')).metrics.map(m => [m.name, m.value]));
  const ft = (await c.evaluate('window.__ft')).slice(2).sort((a, b) => a - b);
  const pct = q => ft[Math.floor(ft.length * q)].toFixed(1);
  const d = k => +(m1[k] - m0[k]).toFixed(3);
  console.log(JSON.stringify({ build: root, frames: ft.length, frameMs: { p50: pct(.5), p90: pct(.9), p99: pct(.99) }, layouts: d('LayoutCount'), layoutSec: d('LayoutDuration'), styleRecalcs: d('RecalcStyleCount'), styleSec: d('RecalcStyleDuration'), scriptSec: d('ScriptDuration') }));
} finally { clearInterval(ka); await c.close(); }
