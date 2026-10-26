"""Summarize the frozen browser run; measure contrast from text-free screenshots."""
import json
import math
import re
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.tmp-shots/storyteller'
progress_only = os.environ.get('JOS_CONTRAST_PROGRESS') == '1'
report = json.loads((OUT / ('contrast-progress.json' if progress_only else 'report.json')).read_text(encoding='utf-8'))
before = json.loads((OUT / 'before.json').read_text(encoding='utf-8'))
stations = json.loads((ROOT / 'src/data/stations.json').read_text(encoding='utf-8'))
revision2 = json.loads((OUT / 'revision2-rhythm.json').read_text(encoding='utf-8'))
station_rhythm = {s['id']: s for b in revision2 for s in b['parts']}
prior_rhythm = {b['id']: b for b in revision2}
expected_rhythm = report.get('expectedRhythm', {b['id']: b['afterPx'] for b in revision2})


def luminance(rgb):
    c = np.asarray(rgb, dtype=float) / 255
    c = np.where(c <= .04045, c / 12.92, ((c + .055) / 1.055) ** 2.4)
    return c[..., 0] * .2126 + c[..., 1] * .7152 + c[..., 2] * .0722


contrasts = []
radius = 12
yy, xx = np.ogrid[-radius:radius+1, -radius:radius+1]
offsets = np.argwhere(xx*xx+yy*yy <= radius*radius)-radius
for shot in report['shots']:
    if not shot['rects']:
        continue
    pixels = np.asarray(Image.open(OUT / (shot['name'] + '-background.png')).convert('RGB'))
    rendered = np.asarray(Image.open(OUT / (shot['name'] + '.png')).convert('RGB'))
    bg_luminance = luminance(pixels)
    minimum = math.inf
    worst = None
    count = 0
    for line in shot['rects']:
        fg = [int(v) for v in re.findall(r'[\d.]+', line['color'])[:3]]
        for r in line['rects']:
            x0, y0 = max(0, math.floor(r['x'])), max(0, math.floor(r['y']))
            x1, y1 = min(pixels.shape[1], math.ceil(r['x'] + r['w'])), min(pixels.shape[0], math.ceil(r['y'] + r['h']))
            if x1 <= x0 or y1 <= y0:
                continue
            ink = rendered[y0:y1,x0:x1].astype(float)
            changed = np.max(np.abs(ink-pixels[y0:y1,x0:x1].astype(float)),axis=-1)>32
            # Use measured, fully inked glyph cores. Antialiasing/fading edges
            # are excluded; the entire 12px disk of background is included.
            mask = changed & (np.max(np.abs(ink-fg),axis=-1)<=12)
            if not mask.any():
                continue
            # A disk around every glyph-core pixel, including background outside
            # its DOM rectangle. Compare the worst measured foreground/background
            # extrema in this union (conservative even across one glyph).
            h,w=mask.shape
            halo=np.zeros((h+2*radius,w+2*radius),dtype=bool)
            for dy,dx in offsets:
                halo[radius+dy:radius+dy+h,radius+dx:radius+dx+w] |= mask
            bx0,by0=max(0,x0-radius),max(0,y0-radius)
            bx1,by1=min(pixels.shape[1],x1+radius),min(pixels.shape[0],y1+radius)
            halo=halo[by0-(y0-radius):by1-(y0-radius),bx0-(x0-radius):bx1-(x0-radius)]
            background=bg_luminance[by0:by1,bx0:bx1][halo]
            f=luminance(ink)[mask]
            if f.max()<background.min(): ratio=(background.min()+.05)/(f.max()+.05)
            elif f.min()>background.max(): ratio=(f.min()+.05)/(background.max()+.05)
            else: ratio=1
            if float(ratio)<minimum:
                minimum=float(ratio)
                worst={'rect':r,'color':line['color'],'foregroundRange':[float(f.min()),float(f.max())],
                       'backgroundRange':[float(background.min()),float(background.max())]}
            count += int(mask.sum())
    if count:
        contrasts.append({'name': shot['name'], 'minRatio': minimum, 'glyphCorePixels': count, 'backgroundRadiusPx':radius,'worst':worst})

if progress_only:
    failures=[c for c in contrasts if c['minRatio']<4.5]
    print(json.dumps({'samples':len(contrasts),'minimum':min(c['minRatio'] for c in contrasts),'failures':failures},indent=2))
    raise SystemExit(1 if failures else 0)

rhythm = []
for device in report['devices']:
    rhythm.append({'device': device['device'], 'beats': [
        {'id': b['id'], 'beforePx': prior_rhythm[b['id']]['beforePx'], 'afterPx': b['height'],
         'beforeWheels': prior_rhythm[b['id']]['beforePx'] / 100, 'afterWheels': b['height'] / 100}
        for b in device['beats']]})

