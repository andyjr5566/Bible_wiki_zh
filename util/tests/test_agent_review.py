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
