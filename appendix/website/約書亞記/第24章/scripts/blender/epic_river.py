"""幼發拉底河（第2節他拉的帳棚與小神像、第3節亞伯拉罕一家渡河）。風格 A。
用法：blender -b --python epic_river.py -- --style A --w 1280 --h 720 --samples 32 --out <不含副檔名>，環境變數 FRAME 選畫格：
  tent_high / tent_descend / tent_scene / ford_high / ford_descend / ford_scene
座標：本地公尺，原點東經 38.05、北緯 36.78；河道見 epic_river_geo.py。
"""
import argparse, math, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import epic_lib as L
import epic_props as P
import epic_river_geo as RG
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
ap.add_argument("--out", default=os.path.join(L.ROOT, "lab", "renders", "epic", "river_test"))
a = ap.parse_args(argv)
env = os.environ
FRAME = env.get("FRAME", "tent_scene")
rnd = random.Random(21)

sc = L.fresh_scene("river")
meta, layers = L.load_terrain("river")
VEX = meta["vexag"]
tmat = P.terrain_material("terrain_river", "desert", veg_k=0.7, field_scale=0.011)
for o in layers:
    o.data.materials.append(tmat)
ground = L.Ground(layers)
gz = ground.z

TENT = (540.0, 10.0)                       # 主帳棚
FORD_Y = -1500.0
FORD_X = float(RG.centerline_x(FORD_Y))


def river_z(y):
    return float(RG.river_level(y)) * VEX


