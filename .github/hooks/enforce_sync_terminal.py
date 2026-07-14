#!/usr/bin/env python3
"""PreToolUse hook: 強制 run_in_terminal 使用 mode=sync。

讀取 stdin JSON，若工具為 run_in_terminal 且 mode=async（或 isBackground=true），
則拒絕執行並提示 agent 改用 mode=sync。
"""
import json
import sys


def main():
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        # 無法解析輸入時放行，不阻斷正常流程
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    if tool_name != "run_in_terminal":
        # 只攔 run_in_terminal，其他工具放行
        sys.exit(0)

    mode = tool_input.get("mode", "")
    is_background = tool_input.get("isBackground", False)

    if mode == "async" or is_background is True:
        # 拒絕背景模式，要求 agent 改用 sync
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    "此專案禁止 run_in_terminal 使用 mode=async / isBackground=true。"
                    "請改用 mode=sync（同步模式），讓 agent 等待命令完成。"
                    "背景模式會導致反覆輪詢 terminal output，浪費 API token。"
                )
            }
        }
        print(json.dumps(output, ensure_ascii=False))
        sys.exit(2)

    # mode=sync 或未指定 mode（預設 sync），放行
    sys.exit(0)


if __name__ == "__main__":
    main()