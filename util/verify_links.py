#!/usr/bin/env python3
"""
verify_links.py — Wiki-link 驗證工具（v3）

輸出四類結果：
  1. BROKEN_LINKS:    真正破損連結（不存在、非合法聖經章節、不在 link_folder）
  2. PENDING_SCRIPTURE: 合法未來聖經章節引用（書卷存在、章數合法）
  3. INVALID_SCRIPTURE: 無效聖經章節引用（書卷存在但章數超出範圍）
  4. UNKNOWN_LINKS:   非 scripture 也非 link_folder/章節檔的未知 target

驗證結果格式：
  VALID LINKS: N
  BROKEN LINKS: N
  PENDING SCRIPTURE REFS: N
  INVALID SCRIPTURE REFS: N
  UNKNOWN LINKS: N

Usage:
  python util/verify_links.py [書卷名]
  python util/verify_links.py --book=創世記
"""
import re
import os
import json
from pathlib import Path

try:
    from .book_paths import (
        book_directory,
        canonical_book_name,
        existing_book_directories,
    )
except ImportError:
    from book_paths import book_directory, canonical_book_name, existing_book_directories

try:
    from .build_link_index import collect_entries, load_resolutions, make_index
    from . import remediation
except ImportError:
    from build_link_index import collect_entries, load_resolutions, make_index
    import remediation

UTIL_DIR = Path(__file__).resolve().parent
ROOT = UTIL_DIR.parent
OUTPUT_DIR = UTIL_DIR / "output"
LINK_FOLDER_PARENT = "link_folder"

import unicodedata

def normalize_name(value):
    """只正規化 Unicode 與空白，不刪除具有語義的括號內容。"""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(value))).strip()

# ========== 1. 聖經書卷章數資料 ==========

BIBLE_BOOKS_FILE = ROOT / "_config" / "bible_books.json"
BIBLE_BOOKS = {}
if BIBLE_BOOKS_FILE.exists():
    with open(BIBLE_BOOKS_FILE, 'r', encoding='utf-8') as f:
        BIBLE_BOOKS = json.load(f)

# 簡繁書名對照（部分書卷可能出現簡體寫法）
BOOK_ALIASES = {
    "創世記": "創世記", "出埃及記": "出埃及記",
    "利未記": "利未記", "民數記": "民數記",
    "申命記": "申命記", "約書亞記": "約書亞記",
    "士師記": "士師記", "路得記": "路得記",
    "撒母耳記上": "撒母耳記上", "撒母耳記下": "撒母耳記下",
    "列王紀上": "列王紀上", "列王紀下": "列王紀下",
    "歷代志上": "歷代志上", "歷代志下": "歷代志下",
    "以斯拉記": "以斯拉記", "尼希米記": "尼希米記",
    "以斯帖記": "以斯帖記", "約伯記": "約伯記",
    "詩篇": "詩篇", "箴言": "箴言",
    "傳道書": "傳道書", "雅歌": "雅歌",
    "以賽亞書": "以賽亞書", "耶利米書": "耶利米書",
    "耶利米哀歌": "耶利米哀歌", "以西結書": "以西結書",
    "但以理書": "但以理書",
    "何西阿書": "何西阿書", "約珥書": "約珥書",
    "阿摩司書": "阿摩司書", "俄巴底亞書": "俄巴底亞書",
    "約拿書": "約拿書", "彌迦書": "彌迦書",
    "那鴻書": "那鴻書", "哈巴谷書": "哈巴谷書",
    "西番雅書": "西番雅書", "哈該書": "哈該書",
    "撒迦利亞書": "撒迦利亞書", "瑪拉基書": "瑪拉基書",
    "馬太福音": "馬太福音", "馬可福音": "馬可福音",
    "路加福音": "路加福音", "約翰福音": "約翰福音",
    "使徒行傳": "使徒行傳",
    "羅馬書": "羅馬書", "哥林多前書": "哥林多前書",
    "哥林多後書": "哥林多後書", "加拉太書": "加拉太書",
    "以弗所書": "以弗所書", "腓立比書": "腓立比書",
    "歌羅西書": "歌羅西書", "帖撒羅尼迦前書": "帖撒羅尼迦前書",
    "帖撒羅尼迦後書": "帖撒羅尼迦後書", "提摩太前書": "提摩太前書",
    "提摩太後書": "提摩太後書", "提多書": "提多書",
    "腓利門書": "腓利門書", "希伯來書": "希伯來書",
    "雅各書": "雅各書", "彼得前書": "彼得前書",
    "彼得後書": "彼得後書", "約翰一書": "約翰一書",
    "約翰二書": "約翰二書", "約翰三書": "約翰三書",
    "猶大書": "猶大書", "啟示錄": "啟示錄",
    # 常見簡體異名
    "创世记": "創世記", "诗篇": "詩篇", "箴言": "箴言",
    "传道书": "傳道書",
    # 常見簡稱
    "代上": "歷代志上", "代下": "歷代志下",
    "撒上": "撒母耳記上", "撒下": "撒母耳記下",
    "王上": "列王紀上", "王下": "列王紀下",
    "林前": "哥林多前書", "林後": "哥林多後書",
    "太": "馬太福音", "可": "馬可福音",
    "路": "路加福音", "約": "約翰福音",
    "徒": "使徒行傳", "羅": "羅馬書",
}

