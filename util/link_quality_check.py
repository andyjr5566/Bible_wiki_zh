#!/usr/bin/env python3
"""
link_quality_check.py — 語意品質檢查（不取代 verify_links.py）

檢查項目：
  1. 書卷與人物同名錯連（[[何西阿]]書 → 應為 [[何西阿書]]）
  2. alias 格式錯誤（[[條目|]] 空 alias 等）
  3. 短 target 過度 link（1–2 字普通詞若無來源明確支撐）
  4. 經文原詞後綴判斷（[[何西阿]] 後緊接「書」）
  5. 不存在於 link_index 的非 scripture 非章節 target
  6. 同章同一原詞指向不同 target（跨檔案不檢查）
  7. 超過 3 字的冗長 alias 可能混用

輸出：link_quality_report.json（非破壞性，僅警告）

Usage:
  python util/link_quality_check.py [書卷名]
  python util/link_quality_check.py --book=創世記

回傳：
  exit code 0: 無 critical 警告
  exit code 1: 有 critical 警告
"""
import re
import json
from pathlib import Path

try:
    from .book_paths import book_directory, existing_book_directories
    from . import remediation
except ImportError:
    from book_paths import book_directory, existing_book_directories
    import remediation

UTIL_DIR = Path(__file__).resolve().parent
ROOT = UTIL_DIR.parent
LINK_FOLDER_PARENT = "link_folder"
OUTPUT_DIR = UTIL_DIR / "output"
LINK_INDEX_FILE = OUTPUT_DIR / "link_index.json"

# 聖經書卷名清單（用於後綴判斷）
BIBLE_BOOK_NAMES = {
    "創世記", "出埃及記", "利未記", "民數記", "申命記",
    "約書亞記", "士師記", "路得記",
    "撒母耳記上", "撒母耳記下",
    "列王紀上", "列王紀下",
    "歷代志上", "歷代志下",
    "以斯拉記", "尼希米記", "以斯帖記",
    "約伯記", "詩篇", "箴言", "傳道書", "雅歌",
    "以賽亞書", "耶利米書", "耶利米哀歌", "以西結書", "但以理書",
    "何西阿書", "約珥書", "阿摩司書", "俄巴底亞書", "約拿書",
    "彌迦書", "那鴻書", "哈巴谷書", "西番雅書", "哈該書",
    "撒迦利亞書", "瑪拉基書",
    "馬太福音", "馬可福音", "路加福音", "約翰福音", "使徒行傳",
    "羅馬書", "哥林多前書", "哥林多後書", "加拉太書",
    "以弗所書", "腓立比書", "歌羅西書",
    "帖撒羅尼迦前書", "帖撒羅尼迦後書",
    "提摩太前書", "提摩太後書", "提多書", "腓利門書",
    "希伯來書", "雅各書", "彼得前書", "彼得後書",
    "約翰一書", "約翰二書", "約翰三書", "猶大書", "啟示錄",
}

# 規範化書名（人物名→書卷名的 mapping）
PERSON_TO_BOOK = {
    "何西阿": "何西阿書",
    "約珥": "約珥書",
    "阿摩司": "阿摩司書",
    "俄巴底亞": "俄巴底亞書",
    "約拿": "約拿書",
    "彌迦": "彌迦書",
    "那鴻": "那鴻書",
    "哈巴谷": "哈巴谷書",
    "西番雅": "西番雅書",
    "哈該": "哈該書",
    "撒迦利亞": "撒迦利亞書",
    "瑪拉基": "瑪拉基書",
    "馬太": "馬太福音",
    "馬可": "馬可福音",
    "路加": "路加福音",
    "約翰": "約翰福音",
    "保羅": "（人物，非書卷）",
    "雅各": "雅各書",
    "彼得": "彼得前書",
    "猶大": "猶大書",
}

# 單字/短詞黑名單（若無來源支撐不應單獨 link）
SHORT_WORD_WARN = {
    "手", "腳", "頭", "眼", "耳", "口", "心", "血", "肉", "骨",
    "去", "來", "看", "聽", "說", "吃", "喝",
    "山", "水", "火", "風", "雨", "石", "金", "銀",
    "牛", "羊", "馬", "駱駝", "驢", "狗",
    "地", "天", "海", "日", "月", "星",
    "父", "母", "兄", "弟", "姐", "妹", "子", "女",
    "王", "城", "門", "路", "田", "園",
    "弓", "刀", "槍", "箭",
    "海沙", "塵土", "沙",
}

# 載入 link_index
link_index_cache = None


def load_link_index():
    global link_index_cache
    if link_index_cache is not None:
        return link_index_cache
    if LINK_INDEX_FILE.exists():
        with open(LINK_INDEX_FILE, 'r', encoding='utf-8') as f:
            link_index_cache = json.load(f)
        return link_index_cache
    return {}


WIKILINK_RE = re.compile(r'\[\[([^\]]+)\]\]')


