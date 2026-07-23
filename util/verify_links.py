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


# ========== 6. 離線 broken 掃描（直接讀磁碟，模擬 Obsidian 解析）==========
#
# 判定 BROKEN 的規則與 Obsidian 的 find-unresolved-link 一致：wiki-link 目標必須對得上
# **確切的檔名 stem 或 vault 相對路徑**；**不解析 frontmatter alias**（這正是舊版
# verify_links 用 alias 註冊表會放行 [[按手]] 的盲區）。
#
# 直接讀磁碟而不驅動 Obsidian 有三個好處：(1) 不受 Obsidian metadataCache 對外部編輯的
# 延遲影響（Windows 下改完檔、快取不會即時更新，曾造成假 broken）；(2) 不必開著 Obsidian；
# (3) 不會每跑一次就在 Obsidian 開一個輸出分頁。判定結果與 Obsidian 逐條一致。

BOOK_CHAPTER_SRC_BOOK_RE = re.compile(r"^\d+\s+(?P<book>.+)/第\d+(?:章|篇)$")

BOOK_INDEX_STEM = "全書目錄及綱要"


def build_resolution_sets(root_path):
    """全庫 .md 的檔名 stem 與 vault 相對路徑（去 .md），作為連結解析基準。

    含 alias 的 frontmatter **不納入**——Obsidian 的 unresolved 判定亦不認 alias。
    """
    stems, relpaths = set(), set()
    for f in root_path.rglob("*.md"):
        rel = str(f.relative_to(root_path)).replace("\\", "/")
        if rel.startswith(".tmp/") or "/.tmp/" in rel:
            continue
        stems.add(f.stem)
        relpaths.add(rel[:-3])
    return stems, relpaths


def _is_tmp(root_path, f):
    p = str(f.relative_to(root_path)).replace("\\", "/")
    return p.startswith(".tmp/") or "/.tmp/" in p


def scope_source_files(root_path):
    """要檢查的來源檔：link_folder 全部 + 書卷章（排除「全書目錄及綱要」與 .tmp 管線暫存）。"""
    files = []
    lf = root_path / LINK_FOLDER_PARENT
    if lf.exists():
        files.extend(f for f in lf.rglob("*.md") if not _is_tmp(root_path, f))
    for _, directory in existing_book_directories(root_path):
        for f in directory.rglob("*.md"):
            if f.stem == BOOK_INDEX_STEM or _is_tmp(root_path, f):
                continue
            files.append(f)
    return files


def scan_disk_broken_entries(root_path, stems, relpaths):
    """掃 in-scope 來源檔，回傳無法解析的 wiki-link：[(target, [sources...]), ...]。"""
    result = {}
    for f in scope_source_files(root_path):
        rel = str(f.relative_to(root_path)).replace("\\", "/")[:-3]
        try:
            content = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for raw in WIKILINK_RE.findall(content):
            target = raw.split("|")[0].split("#")[0].strip()
            if not target:
                continue
            if target in stems or target in relpaths:
                continue  # Obsidian 解析得到 → 不算 broken
            srcs = result.setdefault(target, [])
            if rel not in srcs:
                srcs.append(rel)
    return list(result.items())


def source_in_book(src, canonical_book):
    """--book 過濾：該來源是否屬指定書卷；link_folder 一律納入（與舊版 --book 一致）。"""
    s = src.split("#", 1)[0].strip()
    if s.startswith(LINK_FOLDER_PARENT + "/"):
        return True
    m = BOOK_CHAPTER_SRC_BOOK_RE.match(s)
    if not m:
        return False
    return canonical_book_name(m.group("book")) == canonical_book


def existing_chapter_set(root_path):
    """回傳實際存在的 (正規化書卷名, 章號) 集合，用來區分『未來章節』與『已存在但連結格式錯』。"""
    result = set()
    for book, directory in existing_book_directories(root_path):
        for fname in directory.iterdir():
            if fname.suffix != ".md":
                continue
            m = re.match(r"^第(\d+)(?:章|篇)$", fname.stem)
            if m:
                result.add((book, int(m.group(1))))
    return result


