import sys
import tempfile
import unittest
from pathlib import Path

UTIL_DIR = Path(__file__).resolve().parents[1]
if str(UTIL_DIR) not in sys.path:
    sys.path.insert(0, str(UTIL_DIR))

from source_excerpts import (
    SourceError,
    canonical_source_list,
    full_source_text,
    is_large_chapter,
    manifest_source_identities,
    manifest_urls,
    parse_manifest,
    require_sources,
)

# 裸檔名 manifest（申命記 1-6 的損壞格式）：第4欄無 raw_data/ 前綴
BARE_MANIFEST = """\
| 來源 | 類型 | URL | raw_data 檔案 | 狀態 |
|---|---|---|---|---|
| ccbiblestudy CT | 逐節註解 | http://x | ccbiblestudy_CT_deuteronomy_6.txt | OK |
| ccbiblestudy GT | 拾穗 | http://y | ccbiblestudy_GT_deuteronomy_6.txt | OK |
"""

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

    def test_bare_filename_resolves_under_raw_data(self):
        # 裸檔名（無 raw_data/ 前綴）要補到 raw_data/ 下，而非靜默丟棄
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "raw_data").mkdir()
            manifest = root / "source_manifest.md"
            manifest.write_text(BARE_MANIFEST, encoding="utf-8")
            sources = parse_manifest(manifest, root)
            self.assertEqual(2, len(sources))
            for _label, path in sources:
                self.assertEqual("raw_data", path.parent.name)

    def test_canonical_identity_disambiguates_shared_commentary_kind(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "source_manifest.md"
            manifest.write_text("""\
| 來源 | 類型 | URL | raw_data 檔案 | 狀態 |
|---|---|---|---|---|
| KingComments | 研經註解 | https://x/kc | raw_data/kc.txt | OK |
| BibleHub Study | 研經註解 | https://x/bh | raw_data/bh.txt | OK |
""", encoding="utf-8")
            identities = manifest_source_identities(manifest, root)
            self.assertEqual(["KC", "BH"], [item.key for item in identities])
            self.assertEqual([
                ("研經註解（KingComments）", "https://x/kc"),
                ("研經註解（BibleHub Study）", "https://x/bh"),
            ], canonical_source_list(manifest, root))


class RequireSourcesTests(unittest.TestCase):
    def test_raises_when_no_source_file_exists(self):
        # manifest 宣告 OK 來源但檔案都不存在（前綴 bug 的實際後果）→ 必須報錯
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "raw_data").mkdir()
            manifest = root / "source_manifest.md"
            manifest.write_text(BARE_MANIFEST, encoding="utf-8")
            with self.assertRaises(SourceError):
                require_sources(manifest, root)

    def test_passes_when_files_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "raw_data").mkdir()
            for name in ("ccbiblestudy_CT_deuteronomy_6.txt",
                         "ccbiblestudy_GT_deuteronomy_6.txt"):
                (root / "raw_data" / name).write_text("內容", encoding="utf-8")
            manifest = root / "source_manifest.md"
            manifest.write_text(BARE_MANIFEST, encoding="utf-8")
            present = require_sources(manifest, root)
            self.assertEqual(2, len(present))

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

    def test_large_step_uses_independent_budget_and_does_not_shrink_commentary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            commentary = root / "ct.txt"
            structured = root / "step.txt"
            commentary.write_text("C" * 2000 + "COMMENTARY_TAIL", encoding="utf-8")
            structured.write_text("S" * 10000, encoding="utf-8")
            text = full_source_text(
                [
                    ("CT", "逐節註解", "https://x/ct", commentary),
                    ("STEP", "原文資料", "https://x/step", structured),
                ],
                char_budget=3000,
                structured_char_budget=20,
            )
            self.assertIn("COMMENTARY_TAIL", text)
            self.assertIn("正式 raw source 未截斷", text)

    def test_legacy_two_tuple_step_is_still_classified_as_structured(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            commentary = root / "ct.txt"
            step = root / "stepbible_genesis_1.txt"
            commentary.write_text("C" * 1500 + "COMMENTARY_TAIL", encoding="utf-8")
            step.write_text("S" * 10000, encoding="utf-8")
            text = full_source_text(
                [("CT", commentary), ("STEP Bible", step)],
                char_budget=2000,
                structured_char_budget=20,
            )
            self.assertIn("COMMENTARY_TAIL", text)


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
