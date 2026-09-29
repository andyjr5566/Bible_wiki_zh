import tempfile
import unittest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

UTIL_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = UTIL_DIR.parent
if str(UTIL_DIR) not in sys.path:
    sys.path.insert(0, str(UTIL_DIR))

from appendix.website import build as website_build
from appendix.fhl_maps import build as fhl_maps_build
import build_appendix_links
import validate_knowledge_base
import normalize_format
import render_chapter


class AppendixWebsiteBuildEdgeCaseTests(unittest.TestCase):
    def test_title_extraction_no_title_tag(self):
        with tempfile.NamedTemporaryFile("w+", suffix=".html", encoding="utf-8", delete=False) as tf:
            tf.write("<html><head></head><body><h1>No Title Tag</h1></body></html>")
            tf_path = Path(tf.name)
        try:
            title = website_build.extract_title(tf_path)
            self.assertEqual(title, tf_path.stem)
        finally:
            tf_path.unlink(missing_ok=True)

    def test_title_extraction_multiline_and_pipe_splitting(self):
        with tempfile.NamedTemporaryFile("w+", suffix=".html", encoding="utf-8", delete=False) as tf:
            tf.write("<html><head><title>\n  創世記第6章導覽  |  Bible Explorer  \n</title></head></html>")
            tf_path = Path(tf.name)
        try:
            title = website_build.extract_title(tf_path)
            self.assertEqual(title, "創世記第6章導覽")
        finally:
            tf_path.unlink(missing_ok=True)


class AppendixLinksSyncEdgeCaseTests(unittest.TestCase):
    def test_navigation_stays_at_document_end_after_appendix_sync(self):
        original = (
            "# 創世記 第6章\n\n"
            "1. 經文節1。\n\n"
            "---\n\n"
            "## 本章知識節點\n\n"
            "## 本章整理\n\n正文。\n\n"
            "<!-- chapter-navigation:start -->\n"
            "[[第5章|前一章]]　[[全書目錄及綱要|回目錄]]　[[第7章|下一章]]\n"
            "<!-- chapter-navigation:end -->\n"
        )
        with tempfile.NamedTemporaryFile("w+", suffix=".md", encoding="utf-8", delete=False) as tf:
            tf.write(original)
            tf_path = Path(tf.name)

        try:
            synced = build_appendix_links.sync_chapter(
                tf_path, ["### 互動網站\n- [導覽](app.html)"]
            )
            self.assertTrue(synced.rstrip().endswith("<!-- chapter-navigation:end -->"))
            self.assertLess(synced.index("## 附錄"), synced.rindex("<!-- chapter-navigation:start -->"))
        finally:
            tf_path.unlink(missing_ok=True)

    def test_sync_chapter_removal_when_sections_empty(self):
        """當附錄資源清單為空時，應清理既有的 appendix-links 區塊。"""
        original = (
            "# 創世記 第6章\n\n"
            "1. 經文節1。\n\n"
            "---\n\n"
            "## 本章知識節點\n\n"
            "## 本章整理\n\n正文。\n\n"
            "<!-- appendix-links:start -->\n"
            "## 附錄\n\n"
            "### 互動網站\n"
            "- [舊連結](old.html)\n"
            "<!-- appendix-links:end -->\n"
        )
        with tempfile.NamedTemporaryFile("w+", suffix=".md", encoding="utf-8", delete=False) as tf:
            tf.write(original)
            tf_path = Path(tf.name)

        try:
            synced = build_appendix_links.sync_chapter(tf_path, [])
            self.assertNotIn("<!-- appendix-links:start -->", synced)
            self.assertNotIn("## 附錄", synced)
            self.assertIn("## 本章整理\n\n正文。", synced)
        finally:
            tf_path.unlink(missing_ok=True)

    def test_old_fhl_map_links_migrated_to_appendix_links(self):
        """驗證舊有的 fhl-map-links 區塊會被自動清理並遷移至末尾的 appendix-links 區塊。"""
        original = (
            "# 創世記 第6章\n\n"
            "1. 經文節1。\n\n"
            "<!-- fhl-map-links:start -->\n"
            "## 相關地圖\n\n"
            "- [[appendix/fhl_maps/maps/006|〈創圖一〉]]\n"
            "<!-- fhl-map-links:end -->\n\n"
            "---\n\n"
            "## 本章知識節點\n\n"
            "## 本章整理\n\n正文。\n"
        )
        sections = [
            "### 相關地圖\n- [[appendix/fhl_maps/maps/006|〈創圖一〉]]",
            "### 互動網站\n- [3D導覽](app.html)",
        ]
        with tempfile.NamedTemporaryFile("w+", suffix=".md", encoding="utf-8", delete=False) as tf:
            tf.write(original)
            tf_path = Path(tf.name)

        try:
            synced = build_appendix_links.sync_chapter(tf_path, sections)
            self.assertNotIn("<!-- fhl-map-links:start -->", synced)
            self.assertIn("<!-- appendix-links:start -->", synced)

            org_idx = synced.find("## 本章整理")
            res_idx = synced.find("## 附錄")
            self.assertTrue(org_idx < res_idx)
        finally:
            tf_path.unlink(missing_ok=True)


