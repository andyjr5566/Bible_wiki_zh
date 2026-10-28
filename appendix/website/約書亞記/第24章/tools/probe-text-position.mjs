// 每一拍：列出畫面上應該看得到的字（經文、泡泡、小卡）實際落在哪裡，標出跑出畫面、被頂列蓋住的。
// 2026-10-28 手機橫擺第 9、10 拍的經文被舊的逐拍位移規則推到畫面外，使用者看到整拍沒有字。
// SIZE=932x430（預設）FRACS=0.15,0.5,0.85 OUT=截圖資料夾；最後一行印出有問題的數量。
import { launch, sleep } from './cdp.mjs';
import { siteUrl } from './site-server.mjs';
const [W, H] = (process.env.SIZE ?? '932x430').split('x').map(Number);
const OUT = process.env.OUT;
const c = await launch({ width: W, height: H, mobile: process.env.DESK !== '1', dpr: 2, port: Number(process.env.PORT ?? 9532) });
const ka = setInterval(() => {}, 1000);
try {
  await c.send('Page.navigate', { url: siteUrl });
  for (let i = 0; i < 60; i++) { if (await c.evaluate('!!window.__josState')) break; await sleep(500); }
  await sleep(2500);
  const ids = await c.evaluate(`[...document.querySelectorAll('section[data-beat-id]')].map(e=>e.dataset.beatId)`);
  let bad = 0;
  const fr = (process.env.FRACS ?? '0.5').split(',').map(Number);
  for (const id of ids) for (const f of fr) {
    await c.evaluate(`(()=>{const e=document.querySelector('section[data-beat-id="${id}"]');const r=e.getBoundingClientRect();scrollTo({top:scrollY+r.top-innerHeight*.36+${f}*r.height,behavior:'instant'})})()`);
    await sleep(Number(process.env.WAIT ?? 2200));
    const r = await c.evaluate(`(()=>{const hb=document.querySelector('.jos-header').getBoundingClientRect().bottom;
      const sel='.jos-panel-on .jos-vbox, .jos-bubble, .jos-wcard, .jos-cannot-headline';
      const out=[];
      for(const e of document.querySelectorAll(sel)){const cs=getComputedStyle(e);if(cs.display==='none'||cs.visibility==='hidden')continue;
        const b=e.getBoundingClientRect();if(!b.width||!b.height)continue;if(+cs.opacity<0.05)continue;
        const txt=(e.innerText||'').replace(/\s+/g,'').slice(0,14);if(!txt)continue;
        const flags=[];if(b.top<hb-2)flags.push('頂列下/上方');if(b.bottom>innerHeight+2)flags.push('超出下緣'+Math.round(b.bottom-innerHeight));if(b.left<-2||b.right>innerWidth+2)flags.push('超出左右');if(b.bottom<0||b.top>innerHeight)flags.push('完全在外');
        out.push((e.className.split(' ').find(k=>k.startsWith('jos-vbox-')||k.startsWith('jos-bubble')||k.startsWith('jos-wcard')||k.startsWith('jos-cannot'))||e.className)+' ['+[b.left,b.top,b.width,b.height].map(Math.round).join(',')+'] '+txt+(flags.length?'  <<'+flags.join(','):''));}
      return {hb:Math.round(hb),out};})()`);
    bad += r.out.filter(x => x.includes('<<')).length;
    console.log(`${id}@${f} hb=${r.hb}\n   ` + (r.out.length ? r.out.join('\n   ') : '（沒有任何文字）'));
    if (OUT) await c.shot(`${OUT}/${id}-${Math.round(f*100)}.png`);
  }
  console.log('有問題的文字', bad, '處');
} finally { clearInterval(ka); await c.close(); }
