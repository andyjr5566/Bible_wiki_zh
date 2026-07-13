#!/usr/bin/env python3
"""模型呼叫層 + 端點控制器：schema 強制 + 重試迴圈 + 可切換端點。

orchestrator 只在「內容任務」節點呼叫模型。實際打哪個端點由
`_config/model_endpoints.yaml` 的 active 決定，可用 CLI 或 MODEL_ENDPOINT
環境變數隨時切換（localhost:4000／localhost:4001／claude -p 等）。

每次呼叫：
  1. 取得 active 端點的 runner（openai 相容 HTTP 或 shell 到 claude -p）。
  2. 把 prompt 交給 runner，取回文字。
  3. 從文字抽出 YAML/JSON payload。
  4. 用傳入的 validate() 檢查；不合格時把「具體錯誤 + 原輸出」回饋重試，
     上限 retries 次；全數失敗丟 ModelValidationError，交 orchestrator
     標記人工處理。

runner 可注入，讓 orchestrator 控制流程能以假模型單元測試。
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
ENDPOINTS_FILE = ROOT / "_config" / "model_endpoints.yaml"
ENV_ENDPOINT = "MODEL_ENDPOINT"

FENCE_RE = re.compile(r"```(?:ya?ml|json)?\s*\n(.*?)```", re.S)
DEFAULT_OPENAI_BASE_URL = "http://localhost:4000/v1"
DEFAULT_OPENAI_MODEL = "deepseek-ai/deepseek-v4-pro"


class ModelError(RuntimeError):
    """呼叫模型或解析回應時的可預期錯誤。"""


class ModelValidationError(ModelError):
    """重試上限內 payload 始終不合格。"""


# --------------------------------------------------------------------------- #
# 端點控制器
# --------------------------------------------------------------------------- #
def load_endpoints(path=ENDPOINTS_FILE):
    if not path.exists():
        return {"active": "claude-cli", "endpoints": {"claude-cli": {"type": "claude"}}}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data.get("endpoints"), dict) or not data["endpoints"]:
        raise ModelError(f"{path.name} 缺少 endpoints 設定")
    if data.get("active") not in data["endpoints"]:
        raise ModelError(f"{path.name} 的 active「{data.get('active')}」不在 endpoints 內")
    return data


def select_endpoint(name=None, config=None, task=None):
    """選端點，優先序：明確指定 → MODEL_ENDPOINT → 該 task 的 MODEL_ENDPOINT_<TASK>
    → tasks.<task>（設定檔）→ active。

    task 用來把「做條目」（entry）與「本章整理」（chapter）等內容任務分開指定
    端點，設定見 `_config/model_endpoints.yaml` 的 tasks 區塊；未列出的 task
    或未傳 task 時退回 active。
    """
    config = config or load_endpoints()
    endpoints = config["endpoints"]
    task_env = os.environ.get(f"{ENV_ENDPOINT}_{task.upper()}") if task else None
    task_default = (config.get("tasks") or {}).get(task) if task else None
    chosen = (
        name or task_env or os.environ.get(ENV_ENDPOINT) or task_default
        or config["active"]
    )
    if chosen not in endpoints:
        raise ModelError(f"未知端點「{chosen}」；可用：{', '.join(endpoints)}")
    endpoint = dict(endpoints[chosen])
    endpoint["name"] = chosen
    return endpoint


def _endpoint_api_key(endpoint):
    if endpoint.get("api_key"):
        return endpoint["api_key"]
    env_name = endpoint.get("api_key_env")
    return os.environ.get(env_name) if env_name else None


def make_runner(endpoint):
    """把端點設定轉成 runner 函式（prompt → 文字）。"""
    kind = endpoint.get("type", "openai")
    if kind == "claude":
        model = endpoint.get("model")
        effort = endpoint.get("effort")
        return lambda prompt: claude_runner(prompt, model=model, effort=effort)
    if kind == "openai":
        base_url = endpoint.get("base_url", DEFAULT_OPENAI_BASE_URL)
        model = endpoint.get("model", DEFAULT_OPENAI_MODEL)
        api_key = _endpoint_api_key(endpoint)
        return lambda prompt: openai_runner(
            prompt, base_url=base_url, model=model, api_key=api_key
        )
    raise ModelError(f"未知端點 type「{kind}」")


def active_runner(task=None):
    return make_runner(select_endpoint(task=task))


def set_active(name, path=ENDPOINTS_FILE):
    """切換 active 端點（保留檔案註解）。"""
    config = load_endpoints(path)
    if name not in config["endpoints"]:
        raise ModelError(f"未知端點「{name}」；可用：{', '.join(config['endpoints'])}")
    text = path.read_text(encoding="utf-8")
    new_text, count = re.subn(r"(?m)^active:.*$", f"active: {name}", text, count=1)
    if count != 1:
        raise ModelError(f"{path.name} 找不到可替換的 active 行")
    path.write_text(new_text, encoding="utf-8")


# --------------------------------------------------------------------------- #
# runners
# --------------------------------------------------------------------------- #
def openai_runner(prompt, *, base_url=DEFAULT_OPENAI_BASE_URL,
                  model=DEFAULT_OPENAI_MODEL, api_key=None, timeout=1500):
    """OpenAI 相容 /chat/completions（本機 litellm proxy 等）。"""
    url = base_url.rstrip("/") + "/chat/completions"
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
    }).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError) as exc:
        raise ModelError(f"呼叫 {url} 失敗：{exc}") from exc
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ModelError(f"回應格式非預期：{str(data)[:300]}") from exc


def _find_claude_cli():
    """尋找 claude CLI：先查 PATH，再查常見安裝位置（Windows 原生安裝器不改當前程序的 PATH）。"""
    found = shutil.which("claude")
    if found:
        return found
    home = os.path.expanduser("~")
    for candidate in (
        os.path.join(home, ".local", "bin", "claude.exe"),
        os.path.join(home, ".local", "bin", "claude"),
        os.path.join(os.environ.get("APPDATA", ""), "npm", "claude.cmd"),
    ):
        if candidate and os.path.isfile(candidate):
            return candidate
    return None


def claude_runner(prompt, *, model=None, effort=None, timeout=1500):
    """shell 到 `claude -p --output-format json`，取出 result 文字。"""
    claude_cli = _find_claude_cli()
    if not claude_cli:
        raise ModelError("找不到 claude CLI；請確認 Claude Code 已安裝於 PATH")
    command = [claude_cli, "-p", "--output-format", "json"]
    if model:
        command += ["--model", model]
    if effort:
        command += ["--effort", effort]
    try:
        result = subprocess.run(
            command, input=prompt, capture_output=True,
            text=True, encoding="utf-8", timeout=timeout,
        )
    except FileNotFoundError as exc:
        raise ModelError("找不到 claude CLI；請確認 Claude Code 已安裝於 PATH") from exc
    if result.returncode != 0:
        raise ModelError(
            f"claude -p 失敗（exit {result.returncode}）：{result.stderr.strip()[:500]}"
        )
    return _result_text(result.stdout)


def _result_text(stdout):
    """從 `claude -p --output-format json` 的封套取出 assistant 文字。"""
    try:
        envelope = json.loads(stdout)
    except json.JSONDecodeError:
        return stdout
    if isinstance(envelope, dict) and "result" in envelope:
        return envelope["result"]
    return stdout


# --------------------------------------------------------------------------- #
# payload 抽取 + 驗證重試
# --------------------------------------------------------------------------- #
def extract_payload(text):
    match = FENCE_RE.search(text)
    block = match.group(1) if match else text
    try:
        data = yaml.safe_load(block)
    except yaml.YAMLError as exc:
        raise ModelError(f"模型輸出無法解析為 YAML/JSON：{exc}") from exc
    if not isinstance(data, (dict, list)):
        raise ModelError("模型輸出不是合法 YAML/JSON 物件")
    return data


def _retry_prompt(base_prompt, previous_output, errors):
    bullet = "\n".join(f"- {error}" for error in errors)
    return (
        f"{base_prompt}\n\n"
        f"【上次輸出未通過驗證，請修正】\n"
        f"錯誤：\n{bullet}\n\n"
        f"你上次的輸出：\n{previous_output}\n\n"
        f"請只輸出修正後、完全符合規格的 payload，不要任何說明文字。"
    )


def call_model(prompt, *, validate=None, retries=3, runner=None, label="task",
                retry_delay=5, task=None):
    """呼叫模型並取得通過驗證的 payload；失敗上限後丟 ModelValidationError。

    task（如 "entry"／"chapter"）在未明確傳入 runner 時，交給
    select_endpoint 依 `_config/model_endpoints.yaml` 的 tasks 對照選端點，
    讓「做條目」與「本章整理」可各自指定端點。
    """
    runner = runner or active_runner(task=task)
    current_prompt = prompt
    last_errors = ["未取得任何有效輸出"]
    for _ in range(max(1, retries)):
        last_output = runner(current_prompt)
        try:
            payload = extract_payload(last_output)
        except ModelError as exc:
            last_errors = [str(exc)]
            current_prompt = _retry_prompt(prompt, last_output, last_errors)
            continue
        errors = list(validate(payload)) if validate else []
        if not errors:
            return payload
        last_errors = errors
        current_prompt = _retry_prompt(prompt, last_output, errors)
    raise ModelValidationError(
        f"{label}：重試 {retries} 次仍不合格：{'; '.join(last_errors)}"
    )


# --------------------------------------------------------------------------- #
# CLI 控制器
# --------------------------------------------------------------------------- #
def _cmd_list(_args):
    config = load_endpoints()
    active = config["active"]
    for name, endpoint in config["endpoints"].items():
        marker = "＊" if name == active else "  "
        target = endpoint.get("base_url") or endpoint.get("type")
        model = endpoint.get("model") or "（預設）"
        effort = endpoint.get("effort")
        suffix = f" / effort={effort}" if effort else ""
        print(f"{marker} {name}: {target} / {model}{suffix}")
    tasks = config.get("tasks") or {}
    if tasks:
        print("任務路由：")
        for task, endpoint_name in tasks.items():
            print(f"  {task} → {endpoint_name}")
    override = os.environ.get(ENV_ENDPOINT)
    if override:
        print(f"（MODEL_ENDPOINT 覆蓋中：{override}）")
    for task in tasks:
        task_override = os.environ.get(f"{ENV_ENDPOINT}_{task.upper()}")
        if task_override:
            print(f"（MODEL_ENDPOINT_{task.upper()} 覆蓋中：{task_override}）")
    return 0


def _cmd_use(args):
    set_active(args.name)
    print(f"✅ active 端點已切換為：{args.name}")
    return 0


def _cmd_test(args):
    endpoint = select_endpoint(args.name, task=args.task)
    runner = make_runner(endpoint)
    prompt = (
        "只輸出下列 YAML（放在 ```yaml code block 內），不要任何其他文字：\n"
        "```yaml\nok: true\nendpoint: 測試\n```"
    )
    try:
        payload = call_model(prompt, validate=lambda p: [] if p.get("ok") else ["缺少 ok"], runner=runner)
    except ModelError as exc:
        print(f"❌ {endpoint['name']} 測試失敗：{exc}")
        return 1
    print(f"✅ {endpoint['name']} 回應正常：{payload}")
    return 0


def main():
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="模型端點控制器")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="列出端點與 active").set_defaults(func=_cmd_list)
    use_parser = sub.add_parser("use", help="切換 active 端點")
    use_parser.add_argument("name")
    use_parser.set_defaults(func=_cmd_use)
    test_parser = sub.add_parser("test", help="對端點做一次煙霧測試")
    test_parser.add_argument("name", nargs="?", default=None)
    test_parser.add_argument(
        "--task", default=None,
        help="改測 tasks 對照選出的端點（如 entry／chapter），與 name 併用時 name 優先",
    )
    test_parser.set_defaults(func=_cmd_test)
    args = parser.parse_args()
    try:
        return args.func(args)
    except ModelError as exc:
        print(f"❌ {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
