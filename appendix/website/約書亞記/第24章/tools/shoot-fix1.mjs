import { siteUrl } from './site-server.mjs';
import assert from 'node:assert/strict';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';
import { sleep } from './cdp.mjs';

const baseline = process.argv[2] === 'baseline';
const out = resolve('.tmp-shots/fix1', baseline ? 'before' : '.');
mkdirSync(out, { recursive: true });
const data = JSON.parse(readFileSync('src/data/site.json', 'utf8'));
const beats = data.segments.flatMap(s => s.beats);
const hash = path => createHash('sha256').update(readFileSync(path)).digest('hex');
const report = { created: new Date().toISOString(), engine: 'Chrome / CDP emulation', buildSha256: hash('dist/index.html'), dataSha256: hash('src/data/site.json'), devices: [], failures: [] };
const keepAlive = setInterval(() => {}, 1000);

// PowerShell owns these two browsers and their profiles inside this site.
async function connect(options) {
  let target;
  for (let i=0;i<40;i++) {
    try {
      const targets=await(await fetch(`http://127.0.0.1:${options.port}/json`, {signal:AbortSignal.timeout(1000)})).json();
      target=targets.find(t=>t.type==='page');
      if(target) break;
    } catch {}
    await sleep(250);
  }
  assert(target, 'Chrome did not start');
  const ws=new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve,reject)=>{ws.addEventListener('open',resolve,{once:true});ws.addEventListener('error',reject,{once:true});});
  let id=0;
  const pending=new Map(), consoleLog=[];
  ws.addEventListener('message', event=>{
    const message=JSON.parse(event.data);
    if(pending.has(message.id)) {
      const p=pending.get(message.id);pending.delete(message.id);clearTimeout(p.timer);
      message.error?p.reject(new Error(JSON.stringify(message.error))):p.resolve(message.result);
    } else if(message.method==='Runtime.exceptionThrown') consoleLog.push('[exception] '+JSON.stringify(message.params.exceptionDetails));
    else if(message.method==='Runtime.consoleAPICalled'&&message.params.type==='error') consoleLog.push('[error] '+JSON.stringify(message.params.args));
  });
  const send=(method,params={})=>new Promise((resolve,reject)=>{
    const key=++id;
    const timer=setTimeout(()=>{pending.delete(key);reject(new Error('CDP timeout: '+method));},15000);
    pending.set(key,{resolve,reject,timer});ws.send(JSON.stringify({id:key,method,params}));
  });
  await send('Page.enable');await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride',{width:options.width,height:options.height,deviceScaleFactor:options.dpr??1,mobile:options.mobile??false});
  if(options.mobile) await send('Emulation.setTouchEmulationEnabled',{enabled:true,maxTouchPoints:5});
  return {
    send,consoleLog,
    async evaluate(expression) {
      const result=await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});
      if(result.exceptionDetails) throw new Error(result.exceptionDetails.exception?.description??result.exceptionDetails.text);
      return result.result.value;
    },
    async shot(file) {const {data}=await send('Page.captureScreenshot',{format:'png'});writeFileSync(file,Buffer.from(data,'base64'));},
    wheel(deltaY,x,y) {return send('Input.dispatchMouseEvent',{type:'mouseWheel',x,y,deltaX:0,deltaY});},
    async close() {await send('Browser.close');ws.close();},
  };
}

