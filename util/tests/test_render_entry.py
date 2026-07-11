import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

UTIL_DIR = Path(__file__).resolve().parents[1]
if str(UTIL_DIR) not in sys.path:
    sys.path.insert(0, str(UTIL_DIR))

import validate_knowledge_base as vkb
from normalize_format import normalize_entry
from render_entry import (
    ROOT,
    parse_entry,
    render_entry,
    safe_name,
    validate_payload,
)

KNOWN_TYPES = {"原文", "主題", "神學", "人物", "地點", "互文"}

GOLDEN_FORMAL = {
    "name": "測試施恩座（kapporet）",
    "type": "原文",
    "secondary_types": ["神學"],
    "aliases": ["施恩座"],
    "status": "formal",
    "definition": "希伯來文 כַּפֹּרֶת，字根意為遮蓋、贖罪、平息。施恩座是法櫃的蓋子，純金製。",
    # 故意亂序，測試程式會依章號排序
    "accumulations": [
        {
            "book": "出埃及記",
            "chapter": 26,
            "summary": "施恩座安在至聖所法櫃上。",
            "relation": "神從施恩座與摩西相會。",
        },
        {
            "book": "出埃及記",
            "chapter": 25,
            "summary": "神指示製作施恩座（v17-22）。",
            "relation": "施恩座是法櫃的蓋，也是神與摩西相會之處。",
        },
    ],
    "development": "施恩座在聖經中遞進：出25→利16→來9。",
    "related_entries": ["法櫃（aron）", "基路伯（keruv）"],
    "sources": ["出埃及記25:17-22", "CT: https://example.org/CT25.htm"],
}

GOLDEN_CANDIDATE = {
    "name": "測試樹木",
    "type": "主題",
    "status": "candidate",
    "created_from": "創世記 第23章",
    "trigger_sources": ["[[01 創世記/第23章|創世記 第23章]]：17節"],
    "current_data": "- 交易標的包含田地、洞、四圍的樹木\n- 靈意：樹木代表強韌的生命",
    "related_entries": ["麥比拉洞", "復活盼望"],
    "pending": "- 聖經中「樹木」的象徵意義",
}


class RenderStructureTests(unittest.TestCase):
    def test_formal_orders_chapters_and_uses_stable_markers(self):
        rendered = render_entry(GOLDEN_FORMAL, known_types=KNOWN_TYPES)
        self.assertLess(rendered.index("#### 第25章"), rendered.index("#### 第26章"))
        self.assertIn("<!-- accumulation:出埃及記:25:start -->", rendered)
        self.assertIn("### 出埃及記", rendered)
        # H2 依 scheme 順序
        headings = [line[3:] for line in rendered.splitlines() if line.startswith("## ")]
        self.assertEqual(
            ["定義", "按書卷累積", "主題發展", "相關條目", "來源依據"], headings
        )
        self.assertIn("- [[法櫃（aron）]]", rendered)

    def test_formal_omits_empty_optional_sections_and_stays_valid(self):
        payload = dict(GOLDEN_FORMAL)
        payload.pop("development")
        payload.pop("related_entries")
        rendered = render_entry(payload, known_types=KNOWN_TYPES)
        headings = [line[3:] for line in rendered.splitlines() if line.startswith("## ")]
        self.assertEqual(["定義", "按書卷累積", "來源依據"], headings)
        self._assert_validator_clean(rendered, "原文", payload["name"])

    def test_duplicate_chapter_accumulations_are_merged(self):
        # 模型常為同一章不同節次各給一筆 accumulation；必須合併成單一標記區塊
        payload = dict(GOLDEN_FORMAL, name="測試銅")
        payload["accumulations"] = [
            {"book": "出埃及記", "chapter": 27, "summary": "用銅包裹祭壇。", "relation": "祭壇材料。"},
            {"book": "出埃及記", "chapter": 27, "summary": "銅座作柱基。", "relation": "院子結構。"},
        ]
        rendered = render_entry(payload, known_types=KNOWN_TYPES)
        self.assertEqual(1, rendered.count("<!-- accumulation:出埃及記:27:start -->"))
        self.assertIn("用銅包裹祭壇。；銅座作柱基。", rendered)
        self._assert_validator_clean(rendered, "原文", payload["name"])

    def test_candidate_uses_exact_scheme_headings(self):
        rendered = render_entry(GOLDEN_CANDIDATE, known_types=KNOWN_TYPES)
        headings = [line[3:] for line in rendered.splitlines() if line.startswith("## ")]
        self.assertEqual(["類型", "觸發來源", "目前資料", "相關條目", "待補充"], headings)

    def test_rendered_formal_passes_real_validator(self):
        rendered = render_entry(GOLDEN_FORMAL, known_types=KNOWN_TYPES)
        self._assert_validator_clean(rendered, "原文", GOLDEN_FORMAL["name"])

    def test_rendered_candidate_passes_real_validator(self):
        rendered = render_entry(GOLDEN_CANDIDATE, known_types=KNOWN_TYPES)
        self._assert_validator_clean(rendered, "主題", GOLDEN_CANDIDATE["name"])

    def _assert_validator_clean(self, rendered, entry_type, name):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entry_dir = root / "link_folder" / entry_type
            entry_dir.mkdir(parents=True)
            path = entry_dir / f"{name}.md"
            path.write_text(rendered, encoding="utf-8")
            with patch.object(vkb, "ROOT", root):
                errors, _ = vkb.validate_file(path, strict=True)
            self.assertEqual([], errors)


