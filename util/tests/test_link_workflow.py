import tempfile
import unittest
import sys
from pathlib import Path
from unittest.mock import patch

import yaml

UTIL_DIR = Path(__file__).resolve().parents[1]
if str(UTIL_DIR) not in sys.path:
    sys.path.insert(0, str(UTIL_DIR))

from build_link_index import make_index
from resolve_link_candidates import (
    find_in_index,
    has_book_chapter_data,
    resolve,
)
from validate_knowledge_base import INTERNAL_SOURCE_LINE_RE, ambiguous_wikilinks
from link_updates import apply_updates, render_block, validate_update
from normalize_format import normalize_chapter, normalize_entry


def entry(title, path, entry_type, aliases=None, secondary=None):
    return {
        "title": title,
        "path": path,
        "type": entry_type,
        "aliases": aliases or [],
        "secondary_types": secondary or [],
        "status": "formal",
    }


class IndexTests(unittest.TestCase):
    def test_secondary_type_is_not_alias(self):
        index, errors = make_index([
            entry("天梯", "link_folder/神學/天梯.md", "神學", secondary=["互文"])
        ])
        self.assertFalse(errors)
        self.assertNotIn("互文", index)

    def test_duplicate_alias_is_blocking(self):
        _, errors = make_index([
            entry("甲", "link_folder/主題/甲.md", "主題", aliases=["共同名"]),
            entry("乙", "link_folder/主題/乙.md", "主題", aliases=["共同名"]),
        ])
        self.assertTrue(any("alias 多重指向" in error for error in errors))


class ResolverTests(unittest.TestCase):
    def test_exact_name_keeps_parenthetical_content(self):
        target = entry(
            "全能的神（El Shaddai）",
            "link_folder/神學/全能的神（El Shaddai）.md",
            "神學",
        )
        index = {"全能的神（El Shaddai）": target}
        match_type, matched, title = find_in_index("全能的神（El Shaddai）", index)
        self.assertEqual("exact", match_type)
        self.assertEqual(target, matched)
        self.assertEqual("全能的神（El Shaddai）", title)

    def test_type_mismatch_requires_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "link_folder" / "人物" / "迦南.md"
            path.parent.mkdir(parents=True)
            path.write_text("# 迦南\n", encoding="utf-8")
            index = {"迦南": entry("迦南", "link_folder/人物/迦南.md", "人物")}
            plan = resolve(
                [{"name": "迦南", "suggested_type": "地點", "line_number": 1}],
                index, "創世記", "28", root,
            )
            self.assertEqual(1, len(plan["D_new_candidate"]))
            self.assertEqual("type_conflict", plan["D_new_candidate"][0]["match_type"])

    def test_registered_homonym_requires_manual_target_selection(self):
        homonyms = {
            "示劍": [
                {"target": "示劍（城）", "type": "地點"},
                {"target": "示劍（哈抹之子）", "type": "人物"},
            ]
        }
        plan = resolve(
            [{"name": "示劍", "suggested_type": "地點", "line_number": 1}],
            {}, "創世記", "34", homonyms=homonyms,
        )
        self.assertEqual(1, len(plan["D_new_candidate"]))
        self.assertEqual("homonym", plan["D_new_candidate"][0]["match_type"])

    def test_book_and_chapter_are_both_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "entry.md"
            path.write_text("### 另一卷 第28章\n", encoding="utf-8")
            self.assertFalse(has_book_chapter_data("entry.md", "創世記", "28", root))
            path.write_text("### 創世記 第28章\n", encoding="utf-8")
            self.assertTrue(has_book_chapter_data("entry.md", "創世記", "28", root))


class UpdateTests(unittest.TestCase):
    def test_internal_source_lines_are_forbidden_but_heading_is_allowed(self):
        self.assertIsNone(INTERNAL_SOURCE_LINE_RE.search("### 觸發來源\n"))
        self.assertIsNotNone(INTERNAL_SOURCE_LINE_RE.search("- 觸發來源：CT\n"))
        self.assertIsNotNone(INTERNAL_SOURCE_LINE_RE.search("- 來源檔案：raw_data/a.txt\n"))
        self.assertIsNotNone(INTERNAL_SOURCE_LINE_RE.search("- raw_data：a.txt\n"))

    def test_update_requires_content(self):
        missing = validate_update({
            "title": "天梯", "path": "link_folder/神學/天梯.md",
            "summary": "", "relation": "", "sources": [], "source_files": [],
        })
        self.assertIn("summary", missing)
        self.assertNotIn("sources", missing)

    def test_marker_contains_book_and_chapter(self):
        block = render_block("創世記", 28, {
            "summary": "重點", "relation": "關聯",
            "sources": ["CT"], "source_files": ["raw_data/example.txt"],
        })
        self.assertIn("<!-- accumulation:創世記:28:start -->", block)
        self.assertNotIn("觸發來源", block)
        self.assertNotIn("來源檔案", block)
        self.assertNotIn("raw_data/example.txt", block)
        self.assertNotIn("### 創世記", block)

    def test_apply_inserts_inside_book_group_in_chapter_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entry_path = root / "link_folder" / "人物" / "測試.md"
            entry_path.parent.mkdir(parents=True)
            entry_path.write_text(
                "# 測試\n\n## 定義\n\n內容\n\n## 按書卷累積\n\n### 創世記\n\n"
                "<!-- accumulation:創世記:2:start -->\n#### 第2章\n"
                "- 本章重點：舊資料\n- 來源：CT\n"
                "<!-- accumulation:創世記:2:end -->\n\n"
                "## 主題發展\n\n## 相關條目\n\n## 來源依據\n",
                encoding="utf-8",
            )
            manifest = root / "updates.yaml"
            manifest.write_text(yaml.safe_dump({
                "book": "創世記",
                "chapter": 1,
                "updates": [{
                    "title": "測試",
                    "path": "link_folder/人物/測試.md",
                    "summary": "新資料",
                    "relation": "測試關聯",
                    "sources": ["BH"],
                    "source_files": ["raw_data/example.txt"],
                }],
            }, allow_unicode=True), encoding="utf-8")
            with patch("link_updates.ROOT", root):
                self.assertEqual(1, apply_updates(manifest))
                self.assertEqual(0, apply_updates(manifest))
            rendered = entry_path.read_text(encoding="utf-8")
            self.assertLess(rendered.index("#### 第1章"), rendered.index("#### 第2章"))
            accumulation = rendered[
                rendered.index("## 按書卷累積"):rendered.index("## 主題發展")
            ]
            self.assertIn("#### 第1章", accumulation)


