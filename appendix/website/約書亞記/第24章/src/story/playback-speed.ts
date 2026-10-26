export const PLAYBACK_SPEEDS = [
  { value: 0.75, label: '慢（0.75×）' },
  { value: 1, label: '標準（1×）' },
  { value: 1.5, label: '快（1.5×）' },
  { value: 2, label: '很快（2×）' },
] as const;

export const DEFAULT_PLAYBACK_RATE = 1;
const STORAGE_KEY = 'jos24-playback-rate';

export function sentenceRevealSeconds(rate = 1): number {
  return Math.max(0.3, 0.8 / rate);
}

export function parsePlaybackRate(value: string | null): number {
  const rate = Number(value);
  return PLAYBACK_SPEEDS.some(option => option.value === rate) ? rate : DEFAULT_PLAYBACK_RATE;
}

export function readPlaybackRate(): number {
  try {
    if (typeof window === 'undefined') return DEFAULT_PLAYBACK_RATE;
    return parsePlaybackRate(window.localStorage.getItem(STORAGE_KEY));
  } catch {
    return DEFAULT_PLAYBACK_RATE;
  }
}

export function savePlaybackRate(rate: number): void {
  try {
    if (typeof window !== 'undefined') window.localStorage.setItem(STORAGE_KEY, String(parsePlaybackRate(String(rate))));
  } catch {
    // localStorage 在 file:// 或無痕環境可能不可用。
  }
}

/** Advance one autoplay frame. Velocity is in CSS pixels per wall-clock second. */
export function stepAutoplayFrame(
  position: number,
  velocity: number,
  baseSpeed: number,
  dt: number,
  rate: number,
  paused = false,
): { position: number; velocity: number } {
  const frameSeconds = Number.isFinite(dt) ? Math.max(0, Math.min(0.05, dt)) : 0;
  const playbackSeconds = frameSeconds * rate;
  const targetSpeed = paused ? 0 : baseSpeed * rate;
  const easing = 1 - Math.exp(-playbackSeconds * 4);
  const nextVelocity = velocity + (targetSpeed - velocity) * easing;
  return { position: position + nextVelocity * frameSeconds, velocity: nextVelocity };
}
