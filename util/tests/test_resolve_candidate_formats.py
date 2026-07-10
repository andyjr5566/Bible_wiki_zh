import sys
import tempfile
import unittest
from pathlib import Path

UTIL_DIR = Path(__file__).resolve().parents[1]
if str(UTIL_DIR) not in sys.path:
    sys.path.insert(0, str(UTIL_DIR))

import yaml

from resolve_link_candidates import (
    base_name,
    build_plan_document,
    find_in_index,
    parse_candidates_md,
    parse_candidates_yaml,
    resolve,
)

MD = """\
## 人物
- 以撒 → 人物

## 原文
- 施恩座（kapporet） → 原文 — 名字含義

## 其他
- 某普通詞 → 普通詞
- 怪東西 → 亂分類
"""

YAML_DATA = {
    "book": "創世記",
    "chapter": 26,
    "candidates": [
        {"name": "以撒", "type": "人物", "section": "人物"},
        {"name": "施恩座（kapporet）", "type": "原文", "section": "原文", "evidence": "名字含義"},
        {"name": "某普通詞", "type": "普通詞", "section": "其他"},
        {"name": "怪東西", "type": "亂分類", "section": "其他"},
    ],
}

INDEX = {
    "以撒": {
        "title": "以撒",
        "type": "人物",
        "path": "link_folder/人物/以撒.md",
        "secondary_types": [],
    }
}


class CandidateFormatEquivalenceTests(unittest.TestCase):
    def _plan_document(self, candidates, root):
        plan = resolve(candidates, INDEX, "創世記", "26", root=root, homonyms={})
        return build_plan_document(plan, "創世記", 26)

    def test_md_and_yaml_produce_identical_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entry = root / "link_folder" / "人物" / "以撒.md"
            entry.parent.mkdir(parents=True)
            entry.write_text(
                "# 以撒\n\n## 定義\n\n內容\n\n## 按書卷累積\n\n### 創世記\n"
                "<!-- accumulation:創世記:26:start -->\n#### 第26章\n"
                "- 本章重點：x\n- 與本章關聯：y\n"
                "<!-- accumulation:創世記:26:end -->\n\n## 來源依據\n\n- CT\n",
                encoding="utf-8",
            )
            from_md = self._plan_document(parse_candidates_md(MD), root)
            from_yaml = self._plan_document(parse_candidates_yaml(YAML_DATA), root)
            self.assertEqual(from_md, from_yaml)

    def test_plan_buckets_are_as_expected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entry = root / "link_folder" / "人物" / "以撒.md"
            entry.parent.mkdir(parents=True)
            entry.write_text(
                "# 以撒\n\n## 定義\n\n內容\n\n## 按書卷累積\n\n### 創世記\n"
                "<!-- accumulation:創世記:26:start -->\n#### 第26章\n"
                "- 本章重點：x\n- 與本章關聯：y\n"
                "<!-- accumulation:創世記:26:end -->\n\n## 來源依據\n\n- CT\n",
                encoding="utf-8",
            )
            doc = self._plan_document(parse_candidates_yaml(YAML_DATA), root)
            self.assertEqual(["以撒"], [e["name"] for e in doc["A_use_directly"]])
            self.assertEqual(["施恩座（kapporet）"], [e["name"] for e in doc["C_new_formal"]])
            self.assertEqual(
                "link_folder/原文/施恩座（kapporet）.md",
                doc["C_new_formal"][0]["target_path"],
            )
            self.assertEqual(["某普通詞"], [e["name"] for e in doc["E_skip"]])
            self.assertEqual(["怪東西"], [e["name"] for e in doc["D_new_candidate"]])

    def test_yaml_accepts_suggested_type_alias_key(self):
        candidates = parse_candidates_yaml({
            "candidates": [{"name": "測試", "suggested_type": "神學"}]
        })
        self.assertEqual("神學", candidates[0]["suggested_type"])

    def test_yaml_rejects_missing_fields(self):
        with self.assertRaises(ValueError):
            parse_candidates_yaml({"candidates": [{"name": "只有名字"}]})

    def test_md_and_yaml_candidate_dicts_share_shape(self):
        md_item = parse_candidates_md("## s\n- 甲 → 人物 — 依據x")[0]
        yaml_item = parse_candidates_yaml({
            "candidates": [{"name": "甲", "type": "人物", "evidence": "依據x"}]
        })[0]
        self.assertEqual(set(md_item), set(yaml_item))
        for field in ("name", "suggested_type", "evidence"):
            self.assertEqual(md_item[field], yaml_item[field])


class TranslitBaseNameMatchTests(unittest.TestCase):
    """裸中文候選（皂莢木）須匹配既有音譯條目（皂莢木（atzei shittim）），
    否則每章重複詞被誤判為新條目、覆蓋既有累積。"""

    INDEX = {
        "皂莢木（atzei shittim）": {
            "title": "皂莢木（atzei shittim）",
            "type": "原文",
            "path": "link_folder/原文/皂莢木（atzei shittim）.md",
            "secondary_types": [],
        },
        "銅網（sevakah）": {
            "title": "銅網（sevakah）",
            "type": "原文",
            "path": "link_folder/原文/銅網（sevakah）.md",
            "secondary_types": [],
        },
    }

    def test_base_name_strips_translit_suffix(self):
        self.assertEqual("皂莢木", base_name("皂莢木（atzei shittim）"))
        self.assertEqual("皂莢木", base_name("皂莢木"))
        self.assertEqual("銅", base_name("銅(nechosheth)"))

    def test_bare_candidate_matches_translit_entry(self):
        match_type, entry, title = find_in_index("皂莢木", self.INDEX)
        self.assertEqual("base", match_type)
        self.assertEqual("皂莢木（atzei shittim）", title)

    def test_base_match_does_not_confuse_prefix_words(self):
        # 「銅」不得誤配到「銅網（sevakah）」（基名是「銅網」不是「銅」）
        match_type, entry, title = find_in_index("銅", self.INDEX)
        self.assertEqual("not_found", match_type)

    def test_recurring_word_routes_to_accumulation_not_new(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entry = root / "link_folder" / "原文" / "皂莢木（atzei shittim）.md"
            entry.parent.mkdir(parents=True)
            entry.write_text(
                "# 皂莢木（atzei shittim）\n\n## 定義\n\n木材\n\n## 按書卷累積\n\n"
                "### 出埃及記\n<!-- accumulation:出埃及記:25:start -->\n#### 第25章\n"
                "- 本章重點：x\n- 與本章關聯：y\n"
                "<!-- accumulation:出埃及記:25:end -->\n\n## 來源依據\n\n- CT\n",
                encoding="utf-8",
            )
            candidates = parse_candidates_yaml({
                "candidates": [{"name": "皂莢木", "type": "原文"}]
            })
            plan = resolve(candidates, self.INDEX, "出埃及記", "27", root=root, homonyms={})
            self.assertEqual([], [e["name"] for e in plan["C_new_formal"]])
            self.assertEqual(["皂莢木"], [e["name"] for e in plan["B_needs_update"]])
            self.assertEqual(
                "皂莢木（atzei shittim）", plan["B_needs_update"][0]["existing_title"]
            )


if __name__ == "__main__":
    unittest.main()
