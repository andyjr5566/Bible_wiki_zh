# -*- coding: utf-8 -*-
"""STEP 候選的功能詞 stoplist：M6 選取與 find_step_candidates 預設排除，M3 規則不動。"""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

UTIL_DIR = Path(__file__).resolve().parents[1]
if str(UTIL_DIR) not in sys.path:
    sys.path.insert(0, str(UTIL_DIR))
sys.path.insert(0, str(UTIL_DIR.parent))

import extract_stepbible  # noqa: E402
import step_context  # noqa: E402
from util.tests.test_step_context import make_word, write_step  # noqa: E402


HEBREW = {
    "kol": "כֹּל", "asher": "אֲשֶׁר", "ben": "בֵּן", "nachalah": "נַחֲלָה",
    "yarash": "יָרַשׁ", "et": "אֵת", "prefix": "לְ",
}


def _document():
    """kol(H3605)×4、asher(H834)×3、ben(H1121)×3 比 nachalah(H5159)×2、yarash(H3423)×2 更常見。"""
    ref = extract_stepbible.parse_reference("Joshua 13")
    rows = []
    position = 0

    def add(verse, translit, strong, gloss):
        nonlocal position
        position += 1
        rows.append((verse, make_word(f"Jos.13.{verse}", position, HEBREW[translit], translit, strong,
                                      "Hx", gloss=gloss, lexicon=gloss)))

    for verse in (1, 2, 3, 4):
        add(verse, "kol", "H3605", "all")
    for verse in (1, 2, 3):
        add(verse, "asher", "H834", "which")
        add(verse, "ben", "H1121", "son")
    for verse in (2, 3):
        add(verse, "nachalah", "H5159", "inheritance")
        add(verse, "yarash", "H3423H", "possess")
    add(4, "et", "H853", "[Obj.]")
    add(4, "prefix", "H9005", "to/for")
    verses = {}
    for verse, word in rows:
        verses.setdefault(verse, []).append(word)
    return extract_stepbible.StepDocument(reference=ref, verses=verses)


class StoplistTests(unittest.TestCase):
    def test_known_function_words_are_listed_with_any_extended_suffix(self):
        for strong in ("H3605", "H834", "H1121", "H5704", "H853", "H1961", "H3588", "H3808",
                       "H413", "H5921", "H4480", "G3588", "G2532", "H3605A", "h0834"):
            self.assertTrue(step_context.is_function_word_strong(strong), strong)

    def test_h9xxx_prefix_codes_are_function_words(self):
        for strong in ("H9001", "H9005", "H9009", "H9023"):
            self.assertTrue(step_context.is_function_word_strong(strong), strong)

    def test_content_words_are_not_listed(self):
        for strong in ("H3423", "H5159", "H1366", "H776", "H5414", "H5892", "H4872", "G3056", "H430G", ""):
            self.assertFalse(step_context.is_function_word_strong(strong), strong)


class DiscoverCandidatesTests(unittest.TestCase):
    def test_default_keeps_function_words_so_m3_fallback_is_unchanged(self):
        bases = [c.base_strong for c in step_context.discover_candidates(_document(), nearby_window=0)]
        self.assertIn("H3605", bases)
        self.assertEqual("H3605", bases[0])          # 舊行為：頻率最高的虛詞排第一

    def test_exclude_function_words_leaves_content_words_first(self):
        candidates = step_context.discover_candidates(
            _document(), nearby_window=0, exclude_function_words=True)
        bases = [c.base_strong for c in candidates]
        self.assertEqual(["H3423", "H5159"], sorted(bases))
        for stop in ("H3605", "H834", "H1121", "H853"):
            self.assertNotIn(stop, bases)

    def test_exclusion_happens_before_max_results_truncation(self):
        candidates = step_context.discover_candidates(
            _document(), nearby_window=0, exclude_function_words=True, max_results=2)
        self.assertEqual(2, len(candidates))

    def test_plan_target_function_word_is_kept_and_ranked_first(self):
        candidates = step_context.discover_candidates(
            _document(), nearby_window=0, exclude_function_words=True, plan_strongs=["H834", "H3423H"])
        bases = [c.base_strong for c in candidates]
        self.assertIn("H834", bases)                  # 條目明確點名的虛詞例外保留
        self.assertEqual({"H834", "H3423"}, set(bases[:2]))   # plan_target 先排
        self.assertNotIn("H3605", bases)

    def test_select_step_evidence_defaults_to_excluding_function_words(self):
        evidence = step_context.select_step_evidence(_document(), nearby_window=0, char_budget=50000)
        self.assertIn("H5159", evidence.text)
        self.assertIn("H3423", evidence.text)
        for stop in ("H3605", "H834", "H1121", "H853"):
            self.assertNotIn(f"### {stop} ", evidence.text)

    def test_select_step_evidence_filters_unfiltered_candidates_passed_in(self):
        raw = step_context.discover_candidates(_document(), nearby_window=0)
        evidence = step_context.select_step_evidence(_document(), candidates=raw, char_budget=50000)
        self.assertNotIn("### H3605 ", evidence.text)
        everything = step_context.select_step_evidence(
            _document(), candidates=raw, char_budget=50000, exclude_function_words=False)
        self.assertIn("### H3605 ", everything.text)

    def test_budget_is_spent_on_content_words(self):
        evidence = step_context.select_step_evidence(_document(), nearby_window=0, char_budget=900)
        self.assertGreaterEqual(evidence.selected_count, 1)
        self.assertNotIn("### H3605 ", evidence.text)


class M3RuleUnchangedTests(unittest.TestCase):
    def test_m3_targeted_candidate_may_still_match_a_stoplisted_strong(self):
        """M3 依候選定位（明點 Strong），不看頻率，也不套 stoplist。"""
        evidence = step_context.select_m3_candidate_evidence(
            _document(),
            [{"name": "全部（kol）", "suggested_type": "原文", "evidence": "第1節；H3605 kol", "surfaces": []}],
            char_budget=50000,
        )
        self.assertEqual("targeted", evidence.mode)
        self.assertIn("H3605", evidence.text)


class FindStepCandidatesToolTests(unittest.TestCase):
    def _write(self, root):
        raw = root / "raw_data"
        raw.mkdir(parents=True, exist_ok=True)
        doc = _document()
        write_step(raw / "stepbible_joshua_13.txt", "Joshua 13", doc.verses)
        scripture = root / "raw_scripture" / "約書亞記"
        scripture.mkdir(parents=True, exist_ok=True)
        (scripture / "第13章.txt").write_text("\n".join(f"{i}. 經文" for i in range(1, 5)) + "\n",
                                              encoding="utf-8")

    def test_default_excludes_and_include_function_words_restores(self):
        from util.mcp import server
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write(root)
            with patch.object(server, "ROOT_DIR", root):
                default = server.find_step_candidates("約書亞記", 13, nearby_window=0)
                full = server.find_step_candidates("約書亞記", 13, nearby_window=0,
                                                   include_function_words=True)
        self.assertTrue(default["success"], default)
        self.assertTrue(full["success"], full)
        default_bases = {c["exact_strongs"][0][:5] for c in default["candidates"]}
        full_bases = {c["exact_strongs"][0][:5] for c in full["candidates"]}
        self.assertNotIn("H3605", default_bases)
        self.assertIn("H3423", default_bases)
        self.assertTrue(default["function_words_excluded"])
        self.assertIn("H3605", full_bases)
        self.assertFalse(full["function_words_excluded"])


if __name__ == "__main__":
    unittest.main()
