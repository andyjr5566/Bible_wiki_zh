// 慢速網路開啟網頁：每隔一段時間截圖並記錄載入畫面的百分比，直到它淡出移除。
import { mkdirSync } from 'node:fs';
import { launch, sleep } from './cdp.mjs';
process.env.JOS_KEEP_LOADER = '1';
import { siteUrl } from './site-server.mjs';
const OUT = process.argv[2] ?? '.tmp-shots/loading';
mkdirSync(OUT, { recursive: true });
const c = await launch({ width: 844, height: 390, mobile: true, dpr: 2, port: 9501 });
const ka = setInterval(() => {}, 1000);
try {
  await c.send('Network.enable');
  await c.send('Network.emulateNetworkConditions', { offline: false, latency: 80, downloadThroughput: 4e6 / 8, uploadThroughput: 1e6 / 8 });
  const t0 = Date.now();
  await c.send('Page.navigate', { url: siteUrl });
  const log = [];
  for (let i = 0; i < 40; i++) {
    await sleep(500);
    const s = await c.evaluate(`(()=>{const e=document.getElementById('jos-loading');return e?{pct:e.getAttribute('aria-valuenow'),label:e.querySelector('.jos-loading-label')?.textContent,done:e.classList.contains('jos-loading-done')}:{removed:true}})()`).catch(() => ({ err: 1 }));
    const sec = ((Date.now() - t0) / 1000).toFixed(1);
    log.push(`${sec}s ${JSON.stringify(s)}`);
    if ([1, 3, 6, 10].includes(i)) await c.shot(`${OUT}/t${String(i).padStart(2, '0')}.png`).catch(() => {});
    if (s && s.removed) break;
  }
  console.log(log.join('\n'));
} finally { clearInterval(ka); await c.close(); }
