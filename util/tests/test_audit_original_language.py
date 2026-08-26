# -*- coding: utf-8 -*-
"""audit_original_language 的 maqqef 規則。"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import audit_original_language as audit


def _occurrence(chapter, position, hebrew):
    return audit.Occurrence(
        book_code="Gen", chapter=chapter, verse=1, position=position,
        original=hebrew, hebrew=audit.normalize_hebrew(hebrew),
        transliteration="", transliteration_strict="", transliteration_loose="",
        strong="", base_strong="", morphology_raw="", morphology="", lexicon="",
    )


class MaqqefResolutionTests(unittest.TestCase):
    """STEP 把 maqqef 兩邊分列，連寫形（印刷上正確）永遠配不上單一列。

    報它等於在報 STEP 的標記方式。全庫實測 208 處連寫、兩邊全部有出處。
    """

    def setUp(self):
        self.index = audit.EvidenceIndex([
            _occurrence(1, 1, "אֶת"),
            _occurrence(1, 2, "הָאָרֶץ"),
        ])

    def test_joined_pair_resolves_half_by_half(self):
        joined = "אֶת־הָאָרֶץ"
        self.assertEqual([], self.index.hebrew_matches(audit.normalize_hebrew(joined), [1]))
        resolved = self.index.hebrew_matches(
            audit.normalize_hebrew(joined), [1], raw_token=joined
        )
        self.assertEqual(2, len(resolved))

    def test_joined_pair_with_an_unsourced_half_stays_unmatched(self):
        joined = "אֶת־אבגד"
        self.assertEqual(
            [], self.index.hebrew_matches(audit.normalize_hebrew(joined), [1], raw_token=joined)
        )

    def test_a_single_word_is_unaffected(self):
        self.assertEqual(
            1, len(self.index.hebrew_matches(audit.normalize_hebrew("אֶת"), [1], raw_token="אֶת"))
        )

    def test_a_plain_unsourced_word_is_still_unmatched(self):
        self.assertEqual(
            [], self.index.hebrew_matches(audit.normalize_hebrew("אבגד"), [1], raw_token="אבגד")
        )


if __name__ == "__main__":
    unittest.main()
