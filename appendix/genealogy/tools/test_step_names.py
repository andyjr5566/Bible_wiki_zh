from __future__ import annotations

import json
import unittest

try:
    from .align_parallels import NameRef, align_names, chinese_number_to_int
    from .step_names import Word, audit_rows, classify_kind, load_chapter, proper_nouns
except ImportError:
    from align_parallels import NameRef, align_names, chinese_number_to_int
    from step_names import Word, audit_rows, classify_kind, load_chapter, proper_nouns


class InMemoryReading:
    def __init__(self, data: dict) -> None:
        self.data = data

    def read_text(self, encoding: str = "utf-8-sig") -> str:
        return json.dumps(self.data, ensure_ascii=False)


class StepNameTests(unittest.TestCase):
    def test_chronicles_person_and_place_morphology(self) -> None:
        words = load_chapter("代上", 11)[1]
        david = next(word for word in words if word.strong == "H1732")
        israel = next(word for word in words if word.strong == "H3478")
        self.assertEqual(david.kind, "person_m")
        self.assertEqual(israel.kind, "place")

    def test_genesis_and_matthew_have_person_names(self) -> None:
        genesis_names = [
            word
            for verses in load_chapter("創", 5).values()
            for word in verses
            if word.kind in ("person_m", "person_f", "person")
        ]
        self.assertGreater(len(genesis_names), 0)

        matthew_names = proper_nouns("太", 1, 1)
        glosses = " ".join(word.gloss for word in matthew_names)
        self.assertIn("Jesus", glosses)
        self.assertIn("David", glosses)
        self.assertIn("Abraham", glosses)
        self.assertEqual(classify_kind("N-GSM-P — Noun Genitive Singular Masculine Individual"), "person_m")
        self.assertEqual(classify_kind("N-GSF-L — Noun Genitive Singular Feminine Location"), "place")

    def test_chinese_numbers(self) -> None:
        examples = {
            "九百七十三": 973,
            "一千零五十二": 1052,
            "二萬四千": 24000,
            "四萬二千三百六十": 42360,
        }
        for source, expected in examples.items():
            with self.subTest(source=source):
                self.assertEqual(chinese_number_to_int(source), expected)

    def test_sequence_alignment_reports_matches_and_extras(self) -> None:
        def ref(strong: str, verse: int) -> NameRef:
            word = Word(
                index=1,
                original="",
                translit=strong,
                gloss="",
                strong=strong,
                morph="",
                kind="person_m",
            )
            return NameRef("創", 1, verse, word)

        rows = align_names(
            [ref("H3077G", 1), ref("H7586G", 2)],
            [ref("H3077", 3), ref("H0001G", 4)],
        )
        self.assertEqual([row.status for row in rows], ["擴充 Strong 不同", "只在甲", "只在乙"])
        self.assertEqual(rows[0].basic_strong, "H3077")

    def test_audit_accepts_segment_and_legacy_reading_shapes(self) -> None:
        segment_reading = InMemoryReading(
            {
                "segments": [
                    {
                        "id": "s1",
                        "title": "test",
                        "chapters": [
                            {
                                "book": "代上",
                                "n": 11,
                                "verses": [
                                    {"v": 1, "text": "大衛", "t": [{"s": 0, "e": 2, "k": "p"}]}
                                ],
                            }
                        ],
                    }
                ]
            }
        )
        new_rows = audit_rows(segment_reading)  # type: ignore[arg-type]
        self.assertEqual(len(new_rows), 2)
        self.assertEqual(new_rows[-1], "總計\t1\t1\t\t")

        legacy_reading = InMemoryReading(
            {
                "book": "代上",
                "chapters": [
                    {"n": 11, "verses": [{"v": 1, "text": "大衛", "t": []}]}
                ],
            }
        )
        old_rows = audit_rows(legacy_reading)  # type: ignore[arg-type]
        self.assertTrue(old_rows[1].startswith("代上11:1\t1\t0\t"))
        self.assertEqual(old_rows[-1], "總計\t1\t0\t\t")


if __name__ == "__main__":
    unittest.main()