class BookIndexSyncTests(unittest.TestCase):
    OUTLINE = (
        "## 🗂️ 民數記目錄\n\n### 預備（1-10 章）\n[[04 民數記/第1章|第1章]]\n\n\n"
        "## 🎬 大衛鮑森舊約縱覽\n\n影片\n"
    )

    def _block(self, chapters):
        items = {name: [{"title": t, "path": f"appendix/website/民數記/{name}/dist/index.html"}] for name, t in chapters}
        return build_appendix_links.book_index_block("website", "🕹️ 互動網站", "04 民數記", items)

    def test_block_is_sorted_by_chapter_number_not_by_text(self):
        block = self._block([("第10章", "十"), ("第2章", "二"), ("第1章", "一")])
        order = [block.index(f"[[04 民數記/{n}|{n}]]") for n in ("第1章", "第2章", "第10章")]
        self.assertEqual(order, sorted(order))
        self.assertIn("[二](appendix/website/民數記/第2章/dist/index.html)", block)

    def test_inserted_before_video_section_then_idempotent(self):
        block = self._block([("第2章", "環繞會幕")])
        once = build_appendix_links.sync_book_index(self.OUTLINE, "website", block)
        self.assertLess(once.index("## 🕹️ 互動網站"), once.index("## 🎬"))
        self.assertGreater(once.index("## 🕹️ 互動網站"), once.index("## 🗂️"))
        twice = build_appendix_links.sync_book_index(once, "website", block)
        self.assertEqual(once, twice)

    def test_existing_block_is_replaced_in_place(self):
        once = build_appendix_links.sync_book_index(self.OUTLINE, "website", self._block([("第2章", "舊名")]))
        new = build_appendix_links.sync_book_index(once, "website", self._block([("第2章", "新名"), ("第4章", "四")]))
        self.assertNotIn("舊名", new)
        self.assertIn("新名", new)
        self.assertEqual(new.count("<!-- appendix-index:website:start -->"), 1)
        self.assertLess(new.index("appendix-index:website:end"), new.index("## 🎬"))

    def test_without_entries_the_outline_is_left_byte_for_byte(self):
        self.assertEqual(build_appendix_links.sync_book_index(self.OUTLINE, "website", None), self.OUTLINE)

    def test_stale_block_is_removed_when_book_has_no_entries(self):
        once = build_appendix_links.sync_book_index(self.OUTLINE, "website", self._block([("第2章", "x")]))
        gone = build_appendix_links.sync_book_index(once, "website", None)
        self.assertNotIn("appendix-index", gone)
        self.assertNotIn("互動網站", gone)
        self.assertIn("## 🎬 大衛鮑森舊約縱覽", gone)

    def test_appended_at_end_when_no_video_section(self):
        outline = "## 🗂️ 目錄\n\n[[04 民數記/第1章|第1章]]\n"
        text = build_appendix_links.sync_book_index(outline, "website", self._block([("第2章", "x")]))
        self.assertTrue(text.rstrip().endswith("<!-- appendix-index:website:end -->"))

    def test_only_plugins_that_opt_in_touch_the_outline(self):
        plugin = lambda mod: {"name": "p", "module": mod}  # noqa: E731
        optout = MagicMock(spec=[])  # 沒有 BOOK_INDEX_HEADING
        entries = [{"plugin": plugin(optout), "title": "地圖", "entries": {"民數記/第2章": [{"title": "t", "path": "p"}]}}]
        self.assertEqual(build_appendix_links.book_index_updates(entries), {})

    def test_website_plugin_opts_in(self):
        self.assertTrue(getattr(website_build, "BOOK_INDEX_HEADING", ""))
        self.assertFalse(hasattr(fhl_maps_build, "BOOK_INDEX_HEADING"))


class AppendixValidationEdgeCaseTests(unittest.TestCase):
    def test_mismatched_appendix_comment_tags(self):
        """測試只有 start 標籤或重複標籤時 validate_knowledge_base 報錯。"""
        verses = "\n".join(f"{i}. 經文節{i}。" for i in range(1, 23))
        content = (
            f"# 創世記 第6章\n\n"
            f"{verses}\n\n"
            "---\n\n"
            "## 本章知識節點\n\n"
            "### 主題\n- [[創世記]]\n\n"
            "---\n\n"
            "## 本章整理\n\n正文\n\n"
            "<!-- appendix-links:start -->\n"
            "## 附錄\n\n"
            "### 互動網站\n"
            "- [測試](a.html)\n"
            "<!-- appendix-links:start -->\n"
        )
        test_dir = ROOT_DIR / ".tmp" / "01 創世記"
        test_dir.mkdir(parents=True, exist_ok=True)
        tf_path = test_dir / "第6章.md"
        tf_path.write_text(content, encoding="utf-8")

        try:
            errors = validate_knowledge_base.validate_chapter(tf_path)
            self.assertTrue(any("附錄必須由單一 appendix-links 區塊管理" in err for err in errors))
        finally:
            tf_path.unlink(missing_ok=True)

    def test_appendix_placed_before_organization_fails_validation(self):
        """測試 ## 附錄 若被誤放於「本章整理」之前時 validate_knowledge_base 報錯。"""
        verses = "\n".join(f"{i}. 經文節{i}。" for i in range(1, 23))
        content = (
            f"# 創世記 第6章\n\n"
            f"{verses}\n\n"
            "<!-- appendix-links:start -->\n"
            "## 附錄\n\n"
            "### 互動網站\n"
            "- [測試](a.html)\n"
            "<!-- appendix-links:end -->\n\n"
            "---\n\n"
            "## 本章知識節點\n\n"
            "### 主題\n- [[創世記]]\n\n"
            "---\n\n"
            "## 本章整理\n\n正文\n"
        )
        test_dir = ROOT_DIR / ".tmp" / "01 創世記"
        test_dir.mkdir(parents=True, exist_ok=True)
        tf_path = test_dir / "第6章.md"
        tf_path.write_text(content, encoding="utf-8")

        try:
            errors = validate_knowledge_base.validate_chapter(tf_path)
            self.assertTrue(any("附錄必須位於本章整理之後" in err or "H2 必須依序為" in err for err in errors))
        finally:
            tf_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
