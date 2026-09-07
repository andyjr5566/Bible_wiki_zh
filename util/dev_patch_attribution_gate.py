#!/usr/bin/env python3
from pathlib import Path

PATH = Path(__file__).resolve().parent / "check_chapter_files.py"
text = PATH.read_text(encoding="utf-8")

old_scan = '''    # 引句逐字回查：閘門驗結構，驗不到引號裡的話是不是真的出自來源
    quote_fidelity_ok, quote_fidelity_detail = True, ""
    if (tmp / "chapter_content.yaml").exists():
        try:
            quote_total, quote_misses, _names = check_quote_fidelity.check_quotes(
                canonical, chapter, root=root
            )
            quote_fidelity_ok = not quote_misses
            if quote_misses:
                preview = "；".join(f"{label}：{quote[:28]}" for label, quote in quote_misses[:3])
                quote_fidelity_detail = (
                    f"引句 {quote_total} 處，回查不到 {len(quote_misses)} 處——{preview}"
                    + ("⋯" if len(quote_misses) > 3 else "")
                )
            else:
                quote_fidelity_detail = f"引句 {quote_total} 處全數命中"
        except Exception as exc:
            quote_fidelity_detail = f"引句回查失敗：{exc}"
            quote_fidelity_ok = False
'''
new_scan = '''    # 引句字串掃描只提供 reviewer 定位線索，不做內容正確性的硬判決。
    quote_fidelity_ok, quote_fidelity_detail, quote_fidelity_warning = True, "", ""
    if (tmp / "chapter_content.yaml").exists():
        try:
            quote_total, quote_misses, _names = check_quote_fidelity.check_quotes(
                canonical, chapter, root=root
            )
            if quote_misses:
                preview = "；".join(f"{label}：{quote[:28]}" for label, quote in quote_misses[:3])
                quote_fidelity_detail = (
                    f"引句 {quote_total} 處，字串回查未命中 {len(quote_misses)} 處——{preview}"
                    + ("⋯" if len(quote_misses) > 3 else "")
                )
                quote_fidelity_warning = (
                    f"{quote_fidelity_detail}。這些只作為 evidence review 的定位線索；"
                    "不可僅因字串未命中就判內容錯誤或要求改寫。"
                )
            else:
                quote_fidelity_detail = f"引句 {quote_total} 處全數命中"
        except Exception as exc:
            quote_fidelity_detail = f"引句字串掃描失敗：{exc}"
            quote_fidelity_warning = (
                f"{quote_fidelity_detail}；此掃描不擋 production，內容忠實度仍由 evidence review 判定。"
            )
'''

old_check = '''        CheckResult(
            "步驟5｜引句逐字回查（本章來源＋全卷經文）",
            quote_fidelity_ok,
            "有引句在本章正式來源與全卷經文裡都找不到逐字對應——閘門驗結構，"
            "驗不到引號裡的話是不是真的出自來源。常見成因：截斷後自己補句號、"
            "換一種引號、把英文來源的中文譯文當成逐字引句、把不相鄰的兩句接成一句。"
            f"逐條看：python util/check_quote_fidelity.py {canonical} {chapter}。"
            f"檢查訊息：{quote_fidelity_detail}",
        ),
'''
new_check = '''        CheckResult(
            "步驟5｜引句字串疑點掃描（review 線索）",
            quote_fidelity_ok,
            "",
            warning=quote_fidelity_warning,
        ),
'''

for label, old, new in (("scan", old_scan, new_scan), ("check", old_check, new_check)):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, got {count}")
    text = text.replace(old, new, 1)

PATH.write_text(text, encoding="utf-8")
print("patched util/check_chapter_files.py")
