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


def valid_step_text(reference="Genesis 1:1"):
    ref = extract_stepbible.parse_reference(reference)
    verse = ref.verse_start or 1
    strong = "H1254A" if ref.testament == "OT" else "G3056A"
    original = "בָּרָא" if ref.testament == "OT" else "λόγος"
    word = extract_stepbible.WordEntry(
        reference=f"{ref.code}.{ref.chapter}.{verse}",
        position=1,
        word=original,
        transliteration="bara" if ref.testament == "OT" else "logos",
        gloss="created" if ref.testament == "OT" else "word",
        strongs_raw=strong,
        strongs=[strong],
        main_strong=strong,
        morphology_raw="V-Qal-3ms" if ref.testament == "OT" else "N-NSM",
        morphology="V-Qal-3ms" if ref.testament == "OT" else "N-NSM",
        lexicon_short="create" if ref.testament == "OT" else "word; message",
    )
    return extract_stepbible.render_markdown(ref, {verse: [word]}, False)


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
    def _fixture(self, root, *, omit_step_log=True, malformed_step=False, tail_quote=True):
        chapter = root / "01 創世記" / ".tmp" / "第1章"
        chapter.mkdir(parents=True)
        (root / "raw_data").mkdir()
        rows = []
        logs = ["# 來源讀取回執：創世記 第1章", ""]
        labels = ("CT", "GT", "KC", "BH", "STEP Bible")
        for index, label in enumerate(labels, 1):
            rel = f"raw_data/source_{index}.txt"
            raw_lines = [f"{label} 第{line}行逐字內容足夠長度" for line in range(1, 10)]
            if label == "STEP Bible":
                body = "不是合法 STEP" if malformed_step else valid_step_text()
                (root / rel).write_text(body, encoding="utf-8")
            else:
                (root / rel).write_text("\n".join(raw_lines) + "\n", encoding="utf-8")
            rows.append((label, "原文資料" if label == "STEP Bible" else "研經註解",
                         f"https://example.test/{index}", rel, "OK"))
            if not (omit_step_log and label == "STEP Bible"):
                logs.extend([
                    f"## {rel}", "- 行數：9",
                    f"- 引句：{raw_lines[0]}", f"- 引句：{raw_lines[3]}",
                    f"- 引句：{raw_lines[8 if tail_quote else 4]}", "",
                ])
        (chapter / "source_manifest.md").write_text(manifest_text(rows), encoding="utf-8")
        (chapter / "read_log.md").write_text("\n".join(logs), encoding="utf-8")

    def test_step_passes_machine_gate_without_human_quote_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._fixture(root)
            self.assertEqual([], check_source_read.check("創世記", 1, strict_lines=True, root=root))
            receipt = root / "01 創世記" / ".tmp" / "第1章" / "step_source_receipt.json"
            self.assertEqual("PASS", __import__("json").loads(
                receipt.read_text(encoding="utf-8")
            )["sources"][0]["status"])

    def test_malformed_step_fails_even_without_human_quote_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._fixture(root, malformed_step=True)
            problems = check_source_read.check("創世記", 1, root=root)
            self.assertTrue(any("STEP machine validation FAIL" in item for item in problems), problems)

    def test_commentary_without_tail_quote_still_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._fixture(root, tail_quote=False)
            problems = check_source_read.check("創世記", 1, root=root)
            self.assertTrue(any("後三分之一" in item for item in problems), problems)


