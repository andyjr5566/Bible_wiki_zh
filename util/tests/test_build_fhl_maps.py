import tempfile
import unittest
import sys
from pathlib import Path
from unittest.mock import patch

from appendix.fhl_maps import build as build_fhl_maps
from util import optimize_fhl_map_images

UTIL_DIR = Path(__file__).resolve().parents[1]
if str(UTIL_DIR) not in sys.path:
    sys.path.insert(0, str(UTIL_DIR))

import validate_knowledge_base
import normalize_format


class ScriptureReferenceTests(unittest.TestCase):
    def test_cross_chapter_reference(self):
        self.assertEqual(
            build_fhl_maps.parse_scripture_reference("創37:12-28;39:1-41:57"),
            ("創世記", [37, 39, 40, 41]),
        )

    def test_spaces_and_cross_chapter_range(self):
        self.assertEqual(
            build_fhl_maps.parse_scripture_reference("創 12:10-13:1"),
            ("創世記", [12, 13]),
        )

    def test_unknown_reference_is_preserved(self):
        self.assertEqual(
            build_fhl_maps.parse_scripture_reference("代4:1:1-23"),
            (None, []),
        )

    def test_existing_reference_uses_ordered_book_folder(self):
        with patch.object(build_fhl_maps, "chapter_path") as chapter_path:
            chapter_path.return_value.exists.return_value = True
            self.assertEqual(
                "[[01 創世記/第14章|創14:1-16]]",
                build_fhl_maps.render_scripture_reference("創14:1-16"),
            )

    def test_description_paragraphs_are_separated_by_blank_lines(self):
        rendered = build_fhl_maps.render_description("標題\n第一段\n第二段", {})
        self.assertEqual(rendered, "第一段\n\n第二段")

    def test_jpeg_is_only_adopted_after_reduction_threshold(self):
        self.assertTrue(optimize_fhl_map_images.should_adopt(1000, 899, 0.10))
        self.assertFalse(optimize_fhl_map_images.should_adopt(1000, 901, 0.10))


import build_appendix_links


class ChapterSyncTests(unittest.TestCase):
    def test_block_is_inserted_before_first_rule_and_is_idempotent(self):
        sections = ["### 相關地圖\n- [[appendix/fhl_maps/maps/011|〈創圖六〉北方四王攻打南方五王]]"]
        original = "# 創世記 第14章\n\n1. 經文。\n\n---\n\n## 本章知識節點\n\n## 本章整理\n\n正文。\n"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "第14章.md"
            path.write_text(original, encoding="utf-8")
            first = build_appendix_links.sync_chapter(path, sections)
            path.write_text(first, encoding="utf-8")
            second = build_appendix_links.sync_chapter(path, sections)

        self.assertEqual(first, second)
        self.assertIn("## 附錄", first)
        self.assertIn("<!-- appendix-links:start -->", first)

    def test_normalizer_preserves_managed_map_section(self):
        sections = ["### 相關地圖\n- [[appendix/fhl_maps/maps/011|〈創圖六〉北方四王攻打南方五王]]"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "創世記" / "第14章.md"
            path.parent.mkdir()
            path.write_text(
                "# 創世記 第14章\n\n1. 經文。\n\n---\n\n"
                "## 本章知識節點\n\n- [[測試]]\n\n"
                "## 本章整理\n\n整理。\n",
                encoding="utf-8",
            )
            synced = build_appendix_links.sync_chapter(path, sections)
            path.write_text(synced, encoding="utf-8")
            normalized = normalize_format.normalize_chapter(path)

        self.assertIn("<!-- appendix-links:start -->", normalized)
        self.assertGreater(
            normalized.index("## 附錄"),
            normalized.index("## 本章整理"),
        )

    def test_validator_accepts_managed_map_section_after_scripture(self):
        sections = ["### 相關地圖\n- [[appendix/fhl_maps/maps/011|〈創圖六〉北方四王攻打南方五王]]"]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            chapter_dir = root / "創世記"
            chapter_dir.mkdir()
            path = chapter_dir / "第14章.md"
            verses = "\n".join(f"{i}. 經文節{i}。" for i in range(1, 25))
            base = (
                "# 創世記 第14章\n\n"
                f"{verses}\n\n---\n\n"
                "## 本章知識節點\n\n- [[測試]]\n\n"
                "## 本章整理\n\n整理。\n"
            )
            path.write_text(base, encoding="utf-8")
            synced = build_appendix_links.sync_chapter(path, sections)
            path.write_text(synced, encoding="utf-8")
            with patch.object(validate_knowledge_base, "ROOT", root):
                errors = validate_knowledge_base.validate_chapter(path)

        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
