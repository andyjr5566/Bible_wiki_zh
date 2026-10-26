"""史詩樣張後製（系統 Python + numpy + PIL）。

輸入：Blender 輸出的 <base>.png（美術圖）、<base>_depth.png（深度）、<base>.json（太陽位置）。
風格：
  A 史詩剪影：大氣透視、體積光束（螢幕空間放射模糊）、泛光、暖冷分色、暗角、顆粒。
  B 寫實：輕霧、淺景深、膠片色調。
  C 繪畫：Kuwahara 色塊 + 沿流向的筆觸紋理 + 紙紋 + 色彩收斂。

用法：python -I scripts\\blender\\epic_post.py <base 不含副檔名> <A|B|C> <輸出 png> [--w 1280 --h 720]
"""
import json
import sys as _sys
try:
    _sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
import math
import os
import sys

import numpy as np
from PIL import Image, ImageFilter


# ----------------------------------------------------------------------------- 基本工具
def srgb_to_lin(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(c):
    c = np.clip(c, 0, None)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)


def load16(path):
    im = Image.open(path)
    a = np.array(im).astype(np.float32)
    if a.ndim == 2:
        a = a[:, :, None]
    a = a[:, :, :3] / (65535.0 if im.mode.startswith("I;16") or a.max() > 255 else 255.0)
    return a


def box_blur(a, r):
    """分離式盒狀模糊（可處理 HxW 或 HxWxC），邊緣夾住。"""
    if r < 1:
        return a
    r = int(r)
    k = 2 * r + 1
    out = a
    for ax in (0, 1):
        pad = [(0, 0)] * out.ndim
        pad[ax] = (r + 1, r)
        p = np.pad(out, pad, mode="edge")
        cs = np.cumsum(p, axis=ax, dtype=np.float64)
        n = out.shape[ax]
        sl_hi = [slice(None)] * out.ndim
        sl_lo = [slice(None)] * out.ndim
        sl_hi[ax] = slice(k, k + n)
        sl_lo[ax] = slice(0, n)
        out = ((cs[tuple(sl_hi)] - cs[tuple(sl_lo)]) / k).astype(np.float32)
    return out


def gblur(a, sigma):
    """三次盒狀模糊近似高斯。"""
    if sigma < 0.5:
        return a
    r = max(1, int(round(math.sqrt(12 * sigma * sigma / 3 + 1) / 2)))
    out = a
    for _ in range(3):
        out = box_blur(out, r)
    return out


def resize(a, w, h):
    if a.shape[1] == w and a.shape[0] == h:
        return a
    chans = []
    for c in range(a.shape[2]):
        im = Image.fromarray(a[:, :, c].astype(np.float32), mode="F")
        chans.append(np.array(im.resize((w, h), Image.LANCZOS)))
    return np.stack(chans, axis=-1)


def load_f32(base, w, h):
    a = np.fromfile(base + ".f32", dtype=np.float32).reshape(h, w, 4)
    return np.flipud(a[:, :, :3]).copy()      # Blender 的列由下往上


def depth_meters(dimg):
    v = dimg[:, :, 0]
    sky = v < 2e-4
    z = 200.0 * (1.0 / np.maximum(v, 1e-6) - 1.0)
    z[sky] = 1e9
    # 邊緣像素取 3x3 內最近的深度，避免天際線被當成遠景而發白
    zp = np.pad(z, 1, mode="edge")
    zm = z.copy()
    for dy in (0, 1, 2):
        for dx in (0, 1, 2):
            zm = np.minimum(zm, zp[dy:dy + z.shape[0], dx:dx + z.shape[1]])
    sky2 = sky & (zm > 1e8)
    zw = dimg[:, :, 1] * 3500.0 - 500.0
    xw = dimg[:, :, 2] * 1800.0 - 1400.0
    return zm, sky2, zw, xw


def sample_bilinear(a, x, y):
    h, w = a.shape[:2]
    x = np.clip(x, 0, w - 1.001)
    y = np.clip(y, 0, h - 1.001)
    x0 = x.astype(np.int32)
    y0 = y.astype(np.int32)
    fx = (x - x0)[..., None] if a.ndim == 3 else (x - x0)
    fy = (y - y0)[..., None] if a.ndim == 3 else (y - y0)
    a00 = a[y0, x0]
    a10 = a[y0, x0 + 1]
    a01 = a[y0 + 1, x0]
    a11 = a[y0 + 1, x0 + 1]
    return (a00 * (1 - fx) + a10 * fx) * (1 - fy) + (a01 * (1 - fx) + a11 * fx) * fy


