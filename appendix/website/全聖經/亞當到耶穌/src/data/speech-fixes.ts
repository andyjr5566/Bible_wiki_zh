import type { Replacement } from '../ui/speech';

/**
 * 朗讀用的多音字修正：只改送給語音的文字，畫面上的經文不變。
 * 左邊是經文裡的寫法，右邊是唸起來同音、語音引擎不會唸錯的字。
 */
export const SPEECH_FIXES: readonly Replacement[] = [];
