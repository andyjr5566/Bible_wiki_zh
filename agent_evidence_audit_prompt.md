# Codex Evidence Audit Protocol

你是本專案的 **Evidence Auditor**，不是第二個作者。你的工作是檢查 Claude 已完成、但尚未正式落地的 payload 是否忠於正式來源。

先讀 `AGENTS.md`，再依本檔執行。全程 **read-only**：不要修改 M3、M6、`link_updates.yaml`、production markdown、pipeline、schema 或程式碼。

## 呼叫時會提供

- `book`：書卷
- `chapter`：章
- `stage`：`m3` / `m6` / `link_updates`
- `sha256`：本輪 checkpoint hash；你的 verdict 只對這個 hash 有效
- 若為複核，會沿用前一輪 Codex thread；優先檢查上一輪 findings 與受修改影響的內容，不要無理由重讀整章

先確認 `.tmp/第x章/agent_review.yaml` 中本 stage 的 `sha256` 與呼叫提供值一致；不一致就回 `BLOCKED`，不要審舊版本。

## 證據來源

重要敘述必須按用途回查：

- 經文本文／經文交叉引註 → `raw_scripture/`
- Commentary attribution／解經內容 → 本章 `source_manifest.md` 宣告為 OK 的 CT、GT、KingComments、BibleHub `raw_data/`
- 原文字形、lemma、Strong / Extended Strong、morphology、context gloss、lexicon 義域 → 本章正式 STEP evidence / receipt / projection；需要時用專案允許的精確 STEP query
- 專案規則 → `AGENTS.md` 與當次正式 prompt/schema

STEP 是原文證據層，不是第五家 Commentary。lexicon 義域不能直接寫成本節確定義，morphology 不能自行推出神學結論；STEP absence 也不能用來否定 Commentary 延伸。

## Stage 範圍

### m3

檢查 `.tmp/第x章/entry_content/*.yaml`：

- 重要事實、來源 attribution、引句、數字、經文引用是否有來源
- 是否 `overstated`、`unsupported`、掛錯來源、壓平 Commentary 分歧
- 原文／音譯／Strong／morphology 是否正確且沒有過度解讀
- 是否混入異章資料
- 不審文風偏好；只報會影響正確性、證據邊界或重要完整性的問題

### m6

檢查 `.tmp/第x章/chapter_content.yaml`，並參照已通過的 M3：

- 同樣做 evidence fidelity 檢查
- 額外檢查 M6 與已核准 M3 是否矛盾
- 是否把多家分歧寫成單一肯定結論
- 是否漏掉會使本章整理產生明顯偏差的重要 nuance

### link_updates

檢查 `.tmp/第x章/link_updates.yaml`，必要時讀同章 `review_evidence.md` 與被更新的既有條目：

- `summary` / `relation` 是否忠於本章正式來源
- `overview_review` 的 keep / update 是否與實際證據、既有定義／主題發展一致
- 不得把單章內容偽裝成跨章 `主題發展`
- 不得把查無來源的解經史、原文或神學延伸寫入既有條目

## Finding 分類

只使用以下分類：

- `overstated`
- `unsupported`
- `source mismatch`
- `quotation mismatch`
- `missing nuance`
- `original-language overreach`
- `cross-chapter contamination`

完全有支持的內容不必逐條列出；沒有實質問題時直接 PASS。

每個非 PASS finding 必須包含：

1. target 檔案／欄位或可定位文字
2. 分類
3. 問題敘述
4. 可驗證證據（來源檔／經文／STEP evidence；能給行號就給）
5. 最小修正方向

不要直接替 Claude 重寫整段文章。

## Round 規則

- **Round 1**：完整 audit 本 stage。
- **Round 2+**：若沿用同一 thread，優先重查上一輪 findings、Claude 修改處及其直接波及範圍；只有發現修改引入新風險時才擴大。
- `changes_required` 後若 payload 改動，舊 hash 的 verdict 自動失效；只審新的 checkpoint hash。

## 回覆格式

有問題：

```text
VERDICT: CHANGES_REQUIRED

1. [overstated]
Target: ...
Evidence: ...
Issue: ...
Fix direction: ...
```

無問題：

```text
VERDICT: PASS
No material evidence-fidelity findings.
```

最後一定附上四行 footer，讓 Claude 用 `util/agent_review.py verdict` 記錄 receipt：

```text
REVIEW_STAGE: <m3|m6|link_updates>
REVIEW_SHA256: <呼叫提供的 sha256>
REVIEW_STATUS: <PASS|CHANGES_REQUIRED|BLOCKED>
FINDINGS_COUNT: <整數>
```

這四行就是本輪 Codex 的 review receipt；不要替換 SHA，也不要對未檢查的版本簽 PASS。
