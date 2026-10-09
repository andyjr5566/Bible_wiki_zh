#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build verse → line range index for raw commentary files."""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

BOOK_MAP = {
    'exodus': '出埃及記',
    'leviticus': '利未記',
    'numbers': '民數記',
    'deuteronomy': '申命記',
}

CHINESE_NUMS = {
    '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
    '六': 6, '七': 7, '八': 8, '九': 9,
    '十': 10, '廿': 20, '卅': 30,
}


def parse_chinese_number(s: str) -> Optional[int]:
    """Parse Chinese numerals like 廿三 (23)."""
    if not s:
        return None
    s = s.strip()
    try:
        return int(s)
    except:
        pass

    result = 0
    if '廿' in s:
        result = 20
        s = s.replace('廿', '')
    elif '卅' in s:
        result = 30
        s = s.replace('卅', '')

    if '十' in s:
        idx = s.index('十')
        if idx == 0:
            result = result or 10
            if result > 10:
                result += 10
        else:
            mult = CHINESE_NUMS.get(s[0], 0)
            result = mult * 10
        s = s[idx+1:]

    if s:
        result += CHINESE_NUMS.get(s[0], 0)

    return result if result > 0 else None


def parse_ct_title(line: str) -> Optional[Tuple[int, Optional[int]]]:
    """Parse CT title. Strategy: look for verse numbers at the END before 】."""
    match = re.search(r'【.*?(\d+|[廿卅十一-九]+)(?:[～~\-](\d+|[廿卅十一-九]+))?】', line)
    if not match:
        return None

    # Check if this title has actual verse numbers (not just book/chapter)
    # by looking at the pattern more carefully
    full_match = match.group(0)  # e.g., "【利廿三1】"
    start_str = match.group(1)
    end_str = match.group(2)

    # If we have two groups, the first is usually chapter and second is verse
    # e.g., 【利廿三1】 -> ('廿三', '1')
    # In this case, use the second group
    if end_str is not None:
        # Has both a start and end number
        # They could be (chapter, verse) or (verse_start, verse_end)
        # Check: if first is multi-char Chinese, it's chapter
        if len(start_str) > 1 and all(c in '廿卅十一二三四五六七八九' for c in start_str):
            # First is chapter, treat second as the actual verse start
            # But we need to check if there's another number after
            # Actually, this is ambiguous. Let's check the full match.
            pass

    # Simpler approach: extract the rightmost verse sequence(s)
    # If there's a 【...N】, N is the verse number
    # If there's a 【...N～M】, N and M are verse range

    # Parse the found groups
    start = parse_chinese_number(start_str)
    end = parse_chinese_number(end_str) if end_str else None

    # If both start and end are found, and start is large (>100), it might be a chapter
    # In that case, shift them
    if end is not None and start and start > 66:  # 66 is max verses in some books
        # Probably (chapter, verse_start) pattern
        # Return None or try to handle it specially
        # For now, skip multi-digit chapters
        return None

    if start is None:
        return None

    return (start, end)


def extract_verses_from_ct(raw_data: List[str]) -> Dict[int, Tuple[int, int]]:
    """Extract verse ranges from CT file."""
    result: Dict[int, Tuple[int, int]] = {}

    blocks = []
    for line_num, line in enumerate(raw_data, 1):
        title = parse_ct_title(line)
        if title:
            blocks.append({'start': line_num, 'title': title})

    # Set end line
    for i, block in enumerate(blocks):
        block['end'] = blocks[i + 1]['start'] - 1 if i + 1 < len(blocks) else len(raw_data)

    # Populate result
    for block in blocks:
        start_v, end_v = block['title']
        end_v = end_v or start_v
        for v in range(start_v, end_v + 1):
            result[v] = (block['start'], block['end'])

    return result


def extract_verses_from_bh(raw_data: List[str], book_en: str) -> Dict[int, int]:
    """Extract verse line numbers from BH file."""
    result = {}
    pattern = re.compile(rf'^{book_en.capitalize()}\s+\d+:(\d+)$', re.IGNORECASE)

    for line_num, line in enumerate(raw_data, 1):
        match = pattern.match(line.strip())
        if match:
            verse_num = int(match.group(1))
            result[verse_num] = line_num

    return result


def extract_verses_from_step(raw_data: List[str], book_en: str) -> Dict[int, int]:
    """Extract verse line numbers from STEP file."""
    result = {}
    pattern = re.compile(rf'^##\s+{book_en.capitalize()}\s+\d+:(\d+)$', re.IGNORECASE)

    for line_num, line in enumerate(raw_data, 1):
        match = pattern.match(line.strip())
        if match:
            verse_num = int(match.group(1))
            result[verse_num] = line_num

    return result


