import { mkdirSync, writeFileSync, readFileSync, readdirSync, statSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { gzipSync } from 'node:zlib';
import { launch, sleep } from './cdp.mjs';
import { siteUrl, serveDist } from './site-server.mjs';
import { stationRhythm } from '../src/data/story-content.mjs';

const out = resolve('.tmp-shots/loading'); mkdirSync(out, { recursive: true });
const keepAlive = setInterval(() => {}, 1000);
const c = await launch({ port: 9483, gpu: true });
const requests = new Map(), failures = [];
const report = { url: siteUrl, baseline: { htmlBytes: 14291405, gzipBytes: 9963964 }, failures };
const site = JSON.parse(readFileSync('src/data/site.json', 'utf8'));
let deploy;
try { deploy = JSON.parse(readFileSync('.tmp-shots/loading/deploy.json', 'utf8')); } catch {}
const stations = JSON.parse(readFileSync('src/data/stations.json', 'utf8'));
const beats = site.segments.flatMap(s => s.beats);
let lastRequest = Date.now();
c.onEvent(message => {
  const p = message.params;
  if (message.method === 'Network.responseReceived') {
    const r = p.response;
    requests.set(p.requestId, { url: r.url, status: r.status, mime: r.mimeType, cached: r.fromDiskCache || r.fromServiceWorker, bytes: 0 });
    if (r.status >= 400) failures.push(`${r.status}: ${r.url}`);
    lastRequest = Date.now();
  }
  if (message.method === 'Network.loadingFinished') {
    const item = requests.get(p.requestId);
    if (item) item.bytes = p.encodedDataLength;
    lastRequest = Date.now();
  }
  if (message.method === 'Network.loadingFailed' && !p.canceled) failures.push(p.errorText);
});
async function idle() {
  for (let i = 0; i < 100; i++) {
    await sleep(100);
    if (Date.now() - lastRequest > 1300) break;
  }
}
async function ready() {
  for (let i = 0; i < 150; i++) {
    if (await c.evaluate('!!window.__josState && !!document.querySelector("[data-beat-id]")')) return;
    await sleep(100);
  }
  throw new Error('Story did not mount');
}
async function goto(id, p) {
  await c.evaluate(`(()=>{const e=document.getElementById('jos-beat-${id}');scrollTo({top:scrollY+e.getBoundingClientRect().top-innerHeight*.36+${p}*e.offsetHeight,behavior:'instant'})})()`);
  await sleep(650);
  await idle();
}
function snapshot() {
  const resources = [...requests.values()].filter(r => !r.url.endsWith('/favicon.ico'));
  return { transferBytes: resources.reduce((n, r) => n + r.bytes, 0), requests: resources.length, resources };
}
try {
  await c.send('Network.enable');
  await c.send('Network.clearBrowserCache');
  await c.send('Page.navigate', { url: siteUrl });
  await ready(); await c.evaluate('document.fonts.ready.then(()=>true)'); await idle();
  report.first = snapshot();
  if (report.first.transferBytes > 3_000_000) failures.push('First screen exceeds 3 MB gzip budget');
  const deferred = /\/(?:morning|afternoon|dusk|night|oak-night|wide-relief|review-|beyond-river|river-|crowd-|sea-|stone-thud|desert-wind|valley-wind|oak-leaves)/;
  report.unexpectedFirst = report.first.resources.filter(r => deferred.test(new URL(r.url).pathname));
  if (report.unexpectedFirst.length) failures.push('Deferred assets loaded on first screen');
  await c.shot(join(out, 'first.png'));
  for (const beat of beats) {
    for (const station of stations.filter(s => s.beat === beat.id)) {
      const list = stations.filter(s => s.beat === beat.id), span = s => 800 + stationRhythm(s, site).px;
      const p = (list.slice(0, list.indexOf(station)).reduce((n, s) => n + span(s), 0) + 800 + stationRhythm(station, site).px * .5) / list.reduce((n, s) => n + span(s), 0);
      await goto(beat.id, p);
      const ready = await c.evaluate(`document.querySelector('[data-station-id="${station.id}"]')?.dataset.ready === 'true'`);
      if (!ready) failures.push(`Station not decoded: ${station.id}`);
    }
    await goto(beat.id, .5);
  }
  await c.evaluate('document.getElementById("jos-review-root").scrollIntoView({behavior:"instant"})');
  await sleep(700); await idle();
  for (const id of await c.evaluate('[...document.querySelectorAll(".jos-sec")].map(e=>e.id)')) {
    await c.evaluate(`document.getElementById(${JSON.stringify(id)}).scrollIntoView({behavior:'instant'})`);
    await sleep(700); await idle();
  }
  await c.evaluate('scrollTo({top:document.documentElement.scrollHeight,behavior:"instant"})');
  await sleep(700); await idle();
  report.completeSilent = snapshot();
  if (report.completeSilent.resources.some(r => /audio\/|\.mp3/.test(r.url))) failures.push('Sound downloaded before the first interaction');
  // 聲音預設開，但瀏覽器要讀者先操作頁面才准出聲：用真滑鼠點一下空白處，驗證這之後才發出音檔請求。
  if (!await c.evaluate('window.__josState.soundOn')) failures.push('Sound should default to on');
  for (const type of ['mousePressed', 'mouseReleased']) await c.send('Input.dispatchMouseEvent', { type, x: 700, y: 450, button: 'left', clickCount: 1 });
  await sleep(1500); await idle();
  report.completeWithSound = snapshot();
  if (!report.completeWithSound.resources.some(r => /\.mp3/.test(r.url))) failures.push('First interaction did not start audio');
  report.errors = c.consoleLog.filter(s => /^\[(error|exception)\]/.test(s));
  failures.push(...report.errors);
  const files = readdirSync('dist/assets').map(name => ({ name, bytes: statSync(join('dist/assets', name)).size }));
  report.build = { htmlBytes: statSync('dist/index.html').size, htmlGzip: gzipSync(readFileSync('dist/index.html')).length, files: files.length + 1, totalBytes: files.reduce((n, f) => n + f.bytes, statSync('dist/index.html').size) };
  // 額外入口用同一套 HTTP/CDP 檢查，包含子目錄與 vault 外建置。
  report.openings = [];
  for (const [kind, root, suffix] of [
    ['preview', null, 'http://127.0.0.1:4224/'],
    ['deploy', process.env.JOS_DEPLOY_ROOT || deploy?.deployRoot, process.env.JOS_DEPLOY_PATH || deploy?.deployPath || ''],
    ['ci', process.env.JOS_CI_ROOT || deploy?.ciRoot, ''],
  ]) {
    if (kind !== 'preview' && !root) continue;
    const server = root ? await serveDist(root) : null;
    const url = server ? server.url + suffix : suffix;
    const previousErrors = c.consoleLog.length;
    await c.send('Page.navigate', { url }); await ready(); await idle();
    await goto(beats[14].id, .5);
    const ok = await c.evaluate(`window.__josState.beat === '${beats[14].id}' && !!window.__josScene`);
    const errors = c.consoleLog.slice(previousErrors).filter(s => /^\[(error|exception)\]/.test(s));
    report.openings.push({ kind, url, ok, errors });
    if (!ok || errors.length) failures.push(`Opening failed: ${kind}`);
    server?.server.close();
  }
} finally {
  writeFileSync(join(out, 'report.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify({ first: report.first?.transferBytes, silent: report.completeSilent?.transferBytes, sound: report.completeWithSound?.transferBytes, build: report.build, openings: report.openings, failures }));
  await c.close(); clearInterval(keepAlive);
}
if (failures.length) process.exitCode = 1;
