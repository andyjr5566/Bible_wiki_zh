// 第二幕逐段取樣：每個位置各環境音（含水聲）的實際音量。
import { launch, sleep } from './cdp.mjs';
import { siteUrl } from './site-server.mjs';
const c = await launch({ width: 1440, height: 900, dpr: 1, port: 9489 });
const ka = setInterval(() => {}, 1000);
try {
  await c.send('Page.addScriptToEvaluateOnNewDocument', { source: `(()=>{const N=window.Audio;window.__auds=[];window.Audio=function(src){const a=new N(src);a.__src=String(src);window.__auds.push(a);return a};window.Audio.prototype=N.prototype})()` });
  await c.send('Page.navigate', { url: siteUrl });
  for (let i = 0; i < 60; i++) { if (await c.evaluate('!!window.__josState')) break; await sleep(500); }
  await sleep(1500);
  for (const type of ['mousePressed', 'mouseReleased']) await c.send('Input.dispatchMouseEvent', { type, x: 700, y: 450, button: 'left', clickCount: 1 });
  await sleep(800);
  const beats = ['beat-06-beyond-river', 'beat-07-abraham', 'beat-08-egypt', 'beat-09-east', 'beat-10-jericho', 'beat-11-gifts'];
  const names = ['river', 'sea-roar', 'desert-wind', 'valley-wind', 'oak-leaves', 'crowd-murmur'];
  for (const id of beats) {
    for (const f of [0.03, 0.12, 0.22, 0.34, 0.46, 0.58, 0.7, 0.82, 0.94]) {
      await c.evaluate(`(()=>{const e=document.querySelector('section[data-beat-id="${id}"]');const r=e.getBoundingClientRect();scrollTo({top:scrollY+r.top-innerHeight*.36+${f}*r.height,behavior:'instant'})})()`);
      await sleep(1600);
      const v = await c.evaluate(`(()=>{const o={};for(const n of ${JSON.stringify(names)}){const a=window.__auds.find(a=>a.__src.includes('/'+n+'-'));o[n]=a?(a.paused?0:+a.volume.toFixed(2)):0}return {beat:window.__josState.beat.slice(8),p:+window.__josState.beatProgress.toFixed(2),...o}})()`);
      console.log(JSON.stringify(v));
    }
  }
} finally { clearInterval(ka); await c.close(); }
