"""家譜 basis 檢查器測試，使用 repo 內的正式來源檔。"""
from pathlib import Path
import tempfile
import unittest

from appendix.genealogy.check_basis import check_basis, scan_file


ROOT = Path(__file__).resolve().parents[2]


class CheckBasisTests(unittest.TestCase):
    def test_scripture_quote_matches_real_verse(self):
        # 歷代志上第 24 章第 7 行實際含有「第二是耶大雅」。
        self.assertEqual(
            check_basis([{"ref": "代上24:7", "quote": "第二是耶大雅"}], "test", ROOT),
            [],
        )

    def test_scripture_quote_with_one_changed_character_fails(self):
        errors = check_basis(
            [{"ref": "代上24:7", "quote": "第二是耶大亞"}], "test", ROOT
        )
        self.assertTrue(errors)

    def test_missing_verse_fails(self):
        errors = check_basis([{"ref": "代上99:1", "quote": "任何文字"}], "test", ROOT)
        self.assertTrue(errors)
        self.assertIn("經文檔不存在", errors[0])

    def test_cross_chapter_range_includes_next_chapter(self):
        errors = check_basis(
            [{"ref": "代上23:1-24:2", "quote": "亞倫子孫的班次記在下面"}],
            "test",
            ROOT,
        )
        self.assertEqual(errors, [])

    def test_commentary_quote_matches_with_whitespace(self):
        quote = "然而另外 14個家庭的人數就有不同的記載。"
        self.assertEqual(
            check_basis(
                [{"source": "ccbiblestudy_GT_ezra_2.txt", "quote": quote}],
                "test",
                ROOT,
            ),
            [],
        )

    def test_changed_commentary_quote_fails(self):
        errors = check_basis(
            [{
                "source": "ccbiblestudy_GT_ezra_2.txt",
                "quote": "然而另外 14個家庭的人數就有不同的紀載。",
            }],
            "test",
            ROOT,
        )
        self.assertTrue(errors)

    def test_missing_commentary_file_fails(self):
        errors = check_basis(
            [{"source": "ccbiblestudy_GT_missing.txt", "quote": "一段引句"}],
            "test",
            ROOT,
        )
        self.assertTrue(errors)
        self.assertIn("不存在", errors[0])

    def test_commentary_filename_prefix_is_required(self):
        errors = check_basis(
            [{"source": "foo_ezra_2.txt", "quote": "一段引句"}], "test", ROOT
        )
        self.assertTrue(errors)
        self.assertIn("開頭不符合規定", errors[0])

    def test_external_requires_version(self):
        errors = check_basis(
            [{"external": "TIPNR", "entry": "Jehoiada@2Sa.8.18-1Ch"}],
            "test",
            ROOT,
        )
        self.assertTrue(any("version" in error for error in errors))

    def test_wikipedia_external_is_rejected_case_insensitively(self):
        errors = check_basis(
            [{"external": "wIkIpEdIa", "version": "current", "entry": "entry"}],
            "test",
            ROOT,
        )
        self.assertTrue(any("Wikipedia" in error for error in errors))

    def test_scan_file_finds_nested_basis_and_reports_its_path(self):
        content = (
            "links:\n"
            "  - basis:\n"
            "      - external: Wikipedia\n"
            "        version: current\n"
            "        entry: entry\n"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            yaml_path = Path(temp_dir) / "nested.yaml"
            yaml_path.write_text(content, encoding="utf-8")
            count, errors = scan_file(yaml_path, ROOT)

        self.assertEqual(count, 1)
        self.assertTrue(errors)
        self.assertTrue(any("nested.yaml:links[0].basis[0]" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
