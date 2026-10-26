import { siteUrl } from './site-server.mjs';
// 接手驗收截圖：桌機 1440x900、手機橫向 844x390、手機直式 390x844。
// 用法：node tools/shoot-handoff.mjs [輸出資料夾]   （先 npm run build）
import { mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { launch, sleep } from './cdp.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const PROJECT_DIR = resolve(here, '..');
const url = siteUrl;
const OUT = process.argv[2] ?? resolve(PROJECT_DIR, '.tmp-shots');
mkdirSync(OUT, { recursive: true });

async function setMedia(c) {
  await c.send('Emulation.setEmulatedMedia', {
    features: [
      { name: 'prefers-color-scheme', value: 'light' },
      { name: 'prefers-reduced-motion', value: 'no-preference' },
    ],
  });
}

const scrollToCue = (cue) => `(() => {
  const el = document.querySelector('[data-cue="${cue}"]') || document.getElementById('jos-beat-${cue}');
  if (!el) return 'missing ${cue}';
  const hdr = document.querySelector('.jos-header')?.getBoundingClientRect().height ?? 56;
  window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY + window.innerHeight * 0.3 });
  return 'ok';
})()`;

const errorsOf = (c) =>
  c.consoleLog.filter((l) => l.startsWith('[error]') || l.startsWith('[exception]'));

async function run(name, opts, steps) {
  const c = await launch({ ...opts, gpu: false });
  try {
    await setMedia(c);
    await c.send('Page.navigate', { url });
    await sleep(2500);
    for (const s of steps) {
      if (s.js) console.log(name, s.label ?? 'js', await c.evaluate(s.js));
      if (s.wait) await sleep(s.wait);
      if (s.shot) {
        await c.shot(resolve(OUT, s.shot));
        const dims = await c.evaluate('[innerWidth, document.documentElement.scrollWidth]');
        console.log(name, s.shot, 'dims', JSON.stringify(dims));
        console.log(resolve(OUT, s.shot));
      }
    }
    console.log(name, 'errors', JSON.stringify(errorsOf(c)));
  } finally {
    await c.close();
  }
}

const which = process.argv[3] ?? 'all';
const act2 = `(() => { const s = document.getElementById('jos-seg-act-2'); if (!s) return 'noseg'; window.scrollTo({ top: s.getBoundingClientRect().top + window.scrollY + 40 }); return 'ok'; })()`;

if (which === 'all' || which === 'desk')
  await run('desk', { width: 1440, height: 900, port: 9351 }, [
    { shot: 'desk-hero.png' },
    { js: act2, wait: 1800 },
    { shot: 'desk-act2.png' },
  ]);
if (which === 'all' || which === 'land')
  await run('land', { width: 844, height: 390, mobile: true, dpr: 2, port: 9352 }, [
    { shot: 'land-hero.png' },
    { js: act2, wait: 1800 },
    { shot: 'land-act2.png' },
    { js: scrollToCue('answer-2'), wait: 1800 },
    { shot: 'land-act4.png' },
  ]);
if (which === 'all' || which === 'port')
  await run('port', { width: 390, height: 844, mobile: true, dpr: 2, port: 9353 }, [
    { shot: 'port-hero.png' },
    { js: `document.querySelector('.jos-rotate-hint')?.textContent ?? 'no-hint'`, label: 'hint' },
  ]);

// 額外：手機橫向的整理區、新手教學、小卡、立石拍
if (which === 'extra') {
  const toRaise = scrollToCue('raise');
  await run('land2', { width: 844, height: 390, mobile: true, dpr: 2, port: 9354 }, [
    { js: scrollToCue('raise'), wait: 1800 },
    { shot: 'land-raise.png' },
    { js: `document.querySelector('.jos-coach-trigger')?.click(); 'coach'`, wait: 600 },
    { shot: 'land-coach.png' },
    { js: `document.querySelector('.jos-coach-trigger')?.click(); true ? (window.scrollTo({top: document.getElementById('jos-sec-03').getBoundingClientRect().top + scrollY - 50}), 'sec03') : 'nosec'`, wait: 800 },
    { shot: 'land-review.png' },
    { js: `(() => { const b = document.querySelector('.jos-stage-tag'); return document.querySelectorAll('.jos-prologue-stone-btn').length; })()` },
  ]);
}

if (which === 'map') {
  await run('map', { width: 844, height: 390, mobile: true, dpr: 2, port: 9355 }, [
    { js: scrollToCue('jericho'), wait: 2200 },
    { shot: 'land-jericho.png' },
    { js: scrollToCue('egypt'), wait: 2200 },
    { shot: 'land-egypt.png' },
  ]);
  await run('mapd', { width: 1440, height: 900, port: 9356 }, [
    { js: scrollToCue('jericho'), wait: 2200 },
    { shot: 'desk-jericho.png' },
  ]);
}