def vignette(h, w, strength=0.35, power=2.2):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) / 1.4142
    return 1.0 - strength * np.clip(d, 0, 1) ** power


def grain(h, w, amount=0.02, seed=1):
    rng = np.random.default_rng(seed)
    g = rng.normal(0, 1, (h, w)).astype(np.float32)
    g = gblur(g, 0.7)
    return g[:, :, None] * amount


def bloom(lin, thr=1.0, strength=0.35, sigmas=(4, 12, 32)):
    lum = lin.max(axis=2, keepdims=True)
    bright = lin * np.clip((lum - thr) / np.maximum(lum, 1e-4), 0, 1)
    acc = np.zeros_like(lin)
    for s in sigmas:
        acc += gblur(bright, s)
    return lin + acc * strength / len(sigmas)


def tonemap_filmic(x, contrast=1.0):
    """簡易 filmic 曲線（ACES 近似），輸入線性。"""
    x = x * 0.9
    a, b, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14
    y = (x * (a * x + b)) / (x * (c * x + d) + e)
    return np.clip(y, 0, 1)


def grade(lin, shadows=(0.92, 1.0, 1.12), highs=(1.12, 1.0, 0.86), sat=1.0, split=0.35, gamma=1.0):
    lum = (lin * np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)).sum(axis=2, keepdims=True)
    t = np.clip(lum / (lum + 0.5), 0, 1)
    sh = np.array(shadows, dtype=np.float32)
    hi = np.array(highs, dtype=np.float32)
    mult = sh * (1 - t) + hi * t
    out = lin * (1 + (mult - 1) * split)
    lum2 = (out * np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)).sum(axis=2, keepdims=True)
    out = lum2 + (out - lum2) * sat
    return np.clip(out, 0, None) ** gamma