class SourceUrlLinkifyTests(unittest.TestCase):
    """來源依據的 URL 被全形括號緊貼時，GFM/Obsidian 不會自動連結；
    渲染須包成 <URL>（CommonMark autolink），且重渲染冪等。"""

    def _render_sources(self, sources):
        payload = dict(GOLDEN_FORMAL, sources=sources)
        rendered = render_entry(payload, known_types=KNOWN_TYPES)
        return rendered[rendered.index("## 來源依據"):]

    def test_url_in_fullwidth_parens_is_angle_bracketed(self):
        body = self._render_sources(
            ["BH: Exodus 25 — 說明（https://biblehub.com/study/exodus/25.htm）"]
        )
        self.assertIn("（<https://biblehub.com/study/exodus/25.htm>）", body)

    def test_bare_url_after_space_is_left_as_is(self):
        body = self._render_sources(["CT: https://example.org/CT25.htm"])
        self.assertIn("- CT: https://example.org/CT25.htm", body)
        self.assertNotIn("<https://example.org/CT25.htm>", body)

    def test_rerender_is_idempotent(self):
        source = "BH: 說明（https://biblehub.com/study/exodus/25.htm）"
        first = render_entry(dict(GOLDEN_FORMAL, sources=[source]), known_types=KNOWN_TYPES)
        second = render_entry(parse_entry(first), known_types=KNOWN_TYPES)
        self.assertEqual(first, second)


class RoundTripTests(unittest.TestCase):
    """既有條目 → 正規化 → payload → 重新渲染，必須完全一致。"""

    def _assert_roundtrip(self, relative):
        path = ROOT / relative
        if not path.exists():
            self.skipTest(f"缺少樣本條目：{relative}")
        canonical = normalize_entry(path)
        rendered = render_entry(parse_entry(canonical))
        self.assertEqual(canonical, rendered)

    def test_formal_entry_roundtrip(self):
        self._assert_roundtrip("link_folder/原文/施恩座（kapporet）.md")

    def test_candidate_entry_roundtrip(self):
        self._assert_roundtrip("link_folder/主題/樹木.md")


class PayloadRejectionTests(unittest.TestCase):
    def test_unsafe_name_is_rejected(self):
        payload = dict(GOLDEN_FORMAL, name="施恩座/kapporet")
        errors = validate_payload(payload, known_types=KNOWN_TYPES)
        self.assertTrue(any("不安全字元" in e for e in errors))

    def test_unknown_type_is_rejected(self):
        payload = dict(GOLDEN_FORMAL, type="不存在的分類")
        errors = validate_payload(payload, known_types=KNOWN_TYPES)
        self.assertTrue(any("合法分類" in e for e in errors))

    def test_intertext_bare_scripture_ref_name_is_rejected(self):
        payload = dict(GOLDEN_FORMAL, name="來9:23-24", type="互文")
        errors = validate_payload(payload, known_types=KNOWN_TYPES)
        self.assertTrue(any("互文" in e and "簡短標題" in e for e in errors))

    def test_intertext_titled_name_is_accepted(self):
        payload = dict(GOLDEN_FORMAL, name="天上真聖所（來9:23-24）", type="互文")
        errors = validate_payload(payload, known_types=KNOWN_TYPES)
        self.assertFalse(any("簡短標題" in e for e in errors))

    def test_halfwidth_colon_normalized_to_fullwidth(self):
        # 半形 : 在 Windows 檔名非法（會變 NTFS 資料流留下空檔）；須正規化為全形 ：
        self.assertEqual("天上真聖所（來9：23-24）", safe_name("天上真聖所（來9:23-24）"))
        payload = dict(GOLDEN_FORMAL, name="天上真聖所（來9:23-24）", type="互文")
        errors = validate_payload(payload, known_types=KNOWN_TYPES)
        self.assertFalse(any("不安全字元" in e for e in errors))
        md = render_entry(payload, known_types=KNOWN_TYPES)
        self.assertIn("# 天上真聖所（來9：23-24）", md)
        self.assertNotIn("來9:23-24", md)  # 半形冒號不得殘留

    def test_formal_requires_accumulations(self):
        payload = dict(GOLDEN_FORMAL)
        payload["accumulations"] = []
        errors = validate_payload(payload, known_types=KNOWN_TYPES)
        self.assertTrue(any("按書卷累積" in e for e in errors))

    def test_chapter_out_of_range_is_rejected(self):
        payload = dict(GOLDEN_FORMAL)
        payload["accumulations"] = [{
            "book": "出埃及記", "chapter": 99,
            "summary": "x", "relation": "y",
        }]
        errors = validate_payload(payload, known_types=KNOWN_TYPES)
        self.assertTrue(any("超出" in e for e in errors))

    def test_candidate_requires_current_data(self):
        payload = dict(GOLDEN_CANDIDATE, current_data="")
        errors = validate_payload(payload, known_types=KNOWN_TYPES)
        self.assertTrue(any("目前資料" in e for e in errors))

    def test_render_raises_on_invalid_payload(self):
        payload = dict(GOLDEN_FORMAL, status="bogus")
        with self.assertRaises(ValueError):
            render_entry(payload, known_types=KNOWN_TYPES)


if __name__ == "__main__":
    unittest.main()
