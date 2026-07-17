import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

UTIL_DIR = Path(__file__).resolve().parents[1]
if str(UTIL_DIR) not in sys.path:
    sys.path.insert(0, str(UTIL_DIR))

import model_client
from model_client import (
    ModelError,
    ModelValidationError,
    _result_text,
    call_model,
    embed_texts,
    extract_payload,
    load_endpoints,
    make_runner,
    select_endpoint,
    set_active,
)

CONFIG = {
    "active": "local-4000",
    "tasks": {
        "entry": "local-4001",
        "chapter": "claude-cli",
        "embedding": {
            "endpoint": "local-4000",
            "model": "embed-model",
            "kind": "embedding",
        },
    },
    "endpoints": {
        "local-4000": {"type": "openai", "base_url": "http://localhost:4000/v1", "model": "m-a"},
        "local-4001": {"type": "openai", "base_url": "http://localhost:4001/v1", "model": "m-b"},
        "claude-cli": {"type": "claude", "model": None},
    },
}


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def read(self):
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class ExtractPayloadTests(unittest.TestCase):
    def test_extracts_from_fenced_yaml_block(self):
        text = "說明\n```yaml\nname: 測試\ntype: 原文\n```\n結尾"
        self.assertEqual({"name": "測試", "type": "原文"}, extract_payload(text))

    def test_parses_bare_yaml(self):
        self.assertEqual({"a": 1, "b": 2}, extract_payload("a: 1\nb: 2\n"))

    def test_rejects_non_object_output(self):
        with self.assertRaises(Exception):
            extract_payload("這只是一句話，沒有結構")

    def test_result_text_unwraps_claude_envelope(self):
        envelope = json.dumps({"type": "result", "result": "name: 測試"})
        self.assertEqual("name: 測試", _result_text(envelope))


class CallModelRetryTests(unittest.TestCase):
    def test_returns_on_first_valid_output(self):
        calls = []

        def runner(prompt):
            calls.append(prompt)
            return "name: ok"

        payload = call_model(runner=runner, prompt="P", validate=lambda p: [])
        self.assertEqual({"name": "ok"}, payload)
        self.assertEqual(1, len(calls))

    def test_retries_with_error_feedback_then_succeeds(self):
        outputs = ["value: 1", "value: 2"]
        prompts = []

        def runner(prompt):
            prompts.append(prompt)
            return outputs[len(prompts) - 1]

        def validate(payload):
            return [] if payload.get("value") == 2 else ["value 必須是 2"]

        payload = call_model(runner=runner, prompt="P", validate=validate, retries=3)
        self.assertEqual({"value": 2}, payload)
        self.assertEqual(2, len(prompts))
        # 第二次 prompt 必須帶入上一輪的具體錯誤
        self.assertIn("value 必須是 2", prompts[1])

    def test_raises_after_retries_exhausted(self):
        def runner(prompt):
            return "value: 0"

        with self.assertRaises(ModelValidationError):
            call_model(
                runner=runner, prompt="P",
                validate=lambda p: ["永遠不合格"], retries=3, label="t",
            )


