import { siteUrl } from './site-server.mjs';
import { mkdirSync, writeFileSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';
import { launch, sleep } from './cdp.mjs';

const mobile=process.argv[2]==='mobile';
const device=mobile?'mobile':'desktop', width=mobile?844:1440,height=mobile?390:900;
const out=resolve('.tmp-shots/cards2'); mkdirSync(out,{recursive:true});
const report={device,viewport:[width,height],dpr:mobile?2:1,buildSha256:createHash('sha256').update(readFileSync('dist/index.html')).digest('hex'),shots:[],samples:[],failures:[]};
const c=await launch({width,height,dpr:mobile?2:1,mobile,port:mobile?9442:9441,gpu:true});
const keepAlive=setInterval(()=>{},1000);
const hit=(a,b,tolerance=0)=>a.x0<b.x1-tolerance&&a.x1>b.x0+tolerance&&a.y0<b.y1-tolerance&&a.y1>b.y0+tolerance;
try{
  await c.send('Page.navigate',{url:siteUrl});
  for(let i=0;i<60;i++){if(await c.evaluate('!!window.__josScene && document.querySelectorAll("[data-cue]").length>30'))break;await sleep(500);}
  await sleep(1200);
  await c.evaluate('window.__josState.motionOff=false');
  async function goto(cue,p){
    await c.evaluate(`(()=>{const el=document.querySelector('section[data-cue="${cue}"]');const r=el.getBoundingClientRect();scrollTo({top:scrollY+r.top-innerHeight*.36+${p}*(r.height-innerHeight*.35),behavior:'instant'});})()`);
    await sleep(650);
    if(await c.evaluate('window.__josState.cue')!==cue)report.failures.push(`goto ${cue}: wrong cue`);
  }
  async function measure(name){
    const m=await c.evaluate(`(()=>{
      const rect=e=>{const r=e.getBoundingClientRect();return {x0:r.left,y0:r.top,x1:r.right,y1:r.bottom};};
      const visible=e=>getComputedStyle(e).visibility!=='hidden'&&getComputedStyle(e).display!=='none'&&parseFloat(getComputedStyle(e).opacity)>.05;
      const bubble=[...document.querySelectorAll('.jos-panel-on .jos-bubble')].find(visible);
      const projectedLabels=window.__josScene.getCurrentLabels?.()||[];
      const labels=new Map(projectedLabels.map(l=>[l.id,l]));
      const tags=[...document.querySelectorAll('.jos-stage-tag')].filter(visible).map(e=>{const r=rect(e),id=e.dataset.tagId,label=labels.get(id);return {...r,id,text:e.textContent,headY:label?.headY,headGapPx:label?label.headY-r.y1:null};});
      const hiddenActorTags=projectedLabels.filter(l=>l.id.startsWith('actor-')&&!l.visible).map(l=>l.id);
      return {cue:window.__josState.cue,p:window.__josState.beatProgress,overflow:document.documentElement.scrollWidth-innerWidth,tags,hiddenActorTags,bubble:bubble?{...rect(bubble),docked:bubble.classList.contains('jos-bubble-docked'),headY:Number(bubble.dataset.headY),tailGapPx:Number(bubble.dataset.tailGap)}:null,bodies:window.__josScene.getBodyBoxes(),bench:window.__josScene.benchInfo(),cards:window.__josScene.cardDiagnostics?.()};
    })()`);
    const maxTagGap=mobile?16:24;
    if(m.overflow>0)report.failures.push(`${name}: overflow ${m.overflow}`);
    if(name===`02-${device}-gather-32`&&m.tags.filter(t=>t.id?.startsWith('actor-')).length!==3)report.failures.push(`${name}: expected 3 visible actor tags`);
    for(const tag of m.tags)if(tag.id?.startsWith('actor-')&&(!Number.isFinite(tag.headGapPx)||tag.headGapPx<0||tag.headGapPx>maxTagGap))report.failures.push(`${name}: ${tag.text} head gap ${tag.headGapPx}px (limit ${maxTagGap})`);
    if(m.bubble){
      for(const tag of m.tags)if(hit(m.bubble,tag))report.failures.push(`${name}: bubble/tag ${tag.text}`);
      const j=m.bodies.find(a=>a.id==='joshua');if(j&&hit(m.bubble,j,1/(mobile?2:1)))report.failures.push(`${name}: bubble/Joshua`);
      if(m.bubble.docked)report.failures.push(`${name}: bubble docked`);
      if(!Number.isFinite(m.bubble.tailGapPx)||m.bubble.tailGapPx<0||m.bubble.tailGapPx>maxTagGap)report.failures.push(`${name}: bubble head gap ${m.bubble.tailGapPx}px (limit ${maxTagGap})`);
    }
    for(let i=0;i<m.tags.length;i++)for(let j=i+1;j<m.tags.length;j++)if(hit(m.tags[i],m.tags[j]))report.failures.push(`${name}: tags overlap`);
    if(m.cards?.maxYawError>30)report.failures.push(`${name}: card yaw ${m.cards.maxYawError}`);
    report.samples.push({name,...m});return m;
  }
  const cues=[['02','gather'],['05','family-1'],['15','my-house'],['18','cannot'],['23','family-4'],['26','raise'],['28','dismiss'],['29','family-5'],['31','elders'],['36','epilogue-stone']];
  for(const [n,cue] of cues){
    const positions=cue.startsWith('family-')?[.25,.8]:cue==='elders'?[.25,.8]:[.32];
    for(const p of positions){
      await goto(cue,p);
      if(cue==='raise')await c.evaluate('Object.assign(window.__josState.raiseStone,{done:false,progress:0,holding:false,auto:false})');
      await sleep(200);
      const name=`${n}-${device}-${cue}-${Math.round(p*100)}`;
      await measure(name); await c.shot(resolve(out,`${name}.png`));report.shots.push(`${name}.png`);
      if(cue==='raise'){
        const button=await c.evaluate(`(()=>{const el=document.querySelector('.jos-panel-on .jos-raise-btn')||document.querySelector('.jos-panel-on [data-coach="raise-btn"]');if(!el)return null;const r=el.getBoundingClientRect();return {x:r.left+r.width/2,y:r.top+r.height/2};})()`);
        // The keyboard path is the same supported hold interaction, with an actual DOM event.
        const found=await c.evaluate(`(()=>{const b=[...document.querySelectorAll('.jos-panel-on button')].find(e=>e.textContent.includes('按住'));if(!b)return false;b.focus();b.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}));return true;})()`);
        void button;
        if(!found)report.failures.push('raise: hold control missing');
        await sleep(1850);
        await c.evaluate(`(()=>{const b=document.activeElement;b?.dispatchEvent(new KeyboardEvent('keyup',{key:'Enter',bubbles:true}));})()`);
        if(!await c.evaluate('window.__josState.raiseStone.done'))report.failures.push('raise: interaction did not finish');
        await measure(`${name}-up`);await c.shot(resolve(out,`${name}-up.png`));report.shots.push(`${name}-up.png`);
      }
    }
  }
  // All authored camera paths, including bridge endpoints and dialogue changes.
  const cuesAll=JSON.parse(readFileSync('src/data/site.json','utf8')).segments.flatMap(s=>s.beats).filter(b=>!['beyond-river','abraham','egypt','east','jericho','gifts'].includes(b.cue));
  for(const b of cuesAll)for(const p of [.1,.55,.95]){await goto(b.cue,p);await measure(`path-${b.cue}-${p}`);}
  await goto('gather',.45);
  report.fps=await c.evaluate(`new Promise(resolve=>{const samples=[];const start=performance.now();let previous=start;function frame(t){samples.push(t-previous);previous=t;if(t-start<5000)requestAnimationFrame(frame);else{const sorted=samples.slice().sort((a,b)=>a-b);resolve({seconds:(t-start)/1000,frames:samples.length,fps:samples.length*1000/(t-start),p95FrameMs:sorted[Math.floor(sorted.length*.95)],bench:window.__josScene.benchInfo()});}}requestAnimationFrame(frame);})`);
  const before=await c.evaluate('window.__josScene.cardDiagnostics?.()');
  await c.evaluate('window.__josState.motionOff=true');await sleep(300);
  const after=await c.evaluate('window.__josScene.cardDiagnostics?.()');
  report.motionOff={before,after};
  report.gpu=await c.evaluate(`(()=>{const gl=document.querySelector('canvas').getContext('webgl2');if(!gl)return null;const ext=gl.getExtension('WEBGL_debug_renderer_info');return {renderer:ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER),vendor:ext?gl.getParameter(ext.UNMASKED_VENDOR_WEBGL):gl.getParameter(gl.VENDOR)};})()`);
  report.errors=c.consoleLog.filter(s=>/^\[(error|exception)\]/.test(s));
  if(createHash('sha256').update(readFileSync('dist/index.html')).digest('hex')!==report.buildSha256)report.failures.push('build changed during capture');
  if(report.errors.length)report.failures.push(...report.errors);
  await c.send('Page.navigate',{url:'about:blank'});await sleep(300);
  report.emptyPageFps=await c.evaluate(`new Promise(resolve=>{let n=0;const start=performance.now();function frame(t){n++;if(t-start<5000)requestAnimationFrame(frame);else resolve({seconds:(t-start)/1000,frames:n,fps:n*1000/(t-start)});}requestAnimationFrame(frame);})`);
  const actorTagGaps=report.samples.flatMap(s=>s.tags.filter(t=>t.id?.startsWith('actor-')).map(t=>t.headGapPx));
  const hiddenActorTagSamples=report.samples.filter(s=>s.hiddenActorTags.length).length;
  const bubbleTailGaps=report.samples.filter(s=>s.bubble).map(s=>s.bubble.tailGapPx);
  report.anchorMetrics={tagLimitPx:mobile?16:24,tagCount:actorTagGaps.length,maxTagGapPx:actorTagGaps.length?Math.max(...actorTagGaps):null,minTagGapPx:actorTagGaps.length?Math.min(...actorTagGaps):null,hiddenActorTagSamples,bubbleCount:bubbleTailGaps.length,maxBubbleTailGapPx:bubbleTailGaps.length?Math.max(...bubbleTailGaps):null};
}finally{
  writeFileSync(resolve(out,`report-${device}.json`),JSON.stringify(report,null,2));
  clearInterval(keepAlive);await c.close();
}
console.log(JSON.stringify({device,shots:report.shots.length,samples:report.samples.length,fps:report.fps,failures:report.failures},null,2));
process.exit(report.failures.length?1:0);
