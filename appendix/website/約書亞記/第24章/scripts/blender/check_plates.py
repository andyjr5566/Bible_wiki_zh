"""Full-resolution Sobel + orientation-guided Hough audit (numpy/Pillow only).

python -I scripts/blender/check_plates.py
python -I scripts/blender/check_plates.py --self-test

RGBA is inspected over the station sky, so invisible RGB padding is ignored but
opaque/transparent silhouettes are tested. A second alpha channel edge map tests
the silhouette even where its colour happens to match the sky. No scene-specific
regions or angle exclusions; only horizontal lines wholly within 1.5% of the
camera's geometric horizon are references, rather than failures.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
LAYERS = ROOT / 'lab/renders/layers'
sys.path.insert(0, str(HERE))
from epic_station_config import IDS

PARAMS = dict(min_length_width=.12, sobel_threshold=6., blur_radius=.65,
              angle_step_degrees=.25, gradient_tolerance_degrees=12.,
              rho_bin_pixels=2., support_distance_pixels=1.5,
              max_gap_pixels=9, min_support_fraction=.72,
              horizon_half_height=.015, horizontal_tolerance_degrees=1.5)


def gradients(channel):
    v = np.asarray(Image.fromarray(np.uint8(np.clip(channel, 0, 255))).filter(
        ImageFilter.GaussianBlur(PARAMS['blur_radius'])), dtype=np.float32)
    p = np.pad(v, 1, mode='edge')
    gx = (p[:-2, 2:] + 2*p[1:-1, 2:] + p[2:, 2:]
          - p[:-2, :-2] - 2*p[1:-1, :-2] - p[2:, :-2])/4
    gy = (p[2:, :-2] + 2*p[2:, 1:-1] + p[2:, 2:]
          - p[:-2, :-2] - 2*p[:-2, 1:-1] - p[:-2, 2:])/4
    return gx, gy


def edge_map(rgb, alpha=None):
    # Maximum colour-channel derivative also detects chromatic seams.
    gs = [gradients(rgb[:, :, i]) for i in range(3)]
    if alpha is not None:
        gs.append(gradients(alpha))
    mags = np.stack([np.hypot(x, y) for x, y in gs])
    idx = mags.argmax(axis=0)[None, :, :]
    gx = np.take_along_axis(np.stack([x for x, _ in gs]), idx, axis=0)[0]
    gy = np.take_along_axis(np.stack([y for _, y in gs]), idx, axis=0)[0]
    mag = mags.max(axis=0)
    # Non-maximum suppression across the local gradient, not along the line.
    signed_angle = np.degrees(np.arctan2(gy, gx)) % 360
    angle = signed_angle % 180
    direction = ((angle + 22.5)//45).astype(int) % 4
    keep = np.zeros(mag.shape, bool)
    for k, (dy, dx) in enumerate(((0, 1), (1, 1), (1, 0), (1, -1))):
        keep |= ((direction == k) & (mag >= np.roll(mag, (dy, dx), (0, 1)))
                 & (mag >= np.roll(mag, (-dy, -dx), (0, 1))))
    keep &= mag >= PARAMS['sobel_threshold']
    keep[:2] = keep[-2:] = False
    keep[:, :2] = keep[:, -2:] = False
    return keep, signed_angle


def detect(rgb, alpha=None, horizon=None):
    h, w = rgb.shape[:2]
    edges, normals = edge_map(rgb, alpha)
    y, x = np.nonzero(edges)
    signed_norm = normals[y, x]
    norm = signed_norm % 180
    minlen = w*PARAMS['min_length_width']
    rho_step = PARAMS['rho_bin_pixels']
    offset = math.hypot(w, h)
    bins = int(2*offset/rho_step)+3
    candidates = []
    for deg in np.arange(0, 180, PARAMS['angle_step_degrees']):
        delta = np.abs(norm-deg)
        use = np.minimum(delta, 180-delta) <= PARAMS['gradient_tolerance_degrees']
        theta = math.radians(deg)
        co, si = math.cos(theta), math.sin(theta)
        rho = x[use]*co+y[use]*si
        votes = np.bincount(np.rint((rho+offset)/rho_step).astype(int), minlength=bins)
        for r in np.flatnonzero((votes >= minlen*.48)
                                & (votes >= np.roll(votes, 1))
                                & (votes >= np.roll(votes, -1))):
            candidates.append((int(votes[r]), float(deg), r*rho_step-offset))
    candidates.sort(reverse=True)
    lines = []
    projection_cache = {}
    for votes, deg, rho in candidates:
        th = math.radians(deg)
        n = np.array([math.cos(th), math.sin(th)])
        tangent = np.array([-n[1], n[0]])
        if deg not in projection_cache:
            da = np.abs(norm-deg)
            ids = np.flatnonzero(np.minimum(da, 180-da) <= PARAMS['gradient_tolerance_degrees'])
            projected = x[ids]*n[0]+y[ids]*n[1]
            order = np.argsort(projected)
            projection_cache[deg] = (projected[order], ids[order])
        projected, ids = projection_cache[deg]
        low, high = np.searchsorted(projected, [rho-PARAMS['support_distance_pixels'],
                                                rho+PARAMS['support_distance_pixels']], side='left')
        # Inclusive upper bound, matching the direct distance comparison.
        high = np.searchsorted(projected, rho+PARAMS['support_distance_pixels'], side='right')
        selected = ids[low:high]
        if len(selected) < minlen*.5:
            continue
        runs = []
        # A line must follow one side of an edge. Joining opposite-polarity
        # banks/ripples can manufacture a long line across a curved river.
        polarity = np.cos(np.radians(signed_norm[selected]-deg)) >= 0
        for positive in (True, False):
            one_side = selected[polarity == positive]
            along = np.sort(x[one_side]*tangent[0]+y[one_side]*tangent[1])
            split = np.flatnonzero(np.diff(along) > PARAMS['max_gap_pixels'])+1
            runs.extend((part, one_side) for part in np.split(along, split))
        for run, support_ids in runs:
            if len(run) < 2 or run[-1]-run[0] <= minlen:
                continue
            lo, hi = float(run[0]), float(run[-1])
            coverage = len(np.unique(np.rint(run).astype(int)))/(hi-lo+1)
            if coverage < PARAMS['min_support_fraction']:
                continue
            # Refine the quantized Hough angle against the actual edge pixels.
            # This also prevents tilted Hough bins from describing the same
            # horizontal horizon as a collection of short diagonal segments.
            ss = x[support_ids]*tangent[0]+y[support_ids]*tangent[1]
            support_ids = support_ids[(ss >= lo) & (ss <= hi)]
            xy = np.column_stack((x[support_ids], y[support_ids])).astype(float)
            center = xy.mean(axis=0)
            centered = xy-center
            cov = centered.T@centered/len(xy)
            angle_fit = .5*math.atan2(2*cov[0, 1], cov[0, 0]-cov[1, 1])
            fit_t = np.array([math.cos(angle_fit), math.sin(angle_fit)])
            fit_n = np.array([-fit_t[1], fit_t[0]])
            fitted = np.abs(centered@fit_n) <= PARAMS['support_distance_pixels']
            positions = np.sort(centered[fitted]@fit_t)
            if len(positions) < 2 or positions[-1]-positions[0] <= minlen:
                continue
            if np.max(np.diff(positions)) > PARAMS['max_gap_pixels']:
                continue
            coverage = len(np.unique(np.rint(positions).astype(int)))/(positions[-1]-positions[0]+1)
            if coverage < PARAMS['min_support_fraction']:
                continue
            p0, p1 = center+fit_t*positions[0], center+fit_t*positions[-1]
            ang = math.degrees(angle_fit) % 180
            fit_rho = center@fit_n
            lo, hi = sorted([p0@fit_t, p1@fit_t])
            duplicate = False
            for old in lines:
                aa = abs(old['angle_degrees']-ang)
                if min(aa, 180-aa) > 1.5:
                    continue
                q = np.array([old['start'], old['end']])
                if np.max(np.abs(q@fit_n-fit_rho)) > 5:
                    continue
                qlo, qhi = sorted(q@fit_t)
                if min(hi, qhi)-max(lo, qlo) > .55*min(hi-lo, qhi-qlo):
                    duplicate = True
                    break
            if duplicate:
                continue
            reference = bool(horizon is not None
                             and min(ang, 180-ang) <= PARAMS['horizontal_tolerance_degrees']
                             and max(abs(p0[1]-horizon), abs(p1[1]-horizon)) <= h*.015)
            lines.append(dict(start=[round(float(v), 2) for v in p0],
                              end=[round(float(v), 2) for v in p1],
                              angle_degrees=round(ang, 2), length_pixels=round(hi-lo, 2),
                              length_width_fraction=round((hi-lo)/w, 4),
                              support_fraction=round(coverage, 3), horizon_reference=reference))
    return sorted(lines, key=lambda q: -q['length_pixels'])


def self_test():
    im = Image.new('RGB', (1000, 600), (80, 80, 80))
    d = ImageDraw.Draw(im)
    d.line((50, 80, 400, 80), fill=(200, 200, 200), width=2)
    d.line((600, 150, 600, 500), fill=(115, 115, 115), width=2)
    d.line((30, 500, 370, 250), fill=(230, 230, 230), width=2)
    d.line((20, 570, 95, 570), fill='white', width=2)
    found = detect(np.asarray(im), horizon=80)
    for angle in (0, 90, 143.75):
        assert any(min(abs(s['angle_degrees']-angle), 180-abs(s['angle_degrees']-angle)) < 2 for s in found), (angle, found)
    assert any(s['horizon_reference'] for s in found)
    assert not any(s['start'][1] > 560 and s['end'][1] > 560 for s in found)
    transparent = np.zeros((600, 1000), np.uint8)
    transparent[200:, 100:] = 255
    assert detect(np.zeros((600, 1000, 3), np.uint8), transparent)
    curve = Image.new('RGB', (1000, 600), 'black')
    ImageDraw.Draw(curve).ellipse((200, 50, 700, 550), outline='white', width=2)
    assert not detect(np.asarray(curve))
    print('SELF_TEST PASS: horizontal, vertical, diagonal, faint, alpha, short, curve, horizon')


def audit(base, scenes, output):
    report = dict(algorithm='full-resolution Sobel NMS + orientation-guided Hough + same-polarity continuous support + orthogonal fit',
                  parameters=PARAMS, stations={})
    for scene in scenes:
        folder = base/scene
        meta = json.loads((folder/'render-info.json').read_text(encoding='utf-8-sig'))
        sky = Image.open(folder/'sky.png').convert('RGBA')
        w, h = sky.size
        c = meta['config']
        horizon = h/2+math.tan(math.radians(c['pitch']))*c['lens']*w/36
        entry = dict(horizon_y=round(horizon, 2), plates={}, non_horizon_count=0, horizon_reference_count=0)
        debug = Image.new('RGB', (w*3, h+48), '#141920')
        draw = ImageDraw.Draw(debug)
        for i, plate in enumerate(('far', 'mid', 'composite')):
            path = folder/(plate+'.png')
            source = Image.open(path).convert('RGBA')
            visible = Image.alpha_composite(sky, source).convert('RGB') if plate != 'composite' else source.convert('RGB')
            alpha = np.asarray(source)[:, :, 3] if plate != 'composite' else None
            lines = detect(np.asarray(visible), alpha, horizon)
            bad = sum(not s['horizon_reference'] for s in lines)
            refs = len(lines)-bad
            entry['plates'][plate] = dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                                         non_horizon_count=bad, horizon_reference_count=refs, lines=lines)
            entry['non_horizon_count'] += bad
            entry['horizon_reference_count'] += refs
            debug.paste(visible, (i*w, 48))
            draw.text((i*w+12, 12), f'{scene} / {plate}: {bad} flagged, {refs} horizon references', fill='white')
            for j, line in enumerate(lines):
                col = '#ffce49' if line['horizon_reference'] else '#ff305c'
                p, q = line['start'], line['end']
                draw.line((p[0]+i*w, p[1]+48, q[0]+i*w, q[1]+48), fill=col, width=3)
                draw.text((p[0]+i*w, p[1]+48), str(j+1), fill=col)
        debug.save(folder/'lines-debug.png')
        report['stations'][scene] = entry
        print(f"{scene}: non-horizon={entry['non_horizon_count']}, horizon={entry['horizon_reference_count']}", flush=True)
    report['total_non_horizon'] = sum(s['non_horizon_count'] for s in report['stations'].values())
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return report


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base', type=Path, default=LAYERS)
    ap.add_argument('--scenes', nargs='+', choices=IDS, default=list(IDS))
    ap.add_argument('--output', type=Path)
    ap.add_argument('--self-test', action='store_true')
    ap.add_argument('--require-zero', nargs='*', choices=IDS, default=[])
    args = ap.parse_args()
    if args.self_test:
        self_test()
    else:
        result = audit(args.base, args.scenes, args.output or args.base/'straight-lines.json')
        if any(result['stations'][s]['non_horizon_count'] for s in args.require_zero):
            raise SystemExit(1)
