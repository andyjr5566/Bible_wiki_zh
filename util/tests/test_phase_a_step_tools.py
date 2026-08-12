import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


UTIL_DIR = Path(__file__).resolve().parents[1]
if str(UTIL_DIR) not in sys.path:
    sys.path.insert(0, str(UTIL_DIR))

import audit_original_language
import backfill_step_sources
import build_source_manifest
import extract_stepbible


def formal_step_text(book="創世記", chapter=1):
    reference = extract_stepbible.parse_reference(f"{book} {chapter}")
    word = extract_stepbible.WordEntry(
        reference=f"{reference.code}.{chapter}.1",
        position=1,
        word="בָּרָא",
        transliteration="bārāʾ",
        gloss="created",
        strongs_raw="H1254A H9001",
        strongs=["H1254A", "H9001"],
        main_strong="H1254A",
        morphology_raw="V-Qal-3ms",
        morphology="Verb Qal perfect 3ms masculine singular",
        lexicon_short="create, shape",
    )
    return extract_stepbible.render_markdown(
        reference, {1: [word]}, include_full_definitions=False
    )


def prepare_root(root, book="創世記", chapters=(1,)):
    book_dir = root / ("01 創世記" if book == "創世記" else "02 出埃及記")
    scripture_dir = root / "raw_scripture" / book
    raw_dir = root / "raw_data"
    link_dir = root / "link_folder" / "原文"
    index_dir = root / "util" / "output"
    for directory in (book_dir, scripture_dir, raw_dir, link_dir, index_dir):
        directory.mkdir(parents=True, exist_ok=True)
    for chapter in chapters:
        (book_dir / f"第{chapter}章.md").write_text(
            f"# {book}第{chapter}章\n章節內容 sentinel\n", encoding="utf-8"
        )
        (scripture_dir / f"第{chapter}章.txt").write_text("1 經文\n", encoding="utf-8")
        chapter_dir = book_dir / ".tmp" / f"第{chapter}章"
        chapter_dir.mkdir(parents=True, exist_ok=True)
        rows = []
        for label, kind, url, filename in build_source_manifest.source_specs(book, chapter)[:-1]:
            rel = f"raw_data/{filename}"
            (root / rel).write_bytes(f"{label} sentinel {chapter}\n".encode("utf-8"))
            rows.append(f"| {label} | {kind} | {url} | {rel} | OK |")
        manifest = (
            f"# {book} 第{chapter}章 source manifest\n\n"
            "| 來源 | 類型 | URL | raw_data 檔案 | 狀態 |\n"
            "|---|---|---|---|---|\n"
            + "\n".join(reversed(rows)) + "\n"
        )
        (chapter_dir / "source_manifest.md").write_text(manifest, encoding="utf-8")
        (chapter_dir / "read_log.md").write_bytes(f"commentary receipt {chapter}\n".encode("utf-8"))
    (index_dir / "link_index.json").write_text("{}\n", encoding="utf-8")
    return book_dir


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ManifestPreservationTests(unittest.TestCase):
    def test_only_step_row_is_added_to_legacy_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            book_dir = prepare_root(root)
            path = book_dir / ".tmp" / "第1章" / "source_manifest.md"
            original = path.read_text(encoding="utf-8").replace("\n", "\r\n")
            updated = build_source_manifest.preserve_manifest_with_step(
                "創世記", 1, original, root=root, step_exists=True
            )
            step_rows = [line for line in updated.splitlines() if "STEP Bible" in line]
            self.assertEqual(1, len(step_rows))
            remaining = "\r\n".join(
                line for line in updated.splitlines() if "STEP Bible" not in line
            ) + "\r\n"
            self.assertEqual(original, remaining)


