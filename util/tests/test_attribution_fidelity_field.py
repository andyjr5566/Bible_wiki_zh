# -*- coding: utf-8 -*-
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from util import check_chapter_files as ccf  # noqa: E402
from util import check_quote_fidelity as cqf  # noqa: E402


class AttributionFidelityFieldTests(unittest.TestCase):
    def test_completed_deuteronomy_chapters_remain_clean_under_strict_scanner(self):
        """拿已完成、曾做過完整勘誤的申32–34作既有文章回歸樣本。"""
        results = []
        for chapter in (32, 33, 34):
            total, misses, _names = cqf.check_quotes(
                "申命記", chapter, root=ROOT, min_chars=2
            )
            results.append((chapter, total, len(misses)))
            print(f"FIELD 申命記{chapter}: quotes={total}, misses={len(misses)}")
            self.assertEqual([], misses, f"申命記{chapter}既有完成稿不應被新機制改壞")
        self.assertTrue(all(total > 0 for _chapter, total, _misses in results))

    def test_string_miss_is_advisory_not_a_content_verdict(self):
        """在真實完成章節上注入一筆字串 miss，確認 final file gate 只警告、不判內容錯。"""
        with mock.patch.object(
            ccf.check_quote_fidelity,
            "check_quotes",
            return_value=(7, [("chapter_content.yaml", "這是一段刻意注入的字串未命中")], ["fixture"]),
        ):
            checks = ccf.build_checks("申命記", 32, root=ROOT)

        quote_checks = [item for item in checks if "引句字串疑點掃描" in item.label]
        self.assertEqual(1, len(quote_checks))
        result = quote_checks[0]
        self.assertTrue(result.ok)
        self.assertIn("review", result.warning)
        self.assertIn("不可僅因字串未命中", result.warning)
        print(f"FIELD advisory gate: ok={result.ok}, warning={result.warning}")


if __name__ == "__main__":
    unittest.main()
