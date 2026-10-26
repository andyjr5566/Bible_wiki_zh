"""史詩段落樣張：由 collect/dem 的真實高程產生 Blender 讀得進去的地形網格（系統 Python + numpy）。

Blender 5.2 的 numpy 被應用程式控制封鎖（linalg DLL），所以地形先在這裡算好，
寫成原始二進位檔（float32 / uint32），再由 Blender 端用 array 模組讀進去。

用法（PowerShell，從本站根目錄）：
    python -I scripts\\blender\\epic_prep.py cover
    python -I scripts\\blender\\epic_prep.py s1 | s2 | s3 | s4 | all

輸出：lab/renders/epic/_cache/<scene>/<layer>.{v,q,veg,sea}.bin 與 <scene>.json（圖層清單與原點）。
座標：本地公尺，x = 東、y = 北、z = 海拔（乘 vexag）。原點 = 該場景的 (lon0, lat0)。
縮放：x = R*(lon-lon0)*cos(lat)，y = R*(lat-lat0)（正弦投影，夠近）。
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import epic_river_geo as RG

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
DEM_DIR = os.path.join(ROOT, "collect", "dem")
CACHE = os.path.join(ROOT, "lab", "renders", "epic", "_cache")
R_EARTH = 6371008.8
OFFSET = 11000.0


# ----------------------------------------------------------------------------- DEM
class Dem:
    def __init__(self, name):
        self.name = name
        meta = json.load(open(os.path.join(DEM_DIR, f"{name}_meta.json"), encoding="utf-8"))
        self.zoom = meta["zoom"]
        self.ox = meta["origin_world_px"]["origin_x"]
        self.oy = meta["origin_world_px"]["origin_y"]
        self.N = 256.0 * 2 ** self.zoom
        a = np.array(Image.open(os.path.join(DEM_DIR, f"{name}_height.png"))).astype(np.float32) - OFFSET
        self.h = a
        self.H, self.W = a.shape
        bb = meta["actual_bbox"]
        self.bbox = (bb["west"], bb["south"], bb["east"], bb["north"])

    def lonlat_to_px(self, lon, lat):
        X = (lon + 180.0) / 360.0 * self.N - self.ox
        s = np.sin(np.radians(lat))
        Y = (0.5 - np.log((1 + s) / (1 - s)) / (4 * math.pi)) * self.N - self.oy
        return X, Y

    def sample(self, lon, lat):
        """Catmull-Rom 雙三次取樣，座標在圖外時夾到邊。"""
        X, Y = self.lonlat_to_px(lon, lat)
        X = np.clip(X - 0.5, 0, self.W - 1.001)
        Y = np.clip(Y - 0.5, 0, self.H - 1.001)
        x0 = np.floor(X).astype(np.int32)
        y0 = np.floor(Y).astype(np.int32)
        fx = (X - x0).astype(np.float32)
        fy = (Y - y0).astype(np.float32)

        def w(t):
            t2 = t * t
            t3 = t2 * t
            return (
                -0.5 * t3 + t2 - 0.5 * t,
                1.5 * t3 - 2.5 * t2 + 1.0,
                -1.5 * t3 + 2.0 * t2 + 0.5 * t,
                0.5 * t3 - 0.5 * t2,
            )

        wx = w(fx)
        wy = w(fy)
        out = np.zeros_like(fx)
        for j in range(4):
            yy = np.clip(y0 + j - 1, 0, self.H - 1)
            row = np.zeros_like(fx)
            for i in range(4):
                xx = np.clip(x0 + i - 1, 0, self.W - 1)
                row += wx[i] * self.h[yy, xx]
            out += wy[j] * row
        return out


_DEMS = {}


def dem(name):
    if name not in _DEMS:
        _DEMS[name] = Dem(name)
    return _DEMS[name]


# ----------------------------------------------------------------------------- 雜訊
def _hash(ix, iy, seed):
    n = (ix.astype(np.int64) * 374761393 + iy.astype(np.int64) * 668265263 + seed * 2147483647) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    n = n ^ (n >> 16)
    return (n & 0xFFFF).astype(np.float32) / 65535.0


def vnoise(x, y, wavelength, seed=1):
    u = x / wavelength
    v = y / wavelength
    iu = np.floor(u)
    iv = np.floor(v)
    fu = (u - iu).astype(np.float32)
    fv = (v - iv).astype(np.float32)
    su = fu * fu * (3 - 2 * fu)
    sv = fv * fv * (3 - 2 * fv)
    a = _hash(iu, iv, seed)
    b = _hash(iu + 1, iv, seed)
    c = _hash(iu, iv + 1, seed)
    d = _hash(iu + 1, iv + 1, seed)
    return (a + (b - a) * su + (c - a) * sv + (a - b - c + d) * su * sv) * 2 - 1


def fbm(x, y, wl_max, wl_min, seed=1, gain=0.5):
    tot = np.zeros_like(x, dtype=np.float32)
    amp = 1.0
    norm = 0.0
    wl = wl_max
    k = 0
    while wl >= wl_min:
        tot += amp * vnoise(x, y, wl, seed + k * 17)
        norm += amp
        amp *= gain
        wl *= 0.5
        k += 1
    return tot / max(norm, 1e-6)



def terrain_noise(X, Y, z, wl_min, ly):
    A = ly.get("noise", 0.0)
    if A <= 0:
        return 0.0
    wl_cap = ly.get("noise_wl", 2500.0)
    seed = ly.get("seed", 3)
    tot = np.zeros_like(X, dtype=np.float32)
    wl = wl_cap
    k = 0
    while wl >= wl_min:
        tot += (A * (wl / 1000.0) ** 0.9) * vnoise(X, Y, wl, seed + k * 17)
        wl *= 0.5
        k += 1
    mod = 0.6 + 0.4 * vnoise(X, Y, 2600.0, seed + 101)
    out = tot * mod * (z > 4.0)
    # 山溝：脊狀雜訊（|n| 小處下切），只加在坡面，波長 <= 400 m
    gA = ly.get("gully", 0.0)
    if gA > 0:
        gy, gx = np.gradient(z.astype(np.float32), max(float(X[0, 1] - X[0, 0]), 1.0))
        slope = np.clip(np.sqrt(gx * gx + gy * gy) * 2.5, 0, 1)
        wl = 400.0
        k = 0
        while wl >= max(wl_min, 20.0):
            n = vnoise(X, Y, wl, seed + 300 + k * 13)
            out = out - gA * (wl / 100.0) ** 0.8 * (1.0 - np.abs(n)) ** 2.0 * slope
            wl *= 0.5
            k += 1
    return out

# ----------------------------------------------------------------------------- 地表濕潤度（綠度）
def smooth(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def veg_field(lon, lat, elev):
    """0 = 乾燥岩漠，1 = 綠。粗略的氣候規則：地中海沿岸與山地較濕，往南往東變乾，河谷成綠帶。"""
    # 降雨：北高南低
    rain = smooth(30.6, 33.2, lat) * 0.75 + 0.25 * smooth(35.0, 37.5, lat)
    # 迦南山地隆起帶的迎風面較濕；約旦裂谷與東邊急遽變乾
    ridge_lon = 35.2 + 0.05 * (lat - 31.5)
    east = smooth(ridge_lon + 0.05, ridge_lon + 0.85, lon)
    rain = rain * (1 - 0.85 * east)
    # 北敘利亞與美索不達米亞北部有春雨
    rain = np.maximum(rain, 0.55 * smooth(35.4, 37.0, lat) * (1 - 0.6 * smooth(41, 46, lon)))
    rain *= 0.75 + 0.25 * smooth(-50, 700, elev)
    rain *= 1 - 0.7 * smooth(1300, 2200, elev)
    # 尼羅河谷與三角洲
    nile = np.exp(-(((lon - 31.15) / 0.22) ** 2)) * smooth(-1, 0.8, 31.2 - lat) * 0.0
    delta = smooth(30.4, 31.5, lat) * smooth(29.8, 30.5, lon) * smooth(33.0, 31.5, lon) * smooth(-1000, 20, 20 - elev)
    return np.clip(rain + delta * 0.9, 0, 1)


# ----------------------------------------------------------------------------- 圖層
def make_layer(scene, ly, origin, vexag):
    """ly: name, dem, cx, cy（本地公尺）, hx, hy（半寬）, step, noise（公尺）, noise_wl_max, hole（本地矩形清單）"""
    lon0, lat0 = origin
    step = ly["step"]
    nx = int(2 * ly["hx"] / step) + 1
    ny = int(2 * ly["hy"] / step) + 1
    xs = ly["cx"] - ly["hx"] + np.arange(nx, dtype=np.float64) * step
    ys = ly["cy"] - ly["hy"] + np.arange(ny, dtype=np.float64) * step
    X, Y = np.meshgrid(xs, ys)  # (ny, nx)
    lat = lat0 + np.degrees(Y / R_EARTH)
    lon = lon0 + np.degrees(X / (R_EARTH * np.cos(np.radians(lat))))
    d = dem(ly["dem"])
    z = d.sample(lon, lat)
    sea_lim = ly.get('sea_lon_max', 999.0)
    sea = (np.clip(-z, 0, None) * (lon < sea_lim)).astype(np.float32)
    # 雜訊：全域解析函式，八度音階依波長固定振幅；圖層只加入波長 >= 4 倍格距的部分，
    # 所以粗細圖層在共有的波長上完全一致，不會在交界處裂開。
    z = z + terrain_noise(X, Y, z, step * 4.0, ly)
    rip = None
    if ly.get('carve'):
        z, rip, _ = RG.carve(X, Y, z)
    pz = ly.get("parent")
    if pz:
        # 外緣一圈漸變到上一層的高度，兩層在交界處接起來
        p = dem(pz["dem"])
        zp = p.sample(lon, lat)
        zp = zp + terrain_noise(X, Y, zp, pz["step"] * 4.0, ly)
        if ly.get('carve'):
            zp, _, _ = RG.carve(X, Y, zp)
        band = pz["band"]
        dx = np.minimum(X - (ly["cx"] - ly["hx"]), (ly["cx"] + ly["hx"]) - X)
        dy = np.minimum(Y - (ly["cy"] - ly["hy"]), (ly["cy"] + ly["hy"]) - Y)
        w = 1.0 - smooth(0.0, band, np.minimum(dx, dy))
        z = z * (1 - w) + zp * w
    land = ~((z <= 0.0) & (lon < sea_lim))
    z = np.where(land, z, 0.0)
    veg = veg_field(lon, lat, z).astype(np.float32)
    veg = np.where(land, veg, 0.0)
    if rip is not None:
        veg = np.maximum(veg, rip * 1.1).astype(np.float32)
    verts = np.stack([X, Y, z * vexag], axis=-1).astype(np.float32).reshape(-1, 3)
    # 四邊形
    idx = np.arange(nx * ny, dtype=np.uint32).reshape(ny, nx)
    q = np.stack([idx[:-1, :-1], idx[:-1, 1:], idx[1:, 1:], idx[1:, :-1]], axis=-1).reshape(-1, 4)
    # 洞：四邊形中心落在較細圖層矩形內就拿掉
    cxq = (X[:-1, :-1] + X[1:, 1:]) * 0.5
    cyq = (Y[:-1, :-1] + Y[1:, 1:]) * 0.5
    keep = np.ones(cxq.shape, dtype=bool)
    for (x0, y0, x1, y1) in ly.get("hole", []):
        keep &= ~((cxq > x0) & (cxq < x1) & (cyq > y0) & (cyq < y1))
    q = q[keep.reshape(-1)]
    out = os.path.join(CACHE, scene)
    os.makedirs(out, exist_ok=True)
    base = os.path.join(out, ly["name"])
    verts.tofile(base + ".v.bin")
    q.astype(np.uint32).tofile(base + ".q.bin")
    veg.reshape(-1).tofile(base + ".veg.bin")
    sea.reshape(-1).tofile(base + ".sea.bin")
    info = dict(name=ly["name"], nv=int(verts.shape[0]), nq=int(q.shape[0]), nx=nx, ny=ny,
                zmin=float(z.min() * vexag), zmax=float(z.max() * vexag))
    print(f"  {scene}/{ly['name']}: {nx}x{ny} verts={info['nv']:,} quads={info['nq']:,} z={info['zmin']:.0f}..{info['zmax']:.0f}")
    return info


def lonlat_to_xy(lon, lat, origin):
    lon0, lat0 = origin
    y = math.radians(lat - lat0) * R_EARTH
    x = math.radians(lon - lon0) * R_EARTH * math.cos(math.radians(lat))
    return x, y


def build(scene, spec):
    origin = spec["origin"]
    vexag = spec.get("vexag", 1.0)
    layers = []
    for ly in spec["layers"]:
        layers.append(make_layer(scene, ly, origin, vexag))
    meta = dict(scene=scene, origin=origin, vexag=vexag, layers=layers)
    with open(os.path.join(CACHE, scene, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1)


def rect(cx, cy, hx, hy):
    return (cx - hx, cy - hy, cx + hx, cy + hy)


def specs():
    S = {}
    # ---------- 封面：示劍山谷。原點放在底拉他（約書亞時代示劍的位置）
    o = (35.2833, 32.2133)
    fine = rect(-250, 0, 1700, 1500)       # 近景：谷口到山腳
    mid = rect(0, 0, 7600, 6100)           # 整張 shechem DEM（略內縮）
    S["cover"] = dict(origin=o, vexag=1.8, layers=[
        dict(name="far", dem="canaan", cx=0, cy=0, hx=150000, hy=110000, step=520, noise=14, seed=5, hole=[mid]),
        dict(name="mid", dem="shechem_valley", cx=0, cy=0, hx=7600, hy=6100, step=34, noise=20, gully=2.0, seed=5, hole=[fine],
             parent=dict(dem="canaan", step=520, band=900)),
        dict(name="near", dem="shechem_valley", cx=-250, cy=0, hx=1700, hy=1500, step=6, noise=20, gully=2.0, seed=5,
             parent=dict(dem="shechem_valley", step=34, band=250)),
    ])
    # ---------- 紅海：蘇伊士灣西岸的西奈海岸；原點在海岸線上（東經 32.63、北緯 29.80）
    o2 = (32.63, 29.80)
    cust = (-1288.0, -788.0, 248.0, 788.0)      # Blender 端自建的海與灘（遠景地形在此挖洞）
    S["redsea"] = dict(origin=o2, vexag=1.6, layers=[
        dict(name="far", dem="wide", cx=-200000, cy=0, hx=300000, hy=160000, step=1000, noise=10, seed=21, hole=[(-26000, -9000, 2000, 9000)]),
        dict(name="mid", dem="wide", cx=-12000, cy=0, hx=14000, hy=9000, step=70, noise=18, gully=2.5, seed=21,
             hole=[cust], parent=dict(dem="wide", step=1000, band=1500)),
    ])
    # ---------- 幼發拉底河（他拉的帳棚、亞伯拉罕渡河）：原點在東經 38.05、北緯 36.78
    o3 = (38.05, 36.78)
    camp = rect(520, 0, 636, 636)          # 帳棚營地一帶（洞比細圖層小 14 m，接縫重疊避免露縫）
    ford = rect(-60, -1500, 786, 686)      # 渡口
    S["river"] = dict(origin=o3, vexag=2.6, layers=[
        dict(name="far", dem="wide", cx=0, cy=0, hx=260000, hy=170000, step=1100, noise=8, seed=61, hole=[rect(0, 0, 15000, 15000)]),
        dict(name="mid", dem="wide", cx=0, cy=0, hx=15000, hy=15000, step=50, noise=22, gully=2.0, seed=61, carve=True,
             hole=[camp, ford], parent=dict(dem="wide", step=1100, band=1500)),
        dict(name="camp", dem="wide", cx=520, cy=0, hx=650, hy=650, step=2.2, noise=22, gully=1.0, seed=61, carve=True,
             parent=dict(dem="wide", step=50, band=160)),
        dict(name="ford", dem="wide", cx=-60, cy=-1500, hx=800, hy=700, step=3.0, noise=22, gully=1.0, seed=61, carve=True,
             parent=dict(dem="wide", step=50, band=160)),
    ])
    # ---------- 迦南全地（第13節）：原點在東經 35.3、北緯 32.0；近景用 16 m 的示劍高程
    o4 = (35.3, 32.0)
    near4 = rect(-1900, 23800, 7500, 6000)
    S["canaan"] = dict(origin=o4, vexag=2.0, layers=[
        dict(name="far", dem="wide", cx=0, cy=0, hx=500000, hy=300000, step=1500, noise=6, seed=71, sea_lon_max=35.05,
             hole=[rect(0, 0, 121000, 108000)]),
        dict(name="mid", dem="canaan", cx=0, cy=0, hx=122000, hy=109000, step=260, noise=26, gully=3.0, seed=71, sea_lon_max=35.05,
             hole=[near4], parent=dict(dem="wide", step=1500, band=4000)),
        dict(name="near", dem="shechem_valley", cx=-1900, cy=23800, hx=7440, hy=5940, step=15, noise=26, gully=2.5, seed=71,
             parent=dict(dem="canaan", step=260, band=500)),
    ])
    return S


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    S = specs()
    for k, v in S.items():
        if which in ("all", k):
            print("scene", k)
            build(k, v)
