"""封面（示劍山谷清晨）。用法：
blender -b --python epic_cover.py -- --style A --w 1280 --h 720 --samples 48 --out <png>
"""
import argparse, math, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import epic_lib as L
import epic_props as P
import epic_heroes as H
import style_a as S
import bpy
import bmesh
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--style", default="A")
ap.add_argument("--w", type=int, default=1280)
ap.add_argument("--h", type=int, default=720)
ap.add_argument("--samples", type=int, default=48)
ap.add_argument("--out", default=os.path.join(L.ROOT, "lab", "renders", "epic", "cover_test.png"))
ap.add_argument("--probe", action="store_true")
a = ap.parse_args(argv)

sc = L.fresh_scene("cover")
meta, layers = L.load_terrain("cover")
ground = L.Ground(layers)
mat = P.terrain_material("terrain_cover", "levant_warm", veg_k=0.4)
for o in layers:
    o.data.materials.append(mat)
if a.probe:
    for (x, y) in [(0, 0), (-100, 0), (400, 0), (-1500, 0), (-250, 700), (-250, -700), (-900, 1800), (-900, -1800), (-1200, 1000), (-1200,-1000)]:
        print("Z", x, y, ground.z(x, y))
    sys.exit(0)

rnd = random.Random(11)
STYLE = a.style
env = os.environ
# 谷軸：從鏡頭沿著谷往東南（方位角 AX，數學角）；太陽在谷口，稍偏左
CAM = (float(env.get("CAMX", -1180)), float(env.get("CAMY", 350)))
AX = math.radians(float(env.get("AX", -24)))
ux, uy = math.cos(AX), math.sin(AX)          # 軸向單位向量
vx, vy = -uy, ux                              # 左側單位向量
def at(d, off=0.0):
    return (CAM[0] + ux * d + vx * off, CAM[1] + uy * d + vy * off)
OAK = at(float(env.get("OAKD", 78)), float(env.get("OAKOFF", 7)))
STONE = at(40.0, -9.0)
TGT = at(900, 0)
sun_az, sun_el = math.degrees(AX) + float(env.get("SUNOFF", 3.2)), float(env.get("SUNEL", 7.5))

sky, sunobj, sund = S.world("cover", sun_az, sun_el=sun_el, **({"sun_energy": float(env["SUNE"])} if "SUNE" in env else {}), **({"fill": float(env["FILL"])} if "FILL" in env else {}))
gz = ground.z
print("floor z at oak", gz(*OAK), "cam", gz(*CAM))

# --- 橡樹與立石
wo, fo = P.build_oak(seed=4, spread=15.0, trunk_r=0.8)
P.finish_oak(wo, fo, (OAK[0], OAK[1], gz(*OAK)), 1.25, 0.7)
st = P.build_stone()
st.scale = (1.35, 1.35, 1.35)
st.location = (STONE[0], STONE[1], gz(*STONE) + 0.25)
st.rotation_euler = (0.03, 0.04, math.radians(float(env.get("STONEROT", 40))))

# --- 簡化人形
figs = P.build_figure_meshes()
robe_cols = ["#d8cdb0", "#c9b88e", "#9a7b57", "#7a5a3d", "#a3553f", "#b97b45", "#5b6f8a", "#e2d6b6", "#8a7a63", "#6e5a47"]
crowd = []
_n = [0]


def uid_name():
    _n[0] += 1
    return f"sheep_{_n[0]}"


def person(x, y, heading, col=None, k=None, scale=None):
    z = gz(x, y)
    if z is None:
        return None
    k = rnd.randrange(len(figs)) if k is None else k
    col = tuple(L.srgb(col or rnd.choice(robe_cols)))
    o = L.instance(figs[k], f"p_{len(crowd)}", (x, y, z), rot_z=heading + math.pi / 2 + rnd.uniform(-0.25, 0.25), scale=scale or rnd.uniform(0.94, 1.06), color=col)
    crowd.append(o)
    return o

