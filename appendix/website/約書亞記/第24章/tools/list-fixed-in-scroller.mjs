// 列出放在觸控專用捲動區（#jos-scroll）裡、卻固定在畫面上的元件。
// iPhone Safari 捲動時，這些元件會被系統一格一格來回修正位置而抖動（2026-10-28 使用者錄影），應該一個都沒有。
import { launch, sleep } from './cdp.mjs';
import { siteUrl } from './site-server.mjs';
const c = await launch({ width: 852, height: 393, mobile: true, dpr: 3, port: 9514 });
const ka = setInterval(() => {}, 1000);
try {
  await c.send('Page.navigate', { url: siteUrl });
  for (let i = 0; i < 60; i++) { if (await c.evaluate('!!window.__josState')) break; await sleep(500); }
  await sleep(2500);
  const list = await c.evaluate(`(()=>{const box=document.getElementById('jos-scroll');if(!box)return ['（沒有專用捲動區）'];
    const out=[];for(const e of box.querySelectorAll('*')){const cs=getComputedStyle(e);if(cs.position!=='fixed'&&cs.position!=='sticky')continue;
      if(e.parentElement.closest('#jos-scroll *')&&[...out].some(o=>o.el.contains(e)))continue;
      out.push({el:e,d:cs.position+' '+e.tagName.toLowerCase()+(e.id?'#'+e.id:'')+'.'+[...e.classList].join('.')+' z='+cs.zIndex});}
    return out.map(o=>o.d)})()`);
  console.log(list.length ? list.join('\n') : '捲動區裡沒有固定元件');
  console.log('共', list.length);
} finally { clearInterval(ka); await c.close(); }
