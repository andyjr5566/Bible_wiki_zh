// 配樂進出點驗收：逐段捲到指定位置，記錄每首曲子的實際音量（含紅海驟停、約但河停一屏、第四幕疊上來、立石安靜）。
import { launch, sleep } from './cdp.mjs';
import { siteUrl } from './site-server.mjs';
const c = await launch({ width: 1440, height: 900, dpr: 1, port: 9491 });
const ka = setInterval(() => {}, 1000);
const names = ['ruins', 'plains', 'epic', 'pursuit', 'waiting', 'expansion', 'firstlight', 'hope'];
try {
  await c.send('Page.addScriptToEvaluateOnNewDocument', { source: `(()=>{const N=window.Audio;window.__auds=[];window.Audio=function(src){const a=new N(src);a.__src=String(src);window.__auds.push(a);return a};window.Audio.prototype=N.prototype})()` });
  await c.send('Page.navigate', { url: siteUrl });
  for (let i = 0; i < 60; i++) { if (await c.evaluate('!!window.__josState')) break; await sleep(500); }
  await sleep(1500);
  for (const type of ['mousePressed', 'mouseReleased']) await c.send('Input.dispatchMouseEvent', { type, x: 700, y: 450, button: 'left', clickCount: 1 });
  await sleep(800);
  const go = async (id, f, wait = 2500) => {
    await c.evaluate(`(()=>{const e=document.querySelector('section[data-beat-id="${id}"]');const r=e.getBoundingClientRect();scrollTo({top:scrollY+r.top-innerHeight*.36+${f}*r.height,behavior:'instant'})})()`);
    await sleep(wait);
    return c.evaluate(`(()=>{const o={};for(const n of ${JSON.stringify(names)}){const a=window.__auds.find(a=>a.__src.includes('/'+n+'-'));if(a&&!a.paused&&(a.josLevel??a.volume)>0.004)o[n]=+(a.josLevel??a.volume).toFixed(3)+'@'+a.currentTime.toFixed(0)+'s'}return {beat:window.__josState.beat.slice(8),p:+window.__josState.beatProgress.toFixed(3),music:o}})()`);
  };
  const plan = [
    ['beat-02-gather', [.5]],
    ['beat-07-abraham', [.5]],
    ['beat-08-egypt', [.05, .15, .3, .4, .5, .55, .6, .65, .7, .78, .86, .95]],
    ['beat-09-east', [.3, .8]],
    ['beat-10-jericho', [.2, .5, .6, .66, .7, .75, .8, .9]],
    ['beat-11-gifts', [.7]],
    ['beat-13-now', [.5]],
    ['beat-17-answer-1', [.5]],
    ['beat-18-cannot', [.3]],
    ['beat-19-answer-2', [.2, .8]],
    ['beat-20-witness', [.5]],
    ['beat-22-answer-3', [.6]],
    ['beat-25-write', [.5]],
  ];
  for (const [id, fs] of plan) for (const f of fs) console.log(JSON.stringify(await go(id, f)));
  // 立石：按住到一半、立好、再捲到第27節
  console.log(JSON.stringify(await go('beat-26-raise', .4)));
  await c.evaluate(`window.__josState.raiseStone.progress=.6;scrollBy(0,1)`); await sleep(2000);
  console.log('按住到 0.6', JSON.stringify(await go('beat-26-raise', .41, 2000)));
  await c.evaluate(`window.__josState.raiseStone.progress=1;window.__josState.raiseStone.done=true;scrollBy(0,1)`); await sleep(2000);
  console.log('立好', JSON.stringify(await go('beat-26-raise', .42, 2000)));
  console.log(JSON.stringify(await go('beat-27-the-stone', .3, 6000)));
  console.log(JSON.stringify(await go('beat-30-joshua-dies', .5)));
} finally { clearInterval(ka); await c.close(); }
