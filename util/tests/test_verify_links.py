import tempfile
import unittest
from pathlib import Path

from util.verify_links import build_registry, get_link_folders, is_existing_path_link


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

    def test_registry_recognizes_frontmatter_aliases(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            entry = root / "link_folder" / "神學" / "正式名稱.md"
            entry.parent.mkdir(parents=True)
            entry.write_text(
                "---\n"
                "type: 神學\n"
                "secondary_types: []\n"
                'aliases: ["含/斜線的別名", "別名 (章1:2)"]\n'
                "status: formal\n"
                "source_scope: collected_only\n"
                "---\n\n"
                "# 正式名稱\n",
                encoding="utf-8",
            )

            entities, locations, _ = build_registry(root, get_link_folders(root))

            self.assertIn("正式名稱", entities)
            self.assertIn("含/斜線的別名", entities)
            self.assertIn("別名 (章1:2)", entities)
            self.assertEqual(
                locations["含/斜線的別名"],
                "link_folder/神學/正式名稱.md",
            )


if __name__ == "__main__":
    unittest.main()
