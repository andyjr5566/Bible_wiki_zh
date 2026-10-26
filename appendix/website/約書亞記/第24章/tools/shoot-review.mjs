import { siteUrl } from './site-server.mjs';
// Acceptance: local HTTP, owned jos-shoot-* Chrome profile, viewport captures and scroll samples.
// Run after npm run build: powershell -File tools/shoot-review.ps1
import assert from 'node:assert/strict';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import childProcess from 'node:child_process';
import { syncBuiltinESMExports } from 'node:module';
import { launch, sleep } from './cdp.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const out = resolve(process.argv[2] ?? resolve(root, '.tmp-shots/review'));
mkdirSync(out, { recursive: true });
const url = siteUrl;
const data = JSON.parse(readFileSync(resolve(root, 'src/data/site.json'), 'utf8'));
const sections = ['01', '02', '03', '04', '05', '06', '07', 'questions', 'about'];
const labelsOnly = process.argv[4] === 'labels';
const report = labelsOnly ? JSON.parse(readFileSync(resolve(out, 'acceptance.json'), 'utf8')) : { created: new Date().toISOString(), devices: [] };
const which = process.argv[3] ?? 'all';
// Keep Node alive while Windows starts Chrome and hands off its initial process.
const keepAlive = setInterval(() => {}, 1000);
const watchdog = setTimeout(() => { console.error('Browser acceptance timed out'); process.exitCode = 1; clearInterval(keepAlive); }, 180000);

