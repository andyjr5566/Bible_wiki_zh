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
            projection = step_context.project_step_source(path, allow_full_chapter=True)
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

    def test_unparseable_evidence_fails_small_without_full_chapter(self):
        result = step_context.select_candidate_verses(
            [{"name": "候選", "suggested_type": "原文", "evidence": "這段只描述語義，沒有節號"}],
            range(1, 6),
        )
        self.assertEqual((), result.verses)
        self.assertEqual("unresolved", result.mode)
        self.assertTrue(any("未自動注入整章 STEP" in warning or "精確查詢" in warning for warning in result.warnings))

    def test_non_original_candidates_are_skipped(self):
        batch = [
            {"name": "摩西", "suggested_type": "人物", "evidence": "1-3節"},
            {"name": "敬畏神", "suggested_type": "神學", "evidence": "4-5節"},
        ]
        result = step_context.select_candidate_verses(batch, range(1, 10))
        self.assertEqual((), result.verses)
        self.assertEqual("non-original-skipped", result.mode)
        self.assertTrue(any("非原文類條目" in warning for warning in result.warnings))

    def test_full_chapter_evidence_fails_small(self):
        batch = [
            {"name": "創造", "suggested_type": "原文", "evidence": "全章；創世記第一章整體"},
        ]
        result = step_context.select_candidate_verses(batch, range(1, 32))
        self.assertEqual((), result.verses)
        self.assertEqual("full-chapter-evidence", result.mode)
        self.assertTrue(any("全章" in warning for warning in result.warnings))

    def test_mixed_batch_filters_non_original_verses(self):
        batch = [
            {"name": "穹蒼（raqia）", "suggested_type": "原文", "evidence": "6-8節"},
            {"name": "摩西", "suggested_type": "人物", "evidence": "1-5節"},
        ]
        result = step_context.select_candidate_verses(batch, range(1, 10))
        self.assertEqual((6, 7, 8), result.verses)
        self.assertEqual("targeted", result.mode)


