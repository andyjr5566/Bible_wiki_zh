# 第9章 候選存在性掃描（search_wiki_entries 批次）

以 `search_wiki_entries(queries=[...])` 一次掃過本章 31 個候選名。

## unmatched（完全查無 → C 類新建）

- 基遍
- 基非拉
- 比錄
- 基列耶琳
- 迦南諸王結盟
- 詭計與謹慎（or.mah）
- 沒有求問耶和華
- 會眾的首領
- 指著耶和華起誓的約束力
- 忿怒（qe.tseph）

## 有 match，已逐一確認為同一概念（A／B 累積，沿用既有精確標題）

| 候選名 | 既有條目 | 判定依據 |
| --- | --- | --- |
| 約書亞 | `link_folder/人物/約書亞.md` | exact_title |
| 希未人 | `link_folder/歷史/希未人.md` | exact_title |
| 赫人 | `link_folder/人物/赫人.md` | exact_title |
| 亞摩利人 | `link_folder/人物/亞摩利人.md` | exact_title |
| 迦南人 | `link_folder/人物/迦南人.md` | exact_title |
| 比利洗人 | `link_folder/人物/比利洗人.md` | exact_title |
| 耶布斯人 | `link_folder/人物/耶布斯人.md` | exact_title |
| 利巴嫩 | `link_folder/地點/利巴嫩.md` | exact_title |
| 大海（地中海） | `link_folder/地點/大海（地中海）.md` | exact_title；本章用「大海」，已宣告 surface |
| 高原（Shephelah） | `link_folder/地點/高原（Shephelah）.md` | exact_title；本章用「高原」，已宣告 surface |
| 希實本 | `link_folder/地點/希實本.md` | exact_title |
| 巴珊 | `link_folder/地點/巴珊.md` | exact_title |
| 亞斯她錄 | `link_folder/地點/亞斯她錄.md` | exact_title；經文用字與條目標題同為「亞斯她錄」 |
| 吉甲 | `link_folder/地點/吉甲.md` | exact_title |
| 耶利哥 | `link_folder/地點/耶利哥.md` | exact_title |
| 艾 | `link_folder/地點/艾.md` | exact_title；本章用「艾城」，已宣告 surface |
| 摩西 | `link_folder/人物/摩西.md` | exact_title |
| 立約 | `link_folder/主題/立約.md` | exact_title |
| 以色列人的怨言 | `link_folder/歷史/以色列人的怨言.md` | exact_title；本章用「發怨言」，已宣告 surface |
| 劈柴挑水的人 | `link_folder/文化/劈柴挑水的人.md` | **由 resolver 以 exact 比對抓到**——我第一輪批次查詢把名字打成「勈柴挑水的人」而漏掉它；該條目收的是申29:10-11 的立約名單，其定義本身就引了書九21，本章正是它的來源事件，改走累積 |
| 咒詛（a.rar 與 qa.vav） | `link_folder/原文/咒詛（a.rar 與 qa.vav）.md` | 語義近鄰報出；原擬新建「被咒詛的（a.rar）」，第23節的 'a.ru.Rim 正是該條目已收的 H779 a.rar，改走累積 |

## 同名不同實體：詭計

第4節的「詭計」是 be./'a.re.Mah（H6195，or.mah: craftiness）；庫內既有的
`link_folder/原文/詭計（ne.khel）.md` 寫的是民25:18 的 ne.khel（H5231）／na.khal（H5230），
是另一個希伯來字。中文同名、原文不同字，所以要分建條目。

第一版取名 `詭計（or.mah）`，resolver 以 `match_type: base`（去括號後裸名相同）
把它併進了 `詭計（ne.khel）`——這正是本庫記錄過的靜默誤併。改名為
`詭計與謹慎（or.mah）` 之後裸名不再相撞，也順帶把 or.mah 同時涵蓋「謹慎」與
「陰謀」兩端的義域寫進名字。`_config/link_homonyms.yaml` 因此不需要新增登記。

## 語義近鄰 ⚠ 的逐項裁決

- 基遍／基列耶琳 vs [[基列]]：不同地名，照建。
- 基非拉 vs [[希未人]]（分類不相容）：城 vs 族，照建。
- 比錄 vs [[河東城邑的位置考據]]：無關，照建。
- 迦南諸王結盟 vs [[耶利哥王]]（分類不相容）：不同實體，照建。
- 沒有求問耶和華 vs [[求問與訪問同一個字（da.rash）]]（分類不相容）：本章第14節的「求問」是
  sha.'A.lu（H7592，sha.al），既有條目寫的是 da.rash（H1875），不同字，照建，並在條目裡註明字別。
- 會眾的首領 vs [[以色列的眾長老]]：CT 明說『會眾的首領』指十二支派的首領，與長老是不同職分，照建。
- 指著耶和華起誓的約束力 vs [[古埃及的起誓方式]]（分類不相容）：一個是埃及的起誓套語，
  一個是誓言的約束力，照建。
- 忿怒（qe.tseph） vs [[氣忿忿]]：既有條目是 cho.ri 搭配 af（H2750＋H639G），本章是
  Ke.tzef（H7110A），不同字，照建。
- 被咒詛的（a.rar） vs [[咒詛（a.rar 與 qa.vav）]]：**同一個 H779**，改走 B 類累積（見上表）。
- 詭計與謹慎（or.mah） vs [[詭計（ne.khel）]]（0.649 居中）：中文同名、原文不同字，照建（理由見上一節）。

## 刻意不連的近似項

- **第24節「滅絕」**：STEP 為 u./le./hash.Mid（H8045，sha.mad: to destroy），
  與庫內「滅絕」（原文，收 cha.ram H2763）與「滅絕（herem）」（神學）都不是同一個字，
  不宣告為候選，只在散文與摩西條目的累積裡註明字別。
- **第11節「我們的長老」**：指基遍那地的長老，不是既有條目「以色列的長老」，不連。
- **烏陵和土明**：GT《聖經精讀本》在第14節列舉舊約求問神旨意的方法時提到，
  但本章經文沒有出現這個詞，只在散文提及，不宣告候選以免產生孤兒節點。
- **迦南七族（迦南地原住民）**：第1節只列六族（CT 指出此處未列革迦撒人），
  唯一可用的 surface 會整串吃掉六個族名候選，因此不宣告，改在散文純文字提及。