flights = []
for station in stations:
    row = {'id': station['id'], 'beat': station['beat'], 'afterFlightPx': 800,
           'afterReadPx': station_rhythm[station['id']]['px']}
    for device in before['devices']:
        beat = next(b for b in device['beats'] if b['id'] == station['beat'])
        total_weight = sum(s['weight'] for s in stations if s['beat'] == station['beat'])
        # Prior source snapshot .tmp-ci/act2/src/scene/stations.ts: FLIGHT=.16,
        # stations weighted within each beat; first station had no flight.
        old_span = beat['progressSpan'] * station['weight'] / total_weight
        label = 'desktop' if device['width'] == 1440 else 'mobile'
        row[label + 'BeforeFlightPx'] = old_span * .16 if station is not stations[0] else 0
        row[label + 'BeforeReadPx'] = old_span * (.84 if station is not stations[0] else 1)
    flights.append(row)

font_path = ROOT / 'src/assets/fonts/Iansui-Regular.ttf'
font = ImageFont.truetype(str(font_path), 16)


def contact(files, dest, cols=4, width=360):
    rows = math.ceil(len(files) / cols)
    height = 225
    sheet = Image.new('RGB', (cols * width, rows * (height + 29)), '#e9e2d1')
    draw = ImageDraw.Draw(sheet)
    for i, path in enumerate(files):
        img = Image.open(path).convert('RGB')
        img.thumbnail((width, height))
        x, y = (i % cols) * width, (i // cols) * (height + 29)
        sheet.paste(img, (x + (width - img.width) // 2, y + (height - img.height) // 2))
        draw.text((x + 8, y + height + 4), path.stem, fill='#261e18', font=font)
    sheet.save(OUT / dest, quality=90)


for device in ['desktop', 'mobile']:
    contact([OUT / (s['name'] + '.png') for s in report['shots'] if s['name'].startswith(device)], 'contact-' + device + '.jpg')
    contact([OUT / (device+'-still-'+b['id']+'.png') for b in report['devices'][0]['beats']], 'contact-still-'+device+'.jpg')
contact(sorted(OUT.glob('autoplay-*.png')), 'contact-autoplay.jpg', width=288)
contact(sorted(OUT.glob('boundary-*.png')), 'contact-boundaries.jpg', width=288)
scroll_files = [OUT / (s['name']+'.png') for s in report['scroll300']]
contact(scroll_files, 'contact-scroll300.jpg', width=288)
for start in range(0, len(scroll_files), 12):
    contact(scroll_files[start:start+12], f'contact-scroll300-{start//12+1:02}.jpg', cols=3, width=480)

play = report['autoplaySamples']
steps = [b['y'] - a['y'] for a, b in zip(play, play[1:])]
old_bubbles = [{'width': b['width'], 'dx': max(s['x'] for s in b['samples']) - min(s['x'] for s in b['samples']),
                'dy': max(s['y'] for s in b['samples']) - min(s['y'] for s in b['samples'])} for b in before['bubble']]
failures = list(report['failures'])
for device in report['devices']:
    for beat in device['beats']:
        if beat['height'] != expected_rhythm[beat['id']]:
            failures.append(device['device'] + ': beat height differs ' + beat['id'])
failures.extend(c['name'] + ': contrast below 4.5' for c in contrasts if c['minRatio'] < 4.5)
if min(steps) < 0:
    failures.append('autoplay moved backward')
summary = {'buildSha256': report['sha256'], 'rhythm': rhythm, 'stations': flights,
           'opacity': {'samples':len(report['opacity']), 'beats':len({s['beat'] for s in report['opacity']}),
                       'cards':sum(len(s['cards'])+len(s['layers']) for s in report['opacity']),
                       'nonEntryMinimum':min(c['opacity'] for s in report['opacity'] for c in s['cards']+s['layers'] if not c['entering'])},
           'contrast': contrasts, 'minimumContrast': min(c['minRatio'] for c in contrasts),
           'beforeBubbles': old_bubbles, 'afterBubbles': [{k: b[k] for k in ('device', 'beat', 'dx', 'dy')} for b in report['bubble']],
           'autoplay': {'samples': len(play), 'frames': len(report['autoplay']), 'minStepPx': min(steps), 'maxStepPx': max(steps),
                        'distancePx': play[-1]['y'] - play[0]['y']}, 'failures': failures}
(OUT / 'analysis.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: v for k, v in summary.items() if k not in ('rhythm', 'stations', 'contrast')}, ensure_ascii=False, indent=2))
if failures:
    raise SystemExit(1)
