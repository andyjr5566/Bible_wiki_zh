// 聲音會不會越疊越多：從頭走過故事每一拍，記錄同時在播的聲音與實際音量。
// IOS=1 模擬 iPhone Safari：<audio> 的 volume 設了無效、讀回來永遠是 1（2026-10-28 使用者在 iPhone 上聽到雜音一直疊、很大聲）。
// 經 Web Audio 音量節點播放的聲音，實際音量是 josLevel；直接用 <audio> 的，在 iPhone 上一律是 1。
import { launch, sleep } from './cdp.mjs';
import { siteUrl } from './site-server.mjs';
const c = await launch({ width: 1440, height: 900, dpr: 1, port: 9516 });
const ka = setInterval(() => {}, 1000);
try {
  await c.send('Page.addScriptToEvaluateOnNewDocument', { source: `(()=>{const N=window.Audio;window.__auds=[];window.Audio=function(src){const a=new N(src);a.__src=String(src);window.__auds.push(a);return a};window.Audio.prototype=N.prototype;
    ${process.env.IOS === '1' ? `Object.defineProperty(HTMLMediaElement.prototype,'volume',{configurable:true,get(){return 1},set(){}});` : ''}})()` });
  await c.send('Page.navigate', { url: siteUrl });
  for (let i = 0; i < 60; i++) { if (await c.evaluate('!!window.__josState')) break; await sleep(500); }
  await sleep(1500);
  for (const type of ['mousePressed', 'mouseReleased']) await c.send('Input.dispatchMouseEvent', { type, x: 700, y: 450, button: 'left', clickCount: 1 });
  await sleep(800);
  const ids = await c.evaluate(`[...document.querySelectorAll('section[data-beat-id]')].map(e=>e.dataset.beatId)`);
  let worst = { n: 0 };
  for (const id of ids) {
    await c.evaluate(`(()=>{const e=document.querySelector('section[data-beat-id="${id}"]');const r=e.getBoundingClientRect();scrollTo({top:scrollY+r.top-innerHeight*.36+.5*r.height,behavior:'instant'})})()`);
    await sleep(Number(process.env.WAIT ?? 2500));
    const v = await c.evaluate(`(()=>{const on=window.__auds.filter(a=>!a.paused&&!a.ended);
      const lv=a=>a.josLevel??a.volume;
      return {n:on.length,sum:+on.reduce((s,a)=>s+lv(a),0).toFixed(2),list:on.map(a=>a.__src.split('/').pop().replace(/-[\\w-]{8}\\.mp3$/,'')+'='+lv(a).toFixed(2)).join(' ')}})()`);
    if (v.n > worst.n) worst = { ...v, id };
    console.log(id.padEnd(26), String(v.n).padStart(2), '個在播  實際音量合計', String(v.sum).padStart(5), ' ', v.list);
  }
  console.log('最多同時在播', worst.n, '個（', worst.id, '）');
} finally { clearInterval(ka); await c.close(); }
