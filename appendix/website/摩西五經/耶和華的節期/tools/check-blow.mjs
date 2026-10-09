// 在整合後的網站上驗「吹」：長按按鈕約 2 秒，story.blow.done 要是 true、blasts >= 1，放開後 level 要回到 0。
// 桌機（滑鼠）與手機（觸控）、動態開與關（網站的「動態」開關，localStorage jf-motion）各跑一次，
// 另外驗鍵盤（空白鍵按住）與「捲過去沒做 → auto」。每種都印出 status 文字原文。
// 用法：node tools/check-blow.mjs <url> [outDir]
import { mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { launch, sleep } from './cdp.mjs';

const [url, outDir] = process.argv.slice(2);
if (!url) throw new Error('用法：node tools/check-blow.mjs <url> [outDir]');
if (outDir) mkdirSync(outDir, { recursive: true });

let port = 9421;
let failed = 0;
const fail = (msg) => { failed++; console.log(`  × ${msg}`); };
const ok = (msg) => console.log(`  ✓ ${msg}`);

async function run({ mobile, motionOff, mode }) {
  const tag = `${mobile ? '手機觸控' : '桌機滑鼠'}／動態${motionOff ? '關' : '開'}${mode === 'key' ? '／鍵盤' : mode === 'skip' ? '／捲過去' : ''}`;
  console.log(tag);
  const W = mobile ? 390 : 1440, H = mobile ? 844 : 900;
  const b = await launch({ width: W, height: H, mobile, port: port++, gpu: true });
  await b.send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: 'light' }, { name: 'prefers-reduced-motion', value: motionOff ? 'reduce' : 'no-preference' }] });
  await b.send('Page.addScriptToEvaluateOnNewDocument', { source: `try { localStorage.setItem('jf-coach-seen', '1'); localStorage.setItem('jf-motion', '${motionOff ? 'off' : 'on'}') } catch {}` });
  await b.send('Page.navigate', { url });
  await sleep(4500);
  const story = async () => JSON.parse(await b.evaluate('JSON.stringify(window.__jfStory.blow)'));
  const status = () => b.evaluate(`document.querySelector('.jf-blow-status')?.textContent ?? null`);
  const scrollToCue = (cue, f = 0.5) => b.evaluate(`(() => { const el = document.querySelector('[data-cue="${cue}"]'); window.scrollTo(0, el.getBoundingClientRect().top + scrollY + Math.max(0, el.offsetHeight - innerHeight) * ${f}); })()`);

  if (mode === 'skip') {
    await scrollToCue('trumpet-offerings');
    await sleep(2000);
    const s = await story();
    console.log('  story.blow', JSON.stringify(s), '／status', JSON.stringify(await status()));
    s.auto && s.done && s.blasts === 0 && s.level === 0 ? ok('捲過去沒做：auto、done，沒有補聲波（level 0、blasts 0）') : fail('捲過去沒做的狀態不對');
    await b.close();
    return;
  }

  await scrollToCue('blow');
  await sleep(2200);
  const r = JSON.parse(await b.evaluate(`JSON.stringify((() => { const r = document.querySelector('.jf-blow-btn').getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2, r.width, r.height]; })())`));
  const before = await story();
  console.log('  按之前', JSON.stringify(before), '／status', JSON.stringify(await status()));
  if (outDir) await b.shot(join(outDir, `blow-${mobile ? 'm' : 'd'}-${motionOff ? 'off' : 'on'}-0.png`));

  if (mode === 'key') {
    await b.evaluate(`document.querySelector('.jf-blow-btn').focus()`);
    await b.send('Input.dispatchKeyEvent', { type: 'keyDown', key: ' ', code: 'Space', windowsVirtualKeyCode: 32 });
  } else if (mobile) {
    await b.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: r[0], y: r[1] }] });
  } else {
    await b.send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: r[0], y: r[1] });
    await b.send('Input.dispatchMouseEvent', { type: 'mousePressed', x: r[0], y: r[1], button: 'left', clickCount: 1 });
  }
  await sleep(700);
  const mid = await story();
  console.log('  按住 0.7 秒', JSON.stringify(mid), '／status', JSON.stringify(await status()));
  mid.holding && mid.level > 0.2 && mid.level < 1 ? ok('按住中 level 在升（0.2–1 之間）') : fail(`按住 0.7 秒的 level 不在 0.2–1：${mid.level}`);
  await sleep(1300);
  const held = await story();
  console.log('  按住 2 秒', JSON.stringify(held), '／status', JSON.stringify(await status()));
  if (outDir) await b.shot(join(outDir, `blow-${mobile ? 'm' : 'd'}-${motionOff ? 'off' : 'on'}-1.png`));
  held.done && held.blasts >= 1 ? ok(`done = true、blasts = ${held.blasts}`) : fail('按住 2 秒後 done 不是 true 或 blasts < 1');

  if (mode === 'key') await b.send('Input.dispatchKeyEvent', { type: 'keyUp', key: ' ', code: 'Space', windowsVirtualKeyCode: 32 });
  else if (mobile) await b.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
  else await b.send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: r[0], y: r[1], button: 'left', clickCount: 1 });
  await sleep(300);
  const rel = await story();
  console.log('  放開 0.3 秒', JSON.stringify(rel), '／status', JSON.stringify(await status()));
  !rel.holding && rel.level < held.level ? ok('放開後 holding = false、level 回落中') : fail('放開後沒有回落');
  await sleep(900);
  const end = await story();
  console.log('  放開 1.2 秒', JSON.stringify(end), '／status', JSON.stringify(await status()));
  end.level === 0 ? ok('level 回到 0') : fail(`level 沒回到 0：${end.level}`);

  const errs = b.consoleLog.filter((l) => /^\[(exception|error)\]/.test(l));
  errs.length ? fail(`console 錯誤 ${errs.length} 則（不重複：${[...new Set(errs.map((e) => e.split(/\r?\n/)[0]))].slice(0, 3).join(' | ')}）`) : ok('console 無錯誤');
  await b.close();
}

for (const motionOff of [false, true]) {
  await run({ mobile: false, motionOff });
  await run({ mobile: true, motionOff });
}
await run({ mobile: false, motionOff: false, mode: 'key' });
await run({ mobile: false, motionOff: false, mode: 'skip' });
console.log(failed ? `共 ${failed} 項失敗` : '全部通過');
process.exit(failed ? 1 : 0);