class FormatNormalizationTests(unittest.TestCase):
    def test_chapter_and_entry_use_different_scheme_templates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chapter = root / "創世記" / "第8章.md"
            chapter.parent.mkdir()
            chapter.write_text(
                "# 創世記 第八章\n\n## 經文\n\n1 起初\n\n---\n\n## 補充資料\n\n內容\n",
                encoding="utf-8",
            )
            rendered_chapter = normalize_chapter(chapter)
            self.assertIn("# 創世記 第8章", rendered_chapter)
            self.assertIn("## 本章知識節點", rendered_chapter)
            self.assertIn("## 本章整理", rendered_chapter)
            self.assertNotIn("## 定義", rendered_chapter)

            entry = root / "link_folder" / "神學" / "測試.md"
            entry.parent.mkdir(parents=True)
            entry.write_text(
                "---\ntype: 神學\nstatus: formal\nsource_scope: collected_only\n---\n\n"
                "# 測試\n\n## 定義／基本資料\n\n定義內容\n\n## 來源依據\n\n- CT\n",
                encoding="utf-8",
            )
            rendered_entry = normalize_entry(entry)
            self.assertIn("## 定義", rendered_entry)
            self.assertNotIn("## 核心摘要", rendered_entry)
            self.assertIn("## 按書卷累積", rendered_entry)
            self.assertNotIn("## 本章整理", rendered_entry)

    def test_entry_merges_distinct_summary_and_orders_chapters(self):
        with tempfile.TemporaryDirectory() as tmp:
            entry = Path(tmp) / "link_folder" / "人物" / "測試.md"
            entry.parent.mkdir(parents=True)
            entry.write_text(
                "---\ntype: 人物\nstatus: formal\nsource_scope: collected_only\n---\n\n"
                "# 測試\n\n## 定義\n\n定義內容\n\n## 核心摘要\n\n補充摘要\n\n"
                "## 按書卷累積\n\n### 主題分析\n\n分析內容\n\n"
                "### 創世記 第2章\n\n- 來源：CT\n\n"
                "## 主題發展\n\n既有發展\n\n## 相關條目\n\n"
                "### 創世記 第1章\n\n- 來源：BH\n\n## 來源依據\n\n- CT\n",
                encoding="utf-8",
            )
            rendered = normalize_entry(entry)
            self.assertIn("定義內容\n\n補充摘要", rendered)
            self.assertLess(rendered.index("#### 第1章"), rendered.index("#### 第2章"))
            accumulation = rendered[
                rendered.index("## 按書卷累積"):rendered.index("## 主題發展")
            ]
            self.assertIn("#### 第1章", accumulation)
            self.assertEqual(1, rendered.count("### 創世記\n"))
            self.assertNotIn("### 主題分析", accumulation)
            development = rendered[
                rendered.index("## 主題發展"):rendered.index("## 相關條目")
            ]
            self.assertIn("### 主題分析", development)


class HomonymValidationTests(unittest.TestCase):
    def test_bare_homonym_link_is_detected_but_qualified_target_is_allowed(self):
        homonyms = {
            "示劍": [
                {"target": "示劍（城）", "type": "地點"},
                {"target": "示劍（哈抹之子）", "type": "人物"},
            ]
        }
        text = (
            "[[示劍]]\n"
            "[[示劍|原文]]\n"
            "[[示劍（城）|示劍]]\n"
            "[[示劍（哈抹之子）#生平|示劍]]\n"
        )
        self.assertEqual(
            [("示劍", 1), ("示劍", 2)],
            ambiguous_wikilinks(text, homonyms),
        )


if __name__ == "__main__":
    unittest.main()
