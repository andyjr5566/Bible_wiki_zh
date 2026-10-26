import { mkdirSync, writeFileSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { launch, sleep } from './cdp.mjs';
import { siteUrl } from './site-server.mjs';

const [device = 'desktop', network = 'normal'] = process.argv.slice(2);
const mobile = device === 'mobile';
const out = resolve('.tmp-shots/regress');
mkdirSync(out, { recursive: true });
const report = { device, network, freshProfile: true, samples: [], failures: [] };
const c = await launch({ port: 9484, gpu: true, width: mobile ? 844 : 1440, height: mobile ? 390 : 900, mobile });
const assets = [];
c.onEvent(m => {
  if (m.method === 'Network.responseReceived' && /(?:atlas|oak-|dawn-|stone-texture)/.test(m.params.response.url)) assets.push({ url: m.params.response.url, status: m.params.response.status });
});
const sample = async label => {
  const sampledAt = Math.round(performance.now() - start);
  await c.shot(join(out, `${device}-${network}-${label}.png`));
  const pixels = await c.evaluate('window.__josScene?.openingPixels()');
  const state = await c.evaluate('({y:scrollY,beat:window.__josState?.beat,dark:window.__josState?.dark,ready:!!window.__josScene})');
  const pass = pixels?.joshua > 30 && pixels?.oak > 100 && pixels.textures.filter(t=>['joshua','oak'].includes(t.name)).every(t=>t.width>1);
  const result = { label, sampledAt, completedAt: Math.round(performance.now() - start), state, pixels, pass };
  report.samples.push(result);
  if (state.y !== 0) report.failures.push(`Not at top: ${label}`);
  return result;
};
let start;
try {
  await c.send('Network.enable');
  await c.send('Network.setCacheDisabled', { cacheDisabled: true });
  if (network === 'slow') await c.send('Network.emulateNetworkConditions', { offline: false, latency: 80, downloadThroughput: 1_500_000 / 8, uploadThroughput: 750_000 / 8, connectionType: 'cellular3g' });
  start = performance.now();
  await c.send('Page.navigate', { url: siteUrl });
  for (const ms of [1500, 3000, 6000]) {
    await sleep(Math.max(0, start + ms - performance.now()));
    const result = await sample(`${ms}ms`);
    if (network === 'normal' && !result.pass) report.failures.push(`Opening missing at ${ms}ms`);
  }
  if (network === 'slow') {
    let ready = false;
    for (let i = 0; i < 180; i++) {
      ready = await c.evaluate('window.__josScene?.openingPixels().textures.every(t=>t.width>1)');
      if (ready) break;
      await sleep(500);
    }
    await sleep(700); // allow the existing panorama arrival fade to finish
    if (!(await sample('downloaded')).pass || !ready) report.failures.push('Missing after slow download');
  }
  // Theme changes must not hide cards; keep the scroll position at the opening.
  await c.evaluate("[...document.querySelectorAll('.jos-header-tools button')].find(b=>b.textContent==='深色')?.click()");
  await sleep(100);
  if (!(await sample('dark')).pass) report.failures.push('Missing in dark theme');
  report.assets = assets;
  report.errors = c.consoleLog.filter(s => /^\[(error|exception)\]/.test(s));
  report.failures.push(...report.errors);
} finally {
  writeFileSync(join(out, `${device}-${network}.json`), JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report));
  await c.close();
}
if (report.failures.length) process.exitCode = 1;
