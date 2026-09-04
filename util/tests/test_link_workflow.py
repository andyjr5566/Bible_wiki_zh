import json
import tempfile
import unittest
import sys
from pathlib import Path
from unittest.mock import patch

import yaml

UTIL_DIR = Path(__file__).resolve().parents[1]
if str(UTIL_DIR) not in sys.path:
    sys.path.insert(0, str(UTIL_DIR))

from build_link_index import make_index
from resolve_link_candidates import (
    find_in_index,
    has_book_chapter_data,
    resolve,
)
from validate_knowledge_base import INTERNAL_SOURCE_LINE_RE, ambiguous_wikilinks
import link_updates
from link_updates import apply_updates, plan_updates, render_block, validate_update
from normalize_format import normalize_chapter, normalize_entry


def entry(title, path, entry_type, aliases=None, secondary=None):
    return {
        "title": title,
        "path": path,
        "type": entry_type,
        "aliases": aliases or [],
        "secondary_types": secondary or [],
        "status": "formal",
    }


class IndexTests(unittest.TestCase):
    def test_secondary_type_is_not_alias(self):
        index, errors = make_index([
            entry("天梯", "link_folder/神學/天梯.md", "神學", secondary=["互文"])
        ])
        self.assertFalse(errors)
        self.assertNotIn("互文", index)

    def test_duplicate_alias_is_blocking(self):
        _, errors = make_index([
            entry("甲", "link_folder/主題/甲.md", "主題", aliases=["共同名"]),
            entry("乙", "link_folder/主題/乙.md", "主題", aliases=["共同名"]),
        ])
        self.assertTrue(any("alias 多重指向" in error for error in errors))


