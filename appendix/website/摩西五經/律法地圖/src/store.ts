import type { Depth } from './data/types';

/**
 * 全站狀態：閱讀深度、書卷篩選、足跡、對照清單、深淺色、大字。
 * 個人偏好存 localStorage（前綴 lawmap:），讀寫都包 try/catch——私密視窗或被擋時照樣能用。
 */
const KEY = 'lawmap:';
const load = <T>(k: string, fallback: T): T => {
  try {
    const v = localStorage.getItem(KEY + k);
    return v === null ? fallback : (JSON.parse(v) as T);
  } catch {
    return fallback;
  }
};
const save = (k: string, v: unknown) => {
  try {
    localStorage.setItem(KEY + k, JSON.stringify(v));
  } catch {
    /* 存不了就算了，只是偏好 */
  }
};

export const DEPTHS: Depth[] = ['basic', 'study', 'research'];
export const DEPTH_LABEL: Record<Depth, string> = { basic: '入門', study: '查經', research: '研究' };
export const depthRank = (d: Depth) => DEPTHS.indexOf(d);

export interface TrailItem {
  hash: string;
  label: string;
}

type Topic = 'depth' | 'books' | 'trail' | 'compare' | 'prefs';
const listeners = new Map<Topic, Set<() => void>>();

export const store = {
  /** 第一次來預設入門 */
  depth: load<Depth>('depth', 'basic'),
  /** 書卷篩選：空集合＝全部 */
  books: new Set<string>(load<string[]>('books', [])),
  trail: [] as TrailItem[],
  compare: load<string[]>('compare', []),
  theme: load<'auto' | 'light' | 'dark'>('theme', 'auto'),
  big: load<boolean>('big', false),

  on(topic: Topic, fn: () => void) {
    if (!listeners.has(topic)) listeners.set(topic, new Set());
    listeners.get(topic)!.add(fn);
  },
  emit(topic: Topic) {
    listeners.get(topic)?.forEach((fn) => fn());
  },

  setDepth(d: Depth) {
    if (d === this.depth) return;
    this.depth = d;
    save('depth', d);
    this.emit('depth');
  },
  /** 深度至少到某一層 */
  atLeast(d: Depth) {
    return depthRank(this.depth) >= depthRank(d);
  },

  toggleBook(name: string) {
    if (this.books.has(name)) this.books.delete(name);
    else this.books.add(name);
    save('books', [...this.books]);
    this.emit('books');
  },
  clearBooks() {
    this.books.clear();
    save('books', []);
    this.emit('books');
  },
  bookVisible(name: string) {
    return this.books.size === 0 || this.books.has(name);
  },

  visit(item: TrailItem) {
    this.trail = [item, ...this.trail.filter((t) => t.hash !== item.hash)].slice(0, 8);
    this.emit('trail');
  },

  toggleCompare(id: string) {
    this.compare = this.compare.includes(id) ? this.compare.filter((x) => x !== id) : [...this.compare, id].slice(-4);
    save('compare', this.compare);
    this.emit('compare');
  },

  setTheme(t: 'auto' | 'light' | 'dark') {
    this.theme = t;
    save('theme', t);
    this.emit('prefs');
  },
  setBig(b: boolean) {
    this.big = b;
    save('big', b);
    this.emit('prefs');
  },
};

/** 只看網址就能決定深度（分享連結時用 ?d=research） */
export function applyQuery(q: URLSearchParams) {
  const d = q.get('d');
  if (d && (DEPTHS as string[]).includes(d)) store.setDepth(d as Depth);
}
