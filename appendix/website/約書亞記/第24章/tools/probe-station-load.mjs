// 慢速網路下：讀到第5拍時背景預先下載站圖的進度，以及到站時多久有畫面。
import { launch, sleep } from './cdp.mjs';
import { siteUrl } from './site-server.mjs';
const c = await launch({ width: 844, height: 390, mobile: true, dpr: 2, port: 9500 });
const ka = setInterval(() => {}, 1000);
const go = (id, f) => c.evaluate(`(()=>{const e=document.querySelector('section[data-beat-id="${id}"]');const r=e.getBoundingClientRect();scrollTo({top:scrollY+r.top-innerHeight*.36+${f}*r.height,behavior:'instant'})})()`);
try {
  await c.send('Network.enable');
  await c.send('Network.emulateNetworkConditions', { offline: false, latency: 80, downloadThroughput: 4e6 / 8, uploadThroughput: 1e6 / 8 });
  await c.send('Page.navigate', { url: siteUrl });
  for (let i = 0; i < 120; i++) { if (await c.evaluate('!!window.__josState')) break; await sleep(500); }
  await sleep(2000);
  const count = () => c.evaluate(`performance.getEntriesByType('resource').filter(e=>e.initiatorType==='fetch'&&e.name.endsWith('.webp')&&e.responseEnd>0).length`);
  await go('beat-05-family-1', .5);
  for (const t of [5, 10, 20, 30]) { await sleep(t === 5 ? 5000 : (t === 10 ? 5000 : 10000)); console.log(`停在第5拍 ${t}s：已下載站圖 ${await count()} 張`); }
  await go('beat-07-abraham', .9);
  for (let i = 0; i < 12; i++) {
    await sleep(250);
    const r = await c.evaluate(`(()=>{const n=document.querySelector('.jos-station-composition[data-station-id="esau-jacob"]');return n?n.dataset.ready:'未掛上'})()`);
    if (r === 'true') { console.log(`到以掃雅各站後 ${(i + 1) * 0.25}s 有畫面`); break; }
    if (i === 11) console.log('3 秒內仍沒有畫面：', r);
  }
} finally { clearInterval(ka); await c.close(); }
