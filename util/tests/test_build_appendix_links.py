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