def extract_verses_from_kc(raw_data: List[str]) -> Dict[int, List[Tuple[int, int]]]:
    """Extract KC verse references from paragraphs."""
    result: Dict[int, List[Tuple[int, int]]] = {}

    current_para = []
    para_start = None

    for line_num, line in enumerate(raw_data, 1):
        if line.strip() == '':
            if current_para and para_start is not None:
                para_end = line_num - 1
                verse_nums = extract_verses_from_kc_para('\n'.join(current_para))

                for v in verse_nums:
                    if v not in result:
                        result[v] = []
                    result[v].append((para_start, para_end))

            current_para = []
            para_start = None
        else:
            if para_start is None:
                para_start = line_num
            current_para.append(line)

    if current_para and para_start is not None:
        para_end = len(raw_data)
        verse_nums = extract_verses_from_kc_para('\n'.join(current_para))
        for v in verse_nums:
            if v not in result:
                result[v] = []
            result[v].append((para_start, para_end))

    return result


def extract_verses_from_kc_para(para: str) -> List[int]:
    """Extract verse numbers from (verse N) or (verses N-M) patterns."""
    result = []
    matches = re.finditer(r'\(verses?\s+(\d+)(?:[–—-](\d+))?\)', para)

    for match in matches:
        start = int(match.group(1))
        end = int(match.group(2)) if match.group(2) else start
        result.extend(range(start, end + 1))

    return list(set(result))


def extract_verses_from_gt(raw_data: List[str]) -> Dict[int, List[Tuple[int, int, str]]]:
    """Extract GT verse references and source markers."""
    result: Dict[int, List[Tuple[int, int, str]]] = {}

    current_para = []
    para_start = None
    last_verse_range = None

    for line_num, line in enumerate(raw_data, 1):
        if line.strip() == '':
            if current_para and para_start is not None:
                para_end = line_num - 1
                verses = extract_verses_from_gt_para(current_para)
                if not verses:
                    verses = last_verse_range

                source = extract_source_from_gt_para(current_para) or '（無標記）'

                if verses:
                    last_verse_range = verses
                    for v in verses:
                        if v not in result:
                            result[v] = []
                        result[v].append((para_start, para_end, source))

            current_para = []
            para_start = None
        else:
            if para_start is None:
                para_start = line_num
            current_para.append(line)

            # Update last_verse_range from titles
            title = parse_ct_title(line)
            if title:
                start_v, end_v = title
                end_v = end_v or start_v
                last_verse_range = list(range(start_v, end_v + 1))

    if current_para and para_start is not None:
        para_end = len(raw_data)
        verses = extract_verses_from_gt_para(current_para)
        if not verses:
            verses = last_verse_range

        source = extract_source_from_gt_para(current_para) or '（無標記）'

        if verses:
            for v in verses:
                if v not in result:
                    result[v] = []
                result[v].append((para_start, para_end, source))

    return result


def extract_verses_from_gt_para(para_lines: List[str]) -> Optional[List[int]]:
    """Extract verse numbers from GT paragraph."""
    for line in para_lines:
        title = parse_ct_title(line)
        if title:
            start_v, end_v = title
            end_v = end_v or start_v
            return list(range(start_v, end_v + 1))

    return None


def extract_source_from_gt_para(para_lines: List[str]) -> Optional[str]:
    """Extract source marker from GT paragraph."""
    for i, line in enumerate(reversed(para_lines)):
        dash_count = line.count('─') + line.count('―') + line.count('—')
        if dash_count >= 2:
            match = re.search(r'[─―—]{2,}\s*(.+)', line)
            if match:
                source = match.group(1).strip()
                if source:
                    return source

    return None


def get_verse_count(book_en: str, chapter: int) -> int:
    """Get verse count by reading raw scripture file."""
    book_cn = BOOK_MAP.get(book_en, '')
    if not book_cn:
        return 0

    paths = [
        Path('C:\\Obsidian\\Hermes\\scripture\\raw_scripture') / book_cn / f'第{chapter}章.txt',
        Path('/c/Obsidian/Hermes/scripture/raw_scripture') / book_cn / f'第{chapter}章.txt',
    ]

    for scripture_path in paths:
        try:
            if scripture_path.exists():
                with open(scripture_path, 'r', encoding='utf-8') as f:
                    return len(f.readlines())
        except:
            pass

    return 0


