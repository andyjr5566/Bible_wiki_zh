import sys
import tempfile
import unittest
from pathlib import Path


UTIL_DIR = Path(__file__).resolve().parents[1]
if str(UTIL_DIR) not in sys.path:
    sys.path.insert(0, str(UTIL_DIR))

import extract_stepbible
import step_context


def make_word(
    reference,
    position,
    original,
    transliteration,
    strong,
    morphology,
    *,
    gloss="gloss",
    lexicon="definition",
):
    return extract_stepbible.WordEntry(
        reference=reference,
        position=position,
        word=original,
        transliteration=transliteration,
        gloss=gloss,
        strongs_raw=strong,
        strongs=[strong],
        main_strong=strong,
        morphology_raw=morphology,
        morphology=morphology,
        lexicon_short=lexicon,
    )


def write_step(path, reference, verses):
    ref = extract_stepbible.parse_reference(reference)
    path.write_text(
        extract_stepbible.render_markdown(ref, verses, include_full_definitions=False),
        encoding="utf-8",
    )
    return path


class RenderedStepParserTests(unittest.TestCase):
    def test_renderer_parser_round_trip_preserves_escaped_pipe_and_extended_strong(self):
        ref = extract_stepbible.parse_reference("Genesis 1:1")
        verses = {1: [make_word(
            "Gen.1.1", 1, "אֱלֹהִים", "ʾĕlōhîm", "H430G", "N-mp",
            gloss="God | deity", lexicon="God | gods",
        )]}
        rendered = extract_stepbible.render_markdown(ref, verses, False)
        parsed = extract_stepbible.parse_rendered_markdown_text(rendered)
        word = parsed.verses[1][0]
        self.assertEqual("H430G", word.main_strong)
        self.assertEqual("God | deity", word.gloss)
        self.assertEqual("God | gods", word.lexicon_short)

    def test_noncanonical_table_is_rejected(self):
        text = """# STEP Bible — Genesis 1:1

## Genesis 1:1
| # | 原文 | Strong |
|---:|---|---|
| 1 | ברא | H1254A |
"""
        with self.assertRaises(extract_stepbible.StepFormatError):
            extract_stepbible.parse_rendered_markdown_text(text)

    def test_formal_source_keeps_morphology_code_and_expansion(self):
        ref = extract_stepbible.parse_reference("John 1:1")
        entry = make_word("Jhn.1.1", 1, "λόγος", "logos", "G3056", "N-NSM")
        entry.morphology = "Noun Nominative Singular Masculine"
        parsed = extract_stepbible.parse_rendered_markdown_text(
            extract_stepbible.render_markdown(ref, {1: [entry]}, False)
        )
        word = parsed.verses[1][0]
        self.assertEqual("N-NSM", word.morphology_raw)
        self.assertEqual("Noun Nominative Singular Masculine", word.morphology)


class StepValidationAndProjectionTests(unittest.TestCase):
    def test_validation_receipt_and_exact_strong_lexicon_dedup(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "stepbible_genesis_1.txt"
            write_step(path, "Genesis 1", {
                1: [
                    make_word("Gen.1.1", 1, "אֱלֹהִים", "ʾĕlōhîm", "H430G", "N-mp"),
                    make_word(
                        "Gen.1.1", 2, "אֱלֹהִים", "ʾĕlōhîm", "H430G", "N-mp-c",
                    ),
                ],
                2: [make_word("Gen.1.2", 1, "בָּרָא", "bārāʾ", "H1254A", "V-Qal-3ms")],
            })
            receipt = step_context.validate_step_source(
                path, expected_book="創世記", expected_chapter=1, scripture_verse_count=2
            )
            self.assertEqual("PASS", receipt["status"])
            self.assertEqual(3, receipt["words"])
            self.assertEqual(64, len(receipt["sha256"]))

            projection = step_context.project_step_source(path, verses={1})
            self.assertEqual(2, projection.occurrence_count)
            self.assertEqual(1, projection.lexicon_count)
            self.assertEqual(1, projection.text.count("- H430G |"))
            self.assertIn("N-mp", projection.text)
            self.assertIn("N-mp-c", projection.text)
            self.assertNotIn("H1254A", projection.text)

    def test_validation_rejects_missing_morphology(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.txt"
            write_step(path, "Genesis 1:1", {
                1: [make_word("Gen.1.1", 1, "בָּרָא", "bārāʾ", "H1254A", "")]
            })
            with self.assertRaisesRegex(step_context.StepValidationError, "Morphology"):
                step_context.validate_step_source(path, expected_book="Genesis", expected_chapter=1)

    def test_nt_range_keeps_greek_extended_strong_morphology_and_lexicon(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "stepbible_john_1_1-5.txt"
            verses = {
                number: [make_word(
                    f"Jhn.1.{number}", 1, "λόγος", "logos", "G3056A",
                    f"N-NSM-v{number}", lexicon="word; message",
                )]
                for number in range(1, 6)
            }
            write_step(path, "John 1:1-5", verses)
            receipt = step_context.validate_step_source(
                path, expected_book="約翰福音", expected_chapter=1, scripture_verse_count=51
            )
            self.assertEqual((1, 5), (receipt["verse_start"], receipt["verse_end"]))
            projection = step_context.project_step_source(path)
            self.assertEqual(5, projection.occurrence_count)
            self.assertEqual(1, projection.lexicon_count)
            self.assertIn("G3056A", projection.text)
            self.assertIn("N-NSM-v5", projection.text)


class EvidenceSelectionTests(unittest.TestCase):
    def test_evidence_range_and_surfaces_are_unioned_without_cross_reference(self):
        batch = [{
            "name": "候選",
            "evidence": "1、3-4節；另參詩33:6",
            "surfaces": [{"phrase": "詞", "verses": [2]}],
        }]
        result = step_context.select_candidate_verses(batch, range(1, 7))
        self.assertEqual((1, 2, 3, 4), result.verses)
        self.assertEqual("targeted", result.mode)

    def test_parse_range(self):
        self.assertEqual({1, 2, 3, 5}, step_context.parse_verse_spec("1-3、5"))

    def test_unparseable_evidence_fails_open_to_full_chapter(self):
        result = step_context.select_candidate_verses(
            [{"name": "候選", "evidence": "這段只描述語義，沒有節號"}],
            range(1, 6),
        )
        self.assertEqual((1, 2, 3, 4, 5), result.verses)
        self.assertEqual("chapter-fallback", result.mode)
        self.assertTrue(any("fail-open" in warning for warning in result.warnings))


if __name__ == "__main__":
    unittest.main()
