# Antigravity Fallback Orchestrator Prompt

本檔只在 **Codex 因額度／服務不可用而無法繼續新章 production** 時使用。Antigravity 接手同一條 `agent_start_prompt.md` 正式流程與同一份磁碟狀態；**不是重新做一章，也不是重置 review 次數。**

開始前讀：`AGENTS.md`、`agent_start_prompt.md`、`agent_evidence_audit_prompt.md`。實際 M3/M6 payload 規格仍以當次 `.tmp/第x章/manual/*.prompt.md` 為最高權威。

## 模型政策

Antigravity fallback 使用 **目前 `agy models` 中最新一代、High tier 的 Gemini agent model**；不要因為名稱有 Pro 就退回舊的 Gemini 3.1 Pro。

目前專案指定的 fallback 是：

```text
gemini-3.7-flash-high   # Gemini 3.7 Flash (High)
```

`agy` 的 High reasoning 由 model tier/slug 表達；若未來 `agy models` 出現更新一代的 High tier，改用更新者。若 live catalog 沒有 `gemini-3.7-flash-high`，先跑 preflight／`agy models`，選最新 High；不要自行降成 Low/Medium。

## 接手規則

1. 先讀本章 `.tmp/`、`pipeline_state.json`、`agent_review.yaml`、source/read receipts、payload 與已落地結果，從**最後合法 checkpoint**繼續。
2. `review_attempts` 是 stage-global：Codex 已用掉的 attempt 也算。Codex Round 1 後才斷線，Antigravity 就只剩 Attempt 2；禁止把自己當成新的 Round 1。
3. Codex quota／tool failure 若尚未形成 substantive verdict，可視為 `BLOCKED`，不耗 review attempt；Antigravity可對同一 SHA 接手。
4. Antigravity 接手後，同時扮演 orchestrator + Evidence Reviewer；對 Claude-authored M3/M6/B 內容 audit 時 read-only，問題退回 Claude 修。
5. 所有 reviewer verdict 用：

```text
python util/agent_review.py verdict 書名 章 stage <status> \
  --sha <sha> --reviewer antigravity --findings-count N
```

6. 每 stage 至多兩次 substantive review；Attempt 2 若仍要改，Claude 最後修一次，再 `submit` 自動 `FORCED PASS`，Antigravity不得做第三次 review。

## Claude 作者不變

內容作者仍固定走 `claude-code` MCP：

```text
model=opus
effort=max
cwd=<repo root>
```

同一章優先延續原 Claude `session_id`。找不到舊 session 才開新 session，並把 formal artifacts、目前 stage、已有 findings 明確交接。不得靜默 fallback Sonnet/Haiku。

## 接手後負責的工作

Antigravity 接手 Codex 原本的 orchestration 責任：來源／machine validation、similarity/resolver/prompts、review receipt、M3/M6/B evidence audit、check/run/render、preview/apply、post-landing sanity、final gates、commit。Claude只負責 Commentary/read_log、candidate 語意選擇、M3/M6/B 內容與修稿。

核心：**換 host，不換 SOP；換 reviewer，不重置兩次 review 預算；換到最新 High Gemini，不回退 3.1 Pro。**
