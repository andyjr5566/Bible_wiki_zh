"""迦南全地（第13節）：城邑、葡萄園、橄欖園一處一處亮起來。風格 A（黃昏，天空青紫，地上的光一處處亮）。
用法：blender -b --python epic_canaan.py -- --style A --w 1280 --h 720 --samples 32 --out <不含副檔名>；環境變數 FRAME：
  canaan_high / canaan_descend / canaan_scene
座標：本地公尺，原點東經 35.3、北緯 32.0，垂直誇大 3 倍。亮點只是光（不畫營火、燭光）；城邑位置為示意。
"""
import argparse, math, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import epic_lib as L
import epic_props as P
import style_a as S
import bpy, bmesh
import numpy as np
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--style", default="A")
ap.add_argument("--w", type=int, default=1280)
ap.add_argument("--h", type=int, default=720)
ap.add_argument("--samples", type=int, default=32)
ap.add_argument("--out", default=os.path.join(L.ROOT, "lab", "renders", "epic", "canaan_test"))
a = ap.parse_args(argv)
env = os.environ
FRAME = env.get("FRAME", "canaan_high")
rnd = random.Random(33)
R_EARTH = 6371008.8
LON0, LAT0 = 35.3, 32.0


def xy(lon, lat):
    return (math.radians(lon - LON0) * R_EARTH * math.cos(math.radians(lat)), math.radians(lat - LAT0) * R_EARTH)


sc = L.fresh_scene("canaan")
meta, layers = L.load_terrain("canaan")
VEX = meta["vexag"]
tmat = P.terrain_material("terrain_canaan", "levant_warm", sea=True, veg_k=0.75, field_scale=0.01)
for o in layers:
    o.data.materials.append(tmat)
ground = L.Ground(layers)
gz = ground.z

SHECHEM = xy(35.284, 32.213)
CENTER_NEAR = (-1900.0, 23800.0)
EXAG = {"canaan_high": 24.0, "canaan_descend": 4.0, "canaan_scene": 1.0}[FRAME]

FR = {
    "canaan_high": dict(cam=(-86000.0, -64000.0, 47000.0), tgt=(40000.0, 12000.0, 300.0), lens=27, abs_cam=True, sun_az=250.0),
    "canaan_descend": dict(cam=(-26500.0, 5200.0, 7800.0), tgt=(-1900.0, 23800.0, 1000.0), lens=30, abs_cam=True, sun_az=250.0),
    "canaan_scene": dict(cam=(-5600.0, 20600.0, 70.0), tgt=(-1700.0, 24000.0, 40.0), lens=26, abs_cam=False, sun_az=250.0),
}
fr = FR[FRAME]
sky, sunobj, sund = S.world("canaan", fr["sun_az"])
if FRAME == "canaan_scene":
    best = None
    for i in range(24):
        for j in range(24):
            x = fr["cam"][0] - 1800 + i * 150.0
            y = fr["cam"][1] - 1800 + j * 150.0
            z = gz(x, y)
            if z is not None and (best is None or z > best[2]):
                best = (x, y, z)
    fr["cam"] = (best[0], best[1], 45.0)
    print("scene cam ridge", best)


# ----------------------------------------------------------------------------- 發光材質（強度 = 亮起的程度，放在物件顏色的 Alpha）
glow_mats = {}


def glow_mat(name, color, k):
    m = L.new_mat(name)
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    oi = nt.nodes.new("ShaderNodeObjectInfo")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1)
    nt.links.new(L.math_node(nt, "MULTIPLY", oi.outputs["Alpha"], k), em.inputs["Strength"])
    bs = nt.nodes.new("ShaderNodeBsdfDiffuse")
    bs.inputs["Color"].default_value = (0.05, 0.045, 0.05, 1)
    mix = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(bs.outputs["BSDF"], mix.inputs[0])
    nt.links.new(em.outputs["Emission"], mix.inputs[1])
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
    return m


M_HOUSE = glow_mat("glow_house", P.lin("#ffb25e"), 9.0)
M_VINE = glow_mat("glow_vine", P.lin("#c58bff"), 6.0)
M_OLIVE = glow_mat("glow_olive", P.lin("#cdeea0"), 5.0)
M_WALL = glow_mat("glow_wall", P.lin("#ffc27a"), 4.0)


def unit_mesh(name, mat, kind="box"):
    bm = bmesh.new()
    if kind == "box":
        L.box_bm((1, 1, 1), (0, 0, 0.5), bm)
    else:
        L.sphere_bm(1.0, (0, 0, 0.5), (1, 1, 0.7), 1, bm)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    me.materials.append(mat)
    return me


box_h = unit_mesh("box_house", M_HOUSE)
box_v = unit_mesh("box_vine", M_VINE)
sph_o = unit_mesh("sph_olive", M_OLIVE, "sph")
box_w = unit_mesh("box_wall", M_WALL)
sph_v = unit_mesh("sph_vine", M_VINE, "sph")
sph_h = unit_mesh("sph_halo", M_HOUSE, "sph")
cnt = [0]