# ========== 2. 正規表達式 ==========

# 匹配 [[target]] 或 [[target|alias]]
WIKILINK_RE = re.compile(r'\[\[([^\]]+)\]\]')

# 匹配聖經章節引用格式：
#   [[創世記13]] — 書名+數字
#   [[創世記/第13章]] — 書名/第x章
#   [[詩篇/第25篇]] — 詩篇/第25篇
#   [[創世紀/第13章|創世記13章]] — 帶 alias
SCRIPTURE_REF_RE = re.compile(
    r'^(?P<book>[^0-9/]+?)(?:/第(?P<chapter>\d+)(?:章|篇))?'
    r'(?P<chapter2>\d+)?$'
)

# ========== 3. 解析聖經章節引用 ==========

def parse_scripture_ref(target):
    """
    嘗試將 wiki-link target 解析為聖經章節引用。
    支援格式：
      - 創世記13       → (創世記, 13)
      - 創世記/第13章   → (創世記, 13)
      - 詩篇/第25篇    → (詩篇, 25)
      - 啟示錄/第22章  → (啟示錄, 22)
      - 出20：16       → (出埃及記, 16)  # 簡寫+全形冒號
      - 出20：8-11     → (出埃及記, 8)   # 範圍格式，取起始章
      - 民35：9-34     → (民數記, 9)     # 範圍格式
      - 來10:10        → (希伯來書, 10)  # 簡寫+半形冒號+章:節
      - 來10:10-12     → (希伯來書, 10)  # 簡寫+章:節-節
      - 出25:10-16     → (出埃及記, 25)  # 簡寫+章:節-節
      - 利16:12-13     → (利未記, 16)    # 簡寫+章:節-節
      - 來10:10,14     → (希伯來書, 10)  # 簡寫+章:節,節
      - 利1-7          → (利未記, 1)     # 簡寫+章-章
      - 利16           → (利未記, 16)    # 簡寫+章
      - 申31:9,24-26   → (申命記, 31)    # 簡寫+章:節,節-節
      - 出14:4,17,18   → (出埃及記, 14)  # 簡寫+章:節,節,節
      - 尼8-10         → (尼希米記, 8)   # 簡寫+章-章
      - 利未記17:11    → (利未記, 17)    # 全名+章:節
      - 利未記1章      → (利未記, 1)     # 全名+章
      - 約書亞記4:2-9  → (約書亞記, 4)   # 全名+章:節-節
    
    回傳 (book_name, chapter_num) 或 None
    """
    # 先嘗試移除「第x章」格式
    m = re.match(r'^(?P<book>.+?)/第(\d+)(?:章|篇)$', target)
    if m:
        book = m.group(1).strip()
        chapter = int(m.group(2))
        return (book, chapter)
    
    # 嘗試全名書卷+章:節格式（可能含範圍、逗號）：利未記17:11、約書亞記4:2-9
    m = re.match(r'^(?P<book>[\u4e00-\u9fff]{2,6})(\d+)[：:](\d+)', target)
    if m:
        book = m.group(1).strip()
        chapter = int(m.group(2))
        book = expand_book_abbrev(book)
        return (book, chapter)
    
    # 嘗試全名書卷+章（無冒號）：利未記1章、利未記16
    m = re.match(r'^(?P<book>[\u4e00-\u9fff]{2,6})(\d+)(?:章)?$', target)
    if m:
        book = m.group(1).strip()
        chapter = int(m.group(2))
        book = expand_book_abbrev(book)
        return (book, chapter)
    
    # 嘗試簡寫書名+全形/半形冒號+章節（可能含範圍）：出20：16、出20：8-11
    m = re.match(r'^(?P<book>[\u4e00-\u9fff]{1,4})[：:](\d+)(?:-(\d+))?$', target)
    if m:
        book_abbrev = m.group(1).strip()
        chapter = int(m.group(2))
        # 將簡寫轉為標準書名
        book = expand_book_abbrev(book_abbrev)
        return (book, chapter)
    
    # 嘗試簡寫書名+章:節格式（可能含範圍、逗號）：來10:10、出25:10-16、利16:12-13
    m = re.match(r'^(?P<book>[\u4e00-\u9fff]{1,4})(\d+)[：:](\d+)', target)
    if m:
        book_abbrev = m.group(1).strip()
        chapter = int(m.group(2))
        book = expand_book_abbrev(book_abbrev)
        return (book, chapter)
    
    # 嘗試簡寫書名+章-章格式（無冒號）：利1-7、尼8-10
    m = re.match(r'^(?P<book>[\u4e00-\u9fff]{1,4})(\d+)-(\d+)$', target)
    if m:
        book_abbrev = m.group(1).strip()
        chapter = int(m.group(2))
        book = expand_book_abbrev(book_abbrev)
        return (book, chapter)
    
    # 嘗試簡寫書名+章（無冒號、無範圍）：利16、申28
    m = re.match(r'^(?P<book>[\u4e00-\u9fff]{1,4})(\d+)$', target)
    if m:
        book_abbrev = m.group(1).strip()
        chapter = int(m.group(2))
        book = expand_book_abbrev(book_abbrev)
        return (book, chapter)
    
    # 嘗試純數字尾綴：創世記13
    m = re.match(r'^(?P<book>.+?)(\d+)$', target)
    if m:
        book = m.group(1).strip()
        chapter = int(m.group(2))
        return (book, chapter)
    
    # 嘗試純書名（無章節數字）：詩篇、俄巴底亞書
    m = re.match(r'^(?P<book>[\u4e00-\u9fff]+)$', target)
    if m:
        book = m.group(1).strip()
        return (book, None)
    
    return None


