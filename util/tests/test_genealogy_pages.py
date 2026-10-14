"""appendix/genealogy 的頁面產生器：資料驗證，以及「從亞當到耶穌」的產物有沒有跟資料同步。

產物（Obsidian 頁與網站用的 genealogy.json／verses.json）都是由 YAML 產生的；
改了 YAML 卻忘了重新產生，這裡會失敗。
"""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
GENEALOGY_DIR = ROOT_DIR / "appendix" / "genealogy"
LINEAGE_DIR = GENEALOGY_DIR / "亞當到耶穌"
SITE_DATA = ROOT_DIR / "appendix" / "website" / "全聖經" / "亞當到耶穌" / "src" / "data"
PAGE = ROOT_DIR / "appendix" / "亞當到耶穌的家譜.md"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_genealogy", GENEALOGY_DIR / "build_genealogy.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("build_genealogy", module)
    spec.loader.exec_module(module)
    return module


def normalize(text: str) -> str:
    return text.replace("\r\n", "\n")


class LineagePageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_builder()
        cls.builder = cls.module.LineageBuilder(LINEAGE_DIR)

    def test_data_is_valid(self):
        self.assertEqual(self.builder.errors, [], "\n".join(self.builder.errors[:10]))
        self.assertEqual(len(self.builder.lines["馬太"]), 64)
        self.assertEqual(len(self.builder.lines["路加"]), 76)

    def test_obsidian_page_is_up_to_date(self):
        self.assertEqual(self.builder.errors, [])
        generated = normalize(self.builder.render())
        self.assertEqual(generated, normalize(PAGE.read_text(encoding="utf-8")),
                         "appendix/亞當到耶穌的家譜.md 與資料不同步，請跑 python appendix/genealogy/build_genealogy.py 亞當到耶穌")

    def test_site_data_is_up_to_date(self):
        self.assertEqual(self.builder.errors, [])
        with tempfile.TemporaryDirectory() as tmp:
            self.builder.export(Path(tmp))
            for name in ("genealogy.json", "verses.json"):
                generated = normalize((Path(tmp) / name).read_text(encoding="utf-8"))
                committed = normalize((SITE_DATA / name).read_text(encoding="utf-8"))
                self.assertEqual(generated, committed,
                                 f"網站的 {name} 與資料不同步，請跑 build_genealogy.py 亞當到耶穌 --export-json <網站 src/data>")


class SeriesPagesTests(unittest.TestCase):
    def test_ready_series_pages_validate(self):
        import yaml
        module = load_builder()
        series = yaml.safe_load((GENEALOGY_DIR / "series.yaml").read_text(encoding="utf-8"))
        for item in series.get("pages", []):
            if not item.get("ready"):
                continue
            with self.subTest(page=item["data"]):
                self.assertTrue(module.build_page(item["data"], check=True, print_summary=False))


if __name__ == "__main__":
    unittest.main()
