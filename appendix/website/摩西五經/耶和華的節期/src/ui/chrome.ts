/**
 * 標題列（站名＋「怎麼讀」＋聲音開關）、往下捲提示。
 * 聲音開關：桌機在右下角，手機移到標題列（右下角會壓到貼底的說明框）。
 */
import { SITE } from '../data/site';
import type { AudioController } from '../audio/audio';
import { h, s } from './dom';

function eqIcon(): SVGElement {
  const bar = (x: number, i: number) => s('rect', { x, y: 2, width: 3, height: 16, rx: 1.5, class: `jf-eq-bar jf-eq-${i}` });
  return s('svg', { class: 'jf-eq', viewBox: '0 0 22 20', width: 22, height: 20, 'aria-hidden': 'true', focusable: 'false' },
    bar(2, 1), bar(7.5, 2), bar(13, 3), bar(18.5, 4));
}

export function createChrome(host: HTMLElement, audio: AudioController, openCoach: () => void): void {
  const sound = h('button', { type: 'button', class: 'jf-btn jf-sound', 'aria-pressed': 'false' }, eqIcon(), h('span', null, '聲音'));
  sound.addEventListener('click', () => audio.setEnabled(!audio.enabled));
  audio.onChange((on) => sound.setAttribute('aria-pressed', on ? 'true' : 'false'));

  const help = h('button', { type: 'button', class: 'jf-btn jf-help', onclick: openCoach }, '怎麼讀');

  host.append(
    // 手機：捲到章末、頁尾（紙色底的文字）時，頂部的標題列與月份導覽墊一層紙色，才不會壓在文字上
    h('div', { class: 'jf-topbg', 'aria-hidden': 'true' }),
    h('header', { class: 'jf-top' },
      h('p', { class: 'jf-brand' }, SITE.title),
      h('div', { class: 'jf-bar' }, sound, help)),
    h('p', { class: 'jf-scrollcue', 'aria-hidden': 'true' },
      h('span', null, '往下捲'),
      s('svg', { viewBox: '0 0 16 22', width: 16, height: 22, 'aria-hidden': 'true' },
        s('path', { d: 'M8 2 v16 M2 12 l6 7 l6 -7', fill: 'none', stroke: 'currentColor', 'stroke-width': 2.5, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }))),
  );
}