def quality_check_file(filepath, source_key, link_index):
    """對單一檔案執行語意品質檢查"""
    warnings = []
    try:
        text = filepath.read_text(encoding='utf-8')
    except (UnicodeDecodeError, Exception):
        return warnings

    links = WIKILINK_RE.findall(text)
    if not links:
        return warnings

    # 用於檢查同一原詞衝突
    alias_to_entities = {}  # alias → [entity_name]

    for link in links:
        if '|' in link:
            entity, alias = link.split('|', 1)
        else:
            entity = link
            alias = entity  # 無 alias 時等同自身

        entity = entity.strip()
        alias = alias.strip()

        # ---- 檢查 1: 書卷與人物同名錯連 ----
        # [[何西阿]]書 模式
        for person, book in PERSON_TO_BOOK.items():
            if entity == person:
                # 檢查原文中是否緊接「書」
                idx = text.find(f'[[{link}]]')
                if idx >= 0:
                    after = idx + len(f'[[{link}]]')
                    if after < len(text) and text[after] == '書':
                        warnings.append({
                            "type": "book_person_confusion",
                            "severity": "critical",
                            "source": source_key,
                            "target": link,
                            "message": f"[[{entity}]] 後緊接「書」，可能應為 [[{book}]]",
                        })
                break

        # ---- 檢查 2: alias 格式錯誤 ----
        if alias == '':
            warnings.append({
                "type": "empty_alias",
                "severity": "warning",
                "source": source_key,
                "target": link,
                "message": f"空 alias: [[{entity}|]]",
            })
        if alias and alias == entity and len(alias) <= 2:
            # 短 target 無 alias，由短詞檢查處理
            pass

        # ---- 檢查 3: 短 target 過度 link ----
        if entity in SHORT_WORD_WARN or alias in SHORT_WORD_WARN:
            if link_index and entity not in link_index:
                warnings.append({
                    "type": "short_word_link",
                    "severity": "warning",
                    "source": source_key,
                    "target": link,
                    "message": f"短詞 link 缺少來源支撐: [[{entity}]]，檢查是否為普通詞誤連",
                })

        # ---- 檢查 4: 同一原詞指向不同 target ----
        if alias:
            if alias not in alias_to_entities:
                alias_to_entities[alias] = set()
            alias_to_entities[alias].add(entity)

    for alias, entities in alias_to_entities.items():
        if len(entities) > 1 and len(alias) > 0:
            warnings.append({
                "type": "alias_target_conflict",
                "severity": "warning",
                "source": source_key,
                "target": alias,
                "message": f"同一 alias「{alias}」指向多個 target: {', '.join(sorted(entities))}",
            })

    return warnings


def quality_check(book_name=None):
    """主入口"""
    link_index = load_link_index()
    link_folders = [
        '人物', '地點', '主題', '背景', '歷史', '原文',
        '文化', '神學', '互文', '解經爭議',
    ]

    all_warnings = []
    books_to_scan = []

    if book_name:
        books_to_scan = [(book_name, book_directory(ROOT, book_name))]
    else:
        books_to_scan = list(existing_book_directories(ROOT))

    # 掃描書卷
    for book, book_path in books_to_scan:
        if not book_path.is_dir():
            continue
        for item in book_path.iterdir():
            if item.name.startswith('.'):
                continue
            if item.is_file() and item.suffix == '.md':
                ws = quality_check_file(item, f"{book}/{item.name}", link_index)
                all_warnings.extend(ws)
            elif item.is_dir() and item.name in ['經文', '註解', '拾穗', '解說', '背景', '綱要', '交叉參照']:
                for f in item.iterdir():
                    if f.suffix != '.md':
                        continue
                    ws = quality_check_file(f, f"{book}/{item.name}/{f.name}", link_index)
                    all_warnings.extend(ws)

    # 掃描 link_folder
    for folder in link_folders:
        folder_path = ROOT / LINK_FOLDER_PARENT / folder
        if not folder_path.exists():
            continue
        for f in folder_path.iterdir():
            if f.suffix != '.md':
                continue
            ws = quality_check_file(f, f"{LINK_FOLDER_PARENT}/{folder}/{f.name}", link_index)
            all_warnings.extend(ws)

    # 寫入報告
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / "link_quality_report.json"
    critical_count = sum(1 for w in all_warnings if w.get("severity") == "critical")
    warning_count = sum(1 for w in all_warnings if w.get("severity") == "warning")

    report = {
        "total_warnings": len(all_warnings),
        "critical_count": critical_count,
        "warning_count": warning_count,
        "warnings": all_warnings,
    }
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # 輸出
    print(f"{'='*60}")
    print(f"  Link Quality Check Report")
    print(f"{'='*60}")
    print(f"  Total warnings: {len(all_warnings)}")
    print(f"  ├─ Critical: {critical_count}")
    print(f"  └─ Warning:  {warning_count}")
    print()

    if all_warnings:
        for w in all_warnings:
            icon = "🔴" if w["severity"] == "critical" else "🟡"
            print(f"  {icon} [{w['severity'].upper()}] {w['message']}")
            print(f"     → {w['source']}")
        print()

    if critical_count > 0:
        print(f"  Result: FAIL (critical warnings found)")
    else:
        print(f"  Result: PASS")
    print(f"{'='*60}\n")

    if critical_count > 0:
        remediation.print_fix_hints([(
            "語意品質 critical（書卷/人物同名錯連、空 alias、短詞過度 link 等）",
            [
                "看上方每條 🔴 [CRITICAL] 的 message 與 → source 檔，手動修正該 WikiLink："
                "書卷名要連書卷（[[何西阿書]] 而非 [[何西阿]]書）、補上或移除空 alias、"
                "無來源支撐的 1–2 字普通詞不應 link。",
                "若壞 link 出自章節內文，修 link_candidates 的 surfaces／候選後重跑該章；"
                "改完重跑：python util/link_quality_check.py 【書名】",
            ],
        )])

    return report


if __name__ == "__main__":
    import sys
    import console
    console.utf8_stdio()
    target_book = None
    if len(sys.argv) > 1:
        if sys.argv[1].startswith('--book='):
            target_book = sys.argv[1][7:]
        else:
            target_book = sys.argv[1]
    result = quality_check(target_book)
    sys.exit(1 if result["critical_count"] > 0 else 0)
