import sys
import tempfile
import unittest
from pathlib import Path


UTIL_DIR = Path(__file__).resolve().parents[1]
if str(UTIL_DIR) not in sys.path:
    sys.path.insert(0, str(UTIL_DIR))

import build_source_manifest
import check_source_read
import extract_stepbible
import run_chapter
import run_chapter_manual
import source_excerpts


def manifest_text(rows):
    lines = [
        "| 來源 | 類型 | URL | raw_data 檔案 | 狀態 |",
        "|------|------|-----|---------------|------|",
    ]
    lines.extend(f"| {label} | {kind} | {url} | {path} | {status} |"
                 for label, kind, url, path, status in rows)
    return "\n".join(lines) + "\n"


class ManifestIntegrationTests(unittest.TestCase):
    def test_builder_emits_four_commentaries_plus_step_with_one_filename_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rows = build_source_manifest.source_rows("創世記", 1, root=root)
            self.assertEqual(5, len(rows))
            self.assertEqual("STEP Bible", rows[-1][0])
            self.assertEqual("原文資料", rows[-1][1])
            self.assertEqual(
                f"raw_data/{extract_stepbible.stepbible_filename('創世記', 1)}",
                rows[-1][3],
            )
            rendered = build_source_manifest.render_manifest("創世記", 1, root=root)
            self.assertIn("缺檔（需 crawl_bible_text.py）", rendered)
            self.assertIn("缺檔（需 extract_stepbible.py）", rendered)

            (root / "raw_data").mkdir()
            for _label, _kind, _url, rel, _exists in rows:
                (root / rel).write_text("正式來源內容", encoding="utf-8")
            rendered = build_source_manifest.render_manifest("創世記", 1, root=root)
            self.assertEqual(5, rendered.count("| OK |"))

    def test_generic_loader_returns_all_five_ok_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "raw_data").mkdir()
            rows = []
            for index, label in enumerate(("CT", "GT", "KC", "BH", "STEP Bible"), 1):
                rel = f"raw_data/source_{index}.txt"
                (root / rel).write_text(f"{label} 內容", encoding="utf-8")
                rows.append((label, "原文資料" if index == 5 else "研經註解",
                             f"https://example.test/{index}", rel, "OK"))
            manifest = root / "source_manifest.md"
            manifest.write_text(manifest_text(rows), encoding="utf-8")
            sources = source_excerpts.require_sources(manifest, root)
            self.assertEqual(5, len(sources))
            self.assertIn("【STEP Bible】", source_excerpts.full_source_text(sources))


class ReadReceiptIntegrationTests(unittest.TestCase):
    def _fixture(self, root, omit_step_log=False):
        chapter = root / "01 創世記" / ".tmp" / "第1章"
        chapter.mkdir(parents=True)
        (root / "raw_data").mkdir()
        rows = []
        logs = ["# 來源讀取回執：創世記 第1章", ""]
        labels = ("CT", "GT", "KC", "BH", "STEP Bible")
        for index, label in enumerate(labels, 1):
            rel = f"raw_data/source_{index}.txt"
            raw_lines = [f"{label} 第{line}行逐字內容足夠長度" for line in range(1, 10)]
            (root / rel).write_text("\n".join(raw_lines) + "\n", encoding="utf-8")
            rows.append((label, "原文資料" if label == "STEP Bible" else "研經註解",
                         f"https://example.test/{index}", rel, "OK"))
            if not (omit_step_log and label == "STEP Bible"):
                logs.extend([
                    f"## {rel}", "- 行數：9",
                    f"- 引句：{raw_lines[0]}", f"- 引句：{raw_lines[3]}",
                    f"- 引句：{raw_lines[8]}", "",
                ])
        (chapter / "source_manifest.md").write_text(manifest_text(rows), encoding="utf-8")
        (chapter / "read_log.md").write_text("\n".join(logs), encoding="utf-8")

    def test_step_is_required_by_the_same_read_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._fixture(root)
            self.assertEqual([], check_source_read.check("創世記", 1, strict_lines=True, root=root))

    def test_missing_step_receipt_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._fixture(root, omit_step_log=True)
            problems = check_source_read.check("創世記", 1, root=root)
            self.assertTrue(any("source_5.txt" in item for item in problems), problems)


class ManualPromptIntegrationTests(unittest.TestCase):
    def test_actual_manual_prompt_capture_contains_step_and_hebrew(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "raw_scripture" / "創世記").mkdir(parents=True)
            (root / "raw_scripture" / "創世記" / "第1章.txt").write_text(
                "起初，神創造天地。\n", encoding="utf-8"
            )
            (root / "raw_data").mkdir()
            (root / "raw_data" / "stepbible_genesis_1.txt").write_text(
                "# STEP Bible — Genesis 1\nבְּרֵאשִׁית | bəreʾšît | H7225 | Noun\n",
                encoding="utf-8",
            )
            (root / "link_folder" / "原文").mkdir(parents=True)
            chapter = root / "01 創世記" / ".tmp" / "第1章"
            chapter.mkdir(parents=True)
            (chapter / "source_manifest.md").write_text(manifest_text([
                ("STEP Bible", "原文資料", "https://github.com/STEPBible/STEPBible-Data",
                 "raw_data/stepbible_genesis_1.txt", "OK")
            ]), encoding="utf-8")
            ctx = run_chapter.ChapterContext("創世記", 1, root=root, index={}, homonyms={})
            plan = {
                "A_use_directly": [], "B_needs_update": [],
                "C_new_formal": [{"name": "起初（bəreʾšît）", "suggested_type": "原文"}],
                "D_draft": [],
            }
            manual = chapter / "manual"
            ctx.runner = run_chapter_manual.PromptCapture(manual, "entry_batch")
            run_chapter.entry_content_step(ctx, plan, batch_size=10)
            ctx.runner = run_chapter_manual.PromptCapture(manual, "chapter_content")
            run_chapter.chapter_content_step(ctx, plan)

            entry_prompt = (manual / "entry_batch_1.prompt.md").read_text(encoding="utf-8")
            chapter_prompt = (manual / "chapter_content.prompt.md").read_text(encoding="utf-8")
            for prompt in (entry_prompt, chapter_prompt):
                self.assertIn("STEP Bible", prompt)
                self.assertIn("בְּרֵאשִׁית", prompt)
                self.assertIn("不是第五套 commentary", prompt)
                self.assertIn("Lexicon 是可能義域", prompt)
                self.assertIn("morphology", prompt)
                self.assertIn("共識票", prompt)


if __name__ == "__main__":
    unittest.main()