def uid(p):
    cnt[0] += 1
    return f"{p}_{cnt[0]}"


def lit_of(x, y):
    """亮起的程度：以示劍為起點的一波光，越遠越晚亮（越暗），但整片大致都亮了。"""
    d = math.hypot(x - SHECHEM[0], y - SHECHEM[1])
    return float(min(1.0, max(0.04, 1.25 - d / 130000.0)))


def emit(mesh, x, y, z, sx, sy, sz, yaw, lit):
    o = L.instance(mesh, uid("g"), (x, y, z), rot_z=yaw, scale=(sx, sy, sz), color=(1, 1, 1, lit))
    o.visible_shadow = False
    return o


# ----------------------------------------------------------------------------- 城邑（位置為示意）
TOWNS = [
    ("示劍", 35.284, 32.213, 1.5), ("撒瑪利亞", 35.19, 32.277, 1.1), ("得撒", 35.33, 32.29, 0.9), ("多坍", 35.24, 32.41, 0.9),
    ("米吉多", 35.18, 32.585, 1.1), ("他納", 35.22, 32.52, 0.8), ("伯善", 35.50, 32.50, 1.0), ("耶斯列", 35.33, 32.56, 0.8),
    ("亞柯", 35.07, 32.92, 1.1), ("多珥", 34.92, 32.60, 0.8), ("約帕", 34.75, 32.05, 1.0), ("基色", 34.92, 31.86, 0.9),
    ("伯特利", 35.22, 31.93, 0.9), ("艾", 35.26, 31.92, 0.6), ("基遍", 35.18, 31.85, 0.9), ("耶路撒冷", 35.23, 31.78, 1.3),
    ("伯利恆", 35.20, 31.70, 0.7), ("希伯崙", 35.10, 31.53, 1.0), ("拉吉", 34.85, 31.56, 0.9), ("迦薩", 34.46, 31.52, 1.1),
    ("亞實基倫", 34.55, 31.66, 1.0), ("亞實突", 34.65, 31.80, 0.9), ("耶利哥", 35.44, 31.87, 0.9), ("別是巴", 34.79, 31.25, 0.9),
    ("底璧", 35.0, 31.43, 0.7), ("塔布亞", 35.15, 32.14, 0.6), ("提耳撒", 35.35, 32.34, 0.6), ("示羅", 35.29, 32.06, 0.7),
]
town_pts = []
for name, lon, lat, size in TOWNS:
    x, y = xy(lon, lat)
    z = gz(x, y)
    if z is None:
        continue
    town_pts.append((x, y, z, size))
    lit = lit_of(x, y)
    nh = int((18 + 26 * size) * (2.2 if EXAG > 8 else 1.0))
    R = (150.0 + 160.0 * size) * (EXAG ** 0.8) * (1.35 if EXAG > 8 else 1.0)
    for _ in range(nh):
        r = R * math.sqrt(rnd.random()); t = rnd.uniform(0, 6.28)
        hx, hy = x + r * math.cos(t), y + r * math.sin(t)
        hz = gz(hx, hy)
        if hz is None:
            continue
        s = rnd.uniform(5, 9) * EXAG ** (0.9 if EXAG > 8 or EXAG < 2 else 1.3)
        emit(box_h, hx, hy, hz, s, s * rnd.uniform(0.8, 1.2), s * rnd.uniform(0.5, 0.9), rnd.uniform(0, 3.14), lit * rnd.uniform(0.7, 1.0))
    if EXAG > 8:                        # 高空：城邑外圍一圈柔和的光暈
        pass
    if 2.5 < EXAG <= 8:                 # 降落：城邑中心一塊暖光
        emit(sph_h, x, y, z + 25, R * 0.8, R * 0.8, R * 0.06, 0, lit * 0.45)
    # 城牆圈（一圈短牆段）
    for k in range(36):
        t = 2 * math.pi * k / 36
        wx, wy = x + R * 1.12 * math.cos(t), y + R * 1.12 * math.sin(t)
        wz = gz(wx, wy)
        if wz is None:
            continue
        emit(box_w, wx, wy, wz, R * 0.2, 2.2 * EXAG ** 0.8, 3.0 * EXAG ** 0.8, t + math.pi / 2, lit * 0.8)

