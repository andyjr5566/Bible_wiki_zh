# -*- coding: utf-8 -*-
"""引句逐字回查的判定測試——這一關驗的是閘門驗不到的東西：引號裡的話出自哪裡。"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from util import check_quote_fidelity as cqf  # noqa: E402

BOOK = "創世記"
CHAPTER = 8


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class QuoteFidelityTests(unittest.TestCase):
    def _chapter(self, tmp, *, entry_yaml=None, organization=None, scripture_by_chapter=None):
        root = Path(tmp)
        tmp_dir = root / "01 創世記" / ".tmp" / f"第{CHAPTER}章"
        _write(root / "raw_data" / "ct.txt",
               "CT：『鴿子』原文字義是使者，神記念挪亞，水勢漸落。")
        _write(tmp_dir / "source_manifest.md",
               "| 來源 | 類型 | URL | raw_data 檔案 | 狀態 |\n"
               "|---|---|---|---|---|\n"
               "| ccbiblestudy CT | 逐節註解 | https://example.invalid/ct | raw_data/ct.txt | OK |\n")
        for chapter, text in (scripture_by_chapter or {CHAPTER: "1. 神記念挪亞和方舟裡的一切走獸牲畜。"}).items():
            _write(root / "raw_scripture" / BOOK / f"第{chapter}章.txt", text)
        if entry_yaml is not None:
            _write(tmp_dir / "entry_content" / "測試.yaml", entry_yaml)
        if organization is not None:
            _write(root / "01 創世記" / f"第{CHAPTER}章.md",
                   "## 本章知識節點\n\n### 主題\n\n## 本章整理\n\n" + organization)
        return root

    def test_verbatim_quote_passes_and_added_full_stop_is_caught(self):
        """最常見的飄移是截斷後自己補句號——來源沒有那個句號。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._chapter(
                tmp,
                entry_yaml='name: 測試\ndefinition: CT 說「『鴿子』原文字義是使者」。\n',
            )
            total, misses, _ = cqf.check_quotes(BOOK, CHAPTER, root=root)
            self.assertEqual((1, []), (total, misses))

        with tempfile.TemporaryDirectory() as tmp:
            root = self._chapter(
                tmp,
                entry_yaml='name: 測試\ndefinition: CT 說「『鴿子』原文字義是使者。」\n',
            )
            _total, misses, _ = cqf.check_quotes(BOOK, CHAPTER, root=root)
            self.assertEqual(1, len(misses))

    def test_excerpt_with_ellipsis_is_checked_fragment_by_fragment(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._chapter(
                tmp,
                entry_yaml='name: 測試\ndefinition: CT：「『鴿子』原文字義是使者⋯水勢漸落」\n',
            )
            _total, misses, _ = cqf.check_quotes(BOOK, CHAPTER, root=root)
            self.assertEqual([], misses)

        with tempfile.TemporaryDirectory() as tmp:
            root = self._chapter(
                tmp,
                entry_yaml='name: 測試\ndefinition: CT：「『鴿子』原文字義是使者⋯水勢暴漲不退」\n',
            )
            _total, misses, _ = cqf.check_quotes(BOOK, CHAPTER, root=root)
            self.assertEqual(1, len(misses))

    def test_wikilinks_inside_a_quote_do_not_break_the_match(self):
        """章 md 的引句常夾著 [[目標|別名]]，比對前必須還原成別名。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._chapter(
                tmp,
                organization="### 一、標題（v1-3）\n\n經文說「[[神的記念|神記念]]挪亞和方舟裡的一切走獸牲畜」。\n",
            )
            _total, misses, _ = cqf.check_quotes(BOOK, CHAPTER, root=root)
            self.assertEqual([], misses)

    def test_scripture_corpus_covers_the_whole_book_but_commentary_only_this_chapter(self):
        """引用前面章節的經文是正常的；引用相鄰章的註釋才是要抓的那一型。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._chapter(
                tmp,
                entry_yaml='name: 測試\ndefinition: 前章說「地上的水勢甚大，天下的高山都淹沒了」。\n',
                scripture_by_chapter={
                    CHAPTER: "1. 神記念挪亞和方舟裡的一切走獸牲畜。",
                    7: "19. 地上的水勢甚大，天下的高山都淹沒了。",
                },
            )
            _total, misses, _ = cqf.check_quotes(BOOK, CHAPTER, root=root)
            self.assertEqual([], misses)

    def test_a_verse_quoted_from_another_book_is_verifiable(self):
        """KC 申2 引提後4:7。別卷經文是正當引用，語料限制成本卷會把它報成查無出處。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._chapter(
                tmp,
                entry_yaml="name: 測試\ndefinition: KC 引保羅的話「那美好的仗我已經打過了」。\n",
            )
            _write(root / "raw_scripture" / "提摩太後書" / "第4章.txt",
                   "7. 那美好的仗我已經打過了，當跑的路我已經跑盡了。")
            _total, misses, _ = cqf.check_quotes(BOOK, CHAPTER, root=root)
            self.assertEqual([], misses)

    def test_excerpt_whose_fragments_are_all_short_is_still_checked(self):
        """「因我已將⋯賜給⋯為業」：碎片全短於門檻時，無從判斷不等於查無出處。"""
        verse = {CHAPTER: "5. 因我已將西珥山賜給以掃為業。"}
        with tempfile.TemporaryDirectory() as tmp:
            root = self._chapter(
                tmp,
                entry_yaml="name: 測試\ndefinition: 三次都用「因我已將⋯賜給⋯為業」。\n",
                scripture_by_chapter=verse,
            )
            _total, misses, _ = cqf.check_quotes(BOOK, CHAPTER, root=root)
            self.assertEqual([], misses)

        with tempfile.TemporaryDirectory() as tmp:
            root = self._chapter(
                tmp,
                entry_yaml="name: 測試\ndefinition: 三次都用「因我已買⋯賜給⋯為業」。\n",
                scripture_by_chapter=verse,
            )
            _total, misses, _ = cqf.check_quotes(BOOK, CHAPTER, root=root)
            self.assertEqual(1, len(misses))

    def test_excerpt_ending_in_an_ellipsis_still_matches(self):
        """以 ⋯ 結尾的引句只切得出一段；用段數判會把整句漏掉（申4 實測回歸）。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._chapter(
                tmp,
                entry_yaml="name: 測試\ndefinition: 經文說「神記念挪亞和方舟裡的一切走獸⋯」\n",
            )
            _total, misses, _ = cqf.check_quotes(BOOK, CHAPTER, root=root)
            self.assertEqual([], misses)

    def test_yaml_folded_scalars_are_not_false_positives(self):
        """safe_dump 的折行會在長句中插入反斜線與續行縮排；必須解析 yaml 而不是正則。"""
        import yaml as yaml_module
        with tempfile.TemporaryDirectory() as tmp:
            long_quote = ("CT：「『鴿子』原文字義是使者」 "
                          + "and the dove found no resting place for her foot " * 4)
            payload = yaml_module.safe_dump(
                {"name": "測試", "definition": long_quote},
                allow_unicode=True, sort_keys=False, width=40, default_style='"',
            )
            self.assertIn("\\", payload, "此測試需要 yaml 真的折行才有意義")
            root = self._chapter(tmp, entry_yaml=payload)
            _total, misses, _ = cqf.check_quotes(BOOK, CHAPTER, root=root)
            self.assertEqual([], misses)

    def test_enumeration_brackets_are_not_treated_as_quotes(self):
        """中文用「」兼作強調與並列（「過去／所要去」），那不是宣稱逐字引用。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._chapter(tmp, entry_yaml='name: 測試\ndefinition: 兩種用法是「過去／所要去的」。\n')
            total, misses, _ = cqf.check_quotes(BOOK, CHAPTER, root=root)
            self.assertEqual((0, []), (total, misses))


if __name__ == "__main__":
    unittest.main()