async function run(name, options) {
  console.log('Connecting', name, options.port);
  const c = await connect(options);
  console.log('Connected', name);
  const device = { name, viewport: [options.width, options.height], panels: [], screenshots: [], errors: [] };
  report.devices.push(device);
  const save = () => writeFileSync(resolve(out, 'acceptance.json'), JSON.stringify(report, null, 2));
  async function shot(file) {
    const dimensions = await c.evaluate('[innerWidth, document.documentElement.scrollWidth]');
    assert.equal(dimensions[0], dimensions[1], `${file}: horizontal overflow`);
    await c.shot(resolve(out, file));
    device.screenshots.push(file);
  }
  try {
    await c.send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: 'light' }, { name: 'prefers-reduced-motion', value: 'no-preference' }] });
    await c.send('Page.addScriptToEvaluateOnNewDocument', { source: "localStorage.setItem('jos-dark','0');localStorage.setItem('jos-motion-off','0');" });
    await c.send('Page.navigate', { url: siteUrl });
    for (let attempt=0;attempt<60;attempt++) {
      if (await c.evaluate('!!window.__josState && !!document.querySelector("[data-cue]")')) break;
      await sleep(500);
    }
    console.log('Loaded', name);
    console.log('Page', await c.evaluate('({url:location.href,beats:document.querySelectorAll("[data-cue]").length,state:!!window.__josState,text:document.body.textContent.slice(0,180)})'), c.consoleLog);
    for (const [i, beat] of beats.entries()) {
      if (baseline && !['gather','egypt','jericho','three-gods','answer-1','family-5','epilogue-diff'].includes(beat.cue)) continue;
      const selector = `[data-cue="${beat.cue}"]`;
      await c.evaluate(`(() => { const el=document.querySelector(${JSON.stringify(selector)}); window.scrollTo({top:scrollY+el.getBoundingClientRect().top+innerHeight*.1,behavior:'instant'}); })()`);
      await sleep(450);
      const active = await c.evaluate('window.__josState.cue');
      assert.equal(active, beat.cue);
      const prefix = `${String(i + 1).padStart(2,'0')}-${name}-${beat.cue}`;
      await shot(`${prefix}.png`);
      const measure = async () => c.evaluate(`(() => {
        const b=document.querySelector(${JSON.stringify(selector + ' .jos-box-body')}),box=b.parentElement,r=box.getBoundingClientRect();
        const last=b.lastElementChild.getBoundingClientRect();
        return {scrollHeight:b.scrollHeight,clientHeight:b.clientHeight,scrollTop:b.scrollTop,pageY:scrollY,top:r.top,bottom:r.bottom,bodyBottom:b.getBoundingClientRect().bottom,lastBottom:last.bottom,verseSizes:[...b.querySelectorAll('.jos-verse-box,.jos-diff-text')].map(el=>parseFloat(getComputedStyle(el).fontSize))};
      })()`);
      const panel = { cue: beat.cue, closed: await measure() };
      panel.labels = await c.evaluate(`(() => {
        const labels=[...document.querySelectorAll('.jos-stage-tag')].filter(el=>getComputedStyle(el).display!=='none').map(el=>{const r=el.getBoundingClientRect();return {text:el.textContent,left:r.left,right:r.right,top:r.top,bottom:r.bottom};});
        return {labels,overlaps:labels.flatMap((a,i)=>labels.slice(i+1).filter(b=>a.left<b.right&&a.right>b.left&&a.top<b.bottom&&a.bottom>b.top).map(b=>[a.text,b.text]))};
      })()`);
      device.panels.push(panel);
      await c.evaluate(`document.querySelectorAll(${JSON.stringify(selector + ' details')}).forEach(el=>el.open=true)`);
      await sleep(40);
      panel.expanded = await measure();
      const point = await c.evaluate(`(() => {const r=document.querySelector(${JSON.stringify(selector+' .jos-box-body')}).getBoundingClientRect();return [r.x+r.width/2,Math.min(innerHeight-16,r.y+60)];})()`);
      await c.wheel(160, ...point); await sleep(100);
      panel.afterWheel = await measure();
      await c.evaluate(`document.querySelector(${JSON.stringify(selector+' .jos-box-body')}).scrollTop=1e6`);
      await sleep(50);
      panel.atBottom = await measure();
      panel.scrollPass = panel.expanded.scrollHeight <= panel.expanded.clientHeight || panel.afterWheel.scrollTop > 0;
      panel.bottomReachable = panel.atBottom.lastBottom <= Math.min(options.height,panel.atBottom.bodyBottom) + 1;
      if (!baseline) {
        if (panel.labels.overlaps.length) report.failures.push(`${prefix}: labels overlap`);
        if (!panel.scrollPass) report.failures.push(`${prefix}: wheel did not scroll`);
        if (panel.afterWheel.pageY !== panel.expanded.pageY) report.failures.push(`${prefix}: wheel escaped to page`);
        if (panel.atBottom.bottom > options.height) report.failures.push(`${prefix}: panel clipped`);
        if (!panel.bottomReachable) report.failures.push(`${prefix}: tail inaccessible`);
        if (!panel.atBottom.verseSizes.every(size=>size>=15)) report.failures.push(`${prefix}: Scripture under 15px`);
      }
      if (beat.cue.startsWith('family-') || beat.cue==='epilogue-diff') await shot(`${prefix}-bottom.png`);
      if (beat.cue === 'epilogue-diff') {
        await c.evaluate(`(() => {const b=document.querySelector('[data-cue="epilogue-diff"] .jos-box-body'),last=b.querySelector('.jos-diff-unmatched');b.scrollTop+=last.getBoundingClientRect().bottom-b.getBoundingClientRect().bottom+8;})()`);
        await sleep(50);
        device.epilogue = await c.evaluate(`(() => {const b=document.querySelector('[data-cue="epilogue-diff"] .jos-box-body'), last=b.querySelector('.jos-diff-unmatched'),r=last.getBoundingClientRect();return {pairs:b.querySelectorAll('.jos-diff-pair').length+1,text:last.textContent,top:r.top,bottom:r.bottom,visible:r.top>=b.getBoundingClientRect().top&&r.bottom<=b.getBoundingClientRect().bottom};})()`);
        if (!baseline && !device.epilogue.visible) report.failures.push(`${prefix}: Judges 2:10 is clipped`);
        await shot(`${prefix}-judges-2-10.png`);
      }
      await c.evaluate(`document.querySelectorAll(${JSON.stringify(selector+' details')}).forEach(el=>el.open=false)`);
      save();
      console.log('Captured', prefix);
    }
    device.errors = c.consoleLog.filter(l => /^\[(error|exception)\]/.test(l));
    if (!baseline) assert.deepEqual(device.errors, []);
  } finally { save(); await c.close(); }
}
try {
  if (!baseline) await run('desktop', {width:1440,height:900,port:9394});
  await run('mobile', {width:844,height:390,mobile:true,dpr:2,port:9395});
  console.log(JSON.stringify(report.devices.map(d=>({name:d.name,panels:d.panels.length,screenshots:d.screenshots.length,errors:d.errors,epilogue:d.epilogue}))));
  assert.equal(hash('dist/index.html'), report.buildSha256, 'Build changed during capture');
  if (!baseline) assert.deepEqual(report.failures, []);
} finally { clearInterval(keepAlive); }