walk_head = AX + math.pi        # 人群朝鏡頭走（向谷裡）
# 從谷口（遠處）走過來的一長串，越近越寬
for i in range(int(env.get("NCROWD", 900))):
    t = rnd.random() ** 1.5
    d = 40 + t * 1300
    off = rnd.gauss(0, 10 + 0.02 * d + 14 * (1 - t))
    x, y = at(d, off)
    if abs(x - OAK[0]) < 12 and abs(y - OAK[1]) < 12:
        continue
    person(x, y, walk_head + rnd.uniform(-0.3, 0.3))
# 橡樹前站定的群（十二群）：樹與鏡頭之間的空地
for gi in range(12):
    ang = -0.9 + gi * 0.165
    d = 62 + 28 * math.cos(gi * 1.7) + 8 * gi % 5
    off = 36 * math.sin(ang * 3.6) + (gi - 6) * 5
    cx, cy = at(d, off)
    for j in range(rnd.randint(5, 9)):
        person(cx + rnd.gauss(0, 3.0), cy + rnd.gauss(0, 3.0), AX + rnd.uniform(-0.3, 0.3))
# 近景幾個人（尺度參照），背向鏡頭走遠與側身
for (d, off, hd) in ([] if STYLE == 'B' else [(13, -6.5, 0.1), (17, 5.5, -0.15), (24, -2.0, 0.3), (9, 9.5, 3.4)]):
    x, y = at(d, off)
    person(x, y, AX + hd, k=rnd.choice([1, 0, 4, 6]))

# --- 風格 B：幾位寫實人物放在近景
if STYLE == "B":
    heroes = H.build_all(("elder", "woman", "shepherd", "youth", "mother"))
    placements = [("elder", 9.0, -2.2, 180 + 18), ("woman", 7.2, 3.6, 90 - 25), ("shepherd", 12.0, -7.4, 180 - 22),
                  ("youth", 15.0, 1.6, 180 + 10), ("mother", 10.5, 8.0, 15),
                  ("mother", 6.0, -8.6, 180 - 15), ("youth", 19.0, -5.0, 180 + 35), ("elder", 13.5, 10.5, 180 - 38), ("woman", 22.0, 5.0, 180 + 5)]
    for kind, d, off, rel in placements:
        x, y = at(d, off)
        z = gz(x, y)
        phi = AX + math.radians(rel)
        o = L.instance(heroes[kind], f"hero_{kind}", (x, y, z), rot_z=phi - math.pi / 2, scale=rnd.uniform(0.98, 1.03))
        o.hide_render = False
        o.hide_viewport = False
        for sl in o.material_slots:
            pass

# --- 羊群（遠中景幾群白點）
sheep_m = P.build_sheep()
for (dd, off, n) in [(85, -38, 26), (130, 46, 30), (60, 34, 18), (170, -20, 34), (240, 30, 40)]:
    for _ in range(n):
        x, y = at(dd + rnd.gauss(0, 14), off + rnd.gauss(0, 11))
        if gz(x, y) is None:
            continue
        L.instance(sheep_m, uid_name(), (x, y, gz(x, y)), rot_z=rnd.uniform(0, 6.28), scale=rnd.uniform(0.9, 1.15), color=tuple(L.srgb(rnd.choice(["#e4dcc8", "#cdbf9f", "#d6cdb8", "#8f7a5c"]))))

# --- 灌木與橄欖
bush_m = []
bmat = L.pbr("bush_mat", "#6d7a45", 0.9)
for k in range(3):
    bm = bmesh.new()
    for q in range(3):
        L.sphere_bm(rnd.uniform(0.5, 0.9), (rnd.uniform(-0.5, 0.5), rnd.uniform(-0.5, 0.5), 0.4 + rnd.uniform(0, 0.3)), (1, 1, 0.7), 1, bm, noise=0.25, seed=q + k * 7)
    me = bpy.data.meshes.new(f"bush{k}")
    bm.to_mesh(me); bm.free()
    me.materials.append(bmat)
    bush_m.append(me)