# ----------------------------------------------------------------------------- 葡萄園（紫金色成排）與橄欖園（銀綠色成點）
def candidates(n, region, near_only=False):
    out = []
    tries = 0
    while len(out) < n and tries < n * 40:
        tries += 1
        if region == "near":
            if FRAME == "canaan_scene":      # 取鏡頭視野內的地面
                az = math.atan2(fr["tgt"][1] - fr["cam"][1], fr["tgt"][0] - fr["cam"][0]) + rnd.uniform(-0.55, 0.55)
                dd = rnd.uniform(500.0, 5200.0)
                x = fr["cam"][0] + dd * math.cos(az)
                y = fr["cam"][1] + dd * math.sin(az)
            else:
                x = CENTER_NEAR[0] + rnd.uniform(-8000, 8000)
                y = CENTER_NEAR[1] + rnd.uniform(-6200, 6200)
        else:
            lon = rnd.uniform(34.55, 35.55); lat = rnd.uniform(31.3, 32.95)
            x, y = xy(lon, lat)
        hit = ground.zn(x, y)
        if hit is None:
            continue
        loc, nrm = hit[0], hit[1]
        if nrm.z < 0.72 or loc.z < 90 * VEX * 0.4:
            continue
        out.append((loc.x, loc.y, loc.z, nrm))
    return out


n_v_far = {"canaan_high": 150, "canaan_descend": 60, "canaan_scene": 0}[FRAME]
n_o_far = {"canaan_high": 210, "canaan_descend": 80, "canaan_scene": 0}[FRAME]
n_v_near = {"canaan_high": 40, "canaan_descend": 260, "canaan_scene": 70}[FRAME]
n_o_near = {"canaan_high": 60, "canaan_descend": 420, "canaan_scene": 110}[FRAME]


def vineyard(x, y, z, nrm, scale, lit):
    if scale > 2.5:                     # 高空／降落：整片葡萄園只看得到一塊發光的色斑
        R = rnd.uniform(1100, 2000) * scale / 17.5 * (2.4 if EXAG < 8 else 1.0)
        emit(sph_v, x, y, z + 40, R, R * rnd.uniform(0.6, 1.0), R * 0.08, rnd.uniform(0, 3.14), lit * rnd.uniform(0.7, 1.0))
        return
    # 行沿等高線（垂直於坡向）
    ang = math.atan2(nrm.y, nrm.x) + math.pi / 2
    rows = 9
    for r_ in range(rows):
        off = (r_ - rows / 2) * 7.5 * scale
        cx, cy = x - math.sin(ang) * off, y + math.cos(ang) * off
        cz = gz(cx, cy)
        if cz is None:
            continue
        emit(box_v, cx, cy, cz, rnd.uniform(60, 110) * scale, 0.9 * max(scale ** 0.6, 1.0), 1.1 * max(scale ** 0.6, 1.0), ang, lit * rnd.uniform(0.75, 1.0))


def olive_grove(x, y, z, scale, lit):
    if scale > 2.5:
        R = rnd.uniform(900, 1700) * scale / 17.5 * (2.4 if EXAG < 8 else 1.0)
        emit(sph_o, x, y, z + 40, R, R * rnd.uniform(0.6, 1.0), R * 0.08, rnd.uniform(0, 3.14), lit * rnd.uniform(0.6, 0.95))
        return
    for i in range(-3, 4):
        for j in range(-3, 4):
            if rnd.random() < 0.18:
                continue
            ox, oy = x + (i * 12 + rnd.uniform(-2, 2)) * scale, y + (j * 12 + rnd.uniform(-2, 2)) * scale
            oz = gz(ox, oy)
            if oz is None:
                continue
            r = 2.4 * max(scale ** 0.8, 1.0)
            emit(sph_o, ox, oy, oz, r, r, r, 0, lit * rnd.uniform(0.7, 1.0))


cv = candidates(n_v_far, "far"); co = candidates(n_o_far, "far"); print("CANDS", len(cv), len(co))
for (x, y, z, nrm) in cv:
    vineyard(x, y, z, nrm, EXAG ** 0.9, lit_of(x, y))
for (x, y, z, nrm) in co:
    olive_grove(x, y, z, EXAG ** 0.9, lit_of(x, y))
for (x, y, z, nrm) in candidates(n_v_near, "near"):
    vineyard(x, y, z, nrm, max(EXAG ** 0.6, 1.0) * 0.9, lit_of(x, y))
for (x, y, z, nrm) in candidates(n_o_near, "near"):
    olive_grove(x, y, z, max(EXAG ** 0.6, 1.0) * 0.9, lit_of(x, y))

# ----------------------------------------------------------------------------- 相機
cp = list(fr["cam"])
tg = list(fr["tgt"])
if not fr["abs_cam"]:
    cp[2] = (gz(cp[0], cp[1]) or 0.0) + cp[2]
    tg[2] = (gz(tg[0], tg[1]) or 0.0) + tg[2]
cam = L.set_camera(tuple(cp), tuple(tg), lens=fr["lens"], clip=(1.0, 900000.0))
L.render_settings(a.w, a.h, a.samples)
base = a.out[:-4] if a.out.endswith(".png") else a.out
t = L.render_pair(base, sun_dir=sund)
print("names", len(L.check_names()), "times", t, "objects", cnt[0])