class ResolverTests(unittest.TestCase):
    def test_exact_name_keeps_parenthetical_content(self):
        target = entry(
            "全能的神（El Shaddai）",
            "link_folder/神學/全能的神（El Shaddai）.md",
            "神學",
        )
        index = {"全能的神（El Shaddai）": target}
        match_type, matched, title = find_in_index("全能的神（El Shaddai）", index)
        self.assertEqual("exact", match_type)
        self.assertEqual(target, matched)
        self.assertEqual("全能的神（El Shaddai）", title)

    def test_type_mismatch_requires_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "link_folder" / "人物" / "迦南.md"
            path.parent.mkdir(parents=True)
            path.write_text("# 迦南\n", encoding="utf-8")
            index = {"迦南": entry("迦南", "link_folder/人物/迦南.md", "人物")}
            plan = resolve(
                [{"name": "迦南", "suggested_type": "地點", "line_number": 1}],
                index, "創世記", "28", root,
            )
            self.assertEqual(1, len(plan["D_new_candidate"]))
            self.assertEqual("type_conflict", plan["D_new_candidate"][0]["match_type"])

    def test_registered_homonym_requires_manual_target_selection(self):
        homonyms = {
            "示劍": [
                {"target": "示劍（城）", "type": "地點"},
                {"target": "示劍（哈抹之子）", "type": "人物"},
            ]
        }
        plan = resolve(
            [{"name": "示劍", "suggested_type": "地點", "line_number": 1}],
            {}, "創世記", "34", homonyms=homonyms,
        )
        self.assertEqual(1, len(plan["D_new_candidate"]))
        self.assertEqual("homonym", plan["D_new_candidate"][0]["match_type"])

    def test_book_and_chapter_are_both_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "entry.md"
            path.write_text("### 另一卷 第28章\n", encoding="utf-8")
            self.assertFalse(has_book_chapter_data("entry.md", "創世記", "28", root))
            path.write_text("### 創世記 第28章\n", encoding="utf-8")
            self.assertTrue(has_book_chapter_data("entry.md", "創世記", "28", root))


    def test_nested_lookup_does_not_leak_into_the_next_book_section(self):
        """`### 利未記` 段落的搜尋不可越界撿到 `### 民數記` 底下的同號數章。

        全庫實測（2026-08-19）：裸的 `[\s\S]*?` 造成 701 筆假陽性、涉及 280 個條目。
        後果是該條目被判 A_use_directly（本章資料已存在），link_updates 不會替它
        補累積，而反向孤兒檢查驗的是「條目→章」不是「章→條目」，四道閘門全過。
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "entry.md").write_text(
                "### 利未記\n"
                "#### [[03 利未記/第7章|第7章]]\n- x\n"
                "### 民數記\n"
                "#### [[04 民數記/第19章|第19章]]\n- y\n",
                encoding="utf-8",
            )
            self.assertFalse(has_book_chapter_data("entry.md", "利未記", "19", root))
            self.assertTrue(has_book_chapter_data("entry.md", "民數記", "19", root))
            self.assertTrue(has_book_chapter_data("entry.md", "利未記", "7", root))


class UpdateTests(unittest.TestCase):
    def _prepare_review_fixture(self, root, development="已有跨章發展"):
        chapter_dir = root / "01 創世記" / ".tmp" / "第8章"
        chapter_dir.mkdir(parents=True)
        entry_path = root / "link_folder" / "人物" / "測試.md"
        entry_path.parent.mkdir(parents=True)
        entry_path.write_text(
            "# 測試\n\n## 定義\n\n穩定身分與辨識邊界。\n\n"
            "## 按書卷累積\n\n### 創世記\n\n"
            "<!-- accumulation:創世記:1:start -->\n#### 第1章\n"
            "- 本章重點：舊重點\n- 與本章關聯：舊關聯\n"
            "<!-- accumulation:創世記:1:end -->\n\n"
            f"## 主題發展\n\n{development}\n\n"
            "## 相關條目\n\n## 來源依據\n",
            encoding="utf-8",
        )
        (chapter_dir / "link_plan.yaml").write_text(yaml.safe_dump({
            "B_needs_update": [{
                "name": "測試",
                "existing_title": "測試",
                "existing_path": "link_folder/人物/測試.md",
            }],
        }, allow_unicode=True), encoding="utf-8")
        with patch.object(link_updates, "ROOT", root), patch("builtins.print"):
            manifest = link_updates.prepare("創世記", 8)
        data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
        data["updates"][0]["summary"] = "第八章的新重點"
        data["updates"][0]["relation"] = "第八章與測試條目的新關聯"
        manifest.write_text(
            yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
        )
        return manifest, entry_path

    @staticmethod
    def _fill_keep_review(manifest):
        data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
        review = data["updates"][0]["overview_review"]
        review["definition"] = "keep"
        review["development"] = "keep"
        manifest.write_text(
            yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
        )
        return data

    def test_internal_source_lines_are_forbidden_but_heading_is_allowed(self):
        self.assertIsNone(INTERNAL_SOURCE_LINE_RE.search("### 觸發來源\n"))
        self.assertIsNotNone(INTERNAL_SOURCE_LINE_RE.search("- 觸發來源：CT\n"))
        self.assertIsNotNone(INTERNAL_SOURCE_LINE_RE.search("- 來源檔案：raw_data/a.txt\n"))
        self.assertIsNotNone(INTERNAL_SOURCE_LINE_RE.search("- raw_data：a.txt\n"))

    def test_update_requires_content(self):
        missing = validate_update({
            "title": "天梯", "path": "link_folder/神學/天梯.md",
            "summary": "", "relation": "", "sources": [], "source_files": [],
        })
        self.assertIn("summary", missing)
        self.assertNotIn("sources", missing)

    def test_marker_contains_book_and_chapter(self):
        block = render_block("創世記", 28, {
            "summary": "重點", "relation": "關聯",
            "sources": ["CT"], "source_files": ["raw_data/example.txt"],
        })
        self.assertIn("<!-- accumulation:創世記:28:start -->", block)
        self.assertNotIn("觸發來源", block)
        self.assertNotIn("來源檔案", block)
        self.assertNotIn("raw_data/example.txt", block)
        self.assertNotIn("### 創世記", block)

    def test_seventh_accumulation_hint_includes_definition(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entry_path = root / "link_folder" / "人物" / "測試.md"
            entry_path.parent.mkdir(parents=True)
            blocks = "\n\n".join(
                render_block("創世記", chapter, {
                    "summary": f"重點{chapter}",
                    "relation": f"關聯{chapter}",
                })
                for chapter in range(1, 7)
            )
            entry_path.write_text(
                "# 測試\n\n## 定義\n\n內容\n\n## 按書卷累積\n\n"
                f"### 創世記\n\n{blocks}\n\n"
                "## 主題發展\n\n## 相關條目\n\n## 來源依據\n",
                encoding="utf-8",
            )
            manifest = root / "updates.yaml"
            manifest.write_text(yaml.safe_dump({
                "book": "創世記",
                "chapter": 7,
                "updates": [{
                    "title": "測試",
                    "path": "link_folder/人物/測試.md",
                    "summary": "第七筆",
                    "relation": "第七筆關聯",
                }],
            }, allow_unicode=True), encoding="utf-8")
            logs = []
            with patch("link_updates.ROOT", root):
                self.assertEqual(1, apply_updates(manifest, reporter=logs.append))
            self.assertTrue(any(
                "definition／development／related_entries／sources" in line
                for line in logs
            ))

    def test_prepare_makes_distinct_overview_review_mandatory_but_keep_is_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # 1. 正常條目（綠燈）：預設為 keep，可直接通過預覽
            manifest, _entry_path = self._prepare_review_fixture(root)
            data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
            self.assertEqual(2, data["review_schema_version"])
            self.assertIn("穩定身分", data["review_guidance"]["definition"])
            self.assertIn("跨章", data["review_guidance"]["development"])
            self.assertIn("本章明確資料", data["review_guidance"]["accumulation"])
            self.assertEqual(
                "pending", data["updates"][0]["overview_review"]["definition"]
            )
            self.assertEqual("keep", data["updates"][0]["overview_review"]["definition"])
            self.assertEqual("keep", data["updates"][0]["overview_review"]["development"])
            self.assertNotIn("reason", data["updates"][0]["overview_review"])
            self.assertTrue((manifest.parent / "link_update_review_baseline.yaml").is_file())

            with patch.object(link_updates, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "尚未完成判斷"):
                    link_updates.preview_updates(manifest)

            self._fill_keep_review(manifest)
            with patch.object(link_updates, "ROOT", root):
                preview = link_updates.preview_updates(manifest)
            review = preview["operations"][0]["overview_review"]
            self.assertEqual("keep", review["definition"]["decision"])
            self.assertEqual("keep", review["development"]["decision"])
            self.assertFalse(review["definition"]["changed"])
            self.assertFalse(review["development"]["changed"])

            # 2. 標註 pending 的條目：未完成判斷時強迫報錯攔截
            data["updates"][0]["overview_review"]["definition"] = "pending"
            manifest.write_text(
                yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
            )
            with patch.object(link_updates, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "尚未完成判斷"):
                    link_updates.preview_updates(manifest)

    def test_update_decision_requires_real_section_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest, _entry_path = self._prepare_review_fixture(root)
            data = self._fill_keep_review(manifest)
            data["updates"][0]["overview_review"]["definition"] = "update"
            manifest.write_text(
                yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
            )
            with patch.object(link_updates, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "選了 update.*沒有改變"):
                    link_updates.preview_updates(manifest)

    def test_challenged_keep_requires_only_a_controlled_basis(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest, _entry_path = self._prepare_review_fixture(root, development="")
            data = self._fill_keep_review(manifest)
            with patch.object(link_updates, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "development_blank_with_history.*basis"):
                    link_updates.preview_updates(manifest)

            data["updates"][0]["overview_review"]["development"] = {
                "decision": "keep",
                "basis": "single_chapter_only",
            }
            manifest.write_text(
                yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
            )
            with patch.object(link_updates, "ROOT", root):
                preview = link_updates.preview_updates(manifest)
            review = preview["operations"][0]["overview_review"]["development"]
            self.assertEqual("single_chapter_only", review["basis"])
            self.assertNotIn("reason", review)

    def test_cross_chapter_language_challenges_a_canned_keep(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest, _entry_path = self._prepare_review_fixture(root)
            data = self._fill_keep_review(manifest)
            data["updates"][0]["relation"] = (
                "既有累積記載第一章；本章補上整卷書層級的對照。"
            )
            manifest.write_text(
                yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
            )
            with patch.object(link_updates, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "cross_chapter_language.*basis"):
                    link_updates.preview_updates(manifest)

            data["updates"][0]["overview_review"]["development"] = {
                "decision": "keep",
                "basis": "single_chapter_only",
            }
            manifest.write_text(
                yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
            )
            with patch.object(link_updates, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "不能填 single_chapter_only"):
                    link_updates.preview_updates(manifest)

            data["updates"][0]["overview_review"]["development"] = {
                "decision": "keep",
                "basis": "already_covered",
                "covered_by": "已有跨章發展",
            }
            manifest.write_text(
                yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
            )
            with patch.object(link_updates, "ROOT", root):
                preview = link_updates.preview_updates(manifest)
            self.assertEqual(
                ["cross_chapter_language"],
                preview["operations"][0]["overview_review"]["challenges"]["development"],
            )

    def test_intra_chapter_restatement_is_not_a_cross_chapter_signal(self):
        """章內「第16節重述一次」不是跨章訊號，不該逼出受控 basis。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest, _entry_path = self._prepare_review_fixture(root)
            data = self._fill_keep_review(manifest)
            data["updates"][0]["relation"] = "第12節先給界線，第16節重述一次。"
            manifest.write_text(
                yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
            )
            with patch.object(link_updates, "ROOT", root):
                preview = link_updates.preview_updates(manifest)
            self.assertEqual(
                [],
                preview["operations"][0]["overview_review"]["challenges"]["development"],
            )

    def test_already_covered_needs_a_verbatim_anchor_from_the_section(self):
        """already_covered 必須舉得出該區塊的逐字內容，否則不成立。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest, _entry_path = self._prepare_review_fixture(
                root, development="長子名分在創35章斷送，創49 再次宣告。"
            )
            data = self._fill_keep_review(manifest)
            data["updates"][0]["relation"] = "本章補上跨卷的對照。"
            for verdict, pattern in (
                ({"decision": "keep", "basis": "already_covered"}, "必須加 covered_by"),
                (
                    {
                        "decision": "keep",
                        "basis": "already_covered",
                        "covered_by": "河東分地的安排",
                    },
                    "找不到逐字對應",
                ),
            ):
                data["updates"][0]["overview_review"]["development"] = verdict
                manifest.write_text(
                    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
                    encoding="utf-8",
                )
                with patch.object(link_updates, "ROOT", root):
                    with self.assertRaisesRegex(ValueError, pattern):
                        link_updates.preview_updates(manifest)

            data["updates"][0]["overview_review"]["development"] = {
                "decision": "keep",
                "basis": "already_covered",
                "covered_by": "長子名分在創35章斷送",
            }
            manifest.write_text(
                yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
            )
            with patch.object(link_updates, "ROOT", root):
                preview = link_updates.preview_updates(manifest)
            review = preview["operations"][0]["overview_review"]["development"]
            self.assertEqual("already_covered", review["basis"])
            self.assertEqual("長子名分在創35章斷送", review["covered_by"])

    def test_prepare_writes_the_compact_review_evidence_file(self):
        """證據檔給定義全文與主題發展段落索引，取代逐一開條目。"""
        """證據檔對正常條目給緊湊摘要，對異常條目給段落索引，取代逐一開條目。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # 1. 正常條目（綠燈）：給緊湊摘要卡，不展開全部段落大綱
            manifest, _entry_path = self._prepare_review_fixture(
                root, development="第一段講長子名分。\n\n第二段講河東分地的安排。"
            )
            evidence = manifest.parent / link_updates.REVIEW_EVIDENCE_FILENAME
            self.assertTrue(evidence.is_file())
            text = evidence.read_text(encoding="utf-8")
            self.assertIn("穩定身分與辨識邊界。", text)
            self.assertIn("累積 1 章：創世記 1", text)
            self.assertIn("第一段講長子名分。", text)
            self.assertIn("第二段講河東分地的安排。", text)
            self.assertIn("段落索引", text)
            self.assertIn("- **定義**", text)
            self.assertIn("- **主題發展**", text)
            with patch.object(link_updates, "ROOT", root), patch("builtins.print"):
                with self.assertRaises(FileExistsError):
                    link_updates.prepare("創世記", 8)

            # 2. 異常條目（紅黃燈，例如 development_blank 且有歷史累積）：展開完整段落大綱
            flagged_entry = {
                "title": "異常條目",
                "path": "link_folder/主題/異常條目.md",
                "signals": ["development_blank"],
                "accumulated": ["創世記1", "創世記2"],
                "accumulated_grouped": "創世記 1,2",
                "definition": "短定義內容",
                "development": "",
            }
            flagged_md = link_updates.review_evidence_markdown("創世記", 8, [flagged_entry])
            self.assertIn("### 主題發展：空白", flagged_md)
            self.assertIn("### 定義", flagged_md)

    def test_standing_debt_is_the_only_honest_basis_when_the_entry_owes_a_synthesis(self):
        """條目自己欠帳（累積多／主題發展空白）時，insufficient_evidence 會把欠帳抹掉。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest, entry_path = self._prepare_review_fixture(root, development="")
            blocks = "\n".join(
                render_block("創世記", chapter, {
                    "summary": f"重點{chapter}", "relation": f"關聯{chapter}",
                })
                for chapter in range(1, 10)
            )
            entry_path.write_text(
                "# 測試\n\n## 定義\n\n穩定身分與辨識邊界。\n\n## 按書卷累積\n\n### 創世記\n\n"
                f"{blocks}\n\n## 主題發展\n\n## 相關條目\n\n## 來源依據\n",
                encoding="utf-8",
            )
            data = self._fill_keep_review(manifest)

            for basis, pattern in (("insufficient_evidence", "會把欠帳抹掉"),):
                data["updates"][0]["overview_review"]["development"] = {
                    "decision": "keep", "basis": basis,
                }
                manifest.write_text(
                    yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
                )
                with patch.object(link_updates, "ROOT", root):
                    with self.assertRaisesRegex(ValueError, pattern):
                        link_updates.preview_updates(manifest)

            data["updates"][0]["overview_review"]["development"] = {
                "decision": "keep", "basis": "standing_debt",
            }
            manifest.write_text(
                yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
            )
            with patch.object(link_updates, "ROOT", root):
                preview = link_updates.preview_updates(manifest)
                added, settled = link_updates.record_development_debt(preview, root=root)
            self.assertEqual(["測試"], added)
            self.assertEqual([], settled)
            ledger = json.loads(
                (root / link_updates.DEVELOPMENT_DEBT_PATH).read_text(encoding="utf-8")
            )
            self.assertEqual("link_folder/人物/測試.md", ledger["entries"][0]["path"])
            self.assertEqual("創世記:8", ledger["entries"][0]["deferred_at"])

    def test_a_maintenance_round_can_settle_a_debt_it_actually_paid(self):
        """欠帳原本只有章節 apply 清得掉，維護回合補寫完卻無路可清。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entry = root / "link_folder" / "人物" / "測試.md"
            entry.parent.mkdir(parents=True, exist_ok=True)
            blocks = render_block("創世記", 1, {"summary": "甲", "relation": "乙"})
            blocks += render_block("民數記", 2, {"summary": "丙", "relation": "丁"})
            entry.write_text(
                "# 測試\n\n## 定義\n\n身分。\n\n## 按書卷累積\n\n"
                + blocks
                + "\n\n## 主題發展\n\n創1 起頭的線，到民2 才轉向。\n\n## 相關條目\n\n## 來源依據\n",
                encoding="utf-8",
            )
            ledger = root / "util" / "output" / "development_debt.json"
            ledger.parent.mkdir(parents=True, exist_ok=True)
            ledger.write_text(json.dumps({"entries": [{
                "path": "link_folder/人物/測試.md", "title": "測試",
                "deferred_at": "申命記:4", "accumulated": 2, "fingerprint": "x",
            }]}, ensure_ascii=False), encoding="utf-8")

            item, named = link_updates.settle_development_debt(
                "link_folder/人物/測試.md", root=root
            )
            self.assertEqual("測試", item["title"])
            self.assertEqual(["創世記", "民數記"], named)
            self.assertEqual([], json.loads(ledger.read_text(encoding="utf-8"))["entries"])

    def test_settle_refuses_a_blank_or_single_book_development(self):
        """還帳的判準與 development=update 一致：要跨至少兩卷，不能只是填了字。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entry = root / "link_folder" / "人物" / "測試.md"
            entry.parent.mkdir(parents=True, exist_ok=True)
            blocks = render_block("創世記", 1, {"summary": "甲", "relation": "乙"})
            blocks += render_block("民數記", 2, {"summary": "丙", "relation": "丁"})
            ledger = root / "util" / "output" / "development_debt.json"
            ledger.parent.mkdir(parents=True, exist_ok=True)

            def write(development):
                entry.write_text(
                    "# 測試\n\n## 定義\n\n身分。\n\n## 按書卷累積\n\n" + blocks
                    + "\n\n## 主題發展\n\n" + development
                    + "\n\n## 相關條目\n\n## 來源依據\n",
                    encoding="utf-8",
                )
                ledger.write_text(json.dumps({"entries": [{
                    "path": "link_folder/人物/測試.md", "title": "測試",
                    "deferred_at": "申命記:4", "accumulated": 2, "fingerprint": "x",
                }]}, ensure_ascii=False), encoding="utf-8")

            write("待累積")
            with self.assertRaisesRegex(ValueError, "空白／待累積"):
                link_updates.settle_development_debt("link_folder/人物/測試.md", root=root)

            write("創1 這一章講得很完整，別章沒有補充。")
            with self.assertRaisesRegex(ValueError, "只點名 1 卷"):
                link_updates.settle_development_debt("link_folder/人物/測試.md", root=root)

    def test_standing_debt_needs_a_debt_signal(self):
        """沒有欠帳訊號時不可用 standing_debt 當萬用出口。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest, _entry_path = self._prepare_review_fixture(root)
            data = self._fill_keep_review(manifest)
            data["updates"][0]["overview_review"]["development"] = {
                "decision": "keep", "basis": "standing_debt",
            }
            manifest.write_text(
                yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
            )
            with patch.object(link_updates, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "沒有 challenge"):
                    link_updates.preview_updates(manifest)

    def test_outline_uses_headings_when_present_so_it_stops_growing_per_paragraph(self):
        """成熟條目的段落只會越來越多；有小標題時索引只給小標題。"""
        body = "開場一段。\n\n### 甲\n\n甲的內容。\n\n### 乙\n\n乙的內容。\n\n### 丙\n\n丙的內容。"
        outline = link_updates._section_outline(body)
        labels = [row[0] for row in outline]
        self.assertEqual(["### 甲", "### 乙", "### 丙"], labels[:3])
        self.assertIn("段散文", labels[-1])
        self.assertNotIn("甲的內容。", "".join(labels))

        long_body = "\n\n".join(f"第{n}段的開頭。內文內文。" for n in range(1, 13))
        capped = link_updates._section_outline(long_body)
        self.assertEqual(link_updates.EVIDENCE_OUTLINE_MAX_ROWS + 1, len(capped))
        self.assertIn("段，共", capped[-1][0])

    def test_accumulated_chapters_are_grouped_by_book(self):
        """35 章的條目不該把書卷名重複 35 次。"""
        text = "".join(
            f"<!-- accumulation:{book}:{chapter}:start -->x<!-- accumulation:{book}:{chapter}:end -->"
            for book, chapter in (("創世記", 12), ("創世記", 13), ("出埃及記", 1), ("申命記", 4))
        )
        self.assertEqual("創世記 12,13 ／ 出埃及記 1 ／ 申命記 4",
                         link_updates._format_accumulated(text))

    def test_applied_manifest_is_not_relitigated_when_a_later_edit_lands(self):
        """套用之後，同一個條目會被後面的章節與勘誤合法改動，基線比對不再是良定義的檢查。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest, entry_path = self._prepare_review_fixture(root)
            self._fill_keep_review(manifest)
            with patch.object(link_updates, "ROOT", root):
                link_updates.apply_updates(manifest, reporter=None)

            text = entry_path.read_text(encoding="utf-8")
            entry_path.write_text(text.replace("已有跨章發展", "已有跨章發展（後續章節補寫）"),
                                  encoding="utf-8")
            with patch.object(link_updates, "ROOT", root):
                self.assertEqual(0, link_updates.apply_updates(manifest, dry_run=True,
                                                               reporter=None))

    def test_unapplied_manifest_still_rejects_keep_when_the_section_changed(self):
        """章節進行中仍然全驗：說 keep 卻改了區塊要被擋下。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest, entry_path = self._prepare_review_fixture(root)
            self._fill_keep_review(manifest)
            text = entry_path.read_text(encoding="utf-8")
            entry_path.write_text(text.replace("已有跨章發展", "改寫過的跨章發展"),
                                  encoding="utf-8")
            with patch.object(link_updates, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "選了 keep，但條目中的"):
                    link_updates.preview_updates(manifest)

    def test_guidance_wording_may_change_without_breaking_existing_manifests(self):
        """驗的是三個區塊的定位有沒有被刪掉，不是逐字措辭。

        原本逐字相等，於是每次調整 REVIEW_GUIDANCE 的用語，全部既有 manifest 都會
        變成「被改寫」，而 prepare 拒絕覆寫既有檔——等於逼人手動補那段文字。
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest, _entry_path = self._prepare_review_fixture(root)
            data = self._fill_keep_review(manifest)
            data["review_guidance"]["development"] += "（措辭調整）"
            manifest.write_text(
                yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
            )
            with patch.object(link_updates, "ROOT", root):
                link_updates.preview_updates(manifest)

            data["review_guidance"].pop("development")
            manifest.write_text(
                yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
            )
            with patch.object(link_updates, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "review_guidance 缺漏"):
                    link_updates.preview_updates(manifest)

    def test_long_definitions_ship_as_an_index_not_full_text(self):
        """證據檔會隨累積變肥，長定義改給主張索引；短定義仍給全文。"""
        head = "他是本章的主角，出現在第一節。"
        paras = [
            "**%s。** %s" % (label, "說明內容。" * 40)
            for label in ("他在哪裡", "他做了什麼", "為什麼重要")
        ]
        body = ("%s\n\n" % head) + "\n\n".join(paras)
        header, out = link_updates._definition_evidence(body)
        self.assertIn("索引", header)
        self.assertEqual(head, out[0])
        self.assertTrue(all(line.startswith("- ") for line in out[1:]))
        self.assertIn("他做了什麼。", out[2])
        self.assertNotIn("說明內容。", "".join(out))
        self.assertLess(len("".join(out)), len(body) // 4)

        short_header, short_out = link_updates._definition_evidence("短定義內容。")
        self.assertIn("全文", short_header)
        self.assertEqual(["短定義內容。"], short_out)

    def test_schema_v2_rejects_reason_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest, _entry_path = self._prepare_review_fixture(root)
            data = self._fill_keep_review(manifest)
            data["updates"][0]["overview_review"]["definition"] = {
                "decision": "keep",
                "reason": "這段文字不應再輸出",
            }
            manifest.write_text(
                yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
            )
            with patch.object(link_updates, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "不要填 reason"):
                    link_updates.preview_updates(manifest)

    def test_schema_v1_manifest_remains_compatible(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest, _entry_path = self._prepare_review_fixture(root)
            data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
            data["review_schema_version"] = 1
            data["review_guidance"] = link_updates.REVIEW_GUIDANCE_V1
            data["updates"][0]["overview_review"]["definition"] = {
                "decision": "keep",
                "reason": "本章沒有改變條目的穩定身分或辨識邊界",
            }
            data["updates"][0]["overview_review"]["development"] = {
                "decision": "keep",
                "reason": "本章尚未形成超越既有內容的跨章推進或對照",
                "synthesis_scope": [],
            }
            manifest.write_text(
                yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
            )
            baseline_path = manifest.parent / link_updates.REVIEW_BASELINE_FILENAME
            baseline = yaml.safe_load(baseline_path.read_text(encoding="utf-8"))
            baseline["review_schema_version"] = 1
            baseline_path.write_text(
                yaml.safe_dump(baseline, allow_unicode=True, sort_keys=False), encoding="utf-8"
            )
            with patch.object(link_updates, "ROOT", root):
                preview = link_updates.preview_updates(manifest)
            self.assertEqual(
                "keep", preview["operations"][0]["overview_review"]["definition"]["decision"]
            )

    def test_development_update_requires_cross_chapter_scope_and_returns_diff(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest, entry_path = self._prepare_review_fixture(root)
            data = self._fill_keep_review(manifest)
            data["updates"][0]["overview_review"]["development"] = {
                "decision": "update",
                "synthesis_scope": ["創世記:8"],
            }
            manifest.write_text(
                yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
            )
            text = entry_path.read_text(encoding="utf-8")
            entry_path.write_text(
                text.replace(
                    "已有跨章發展",
                    "已有跨章發展\n\n第一章建立身分，第八章則顯出這身分如何轉為公開責任。",
                ),
                encoding="utf-8",
            )
            with patch.object(link_updates, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "本章與至少另一章"):
                    link_updates.preview_updates(manifest)

            data["updates"][0]["overview_review"]["development"]["synthesis_scope"] = [
                "創世記:1", "創世記:8",
            ]
            manifest.write_text(
                yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
            )
            with patch.object(link_updates, "ROOT", root):
                preview = link_updates.preview_updates(manifest)
            review = preview["operations"][0]["overview_review"]["development"]
            self.assertTrue(review["changed"])
            self.assertIn("第一章建立身分", review["diff"])
            logs = []
            with patch.object(link_updates, "ROOT", root):
                self.assertEqual(
                    1, link_updates.apply_updates(manifest, dry_run=True, reporter=logs.append)
                )
            self.assertTrue(any("主題發展 diff" in line for line in logs))

    def test_development_update_rejects_current_chapter_restatement(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest, entry_path = self._prepare_review_fixture(root)
            data = self._fill_keep_review(manifest)
            update = data["updates"][0]
            update["summary"] = "第八章記載測試人物在眾人面前承擔新的公開責任"
            update["relation"] = "這件事顯明測試人物的身分在本章轉為公開責任"
            update["overview_review"]["development"] = {
                "decision": "update",
                "synthesis_scope": ["創世記:1", "創世記:8"],
            }
            manifest.write_text(
                yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
            )
            text = entry_path.read_text(encoding="utf-8")
            entry_path.write_text(
                text.replace(
                    "已有跨章發展",
                    "已有跨章發展\n\n### 創8：公開責任\n\n"
                    "第八章記載測試人物在眾人面前承擔新的公開責任。",
                ),
                encoding="utf-8",
            )
            with patch.object(link_updates, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "summary／relation 高度重疊"):
                    link_updates.preview_updates(manifest)

    def test_apply_inserts_inside_book_group_in_chapter_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entry_path = root / "link_folder" / "人物" / "測試.md"
            entry_path.parent.mkdir(parents=True)
            entry_path.write_text(
                "# 測試\n\n## 定義\n\n內容\n\n## 按書卷累積\n\n### 創世記\n\n"
                "<!-- accumulation:創世記:2:start -->\n#### 第2章\n"
                "- 本章重點：舊資料\n- 來源：CT\n"
                "<!-- accumulation:創世記:2:end -->\n\n"
                "## 主題發展\n\n## 相關條目\n\n## 來源依據\n",
                encoding="utf-8",
            )
            manifest = root / "updates.yaml"
            manifest.write_text(yaml.safe_dump({
                "book": "創世記",
                "chapter": 1,
                "updates": [{
                    "title": "測試",
                    "path": "link_folder/人物/測試.md",
                    "summary": "新資料",
                    "relation": "測試關聯",
                    "sources": ["BH"],
                    "source_files": ["raw_data/example.txt"],
                }],
            }, allow_unicode=True), encoding="utf-8")
            with patch("link_updates.ROOT", root):
                self.assertEqual(1, apply_updates(manifest))
                self.assertEqual(0, apply_updates(manifest))
            rendered = entry_path.read_text(encoding="utf-8")
            self.assertLess(
                rendered.index("#### [[01 創世記/第1章|第1章]]"),
                rendered.index("#### 第2章"),
            )
            accumulation = rendered[
                rendered.index("## 按書卷累積"):rendered.index("## 主題發展")
            ]
            self.assertIn("#### [[01 創世記/第1章|第1章]]", accumulation)

    def test_preview_is_read_only_and_rejects_non_entry_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entry_path = root / "link_folder" / "人物" / "測試.md"
            entry_path.parent.mkdir(parents=True)
            original = "# 測試\n\n## 按書卷累積\n\n## 主題發展\n"
            entry_path.write_text(original, encoding="utf-8")
            manifest = root / "updates.yaml"
            manifest.write_text(yaml.safe_dump({
                "book": "創世記",
                "chapter": 1,
                "updates": [{
                    "title": "測試", "path": "link_folder/人物/測試.md",
                    "summary": "新資料", "relation": "測試關聯",
                }],
            }, allow_unicode=True), encoding="utf-8")
            with patch("link_updates.ROOT", root):
                preview = link_updates.preview_updates(manifest)
            self.assertEqual(1, len(preview["operations"]))
            self.assertEqual(original, entry_path.read_text(encoding="utf-8"))

            manifest.write_text(yaml.safe_dump({
                "book": "創世記",
                "chapter": 1,
                "updates": [{
                    "title": "測試", "path": "README.md",
                    "summary": "新資料", "relation": "測試關聯",
                }],
            }, allow_unicode=True), encoding="utf-8")
            with patch("link_updates.ROOT", root):
                with self.assertRaisesRegex(ValueError, "link_folder"):
                    link_updates.preview_updates(manifest)

    def test_failed_prevalidation_does_not_write_an_earlier_update(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entry_path = root / "link_folder" / "人物" / "測試.md"
            entry_path.parent.mkdir(parents=True)
            original = "# 測試\n\n## 按書卷累積\n\n## 主題發展\n"
            entry_path.write_text(original, encoding="utf-8")
            manifest = root / "updates.yaml"
            manifest.write_text(yaml.safe_dump({
                "book": "創世記",
                "chapter": 1,
                "updates": [
                    {
                        "title": "測試", "path": "link_folder/人物/測試.md",
                        "summary": "新資料", "relation": "測試關聯",
                    },
                    {
                        "title": "壞資料", "path": "link_folder/人物/不存在.md",
                        "summary": "不應寫入", "relation": "不應寫入",
                    },
                ],
            }, allow_unicode=True), encoding="utf-8")
            with patch("link_updates.ROOT", root):
                with self.assertRaisesRegex(ValueError, "找不到條目檔案"):
                    apply_updates(manifest, reporter=None)
            self.assertEqual(original, entry_path.read_text(encoding="utf-8"))

    def test_apply_inserts_new_book_group_in_canonical_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entry_path = root / "link_folder" / "人物" / "測試.md"
            entry_path.parent.mkdir(parents=True)
            entry_path.write_text(
                "# 測試\n\n## 定義\n\n內容\n\n## 按書卷累積\n\n"
                "### 創世記\n\n"
                "<!-- accumulation:創世記:1:start -->\n#### 第1章\n"
                "- 本章重點：創世記資料\n- 與本章關聯：創世記關聯\n"
                "<!-- accumulation:創世記:1:end -->\n\n"
                "### 約書亞記\n\n"
                "<!-- accumulation:約書亞記:1:start -->\n#### 第1章\n"
                "- 本章重點：約書亞記資料\n- 與本章關聯：約書亞記關聯\n"
                "<!-- accumulation:約書亞記:1:end -->\n\n"
                "## 主題發展\n\n## 相關條目\n\n## 來源依據\n",
                encoding="utf-8",
            )
            manifest = root / "updates.yaml"
            manifest.write_text(yaml.safe_dump({
                "book": "出埃及記",
                "chapter": 3,
                "updates": [{
                    "title": "測試",
                    "path": "link_folder/人物/測試.md",
                    "summary": "新資料",
                    "relation": "測試關聯",
                }],
            }, allow_unicode=True), encoding="utf-8")
            with patch("link_updates.ROOT", root):
                self.assertEqual(1, apply_updates(manifest))
            rendered = entry_path.read_text(encoding="utf-8")
            self.assertLess(rendered.index("### 創世記"), rendered.index("### 出埃及記"))
            self.assertLess(rendered.index("### 出埃及記"), rendered.index("### 約書亞記"))

    def test_apply_ignores_legacy_non_book_headings_when_ordering(self):
        """舊格式條目在「## 按書卷累積」下混有非書卷子標題（觸發來源／聖經出現／
        與目前整理書卷的關聯），新書卷區塊插入時不得誤把它們當書卷排序依據。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entry_path = root / "link_folder" / "神學" / "測試.md"
            entry_path.parent.mkdir(parents=True)
            entry_path.write_text(
                "# 測試\n\n## 定義\n\n內容\n\n## 按書卷累積\n\n"
                "### 觸發來源\n\n- [[01 創世記/第3章|創世記 第3章]]：24 節\n\n"
                "### 聖經出現\n\n- 內容\n\n"
                "### 與目前整理書卷的關聯\n\n內容\n\n"
                "### 創世記\n\n"
                "<!-- accumulation:創世記:3:start -->\n#### 第3章\n"
                "- 本章重點：創世記資料\n- 與本章關聯：創世記關聯\n"
                "<!-- accumulation:創世記:3:end -->\n\n"
                "## 主題發展\n\n## 相關條目\n\n## 來源依據\n",
                encoding="utf-8",
            )
            manifest = root / "updates.yaml"
            manifest.write_text(yaml.safe_dump({
                "book": "出埃及記",
                "chapter": 25,
                "updates": [{
                    "title": "測試",
                    "path": "link_folder/神學/測試.md",
                    "summary": "新資料",
                    "relation": "測試關聯",
                }],
            }, allow_unicode=True), encoding="utf-8")
            with patch("link_updates.ROOT", root):
                self.assertEqual(1, apply_updates(manifest))
            rendered = entry_path.read_text(encoding="utf-8")
            self.assertLess(rendered.index("### 創世記"), rendered.index("### 出埃及記"))
            self.assertLess(rendered.index("### 出埃及記"), rendered.index("## 主題發展"))


