/**
 * 聲音：預設關閉；讀者按下開關才建立 <audio> 元素（不用 Web Audio，file:// 也能播）。
 * - 環境音（night-wind、depart）用 requestAnimationFrame 淡入淡出。
 * - 單次音效（lamb、dip、strike、door）直接播放；wailing 進入時淡入、離開時淡出。
 * - 檔案載入或播放失敗一律安靜略過。
 * 音檔清單與授權在 data/audio-sources.yaml，授權頁由 src/ui/ending.ts 列出。
 */
import type { AudioSource } from '../data/types';
import type { SceneEvent } from '../scene/api';

interface Track {
  id: string;
  file: string;
  loop: boolean;
  /** 這個音檔的最大音量（0–1） */
  max: number;
  /** 淡入、淡出各要幾秒（從 0 到 max） */
  fadeIn: number;
  fadeOut: number;
  el: HTMLAudioElement | null;
  vol: number;
  want: number;
  /** 在手勢內解鎖過（iOS／Safari 要求每個元素都先在讀者操作時播過一次） */
  ready: boolean;
  failed: boolean;
}

const SPEC: Record<string, Pick<Track, 'max' | 'fadeIn' | 'fadeOut'>> = {
  'night-wind': { max: 0.5, fadeIn: 2.2, fadeOut: 1.6 },
  depart: { max: 0.55, fadeIn: 1.8, fadeOut: 1.8 },
  wailing: { max: 0.7, fadeIn: 0.9, fadeOut: 1.4 },
  lamb: { max: 0.9, fadeIn: 0.05, fadeOut: 0.8 },
  dip: { max: 0.9, fadeIn: 0.02, fadeOut: 0.3 },
  strike: { max: 0.95, fadeIn: 0.02, fadeOut: 0.3 },
  door: { max: 0.9, fadeIn: 0.02, fadeOut: 0.6 },
};

export interface AudioController {
  readonly enabled: boolean;
  setEnabled(on: boolean): void;
  /** 目前所在的拍改變時呼叫 */
  onBeat(index: number): void;
  onSceneEvent(e: SceneEvent): void;
  onChange(cb: (enabled: boolean) => void): void;
}

