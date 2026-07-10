import sys
import tempfile
import unittest
from pathlib import Path

UTIL_DIR = Path(__file__).resolve().parents[1]
if str(UTIL_DIR) not in sys.path:
    sys.path.insert(0, str(UTIL_DIR))

import yaml

import run_chapter

RAW = ["要做施恩座安在法櫃上。", "用金子包裹。"]
ENTRY_NAME = "施恩座（kapporet 測試）"

ENTRY_PAYLOAD = f"""\
name: {ENTRY_NAME}
type: 原文
secondary_types: []
aliases: []
status: formal
definition: 希伯來文 kapporet，法櫃的蓋子，神與人相會之處。
accumulations:
  - book: 出埃及記
    chapter: 26
    summary: 神指示製作施恩座。
    relation: 施恩座是神與摩西相會之處。
related_entries: []
sources:
  - 出埃及記26:1
"""

VERSE_LINKS_PAYLOAD = f"""\
book: 出埃及記
chapter: 26
links:
  - verse: 1
    phrase: 施恩座
    target: {ENTRY_NAME}
    occurrence: 1
"""

CHAPTER_CONTENT_PAYLOAD = f"""\
book: 出埃及記
chapter: 26
knowledge_nodes:
  神學:
    - {ENTRY_NAME}
organization: |
  **重點摘要**
  - 施恩座與會幕
"""


def fake_runner(prompt):
    """依 prompt 內容回傳對應步驟的 payload（模擬 claude -p）。"""
    if "entry_content payload" in prompt:
        return ENTRY_PAYLOAD
    if "verse_links payload" in prompt:
        return VERSE_LINKS_PAYLOAD
    if "chapter_content payload" in prompt:
        return CHAPTER_CONTENT_PAYLOAD
    raise AssertionError(f"未預期的 prompt：{prompt[:60]}")


class OrchestratorTests(unittest.TestCase):
    def _make_vault(self, tmp):
        root = Path(tmp)
        (root / "raw_scripture" / "出埃及記").mkdir(parents=True)
        (root / "raw_scripture" / "出埃及記" / "第26章.txt").write_text(
            "\n".join(RAW) + "\n", encoding="utf-8"
        )
        for group in ("原文", "神學"):
            (root / "link_folder" / group).mkdir(parents=True)
        tmp_dir = root / "02 出埃及記" / ".tmp" / "第26章"
        tmp_dir.mkdir(parents=True)
        (tmp_dir / "link_candidates.yaml").write_text(
            yaml.safe_dump({
                "book": "出埃及記", "chapter": 26,
                "candidates": [{"name": ENTRY_NAME, "type": "原文"}],
            }, allow_unicode=True),
            encoding="utf-8",
        )
        return root

    def test_end_to_end_produces_validated_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_vault(tmp)
            result = run_chapter.run_chapter(
                "出埃及記", 26, root=root, runner=fake_runner, index={}, homonyms={},
            )
            self.assertEqual([], result["errors"])
            self.assertEqual([], result["manual_review"])
            self.assertEqual(1, result["entry_count"])
            # 條目與章節主檔都由程式渲染寫出
            entry = root / "link_folder" / "原文" / f"{ENTRY_NAME}.md"
            chapter = root / "02 出埃及記" / "第26章.md"
            self.assertTrue(entry.exists())
            self.assertTrue(chapter.exists())
            # 章節經文只連指定 occurrence，alias 格式由程式產生
            self.assertIn(f"[[{ENTRY_NAME}|施恩座]]", chapter.read_text(encoding="utf-8"))

    def test_resume_skips_model_on_second_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_vault(tmp)
            run_chapter.run_chapter(
                "出埃及記", 26, root=root, runner=fake_runner, index={}, homonyms={},
            )

            def exploding_runner(prompt):
                raise AssertionError("resume 應該直接沿用 .tmp payload，不得再呼叫模型")

            result = run_chapter.run_chapter(
                "出埃及記", 26, root=root, runner=exploding_runner, index={}, homonyms={},
            )
            self.assertEqual([], result["errors"])

    def test_invalid_model_output_is_routed_to_manual_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_vault(tmp)

            def bad_entry_runner(prompt):
                if "entry_content payload" in prompt:
                    return "name: 缺很多必填欄位\ntype: 原文\nstatus: formal\n"
                return fake_runner(prompt)

            result = run_chapter.run_chapter(
                "出埃及記", 26, root=root, runner=bad_entry_runner, index={}, homonyms={},
            )
            self.assertEqual(1, len(result["manual_review"]))
            self.assertIn("entry_content", result["manual_review"][0])
            # 條目未通過驗證，不得產生 markdown
            self.assertFalse((root / "link_folder" / "原文" / f"{ENTRY_NAME}.md").exists())


if __name__ == "__main__":
    unittest.main()
