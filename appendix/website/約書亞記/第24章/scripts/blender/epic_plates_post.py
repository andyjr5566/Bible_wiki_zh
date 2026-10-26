"""背景圖層後製：大氣透視（霧色取自天空地平線）→ 泛光 → 分色與色調 → 繪畫層（只動 RGB，保留 alpha）→ PNG（RGBA）。
用法：python -I scripts\\blender\\epic_plates_post.py <redsea|ford> [--w 1920 --h 1080]
輸入：lab/renders/layers/_work/<scene>/<plate>.f32、<plate>_depth.f32；輸出：lab/renders/layers/<scene>/<plate>.png 與 composite.png。
"""
import json
import math
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
import numpy as np
from PIL import Image
import epic_post as E
import style_a as S

PITCH_DEG = 1.6
LENS = 28.0
PLATES = ["sky", "far", "sea", "near"]

PARAMS = {
    "redsea-west": {"haze": {"far": (9000.0, 0.6), "sea": (6000.0, 0.85)}, "exposure": 1.0, "sky_exposure": 1.0, "bloom": {}},
    "redsea": {"haze": {"far": (11000.0, 0.72), "sea": (6500.0, 0.9)}, "exposure": 1.0, "sky_exposure": 0.7, "bloom": {"sky": (1.2, 0.55), "sea": (1.0, 0.35)}},
    "ford": {"haze": {"far": (5500.0, 0.8), "sea": (900.0, 0.55)}, "exposure": 1.0, "sky_exposure": 0.7, "bloom": {"sky": (1.2, 0.55), "sea": (1.0, 0.3)}},
}


def load_rgba(path, w, h):
    a = np.fromfile(path, dtype=np.float32).reshape(h, w, 4)
    return np.flipud(a).copy()


def horizon_row(h):
    sensor_h = 36.0 * 9.0 / 16.0
    half = math.atan(sensor_h / 2 / LENS)
    return h / 2 + math.tan(math.radians(PITCH_DEG)) / math.tan(half) * (h / 2)


def fill_transparent(c, a):
    """把透明處的顏色以鄰近不透明處的顏色延伸出去，繪畫濾鏡才不會在邊緣滲進黑色。"""
    out = c * a[:, :, None]
    cover = a.copy()
    for s in (2, 5, 12, 30, 70):
        num = E.gblur(c * a[:, :, None], s)
        den = E.gblur(a, s)[:, :, None]
        fill = num / np.maximum(den, 1e-4)
        k = np.clip(1.0 - cover, 0, 1)[:, :, None]
        out = out + fill * k * np.clip(den * 2.0, 0, 1)
        cover = np.clip(cover + np.clip(den[:, :, 0] * 2.0, 0, 1) * (1 - cover), 0, 1)
    return np.clip(out, 0, 4)


def process(scene, w, h, paint_choice):
    work = os.path.join(ROOT, "lab", "renders", "layers", "_work", scene)
    outd = os.path.join(ROOT, "lab", "renders", "layers", scene)
    os.makedirs(outd, exist_ok=True)
    P = PARAMS[scene]
    raw = {}
    for pl in PLATES:
        raw[pl] = load_rgba(os.path.join(work, pl + ".f32"), w, h)
    yh = int(horizon_row(h))
    sky = raw["sky"][:, :, :3]
    # 霧色：天空地平線上緣，每欄各取一條（水平方向模糊），並限制亮度（避免日盤把整欄染白）
    band = np.minimum(sky[max(yh - 14, 0):max(yh - 3, 1), :, :], 1.8).mean(axis=0)
    hz = E.box_blur(band[None, :, :], max(3, w // 40))[0]
    hz_img = np.broadcast_to(hz[None, :, :], (h, w, 3)).astype(np.float32)
    pc = S.PAINT[paint_choice] if paint_choice else None
    results = {}
    for pl in PLATES:
        rgba = raw[pl]
        a = np.clip(rgba[:, :, 3], 0, 1)
        c = np.where(a[:, :, None] > 1e-4, rgba[:, :, :3] / np.maximum(a[:, :, None], 1e-4), 0.0).astype(np.float32)
        if pl in ("far", "sea"):
            d = load_rgba(os.path.join(work, pl + "_depth.f32"), w, h)
            v = np.where(a > 1e-4, d[:, :, 0] / np.maximum(a, 1e-4), 1.0)
            z = 200.0 * (1.0 / np.maximum(v, 1e-6) - 1.0)
            hd, hm = P["haze"][pl]
            amt = (1.0 - np.exp(-z / hd)) * hm
            c = c * (1 - amt[:, :, None]) + hz_img * amt[:, :, None]
        if pl in P["bloom"]:
            thr, k = P["bloom"][pl]
            c = E.bloom(np.minimum(c, 14.0), thr, k)
        c = E.grade(c, shadows=(0.88, 1.0, 1.18), highs=(1.15, 1.0, 0.84), sat=0.95, split=0.5)
        ldr = E.tonemap_filmic(c * P["exposure"] * (P.get("sky_exposure", 1.0) if pl == "sky" else 1.0))
        if pc:
            filled = fill_transparent(ldr, a) if pl != "sky" else ldr
            filled = np.clip(filled, 0, 1)
            ldr = E.paint_overlay(filled, pc)
            if pl != "sky":
                ldr = ldr * 1.0
        results[pl] = (np.clip(ldr, 0, 1), a)
    comp = np.zeros((h, w, 3), np.float32)
    for pl in PLATES:
        ldr, a = results[pl]
        al = a[:, :, None] if pl != "sky" else np.ones((h, w, 1), np.float32)
        comp = comp * (1 - al) + ldr * al
        rgba8 = np.dstack([ldr, a if pl != "sky" else np.ones((h, w), np.float32)])
        Image.fromarray((np.clip(rgba8, 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA" if pl != "sky" else "RGBA").save(os.path.join(outd, pl + ".png"))
        print("plate", pl, "->", os.path.join(outd, pl + ".png"))
    Image.fromarray((np.clip(comp, 0, 1) * 255 + 0.5).astype(np.uint8)).save(os.path.join(outd, "composite.png"))
    print("composite ->", os.path.join(outd, "composite.png"))


if __name__ == "__main__":
    scene = sys.argv[1]
    w, h = 1920, 1080
    if "--w" in sys.argv:
        w = int(sys.argv[sys.argv.index("--w") + 1]); h = int(sys.argv[sys.argv.index("--h") + 1])
    choice = S.PAINT_CHOICE
    for a_ in sys.argv:
        if a_.startswith("--paint="):
            choice = a_.split("=")[1] or None
    process(scene, w, h, choice)
