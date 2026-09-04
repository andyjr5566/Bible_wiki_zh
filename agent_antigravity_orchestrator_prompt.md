# Antigravity Fallback Orchestrator Prompt

本檔只在 **Codex 因額度／服務不可用而無法繼續新章 production** 時使用。Antigravity 接手同一條 `agent_start_prompt.md` 正式流程與同一份磁碟狀態；**不是重新做一章，也不是重置 review 次數。**

開始前讀：`AGENTS.md`、`agent_start_prompt.md`、`agent_evidence_audit_prompt.md`。實際 M3/M6 payload 規格仍以當次 `.tmp/第x章/manual/*.prompt.md` 為最高權威。

## 模型政策

Antigravity fallback 一律使用 **當下 `agy models` live catalog 中最新一代、High tier 的 Gemini agent model**；不寫死特定版本號，每次接手先跑 `agy models` 現查，不沿用快取或記憶中的舊 slug，也不要因為名稱有 Pro 就退回較舊世代。

`agy` 的 High reasoning 由 model tier/slug 表達；若 live catalog 出現更新一代的 High tier，立即改用更新者。不要自行降成 Low/Medium。

## 接手規則

1. 先讀本章 `.tmp/`、`pipeline_state.json`、`agent_review.yaml`、source/read receipts、payload 與已落地結果，從**最後合法 checkpoint**繼續。
2. `review_attempts` 是 stage-global：Codex 已用掉的 attempt 也算。Codex Round 1 後才斷線，Antigravity 就只剩 Attempt 2；禁止把自己當成新的 Round 1。
3. Codex quota／tool failure 若尚未形成 substantive verdict，可視為 `BLOCKED`，不耗 review attempt；Antigravity可對同一 SHA 接手。
4. Antigravity 接手後，同時扮演 orchestrator + Evidence Reviewer——但這是同一角色的兩個不同權限狀態，**不是同一種權限**。orchestration 工作（run/render/apply/commit 等）維持正常寫入權限；進入 M3/M6/B 的 Evidence Reviewer audit **之前**，先把 `~/.gemini/antigravity-cli/settings.json` 設成：

```json
{"permissions": {"allow": ["read_file(*)"], "deny": ["write_file(*)", "command(*)"]}}
```

（不要加 `--dangerously-skip-permissions`，那會整組跳過這個 deny。）在這個設定下做 audit，findings 只能純文字回傳——reviewer 在 CLI 層就沒有寫檔／跑指令的能力，包括不能自己改 `util/agent_review.py` 或任何 gate 腳本。因為 deny 也擋掉 `command`，reviewer 自己跑不了 `agent_review.py verdict`；**改由 orchestrator（audit 結束後把 settings.json 恢復正常權限的那個 session）依 reviewer 的報告代記 verdict**，sha 對不上就記不進去，reviewer 偽造不了 PASS。
5. **同一章的 review 呼叫延續同一個 `agy` conversation，不要每次 audit 都開新的。** M3 第一次 audit 用一般 `agy -p` 開對話並記下 conversation id；之後 M3 Attempt 2、M6 audit、link_updates audit 一律用 `--conversation {id}` 接續同一個 thread。settings.json 的 deny/allow 是每次呼叫時讀取，可以隨呼叫用途切換（做 orchestration 動作時切回正常權限、下一次做 audit 前再切回 deny），但**對話本身不必因為權限切換而重開**——reviewer 因此記得住自己前面已經審過、講過什麼，不必每次重新餵整章上下文。只有真的找不到可延續的舊 conversation，或 Codex／Antigravity 互相交接時，才視為新 thread。
6. 所有 reviewer verdict 用：

```text
python util/agent_review.py verdict 書名 章 stage <status> \
  --sha <sha> --reviewer antigravity --findings-count N
```

7. 每 stage 至多兩次 substantive review；Attempt 2 若仍要改，Claude 最後修一次，再 `submit` 自動 `FORCED PASS`，Antigravity不得做第三次 review。
8. **絕不修改 `util/agent_review.py` 或任何 gate／驗證腳本來讓某次 review 過關**（例如加旗標讓自己對未改動內容宣告 PASS）。這曾實際發生過並被使用者當場糾正；每輪 audit 後 orchestrator 要 `git status util/` 確認沒有意外改動，再採信這輪 verdict。

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