def build_index_for_chapter(book_en: str, chapter: int) -> None:
    """Build index for a specific chapter."""
    path_candidates = [
        Path('C:\\Obsidian\\Hermes\\scripture\\raw_data'),
        Path('/c/Obsidian/Hermes/scripture/raw_data'),
    ]
    raw_data_path = None
    for p in path_candidates:
        if p.exists():
            raw_data_path = p
            break

    if raw_data_path is None:
        print(f'Raw data path not found')
        return

    ct_file = raw_data_path / f'ccbiblestudy_CT_{book_en}_{chapter}.txt'
    bh_file = raw_data_path / f'biblehub_study_{book_en}_{chapter}.txt'
    step_file = raw_data_path / f'stepbible_{book_en}_{chapter}.txt'
    kc_file = raw_data_path / f'kingcomments_{book_en}_{chapter}.txt'
    gt_file = raw_data_path / f'ccbiblestudy_GT_{book_en}_{chapter}.txt'

    book_cn = BOOK_MAP[book_en]
    verse_count = get_verse_count(book_en, chapter)

    ct_verses = {}
    bh_verses = {}
    step_verses = {}
    kc_verses = {}
    gt_verses = {}
    gt_raw = []

    if ct_file.exists():
        with open(ct_file, 'r', encoding='utf-8') as f:
            ct_verses = extract_verses_from_ct(f.readlines())

    if bh_file.exists():
        with open(bh_file, 'r', encoding='utf-8') as f:
            bh_verses = extract_verses_from_bh(f.readlines(), book_en)

    if step_file.exists():
        with open(step_file, 'r', encoding='utf-8') as f:
            step_verses = extract_verses_from_step(f.readlines(), book_en)

    if kc_file.exists():
        with open(kc_file, 'r', encoding='utf-8') as f:
            kc_verses = extract_verses_from_kc(f.readlines())

    if gt_file.exists():
        with open(gt_file, 'r', encoding='utf-8') as f:
            gt_raw = f.readlines()
        gt_verses = extract_verses_from_gt(gt_raw)

    # Build output
    output_lines = [
        f'# {book_cn} 第{chapter}章 索引（自動產生，勿手改）\n',
        '\n',
        '## 逐節\n',
        '| 節 | CT | BH | STEP | KC 段落 | GT 段落 |\n',
        '|---|---|---|---|---|---|\n',
    ]

    for v in range(1, verse_count + 1):
        ct_str = '—'
        if v in ct_verses:
            start, end = ct_verses[v]
            ct_str = f'{start}–{end}'

        bh_str = '—'
        if v in bh_verses:
            bh_str = str(bh_verses[v])

        step_str = '—'
        if v in step_verses:
            step_str = str(step_verses[v])

        kc_str = '—'
        if v in kc_verses:
            parts = [f'{start}–{end}' for start, end in kc_verses[v]]
            kc_str = '；'.join(parts)

        gt_str = '—'
        if v in gt_verses:
            parts = [f'{start}–{end}（{src}）' for start, end, src in gt_verses[v]]
            gt_str = '；'.join(parts)

        output_lines.append(f'| {v} | {ct_str} | {bh_str} | {step_str} | {kc_str} | {gt_str} |\n')

    output_lines.extend([
        '\n',
        '## GT 段落總表\n',
        '| 行 | 經節範圍 | 子來源 | 開頭 20 字 |\n',
        '|---|---|---|---|\n',
    ])

    if gt_raw:
        seen = set()
        for v in sorted(gt_verses.keys()):
            for start, end, source in gt_verses[v]:
                key = (start, end)
                if key in seen:
                    continue
                seen.add(key)

                para_text = ''.join(gt_raw[start-1:end])
                para_text = para_text[:20].replace('\n', ' ')

                output_lines.append(f'| {start}–{end} | {v} | {source} | {para_text} |\n')

    output_path = Path(__file__).parent / f'{book_en}_{chapter}.md'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)

    print(f'Created {output_path.name}')


def main():
    if len(sys.argv) < 3 or len(sys.argv) % 2 == 0:
        print('Usage: python build_index.py book1 ch1 book2 ch2 ...')
        sys.exit(1)

    for i in range(1, len(sys.argv), 2):
        book_en = sys.argv[i].lower()
        try:
            chapter = int(sys.argv[i + 1])
        except ValueError:
            continue

        if book_en not in BOOK_MAP:
            continue

        build_index_for_chapter(book_en, chapter)


if __name__ == '__main__':
    main()
