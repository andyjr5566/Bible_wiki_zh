// 極簡 CDP 驅動：啟動自己的 headless Chrome（固定 jos-shoot- 前綴的 user-data-dir），只關自己開的 Chrome。
import { spawn } from 'node:child_process';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve, basename, dirname } from 'node:path';

const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export async function launch({
  width = 1440,
  height = 900,
  mobile = false,
  dpr = 1,
  port = 9344,
  headless = true,
  gpu = false,
  ua = null,
  connectOnly = process.env.JOS_CDP_EXTERNAL === '1',
} = {}) {
  // Node 的 WebSocket 握手不一定維持事件迴圈；本機伺服器則刻意 unref。
  const lifetime = setInterval(() => {}, 1000);
  const dir = connectOnly ? null : mkdtempSync(join(tmpdir(), 'jos-shoot-'));
  const args = [
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${dir}`,
    '--no-first-run',
    '--no-default-browser-check',
    '--hide-scrollbars',
    '--mute-audio',
    '--ignore-gpu-blocklist',
    '--autoplay-policy=no-user-gesture-required',
    `--window-size=${width},${height}`,
  ];
  if (!gpu) args.push('--enable-unsafe-swiftshader', '--use-angle=swiftshader');
  else args.push('--use-angle=d3d11', '--enable-gpu-rasterization');
  if (headless) args.unshift('--headless=new');
  const proc = connectOnly ? null : spawn(CHROME, [...args, 'about:blank'], { stdio: 'ignore' });
  let ws;
  for (let i = 0; i < 60; i++) {
    try {
      const list = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
      const page = list.find((t) => t.type === 'page');
      if (page) {
        ws = new WebSocket(page.webSocketDebuggerUrl);
        break;
      }
    } catch {}
    await sleep(250);
  }
  if (!ws) { clearInterval(lifetime); throw new Error('Chrome 沒有開起來'); }
  await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('CDP connection timeout')), 15000);
    ws.addEventListener('open', () => { clearTimeout(timer); resolve(); }, { once: true });
    ws.addEventListener('error', () => { clearTimeout(timer); reject(new Error('CDP connection failed')); }, { once: true });
  }).catch(error => { clearInterval(lifetime); throw error; });
  let id = 0;
  const pending = new Map();
  ws.addEventListener('close', () => {
    clearInterval(lifetime);
    for (const request of pending.values()) request.reject(new Error('CDP connection closed'));
    pending.clear();
  });
  const listeners = [];
  ws.addEventListener('message', (e) => {
    const msg = JSON.parse(e.data);
    if (msg.id && pending.has(msg.id)) {
      const { resolve, reject } = pending.get(msg.id);
      pending.delete(msg.id);
      msg.error ? reject(new Error(JSON.stringify(msg.error))) : resolve(msg.result);
    } else if (msg.method) listeners.forEach((fn) => fn(msg));
  });
  const send = (method, params = {}) =>
    new Promise((resolve, reject) => {
      const i = ++id;
      pending.set(i, { resolve, reject });
      ws.send(JSON.stringify({ id: i, method, params }));
    });
  await send('Page.enable');
  await send('Runtime.enable');
  // 開頁的載入畫面會擋住點擊；檢查故事的工具預設把它藏起來（檢查載入畫面本身的工具設 JOS_KEEP_LOADER=1）
  if (process.env.JOS_KEEP_LOADER !== '1') {
    await send('Page.addScriptToEvaluateOnNewDocument', { source: `document.addEventListener('DOMContentLoaded', () => {
      const s = document.createElement('style'); s.textContent = '#jos-loading{display:none!important}'; document.head.appendChild(s); });` });
  }
  // 手機模式下網站在專用捲動區（#jos-scroll）裡捲；讓各工具沿用 window.scrollTo／scrollY 也能操作它
  await send('Page.addScriptToEvaluateOnNewDocument', { source: `(() => {
    const box = () => document.getElementById('jos-scroll');
    const nativeTo = window.scrollTo.bind(window), nativeBy = window.scrollBy.bind(window);
    window.scrollTo = function (a, b) { const e = box(); if (!e) return b === undefined ? nativeTo(a) : nativeTo(a, b);
      e.scrollTo({ top: typeof a === 'object' ? (a.top ?? e.scrollTop) : b, behavior: 'instant' }); };
    window.scrollBy = function (a, b) { const e = box(); if (!e) return b === undefined ? nativeBy(a) : nativeBy(a, b);
      e.scrollBy({ top: typeof a === 'object' ? (a.top ?? 0) : b, behavior: 'instant' }); };
    const desc = Object.getOwnPropertyDescriptor(window, 'scrollY') ?? Object.getOwnPropertyDescriptor(Window.prototype, 'scrollY');
    for (const name of ['scrollY', 'pageYOffset']) Object.defineProperty(window, name, { configurable: true,
      get() { const e = box(); return e ? e.scrollTop : desc.get.call(window); } });
  })();` });
  if (ua) await send('Network.setUserAgentOverride', { userAgent: ua });
  await send('Emulation.setDeviceMetricsOverride', {
    width,
    height,
    deviceScaleFactor: dpr,
    mobile,
  });
  if (mobile) {
    await send('Emulation.setTouchEmulationEnabled', { enabled: true, maxTouchPoints: 5 });
  }
  const consoleLog = [];
  listeners.push((m) => {
    if (m.method === 'Runtime.consoleAPICalled') {
      consoleLog.push(
        `[${m.params.type}] ${m.params.args.map((a) => a.value ?? a.description).join(' ')}`,
      );
    }
    if (m.method === 'Runtime.exceptionThrown') {
      consoleLog.push(
        `[exception] ${
          m.params.exceptionDetails.exception?.description ?? m.params.exceptionDetails.text
        }`,
      );
    }
  });
  const evaluate = async (expression) =>
    (await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true })).result
      .value;
  const shot = async (file) => {
    const { data } = await send('Page.captureScreenshot', { format: 'png' });
    const { writeFileSync } = await import('node:fs');
    writeFileSync(file, Buffer.from(data, 'base64'));
  };
  const wheel = async (dy, x = width / 2, y = height / 2) =>
    send('Input.dispatchMouseEvent', { type: 'mouseWheel', x, y, deltaX: 0, deltaY: dy });
  const click = async (x, y) => {
    await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x, y });
    await send('Input.dispatchMouseEvent', {
      type: 'mousePressed',
      x,
      y,
      button: 'left',
      clickCount: 1,
    });
    await send('Input.dispatchMouseEvent', {
      type: 'mouseReleased',
      x,
      y,
      button: 'left',
      clickCount: 1,
    });
  };
  const close = async () => {
    try {
      await send('Browser.close');
    } catch {}
    try {
      proc?.kill();
    } catch {}
    clearInterval(lifetime);
    await sleep(300);
    try {
      if (dir && dirname(resolve(dir)) === resolve(tmpdir()) && basename(dir).startsWith('jos-shoot-')) {
        rmSync(dir, { recursive: true, force: true });
      }
    } catch {}
  };
  const onEvent = (fn) => listeners.push(fn);
  return { send, evaluate, shot, wheel, click, close, consoleLog, dir, onEvent };
}
