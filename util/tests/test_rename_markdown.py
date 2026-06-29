import sys
import tempfile
import unittest
from pathlib import Path


UTIL_DIR = Path(__file__).resolve().parents[1]
if str(UTIL_DIR) not in sys.path:
    sys.path.insert(0, str(UTIL_DIR))

from rename_markdown import RenameError, rename_markdown


class RenameMarkdownTests(unittest.TestCase):
    def make_file(self, root, relative, text):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_rename_updates_targets_and_preserves_aliases_and_fragments(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self.make_file(
                root,
                "link_folder/文化/風茄（催情果）.md",
                "# 風茄（催情果）\n\n[[風茄（催情果）|自身]]\n",
            )
            reference = self.make_file(
                root,
                "創世記/第30章.md",
                "\n".join([
                    "[[風茄（催情果）]]",
                    "[[風茄（催情果）|催情果]]",
                    "![[風茄（催情果）#定義|圖片別名]]",
                    "[[link_folder/文化/風茄（催情果）|完整路徑]]",
                ]),
            )
            destination = root / "link_folder/文化/風茄_催情果.md"

            result = rename_markdown(source, destination, root=root)

            self.assertFalse(source.exists())
            self.assertTrue(destination.exists())
            self.assertEqual(5, result.changed_links)
            self.assertEqual(2, result.changed_files)
            self.assertIn(
                "[[風茄_催情果|自身]]",
                destination.read_text(encoding="utf-8"),
            )
            self.assertIn(
                "# 風茄_催情果",
                destination.read_text(encoding="utf-8"),
            )
            updated = reference.read_text(encoding="utf-8")
            self.assertIn("[[風茄_催情果]]", updated)
            self.assertIn("[[風茄_催情果|催情果]]", updated)
            self.assertIn("![[風茄_催情果#定義|圖片別名]]", updated)
            self.assertIn(
                "[[link_folder/文化/風茄_催情果|完整路徑]]", updated
            )

    def test_duplicate_destination_filename_is_rejected_without_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self.make_file(root, "a/舊名.md", "# 舊名\n")
            self.make_file(root, "b/新名.md", "# 已存在\n")
            reference = self.make_file(root, "ref.md", "[[舊名]]\n")

            with self.assertRaisesRegex(RenameError, "目標檔名.*已存在"):
                rename_markdown(source, root / "a/新名.md", root=root)

            self.assertTrue(source.exists())
            self.assertEqual("[[舊名]]\n", reference.read_text(encoding="utf-8"))

    def test_ambiguous_unqualified_link_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self.make_file(root, "a/同名.md", "# A\n")
            self.make_file(root, "b/同名.md", "# B\n")
            reference = self.make_file(root, "ref.md", "[[同名]]\n")

            with self.assertRaisesRegex(RenameError, "無法判定"):
                rename_markdown(source, root / "a/新名.md", root=root)

            self.assertTrue(source.exists())
            self.assertFalse((root / "a/新名.md").exists())
            self.assertEqual("[[同名]]\n", reference.read_text(encoding="utf-8"))

    def test_dry_run_reports_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self.make_file(root, "a/舊名.md", "# 舊名\n")
            reference = self.make_file(root, "ref.md", "[[舊名|顯示文字]]\n")
            destination = root / "a/新名.md"

            result = rename_markdown(
                source, destination, root=root, dry_run=True
            )

            self.assertTrue(result.dry_run)
            self.assertEqual(1, result.changed_links)
            self.assertTrue(source.exists())
            self.assertFalse(destination.exists())
            self.assertEqual(
                "[[舊名|顯示文字]]\n", reference.read_text(encoding="utf-8")
            )


if __name__ == "__main__":
    unittest.main()