def expand_book_abbrev(abbrev):
    """將聖經書卷簡寫展開為標準書名"""
    ABBREV_MAP = {
        "創": "創世記", "出": "出埃及記", "利": "利未記", "民": "民數記", "申": "申命記",
        "書": "約書亞記", "士": "士師記", "得": "路得記",
        "撒上": "撒母耳記上", "撒下": "撒母耳記下",
        "王上": "列王紀上", "王下": "列王紀下",
        "代上": "歷代志上", "代下": "歷代志下",
        "斯": "以斯拉記", "尼": "尼希米記", "斯帖": "以斯帖記", "伯": "約伯記",
        "詩": "詩篇", "箴": "箴言", "傳": "傳道書", "歌": "雅歌",
        "賽": "以賽亞書", "耶": "耶利米書", "哀": "耶利米哀歌", "結": "以西結書", "但": "但以理書",
        "何": "何西阿書", "珥": "約珥書", "摩": "阿摩司書", "俄": "俄巴底亞書", "拿": "約拿書", "彌": "彌迦書",
        "鴻": "那鴻書", "哈": "哈巴谷書", "番": "西番雅書", "該": "哈該書", "亞": "撒迦利亞書", "瑪": "瑪拉基書",
        "太": "馬太福音", "可": "馬可福音", "路": "路加福音", "約": "約翰福音",
        "徒": "使徒行傳",
        "羅": "羅馬書", "林前": "哥林多前書", "林後": "哥林多後書", "加": "加拉太書",
        "弗": "以弗所書", "腓": "腓立比書", "西": "歌羅西書",
        "帖前": "帖撒羅尼迦前書", "帖後": "帖撒羅尼迦後書",
        "提前": "提摩太前書", "提後": "提摩太後書", "多": "提多書", "門": "腓利門書",
        "來": "希伯來書", "雅": "雅各書",
        "彼前": "彼得前書", "彼後": "彼得後書",
        "約壹": "約翰一書", "約貳": "約翰二書", "約參": "約翰三書",
        "猶": "猶大書", "啟": "啟示錄",
    }
    return ABBREV_MAP.get(abbrev, abbrev)