class ManualPromptIntegrationTests(unittest.TestCase):
    def test_manual_prompts_reference_commentary_and_embed_only_step_projection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "raw_scripture" / "創世記").mkdir(parents=True)
            (root / "raw_scripture" / "創世記" / "第1章.txt").write_text(
                "起初，神創造天地。\n", encoding="utf-8"
            )
            (root / "raw_data").mkdir()
            step = valid_step_text().replace(
                "> 本檔是「原文證據層」資料，不是 Commentary。",
                "> 本檔是「原文證據層」資料，不是 Commentary。\nSTEP_SENTINEL_789",
            )
            (root / "raw_data" / "stepbible_genesis_1_1.txt").write_text(step, encoding="utf-8")
            (root / "raw_data" / "ct.txt").write_text("CT_SENTINEL_123 commentary body", encoding="utf-8")
            (root / "raw_data" / "gt.txt").write_text("GT_SENTINEL_456 commentary body", encoding="utf-8")
            (root / "link_folder" / "原文").mkdir(parents=True)
            chapter = root / "01 創世記" / ".tmp" / "第1章"
            chapter.mkdir(parents=True)
            (chapter / "source_manifest.md").write_text(manifest_text([
                ("ccbiblestudy CT", "逐節註解", "https://example.test/ct",
                 "raw_data/ct.txt", "OK"),
                ("ccbiblestudy GT", "拾穗", "https://example.test/gt",
                 "raw_data/gt.txt", "OK"),
                ("STEP Bible", "原文資料", "https://github.com/STEPBible/STEPBible-Data",
                 "raw_data/stepbible_genesis_1_1.txt", "OK")
            ]), encoding="utf-8")
            (chapter / "manual").mkdir()
            (chapter / "manual" / "sources.md").write_text(
                source_excerpts.render_source_reading_plan(
                    chapter / "source_manifest.md", root
                ), encoding="utf-8"
            )
            ctx = run_chapter.ChapterContext("創世記", 1, root=root, index={}, homonyms={})
            plan = {
                "A_use_directly": [], "B_needs_update": [],
                "C_new_formal": [{
                    "name": "創造（bara）", "suggested_type": "神學", "evidence": "1節；H1254",
                    "surfaces": [{"phrase": "創造", "verses": [1]}],
                }],
                "D_draft": [],
            }
            manual = chapter / "manual"
            ctx.runner = run_chapter_manual.PromptCapture(manual, "entry_batch", ctx=ctx)
            run_chapter.entry_content_step(
                ctx, plan, batch_size=10,
                source_context_policy=source_excerpts.MANUAL_PROJECTED,
            )
            ctx.runner = run_chapter_manual.PromptCapture(manual, "chapter_content", ctx=ctx)
            run_chapter.chapter_content_step(
                ctx, plan, source_context_policy=source_excerpts.MANUAL_PROJECTED
            )

            entry_prompt = (manual / "entry_batch_1.prompt.md").read_text(encoding="utf-8")
            chapter_prompt = (manual / "chapter_content.prompt.md").read_text(encoding="utf-8")
            for prompt in (entry_prompt, chapter_prompt):
                self.assertIn("STEP Bible", prompt)
                self.assertIn("בָּרָא", prompt)
                self.assertIn("不是第五套 commentary", prompt)
                self.assertIn("Lexicon 是可能義域", prompt)
                self.assertIn("morphology", prompt)
                self.assertIn("共識票", prompt)
                self.assertIn("正面分層", prompt)
                self.assertIn("部分註釋如何從整段或其他經文進一步理解", prompt)
                self.assertNotIn("CT_SENTINEL_123", prompt)
                self.assertNotIn("GT_SENTINEL_456", prompt)
                self.assertNotIn("STEP_SENTINEL_789", prompt)
            sources_plan = (manual / "sources.md").read_text(encoding="utf-8")
            self.assertIn("raw_data/ct.txt", sources_plan)
            self.assertIn("raw_data/gt.txt", sources_plan)
            self.assertIn("raw_data/stepbible_genesis_1_1.txt", sources_plan)

    def test_m3_unparseable_evidence_fails_small_without_dumping_full_chapter(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def make_word(ref, pos, w, t, s, m, gloss, lexicon):
                return extract_stepbible.WordEntry(
                    reference=ref, position=pos, word=w, transliteration=t,
                    gloss=gloss, strongs_raw=s, strongs=[s], main_strong=s,
                    morphology_raw=m, morphology=m, lexicon_short=lexicon,
                )
            def write_step(path, title, verses):
                ref = extract_stepbible.parse_reference(title)
                path.write_text(extract_stepbible.render_markdown(ref, verses, False), encoding="utf-8")

            (root / "raw_scripture" / "創世記").mkdir(parents=True)
            (root / "raw_scripture" / "創世記" / "第1章.txt").write_text(
                "起初，神創造天地。\n地是空虛混沌。\n", encoding="utf-8"
            )
            (root / "raw_data").mkdir()
            verses = {
                1: [
                    make_word("Gen.1.1", 1, "בָּרָא", "bara", "H1254A", "V-Qal", gloss="created", lexicon="create"),
                ],
                2: [
                    make_word("Gen.1.2", 1, "הָיְתָה", "haytah", "H1961", "V-Qal", gloss="was", lexicon="be"),
                ],
            }
            write_step(root / "raw_data" / "stepbible_genesis_1.txt", "Genesis 1", verses)
            chapter = root / "01 創世記" / ".tmp" / "第1章"
            chapter.mkdir(parents=True)
            (chapter / "source_manifest.md").write_text(
                "| 來源 | 類型 | URL | raw_data 檔案 | 狀態 |\n"
                "|---|---|---|---|---|\n"
                "| STEP Bible | 原文資料 | https://x/step | raw_data/stepbible_genesis_1.txt | OK |\n",
                encoding="utf-8",
            )
            (chapter / "manual").mkdir()
            ctx = run_chapter.ChapterContext("創世記", 1, root=root, index={}, homonyms={})
            plan = {
                "A_use_directly": [], "B_needs_update": [],
                "C_new_formal": [{
                    "name": "原文候選", "suggested_type": "原文", "evidence": "純語義描述無節號",
                    "surfaces": [],
                }],
                "D_draft": [],
            }
            manual = chapter / "manual"
            ctx.runner = run_chapter_manual.PromptCapture(manual, "entry_batch", ctx=ctx)
            run_chapter.entry_content_step(
                ctx, plan, batch_size=10,
                source_context_policy=source_excerpts.MANUAL_PROJECTED,
            )
            entry_prompt = (manual / "entry_batch_1.prompt.md").read_text(encoding="utf-8")
            self.assertIn("mode: unresolved", entry_prompt)
            self.assertIn("candidate count: 0", entry_prompt)
            self.assertNotIn("H1254A", entry_prompt)
            self.assertTrue(any("未自動注入整章 STEP" in item or "精確查詢" in item for item in ctx.manual_review))


if __name__ == "__main__":
    unittest.main()