async function run(name, options) {
  // The PowerShell launcher owns these profiles. Reuse the shared CDP client without launching twice.
  const originalSpawn = childProcess.spawn;
  const ownedProfiles = JSON.parse(process.env.JOS_REVIEW_OWNED_PROFILES ?? '[]');
  childProcess.spawn = (command, args, config) => {
    if (!String(command).toLowerCase().endsWith('chrome.exe')) return originalSpawn(command, args, config);
    if (ownedProfiles.some(profile => profile.port === options.port && /jos-shoot-review-/.test(profile.path))) return { kill() {} };
    return originalSpawn(command, args, config);
  };
  syncBuiltinESMExports();
  let c;
  try { c = await launch({ ...options, gpu: false }); }
  finally { childProcess.spawn = originalSpawn; syncBuiltinESMExports(); }
  const device = labelsOnly ? report.devices.find(device => device.name === name) : { name, dimensions: [], checks: {}, scroll: {}, errors: [] };
  if (!labelsOnly) report.devices.push(device);
  async function position(selector, offset = 0) {
    assert(await c.evaluate(`(() => {
      const el = document.querySelector(${JSON.stringify(selector)}); if (!el) return false;
      window.scrollTo({top: scrollY + el.getBoundingClientRect().top - document.querySelector('.jos-header').getBoundingClientRect().height - 16 + ${offset}, behavior:'instant'});
      return true;
    })()`), `Missing ${selector}`);
    await sleep(180);
  }
  async function shot(label) {
    const dimensions = await c.evaluate('[innerWidth, document.documentElement.scrollWidth]');
    device.dimensions.push({ label, dimensions });
    assert.equal(dimensions[0], options.width);
    assert.equal(dimensions[1], options.width, `${name}/${label} horizontal overflow`);
    await c.shot(resolve(out, `${name}-${label}.png`));
  }
  async function click(selector) {
    const rect = await c.evaluate(`(() => { const el = document.querySelector(${JSON.stringify(selector)}); if (!el) return null; const r = el.getBoundingClientRect(); return [r.x+r.width/2,r.y+r.height/2]; })()`);
    assert(rect, `Missing control ${selector}`);
    await c.click(...rect);
  }
  try {
    await c.send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: 'light' }, { name: 'prefers-reduced-motion', value: 'no-preference' }] });
    await c.send('Emulation.setScrollbarsHidden', { hidden: true });
    await c.send('Page.addScriptToEvaluateOnNewDocument', { source: `try { localStorage.setItem('jos-dark','0'); localStorage.setItem('jos-motion-off','0'); } catch {}` });
    await c.send('Page.navigate', { url });
    await sleep(1500);
    if (labelsOnly) {
      await position('[data-cue="jericho"]', options.height * .25); await sleep(500); await shot('jericho');
      await position('#jos-sec-03'); await shot('03');
      await position('#jos-sec-03 .jos-review-map'); await shot('stones-map');
      const overlaps = await c.evaluate(`(() => {
        const markers=[...document.querySelectorAll('#jos-sec-03 .jos-map-marker')].map(el=>({name:el.getAttribute('aria-label'),r:el.getBoundingClientRect()}));
        return markers.flatMap((a,i)=>markers.slice(i+1).filter(b=>a.r.left<b.r.right&&a.r.right>b.r.left&&a.r.top<b.r.bottom&&a.r.bottom>b.r.top).map(b=>[a.name,b.name]));
      })()`);
      assert.deepEqual(overlaps, []); device.checks.mapMarkerOverlaps = 0;
      device.checks.labelConfirmation = new Date().toISOString();
      return;
    }
    await shot('hero');
    device.checks.heroBox = await c.evaluate(`(() => { const r=document.querySelector('[data-cue="prologue"] .jos-box').getBoundingClientRect();return {top:r.top,bottom:r.bottom,height:r.height,viewport:innerHeight}; })()`);
    if (name === 'land') assert(device.checks.heroBox.bottom <= options.height, 'Landscape hero panel is clipped');
    if (name === 'port') {
      device.checks.portrait = await c.evaluate(`(() => {const h=document.querySelector('.jos-header').getBoundingClientRect(), t=document.querySelector('.jos-thread-rail').getBoundingClientRect();return {headerBottom:h.bottom,threadTop:t.top,hint:document.querySelector('.jos-rotate-hint').textContent};})()`);
      assert(device.checks.portrait.threadTop >= device.checks.portrait.headerBottom, 'Thread/header overlap');
      await position('#jos-sec-01'); await shot('01');
      await position('#jos-sec-07'); await shot('07');
      return;
    }
    await position('[data-cue="jericho"]', options.height * .25);
    await sleep(500); await shot('jericho');
    for (const id of sections) { await position(`#jos-sec-${id}`); await shot(id); }
    // Supplemental crops make the maps and long sections visible on short landscape screens.
    for (const [label, selector] of [
      ['shape-detail', '.jos-shape-serve'], ['stones-map', '#jos-sec-03 .jos-review-map'],
      ['burials-map', '#jos-sec-04 .jos-review-map'], ['stones-cards', '#jos-sec-03 .jos-grid-cards'],
      ['shechem-timeline', '#jos-sec-02 .jos-timeline'], ['burial-cards', '#jos-sec-04 .jos-grid-cards'],
    ]) { await position(selector); await shot(label); }
    await position('.jos-oak-slider-box'); await shot('oak');
    const counts = await c.evaluate(`Object.fromEntries(['i','give','serve','servant','stone'].map(id => [id,document.querySelectorAll('.jos-shape-'+id+' .jos-shape-dot').length]))`);
    assert.deepEqual(counts, { i: 20, give: 7, serve: 16, servant: 2, stone: 2 });
    device.checks.shapeCounts = counts;
    const texts = await c.evaluate(`[...document.querySelectorAll('.jos-scripture-verse p')].map(el => el.textContent)`);
    assert.deepEqual(texts, Array.from({ length: 33 }, (_, i) => data.verses[`書24:${i + 1}`]));
    device.checks.scriptureVerses = texts.length;
    device.checks.timelines = await c.evaluate(`({shechem:document.querySelectorAll('#jos-sec-02 .jos-tl-item').length,later:document.querySelectorAll('.jos-tl-later').length,forget:document.querySelectorAll('#jos-sec-05 .jos-tl-item').length,questions:document.querySelectorAll('.jos-q-card').length,beads:document.querySelectorAll('.jos-bead-item').length})`);
    assert.deepEqual(device.checks.timelines, { shechem: 13, later: 5, forget: 6, questions: 15, beads: 6 });
    device.checks.maps = await c.evaluate(`[...document.querySelectorAll('.jos-review-map')].map(el => ({markers:el.querySelectorAll('.jos-map-marker').length,regions:el.querySelectorAll('.jos-map-region').length,image:el.querySelector('image').getAttribute('href').startsWith('data:image/webp;base64,')}))`);
    await position('#jos-sec-03 .jos-relief-stage');
    const beforeWheel = await c.evaluate('scrollY');
    const wheelPoint = await c.evaluate(`(() => { const r=document.querySelector('#jos-sec-03 .jos-relief-stage').getBoundingClientRect();return [r.x+r.width/2,Math.min(innerHeight-20,r.y+100)]; })()`);
    await c.wheel(140, ...wheelPoint); await sleep(200);
    assert(await c.evaluate('scrollY') > beforeWheel, 'Map swallowed ordinary scrolling');
    device.checks.mapAllowsScroll = true;

    // Real pointer click opens a preview; its highlight, focus and explicit round-trip are checked.
    await position('.jos-shape-serve');
    const bookmark = await c.evaluate('scrollY');
    await click('.jos-shape-serve .jos-shape-dot'); await sleep(100);
    assert.equal(await c.evaluate('scrollY'), bookmark);
    assert.equal(await c.evaluate(`document.querySelector('.jos-peek-body mark')?.textContent`), '事奉');
    await shot('peek');
    const focusInPeek = await c.evaluate(`document.querySelector('.jos-peek-panel').contains(document.activeElement)`);
    assert(focusInPeek); device.checks.peekFocus = focusInPeek;
    await click('.jos-peek-links .jos-primary-btn'); await sleep(150);
    assert.notEqual(await c.evaluate('scrollY'), bookmark);
    assert.equal(await c.evaluate('window.__josState.returnSpot.scrollY'), bookmark);
    await click('.jos-return-btn'); await sleep(150);
    assert.equal(await c.evaluate('scrollY'), bookmark); device.checks.returnRestored = true;

    // One 9-second trace per main device, every 80ms; all actions are non-navigation actions.
    // Focus stays at this location; programmatic actions also exercise controls outside this short viewport.
    await position('#jos-sec-01');
    const sample = await c.evaluate(`new Promise(resolve => {
      const values=[]; const began=performance.now();
      const timer=setInterval(() => { values.push({ms:Math.round(performance.now()-began),y:scrollY}); if(performance.now()-began>=9000){clearInterval(timer);resolve(values);} },80);
      setTimeout(()=>document.querySelector('.jos-shape-i .jos-shape-dot').click(),500);
      setTimeout(()=>document.querySelector('.jos-peek-close').click(),1500);
      setTimeout(()=>document.querySelector('#jos-sec-01 details').open=true,2300);
      setTimeout(()=>document.querySelector('[aria-controls="jos-shape-give"]').click(),3300);
      setTimeout(()=>document.querySelector('[aria-controls="jos-shape-give"]').click(),4300);
      setTimeout(()=>document.querySelector('#jos-sec-01 details').open=false,5300);
      setTimeout(()=>document.querySelector('.jos-oak-range').value='0',6300);
      setTimeout(()=>document.querySelector('.jos-oak-range').dispatchEvent(new Event('input',{bubbles:true})),6400);
    })`);
    device.scroll = { intervalMs: 80, durationMs: 9000, samples: sample.length, min: Math.min(...sample.map(x => x.y)), max: Math.max(...sample.map(x => x.y)) };
    writeFileSync(resolve(out, `${name}-scroll.json`), JSON.stringify(sample, null, 2));
    assert.equal(device.scroll.min, device.scroll.max, 'Non-navigation interactions moved the page');
    assert(sample.at(-1).ms >= 9000);

    // Filter/source identity and exact Scripture routes, including the initial URL entry.
    await position('#jos-sec-06');
    await c.evaluate(`[...document.querySelectorAll('.jos-filter-bar button')].find(b=>b.textContent.includes('KingComments')).click()`);
    assert(await c.evaluate(`[...document.querySelectorAll('.jos-q-views .jos-comm-work')].every(el=>el.textContent.startsWith('KC'))`));
    await c.evaluate(`document.querySelector('.jos-filter-bar button').click()`);
    await c.send('Page.navigate', { url: `${url}#v=24:15` }); await sleep(650);
    device.checks.verseRoute = await c.evaluate(`(() => { const el=document.getElementById('jos-review-verse-15');return {target:el.classList.contains('jos-review-target'),top:el.getBoundingClientRect().top};})()`);
    assert(device.checks.verseRoute.target); await shot('verse-route');
    await c.evaluate(`location.hash='sec=scripture'`); await sleep(200);
    assert(await c.evaluate(`document.getElementById('jos-sec-07').classList.contains('jos-review-target')`));
    await c.evaluate(`location.hash='sec=readings'`); await sleep(400);
    assert(await c.evaluate(`document.getElementById('jos-sec-06').classList.contains('jos-review-target')`));
    device.checks.readingsRoute = true;
    await c.evaluate(`location.hash='card='+encodeURIComponent(${JSON.stringify(data.readingCards[0].question)})`); await sleep(200);
    assert(await c.evaluate(`document.querySelector('.jos-q-card').classList.contains('jos-review-target')`));
    device.checks.questionRoute = true;
  } finally {
    device.errors = c.consoleLog.filter(line => line.startsWith('[error]') || line.startsWith('[exception]'));
    await Promise.race([c.close(), sleep(2000)]);
    writeFileSync(resolve(out, 'acceptance.json'), JSON.stringify(report, null, 2));
    console.log(name, JSON.stringify(device));
    assert.equal(device.errors.length, 0, `${name}: browser errors`);
  }
}
try {
  if (which === 'all' || which === 'desk') await run('desk', { width: 1440, height: 900, port: 9374 });
  if (which === 'all' || which === 'land') await run('land', { width: 844, height: 390, mobile: true, dpr: 1, port: 9375 });
  if (which === 'all' || which === 'port') await run('port', { width: 390, height: 844, mobile: true, dpr: 1, port: 9376 });
  console.log(`Screenshots and acceptance reports: ${out}`);
} finally { clearInterval(keepAlive); clearTimeout(watchdog); }