def classify_scripture_ref(target):
    """
    判斷聖經引用是否合法。
    
    回傳：
      ("pending", book, chapter)     — 合法未來書卷引用
      ("invalid", book, chapter)     — 不合法（超出章數）
      None                           — 不是聖經章節引用
    """
    parsed = parse_scripture_ref(target)
    if parsed is None:
        return None
    
    book, chapter = parsed
    book = canonical_book_name(book)
    
    # 檢查書卷名（支援別名）
    canonical = BOOK_ALIASES.get(book, None)
    if canonical is None:
        # 嘗試直接匹配
        if book in BIBLE_BOOKS:
            canonical = book
        else:
            return None  # 不是已知書卷名
    
    max_chapters = BIBLE_BOOKS.get(canonical, 0)
    if max_chapters == 0:
        return None
    
    if chapter is None:
        # 純書名無章節，視為合法的未來書卷引用
        return ("pending", canonical, 0)
    
    if 1 <= chapter <= max_chapters:
        return ("pending", canonical, chapter)
    else:
        return ("invalid", canonical, chapter)


# ========== 4. 動態取得 link_folder 下的所有資料夾 ==========

def get_link_folders(root_path):
    """
    動態掃描 link_folder 下的所有子資料夾。
    忽略隱藏資料夾和非資料夾的項目。
    """
    link_folder_path = root_path / LINK_FOLDER_PARENT
    if not link_folder_path.exists():
        return []
    
    folders = []
    for item in link_folder_path.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            folders.append(item.name)
    
    return sorted(folders)


# ========== 5. 建立實體註冊表 ==========

def build_registry(root_path, link_folders):
    """建立 link_folder 條目與章節檔的實體註冊表"""
    existing_entities = set()      # 條目名稱
    entity_locations = {}          # 條目名稱 → 路徑

    # 與 build_link_index 共用同一套 frontmatter alias 與衝突解決規則。
    entries, _ = collect_entries(root_path / LINK_FOLDER_PARENT, root_path)
    index, _ = make_index(
        entries,
        load_resolutions(root_path / "_config" / "link_conflict_resolutions.yaml"),
    )
    title_locations = {entry["title"]: entry["path"] for entry in entries}
    for entity_name, metadata in index.items():
        normalized_name = normalize_name(entity_name)
        existing_entities.add(normalized_name)
        canonical = metadata.get("alias_of", entity_name)
        location = title_locations.get(canonical)
        if location:
            entity_locations[normalized_name] = location
    
    # 掃描章節檔
    existing_chapter_links = set()
    for book, item in existing_book_directories(root_path):
        # 新架構：書卷名/第x章.md
        for fname in item.iterdir():
            if fname.suffix != '.md':
                continue
            if fname.stem.startswith('第') and (fname.stem.endswith('章') or fname.stem.endswith('篇')):
                chapter = fname.stem
                existing_chapter_links.add(normalize_name(f"{item.name} {chapter}"))
                existing_chapter_links.add(normalize_name(f"{item.name}/{chapter}"))
        
        # 舊架構
        for section in ['經文', '註解', '拾穗', '解說', '背景', '綱要', '交叉參照']:
            section_path = item / section
            if not section_path.exists():
                continue
            for f in section_path.iterdir():
                if f.suffix == '.md':
                    chapter = f.stem
                    existing_chapter_links.add(normalize_name(f"{item.name} {chapter}"))
                    existing_chapter_links.add(normalize_name(f"{item.name} {chapter} {section}"))
    
    return existing_entities, entity_locations, existing_chapter_links


