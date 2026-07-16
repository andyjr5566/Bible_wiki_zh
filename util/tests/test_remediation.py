import sys
import unittest
from pathlib import Path

UTIL_DIR = Path(__file__).resolve().parents[1]
if str(UTIL_DIR) not in sys.path:
    sys.path.insert(0, str(UTIL_DIR))

import remediation
import verify_links
import validate_knowledge_base as vkb


class FormatFixHintsTests(unittest.TestCase):
    def test_empty_hints_produce_no_block(self):
        self.assertEqual("", remediation.format_fix_hints([]))
        self.assertEqual("", remediation.format_fix_hints([("問題", [])]))

    def test_block_lists_problem_and_actions(self):
        block = remediation.format_fix_hints([("有東西壞了", ["跑 A", "跑 B"])])
        self.assertIn("如何修復", block)
        self.assertIn("有東西壞了", block)
        self.assertIn("→ 跑 A", block)
        self.assertIn("→ 跑 B", block)


class VerifyFixHintsTests(unittest.TestCase):
    def _report(self, broken=0, invalid=0):
        return {
            "broken_links_count": broken,
            "invalid_scripture_refs_count": invalid,
            "unknown_links_count": 0,
        }

    def test_pending_only_yields_no_hints(self):
        self.assertEqual([], verify_links._verify_fix_hints(self._report()))

    def test_broken_and_invalid_each_trigger_a_hint(self):
        hints = verify_links._verify_fix_hints(self._report(broken=2, invalid=1))
        problems = " ".join(p for p, _ in hints)
        self.assertIn("BROKEN", problems)
        self.assertIn("INVALID", problems)

    def test_only_broken_omits_invalid_hint(self):
        hints = verify_links._verify_fix_hints(self._report(broken=1))
        problems = " ".join(p for p, _ in hints)
        self.assertIn("BROKEN", problems)
        self.assertNotIn("INVALID", problems)


class ValidateFixHintsTests(unittest.TestCase):
    def test_ambiguous_wikilink_detected(self):
        hints = vkb.fix_hints_for(["a.md:3: 歧義裸 WikiLink [[摩西]] 必須改用完整 target"])
        self.assertTrue(any("歧義" in p for p, _ in hints))

    def test_protected_region_detected(self):
        hints = vkb.fix_hints_for(["某條目: 既有正式條目的保護區被修改：定義"])
        self.assertTrue(any("保護區" in p for p, _ in hints))

    def test_structural_error_falls_through_to_generic(self):
        hints = vkb.fix_hints_for(["x.md: frontmatter 缺 type 欄位"])
        self.assertTrue(any("結構" in p for p, _ in hints))

    def test_no_errors_no_hints(self):
        self.assertEqual([], vkb.fix_hints_for([]))


if __name__ == "__main__":
    unittest.main()
