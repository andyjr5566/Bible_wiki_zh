import { siteUrl } from './site-server.mjs';
import { mkdirSync, writeFileSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';
import { launch, sleep } from './cdp.mjs';
import { beatRhythm, primaryRefOf, storyLines, stationRhythm, validateStoryContent } from '../src/data/story-content.mjs';
import { waitForStory, sampleNote, notePasses } from './check-storyteller-notes.mjs';
const keepAlive=setInterval(()=>{},1000);
const out=resolve('.tmp-shots/storyteller'); mkdirSync(out,{recursive:true});
const report={sha256:createHash('sha256').update(readFileSync('dist/index.html')).digest('hex'),devices:[],shots:[],bubble:[],notes:[],autoplay:[],entrances:[],opacity:[],failures:[]};
const site=JSON.parse(readFileSync('src/data/site.json','utf8'));
const stations=JSON.parse(readFileSync('src/data/stations.json','utf8'));
const beats=site.segments.flatMap(s=>s.beats);
const stationLength=s=>800+stationRhythm(s,site).px;
// 舊版快照只作前後對照；當輪拍長必須對本輪正式資料，不沿用舊對話字數。
report.siteSha256=createHash('sha256').update(readFileSync('src/data/site.json')).digest('hex');
report.expectedRhythm=Object.fromEntries(beats.map(beat=>{
  const list=stations.filter(s=>s.beat===beat.id);
  return [beat.id,list.length?list.reduce((sum,s)=>sum+stationLength(s),0):beatRhythm(beat,site).px];
}));
report.contentGate=validateStoryContent(site,stations);
function stationProgress(id,p){
  const station=stations.find(s=>s.id===id), list=stations.filter(s=>s.beat===station.beat);
  return {id:station.beat,p:(list.slice(0,list.indexOf(station)).reduce((n,s)=>n+stationLength(s),0)+800+p*(stationLength(station)-800))/list.reduce((n,s)=>n+stationLength(s),0)};
}
const c=await launch({port:9471,gpu:true});
try{
  await c.send('Page.navigate',{url:siteUrl});
  await waitForStory(c);
  async function goto(id,p){
    await c.evaluate(`(()=>{const e=document.getElementById('jos-beat-${id}');scrollTo({top:scrollY+e.getBoundingClientRect().top-innerHeight*.36+${p}*e.offsetHeight,behavior:'instant'})})()`);
    for(let i=0;i<70;i++){
      if(await c.evaluate(`window.__josState.beat==='${id}'&&Math.abs(window.__josState.beatProgress-${p})<.0005`))break;
      await sleep(60);
    }
    await sleep(180);
  }
  async function capture(name){
    const info=await c.evaluate(`(()=>{
      const panel=document.querySelector('.jos-panel-on'),v=panel.querySelector('.jos-vbox-verse'),n=panel.querySelector('.jos-vbox-note');
      const rect=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}};
      const visible=e=>!!e&&getComputedStyle(e).visibility!=='hidden'&&+getComputedStyle(e).opacity>.005;
      const clippedRects=e=>[...e.getClientRects()].map(r=>{
        let x0=Math.max(0,r.left),y0=Math.max(0,r.top),x1=Math.min(innerWidth,r.right),y1=Math.min(innerHeight,r.bottom);
        for(let a=e.parentElement;a;a=a.parentElement){const s=getComputedStyle(a),c=a.getBoundingClientRect();
          if(s.overflowX!=='visible'){x0=Math.max(x0,c.left);x1=Math.min(x1,c.right)}
          if(s.overflowY!=='visible'){y0=Math.max(y0,c.top);y1=Math.min(y1,c.bottom)}}
        return {x:x0,y:y0,w:x1-x0,h:y1-y0};
      }).filter(r=>r.w>0&&r.h>0);
      return {beat:window.__josState.beat,p:window.__josState.beatProgress,font:v?getComputedStyle(v).fontFamily:null,fontSize:v?parseFloat(getComputedStyle(v).fontSize):null,verse:visible(v),note:visible(n),overflow:document.documentElement.scrollWidth-innerWidth,
        tone:panel.dataset.verseTone,verseOpacity:v?+getComputedStyle(v).opacity:0,
        rects:[...(v&&visible(v)&&+getComputedStyle(v).opacity>.995?[...v.querySelectorAll('.jos-story-char,.jos-story-ref')].filter(e=>visible(e)&&+getComputedStyle(e).opacity>.995):[]),
          ...panel.querySelectorAll('.jos-diff-text,.jos-diff-hl,.jos-cannot-headline')].filter(visible).map(e=>({color:getComputedStyle(e).color,fontSize:parseFloat(getComputedStyle(e).fontSize),rects:clippedRects(e)})),
        visibleSentences:v?[...v.querySelectorAll('.jos-story-sentence')].filter(e=>visible(e)&&e.getClientRects().length&&[...e.querySelectorAll('.jos-story-char')].some(c=>+getComputedStyle(c).opacity>.05)).map(e=>e.textContent):[],
        bodies:window.__josScene?.getBodyBoxes()??[]};})()`);
    if(info.verse&&info.note) report.failures.push(name+': note overlaps verse');
    if(info.overflow>0) report.failures.push(name+': overflow '+info.overflow);
    if(info.fontSize&&info.fontSize<18) report.failures.push(name+': font too small');
    await c.shot(resolve(out,name+'.png'));
    if(info.rects.length){
      await c.evaluate(`(()=>{const s=document.createElement('style');s.id='jos-contrast-probe';s.textContent='.jos-panel-on :is(.jos-story-char,.jos-story-ref,.jos-diff-text,.jos-cannot-headline),.jos-panel-on :is(.jos-story-char,.jos-story-ref,.jos-diff-text,.jos-cannot-headline) *{color:transparent!important;text-shadow:none!important;text-decoration-color:transparent!important}';document.head.append(s)})()`);
      await c.shot(resolve(out,name+'-background.png'));
      await c.evaluate(`document.getElementById('jos-contrast-probe').remove()`);
    }
    report.shots.push({name,...info});
    writeFileSync(resolve(out,'contrast-progress.json'),JSON.stringify({sha256:report.sha256,shots:report.shots}));
  }
  for(const [device,width,height] of [['desktop',1440,900],['mobile',844,390]]){
    await c.send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:device==='mobile'});
    await sleep(400);
    report.devices.push({device,width,height,beats:await c.evaluate(`Array.from(document.querySelectorAll('section[data-beat-id]')).map(e=>({id:e.dataset.beatId,cue:e.dataset.cue,height:e.offsetHeight,layout:document.querySelector('[data-panel-beat="'+e.dataset.beatId+'"]').dataset.verseLayout}))`)});
    // Every beat, forward and reverse seeks, with multiple still positions. This
    // checks the actual shader uniforms/instance attributes, not material.opacity.
    async function measureOpacity(){
    for(const order of [beats,[...beats].reverse()]) for(const beat of order){
      for(const p of (['put-away','elders'].includes(beat.cue)?[.46,.98]:[.46])){
        await goto(beat.id,p);
        const sample=await c.evaluate(`(()=>{
          const cards=window.__josScene.cardDiagnostics().opacitySamples;
          const player=document.querySelector('.jos-station-player');
          const layers=player&&!player.hidden&&player.dataset.phase==='scene'
            ?[...player.querySelectorAll('.jos-station-person')].filter(e=>getComputedStyle(e.parentElement).visibility==='visible'&&+getComputedStyle(e).opacity>0).map(e=>({id:e.dataset.layerId,opacity:+getComputedStyle(e).opacity*+getComputedStyle(e.parentElement).opacity,entering:false})):[];
          return {cards,layers};})()`);
        report.opacity.push({device,beat:beat.id,p,direction:order===beats?'forward':'reverse',...sample});
        for(const card of [...sample.cards,...sample.layers]) if(!card.entering && Math.abs(card.opacity-1)>1e-6)
          report.failures.push(device+' '+beat.id+' '+p+': translucent '+card.id+' '+card.opacity);
        if(order===beats&&p===.46)await capture(device+'-still-'+beat.id);
      }
      console.log('opacity',device,order===beats?'forward':'reverse',beat.cue);
    }
    }
    const targets=[['06-beyond-river',stationProgress('beyond-river',.20),stationProgress('beyond-river',.46)],
      ['07-ford',stationProgress('ford',.30),stationProgress('ford',.70)],
      ['08-redsea',stationProgress('redsea',.64),stationProgress('redsea',.84)],
      ...[15,19,26,28,35].map(n=>[String(n).padStart(2,'0')+'-'+beats[n-1].cue,{id:beats[n-1].id,p:.20},{id:beats[n-1].id,p:.46}]),
      ['18-pause',{id:beats[17].id,p:.10},{id:beats[17].id,p:.20}]];
    for(const [name,a,b] of targets){
      for(const [time,target] of [['a',a],['b',b]]){
        await goto(target.id,target.p); await capture(`${device}-${name}-${time}`);
      }
      console.log('shots',device,name);
    }
    await measureOpacity();
    for(const beat of beats.filter(b=>b.note)){
      await goto(beat.id,.90);
      const m=await sampleNote(c);
      report.notes.push({device,id:beat.id,...m});
      if(!notePasses(m,beat))report.failures.push(device+': note handoff '+beat.id);
    }
    for(const beat of beats.filter(b=>b.familyLines)){
      await goto(beat.id,.20); await sleep(700);
      const samples=await c.evaluate(`new Promise(resolve=>{const a=[],start=performance.now();function f(){const e=document.querySelector('.jos-panel-on .jos-bubble'),r=e.getBoundingClientRect();a.push({t:performance.now()-start,x:r.x,y:r.y});if(performance.now()-start<2000)requestAnimationFrame(f);else resolve(a)}f()})`);
      const dx=Math.max(...samples.map(s=>s.x))-Math.min(...samples.map(s=>s.x));
      const dy=Math.max(...samples.map(s=>s.y))-Math.min(...samples.map(s=>s.y));
      report.bubble.push({device,beat:beat.id,dx,dy,samples});
      if(dx>1||dy>1)report.failures.push(`${device} ${beat.id}: bubble ${dx},${dy}`);
    }
    await goto(beats[11].id,.20);
    await c.evaluate(`document.querySelector('.jos-panel-on .jos-more-btn').click()`);
    const refs=await c.evaluate(`(()=>{const e=document.querySelector('.jos-more-body');return ['民14:29-31','申11:7'].map(ref=>({ref,shown:e.textContent.includes(ref),text:e.textContent}))})()`);
    report.devices.at(-1).daughterRefs=refs.map(({ref,shown})=>({ref,shown}));
    if(refs.some(r=>!r.shown))report.failures.push(device+': missing daughter references');
    await c.shot(resolve(out,device+'-12-more.png'));
    await c.evaluate(`document.querySelector('.jos-more-close').click()`);
  }
  // Adjacent 100px frames at every cue boundary, plus the earlier reported entrances.
  await c.send('Emulation.setDeviceMetricsOverride',{width:1440,height:900,deviceScaleFactor:1,mobile:false});
  // Verify actual DOM clauses at every verse/stop, including the prologue and coda.
  report.contentUnits=[];
  for(const beat of beats){
    const list=stations.filter(s=>s.beat===beat.id);
    for(const station of list.length?list:[undefined]){
      const lines=storyLines(beat,site,station);
      for(const [i,line] of lines.entries()){
        const start=beat.interaction==='cannot-pause'?.30:0,end=beat.note?.70:.86;
        const progress=station?stationProgress(station.id,(i+.4)/lines.length*(beat.note?.70:1))
          :{id:beat.id,p:start+(i+.4)/lines.length*(end-start)};
        await goto(progress.id,progress.p);
        const actual=await c.evaluate(`[...document.querySelectorAll('.jos-panel-on .jos-story-sentence')].map(e=>e.textContent).join('')`);
        report.contentUnits.push({beat:beat.id,station:station?.id,ref:primaryRefOf(beat),v:line.v,expected:line.text,actual});
        if(actual!==line.text)report.failures.push(beat.id+': rendered clause differs '+line.v);
      }
    }
  }
  await goto(beats.at(-1).id,.4);
  if(await c.evaluate(`!!document.querySelector('.jos-panel-on .jos-vbox-verse')`))report.failures.push('coda repeats verse');
  // Start at the very top, in 300px increments, through the end of beat 12.
  report.scroll300=[];
  const finish=await c.evaluate(`(()=>{const e=document.getElementById('jos-beat-${beats[11].id}');return scrollY+e.getBoundingClientRect().bottom-innerHeight*.36-1})()`);
  const owners=new Map();
  for(let y=0;y<=finish;y+=300){
    await c.evaluate(`scrollTo({top:${y},behavior:'instant'})`);await sleep(1100);
    const info=await c.evaluate(`(()=>{const p=document.querySelector('.jos-panel-on'),v=p.querySelector('.jos-vbox-verse'),s=window.__josState;
      const live=e=>getComputedStyle(e).visibility!=='hidden'&&+getComputedStyle(e).opacity>.01;
      return {y:scrollY,beat:s.beat,p:s.beatProgress,key:v?.dataset.stationVerse,ref:v?.getAttribute('aria-label'),
        sentences:v&&live(v)?[...v.querySelectorAll('.jos-story-sentence')].filter(e=>!e.hidden&&live(e)&&[...e.querySelectorAll('.jos-story-char')].some(live)).map(e=>e.textContent):[]}})()`);
    for(const sentence of info.sentences){
      const key=info.ref+'|'+sentence,owner=info.key?.split(':')[0];
      if(owners.has(key)&&owners.get(key)!==owner)report.failures.push('300px scan: repeated '+key);
      owners.set(key,owner);
    }
    const name='scroll300-'+String(y).padStart(6,'0');
    await c.shot(resolve(out,name+'.png'));report.scroll300.push({name,...info});
    if(y%3000===0)console.log('scroll300',y,info.beat);
  }
  for(let i=1;i<beats.length;i++){
    for(const delta of [-50,50]){
      const beat=beats[i];
      await c.evaluate(`(()=>{const e=document.getElementById('jos-beat-${beat.id}');scrollTo({top:scrollY+e.getBoundingClientRect().top-innerHeight*.36+${delta},behavior:'instant'})})()`);
      await sleep(1500);
      await c.shot(resolve(out,`boundary-${String(i+1).padStart(2,'0')}-${delta}.png`));
      report.entrances.push({beat:beat.id,delta,figures:await c.evaluate('window.__josScene.visualDiagnostics().figures.map(f=>f.id)')});
    }
  }
  // User-started playback, 31 frames over the first sixty seconds.
  await c.evaluate(`scrollTo({top:0,behavior:'instant'})`);await sleep(2000);
  await c.evaluate(`(()=>{window.__storyPlaySamples=[];window.__storySampleRaf=0;const start=performance.now();function tick(){window.__storyPlaySamples.push({t:performance.now()-start,y:scrollY,beat:window.__josState.beat});if(performance.now()-start<61000)window.__storySampleRaf=requestAnimationFrame(tick)}tick();document.querySelector('.jos-autoplay').click()})()`);
  const started=Date.now();
  for(let seconds=0;seconds<=60;seconds+=2){
    await sleep(Math.max(0,started+seconds*1000-Date.now()));
    await c.shot(resolve(out,`autoplay-${String(seconds).padStart(2,'0')}.png`));
    report.autoplay.push(await c.evaluate(`({seconds:${seconds},y:scrollY,beat:window.__josState.beat,playing:document.querySelector('.jos-autoplay').getAttribute('aria-pressed')})`));
  }
  report.autoplaySamples=await c.evaluate('window.__storyPlaySamples');
  await c.evaluate(`document.querySelector('.jos-autoplay').focus();document.querySelector('.jos-autoplay').dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowDown',bubbles:true}))`);
  report.focusedKeyPause=await c.evaluate(`document.querySelector('.jos-autoplay').getAttribute('aria-pressed')==='false'`);
  if(!report.focusedKeyPause)report.failures.push('focused playback button ignored ArrowDown');
  for(const [label,event] of [['keyboard',"new KeyboardEvent('keydown',{key:'ArrowDown',bubbles:true})"],['touch',"new Event('touchstart',{bubbles:true})"],['pointer',"new Event('pointerdown',{bubbles:true})"],['click',"new MouseEvent('click',{bubbles:true})"]]){
    await c.evaluate(`if(document.querySelector('.jos-autoplay').getAttribute('aria-pressed')!=='true')document.querySelector('.jos-autoplay').click();document.body.dispatchEvent(${event})`);
    const paused=await c.evaluate(`document.querySelector('.jos-autoplay').getAttribute('aria-pressed')==='false'`);
    report[label+'Pause']=paused;
    if(!paused)report.failures.push('autoplay did not pause on '+label);
  }
  await c.evaluate(`document.querySelector('.jos-autoplay').click()`);
  await c.wheel(100); await sleep(150);
  report.wheelPause=await c.evaluate(`document.querySelector('.jos-autoplay').textContent==='自動播放'`);
  if(!report.wheelPause)report.failures.push('autoplay did not pause on wheel');
  // Late-story playback verifies automatic raising, headline dwell and the end cap.
  await goto(beats[25].id,.05);
  await c.evaluate(`Object.assign(window.__josState.raiseStone,{done:false,progress:0,holding:false});document.querySelector('.jos-autoplay').click()`);
  await sleep(3700);
  report.autoStone=await c.evaluate('({...window.__josState.raiseStone})');
  if(!report.autoStone.done)report.failures.push('automatic stone failed');
  await c.send('Input.dispatchKeyEvent',{type:'keyDown',key:'Escape',code:'Escape'});
  await goto(beats[17].id,.10);await c.evaluate(`document.querySelector('.jos-autoplay').click()`);
  await sleep(2000);const y1=await c.evaluate('scrollY');await sleep(2000);const y2=await c.evaluate('scrollY');
  report.headlineHold={y1,y2,delta:y2-y1};
  if(Math.abs(y2-y1)>1)report.failures.push('headline did not hold');
  await c.wheel(1);
  await goto(beats.at(-1).id,.99);await c.evaluate(`document.querySelector('.jos-autoplay').click()`);
  await sleep(3000);
  report.end=await c.evaluate(`({beat:window.__josState.beat,playing:document.querySelector('.jos-autoplay').getAttribute('aria-pressed'),reviewTop:document.getElementById('jos-review-root').getBoundingClientRect().top,height:innerHeight})`);
  if(report.end.playing!=='false')report.failures.push('end did not stop');
  if(report.end.reviewTop<report.end.height*.58)report.failures.push('end entered review area');
  // Loss of WebGL uses exactly the same DOM typography and clause reveals.
  await c.evaluate(`window.__josScene.renderer?.getContext?.()`);
  await c.evaluate(`document.querySelector('canvas').dispatchEvent(new Event('webglcontextlost',{cancelable:true}))`);
  await goto(beats[14].id,.3);await capture('fallback-15');
  report.errors=c.consoleLog.filter(s=>s.startsWith('[error]')||s.startsWith('[exception]'));
  report.failures.push(...report.errors);
}finally{
  writeFileSync(resolve(out,'report.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify({shots:report.shots.length,bubbles:report.bubble.map(b=>({device:b.device,beat:b.beat,dx:b.dx,dy:b.dy})),failures:report.failures}));
  await c.close();clearInterval(keepAlive);
}
if(report.failures.length)process.exitCode=1;
