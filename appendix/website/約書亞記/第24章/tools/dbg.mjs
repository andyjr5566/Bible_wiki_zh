import { siteUrl } from './site-server.mjs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { launch, sleep } from './cdp.mjs';
const c = await launch({ width: 1440, height: 900, dpr: 1, port: 9431 });
const ka = setInterval(() => {}, 1000);
try {
  await c.send('Page.navigate', { url: siteUrl });
  for (let i = 0; i < 40; i++) { if (await c.evaluate('!!window.__josState')) break; await sleep(500); }
  await sleep(1500);
  console.log(await c.evaluate('({y:scrollY})'));
  await c.evaluate('location.hash = "#v=24:15"');
  for (let i = 0; i < 6; i++) { await sleep(700); console.log(await c.evaluate('({cue: window.__josState?.cue, y: scrollY})')); }
  await c.evaluate('location.hash = "#v=24:3"');
  for (let i = 0; i < 4; i++) { await sleep(700); console.log(await c.evaluate('({cue: window.__josState?.cue, y: scrollY})')); }
} finally { clearInterval(ka); await c.close(); }
