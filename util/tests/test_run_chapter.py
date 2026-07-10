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

ENTRY_PAYLOAD = {
    "name": ENTRY_NAME,
    "type": "原文",
    "secondary_types": [],
    "aliases": [],
    "status": "formal",
    "definition": "希伯來文 kapporet，法櫃的蓋子，神與人相會之處。",
    "accumulations": [
        {"book": "出埃及記", "chapter": 26, "summary": "神指示製作施恩座。",
         "relation": "施恩座是神與摩西相會之處。"},
    ],
    "related_entries": [],
    "sources": ["出埃及記26:1"],
}

# 批量步驟要求模型回傳「陣列」；單筆步驟仍回傳物件
ENTRY_BATCH_RESPONSE = yaml.safe_dump([ENTRY_PAYLOAD], allow_unicode=True, sort_keys=False)

# 故意用英文書名 + 清單外 target + list-form 節點，測程式的三個修正
VERSE_LINKS_PAYLOAD = yaml.safe_dump({
    "book": "Exodus", "chapter": 26,
    "links": [
        {"verse": 1, "phrase": "施恩座", "target": ENTRY_NAME},
        {"verse": 1, "phrase": "法櫃", "target": "清單外的東西"},
    ],
}, allow_unicode=True, sort_keys=False)

CHAPTER_CONTENT_PAYLOAD = yaml.safe_dump({
    "book": "Exodus", "chapter": 26,
    "knowledge_nodes": [{"group": "神學", "nodes": [ENTRY_NAME]}],
    "organization": "**重點摘要**\n- 施恩座與會幕",
}, allow_unicode=True, sort_keys=False)


def fake_runner(prompt):
    if "verse_links payload" in prompt:
        return VERSE_LINKS_PAYLOAD
    if "chapter_content payload" in prompt:
        return CHAPTER_CONTENT_PAYLOAD
    if "entry_content payload" in prompt:
        return ENTRY_BATCH_RESPONSE
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
            # 清單外 target 的 broken link 被丟棄會留一則 verse_links 說明；其餘應為空
            self.assertEqual(
                [], [m for m in result["manual_review"] if not m.startswith("verse_links")]
            )
            self.assertEqual(1, result["entry_count"])
            entry = root / "link_folder" / "原文" / f"{ENTRY_NAME}.md"
            chapter = root / "02 出埃及記" / "第26章.md"
            self.assertTrue(entry.exists())
            self.assertTrue(chapter.exists())
            text = chapter.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("# 出埃及記 第26章"))  # 英文書名被覆蓋
            self.assertIn(f"[[{ENTRY_NAME}|施恩座]]", text)
            self.assertNotIn("清單外的東西", text)  # broken target 被丟棄
            self.assertIn("### 神學", text)  # list-form knowledge_nodes 被 coerce

    def test_resume_skips_model_on_second_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_vault(tmp)
            run_chapter.run_chapter(
                "出埃及記", 26, root=root, runner=fake_runner, index={}, homonyms={},
            )

            def exploding_runner(prompt):
                raise AssertionError("resume 應直接沿用 .tmp payload，不得再呼叫模型")

            result = run_chapter.run_chapter(
                "出埃及記", 26, root=root, runner=exploding_runner, index={}, homonyms={},
            )
            self.assertEqual([], result["errors"])

    def test_failed_batch_entry_is_routed_to_manual_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_vault(tmp)

            def bad_entry_runner(prompt):
                if "entry_content payload" in prompt and "verse_links" not in prompt \
                        and "chapter_content" not in prompt:
                    return "name: 缺欄位\ntype: 原文\nstatus: formal\n"  # 非陣列，恆失敗
                return fake_runner(prompt)

            result = run_chapter.run_chapter(
                "出埃及記", 26, root=root, runner=bad_entry_runner, index={}, homonyms={},
            )
            entry_notes = [m for m in result["manual_review"] if m.startswith("entry_content")]
            self.assertEqual(1, len(entry_notes))
            self.assertIn("entry_content", entry_notes[0])
            self.assertFalse((root / "link_folder" / "原文" / f"{ENTRY_NAME}.md").exists())


class MatchPayloadTests(unittest.TestCase):
    def test_accepts_translit_suffix(self):
        entry = {"name": "皂莢木", "suggested_type": "原文"}
        results = [{"name": "皂莢木（atzei shittim）"}]
        self.assertIs(results[0], run_chapter._match_payload(entry, results))

    def test_prefix_word_not_confused(self):
        # 「銅」不得誤配到「銅網（sevakah）」
        entry = {"name": "銅", "suggested_type": "原文"}
        results = [{"name": "銅網（sevakah）"}]
        self.assertIsNone(run_chapter._match_payload(entry, results))

    def test_intext_substring_still_matches(self):
        entry = {"name": "出27:1-8", "suggested_type": "互文"}
        results = [{"name": "幕外之壇（出27:1-8）"}]
        self.assertIs(results[0], run_chapter._match_payload(entry, results))


