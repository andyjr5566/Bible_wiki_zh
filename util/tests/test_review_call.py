# -*- coding: utf-8 -*-
"""util/review_call.py：指令組裝、footer 解析、thread 記錄、repo 變動偵測。

codex／agy 一律 mock（patch review_call._run_process 等縫），測試不會呼叫任何 reviewer。
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from util import agent_review, review_call  # noqa: E402

BOOK = "申命記"
CHAPTER = 1
SHA_RE_LEN = 64


def _footer(sha, status="PASS", count=0, stage="m3", reviewer="codex", attempt=1):
    return (
        "審查完畢，沒有重大問題。\n\n"
        f"REVIEW_STAGE: {stage}\nREVIEW_SHA256: {sha}\nREVIEW_REVIEWER: {reviewer}\n"
        f"REVIEW_ATTEMPT: {attempt}\nREVIEW_STATUS: {status}\nFINDINGS_COUNT: {count}\n"
    )


class FooterAndModelTests(unittest.TestCase):
    def test_parse_footer_takes_last_occurrence_and_ignores_template(self):
        sha = "a" * 64
        text = (
            "REVIEW_STATUS: <PASS|CHANGES_REQUIRED|BLOCKED>\n"      # 範本，不是結果
            + _footer(sha, status="CHANGES_REQUIRED", count=3)
        )
        footer = review_call.parse_footer(text)
        self.assertEqual("CHANGES_REQUIRED", footer["REVIEW_STATUS"])
        self.assertEqual(sha, footer["REVIEW_SHA256"])
        self.assertEqual("3", footer["FINDINGS_COUNT"])
        self.assertEqual("m3", footer["REVIEW_STAGE"])

    def test_parse_footer_tolerates_markdown_and_json_escaped_newlines(self):
        sha = "b" * 64
        escaped = json.dumps({"result": _footer(sha, status="BLOCKED")})
        footer = review_call.parse_footer(escaped)
        self.assertEqual("BLOCKED", footer["REVIEW_STATUS"])
        bold = f"**REVIEW_SHA256:** `{sha}`\nREVIEW_STATUS: **PASS**\nFINDINGS_COUNT: 0"
        self.assertEqual(sha, review_call.parse_footer(bold)["REVIEW_SHA256"])

    def test_parse_footer_missing_fields(self):
        self.assertEqual({}, review_call.parse_footer("沒有 footer"))

    def test_parse_global(self):
        self.assertEqual("PASS", review_call.parse_global("...\nGLOBAL_REVIEW: PASS"))
        self.assertEqual("CHANGES_REQUIRED",
                         review_call.parse_global("GLOBAL_REVIEW: PASS\n改判\nGLOBAL_REVIEW: CHANGES_REQUIRED"))
        self.assertIsNone(review_call.parse_global("none"))

    def test_pick_agy_model_takes_newest_generation_high_gemini(self):
        listing = (
            "gemini-3.8-flash-high\tGemini 3.8 Flash (High)\n"
            "gemini-3.8-flash-low\tGemini 3.8 Flash (Low)\n"
            "gemini-3.7-flash-high\tGemini 3.7 Flash (High)\n"
            "gemini-3.1-pro-high\tGemini 3.1 Pro (High)\n"
            "claude-opus-4-6-thinking\tClaude Opus\n"
            "gemini-3.10-flash-high\tGemini 3.10 Flash (High)\n"
        )
        self.assertEqual("gemini-3.10-flash-high", review_call.pick_agy_model(listing))
        listing2 = "gemini-4.0-flash-high\tx\ngemini-4.0-pro-high\ty\ngemini-4.0-pro-low\tz\n"
        self.assertEqual("gemini-4.0-pro-high", review_call.pick_agy_model(listing2))

    def test_pick_agy_model_errors_without_high(self):
        with self.assertRaises(review_call.ReviewCallError):
            review_call.pick_agy_model("gemini-3.8-flash-low\tx\nclaude-sonnet-4-6\ty\n")

    def test_codex_command_first_call_and_resume(self):
        root = Path("C:/repo")
        first = review_call.codex_command("codex", root, None)
        self.assertEqual(["codex", "exec", "--sandbox", "read-only", "--skip-git-repo-check",
                          "-c", review_call.CODEX_MCP_APPROVAL, "-C", str(root), "-"], first)
        resumed = review_call.codex_command("codex", root, "abc-123")
        self.assertEqual(["codex", "exec", "resume", "abc-123", "--skip-git-repo-check",
                          "-c", 'sandbox_mode="read-only"', "-c", review_call.CODEX_MCP_APPROVAL, "-"], resumed)
        self.assertNotIn("--sandbox", resumed)          # resume 子命令不吃 --sandbox
        self.assertIn('default_tools_approval_mode="approve"', review_call.CODEX_MCP_APPROVAL)

    def test_agy_command(self):
        cmd = review_call.agy_command("PROMPT", "gemini-3.8-flash-high", None)
        self.assertEqual(["-p", "PROMPT", "--model", "gemini-3.8-flash-high", "--mode", "plan", "--sandbox"],
                         cmd[1:8])
        self.assertNotIn("--conversation", cmd)
        resumed = review_call.agy_command("PROMPT", "m", "conv-1")
        self.assertEqual(["--conversation", "conv-1"], resumed[-2:])

    def test_parse_agy_output_json(self):
        sha = "c" * 64
        raw = json.dumps({"conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                          "result": _footer(sha, reviewer="antigravity")})
        text, conversation = review_call.parse_agy_output(raw)
        self.assertEqual("123e4567-e89b-12d3-a456-426614174000", conversation)
        self.assertEqual(sha, review_call.parse_footer(text)["REVIEW_SHA256"])

    def test_parse_agy_output_plain_text_fallback(self):
        text, conversation = review_call.parse_agy_output("just text REVIEW_STATUS: PASS")
        self.assertIn("REVIEW_STATUS", text)
        self.assertIsNone(conversation)

    def test_prompts(self):
        prompt = review_call.build_prompt(BOOK, CHAPTER, "m3", "f" * 64, attempt=2, note="改了定義")
        for needle in ("申命記", "1", "m3", "f" * 64, "agent_evidence_audit_prompt.md", "改了定義"):
            self.assertIn(needle, prompt)
        self.assertNotIn("變更說明", review_call.build_prompt(BOOK, CHAPTER, "m3", "f" * 64))
        global_prompt = review_call.build_global_prompt(BOOK, CHAPTER)
        self.assertIn("GLOBAL_REVIEW: PASS", global_prompt)
        self.assertIn("CHANGES_REQUIRED", global_prompt)
        self.assertIn("重大遺漏", global_prompt)
        self.assertIn("wording", global_prompt)


class GitSnapshotTests(unittest.TestCase):
    def test_real_git_repo_detects_edits_and_ignores_own_logs(self):
        import shutil
        import subprocess
        if not shutil.which("git"):
            self.skipTest("git 不可用")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "util").mkdir()
            (root / "util" / "tool.py").write_text("print(1)\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t",
                            "commit", "-q", "-m", "init"], check=True)
            before = review_call.git_snapshot(root)
            # 本工具自己寫的檔不算變動
            logs = root / "05 申命記" / ".tmp" / "第1章" / review_call.LOG_DIRNAME
            logs.mkdir(parents=True)
            (logs / "m3_1.out").write_text("log", encoding="utf-8")
            (root / "05 申命記" / ".tmp" / "第1章" / review_call.THREAD_FILENAME).write_text(
                "threads: {}\n", encoding="utf-8")
            self.assertEqual([], review_call.snapshot_changes(before, review_call.git_snapshot(root)))
            # reviewer 偷改 util/ 就要被抓到
            (root / "util" / "tool.py").write_text("print(2)\n", encoding="utf-8")
            changed = review_call.snapshot_changes(before, review_call.git_snapshot(root))
            self.assertEqual(["util/tool.py"], changed)
            # 已經是 dirty 的檔案再被改一次也抓得到
            mid = review_call.git_snapshot(root)
            (root / "util" / "tool.py").write_text("print(3)\n", encoding="utf-8")
            self.assertEqual(["util/tool.py"], review_call.snapshot_changes(mid, review_call.git_snapshot(root)))
            # 新增未追蹤檔
            (root / "new.txt").write_text("x", encoding="utf-8")
            self.assertIn("new.txt", review_call.snapshot_changes(mid, review_call.git_snapshot(root)))


class RunReviewTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.tmp_dir = self.root / "05 申命記" / ".tmp" / "第1章"
        entry = self.tmp_dir / "entry_content" / "測試.yaml"
        entry.parent.mkdir(parents=True)
        entry.write_text("content: v1\n", encoding="utf-8")
        _path, self.record = agent_review.submit(BOOK, CHAPTER, "m3", self.root)
        self.sha = self.record["sha256"]
        self.out = []
        self.quiet_snapshot = {"status_hash": "s", "diff_hash": "d", "status_lines": [], "files": {}}

    def _fake_runner(self, reply, *, session_id="11111111-2222-3333-4444-555555555555",
                     exit_code=0, calls=None):
        def runner(cmd, stdin_text, cwd, log_path):
            if calls is not None:
                calls.append((list(cmd), stdin_text))
            log_path.write_text(f"session id: {session_id}\n（reviewer 過程）\n", encoding="utf-8")
            if "-o" in cmd:
                Path(cmd[cmd.index("-o") + 1]).write_text(reply, encoding="utf-8")
            return exit_code
        return runner

    def _run(self, runner, *, reviewer="codex", snapshots=None, **kwargs):
        snaps = iter(snapshots or [self.quiet_snapshot, self.quiet_snapshot])
        patches = [
            patch.object(review_call, "_run_process", runner),
            patch.object(review_call, "find_codex", lambda: "codex"),
            patch.object(review_call, "git_snapshot", lambda root=None: next(snaps)),
            patch.object(review_call, "list_agy_models",
                         lambda: "gemini-3.8-flash-high\tx\ngemini-3.1-pro-high\ty\n"),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        return review_call.run_review(
            BOOK, CHAPTER, kwargs.pop("stage", "m3"), reviewer=reviewer, root=self.root,
            out=self.out.append, **kwargs)

    def test_codex_first_call_saves_thread_log_and_prints_verdict_command(self):
        calls = []
        code = self._run(self._fake_runner(_footer(self.sha, count=0), calls=calls))
        self.assertEqual(review_call.EXIT_OK, code)
        cmd, stdin_text = calls[0]
        self.assertIn("--sandbox", cmd)
        self.assertIn(self.sha, stdin_text)
        threads = review_call.load_threads(BOOK, CHAPTER, self.root)
        self.assertEqual("11111111-2222-3333-4444-555555555555", threads["threads"]["review"]["codex"])
        logs = list((self.tmp_dir / review_call.LOG_DIRNAME).glob("m3_*.out"))
        self.assertEqual(["m3_1.out"], [p.name for p in logs])
        joined = "\n".join(self.out)
        self.assertIn(f"python util/agent_review.py verdict {BOOK} {CHAPTER} m3 pass --sha {self.sha}"
                      " --reviewer codex --findings-count 0 --thread-id 11111111-2222-3333-4444-555555555555",
                      joined)
        self.assertNotIn("--observed-sha", joined)
        # 沒有自動記 verdict
        state = agent_review._read_state(BOOK, CHAPTER, self.root)
        self.assertEqual("pending", agent_review._review_status(state["stages"]["m3"]))

    def test_second_call_resumes_the_saved_thread_and_numbers_the_log(self):
        self._run(self._fake_runner(_footer(self.sha)))
        calls = []
        self._run(self._fake_runner(_footer(self.sha), calls=calls))
        cmd, _stdin = calls[0]
        self.assertEqual(["exec", "resume", "11111111-2222-3333-4444-555555555555"], cmd[1:4])
        self.assertTrue((self.tmp_dir / review_call.LOG_DIRNAME / "m3_2.out").is_file())

    def test_sha_mismatch_warns_and_uses_observed_sha(self):
        other = "9" * 64
        self._run(self._fake_runner(_footer(other, status="CHANGES_REQUIRED", count=2)))
        joined = "\n".join(self.out)
        self.assertIn("不同", joined)
        self.assertIn(f"--sha {other}", joined)
        self.assertIn(f"--observed-sha {other}", joined)
        self.assertIn("changes_required", joined)

    def test_content_changed_during_review_uses_observed_sha(self):
        (self.tmp_dir / "entry_content" / "測試.yaml").write_text("content: v2\n", encoding="utf-8")
        self._run(self._fake_runner(_footer(self.sha)))
        joined = "\n".join(self.out)
        self.assertIn("--observed-sha", joined)

    def test_repo_change_during_review_is_loud_and_nonzero(self):
        changed = {"status_hash": "s2", "diff_hash": "d2",
                   "status_lines": [" M util/agent_review.py"], "files": {"util/agent_review.py": "h1"}}
        code = self._run(self._fake_runner(_footer(self.sha)), snapshots=[self.quiet_snapshot, changed])
        self.assertEqual(review_call.EXIT_REPO_CHANGED, code)
        joined = "\n".join(self.out)
        self.assertIn("util/agent_review.py", joined)
        self.assertIn("警告", joined)

    def test_snapshot_changes_detects_content_edit_of_already_dirty_file(self):
        before = {"status_hash": "x", "diff_hash": "y", "status_lines": [" M util/a.py"], "files": {"util/a.py": "1"}}
        after = {"status_hash": "x", "diff_hash": "z", "status_lines": [" M util/a.py"], "files": {"util/a.py": "2"}}
        self.assertEqual(["util/a.py"], review_call.snapshot_changes(before, after))
        self.assertEqual([], review_call.snapshot_changes(before, before))

    def test_quota_exhaustion_prints_reset_and_exits_with_quota_code(self):
        def runner(cmd, stdin_text, cwd, log_path):
            log_path.write_text("ERROR: You've hit your usage limit. Try again at 3:40 PM.\n", encoding="utf-8")
            return 1
        code = self._run(runner)
        self.assertEqual(review_call.EXIT_QUOTA, code)
        joined = "\n".join(self.out)
        self.assertIn("額度用完", joined)
        self.assertIn("3:40 PM", joined)

    def test_missing_footer_exits_with_footer_code(self):
        code = self._run(self._fake_runner("我看完了，但是忘了 footer"))
        self.assertEqual(review_call.EXIT_NO_FOOTER, code)
        self.assertNotIn("python util/agent_review.py verdict", "\n".join(self.out))

    def test_antigravity_uses_live_model_and_saves_conversation(self):
        calls = []
        reply = json.dumps({"conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                            "result": _footer(self.sha, reviewer="antigravity")})

        def runner(cmd, stdin_text, cwd, log_path):
            calls.append(list(cmd))
            log_path.write_text(reply, encoding="utf-8")
            return 0
        code = self._run(runner, reviewer="antigravity")
        self.assertEqual(review_call.EXIT_OK, code)
        self.assertEqual("gemini-3.8-flash-high", calls[0][calls[0].index("--model") + 1])
        self.assertIn("plan", calls[0])
        threads = review_call.load_threads(BOOK, CHAPTER, self.root)
        self.assertEqual("123e4567-e89b-12d3-a456-426614174000",
                         threads["threads"]["review"]["antigravity"])
        # 第二次延續
        calls.clear()
        self._run(runner, reviewer="antigravity")
        self.assertEqual(["--conversation", "123e4567-e89b-12d3-a456-426614174000"], calls[0][-2:])

    def test_global_review_uses_separate_thread_and_log(self):
        self._run(self._fake_runner(_footer(self.sha), session_id="aaaaaaaa-0000-0000-0000-000000000001"))
        calls = []
        self.out.clear()
        code = self._run(
            self._fake_runner("看完了。\nGLOBAL_REVIEW: PASS\n",
                              session_id="bbbbbbbb-0000-0000-0000-000000000002", calls=calls),
            stage=None, global_review=True)
        self.assertEqual(review_call.EXIT_OK, code)
        cmd, stdin_text = calls[0]
        self.assertNotIn("resume", cmd)                  # 不沿用審查 thread
        self.assertIn("GLOBAL_REVIEW", stdin_text)
        threads = review_call.load_threads(BOOK, CHAPTER, self.root)["threads"]
        self.assertEqual("aaaaaaaa-0000-0000-0000-000000000001", threads["review"]["codex"])
        self.assertEqual("bbbbbbbb-0000-0000-0000-000000000002", threads["global"]["codex"])
        self.assertTrue((self.tmp_dir / review_call.LOG_DIRNAME / "global_1.out").is_file())
        self.assertNotIn("python util/agent_review.py verdict", "\n".join(self.out))

    def test_dry_run_writes_nothing_and_never_runs_the_reviewer(self):
        called = []

        def runner(*args, **kwargs):
            called.append(1)
            return 0
        code = self._run(runner, dry_run=True, note="說明一句")
        self.assertEqual(review_call.EXIT_OK, code)
        self.assertEqual([], called)
        self.assertFalse((self.tmp_dir / review_call.LOG_DIRNAME).exists())
        self.assertFalse((self.tmp_dir / review_call.THREAD_FILENAME).exists())
        joined = "\n".join(self.out)
        self.assertIn("說明一句", joined)
        self.assertIn("read-only", joined)

    def test_unsubmitted_stage_is_an_error(self):
        with patch.object(review_call, "find_codex", lambda: "codex"):
            with self.assertRaises(review_call.ReviewCallError):
                review_call.run_review(BOOK, CHAPTER, "m6", root=self.root, out=self.out.append)


if __name__ == "__main__":
    unittest.main()
