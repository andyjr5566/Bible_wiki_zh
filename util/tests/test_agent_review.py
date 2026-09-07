import tempfile
import unittest
from pathlib import Path

from util import agent_review


class AgentReviewTests(unittest.TestCase):
    def _root_with_m3(self):
        tmpdir = tempfile.TemporaryDirectory()
        root = Path(tmpdir.name)
        entry_dir = root / "05 申命記" / ".tmp" / "第1章" / "entry_content"
        entry_dir.mkdir(parents=True)
        target = entry_dir / "測試.yaml"
        target.write_text("content: v1\n", encoding="utf-8")
        return tmpdir, root, target

    def test_two_reviews_then_final_revision_forces_pass(self):
        tmpdir, root, target = self._root_with_m3()
        self.addCleanup(tmpdir.cleanup)

        _, first = agent_review.submit("申命記", 1, "m3", root)
        self.assertEqual(1, first["round"])
        self.assertEqual(0, first["review_attempts"])
        _, first_verdict = agent_review.record_verdict(
            "申命記", 1, "m3", "changes_required", first["sha256"],
            reviewer="codex", findings_count=2, root=root,
        )
        self.assertEqual(1, first_verdict["review_attempts"])

        target.write_text("content: v2\n", encoding="utf-8")
        _, second = agent_review.submit("申命記", 1, "m3", root)
        self.assertEqual(2, second["round"])
        self.assertFalse(second["forced_pass"])
        _, second_verdict = agent_review.record_verdict(
            "申命記", 1, "m3", "changes_required", second["sha256"],
            reviewer="codex", findings_count=1, root=root,
        )
        self.assertEqual(2, second_verdict["review_attempts"])
        self.assertTrue(second_verdict["final_revision_required"])

        target.write_text("content: v3\n", encoding="utf-8")
        _, final = agent_review.submit("申命記", 1, "m3", root)
        self.assertEqual(2, final["round"])
        self.assertEqual(3, final["revision"])
        self.assertTrue(final["forced_pass"])
        self.assertEqual("pass", final["reviewer_status"])
        self.assertEqual(2, final["review_attempts"])
        self.assertEqual(1, final["forced_from_findings_count"])
        self.assertEqual(final, agent_review.require_pass("申命記", 1, "m3", root))

    def test_review_budget_is_shared_across_codex_and_antigravity(self):
        tmpdir, root, target = self._root_with_m3()
        self.addCleanup(tmpdir.cleanup)

        _, first = agent_review.submit("申命記", 1, "m3", root)
        _, blocked = agent_review.record_verdict(
            "申命記", 1, "m3", "blocked", first["sha256"],
            reviewer="codex", root=root,
        )
        self.assertEqual(0, blocked["review_attempts"])

        _, agy_first = agent_review.record_verdict(
            "申命記", 1, "m3", "changes_required", first["sha256"],
            reviewer="antigravity", findings_count=2, root=root,
        )
        self.assertEqual(1, agy_first["review_attempts"])
        self.assertEqual("antigravity", agy_first["reviewer_agent"])

        target.write_text("content: v2\n", encoding="utf-8")
        _, second = agent_review.submit("申命記", 1, "m3", root)
        _, codex_second = agent_review.record_verdict(
            "申命記", 1, "m3", "changes_required", second["sha256"],
            reviewer="codex", findings_count=1, root=root,
        )
        self.assertEqual(2, codex_second["review_attempts"])

        target.write_text("content: v3\n", encoding="utf-8")
        _, final = agent_review.submit("申命記", 1, "m3", root)
        self.assertTrue(final["forced_pass"])
        self.assertEqual(2, final["review_attempts"])
        self.assertEqual(2, len([h for h in final["review_history"] if h.get("attempt") is not None]))

    def test_no_change_after_second_changes_required_does_not_force_pass(self):
        tmpdir, root, target = self._root_with_m3()
        self.addCleanup(tmpdir.cleanup)

        _, first = agent_review.submit("申命記", 1, "m3", root)
        agent_review.record_verdict(
            "申命記", 1, "m3", "changes_required", first["sha256"],
            reviewer="codex", root=root,
        )
        target.write_text("content: v2\n", encoding="utf-8")
        _, second = agent_review.submit("申命記", 1, "m3", root)
        agent_review.record_verdict(
            "申命記", 1, "m3", "changes_required", second["sha256"],
            reviewer="codex", root=root,
        )

        _, unchanged = agent_review.submit("申命記", 1, "m3", root)
        self.assertFalse(unchanged.get("forced_pass"))
        self.assertEqual("changes_required", unchanged["reviewer_status"])
        with self.assertRaises(agent_review.ReviewGateError):
            agent_review.require_pass("申命記", 1, "m3", root)

    def test_clean_pass_still_works_on_first_review(self):
        tmpdir, root, _ = self._root_with_m3()
        self.addCleanup(tmpdir.cleanup)

        _, first = agent_review.submit("申命記", 1, "m3", root)
        _, reviewed = agent_review.record_verdict(
            "申命記", 1, "m3", "pass", first["sha256"],
            reviewer="codex", findings_count=0, root=root,
        )
        self.assertEqual(1, reviewed["review_attempts"])
        self.assertFalse(reviewed["forced_pass"])
        self.assertEqual("pass", agent_review.require_pass("申命記", 1, "m3", root)["reviewer_status"])

    def test_same_hash_cannot_consume_second_substantive_attempt(self):
        tmpdir, root, _ = self._root_with_m3()
        self.addCleanup(tmpdir.cleanup)
        _, first = agent_review.submit("申命記", 1, "m3", root)
        agent_review.record_verdict(
            "申命記", 1, "m3", "changes_required", first["sha256"],
            reviewer="codex", root=root,
        )
        with self.assertRaises(agent_review.ReviewGateError):
            agent_review.record_verdict(
                "申命記", 1, "m3", "changes_required", first["sha256"],
                reviewer="antigravity", root=root,
            )

    def test_late_recorded_verdict_credits_attempt_without_blessing_current(self):
        # A3：搞反順序（先改檔、後記 verdict）不再讓那次 attempt 蒸發。
        tmpdir, root, target = self._root_with_m3()
        self.addCleanup(tmpdir.cleanup)

        _, first = agent_review.submit("申命記", 1, "m3", root)
        reviewed_sha = first["sha256"]
        target.write_text("content: edited-before-recording\n", encoding="utf-8")

        # 不帶 --observed-sha：拒絕，訊息含可直接複製的補救指令
        with self.assertRaises(agent_review.ReviewGateError) as cm:
            agent_review.record_verdict(
                "申命記", 1, "m3", "changes_required", reviewed_sha,
                reviewer="codex", findings_count=2, root=root,
            )
        message = str(cm.exception)
        self.assertIn("--observed-sha", message)
        self.assertIn(f"--sha {reviewed_sha} --observed-sha {reviewed_sha}", message)

        # 帶 --observed-sha：attempt 照算、寫進 history 並標 late_recorded
        _, rec = agent_review.record_verdict(
            "申命記", 1, "m3", "changes_required", reviewed_sha,
            reviewer="codex", findings_count=2, observed_sha=reviewed_sha, root=root,
        )
        self.assertEqual(1, rec["review_attempts"])
        self.assertTrue(rec["review_history"][-1]["late_recorded"])

        # 補記不追認「目前內容」：gate 仍不過
        with self.assertRaises(agent_review.ReviewGateError):
            agent_review.require_pass("申命記", 1, "m3", root)

    def test_late_recorded_pass_does_not_pass_gate_for_new_bytes(self):
        # 補記一個 PASS，但那是對舊 sha；改後重新 submit 的新內容不得被追認。
        tmpdir, root, target = self._root_with_m3()
        self.addCleanup(tmpdir.cleanup)

        _, first = agent_review.submit("申命記", 1, "m3", root)
        old_sha = first["sha256"]
        target.write_text("content: v2\n", encoding="utf-8")
        agent_review.submit("申命記", 1, "m3", root)  # 記錄前進到 v2

        _, rec = agent_review.record_verdict(
            "申命記", 1, "m3", "pass", old_sha,
            reviewer="codex", findings_count=0, observed_sha=old_sha, root=root,
        )
        self.assertEqual(1, rec["review_attempts"])
        with self.assertRaises(agent_review.ReviewGateError):
            agent_review.require_pass("申命記", 1, "m3", root)

    def test_observed_sha_must_equal_sha(self):
        tmpdir, root, _ = self._root_with_m3()
        self.addCleanup(tmpdir.cleanup)
        _, first = agent_review.submit("申命記", 1, "m3", root)
        with self.assertRaises(agent_review.ReviewGateError):
            agent_review.record_verdict(
                "申命記", 1, "m3", "pass", first["sha256"],
                observed_sha="0" * 64, root=root,
            )

    def _root_with_m3_pass(self):
        tmpdir = tempfile.TemporaryDirectory()
        root = Path(tmpdir.name)
        tmp = root / "05 申命記" / ".tmp" / "第1章"
        (tmp / "entry_content").mkdir(parents=True)
        (tmp / "entry_content" / "測試.yaml").write_text("content: v1\n", encoding="utf-8")
        cc = tmp / "chapter_content.yaml"
        cc.write_text("organization: v1\n", encoding="utf-8")
        _, first = agent_review.submit("申命記", 1, "m3", root)
        agent_review.record_verdict(
            "申命記", 1, "m3", "pass", first["sha256"],
            reviewer="codex", findings_count=0, root=root,
        )
        return tmpdir, root, tmp, cc

    def test_m6_hash_isolates_from_m3(self):
        # A4：只改 chapter_content.yaml → m6 hash 變、m3 hash 不變。
        tmpdir, root, _tmp, cc = self._root_with_m3_pass()
        self.addCleanup(tmpdir.cleanup)
        m3_before = agent_review.stage_fingerprint("申命記", 1, "m3", root)
        m6_before = agent_review.stage_fingerprint("申命記", 1, "m6", root)
        cc.write_text("organization: v2 changed\n", encoding="utf-8")
        self.assertEqual(
            m3_before, agent_review.stage_fingerprint("申命記", 1, "m3", root)
        )
        self.assertNotEqual(
            m6_before, agent_review.stage_fingerprint("申命記", 1, "m6", root)
        )

    def test_receipt_records_hash_inputs_per_stage(self):
        # A4：receipt 看得到每個 stage 實際涵蓋了哪些檔案／parent hash。
        tmpdir, root, _tmp, _cc = self._root_with_m3_pass()
        self.addCleanup(tmpdir.cleanup)
        _, m3rec = agent_review.submit("申命記", 1, "m3", root)
        self.assertEqual(["entry_content/測試.yaml"], m3rec["hash_inputs"])
        _, m6rec = agent_review.submit("申命記", 1, "m6", root)
        self.assertIn("chapter_content.yaml", m6rec["hash_inputs"])
        self.assertTrue(any(x.startswith("parent:m3=") for x in m6rec["hash_inputs"]))

    def test_no_allow_same_sha_bypass_flag(self):
        # A4：不得存在 --allow-same-sha 這類把 stale verdict 塞進 gate 的旁路。
        source = Path(agent_review.__file__).read_text(encoding="utf-8")
        self.assertNotIn('add_argument("--allow-same-sha"', source)
        self.assertNotIn("args.allow_same_sha", source)
        self.assertNotIn("allow_same_sha=", source)
        # require_pass 唯一放行 stale sha 的路徑必須是明示的 forced_pass
        import inspect
        rp = inspect.getsource(agent_review.require_pass)
        self.assertIn("forced_pass", rp)
        self.assertNotIn("allow_same_sha", rp)

    def test_legacy_v1_codex_pass_remains_readable(self):
        tmpdir, root, _ = self._root_with_m3()
        self.addCleanup(tmpdir.cleanup)
        current = agent_review.stage_fingerprint("申命記", 1, "m3", root)
        state_path = root / "05 申命記" / ".tmp" / "第1章" / "agent_review.yaml"
        state_path.write_text(
            "version: 1\nbook: 申命記\nchapter: 1\nstages:\n  m3:\n"
            f"    round: 4\n    sha256: {current}\n    claude: revised\n    codex: pass\n",
            encoding="utf-8",
        )
        record = agent_review.require_pass("申命記", 1, "m3", root)
        self.assertEqual("pass", agent_review._review_status(record))
        self.assertEqual("codex", agent_review._reviewer_agent(record))


if __name__ == "__main__":
    unittest.main()
