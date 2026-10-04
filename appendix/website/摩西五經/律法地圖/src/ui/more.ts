import type { Depth } from '../data/types';
import { DEPTH_LABEL, store } from '../store';
import { h, type Child } from './dom';

/**
 * 深入淺出的核心元件：一個就地展開的區塊。
 * - level：這個區塊屬於哪一層。目前的閱讀深度 ≥ level 時預設展開，否則收合。
 * - 收合列要寫清楚裡面有什麼（「經文裡提到 6 個人物、地點與背景」），不是只寫「更多」。
 * - 內容永遠在 DOM 裡：入門模式按一下一樣看得到研究層的資料，不會有死角。
 * 用原生 <details>：展開不換頁、不捲動頁面。
 */
export function more(level: Depth, summary: Child, ...content: Child[]): HTMLDetailsElement {
  const d = h('details', { class: `lm-more lm-lv-${level}`, 'data-level': level }, h('summary', null, h('span', { class: 'lm-more-label' }, summary), level !== 'basic' ? h('span', { class: 'lm-lv-tag' }, DEPTH_LABEL[level]) : null), h('div', { class: 'lm-more-body' }, ...content));
  d.open = store.atLeast(level);
  return d;
}

/** 依閱讀深度選用詞：入門用白話、研究用術語 */
export function lbl(basic: string, study = basic, research = study): string {
  return store.depth === 'basic' ? basic : store.depth === 'study' ? study : research;
}

/** 只在某一層以上才出現的小東西（數字、代號），不值得做成可展開區塊時用 */
export const at = (level: Depth, node: Child): Child => (store.atLeast(level) ? node : null);
