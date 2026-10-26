"""2.5D 繪本視差用的背景圖層（只有天空、陸地、水；沒有人與動物）。
用法：blender -b --python epic_plates.py -- --scene redsea|ford --w 1920 --h 1080 --samples 48 --out <資料夾>
輸出：<資料夾>/<sky|far|sea|near>.f32 與 _depth.f32（線性 RGBA；後製由 epic_plates_post.py 做）。
鏡頭在西岸、離水面很低、往東看，太陽剛離地平線（正前方偏左）。層次由後到前：sky → far → sea → near。
全部用程序生成的幾何（不用 DEM），所以沒有圖層邊緣；遠岸山脊連續涵蓋整個視野，其後的平面被山脊擋住。
"""
import argparse, json, math, os, random, sys
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
ap.add_argument("--scene", default="redsea")
ap.add_argument("--w", type=int, default=1920)
ap.add_argument("--h", type=int, default=1080)
ap.add_argument("--samples", type=int, default=48)
ap.add_argument("--out", default=os.path.join(L.ROOT, "lab", "renders", "layers", "_work", "redsea"))
ap.add_argument("--only", default="")
a = ap.parse_args(argv)
SCENE = a.scene
WEST = SCENE == "redsea-west"
GEO = "redsea" if SCENE.startswith("redsea") else "ford"
rnd = random.Random(5)
os.makedirs(a.out, exist_ok=True)

sc = L.fresh_scene("plates_" + SCENE)
CAM_Z = 2.2 if GEO == "redsea" else 1.45
RIDGE_K = 0.8 if WEST else 1.0
SUN_AZ = 16.0          # 太陽方位：正東偏北 6 度（鏡頭看東，偏北＝畫面偏左）
if WEST:
    sky, sunobj, sund = S.world("plate_west", 188.0)
else:
    sky, sunobj, sund = S.world("plate_dawn", SUN_AZ, **({"sun_el": 2.2} if GEO == "ford" else {}))
if GEO == "ford":       # 渡口的光比較暖、霧較重
    pass

objs = {"sky": [], "far": [], "sea": [], "near": []}


def add(plate, ob):
    objs[plate].append(ob)
    return ob


def lin(h):
    return tuple(L.srgb(h))


def log_axis(lo, hi, n, power=3.0):
    t = np.linspace(0.0, 1.0, n)
    return lo + (hi - lo) * t ** power


def sym_axis(span, n, power=3.0, dense=()):
    t = np.linspace(-1.0, 1.0, n)
    ys = np.sign(t) * span * np.abs(t) ** power
    for seg in dense:                   # (lo, hi, step) 在這些範圍內加密
        ys = np.concatenate([ys, np.arange(seg[0], seg[1] + 1e-6, seg[2])])
    return np.unique(np.round(ys, 4))


