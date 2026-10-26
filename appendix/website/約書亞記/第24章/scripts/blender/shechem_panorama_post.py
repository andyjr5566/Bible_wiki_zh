"""Tone-map, paint, composite, and audit the Shechem equirectangular plates."""
import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
import epic_plates_post as plate_post
import epic_post as E
import style_a as S
from check_plates import detect

TIMES = ("dawn", "morning", "afternoon", "dusk", "night")
PAINT = dict(S.PAINT["chosen"])


def read_rgba(path, width, height):
    return np.flipud(np.fromfile(path, dtype=np.float32).reshape(height, width, 4)).copy()


def process_plate(raw, is_sky, exposure):
    alpha = np.clip(raw[:, :, 3], 0.0, 1.0)
    if is_sky:
        alpha[:] = 1.0
    colour = np.where(alpha[:, :, None] > 1e-5,
                      raw[:, :, :3] / np.maximum(alpha[:, :, None], 1e-5), 0.0).astype(np.float32)
    if is_sky:
        colour = E.bloom(np.minimum(colour, 12.0), 1.1, 0.25)
    colour = E.grade(colour, shadows=(0.88, 1.0, 1.18), highs=(1.15, 1.0, 0.84), sat=0.95, split=0.5)
    # Filmic returns linear RGB. Encode once before writing an sRGB PNG.
    ldr = E.lin_to_srgb(E.tonemap_filmic(colour * exposure))
    if not is_sky:
        # The terrain plate is a continuous horizon. Extend each column's
        # nearest opaque colour upward, without repeated full-frame blurs.
        rows = np.arange(alpha.shape[0])[:, None]
        opaque = alpha > .05
        nearest = np.minimum.accumulate(np.where(opaque, rows, alpha.shape[0]-1)[::-1], axis=0)[::-1]
        filled = ldr[nearest, np.arange(alpha.shape[1])[None, :]]
        ldr = np.where(opaque[:, :, None], ldr, filled)
    # Fine strokes at final resolution, without coarse quantised sky patches.
    paint = dict(PAINT, amount=0.16, kuwahara=0, strokes=0, levels=64,
                 edge_px=0.25, paper=0)
    ldr = E.paint_overlay(np.clip(ldr, 0.0, 1.0), paint)
    rgba = np.dstack((np.clip(ldr, 0.0, 1.0), alpha))
    return Image.fromarray((rgba * 255.0 + 0.5).astype(np.uint8), "RGBA")


def save_contact(out_dir):
    width, height = 1536, 768
    label_h, gap = 32, 18
    sheet_h = 14 + len(TIMES) * (height + label_h + gap)
    sheet = Image.new("RGB", (width, sheet_h), "#1a1d28")
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 23)
    except OSError:
        font = ImageFont.load_default()
    y = 8
    for time_name in TIMES:
        draw.text((18, y), time_name.upper(), font=font, fill="#f5dfb9")
        y += label_h
        image = Image.open(out_dir / f"composite-{time_name}.png").convert("RGB")
        image = image.resize((width, height), Image.Resampling.LANCZOS)
        sheet.paste(image, (0, y))
        y += height + gap
    sheet.save(out_dir / "shechem-contact.png")


def audit(out_dir, width, height):
    report = {"checker": "scripts/blender/check_plates.py:detect",
              "scope": "alpha silhouette of hills plate; no horizon exemption",
              "minimum_line_width_fraction": 0.12,
              "times": {}, "total_ridgeline_long_lines": 0}
    for time_name in TIMES:
        hills = np.asarray(Image.open(out_dir / f"hills-{time_name}.png").convert("RGBA"))
        alpha = hills[:, :, 3]
        lines = detect(np.zeros((height, width, 3), dtype=np.uint8), alpha=alpha)
        report["times"][time_name] = {"long_straight_ridge_lines": len(lines), "lines": lines}
        report["total_ridgeline_long_lines"] += len(lines)
        print(f"CHECK {time_name}: long straight ridge lines={len(lines)}", flush=True)
    (out_dir / "straight-lines.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--w", type=int, default=4096)
    parser.add_argument("--h", type=int, default=2048)
    args = parser.parse_args()
    args.work.mkdir(parents=True, exist_ok=True)
    args.out.mkdir(parents=True, exist_ok=True)
    for time_name in TIMES:
        raw_sky = read_rgba(args.work / time_name / "sky.f32", args.w, args.h)
        raw_hills = read_rgba(args.work / time_name / "hills.f32", args.w, args.h)
        sky = process_plate(raw_sky, True, 0.82 if time_name != "night" else 1.3)
        hills_exposure = .9 if time_name in ("dawn", "morning", "afternoon") else .35 if time_name == "dusk" else .55
        hills = process_plate(raw_hills, False, hills_exposure)
        sky.save(args.out / f"sky-{time_name}.png")
        # read_rgba already converts Blender's bottom-up rows. Both plates use
        # the same orientation; a second flip puts solid terrain over the sky.
        hill_alpha = np.asarray(hills)[:, :, 3]
        if np.any(hill_alpha[0] > 5) or np.any(hill_alpha[-1] < 250):
            raise ValueError(f"Terrain orientation invalid: {time_name}")
        hills.save(args.out / f"hills-{time_name}.png")
        Image.alpha_composite(sky, hills).convert("RGB").save(args.out / f"composite-{time_name}.png")
        print(f"PLATE_COMPLETE {time_name}", flush=True)

    source_path = args.work / "shechem-panorama-source.json"
    if source_path.exists():
        source = json.loads(source_path.read_text(encoding="utf-8"))
        source["postprocess"] = {"encoding": "linear filmic -> sRGB", "paint_amount": 0.16,
                                 "day_hills_exposure": .9, "dusk_hills_exposure": .35,
                                 "night_hills_exposure": .55, "hills_extra_vertical_flip": False}
        (args.out / "shechem-panorama-info.json").write_text(
            json.dumps(source, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    save_contact(args.out)
    report = audit(args.out, args.w, args.h)
    if report["total_ridgeline_long_lines"] != 0:
        raise SystemExit("Long straight mountain ridge lines remain; inspect straight-lines.json")


if __name__ == "__main__":
    main()
