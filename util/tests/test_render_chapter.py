import re
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

UTIL_DIR = Path(__file__).resolve().parents[1]
if str(UTIL_DIR) not in sys.path:
    sys.path.insert(0, str(UTIL_DIR))

import validate_knowledge_base as vkb
from render_chapter import (
    coerce_knowledge_nodes,
    coerce_organization,
    parse_chapter,
    render_chapter,
    validate_chapter_content,
    validate_verse_links,
)

# 受控 raw 經文（v1 的「幔子」出現兩次，用來測 occurrence 只連指定那一次）
RAW = [
    "你要用十幅幔子做帳幕。這些幔子要用撚的細麻繡上基路伯。",
    "每幅幔子要長二十八肘。",
    "又要做五十個金鉤，使幔子相連。",
]

VERSE_LINKS = {
    "book": "出埃及記",
    "chapter": 26,
    "links": [
        {"verse": 1, "phrase": "幔子", "target": "幔子（yeriah）", "occurrence": 1},
        {"verse": 1, "phrase": "帳幕", "target": "帳幕", "occurrence": 1},
        {"verse": 3, "phrase": "金鉤", "target": "金鉤（qeres）", "occurrence": 1},
    ],
}

CHAPTER_CONTENT = {
    "book": "出埃及記",
    "chapter": 26,
    "knowledge_nodes": {"神學": ["會幕", "帳幕"], "原文": ["幔子（yeriah）"]},
    "organization": "**重點摘要**\n- 會幕結構與材料",
}


def _strip_links(text):
    return re.sub(
        r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]",
        lambda m: m.group(2) or m.group(1),
        text,
    )


class RenderChapterTests(unittest.TestCase):
    def test_only_specified_occurrence_is_linked(self):
        rendered = render_chapter(VERSE_LINKS, CHAPTER_CONTENT, raw_verses=RAW)
        verse1 = rendered.splitlines()[2]  # H1, blank, then "1. ..."
        # 第一個「幔子」被連、alias 格式正確；第二個「這些幔子」保持純文字
        self.assertIn("十幅[[幔子（yeriah）|幔子]]做[[帳幕]]", verse1)
        self.assertIn("這些幔子要用", verse1)
        self.assertEqual(1, verse1.count("[[幔子（yeriah）|幔子]]"))

    def test_scripture_text_matches_raw_exactly(self):
        rendered = render_chapter(VERSE_LINKS, CHAPTER_CONTENT, raw_verses=RAW)
        scripture_zone = rendered.split("## 本章知識節點")[0]
        stripped = [
            _strip_links(m.group(2))
            for m in re.finditer(r"^(\d+)\.\s(.*)$", scripture_zone, re.M)
        ]
        self.assertEqual(RAW, stripped)

    def test_section_skeleton_and_headings(self):
        rendered = render_chapter(VERSE_LINKS, CHAPTER_CONTENT, raw_verses=RAW)
        self.assertTrue(rendered.startswith("# 出埃及記 第26章\n"))
        headings = [line[3:] for line in rendered.splitlines() if line.startswith("## ")]
        self.assertEqual(["本章知識節點", "本章整理"], headings)
        self.assertIn("### 神學\n- [[會幕]]\n- [[帳幕]]", rendered)

    def test_payload_is_idempotent_through_parse(self):
        rendered = render_chapter(VERSE_LINKS, CHAPTER_CONTENT, raw_verses=RAW)
        verse_links, chapter_content, _ = parse_chapter(rendered)
        self.assertEqual(VERSE_LINKS, verse_links)
        self.assertEqual(
            CHAPTER_CONTENT["knowledge_nodes"], chapter_content["knowledge_nodes"]
        )
        self.assertEqual(
            CHAPTER_CONTENT["organization"], chapter_content["organization"]
        )

    def test_map_block_is_preserved_as_passthrough(self):
        block = (
            "<!-- fhl-map-links:start -->\n## 相關地圖\n\n"
            "- [[appendix/fhl_maps/maps/019|〈出圖二〉]]\n"
            "<!-- fhl-map-links:end -->"
        )
        rendered = render_chapter(
            VERSE_LINKS, CHAPTER_CONTENT, raw_verses=RAW, map_block=block
        )
        self.assertIn(block, rendered)
        # 地圖必須在經文後、第一條分隔線前
        self.assertLess(rendered.index("相關地圖"), rendered.index("\n---\n"))

    def test_references_render_and_roundtrip(self):
        content = dict(
            CHAPTER_CONTENT, references=["https://a.example/1", "https://b.example/2"]
        )
        rendered = render_chapter(VERSE_LINKS, content, raw_verses=RAW)
        self.assertIn(
            "**參考資料**\nhttps://a.example/1\nhttps://b.example/2", rendered
        )
        _, parsed, _ = parse_chapter(rendered)
        self.assertEqual(
            ["https://a.example/1", "https://b.example/2"], parsed["references"]
        )
        self.assertEqual(CHAPTER_CONTENT["organization"], parsed["organization"])

    def test_inline_references_in_organization_render_once(self):
        content = dict(
            CHAPTER_CONTENT,
            organization=CHAPTER_CONTENT["organization"]
            + "\n\n**參考資料**\nhttps://x.example",
        )
        rendered = render_chapter(VERSE_LINKS, content, raw_verses=RAW)
        self.assertEqual(1, rendered.count("**參考資料**"))
        self.assertIn("**參考資料**\nhttps://x.example", rendered)

    def test_rendered_chapter_passes_real_validator(self):
        rendered = render_chapter(VERSE_LINKS, CHAPTER_CONTENT, raw_verses=RAW)
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "raw_scripture" / "出埃及記").mkdir(parents=True)
            (root / "raw_scripture" / "出埃及記" / "第26章.txt").write_text(
                "\n".join(RAW) + "\n", encoding="utf-8"
            )
            chapter_dir = root / "02 出埃及記"
            chapter_dir.mkdir()
            path = chapter_dir / "第26章.md"
            path.write_text(rendered, encoding="utf-8")
            with patch.object(vkb, "ROOT", root):
                errors = vkb.validate_chapter(path)
            self.assertEqual([], errors)