class EndpointControllerTests(unittest.TestCase):
    def test_select_prefers_explicit_over_env_over_active(self):
        self.assertEqual("local-4001", select_endpoint("local-4001", config=CONFIG)["name"])
        with patch.dict("os.environ", {"MODEL_ENDPOINT": "claude-cli"}):
            self.assertEqual("claude-cli", select_endpoint(config=CONFIG)["name"])
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual("local-4000", select_endpoint(config=CONFIG)["name"])

    def test_select_unknown_endpoint_raises(self):
        with self.assertRaises(ModelError):
            select_endpoint("does-not-exist", config=CONFIG)

    def test_select_task_default_used_when_no_explicit_or_env(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(
                "local-4001", select_endpoint(config=CONFIG, task="entry")["name"]
            )
            self.assertEqual(
                "claude-cli", select_endpoint(config=CONFIG, task="chapter")["name"]
            )
            # 沒有對照或沒傳 task：退回 active
            self.assertEqual(
                "local-4000", select_endpoint(config=CONFIG, task="unknown-task")["name"]
            )
            self.assertEqual("local-4000", select_endpoint(config=CONFIG)["name"])

    def test_select_task_env_override_beats_task_default(self):
        with patch.dict("os.environ", {"MODEL_ENDPOINT_ENTRY": "claude-cli"}, clear=True):
            self.assertEqual(
                "claude-cli", select_endpoint(config=CONFIG, task="entry")["name"]
            )
            # 不影響其他 task
            self.assertEqual(
                "claude-cli", select_endpoint(config=CONFIG, task="chapter")["name"]
            )

    def test_select_explicit_name_beats_task_routing(self):
        with patch.dict("os.environ", {"MODEL_ENDPOINT_ENTRY": "claude-cli"}, clear=True):
            self.assertEqual(
                "local-4000",
                select_endpoint("local-4000", config=CONFIG, task="entry")["name"],
            )

    def test_select_task_mapping_overrides_model_and_kind(self):
        with patch.dict("os.environ", {}, clear=True):
            endpoint = select_endpoint(config=CONFIG, task="embedding")
        self.assertEqual("local-4000", endpoint["name"])
        self.assertEqual("embed-model", endpoint["model"])
        self.assertEqual("embedding", endpoint["kind"])
        # 其他 task 選到同端點時不受 embedding 的 model 影響
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual("m-a", select_endpoint(config=CONFIG)["model"])

    def test_select_task_mapping_model_dropped_when_env_switches_endpoint(self):
        with patch.dict(
            "os.environ", {"MODEL_ENDPOINT_EMBEDDING": "local-4001"}, clear=True
        ):
            endpoint = select_endpoint(config=CONFIG, task="embedding")
        # env 覆蓋＝整組覆蓋：用 local-4001 自己的 model
        self.assertEqual("local-4001", endpoint["name"])
        self.assertEqual("m-b", endpoint["model"])

    def test_task_mapping_without_endpoint_raises(self):
        broken = dict(CONFIG, tasks={"embedding": {"model": "x"}})
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ModelError):
                select_endpoint(config=broken, task="embedding")

    def test_make_runner_openai_posts_and_parses(self):
        endpoint = select_endpoint("local-4000", config=CONFIG)
        runner = make_runner(endpoint)
        captured = {}

        def fake_urlopen(request, timeout=None):
            captured["url"] = request.full_url
            captured["body"] = json.loads(request.data.decode("utf-8"))
            return _FakeResponse({"choices": [{"message": {"content": "name: 從代理"}}]})

        with patch.object(model_client.urllib.request, "urlopen", fake_urlopen):
            text = runner("這是 prompt")
        self.assertEqual("name: 從代理", text)
        self.assertEqual("http://localhost:4000/v1/chat/completions", captured["url"])
        self.assertEqual("m-a", captured["body"]["model"])

    def test_make_runner_claude_dispatches_to_claude_runner(self):
        endpoint = select_endpoint("claude-cli", config=CONFIG)
        runner = make_runner(endpoint)
        with patch.object(model_client, "claude_runner", return_value="ok: 1") as spy:
            runner("prompt")
        spy.assert_called_once()

    def test_set_active_rewrites_line_and_keeps_comments(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "model_endpoints.yaml"
            path.write_text(
                "# 註解必須保留\nactive: local-4000\nendpoints:\n"
                "  local-4000: {type: openai, base_url: u, model: m}\n"
                "  local-4001: {type: openai, base_url: u2, model: m2}\n",
                encoding="utf-8",
            )
            set_active("local-4001", path=path)
            reloaded = load_endpoints(path)
            self.assertEqual("local-4001", reloaded["active"])
            self.assertIn("# 註解必須保留", path.read_text(encoding="utf-8"))

    def test_load_endpoints_rejects_active_not_in_endpoints(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "model_endpoints.yaml"
            path.write_text(
                "active: 不存在\nendpoints:\n  x: {type: openai, base_url: u, model: m}\n",
                encoding="utf-8",
            )
            with self.assertRaises(ModelError):
                load_endpoints(path)


class EmbedTextsTests(unittest.TestCase):
    def test_batches_and_preserves_order(self):
        calls = []

        def fake_runner(batch):
            calls.append(list(batch))
            return [[float(len(text))] for text in batch]

        vectors = embed_texts(
            ["一", "二二", "三三三"], batch_size=2, runner=fake_runner
        )
        self.assertEqual([["一", "二二"], ["三三三"]], calls)
        self.assertEqual([[1.0], [2.0], [3.0]], vectors)

    def test_empty_input_returns_empty_without_calls(self):
        def exploding_runner(_batch):
            raise AssertionError("不應被呼叫")

        self.assertEqual([], embed_texts([], runner=exploding_runner))

    def test_claude_endpoint_rejected(self):
        config = dict(
            CONFIG,
            tasks={"embedding": {"endpoint": "claude-cli", "kind": "embedding"}},
        )
        with patch.dict("os.environ", {}, clear=True):
            with patch.object(model_client, "load_endpoints", return_value=config):
                with self.assertRaises(ModelError):
                    embed_texts(["x"], task="embedding")

    def test_embed_runner_sorts_by_index(self):
        def fake_urlopen(request, timeout=None):
            body = json.loads(request.data.decode("utf-8"))
            self.assertEqual("embed-model", body["model"])
            return _FakeResponse({
                "data": [
                    {"index": 1, "embedding": [2.0]},
                    {"index": 0, "embedding": [1.0]},
                ]
            })

        with patch.object(model_client.urllib.request, "urlopen", fake_urlopen):
            vectors = model_client.openai_embed_runner(
                ["甲", "乙"], base_url="http://localhost:4000/v1", model="embed-model"
            )
        self.assertEqual([[1.0], [2.0]], vectors)


if __name__ == "__main__":
    unittest.main()
