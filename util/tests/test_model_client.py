import json
import sys
import unittest
from pathlib import Path

UTIL_DIR = Path(__file__).resolve().parents[1]
if str(UTIL_DIR) not in sys.path:
    sys.path.insert(0, str(UTIL_DIR))

from model_client import (
    ModelValidationError,
    _result_text,
    call_model,
    extract_payload,
)


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


if __name__ == "__main__":
    unittest.main()
