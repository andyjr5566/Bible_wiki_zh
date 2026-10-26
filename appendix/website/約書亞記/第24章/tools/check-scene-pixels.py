"""Measure the captured pixels, excluding UI, and verify projected silhouettes."""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image


def measure(path, sample, viewport):
    rgb = np.asarray(Image.open(path).convert('RGB'), dtype=np.float32) / 255
    height, width = rgb.shape[:2]
    sx, sy = width / viewport[0], height / viewport[1]
    linear = np.where(rgb <= .04045, rgb / 12.92, ((rgb + .055) / 1.055) ** 2.4)
    y = linear @ np.array([.2126, .7152, .0722], dtype=np.float32)
    lightness = np.where(y > 216 / 24389, 116 * np.cbrt(y) - 16, y * 24389 / 27)
    scene = np.ones((height, width), dtype=bool)
    for rect in sample['uiMasks']:
        x0, x1 = np.clip(np.array([rect['x0'], rect['x1']]) * sx, 0, width).astype(int)
        y0, y1 = np.clip(np.array([rect['y0'], rect['y1']]) * sy, 0, height).astype(int)
        scene[y0:y1, x0:x1] = False

    def patch(cx, cy, rx, ry):
        x0, x1 = max(0, int(cx-rx)), min(width, int(cx+rx)+1)
        y0, y1 = max(0, int(cy-ry)), min(height, int(cy+ry)+1)
        if x1 <= x0 or y1 <= y0:
            return np.array([]), np.array([])
        mask = scene[y0:y1, x0:x1]
        return lightness[y0:y1, x0:x1][mask], y[y0:y1, x0:x1][mask]

    figures = []
    for figure in sample['visual']['figures']:
        if not figure['inFrame']:
            continue
        hx, hy = figure['headX']*sx, figure['headY']*sy
        h = np.hypot((figure['footX']-figure['headX'])*sx, (figure['footY']-figure['headY'])*sy)
        if not (0 <= hx < width and 0 <= hy < height) or h < 8:
            continue
        if not scene[min(height-1, int(hy)), min(width-1, int(hx))]:
            continue
        # Read the head/neck just below the top anchor. Compare both adjacent
        # background patches, so an occluding crowd cannot pass on coordinates alone.
        ink, ink_y = patch(hx, hy+h*.12, max(2, h*.045), max(2, h*.055))
        backgrounds = [patch(hx+side*h*.30, hy+h*.10, max(2, h*.07), max(2, h*.08)) for side in (-1, 1)]
        backgrounds = [(l, v) for l, v in backgrounds if len(l) >= 5]
        if len(ink) < 5 or not backgrounds:
            continue
        bg, bg_y = max(backgrounds, key=lambda pair: np.median(pair[0]))
        delta = float(np.median(bg)-np.percentile(ink, 30))
        contrast = float((np.median(bg_y)+.05)/(np.percentile(ink_y, 30)+.05))
        figures.append({'id':figure['id'], 'deltaL':round(delta, 2), 'contrast':round(contrast, 2),
                        'detected':delta >= 10 and contrast >= 1.5})
    env = sample['visual']['environment']
    weights = {env['from']: 1-env['amount']}
    weights[env['to']] = weights.get(env['to'], 0)+env['amount']
    dominant = max(weights, key=weights.get)
    daylight = dominant not in ('dusk', 'night')
    mean = float(lightness[scene].mean())
    count = sum(f['detected'] for f in figures)
    empty = sample['cue'] == 'epilogue-stone'
    return {'meanL':round(mean, 2), 'scenePixels':int(scene.sum()), 'environment':dominant,
            'daylight':daylight, 'inFrameHeads':len(figures), 'detectedFigures':count, 'figures':figures,
            'failures':(['daylight mean L* < 40'] if daylight and mean < 40 else []) +
                       (['no contrasted silhouette with in-frame head'] if not empty and count < 1 else []) +
                       (['ending must have no people'] if empty and figures else [])}


if __name__ == '__main__':
    sys.stdin.reconfigure(encoding='utf-8')
    request = json.loads(sys.stdin.read())
    print(json.dumps(measure(Path(request['image']), request['sample'], request['viewport'])))
