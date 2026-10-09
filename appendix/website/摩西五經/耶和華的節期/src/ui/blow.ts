/**
 * 吹角的介面層：圓形大按鈕「吹」（規格同 bake 的長按）。
 * - 滑鼠、觸控按住，或鍵盤按住空白鍵／Enter 都算；放開就停。
 * - 按住時 story.blow.level 在 1.2 秒內從 0 升到 1；放開後 0.6 秒內回落到 0。
 * - level 第一次到 1：blasts += 1、done = true。放開再按，再到 1 又算一聲（按鈕不會鎖死，讀者可以多吹幾次）。
 * - 讀者捲過這一拍還沒做：auto = true、done = true（sync）。不補畫聲波（level 維持 0）。
 * - 讀者觸發的動作：動態開關不影響，照常播放。
 * - 迴圈只在按住或 level > 0 時跑；pointerdown／keydown 會叫醒它；dt 夾在 0–0.1。
 * - 聲音由 audio.blow 合成（WebAudio），受聲音開關控制；沒有場景時也能用（只改 story 狀態與聲音）。
 */
import { SITE } from '../data/site';
import { story } from '../story/state';
import { clamp, h } from './dom';
import { makeFold } from './fold';

const RISE = 1 / 1.2; // 每秒
const FALL = 1 / 0.6; // 每秒
/** 吹滿一聲之後，level 要先落到這個值以下，再吹滿才算下一聲 */
const REARM = 0.2;

export interface BlowUI {
  controls(prompt: string): HTMLElement;
  /** 目前所在的拍（整份故事裡的序號）改變時呼叫：捲過去沒做就補完 */
  sync(index: number): void;
}

export function createBlowUI(onVoice: (holding: boolean, level: number) => void): BlowUI {
  const blowIndex = SITE.chapters.flatMap((c) => c.beats).findIndex((b) => b.interaction === 'blow');
  const held = new Set<string>();
  let raf = 0;
  let last = 0;
  let armed = true;
  let btn: HTMLButtonElement | null = null;
  let status: HTMLElement | null = null;
  let lastSig = '';

  function statusText(): string {
    const b = story.blow;
    if (b.auto && b.blasts === 0) return '已替你吹過';
    if (b.blasts > 0) return b.blasts === 1 ? '吹了一聲' : `吹了 ${b.blasts} 聲`;
    return b.holding ? '吹著' : '還沒有吹';
  }

  function render() {
    const b = story.blow;
    const sig = `${Math.round(b.level * 200)}|${b.done}|${b.auto}|${b.blasts}|${b.holding}`;
    if (sig === lastSig) return;
    lastSig = sig;
    if (btn) {
      btn.style.setProperty('--p', b.level.toFixed(3));
      btn.classList.toggle('is-held', b.holding);
    }
    if (status) status.textContent = statusText();
  }

  function step(now: number) {
    raf = 0;
    const dt = Math.min(0.1, Math.max(0, (now - last) / 1000));
    last = now;
    const b = story.blow;
    b.holding = held.size > 0;
    if (b.holding) {
      b.level = clamp(b.level + RISE * dt);
      if (b.level >= 1 && armed) {
        armed = false;
        b.blasts += 1;
        b.done = true;
      }
    } else {
      b.level = clamp(b.level - FALL * dt);
      if (b.level <= REARM) armed = true;
    }
    onVoice(b.holding, b.level);
    render();
    if (b.holding || b.level > 0) raf = requestAnimationFrame(step);
  }

  function wake() {
    if (!raf) {
      last = performance.now();
      raf = requestAnimationFrame(step);
    }
  }

  function press(src: string) {
    held.add(src);
    story.blow.holding = true;
    // 在按下的手勢裡先呼叫一次，WebAudio 才能建立／恢復 AudioContext
    onVoice(true, story.blow.level);
    wake();
    render();
  }
  function release(src: string) {
    if (!held.delete(src)) return;
    if (!held.size) story.blow.holding = false;
    wake();
    render();
  }

  function controls(prompt: string): HTMLElement {
    const button = h('button', { type: 'button', class: 'jf-bake-btn jf-blow-btn', 'aria-describedby': 'jf-blow-prompt' },
      h('span', { class: 'jf-bake-label' }, '吹'));
    btn = button;
    button.addEventListener('pointerdown', (e) => {
      if (e.button > 0) return;
      e.preventDefault();
      try {
        button.setPointerCapture(e.pointerId);
      } catch {
        /* 沒有 capture 也照常 */
      }
      press(`p${e.pointerId}`);
    });
    const up = (e: PointerEvent) => release(`p${e.pointerId}`);
    button.addEventListener('pointerup', up);
    button.addEventListener('pointercancel', up);
    button.addEventListener('lostpointercapture', up);
    button.addEventListener('contextmenu', (e) => e.preventDefault());
    button.addEventListener('keydown', (e) => {
      if (e.key !== ' ' && e.key !== 'Enter') return;
      e.preventDefault();
      if (!e.repeat) press('key');
    });
    button.addEventListener('keyup', (e) => {
      if (e.key !== ' ' && e.key !== 'Enter') return;
      e.preventDefault();
      release('key');
    });
    button.addEventListener('blur', () => release('key'));

    status = h('p', { class: 'jf-bake-status jf-blow-status', role: 'status', 'aria-live': 'polite' });
    lastSig = '';
    render();
    return h('div', { class: 'jf-interact jf-bake jf-blow' },
      h('div', { class: 'jf-bake-row' },
        button,
        h('div', { class: 'jf-bake-side' },
          h('p', { class: 'jf-prompt', id: 'jf-blow-prompt' }, prompt),
          h('div', { class: 'jf-status-row' }, status, makeFold()))));
  }

  function sync(index: number) {
    if (blowIndex < 0 || index <= blowIndex) return;
    const b = story.blow;
    if (b.done) return;
    // 捲過去沒做：記一筆已完成，不補畫聲波（level 維持 0）
    held.clear();
    b.holding = false;
    b.done = true;
    b.auto = true;
    render();
  }

  return { controls, sync };
}