class BackfillTests(unittest.TestCase):
    def test_dry_run_extracts_and_validates_without_writing_production_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            book_dir = prepare_root(root)
            manifest = book_dir / ".tmp" / "第1章" / "source_manifest.md"
            receipt = manifest.parent / "step_source_receipt.json"
            before_manifest = manifest.read_bytes()
            chapter_before = (book_dir / "第1章.md").read_bytes()
            report = backfill_step_sources.run_backfill(
                "創世記", chapters="1", root=root, dry_run=True,
                extractor=lambda _book, _chapter: formal_step_text(),
                write_report=False,
            )
            target = root / "raw_data" / "stepbible_genesis_1.txt"
            self.assertFalse(target.exists())
            self.assertFalse(receipt.exists())
            self.assertEqual(before_manifest, manifest.read_bytes())
            self.assertEqual(chapter_before, (book_dir / "第1章.md").read_bytes())
            self.assertEqual(1, report["would_generate"])
            self.assertEqual(1, report["step_validation_pass"])
            self.assertTrue(report["safety"]["byte_identical"])
            self.assertFalse(list((root / "raw_data").glob("*.part")))

    def test_write_then_idempotent_reuse_preserves_source_manifest_and_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            book_dir = prepare_root(root)
            report = backfill_step_sources.run_backfill(
                "創世記", chapters=[1], root=root,
                extractor=lambda _book, _chapter: formal_step_text(),
                write_report=False,
            )
            target = root / "raw_data" / "stepbible_genesis_1.txt"
            manifest = book_dir / ".tmp" / "第1章" / "source_manifest.md"
            receipt = manifest.parent / "step_source_receipt.json"
            self.assertEqual(1, report["generated"])
            self.assertEqual(1, manifest.read_text(encoding="utf-8").count("STEP Bible"))
            self.assertTrue(receipt.is_file())
            before = tuple(digest(path) for path in (target, manifest, receipt))

            def forbidden_extractor(_book, _chapter):
                raise AssertionError("valid existing STEP must be reused")

            rerun = backfill_step_sources.run_backfill(
                "創世記", chapters="1", root=root,
                extractor=forbidden_extractor, write_report=False,
            )
            self.assertEqual(1, rerun["reused"])
            self.assertEqual(before, tuple(digest(path) for path in (target, manifest, receipt)))
            self.assertEqual("reused", rerun["chapters"][0]["manifest"])
            self.assertEqual("reused", rerun["chapters"][0]["receipt"])

    def test_damaged_existing_step_fails_closed_without_manifest_or_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            book_dir = prepare_root(root)
            target = root / "raw_data" / "stepbible_genesis_1.txt"
            target.write_text("damaged\n", encoding="utf-8")
            manifest = book_dir / ".tmp" / "第1章" / "source_manifest.md"
            before = manifest.read_bytes()
            report = backfill_step_sources.run_backfill(
                "創世記", chapters="1", root=root,
                extractor=lambda *_args: (_ for _ in ()).throw(AssertionError("must not overwrite")),
                write_report=False,
            )
            self.assertEqual(1, report["failed"])
            self.assertEqual(before, manifest.read_bytes())
            self.assertNotIn("STEP Bible", manifest.read_text(encoding="utf-8"))
            self.assertFalse((manifest.parent / "step_source_receipt.json").exists())

    def test_missing_extraction_failure_and_whole_book_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prepare_root(root, chapters=(1, 2))
            report = backfill_step_sources.run_backfill(
                "創世記", root=root,
                extractor=lambda _book, chapter: formal_step_text(chapter=chapter),
                write_report=False,
            )
            self.assertEqual([1, 2], report["chapters_selected"])
            self.assertEqual(2, report["generated"])
            self.assertEqual([1, 3, 5, 6, 7, 8], backfill_step_sources.parse_chapter_spec("1,3,5-8"))

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            book_dir = prepare_root(root)
            manifest = book_dir / ".tmp" / "第1章" / "source_manifest.md"
            report = backfill_step_sources.run_backfill(
                "創世記", root=root,
                extractor=lambda *_args: (_ for _ in ()).throw(FileNotFoundError("missing STEP cache")),
                write_report=False,
            )
            self.assertEqual(1, report["failed"])
            self.assertNotIn("STEP Bible", manifest.read_text(encoding="utf-8"))


