import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from clean_bible_html import normalize_text, filter_ccb_text, extract_kingcomments, TreeParser, decode_html


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

    def test_filter_ccb_text_ct_preserves_scripture(self):
        input_text = (
            "【利一1】「耶和華從會幕中呼叫摩西，對他說：」\n"
            "〔呂振中譯〕「永恆主呼叫摩西...」\n"
            "〔文意註解〕「耶和華從會幕中呼叫摩西」：按原文本節首字有「又」...\n"
        )
        expected_ct = (
            "【利一1】「耶和華從會幕中呼叫摩西，對他說：」\n"
            "〔文意註解〕「耶和華從會幕中呼叫摩西」：按原文本節首字有「又」..."
        )
        self.assertEqual(expected_ct, filter_ccb_text(input_text, is_gt=False))

    def test_filter_ccb_text_gt_strips_scripture_quote_retains_header(self):
        input_text = (
            "【利一1】「耶和華從會幕中呼叫摩西，對他說：」\n"
            "【利一1 利未記的寫作背景是──】出埃及記結束的時候...\n"
        )
        expected_gt = (
            "【利一1】\n"
            "【利一1 利未記的寫作背景是──】出埃及記結束的時候..."
        )
        self.assertEqual(expected_gt, filter_ccb_text(input_text, is_gt=True))

    def test_extract_kingcomments_omits_scripture_verse_blocks(self):
        sample_html = (
            "<html><body><main id='main-container'>"
            "<h1>Leviticus 1</h1>"
            "<div class='content'>"
            "  <div class='row'>"
            "    <div class='col-md-3 bg-body-dark'>"
            "      <p class='lead'>1 Then the LORD called to Moses...</p>"
            "    </div>"
            "    <div class='col-md-8'>"
            "      <p>There can and may always be fellowship with God...</p>"
            "    </div>"
            "  </div>"
            "</div>"
            "</main></body></html>"
        )
        parser = TreeParser()
        parser.feed(sample_html)
        text = extract_kingcomments(parser.root)
        self.assertNotIn("Then the LORD called to Moses", text)
        self.assertIn("There can and may always be fellowship with God", text)


if __name__ == "__main__":
    unittest.main()