def classify_broken_target(target, node_basenames, existing_chapters):
    """把一個無法解析的 target 分類。

    回傳 dict，category 為：
      pending  — 合法未來『章節級』聖經引用（書卷未建、章數合法、無節號）。資訊性，不算錯。
      invalid  — 聖經引用章數超出書卷範圍，須修。
      broken   — 其餘一律須處理（拆連結、補 md 或改名）。
    """
    t = target.strip()
    has_verse_colon = ("：" in t) or (":" in t)

    # 半形冒號、但全形冒號版本正好是真檔名 → 只是冒號打錯，改冒號即可
    if ":" in t:
        fullwidth = t.replace(":", "：")
        if fullwidth in node_basenames:
            return {
                "category": "broken",
                "subtype": "冒號半形應改全形（節點已存在，改冒號即可）",
            }

    sci = classify_scripture_ref(t)
    if sci is not None:
        cat, book, chapter = sci
        if cat == "invalid":
            return {
                "category": "invalid",
                "book": book,
                "chapter": chapter,
                "subtype": f"章數超出範圍（{book} 最多 {BIBLE_BOOKS.get(book, '?')} 章）",
            }
        # cat == "pending"
        if not has_verse_colon:
            if (book, chapter) in existing_chapters:
                return {
                    "category": "broken",
                    "subtype": "連結格式錯誤（該章已存在，應改用 [[NN 書卷/第X章]]）",
                }
            return {"category": "pending", "book": book, "chapter": chapter}
        return {
            "category": "broken",
            "subtype": "節級經文引用無對應節點（拆連結、改指章節或建節點）",
        }

    return {"category": "broken", "subtype": "缺條目/節點（建 md 或改正名稱）"}


# ========== 7. 報告輸出 ==========


def _has_error(report):
    return (
        report["broken_links_count"] > 0
        or report["invalid_scripture_refs_count"] > 0
        or report["unknown_links_count"] > 0
    )


