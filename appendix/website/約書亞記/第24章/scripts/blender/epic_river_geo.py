"""幼發拉底河的示意河道（本地公尺，原點在東經 38.05、北緯 36.78；河由北往南偏東流）。
epic_prep.py（系統 Python）與 epic_river.py（Blender）共用，所以只用 numpy。
高程數據（wide，1 km）看得到河谷但看不到河；這裡用解析函式把河道刻進地形，Blender 端用同一個函式放水面。"""
import numpy as np

HALF_W = 130.0       # 水面半寬（河寬約 260 m）
DEPTH = 5.0
LEVEL0 = 338.0       # 河面高程（公尺，未誇大）
SLOPE = 0.0007       # 往南每公尺降多少（y 越小越低）


def centerline_x(y):
    y = np.asarray(y, dtype=np.float64)
    return 430.0 * np.sin(y / 1500.0 + 0.4) + 210.0 * np.sin(y / 560.0 + 1.0) - 150.0


def river_level(y):
    return LEVEL0 + SLOPE * np.asarray(y, dtype=np.float64)


PATH_Y = np.arange(14000.0, -14000.01, -60.0)
PATH_X = centerline_x(PATH_Y)


def dist_to_path(X, Y):
    """到河道中線的距離（近似：沿 y 找最近的折線點，再用線段精修）。回傳 (s, y_near)。"""
    shape = X.shape
    x = X.ravel()
    y = Y.ravel()
    # 粗略：假設河道大致南北向，先在 y 附近 ±900 m 的折線點中找最近
    best = np.full(x.shape, 1e18)
    ybest = y.copy()
    for off in np.arange(-900.0, 901.0, 60.0):
        yy = y + off
        xx = centerline_x(yy)
        dd = (x - xx) ** 2 + (y - yy) ** 2
        m = dd < best
        best = np.where(m, dd, best)
        ybest = np.where(m, yy, ybest)
    return np.sqrt(best).reshape(shape), ybest.reshape(shape)


def carve(X, Y, z):
    """回傳 (z 新高程, 河岸綠度 0..1, 河道內遮罩)。"""
    s, yn = dist_to_path(X, Y)
    lvl = river_level(yn)
    Wr = HALF_W
    bank_t = np.clip((s - Wr * 0.85) / (Wr + 35 - Wr * 0.85), 0, 1)
    bank_t = bank_t * bank_t * (3 - 2 * bank_t)
    flood_surface = lvl + 3.0 + 0.012 * np.maximum(s - Wr, 0)
    depth = DEPTH * (1.0 - 0.9 * np.exp(-((yn + 1500.0) / 170.0) ** 2))   # 渡口（y=-1500）有一段淺灘
    chan = lvl - depth * (1 - (np.minimum(s, Wr) / Wr) ** 2)
    zone = chan * (1 - bank_t) + flood_surface * bank_t
    m = np.clip((s - 300.0) / 800.0, 0, 1)
    m = m * m * (3 - 2 * m)
    znew = zone * (1 - m) + z * m
    rip = np.exp(-(np.maximum(s - Wr, 0) / 380.0) ** 2)
    return znew.astype(np.float32), rip.astype(np.float32), (s < Wr)
