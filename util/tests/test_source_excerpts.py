import sys
import tempfile
import unittest
from pathlib import Path

UTIL_DIR = Path(__file__).resolve().parents[1]
if str(UTIL_DIR) not in sys.path:
    sys.path.insert(0, str(UTIL_DIR))

from source_excerpts import (
    full_source_text,
    is_large_chapter,
    manifest_urls,
    parse_manifest,
)

MANIFEST = """\
# Source Manifest — 出埃及記 第27章

| 來源 | 類型 | URL | raw_data 檔案 | 狀態 |
|------|-----|-----|--------------|------|
| BibleHub | BH | http://x | raw_data/bh_exo_27.txt | ✅ OK (100 chars) |
| KingComments | KC | http://y | raw_data/kc_exo_27.txt | ✅ OK (50 chars) |
| ccbiblestudy | CT | http://z | raw_data/ct_exo_27.txt | ❌ FAILED |
"""


class ManifestTests(unittest.TestCase):
    def test_parses_only_ok_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "raw_data").mkdir()
            manifest = root / "source_manifest.md"
            manifest.write_text(MANIFEST, encoding="utf-8")
            sources = parse_manifest(manifest, root)
            self.assertEqual(["BibleHub", "KingComments"], [label for label, _ in sources])
            self.assertTrue(str(sources[0][1]).endswith("bh_exo_27.txt"))

    def test_missing_manifest_returns_empty(self):
        self.assertEqual([], parse_manifest(Path("nope.md"), Path(".")))

    def test_manifest_urls_only_ok_http(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "source_manifest.md"
            manifest.write_text(MANIFEST, encoding="utf-8")
            self.assertEqual(
                [("BibleHub", "http://x"), ("KingComments", "http://y")],
                manifest_urls(manifest),  # FAILED 的 ct 不入列
            )

    def test_manifest_urls_missing_manifest_returns_empty(self):
        self.assertEqual([], manifest_urls(Path("nope.md")))


class FullSourceTests(unittest.TestCase):
    def _sources(self, tmp):
        root = Path(tmp)
        ct = root / "ct.txt"
        ct.write_text("CT 全文內容第一段。\n\n第二段。", encoding="utf-8")
        kc = root / "kc.txt"
        kc.write_text("KC full commentary text.", encoding="utf-8")
        return [("CT", ct), ("KC", kc)]

    def test_feeds_full_text_labeled(self):
        with tempfile.TemporaryDirectory() as tmp:
            text = full_source_text(self._sources(tmp))
            self.assertIn("【CT】", text)
            self.assertIn("【KC】", text)
            self.assertIn("CT 全文內容第一段。", text)
            self.assertIn("第二段。", text)  # 不切片，整段保留
            self.assertIn("KC full commentary text.", text)

    def test_budget_truncates_proportionally(self):
        with tempfile.TemporaryDirectory() as tmp:
            text = full_source_text(self._sources(tmp), char_budget=20)
            self.assertIn("截斷", text)

    def test_missing_files_are_skipped(self):
        self.assertEqual("", full_source_text([("X", Path("nope.txt"))]))


class LargeChapterTests(unittest.TestCase):
    def test_many_verses_is_large(self):
        self.assertTrue(is_large_chapter([], ["v"] * 61))

    def test_small_chapter_is_not_large(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "s.txt"
            src.write_text("短", encoding="utf-8")
            self.assertFalse(is_large_chapter([("CT", src)], ["v"] * 10))


if __name__ == "__main__":
    unittest.main()
