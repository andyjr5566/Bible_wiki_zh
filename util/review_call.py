#!/usr/bin/env python3
"""reviewer 呼叫包裝腳本：把 Codex／Antigravity 的唯讀 audit 呼叫固定成一行指令。

用法::

  python util/review_call.py 約書亞記 13 m6
  python util/review_call.py 約書亞記 13 m6 --note "M3 微調了米法押的定義"
  python util/review_call.py 約書亞記 13 m6 --reviewer antigravity
  python util/review_call.py 約書亞記 13 m6 --dry-run          # 只印出將執行的指令與 prompt
  python util/review_call.py 約書亞記 13 link_updates --global-review   # commit 前全局 review

它做的事：

1. 從 ``.tmp/第x章/agent_review.yaml`` 讀該 stage 目前的 sha，組出最小 prompt
   （書卷、章、stage、sha，請 reviewer 依 ``agent_evidence_audit_prompt.md`` 審查）。
2. Codex：第一次 ``codex exec --sandbox read-only ...``，之後同章一律
   ``codex exec resume <id> ...``（延續同一個 thread；id 存在
   ``.tmp/第x章/reviewer_thread.yaml``）。MCP 核准旗標固定帶上，不必手打。
   Antigravity：每次用 ``agy models`` 的 live 輸出挑最新一代 ``-high`` 的 Gemini，
   ``agy -p ... --mode plan --sandbox``，有 conversation id 就存起來、下次 ``--conversation`` 延續。
3. 輸出存到 ``.tmp/第x章/review_logs/<stage>_<序號>.out``；解析最後的 footer，印出 reviewer
   的最終訊息與一行可直接執行的 ``agent_review.py verdict ...``（**不會自動記 verdict**）。
4. 執行前後各取一次 ``git status``／``git diff`` 指紋；reviewer 執行期間 repo 有任何變動
   （尤其 util/）就大聲警告並以非 0 結束。

結束碼：0 正常；1 一般錯誤；2 reviewer 執行期間 repo 被改動；3 額度用完（quota／429）；
4 沒有取得 footer（無法產生 verdict 指令）。

審查常要跑 10–20 分鐘，這支腳本不設 timeout。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import yaml

try:
    from . import agent_review
    from .book_paths import book_directory, canonical_book_name
    from .yaml_io import write_yaml_atomic
except ImportError:
    import agent_review  # type: ignore[no-redef]
    from book_paths import book_directory, canonical_book_name  # type: ignore[no-redef]
    from yaml_io import write_yaml_atomic  # type: ignore[no-redef]

ROOT = Path(__file__).resolve().parent.parent
THREAD_FILENAME = "reviewer_thread.yaml"
LOG_DIRNAME = "review_logs"
REVIEWERS = ("codex", "antigravity")
STAGES = agent_review.STAGES

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_REPO_CHANGED = 2
EXIT_QUOTA = 3
EXIT_NO_FOOTER = 4

CODEX_MCP_APPROVAL = 'mcp_servers.hermes-scripture.default_tools_approval_mode="approve"'
CODEX_READONLY_CONFIG = 'sandbox_mode="read-only"'

QUOTA_RE = re.compile(
    r"(429|quota|rate[ -]?limit|usage limit|RESOURCE_EXHAUSTED|exhausted|"
    r"hit your .{0,20}limit|額度|用量上限)", re.IGNORECASE)
RESET_RE = re.compile(
    r"((?:reset|resets|try again|retry)[^\n]{0,80}|(?:重置|重設|恢復)[^\n]{0,60})", re.IGNORECASE)
SESSION_ID_RE = re.compile(r"session id:\s*([0-9a-fA-F]{8}-[0-9a-fA-F-]{27})")
UUID_RE = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")

# footer 欄位：不依賴行首（agy 的 json 輸出會把換行跳脫掉），取「最後一次」出現。
_FOOTER_VALUE = {
    "REVIEW_STAGE": r"(m3|m6|link_updates)",
    "REVIEW_SHA256": r"([0-9a-fA-F]{64})",
    "REVIEW_REVIEWER": r"(codex|antigravity)",
    "REVIEW_ATTEMPT": r"(\d+)",
    "REVIEW_STATUS": r"(PASS|CHANGES_REQUIRED|BLOCKED)",
    "FINDINGS_COUNT": r"(\d+)",
}
GLOBAL_RE = re.compile(r"GLOBAL_REVIEW:[ \t*`]*(PASS|CHANGES_REQUIRED)")


class ReviewCallError(RuntimeError):
    pass


# ----------------------------------------------------------------------------
# prompt
# ----------------------------------------------------------------------------

def build_prompt(book: str, chapter: int, stage: str, sha: str, *, attempt: int | None = None,
                 delta: bool = False, note: str | None = None) -> str:
    lines = [
        "你是唯讀 evidence reviewer，不得修改任何檔案。請依 agent_evidence_audit_prompt.md 審查下面這個 stage，"
        "並照該檔「Verdict」一節的格式，在最後輸出 footer（REVIEW_STAGE／REVIEW_SHA256／REVIEW_REVIEWER／"
        "REVIEW_ATTEMPT／REVIEW_STATUS／FINDINGS_COUNT）。",
        f"書卷：{book}",
        f"章：{chapter}",
        f"stage：{stage}",
        f"sha256：{sha}",
    ]
    if attempt is not None:
        lines.append(f"REVIEW_ATTEMPT：{attempt}" + ("（差異複核，不耗額度）" if delta else ""))
    if note:
        lines.append(f"變更說明：{note.strip()}")
    return "\n".join(lines) + "\n"


def build_global_prompt(book: str, chapter: int, *, note: str | None = None) -> str:
    lines = [
        "你是唯讀 reviewer，不得修改任何檔案。這是 commit 前的「全局 review」，不是 stage 審查，"
        "不佔兩次 reviewer 額度。",
        f"書卷：{book}",
        f"章：{chapter}",
        "請通讀這一章目前的 M3 條目內容（.tmp/第x章/entry_content）、M6（chapter_content.yaml）、"
        "link_updates.yaml、渲染後的章 md，以及它們連到的 link_folder 既有條目，只找下列問題：",
        "1. 重大遺漏（來源明確講了、卻沒寫進來的重要內容或該建未建的條目）。",
        "2. 內容失衡（某些主題篇幅畸重或畸輕，或散文與圖表比例失當）。",
        "3. M3／M6 之間、或本章與跨章條目之間的不一致（同一事實說法不同、定義與累積區塊矛盾）。",
        "wording 偏好、文風、可有可無的「更完整」建議一律不算 finding。每個 finding 附可機械複核的錨點。",
        "讀檔可用 MCP：read_chapter_artifact 的 artifact 可傳 entry_content/<條目名>.yaml 與 chapter.md"
        "（渲染後的章 md）；read_chapter_source 與 read_chapter_artifact 都有 start_character，"
        "長檔照回傳的 next_start_character 分段讀到 truncated=false 為止。",
        "最後一行請輸出 `GLOBAL_REVIEW: PASS` 或 `GLOBAL_REVIEW: CHANGES_REQUIRED`。",
    ]
    if note:
        lines.append(f"補充說明：{note.strip()}")
    return "\n".join(lines) + "\n"


# ----------------------------------------------------------------------------
# footer 解析
# ----------------------------------------------------------------------------

def parse_footer(text: str) -> dict:
    """解析 reviewer footer；每個欄位取最後一次出現。缺的欄位不在結果裡。"""
    out = {}
    for key, value_re in _FOOTER_VALUE.items():
        matches = re.findall(key + r":[ \t*`]*" + value_re, text or "")
        if matches:
            value = matches[-1]
            out[key] = value.lower() if key in ("REVIEW_STAGE", "REVIEW_REVIEWER", "REVIEW_SHA256") else value
    return out


def parse_global(text: str) -> str | None:
    matches = GLOBAL_RE.findall(text or "")
    return matches[-1] if matches else None


# ----------------------------------------------------------------------------
# thread 記錄
# ----------------------------------------------------------------------------

def _tmp_dir(book: str, chapter: int, root: Path) -> Path:
    return book_directory(Path(root), book) / ".tmp" / f"第{int(chapter)}章"


def thread_path(book: str, chapter: int, root: Path = ROOT) -> Path:
    return _tmp_dir(book, chapter, root) / THREAD_FILENAME


def load_threads(book: str, chapter: int, root: Path = ROOT) -> dict:
    path = thread_path(book, chapter, root)
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def get_thread(book: str, chapter: int, scope: str, reviewer: str, root: Path = ROOT) -> str | None:
    value = ((load_threads(book, chapter, root).get("threads") or {}).get(scope) or {}).get(reviewer)
    return str(value) if value else None


def save_thread(book: str, chapter: int, scope: str, reviewer: str, thread_id: str | None,
                root: Path = ROOT) -> Path:
    data = load_threads(book, chapter, root)
    data.setdefault("book", book)
    data.setdefault("chapter", int(chapter))
    threads = data.setdefault("threads", {})
    bucket = threads.setdefault(scope, {})
    if thread_id:
        bucket[reviewer] = thread_id
    else:
        bucket.pop(reviewer, None)
    data["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    return write_yaml_atomic(thread_path(book, chapter, root), data)


# ----------------------------------------------------------------------------
# 指令組裝
# ----------------------------------------------------------------------------

def find_codex() -> str:
    """找 codex 執行檔。優先 CODEX_BIN，其次 npm 全域套件裡的 vendor codex.exe，最後 PATH。

    不直接用 codex.cmd：Windows 的 cmd.exe 會弄壞參數裡的雙引號（-c 的 TOML 值）。
    """
    env = os.environ.get("CODEX_BIN")
    if env:
        return env
    found = shutil.which("codex")
    if found:
        base = Path(found).resolve().parent
        for pattern in ("node_modules/@openai/codex/node_modules/@openai/codex-*/vendor/*/bin/codex.exe",
                        "node_modules/@openai/codex/node_modules/@openai/codex-*/vendor/*/codex/codex.exe"):
            hits = sorted(base.glob(pattern))
            if hits:
                return str(hits[-1])
        return found
    raise ReviewCallError("找不到 codex 執行檔（可設環境變數 CODEX_BIN）")


def codex_command(codex_bin: str, root: Path, thread_id: str | None,
                  last_message_file: Path | None = None) -> list[str]:
    if thread_id:
        cmd = [codex_bin, "exec", "resume", thread_id, "--skip-git-repo-check",
               "-c", CODEX_READONLY_CONFIG, "-c", CODEX_MCP_APPROVAL]
    else:
        cmd = [codex_bin, "exec", "--sandbox", "read-only", "--skip-git-repo-check",
               "-c", CODEX_MCP_APPROVAL, "-C", str(root)]
    # 額外的 -c 覆寫（分號分隔），例如在 Windows 沙箱 setup 被某個 MCP runtime 卡住時
    # 只對 reviewer 呼叫停用它：mcp_servers.node_repl.enabled=false。不得用來放寬沙箱。
    for item in os.environ.get("HERMES_CODEX_EXTRA_CONFIG", "").split(";"):
        item = item.strip()
        if item:
            if item.split("=", 1)[0].strip() in {"sandbox_mode", "sandbox"}:
                raise ReviewCallError("HERMES_CODEX_EXTRA_CONFIG 不得覆寫沙箱設定")
            cmd += ["-c", item]
    if last_message_file is not None:
        cmd += ["-o", str(last_message_file)]
    cmd.append("-")
    return cmd


def _version_key(slug: str):
    match = re.match(r"gemini-(\d+(?:\.\d+)*)-([a-z]+)", slug)
    if not match:
        return None
    version = tuple(int(p) for p in match.group(1).split("."))
    family = {"pro": 2, "flash": 1}.get(match.group(2), 0)
    return version, family


def pick_agy_model(models_output: str) -> str:
    """從 ``agy models`` 的輸出挑最新一代、以 -high 結尾的 Gemini；同代 pro 優先於 flash。"""
    best, best_key = None, None
    for line in models_output.splitlines():
        slug = line.strip().split("\t")[0].split()[0] if line.strip() else ""
        if not slug.startswith("gemini-") or not slug.endswith("-high"):
            continue
        key = _version_key(slug)
        if key is None:
            continue
        if best_key is None or key > best_key:
            best, best_key = slug, key
    if not best:
        raise ReviewCallError("`agy models` 的輸出裡找不到以 -high 結尾的 Gemini 模型")
    return best


def list_agy_models() -> str:
    agy = shutil.which("agy") or "agy"
    result = subprocess.run([agy, "models"], capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise ReviewCallError(f"`agy models` 失敗（exit {result.returncode}）：{result.stderr.strip()[:300]}")
    return result.stdout


def agy_command(prompt: str, model: str, conversation_id: str | None) -> list[str]:
    agy = shutil.which("agy") or "agy"
    cmd = [agy, "-p", prompt, "--model", model, "--mode", "plan", "--sandbox",
           "--output-format", "json"]
    if conversation_id:
        cmd += ["--conversation", conversation_id]
    return cmd


def _extract_json_strings(node, keys, found):
    if isinstance(node, dict):
        for key, value in node.items():
            if key in keys and isinstance(value, str) and value:
                found.append((key, value))
            _extract_json_strings(value, keys, found)
    elif isinstance(node, list):
        for item in node:
            _extract_json_strings(item, keys, found)


_AGY_TEXT_KEYS = ("result", "response", "text", "message", "content", "output", "final_response")
_AGY_ID_KEYS = ("conversation_id", "conversationId", "conversation", "session_id", "sessionId",
                "cascade_id", "cascadeId", "trajectory_id", "trajectoryId")


def parse_agy_output(raw: str) -> tuple[str, str | None]:
    """回傳 (最終文字, conversation id)。

    agy 的 json 欄位名稱沒有官方文件，所以這裡盡量寬鬆：整段或逐行嘗試 JSON 解析，
    抓常見的文字／id 欄位；全都抓不到就回傳原始輸出（footer 解析本身不依賴行首，仍然可用）。
    """
    docs = []
    stripped = raw.strip()
    try:
        docs.append(json.loads(stripped))
    except ValueError:
        for line in stripped.splitlines():
            line = line.strip()
            if line.startswith("{") or line.startswith("["):
                try:
                    docs.append(json.loads(line))
                except ValueError:
                    continue
    texts, ids = [], []
    for doc in docs:
        _extract_json_strings(doc, _AGY_TEXT_KEYS, texts)
        _extract_json_strings(doc, _AGY_ID_KEYS, ids)
    text = texts[-1][1] if texts else raw
    # 最後訊息通常含 footer；若最後一個文字欄位沒有，改用含 footer 的那個
    if "REVIEW_STATUS" not in text and "GLOBAL_REVIEW" not in text:
        for _key, value in reversed(texts):
            if "REVIEW_STATUS" in value or "GLOBAL_REVIEW" in value:
                text = value
                break
    conversation = None
    for _key, value in reversed(ids):
        match = UUID_RE.search(value)
        if match:
            conversation = match.group(0)
            break
        if re.fullmatch(r"[\w-]{8,}", value):
            conversation = value
            break
    if conversation is None:
        match = re.search(r"conversation[ _-]?id\W{0,5}([0-9a-fA-F-]{8,})", raw, re.IGNORECASE)
        if match:
            conversation = match.group(1)
    return text, conversation


# ----------------------------------------------------------------------------
# repo 變動偵測
# ----------------------------------------------------------------------------

_GUARD_EXCLUDES = (f"/{LOG_DIRNAME}/", f"/{THREAD_FILENAME}")


def _is_guard_excluded(path: str) -> bool:
    norm = "/" + path.replace("\\", "/")
    return any(token in norm for token in _GUARD_EXCLUDES)


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(root), "-c", "core.quotepath=false", *args],
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise ReviewCallError(f"git {' '.join(args)} 失敗：{result.stderr.strip()[:200]}")
    return result.stdout


def git_snapshot(root: Path = ROOT) -> dict:
    """repo 指紋：``git status --porcelain`` 與 ``git diff`` 的雜湊，加上每個有變動檔案的內容雜湊。

    本工具自己寫的 review_logs／reviewer_thread.yaml 不算（它們在 reviewer 結束後才寫，
    但先前呼叫留下的檔案仍會出現在 status，要排除才不會誤報）。
    """
    status_raw = _git(root, "status", "--porcelain", "--untracked-files=all")
    status_lines = [line for line in status_raw.splitlines()
                    if not _is_guard_excluded(line[3:].strip().strip('"'))]
    diff_raw = _git(root, "diff", "--no-color")
    files = {}
    for line in status_lines:
        rel = line[3:].strip().strip('"')
        if " -> " in rel:
            rel = rel.split(" -> ")[-1]
        path = Path(root) / rel
        if path.is_file():
            try:
                if path.stat().st_size <= 4_000_000:
                    files[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
            except OSError:
                files[rel] = "unreadable"
    return {
        "status_hash": hashlib.sha256("\n".join(status_lines).encode("utf-8")).hexdigest(),
        "diff_hash": hashlib.sha256(diff_raw.encode("utf-8")).hexdigest(),
        "status_lines": status_lines,
        "files": files,
    }


def snapshot_changes(before: dict, after: dict) -> list[str]:
    """兩次指紋之間有差異的路徑（空清單＝沒變）。"""
    changed = set()
    b_paths = {line[3:].strip().strip('"') for line in before["status_lines"]}
    a_paths = {line[3:].strip().strip('"') for line in after["status_lines"]}
    changed |= b_paths ^ a_paths
    for path in b_paths & a_paths:
        if before["files"].get(path) != after["files"].get(path):
            changed.add(path)
    if not changed and (before["status_hash"] != after["status_hash"]
                        or before["diff_hash"] != after["diff_hash"]):
        changed.add("（git status／diff 指紋改變，無法定位到單一路徑）")
    return sorted(changed)


# ----------------------------------------------------------------------------
# 執行
# ----------------------------------------------------------------------------

def _run_process(cmd: list[str], stdin_text: str | None, cwd: Path, log_path: Path) -> int:
    """跑子行程，stdout＋stderr 合併即時寫進 log_path；不設 timeout。測試時 patch 這個函式。"""
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    with open(log_path, "wb") as log:
        proc = subprocess.Popen(
            cmd, cwd=str(cwd), env=env, stdin=subprocess.PIPE if stdin_text is not None else None,
            stdout=log, stderr=subprocess.STDOUT)
        try:
            if stdin_text is not None:
                proc.stdin.write(stdin_text.encode("utf-8"))
                proc.stdin.close()
            return proc.wait()
        except KeyboardInterrupt:
            proc.terminate()
            raise


def _next_log_path(book: str, chapter: int, label: str, root: Path) -> Path:
    log_dir = _tmp_dir(book, chapter, root) / LOG_DIRNAME
    seqs = []
    for existing in log_dir.glob(f"{label}_*.out") if log_dir.is_dir() else []:
        match = re.fullmatch(rf"{re.escape(label)}_(\d+)\.out", existing.name)
        if match:
            seqs.append(int(match.group(1)))
    return log_dir / f"{label}_{(max(seqs) + 1) if seqs else 1}.out"


def _quote_for_display(cmd: list[str], long_arg_limit: int = 80) -> str:
    shown = []
    for arg in cmd:
        # 只縮短 prompt 這種多行長參數；執行檔路徑與 -c 旗標要完整顯示
        shown.append(arg if "\n" not in arg or len(arg) <= long_arg_limit
                     else arg[:long_arg_limit].replace("\n", " ") + "…")
    return " ".join(shlex.quote(a) if re.search(r"[\s\"'$`]", a) else a for a in shown)


def _quota_message(reviewer: str, text: str) -> str:
    quota_line = next((l.strip() for l in text.splitlines() if QUOTA_RE.search(l)), "")
    reset = RESET_RE.search(text)
    parts = [f"❌ {reviewer} 額度用完（quota／429）。"]
    if quota_line:
        parts.append(f"   訊息：{quota_line[:200]}")
    parts.append("   重置時間：" + (reset.group(1).strip()[:160] if reset
                                    else "輸出裡沒有重置時間；可用 `agy -p \"/usage\"`（agy）或稍後再試"))
    parts.append("   BLOCKED 不耗 attempt：可改用另一位 reviewer（--reviewer）接手同一個 sha。")
    return "\n".join(parts)


def run_review(book: str, chapter: int, stage: str | None, *, reviewer: str = "codex",
               note: str | None = None, global_review: bool = False, dry_run: bool = False,
               root: Path = ROOT, out=print) -> int:
    canonical = canonical_book_name(book)
    chapter = int(chapter)
    if reviewer not in REVIEWERS:
        raise ReviewCallError(f"--reviewer 必須是：{', '.join(REVIEWERS)}")
    root = Path(root)
    # 每個 stage 各用自己的 thread；同一 stage 的第二次審查才延續。
    scope = "global" if global_review else str(stage)
    label = "global" if global_review else str(stage)

    sha = attempt = None
    delta = False
    if global_review:
        prompt = build_global_prompt(canonical, chapter, note=note)
    else:
        if stage not in STAGES:
            raise ReviewCallError(f"stage 必須是：{', '.join(STAGES)}")
        state = agent_review._read_state(canonical, chapter, root)
        record = agent_review._stage_record(state, stage)
        sha = str(record.get("sha256") or "")
        if not sha:
            raise ReviewCallError(
                f"{stage} 尚未 submit，沒有 checkpoint sha；先跑 "
                f"python util/agent_review.py submit {canonical} {chapter} {stage}")
        delta = record.get("review_mode") == "delta" and agent_review._review_status(record) == "pending"
        attempt = min(agent_review._review_attempts(record) + (0 if delta else 1),
                      agent_review.MAX_REVIEW_ATTEMPTS)
        attempt = max(attempt, 1)
        prompt = build_prompt(canonical, chapter, stage, sha, attempt=attempt, delta=delta, note=note)
        if agent_review._review_status(record) == "pass" and not delta:
            out("ℹ️ 這個 stage 目前已是 PASS；若仍要呼叫 reviewer 請確認是否真的需要。")
        if record.get("forced_pass"):
            message = f"{stage} 已 FORCED PASS（兩次 reviewer 額度用盡），禁止第三次 reviewer call"
            if not dry_run:
                raise ReviewCallError(message)
            out(f"⚠️ {message}（dry-run 僅預覽，正式執行會拒絕）")

    thread_id = get_thread(canonical, chapter, scope, reviewer, root)
    log_path = _next_log_path(canonical, chapter, label, root)

    work_dir = Path(tempfile.mkdtemp(prefix="review_call_"))
    tmp_log = work_dir / log_path.name
    last_message = work_dir / "last_message.txt"

    if reviewer == "codex":
        cmd = codex_command(find_codex(), root, thread_id, last_message)
        stdin_text = prompt
    else:
        model = pick_agy_model(list_agy_models())
        cmd = agy_command(prompt, model, thread_id)
        stdin_text = None

    out(f"reviewer：{reviewer}｜{'全局 review' if global_review else f'stage={stage}'}｜"
        f"{'延續 thread ' + thread_id if thread_id else '新 thread'}")
    out("指令：" + _quote_for_display(cmd))
    if dry_run:
        out("── prompt ──")
        out(prompt.rstrip())
        out("── dry-run：未執行 reviewer、未寫任何檔案 ──")
        out(f"（正式執行時 log 會存到 {log_path}）")
        shutil.rmtree(work_dir, ignore_errors=True)
        return EXIT_OK

    try:
        before = git_snapshot(root)
    except ReviewCallError as exc:
        before = None
        out(f"⚠️ 無法取得 git 指紋，略過 repo 變動偵測：{exc}")

    out(f"執行中（不設 timeout，審查常要 10–20 分鐘）；即時輸出可 tail：{tmp_log}")
    started = time.time()
    code = _run_process(cmd, stdin_text, root, tmp_log)
    elapsed = time.time() - started
    raw = tmp_log.read_text(encoding="utf-8", errors="replace") if tmp_log.is_file() else ""

    # resume 失敗（thread 遺失）→ 清掉舊 id 後開新的一次
    if (reviewer == "codex" and thread_id and code != 0
            and re.search(r"no (saved )?session|session .{0,40}not found|could not find|找不到", raw, re.IGNORECASE)
            and not QUOTA_RE.search(raw)):
        out(f"⚠️ 找不到可延續的 thread {thread_id}，改開新的 thread。")
        thread_id = None
        cmd = codex_command(find_codex(), root, None, last_message)
        code = _run_process(cmd, prompt, root, tmp_log)
        raw = tmp_log.read_text(encoding="utf-8", errors="replace") if tmp_log.is_file() else ""

    # 最終訊息
    if reviewer == "codex":
        final_text = (last_message.read_text(encoding="utf-8", errors="replace")
                      if last_message.is_file() else "")
        new_thread = thread_id or (SESSION_ID_RE.findall(raw) or [None])[0]
    else:
        final_text, conversation = parse_agy_output(raw)
        new_thread = conversation or thread_id
    if not final_text.strip():
        final_text = raw

    after = None
    if before is not None:
        try:
            after = git_snapshot(root)
        except ReviewCallError as exc:
            out(f"⚠️ 無法取得執行後的 git 指紋：{exc}")

    # 寫 log／thread（在 after 快照之後）
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(raw, encoding="utf-8")
    shutil.rmtree(work_dir, ignore_errors=True)
    if new_thread and not (code != 0 and not final_text.strip()):
        save_thread(canonical, chapter, scope, reviewer, new_thread, root)

    out(f"reviewer 結束（exit {code}，{elapsed / 60:.1f} 分鐘）；完整輸出：{log_path}")
    if new_thread:
        out(f"thread id：{new_thread}（存於 {thread_path(canonical, chapter, root)}）")

    exit_code = EXIT_OK
    if before is not None and after is not None:
        changed = snapshot_changes(before, after)
        if changed:
            exit_code = EXIT_REPO_CHANGED
            out("!" * 70)
            out("‼️ 警告：reviewer 執行期間 repo 有檔案被改動（reviewer 應為唯讀）！")
            for path in changed:
                mark = "  <<< util/" if path.replace("\\", "/").startswith("util/") else ""
                out(f"   {path}{mark}")
            out("   請先 `git status` / `git diff` 檢視；若是 util/ 被改，不要採信這次 verdict。")
            out("   （若是你自己或別的行程同時在改檔，結果也同樣不可信，建議重跑。）")
            out("!" * 70)

    if code != 0 and not parse_footer(final_text) and QUOTA_RE.search(raw):
        out(_quota_message(reviewer, raw))
        return EXIT_QUOTA if exit_code == EXIT_OK else exit_code

    out("── reviewer 最終訊息 ──")
    out(final_text.rstrip())
    out("── 最終訊息結束 ──")

    if global_review:
        verdict = parse_global(final_text)
        if verdict:
            out(f"GLOBAL_REVIEW 結果：{verdict}（全局 review 不記 verdict、不耗 stage 額度）")
            return exit_code
        out("⚠️ 沒有找到 `GLOBAL_REVIEW: PASS|CHANGES_REQUIRED` 這一行。")
        return exit_code if exit_code != EXIT_OK else EXIT_NO_FOOTER

    footer = parse_footer(final_text)
    required = ("REVIEW_SHA256", "REVIEW_STATUS", "FINDINGS_COUNT")
    missing = [key for key in required if key not in footer]
    if missing:
        out(f"⚠️ footer 缺欄位：{', '.join(missing)}；無法產生 verdict 指令，請人工查看上面的訊息／log。")
        return exit_code if exit_code != EXIT_OK else EXIT_NO_FOOTER

    if footer.get("REVIEW_STAGE") and footer["REVIEW_STAGE"] != stage:
        out(f"⚠️ footer 的 REVIEW_STAGE={footer['REVIEW_STAGE']} 與呼叫的 stage={stage} 不符。")
    if footer.get("REVIEW_REVIEWER") and footer["REVIEW_REVIEWER"] != reviewer:
        out(f"⚠️ footer 的 REVIEW_REVIEWER={footer['REVIEW_REVIEWER']} 與實際 reviewer={reviewer} 不符。")
    status = footer["REVIEW_STATUS"].lower()
    review_sha = footer["REVIEW_SHA256"]

    try:
        current = agent_review.stage_fingerprint(canonical, chapter, stage, root)
    except agent_review.ReviewGateError:
        current = None
    sha_note = []
    if review_sha != sha:
        sha_note.append(f"⚠️ reviewer 回報的 sha（{review_sha}）與送審時的 checkpoint（{sha}）不同。")
    if current is not None and current != review_sha:
        sha_note.append(f"⚠️ 目前內容的 sha（{current}）與 reviewer 看到的（{review_sha}）不同——"
                        "reviewer 審查期間或之後內容已變；下面的指令改用 --observed-sha 補記。")
    for line in sha_note:
        out(line)
    stale = bool(sha_note)

    verdict_cmd = (f"python util/agent_review.py verdict {canonical} {chapter} {stage} {status} "
                   f"--sha {review_sha} --reviewer {reviewer} --findings-count {footer['FINDINGS_COUNT']}")
    if new_thread:
        verdict_cmd += f" --thread-id {new_thread}"
    if stale:
        verdict_cmd += f" --observed-sha {review_sha}"
    out("下一步（未自動記錄 verdict，確認後再執行）：")
    out(verdict_cmd)
    return exit_code


def main(argv: list[str] | None = None) -> int:
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="呼叫 Codex／Antigravity 做唯讀 stage audit（或全局 review）")
    parser.add_argument("book")
    parser.add_argument("chapter", type=int)
    parser.add_argument("stage", nargs="?", choices=STAGES,
                        help="m3／m6／link_updates（--global-review 時可省略）")
    parser.add_argument("--reviewer", choices=REVIEWERS, default="codex")
    parser.add_argument("--note", help="給 reviewer 的一句變更說明")
    parser.add_argument("--global-review", action="store_true",
                        help="commit 前全局 review（獨立 thread，不佔 stage 額度）")
    parser.add_argument("--dry-run", action="store_true",
                        help="只印出將執行的指令與 prompt，不呼叫 reviewer、不寫檔")
    args = parser.parse_args(argv)
    if not args.global_review and not args.stage:
        parser.error("需要 stage（m3／m6／link_updates），或改用 --global-review")
    try:
        return run_review(args.book, args.chapter, args.stage, reviewer=args.reviewer,
                          note=args.note, global_review=args.global_review, dry_run=args.dry_run)
    except (ReviewCallError, agent_review.ReviewGateError, ValueError, OSError, yaml.YAMLError) as exc:
        print(f"❌ {exc}")
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