# ----------------------------------------------------------------------------- 河面
def build_river():
    ys = np.arange(11000.0, -11000.01, -30.0)
    cols = np.linspace(-1.0, 1.0, 9)
    X = np.zeros((len(ys), len(cols)))
    Y = np.zeros_like(X)
    Z = np.zeros_like(X)
    for i, y in enumerate(ys):
        cx = float(RG.centerline_x(y))
        for j, c in enumerate(cols):
            X[i, j] = cx + c * (RG.HALF_W + 4.0)
            Y[i, j] = y
            Z[i, j] = river_z(y) + 0.35
    m = L.new_mat("river_water")
    nt = m.node_tree
    b = L.bsdf_of(m)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (0.6, 0.12, 1.0)      # 沿河（y）拉長的水紋
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    n1 = L.noise_tex(nt, mp.outputs["Vector"], 1.6, 4.0, 0.5)
    n2 = L.noise_tex(nt, tc.outputs["Object"], 0.25, 3.0, 0.5)
    col = L.ramp(nt, n1, [(0.2, P.lin("#17434a")), (0.55, P.lin("#256068")), (0.9, P.lin("#4e8d88"))])
    nt.links.new(col, b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.13
    for k, v in (("IOR", 1.33), ("Specular IOR Level", 0.6)):
        if k in b.inputs:
            b.inputs[k].default_value = v
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.3
    bump.inputs["Distance"].default_value = 0.25
    nt.links.new(L.math_node(nt, "ADD", L.math_node(nt, "MULTIPLY", n1, 0.6), L.math_node(nt, "MULTIPLY", n2, 0.5)), bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return L.mesh_from_grid("river_water", X, Y, Z, {"wet": np.ones_like(X)}, m)


river = build_river()

# ----------------------------------------------------------------------------- 天空與光
FR = {
    # 畫格：相機、目標、太陽方位、鏡頭
    "tent_high": dict(cam=(-2700.0, -2000.0, 760.0), tgt=(650.0, 40.0, 150.0), lens=30, sun_az=18.0, sun_el=8.0),
    "tent_descend": dict(cam=(300.0, -300.0, 70.0), tgt=(560.0, 12.0, 4.0), lens=40, sun_az=20.0, sun_el=8.0),
    "tent_scene": dict(cam=(TENT[0] + 1.2, TENT[1] - 6.0, 1.2), tgt=(TENT[0] - 0.3, TENT[1] + 1.1, 0.78), lens=27, sun_az=343.0, sun_el=9.0),
    "ford_high": dict(cam=(FORD_X - 3000.0, FORD_Y - 900.0, 760.0), tgt=(FORD_X + 100.0, FORD_Y, 150.0), lens=30, sun_az=12.0, sun_el=7.0),
    "ford_descend": dict(cam=(FORD_X - 520.0, FORD_Y - 40.0, 95.0), tgt=(FORD_X + 60.0, FORD_Y, 4.0), lens=32, sun_az=10.0, sun_el=7.0),
    "ford_scene": dict(cam=(FORD_X - 160.0, FORD_Y - 10.0, None), tgt=(FORD_X + 80.0, FORD_Y + 2.0, None), lens=24, sun_az=8.0, sun_el=6.0),
}
fr = FR[FRAME]
sky, sunobj, sund = S.world("river", fr["sun_az"], sun_el=fr["sun_el"])


# ----------------------------------------------------------------------------- 放置工具
fig_meshes = P.build_figure_meshes()
robe_cols = ["#d8cdb0", "#c9b88e", "#9a7b57", "#7a5a3d", "#a3553f", "#b97b45", "#5b6f8a", "#e2d6b6", "#8a7a63", "#6e5a47"]
sheep_m = P.build_sheep()
horse_m = P.build_horse(gallop=0.2)
tent_m = P.build_tent()
idols = P.build_idols()
cnt = [0]


def uid(p):
    cnt[0] += 1
    return f"{p}_{cnt[0]}"


def lc(h):
    return tuple(L.srgb(h))


def put(mesh, x, y, yaw=0.0, scale=1.0, color=None, z=None, dz=0.0, tilt=(0.0, 0.0)):
    zz = gz(x, y) if z is None else z
    if zz is None or (FRAME == 'ford_scene' and near_cam(x, y, 15.0)):
        return None
    return L.instance(mesh, uid("o"), (x, y, zz + dz), rot=(tilt[0], tilt[1], yaw), scale=scale, color=color)


def person(x, y, heading, k=None, col=None, scale=None, dz=0.0):
    k = rnd.randrange(len(fig_meshes)) if k is None else k
    return put(fig_meshes[k], x, y, heading + math.pi / 2 + rnd.uniform(-0.2, 0.2), scale or rnd.uniform(0.95, 1.05), lc(col or rnd.choice(robe_cols)), dz=dz)


def near_cam(x, y, r=45.0):
    return math.hypot(x - fr['cam'][0], y - fr['cam'][1]) < r


# ----------------------------------------------------------------------------- 河岸的樹與蘆葦
tree_mats = {
    "poplar": L.pbr("poplar_leaf", "#5e7436", 0.8),
    "tamarisk": L.pbr("tamarisk_leaf", "#7b8a55", 0.8),
    "reed": L.pbr("reed_mat", "#8a8c4c", 0.9),
    "trunk": L.pbr("trunk_mat", "#4b3d2c", 0.9),
}
tree_ms = []
for k in range(4):
    bm = bmesh.new()
    h = rnd.uniform(9.0, 14.0)
    L.tube_bm([(0, 0, 0), (0.1, 0, h * 0.5), (0, 0.1, h * 0.9)], [0.28, 0.2, 0.08], 6, bm)
    for q in range(7):
        zq = h * (0.28 + 0.1 * q)
        L.sphere_bm(rnd.uniform(1.3, 2.0) * (1.0 - 0.06 * q), (rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4), zq), (1.0, 1.0, 1.5), 1, bm, noise=0.25, seed=q + 5 * k)
    me = bpy.data.meshes.new(f"poplar{k}")
    bm.to_mesh(me); bm.free()
    me.materials.append(tree_mats["poplar"])
    tree_ms.append(me)
bush_ms = []
for k in range(3):
    bm = bmesh.new()
    for q in range(4):
        L.sphere_bm(rnd.uniform(0.8, 1.5), (rnd.uniform(-0.8, 0.8), rnd.uniform(-0.8, 0.8), rnd.uniform(0.5, 1.2)), (1, 1, 0.8), 1, bm, noise=0.3, seed=q + 9 * k)
    me = bpy.data.meshes.new(f"tamarisk{k}")
    bm.to_mesh(me); bm.free()
    me.materials.append(tree_mats["tamarisk"])
    bush_ms.append(me)
ntree = 0
for _ in range(int(env.get("NTREE", 1700))):
    y = rnd.uniform(-3600.0, 1600.0)
    side = rnd.choice([-1, 1])
    s = RG.HALF_W + rnd.uniform(6.0, 220.0) ** 1.0
    x = float(RG.centerline_x(y)) + side * s
    z = gz(x, y)
    if z is None:
        continue
    if abs(x - TENT[0]) < 160 and abs(y - TENT[1]) < 90 or near_cam(x, y):
        continue
    L.instance(rnd.choice(tree_ms) if rnd.random() < 0.55 else rnd.choice(bush_ms), uid("tree"), (x, y, z), rot_z=rnd.uniform(0, 6.28), scale=rnd.uniform(0.8, 1.35))
    ntree += 1

# 灌木 / 乾草叢（高地上零星）
for _ in range(int(env.get("NBUSH", 4500))):
    x = rnd.uniform(-1800, 1800)
    y = rnd.uniform(-3200, 1500)
    z = gz(x, y)
    if z is None or near_cam(x, y, 60.0) or (abs(x - TENT[0]) < 14 and abs(y - TENT[1]) < 10):
        continue
    L.instance(rnd.choice(bush_ms), uid("shr"), (x, y, z - 0.1), rot_z=rnd.uniform(0, 6.28), scale=rnd.uniform(0.35, 0.8))

# 水邊蘆葦
reed_m = bpy.data.meshes.new("reed")
bm = bmesh.new()
for q in range(9):
    a_ = rnd.uniform(0, 6.28); r_ = rnd.uniform(0, 0.35); hh = rnd.uniform(1.6, 2.6)
    L.tube_bm([(r_ * math.cos(a_), r_ * math.sin(a_), 0), (r_ * math.cos(a_) + rnd.uniform(-0.2, 0.2), r_ * math.sin(a_), hh * 0.6), (r_ * math.cos(a_) + rnd.uniform(-0.5, 0.5), r_ * math.sin(a_) + rnd.uniform(-0.3, 0.3), hh)], [0.03, 0.02, 0.005], 4, bm)
bm.to_mesh(reed_m); bm.free()
reed_m.materials.append(tree_mats["reed"])
for _ in range(int(env.get("NREED", 900))):
    y = rnd.uniform(FORD_Y - 450, FORD_Y + 450) if rnd.random() < 0.6 else rnd.uniform(-400, 300)
    side = rnd.choice([-1, 1])
    x = float(RG.centerline_x(y)) + side * (RG.HALF_W - 4.0 + rnd.uniform(0, 14.0))
    z = gz(x, y)
    if z is None or near_cam(x, y, 22.0):
        continue
    L.instance(reed_m, uid("reed"), (x, y, z - 0.1), rot_z=rnd.uniform(0, 6.28), scale=rnd.uniform(0.7, 1.4))

# ----------------------------------------------------------------------------- 帳棚營地
def tent_at(x, y, yaw, sc_=1.0):
    return put(tent_m, x, y, yaw, sc_, lc(rnd.choice(["#7a2e22", "#a9772e", "#1c3a52", "#8a6a3c"])))


# 主帳棚：開口朝 -y（朝南），裡面放神像
tz = gz(*TENT)
tent_main = L.instance(tent_m, "tent_main", (TENT[0], TENT[1], tz), rot_z=0.0, scale=1.0, color=lc("#5c2a21"))
# 平台（石板）與神像
plat = L.mesh_obj("idol_platform", (lambda bm: (L.box_bm((2.6, 0.8, 0.22), (0, 0, 0.11), bm), bm)[1])(bmesh.new()), L.pbr("plat_mat", "#a89c82", 0.9))
plat.location = (TENT[0], TENT[1] + 1.05, tz)
placements = [("idol_pillar", -1.05, 0.0, 0.2), ("idol_standing", -0.5, 0.0, -0.12), ("idol_bull", 0.12, 0.05, 0.15), ("idol_seated", 0.62, 0.0, -0.2),
              ("idol_small", 1.0, -0.12, 0.3), ("idol_small", -0.12, -0.22, 0.0)]
for nm, dx, dy, yaw in placements:
    o = L.instance(idols[nm], uid("idol"), (TENT[0] + dx * 1.2, TENT[1] + 1.05 + dy, tz + 0.22), rot_z=yaw, scale=1.45)
# 帳內雜物：罐、袋、卷鋪蓋
pot_m = bpy.data.meshes.new("pot")
bm = bmesh.new()
L.lathe_bm([(0.12, 0.0), (0.2, 0.12), (0.22, 0.26), (0.14, 0.4), (0.1, 0.48), (0.13, 0.52)], 12, (1, 1), bm, closed_top=False)
bm.to_mesh(pot_m); bm.free()
pot_m.materials.append(L.pbr("pot_clay", "#8a5a3c", 0.85))
for p in pot_m.polygons:
    p.use_smooth = True
for dx, dy in ((-2.5, 0.9), (-2.2, 0.2), (2.4, 0.8), (2.1, -0.2), (-1.6, -0.8)):
    L.instance(pot_m, uid("pot"), (TENT[0] + dx, TENT[1] + dy, tz), rot_z=rnd.uniform(0, 6), scale=rnd.uniform(0.8, 1.2))
roll_m = bpy.data.meshes.new("roll")
bm = bmesh.new()
L.tube_bm([(-0.5, 0, 0.17), (0.5, 0, 0.17)], [0.17, 0.17], 10, bm)
bm.to_mesh(roll_m); bm.free()
roll_m.materials.append(L.pbr("roll_mat", "#a8553b", 0.9))
for dx, dy in ((2.0, 0.8), (-2.6, -0.4)):
    L.instance(roll_m, uid("roll"), (TENT[0] + dx, TENT[1] + dy, tz), rot_z=rnd.uniform(0, 3))
# 其他帳棚
others = [(TENT[0] - 22, TENT[1] + 14, 0.2, 0.9), (TENT[0] + 24, TENT[1] + 10, -0.3, 1.0), (TENT[0] - 8, TENT[1] + 34, 0.1, 0.85),
          (TENT[0] + 18, TENT[1] + 38, 0.4, 1.05), (TENT[0] - 40, TENT[1] - 6, 0.0, 0.95), (TENT[0] + 44, TENT[1] - 14, 0.3, 0.9),
          (TENT[0] - 30, TENT[1] + 52, -0.2, 0.8)]
for x, y, yaw, s_ in others:
    tent_at(x, y, yaw, s_)
# 羊圈（石牆圓圈）與羊
pen_c = (TENT[0] - 6, TENT[1] - 40)
ring_m = bpy.data.meshes.new("pen_stone")
bm = bmesh.new()
for k in range(36):
    a_ = 2 * math.pi * k / 36
    L.sphere_bm(0.55, (14 * math.cos(a_), 14 * math.sin(a_), 0.4), (1.5, 1.0, 0.8), 1, bm, noise=0.2, seed=k)
bm.to_mesh(ring_m); bm.free()
ring_m.materials.append(L.pbr("pen_mat", "#a3977c", 0.95))
put(ring_m, pen_c[0], pen_c[1], 0.0)
for _ in range(70):
    r = 12.5 * math.sqrt(rnd.random()); a_ = rnd.uniform(0, 6.28)
    put(sheep_m, pen_c[0] + r * math.cos(a_), pen_c[1] + r * math.sin(a_), rnd.uniform(0, 6.28), rnd.uniform(0.9, 1.15), lc(rnd.choice(["#e4dcc8", "#cdbf9f", "#d6cdb8", "#8f7a5c", "#5d4c3b"])))
for _ in range(10):
    put(horse_m, TENT[0] + rnd.uniform(-45, 45), TENT[1] + rnd.uniform(-35, 25), rnd.uniform(0, 6.28), 0.58, lc(rnd.choice(["#7d6b57", "#5f5043", "#9a8872"])))
# 人：主帳棚兩側的一家（剪影）與營地的人
for dx, dy, hd in ((-2.9, -0.2, 0.0), (3.0, 0.1, math.pi), (-6.2, -2.2, 0.3), (7.2, -1.8, math.pi * 0.8)):
    person(TENT[0] + dx, TENT[1] + dy, hd, k=rnd.choice([0, 1, 4, 6, 5]))
for _ in range(34):
    x, y = TENT[0] + rnd.uniform(-55, 55), TENT[1] + rnd.uniform(-50, 55)
    if abs(x - TENT[0]) < 12 and y < TENT[1] + 3:
        continue
    person(x, y, rnd.uniform(0, 6.28))
# 麥田由材質的田塊色表示；再加幾個運水的人沿河岸
for _ in range(20):
    y = rnd.uniform(-60, 60)
    person(float(RG.centerline_x(y)) + RG.HALF_W + rnd.uniform(4, 30), y, rnd.uniform(0, 6.28), k=3)

# ----------------------------------------------------------------------------- 渡口：亞伯拉罕一家與羊群過河往西
spray_m = bpy.data.meshes.new("splash")
bm = bmesh.new()
L.sphere_bm(0.25, (0, 0, 0), (1.4, 1.0, 0.6), 1, bm, noise=0.3, seed=3)
bm.to_mesh(spray_m); bm.free()
spray_m.materials.append(L.pbr("splash_mat", "#f4f6f2", 0.9))
bank_e = FORD_X + RG.HALF_W + 25
bank_w = FORD_X - RG.HALF_W - 25
n_sheep = int(env.get("NFLOCK", 260))
for i in range(n_sheep):
    t = rnd.random() ** 0.9 * (1.0 if rnd.random() < 0.75 else 1.18)   # 0 東岸 -> 1 西岸（>1 已上岸）
    x = bank_e + (bank_w - bank_e) * t + rnd.gauss(0, 10)
    y = FORD_Y + rnd.gauss(0, 24 - 10 * abs(t - 0.5))
    z = gz(x, y)
    if z is None:
        continue
    o = put(sheep_m, x, y, math.pi + rnd.uniform(-0.5, 0.5), rnd.uniform(0.9, 1.18), lc(rnd.choice(["#e4dcc8", "#cdbf9f", "#d6cdb8", "#8f7a5c", "#5d4c3b"])))
    if abs(x - FORD_X) < RG.HALF_W:
        L.instance(spray_m, uid("spl"), (x + rnd.uniform(-0.5, 0.5), y + rnd.uniform(-0.5, 0.5), river_z(FORD_Y) + 0.45), rot_z=rnd.uniform(0, 6), scale=rnd.uniform(0.8, 1.6))
for i in range(int(env.get("NCARAVAN", 70))):
    t = rnd.random()
    x = bank_e + (bank_w - bank_e) * t + rnd.gauss(0, 9)
    y = FORD_Y + rnd.gauss(0, 20)
    if rnd.random() < 0.28:
        o = put(horse_m, x, y, math.pi + rnd.uniform(-0.3, 0.3), 0.6, lc(rnd.choice(["#7d6b57", "#5f5043", "#9a8872"])))
    else:
        person(x, y, math.pi, k=rnd.choice([0, 1, 2, 3, 4, 6]))
    if abs(x - FORD_X) < RG.HALF_W:
        L.instance(spray_m, uid("spl"), (x, y, river_z(FORD_Y) + 0.45), rot_z=0, scale=rnd.uniform(0.8, 1.8))
# 鏡頭前的羊群與牧人（已上西岸，往西走）
for i in range(70):
    x = FORD_X - RG.HALF_W - rnd.uniform(8, 85)
    y = FORD_Y + rnd.gauss(-4, 15)
    put(sheep_m, x, y, math.pi + rnd.uniform(-0.7, 0.7), rnd.uniform(0.95, 1.2), lc(rnd.choice(["#e4dcc8", "#cdbf9f", "#d6cdb8", "#8f7a5c", "#5d4c3b"])))
for dx, dy in ((22, -3), (46, 7), (14, 9), (66, -9)):
    person(FORD_X - RG.HALF_W - dx, FORD_Y + dy, math.pi + rnd.uniform(-0.4, 0.4), k=rnd.choice([1, 4, 6]))
# 東岸等待與已經上西岸的人群
for i in range(60):
    side = rnd.choice([-1, 1])
    x = (bank_e + rnd.uniform(0, 70)) if side > 0 else (bank_w - rnd.uniform(0, 60))
    person(x, FORD_Y + rnd.gauss(0, 30), math.pi + rnd.uniform(-0.4, 0.4))

# 一道斜射進帳棚的日光：用聚光燈表示（打在神像上）
if FRAME == "tent_scene":
    sp = bpy.data.lights.new("idol_spot", "SPOT")
    sp.energy = 4500.0
    sp.color = (1.0, 0.76, 0.48)
    sp.spot_size = math.radians(24)
    sp.spot_blend = 0.7
    sp.shadow_soft_size = 0.4
    spo = bpy.data.objects.new("idol_spot", sp)
    L.link(spo)
    spo.location = (TENT[0] + 8.5, TENT[1] - 7.0, tz + 3.4)
    dirv = Vector((TENT[0] - 0.1, TENT[1] + 1.05, tz + 0.5)) - spo.location
    spo.rotation_euler = dirv.to_track_quat("-Z", "Y").to_euler()

# ----------------------------------------------------------------------------- 相機
cam_pos = list(fr["cam"])
tgt = list(fr["tgt"])
if cam_pos[2] is None:       # 貼地：站在西岸，鏡頭離地 1.6 m
    cam_pos[2] = (gz(cam_pos[0], cam_pos[1]) or 0.0) + 1.25
if tgt[2] is None:
    tgt[2] = (gz(tgt[0], tgt[1]) or 0.0) + 1.3
elif FRAME in ("tent_high", "tent_descend", "ford_high", "ford_descend"):
    zt = gz(tgt[0], tgt[1]) or 0.0
    zc = gz(cam_pos[0], cam_pos[1]) or 0.0
    cam_pos[2] = max(zc, zt) + cam_pos[2]
    tgt[2] = zt + tgt[2]
else:
    cam_pos[2] = (gz(cam_pos[0], cam_pos[1]) or 0.0) + cam_pos[2]
    tgt[2] = (gz(tgt[0], tgt[1]) or 0.0) + tgt[2]
cam = L.set_camera(tuple(cam_pos), tuple(tgt), lens=fr["lens"])
L.render_settings(a.w, a.h, a.samples)
base = a.out[:-4] if a.out.endswith(".png") else a.out
t = L.render_pair(base, sun_dir=sund)
print("names", len(L.check_names()), "times", t, "trees", ntree)
