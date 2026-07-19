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
SOURCE_URL = "https://biblehub.com/study/exodus/26.htm"

MANIFEST = (
    "# Source Manifest — 出埃及記 第26章\n\n"
    "| 來源 | 類型 | URL | raw_data 檔案 | 狀態 |\n"
    "|------|-----|-----|--------------|------|\n"
    f"| BibleHub Study | BH | {SOURCE_URL} | raw_data/biblehub_study_exodus_26.txt | ✅ OK |\n"
)

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
    "sources": [f"BH: Exodus 26 — 施恩座的樣式（{SOURCE_URL}）"],
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

# 2 節經文 → 門檻為 2 個 ### 小節、≥400 字（_org_requirements）
_ORG_PARA = (
    "CT指出施恩座是神與人相會之處，蔽罪的意義由此而來；KC指出這預表基督的救贖工作，"
    "遮蓋律法對人的定罪；BH指出精金象徵神聖潔的性情，不可攙雜；GT指出一切樣式全"
    "出於神在山上的啟示，人不得憑己意增減，事奉的根基在於完全的順服。"
)
_ORG_PLAIN = (
    "### 施恩座的樣式（v1）\n\n" + _ORG_PARA * 3 +
    "\n\n### 照樣式而造（v2）\n\n" + _ORG_PARA * 3
)
# 首次提及以 wiki-link 連回本章條目（M6 白名單要求至少一個行內連結）
CHAPTER_ORGANIZATION = _ORG_PLAIN.replace(
    "CT指出施恩座", f"CT指出[[{ENTRY_NAME}|施恩座]]", 1
)

