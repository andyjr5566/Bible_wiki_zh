#!/usr/bin/env python3
"""驗證腳本失敗時的統一「問題 → 解法 → 該跑什麼」提示。

步驟 6 的驗證腳本原本只印「什麼壞了」（一串 ❌／🔴），使用者還得自己判斷
該回哪一步、跑什麼指令。本模組補上可據以行動的修復提示，讓輸出向
check_chapter_files.py 看齊。提示只在腳本判定失敗（exit 1）時印出。

各腳本的失敗類別不同，故修復內容由呼叫端依實際命中的類別組出，本模組只
負責一致的排版。`hints` 是 (問題描述, [動作/指令, …]) 的清單。
"""


def format_fix_hints(hints):
    """回傳修復提示區塊字串（無 hints 回空字串）。

    每個 hint 是 (problem, actions)：problem 一句話講「這類錯誤是什麼」，
    actions 是逐條「怎麼修 / 該跑什麼指令」。
    """
    hints = [h for h in hints if h and h[1]]
    if not hints:
        return ""
    lines = ["", "🔧 如何修復（依上方每條錯誤對症處理）："]
    for problem, actions in hints:
        lines.append(f"  • {problem}")
        for action in actions:
            lines.append(f"      → {action}")
    lines.append("  修好後，重跑本檢查（及其後續步驟）直到通過才 commit。")
    return "\n".join(lines)


def print_fix_hints(hints, stream=None):
    """把修復提示印到 stream（預設 stdout），空提示則不印。"""
    block = format_fix_hints(hints)
    if block:
        print(block, file=stream)