olive_m = []
omat = L.pbr("olive_mat", "#59603c", 0.85)
for k in range(3):
    bm = bmesh.new()
    L.tube_bm([(0, 0, 0), (0.1, 0, 0.8), (0.15, 0.05, 1.6)], [0.22, 0.16, 0.12], 6, bm)
    for q in range(4):
        L.sphere_bm(rnd.uniform(1.2, 1.8), (rnd.uniform(-1, 1), rnd.uniform(-1, 1), 2.1 + rnd.uniform(-0.2, 0.6)), (1, 1, 0.7), 1, bm, noise=0.2, seed=q + 10 * k)
    me = bpy.data.meshes.new(f"olive{k}")
    bm.to_mesh(me); bm.free()
    me.materials.append(omat)
    olive_m.append(me)
nb = nt = 0
for _ in range(int(env.get("NBUSH", 16000))):
    d = rnd.uniform(-60, 1400); off = rnd.uniform(-700, 700)
    x, y = at(d, off)
    hit = ground.zn(x, y)
    if hit is None:
        continue
    loc, nrm = hit[0], hit[1]
    if nrm.z < 0.5:
        continue
    near_path = abs(off) < 40 and d < 1000
    if near_path and rnd.random() < 0.85:
        continue
    if nrm.z > 0.9 and rnd.random() < 0.9:
        continue
    L.instance(rnd.choice(bush_m), f"bush_{nb}", (loc.x, loc.y, loc.z - 0.1), rot_z=rnd.uniform(0, 6.28), scale=rnd.uniform(0.9, 2.2))
    nb += 1
for _ in range(2500):
    d = rnd.uniform(-60, 1500); off = rnd.uniform(-900, 900)
    x, y = at(d, off)
    if abs(x - OAK[0]) < 30 and abs(y - OAK[1]) < 30:
        continue
    hit = ground.zn(x, y)
    if hit is None:
        continue
    loc, nrm = hit[0], hit[1]
    if nrm.z < 0.80 or nrm.z > 0.96 or abs(off) < 70:
        continue
    L.instance(rnd.choice(olive_m), f"olive_{nt}", (loc.x, loc.y, loc.z), rot_z=rnd.uniform(0, 6.28), scale=rnd.uniform(0.9, 1.6))
    nt += 1
print("bushes", nb, "olives", nt, "people", len(crowd))

# --- 岩塊（淺色石灰岩，散在坡面與谷底，打破石膏感）
rock_m = []
rmat = L.pbr("rock_mat", "#c9b88f", 0.95)
for k in range(4):
    bm = bmesh.new()
    L.sphere_bm(1.0, (0, 0, 0.2), (rnd.uniform(1.0, 1.7), rnd.uniform(0.8, 1.2), rnd.uniform(0.5, 0.8)), 2, bm, noise=0.28, seed=40 + k)
    me = bpy.data.meshes.new(f"rock{k}")
    bm.to_mesh(me); bm.free()
    me.materials.append(rmat)
    rock_m.append(me)
nr = 0
for _ in range(int(env.get("NROCK", 5000))):
    dd = rnd.uniform(-60, 1300); off = rnd.uniform(-650, 650)
    x, y = at(dd, off)
    hit = ground.zn(x, y)
    if hit is None:
        continue
    loc, nrm = hit[0], hit[1]
    if nrm.z > 0.97 and rnd.random() < 0.85:
        continue
    if abs(off) < 25 and dd < 600 and rnd.random() < 0.9:
        continue
    L.instance(rnd.choice(rock_m), f"rock_{nr}", (loc.x, loc.y, loc.z - 0.15), rot_z=rnd.uniform(0, 6.28), scale=rnd.uniform(0.35, 2.4) * (1.6 if nrm.z < 0.8 else 1.0))
    nr += 1

# --- 相機
CH = float(env.get("CAMH", 2.7 if STYLE == "B" else 6.5))
cam = L.set_camera((CAM[0], CAM[1], gz(*CAM) + CH), (TGT[0], TGT[1], gz(*TGT) + float(env.get("TGTH", 55))), lens=float(env.get("LENS", 24)))
L.render_settings(a.w, a.h, a.samples)
base = a.out[:-4] if a.out.endswith(".png") else a.out
t = L.render_pair(base, sun_dir=sund)
print("names", len(L.check_names()), "times", t)
