import { siteUrl } from './site-server.mjs';
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';
import { launch, sleep } from './cdp.mjs';
import { primaryRefOf } from '../src/data/story-content.mjs';

export async function waitForStory(c) {
  let ready=false;
  for(let i=0;i<200;i++){
    ready=await c.evaluate(`Boolean(window.__josState&&document.getElementById('jos-beat-beat-36-epilogue-stone'))`);
    if(ready)break;
    await sleep(100);
  }
  if(!ready)throw new Error('Story did not mount before the browser check');
  await c.evaluate('document.fonts.ready.then(()=>true)');await sleep(300);
}
export async function sampleNote(c) {
  return c.evaluate(`(()=>{const p=document.querySelector('.jos-panel-on'),v=p.querySelector('.jos-vbox-verse'),n=p.querySelector('.jos-vbox-note');
    return {beat:window.__josState.beat,p:window.__josState.beatProgress,hasVerse:!!v,verse:v?+getComputedStyle(v).opacity:0,note:n?+getComputedStyle(n).opacity:0}})()`);
}
export function notePasses(sample, beat) {
  return !!sample && sample.beat === beat.id && Math.abs(sample.p-.90)<.001
    && sample.hasVerse === Boolean(primaryRefOf(beat)) && sample.verse === 0 && sample.note > 0;
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  const out=resolve('.tmp-shots/storyteller/report.json');
  const report=JSON.parse(readFileSync(out,'utf8'));
  const sha256=createHash('sha256').update(readFileSync('dist/index.html')).digest('hex');
  if(sha256!==report.sha256)throw new Error('Build differs from the frozen screenshot run');
  const site=JSON.parse(readFileSync('src/data/site.json','utf8'));
  const checks=[],failures=[];
  const keepAlive=setInterval(()=>{},1000);
  const c=await launch({port:9471,gpu:true});
  try {
    await c.send('Page.navigate',{url:siteUrl});
    await waitForStory(c);
    for(const [device,width,height] of [['desktop',1440,900],['mobile',844,390]]){
      await c.send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:device==='mobile'});
      for(const beat of site.segments.flatMap(s=>s.beats).filter(b=>b.note)){
        await c.evaluate(`(()=>{const e=document.getElementById('jos-beat-${beat.id}');scrollTo({top:scrollY+e.getBoundingClientRect().top-innerHeight*.36+.90*e.offsetHeight,behavior:'instant'})})()`);
        for(let i=0;i<100;i++){
          if(await c.evaluate(`window.__josState.beat==='${beat.id}'&&Math.abs(window.__josState.beatProgress-.90)<.0005`))break;
          await sleep(60);
        }
        const sample=await sampleNote(c);
        checks.push({device,id:beat.id,...sample});
        if(!notePasses(sample,beat))failures.push(device+': note handoff '+beat.id);
      }
    }
    const previous=report.failures.filter(f=>f.includes(': note handoff '));
    const history=report.noteCheckHistory??[];
    if(report.noteCheckCorrection)history.push(report.noteCheckCorrection);
    report.noteCheckHistory=history;
    report.noteCheckCorrection={reason:'The coda intentionally has a note and no verse box; check for absence explicitly. Wait for the measured scroll progress before sampling.',sha256,previous,checks};
    report.notes=checks;
    report.failures=[...report.failures.filter(f=>!f.includes(': note handoff ')),...failures];
    writeFileSync(out,JSON.stringify(report,null,2));
    console.log(JSON.stringify({checks:checks.length,failures:report.failures}));
    if(report.failures.length)process.exitCode=1;
  } finally { await c.close();clearInterval(keepAlive); }
}
