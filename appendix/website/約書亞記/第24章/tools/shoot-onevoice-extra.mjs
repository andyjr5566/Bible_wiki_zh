import { siteUrl } from './site-server.mjs';
// 補充驗收：無 WebGL 備援（對話改放經文框位置）、直式手機、直達網址。
import { mkdirSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { launch, sleep } from './cdp.mjs';

const out = resolve('.tmp-shots/onevoice');
mkdirSync(out, { recursive: true });
const failures = [];
const checks = [];
const fail = (m) => { failures.push(m); console.log('FAIL', m); };
const ka = setInterval(() => {}, 1000);

async function session(opts, fn) {
  const c = await launch(opts);
  try {
    if (opts.noWebgl) {
      await c.send('Page.addScriptToEvaluateOnNewDocument', {
        source: `const _gc = HTMLCanvasElement.prototype.getContext; HTMLCanvasElement.prototype.getContext = function (t, ...a) { if (/webgl/i.test(t)) return null; return _gc.call(this, t, ...a); };`,
      });
    }
    await c.send('Page.navigate', { url: siteUrl + (opts.hash ?? '') });
    for (let i = 0; i < 60; i++) {
      if (await c.evaluate('!!window.__josState && document.querySelectorAll("[data-cue]").length>30')) break;
      await sleep(500);
    }
    await sleep(1200);
    await fn(c);
  } finally {
    await c.close();
  }
}

const goto = (c) => async (cue, p) => {
  await c.evaluate(`(() => { const el = document.querySelector('section[data-cue="${cue}"]'); const H = innerHeight; const r = el.getBoundingClientRect(); window.scrollTo({ top: scrollY + r.top - (H * 0.36 - ${p} * (r.height - H * 0.35)), behavior: 'instant' }); })()`);
  await sleep(900);
};

try {
for (const dev of [
  { name: 'desktop', width: 1440, height: 900, dpr: 1, mobile: false, port: 9421 },
  { name: 'mobile', width: 844, height: 390, dpr: 2, mobile: true, port: 9422 },
]) {
  await session({ ...dev, noWebgl: true }, async (c) => {
    const g = goto(c);
    for (const [cue, p, tag] of [['family-5', 0.25, 'family-question'], ['family-5', 0.75, 'family'], ['the-stone', 0.3, 'verse'], ['the-stone', 0.9, 'note']]) {
      await g(cue, p);
      const m = await c.evaluate(`(() => { const b = document.querySelector('.jos-panel-on .jos-bubble'); const r = b && b.getBoundingClientRect(); return { sw: document.documentElement.scrollWidth, iw: innerWidth, bubble: b ? { docked: b.classList.contains('jos-bubble-docked'), text: b.textContent, x0: r.left, y0: r.top, x1: r.right, y1: r.bottom } : null, fallbackOn: document.querySelector('.jos-webgl-fallback-on') !== null }; })()`);
      if (m.sw > m.iw) fail(`noWebgl ${dev.name} ${cue}: 水平溢出`);
      if (!m.fallbackOn) fail(`noWebgl ${dev.name}: 備援插圖沒開`);
      if (cue === 'family-5') {
        if (!m.bubble?.docked) fail(`noWebgl ${dev.name}: 對話沒有改放經文框位置`);
        const expected = p < 0.5 ? '這塊石頭是什麼意思' : '看哪';
        if (!m.bubble?.text.includes(expected)) fail(`noWebgl ${dev.name}: 沒有隨捲動換句：${m.bubble?.text}`);
        const count = await c.evaluate("document.querySelectorAll('.jos-panel-on .jos-bubble-line').length");
        if (count !== 1) fail(`noWebgl ${dev.name}: 對話沒有一次一句`);
      }
      checks.push({ device: dev.name, noWebgl: true, cue, p, ...m });
      await c.shot(resolve(out, `nowebgl-${dev.name}-${cue}-${tag}.png`));
      console.log('shot', `nowebgl-${dev.name}-${cue}-${tag}.png`, JSON.stringify(m.bubble));
    }
  });
}

// 直式手機
await session({ width: 390, height: 844, dpr: 2, mobile: true, port: 9423 }, async (c) => {
  const g = goto(c);
  for (const [cue, p, tag] of [['prologue', 0.2, 'a'], ['my-house', 0.3, 'verse'], ['family-4', 0.25, 'bubble'], ['egypt', 0.5, 'map'], ['the-stone', 0.9, 'note']]) {
    await g(cue, p);
    const m = await c.evaluate('({ sw: document.documentElement.scrollWidth, iw: innerWidth })');
    checks.push({ portrait: true, cue, ...m });
    if (m.sw > m.iw) fail(`portrait ${cue}: 水平溢出 ${m.sw}>${m.iw}`);
    await c.shot(resolve(out, `portrait-${cue}-${tag}.png`));
  }
  // 直式：開更多小卡
  await g('beyond-river', 0.3);
  const b = await c.evaluate(`(() => { const r = document.querySelector('.jos-panel-on .jos-more-btn').getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; })()`);
  await c.click(b.x, b.y);
  await sleep(400);
  const k = await c.evaluate(`(() => { const r = document.querySelector('.jos-more-card').getBoundingClientRect(); return { x0: r.left, y0: r.top, x1: r.right, y1: r.bottom, sw: document.documentElement.scrollWidth }; })()`);
  if (k.x0 < 0 || k.x1 > 391 || k.y1 > 845 || k.sw > 390) fail('portrait: 更多小卡超出視窗 ' + JSON.stringify(k));
  await c.shot(resolve(out, 'portrait-beyond-river-more.png'));
});

// 直達網址
await session({ width: 1440, height: 900, dpr: 1, mobile: false, port: 9424, hash: '#beat=beat-27-the-stone' }, async (c) => {
  await sleep(1800);
  const m = await c.evaluate('({ cue: window.__josState.cue, y: scrollY })');
  if (m.cue !== 'the-stone') fail('#beat= 直達網址沒有停在 the-stone：' + m.cue);
  console.log('deep link', JSON.stringify(m));
});
// 不自動捲頁：每 80 ms 取樣 scrollY 9 秒，期間打開更多、開關、關閉、點經文小卡，數值要一直不變
for (const dev of [
  { name: 'desktop', width: 1440, height: 900, dpr: 1, mobile: false, port: 9426 },
  { name: 'mobile', width: 844, height: 390, dpr: 2, mobile: true, port: 9427 },
]) {
  await session(dev, async (c) => {
    const g = goto(c);
    await g('beyond-river', 0.3);
    await c.evaluate('window.__ys = []; window.__ysStart = performance.now(); window.__yt = setInterval(() => window.__ys.push(scrollY), 80); true');
    const pt = async (sel) => c.evaluate(`(() => { const r = document.querySelector(${JSON.stringify(sel)}).getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; })()`);
    let p = await pt('.jos-panel-on .jos-more-btn');
    await c.click(p.x, p.y); await sleep(700);
    p = await pt('.jos-more-card [data-coach="only-i-btn"]');
    await c.click(p.x, p.y); await sleep(700);
    p = await pt('.jos-more-card .jos-chip');
    await c.click(p.x, p.y); await sleep(900); // 地名小卡
    await c.send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 });
    await c.send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 });
    await sleep(700);
    await c.send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 });
    await c.send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 });
    const remaining = await c.evaluate('Math.max(0, 9100 - (performance.now() - window.__ysStart))');
    await sleep(remaining);
    const ys = await c.evaluate('clearInterval(window.__yt); window.__ys');
    const uniq = [...new Set(ys)];
    checks.push({ device: dev.name, scrollSamples: ys, scrollRange: Math.max(...ys) - Math.min(...ys) });
    console.log('scrollY samples', dev.name, ys.length, JSON.stringify(uniq));
    if (uniq.length !== 1) fail(`${dev.name}: 互動期間 scrollY 變動 ${JSON.stringify(uniq)}`);
    const st = await c.evaluate('({ more: window.__josState.moreOpen })');
    if (st.more) fail(`${dev.name}: Esc 之後更多小卡仍開著`);
  });
}
} finally {
  clearInterval(ka);
  writeFileSync(resolve(out, 'report-extra.json'), JSON.stringify({ created: new Date().toISOString(), checks, failures }, null, 2));
}
console.log('failures:', failures.length);
process.exit(failures.length ? 1 : 0);
