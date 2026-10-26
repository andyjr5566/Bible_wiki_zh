import { siteUrl } from './site-server.mjs';
// 第 1 階段畫面與橫向不溢出驗證：由本機伺服器開啟 dist 並輸出截圖。
import { mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { launch, sleep } from './cdp.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const PROJECT_DIR = resolve(here, '..');
const DIST_HTML = resolve(PROJECT_DIR, 'dist/index.html');
const OUT_DIR = process.argv[2] ?? resolve(PROJECT_DIR, '.tmp-shots');

mkdirSync(OUT_DIR, { recursive: true });
const url = siteUrl;

// 1. 桌機 1440x900
const desktop = await launch({ width: 1440, height: 900, port: 9344 });
try {
  await desktop.send('Page.navigate', { url });
  await sleep(1200);
  const deskDims = await desktop.evaluate(
    '[window.innerWidth, document.documentElement.scrollWidth, document.querySelectorAll("[data-beat-id]").length]',
  );
  console.log('Desktop dims & beats:', deskDims);
  await desktop.shot(resolve(OUT_DIR, 'phase1-desktop-hero.png'));

  // 跳至第二幕並開啟「只留下神說『我』的地方」
  await desktop.evaluate(`(() => {
    const seg2 = document.getElementById('jos-seg-act-2');
    if (seg2) window.scrollTo({ top: seg2.getBoundingClientRect().top + window.scrollY - 72 });
    const btn = seg2?.querySelector('.jos-toggle-pill');
    if (btn) btn.click();
  })()`);
  await sleep(500);
  await desktop.shot(resolve(OUT_DIR, 'phase1-desktop-act2-onlyi.png'));

  // 跳至終幕平行經文比對並切深色
  await desktop.evaluate(`(() => {
    const diffBeat = document.getElementById('jos-beat-beat-35-epilogue-diff');
    if (diffBeat) window.scrollTo({ top: diffBeat.getBoundingClientRect().top + window.scrollY - 72 });
    const btns = Array.from(document.querySelectorAll('.jos-tool-btn'));
    const darkBtn = btns.find((b) => b.textContent?.includes('深色'));
    if (darkBtn) darkBtn.click();
  })()`);
  await sleep(500);
  await desktop.shot(resolve(OUT_DIR, 'phase1-desktop-epilogue-dark.png'));

  const errors = desktop.consoleLog.filter(
    (l) => l.startsWith('[error]') || l.startsWith('[exception]'),
  );
  console.log('Desktop console errors:', errors.length, errors);
  if (errors.length > 0) process.exitCode = 1;
} finally {
  await desktop.close();
}

// 2. 手機 390x844（檢查橫向零溢出）
const mobile = await launch({ width: 390, height: 844, mobile: true, dpr: 2, port: 9345 });
try {
  await mobile.send('Page.navigate', { url });
  await sleep(1200);
  const mobDims = await mobile.evaluate(
    '[window.innerWidth, document.documentElement.scrollWidth]',
  );
  console.log('Mobile [innerWidth, scrollWidth]:', mobDims);
  await mobile.shot(resolve(OUT_DIR, 'phase1-mobile-390.png'));

  // 捲動到 02 示劍的每一次與 06 各家怎麼讀，確認整頁無橫向溢出
  await mobile.evaluate(`(() => {
    const sec02 = document.getElementById('jos-sec-02');
    const hdrH = document.querySelector('.jos-header')?.getBoundingClientRect().height ?? 56;
    if (sec02) window.scrollTo({ top: sec02.getBoundingClientRect().top + window.scrollY - hdrH - 12 });
  })()`);
  await sleep(400);
  const mobDimsMid = await mobile.evaluate(
    '[window.innerWidth, document.documentElement.scrollWidth]',
  );
  console.log('Mobile mid [innerWidth, scrollWidth]:', mobDimsMid);
  await mobile.shot(resolve(OUT_DIR, 'phase1-mobile-sec02.png'));

  if (mobDims[0] !== 390 || mobDims[1] !== 390 || mobDimsMid[1] !== 390) {
    console.error('手機版發生橫向溢出！', mobDims, mobDimsMid);
    process.exitCode = 1;
  }
  const errors = mobile.consoleLog.filter(
    (l) => l.startsWith('[error]') || l.startsWith('[exception]'),
  );
  console.log('Mobile console errors:', errors.length, errors);
  if (errors.length > 0) process.exitCode = 1;
} finally {
  await mobile.close();
}
