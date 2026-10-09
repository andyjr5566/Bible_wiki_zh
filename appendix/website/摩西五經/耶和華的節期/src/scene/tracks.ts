// 時間軸：s = cue 序號 + beatProgress。鏡頭、月亮、光線都是 s 的純函數（捲回去就倒回去）。
import { clamp, sampleKeys, smooth, type Key } from './util';

export const CUES = ['title', 'month', 'day-10', 'day-14', 'dusk-street', 'hyssop', 'door-shut', 'meal', 'midnight', 'wailing', 'depart', 'vigil', 'children'] as const;
export const CUE_IDX: Record<string, number> = {};
CUES.forEach((c, i) => (CUE_IDX[c] = i));
export const HYSSOP_IDX = CUE_IDX['hyssop'];
/** 抹除轉場全蓋的時刻：在這之後才切到隔日的世界 */
export const DAY_S = 11.93;

/** 隔天（應許之地）那一幕搭在遠處，與夜間世界分開 */
export const OX = 300;

// 鏡頭欄位：[px, py, pz, tx, ty, tz, fov(垂直度), fitW(目標處至少要容納的水平寬度，公尺)]
type Pose = [number, number, number, number, number, number, number, number];

const BEATS: Array<[Pose, Pose]> = [
  // 0 title：越過大麥田看遠方的村子，月亮是一彎細鉤
  [[0, 1.2, 36, 3, 3.3, -15, 56, 0], [0.3, 1.1, 32, 2, 3.2, -15, 56, 0]],
  // 1 month：鏡頭降進麥田，停在青穗上
  [[0.4, 1.0, 30, 1.5, 2.6, -6, 58, 0], [0.2, 0.55, 21, 0.8, 1.9, 4, 60, 0]],
  // 2 day-10：走到一家門口，羊羔拴在門邊
  [[-0.4, 0.9, 17, 0.8, 2.6, 0, 60, 0], [-1.9, 1.3, 8.2, 0.9, 2.2, 0, 58, 5.2]],
  // 3 day-14：滿月，收在那扇門
  [[-1.9, 1.3, 8.2, 0.9, 3.2, 0, 62, 5.2], [-0.2, 1.45, 6.6, 0, 1.55, 0, 46, 4.4]],
  // 4 dusk-street：黃昏的街，門口有人影
  [[-10, 2.0, 10, 3, 2.2, -1, 52, 0], [-8.4, 1.95, 8.2, 4.2, 2.3, -2, 50, 0]],
  // 5 hyssop：鏡頭推近正面看門
  [[0.3, 1.5, 5.7, 0.1, 1.2, 0, 40, 4.7], [0.15, 1.5, 5.2, 0.05, 1.2, 0, 40, 4.7]],
  // 6 door-shut
  [[0.5, 1.55, 5.8, 0.2, 1.35, 0, 40, 4.7], [2.2, 1.7, 8.6, 0.6, 1.6, 0, 44, 5.4]],
  // 7 meal：退一步，門關著，窗透光
  [[3.6, 1.8, 9.6, 0.6, 1.7, 0, 46, 6.2], [5.4, 1.9, 12, 1.0, 1.8, 0, 48, 8]],
  // 8 midnight：拉遠到整條街，月亮高掛
  [[0, 3.4, 34, 0, 9, 0, 64, 48], [0, 3.8, 36, 0, 9.5, 0, 64, 48]],
  // 9 wailing：轉向埃及人的城
  [[44, 3.2, 8, 46, 6, -30, 60, 0], [52, 2.4, -7, 46.5, 4.2, -22, 52, 11]],
  // 10 depart：月光下的隊伍往左走
  [[7, 2.7, 23, -2, 4.0, 3, 46, 0], [-4, 2.4, 22, -13, 4.2, 3, 46, 0]],
  // 11 vigil：仰起頭看天
  [[6, 1.6, 24, -26, 14.4, -27, 60, 0], [6, 1.5, 24, -26, 36, -27, 64, 0]],
  // 12 children：日後，應許之地
  [[OX - 1.6, 1.35, 8.6, OX + 0.2, 1.25, 0, 42, 4.6], [OX - 0.6, 1.35, 7.4, OX + 0.3, 1.3, 0, 42, 4.6]],
];

