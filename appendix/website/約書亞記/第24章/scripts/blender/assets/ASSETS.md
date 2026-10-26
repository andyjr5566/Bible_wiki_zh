# scripts/blender/assets 素材來源與授權

## ubc/（Universal Base Characters［Standard］）

- 作者：Quaternius
- 頁面：https://quaternius.itch.io/universal-base-characters
- 授權：CC0 1.0（公眾領域貢獻）。原壓縮包內 `License_Standard.txt` 已原樣複製到 `ubc/License_Standard.txt`；
  itch.io 頁面也標示 Creative Commons Zero v1.0 Universal，可個人、教學與商用。
- 取得日期：2026-10-26。Standard 版是作者提供、可免費下載的版本（頁面上的「No thanks, just take me to the downloads」），
  下載檔放進全新的空暫存資料夾，只當資料讀取，沒有執行壓縮包內任何程式。
- 用到的檔案（從 zip 內原樣取出）：
  - `Superhero_Male_FullBody.fbx`、`Superhero_Female_FullBody.fbx`（Unity 版 FBX，含骨架與蒙皮）
  - `Hair_Beard.fbx`、`Hair_SimpleParted.fbx`、`Hair_Long.fbx`、`Hair_Buns.fbx`、`Eyebrows_Regular.fbx`、`Eyebrows_Female.fbx`（Origin at 0 版）
  - 貼圖：`T_Superhero_Male_Dark.png`、`T_Superhero_Male_Ligh.png`（檔名原樣）、`T_Superhero_Female_Dark_BaseColor.png`、
    `T_Superhero_Female_Light_BaseColor.png`、`T_Eye_Brown.png`、`T_Hair_1_BaseColor.png`、`T_Hair_2_BaseColor.png`
- 沒有用到：法線與粗糙度貼圖、Unreal 與 glTF 版本、Preview 圖。
- 用法：`epic_chars.py` 匯入後把雙臂放下、烘成靜態網格；衣服（長袍、袖子、披風、頭巾、腰帶、頭箍）全部是我們自己在 Blender 內
  建模與布料模擬，底模本身的內衣不會露出來（本站畫面沒有裸身）。
- 技術備註：Blender 內建 FBX 匯入器需要 numpy；這台電腦的應用程式控制封鎖了 numpy 的 `_umath_linalg` 擴充模組，
  所以 `epic_lib.py` 開頭先放一個空殼模組再載入 numpy（只影響線性代數函式，匯入與網格運算不受影響）。

## 未使用的下載

- 試過 Quaternius 的 Ultimate Modular Men／Women：官方 quaternius.com 的頁面目前回 404，故改用 itch.io 的 Universal Base Characters。
