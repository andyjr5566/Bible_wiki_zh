import tempfile
import unittest
from pathlib import Path

from util.book_paths import (
    book_directory,
    canonical_book_name,
    ordered_book_dir_name,
)


class BookPathTests(unittest.TestCase):
    def test_ordered_names_follow_canonical_book_order(self):
        self.assertEqual("01 創世記", ordered_book_dir_name("創世記"))
        self.assertEqual("02 出埃及記", ordered_book_dir_name("出埃及記"))
        self.assertEqual("40 馬太福音", ordered_book_dir_name("馬太福音"))

    def test_ordered_folder_is_preferred_with_legacy_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            legacy = root / "創世記"
            legacy.mkdir()
            self.assertEqual(legacy, book_directory(root, "創世記"))

            ordered = root / "01 創世記"
            ordered.mkdir()
            self.assertEqual(ordered, book_directory(root, "創世記"))
            self.assertEqual("創世記", canonical_book_name(ordered.name))


if __name__ == "__main__":
    unittest.main()
