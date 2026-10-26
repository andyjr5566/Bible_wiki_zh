import { readFileSync, mkdirSync, writeFileSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { launch, sleep } from './cdp.mjs';
import { siteUrl, serveDist } from './site-server.mjs';

const keepAlive = setInterval(() => {}, 1000);
const c = await launch({ port: 9483, gpu: true });
const out = resolve('.tmp-shots/loading'); mkdirSync(out, { recursive: true });
const report = { openings: [], delayed: [], failures: [] };
const deploy = JSON.parse(readFileSync(join(out, 'deploy.json'), 'utf8'));
const requested = [], badResponses = [];
c.onEvent(message => {
  if (message.method === 'Fetch.requestPaused') {
    void sleep(1800).then(() => c.send('Fetch.continueRequest', { requestId: message.params.requestId }));
  }
  if (message.method === 'Network.responseReceived') {
    requested.push(message.params.response.url);
    if (message.params.response.status >= 400) badResponses.push(message.params.response.url);
  }
});
async function wait(expression) {
  for (let i = 0; i < 160; i++) { if (await c.evaluate(expression)) return; await sleep(100); }
  throw new Error('Timed out: ' + expression);
}
async function scroll(id, p = .5) {
  await c.evaluate(`(()=>{const e=document.getElementById('jos-beat-${id}');scrollTo({top:scrollY+e.getBoundingClientRect().top-innerHeight*.36+${p}*e.offsetHeight,behavior:'instant'})})()`);
  await wait(`window.__josState.beat === '${id}'`);
}
try {
  await c.send('Network.enable');
  for (const [kind, root, suffix] of [['preview', null, 'http://127.0.0.1:4224/'], ['deploy', deploy.deployRoot, deploy.deployPath], ['ci', deploy.ciRoot, '']]) {
    const local = root ? await serveDist(root) : null;
    const url = local ? local.url + suffix : suffix;
    const start = c.consoleLog.length;
    await c.send('Page.navigate', { url });
    await wait('!!window.__josScene && document.querySelectorAll("[data-beat-id]").length === 36');
    await scroll('beat-06-beyond-river');
    await wait('document.querySelector("[data-station-id=beyond-river]")?.dataset.ready === "true"');
    await scroll('beat-15-my-house');
    await sleep(800);
    const errors = c.consoleLog.slice(start).filter(s => /^\[(error|exception)\]/.test(s));
    report.openings.push({ kind, url, ok: !errors.length, errors });
    if (errors.length) report.failures.push(kind + ': browser error');
    local?.server.close();
  }
  await c.send('Fetch.enable', { patterns: [{ urlPattern: '*beyond-river*.webp', requestStage: 'Request' }] });
  for (const [device, width, height] of [['desktop', 1440, 900], ['mobile', 844, 390]]) {
    await c.send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: device === 'mobile' });
    await c.send('Network.clearBrowserCache');
    await c.send('Page.navigate', { url: siteUrl });
    await wait('!!window.__josScene && document.querySelectorAll("[data-beat-id]").length === 36');
    await scroll('beat-06-beyond-river');
    await sleep(120);
    const pending = await c.evaluate(`(()=>{const n=document.querySelector('[data-station-id=beyond-river]');return {ready:n.dataset.ready,opacity:getComputedStyle(n.querySelector('.jos-station-artwork')).opacity,background:getComputedStyle(n).backgroundColor}})()`);
    if (pending.ready !== 'false' || +pending.opacity !== 0 || pending.background !== 'rgb(48, 42, 41)') report.failures.push(device + ': loading placeholder missing');
    await c.shot(join(out, device + '-pending.png'));
    await wait('document.querySelector("[data-station-id=beyond-river]")?.dataset.ready === "true"');
    await sleep(600);
    const loaded = await c.evaluate(`(()=>{const n=document.querySelector('[data-station-id=beyond-river]');return {ready:n.dataset.ready,opacity:getComputedStyle(n.querySelector('.jos-station-artwork')).opacity,broken:[...n.querySelectorAll('img')].filter(i=>!i.complete||!i.naturalWidth).length}})()`);
    if (+loaded.opacity !== 1 || loaded.broken !== 0) report.failures.push(device + ': decoded scene missing');
    await c.shot(join(out, device + '-ready.png'));
    report.delayed.push({ device, delayMs: 1800, pending, loaded });
    // 冷快取跳讀與倒讀皆直接補載當前站，不依賴上一站走過。
    await scroll('beat-08-egypt', .7);
    await sleep(800);
    await scroll('beat-06-beyond-river');
    await wait('document.querySelector("[data-station-id=beyond-river]")?.dataset.ready === "true"');
  }
  await c.send('Fetch.disable');
  report.silentAudioRequests = requested.filter(url => /\.mp3/.test(url)).length;
  if (report.silentAudioRequests) report.failures.push('Audio requested without opt-in');
  report.errors = c.consoleLog.filter(s => /^\[(error|exception)\]/.test(s));
  report.badResponses = badResponses;
  report.failures.push(...report.errors, ...badResponses);
  await c.send('Page.navigate', { url: pathToFileURL(resolve('dist/index.html')).href });
  await sleep(1500);
  report.fileUnsupported = !await c.evaluate('Boolean(window.__josState)');
} finally {
  writeFileSync(join(out, 'checks.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report));
  await c.close(); clearInterval(keepAlive);
}
if (report.failures.length) process.exitCode = 1;
