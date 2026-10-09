// WebGL 不可用時的靜態插圖：用場景實驗室逐 cue 截圖，存成 public/fallback/<cue>.webp。
// 用法：先開 dev server（npx vite --port 3071 --strictPort），再 node tools/shoot-fallback.mjs [port]
import { mkdirSync, writeFileSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { launch, sleep } from './cdp.mjs';

const port = Number(process.argv[2] ?? 3071);
const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const out = join(root, 'public', 'fallback');
mkdirSync(out, { recursive: true });

// 每個 cue 取哪一個進度點：大多取中段；有動作的拍取動作完成之後
const SHOTS = [
  ['title', 0.5], ['month', 0.6], ['day-10', 0.6], ['day-14', 0.6],
  ['dusk-street', 0.6], ['hyssop', 0.5], ['door-shut', 0.8], ['meal', 0.5],
  ['midnight', 0.6], ['wailing', 0.5], ['depart', 0.5], ['vigil', 0.5], ['children', 0.5],
];

const b = await launch({ width: 1600, height: 1000, gpu: true, port: 9341 });
let failed = 0;
try {
  for (const [cue, p] of SHOTS) {
    await b.send('Page.navigate', { url: `http://127.0.0.1:${port}/scene-lab.html?cue=${cue}&p=${p}&ui=0&motion=1` });
    await sleep(3500);
    const info = await b.evaluate('JSON.stringify(window.__lab ? window.__lab.story.cue : null)');
    if (JSON.parse(info) !== cue) { console.log(`✗ ${cue}：實驗室沒有切到這個 cue（${info}）`); failed++; continue; }
    const { data } = await b.send('Page.captureScreenshot', { format: 'webp', quality: 72 });
    const file = join(out, `${cue}.webp`);
    writeFileSync(file, Buffer.from(data, 'base64'));
    console.log(`✓ ${cue}  ${(statSync(file).size / 1024).toFixed(0)} KB`);
  }
  if (b.consoleLog.some((l) => l.startsWith('[exception]') || l.startsWith('[error]'))) {
    console.log('console 有錯誤：\n' + b.consoleLog.filter((l) => /^\[(exception|error)\]/.test(l)).join('\n'));
    failed++;
  }
} finally {
  await b.close();
}
process.exit(failed ? 1 : 0);
