import tempfile
import unittest
from pathlib import Path

from util.verify_links import is_existing_path_link


class ExistingPathLinkTests(unittest.TestCase):
    def test_resolves_vault_relative_markdown_path(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "appendix" / "maps" / "001.md"
            target.parent.mkdir(parents=True)
            target.write_text("# Map\n", encoding="utf-8")

            self.assertTrue(is_existing_path_link(root, "appendix/maps/001"))
            self.assertTrue(is_existing_path_link(root, "appendix/maps/001#section"))
            self.assertFalse(is_existing_path_link(root, "appendix/maps/002"))
            self.assertFalse(is_existing_path_link(root, "../outside"))


if __name__ == "__main__":
    unittest.main()
