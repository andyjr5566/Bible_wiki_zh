// 3D 畫布的繪製尺寸是否跟畫面上實際的大小一致：不一致時畫面會被拉伸、變糊，繪畫後製的筆觸變成一道道錯開的重影。
// 模擬 iPhone：先直拿開頁、再轉成橫擺（也可 START=landscape 直接橫擺開），每一步記錄畫布緩衝區與顯示大小。
import { launch, sleep } from './cdp.mjs';
import { siteUrl } from './site-server.mjs';
const OUT = process.argv[2];
const P = [430, 932], L = [932, 430];
const start = process.env.START === 'landscape' ? L : P;
const c = await launch({ width: start[0], height: start[1], mobile: true, dpr: 3, port: 9511 });
const ka = setInterval(() => {}, 1000);
// NO_RESIZE=1：網頁收不到 window 的 resize 事件（模擬 iPhone 轉向時事件帶舊尺寸、之後不再補送）
if (process.env.NO_RESIZE === '1') await c.send('Page.addScriptToEvaluateOnNewDocument', { source: `(() => {
  const add = window.addEventListener.bind(window);
  window.addEventListener = (type, fn, opt) => type === 'resize' ? undefined : add(type, fn, opt); })();` });
const report = async (label) => {
  const r = await c.evaluate(`(()=>{const cv=document.getElementById('jos-canvas');const b=cv.getBoundingClientRect();
    return {buf:[cv.width,cv.height],css:[Math.round(b.width),Math.round(b.height)],inner:[innerWidth,innerHeight],dpr:devicePixelRatio,
      bufAspect:+(cv.width/cv.height).toFixed(3),cssAspect:+(b.width/b.height).toFixed(3)}})()`);
  console.log(label.padEnd(22), JSON.stringify(r), r.bufAspect !== r.cssAspect ? '  <-- 比例不一致' : '');
};
try {
  await c.send('Page.navigate', { url: siteUrl });
  for (let i = 0; i < 60; i++) { if (await c.evaluate('!!window.__josState')) break; await sleep(500); }
  await sleep(2500);
  await report(start === P ? '直拿開頁' : '橫擺開頁');
  if (start === P) {
    // iOS 轉向時常先送出舊尺寸的 resize，再改版面；這裡只改尺寸、不另外觸發 resize
    await c.send('Emulation.setDeviceMetricsOverride', { width: L[0], height: L[1], deviceScaleFactor: 3, mobile: true,
      screenOrientation: { type: 'landscapePrimary', angle: 90 } });
    await sleep(1500);
    await report('轉成橫擺');
  }
  await c.evaluate(`(()=>{const e=document.querySelector('section[data-beat-id*="family-4"]');scrollTo({top:scrollY+e.getBoundingClientRect().top,behavior:'instant'})})()`);
  await sleep(2500);
  await report('第四幕對話拍');
  if (OUT) await c.shot(OUT);
} finally { clearInterval(ka); await c.close(); }
