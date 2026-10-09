/**
 * 場景層對外的介面。介面層（src/main.ts、src/ui）只透過這裡和場景溝通。
 * 場景層的實作在 src/scene/ 底下（Three.js + 刻線著色器），介面層不直接碰 Three.js 物件。
 */
import type { Palette } from '../data/types';
import type { HyssopPart, StoryState } from '../story/state';

export type SceneEvent =
  | { type: 'hyssop-dip' }
  | { type: 'hyssop-strike'; part: HyssopPart }
  | { type: 'hyssop-miss' }
  | { type: 'hyssop-done'; auto: boolean }
  | { type: 'door-shut' }
  | { type: 'ready' }
  | { type: 'webgl-lost' };

export interface SceneOptions {
  canvas: HTMLCanvasElement;
  story: StoryState;
  /** 各章配色（feasts.yaml），key 是章 id */
  palettes: Record<string, Palette>;
  onEvent: (e: SceneEvent) => void;
}

export interface SceneHandle {
  /** 視窗尺寸或 devicePixelRatio 改變時呼叫 */
  resize(width: number, height: number, dpr: number): void;
  /** 停止 render loop 並釋放 GPU 資源 */
  dispose(): void;
  /**
   * 鍵盤／按鈕的替代操作（無法拖曳的讀者用）：
   * 'dip' 蘸血；'lintel'/'left'/'right' 打在該處。行為與拖曳完全相同（含動畫與事件）。
   */
  hyssopAction(action: 'dip' | HyssopPart): void;
  /** 畫布上目前可互動的區域（介面層據此只在這些區域攔截觸控，其餘照常捲動）。座標是 CSS px。 */
  interactiveRects(): DOMRect[];
}

/** 不支援 WebGL2 時回傳 null，介面層改用預先輸出的靜態插圖。 */
export type CreateScene = (opts: SceneOptions) => SceneHandle | null;