class FormatNormalizationTests(unittest.TestCase):
    def test_chapter_and_entry_use_different_scheme_templates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chapter = root / "創世記" / "第8章.md"
            chapter.parent.mkdir()
            chapter.write_text(
                "# 創世記 第八章\n\n## 經文\n\n1 起初\n\n---\n\n## 補充資料\n\n內容\n",
                encoding="utf-8",
            )
            rendered_chapter = normalize_chapter(chapter)
            self.assertIn("# 創世記 第8章", rendered_chapter)
            self.assertIn("## 本章知識節點", rendered_chapter)
            self.assertIn("## 本章整理", rendered_chapter)
            self.assertNotIn("## 定義", rendered_chapter)

            entry = root / "link_folder" / "神學" / "測試.md"
            entry.parent.mkdir(parents=True)
            entry.write_text(
                "---\ntype: 神學\nstatus: formal\nsource_scope: collected_only\n---\n\n"
                "# 測試\n\n## 定義／基本資料\n\n定義內容\n\n## 來源依據\n\n- CT\n",
                encoding="utf-8",
            )
            rendered_entry = normalize_entry(entry)
            self.assertIn("## 定義", rendered_entry)
            self.assertNotIn("## 核心摘要", rendered_entry)
            self.assertIn("## 按書卷累積", rendered_entry)
            self.assertNotIn("## 本章整理", rendered_entry)

    def test_entry_merges_distinct_summary_and_orders_chapters(self):
        with tempfile.TemporaryDirectory() as tmp:
            entry = Path(tmp) / "link_folder" / "人物" / "測試.md"
            entry.parent.mkdir(parents=True)
            entry.write_text(
                "---\ntype: 人物\nstatus: formal\nsource_scope: collected_only\n---\n\n"
                "# 測試\n\n## 定義\n\n定義內容\n\n## 核心摘要\n\n補充摘要\n\n"
                "## 按書卷累積\n\n### 主題分析\n\n分析內容\n\n"
                "### 創世記 第2章\n\n- 來源：CT\n\n"
                "## 主題發展\n\n既有發展\n\n## 相關條目\n\n"
                "### 創世記 第1章\n\n- 來源：BH\n\n## 來源依據\n\n- CT\n",
                encoding="utf-8",
            )
            rendered = normalize_entry(entry)
            self.assertIn("定義內容\n\n補充摘要", rendered)
            self.assertLess(
                rendered.index("#### [[01 創世記/第1章|第1章]]"),
                rendered.index("#### [[01 創世記/第2章|第2章]]"),
            )
            accumulation = rendered[
                rendered.index("## 按書卷累積"):rendered.index("## 主題發展")
            ]
            self.assertIn("#### [[01 創世記/第1章|第1章]]", accumulation)
            self.assertEqual(1, rendered.count("### 創世記\n"))
            self.assertNotIn("### 主題分析", accumulation)
            development = rendered[
                rendered.index("## 主題發展"):rendered.index("## 相關條目")
            ]
            self.assertIn("### 主題分析", development)