def is_existing_path_link(root_path, target):
    """Return whether an Obsidian path target resolves to a Markdown file in the vault."""
    target = target.split("#", 1)[0].strip().replace("\\", "/")
    if not target:
        return False
    relative = Path(target)
    if relative.is_absolute() or ".." in relative.parts:
        return False
    candidate = root_path / relative
    if candidate.suffix.lower() != ".md":
        candidate = Path(f"{candidate}.md")
    try:
        candidate.resolve().relative_to(root_path.resolve())
    except ValueError:
        return False
    return candidate.is_file()


# ========== 6. 掃描 wiki-link ==========

def scan_links(root_path, link_folders, book_name=None):
    """掃描所有 wiki-link，回傳四類分類結果"""
    broken_links = {}       # 真正破損
    pending_refs = {}       # 合法未來書卷引用
    invalid_refs = {}       # 不合法聖經引用
    unknown_links = {}      # 無法判斷

    books_to_scan = []
    if book_name:
        books_to_scan = [(book_name, book_directory(root_path, book_name))]
    else:
        books_to_scan = list(existing_book_directories(root_path))

    existing_entities, entity_locations, existing_chapter_links = build_registry(root_path, link_folders)

    def process_content(content, source_key):
        """處理一個檔案的內容，分類所有 wiki-link"""
        links = WIKILINK_RE.findall(content)
        for link in links:
            entity = link.split('|')[0].strip()
            
            # 檢查是否在實體註冊表或章節檔中
            normalized_entity = normalize_name(entity)
            if (
                normalized_entity in existing_entities
                or normalized_entity in existing_chapter_links
                or is_existing_path_link(root_path, entity)
            ):
                continue  # 正常連結
            
            # 檢查是否為聖經章節引用
            scripture = classify_scripture_ref(entity)
            if scripture is not None:
                cat, book, chapter = scripture
                if cat == "pending":
                    pending_refs.setdefault(source_key, set()).add(
                        (entity, book, chapter)
                    )
                elif cat == "invalid":
                    invalid_refs.setdefault(source_key, set()).add(
                        (entity, book, chapter)
                    )
                continue
            
            # 不屬於上述任何分類 → broken
            broken_links.setdefault(source_key, set()).add(entity)

    # 掃描書卷資料夾
    for book, book_path in books_to_scan:
        if not book_path.is_dir():
            continue

        for item in book_path.iterdir():
            if item.name.startswith('.'):
                continue
            if item.is_file() and item.suffix == '.md':
                try:
                    content = item.read_text(encoding='utf-8')
                except (UnicodeDecodeError, Exception):
                    continue
                process_content(content, f"{book_path.name}/{item.name}")

            elif item.is_dir() and item.name in ['經文', '註解', '拾穗', '解說', '背景', '綱要', '交叉參照']:
                for f in item.iterdir():
                    if f.suffix != '.md':
                        continue
                    try:
                        content = f.read_text(encoding='utf-8')
                    except (UnicodeDecodeError, Exception):
                        continue
                    process_content(content, f"{book_path.name}/{item.name}/{f.name}")

    # 掃描 link_folder
    for folder in link_folders:
        folder_path = root_path / LINK_FOLDER_PARENT / folder
        if not folder_path.exists():
            continue
        for f in folder_path.iterdir():
            if f.suffix != '.md':
                continue
            try:
                content = f.read_text(encoding='utf-8')
            except (UnicodeDecodeError, Exception):
                continue
            process_content(content, f"{LINK_FOLDER_PARENT}/{folder}/{f.name}")

    return broken_links, pending_refs, invalid_refs


# ========== 7. 輸出報告 ==========

