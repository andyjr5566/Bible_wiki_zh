import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

UTIL_DIR = Path(__file__).resolve().parents[1]
if str(UTIL_DIR) not in sys.path:
    sys.path.insert(0, str(UTIL_DIR))

import check_existing_links as cel

INDEX = {
    "割禮": {"title": "割禮", "path": "link_folder/主題/割禮.md"},
    "約書亞": {"title": "約書亞", "path": "link_folder/人物/約書亞.md"},
}


def _accum(book, chapter):
    return (f"<!-- accumulation:{book}:{chapter}:start -->\n#### 第{chapter}章\n"
            f"- x\n<!-- accumulation:{book}:{chapter}:end -->\n")


class CorpusScanTests(unittest.TestCase):
    def _vault(self, tmp, *, circ_ch1=False):
        root = Path(tmp)
        (root / "06 約書亞記").mkdir(parents=True)
        (root / "06 約書亞記" / "第1章.md").write_text(
            "見 [[割禮]] 與 [[約書亞]]。", encoding="utf-8")
        (root / "06 約書亞記" / "第2章.md").write_text("見 [[割禮]]。", encoding="utf-8")
        (root / "link_folder" / "主題").mkdir(parents=True)
        circ = _accum("約書亞記", 1) if circ_ch1 else ""
        (root / "link_folder" / "主題" / "割禮.md").write_text(
            "# 割禮\n\n## 按書卷累積\n\n### 約書亞記\n" + circ + _accum("約書亞記", 2),
            encoding="utf-8")
        (root / "link_folder" / "人物").mkdir(parents=True)
        (root / "link_folder" / "人物" / "約書亞.md").write_text(
            "# 約書亞\n\n## 按書卷累積\n\n### 約書亞記\n" + _accum("約書亞記", 1),
            encoding="utf-8")
        return root

    def _run(self, root, **kw):
        buf = io.StringIO()
        with patch.object(cel, "ROOT", root), contextlib.redirect_stdout(buf):
            code = cel._run_corpus(dict(INDEX), **kw)
        return code, buf.getvalue()

    def test_all_flags_forward_orphan(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._vault(tmp)
            code, out = self._run(root)
            self.assertEqual(1, code)
            self.assertIn("割禮", out)
            self.assertIn("約書亞記第1章", out)
            self.assertNotIn("約書亞記第2章", out)  # 第2章連的割禮已補

    def test_all_passes_when_covered(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._vault(tmp, circ_ch1=True)
            code, out = self._run(root)
            self.assertEqual(0, code)
            self.assertIn("PASS", out)

    def test_book_scope_label(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._vault(tmp)
            _code, out = self._run(root, book="約書亞記")
            self.assertIn("約書亞記 全卷", out)

    def test_iter_chapter_files_orders_and_filters(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._vault(tmp)
            (root / "01 創世記").mkdir(parents=True)
            (root / "01 創世記" / "第1章.md").write_text("x", encoding="utf-8")
            (root / "06 約書亞記" / "全書目錄及綱要.md").write_text("x", encoding="utf-8")
            allf = [p.parent.name + "/" + p.name for p in cel.iter_chapter_files(root)]
            self.assertEqual(
                ["01 創世記/第1章.md", "06 約書亞記/第1章.md", "06 約書亞記/第2章.md"], allf)
            josh = [p.name for p in cel.iter_chapter_files(root, book="約書亞記")]
            self.assertEqual(["第1章.md", "第2章.md"], josh)


if __name__ == "__main__":
    unittest.main()
