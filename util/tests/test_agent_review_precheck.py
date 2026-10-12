# -*- coding: utf-8 -*-
"""agent_review.py submit 的前置檢查：引句回查（兩種門檻）＋ link_updates dry-run。"""
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from util import agent_review, check_quote_fidelity as cqf  # noqa: E402

BOOK = "創世記"
CHAPTER = 8
GOOD = "CT 說「『鴿子』原文字義是使者」。"
BAD_LONG = "CT 說「『鴿子』原文字義是使者。」"      # 補了來源沒有的句號 → 預設門檻就抓得到
BAD_SHORT = "他說「甲乙丙丁」。"                    # 4 字短引句 → 只有 --min-chars 2 抓得到


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class PrecheckTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.tmp_dir = self.root / "01 創世記" / ".tmp" / f"第{CHAPTER}章"
        _write(self.root / "raw_data" / "ct.txt",
               "CT：『鴿子』原文字義是使者，神記念挪亞，水勢漸落。")
        _write(self.tmp_dir / "source_manifest.md",
               "| 來源 | 類型 | URL | raw_data 檔案 | 狀態 |\n"
               "|---|---|---|---|---|\n"
               "| ccbiblestudy CT | 逐節註解 | https://example.invalid/ct | raw_data/ct.txt | OK |\n")
        _write(self.root / "raw_scripture" / BOOK / f"第{CHAPTER}章.txt",
               "1. 神記念挪亞和方舟裡的一切走獸牲畜。")

    def _entry(self, definition):
        return _write(self.tmp_dir / "entry_content" / "測試.yaml",
                      f"name: 測試\ndefinition: {definition}\n")

    def _chapter_content(self, text):
        return _write(self.tmp_dir / "chapter_content.yaml", f"organization: {text}\n")

    def _link_updates(self, summary):
        return _write(self.tmp_dir / "link_updates.yaml", f"summary: {summary}\n")

    # --- 引句回查 -----------------------------------------------------------

    def test_clean_m3_passes(self):
        self._entry(GOOD)
        self.assertEqual([], agent_review.run_precheck(BOOK, CHAPTER, "m3", self.root))

    def test_long_bad_quote_fails_and_names_the_file(self):
        self._entry(BAD_LONG)
        failures = agent_review.run_precheck(BOOK, CHAPTER, "m3", self.root)
        self.assertTrue(failures)
        self.assertIn("entry_content/測試.yaml", failures[0])
        self.assertIn("check_quote_fidelity", failures[0])

    def test_short_bad_quote_only_caught_by_min_chars_2_mode(self):
        self._entry(BAD_SHORT)
        # 預設門檻（10 字）看不到，--min-chars 2 才抓得到
        total, misses, _ = cqf.check_quotes(BOOK, CHAPTER, root=self.root)
        self.assertEqual([], misses)
        failures = agent_review.run_precheck(BOOK, CHAPTER, "m3", self.root)
        self.assertEqual(1, len(failures))
        self.assertIn("--min-chars 2", failures[0])

    def test_stage_scope_ignores_files_that_do_not_belong_to_the_stage_yet(self):
        self._entry(GOOD)
        self._chapter_content(BAD_LONG)          # m6 的檔：m3 submit 不該被它擋住
        self._link_updates(BAD_LONG)             # link_updates 的檔：m3／m6 不該被它擋住
        self.assertEqual([], agent_review.run_precheck(BOOK, CHAPTER, "m3", self.root))
        failures = agent_review.run_precheck(BOOK, CHAPTER, "m6", self.root)
        self.assertTrue(any("chapter_content.yaml" in f for f in failures))
        self.assertFalse(any("link_updates.yaml" in f for f in failures))

    def test_link_updates_stage_checks_summary_and_runs_dry_run(self):
        self._entry(GOOD)
        self._chapter_content(GOOD)
        self._link_updates(BAD_LONG)
        with patch.object(agent_review, "_run_link_updates_dry_run", return_value=(0, "ok")) as dry:
            failures = agent_review.run_precheck(BOOK, CHAPTER, "link_updates", self.root)
        dry.assert_called_once()
        self.assertTrue(any("link_updates.yaml" in f for f in failures))

    def test_link_updates_dry_run_failure_is_reported(self):
        self._entry(GOOD)
        self._link_updates(GOOD)
        with patch.object(agent_review, "_run_link_updates_dry_run",
                          return_value=(1, "❌ 找不到條目 link_folder/地點/X.md")):
            failures = agent_review.run_precheck(BOOK, CHAPTER, "link_updates", self.root)
        self.assertEqual(1, len(failures))
        self.assertIn("--dry-run 失敗", failures[0])
        self.assertIn("找不到條目", failures[0])

    def test_dry_run_is_not_invoked_for_m3_or_m6(self):
        self._entry(GOOD)
        self._chapter_content(GOOD)
        with patch.object(agent_review, "_run_link_updates_dry_run") as dry:
            agent_review.run_precheck(BOOK, CHAPTER, "m3", self.root)
            agent_review.run_precheck(BOOK, CHAPTER, "m6", self.root)
        dry.assert_not_called()

    def test_missing_manifest_is_a_failure_not_a_crash(self):
        self._entry(GOOD)
        (self.tmp_dir / "source_manifest.md").unlink()
        failures = agent_review.run_precheck(BOOK, CHAPTER, "m3", self.root)
        self.assertTrue(failures)
        self.assertIn("source_manifest", failures[0])

    def test_precheck_does_not_modify_any_file(self):
        self._entry(BAD_LONG)
        before = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        agent_review.run_precheck(BOOK, CHAPTER, "m3", self.root)
        after = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    # --- submit 指令與 --no-precheck ---------------------------------------

    def _run_main(self, *argv):
        out = io.StringIO()
        with patch.object(agent_review, "ROOT", self.root), \
                patch.object(sys, "argv", ["agent_review.py", *argv]), redirect_stdout(out):
            code = self._call_main()
        return code, out.getvalue()

    def _call_main(self):
        # run_precheck／submit 的 root 預設值在 def 時就綁定，這裡直接把 root 注入
        real_precheck, real_submit = agent_review.run_precheck, agent_review.submit
        with patch.object(agent_review, "run_precheck",
                          lambda b, c, s, root=self.root: real_precheck(b, c, s, root)), \
                patch.object(agent_review, "submit",
                             lambda b, c, s, root=self.root, no_precheck_reason=None:
                             real_submit(b, c, s, root, no_precheck_reason=no_precheck_reason)):
            return agent_review.main()

    def test_cli_submit_refused_when_precheck_fails_and_writes_nothing(self):
        self._entry(BAD_LONG)
        code, output = self._run_main("submit", BOOK, str(CHAPTER), "m3")
        self.assertEqual(1, code)
        self.assertIn("前置檢查 FAIL", output)
        self.assertFalse((self.tmp_dir / agent_review.STATE_FILENAME).exists())

    def test_cli_submit_passes_and_writes_checkpoint(self):
        self._entry(GOOD)
        code, output = self._run_main("submit", BOOK, str(CHAPTER), "m3")
        self.assertEqual(0, code)
        self.assertIn("前置檢查 PASS", output)
        self.assertTrue((self.tmp_dir / agent_review.STATE_FILENAME).is_file())

    def test_no_precheck_requires_reason(self):
        self._entry(BAD_LONG)
        code, output = self._run_main("submit", BOOK, str(CHAPTER), "m3", "--no-precheck")
        self.assertEqual(2, code)
        self.assertIn("--reason", output)
        self.assertFalse((self.tmp_dir / agent_review.STATE_FILENAME).exists())

    def test_no_precheck_with_reason_is_recorded_and_listed_in_summary(self):
        self._entry(BAD_LONG)
        code, output = self._run_main(
            "submit", BOOK, str(CHAPTER), "m3", "--no-precheck", "--reason", "短引句是強調用法，已人工確認")
        self.assertEqual(0, code)
        state = agent_review._read_state(BOOK, CHAPTER, self.root)
        history = state["stages"]["m3"]["review_history"]
        self.assertEqual(agent_review.NO_PRECHECK_VERDICT, history[-1]["verdict"])
        self.assertEqual("短引句是強調用法，已人工確認", history[-1]["reason"])
        self.assertIsNone(history[-1]["attempt"])      # 不佔 reviewer 額度

        rows = agent_review.no_precheck_stages(BOOK, self.root)
        self.assertEqual([(BOOK, CHAPTER, "m3", "短引句是強調用法，已人工確認")], rows)
        out = io.StringIO()
        with redirect_stdout(out):
            agent_review._print_forced_pass_report(BOOK, self.root)
        self.assertIn("--no-precheck", out.getvalue())
        self.assertIn("短引句是強調用法", out.getvalue())

    def test_no_precheck_history_does_not_consume_review_budget(self):
        self._entry(BAD_LONG)
        _path, record = agent_review.submit(
            BOOK, CHAPTER, "m3", self.root, no_precheck_reason="測試")
        self.assertEqual(0, record["review_attempts"])
        _path, verdict = agent_review.record_verdict(
            BOOK, CHAPTER, "m3", "pass", record["sha256"], root=self.root)
        self.assertEqual(1, verdict["review_attempts"])

    def test_reason_without_no_precheck_is_rejected(self):
        self._entry(GOOD)
        code, _output = self._run_main("submit", BOOK, str(CHAPTER), "m3", "--reason", "x")
        self.assertEqual(2, code)


if __name__ == "__main__":
    unittest.main()