class VerseLinkValidationTests(unittest.TestCase):
    def test_phrase_absent_from_verse_is_rejected(self):
        links = [{"verse": 2, "phrase": "不存在的詞", "target": "x"}]
        errors = validate_verse_links(links, RAW)
        self.assertTrue(any("沒有" in e for e in errors))

    def test_extra_links_are_capped_not_failed(self):
        # 「幔子」在 v1 只出現兩次；給三個 link 應通過驗證，渲染時只連兩次、捨棄多的
        links = [
            {"verse": 1, "phrase": "幔子", "target": "幔子"},
            {"verse": 1, "phrase": "幔子", "target": "幔子"},
            {"verse": 1, "phrase": "幔子", "target": "幔子"},
        ]
        self.assertEqual([], validate_verse_links(links, RAW))
        rendered = render_chapter(
            {"book": "出埃及記", "chapter": 26, "links": links},
            CHAPTER_CONTENT, raw_verses=RAW,
        )
        verse1 = rendered.splitlines()[2]
        self.assertEqual(2, verse1.count("[[幔子]]"))

    def test_verse_out_of_range_is_rejected(self):
        links = [{"verse": 99, "phrase": "幔子", "target": "x"}]
        errors = validate_verse_links(links, RAW)
        self.assertTrue(any("verse" in e for e in errors))

    def test_overlapping_links_are_resolved_not_failed(self):
        # 重疊的 phrase 不再讓整章失敗；渲染時保留較前、捨棄較後
        links = [
            {"verse": 1, "phrase": "幔子做", "target": "a"},
            {"verse": 1, "phrase": "做帳幕", "target": "b"},
        ]
        self.assertEqual([], validate_verse_links(links, RAW))
        rendered = render_chapter(
            {"book": "出埃及記", "chapter": 26, "links": links},
            CHAPTER_CONTENT, raw_verses=RAW,
        )
        verse1 = rendered.splitlines()[2]
        self.assertIn("[[a|幔子做]]", verse1)
        self.assertNotIn("[[b|", verse1)

    def test_empty_organization_is_rejected(self):
        errors = validate_chapter_content(
            {"knowledge_nodes": {"神學": ["會幕"]}, "organization": "  "}
        )
        self.assertTrue(any("本章整理" in e for e in errors))

    def test_empty_knowledge_nodes_is_rejected(self):
        errors = validate_chapter_content(
            {"knowledge_nodes": {}, "organization": "內容"}
        )
        self.assertTrue(any("knowledge_nodes" in e for e in errors))

    def test_coerce_knowledge_nodes_handles_list_and_string_forms(self):
        self.assertEqual(
            {"神學": ["會幕"]},
            coerce_knowledge_nodes([{"group": "神學", "nodes": ["會幕"]}]),
        )
        self.assertEqual({"神學": ["會幕"]}, coerce_knowledge_nodes({"神學": "會幕"}))
        self.assertEqual(
            {"神學": ["會幕", "銅"]}, coerce_knowledge_nodes({"神學": ["會幕", "銅"]})
        )
        self.assertEqual({}, coerce_knowledge_nodes("garbage"))

    def test_list_form_knowledge_nodes_passes_validation(self):
        errors = validate_chapter_content(
            {"knowledge_nodes": [{"group": "神學", "nodes": ["會幕"]}], "organization": "x"}
        )
        self.assertEqual([], errors)

    def test_coerce_organization_handles_dict_list_string(self):
        self.assertEqual("純文字", coerce_organization("純文字"))
        self.assertEqual(
            "**結構**\n- 甲\n- 乙\n\n**主題**\n- 丙",
            coerce_organization({"結構": ["甲", "乙"], "主題": ["丙"]}),
        )
        self.assertEqual("- 甲\n- 乙", coerce_organization(["甲", "乙"]))
        self.assertEqual("", coerce_organization(None))

    def test_dict_organization_renders_markdown_not_repr(self):
        content = dict(CHAPTER_CONTENT, organization={"結構": ["會幕外院兩大物件"]})
        rendered = render_chapter(VERSE_LINKS, content, raw_verses=RAW)
        body = rendered.split("## 本章整理")[1]
        self.assertNotIn("{'", body)  # 不得出現 dict repr
        self.assertIn("**結構**", body)
        self.assertIn("- 會幕外院兩大物件", body)

    def test_dict_organization_passes_validation(self):
        self.assertEqual(
            [],
            validate_chapter_content(
                {"knowledge_nodes": {"神學": ["會幕"]},
                 "organization": {"結構": ["重點"]}}
            ),
        )


if __name__ == "__main__":
    unittest.main()
