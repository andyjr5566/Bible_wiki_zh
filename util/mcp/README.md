# Hermes Scripture MCP

這個 server 是既有章節流程的安全介面，不是另一套 workflow。內容規格仍以
[`agent_start_prompt.md`](../../agent_start_prompt.md) 與
[`agent_maintenance_prompt.md`](../../agent_maintenance_prompt.md) 為準；MCP 不會代替四來源勘誤或最終驗證。

## 工具

| 工具 | 用途 | 是否寫入 |
| --- | --- | --- |
| `get_chapter_status` | 依 `check_chapter_files.build_checks` 回報管線缺口與續作指令。 | 否 |
| `search_wiki_entries` | 查 canonical link index 的 title、alias、主分類與 secondary types。 | 否 |
| `read_wiki_entry` | 只讀取索引中的 `link_folder/**/*.md` 條目。 | 否 |
| `read_chapter_artifact` | 只讀取白名單內的 `.tmp/第X章` payload／manual prompt。 | 否 |
| `read_chapter_source` | 讀本地經文或該章 manifest 宣告為 OK 的 raw_data 來源。 | 否 |
| `lint_chapter_content` | 對**傳入文字**做 Mermaid／YAML 輕量格式提示，不讀任何路徑。 | 否 |
| `prepare_manual_payload_prompts` | 執行 `run_chapter_manual.py prompts` 產出手寫 M3/M6 prompt。 | 是，可能在確認後作廢過期 payload |
| `check_manual_payloads` | 執行 `run_chapter_manual.py check --no-rewrite`；缺 M3/M6 payload 會明確判為 incomplete。 | 否 |
| `render_manual_chapter` | 驗證通過後執行 `run_chapter_manual.py run`。 | 是，render／產生 verse links |
| `preview_chapter_link_updates` | 驗證 B 類累積更新並產生一次性 preview token。 | 否 |
| `apply_chapter_link_updates` | 只套用 token 對應的預覽；預覽或目標檔改變後 token 立即失效。 | 是 |

## M3／M6：固定走人工模式

M3 與 M6 不會呼叫 `run_chapter.py` 的模型端點。標準順序是：

1. `prepare_manual_payload_prompts`
2. 讀 manifest 指定的完整來源，手寫 `entry_content/*.yaml`（M3）
3. 再次 `prepare_manual_payload_prompts`，取得包含實建條目白名單的 M6 prompt
4. 手寫 `chapter_content.yaml`
5. `check_manual_payloads`
6. `render_manual_chapter`

`check_manual_payloads` 是唯讀的；它不會把 alias 連結回寫檔案。任何內容敘述仍須人工對回經文與有效 raw_data。

## B 類累積：先預覽才套用

先依來源人工填完 `link_updates.yaml`，再依序呼叫：

1. `preview_chapter_link_updates`
2. 核對回傳的條目與 yaml 中的 `summary`／`relation`
3. 將回傳的 `preview_token` 傳給 `apply_chapter_link_updates`
4. 再次 preview，確認 `change_count` 為 0

底層會先驗證所有更新目標只在 `link_folder/**/*.md`，預先計算全部變更，暫存後才逐檔替換；作業系統寫入失敗時會嘗試還原已替換的檔案。

## MCP prompts

- `biblical_chapter_sop`：新章流程的 MCP 操作摘要。
- `biblical_maintenance_sop`：維護既有章節／條目的 MCP 操作摘要。

兩者都明定 M3/M6 使用 manual wrapper，並連回兩份 agent prompt 的完整規格；載入 prompt 不會自動改檔或呼叫模型。

## 路徑與輸出邊界

- 不接受絕對路徑或 `..`；不能藉工具讀取 workspace 外的內容。
- `read_wiki_entry` 不接受任意 repo 檔案；`.tmp` 只能經 `read_chapter_artifact` 的白名單讀取。
- stdio transport 的 stdout 保留給 MCP JSON-RPC。底層 CLI 的文字輸出會被捕捉並結構化回傳，不能直接污染 protocol。

## 設定

複製本目錄的 `mcp_config_template.json`，並把 `command` 改為**安裝了 `mcp` 套件的 Python**。範本以 module 方式啟動：

```json
{
  "command": "C:/path/to/venv/Scripts/python.exe",
  "args": ["-m", "util.mcp.server"],
  "cwd": "C:/Obsidian/Hermes/scripture"
}
```

不要使用 `python -m mcp run ...`：目前安裝的 `mcp` 套件沒有這個 module 入口。直接用上例的 `python -m util.mcp.server` 即可。
