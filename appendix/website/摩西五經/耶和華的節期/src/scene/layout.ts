// 世界座標的配置：各個地點搭在遠處，互不相干（x 方向相隔 300 公尺）。純資料，tracks／poses2／各場景模組共用。
export const OX = 300; // 日後的屋子（children、no-leaven、remember）
export const SX = 600; // 疏割
export const BX = 900; // 大麥田
export const NX = 1200; // 西乃營地（第二批：曠野的會幕營地）
export const WX = 1500; // 小麥田（夏日過場沿用）
export const GX = 1800; // 吉甲（回聲）
export const JX = 2100; // 耶路撒冷聖殿院子（回聲）
export const RX = 2400; // 伯利恆的大麥田（回聲）
export const GTX = 2700; // 水門前的廣場（回聲）
export const BLX = 3000; // 住棚節的那地（村子）
export const JRX = 3300; // 耶路撒冷的房頂（回聲）

/** 會幕院子在西乃營地群組裡的位置（營地原點是 NX）：院子中心 */
export const CX = -6;
export const CZ = -36;
/** 會幕院子的尺寸（公尺）：1 肘 ≈ 0.3 公尺，院子 100×50 肘 */
export const COURT_W = 30;
export const COURT_D = 19;
/** 院子門（前，+z 側）的世界座標 */
export const GATE_X = NX + CX;
export const GATE_Z = CZ + COURT_D / 2;
