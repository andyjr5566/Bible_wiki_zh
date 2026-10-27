// 手機畫面總檢：每一拍取 3 個進度截圖（橫擺 844×390、直拿 390×844），給視覺審查用。
import { mkdirSync, writeFileSync } from 'node:fs';
import { launch, sleep } from './cdp.mjs';
import { siteUrl } from './site-server.mjs';
const OUT = process.argv[2];
const sizes = [['landscape', 844, 390], ['portrait', 390, 844]].filter(([n]) => !process.env.SIZES || process.env.SIZES.split(',').includes(n));
const fracs = process.env.FRACS ? process.env.FRACS.split(',').map(Number) : [0.15, 0.5, 0.85];
const only = process.env.BEATS ? process.env.BEATS.split(',') : null;
for (const [name, W, H] of sizes) {
  mkdirSync(`${OUT}/${name}`, { recursive: true });
  const c = await launch({ width: W, height: H, mobile: true, dpr: 2, port: name === 'landscape' ? 9494 : 9495 });
  const ka = setInterval(() => {}, 1000);
  try {
    await c.send('Page.navigate', { url: siteUrl });
    for (let i = 0; i < 60; i++) { if (await c.evaluate('!!window.__josState')) break; await sleep(500); }
    await sleep(3000);
    const ids = await c.evaluate(`[...document.querySelectorAll('section[data-beat-id]')].map(e=>e.dataset.beatId)`);
    const rows = [];
    for (const id of ids.filter(x => !only || only.some(o => x.includes(o)))) for (const f of fracs) {
      await c.evaluate(`(()=>{const e=document.querySelector('section[data-beat-id="${id}"]');const r=e.getBoundingClientRect();scrollTo({top:scrollY+r.top-innerHeight*.36+${f}*r.height,behavior:'instant'})})()`);
      await sleep(Number(process.env.WAIT ?? 1600));
      const file = `${id}-${String(Math.round(f * 100)).padStart(2, '0')}.png`;
      await c.shot(`${OUT}/${name}/${file}`);
      const sw = await c.evaluate('document.documentElement.scrollWidth');
      rows.push({ id, f, file, scrollWidth: sw, width: W });
    }
    // 整理區開頭兩屏
    for (const [k, off] of [[1, 0], [2, 1]]) {
      await c.evaluate(`(()=>{const r=document.getElementById('jos-review-root');scrollTo({top:scrollY+r.getBoundingClientRect().top+${off}*innerHeight,behavior:'instant'})})()`);
      await sleep(1200);
      await c.shot(`${OUT}/${name}/review-${k}.png`);
    }
    writeFileSync(`${OUT}/${name}/index.json`, JSON.stringify(rows, null, 1));
    console.log(name, rows.length, 'shots; overflow', rows.filter(r => r.scrollWidth > r.width).length);
  } finally { clearInterval(ka); await c.close(); }
}
