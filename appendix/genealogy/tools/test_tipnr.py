"""TIPNR 的離線解析、同名歧義與輸出測試。"""
from __future__ import annotations

import csv
import io
import unittest
from unittest.mock import patch

from appendix.genealogy.tools import tipnr as t


def person(unique: str, strong: str, refs: str, translated: str = "") -> t.TipnrPerson:
    form = t.TipnrForm(unique, strong, translated or unique.split("@")[0], t.parse_refs(refs))
    return t.TipnrPerson(unique, strong, "原始描述", "父 + 母", "", "", "子", "", "#摘要", "Male",
                         [form], set(form.refs))


def local(pid: str, name: str, reference: str = "", **extra) -> dict:
    return {"id": pid, "name": name, "names": [{"as": name, "ref": reference}], **extra}


class ReferencesTest(unittest.TestCase):
    def test_same_chapter_ranges_and_occurrence_suffixes(self):
        self.assertEqual(t.parse_refs("Gen.4.17a; Gen.4.17b; 18,20-22"),
                         {"Gen.4.17", "Gen.4.18", "Gen.4.20", "Gen.4.21", "Gen.4.22"})

    def test_abbreviated_chapter_and_full_range_end(self):
        self.assertEqual(t.parse_refs("1Ch.24.7-1Ch.24.9; 25.1,3–4; Neh.7.39"),
                         {"1Ch.24.7", "1Ch.24.8", "1Ch.24.9", "1Ch.25.1",
                          "1Ch.25.3", "1Ch.25.4", "Neh.7.39"})
        self.assertEqual(t.parse_refs("Num.13.8,16; Deu.32.44"),
                         {"Num.13.8", "Num.13.16", "Deu.32.44"})

    def test_cross_chapter_needs_known_lengths(self):
        counts = {("Gen", 1): 31, ("Gen", 2): 25}
        self.assertEqual(t.parse_refs("Gen.1.30-2.2", counts),
                         {"Gen.1.30", "Gen.1.31", "Gen.2.1", "Gen.2.2"})
        with self.assertRaises(ValueError):
            t.parse_refs("Gen.1.30-2.2")
        with self.assertRaises(ValueError):
            t.parse_refs("Gen.1.32-2.2", counts)
        with self.assertRaises(ValueError):
            t.parse_refs("Gen.1.30-2.26", counts)

    def test_lxx_namespace_and_psalm_title(self):
        self.assertEqual(t.parse_refs("LXX.Est.3.1; 7.9; Est.3.1; Psa.3.0"),
                         {"LXX.Est.3.1", "LXX.Est.7.9", "Est.3.1", "Psa.3.0"})

    def test_invalid_refs_fail_explicitly(self):
        for text in ("Gen.4.22-17", "Gen.4.1ff", "17", "Foo.1.1",
                     "Gen.1.1-Exo.1.2", "Gen.0.1", "Gen.1.0", "Gen.1.1; @"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                t.parse_refs(text)

    def test_chinese_multiple_segments(self):
        self.assertEqual(t.parse_chinese_refs("代上1:5-7,10,2:1-2；創4:1-3"),
                         {"1Ch.1.5", "1Ch.1.6", "1Ch.1.7", "1Ch.1.10",
                          "1Ch.2.1", "1Ch.2.2", "Gen.4.1", "Gen.4.2", "Gen.4.3"})
        self.assertEqual(t.parse_chinese_refs("太4:21, 太20:20"), {"Mat.4.21", "Mat.20.20"})
        with self.assertRaises(ValueError):
            t.parse_chinese_refs("未知1:1")


class ParserTest(unittest.TestCase):
    def test_person_fields_variants_link_column_and_total(self):
        source = "\n".join([
            "$==========PERSON(s)",
            "UnifiedName=uStrong\tDescription\tParents\tSiblings\tPartners\tOffspring\tTribe\tSummary\tType",
            "$========== PERSON(s)",
            "Alpha@Gen.1.1-=H0001G\t描述\t父 + 母\t兄\t配偶\t子\t族\t#摘要\tMale",
            "– Named\tAlpha@Gen.1.1-\tH0001G«H0001=原字\tAlpha\tGen.1.1a; Gen.1.1b\t\t@",
            "– Spelled\tBeta|Alpha@Gen.1.1-\tH0002H«H0002=原字\tBeta\t"
            "https://example.invalid/Gen.1.2\tGen.1.2-3",
            "– Total\tAlpha or Beta\tAlpha\tH0001G, H0002H\tGen.1.1ff",
            "@Brief= 不使用這一段",
            "$========== PLACE",
            "Place@Gen.1.1=H0003\t地點\t\t\t\t\t\t#摘要\tPlace",
            "– Named\tPlace@Gen.1.1\tH0003«H0003=原字\tPlace\tGen.1.1",
        ])
        people = t.parse_tipnr(source)
        self.assertEqual(len(people), 1)
        p = people[0]
        self.assertEqual((p.unique_name, p.ustrong, p.description, p.parents, p.siblings,
                          p.partners, p.offspring, p.tribe, p.summary, p.sex),
                         ("Alpha@Gen.1.1-", "H0001G", "描述", "父 + 母", "兄",
                          "配偶", "子", "族", "#摘要", "Male"))
        self.assertEqual(len(p.forms), 2)
        self.assertEqual(p.forms[1].dstrong, "H0002H")
        self.assertEqual(p.refs, {"Gen.1.1", "Gen.1.2", "Gen.1.3"})
        index = t.TipnrIndex(people)
        self.assertEqual(index.by_ref["Gen.1.1"], [p])
        self.assertNotIn("Gen.1.4", index.by_ref)
        self.assertIn("beta", index.by_name)

    def test_exact_strong_precedes_bounded_base_fallback(self):
        first = person("One@Gen.1.1", "H3077G", "Gen.1.1")
        second = person("Two@Gen.1.2", "H3077H", "Gen.1.2")
        index = t.TipnrIndex([first, second])
        self.assertEqual(index.match_step("H3077G", "Gen.1.1"), [first])
        # 完全相同的字碼本節沒有、本節另有同基本碼的人：以本節為準（個人後綴字母 STEP／TIPNR 不一定一致）
        self.assertEqual(index.match_step("H3077G", "Gen.1.2"), [second])
        # 本節也沒有同基本碼的人：仍回完全相同字碼的人
        self.assertEqual(index.match_step("H3077G", "Gen.1.5"), [first])
        self.assertEqual(index.match_step("H3077Z", "Gen.1.2"), [second])
        self.assertEqual(index.match_step("H3077Z", "Gen.1.3"), [])
        self.assertEqual(index.match_step("G3077", "Gen.1.2"), [])

    def test_exact_strong_absent_from_verse_yields_to_same_base_here(self):
        # 亞薩：STEP 的 H0623H 在 TIPNR 是另一個人（王下18:18），本節（代上6:39）是 H0623G
        other = person("Other@2Ki.18.18", "H0623H", "2Ki.18.18")
        singer = person("Singer@1Ch.6.39", "H0623G", "1Ch.6.39")
        index = t.TipnrIndex([other, singer])
        self.assertEqual(index.match_step("H0623H", "1Ch.6.39"), [singer])
        self.assertEqual(index.match_step("H0623H", "2Ki.18.18"), [other])

    def test_unpadded_strong_retains_person_suffix(self):
        adam = person("Adam@Gen.1.1", "H0121G", "Gen.1.1")
        other = person("Other@Gen.1.1", "H0121H", "Gen.1.1")
        index = t.TipnrIndex([adam, other])
        self.assertEqual(index.match_step("H121G", "Gen.1.1"), [adam])
        self.assertEqual(t.canonical_strong("G2"), "G0002")
        self.assertEqual(t.canonical_strong("H2148w"), "H2148w")
        self.assertEqual(t.base_strong("H121G"), "H0121")

    def test_fallback_uses_same_form_at_same_verse(self):
        first = person("One@Gen.1.1", "H0001G", "Gen.1.1")
        first.forms.append(t.TipnrForm("Other|One@Gen.1.1", "H0002G", "Other", {"Gen.1.2"}))
        first.refs.add("Gen.1.2")
        index = t.TipnrIndex([first])
        self.assertEqual(index.match_step("H0001Z", "Gen.1.2"), [])
        self.assertEqual(index.match_step("H0002Z", "Gen.1.2"), [first])

    def test_bad_ref_is_not_silently_discarded(self):
        source = ("$========== PERSON(s)\n"
                  "Alpha@Gen.1.1=H0001G\t描述\t父\t\t\t\t族\t#摘要\tMale\n"
                  "– Named\tAlpha@Gen.1.1\tH0001G«H0001=原字\tAlpha\tGen.1.1; typo")
        with self.assertRaisesRegex(ValueError, "第 3 行"):
            t.parse_tipnr(source)


class ComparisonTest(unittest.TestCase):
    def setUp(self):
        self.index = t.TipnrIndex([
            person("Same@Gen.1.1-", "H0001G", "Gen.1.1-2"),
            person("Same@Gen.1.3", "H0001H", "Gen.1.3"),
            person("Only@Gen.1.4", "H0002", "Gen.1.4"),
        ])
        self.english = {"同名": {"Same"}, "唯一": {"Only"}}

    def test_categories_keep_all_ambiguous_edges(self):
        people = [local("同甲", "同名", "創1:1"), local("同乙", "同名", "創1:2"),
                  local("同丙", "同名", "創1:1-3"), local("單一", "唯一", "創1:4"),
                  local("無英名", "某人", "創1:1"), local("異節", "同名", "創1:5")]
        c = t.compare_people(people, self.english, self.index)
        self.assertEqual([m.person["id"] for m in c.a], ["單一"])
        self.assertEqual(list(c.b), ["Same@Gen.1.1-"])
        self.assertEqual([m.person["id"] for m in c.b["Same@Gen.1.1-"]], ["同甲", "同乙", "同丙"])
        self.assertEqual([m.person["id"] for m in c.c], ["同丙"])
        self.assertEqual([m.person["id"] for m in c.d], ["無英名", "異節"])
        self.assertEqual(c.matches["同丙"].evidence["Same@Gen.1.3"], {"Gen.1.3"})
        text = t.concordance_tsv(c)
        self.assertEqual(text.splitlines()[0], t.ATTRIBUTION)
        rows = list(csv.reader(io.StringIO(text.split("\n", 1)[1]), delimiter="\t"))
        self.assertEqual(rows[1], ["單一", "Only@Gen.1.4", "H0002", "原始描述"])

    def test_aliases_normalization_and_all_relation_refs(self):
        index = t.TipnrIndex([person("Obed-edom@Gen.1.1", "H0001", "Gen.1.1")])
        english = {"別名": {"oBEDedOM"}}
        for key in ("parents", "spouses", "siblings", "kin", "descends"):
            with self.subTest(key=key):
                p = local("人物", "無名", "", **{key: [{"id": "親屬", "ref": "創1:1"}]})
                p["names"].append({"as": "別名", "ref": ""})
                c = t.compare_people([p], english, index)
                self.assertEqual(len(c.a), 1)
        self.assertEqual(t.normalize_name("Obed-edom"), t.normalize_name("OBED EDOM"))

    def test_matching_name_must_occur_in_referenced_verse(self):
        p = person("Alpha@Gen.1.1", "H0001", "Gen.1.1")
        p.forms.append(t.TipnrForm("Beta|Alpha@Gen.1.1", "H0002", "Beta", {"Gen.1.2"}))
        p.refs.add("Gen.1.2")
        c = t.compare_people([local("乙", "乙", "創1:1")], {"乙": {"Beta"}}, t.TipnrIndex([p]))
        self.assertEqual(len(c.d), 1)

    def test_reading_preserves_step_index_marker_order_and_repeats(self):
        reading = {"segments": [{"chapters": [{"book": "創", "n": 1, "verses": [
            {"v": 1, "t": [{"k": "p", "s": 8, "id": "後"},
                           {"k": "p", "s": 0, "id": "前"},
                           {"k": "r", "s": 1}, {"k": "p", "s": 2},
                           {"k": "p", "s": 4, "id": "前"}]},
            {"v": 2, "t": []},
        ]}]}]}
        word = t.step_names.Word(7, "原", "translit", "gloss", "H0001G", "HNpm", "person_m")
        with patch.object(t.step_names, "load_chapter", return_value={1: [word], 2: []}), \
                patch.object(t.step_names, "proper_nouns", side_effect=[[word], []]) as proper:
            text, stats = t.reading_tsv(reading, self.index)
        self.assertEqual(text.splitlines()[0], t.ATTRIBUTION)
        rows = list(csv.reader(io.StringIO(text.split("\n", 1)[1]), delimiter="\t"))
        self.assertEqual(len(rows), 2)
        self.assertEqual(len(rows[1]), 9)
        self.assertEqual(rows[1][:5], ["創1:1", "7", "translit", "H0001G", "Same@Gen.1.1-"])
        self.assertEqual(rows[1][-1], "前, 前, 後")
        self.assertEqual(stats, {"verses": 2, "words": 1, "unmatched": 0, "multiple": 0, "unidentified_markers": 1})
        self.assertEqual(proper.call_count, 2)
        self.assertEqual(proper.call_args.kwargs["kinds"], t.step_names.PERSON_KINDS)

    def test_missing_step_verse_fails(self):
        reading = {"segments": [{"chapters": [{"book": "創", "n": 1, "verses": [{"v": 1}]}]}]}
        with patch.object(t.step_names, "load_chapter", return_value={}):
            with self.assertRaisesRegex(ValueError, "創1:1"):
                t.reading_tsv(reading, self.index)


class CorpusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = t.load_tipnr()

    def test_person_count(self):
        self.assertGreater(len(self.index.persons), 2000)

    def test_jehoiada_disambiguated_strong(self):
        self.assertEqual([p.unique_name for p in self.index.by_dstrong["H3077G"]],
                         ["Jehoiada@2Sa.8.18-1Ch"])

    def test_jedaiah_in_chronicles_24_7(self):
        self.assertIn("Jedaiah@1Ch.24.7-Neh", [p.unique_name for p in self.index.by_ref["1Ch.24.7"]])

    def test_all_indices_have_exact_backing_evidence(self):
        for strong, people in self.index.by_dstrong.items():
            self.assertEqual(len(people), len({p.unique_name for p in people}))
            for p in people:
                self.assertTrue(any(f.dstrong == strong for f in p.forms))
        for ref, people in self.index.by_ref.items():
            self.assertEqual(len(people), len({p.unique_name for p in people}))
            for p in people:
                self.assertIn(ref, p.refs)

    def test_full_reading_output_keeps_all_step_names_and_marker_order(self):
        import json
        reading = json.loads((t.DATA / "reading.json").read_text(encoding="utf-8-sig"))
        text, stats = t.reading_tsv(reading, self.index)
        rows = list(csv.DictReader(io.StringIO(text.split("\n", 1)[1]), delimiter="\t"))
        expected = []
        for segment in reading["segments"]:
            for chapter in segment["chapters"]:
                book, number = chapter["book"], chapter["n"]
                for verse in chapter["verses"]:
                    ids = ", ".join(x["id"] for x in sorted(verse.get("t", []), key=lambda x: x["s"])
                                    if x.get("k") == "p" and x.get("id"))
                    for word in t.step_names.proper_nouns(book, number, verse["v"]):
                        expected.append((f"{book}{number}:{verse['v']}", str(word.index), word.strong, ids))
        self.assertEqual([(row["經節"], row["序"], row["dStrong"],
                           row["同一節我們標的人物 id（依 s 順序列出）"]) for row in rows], expected)
        self.assertEqual(len(rows), stats["words"])

    def test_main_writes_only_three_authorized_outputs(self):
        from contextlib import redirect_stdout
        with patch.object(t, "load_tipnr", return_value=self.index), \
                patch.object(t.Path, "write_text", autospec=True) as write, redirect_stdout(io.StringIO()):
            self.assertEqual(t.main(), 0)
        self.assertEqual({call.args[0] for call in write.call_args_list}, {
            t.BASE / "sources/tipnr_對照.tsv",
            t.DRAFT / "TIPNR_人物對照.md",
            t.DRAFT / "TIPNR_經節人名.tsv",
        })
        self.assertEqual(write.call_count, 3)
        for call in write.call_args_list:
            self.assertEqual(call.kwargs["encoding"], "utf-8")
            self.assertEqual(call.kwargs["newline"], "\n")

    def test_focus_is_bounded_and_includes_named_homonyms(self):
        for chinese, english in t.FOCUS.items():
            for p in t.focus_people(chinese, english, {}, self.index):
                self.assertTrue(any(t.in_focus(ref) for ref in p.refs))
        jehoiada = t.focus_people("耶何耶大", "Jehoiada", {}, self.index)
        self.assertEqual({p.unique_name for p in jehoiada},
                         {"Jehoiada@2Sa.8.18-1Ch", "Jehoiada@1Ch.27.34", "Joiada@Neh.12.10-"})
        self.assertFalse(t.in_focus("1Ch.9.1"))
        self.assertFalse(t.in_focus("LXX.1Ch.24.7"))
        self.assertTrue(t.in_focus("Neh.12.1"))


if __name__ == "__main__":
    unittest.main()