class OriginalLanguageAuditTests(unittest.TestCase):
    def test_deterministic_classifications_reports_and_safety(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            book_dir = prepare_root(root)
            backfill = backfill_step_sources.run_backfill(
                "創世記", chapters="1", root=root,
                extractor=lambda *_args: formal_step_text(), write_report=False,
            )
            self.assertEqual(0, backfill["failed"])

            entry = root / "link_folder" / "原文" / "測試原文.md"
            entry.write_text(
                "---\ntype: 原文\nstatus: formal\n---\n\n"
                "# 測試原文（bārāʾ）\n\n## 定義\n"
                "希伯來文 בָּרָא 對應 H1254A。\n"
                "<!-- accumulation:創世記:1:start -->\n"
                "未標音形式 ברא 也在本章。\n"
                "<!-- accumulation:創世記:1:end -->\n",
                encoding="utf-8",
            )
            index_path = root / "util" / "output" / "link_index.json"
            index_path.write_text(json.dumps({
                "測試原文": {
                    "path": "link_folder/原文/測試原文.md", "type": "原文",
                    "secondary_types": [], "title": "測試原文", "status": "formal", "aliases": [],
                }
            }, ensure_ascii=False), encoding="utf-8")
            chapter = book_dir / "第1章.md"
            chapter.write_text(
                "# 創世記第1章\n[[測試原文]]\n"
                "希伯來文 בָּרָא。\n希伯來文 ברא。\n希伯來文 בָּד 對應 H1254A。\n"
                "原文 *bārāʾ*。\n原文 *bara*。\n原文 *baraz*。\n"
                "Strong H1254A。\nStrong H1254。\n希伯來文 בָּרָא 對應 H7777。\nStrong H9001。\n"
                "原文 *bārāʾ* 是 Qal perfect 3ms。\n"
                "原文 *bārāʾ* 是 Piel imperfect 3mp。\n"
                "原文 *bara* 表示從無到有。\n"
                "原文 *bara* 意為創造。\n",
                encoding="utf-8",
            )
            protected = {
                path: path.read_bytes()
                for path in [chapter, entry, *sorted((root / "raw_data").glob("*.txt"))]
            }
            report = audit_original_language.run_audit(
                "創世記", chapters="1", root=root, write_reports=True
            )
            self.assertTrue(report["safety"]["byte_identical"])
            self.assertEqual(1, report["chapter_files_scanned"])
            self.assertEqual(1, report["owned_link_files_scanned"])
            for path, content in protected.items():
                self.assertEqual(content, path.read_bytes())
            self.assertTrue((root / "reports" / "step_audit" / "genesis_findings.json").is_file())
            self.assertTrue((root / "reports" / "step_audit" / "genesis_summary.md").is_file())

            findings = report["findings"]
            def classifications(claim_type, claim):
                return {
                    item["classification"] for item in findings
                    if item["claim_type"] == claim_type and item["claim"] == claim
                }

            self.assertEqual({"PASS"}, classifications("hebrew", "בָּרָא"))
            self.assertEqual({"PASS"}, classifications("hebrew", "ברא"))
            self.assertEqual({"REVIEW_HIGH"}, classifications("hebrew", "בָּד"))
            self.assertEqual({"PASS"}, classifications("transliteration", "bārāʾ"))
            self.assertEqual({"REVIEW_LOW"}, classifications("transliteration", "bara"))
            self.assertEqual({"REVIEW_LOW"}, classifications("transliteration", "baraz"))
            self.assertEqual({"PASS"}, classifications("strong", "H1254A"))
            self.assertEqual({"PASS"}, classifications("strong", "H1254"))
            self.assertEqual({"REVIEW_HIGH"}, classifications("strong", "H7777"))
            self.assertEqual({"UNVERIFIABLE"}, classifications("strong", "H9001"))
            self.assertIn("PASS", classifications("morphology", "qal, perfect, 3ms"))
            self.assertIn("REVIEW_HIGH", classifications("morphology", "piel, imperfect, 3mp"))
            self.assertIn("INTERPRETIVE", {
                item["classification"] for item in findings
                if item["claim_type"] == "lexical_interpretation"
            })
            self.assertIn("UNVERIFIABLE", {
                item["classification"] for item in findings
                if item["claim_type"] == "lexical_meaning"
            })


if __name__ == "__main__":
    unittest.main()
