// 在整合後的網站上驗回聲連結：
//  1. 每個回聲拍的每個「呼應」連結：點了之後 story.beat 要等於目標拍；畫面角落出現「回到：…」；再點它要回到回聲拍。
//  2. 每個被呼應的拍的「後來」連結：點了之後 story.beat 要等於回聲拍；「回到」要回到原來的拍。
//  3. 不可有平滑捲動：捲動位置只有「起點」與「終點」兩個值（逐幀取樣），computed scroll-behavior 是 auto。
// 桌機（滑鼠點擊）與手機（觸控點擊）各跑一次。用法：node tools/check-echo.mjs <url> [outDir]
import { mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { launch, sleep } from './cdp.mjs';

const [url, outDir] = process.argv.slice(2);
if (!url) throw new Error('用法：node tools/check-echo.mjs <url> [outDir]');
if (outDir) mkdirSync(outDir, { recursive: true });

let failed = 0;
const fail = (msg) => { failed++; console.log(`  × ${msg}`); };
const ok = (msg) => console.log(`  ✓ ${msg}`);

async function run(mobile, port) {
  console.log(mobile ? '手機（觸控）' : '桌機（滑鼠）');
  const W = mobile ? 390 : 1440, H = mobile ? 844 : 900;
  const b = await launch({ width: W, height: H, mobile, port, gpu: true });
  await b.send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: 'light' }, { name: 'prefers-reduced-motion', value: 'no-preference' }] });
  await b.send('Page.addScriptToEvaluateOnNewDocument', { source: `try { localStorage.setItem('jf-coach-seen', '1'); localStorage.setItem('jf-motion', 'on') } catch {}` });
  await b.send('Page.navigate', { url });
  await sleep(4500);

  const beatNow = () => b.evaluate('window.__jfStory.beat');
  const behavior = await b.evaluate(`getComputedStyle(document.documentElement).scrollBehavior`);
  behavior === 'auto' ? ok('computed scroll-behavior 是 auto') : fail(`scroll-behavior 是 ${behavior}`);

  const tap = async (x, y) => {
    if (mobile) {
      await b.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y }] });
      await sleep(60);
      await b.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
    } else {
      await b.send('Input.dispatchMouseEvent', { type: 'mouseMoved', x, y });
      await b.send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', clickCount: 1 });
      await b.send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 });
    }
  };
  /** 捲到某一拍的中段，再把說明框內的目標按鈕帶進視野（只捲框自己），回傳按鈕中心 */
  const reveal = async (beatId, selector, nth) => {
    await b.evaluate(`(() => { const el = document.querySelector('[data-beat="${beatId}"]'); window.scrollTo(0, el.getBoundingClientRect().top + scrollY + Math.max(0, el.offsetHeight - innerHeight) * 0.5); })()`);
    await sleep(1800);
    return JSON.parse(await b.evaluate(`JSON.stringify((() => {
      const el = document.querySelector('[data-beat="${beatId}"]');
      const btn = el.querySelectorAll(${JSON.stringify(selector)})[${nth}];
      const body = btn.closest('.jf-box-body');
      if (body && body.scrollHeight > body.clientHeight) body.scrollTop = Math.max(0, btn.offsetTop - 60);
      const r = btn.getBoundingClientRect();
      return { x: r.x + r.width / 2, y: r.y + r.height / 2, to: btn.dataset.to, inView: r.top >= 0 && r.bottom <= innerHeight };
    })())`));
  };
  const sampleStart = () => b.evaluate(`(() => { window.__ys = new Set(); const f = () => { window.__ys.add(Math.round(scrollY)); window.__raf = requestAnimationFrame(f); }; f(); })()`);
  const sampleStop = async () => JSON.parse(await b.evaluate(`JSON.stringify((() => { cancelAnimationFrame(window.__raf); return [...window.__ys]; })())`));
  const backText = () => b.evaluate(`(() => { const e = document.querySelector('.jf-return'); return e && !e.hidden ? e.textContent : null; })()`);

  const pairs = JSON.parse(await b.evaluate(`JSON.stringify([...document.querySelectorAll('.jf-beat')].map((s) => ({ id: s.dataset.beat, to: s.querySelectorAll('.jf-echo-to').length, later: s.querySelectorAll('.jf-echo-later').length })).filter((p) => p.to || p.later))`));
  console.log(`  有連結的拍：${pairs.map((p) => `${p.id}（呼應 ${p.to}、後來 ${p.later}）`).join('、')}`);
  let shots = 0;

  for (const p of pairs) {
    for (const [sel, count] of [['.jf-echo-to', p.to], ['.jf-echo-later', p.later]]) {
      for (let i = 0; i < count; i++) {
        const info = await reveal(p.id, sel, i);
        const label = `${p.id} → ${info.to}（${sel === '.jf-echo-to' ? '呼應' : '後來'}）`;
        if (!info.inView) { fail(`${label}：連結不在視野內，點不到`); continue; }
        await sampleStart();
        await tap(info.x, info.y);
        await sleep(1100);
        const ys = await sampleStop();
        const beat = await beatNow();
        const back = await backText();
        const expectBeat = info.to;
        beat === expectBeat ? ok(`${label}：story.beat = ${beat}`) : fail(`${label}：story.beat 是 ${beat}，應為 ${expectBeat}`);
        back && back.startsWith('回到：') ? ok(`  「${back}」按鈕出現`) : fail(`${label}：沒有出現「回到」按鈕（${JSON.stringify(back)}）`);
        ys.length <= 2 ? ok(`  無平滑捲動（scrollY 取樣值 ${ys.length} 個：${ys.join('、')}）`) : fail(`${label}：scrollY 取樣到 ${ys.length} 個值（${ys.join('、')}），疑似平滑捲動`);
        if (outDir && shots < 4) await b.shot(join(outDir, `echo-${mobile ? 'm' : 'd'}-${String(++shots).padStart(2, '0')}-${p.id}-to-${info.to}.png`));
        // 回到
        const bx = JSON.parse(await b.evaluate(`JSON.stringify((() => { const e = document.querySelector('.jf-return'); if (!e || e.hidden) return null; const r = e.getBoundingClientRect(); return { x: r.x + r.width / 2, y: r.y + r.height / 2 }; })())`));
        if (bx) {
          await tap(bx.x, bx.y);
          await sleep(1100);
          const again = await beatNow();
          again === p.id ? ok(`  按「回到」→ story.beat = ${again}`) : fail(`${label}：按「回到」後 story.beat 是 ${again}，應為 ${p.id}`);
          (await backText()) === null ? ok('  回到後按鈕收起來') : fail('  回到後按鈕還在');
        }
      }
    }
  }

  // 章末「後來的人怎麼守」：本章的回聲拍自動列在最前面，「看故事裡的這一段」跳回該回聲拍
  const ends = JSON.parse(await b.evaluate(`JSON.stringify([...document.querySelectorAll('.jf-end')].map((e) => ({
    chapter: e.dataset.chapter,
    ot: e.querySelectorAll('.jf-ot-item').length,
    echoes: [...e.querySelectorAll('.jf-ot-echo')].map((x) => x.dataset.beat),
    firstIsEcho: e.querySelector('.jf-ot-sub[data-kind="kept"] .jf-ot-item')?.classList.contains('jf-ot-echo') ?? false,
    hasOt: !!e.querySelector('.jf-ot'),
  })))`));
  for (const e of ends) console.log(`  章末 ${e.chapter}：舊約其他書卷 ${e.hasOt ? e.ot + ' 筆' : '（不顯示）'}，其中回聲拍 ${e.echoes.length}（${e.echoes.join('、') || '—'}）`);
  const expectEnds = { firstfruits: ['gilgal'], 'second-passover': ['hezekiah'], weeks: ['ruth'], trumpets: ['ezra-reads'], booths: ['neh-booths'] };
  for (const [ch, ids] of Object.entries(expectEnds)) {
    const e = ends.find((x) => x.chapter === ch);
    e && JSON.stringify(e.echoes) === JSON.stringify(ids) && e.firstIsEcho ? ok(`章末 ${ch}：回聲拍 ${ids.join('、')} 列在「後來的人怎麼守」最前面`) : fail(`章末 ${ch}：回聲拍 ${JSON.stringify(e?.echoes)}、排最前面 ${e?.firstIsEcho}`);
  }
  const atone = ends.find((x) => x.chapter === 'atonement');
  atone && !atone.hasOt ? ok('章末 atonement：沒有回聲拍也沒有 ot，不顯示這一欄') : fail('章末 atonement 不該顯示舊約欄');
  for (const e of ends.filter((x) => x.echoes.length)) {
    for (const beatId of e.echoes) {
      const info = JSON.parse(await b.evaluate(`JSON.stringify((() => {
        const btn = document.querySelector('.jf-end[data-chapter="${e.chapter}"] .jf-ot-story[data-to="${beatId}"]');
        const y = btn.getBoundingClientRect().top + scrollY - innerHeight / 2;
        window.scrollTo(0, Math.max(0, y));
        return null;
      })())`));
      void info;
      await sleep(900);
      const pos = JSON.parse(await b.evaluate(`JSON.stringify((() => { const r = document.querySelector('.jf-end[data-chapter="${e.chapter}"] .jf-ot-story[data-to="${beatId}"]').getBoundingClientRect(); return { x: r.x + r.width / 2, y: r.y + r.height / 2, inView: r.top >= 0 && r.bottom <= innerHeight, text: document.querySelector('.jf-end[data-chapter="${e.chapter}"] .jf-ot-story[data-to="${beatId}"]').textContent }; })())`));
      const label = `章末 ${e.chapter} →「${pos.text}」→ ${beatId}`;
      if (!pos.inView) { fail(`${label}：連結不在視野內`); continue; }
      await sampleStart();
      await tap(pos.x, pos.y);
      await sleep(1100);
      const ys = await sampleStop();
      const beat = await beatNow();
      beat === beatId ? ok(`${label}：story.beat = ${beat}`) : fail(`${label}：story.beat 是 ${beat}`);
      ys.length <= 2 ? ok(`  無平滑捲動（scrollY 取樣值 ${ys.length} 個）`) : fail(`${label}：scrollY 取樣到 ${ys.length} 個值，疑似平滑捲動`);
      (await backText()) === null ? ok('  章末的跳轉不出現「回到」按鈕') : fail(`${label}：多出「回到」按鈕`);
    }
  }

  // 8 秒後自動消失、以及捲動超過一個螢幕高就消失
  if (pairs.length) {
    const p = pairs.find((x) => x.to);
    if (p) {
      const info = await reveal(p.id, '.jf-echo-to', 0);
      await tap(info.x, info.y);
      await sleep(1100);
      (await backText()) ? ok('「回到」按鈕出現（準備驗 8 秒消失）') : fail('「回到」按鈕沒有出現');
      await sleep(8200);
      (await backText()) === null ? ok('8 秒後「回到」按鈕消失') : fail('8 秒後按鈕還在');
      await tap(info.x, info.y).catch(() => undefined);
    }
  }

  const w = await b.evaluate('JSON.stringify([innerWidth, document.documentElement.scrollWidth])');
  console.log(`  [innerWidth, scrollWidth] = ${w}`);
  const [iw, sw] = JSON.parse(w);
  iw === sw ? ok('沒有橫向捲動') : fail('scrollWidth 不等於 innerWidth');
  const errs = b.consoleLog.filter((l) => /^\[(exception|error)\]/.test(l));
  errs.length ? fail(`console 錯誤 ${errs.length} 則（不重複：${[...new Set(errs.map((e) => e.split(/\r?\n/)[0]))].slice(0, 3).join(' | ')}）`) : ok('console 無錯誤');
  await b.close();
}

await run(false, 9441);
await run(true, 9442);
console.log(failed ? `共 ${failed} 項失敗` : '全部通過');
process.exit(failed ? 1 : 0);
