import tempfile
import unittest
import sys
from pathlib import Path

UTIL_DIR = Path(__file__).resolve().parents[1]
if str(UTIL_DIR) not in sys.path:
    sys.path.insert(0, str(UTIL_DIR))

from build_link_index import make_index
from resolve_link_candidates import (
    find_in_index,
    has_book_chapter_data,
    resolve,
)
from link_updates import render_block, validate_update


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

    def test_book_and_chapter_are_both_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "entry.md"
            path.write_text("### 另一卷 第28章\n", encoding="utf-8")
            self.assertFalse(has_book_chapter_data("entry.md", "創世記", "28", root))
            path.write_text("### 創世記 第28章\n", encoding="utf-8")
            self.assertTrue(has_book_chapter_data("entry.md", "創世記", "28", root))


class UpdateTests(unittest.TestCase):
    def test_update_requires_sources_and_content(self):
        missing = validate_update({
            "title": "天梯", "path": "link_folder/神學/天梯.md",
            "summary": "", "relation": "", "sources": [], "source_files": [],
        })
        self.assertIn("summary", missing)
        self.assertIn("sources", missing)

    def test_marker_contains_book_and_chapter(self):
        block = render_block("創世記", 28, {
            "summary": "重點", "relation": "關聯",
            "sources": ["CT"], "source_files": ["raw_data/example.txt"],
        })
        self.assertIn("<!-- accumulation:創世記:28:start -->", block)
        self.assertIn("觸發來源：CT", block)


if __name__ == "__main__":
    unittest.main()
