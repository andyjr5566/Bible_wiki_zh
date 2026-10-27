// 字到底有沒有在晃：觸控甩動時，每幀記錄「同一個字」（經文第一個可見字、泡泡第一個字）的螢幕位置，
// 統計位置來回反覆的次數與幅度。CPU 降速模擬手機。
import { launch, sleep } from './cdp.mjs';
import { siteUrl } from './site-server.mjs';
const W = 844, H = 390;
const c = await launch({ width: W, height: H, mobile: true, dpr: 3, port: 9502 });
const ka = setInterval(() => {}, 1000);
const startBeat = process.argv[2] ?? 'beat-13-now';
try {
  await c.send('Page.navigate', { url: siteUrl });
  for (let i = 0; i < 60; i++) { if (await c.evaluate('!!window.__josState && !document.getElementById("jos-loading")')) break; await sleep(500); }
  await c.evaluate(`(()=>{const e=document.querySelector('section[data-beat-id="${startBeat}"]');scrollTo({top:scrollY+e.getBoundingClientRect().top,behavior:'instant'})})()`);
  await sleep(4000);
  await c.send('Emulation.setCPUThrottlingRate', { rate: Number(process.env.CPU ?? 4) });
  await c.evaluate(`window.__rec=[];window.__on=true;(function f(){if(!window.__on)return;
    const pick=sel=>{const e=[...document.querySelectorAll(sel)].find(x=>{const r=x.getBoundingClientRect();return r.width>0&&getComputedStyle(x).opacity>0.5&&getComputedStyle(x).visibility!=='hidden'});if(!e)return null;if(!e.__id)e.__id=Math.random().toString(36).slice(2,7);const r=e.getBoundingClientRect();return [e.__id,+r.left.toFixed(2),+r.top.toFixed(2)]};
    window.__rec.push({y:scrollY,beat:window.__josState.beat,verse:pick('.jos-panel-on .jos-vbox-verse .jos-story-char'),bubble:pick('.jos-panel-on .jos-bubble .jos-bubble-line'),box:pick('.jos-panel-on .jos-vbox-verse')});requestAnimationFrame(f)})()`);
  for (let k = 0; k < Number(process.env.FLINGS ?? 16); k++) {
    await c.send('Input.synthesizeScrollGesture', { x: W / 2, y: H * 0.7, yDistance: -260, speed: 700, repeatCount: 1 });
    await sleep(500);
  }
  await c.evaluate('window.__on=false');
  const rec = await c.evaluate('window.__rec');
  for (const key of ['verse', 'bubble', 'box']) {
    let frames = 0, moves = 0, rev = 0, maxMove = 0;
    const samples = [];
    for (let i = 2; i < rec.length; i++) {
      const a = rec[i - 2][key], b = rec[i - 1][key], d = rec[i][key];
      if (!a || !b || !d || a[0] !== b[0] || b[0] !== d[0]) continue;
      frames++;
      for (const dim of [1, 2]) {
        const m1 = b[dim] - a[dim], m2 = d[dim] - b[dim];
        if (Math.abs(m2) > 0.1) { moves++; maxMove = Math.max(maxMove, Math.abs(m2)); }
        if (m1 * m2 < 0 && Math.abs(m1) > 0.1 && Math.abs(m2) > 0.1) { rev++; if (samples.length < 6) samples.push(`${rec[i].beat.slice(5)} ${dim === 1 ? 'x' : 'y'} ${m1.toFixed(1)}→${m2.toFixed(1)}`); }
      }
    }
    console.log(`${key.padEnd(6)} 同一個字被追蹤 ${frames} 幀；有移動 ${moves} 次（最大 ${maxMove.toFixed(1)}px）；來回反覆 ${rev} 次 ${samples.join(' | ')}`);
  }
  console.log('scroll', rec[0].y, '→', rec.at(-1).y, 'frames', rec.length);
} finally { clearInterval(ka); await c.close(); }