class RenderStepGuardTests(unittest.TestCase):
    def _vault(self, tmp):
        root = Path(tmp)
        (root / "link_folder" / "原文").mkdir(parents=True)
        return root

    def test_refuses_to_clobber_other_chapter_accumulation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._vault(tmp)
            existing = root / "link_folder" / "原文" / "皂莢木（atzei shittim）.md"
            existing.write_text(
                "# 皂莢木（atzei shittim）\n\n## 定義\n\n木\n\n## 按書卷累積\n\n### 出埃及記\n"
                "<!-- accumulation:出埃及記:25:start -->\n#### 第25章\n"
                "- 本章重點：x\n- 與本章關聯：y\n"
                "<!-- accumulation:出埃及記:25:end -->\n\n## 來源依據\n\n- CT\n",
                encoding="utf-8",
            )
            original = existing.read_text(encoding="utf-8")
            ctx = run_chapter.ChapterContext(
                "出埃及記", 27, root=root, index={}, homonyms={}
            )
            payload = dict(ENTRY_PAYLOAD, name="皂莢木（atzei shittim）")
            written = run_chapter.render_step(
                ctx, {"皂莢木（atzei shittim）": payload}, None, None
            )
            self.assertEqual([], written)
            self.assertTrue(any("皂莢木" in m for m in ctx.manual_review))
            self.assertEqual(original, existing.read_text(encoding="utf-8"))  # 未被覆蓋


class VerseLinkTargetTests(unittest.TestCase):
    """verse_links 改為程式化標注：逐節掃描已知詞、長詞優先、連到條目全名。"""

    def _ctx(self, tmp, raw, created=None):
        root = Path(tmp)
        (root / "raw_scripture" / "出埃及記").mkdir(parents=True)
        (root / "raw_scripture" / "出埃及記" / "第26章.txt").write_text(
            "\n".join(raw) + "\n", encoding="utf-8"
        )
        (root / "02 出埃及記" / ".tmp" / "第26章").mkdir(parents=True)
        (root / "link_folder").mkdir(exist_ok=True)
        ctx = run_chapter.ChapterContext("出埃及記", 26, root=root, index={}, homonyms={})
        if created is not None:
            ctx.created_entry_names = created
        return ctx

    def test_bare_term_links_to_existing_title(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx = self._ctx(tmp, ["要做施恩座安在法櫃上。"])
            plan = {"A_use_directly": [{"name": "法櫃", "existing_title": "法櫃（aron）"}],
                    "B_needs_update": []}
            links = run_chapter.verse_links_step(ctx, plan)["links"]
            self.assertEqual(
                [{"verse": 1, "phrase": "法櫃", "target": "法櫃（aron）"}], links
            )

    def test_longest_match_wins_no_overlap(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx = self._ctx(tmp, ["帶卯的銅座二十個。"],
                            created=["銅座（eden）", "銅（nechosheth）"])
            plan = {"A_use_directly": [], "B_needs_update": [], "C_new_formal": []}
            phrases = [l["phrase"] for l in run_chapter.verse_links_step(ctx, plan)["links"]]
            self.assertIn("銅座", phrases)      # 長詞優先
            self.assertNotIn("銅", phrases)     # 被 銅座 覆蓋、不重疊

    def test_term_absent_from_all_verses_is_not_linked(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx = self._ctx(tmp, ["用金子包裹。"], created=["皂莢木（atzei shittim）"])
            plan = {"A_use_directly": [], "B_needs_update": [], "C_new_formal": []}
            links = run_chapter.verse_links_step(ctx, plan)["links"]
            self.assertEqual([], links)  # 皂莢木 不在經文，不硬連

    def test_each_term_linked_once_per_verse(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx = self._ctx(tmp, ["幔子相連，幔子接連。"], created=["幔子（yeriah）"])
            plan = {"A_use_directly": [], "B_needs_update": [], "C_new_formal": []}
            links = run_chapter.verse_links_step(ctx, plan)["links"]
            self.assertEqual(1, len(links))  # 同節同詞只連首次出現
            self.assertEqual("幔子（yeriah）", links[0]["target"])


if __name__ == "__main__":
    unittest.main()
