// 自動播放時對話泡泡會不會來回跳：iPhone 橫擺尺寸，從指定的對話拍開始自動播放，每幀記錄泡泡的位置，
// 統計「這一格往上、下一格又往下」的來回次數（2026-10-28 使用者錄影：泡泡每格上下跳約 2px）。
import { launch, sleep } from './cdp.mjs';
import { siteUrl } from './site-server.mjs';
const W = Number(process.env.W ?? 852), H = Number(process.env.H ?? 393);
const beat = process.argv[2] ?? 'family-1';
const c = await launch({ width: W, height: H, mobile: true, dpr: 3, port: 9513 });
const ka = setInterval(() => {}, 1000);
try {
  await c.send('Page.navigate', { url: siteUrl });
  for (let i = 0; i < 60; i++) { if (await c.evaluate('!!window.__josState')) break; await sleep(500); }
  await sleep(2500);
  await c.evaluate(`(()=>{const e=document.querySelector('section[data-beat-id*="${beat}"]');scrollTo({top:scrollY+e.getBoundingClientRect().top+20,behavior:'instant'})})()`);
  await sleep(2500);
  await c.evaluate(`[...document.querySelectorAll('button')].find(b=>/自動播放/.test(b.textContent)).click()`);
  await c.evaluate(`window.__rec=[];window.__on=true;(function f(){if(!window.__on)return;
    const b=document.querySelector('.jos-panel-on .jos-bubble');
    const m=b&&/translate\\((-?[\\d.]+)px, (-?[\\d.]+)px\\)/.exec(b.style.transform);
    window.__rec.push(m?[+m[1],+m[2],+(b.dataset.headY??0),+(b.dataset.tailGap??0)]:null);requestAnimationFrame(f)})()`);
  await sleep(Number(process.env.MS ?? 5000));
  await c.evaluate('window.__on=false');
  const rec = (await c.evaluate('window.__rec')).filter(Boolean);
  let moves = 0, rev = 0; const samples = [];
  for (let i = 2; i < rec.length; i++) for (const d of [0, 1]) {
    const m1 = rec[i - 1][d] - rec[i - 2][d], m2 = rec[i][d] - rec[i - 1][d];
    if (m2) moves++;
    if (m1 * m2 < 0) { rev++; if (samples.length < 8) samples.push(`${d ? 'y' : 'x'} ${rec[i - 2][d]}→${rec[i - 1][d]}→${rec[i][d]} head ${rec[i][2].toFixed(1)}`); }
  }
  console.log(`泡泡 ${rec.length} 幀；移動 ${moves} 次；來回反覆 ${rev} 次`);
  console.log(samples.join('\n'));
  console.log('y 序列（前 60 幀）', rec.slice(0, 60).map(r => r[1]).join(' '));
} finally { clearInterval(ka); await c.close(); }