def _write_reports(report):
    """寫出 verify_report.json 與 verify_result.txt（check_chapter_files 只檢查存在）。"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "verify_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = []
    lines.append("=" * 60)
    lines.append("  Wiki-Link 驗證報告（離線掃描，模擬 Obsidian 解析）")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"  BROKEN LINKS:           {report['broken_links_count']:>5}")
    lines.append(f"  PENDING SCRIPTURE REFS: {report['pending_scripture_refs_count']:>5}")
    lines.append(f"  INVALID SCRIPTURE REFS: {report['invalid_scripture_refs_count']:>5}")
    lines.append(f"  UNKNOWN LINKS:          {report['unknown_links_count']:>5}")
    lines.append("")

    if report["broken_links"]:
        lines.append("--- BROKEN LINKS (must fix：拆連結或補 md) ---")
        for item in report["broken_links"]:
            srcs = "、".join(item["sources"][:6])
            more = " …" if len(item["sources"]) > 6 else ""
            lines.append(f"  [[{item['entity']}]]  〔{item['subtype']}〕")
            lines.append(f"      ← {srcs}{more}")
        lines.append("")

    if report["invalid_scripture_refs"]:
        lines.append("--- INVALID SCRIPTURE REFS (must fix) ---")
        for item in report["invalid_scripture_refs"]:
            lines.append(f"  [[{item['entity']}]]  〔{item['subtype']}〕")
        lines.append("")

    if report["pending_scripture_refs"]:
        lines.append("--- PENDING SCRIPTURE REFS (info only：未來章節) ---")
        for ref in report["pending_scripture_refs"]:
            lines.append(
                f"  [[{ref['entity']}]] → 合法未來引用 {ref['book']} 第{ref['chapter']}章"
            )
        lines.append("")

    lines.append("Result: " + ("FAIL" if _has_error(report) else "PASS"))
    (OUTPUT_DIR / "verify_result.txt").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def _print_summary(report):
    print()
    print("=" * 60)
    print("  Wiki-Link 驗證（離線掃描，模擬 Obsidian 解析）")
    print("=" * 60)
    print(f"  BROKEN LINKS:           {report['broken_links_count']:>5}")
    print(f"  PENDING SCRIPTURE REFS: {report['pending_scripture_refs_count']:>5}")
    print(f"  INVALID SCRIPTURE REFS: {report['invalid_scripture_refs_count']:>5}")
    print(f"  UNKNOWN LINKS:          {report['unknown_links_count']:>5}")
    print()
    for item in report["broken_links"][:40]:
        print(f"  [[{item['entity']}]]  〔{item['subtype']}〕")
    if len(report["broken_links"]) > 40:
        print(f"  ... 還有 {len(report['broken_links']) - 40} 筆，詳見 verify_result.txt")
    for item in report["invalid_scripture_refs"]:
        print(f"  [INVALID] [[{item['entity']}]]  〔{item['subtype']}〕")
    print()
    print(f"  Result: {'FAIL' if _has_error(report) else 'PASS'}")
    print(f"  Report: {OUTPUT_DIR / 'verify_result.txt'}")
    print("=" * 60)


# ========== 8. Main ==========


def verify_links(book_name=None):
    """主入口：離線掃描 in-scope 檔的 wiki-link → 套聖經知識分流 → 產報告。"""
    root_path = ROOT
    canonical = canonical_book_name(book_name) if book_name else None

    stems, relpaths = build_resolution_sets(root_path)
    existing_chapters = existing_chapter_set(root_path)
    entries = scan_disk_broken_entries(root_path, stems, relpaths)

    broken_items, pending_items, invalid_items = [], [], []
    for target, sources in entries:
        scoped = sources
        if canonical is not None:
            scoped = [s for s in sources if source_in_book(s, canonical)]
            if not scoped:
                continue

        cls = classify_broken_target(target, stems, existing_chapters)
        if cls["category"] == "pending":
            pending_items.append(
                {"entity": target, "book": cls["book"], "chapter": cls["chapter"]}
            )
        elif cls["category"] == "invalid":
            invalid_items.append(
                {
                    "entity": target,
                    "book": cls["book"],
                    "chapter": cls["chapter"],
                    "subtype": cls["subtype"],
                    "sources": scoped,
                }
            )
        else:
            broken_items.append(
                {"entity": target, "subtype": cls["subtype"], "sources": scoped}
            )

    broken_items.sort(key=lambda x: x["entity"])
    invalid_items.sort(key=lambda x: (x["book"], x["chapter"]))
    pending_items.sort(key=lambda x: (x["book"], x["chapter"]))

    report = {
        "source": "offline-disk-scan",
        "broken_links_count": len(broken_items),
        "pending_scripture_refs_count": len(pending_items),
        "invalid_scripture_refs_count": len(invalid_items),
        "unknown_links_count": 0,
        "broken_links": broken_items,
        "pending_scripture_refs": pending_items,
        "invalid_scripture_refs": invalid_items,
    }

    _write_reports(report)
    _print_summary(report)

    if _has_error(report):
        remediation.print_fix_hints(_verify_fix_hints(report))
    else:
        print("結論：PASS")

    return report


def _verify_fix_hints(report):
    """依 verify 報告命中的失敗類別組出修復指引（PENDING 屬正常，不列）。"""
    hints = []
    if report["broken_links_count"] > 0:
        hints.append((
            "BROKEN LINKS：wiki-link 目標對不到任何檔名（每條都要修掉或刪掉）",
            [
                "缺條目/節點：建對應 md，或把 [[錯名]] 改成正確條目全名（含斜線／括號的名字多半要改指底線真檔名）。",
                "冒號半形應改全形：把引用處的半形冒號 : 改成全形 ：（節點已存在）。",
                "節級經文引用無節點：不建節點就把 [[ ]] 拆成純文字，或改指整章／既有節點。",
                "連結格式錯誤：改用 [[NN 書卷/第X章]] 正確格式（該章已存在）。",
                "改完直接重跑：python util/verify_links.py 【書名】",
            ],
        ))
    if report["invalid_scripture_refs_count"] > 0:
        hints.append((
            "INVALID SCRIPTURE REFS：經文引用的章數超出該書卷實際範圍",
            ["依上方 subtype 提示的最大章數，修正引用該經文的檔案中的章數。"],
        ))
    return hints


if __name__ == "__main__":
    import sys
    import console

    console.utf8_stdio()
    target_book = None
    for arg in sys.argv[1:]:
        if arg.startswith("--book="):
            target_book = arg[7:]
        elif not arg.startswith("--"):
            target_book = arg
    result = verify_links(target_book)
    sys.exit(1 if _has_error(result) else 0)


# example usage:
#   python util/verify_links.py            # 離線驗證全庫（不需開 Obsidian）
#   python util/verify_links.py 出埃及記
