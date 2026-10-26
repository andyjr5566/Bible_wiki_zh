"""Render story-font glyphs beside MOE's reference font for visual review.

The reference TTF is only used for engineering review; it is not shipped.
"""
import hashlib
import json
from pathlib import Path
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.tmp-shots/storyteller/font-audit'
site = json.loads((ROOT / 'src/data/site.json').read_text(encoding='utf-8'))
receipt = json.loads((ROOT / 'src/assets/fonts/story-iansui.json').read_text(encoding='utf-8'))
source = ROOT / 'src/assets/fonts/Iansui-Regular.ttf'
subset = ROOT / 'src/assets/fonts/story-iansui.woff2'
reference = OUT / 'moe-kai.ttf'
iansui = TTFont(source)
subset_font = TTFont(subset)
moe = TTFont(reference)
source_cmap = iansui.getBestCmap()
subset_cmap = subset_font.getBestCmap()
refs = {}
for _, block in site['verseBlocks'].items():
    for line in block['lines']:
        for char in set(line['text']):
            if '\u3400' <= char <= '\u9fff':
                refs.setdefault(char, []).append(f"{block['abbr']}{block['chapter']}:{line['v']}")

chars = sorted((chr(cp) for cp in receipt['codepoints'] if '\u3400' <= chr(cp) <= '\u9fff'), key=ord)
fonts = [ImageFont.truetype(str(path), 54) for path in [source, reference]]
label = ImageFont.truetype(str(reference), 13)
for start in range(0, len(chars), 80):
    sheet = Image.new('RGB', (1280, 1000), '#fffaf0')
    draw = ImageDraw.Draw(sheet)
    for i, char in enumerate(chars[start:start + 80]):
        x = (i % 8) * 160
        y = (i // 8) * 100
        draw.text((x + 4, y), f'U+{ord(char):04X}   Iansui / MOE', font=label, fill='#4b4035')
        for j, font in enumerate(fonts):
            draw.text((x + 5 + j * 70, y + 20), char, font=font, fill='#20180f')
    sheet.save(OUT / f'all-{start // 80 + 1:02}.png')

focus = [char for char in '為說內全慎別' if ord(char) in subset_cmap]
focus_sheet = Image.new('RGB', (1280, ((len(focus) + 7) // 8) * 100), '#fffaf0')
draw = ImageDraw.Draw(focus_sheet)
for i, char in enumerate(focus):
    x = (i % 8) * 160
    y = (i // 8) * 100
    draw.text((x + 4, y), f'U+{ord(char):04X}   Iansui / MOE', font=label, fill='#4b4035')
    for j, font in enumerate(fonts):
        draw.text((x + 5 + j * 70, y + 20), char, font=font, fill='#20180f')
focus_sheet.save(OUT / 'selected-glyphs.png')

record = {
    'referenceUrl': 'https://language.moe.gov.tw/material/info?m=9fe3fe82-8bbf-44c0-961d-873ea079e284',
    'source': receipt['source'],
    'sourceVersion': receipt['version'],
    'referenceSha256': hashlib.sha256(reference.read_bytes()).hexdigest(),
    'sourceSha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'subsetSha256': hashlib.sha256(subset.read_bytes()).hexdigest(),
    'characters': len(chars),
    'blocks': len(site['verseBlocks']),
    'unicodeCounts': {
        f'U+{cp:04X}': sum(line['text'].count(chr(cp)) for block in site['verseBlocks'].values() for line in block['lines'])
        for cp in [0x70ba, 0x7232]
    },
    'subsetCoverage': all(ord(char) in subset_cmap for char in chars),
    'focusGlyphs': [
        {'char': char, 'codepoint': f'U+{ord(char):04X}', 'inSubset': ord(char) in subset_cmap,
         'refs': sorted(set(refs.get(char, [])))}
        for char in '為說內全慎別' if ord(char) in source_cmap
    ],
    'glyphs': [
        {'char': char, 'codepoint': f'U+{ord(char):04X}', 'glyph': iansui.getBestCmap().get(ord(char)),
         'refs': sorted(set(refs.get(char, [])))}
        for char in chars
    ],
}
assert all(ord(char) in source_cmap for char in chars)
assert record['subsetCoverage']
(OUT / 'census.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({key: value for key, value in record.items() if key != 'glyphs'}, ensure_ascii=True))
