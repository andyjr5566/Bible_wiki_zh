import { siteUrl } from './site-server.mjs';
// 「一拍只講一種東西」驗收：用 headless Chrome（jos-shoot- 暫存設定檔）開 dist/index.html，
// 依捲動進度停在各拍，截圖並量測：水平溢出、更多小卡開關前後 scrollY、泡泡與名牌／約書亞是否重疊。
// 用法：node tools/shoot-onevoice.mjs desktop|mobile [all]
import { mkdirSync, writeFileSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';
import { launch, sleep } from './cdp.mjs';

const which = process.argv[2] ?? 'desktop';
const doAll = process.argv.includes('all');
const device =
  which === 'mobile'
    ? { name: 'mobile', width: 844, height: 390, dpr: 2, mobile: true, port: 9402 }
    : { name: 'desktop', width: 1440, height: 900, dpr: 1, mobile: false, port: 9401 };

const out = resolve('.tmp-shots/onevoice');
mkdirSync(out, { recursive: true });
const site = JSON.parse(readFileSync('src/data/site.json', 'utf8'));
const beats = site.segments.flatMap((s) => s.beats);
const idxOf = (cue) => beats.findIndex((b) => b.cue === cue) + 1;

const hash = (file) => createHash('sha256').update(readFileSync(file)).digest('hex');
const report = { created: new Date().toISOString(), device: device.name, viewport: [device.width, device.height], dpr: device.dpr, buildSha256: hash('dist/index.html'), dataSha256: hash('src/data/site.json'), shots: [], checks: [], failures: [] };
const fail = (msg) => {
  report.failures.push(msg);
  console.log('FAIL', msg);
};

const keepAlive = setInterval(() => {}, 1000);
const c = await launch({ width: device.width, height: device.height, dpr: device.dpr, mobile: device.mobile, port: device.port });
try {
  await c.send('Page.navigate', { url: siteUrl });
  for (let i = 0; i < 80; i++) {
    if (await c.evaluate('!!window.__josState && !!window.__josScene && document.querySelectorAll("[data-cue]").length>30')) break;
    await sleep(500);
  }
  await sleep(1500);

  async function goto(cue, p) {
    await c.evaluate(`(() => {
      const el = document.querySelector('section[data-cue="${cue}"]');
      const H = innerHeight, anchor = H * 0.36;
      const r = el.getBoundingClientRect();
      const top = anchor - ${p} * (r.height - H * 0.35);
      window.scrollTo({ top: scrollY + r.top - top, behavior: 'instant' });
    })()`);
    await sleep(1100);
    const cur = await c.evaluate('window.__josState.cue');
    if (cur !== cue) fail(`goto ${cue}: 實際停在 ${cur}`);
  }

  async function measureCommon(tag) {
    const m = await c.evaluate(`(() => {
      const rect = (el) => { if (!el) return null; const r = el.getBoundingClientRect(); return { x0: r.left, y0: r.top, x1: r.right, y1: r.bottom, w: r.width, h: r.height }; };
      const vis = (el) => el && getComputedStyle(el).visibility !== 'hidden' && getComputedStyle(el).display !== 'none' && parseFloat(getComputedStyle(el).opacity) > 0.05;
      const panel = document.querySelector('.jos-panel-on');
      const q = (sel) => panel ? [...panel.querySelectorAll(sel)].filter(vis) : [];
      const tags = [...document.querySelectorAll('.jos-stage-tag')].filter((e) => getComputedStyle(e).display !== 'none').map((e) => ({ text: e.textContent, ...rect(e) }));
      const bubble = q('.jos-bubble')[0];
      const bodies = window.__josScene.getBodyBoxes();
      return {
        scrollW: document.documentElement.scrollWidth, innerW: innerWidth, scrollY,
        verse: q('.jos-vbox-verse').map((e) => ({ ...rect(e), op: getComputedStyle(e).opacity, font: parseFloat(getComputedStyle(e).fontSize), scrollable: e.scrollHeight > e.clientHeight + 1, lines: Math.round(e.scrollHeight / parseFloat(getComputedStyle(e).lineHeight)) }))[0] ?? null,
        note: q('.jos-vbox-note').map((e) => ({ ...rect(e), op: getComputedStyle(e).opacity }))[0] ?? null,
        head: q('.jos-vbox-headline').map((e) => ({ ...rect(e), op: getComputedStyle(e).opacity }))[0] ?? null,
        more: rect(q('.jos-more-btn')[0]),
        bubble: bubble ? { ...rect(bubble), text: bubble.textContent, docked: bubble.classList.contains('jos-bubble-docked'), lines: Math.round(bubble.querySelector('.jos-bubble-text').getBoundingClientRect().height / parseFloat(getComputedStyle(bubble).lineHeight)) } : null,
        tags, joshua: bodies.find((b) => b.id === 'joshua') ?? null, bodies,
        cue: window.__josState.cue, beat: window.__josState.beat, p: window.__josState.beatProgress,
      };
    })()`);
    if (m.scrollW > m.innerW) fail(`${tag}: 水平溢出 ${m.scrollW}>${m.innerW}`);
    if (m.verse && m.verse.w > device.width * 0.4 + 1) fail(`${tag}: 經文框寬 ${Math.round(m.verse.w)} 超過 40%`);
    if (m.bubble && !m.bubble.docked) {
      const bb = m.bubble;
      const hit = (a, b, pad = 0) => a.x0 < b.x1 + pad && a.x1 > b.x0 - pad && a.y0 < b.y1 + pad && a.y1 > b.y0 - pad;
      for (const t of m.tags) if (hit(bb, t)) fail(`${tag}: 泡泡蓋住名牌 ${t.text}`);
      if (m.joshua && hit(bb, m.joshua)) {
        const ox = Math.min(bb.x1, m.joshua.x1) - Math.max(bb.x0, m.joshua.x0);
        const oy = Math.min(bb.y1, m.joshua.y1) - Math.max(bb.y0, m.joshua.y0);
        const ratio = (ox * oy) / ((m.joshua.x1 - m.joshua.x0) * (m.joshua.y1 - m.joshua.y0));
        m.joshuaOverlap = Number(ratio.toFixed(3));
        if (ratio > 0) fail(`${tag}: 泡泡蓋住約書亞（${Math.round(ratio * 100)}%）`);
      }
      if (bb.y0 < 0 || bb.x0 < 0 || bb.x1 > device.width) fail(`${tag}: 泡泡超出視窗`);
      if (device.mobile && bb.lines > 2) fail(`${tag}: 手機橫擺泡泡 ${bb.lines} 行`);
    }
    if (m.bubble?.docked) fail(`${tag}: 有 3D 時對話沒有浮在人物旁`);
    return m;
  }

  async function shot(name, tag) {
    const file = `${String(idxOf(tag.cue)).padStart(2, '0')}-${device.name}-${tag.cue}${tag.suffix ? '-' + tag.suffix : ''}.png`;
    await c.shot(resolve(out, file));
    report.shots.push(file);
    return file;
  }

  async function snap(cue, p, suffix) {
    await goto(cue, p);
    const m = await measureCommon(`${cue}@${p}`);
    if (suffix === 'note' && (!m.note || m.verse)) fail(`${cue}: 短註段仍顯示經文或缺少短註`);
    if (suffix === 'verse' && (!m.verse || m.note)) fail(`${cue}: 經文段仍顯示短註或缺少經文`);
    const file = await shot('', { cue, suffix });
    report.checks.push({ cue, p, suffix, file, m: { ...m, bodies: undefined } });
    console.log('shot', file);
    return m;
  }

  // 必拍
  await snap('prologue', 0.3, 'verse');
  await snap('beyond-river', 0.3, 'verse');
  await snap('beyond-river', 0.9, 'note');
  await snap('egypt', 0.6, 'coffin');
  await snap('family-2', 0.25, 'line1');
  await snap('family-2', 0.75, 'line2');
  await snap('my-house', 0.3, 'verse');
  await snap('my-house', 0.9, 'note');
  await snap('cannot', 0.1, 'headline');
  await snap('cannot', 0.45, 'verse');
  await snap('cannot', 0.9, 'note');
  await snap('family-4', 0.25, 'line1');
  await snap('family-4', 0.75, 'line2');
  await snap('the-stone', 0.3, 'verse');
  await snap('the-stone', 0.9, 'note');
  await snap('family-5', 0.25, 'line1');
  await snap('family-5', 0.75, 'line2');
  await snap('epilogue-diff', 0.5, 'diff');
  await snap('east', 0.4, 'balak');
  await snap('gifts', 0.4, 'cards');
  await snap('raise', 0.3, 'button');
  await snap('put-away', 0.3, 'past');
  await snap('epilogue-stone', 0.3, 'verse');
  await snap('epilogue-stone', 0.9, 'note');
  await snap('gather', 0.1, 'kicker');

  // 更多小卡：開／關前後 scrollY 不變、Esc 關閉、焦點回到按鈕
  for (const [cue, p] of [['beyond-river', 0.3], ['family-2', 0.25], ['jericho', 0.3], ['bones', 0.3]]) {
    await goto(cue, p);
    const before = await c.evaluate('scrollY');
    const btn = await c.evaluate(`(() => { const b = document.querySelector('.jos-panel-on .jos-more-btn'); if (!b) return null; const r = b.getBoundingClientRect(); const e = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); return { x: r.left + r.width / 2, y: r.top + r.height / 2, hit: e && e.className, beat: window.__josState.beat, on: document.querySelector('.jos-panel-on')?.dataset.panelBeat }; })()`);
    console.log('click target', cue, JSON.stringify(btn));
    if (!btn) { fail(`${cue}: 沒有更多鈕`); continue; }
    await c.click(btn.x, btn.y);
    await sleep(500);
    const open = await c.evaluate(`(() => { const k = document.querySelector('.jos-more-card'); const r = k.getBoundingClientRect(); return { hidden: k.classList.contains('jos-more-hidden'), y: scrollY, r: { x0: r.left, y0: r.top, x1: r.right, y1: r.bottom }, active: document.activeElement?.className, st: window.__josState.moreOpen, bodyScroll: k.querySelector('.jos-more-body').scrollHeight + '/' + k.querySelector('.jos-more-body').clientHeight, scrollW: document.documentElement.scrollWidth }; })()`);
    if (open.hidden) fail(`${cue}: 更多小卡沒開`);
    if (open.y !== before) fail(`${cue}: 開小卡後 scrollY ${before}->${open.y}`);
    if (open.scrollW > device.width) fail(`${cue}: 開小卡後水平溢出`);
    if (open.r.y0 < 0 || open.r.y1 > device.height + 1 || open.r.x1 > device.width + 1) fail(`${cue}: 小卡超出視窗`);
    await c.shot(resolve(out, `${String(idxOf(cue)).padStart(2, '0')}-${device.name}-${cue}-more.png`));
    report.shots.push(`${String(idxOf(cue)).padStart(2, '0')}-${device.name}-${cue}-more.png`);
    // 在小卡裡滾輪：頁面不動
    await c.wheel(300, open.r.x0 + 40, open.r.y0 + 80);
    await sleep(200);
    const afterWheel = await c.evaluate('scrollY');
    if (afterWheel !== before) fail(`${cue}: 小卡內滾輪帶動頁面 ${before}->${afterWheel}`);
    await c.send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 });
    await c.send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 });
    await sleep(300);
    const closed = await c.evaluate(`({ hidden: document.querySelector('.jos-more-card').classList.contains('jos-more-hidden'), y: scrollY, focus: document.activeElement?.className, st: window.__josState.moreOpen })`);
    if (!closed.hidden) fail(`${cue}: Esc 沒關小卡`);
    if (closed.y !== before) fail(`${cue}: 關小卡後 scrollY ${before}->${closed.y}`);
    if (!/jos-more-btn/.test(closed.focus ?? '')) fail(`${cue}: 焦點沒回到更多鈕（${closed.focus}）`);
    await c.click(btn.x, btn.y);
    await sleep(150);
    const cross = await c.evaluate(`(() => { const r=document.querySelector('.jos-more-close').getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]; })()`);
    await c.click(...cross);
    await sleep(150);
    const crossClosed = await c.evaluate(`({hidden:document.querySelector('.jos-more-card').classList.contains('jos-more-hidden'),y:scrollY,focus:document.activeElement?.className})`);
    if (!crossClosed.hidden || crossClosed.y !== before || !/jos-more-btn/.test(crossClosed.focus ?? '')) fail(`${cue}: × 關閉、scrollY 或焦點返回失敗`);
    report.checks.push({ cue, more: { before, open, closed, crossClosed } });
    console.log('more', cue, JSON.stringify({ before, openY: open.y, closed }));
  }

  // 第二幕開關在小卡裡打開，經文變淡
  await goto('beyond-river', 0.3);
  {
    const b = await c.evaluate(`(() => { const x = document.querySelector('.jos-panel-on .jos-more-btn').getBoundingClientRect(); return { x: x.left + x.width / 2, y: x.top + x.height / 2 }; })()`);
    await c.click(b.x, b.y);
    await sleep(400);
    const t = await c.evaluate(`(() => { const t = document.querySelector('.jos-more-card [data-coach="only-i-btn"]'); const r = t.getBoundingClientRect(); const e = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); return { x: r.left + r.width / 2, y: r.top + r.height / 2, hit: e && (e.className + '|' + e.tagName), open: window.__josState.moreOpen, before: window.__josState.onlyI }; })()`);
    console.log('toggle target', JSON.stringify(t));
    await c.click(t.x, t.y);
    await sleep(500);
    const st = await c.evaluate('({ onlyI: window.__josState.onlyI, dim: document.querySelectorAll(".jos-panel-on .jos-verse-dim").length, y: scrollY })');
    if (!st.onlyI) fail('小卡裡的只看我開關沒作用');
    await c.shot(resolve(out, `06-${device.name}-beyond-river-more-onlyI.png`));
    report.shots.push(`06-${device.name}-beyond-river-more-onlyI.png`);
    await c.send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 });
    await c.send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 });
    await sleep(300);
    // 關回去，避免影響後續
    await c.evaluate('window.__josState.onlyI = false');
    report.checks.push({ onlyIToggle: st });
  }

  // 經文框內捲動：滾輪在框內只捲框，不帶動頁面
  for (const cue of ['answer-1', 'egypt', 'my-house', 'the-stone']) {
    await goto(cue, 0.3);
    const r = await c.evaluate(`(() => { const e = document.querySelector('.jos-panel-on .jos-vbox-verse'); const b = e.getBoundingClientRect(); return { x: b.left + b.width / 2, y: b.top + 40, y0: scrollY, can: e.scrollHeight > e.clientHeight + 1 }; })()`);
    await c.wheel(120, r.x, r.y);
    await sleep(250);
    const after = await c.evaluate(`({ y: scrollY, st: document.querySelector('.jos-panel-on .jos-vbox-verse').scrollTop })`);
    report.checks.push({ cue, verseWheel: { before: r.y0, after } });
    if (after.y !== r.y0) fail(`${cue}: 經文框內滾輪帶動頁面 ${r.y0}->${after.y}`);
    if (r.can && after.st <= 0) fail(`${cue}: 經文框內滾輪沒有捲動框`);
    await c.evaluate("document.querySelector('.jos-panel-on .jos-vbox-verse').scrollTop=1e6");
    await c.wheel(160, r.x, r.y);
    await sleep(150);
    const bottomY = await c.evaluate('scrollY');
    if (bottomY !== r.y0) fail(`${cue}: 經文到底後滾輪帶動頁面`);
    report.checks.push({ cue, verseBoundary: { canScroll: r.can, before: r.y0, bottomY } });
    console.log('verse wheel', cue, JSON.stringify(after), r.y0);
  }

  // 新手教學第 2 段：真的打開「更多」、真的打開開關才會往下走
  {
    const coachInfo = () => c.evaluate(`({ vis: !document.querySelector('.jos-coach-bar').classList.contains('jos-coach-hidden'), stage: document.querySelector('.jos-coach-stage')?.textContent, prompt: document.querySelector('.jos-coach-prompt')?.textContent, noteShown: getComputedStyle(document.querySelector('.jos-coach-note')).display !== 'none', nextShown: getComputedStyle(document.querySelector('.jos-coach-actions .jos-primary-btn')).display !== 'none', pulse: document.querySelector('.jos-coach-pulse')?.textContent ?? null })`);
    const nextClick = async () => {
      const p = await c.evaluate(`(() => { const b = document.querySelector('.jos-coach-actions .jos-primary-btn'); const r = b.getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; })()`);
      await c.click(p.x, p.y);
      await sleep(300);
    };
    await goto('prologue', 0.05);
    await c.evaluate("document.querySelector('.jos-coach-trigger').click()");
    await sleep(300);
    let info = await coachInfo();
    report.checks.push({ coach: 'open', info });
    // 第 1 段：捲動 → 目錄/第五幕 → 立石
    await goto('gather', 0.3);
    await sleep(300);
    info = await coachInfo();
    if (!info.nextShown) fail('教學 1-1 往下捲後沒有出現下一步');
    await nextClick();
    await goto('raise', 0.3);
    await sleep(300);
    info = await coachInfo();
    if (!info.nextShown) fail('教學 1-2 到第五幕後沒有出現下一步');
    await nextClick();
    // 1-3：按住立石
    const hp = await c.evaluate(`(() => { const b = document.querySelector('.jos-panel-on [data-coach="raise-btn"]'); const r = b.getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; })()`);
    await c.send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: hp.x, y: hp.y });
    await c.send('Input.dispatchMouseEvent', { type: 'mousePressed', x: hp.x, y: hp.y, button: 'left', clickCount: 1 });
    await sleep(2600);
    await c.send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: hp.x, y: hp.y, button: 'left', clickCount: 1 });
    await sleep(400);
    info = await coachInfo();
    if (!info.nextShown) fail('教學 1-3 立石後沒有出現下一步');
    await nextClick(); // → 小結
    // 先前已開的小卡不算完成第 2 段的操作。
    await goto('beyond-river', 0.3);
    await c.evaluate("document.querySelector('.jos-panel-on .jos-more-btn').click()");
    await nextClick(); // → 第 2 段步驟 1
    info = await coachInfo();
    report.checks.push({ coach: 'stage2-step1', info });
    if (!/更多/.test(info.prompt ?? '')) fail('教學第 2 段第 1 步提示沒有提到更多：' + info.prompt);
    if (info.nextShown) fail('教學 2-1 還沒點更多就顯示可以下一步');
    await c.evaluate("document.querySelector('.jos-more-close').click()");
    // 到第二幕點更多
    await goto('beyond-river', 0.3);
    info = await coachInfo();
    if (info.nextShown) fail('教學 2-1 只是捲到第二幕就算完成');
    if (!info.pulse || !/更多/.test(info.pulse)) fail('教學 2-1 沒有標出更多鈕：' + info.pulse);
    const mp = await c.evaluate(`(() => { const b = document.querySelector('.jos-panel-on .jos-more-btn'); const r = b.getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; })()`);
    await c.click(mp.x, mp.y);
    await sleep(400);
    info = await coachInfo();
    if (!info.nextShown) fail('教學 2-1 點開更多後沒有出現下一步');
    await c.evaluate("document.querySelector('.jos-more-card [data-coach=\"only-i-btn\"]').click()");
    await nextClick();
    info = await coachInfo();
    report.checks.push({ coach: 'stage2-step2', info });
    if (info.nextShown) fail('教學 2-2 把先前已開的開關算成完成');
    if (!info.pulse || !/只留下神說/.test(info.pulse)) fail('教學 2-2 沒有標出開關：' + info.pulse);
    const tp = await c.evaluate(`(() => { const b = document.querySelector('.jos-more-card [data-coach="only-i-btn"]'); const r = b.getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; })()`);
    await c.click(tp.x, tp.y); // 已開的先關掉，仍不能算完成
    await sleep(200);
    if ((await coachInfo()).nextShown) fail('教學 2-2 關閉開關就算完成');
    await c.click(tp.x, tp.y);
    await sleep(400);
    info = await coachInfo();
    if (!info.nextShown) fail('教學 2-2 打開開關後沒有出現下一步');
    await c.shot(resolve(out, `coach-${device.name}-stage2-step2-done.png`));
    report.shots.push(`coach-${device.name}-stage2-step2-done.png`);
    await nextClick();
    info = await coachInfo();
    report.checks.push({ coach: 'stage2-summary', info });
    if (!/小結/.test(info.stage ?? '')) fail('教學第 2 段沒有進到小結：' + info.stage);
    console.log('coach ok', JSON.stringify(info));
  }

  if (doAll) {
    await c.evaluate("document.querySelector('.jos-coach-top .jos-peek-close').click();document.querySelector('.jos-more-close').click()");
    for (const b of beats) {
      for (const p of b.familyLines ? [0.1, 0.3, 0.55, 0.8, 0.95] : [0.3, 0.9]) {
        await goto(b.cue, p);
        const m = await measureCommon(`${b.cue}@${p}`);
        if (b.note && p === 0.3 && (!m.verse || m.note)) fail(`${b.cue}: 前段不是經文`);
        if (b.note && p === 0.9 && (!m.note || m.verse)) fail(`${b.cue}: 後段不是短註`);
        report.checks.push({ cue: b.cue, p, all: true, verse: m.verse && { w: Math.round(m.verse.w), h: Math.round(m.verse.h), lines: m.verse.lines, scrollable: m.verse.scrollable }, bubble: m.bubble && { docked: m.bubble.docked, lines: m.bubble.lines } });
      }
    }
  }
  report.errors = c.consoleLog.filter((l) => /^\[(error|exception)\]/.test(l));
  if (hash('dist/index.html') !== report.buildSha256) fail('截圖期間建置檔改變');
  if (report.errors.length) fail('瀏覽器錯誤：' + report.errors.join(' | '));
} finally {
  writeFileSync(resolve(out, `report-${device.name}.json`), JSON.stringify(report, null, 2));
  clearInterval(keepAlive);
  await c.close();
}
console.log('failures:', report.failures.length);
process.exit(report.failures.length ? 1 : 0);