class CandidateDiscoveryTests(unittest.TestCase):
    def _sample_document(self):
        ref = extract_stepbible.parse_reference("Genesis 1")
        verses = {
            1: [
                make_word("Gen.1.1", 1, "בְּרֵאשִׁית", "bərēʾšît", "H7225", "N-fs", gloss="in the beginning", lexicon="beginning"),
                make_word("Gen.1.1", 2, "בָּרָא", "bārāʾ", "H1254A", "V-Qal-3ms", gloss="created", lexicon="create"),
                make_word("Gen.1.1", 3, "אֱלֹהִים", "ʾĕlōhîm", "H430G", "N-mp", gloss="God", lexicon="God"),
                make_word("Gen.1.1", 4, "־", "-", "H9003", "Punct", gloss="punct", lexicon=""),
            ],
            2: [
                make_word("Gen.1.2", 1, "וְהָאָרֶץ", "wəhāʾāreṣ", "H776", "N-fs", gloss="and the earth", lexicon="earth"),
                make_word("Gen.1.2", 2, "אֱלֹהִים", "ʾĕlōhîm", "H430G", "N-mp", gloss="God", lexicon="God"),
            ],
            3: [
                make_word("Gen.1.3", 1, "וַיֹּאמֶר", "wayyōʾmer", "H559", "V-Qal-3ms", gloss="and said", lexicon="say"),
                make_word("Gen.1.3", 2, "אֱלֹהִים", "ʾĕlōhîm", "H430G", "N-mp", gloss="God", lexicon="God"),
                make_word("Gen.1.3", 3, "בָּרָא", "bārāʾ", "H1254B", "V-Qal-3ms", gloss="created", lexicon="create"),
            ],
        }
        return extract_stepbible.StepDocument(reference=ref, verses=verses)

    def test_discover_candidates_excludes_step_control_strong(self):
        doc = self._sample_document()
        candidates = step_context.discover_candidates(doc, include_low=True)
        base_strongs = [c.base_strong for c in candidates]
        self.assertNotIn("H9003", base_strongs)

    def test_discover_candidates_priority_and_extended_variants(self):
        doc = self._sample_document()
        # H430 appears 3 times -> HIGH
        # H1254 appears 2 times -> MEDIUM
        # H7225 appears 1 time -> LOW
        candidates = step_context.discover_candidates(doc, include_low=True)
        cand_map = {c.base_strong: c for c in candidates}
        self.assertIn("H430", cand_map)
        self.assertEqual("HIGH", cand_map["H430"].priority)
        self.assertEqual(3, len(cand_map["H430"].occurrences))

        self.assertIn("H1254", cand_map)
        self.assertEqual(set(cand_map["H1254"].exact_strongs), {"H1254A", "H1254B"})

        self.assertIn("H7225", cand_map)
        self.assertEqual("LOW", cand_map["H7225"].priority)

    def test_candidate_lexical_fields_separated(self):
        doc = self._sample_document()
        candidates = step_context.discover_candidates(doc, include_low=True)
        c = next(cand for cand in candidates if cand.base_strong == "H1254")
        self.assertEqual("בָּרָא", c.surface)
        self.assertEqual("created", c.context_gloss)
        self.assertEqual("בָּרָא", c.lexicon_word)
        self.assertEqual("bārāʾ", c.lexicon_transliteration)
        self.assertEqual("create", c.lexicon_short)
        self.assertEqual(2, len(c.variants))
        self.assertEqual("H1254A", c.variants[0]["exact_strong"])
        self.assertEqual("H1254B", c.variants[1]["exact_strong"])

    def test_extended_variants_alone_does_not_promote_single_occurrence_to_medium(self):
        ref = extract_stepbible.parse_reference("Genesis 1")
        # Word appears once, but with 2 strongs attached in raw row
        verses = {
            1: [
                make_word("Gen.1.1", 1, "בְּרֵאשִׁית", "bərēʾšît", "H7225A", "N-fs", gloss="in the beginning", lexicon="beginning"),
            ]
        }
        doc = extract_stepbible.StepDocument(reference=ref, verses=verses)
        # Without nearby recurrence, count=1 remains LOW
        candidates = step_context.discover_candidates(doc, nearby_window=0, include_low=True)
        self.assertEqual(1, len(candidates))
        self.assertEqual("LOW", candidates[0].priority)

    def test_nearby_recurrence_promotes_single_occurrence_to_medium(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw_dir = root / "raw_data"
            raw_dir.mkdir()
            # Genesis 2 has H7225
            verses_ch2 = {
                1: [make_word("Gen.2.1", 1, "בְּרֵאשִׁית", "bərēʾšît", "H7225", "N-fs", gloss="beginning", lexicon="beginning")]
            }
            write_step(raw_dir / "stepbible_genesis_2.txt", "Genesis 2", verses_ch2)

            # Genesis 1 has H7225 only once
            verses_ch1 = {
                1: [make_word("Gen.1.1", 1, "בְּרֵאשִׁית", "bərēʾšît", "H7225", "N-fs", gloss="beginning", lexicon="beginning")]
            }
            doc_ch1 = extract_stepbible.StepDocument(reference=extract_stepbible.parse_reference("Genesis 1"), verses=verses_ch1)

            candidates = step_context.discover_candidates(
                doc_ch1, root=root, nearby_window=5, include_medium=True, include_low=False
            )
            # Promoted to MEDIUM by nearby chapter recurrence!
            self.assertEqual(1, len(candidates))
            self.assertEqual("H7225", candidates[0].base_strong)
            self.assertEqual("MEDIUM", candidates[0].priority)
            self.assertTrue(any("nearby_chapter_recurrence" in s for s in candidates[0].signals))

    def test_discover_candidates_respects_max_results(self):
        doc = self._sample_document()
        candidates = step_context.discover_candidates(doc, max_results=2)
        self.assertLessEqual(len(candidates), 2)

    def test_select_step_evidence_respects_char_budget(self):
        doc = self._sample_document()
        evidence = step_context.select_step_evidence(doc, char_budget=600)
        self.assertLessEqual(len(evidence.text), 600)
        self.assertIn("H430", evidence.text)
        self.assertNotIn("H7225", evidence.text)
        self.assertTrue(evidence.truncated)
        self.assertEqual(1, evidence.selected_count)
        # Without LOW, candidate_count is the count of HIGH + MEDIUM candidates
        high_medium = step_context.discover_candidates(doc, include_medium=True, include_low=False)
        self.assertEqual(len(high_medium), evidence.candidate_count)

    def test_select_step_evidence_never_pads_with_low_candidates(self):
        doc = self._sample_document()
        # Even with an enormous char budget, LOW candidates like H7225 (single occurrence) are never added
        evidence = step_context.select_step_evidence(doc, nearby_window=0, char_budget=50000)
        self.assertNotIn("H7225", evidence.text)
        self.assertIn("H430", evidence.text)


class NearbyOccurrencesTests(unittest.TestCase):
    def test_find_nearby_occurrences_bounded_window(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "raw_data").mkdir()
            # Write Exodus 19, 20, 21
            for ch in (19, 20, 21):
                path = root / "raw_data" / f"stepbible_exodus_{ch}.txt"
                verses = {
                    1: [make_word(f"Exo.{ch}.1", 1, "נָסָה", "nāsāh", "H5254G", "V-Piel", gloss="to test", lexicon="test")]
                }
                write_step(path, f"Exodus {ch}", verses)

            results = step_context.find_nearby_occurrences(
                root, "出埃及記", 20, base_strong="H5254", window=2, max_results=10
            )
            self.assertTrue(results["success"])
            self.assertEqual(3, len(results["occurrences"]))
            refs = [occ["reference"] for occ in results["occurrences"]]
            self.assertEqual(["Exo.19.1", "Exo.20.1", "Exo.21.1"], refs)

    def test_exact_strong_vs_base_strong_matching(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "raw_data").mkdir()
            path = root / "raw_data" / "stepbible_exodus_20.txt"
            verses = {
                1: [
                    make_word("Exo.20.1", 1, "נָסָה", "nāsāh", "H5254A", "V-Qal", gloss="to test", lexicon="test"),
                    make_word("Exo.20.1", 2, "נָסָה", "nāsāh", "H5254G", "V-Piel", gloss="to test", lexicon="test"),
                ]
            }
            write_step(path, "Exodus 20", verses)

            # Exact strong matches only H5254G
            res_exact = step_context.find_nearby_occurrences(
                root, "出埃及記", 20, strong="H5254G", window=1
            )
            self.assertEqual(1, len(res_exact["occurrences"]))
            self.assertEqual("H5254G", res_exact["occurrences"][0]["strong"])

            # Base strong matches both H5254A and H5254G
            res_base = step_context.find_nearby_occurrences(
                root, "出埃及記", 20, base_strong="H5254", window=1
            )
            self.assertEqual(2, len(res_base["occurrences"]))

            # Specifying both raises error
            res_both = step_context.find_nearby_occurrences(
                root, "出埃及記", 20, strong="H5254G", base_strong="H5254", window=1
            )
            self.assertFalse(res_both["success"])
            self.assertIn("不可同時指定", res_both["error"])

    def test_find_nearby_occurrences_records_missing_and_invalid_chapters(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw_dir = root / "raw_data"
            raw_dir.mkdir()
            # Chapter 20 exists and is valid
            verses = {1: [make_word("Exo.20.1", 1, "word", "w", "H1234", "N", gloss="g", lexicon="l")]}
            write_step(raw_dir / "stepbible_exodus_20.txt", "Exodus 20", verses)
            # Chapter 21 is corrupted/invalid
            (raw_dir / "stepbible_exodus_21.txt").write_text("CORRUPTED INVALID DATA", encoding="utf-8")
            # Chapter 19 is missing

            result = step_context.find_nearby_occurrences(
                root, "出埃及記", 20, base_strong="H1234", window=1
            )
            self.assertTrue(result["success"])
            self.assertIn(19, result["missing_chapters"])
            self.assertTrue(any(inv["chapter"] == 21 for inv in result["invalid_chapters"]))


class QueryStepContextTests(unittest.TestCase):
    def test_query_requires_target_unless_allowed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "stepbible_genesis_1.txt"
            verses = {1: [make_word("Gen.1.1", 1, "בָּרָא", "bārāʾ", "H1254A", "V-Qal", gloss="created", lexicon="create")]}
            write_step(path, "Genesis 1", verses)

            with self.assertRaises(ValueError) as ctx:
                step_context.project_step_source(path)
            self.assertIn("至少必須提供", str(ctx.exception))

            # With allow_full_chapter=True, succeeds
            proj = step_context.project_step_source(path, allow_full_chapter=True)
            self.assertEqual(1, proj.occurrence_count)

    def test_max_results_and_max_characters_bounds(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "stepbible_genesis_1.txt"
            verses = {
                1: [
                    make_word("Gen.1.1", 1, "word1", "w1", "H1111", "N", gloss="g1", lexicon="l1"),
                    make_word("Gen.1.1", 2, "word2", "w2", "H2222", "N", gloss="g2", lexicon="l2"),
                    make_word("Gen.1.1", 3, "word3", "w3", "H3333", "N", gloss="g3", lexicon="l3"),
                ]
            }
            write_step(path, "Genesis 1", verses)

            proj = step_context.project_step_source(path, verses=[1], max_results=2)
            self.assertEqual(2, proj.occurrence_count)
            self.assertTrue(proj.truncated)


class SelectM3CandidateEvidenceTests(unittest.TestCase):
    def setUp(self):
        ref = extract_stepbible.parse_reference("Genesis 1:1-8")
        self.doc = extract_stepbible.StepDocument(
            reference=ref,
            verses={
                1: [
                    make_word("Gen.1.1", 1, "בְּרֵאשִׁית", "bərēʾšît", "H7225", "N-fs", gloss="in the beginning", lexicon="beginning"),
                    make_word("Gen.1.1", 2, "בָּרָא", "bārāʾ", "H1254A", "V-Qal", gloss="created", lexicon="create"),
                    make_word("Gen.1.1", 3, "אֱלֹהִים", "ʾĕlōhîm", "H0430", "N-mp", gloss="God", lexicon="God"),
                ],
                6: [
                    make_word("Gen.1.6", 1, "וַיֹּאמֶר", "wayyōʾmer", "H0559", "V-Qal", gloss="and said", lexicon="say"),
                    make_word("Gen.1.6", 2, "אֱלֹהִים", "ʾĕlōhîm", "H0430", "N-mp", gloss="God", lexicon="God"),
                    make_word("Gen.1.6", 3, "יְהִי", "yəhî", "H1961", "V-Qal", gloss="let there be", lexicon="be"),
                    make_word("Gen.1.6", 4, "רָקִיעַ", "rāqîaʿ", "H7549", "N-ms", gloss="expanse", lexicon="firmament; expanse"),
                ],
                7: [
                    make_word("Gen.1.7", 1, "וַיַּעַשׂ", "wayyaʿaś", "H6213A", "V-Qal", gloss="and made", lexicon="make"),
                    make_word("Gen.1.7", 2, "אֱלֹהִים", "ʾĕlōhîm", "H0430", "N-mp", gloss="God", lexicon="God"),
                    make_word("Gen.1.7", 3, "אֶת", "ʾet", "H0853", "Part", gloss="[obj]", lexicon="obj"),
                    make_word("Gen.1.7", 4, "הָרָקִיעַ", "hārāqîaʿ", "H7549", "N-ms", gloss="the expanse", lexicon="firmament; expanse"),
                ],
            },
        )

    def test_transliteration_match_raqia_injects_only_h7549(self):
        batch = [{
            "name": "穹蒼（raqia）",
            "suggested_type": "原文",
            "evidence": "6-7節",
            "surfaces": [{"phrase": "空氣", "verses": [6, 7]}],
        }]
        evidence = step_context.select_m3_candidate_evidence(self.doc, batch)
        self.assertEqual("targeted", evidence.mode)
        self.assertEqual(1, evidence.candidate_count)
        self.assertEqual(1, evidence.selected_count)
        self.assertEqual(2, evidence.occurrences)
        self.assertIn("H7549", evidence.text)
        self.assertIn("rāqîaʿ", evidence.text)
        # Should NOT contain other words in v6 or v7
        self.assertNotIn("wayyōʾmer", evidence.text)
        self.assertNotIn("H6213A", evidence.text)

    def test_explicit_strong_matching(self):
        batch = [{
            "name": "創造",
            "suggested_type": "原文",
            "evidence": "1節；H1254",
            "surfaces": [],
        }]
        evidence = step_context.select_m3_candidate_evidence(self.doc, batch)
        self.assertEqual("targeted", evidence.mode)
        self.assertEqual(1, evidence.candidate_count)
        self.assertEqual(1, evidence.occurrences)
        self.assertIn("H1254", evidence.text)
        self.assertNotIn("H7225", evidence.text)

    def test_non_original_candidate_skipped(self):
        batch = [{
            "name": "敬畏神",
            "suggested_type": "神學",
            "evidence": "20節；CT 區分「敬畏」與「懼怕」",
            "surfaces": [],
        }]
        evidence = step_context.select_m3_candidate_evidence(self.doc, batch)
        self.assertEqual("non-original-skipped", evidence.mode)
        self.assertEqual(0, evidence.candidate_count)
        self.assertIn("非原文類條目", evidence.text)
        self.assertNotIn("H7549", evidence.text)

    def test_full_chapter_evidence_fails_small(self):
        batch = [{
            "name": "創造之工",
            "suggested_type": "原文",
            "evidence": "全章",
            "surfaces": [],
        }]
        evidence = step_context.select_m3_candidate_evidence(self.doc, batch)
        self.assertEqual("full-chapter-evidence", evidence.mode)
        self.assertEqual(0, evidence.candidate_count)
        self.assertIn("候選範圍為全章", evidence.text)

    def test_unresolved_fails_small(self):
        batch = [{
            "name": "完全未知詞彙",
            "suggested_type": "原文",
            "evidence": "無節號純文字",
            "surfaces": [],
        }]
        evidence = step_context.select_m3_candidate_evidence(self.doc, batch)
        self.assertEqual("unresolved", evidence.mode)
        self.assertEqual(0, evidence.candidate_count)
        self.assertIn("無法機械定位", evidence.text)

    def test_hebrew_shared_characters_does_not_false_positive(self):
        # In a single verse, words share letters (e.g. ה, י):
        # נָסָה (H5254), אֱלֹהִים (H0430), הָיָה (H1961)
        ref = extract_stepbible.parse_reference("Genesis 22:1")
        doc = extract_stepbible.StepDocument(
            reference=ref,
            verses={
                1: [
                    make_word("Gen.22.1", 1, "וְהָאֱלֹהִים", "wəhāʾĕlōhîm", "H0430", "N-mp", gloss="and God", lexicon="God"),
                    make_word("Gen.22.1", 2, "נִסָּה", "nissâ", "H5254", "V-Piel", gloss="tested", lexicon="test; prove"),
                    make_word("Gen.22.1", 3, "וַיְהִי", "wayhî", "H1961", "V-Qal", gloss="and it came to pass", lexicon="be; become"),
                ]
            }
        )
        batch = [{
            "name": "試驗（נָסָה）",
            "suggested_type": "原文",
            "evidence": "1節",
            "surfaces": [],
        }]
        evidence = step_context.select_m3_candidate_evidence(doc, batch)
        self.assertEqual("targeted", evidence.mode)
        self.assertEqual(1, evidence.candidate_count)
        self.assertIn("H5254", evidence.text)
        # H0430 (God) and H1961 (be) share letters with נסה but must NOT be matched!
        self.assertNotIn("H0430", evidence.text)
        self.assertNotIn("H1961", evidence.text)

    def test_greek_shared_characters_does_not_false_positive(self):
        # In a single verse, Greek words share letters:
        # λόγος (G3056), θεός (G2316), ἦν (G2258)
        ref = extract_stepbible.parse_reference("John 1:1")
        doc = extract_stepbible.StepDocument(
            reference=ref,
            verses={
                1: [
                    make_word("John.1.1", 1, "Ἐν", "En", "G1722", "Prep", gloss="In", lexicon="in"),
                    make_word("John.1.1", 2, "ἀρχῇ", "archē", "G0746", "N-DFS", gloss="beginning", lexicon="beginning"),
                    make_word("John.1.1", 3, "ἦν", "ēn", "G2258", "V-IAI-3S", gloss="was", lexicon="be"),
                    make_word("John.1.1", 4, "ὁ", "ho", "G3588", "T-NSM", gloss="the", lexicon="the"),
                    make_word("John.1.1", 5, "λόγος", "logos", "G3056", "N-NSM", gloss="Word", lexicon="word"),
                    make_word("John.1.1", 6, "καὶ", "kai", "G2532", "Conj", gloss="and", lexicon="and"),
                    make_word("John.1.1", 7, "ὁ", "ho", "G3588", "T-NSM", gloss="the", lexicon="the"),
                    make_word("John.1.1", 8, "λόγος", "logos", "G3056", "N-NSM", gloss="Word", lexicon="word"),
                    make_word("John.1.1", 9, "ἦν", "ēn", "G2258", "V-IAI-3S", gloss="was", lexicon="be"),
                    make_word("John.1.1", 10, "πρὸς", "pros", "G4314", "Prep", gloss="with", lexicon="with"),
                    make_word("John.1.1", 11, "τὸν", "ton", "G3588", "T-ASM", gloss="the", lexicon="the"),
                    make_word("John.1.1", 12, "θεόν", "theon", "G2316", "N-ASM", gloss="God", lexicon="God"),
                ]
            }
        )
        batch = [{
            "name": "道（λόγος）",
            "suggested_type": "原文",
            "evidence": "1節",
            "surfaces": [],
        }]
        evidence = step_context.select_m3_candidate_evidence(doc, batch)
        self.assertEqual("targeted", evidence.mode)
        self.assertEqual(1, evidence.candidate_count)
        self.assertIn("G3056", evidence.text)
        self.assertNotIn("G2316", evidence.text)
        self.assertNotIn("G2258", evidence.text)

    def test_bare_chinese_no_anchor_fails_small_without_guessing_high(self):
        # Candidate with no lexical anchor in a verse with a repeated word
        batch = [{
            "name": "純中文無錨點條目",
            "suggested_type": "原文",
            "evidence": "1節",
            "surfaces": [],
        }]
        evidence = step_context.select_m3_candidate_evidence(self.doc, batch)
        self.assertEqual("unresolved", evidence.mode)
        self.assertEqual(0, evidence.candidate_count)
        self.assertIn("無法機械定位", evidence.text)

    def test_multi_entry_batch_unions_occurrences_for_same_base_strong(self):
        # Two entries in the same batch point to the same Strong across different verses
        batch = [
            {
                "name": "穹蒼（raqia）",
                "suggested_type": "原文",
                "evidence": "6節",
                "surfaces": [],
            },
            {
                "name": "穹蒼（raqia）",
                "suggested_type": "原文",
                "evidence": "7節",
                "surfaces": [],
            },
        ]
        evidence = step_context.select_m3_candidate_evidence(self.doc, batch)
        self.assertEqual("targeted", evidence.mode)
        self.assertEqual(1, evidence.candidate_count)
        self.assertEqual(2, evidence.occurrences)
        self.assertEqual((6, 7), evidence.selected_verses)
        self.assertIn("6:4", evidence.text)
        self.assertIn("7:4", evidence.text)


if __name__ == "__main__":
    unittest.main()