def build_report(broken_links, pending_refs, invalid_refs, root_path, link_folders):
    """產生 4 類輸出報告"""
    # 收集 unique entities
    all_broken = set()
    for links_set in broken_links.values():
        all_broken.update(links_set)
    
    all_pending = set()
    for refs_set in pending_refs.values():
        for entity, book, chapter in refs_set:
            all_pending.add((entity, book, chapter))
    
    all_invalid = set()
    for refs_set in invalid_refs.values():
        for entity, book, chapter in refs_set:
            all_invalid.add((entity, book, chapter))
    
    # 計算總 valid 連結數
    total_valid_link_occurrences = 0
    # 略估：從已索引的檔案中估算 valid 數量，這裡先掃一次
    existing_entities, _, existing_chapter_links = build_registry(root_path, link_folders)
    all_valid_targets = existing_entities | existing_chapter_links
    
    for item in root_path.iterdir():
        if item.is_dir() and item.name not in [LINK_FOLDER_PARENT] + link_folders:
            for f in item.rglob('*.md'):
                if f.name.startswith('.'):
                    continue
                try:
                    content = f.read_text(encoding='utf-8')
                    links = WIKILINK_RE.findall(content)
                    for link in links:
                        entity = link.split('|')[0].strip()
                        if entity in all_valid_targets or is_existing_path_link(root_path, entity):
                            total_valid_link_occurrences += 1
                except:
                    pass
    
    for folder in link_folders:
        folder_path = root_path / LINK_FOLDER_PARENT / folder
        if not folder_path.exists():
            continue
        for f in folder_path.rglob('*.md'):
            try:
                content = f.read_text(encoding='utf-8')
                links = WIKILINK_RE.findall(content)
                for link in links:
                    entity = link.split('|')[0].strip()
                    if entity in all_valid_targets or is_existing_path_link(root_path, entity):
                        total_valid_link_occurrences += 1
            except:
                pass
    
    # 儲存 JSON 報告
    report = {
        "valid_links_count": total_valid_link_occurrences,
        "broken_links_count": len(all_broken),
        "pending_scripture_refs_count": len(all_pending),
        "invalid_scripture_refs_count": len(all_invalid),
        "unknown_links_count": 0,  # 目前暫時沒有獨立 unknown 分類
        "broken_links": sorted(list(all_broken)),
        "pending_scripture_refs": sorted(
            [{"entity": e, "book": b, "chapter": c} for e, b, c in all_pending],
            key=lambda x: (x["book"], x["chapter"])
        ),
        "invalid_scripture_refs": sorted(
            [{"entity": e, "book": b, "chapter": c} for e, b, c in all_invalid],
            key=lambda x: (x["book"], x["chapter"])
        ),
        "details": {
            "broken": {k: sorted(list(v)) for k, v in sorted(broken_links.items())},
            "pending": {k: sorted([(e, b, c) for e, b, c in v]) for k, v in sorted(pending_refs.items())},
            "invalid": {k: sorted([(e, b, c) for e, b, c in v]) for k, v in sorted(invalid_refs.items())},
        }
    }
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / "verify_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 人類可讀輸出
    txt_path = OUTPUT_DIR / "verify_result.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("  Wiki-Link Verification Report\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"  VALID LINKS:           {total_valid_link_occurrences:>5}\n")
        f.write(f"  BROKEN LINKS:          {len(all_broken):>5}\n")
        f.write(f"  PENDING SCRIPTURE REFS:{len(all_pending):>5}\n")
        f.write(f"  INVALID SCRIPTURE REFS:{len(all_invalid):>5}\n")
        f.write(f"  UNKNOWN LINKS:         {0:>5}\n\n")
        
        if all_broken:
            f.write("--- BROKEN LINKS (must fix) ---\n")
            for entity in sorted(all_broken):
                f.write(f"  [[{entity}]]\n")
            f.write("\n")
        
        if all_pending:
            f.write("--- PENDING SCRIPTURE REFS (info only) ---\n")
            for entity, book, chapter in sorted(all_pending, key=lambda x: (x[1], x[2])):
                f.write(f"  [[{entity}]] → valid future {book} chapter {chapter} reference\n")
            f.write("\n")
        
        if all_invalid:
            f.write("--- INVALID SCRIPTURE REFS (must fix) ---\n")
            for entity, book, chapter in sorted(all_invalid, key=lambda x: (x[1], x[2])):
                f.write(f"  [[{entity}]] → ERROR: {book} only has {BIBLE_BOOKS.get(book, '?')} chapters\n")
            f.write("\n")
        
        if all_broken or all_invalid:
            f.write("Result: FAIL (broken or invalid refs found)\n")
        else:
            f.write("Result: PASS\n")
    
    return report, txt_path


