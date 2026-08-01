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
    def test_sync_chapter_removal_when_sections_empty(self):
        """當附錄資源清單為空時，應清理既有的 appendix-links 區塊。"""
        original = (
            "# 創世記 第6章\n\n"
            "1. 經文節1。\n\n"
            "<!-- appendix-links:start -->\n"
            "## 相關資源\n\n"
            "### 互動網站\n"
            "- [舊連結](old.html)\n"
            "<!-- appendix-links:end -->\n\n"
            "---\n\n"
            "## 本章知識節點\n"
        )
        with tempfile.NamedTemporaryFile("w+", suffix=".md", encoding="utf-8", delete=False) as tf:
            tf.write(original)
            tf_path = Path(tf.name)

        try:
            synced = build_appendix_links.sync_chapter(tf_path, [])
            self.assertNotIn("<!-- appendix-links:start -->", synced)
            self.assertNotIn("## 相關資源", synced)
            self.assertIn("# 創世記 第6章\n\n1. 經文節1。\n\n---\n\n## 本章知識節點", synced)
        finally:
            tf_path.unlink(missing_ok=True)

    def test_sync_chapter_missing_divider_raises_value_error(self):
        """若章節檔找不到經文後的分隔線，應拋出明確 ValueError 訊息。"""
        bad_chapter = "# 創世記 第6章\n\n1. 經文節1。\n\n## 本章知識節點\n"
        with tempfile.NamedTemporaryFile("w+", suffix=".md", encoding="utf-8", delete=False) as tf:
            tf.write(bad_chapter)
            tf_path = Path(tf.name)

        try:
            with self.assertRaises(ValueError) as cm:
                build_appendix_links.sync_chapter(tf_path, ["### 互動網站\n- [test](a.html)"])
            self.assertIn("找不到經文正文後的分隔線", str(cm.exception))
        finally:
            tf_path.unlink(missing_ok=True)

    def test_both_fhl_maps_and_appendix_links_coexist(self):
        """驗證 ## 相關地圖 與 ## 相關資源 並存時之順序與獨立維護。"""
        original = (
            "# 創世記 第6章\n\n"
            "1. 經文節1。\n\n"
            "<!-- fhl-map-links:start -->\n"
            "## 相關地圖\n\n"
            "- [[appendix/fhl_maps/maps/006|〈創圖一〉]]\n"
            "<!-- fhl-map-links:end -->\n\n"
            "---\n\n"
            "## 本章知識節點\n"
        )
        sections = ["### 互動網站\n- [3D導覽](app.html)"]
        with tempfile.NamedTemporaryFile("w+", suffix=".md", encoding="utf-8", delete=False) as tf:
            tf.write(original)
            tf_path = Path(tf.name)

        try:
            synced = build_appendix_links.sync_chapter(tf_path, sections)
            self.assertIn("<!-- fhl-map-links:start -->", synced)
            self.assertIn("<!-- appendix-links:start -->", synced)

            # 驗證結構順序：地圖 -> 資源 -> 分隔線
            map_idx = synced.find("## 相關地圖")
            res_idx = synced.find("## 相關資源")
            rule_idx = synced.find("---")
            self.assertTrue(map_idx < res_idx < rule_idx)
        finally:
            tf_path.unlink(missing_ok=True)


class AppendixValidationEdgeCaseTests(unittest.TestCase):
    def test_mismatched_appendix_comment_tags(self):
        """測試只有 start 標籤或重複標籤時 validate_knowledge_base 報錯。"""
        verses = "\n".join(f"{i}. 經文節{i}。" for i in range(1, 23))
        content = (
            f"# 創世記 第6章\n\n"
            f"{verses}\n\n"
            "<!-- appendix-links:start -->\n"
            "## 相關資源\n\n"
            "### 互動網站\n"
            "- [測試](a.html)\n"
            "<!-- appendix-links:start -->\n\n"
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
            self.assertTrue(any("相關資源必須由單一 appendix-links 區塊管理" in err for err in errors))
        finally:
            tf_path.unlink(missing_ok=True)

    def test_appendix_placed_after_rule_fails_validation(self):
        """測試 ## 相關資源 若被誤放於分隔線 --- 之後時 validate_knowledge_base 報錯。"""
        verses = "\n".join(f"{i}. 經文節{i}。" for i in range(1, 23))
        content = (
            f"# 創世記 第6章\n\n"
            f"{verses}\n\n"
            "---\n\n"
            "<!-- appendix-links:start -->\n"
            "## 相關資源\n\n"
            "### 互動網站\n"
            "- [測試](a.html)\n"
            "<!-- appendix-links:end -->\n\n"
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
            self.assertTrue(any("相關資源必須位於經文正文後、第一條分隔線前" in err or "H2 必須依序為" in err for err in errors))
        finally:
            tf_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
