import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from clean_bible_html import normalize_text


class CleanBibleHtmlTests(unittest.TestCase):
    def test_repairs_big5_text_decoded_as_latin1(self):
        original = "創世記第三十六章註解\n\n【以掃的後裔】"
        mojibake = original.encode("cp950").decode("latin-1")

        self.assertEqual(original, normalize_text(mojibake))

    def test_repairs_big5_lines_when_document_has_unicode(self):
        original = "創世記第三十六章註解\n\n【以掃的後裔】"
        mojibake = original.encode("cp950").decode("latin-1")

        self.assertEqual(
            original + "\n\nAlready decoded – ok",
            normalize_text(mojibake + "\n\nAlready decoded – ok"),
        )


if __name__ == "__main__":
    unittest.main()
