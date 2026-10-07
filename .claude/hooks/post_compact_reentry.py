#!/usr/bin/env python3
"""SessionStart(compact) hook：compact 後把「重新進場」指令注入 Claude 的上下文。

compact 會把讀過的 commentary、經文、SOP 細節壓成摘要；摘要只記得「讀過了」，
內容本身已經不在。這支 hook 要求先重讀 SOP、進度檔與本章來源，才能繼續寫內容。
進度一律以 `.tmp/第x章/progress.md` 為準，不以摘要為準。

觸發條件：本 session 的 transcript 裡有寫入 `.tmp/第x章/progress.md` 的紀錄
（Write／Edit，或 Bash／PowerShell 的寫檔指令），且該檔狀態不是「已完成」。只讀過
SOP、只讀過進度檔、只提到檔名、或在做網站等其他工作，一律不輸出。
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2])
PROGRESS_MAX_CHARS = 8000
WRITE_TOOLS = {"Write", "Edit", "MultiEdit"}
SHELL_TOOLS = {"Bash", "PowerShell"}
PROGRESS_RE = re.compile(r"/\.tmp/第\d+章/progress\.md$")
# shell 指令裡的 progress.md 路徑；書卷資料夾（如「03 利未記」）可有可無
SHELL_PATH_RE = re.compile(r"(?:(\d{2,3} [^/\\\"'\s]+)[/\\])?\.tmp[/\\](第\d+章)[/\\]progress\.md")
# 只算寫入：重導向、tee、sed -i、複製／搬移、PowerShell 寫檔、Python 寫檔；cat／Get-Content 等純讀取不算
SHELL_WRITE_RES = [
    re.compile(r">>?\s*[^;|&\n>]*?progress\.md"),
    re.compile(r"\btee\b[^;|&\n]*?progress\.md"),
    re.compile(r"progress\.md[^;|&\n]*?\|\s*tee\b"),
    re.compile(r"\bsed\s+(?:-\w*\s+)*-i[^;|&\n]*?progress\.md"),
    re.compile(r"\b(?:cp|mv|Copy-Item|Move-Item|New-Item|Set-Content|Add-Content|Out-File)\b[^;|&\n]*?progress\.md", re.I),
    re.compile(r"progress\.md[^;|&\n]*?\|\s*(?:Set-Content|Add-Content|Out-File)\b", re.I),
    re.compile(r"(?:write_text|WriteAllText|open\([^)]*progress\.md[^)]*['\"][wa])"),
]


def shell_progress_path(command: str) -> Path | None:
    """shell 指令若寫入 progress.md，回傳該檔路徑；純讀取回 None。"""
    if "progress.md" not in command or not any(r.search(command) for r in SHELL_WRITE_RES):
        return None
    m = SHELL_PATH_RE.search(command)
    if not m:
        return None
    book, chapter = m.groups()
    if book:
        return ROOT / book / ".tmp" / chapter / "progress.md"
    # 指令沒帶書卷資料夾（先 cd 進去再寫）：取同章號中最近修改的那一份
    found = [p for p in ROOT.glob(f"*/.tmp/{chapter}/progress.md") if p.is_file()]
    return max(found, key=lambda p: p.stat().st_mtime) if found else None


def progress_written_in_session(transcript_path: str) -> Path | None:
    """回傳本 session 最後一次寫入（Write／Edit 或 shell）的 progress.md；沒有就回 None。"""
    path = Path(transcript_path) if transcript_path else None
    if not path or not path.is_file():
        return None
    last: Path | None = None
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if "progress.md" not in line or '"tool_use"' not in line:
                continue
            try:
                content = json.loads(line).get("message", {}).get("content", [])
            except json.JSONDecodeError:
                continue
            for item in content if isinstance(content, list) else []:
                if not isinstance(item, dict) or item.get("type") != "tool_use":
                    continue
                name, tool_input = item.get("name"), item.get("input", {}) or {}
                if name in WRITE_TOOLS:
                    file_path = str(tool_input.get("file_path", "")).replace("\\", "/")
                    if PROGRESS_RE.search(file_path):
                        last = Path(file_path)
                elif name in SHELL_TOOLS:
                    found = shell_progress_path(str(tool_input.get("command", "")))
                    if found:
                        last = found
    return last


def progress_status(progress: Path) -> str:
    m = re.search(r"^狀態[：:]\s*(\S+)", progress.read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else ""


def manifest_files(chapter: Path) -> list[str]:
    manifest = chapter / "source_manifest.md"
    if not manifest.is_file():
        return []
    return re.findall(r"raw_data/[^\s|]+\.txt", manifest.read_text(encoding="utf-8"))


def build_message(progress: Path) -> str:
    chapter = progress.parent
    book = re.sub(r"^\d+\s*", "", chapter.parents[1].name)
    chap_no = re.sub(r"\D", "", chapter.name)
    try:
        rel = chapter.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        rel = chapter.as_posix()

    lines = [
        "【compact 後重新進場】你剛被 auto compact。之前讀過的 commentary、經文、STEP 內容與",
        "SOP 細節都只剩摘要，一律視為已遺失；摘要裡的進度描述也可能失真。",
        "",
        f"進行中的章節：{book} 第{chap_no}章　`{rel}/`",
        "",
        "在寫或修改任何 `.tmp` payload、link_folder 條目或章節 md 之前，依序做完：",
        "1. 用 Read 讀 `agent_start_prompt.md` 全文。",
        "2. 讀下面這章的 `progress.md`，以它記的步驟為準，不以 compact 摘要為準。",
        "3. 用 Read 把本章四套 commentary 與經文重新全文讀一遍（清單見下）。這是恢復記憶，不必改 read_log.md。",
        "4. 讀本章已寫好的 payload（link_candidates.yaml、entry_content/、chapter_content.yaml、link_updates.yaml 中已存在者）。",
        "5. 跑 `python util/agent_review.py summary` 或 MCP `get_chapter_status` 對照磁碟狀態。",
        "做完再接續 progress.md 的「下一步」，並在完成每一步後更新 progress.md。",
        "",
        "要重新全文讀的來源：",
    ]
    scripture = ROOT / "raw_scripture" / book / f"第{chap_no}章.txt"
    if scripture.is_file():
        lines.append(f"- raw_scripture/{book}/第{chap_no}章.txt（經文）")
    commentary = [f for f in manifest_files(chapter) if "stepbible_" not in f]
    lines += [f"- {f}" for f in commentary] or ["- （manifest 不存在或無 commentary；來源準備尚未完成）"]
    lines.append("- STEP 不全文重讀：需要時讀 M3 prompt 的 projection 或用 MCP query_step_context。")

    text = progress.read_text(encoding="utf-8")
    if len(text) > PROGRESS_MAX_CHARS:
        text = text[:PROGRESS_MAX_CHARS] + "\n…（已截斷，請用 Read 讀全文）"
    lines += ["", f"--- {rel}/progress.md ---", text]
    return "\n".join(lines)


def main() -> None:
    try:
        hook_input = json.load(sys.stdin)
    except Exception:
        hook_input = {}
    try:
        progress = progress_written_in_session(hook_input.get("transcript_path", ""))
        if progress is None or not progress.is_file() or progress_status(progress) == "已完成":
            return  # 不是進行中的章節撰寫 session：安靜結束
        message = build_message(progress)
    except Exception as exc:  # hook 絕不能讓 session 起不來
        message = f"【compact 後重新進場】hook 執行失敗（{exc}）；請手動重讀 agent_start_prompt.md 與本章 progress.md、四套 commentary。"
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(
        {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": message}},
        ensure_ascii=False,
    ))


if __name__ == "__main__":
    main()
