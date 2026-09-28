# -*- coding: utf-8 -*-
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "util"))

import run_chapter_manual as manual  # noqa: E402
from model_client import ModelValidationError  # noqa: E402


class PromptNeutralityTests(unittest.TestCase):
    def test_removes_quote_style_prescriptions_but_keeps_attribution_duty(self):
        raw = (
            "前文\n"
            "- 所有輸出用繁體中文，但「」是逐字宣告而不是強調記號：引用英文來源"
            "（KingComments、BibleHub）時只有兩種寫法——①英文原句放進「」，"
            "緊接著在（）內附上繁體中文翻譯；②具名轉述並完全不加引號，"
            "且要把那句話的內容講完，不可縮成「KC 也談到這點」的摘要體。"
            "**不可把中譯放進「」**：來源說的不是中文，那等於偽造逐字引句，"
            "check_quote_fidelity 會逐條回查並報出。也不可整段貼英文原文。"
            "只有原文用字本身是重點時，才以括號附註原文詞。\n"
            "- 內容只能出自上面的經文與來源；整合重點而非搬運來源全文。\n"
            "- 引述註釋請「直接引原話」並標明是哪一家（CT／GT／KC／BH 或 GT 內的"
            "《丁道爾》《舊約背景註釋》《中文聖經註釋》《精讀本》等），不要改寫成"
            "「CT指出…」的轉述體，也不可把甲家的話掛到乙家名下——已知實例："
            "《舊約背景註釋》的古代近東材料被誤植為 KC、CT 的靈意註解被誤植為 KC。"
            "某一家在某處沒有說法，就不要替他生一個。\n"
            "後文\n"
        )
        cleaned = manual.neutralize_authoring_prompt(raw)
        self.assertIn("- 所有輸出用繁體中文。", cleaned)
        self.assertIn("英文原句放進「」", cleaned)
        self.assertIn("註釋來源歸屬必須正確", cleaned)
        self.assertNotIn("只有兩種寫法", cleaned)
        self.assertNotIn("直接引原話", cleaned)
        self.assertNotIn("不要改寫成", cleaned)
        self.assertNotIn("check_quote_fidelity 會逐條回查", cleaned)

    def test_unrelated_prompt_is_unchanged(self):
        raw = "內容只能出自本章經文與正式來源；來源有分歧時並陳。"
        self.assertEqual(raw, manual.neutralize_authoring_prompt(raw))

    def test_prompt_capture_writes_the_neutralized_prompt(self):
        raw = (
            "- 所有輸出用繁體中文，但「」是逐字宣告而不是強調記號：引用英文來源"
            "（KingComments、BibleHub）時只有兩種寫法——①英文原句放進「」，"
            "緊接著在（）內附上繁體中文翻譯；②具名轉述並完全不加引號，"
            "且要把那句話的內容講完，不可縮成「KC 也談到這點」的摘要體。"
            "**不可把中譯放進「」**：來源說的不是中文，那等於偽造逐字引句，"
            "check_quote_fidelity 會逐條回查並報出。也不可整段貼英文原文。"
            "只有原文用字本身是重點時，才以括號附註原文詞。\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            cap = manual.PromptCapture(Path(tmp), "chapter_content")
            with self.assertRaises(ModelValidationError):
                cap(raw)
            text = (Path(tmp) / "chapter_content.prompt.md").read_text(encoding="utf-8")
            self.assertEqual(manual._M6_QUOTE_RULE, text)

    def test_m3_reply_format_becomes_per_entry_files(self):
        raw = (
            "【輸出格式範例——照此結構輸出一個 YAML 陣列】\n- name: 施恩座（kapporet）\n"
            "【輸出】只輸出一個 YAML 陣列（每個元素以 - 開頭），不要任何說明文字。"
        )
        cleaned = manual.neutralize_authoring_prompt(raw)
        self.assertNotIn("只輸出一個 YAML 陣列", cleaned)
        self.assertIn("entry_content/<name>.yaml", cleaned)
        self.assertIn("每個條目一個檔", cleaned)

    def test_m6_reply_format_becomes_chapter_content_yaml(self):
        delim = manual.rc.ORG_DELIM
        raw = (
            "organization（本章整理）用「裸 markdown」直接寫在分隔線之後"
            "（輸出格式見文末）——不是 YAML 欄位、不用縮排、不用任何跳脫，"
            "mermaid／表格／callout 照一般 markdown 寫即可。\n\n"
            f"【輸出格式，極重要】輸出分成兩段，中間用單獨一行「{delim}」隔開：\n"
            "第一段：只含 book/chapter/knowledge_nodes 的 YAML。\n"
            "```yaml\nbook: 約書亞記\nchapter: 12\n"
            "knowledge_nodes:\n  神學: [山上的樣式]\n```\n"
            f"{delim}\n### 標題一（v1-6）\n文字…\n\n"
            "### 標題二（v7-13）\n文字…\n\n"
            "payload 欄位：book, chapter。"
        )
        cleaned = manual.neutralize_authoring_prompt(raw)
        self.assertNotIn(delim, cleaned)
        self.assertNotIn("裸 markdown", cleaned)
        self.assertIn("organization: |", cleaned)
        self.assertIn(".tmp/第12章/chapter_content.yaml", cleaned)
        self.assertIn("book: 約書亞記", cleaned)
        self.assertTrue(cleaned.endswith("payload 欄位：book, chapter。"))


if __name__ == "__main__":
    unittest.main()
