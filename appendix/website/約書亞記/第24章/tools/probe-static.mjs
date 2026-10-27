// 找停格：每捲 STEP px 截一張小圖（藏文字與頂列、關常駐動態），之後由 probe-static.py 比對相鄰兩張的差異。
import { mkdirSync, writeFileSync } from 'node:fs';
import { launch, sleep } from './cdp.mjs';
import { siteUrl } from './site-server.mjs';
const OUT = process.argv[2];
const STEP = Number(process.argv[3] ?? 200);
mkdirSync(OUT, { recursive: true });
const c = await launch({ width: 960, height: 600, dpr: 1, port: 9492 });
const ka = setInterval(() => {}, 1000);
try {
  await c.send('Page.navigate', { url: siteUrl });
  for (let i = 0; i < 60; i++) { if (await c.evaluate('!!window.__josState')) break; await sleep(500); }
  await sleep(2500);
  await c.evaluate(`(()=>{const s=document.createElement('style');s.textContent='.jos-onevoice,.jos-header,.jos-stage-tags,.jos-coach,.jos-serve-thread{visibility:hidden!important}';document.head.appendChild(s);window.__josState.motionOff=true;document.body.classList.add('jos-motion-off')})()`);
  const end = await c.evaluate(`(()=>{const r=document.getElementById('jos-review-root');return scrollY+r.getBoundingClientRect().top-innerHeight})()`);
  const rows = [];
  let i = 0;
  for (let y = 0; y <= end; y += STEP, i++) {
    await c.evaluate(`scrollTo({top:${y},behavior:'instant'})`);
    await sleep(420);
    const st = await c.evaluate(`({beat:window.__josState.beat,p:+window.__josState.beatProgress.toFixed(3)})`);
    const { data } = await c.send('Page.captureScreenshot', { format: 'png', clip: { x: 0, y: await c.evaluate('scrollY'), width: 960, height: 600, scale: 0.4 } });
    const file = `${String(i).padStart(4, '0')}.png`;
    writeFileSync(`${OUT}/${file}`, Buffer.from(data, 'base64'));
    rows.push({ i, y, file, ...st });
  }
  writeFileSync(`${OUT}/index.json`, JSON.stringify(rows));
  console.log('shots', rows.length, 'end', end);
} finally { clearInterval(ka); await c.close(); }
