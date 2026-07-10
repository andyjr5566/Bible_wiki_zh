#!/usr/bin/env python3
"""模型呼叫層：schema 強制 + 重試迴圈 + 最小輸入。

orchestrator 只在「內容任務」節點呼叫模型。每次呼叫：
  1. 把 prompt 交給 runner（預設 shell 到 `claude -p --output-format json`）。
  2. 從回應抽出 YAML/JSON payload。
  3. 用傳入的 validate() 檢查 payload（schema／語義）。
  4. 不合格時把「具體錯誤 + 原輸出」回饋給模型重試，上限 retries 次；
     全數失敗則丟 ModelValidationError，交由 orchestrator 標記人工處理。

runner 可注入，讓 orchestrator 的控制流程能以假模型單元測試，不需真的
花 token 呼叫 claude。
"""
import json
import re
import subprocess
import sys

import yaml

FENCE_RE = re.compile(r"```(?:ya?ml|json)?\s*\n(.*?)```", re.S)


class ModelError(RuntimeError):
    """呼叫模型或解析回應時的可預期錯誤。"""


class ModelValidationError(ModelError):
    """重試上限內 payload 始終不合格。"""


def claude_runner(prompt, *, model=None, timeout=600):
    """預設 runner：呼叫 `claude -p --output-format json` 並取出 result 文字。"""
    command = ["claude", "-p", "--output-format", "json"]
    if model:
        command += ["--model", model]
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


def extract_payload(text):
    """從模型文字取出 payload；優先 fenced code block，否則整段當 YAML。"""
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


def call_model(prompt, *, validate=None, retries=3, runner=None, label="task"):
    """呼叫模型並取得通過驗證的 payload；失敗上限後丟 ModelValidationError。"""
    runner = runner or claude_runner
    current_prompt = prompt
    last_errors = ["未取得任何有效輸出"]
    last_output = ""
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


def _main():
    """CLI 煙霧測試：從 stdin 讀 prompt，用真 claude runner 回一段 payload。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")
    prompt = sys.stdin.read()
    try:
        payload = call_model(prompt, label="cli-smoke")
    except ModelError as exc:
        print(f"❌ {exc}")
        return 1
    sys.stdout.write(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