export function createAudio(sources: AudioSource[], cues: string[], hasScene: () => boolean): AudioController {
  const tracks = new Map<string, Track>();
  for (const s of sources) {
    const spec = SPEC[s.id] ?? { max: 0.7, fadeIn: 1, fadeOut: 1 };
    tracks.set(s.id, { id: s.id, file: s.file, loop: !!s.loop, ...spec, el: null, vol: 0, want: 0, ready: false, failed: false });
  }
  const listeners: ((on: boolean) => void)[] = [];
  let enabled = false;
  let beat = 0;
  let raf = 0;
  let last = 0;

  const idxOf = (cue: string) => cues.indexOf(cue);

  function make(t: Track) {
    if (t.el || t.failed) return;
    const el = new Audio();
    el.preload = 'auto';
    el.loop = t.loop;
    el.addEventListener('error', () => {
      t.failed = true;
    });
    el.src = `./audio/${t.file}`;
    t.el = el;
    // 在讀者按下開關的手勢裡先靜音播一下再停，之後才能由捲動自動播放
    el.muted = true;
    const p = el.play();
    const done = () => {
      try {
        el.pause();
        el.currentTime = 0;
      } catch {
        /* 略過 */
      }
      el.muted = false;
      t.ready = true;
      reapply();
    };
    if (p && typeof p.then === 'function') p.then(done, () => {
      el.muted = false;
      t.ready = true;
      reapply();
    });
    else done();
  }

  function play(t: Track, force = false) {
    const el = t.el;
    if (!el || !t.ready || t.failed || !el.paused) return;
    // 播完的單次音效不因為重新判斷而再播一次
    if (!t.loop && el.ended && !force) return;
    const p = el.play();
    if (p && typeof p.catch === 'function') p.catch(() => undefined);
  }

  function frame(now: number) {
    raf = 0;
    const dt = Math.min(0.1, Math.max(0, (now - last) / 1000));
    last = now;
    let busy = false;
    for (const t of tracks.values()) {
      const el = t.el;
      if (!el) continue;
      if (t.vol !== t.want) {
        const rate = (t.want > t.vol ? 1 / t.fadeIn : 1 / t.fadeOut) * t.max;
        t.vol = t.want > t.vol ? Math.min(t.want, t.vol + rate * dt) : Math.max(t.want, t.vol - rate * dt);
        el.volume = Math.min(1, Math.max(0, t.vol));
        busy = true;
      }
      if (t.want === 0 && t.vol === 0 && !el.paused) el.pause();
    }
    if (busy) raf = requestAnimationFrame(frame);
  }

  function kick() {
    if (!raf) {
      last = performance.now();
      raf = requestAnimationFrame(frame);
    }
  }

  /** 設定某個音檔的目標音量並確保它在播（want > 0）或淡出後停（want = 0） */
  function setWant(id: string, want: number, restart = false) {
    const t = tracks.get(id);
    if (!t || !enabled) return;
    if (!t.el) make(t);
    if (!t.el || t.failed) return;
    t.want = want;
    if (want > 0) {
      if (restart) {
        try {
          t.el.currentTime = 0;
        } catch {
          /* 還沒載入完：從頭開始播即可 */
        }
      }
      play(t, restart);
    }
    kick();
  }

  /** 照目前所在的拍，重新決定環境音與 wailing 該不該響 */
  function reapply() {
    if (!enabled || document.hidden) return;
    const cue = cues[beat];
    const mid = idxOf('midnight');
    const dep = idxOf('depart');
    const vig = idxOf('vigil');
    setWant('night-wind', mid < 0 || beat < mid ? SPEC['night-wind'].max : 0);
    setWant('depart', dep >= 0 && beat >= dep && beat <= (vig < 0 ? dep : vig) ? SPEC.depart.max : 0);
    setWant('wailing', cue === 'wailing' ? SPEC.wailing.max : 0);
  }

  function fire(id: string) {
    const t = tracks.get(id);
    if (!t || !enabled) return;
    if (!t.el) make(t);
    if (!t.el || t.failed) return;
    t.vol = t.want = t.max;
    t.el.volume = t.max;
    try {
      t.el.currentTime = 0;
    } catch {
      /* 略過 */
    }
    play(t, true);
  }

  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      for (const t of tracks.values()) t.el?.pause();
    } else {
      reapply();
    }
  });

  return {
    get enabled() {
      return enabled;
    },
    setEnabled(on: boolean) {
      if (on === enabled) return;
      enabled = on;
      if (on) {
        for (const t of tracks.values()) make(t);
        reapply();
      } else {
        for (const t of tracks.values()) {
          t.want = 0;
          t.vol = 0;
          t.el?.pause();
        }
      }
      for (const cb of listeners) cb(enabled);
    },
    onBeat(index: number) {
      const prev = cues[beat];
      beat = index;
      const cue = cues[index];
      if (!enabled) return;
      if (cue !== prev) {
        if (cue === 'day-10') {
          setWant('lamb', SPEC.lamb.max, true);
        }
        // 場景載不進來時沒有 door-shut 事件，改在進入那一拍時播關門聲
        if (cue === 'door-shut' && !hasScene()) fire('door');
        if (cue === 'wailing') {
          setWant('wailing', SPEC.wailing.max, true);
        }
        if (prev === 'day-10') setWant('lamb', 0);
      }
      reapply();
    },
    onSceneEvent(e: SceneEvent) {
      if (e.type === 'hyssop-dip') fire('dip');
      else if (e.type === 'hyssop-strike') fire('strike');
      else if (e.type === 'door-shut') fire('door');
    },
    onChange(cb) {
      listeners.push(cb);
    },
  };
}
