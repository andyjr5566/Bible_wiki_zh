import json
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


UTIL_DIR = Path(__file__).resolve().parents[1]
if str(UTIL_DIR) not in sys.path:
    sys.path.insert(0, str(UTIL_DIR))

import extract_stepbible as step


class ReferenceAndFilenameTests(unittest.TestCase):
    def test_chinese_and_english_references_match(self):
        zh = step.parse_reference("創世記 第1章 第2節")
        en = step.parse_reference("Genesis 1:2")
        self.assertEqual((zh.code, zh.chapter, zh.verse_start, zh.verse_end),
                         (en.code, en.chapter, en.verse_start, en.verse_end))

    def test_nt_range_parses(self):
        ref = step.parse_reference("John 1:1-5")
        self.assertEqual(("Jhn", 1, 1, 5, "NT"),
                         (ref.code, ref.chapter, ref.verse_start, ref.verse_end, ref.testament))

    def test_all_66_books_have_unique_canonical_filenames(self):
        names = step.validate_book_contract()
        self.assertEqual(66, len(names))
        self.assertEqual(66, len(set(names)))
        self.assertEqual("stepbible_genesis_1.txt", names[0])
        self.assertEqual("stepbible_revelation_1.txt", names[-1])

    def test_range_filename_is_not_the_full_chapter_contract(self):
        self.assertEqual(
            "stepbible_john_1_1-5.json",
            step.stepbible_filename("約翰福音", 1, 1, 5, extension="json"),
        )


class ParserAndRendererTests(unittest.TestCase):
    def test_ot_strong_morphology_lexicon_and_h90xx_filter(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tagged = root / "TAHOT Gen-Deu fixture.txt"
            tagged.write_text(
                "Gen.1.1#01=L\tבְּרֵאשִׁית\tbəreʾšît\tin beginning\tH9001 H7225\tHR/Ncfsa\n"
                "Gen.1.2#01\tהָיְתָה\thayetah\twas\tH1961\tHVqp3fs\n",
                encoding="utf-8",
            )
            lex = root / "TBESH fixture.txt"
            lex.write_text(
                "H7225\t=\tH7225\tרֵאשִׁית\tre'shith\tN\tbeginning\tfirst or beginning\n",
                encoding="utf-8",
            )
            morph = root / "TEHMC fixture.txt"
            morph.write_text(
                "HR\tFunction=Preposition\n\tPreposition\n$\n"
                "HNcfsa\tFunction=Noun\n\tNoun feminine singular absolute\n$\n",
                encoding="utf-8",
            )
            ref = step.parse_reference("創世記 1:1")
            verses = step.parse_tahot(
                tagged, ref, step.parse_lexicon(lex, "hebrew"), step.parse_morphology_file(morph)
            )
            word = verses[1][0]
            self.assertEqual("H7225", word.main_strong)
            self.assertIn("H9001", word.strongs)
            self.assertEqual("beginning", word.lexicon_short)
            self.assertIn("Preposition", word.morphology)
            self.assertIn("Noun feminine singular absolute", word.morphology)

            txt = step.render_markdown(ref, verses, False)
            self.assertIn("原文證據層", txt)
            self.assertIn("בְּרֵאשִׁית", txt)
            self.assertIn("H7225", txt)
            self.assertIn("CC BY 4.0", txt)
            self.assertIn("creativecommons.org/licenses/by/4.0", txt)

    def test_nt_parser_and_json_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tagged = root / "TAGNT Mat-Jhn fixture.txt"
            tagged.write_text(
                "Jhn.1.1#01\tἘν (En)\tin\tG1722=PREP\tin\n"
                "Jhn.1.1#02\tἀρχῇ (archē)\tbeginning\tG746=N-DSF\tbeginning\n",
                encoding="utf-8",
            )
            lex = root / "TBESG fixture.txt"
            lex.write_text(
                "G1722\t=\tG1722\tἐν\ten\tPrep\tin\tin, on, at\n",
                encoding="utf-8",
            )
            morph = root / "TEGMC fixture.txt"
            morph.write_text("PREP\tFunction=Preposition\n\tPreposition\n$\n", encoding="utf-8")
            ref = step.parse_reference("John 1:1")
            verses = step.parse_tagnt(
                tagged, ref, step.parse_lexicon(lex, "greek"), step.parse_morphology_file(morph)
            )
            first = verses[1][0]
            self.assertEqual(("Ἐν", "En", "G1722", "Preposition"),
                             (first.word, first.transliteration, first.main_strong, first.morphology))
            payload = json.loads(step.render_json(ref, verses))
            self.assertEqual("STEP Bible / STEPBible-Data", payload["source"])
            self.assertEqual("CC BY 4.0", payload["license"])
            self.assertEqual("https://creativecommons.org/licenses/by/4.0/",
                             payload["license_url"])
            self.assertEqual("Ἐν ἀρχῇ", payload["verses"][0]["original"])

    def test_primary_lexicon_row_overrides_earlier_cross_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "TBESG fixture.txt"
            path.write_text(
                "G999\tsee G3588\tG3588\tτανῦν\ttanun\tAdv\tnow\tnow\n"
                "G3588\tG3588 =\tG3588\tὁ\tho\tG:T\tthe/this/who\tthe article\n",
                encoding="utf-8",
            )
            lexicon = step.parse_lexicon(path, "greek")
            self.assertEqual("ὁ", lexicon["G3588"].word)
            self.assertEqual("the/this/who", lexicon["G3588"].short_definition)

    def test_extended_hebrew_key_comes_from_relation_column(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "TBESH fixture.txt"
            path.write_text(
                "H0410\tH0410I = combination of\tH3068G (H0410I+H0430G)\t"
                "אֵל\tel\tH:N-M\tEl (Elohe)\tcombined name\n"
                "H0430\tH0430G = a Name of\tH3068G\t"
                "אֱלֹהִים\te.lo.him\tH:N-M\tGod\tgods; God\n",
                encoding="utf-8",
            )
            lexicon = step.parse_lexicon(path, "hebrew")
            self.assertEqual("אֱלֹהִים", lexicon["H430G"].word)
            self.assertEqual("God", lexicon["H430G"].short_definition)
            self.assertEqual("אֵל", lexicon["H410I"].word)

    def test_cli_refuses_to_write_empty_formal_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tagged = root / "TAHOT Gen-Deu fixture.txt"
            tagged.write_text("Gen.2.1#01\tדבר\tdabar\tword\tH1697\tHNcmsa\n", encoding="utf-8")
            out = root / "raw_data"
            with patch.object(sys, "argv", [
                "extract_stepbible.py", "Genesis 1", "--data_path", str(root),
                "--output_path", str(out), "--format", "txt",
            ]):
                self.assertEqual(4, step.main())
            self.assertFalse((out / "stepbible_genesis_1.txt").exists())

    def test_download_is_atomic_and_rejects_truncation(self):
        class FakeResponse:
            def __init__(self):
                self.headers = {"Content-Length": "10"}
                self.stream = io.BytesIO(b"short")

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self, size=-1):
                return self.stream.read(size)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(step.urllib.request, "urlopen", return_value=FakeResponse()):
                with self.assertRaises(OSError):
                    step.download_official_file(root, "TBESH")
            dest = root / step.OFFICIAL_FILES["TBESH"]
            self.assertFalse(dest.exists())
            self.assertFalse(dest.with_suffix(dest.suffix + ".part").exists())


if __name__ == "__main__":
    unittest.main()