/** 手機（寬 ≤720px）：說明框蓋住下半，個別 cue 改用較遠的鏡頭，讓主體整個落在上半部 */
const MOBILE_OVERRIDE: Record<number, [Pose, Pose]> = {
  // 3 day-14：退到能同時看到滿月與門（門在說明框上緣之上）
  3: [[-0.3, 1.5, 18, 0, 1.4, 0, 46, 0], [-0.3, 1.5, 16.5, 0, 1.4, 0, 46, 0]],
  // 9 wailing：靠近那扇亮窗，人影才看得清楚；埃及城的燈在上方一盞盞熄滅
  9: [[50, 2.9, -1, 45.5, 3.8, -23, 52, 0], [49, 2.8, -4, 45.2, 3.9, -23, 50, 0]],
  // 10 depart：人群貼近鏡頭，才站得滿上半部
  10: [[7, 2.0, 20, -1, 1.2, 7, 46, 0], [-3, 2.0, 20, -11, 1.2, 7, 46, 0]],
};

function buildCam(mobile: boolean): Key[] {
  const out: Key[] = [];
  BEATS.forEach((pair, i) => {
    const [a, b] = mobile && MOBILE_OVERRIDE[i] ? MOBILE_OVERRIDE[i] : pair;
    if (i === 0) out.push({ s: 0, v: a, e: 0 });
    // children 的鏡頭要在抹除全蓋之前就到位（切場發生在 s≈11.93）
    out.push({ s: i === 12 ? 11.96 : i + 0.3, v: a, e: 0 });
    out.push({ s: i === 11 ? 11.9 : i + 1.0, v: b, e: 1 });
  });
  return out;
}
const CAM = buildCam(false);
const CAM_M = buildCam(true);

// 手機的月亮：直接指定月亮在畫面上的位置（避開標題列、日數牌、說明框）。[權重, 水平位置(0..1), 垂直位置(0..1, 由上往下)]
const MOON_S: Key[] = [
  { s: 0, v: [1, 0.46, 0.3], e: 1 },
  { s: 1, v: [1, 0.46, 0.3], e: 1 },
  { s: 2.5, v: [1, 0.46, 0.27], e: 1 },
  { s: 3.6, v: [1, 0.42, 0.25], e: 1 },
  { s: 3.95, v: [1, 0.42, 0.25], e: 1 },
  { s: 4.4, v: [0, 0.5, 0.3], e: 1 },
  { s: 7.5, v: [0, 0.5, 0.3], e: 1 },
  { s: 7.95, v: [1, 0.5, 0.27], e: 1 },
  { s: 8.9, v: [1, 0.5, 0.27], e: 1 },
  { s: 9.25, v: [0, 0.5, 0.3], e: 1 },
  { s: 9.6, v: [0, 0.5, 0.3], e: 1 },
  { s: 10.05, v: [1, 0.5, 0.3], e: 1 },
  { s: 11.9, v: [1, 0.5, 0.3], e: 0 },
];

// 月亮：[方位角(從 -z 轉向 +x，弧度), 仰角(度), 視直徑(度)]
const MOON: Key[] = [
  { s: 0, v: [0.32, 9, 8.5], e: 1 },
  { s: 1, v: [0.26, 15, 9.5], e: 1 },
  { s: 2, v: [0.2, 22, 11.5], e: 1 },
  { s: 3, v: [0.1, 27, 14], e: 1 },
  { s: 4, v: [0.55, 29, 11], e: 1 },
  { s: 5, v: [0.3, 40, 11], e: 1 },
  { s: 8, v: [0.0, 30, 11], e: 1 },
  { s: 9.0, v: [0.0, 31, 11], e: 1 },
  { s: 9.3, v: [0.7, 42, 11], e: 1 },
  { s: 10, v: [-0.2, 22, 11], e: 1 },
  { s: 10.9, v: [-0.3, 27, 11.5], e: 1 },
  { s: 11, v: [-0.55, 34, 12], e: 0 },
  { s: 11.9, v: [-0.55, 46, 13], e: 0 },
];

// 光線：[lx, ly, lz, 環境光, 增益]
const LIGHT: Key[] = [
  { s: 0, v: [0.5, 0.6, 0.6, 0.3, 0.88], e: 1 },
  { s: 3.4, v: [0.75, 0.42, 0.55, 0.33, 0.95], e: 1 },
  { s: 4.0, v: [0.85, 0.32, 0.45, 0.36, 1.0], e: 0 },
  { s: 5.8, v: [0.8, 0.36, 0.5, 0.36, 0.98], e: 1 },
  { s: 7.2, v: [0.45, 0.7, 0.5, 0.3, 0.8], e: 1 },
  { s: 8.0, v: [0.12, 1.0, 0.3, 0.28, 0.68], e: 1 },
  { s: 9.5, v: [0.3, 0.8, 0.5, 0.28, 0.66], e: 1 },
  { s: 11.9, v: [0.3, 0.8, 0.5, 0.3, 0.86], e: 1 },
  { s: 11.97, v: [0.5, 0.75, 0.55, 0.52, 1.02], e: 0 },
  { s: 13, v: [0.5, 0.75, 0.55, 0.52, 1.02], e: 0 },
];

