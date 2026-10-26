import { siteUrl } from './site-server.mjs';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';
import { launch, sleep } from './cdp.mjs';

const mobile = process.argv[2] === 'mobile';
const interactionsOnly = process.env.JOS_ACT2_INTERACTIONS_ONLY === '1';
const device = mobile ? 'mobile' : 'desktop';
const width = mobile ? 844 : 1440, height = mobile ? 390 : 900;
const out = resolve('.tmp-shots/act2');
mkdirSync(out, { recursive: true });
const stations = JSON.parse(readFileSync('src/data/stations.json', 'utf8'));
const ledger = JSON.parse(readFileSync('src/assets/stations/sources.json', 'utf8'));
const c = await launch({ width, height, dpr: mobile ? 2 : 1, mobile, gpu: true, port: mobile ? 9452 : 9451 });
const keepAlive = setInterval(() => {}, 1000);
const report = interactionsOnly ? JSON.parse(readFileSync(resolve(out,`report-${device}.json`),'utf8')) : { device, viewport: [width, height], dpr: mobile ? 2 : 1,
  buildSha256: createHash('sha256').update(readFileSync('dist/index.html')).digest('hex'),
  shots: [], samples: [], interactions: [], static: [], failures: [] };
if (interactionsOnly) {
  report.failures = report.failures.filter(f => f !== 'gift cards: expected all four flipped');
  report.interactions = [];
  if(report.buildSha256!==createHash('sha256').update(readFileSync('dist/index.html')).digest('hex'))throw new Error('Acceptance build changed');
}
function beatP(station, local) {
  const list = stations.filter(s => s.beat === station.beat);
  const offset = list.slice(0, list.indexOf(station)).reduce((n, s) => n + s.weight, 0);
  return (offset + station.weight * local) / list.reduce((n, s) => n + s.weight, 0);
}
async function goto(station, p = .5, flight = false) {
  const i = stations.indexOf(station);
  const local = flight ? .16 * p : i > 0 ? .16 + .84 * p : p;
  const progress = beatP(station, local);
  await c.evaluate(`(()=>{ const el=document.querySelector('section[data-beat-id="${station.beat}"]');
    const r=el.getBoundingClientRect(); scrollTo({top:scrollY+r.top-innerHeight*.36+${progress}*(r.height-innerHeight*.35),behavior:'instant'}); })()`);
  for (let i = 0; i < 80; i++) {
    if (await c.evaluate(`document.querySelector('.jos-station-player').dataset.station==='${station.id}' && [...document.querySelectorAll('.jos-station-composition img')].every(i=>i.complete && i.naturalWidth>0)`)) break;
    await sleep(100);
  }
  await sleep(300);
}
async function measure(name, station, flight) {
  const sample = await c.evaluate(`(()=>{
    const rect=e=>{const r=e.getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height};};
    const player=document.querySelector('.jos-station-player');
    const node=document.querySelector('.jos-station-composition[data-station-id="${station.id}"]');
    const verse=document.querySelector('.jos-panel-on .jos-vbox-verse');
    return {station:player.dataset.station,phase:player.dataset.phase,p:Number(player.dataset.progress),
      overflow:document.documentElement.scrollWidth-innerWidth,scrollY,verse:verse?{...rect(verse),v:Number(verse.dataset.verse)}:null,
      layers:[...node.querySelectorAll('img')].map(img=>({id:img.dataset.layerId,...rect(img),opacity:Number(img.style.opacity),complete:img.complete&&img.naturalWidth>0})),
      resident:document.querySelectorAll('.jos-station-composition').length,
      preloaded:player.dataset.preloaded}; })()`);
  if (sample.station !== station.id) report.failures.push(`${name}: wrong station`);
  if (sample.overflow > 0) report.failures.push(`${name}: overflow ${sample.overflow}`);
  if (sample.layers.some(l => !l.complete)) report.failures.push(`${name}: incomplete image`);
  if (sample.resident > 2) report.failures.push(`${name}: too many resident compositions`);
  if (!station.verses.includes(sample.verse.v)) report.failures.push(`${name}: verse outside station`);
  const main = station.layers.filter(l => l.role === 'person' && l.id !== 'far-crowd');
  sample.people = main.map(l => {
    const r = sample.layers.find(r => r.id === l.id), source = ledger[l.asset];
    if (!source.bounds) return null;
    const [x0,y0,x1,y1] = source.bounds, [w,h] = source.size;
    return {id:l.id,x:r.x+x0/w*r.w,y:r.y+y0/h*r.h,w:(x1-x0)/w*r.w,h:(y1-y0)/h*r.h,opacity:r.opacity};
  }).filter(Boolean);
  const hit = (a,b) => a.x<b.x+b.w&&a.x+a.w>b.x&&a.y<b.y+b.h&&a.y+a.h>b.y;
  if (!flight) for (const person of sample.people) if (person.opacity>.1&&hit(person,sample.verse)) report.failures.push(`${name}: verse covers ${person.id}`);
  report.samples.push({name,...sample});
  return sample;
}
async function shot(station, suffix, p=.5, flight=false) {
  await goto(station,p,flight);
  const name=`${device}-${String(stations.indexOf(station)+1).padStart(2,'0')}-${station.id}-${suffix}`;
  await measure(name,station,flight);
  await c.shot(resolve(out,`${name}.png`));
  report.shots.push(`${name}.png`);
}
async function click(selector) {
  const point=await c.evaluate(`(()=>{const e=document.querySelector(${JSON.stringify(selector)});if(!e)return null;const slot=e.closest('.jos-wslot');if(slot){const r=e.getBoundingClientRect(),s=slot.getBoundingClientRect();if(r.bottom>s.bottom)slot.scrollTop+=r.bottom-s.bottom+8;else if(r.top<s.top)slot.scrollTop-=s.top-r.top+8;}const r=e.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2};})()`);
  if(!point) throw new Error(`Missing ${selector}`);
  await c.send('Input.dispatchMouseEvent',{type:'mousePressed',...point,button:'left',clickCount:1});
  await c.send('Input.dispatchMouseEvent',{type:'mouseReleased',...point,button:'left',clickCount:1});
  await sleep(150);
}
async function clickMotion() {
  const point=await c.evaluate(`(()=>{const e=[...document.querySelectorAll('.jos-header button')].find(e=>e.textContent.startsWith('動態'));const r=e.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2};})()`);
  await c.send('Input.dispatchMouseEvent',{type:'mousePressed',...point,button:'left',clickCount:1});
  await c.send('Input.dispatchMouseEvent',{type:'mouseReleased',...point,button:'left',clickCount:1});
  await sleep(150);
}
try {
  await c.send('Page.navigate',{url:siteUrl});
  for(let i=0;i<60;i++) { if(await c.evaluate('!!window.__josState && document.querySelectorAll("[data-beat-id]").length===36')) break; await sleep(250); }
  await c.evaluate('window.__josState.motionOff=false');
  for(const station of interactionsOnly ? [] : stations) {
    if(stations.indexOf(station)>0) {
      const opacity=()=>c.evaluate(`(()=>{const nodes=[...document.querySelectorAll('.jos-station-composition')];return Object.fromEntries(nodes.map(n=>[n.dataset.stationId,Number(n.style.opacity)]));})()`);
      const previous=stations[stations.indexOf(station)-1];
      await goto(station,.15,true);const start=await opacity();
      await goto(station,.5,true);const middle=await opacity();
      await goto(station,.85,true);const end=await opacity();
      report.flights??=[];report.flights.push({station:station.id,start,middle,end});
      if(!(start[previous.id]>.1&&middle[previous.id]===0&&middle[station.id]===0&&end[station.id]>.1))report.failures.push(`${station.id}: continuous flight fade failed`);
      await shot(station,'flight',.5,true);
    }
    if(station.id==='redsea') {
      await shot(station,'start',.08); await shot(station,'closing',.63); await shot(station,'dawn',.98);
    } else await shot(station,'key');
  }
  // 逐站比較不同捲動進度的圖層位置、透明度與日月位置，關閉動態後須完全不變。
  const motionY=await c.evaluate('scrollY');
  await clickMotion();
  report.interactions.push({kind:'motion',before:motionY,after:await c.evaluate('scrollY')});
  if(!await c.evaluate('window.__josState.motionOff'))report.failures.push('motion switch failed');
  const signature=()=>c.evaluate(`(()=>{const p=document.querySelector('.jos-station-player'),n=p.querySelector('[data-station-id="'+p.dataset.station+'"]');return [...n.querySelectorAll('img,.jos-station-orbit,.jos-station-marks i')].map(e=>[e.style.transform,e.style.opacity,e.style.filter]);})()`);
  for(const station of interactionsOnly ? [] : stations) {
    await goto(station,.12);const a=await signature();
    await goto(station,.88);const b=await signature();
    const stable=JSON.stringify(a)===JSON.stringify(b);
    report.static.push({station:station.id,stable});
    if(!stable)report.failures.push(`static ${station.id}: changed composition`);
  }
  await clickMotion();
  const gift=stations.at(-1); await goto(gift);
  const y=await c.evaluate('scrollY');
  for(let i=1;i<=4;i++)await click(`.jos-panel-on .jos-gift-card:nth-child(${i})`);
  report.interactions.push({kind:'gift',before:y,after:await c.evaluate('scrollY'),flipped:await c.evaluate('document.querySelectorAll(".jos-panel-on .jos-gift-card-flipped").length')});
  await click('.jos-panel-on .jos-more-btn');
  const toggles=await c.evaluate(`[...document.querySelectorAll('.jos-more-card button,.jos-more-card input')].map(e=>({text:e.textContent,aria:e.getAttribute('aria-label'),type:e.type}))`);
  report.toggles=toggles;
  // 真實點擊「只留下神說『我』的地方」。
  const toggle=await c.evaluate(`(()=>{const e=document.querySelector('.jos-more-card [data-coach="only-i-btn"]');if(!e)return null;const r=e.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2};})()`);
  if(toggle){await c.send('Input.dispatchMouseEvent',{type:'mousePressed',...toggle,button:'left',clickCount:1});await c.send('Input.dispatchMouseEvent',{type:'mouseReleased',...toggle,button:'left',clickCount:1});}
  else report.failures.push('onlyI toggle missing');
  const ys=[];for(let i=0;i<112;i++){ys.push(await c.evaluate('scrollY'));await sleep(80);}
  report.interactions.push({kind:'more/onlyI',before:y,after:await c.evaluate('scrollY'),samples:ys,onlyI:await c.evaluate('window.__josState.onlyI')});
  for(const interaction of report.interactions)if(interaction.before!==interaction.after||interaction.samples?.some(v=>v!==y))report.failures.push(`${interaction.kind}: scroll changed`);
  if(report.interactions.find(x=>x.kind==='gift').flipped!==4)report.failures.push('gift cards: expected all four flipped');
  if(!report.interactions.at(-1).onlyI)report.failures.push('onlyI toggle did not change state');
  report.errors=c.consoleLog.filter(s=>/^\[(error|exception)\]/.test(s));
  if(report.errors.length)report.failures.push(...report.errors);
  report.storyShare=await c.evaluate(`(()=>{const beats=[...document.querySelectorAll('section[data-beat-id]')],act=beats.filter(e=>e.dataset.segId==='act-2');return act.reduce((n,e)=>n+e.offsetHeight,0)/beats.reduce((n,e)=>n+e.offsetHeight,0)})()`);
} finally {
  writeFileSync(resolve(out,`report-${device}.json`),JSON.stringify(report,null,2));
  clearInterval(keepAlive);await c.close();
}
console.log(JSON.stringify({device,shots:report.shots.length,samples:report.samples.length,static:report.static.length,failures:report.failures},null,2));
process.exit(report.failures.length?1:0);