# ----------------------------------------------------------------------------- 材質
def mat_sand(name, hexc, rough=0.95):
    m = L.pbr(name, hexc, rough)
    nt = m.node_tree
    b = L.bsdf_of(m)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    n1 = L.noise_tex(nt, tc.outputs["Object"], 1.3, 5.0, 0.55)
    n2 = L.noise_tex(nt, tc.outputs["Object"], 14.0, 4.0, 0.6)
    col = L.mix_rgb(nt, lin(hexc), (0.0, 0.0, 0.0), L.math_node(nt, "MULTIPLY", L.math_node(nt, "SUBTRACT", n1, 0.3, clamp=True), 0.5))
    nt.links.new(col, b.inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.6
    bump.inputs["Distance"].default_value = 0.2
    nt.links.new(L.math_node(nt, "ADD", n1, L.math_node(nt, "MULTIPLY", n2, 0.5)), bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


def mat_water(river):
    """水面：深色、很光滑，倒映天空與日盤；'path' 屬性處是淺灘／乾海床（濕沙，帶倒影）；'edge' 屬性是水線泡沫。"""
    m = L.new_mat("plate_water")
    nt = m.node_tree
    b = L.bsdf_of(m)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (0.6, 0.12, 1.0) if not river else (0.8, 0.14, 1.0)    # 沿視線（x）拉長，反光成一條光帶
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    n1 = L.noise_tex(nt, mp.outputs["Vector"], 1.0, 5.0, 0.55)
    n2 = L.noise_tex(nt, tc.outputs["Object"], 0.8, 3.0, 0.5)
    pa = nt.nodes.new("ShaderNodeAttribute"); pa.attribute_name = "path"; pa.attribute_type = "GEOMETRY"
    ea = nt.nodes.new("ShaderNodeAttribute"); ea.attribute_name = "edge"; ea.attribute_type = "GEOMETRY"
    water = L.ramp(nt, n1, [(0.2, lin("#0a1f2c" if not river else "#12303a")), (0.6, lin("#17394a" if not river else "#23505a")), (0.9, lin("#2d5a66"))]) if not WEST else L.ramp(nt, n1, [(0.2, lin("#101a3a")), (0.6, lin("#26325e")), (0.9, lin("#4a4a7a"))])
    sand = L.mix_rgb(nt, lin("#3b2b1f"), lin("#6a4f36"), n2) if not WEST else L.mix_rgb(nt, lin("#9a6a58"), lin("#d19a80"), n2)
    col = L.mix_rgb(nt, water, sand, pa.outputs["Fac"])
    col = L.mix_rgb(nt, col, lin("#f3e9dc"), L.math_node(nt, "MULTIPLY", ea.outputs["Fac"], 0.8, clamp=True))
    nt.links.new(col, b.inputs["Base Color"])
    rough = L.math_node(nt, "ADD", 0.09, L.math_node(nt, "ADD", L.math_node(nt, "MULTIPLY", pa.outputs["Fac"], 0.3), L.math_node(nt, "MULTIPLY", ea.outputs["Fac"], 0.7)))
    nt.links.new(rough, b.inputs["Roughness"])
    for k, v in (("IOR", 1.33), ("Specular IOR Level", 0.7)):
        if k in b.inputs:
            b.inputs[k].default_value = v
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.5 if not river else 0.35
    bump.inputs["Distance"].default_value = 0.4
    nt.links.new(L.math_node(nt, "ADD", L.math_node(nt, "MULTIPLY", n1, 0.8), L.math_node(nt, "MULTIPLY", n2, 0.3)), bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


def mat_far(hexa, hexb):
    m = L.new_mat("plate_far")
    nt = m.node_tree
    b = L.bsdf_of(m)
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], sep.inputs["Vector"])
    n1 = L.noise_tex(nt, geo.outputs["Position"], 0.0012, 5.0, 0.6)
    n2 = L.noise_tex(nt, geo.outputs["Position"], 0.02, 4.0, 0.6)
    steep = L.math_node(nt, "SUBTRACT", 1.0, nt.nodes.new("ShaderNodeSeparateXYZ").outputs["Z"]) if False else None
    col = L.mix_rgb(nt, lin(hexa), lin(hexb), L.math_node(nt, "ADD", L.math_node(nt, "MULTIPLY", n1, 0.7), L.math_node(nt, "MULTIPLY", n2, 0.3)))
    nt.links.new(col, b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.95
    return m


# ----------------------------------------------------------------------------- 場景
if GEO == "redsea":
    NEAR_CREST = 10.5          # 近岸沙丘脊離鏡頭的距離
    SEA_X0, SEA_X1 = 6.0, 13600.0
    RIDGE_X0 = 13000.0
    CH_HALF = 14.0
else:
    NEAR_CREST = 6.0
    SEA_X0, SEA_X1 = 3.0, 285.0
    RIDGE_X0 = 0.0
    CH_HALF = 11.0

# --- 水面（含通道／淺灘）
xs = np.unique(np.concatenate([log_axis(SEA_X0, SEA_X1, 360, 3.2 if GEO == "redsea" else 1.6), np.arange(SEA_X0, min(SEA_X0 + 40, SEA_X1), 0.25)]))
span_y = 60000.0 if GEO == "redsea" else 3000.0
ys = sym_axis(span_y, 360, 3.0, dense=[(-CH_HALF - 4, CH_HALF + 4, 0.2 if GEO == "redsea" else 0.1)])
X, Y = np.meshgrid(xs, ys)
# 岸線不要太直：水線 x 隨 y 擾動
shore = SEA_X0 + (2.5 * L.fbm2(Y * 1.0, Y * 0.0, 40.0, 4.0, seed=5) if True else 0)
path = ((np.abs(Y) <= CH_HALF + (0.0 if GEO == "redsea" else 0.0)) & (X > SEA_X0 + 1.0)).astype(np.float32)
if GEO == "ford":       # 淺灘：緩緩彎的一條帶
    cy = 6.0 * np.sin(X / 60.0 + 0.5)
    path = ((np.abs(Y - cy) <= CH_HALF) & (X > SEA_X0 + 1.0)).astype(np.float32)
Z = np.where(path > 0.5, 0.11 if GEO == "redsea" else -0.05, 0.0)
Z = Z + 0.025 * L.fbm2(X, Y, 30.0, 1.5, seed=8)
edge = np.zeros_like(X)
# 水線泡沫帶：通道邊緣與近岸
edge = np.maximum(edge, np.exp(-((np.abs(np.abs(Y if GEO == "redsea" else Y - 0.0) - CH_HALF)) / 1.2) ** 2) * (X < 3000) * (1.0 if GEO == "redsea" else 0.0))
sea_ob = add("sea", L.mesh_from_grid("sea", X, Y, Z, {"path": path, "edge": edge.astype(np.float32)}, mat_water(GEO == "ford")))
sea_ob.data.materials.append  # noqa

# --- 近景：岸邊沙丘（暗）、石頭與蘆葦的剪影
nx = np.arange(-12.0, NEAR_CREST + 4.0, 0.12)
ny = np.arange(-45.0, 45.01, 0.12)
NX, NY = np.meshgrid(nx, ny)
crest = L.fbm2(NY, NY * 0.0, 12.0, 1.2, seed=3) * 0.28
zn = 0.12 + crest + 0.05 * (NX - NEAR_CREST)
zn = np.where(NX > NEAR_CREST, 0.12 + crest - 0.6 * (NX - NEAR_CREST) / 4.0, zn)
zn = zn + 0.35 * L.fbm2(NX, NY, 7.0, 0.8, seed=4) * L.smoothstep(NEAR_CREST - 6, NEAR_CREST, NX)
near_mat = mat_sand("near_sand", "#4a3a2c")
add("near", L.mesh_from_grid("near_ground", NX, NY, zn, None, near_mat))
rock_mat = L.pbr("near_rock", "#2d2620", 0.95)
rocks = []
for k in range(5):
    bm = bmesh.new()
    L.sphere_bm(1.0, (0, 0, 0.3), (rnd.uniform(1.0, 1.6), rnd.uniform(0.8, 1.2), rnd.uniform(0.5, 0.9)), 2, bm, noise=0.3, seed=k + 50)
    me = bpy.data.meshes.new(f"nrock{k}"); bm.to_mesh(me); bm.free(); me.materials.append(rock_mat); rocks.append(me)
reed_mat = L.pbr("near_reed", "#3a3622", 0.9)
reed = bpy.data.meshes.new("nreed")
bm = bmesh.new()
for q in range(10):
    a_ = rnd.uniform(0, 6.28); r_ = rnd.uniform(0, 0.25); hh = rnd.uniform(1.0, 2.2)
    L.tube_bm([(r_ * math.cos(a_), r_ * math.sin(a_), 0), (r_ * math.cos(a_) + rnd.uniform(-0.15, 0.15), r_ * math.sin(a_), hh * 0.6), (r_ * math.cos(a_) + rnd.uniform(-0.4, 0.4), r_ * math.sin(a_) + rnd.uniform(-0.2, 0.2), hh)], [0.025, 0.018, 0.004], 4, bm)
bm.to_mesh(reed); bm.free(); reed.materials.append(reed_mat)
ng = L.Ground([objs["near"][0]])
for i in range(46):
    y = rnd.uniform(-22, 22)
    x = NEAR_CREST + rnd.uniform(-1.6, 0.8)
    z = ng.z(x, y)
    if z is None:
        continue
    add("near", L.instance(rnd.choice(rocks), f"nr_{i}", (x, y, z - 0.08), rot_z=rnd.uniform(0, 6.28), scale=rnd.uniform(0.25, 0.85)))
for i in range(60 if GEO == "ford" else 40):
    y = rnd.uniform(-24, 24)
    x = NEAR_CREST + rnd.uniform(-1.8, 1.2)
    z = ng.z(x, y)
    if z is None:
        continue
    add("near", L.instance(reed, f"rd_{i}", (x, y, z - 0.05), rot_z=rnd.uniform(0, 6.28), scale=rnd.uniform(0.4, 1.0)))

# --- 遠岸：連續的山脊（redsea）或東岸平原＋楊樹＋遠方台地（ford）
if GEO == "redsea":
    fx = log_axis(RIDGE_X0, 40000.0, 160, 2.2)
    fy = sym_axis(90000.0, 420, 3.0)
    FX, FY = np.meshgrid(fx, fy)
    ramp = L.smoothstep(RIDGE_X0, RIDGE_X0 + 2600.0, FX)
    r = 1.0 - np.abs(L.fbm2(FX * 0.9, FY * 0.9, 9000.0, 450.0, seed=11))
    FZ = RIDGE_K * ramp * (140.0 + 360.0 * r ** 2.2 + 90.0 * L.fbm2(FX, FY, 1800.0, 120.0, seed=12))
    FZ = FZ + 6.0 * L.fbm2(FX, FY, 400.0, 20.0, seed=13) * ramp
    far_ob = add("far", L.mesh_from_grid("far_ridge", FX, FY, FZ, None, mat_far("#7b6354", "#9a7a66")))
else:
    fx = np.unique(np.concatenate([np.linspace(SEA_X1 - 6, 600, 90), log_axis(600, 30000.0, 120, 2.0)]))
    fy = sym_axis(30000.0, 360, 3.0)
    FX, FY = np.meshgrid(fx, fy)
    plateau = L.smoothstep(7000.0, 11000.0, FX)
    r = 1.0 - np.abs(L.fbm2(FX, FY, 7000.0, 350.0, seed=21))
    FZ = 0.8 + 1.5 * L.fbm2(FX, FY, 60.0, 4.0, seed=22) + plateau * (60.0 + 170.0 * r ** 2.0)
    FZ = np.where(FX < SEA_X1 + 10, np.minimum(FZ, 0.35 + 0.5 * (FX - (SEA_X1 - 6)) / 16.0), FZ)
    shore_x = 283.0 + 10.0 * L.fbm2(FY, FY * 0.0, 70.0, 5.0, seed=31)
    FZ = np.where(FX < shore_x, -1.0, FZ)
    far_ob = add("far", L.mesh_from_grid("far_bank", FX, FY, FZ, {}, mat_far("#8a6e52", "#a68563")))
    # 東岸的楊樹與蘆葦（細長剪影）
    tree_mat = L.pbr("far_tree", "#3d4a2a", 0.85)
    tms = []
    for k in range(4):
        bm = bmesh.new()
        h = rnd.uniform(9.0, 15.0)
        L.tube_bm([(0, 0, 0), (0.1, 0, h * 0.5), (0, 0.1, h * 0.9)], [0.28, 0.2, 0.08], 6, bm)
        for q in range(7):
            L.sphere_bm(rnd.uniform(1.3, 2.0) * (1.0 - 0.06 * q), (rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4), h * (0.28 + 0.1 * q)), (1.0, 1.0, 1.5), 1, bm, noise=0.25, seed=q + 5 * k)
        me = bpy.data.meshes.new(f"ptree{k}"); bm.to_mesh(me); bm.free(); me.materials.append(tree_mat); tms.append(me)
    fg = L.Ground([far_ob])
    for i in range(260):
        y = rnd.gauss(0, 520)
        x = SEA_X1 + rnd.uniform(4.0, 150.0) * (0.3 + abs(rnd.gauss(0, 1.0)))
        z = fg.z(x, y)
        if z is None:
            continue
        add("far", L.instance(rnd.choice(tms), f"pt_{i}", (x, y, z), rot_z=rnd.uniform(0, 6.28), scale=rnd.uniform(0.7, 1.4)))

# ----------------------------------------------------------------------------- 相機與渲染
cam = L.set_camera((0.0, 0.0, CAM_Z), (100.0, 0.0, CAM_Z + 4.0), lens=28.0, clip=(0.1, 2.0e6))
cam.rotation_euler = (math.pi / 2 + math.radians(1.6), 0.0, -math.pi / 2)       # 朝 +x，略仰（地平線約在畫面 55% 處）
L.render_settings(a.w, a.h, a.samples)
sc.render.film_transparent = False
meta_out = {"scene": SCENE, "res": [a.w, a.h]}
order = ["sky", "far", "sea", "near"]
vis_all = [o for k in objs for o in objs[k]]
for plate in order:
    if a.only and plate != a.only:
        continue
    for o in vis_all:
        o.hide_render = True
    for o in objs[plate]:
        o.hide_render = False
    sc.render.film_transparent = plate != "sky"
    base = os.path.join(a.out, plate)
    L.render_pair(base, sun_dir=sund, y_pass=False)
    print("PLATE", plate)
with open(os.path.join(a.out, "meta.json"), "w", encoding="utf-8") as f:
    json.dump(meta_out, f)
print("done", SCENE)
