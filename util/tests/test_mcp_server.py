import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from util.mcp import server


class MCPReadBoundaryTests(unittest.TestCase):
    def _index(self, root):
        entry = {
            "title": "測試條目",
            "path": "link_folder/神學/測試條目.md",
            "type": "神學",
            "secondary_types": [],
            "status": "formal",
            "aliases": ["測試別名"],
        }
        index = {"測試條目": entry, "測試別名": {"alias_of": "測試條目"}}
        path = root / "util" / "output" / "link_index.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
        return entry

    def test_reads_only_indexed_link_folder_entry(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            entry = self._index(root)
            path = root / entry["path"]
            path.parent.mkdir(parents=True)
            path.write_text("# 測試條目\n\n內容", encoding="utf-8")
            with patch.object(server, "ROOT_DIR", root):
                result = server.read_wiki_entry("測試別名")
            self.assertTrue(result["success"])
            self.assertEqual("測試條目", result["title"])
            self.assertEqual("# 測試條目\n\n內容", result["content"])

    def test_rejects_parent_traversal_instead_of_reading_it(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "vault"
            root.mkdir()
            self._index(root)
            outside = root.parent / "secret.md"
            outside.write_text("不得讀取", encoding="utf-8")
            with patch.object(server, "ROOT_DIR", root):
                result = server.read_wiki_entry("../secret.md")
            self.assertFalse(result["success"])
            self.assertNotIn("content", result)

    def test_linter_treats_path_like_input_as_text(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("[[不該讀取]]", encoding="utf-8")
            with patch.object(server, "ROOT_DIR", root):
                result = server.lint_chapter_content("README.md")
            self.assertTrue(result["success"])
            self.assertTrue(result["passed"])

    def test_searches_aliases_from_canonical_index(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            entry = self._index(root)
            path = root / entry["path"]
            path.parent.mkdir(parents=True)
            path.write_text("# 測試條目", encoding="utf-8")
            with patch.object(server, "ROOT_DIR", root):
                result = server.search_wiki_entries("測試別名")
            self.assertTrue(result["success"])
            self.assertEqual("exact_alias", result["results"][0]["matched_by"])


class ManualCompletionTests(unittest.TestCase):
    def test_missing_m3_and_m6_are_incomplete(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tmp = root / "01 創世記" / ".tmp" / "第1章"
            tmp.mkdir(parents=True)
            (tmp / "link_plan.yaml").write_text(
                "C_new_formal:\n  - name: 新條目\n", encoding="utf-8"
            )
            with patch.object(server, "ROOT_DIR", root):
                missing = server._manual_completion("創世記", 1)
            self.assertTrue(any("C 類條目" in item for item in missing))
            self.assertTrue(any("chapter_content.yaml" in item for item in missing))


class MCPUpdateTokenTests(unittest.TestCase):
    def test_apply_rejects_a_preview_token_when_target_changed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            entry = root / "link_folder" / "主題" / "測試.md"
            entry.parent.mkdir(parents=True)
            entry.write_text(
                "# 測試\n\n## 按書卷累積\n\n## 主題發展\n", encoding="utf-8"
            )
            tmp = root / "01 創世記" / ".tmp" / "第1章"
            tmp.mkdir(parents=True)
            (tmp / "link_updates.yaml").write_text(
                "book: 創世記\nchapter: 1\nupdates:\n"
                "  - title: 測試\n"
                "    path: link_folder/主題/測試.md\n"
                "    summary: 本章重點\n"
                "    relation: 本章關聯\n",
                encoding="utf-8",
            )
            with patch.object(server, "ROOT_DIR", root), patch.object(server.link_updates, "ROOT", root):
                preview = server.preview_chapter_link_updates("創世記", 1)
                self.assertTrue(preview["success"])
                entry.write_text(entry.read_text(encoding="utf-8") + "\n外部修改\n", encoding="utf-8")
                result = server.apply_chapter_link_updates("創世記", 1, preview["preview_token"])
            self.assertFalse(result["success"])
            self.assertIn("preview_token", result["error"])


if __name__ == "__main__":
    unittest.main()
