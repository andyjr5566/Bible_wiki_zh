/**
 * 捲動狀態：唯一的共享可變物件。
 * - 介面層（src/ui、src/story/scroll.ts）在每次捲動時寫入。
 * - 場景層（src/scene）每一幀讀取，不寫入（互動結果除外，見 hyssop）。
 * 不用框架的響應式狀態；每幀直接讀這個物件，避免捲動時大量重繪。
 */

export type HyssopPart = 'lintel' | 'left' | 'right';

export interface StoryState {
  /** 目前所在的章（opening、passover……）與拍 */
  chapter: string;
  beat: string;
  /** 目前這一拍的場景提示（story.yaml 的 cue） */
  cue: string;
  /** 前一拍的 cue（場景做轉場用） */
  prevCue: string;
  /** 0–1：在目前這一拍裡捲到哪裡 */
  beatProgress: number;
  /** 0–1：在目前這一章裡捲到哪裡 */
  chapterProgress: number;
  /** 0–1：整頁 */
  pageProgress: number;
  /** 開場的月亮日子（1–14，可為小數，隨捲動連續變化） */
  day: number;
  /** 系統偏好：暗色模式 */
  dark: boolean;
  /**
   * 系統偏好「減少動態」。只停背景裝飾性的動態（風吹麥浪、紙紋閃動、鏡頭漂移），
   * 讀者自己觸發的動作（打門框、關門）照常播放，不能變成跳格。
   */
  motionOff: boolean;
  /** 塗血互動的進度：由場景寫入（讀者在畫布上操作），介面層讀取更新提示與音效 */
  hyssop: {
    dipped: boolean;
    marks: Record<HyssopPart, boolean>;
    /** 三處都打過了；讀者沒做就捲過去時，場景會自動補完並設為 true */
    done: boolean;
    auto: boolean;
  };
}

export const story: StoryState = {
  chapter: 'opening',
  beat: 'title',
  cue: 'title',
  prevCue: 'title',
  beatProgress: 0,
  chapterProgress: 0,
  pageProgress: 0,
  day: 1,
  dark: false,
  motionOff: false,
  hyssop: {
    dipped: false,
    marks: { lintel: false, left: false, right: false },
    done: false,
    auto: false,
  },
};
