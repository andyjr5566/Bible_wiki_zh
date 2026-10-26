import { siteUrl } from './site-server.mjs';
import { mkdirSync, writeFileSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { launch, sleep } from './cdp.mjs';

const mobile = process.argv[2] === 'mobile';
const device = mobile ? 'mobile' : 'desktop';
const width = mobile ? 844 : 1440;
const height = mobile ? 390 : 900;
const out = resolve('.tmp-shots/shechem-env');
mkdirSync(out, { recursive: true });
const report = {
  device,
  viewport: [width, height],
  dpr: mobile ? 2 : 1,
  buildSha256: createHash('sha256').update(readFileSync('dist/index.html')).digest('hex'),
  shots: [],
  samples: [],
  failures: [],
};
const port = mobile ? 9462 : 9461;
const c = await launch({ width, height, dpr: mobile ? 2 : 1, mobile, port, gpu: true });
const keepAlive = setInterval(() => {}, 1000);
const hit = (a, b, tolerance = 0) =>
  a.x0 < b.x1 - tolerance && a.x1 > b.x0 + tolerance &&
  a.y0 < b.y1 - tolerance && a.y1 > b.y0 + tolerance;

try {
  await c.send('Page.navigate', { url: siteUrl });
  for (let i = 0; i < 60; i++) {
    if (await c.evaluate('!!window.__josScene && document.querySelectorAll("[data-cue]").length > 30')) break;
    await sleep(500);
  }
  await sleep(1200);
  await c.evaluate('window.__josState.motionOff=false');

  async function goto(cue, progress) {
    await c.evaluate(`(()=>{
      const el=document.querySelector('section[data-cue="${cue}"]');
      if(!el) throw new Error('missing cue ${cue}');
      const r=el.getBoundingClientRect();
      scrollTo({top:scrollY+r.top-innerHeight*.36+${progress}*(r.height-innerHeight*.35),behavior:'instant'});
    })()`);
    await sleep(1050);
    const actual = await c.evaluate('window.__josState.cue');
    if (actual !== cue) report.failures.push(`goto ${cue}: got ${actual}`);
  }

  async function measure(name) {
    const m = await c.evaluate(`(()=>{
      const rect=e=>{const r=e.getBoundingClientRect();return {x0:r.left,y0:r.top,x1:r.right,y1:r.bottom};};
      const visible=e=>getComputedStyle(e).visibility!=='hidden'&&getComputedStyle(e).display!=='none'&&parseFloat(getComputedStyle(e).opacity)>.05;
      const shown=e=>{for(let n=e;n;n=n.parentElement){if(!visible(n)||n.hidden)return false;}return e.getBoundingClientRect().width>0;};
      const bubble=[...document.querySelectorAll('.jos-panel-on .jos-bubble')].find(visible);
      const projected=window.__josScene.getCurrentLabels?.()||[];
      const byId=new Map(projected.map(item=>[item.id,item]));
      const tags=[...document.querySelectorAll('.jos-stage-tag')].filter(visible).map(e=>{
        const r=rect(e), item=byId.get(e.dataset.tagId);
        return {...r,id:e.dataset.tagId,text:e.textContent,headGapPx:item?item.headY-r.y1:null};
      });
      return {
        cue:window.__josState.cue,segment:window.__josState.segment,p:window.__josState.beatProgress,
        overflow:document.documentElement.scrollWidth-innerWidth,
        tags,hiddenActorTags:projected.filter(item=>item.id.startsWith('actor-')&&!item.visible).map(item=>item.id),
        bubble:bubble?{...rect(bubble),docked:bubble.classList.contains('jos-bubble-docked'),tailGapPx:Number(bubble.dataset.tailGap)}:null,
        bodies:window.__josScene.getBodyBoxes(),bench:window.__josScene.benchInfo(),
        cards:window.__josScene.cardDiagnostics?.(),scrollY,
        visual:window.__josScene.visualDiagnostics(),
        uiMasks:[...document.querySelectorAll('header,.jos-thread-rail,.jos-panel-on .jos-voice,.jos-panel-on .jos-wslot,.jos-panel-on .jos-bubble,.jos-stage-tag,button')].filter(shown).map(rect)
      };
    })()`);
    const maxGap = mobile ? 16 : 24;
    if (m.overflow > 0) report.failures.push(`${name}: overflow ${m.overflow}`);
    for (const tag of m.tags) {
      if (tag.id?.startsWith('actor-') && (!Number.isFinite(tag.headGapPx) || tag.headGapPx < 0 || tag.headGapPx > maxGap)) {
        report.failures.push(`${name}: ${tag.text} head gap ${tag.headGapPx}px`);
      }
    }
    if (m.bubble) {
      for (const tag of m.tags) if (hit(m.bubble, tag)) report.failures.push(`${name}: bubble/tag ${tag.text}`);
      const joshua = m.bodies.find(actor => actor.id === 'joshua');
      if (joshua && hit(m.bubble, joshua, 1 / (mobile ? 2 : 1))) report.failures.push(`${name}: bubble/Joshua`);
      if (m.bubble.docked) report.failures.push(`${name}: bubble docked`);
      if (!Number.isFinite(m.bubble.tailGapPx) || m.bubble.tailGapPx < 0 || m.bubble.tailGapPx > maxGap) {
        report.failures.push(`${name}: bubble tail gap ${m.bubble.tailGapPx}px`);
      }
    }
    for (let i = 0; i < m.tags.length; i++) {
      for (let j = i + 1; j < m.tags.length; j++) if (hit(m.tags[i], m.tags[j])) report.failures.push(`${name}: tags overlap`);
    }
    if (m.cards?.maxYawError > 30) report.failures.push(`${name}: card yaw ${m.cards.maxYawError}`);
    report.samples.push({ name, ...m });
    return m;
  }

  async function capture(prefix, cue, progress, label = String(Math.round(progress * 100))) {
    await goto(cue, progress);
    const name = `${prefix}-${device}-${label}`;
    await measure(name);
    await c.shot(resolve(out, `${name}.png`));
    report.shots.push(`${name}.png`);
    return name;
  }

  async function pixels(name) {
    const sample=report.samples.at(-1);
    // Station actors live in DOM layers, with their own transparent silhouettes.
    if (sample.cue==='jericho') {
      sample.visual.figures=await c.evaluate(`(()=>{
        return [...document.querySelectorAll('.jos-station-person,.jos-station-layer[data-role="coffin"]')].filter(img=>img.complete&&+getComputedStyle(img).opacity>.8).map(img=>{
          const canvas=document.createElement('canvas');canvas.width=img.naturalWidth;canvas.height=img.naturalHeight;
          const ctx=canvas.getContext('2d');ctx.drawImage(img,0,0);const a=ctx.getImageData(0,0,canvas.width,canvas.height).data;
          let top=-1,bottom=-1,x=0;for(let y=0;y<canvas.height;y++){let sum=0,count=0;for(let i=0;i<canvas.width;i++){if(a[(y*canvas.width+i)*4+3]>240){sum+=i;count++;}}if(count>=6){if(top<0){top=y;x=sum/count;}bottom=y;}}
          const r=img.getBoundingClientRect();return {id:'station-'+img.dataset.layerId,headX:r.x+x/canvas.width*r.width,headY:r.y+top/canvas.height*r.height,footX:r.x+x/canvas.width*r.width,footY:r.y+bottom/canvas.height*r.height,inFrame:top>=0};
        });
      })()`);
      sample.visual.environment={from:'morning',to:'morning',amount:0};
    }
    const result=spawnSync('python',['-I','tools/check-scene-pixels.py'],{
      input:JSON.stringify({image:resolve(out,`${name}.png`),sample,viewport:[width,height]}),encoding:'utf8',maxBuffer:2_000_000,
    });
    if(result.status!==0)throw new Error(result.stderr||'pixel checker failed');
    sample.pixels=JSON.parse(result.stdout);
    report.failures.push(...sample.pixels.failures.map(f=>`${name}: ${f}`));
  }

  // Every screenshot uses the same pixel gate, including both stone states.
  const rawShot=c.shot;
  c.shot=async path=>{await rawShot(path);await pixels(path.split(/[\\/]/).at(-1).replace(/\.png$/,''));};

  await capture('02-gather', 'gather', 0.32);
  await capture('05-family-1', 'family-1', 0.25);
  await capture('05-family-1', 'family-1', 0.8);
  await capture('15-my-house', 'my-house', 0.32);
  await capture('18-cannot', 'cannot', 0.32);
  await capture('24-covenant', 'covenant', 0.32);

  await goto('raise', 0.32);
  await c.evaluate('Object.assign(window.__josState.raiseStone,{done:false,progress:0,holding:false,auto:false})');
  await sleep(150);
  const downName = `26-raise-${device}-down`;
  await measure(downName);
  await c.shot(resolve(out, `${downName}.png`));
  report.shots.push(`${downName}.png`);
  const held = await c.evaluate(`(()=>{
    const b=[...document.querySelectorAll('.jos-panel-on button')].find(e=>e.textContent.includes('按住'));
    if(!b)return false;
    b.focus();
    b.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}));
    return true;
  })()`);
  if (!held) report.failures.push('26-raise: hold control missing');
  for(let i=0;i<50&&!await c.evaluate('window.__josState.raiseStone.done');i++)await sleep(100);
  await c.evaluate('document.activeElement?.dispatchEvent(new KeyboardEvent("keyup",{key:"Enter",bubbles:true}))');
  if (!await c.evaluate('window.__josState.raiseStone.done')) report.failures.push('26-raise: hold action did not finish');
  const upName = `26-raise-${device}-up`;
  await measure(upName);
  await c.shot(resolve(out, `${upName}.png`));
  report.shots.push(`${upName}.png`);

  await capture('28-dismiss', 'dismiss', 0.32);
  await capture('28-dismiss', 'dismiss', 0.05, 'start');
  await capture('28-dismiss', 'dismiss', 0.60, 'departing');
  await capture('28-dismiss', 'dismiss', 0.85, 'joshua');
  await capture('28-dismiss', 'dismiss', 0.98, 'last');
  await c.evaluate('window.__josState.motionOff=true');
  await capture('31-elders', 'elders', 0.0, 'day');
  await capture('31-elders', 'elders', 0.21, 'night');
  await c.evaluate('window.__josState.motionOff=false');
  await capture('36-epilogue-stone', 'epilogue-stone', 0.32);
  await capture('jordan-jericho', 'jericho', 0.5, 'shoreline');

  const initialScroll = await c.evaluate('scrollY');
  const samples = [];
  for (let i = 0; i < 112; i++) {
    await sleep(80);
    samples.push(await c.evaluate('scrollY'));
  }
  const drift = Math.max(...samples.map(value => Math.abs(value - initialScroll)));
  report.scrollStability = { initial: initialScroll, final: samples.at(-1), maxDeltaPx: drift, samples: samples.length };
  if (drift > 1) report.failures.push(`scrollY drift ${drift}px`);
  report.errors = c.consoleLog.filter(line => /^\[(error|exception)\]/.test(line));
  if (report.errors.length) report.failures.push(...report.errors);
  if (createHash('sha256').update(readFileSync('dist/index.html')).digest('hex') !== report.buildSha256) {
    report.failures.push('build changed during capture');
  }
} finally {
  writeFileSync(resolve(out, `report-${device}.json`), JSON.stringify(report, null, 2));
  clearInterval(keepAlive);
  await c.close();
}

console.log(JSON.stringify({ device, shots: report.shots.length, samples: report.samples.length,
  scrollStability: report.scrollStability, failures: report.failures }, null, 2));
process.exit(report.failures.length ? 1 : 0);
