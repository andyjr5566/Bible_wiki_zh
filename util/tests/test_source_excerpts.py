import sys
import tempfile
import unittest
from pathlib import Path

UTIL_DIR = Path(__file__).resolve().parents[1]
if str(UTIL_DIR) not in sys.path:
    sys.path.insert(0, str(UTIL_DIR))

from source_excerpts import (
    chapter_digest,
    keyword_variants,
    parse_manifest,
    slice_for_keywords,
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
            labels = [label for label, _ in sources]
            self.assertEqual(["BH", "KC"], labels)
            self.assertTrue(str(sources[0][1]).endswith("bh_exo_27.txt"))

    def test_missing_manifest_returns_empty(self):
        self.assertEqual([], parse_manifest(Path("nope.md"), Path(".")))


class SliceTests(unittest.TestCase):
    def _sources(self, tmp):
        root = Path(tmp)
        ct = root / "ct.txt"
        ct.write_text(
            "【出二十七1】要用皂莢木做壇。\n\n"
            "〔靈意註解〕皂莢木表徵道成肉身的耶穌。\n\n"
            "【出二十七9】院子的帷子要用細麻。",
            encoding="utf-8",
        )
        kc = root / "kc.txt"
        kc.write_text("The altar was made of acacia wood.\n\n無關段落。", encoding="utf-8")
        return [("CT", ct), ("KC", kc)]

    def test_slices_only_matching_paragraphs(self):
        with tempfile.TemporaryDirectory() as tmp:
            excerpt = slice_for_keywords(self._sources(tmp), ["皂莢木"])
            self.assertIn("皂莢木做壇", excerpt)
            self.assertIn("表徵道成肉身", excerpt)
            self.assertNotIn("院子的帷子", excerpt)
            self.assertIn("【CT】", excerpt)

    def test_respects_char_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            excerpt = slice_for_keywords(self._sources(tmp), ["皂莢木"], max_chars=10)
            self.assertLessEqual(len(excerpt), 10)

    def test_no_keywords_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual("", slice_for_keywords(self._sources(tmp), []))

    def test_chapter_digest_takes_head_of_each_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            digest = chapter_digest(self._sources(tmp), per_source_chars=20)
            self.assertIn("【CT】", digest)
            self.assertIn("【KC】", digest)


class KeywordVariantTests(unittest.TestCase):
    def test_strips_parenthetical(self):
        self.assertEqual(
            {"皂莢木（atzei shittim）", "皂莢木"},
            set(keyword_variants("皂莢木（atzei shittim）")),
        )

    def test_plain_name_has_single_variant(self):
        self.assertEqual(["祭壇"], keyword_variants("祭壇"))


if __name__ == "__main__":
    unittest.main()