// 天空：[地平線暈染強度, 星星強度, 白天程度]
const SKYK: Key[] = [
  { s: 0, v: [0.06, 1, 0], e: 1 },
  { s: 2, v: [0.12, 1, 0], e: 1 },
  { s: 3, v: [0.3, 0.9, 0], e: 1 },
  { s: 3.9, v: [0.92, 0.35, 0], e: 0 },
  { s: 5.2, v: [0.78, 0.4, 0], e: 1 },
  { s: 6.5, v: [0.42, 0.7, 0], e: 1 },
  { s: 7.6, v: [0.1, 1, 0], e: 1 },
  { s: 8.4, v: [0.0, 1, 0], e: 0 },
  { s: 11.9, v: [0.0, 1, 0], e: 1 },
  { s: 11.97, v: [0.0, 0, 1], e: 0 },
  { s: 13, v: [0.0, 0, 1], e: 0 },
];

// 手機（寬 ≤720px）說明框蓋住畫面下半（約 y>0.55h）、上方還有標題列與月份導覽（約 y<0.13h）：
// 每個 cue 的畫面整體往上推（單位：畫面高度的比例），讓主體落在 0.13h–0.55h 之間。
// hyssop 那一拍說明框收成小條，不推。
const UP_SHIFT_BY_CUE = [0.1, 0.1, 0.12, 0.04, 0.17, 0, 0.17, 0, 0.14, 0.2, 0.22, 0.2, 0.2];
const UP: Key[] = [];
UP_SHIFT_BY_CUE.forEach((v, i) => {
  UP.push({ s: i === 12 ? 11.96 : i + 0.3, v: [v], e: 1 });
  UP.push({ s: i === 11 ? 11.9 : i + 1.0, v: [v], e: 1 });
});
UP.unshift({ s: 0, v: [UP_SHIFT_BY_CUE[0]], e: 1 });
const _up = [0];
export function upShiftAt(s: number): number {
  sampleKeys(UP, s, _up);
  return _up[0];
}
export interface TrackOut {
  cam: number[];
  moon: number[];
  light: number[];
  sky: number[];
  /** 手機用：月亮的畫面位置 [權重, x, y] */
  moonS: number[];
}

export function createTrackOut(): TrackOut {
  return { cam: new Array(8).fill(0), moon: new Array(3).fill(0), light: new Array(5).fill(0), sky: new Array(3).fill(0), moonS: new Array(3).fill(0) };
}

export function sampleTracks(s: number, out: TrackOut, mobile = false): void {
  sampleKeys(mobile ? CAM_M : CAM, s, out.cam);
  sampleKeys(MOON_S, s, out.moonS);
  sampleKeys(MOON, s, out.moon);
  sampleKeys(LIGHT, s, out.light);
  sampleKeys(SKYK, s, out.sky);
}

// 各種由 s 推導的單一量 ------------------------------------------------
/** 章配色插值：0＝開場，1＝逾越節 */
export const palK = (s: number): number => smooth(3.4, 4.0, s);

/** 整片直向刻線抹除（vigil 末尾 → children 開頭），在 s≈11.93 全蓋 */
export const wipeAmt = (s: number): number => smooth(11.78, 11.91, s) * (1 - smooth(11.95, 12.1, s));

/** 半夜的黑暗：帶狀遮罩從右掃到左，位置 0..1 */
export const midnightP = (s: number): number => clamp(s - 8, 0, 1);
export const inMidnight = (s: number): boolean => s >= 8 && s < 9.02;

/** 埃及城的窗：從 wailing 起一扇一扇熄燈（回傳門檻；亮燈 = 窗的隨機值 ≥ 門檻） */
export const windowOff = (s: number): number => smooth(9.12, 9.92, s) * 1.02;
/** 火炬熄滅 */
export const torchOn = (s: number): number => 1 - smooth(9.55, 9.9, s);

/** 隊伍位移（公尺，往 -x）：起步與到達用慢速，中間加速 */
export const departDist = (s: number): number => {
  const p = clamp(s - 10, 0, 1);
  const f = 0.3 * p + 0.7 * (p * p * (3 - 2 * p));
  return f * 120;
};















