import sys
import tempfile
import unittest
from pathlib import Path

import yaml

UTIL_DIR = Path(__file__).resolve().parents[1]
if str(UTIL_DIR) not in sys.path:
    sys.path.insert(0, str(UTIL_DIR))

from yaml_io import write_yaml_atomic


class _Unserializable:
    """yaml.safe_dump 無法表示的物件（觸發 RepresenterError）。"""


class WriteYamlAtomicTests(unittest.TestCase):
    def test_writes_expected_yaml_and_leaves_no_temp(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sub" / "payload.yaml"
            write_yaml_atomic(path, {"b": 1, "a": [2, 3]})
            self.assertEqual({"b": 1, "a": [2, 3]}, yaml.safe_load(path.read_text("utf-8")))
            # 不留 <name>.<pid>.tmp
            self.assertEqual(["payload.yaml"], [p.name for p in path.parent.iterdir()])

    def test_dump_failure_leaves_original_intact(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "payload.yaml"
            path.write_text("original: kept\n", encoding="utf-8")
            before = path.read_bytes()
            with self.assertRaises(yaml.YAMLError):
                write_yaml_atomic(path, {"bad": _Unserializable()})
            self.assertEqual(before, path.read_bytes())
            # 中途失敗不得留下暫存檔
            self.assertEqual(["payload.yaml"], [p.name for p in path.parent.iterdir()])

    def test_dump_failure_on_absent_target_creates_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "new.yaml"
            with self.assertRaises(yaml.YAMLError):
                write_yaml_atomic(path, _Unserializable())
            self.assertFalse(path.exists())
            self.assertEqual([], list(path.parent.iterdir()))

    def test_dump_kwargs_are_forwarded(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "styled.yaml"
            write_yaml_atomic(path, {"k": "v"}, default_style='"')
            self.assertIn('"k"', path.read_text("utf-8"))


if __name__ == "__main__":
    unittest.main()
