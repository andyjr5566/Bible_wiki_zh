import { launch, sleep } from './cdp.mjs';
import { siteUrl } from './site-server.mjs';
const c = await launch({ width: 1440, height: 900, dpr: 1, port: 9488 });
const ka = setInterval(() => {}, 1000);
try {
  await c.send('Page.addScriptToEvaluateOnNewDocument', { source: `(()=>{const N=window.Audio;window.__auds=[];window.Audio=function(src){const a=new N(src);a.__src=String(src);window.__auds.push(a);return a};window.Audio.prototype=N.prototype})()` });
  await c.send('Page.navigate', { url: siteUrl });
  for (let i = 0; i < 60; i++) { if (await c.evaluate('!!window.__josState')) break; await sleep(500); }
  await sleep(1500);
  // 真實滑鼠點擊『聲音』按鈕（算使用者操作）
  const pos = await c.evaluate(`(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.textContent.includes('聲音'));const r=b.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()`);
  for (const type of ['mousePressed', 'mouseReleased']) await c.send('Input.dispatchMouseEvent', { type, x: pos.x, y: pos.y, button: 'left', clickCount: 1 });
  await sleep(800);
  const beats = ['beat-02-gather', 'beat-06-beyond-river', 'beat-08-egypt', 'beat-11-gifts', 'beat-13-now', 'beat-17-answer-1', 'beat-18-cannot', 'beat-23-family-4', 'beat-26-raise', 'beat-30-joshua-dies'];
  for (const id of beats) {
    await c.evaluate(`(()=>{const e=document.querySelector('section[data-beat-id="${id}"]');const r=e.getBoundingClientRect();scrollTo({top:scrollY+r.top-innerHeight*.36+.35*(r.height-innerHeight*.35),behavior:'instant'})})()`);
    await sleep(id === 'beat-18-cannot' ? 3000 : 7000);
    const st = await c.evaluate(`(()=>({sound:window.__josState.soundOn,cue:window.__josState.cue,music:window.__auds.filter(a=>/(ruins|plains|laments|hope|choir)-/.test(a.__src)).map(a=>a.__src.split('/').pop().split('-')[0]+':'+a.volume.toFixed(2)+(a.paused?'(paused)':'(playing)'))}))()`);
    console.log(id.padEnd(24), JSON.stringify(st));
  }
} finally { clearInterval(ka); await c.close(); }