def haze_from_sky(lin, sky, default=(0.6, 0.5, 0.45)):
    """霧色取自每一欄「最低的天空像素」（地平線上緣）的顏色，讓遠景融進天空。回傳 (h, w, 3)。"""
    h, w = sky.shape
    out = np.zeros((h, w, 3), np.float32)
    cols = np.zeros((w, 3), np.float32)
    ok = np.zeros(w, bool)
    ys = np.arange(h)[:, None]
    # 每欄最後一個天空像素的列
    last = np.where(sky, ys, -1).max(axis=0)
    for x in range(w):
        y = last[x]
        if y >= 3:
            cols[x] = np.minimum(lin[max(0, y - 6):y - 1, x], 1.6).mean(axis=0)
            ok[x] = True
    if ok.any():
        idx = np.arange(w)
        for c in range(3):
            cols[:, c] = np.interp(idx, idx[ok], cols[ok][:, c])
        k = max(3, w // 60)
        cols = box_blur(cols[None, :, :], k)[0]
    else:
        cols[:] = np.array(default, np.float32)
    out[:] = cols[None, :, :]
    return out


def smoothstep_np(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def apply_dark(lin, z, sky, meta, p):
    """第 7 節的黑暗：世界座標 x 落在帶狀範圍內的像素壓暗成近黑（含雲狀紋理），帶後方（更遠）也被遮暗；天空整體壓暗。"""
    d = p.get("dark")
    if not d:
        return lin
    h, w = lin.shape[:2]
    xw = meta["xw"]
    zw = meta["zw"]
    xc, core, soft = d.get("xc", -85.0), d.get("core", 22.0), d.get("soft", 38.0)
    rng = np.random.default_rng(5)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    n = np.zeros((h, w), np.float32)
    amp = 1.0
    for s in (90, 40, 18):
        g = gblur(rng.random((h, w)).astype(np.float32), s)
        g = (g - g.mean()) / (g.std() + 1e-6)
        n += g * amp
        amp *= 0.55
    n = np.clip(0.55 + 0.32 * n, 0, 1)
    dist = np.abs(xw + (n - 0.55) * d.get('warp', 55.0) - xc) - core
    band = 1.0 - smoothstep_np(0.0, soft, dist)
    hf = 1.0 - smoothstep_np(d.get("zh0", 40.0), d.get("zh1", 110.0), zw)
    behind = smoothstep_np(xc - core - soft * 0.2, xc - core - soft * 1.2, xw)     # 越過帶子更遠
    fy = 1.0
    if 'yw' in meta:
        fy = 1.0 - smoothstep_np(d.get('y0', 70.0), d.get('y1', 190.0), np.abs(meta['yw']))
    band = band * fy
    D = np.clip(band * hf * (0.55 + 0.6 * n) * d.get("k", 1.25), 0, 0.97)
    D = np.where(sky, 0.0, D)
    dark = np.array(d.get("color", (0.015, 0.014, 0.024)), dtype=np.float32)
    bm = np.clip(behind * fy * d.get("behind", 0.62) * (0.75 + 0.5 * n), 0, 0.9)
    bm = np.where(sky, 0.0, bm)
    out = lin * (1 - D[:, :, None]) + dark * D[:, :, None]
    out = out * (1 - bm[:, :, None]) + dark * bm[:, :, None]
    # 天空：整體壓暗，上方更暗
    sk = d.get("sky", 0.5)
    vgrad = 1.0 - 0.6 * (1.0 - yy / h)
    sdark = np.clip(sk * vgrad * (0.7 + 0.5 * n), 0, 0.95)
    out = np.where(sky[:, :, None], out * (1 - sdark[:, :, None]) + dark * sdark[:, :, None], out)
    return out


# ----------------------------------------------------------------------------- 繪畫質感在 A 之上的疊加（A+C）
def kuwahara_placeholder():
    pass


def style_A(lin, z, sky, meta, p):
    h, w = lin.shape[:2]
    if p.get('hdr_cap'):
        lin = np.minimum(lin, p['hdr_cap'])
    sun = meta.get("sun_xy")
    sun_front = meta.get("sun_front", False)
    # 大氣透視：遠處往暖藍霧色褪去；靠近太陽的一側霧更暖更亮
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    zcap = p.get('zcap', 30000.0)
    zs = np.where(sky, zcap, z)
    k = p.get("haze_k", 1.0)
    amt = 1.0 - np.exp(-np.minimum(zs, zcap) / (p.get("haze_dist", 2600.0) / k))
    zwm = meta['zw']
    mz0 = p.get('mist_z0', 800.0)
    mH = p.get('mist_H', 90.0)
    mist = (1.0 - np.exp(-np.minimum(zs, 8000) * p.get('mist_rho', 0.0016) * np.exp(-np.maximum(zwm - mz0, 0) / mH))) * (~sky)
    amt = 1.0 - (1.0 - amt) * (1.0 - mist)
    amt = amt[:, :, None]
    cool = np.array(p.get("haze_cool", (0.34, 0.42, 0.58)), dtype=np.float32)
    warm = np.array(p.get("haze_warm", (1.25, 0.70, 0.34)), dtype=np.float32)
    if sun is not None:
        sx, sy = sun[0] * w, sun[1] * h
        d = np.sqrt(((xx - sx) / w) ** 2 + ((yy - sy) / h * 0.9) ** 2)
        wf = np.exp(-(d / 0.42) ** 2)[:, :, None] if sun_front else np.full((h, w, 1), 0.25, np.float32)
    else:
        wf = np.full((h, w, 1), 0.25, np.float32)
    hz = cool * (1 - wf) + warm * wf
    if p.get('haze_sky', True):
        hs = haze_from_sky(lin, sky)
        hz = hs * p.get('haze_sky_k', 0.92) + hz * 0.0
    # 近地面霧：靠近地平線（畫面中段）更濃
    hz = hz * p.get("haze_gain", 1.0)
    amt = amt * (~sky)[:, :, None]
    hm = p.get('haze_mix', 0.85)
    lin = lin * (1 - amt * hm) + hz * amt * hm
    # 體積光束：以太陽為中心的放射模糊，只取天空與亮部、被地形遮擋
    if sun is not None and sun_front:
        sx, sy = sun[0] * w, sun[1] * h
        lum = lin.max(axis=2)
        mask = (sky.astype(np.float32) * 1.0 + np.clip(lum - 1.5, 0, 4) * 0.4)
        mask = np.clip(mask, 0, 1.5)
        # 日盤附近的光暈作為光源
        d = np.sqrt((xx - sx) ** 2 + (yy - sy) ** 2) / w
        src = mask * np.exp(-(d / 0.5) ** 2) * (0.35 + 1.2 * np.exp(-(d / 0.04) ** 2))
        src = gblur(src, p.get('ray_soft', 10.0))
        src = src[:, :, None] * np.array(p.get("ray_color", (1.0, 0.72, 0.42)), dtype=np.float32)
        acc = np.zeros_like(src)
        steps = 48
        dens = p.get("ray_len", 0.85)
        for i in range(steps):
            s = 1.0 - dens * (i / steps)
            xs = sx + (xx - sx) * s
            ys = sy + (yy - sy) * s
            acc += sample_bilinear(src, xs, ys) * (0.965 ** i)
        rays = np.minimum(acc / steps * p.get("ray_gain", 3.0), p.get('ray_max', 0.7))
        # 地面（非天空）接收光束，天空本身不重複加
        lin = lin + rays * (1.0 - 0.6 * sky[:, :, None])
    lin = bloom(lin, p.get("bloom_thr", 1.1), p.get("bloom", 0.5))
    lin = grade(lin, shadows=p.get("shadows", (0.85, 1.0, 1.22)), highs=p.get("highs", (1.15, 1.0, 0.82)), sat=p.get("sat", 1.05), split=0.55)
    ldr = tonemap_filmic(lin * p.get("exposure", 1.0))
    if p.get('paint'):
        ldr = paint_overlay(ldr, p['paint'])
    ldr = ldr * vignette(h, w, p.get("vig", 0.5))[:, :, None]
    ldr = ldr + grain(h, w, 0.012)
    return np.clip(ldr, 0, 1)


# ----------------------------------------------------------------------------- 風格 B：寫實
def style_B(lin, z, sky, meta, p):
    h, w = lin.shape[:2]
    focus = p.get("focus_m", 25.0)
    # 淺景深：依深度混合三層模糊
    zz = np.where(sky, 1e5, z)
    coc = np.clip(np.abs(1.0 / focus - 1.0 / np.maximum(zz, 0.5)) * p.get("dof_k", 22.0), 0, 1)
    b1 = gblur(lin, 2.0)
    b2 = gblur(lin, 5.5)
    b3 = gblur(lin, 11.0)
    c = coc[:, :, None]
    out = np.where(c < 0.33, lin * (1 - c / 0.33) + b1 * (c / 0.33),
                   np.where(c < 0.66, b1 * (1 - (c - 0.33) / 0.33) + b2 * ((c - 0.33) / 0.33),
                            b2 * (1 - (c - 0.66) / 0.34) + b3 * ((c - 0.66) / 0.34)))
    lin = out
    # 輕霧
    amt = (1.0 - np.exp(-np.minimum(zz, 40000) / p.get("haze_dist", 5200.0)))[:, :, None] * (~sky)[:, :, None]
    hz = haze_from_sky(lin, sky) * p.get('haze_sky_k', 0.9)
    lin = lin * (1 - amt * p.get('haze_mix', 0.75)) + hz * amt * p.get('haze_mix', 0.75)
    lin = bloom(lin, p.get("bloom_thr", 1.3), p.get("bloom", 0.28))
    lin = grade(lin, shadows=(0.95, 1.0, 1.08), highs=(1.06, 1.0, 0.92), sat=p.get("sat", 1.0), split=0.4)
    ldr = tonemap_filmic(lin * p.get("exposure", 1.0))
    ldr = ldr * vignette(h, w, 0.32)[:, :, None]
    ldr = ldr + grain(h, w, 0.018)
    return np.clip(ldr, 0, 1)


# ----------------------------------------------------------------------------- 風格 C：繪畫
def kuwahara(img, r):
    """廣義 Kuwahara（四象限）：保邊的色塊化。img: HxWx3 [0,1]"""
    h, w = img.shape[:2]
    pad = r
    p = np.pad(img, ((pad, pad), (pad, pad), (0, 0)), mode="edge")
    gray = p.mean(axis=2)

    def integral(a):
        return np.pad(np.cumsum(np.cumsum(a, axis=0, dtype=np.float64), axis=1, dtype=np.float64), ((1, 0), (1, 0)) + ((0, 0),) * (a.ndim - 2))

    I = integral(p)
    I2 = integral(gray * gray)
    Ig = integral(gray)

    def rect(Iarr, y0, y1, x0, x1):
        return Iarr[y1, x1] - Iarr[y0, x1] - Iarr[y1, x0] + Iarr[y0, x0]

    yy, xx = np.mgrid[0:h, 0:w]
    yy = yy + pad
    xx = xx + pad
    best_var = np.full((h, w), 1e9, dtype=np.float64)
    best_mean = np.zeros((h, w, 3), dtype=np.float64)
    n = (r + 1) ** 2
    for (dy0, dy1, dx0, dx1) in ((-r, 0, -r, 0), (-r, 0, 0, r), (0, r, -r, 0), (0, r, 0, r)):
        y0, y1 = yy + dy0, yy + dy1 + 1
        x0, x1 = xx + dx0, xx + dx1 + 1
        s = rect(I, y0, y1, x0, x1)
        s2 = rect(I2, y0, y1, x0, x1)
        sg = rect(Ig, y0, y1, x0, x1)
        mean = s / n
        var = s2 / n - (sg / n) ** 2
        m = var < best_var
        best_var = np.where(m, var, best_var)
        best_mean = np.where(m[:, :, None], mean, best_mean)
    return best_mean.astype(np.float32)


p_noise_blur = 1.4


def flow_texture(lum, length=14, seed=3, scale=1.0):
    """沿影像等亮度線方向的線積分卷積（LIC）紋理，做筆觸感。"""
    h, w = lum.shape
    rng = np.random.default_rng(seed)
    noise = gblur(rng.random((h, w)).astype(np.float32), p_noise_blur)
    noise = (noise - noise.mean()) / (noise.std() + 1e-6)
    sm = gblur(lum, 3.0)
    gy, gx = np.gradient(sm)
    # 筆觸沿等亮度線（垂直於梯度）
    tx, ty = -gy, gx
    mag = np.sqrt(tx * tx + ty * ty) + 1e-4
    # 梯度弱的地方用緩慢旋轉的場代替，避免死區
    g0 = gblur(rng.random((h, w)).astype(np.float32), 30)
    g0 = (g0 - g0.mean()) / (g0.std() + 1e-6)
    ang = g0 * 2.2
    wk = np.clip(mag * 30.0, 0, 1)
    tx = (tx / mag) * wk + np.cos(ang) * (1 - wk)
    ty = (ty / mag) * wk + np.sin(ang) * (1 - wk)
    nrm = np.sqrt(tx * tx + ty * ty) + 1e-6
    tx /= nrm
    ty /= nrm
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    acc = noise.copy()
    cnt = 1.0
    for sgn in (1, -1):
        px, py = xx.copy(), yy.copy()
        for i in range(length):
            vx = sample_bilinear(tx, px, py)
            vy = sample_bilinear(ty, px, py)
            px = px + sgn * vx * 1.2 * scale
            py = py + sgn * vy * 1.2 * scale
            acc += sample_bilinear(noise, px, py)
            cnt += 1
    return acc / cnt



def paint_strokes(ref, layers, seed=4, jitter=0.035):
    """Hertzmann 式筆觸：依序以粗到細的短線條（寬度＝筆刷），顏色取自參考圖，方向垂直於亮度梯度（沿形體等高線）。"""
    from PIL import ImageDraw
    h, w = ref.shape[:2]
    rng = np.random.default_rng(seed)
    base = gblur(ref, 3.0)
    canvas = Image.fromarray((np.clip(base, 0, 1) * 255).astype(np.uint8))
    dr = ImageDraw.Draw(canvas)
    lum = ref.mean(axis=2)
    for (brush, length, spacing, edge_only) in layers:
        sm = gblur(lum, max(1.5, brush * 0.7))
        gy, gx = np.gradient(sm)
        mag = np.sqrt(gx * gx + gy * gy)
        ang = np.arctan2(gx, -gy)          # 垂直於梯度
        # 弱梯度處：用緩慢變化的亂數方向
        g0 = gblur(rng.random((h, w)).astype(np.float32), 25)
        g0 = (g0 - g0.mean()) / (g0.std() + 1e-6)
        wk = np.clip(mag * 40.0, 0, 1)
        ang = ang * wk + (g0 * 0.9 - 0.4) * (1 - wk)
        refb = gblur(ref, max(1.0, brush * 0.5)) if brush > 2 else ref
        ys = np.arange(spacing / 2, h, spacing)
        xs = np.arange(spacing / 2, w, spacing)
        pts = [(float(x + rng.uniform(-0.5, 0.5) * spacing), float(y + rng.uniform(-0.5, 0.5) * spacing)) for y in ys for x in xs]
        order = rng.permutation(len(pts))
        thr = np.percentile(mag, 62 if brush > 2.5 else 75) if edge_only else -1
        for oi in order:
            x, y = pts[oi]
            xi, yi = int(min(max(x, 0), w - 1)), int(min(max(y, 0), h - 1))
            if edge_only and mag[yi, xi] < thr:
                continue
            a = ang[yi, xi]
            L = length * rng.uniform(0.7, 1.25)
            dx, dy = math.cos(a) * L / 2, math.sin(a) * L / 2
            c = refb[yi, xi] + rng.normal(0, jitter, 3)
            col = tuple(int(v) for v in np.clip(c * 255, 0, 255))
            dr.line([(x - dx, y - dy), (x + dx, y + dy)], fill=col, width=max(1, int(round(brush))))
    return np.asarray(canvas).astype(np.float32) / 255.0


def style_C(lin, z, sky, meta, p):
    h, w = lin.shape[:2]
    # 先做大氣透視（較柔、偏繪畫）
    zs = np.where(sky, 30000.0, z)
    amt = (1.0 - np.exp(-np.minimum(zs, 30000) / p.get("haze_dist", 2200.0)))[:, :, None] * (~sky)[:, :, None]
    hz = haze_from_sky(lin, sky) * 0.95
    lin = lin * (1 - amt * 0.8) + hz * amt * 0.8
    lin = bloom(lin, 1.0, 0.45)
    lin = grade(lin, shadows=p.get("shadows", (0.82, 0.95, 1.25)), highs=p.get("highs", (1.2, 1.0, 0.78)), sat=p.get("sat", 1.2), split=0.8)
    base = tonemap_filmic(lin * p.get("exposure", 1.0))
    # 色塊化：兩層 Kuwahara（大塊 + 小塊）
    k1 = kuwahara(base, 6)
    k2 = kuwahara(base, 3)
    d = np.abs(base - gblur(base, 2.0)).sum(axis=2, keepdims=True)
    detail = np.clip(d * 6.0, 0, 1)
    img = k1 * (1 - detail * 0.6) + k2 * (detail * 0.6)
    # 輪廓：深度與亮度的邊緣，淡淡的深褐色
    lumi = img.mean(axis=2)
    gy, gx = np.gradient(gblur(lumi, 1.2))
    edge = np.clip(np.sqrt(gx * gx + gy * gy) * 14.0, 0, 1)
    zz = np.log(np.minimum(zs, 30000) + 1.0)
    gzy, gzx = np.gradient(gblur(zz, 1.0))
    zedge = np.clip(np.sqrt(gzx * gzx + gzy * gzy) * 3.0, 0, 1)
    ink = np.clip(edge * 0.55 + zedge * 0.6, 0, 1)[:, :, None]
    inkcol = np.array((0.16, 0.1, 0.09), dtype=np.float32)
    img = img * (1 - ink * 0.5) + inkcol * ink * 0.5
    # 筆觸：粗到細三層（Hertzmann）；細筆只畫在邊緣與細節處
    img = paint_strokes(img, [(11, 34, 9, False), (6, 18, 4.5, False), (3.5, 9, 2.6, True), (2, 5, 2.0, True)], seed=p.get("seed", 4))
    # 色彩收斂（柔性海報化）
    q = p.get("levels", 14)
    img = np.clip(img, 0, 1)
    img = np.round(img * q) / q * 0.5 + img * 0.5
    # 紙紋與暈染
    rng = np.random.default_rng(9)
    paper = gblur(rng.normal(0, 1, (h, w)).astype(np.float32), 1.2) + 0.6 * gblur(rng.normal(0, 1, (h, w)).astype(np.float32), 4.0)
    img = img * (1 + paper[:, :, None] * 0.025)
    img = img * vignette(h, w, 0.42)[:, :, None]
    return np.clip(img, 0, 1)



def paint_overlay(ldr, cfg):
    """A+C：在已經調好光影的 A 影像上疊一層輕的繪本質感。保留逆光、體積光與大氣透視，只改表面。
    cfg：amount 總強度 0..1；kuwahara 色塊半徑（以 1280 寬為準，高解析度自動放大）；levels 柔性色階；strokes 筆觸層強度；
    paper 畫布紋與水彩暈染；edge_soft 邊緣柔化；warm 暖色繪本色盤；seed。"""
    a = float(cfg.get("amount", 0.5))
    if a <= 0:
        return ldr
    h, w = ldr.shape[:2]
    sc = w / 1280.0
    rng = np.random.default_rng(cfg.get("seed", 4))
    # 1. 邊緣柔化：輪廓稍微暈開（繪畫沒有電腦渲染的銳利鋸齒）
    soft = gblur(ldr, cfg.get("edge_px", 1.1) * sc)
    es = cfg.get("edge_soft", 0.6) * a
    img = ldr * (1 - es) + soft * es
    # 2. 色塊：Kuwahara
    kr = int(round(cfg.get("kuwahara", 3) * sc))
    if kr >= 1:
        k = kuwahara(img, kr)
        img = img * (1 - a * 0.9) + k * (a * 0.9)
    # 3. 筆觸：粗到細兩層短筆（顏色取自影像本身）
    sa = cfg.get("strokes", 0.6) * a
    if sa > 0.02:
        layers = [(10 * sc, 30 * sc, 8 * sc, False), (5 * sc, 14 * sc, 4.2 * sc, False)]
        sl = paint_strokes(img, layers, seed=cfg.get("seed", 4), jitter=0.03)
        img = img * (1 - sa) + sl * sa
    # 4. 柔性色階（輕度 posterize）
    lv = cfg.get("levels", 14)
    q = np.round(img * lv) / lv
    img = img * (1 - 0.55 * a) + q * (0.55 * a)
    # 5. 暖色繪本色盤：暗部偏暖褐、亮部偏奶油，藍色稍微收斂
    wm = cfg.get("warm", 0.35) * a
    lum = img.mean(axis=2, keepdims=True)
    shadow_tint = np.array([1.10, 0.92, 0.82], np.float32)
    high_tint = np.array([1.04, 1.0, 0.92], np.float32)
    t = np.clip(lum * 1.4, 0, 1)
    tint = shadow_tint * (1 - t) + high_tint * t
    img = img * (1 + (tint - 1) * wm * 2.2)
    # 6. 水彩暈染（低頻明暗與色相不均）+ 畫布織紋（很淡）
    pa = cfg.get("paper", 0.05) * a
    if pa > 0:
        wash = gblur(rng.normal(0, 1, (h, w)).astype(np.float32), 38 * sc)
        wash = wash / (wash.std() + 1e-6)
        wash2 = gblur(rng.normal(0, 1, (h, w)).astype(np.float32), 90 * sc)
        wash2 = wash2 / (wash2.std() + 1e-6)
        tint2 = np.stack([wash * 0.7 + wash2 * 0.3, wash * 0.2, -wash * 0.5 - wash2 * 0.3], axis=-1)
        img = img * (1 + tint2 * pa * 1.6)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        weave = (np.sin(xx * 2.1 / sc) * np.sin(yy * 1.9 / sc)) * 0.5 + 0.5
        fib = gblur(rng.normal(0, 1, (h, w)).astype(np.float32), 1.6 * sc)
        fib = fib / (fib.std() + 1e-6)
        img = img * (1 + ((weave - 0.5) * 0.5 + fib * 0.35)[:, :, None] * pa * 0.45)
    return np.clip(img, 0, 1)


def style_RAW(lin, z, sky, meta, p):
    return np.clip(tonemap_filmic(lin * p.get("exposure", 1.0)), 0, 1)


STYLES = {"A": style_A, "B": style_B, "C": style_C, "RAW": style_RAW}


def run(base, style, out, w=1280, h=720, params=None):
    p = params or {}
    meta = json.load(open(base + ".json", encoding="utf-8"))
    rw, rh = meta["res"]
    lin = load_f32(base, rw, rh) * float(meta.get("hdr_scale", 1.0))
    depth = load_f32(base + "_depth", rw, rh)
    z, sky, zw, xw = depth_meters(depth)
    meta['zw'] = zw
    meta['xw'] = xw
    if os.path.exists(base + '_depth2.f32'):
        d2 = load_f32(base + '_depth2', rw, rh)
        meta['yw'] = d2[:, :, 0] * 3000.0 - 1500.0
    lin = apply_dark(lin, z, sky, meta, p)
    img = STYLES[style](lin, z, sky, meta, p)
    im = Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8))
    if im.size != (w, h):
        im = im.resize((w, h), Image.LANCZOS)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    im.save(out)
    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    base, style, out = args[0], args[1], args[2]
    params = {}
    if len(args) > 3:
        params = json.loads(args[3])
    osz = params.pop('out_size', None)
    if osz:
        run(base, style, out, w=osz[0], h=osz[1], params=params)
    else:
        run(base, style, out, params=params)
    print("post ->", out)
