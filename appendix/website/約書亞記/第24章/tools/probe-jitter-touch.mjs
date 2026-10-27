// 手機橫擺觸控甩動時逐幀記錄各層位置與捲動進度，找出來回晃動（方向反覆）的東西。
import { launch, sleep } from './cdp.mjs';
import { siteUrl } from './site-server.mjs';
const W = Number(process.argv[2] ?? 844), H = Number(process.argv[3] ?? 390);
const c = await launch({ width: W, height: H, mobile: true, dpr: 2, port: 9493 });
const ka = setInterval(() => {}, 1000);
try {
  await c.send('Page.navigate', { url: siteUrl });
  for (let i = 0; i < 60; i++) { if (await c.evaluate('!!window.__josState')) break; await sleep(500); }
  await sleep(2500);
  await c.evaluate(`window.__rec=[];window.__on=true;(function f(){if(!window.__on)return;
    const pick=(sel,all)=>{const out=[];document.querySelectorAll(sel).forEach((e,i)=>{const cs=getComputedStyle(e);if(cs.visibility==='hidden'||cs.display==='none'||+cs.opacity<.05)return;const r=e.getBoundingClientRect();if(!r.width)return;out.push([sel.slice(0,22)+'#'+i,+r.left.toFixed(2),+r.top.toFixed(2),+r.width.toFixed(1),+r.height.toFixed(1)])});return out};
    const els=[...pick('.jos-panel-on .jos-vbox'),...pick('.jos-panel-on .jos-bubble'),...pick('.jos-station-layer'),...pick('.jos-serve-thread'),...pick('.jos-header'),...pick('.jos-panel-on .jos-more-btn'),...pick('.jos-canvas'),...pick('.jos-stage-tag')];
    window.__rec.push({t:performance.now(),y:scrollY,ih:innerHeight,beat:window.__josState.beat,p:window.__josState.beatProgress,els});requestAnimationFrame(f)})()`);
  const starts = Number(process.argv[4] ?? 12);
  for (let k = 0; k < starts; k++) {
    await c.send('Input.synthesizeScrollGesture', { x: W / 2, y: H * 0.7, yDistance: -900, speed: 2400, gestureSourceType: process.env.SRC ?? 'default', repeatCount: 1 });
    await sleep(900);
  }
  await c.evaluate('window.__on=false');
  const rec = await c.evaluate('window.__rec');
  // 進度倒退（捲動往下時）
  let pBack = 0, yBack = 0;
  for (let i = 1; i < rec.length; i++) {
    if (rec[i].y < rec[i - 1].y - 0.5) yBack++;
    if (rec[i].beat === rec[i - 1].beat && rec[i].p < rec[i - 1].p - 1e-4 && rec[i].y >= rec[i - 1].y) pBack++;
  }
  const by = new Map();
  for (const r of rec) for (const e of r.els) { if (!by.has(e[0])) by.set(e[0], []); by.get(e[0]).push({ beat: r.beat, v: e.slice(1) }); }
  const report = [];
  for (const [k, arr] of by) for (const dim of [0, 1, 2, 3]) {
    let rev = 0, max = 0, moves = 0;
    for (let i = 2; i < arr.length; i++) {
      if (arr[i].beat !== arr[i - 1].beat || arr[i - 1].beat !== arr[i - 2].beat) continue;
      const a = arr[i - 1].v[dim] - arr[i - 2].v[dim], b = arr[i].v[dim] - arr[i - 1].v[dim];
      if (Math.abs(b) > 0.3) moves++;
      if (a * b < 0 && Math.abs(a) > 0.3 && Math.abs(b) > 0.3) { rev++; max = Math.max(max, Math.abs(a), Math.abs(b)); }
    }
    if (rev > 2) report.push({ el: k, dim: ['left', 'top', 'w', 'h'][dim], frames: arr.length, moves, reversals: rev, maxJump: +max.toFixed(1) });
  }
  report.sort((a, b) => b.reversals - a.reversals);
  console.log(`frames ${rec.length}  scrollY ${rec[0].y}→${rec.at(-1).y}  innerHeight 變化 ${new Set(rec.map(r => r.ih)).size} 種  捲動倒退 ${yBack}  同拍進度倒退 ${pBack}`);
  console.log(JSON.stringify(report.slice(0, 20), null, 1));
} finally { clearInterval(ka); await c.close(); }
