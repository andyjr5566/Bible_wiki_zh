import { siteUrl } from './site-server.mjs';
import { mkdirSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { launch, sleep } from './cdp.mjs';
const out=resolve('.tmp-shots/storyteller'); mkdirSync(out,{recursive:true});
const keepAlive=setInterval(()=>{},1000);
const c=await launch({port:9471,gpu:true});
const report={devices:[],bubble:[]};
try {
  await c.send('Page.navigate',{url:siteUrl});
  await sleep(3500);
  for(const [width,height] of [[1440,900],[844,390]]){
    await c.send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:height===390});
    await sleep(500);
    report.devices.push({width,height,beats:await c.evaluate(`Array.from(document.querySelectorAll('section[data-beat-id]')).map(e=>({id:e.dataset.beatId,cue:e.dataset.cue,height:e.getBoundingClientRect().height,progressSpan:e.getBoundingClientRect().height-innerHeight*.35}))`)});
    await c.evaluate(`(()=>{const e=document.querySelector('section[data-cue="family-2"]');scrollTo(0,scrollY+e.getBoundingClientRect().top-innerHeight*.36+.2*(e.offsetHeight-innerHeight*.35))})()`);
    await sleep(1800);
    report.bubble.push({width,height,samples:await c.evaluate(`new Promise(resolve=>{const a=[];const start=performance.now();function f(){const e=document.querySelector('.jos-panel-on .jos-bubble');const r=e.getBoundingClientRect();a.push({t:performance.now()-start,x:r.x,y:r.y,docked:e.classList.contains('jos-bubble-docked')});if(performance.now()-start<2000)requestAnimationFrame(f);else resolve(a)}f()})`)});
  }
  await c.send('Emulation.setDeviceMetricsOverride',{width:1440,height:900,deviceScaleFactor:1,mobile:false});
  for(const cue of ['gather','leaders','my-house','put-away','raise','joshua-dies','bones','eleazar']){
    for(const delta of [-50,50]){
      await c.evaluate(`(()=>{const e=document.querySelector('section[data-cue="${cue}"]');scrollTo(0,scrollY+e.getBoundingClientRect().top-innerHeight*.36+${delta})})()`);
      await sleep(450); await c.shot(resolve(out,`before-${cue}-${delta}.png`));
    }
  }
  writeFileSync(resolve(out,'before.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify({devices:report.devices.map(d=>[d.width,d.height,d.beats.length]),bubble:report.bubble.map(d=>({width:d.width,dx:Math.max(...d.samples.map(s=>s.x))-Math.min(...d.samples.map(s=>s.x)),dy:Math.max(...d.samples.map(s=>s.y))-Math.min(...d.samples.map(s=>s.y))}))}));
}finally{await c.close();clearInterval(keepAlive)}