# ========== 8. Main ==========

def verify_links(book_name=None):
    """主入口"""
    root_path = ROOT
    
    # 動態取得 link_folder 下的所有資料夾
    link_folders = get_link_folders(root_path)
    
    broken_links, pending_refs, invalid_refs = scan_links(
        root_path, link_folders, book_name
    )
    
    report, txt_path = build_report(broken_links, pending_refs, invalid_refs, root_path, link_folders)
    
    # 顯示摘要到 stdout
    print(f"\n{'='*60}")
    print(f"  Wiki-Link Verification Report")
    print(f"{'='*60}")
    print(f"  VALID LINKS:           {report['valid_links_count']:>5}")
    print(f"  BROKEN LINKS:          {report['broken_links_count']:>5}")
    print(f"  PENDING SCRIPTURE REFS:{report['pending_scripture_refs_count']:>5}")
    print(f"  INVALID SCRIPTURE REFS:{report['invalid_scripture_refs_count']:>5}")
    print(f"  UNKNOWN LINKS:         {report['unknown_links_count']:>5}")
    print()
    
    if report['broken_links']:
        print("--- BROKEN LINKS (must fix) ---")
        for entity in report['broken_links']:
            print(f"  [[{entity}]]")
        print()
    
    if report['pending_scripture_refs']:
        print("--- PENDING SCRIPTURE REFS (info only) ---")
        for ref in report['pending_scripture_refs'][:10]:
            print(f"  [[{ref['entity']}]] → valid future {ref['book']} ch.{ref['chapter']}")
        if len(report['pending_scripture_refs']) > 10:
            print(f"  ... and {len(report['pending_scripture_refs']) - 10} more")
        print()
    
    if report['invalid_scripture_refs']:
        print("--- INVALID SCRIPTURE REFS (must fix) ---")
        for ref in report['invalid_scripture_refs']:
            print(f"  [[{ref['entity']}]] → ERROR: {ref['book']} max {BIBLE_BOOKS.get(ref['book'], '?')} ch.")
        print()
    
    has_error = (
        report['broken_links_count'] > 0
        or report['invalid_scripture_refs_count'] > 0
        or report['unknown_links_count'] > 0
    )
    print(f"  Result: {'FAIL' if has_error else 'PASS'}")
    print(f"  Report: {txt_path}")
    print(f"{'='*60}\n")

    if has_error:
        remediation.print_fix_hints(_verify_fix_hints(report))
    else:
        print("結論：PASS")

    return report


def _verify_fix_hints(report):
    """依 verify 報告命中的失敗類別組出修復指引（PENDING 屬正常，不列）。"""
    hints = []
    if report['broken_links_count'] > 0:
        hints.append((
            "BROKEN LINKS：target 條目不存在（非合法聖經章節、也不在 link_folder）",
            [
                "看上方每個 [[target]]：若是打錯條目名，改成正確全名；"
                "若該條目確實該存在，補建或改用其別名。",
                "若 target 是既有條目的別名卻沒被認出，補進該條目 aliases 或 "
                "_config/link_conflict_resolutions.yaml，再 python util/build_link_index.py 重建索引。",
                "改完重跑：python util/verify_links.py 【書名】",
            ],
        ))
    if report['invalid_scripture_refs_count'] > 0:
        hints.append((
            "INVALID SCRIPTURE REFS：經文引用的章數超出該書卷實際範圍",
            ["依上方 ERROR 提示的最大章數，修正引用該經文的檔案中的章數。"],
        ))
    return hints


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
    result = verify_links(target_book)
    has_error = (
        result["broken_links_count"] > 0
        or result["invalid_scripture_refs_count"] > 0
        or result["unknown_links_count"] > 0
    )
    sys.exit(1 if has_error else 0)

'''
example usage:
  python util/verify_links.py
  python util/verify_links.py --book=創世記
'''