CHAPTER_CONTENT_PAYLOAD = yaml.safe_dump({
    "book": "Exodus", "chapter": 26,
    "knowledge_nodes": [{"group": "神學", "nodes": [ENTRY_NAME]}],
    "organization": CHAPTER_ORGANIZATION,
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
        # M3/M6 的來源護欄要求 manifest 宣告的 raw_data 檔案實際存在
        (root / "raw_data").mkdir(parents=True, exist_ok=True)
        (root / "raw_data" / "biblehub_study_exodus_26.txt").write_text(
            "BH：施恩座（kapporet）是法櫃的蓋子，神與人相會之處。", encoding="utf-8"
        )
        tmp_dir = root / "02 出埃及記" / ".tmp" / "第26章"
        tmp_dir.mkdir(parents=True)
        (tmp_dir / "source_manifest.md").write_text(MANIFEST, encoding="utf-8")
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
            # 參考資料由程式從 source_manifest 注入，模型不手寫 URL
            self.assertIn(f"**參考資料**\n{SOURCE_URL}", text)

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

    def _candidates_path(self, root):
        return root / "02 出埃及記" / ".tmp" / "第26章" / "link_candidates.yaml"

    def test_editing_candidates_invalidates_downstream(self):
        # 坑：改了 link_candidates.yaml 後重跑，斷點續跑卻沿用照舊 candidates 生成的
        # link_plan.yaml 及其下游（verse_links／chapter_content／第x章.md），靜默套用
        # 過期結果。這裡驗證：改動 candidates → 下游自動作廢並重生（模型被重新呼叫）。
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_vault(tmp)
            run_chapter.run_chapter(
                "出埃及記", 26, root=root, runner=fake_runner, index={}, homonyms={},
            )
            plan_path = root / "02 出埃及記" / ".tmp" / "第26章" / "link_plan.yaml"
            self.assertTrue(plan_path.exists())

            # 改動 candidates 的內容（宣告 surfaces）——指紋改變
            cand = self._candidates_path(root)
            data = yaml.safe_load(cand.read_text(encoding="utf-8"))
            data["candidates"][0]["surfaces"] = ["施恩座"]
            cand.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")

            calls = []

            def counting_runner(prompt):
                calls.append(prompt)
                return fake_runner(prompt)

            result = run_chapter.run_chapter(
                "出埃及記", 26, root=root, runner=counting_runner, index={}, homonyms={},
            )
            self.assertEqual([], result["errors"])
            # 下游被作廢 → 模型被重新呼叫（若沒作廢，resume 會是 0 次呼叫）
            self.assertTrue(calls, "改了 candidates 後應重新呼叫模型（下游已作廢重生）")
            self.assertTrue((root / "02 出埃及記" / "第26章.md").exists())

    def test_untouched_candidates_still_resume(self):
        # 反向護欄：沒改 candidates 時，作廢機制不得誤刪，resume 必須照舊生效
        # （不呼叫模型）。避免自動作廢變成「每跑必重生」。
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_vault(tmp)
            run_chapter.run_chapter(
                "出埃及記", 26, root=root, runner=fake_runner, index={}, homonyms={},
            )

            def exploding_runner(prompt):
                raise AssertionError("candidates 未改動，作廢機制不該觸發重生／呼叫模型")

            result = run_chapter.run_chapter(
                "出埃及記", 26, root=root, runner=exploding_runner, index={}, homonyms={},
            )
            self.assertEqual([], result["errors"])

    def test_editing_entry_content_invalidates_verse_and_chapter(self):
        # 老坑：晚建／補改的條目 payload，verse_links（讀 aliases）與 chapter_content
        # （讀新建條目白名單）沿用舊檔就漏掉它。candidates 沒動、開頭作廢比對不到，
        # 靠 entry_content_step 之後的 _invalidate_after_entry 補作廢這兩個下游。
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_vault(tmp)
            run_chapter.run_chapter(
                "出埃及記", 26, root=root, runner=fake_runner, index={}, homonyms={},
            )
            entry_yaml = (root / "02 出埃及記" / ".tmp" / "第26章"
                          / "entry_content" / f"{ENTRY_NAME}.yaml")
            self.assertTrue(entry_yaml.exists())
            verse_links = root / "02 出埃及記" / ".tmp" / "第26章" / "verse_links.yaml"
            chapter_content = root / "02 出埃及記" / ".tmp" / "第26章" / "chapter_content.yaml"
            self.assertTrue(verse_links.exists() and chapter_content.exists())

            # 模擬「補改條目 payload」：加一個別名——指紋改變（candidates 沒動）
            payload = yaml.safe_load(entry_yaml.read_text(encoding="utf-8"))
            payload["aliases"] = list(payload.get("aliases") or []) + ["蔽罪座"]
            entry_yaml.write_text(
                yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )

            calls = []

            def counting_runner(prompt):
                calls.append(prompt)
                return fake_runner(prompt)

            result = run_chapter.run_chapter(
                "出埃及記", 26, root=root, runner=counting_runner, index={}, homonyms={},
            )
            self.assertEqual([], result["errors"])
            # chapter_content 被作廢 → M6 重新呼叫模型；entry 本身 resume 不重呼叫
            self.assertTrue(
                any("chapter_content payload" in p for p in calls),
                "改了 entry_content 後 chapter_content 應重生（M6 重新呼叫模型）",
            )
            self.assertFalse(
                any("entry_content payload" in p for p in calls),
                "entry payload 已存在，不該重新呼叫模型重建",
            )
            self.assertTrue(verse_links.exists() and chapter_content.exists())


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


class SurfaceVocabularyTests(unittest.TestCase):
    """出26 回饋：經文用簡稱（法櫃、燈臺、皂莢木）時 raw data 明明有補充，
    卻因詞彙表只含候選宣告名而全部連不上。詞彙表必須涵蓋條目全名的括號前
    裸名、條目 aliases，以及候選宣告的 surfaces（可帶節次限定）。"""

    def _ctx(self, tmp, raw, created=None, index=None, payloads=None):
        root = Path(tmp)
        (root / "raw_scripture" / "出埃及記").mkdir(parents=True)
        (root / "raw_scripture" / "出埃及記" / "第26章.txt").write_text(
            "\n".join(raw) + "\n", encoding="utf-8"
        )
        tmp_dir = root / "02 出埃及記" / ".tmp" / "第26章"
        tmp_dir.mkdir(parents=True)
        (root / "link_folder").mkdir(exist_ok=True)
        if payloads:
            (tmp_dir / "entry_content").mkdir()
            for payload in payloads:
                (tmp_dir / "entry_content" / f"{payload['name']}.yaml").write_text(
                    yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8"
                )
        ctx = run_chapter.ChapterContext(
            "出埃及記", 26, root=root, index=index if index is not None else {}, homonyms={}
        )
        if created is not None:
            ctx.created_entry_names = created
        return ctx

    def test_alias_of_existing_entry_links(self):
        # 經文寫「法櫃」，條目是「約櫃」（alias 含 法櫃）→ 必須連上
        index = {"約櫃": {"title": "約櫃", "aliases": ["法櫃", "見證的櫃"]}}
        with tempfile.TemporaryDirectory() as tmp:
            ctx = self._ctx(tmp, ["把法櫃抬進幔子內。"], index=index)
            plan = {"B_needs_update": [{"name": "約櫃", "existing_title": "約櫃"}]}
            links = run_chapter.verse_links_step(ctx, plan)["links"]
            self.assertEqual(
                [{"verse": 1, "phrase": "法櫃", "target": "約櫃"}], links
            )

    def test_base_name_of_existing_title_links(self):
        # B 類既有條目「皂莢木（atzei shittim）」，經文寫裸名「皂莢木」→ 必須連上
        with tempfile.TemporaryDirectory() as tmp:
            ctx = self._ctx(tmp, ["你要用皂莢木做帳幕的豎板。"])
            plan = {"B_needs_update": [{
                "name": "皂莢木（atzei shittim）",
                "existing_title": "皂莢木（atzei shittim）",
            }]}
            links = run_chapter.verse_links_step(ctx, plan)["links"]
            self.assertEqual(
                [{"verse": 1, "phrase": "皂莢木", "target": "皂莢木（atzei shittim）"}],
                links,
            )

    def test_created_payload_alias_links(self):
        # C 類新條目尚未進索引；其 payload aliases 也要入詞彙表
        payload = {"name": "內幔", "aliases": ["至聖所的幔子"]}
        with tempfile.TemporaryDirectory() as tmp:
            ctx = self._ctx(tmp, ["至聖所的幔子要垂下來。"],
                            created=["內幔"], payloads=[payload])
            plan = {"C_new_formal": [{"name": "內幔", "suggested_type": "主題"}]}
            links = run_chapter.verse_links_step(ctx, plan)["links"]
            self.assertEqual(
                [{"verse": 1, "phrase": "至聖所的幔子", "target": "內幔"}], links
            )

    def test_declared_surface_with_verse_restriction(self):
        # 同詞多義：v1 幔子=幕幔、v3 幔子=內幔；宣告 surfaces 限定 v3 才連
        with tempfile.TemporaryDirectory() as tmp:
            ctx = self._ctx(tmp, [
                "你要用十幅幔子做帳幕。",
                "用金子包裹。",
                "這幔子要將聖所和至聖所隔開。",
            ])
            plan = {"B_needs_update": [{
                "name": "內幔", "existing_title": "內幔",
                "surfaces": [{"phrase": "幔子", "verses": [3]}],
            }]}
            links = run_chapter.verse_links_step(ctx, plan)["links"]
            self.assertEqual(
                [{"verse": 3, "phrase": "幔子", "target": "內幔"}], links
            )

    def test_declared_surface_without_restriction_links_everywhere(self):
        # 字串形式的 surface：全章比對（桌子→陳設餅桌子）
        with tempfile.TemporaryDirectory() as tmp:
            ctx = self._ctx(tmp, ["把桌子安在帳幕的北面。"])
            plan = {"B_needs_update": [{
                "name": "陳設餅桌子", "existing_title": "陳設餅桌子",
                "surfaces": ["桌子"],
            }]}
            links = run_chapter.verse_links_step(ctx, plan)["links"]
            self.assertEqual(
                [{"verse": 1, "phrase": "桌子", "target": "陳設餅桌子"}], links
            )

    def test_ambiguous_surface_is_dropped_and_reported(self):
        # 兩個條目 aliases 撞同一個詞 → 整詞不連、記 manual_review（D 類精神）
        index = {
            "金燈臺": {"title": "金燈臺", "aliases": ["燈"]},
            "燈油": {"title": "燈油", "aliases": ["燈"]},
        }
        with tempfile.TemporaryDirectory() as tmp:
            ctx = self._ctx(tmp, ["點燈的時候。"], index=index)
            plan = {"B_needs_update": [
                {"name": "金燈臺", "existing_title": "金燈臺"},
                {"name": "燈油", "existing_title": "燈油"},
            ]}
            links = run_chapter.verse_links_step(ctx, plan)["links"]
            self.assertEqual([], links)
            self.assertTrue(any("歧義" in m and "燈" in m for m in ctx.manual_review))

    def test_declared_surface_overrides_derived_ambiguity(self):
        # 人工宣告（priority 0）勝過推導層的歧義：宣告 燈→金燈臺 就照宣告連
        index = {
            "金燈臺": {"title": "金燈臺", "aliases": ["燈"]},
            "燈油": {"title": "燈油", "aliases": ["燈"]},
        }
        with tempfile.TemporaryDirectory() as tmp:
            ctx = self._ctx(tmp, ["點燈的時候。"], index=index)
            plan = {"B_needs_update": [
                {"name": "金燈臺", "existing_title": "金燈臺", "surfaces": ["燈"]},
                {"name": "燈油", "existing_title": "燈油"},
            ]}
            links = run_chapter.verse_links_step(ctx, plan)["links"]
            self.assertEqual(
                [{"verse": 1, "phrase": "燈", "target": "金燈臺"}], links
            )
            self.assertFalse(any("歧義" in m for m in ctx.manual_review))

    def test_unmatched_declared_surface_is_reported(self):
        # 宣告的 surface 打錯字連不上任何節 → 記 manual_review 供人工檢查
        with tempfile.TemporaryDirectory() as tmp:
            ctx = self._ctx(tmp, ["把桌子安在帳幕的北面。"])
            plan = {"B_needs_update": [{
                "name": "陳設餅桌子", "existing_title": "陳設餅桌子",
                "surfaces": ["桌孒"],
            }]}
            links = run_chapter.verse_links_step(ctx, plan)["links"]
            self.assertEqual([], links)
            self.assertTrue(any("surfaces" in m and "桌孒" in m for m in ctx.manual_review))


class EntrySourceUrlTests(unittest.TestCase):
    """條目 sources 每項必須含本章 manifest 的來源 URL（出25 重做回饋）。"""

    def test_source_without_url_is_rejected(self):
        payload = dict(ENTRY_PAYLOAD, sources=["BibleHub Study (Exodus 26)"])
        errors = run_chapter._entry_source_errors(payload, [SOURCE_URL])
        self.assertEqual(1, len(errors))
        self.assertIn("URL", errors[0])

    def test_source_with_manifest_url_passes(self):
        self.assertEqual(
            [], run_chapter._entry_source_errors(ENTRY_PAYLOAD, [SOURCE_URL])
        )

    def test_no_manifest_urls_skips_check(self):
        payload = dict(ENTRY_PAYLOAD, sources=["出埃及記26:1"])
        self.assertEqual([], run_chapter._entry_source_errors(payload, []))


class EntrySourceLabelTests(unittest.TestCase):
    """sources 行首標籤須與 URL 的 manifest 類型一致（出25 實例：KC 標籤配 CT URL）。"""

    CT_URL = "https://www.ccbiblestudy.org/Old%20Testament/02Exo/02CT26.htm"
    URL_KINDS = {SOURCE_URL: "BH", CT_URL: "CT"}

    def _errors(self, sources):
        payload = dict(ENTRY_PAYLOAD, sources=sources)
        return run_chapter._entry_source_errors(
            payload, list(self.URL_KINDS), self.URL_KINDS
        )

    def test_wrong_label_for_url_is_rejected(self):
        errors = self._errors([f"KC: 出埃及記第26章 — 說明（{self.CT_URL}）"])
        self.assertEqual(1, len(errors))
        self.assertIn("標籤", errors[0])
        self.assertIn("CT", errors[0])

    def test_matching_label_passes(self):
        self.assertEqual([], self._errors([f"CT: 出埃及記第26章 — 說明（{self.CT_URL}）"]))

    def test_free_form_label_is_not_restricted(self):
        # 標籤不是 manifest 已知類型（如舊式 ccbiblestudy.org 寫法）→ 只驗 URL
        self.assertEqual([], self._errors([f"ccbiblestudy 註解: 說明（{self.CT_URL}）"]))


class EntryAliasConflictTests(unittest.TestCase):
    """aliases 驗證左移（出25 實例：alias 撞同批正式條目、兩條目搶同一 alias）。"""

    def test_alias_owned_by_existing_or_planned_entry_is_rejected(self):
        owners = run_chapter._alias_owners(
            {"甘心樂意的奉獻": {"title": "甘心樂意的奉獻", "status": "formal"}},
            set(), {},
        )
        entry = {"name": "甘心樂意的奉獻（林後9：7）", "suggested_type": "互文"}
        payload = {"name": "甘心樂意的奉獻（林後9：7）", "aliases": ["甘心樂意的奉獻"]}
        errors = run_chapter._entry_alias_errors(entry, payload, owners)
        self.assertEqual(1, len(errors))
        self.assertIn("甘心樂意的奉獻", errors[0])

    def test_bare_planned_name_as_own_alias_is_allowed(self):
        owners = run_chapter._alias_owners({}, {"皂莢木"}, {})
        entry = {"name": "皂莢木", "suggested_type": "原文"}
        payload = {"name": "皂莢木（atzei shittim）", "aliases": ["皂莢木"]}
        self.assertEqual([], run_chapter._entry_alias_errors(entry, payload, owners))

    def test_index_alias_key_resolves_to_its_formal_owner(self):
        owners = run_chapter._alias_owners(
            {"道成肉身": {"alias_of": "約1：14"}}, set(), {},
        )
        entry = {"name": "新條目", "suggested_type": "神學"}
        payload = {"name": "新條目", "aliases": ["道成肉身"]}
        errors = run_chapter._entry_alias_errors(entry, payload, owners)
        self.assertEqual(1, len(errors))
        self.assertIn("約1：14", errors[0])

    def test_same_batch_double_claim_is_rejected(self):
        owners = run_chapter._alias_owners(
            {}, {"山上的樣式", "天上事的形狀和影像（來8：5）"}, {},
        )
        run_chapter._register_alias_owner(
            owners, {"name": "山上的樣式", "aliases": ["山上指示的樣式"]}
        )
        entry = {"name": "天上事的形狀和影像（來8：5）", "suggested_type": "互文"}
        second = {"name": "天上事的形狀和影像（來8：5）", "aliases": ["山上指示的樣式"]}
        errors = run_chapter._entry_alias_errors(entry, second, owners)
        self.assertEqual(1, len(errors))


class KnowledgeNodesClosureTests(unittest.TestCase):
    """knowledge_nodes 與 related_entries 同法閉合（出25 實例：裸名 禮物／法版）。"""

    MAPPING = {
        "禮物（terumah）": "禮物（terumah）",
        "法版（edut）": "法版（edut）",
        "約櫃": "約櫃",
    }

    def test_bare_names_closed_and_unknown_dropped(self):
        content = {"knowledge_nodes": {"原文": ["禮物", "法版", "不存在的節點"],
                                       "主題": ["約櫃"]}}
        closed, dropped = run_chapter._close_knowledge_nodes(content, self.MAPPING)
        self.assertEqual(
            ["禮物（terumah）", "法版（edut）"], closed["knowledge_nodes"]["原文"]
        )
        self.assertEqual(["約櫃"], closed["knowledge_nodes"]["主題"])
        self.assertEqual(["不存在的節點"], dropped)

    def test_group_left_empty_after_drops_is_removed(self):
        content = {"knowledge_nodes": {"神學": ["全部都不存在"], "主題": ["約櫃"]}}
        closed, dropped = run_chapter._close_knowledge_nodes(content, self.MAPPING)
        self.assertNotIn("神學", closed["knowledge_nodes"])
        self.assertEqual(["全部都不存在"], dropped)


class ChapterDepthTests(unittest.TestCase):
    """本章整理需達份量門檻：### 小節＋整合性散文（出25 重做太薄的教訓）；
    給定白名單時 wiki-link 只能連本章條目、且至少要有一個（出34 零連結的教訓）；
    體裁自由（表格／callout／高亮／mermaid 圖表）但散文主幹有下限，
    ![[]] 嵌入與 mermaid 以外的 ``` 區塊禁用、mermaid 圖型限穩定清單。"""

    def test_thin_bullet_summary_is_rejected(self):
        validate = run_chapter._chapter_payload_validator(40)
        errors = validate({
            "knowledge_nodes": {"神學": ["會幕"]},
            "organization": "**本章主題**\n- 建造會幕的材料與樣式",
        })
        self.assertTrue(any("小節" in e for e in errors))
        self.assertTrue(any("太薄" in e for e in errors))

    def test_sectioned_prose_passes(self):
        validate = run_chapter._chapter_payload_validator(2)
        errors = validate({
            "knowledge_nodes": {"神學": ["會幕"]},
            "organization": CHAPTER_ORGANIZATION,
        })
        self.assertEqual([], errors)

    def test_requirements_scale_with_chapter_length(self):
        self.assertEqual((2, 400), run_chapter._org_requirements(2))
        self.assertEqual((3, 1500), run_chapter._org_requirements(40))

    def test_allowed_wikilink_passes(self):
        validate = run_chapter._chapter_payload_validator(2, [ENTRY_NAME])
        errors = validate({
            "knowledge_nodes": {"神學": [ENTRY_NAME]},
            "organization": CHAPTER_ORGANIZATION,
        })
        self.assertEqual([], errors)

    def test_wikilink_outside_allowed_list_is_rejected(self):
        validate = run_chapter._chapter_payload_validator(2, [ENTRY_NAME])
        errors = validate({
            "knowledge_nodes": {"神學": [ENTRY_NAME]},
            "organization": CHAPTER_ORGANIZATION + "\n\n另見 [[清單外條目]]。",
        })
        self.assertTrue(any("清單外條目" in e for e in errors))

    def test_organization_without_any_wikilink_is_rejected(self):
        validate = run_chapter._chapter_payload_validator(2, [ENTRY_NAME])
        errors = validate({
            "knowledge_nodes": {"神學": [ENTRY_NAME]},
            "organization": _ORG_PLAIN,
        })
        self.assertTrue(any("wiki-link" in e for e in errors))

    def test_prose_with_table_and_callout_passes(self):
        validate = run_chapter._chapter_payload_validator(2, [ENTRY_NAME])
        supplement = (
            "\n\n| 來源 | 觀點 |\n| --- | --- |\n"
            "| CT | 相會之處 |\n| KC | 預表救贖 |\n\n"
            "> [!quote] CT\n> 施恩座是神與人==相會之處==。"
        )
        errors = validate({
            "knowledge_nodes": {"神學": [ENTRY_NAME]},
            "organization": CHAPTER_ORGANIZATION + supplement,
        })
        self.assertEqual([], errors)

    def test_structure_heavy_organization_is_rejected(self):
        # 總字數過門檻（2 節→400 字）但散文只有十來字：大半內容包進表格
        validate = run_chapter._chapter_payload_validator(2)
        row = "| CT | " + "解讀文字" * 10 + " |\n"
        errors = validate({
            "knowledge_nodes": {"神學": ["會幕"]},
            "organization": (
                "### 施恩座的樣式（v1）\n\n短短一句。\n\n" + row * 12 +
                "\n### 照樣式而造（v2）\n\n又是一句。\n\n" + row * 12
            ),
        })
        self.assertTrue(any("散文主幹" in e for e in errors))

    def test_embed_syntax_is_rejected(self):
        validate = run_chapter._chapter_payload_validator(2, [ENTRY_NAME])
        errors = validate({
            "knowledge_nodes": {"神學": [ENTRY_NAME]},
            "organization": CHAPTER_ORGANIZATION + f"\n\n![[{ENTRY_NAME}]]",
        })
        self.assertTrue(any("![[]]" in e for e in errors))

    def test_non_mermaid_code_fence_is_rejected(self):
        validate = run_chapter._chapter_payload_validator(2, [ENTRY_NAME])
        errors = validate({
            "knowledge_nodes": {"神學": [ENTRY_NAME]},
            "organization": CHAPTER_ORGANIZATION
            + "\n\n```python\nprint('hi')\n```",
        })
        self.assertTrue(any("程式碼區塊" in e for e in errors))

    def test_mermaid_diagram_passes(self):
        validate = run_chapter._chapter_payload_validator(2, [ENTRY_NAME])
        mermaid = (
            "\n\n```mermaid\nflowchart TD\n"
            '  A["金牛犢"] --> B["摔碎法版"] --> C["重造法版"]\n```'
        )
        errors = validate({
            "knowledge_nodes": {"神學": [ENTRY_NAME]},
            "organization": CHAPTER_ORGANIZATION + mermaid,
        })
        self.assertEqual([], errors)

    def test_mermaid_unstable_diagram_type_is_rejected(self):
        validate = run_chapter._chapter_payload_validator(2, [ENTRY_NAME])
        errors = validate({
            "knowledge_nodes": {"神學": [ENTRY_NAME]},
            "organization": CHAPTER_ORGANIZATION
            + "\n\n```mermaid\ngantt\n  title 節期\n```",
        })
        self.assertTrue(any("第一行必須是" in e for e in errors))

    def test_unclosed_fence_is_rejected(self):
        validate = run_chapter._chapter_payload_validator(2, [ENTRY_NAME])
        errors = validate({
            "knowledge_nodes": {"神學": [ENTRY_NAME]},
            "organization": CHAPTER_ORGANIZATION + "\n\n```mermaid\nflowchart TD\n",
        })
        self.assertTrue(any("閉合" in e for e in errors))

    def test_mermaid_double_bracket_node_is_not_a_wikilink(self):
        # A[[x]] 是 mermaid 的 subroutine 節點語法，不得算成 wiki-link：
        # 不能誤觸白名單、不能充當「至少一個連結」，且圖內 [[ 本身要退回
        # （渲染後會被 verify_links.py 掃成 BROKEN）
        validate = run_chapter._chapter_payload_validator(2, [ENTRY_NAME])
        errors = validate({
            "knowledge_nodes": {"神學": [ENTRY_NAME]},
            "organization": _ORG_PLAIN
            + "\n\n```mermaid\nflowchart TD\n  A[[清單外條目]] --> B\n```",
        })
        self.assertFalse(any("不在本章可連清單" in e for e in errors))
        self.assertTrue(any("沒有任何 wiki-link" in e for e in errors))
        self.assertTrue(any("圖內不可出現" in e for e in errors))


class RelatedEntriesClosureTests(unittest.TestCase):
    """related_entries 渲染前閉合：裸經文引用改寫為互文全名、無對應者移除。"""

    def test_related_entries_closed_to_known_titles(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for group in ("神學", "互文"):
                (root / "link_folder" / group).mkdir(parents=True)
            ctx = run_chapter.ChapterContext(
                "出埃及記", 25, root=root,
                index={"約櫃": {"title": "約櫃"}}, homonyms={},
            )
            plan = {"A_use_directly": [{"name": "摩西", "existing_title": "摩西"}],
                    "B_needs_update": []}
            intertext = dict(
                ENTRY_PAYLOAD, name="把守生命樹的道路（創3：24）", type="互文",
                related_entries=[],
            )
            main = dict(
                ENTRY_PAYLOAD, name="基路伯（施恩座）", type="神學",
                related_entries=["約櫃", "摩西", "創3:24", "來9:5"],
            )
            run_chapter.render_step(
                ctx,
                {intertext["name"]: intertext, main["name"]: main},
                None, None, plan=plan,
            )
            text = (root / "link_folder" / "神學" / "基路伯（施恩座）.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("[[約櫃]]", text)          # 全庫索引命中
            self.assertIn("[[摩西]]", text)          # 計畫 A 類命中
            self.assertIn("[[把守生命樹的道路（創3：24）]]", text)  # 裸經文引用 → 互文全名
            self.assertNotIn("[[創3:24]]", text)
            self.assertNotIn("[[來9:5]]", text)      # 無對應條目 → 移除
            self.assertTrue(any("來9:5" in m for m in ctx.manual_review))

    def test_self_reference_is_dropped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "link_folder" / "原文").mkdir(parents=True)
            ctx = run_chapter.ChapterContext(
                "出埃及記", 26, root=root, index={}, homonyms={},
            )
            payload = dict(ENTRY_PAYLOAD, related_entries=[ENTRY_NAME])
            run_chapter.render_step(ctx, {ENTRY_NAME: payload}, None, None, plan={})
            text = (root / "link_folder" / "原文" / f"{ENTRY_NAME}.md").read_text(
                encoding="utf-8"
            )
            self.assertNotIn("## 相關條目", text)  # 不自連
            self.assertEqual([], ctx.manual_review)  # 自我引用靜默去除，不吵人


class ChapterExtractorTests(unittest.TestCase):
    """M6 線上格式：YAML 頭＋===ORGANIZATION=== 裸 markdown（程式組裝）。"""

    def test_two_part_protocol(self):
        text = (
            "```yaml\nbook: 申命記\nchapter: 2\n"
            "knowledge_nodes:\n  神學: [耶和華的爭戰]\n```\n"
            "===ORGANIZATION===\n### 甲（v1-8）\n\n內文與 mermaid 圖。"
        )
        payload = run_chapter._extract_chapter_payload(text)
        self.assertEqual("申命記", payload["book"])
        self.assertTrue(payload["organization"].startswith("### 甲"))

    def test_outer_fence_stripped_inner_mermaid_kept(self):
        text = (
            "book: x\nchapter: 1\nknowledge_nodes: {神學: [a]}\n"
            "===ORGANIZATION===\n```markdown\n### 乙\n\n"
            "```mermaid\nflowchart\n```\n內文\n```"
        )
        payload = run_chapter._extract_chapter_payload(text)
        self.assertTrue(payload["organization"].startswith("### 乙"))
        self.assertIn("mermaid", payload["organization"])

    def test_legacy_full_yaml_still_accepted(self):
        text = (
            "book: x\nchapter: 1\nknowledge_nodes: {神學: [a]}\n"
            "organization: |\n  ### 丙\n  文"
        )
        payload = run_chapter._extract_chapter_payload(text)
        self.assertTrue(payload["organization"].strip().startswith("### 丙"))

    def test_missing_delimiter_and_organization_errors(self):
        from model_client import ModelError
        with self.assertRaises(ModelError) as ctx:
            run_chapter._extract_chapter_payload(
                "book: x\nchapter: 1\nknowledge_nodes: {神學: [a]}"
            )
        self.assertIn("ORGANIZATION", str(ctx.exception))


class BareCreatedLinkGuardTest(unittest.TestCase):
    """散文用「本章新建條目裸名」連結的收窄檢查——申3 實例（黑門山 vs 黑門山（Hermon））。

    這道護欄補 _model_step 對既有檔跳過驗證的洞：手寫／勘誤路徑的 chapter_content
    也要守住。收窄到「裸名對不上白名單、但『裸名（…）』正是本章實建條目」——
    全庫實測 0 誤報，跨章既有條目引用不受影響。
    """

    CREATED = ["黑門山（Hermon）", "亞珥歌伯（Argob）", "瑪吉（Machir）"]
    ALLOWED = ["巴珊", "摩西"] + CREATED  # A/B 既有 + 本章實建全名

    def test_bare_name_of_created_entry_flagged(self):
        org = "摩西過[[黑門山]]，把[[亞珥歌伯]]給[[瑪吉]]。"
        errs = run_chapter._org_bare_created_link_errors(org, self.ALLOWED, self.CREATED)
        self.assertEqual(len(errs), 3)
        self.assertTrue(all("本章新建條目" in e for e in errs))
        joined = "\n".join(errs)
        self.assertIn("[[黑門山（Hermon）|黑門山]]", joined)

    def test_full_name_links_pass(self):
        org = "摩西過[[黑門山（Hermon）|黑門山]]，安置[[瑪吉（Machir）]]。"
        self.assertEqual(
            run_chapter._org_bare_created_link_errors(org, self.ALLOWED, self.CREATED), []
        )

    def test_cross_chapter_reference_not_flagged(self):
        # 散文合法連別章既有條目／經文——不具「裸名（…）是本章實建」特徵，不可誤報
        org = "呼應[[亞伯拉罕之約的應驗]]，參[[43 約翰福音/第1章]]、[[雅博]]。"
        self.assertEqual(
            run_chapter._org_bare_created_link_errors(org, self.ALLOWED, self.CREATED), []
        )

    def test_no_created_entries_is_noop(self):
        org = "摩西過[[黑門山]]。"
        self.assertEqual(
            run_chapter._org_bare_created_link_errors(org, ["巴珊"], []), []
        )


if __name__ == "__main__":
    unittest.main()
