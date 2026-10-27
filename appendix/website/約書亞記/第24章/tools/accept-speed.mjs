import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { launch, sleep } from './cdp.mjs';
import { siteUrl } from './site-server.mjs';

const device = process.argv[2] || 'desktop', mobile = device === 'mobile';
const out = resolve('.tmp-shots/speed'); mkdirSync(out, { recursive: true });
const site = JSON.parse(readFileSync('src/data/site.json', 'utf8'));
const report = { device, distances: [], holds: [], stones: [], bubbles: [], failures: [] };
const c = await launch({ port: 9484, gpu: true, width: mobile ? 844 : 1440, height: mobile ? 390 : 900, mobile });
async function wait(expression, seconds = 20) {
  for (let i = 0; i < seconds * 10; i++) { if (await c.evaluate(expression)) return; await sleep(100); }
  throw new Error('Timed out: ' + expression);
}
const choose = async rate => c.evaluate(`(()=>{const s=document.querySelector('.jos-speed-select');s.value='${rate}';s.dispatchEvent(new Event('change',{bubbles:true}));return window.__josState.playbackRate})()`);
async function goto(id, p = .5) {
  await c.evaluate(`(()=>{if(window.__josState.autoplaying)document.querySelector('.jos-autoplay').click();const e=document.getElementById('jos-beat-${id}');scrollTo({top:scrollY+e.getBoundingClientRect().top-innerHeight*.36+${p}*e.offsetHeight,behavior:'instant'})})()`);
  await wait(`window.__josState.beat==='${id}' && Math.abs(window.__josState.beatProgress-${p})<.002`);
  await sleep(350);
}
try {
  await c.send('Page.navigate', { url: siteUrl });
  await wait('!!window.__josScene && document.querySelectorAll("[data-beat-id]").length===36');
  await sleep(700);
  for (const rate of [.5, .75, 1, 1.5, 2]) {
    await c.evaluate(`if(window.__josState.autoplaying)document.querySelector('.jos-autoplay').click();scrollTo({top:0,behavior:'instant'})`);
    await choose(rate); await sleep(350);
    await c.shot(join(out, `${device}-${rate}-start.png`));
    const result = await c.evaluate(`new Promise(resolve=>{
      const start=performance.now(), y=scrollY, samples=[];
      function sample(){samples.push({t:performance.now()-start,y:scrollY});if(performance.now()-start<20000)requestAnimationFrame(sample)}
      document.querySelector('.jos-autoplay').click();requestAnimationFrame(sample);
      setTimeout(()=>{const result={rate:${rate},seconds:(performance.now()-start)/1000,distance:scrollY-y,playing:window.__josState.autoplaying,samples};document.querySelector('.jos-autoplay').click();resolve(result)},20000);
    })`);
    await c.shot(join(out, `${device}-${rate}-20s.png`));
    if (!result.playing || result.distance <= 0) report.failures.push(`Stopped at ${rate}`);
    report.distances.push(result);
    console.log(`${device} ${rate}x 20s: ${result.distance}px`);
  }
  const standard = report.distances.find(r => r.rate === 1).distance;
  for (const result of report.distances) {
    result.ratio = result.distance / standard;
    result.relativeError = Math.abs(result.ratio / result.rate - 1);
    if (result.relativeError > .12) report.failures.push(`Distance ratio: ${result.rate} ${result.ratio}`);
  }
  // Real keyboard input while playing: select changes immediately, no restart.
  await c.evaluate("scrollTo({top:0,behavior:'instant'})"); await sleep(250); await choose(.75);
  await c.evaluate("document.querySelector('.jos-autoplay').click();document.querySelector('.jos-speed-select').focus()");
  await c.send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'ArrowDown', code: 'ArrowDown', windowsVirtualKeyCode: 40 });
  await c.send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'ArrowDown', code: 'ArrowDown', windowsVirtualKeyCode: 40 });
  await sleep(500);
  report.keyboard = await c.evaluate("({rate:window.__josState.playbackRate,playing:window.__josState.autoplaying,y:scrollY})");
  if (report.keyboard.rate !== 1 || !report.keyboard.playing) report.failures.push('Keyboard speed change stopped playback');
  await c.evaluate("document.querySelector('.jos-autoplay').click()");
  await choose(1.5); await c.send('Page.reload');
  await wait('!!window.__josState');
  report.persistedRate = await c.evaluate('window.__josState.playbackRate');
  if (report.persistedRate !== 1.5) report.failures.push('Speed did not persist');
  report.header = await c.evaluate(`(()=>{const e=document.querySelector('.jos-header'),r=e.getBoundingClientRect(),s=document.querySelector('.jos-speed-select').getBoundingClientRect();return {height:r.height,overflow:document.documentElement.scrollWidth-innerWidth,selectRight:s.right,selectBottom:s.bottom}})()`);
  if (report.header.overflow || report.header.selectRight > (mobile ? 844 : 1440) || report.header.selectBottom > report.header.height) report.failures.push('Speed control overflowed header');
  // The authored pause and automatic raising use playback time in every gear.
  for (const rate of [.5, .75, 1, 1.5, 2]) {
    await choose(rate); await goto('beat-18-cannot', .10);
    const hold = await c.evaluate(`new Promise(resolve=>{
      const start=performance.now(), y=scrollY;document.querySelector('.jos-autoplay').click();
      const timer=setInterval(()=>{if(scrollY-y>2){clearInterval(timer);resolve({rate:${rate},seconds:(performance.now()-start)/1000,y0:y,y1:scrollY})}},30);
      setTimeout(()=>{clearInterval(timer);resolve({rate:${rate},timeout:true})},12000);
    })`);
    report.holds.push(hold);
    if (hold.timeout || Math.abs(hold.seconds - 4.5 / (rate * 1.5)) > .65) report.failures.push(`Pause timing ${rate}: ${hold.seconds}`);
    await goto('beat-26-raise', .05);
    const stone = await c.evaluate(`new Promise(resolve=>{
      Object.assign(window.__josState.raiseStone,{done:false,progress:0,holding:false});
      const start=performance.now();document.querySelector('.jos-autoplay').click();
      const timer=setInterval(()=>{if(window.__josState.raiseStone.done){clearInterval(timer);resolve({rate:${rate},seconds:(performance.now()-start)/1000})}},30);
      setTimeout(()=>{clearInterval(timer);resolve({rate:${rate},timeout:true})},6500);
    })`);
    report.stones.push(stone);
    if (stone.timeout || Math.abs(stone.seconds - 3 / (rate * 1.5)) > .4) report.failures.push(`Stone timing ${rate}: ${stone.seconds}`);
  }
  // Check every line of all three changed dialogues, without truncating text.
  for (const index of [4, 11, 33]) {
    const beat = site.segments.flatMap(s=>s.beats)[index];
    for (const [i, line] of beat.familyLines.entries()) {
      await goto(beat.id, (i + .5) / beat.familyLines.length);
      const bubble = await c.evaluate(`(()=>{
        const e=document.querySelector('.jos-panel-on .jos-bubble-line'),text=e.firstChild,range=document.createRange();range.selectNodeContents(text);
        const rects=[...range.getClientRects()],box=e.parentElement.parentElement.getBoundingClientRect();
        return {text:text.textContent,lines:new Set(rects.map(r=>Math.round(r.top))).size,left:box.left,right:box.right,top:box.top,bottom:box.bottom};
      })()`);
      report.bubbles.push({ beat: beat.id, index: i, ...bubble });
      if (!bubble.text.includes(line.text) || bubble.lines > 2 || bubble.left < 0 || bubble.right > (mobile ? 844 : 1440)) report.failures.push(`Dialogue overflow: ${beat.id} line ${i}`);
      await c.shot(join(out, `${device}-${beat.id}-line${i}.png`));
    }
  }
  const blocked = await c.send('Page.addScriptToEvaluateOnNewDocument', { source: "Object.defineProperty(window,'localStorage',{get(){throw new DOMException('Blocked','SecurityError')}})" });
  await c.send('Page.reload'); await wait('!!window.__josState');
  report.blockedStorageRate = await c.evaluate('window.__josState.playbackRate');
  await choose(2);
  report.blockedStorageChange = await c.evaluate('window.__josState.playbackRate');
  if (report.blockedStorageRate !== 1 || report.blockedStorageChange !== 2) report.failures.push('Storage fallback failed');
  await c.send('Page.removeScriptToEvaluateOnNewDocument', { identifier: blocked.identifier });
  report.errors = c.consoleLog.filter(s => /^\[(error|exception)\]/.test(s));
  report.failures.push(...report.errors);
} finally {
  writeFileSync(join(out, `${device}.json`), JSON.stringify(report, null, 2));
  console.log(JSON.stringify({ device, distances: report.distances.map(({samples,...r})=>r), holds: report.holds, stones: report.stones, header: report.header, bubbles: report.bubbles, failures: report.failures }));
  await c.close();
}
if (report.failures.length) process.exitCode = 1;