class HomonymValidationTests(unittest.TestCase):
    def test_bare_homonym_link_is_detected_but_qualified_target_is_allowed(self):
        homonyms = {
            "示劍": [
                {"target": "示劍（城）", "type": "地點"},
                {"target": "示劍（哈抹之子）", "type": "人物"},
            ]
        }
        text = (
            "[[示劍]]\n"
            "[[示劍|原文]]\n"
            "[[示劍（城）|示劍]]\n"
            "[[示劍（哈抹之子）#生平|示劍]]\n"
        )
        self.assertEqual(
            [("示劍", 1), ("示劍", 2)],
            ambiguous_wikilinks(text, homonyms),
        )


class PlanUpdatesTests(unittest.TestCase):
    """prepare 讀 link_plan：yaml（orchestrator 產物）優先，md 為舊流程 fallback。"""

    def _tmp_dir(self, root):
        d = root / "02 出埃及記" / ".tmp" / "第26章"
        d.mkdir(parents=True)
        return d

    def test_prefers_yaml_plan_and_uses_existing_title(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = self._tmp_dir(root)
            (d / "link_plan.yaml").write_text(yaml.safe_dump({
                "B_needs_update": [{
                    "name": "皂莢木",
                    "existing_title": "皂莢木（atzei shittim）",
                    "existing_path": "link_folder/原文/皂莢木（atzei shittim）.md",
                }],
            }, allow_unicode=True), encoding="utf-8")
            with patch.object(link_updates, "ROOT", root):
                data = plan_updates("出埃及記", 26)
            self.assertEqual(1, len(data["updates"]))
            self.assertEqual("皂莢木（atzei shittim）", data["updates"][0]["title"])
            self.assertEqual(
                "link_folder/原文/皂莢木（atzei shittim）.md", data["updates"][0]["path"]
            )

    def test_falls_back_to_md_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = self._tmp_dir(root)
            (d / "link_plan.md").write_text(
                "## B. 需更新既有條目\n\n"
                "- [[摩西]] → link_folder/人物/摩西.md（exact；來源行=1）\n",
                encoding="utf-8",
            )
            with patch.object(link_updates, "ROOT", root):
                data = plan_updates("出埃及記", 26)
            self.assertEqual(
                [("摩西", "link_folder/人物/摩西.md")],
                [(u["title"], u["path"]) for u in data["updates"]],
            )

    def test_missing_both_plans_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._tmp_dir(root)
            with patch.object(link_updates, "ROOT", root):
                with self.assertRaises(FileNotFoundError):
                    plan_updates("出埃及記", 26)


class StaleIntervalTests(unittest.TestCase):
    """許多累積條目的提醒與 challenge 應逢 7, 12, 17, 22... 才觸發，避免每章洗版。"""

    def test_review_signals_many_accumulations_interval(self):
        def make_entry(count):
            blocks = "".join(f"<!-- accumulation:創世記:{i}:start -->\n" for i in range(1, count + 1))
            return f"# 條目\n\n## 定義\n內容\n\n## 主題發展\n內容\n\n## 按書卷累積\n\n{blocks}"

        # 累積 6 章 + 本章 1 章 = 7 筆 (觸發)
        signals_7, _, _ = link_updates._review_signals(make_entry(6), "出埃及記", 1)
        self.assertIn("many_accumulations", signals_7)

        # 累積 7 章 + 本章 1 章 = 8 筆 (不觸發)
        signals_8, _, _ = link_updates._review_signals(make_entry(7), "出埃及記", 1)
        self.assertNotIn("many_accumulations", signals_8)

        # 累積 10 章 + 本章 1 章 = 11 筆 (不觸發)
        signals_11, _, _ = link_updates._review_signals(make_entry(10), "出埃及記", 1)
        self.assertNotIn("many_accumulations", signals_11)

        # 累積 11 章 + 本章 1 章 = 12 筆 (觸發)
        signals_12, _, _ = link_updates._review_signals(make_entry(11), "出埃及記", 1)
        self.assertIn("many_accumulations", signals_12)

        # 累積 16 章 + 本章 1 章 = 17 筆 (觸發)
        signals_17, _, _ = link_updates._review_signals(make_entry(16), "出埃及記", 1)
        self.assertIn("many_accumulations", signals_17)

    def test_development_stale_hint_interval(self):
        def make_blocks(count):
            return "".join(f"<!-- accumulation:創世記:{i}:start -->\n" for i in range(1, count + 1))

        # 6 -> 7 筆 (觸發)
        self.assertEqual(7, link_updates._development_stale_hint(make_blocks(6), make_blocks(7)))

        # 7 -> 8 筆 (不觸發)
        self.assertIsNone(link_updates._development_stale_hint(make_blocks(7), make_blocks(8)))

        # 10 -> 11 筆 (不觸發)
        self.assertIsNone(link_updates._development_stale_hint(make_blocks(10), make_blocks(11)))

        # 11 -> 12 筆 (觸發)
        self.assertEqual(12, link_updates._development_stale_hint(make_blocks(11), make_blocks(12)))

        # 16 -> 17 筆 (觸發)
        self.assertEqual(17, link_updates._development_stale_hint(make_blocks(16), make_blocks(17)))


if __name__ == "__main__":
    unittest.main()
