## vexp — Context-Aware AI Coding <!-- vexp v1.3.11 -->

### MANDATORY: use vexp pipeline — do NOT grep or glob the codebase
For every task — bug fixes, features, refactors, debugging:
**call `run_pipeline` FIRST**. It executes context search + impact analysis +
memory recall in a single call, returning compressed results.

Do NOT use grep, glob, Bash, or cat to search/explore the codebase.
vexp returns pre-indexed, graph-ranked context that is more relevant and
uses fewer tokens than manual searching. Prefer `get_skeleton` over Read to
inspect files (detail: minimal/standard/detailed, 70-90% token savings).
Only use Read when you need exact raw content to edit a specific line.

### Primary Tool
- `run_pipeline` — **USE THIS FOR EVERYTHING**. Single call that runs
  capsule + impact + memory server-side. Returns compressed results.
  Auto-detects intent (debug/modify/refactor/explore) from your task.
  Includes full file content for pivots.
  Examples:
  - `run_pipeline({ "task": "fix JWT validation bug" })` — auto-detect
  - `run_pipeline({ "task": "refactor db layer", "preset": "refactor" })` — explicit
  - `run_pipeline({ "task": "add auth", "observation": "using JWT" })` — save insight in same call

### Other MCP tools (use only when run_pipeline is insufficient)
- `get_context_capsule` — lightweight alternative for simple questions only
- `get_impact_graph` — standalone deep impact analysis of a specific symbol
- `search_logic_flow` — trace execution paths between two specific symbols
- `get_skeleton` — **preferred over Read** for inspecting files (minimal/standard/detailed detail levels, 70-90% token savings)
- `index_status` — indexing status and health check
- `get_session_context` — recall observations from current/previous sessions
- `search_memory` — cross-session search for past decisions
- `save_observation` — persist insights (prefer using run_pipeline's observation param instead)

### Workflow
1. `run_pipeline("your task")` — ALWAYS FIRST. Returns pivots + impact + memories in 1 call
2. Need more detail on a file? Use `get_skeleton({ files: [...], detail: "detailed" })` — avoid Read unless editing
3. Make targeted changes based on the context returned
4. `run_pipeline` again ONLY if you need more context during implementation
5. Do NOT chain multiple vexp calls — one `run_pipeline` replaces capsule + impact + memory + observation

### Subagent / Explore / Plan mode
- Subagents CAN and MUST call `run_pipeline` — always include the task description
- The PreToolUse hook blocks Grep/Glob when vexp daemon is running
- Do NOT spawn Agent(Explore) to freely search — call `run_pipeline` first,
  then pass the returned context into the agent prompt if needed
- Always: `run_pipeline` → get context → spawn agent with context

### Smart Features (automatic — no action needed)
- **Intent Detection**: auto-detects from your task keywords. "fix bug" → Debug, "refactor" → blast-radius, "add" → Modify
- **Hybrid Search**: keyword + semantic + graph centrality ranking
- **Session Memory**: auto-captures observations; memories auto-surfaced in results
- **LSP Bridge**: VS Code captures type-resolved call edges
- **Change Coupling**: co-changed files included as related context

### Advanced Parameters
- `preset: "debug"` — forces debug mode (capsule+tests+impact+memory)
- `preset: "refactor"` — deep impact analysis (depth 5)
- `max_tokens: 12000` — increase total budget for complex tasks
- `include_tests: true` — include test files in results
- `include_file_content: false` — omit full file content (lighter response)

### Multi-Repo Workspaces
`run_pipeline` auto-queries all indexed repos. Use `repos: ["alias"]` to scope.
Use `index_status` to discover available repo aliases.
<!-- /vexp -->

## Hermes Scripture — Claude-specific bridge

Hermes Scripture 的跨 Agent 共用規則只維護在根目錄 `AGENTS.md`；根目錄 `CLAUDE.md` 以 `@AGENTS.md` 載入它。本檔只保留 Claude Code 專屬的 vexp 細節，不再複製 source architecture、STEP lifecycle 或當前書卷進度，避免形成第二份真相。

Claude 處理 Scripture 任務時：

- 新章 production → `agent_start_prompt.md`。
- 已完成章節勘誤／補充 → `agent_maintenance_prompt.md`。
- 架構、來源與設計判斷 → `scheme.md`。
- M3／M6 的當次 payload schema、欄位、輸入範圍與格式 → 當次 `util/run_chapter_manual.py prompts`。
- STEP／Commentary 的角色、evidence boundary、validation、multi-agent collaboration 與 conflict handling → `AGENTS.md`。

不要在本檔維護歷史 Phase 清單或書卷 migration 狀態；目前狀態一律查當前 project status、manifest 與 receipts。

M3 STEP projection 依目前正式實作與 `AGENTS.md`：只使用 candidate-matched evidence；candidate 無法定位或 evidence=全章時 fail-small，不得 fallback 成整節／整章 STEP raw，必要時改用精確 STEP query。

若本檔、`AGENTS.md`、SOP 或當次 prompts 出現真正衝突，依 `AGENTS.md` 的「規則權威範圍」判定；無法消解時標記 `unresolved`，不得自行猜測。
