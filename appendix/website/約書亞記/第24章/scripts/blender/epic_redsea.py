"""紅海（第6–7節）：大隊人馬在海邊，兩者中間落下一片黑暗，海水合上淹沒追兵。
用法：blender -b --python epic_redsea.py -- --style A|B|C --w 1280 --h 720 --samples 24 --out <不含副檔名>
座標：本地公尺，原點在西奈海岸線（東經 32.63、北緯 29.80），x 向東、y 向北；鏡頭在東岸往西看。
"""
import argparse, math, os, random, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import epic_lib as L
import epic_props as P
import epic_heroes as H
import style_a as S
import bpy, bmesh
import numpy as np
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--style", default="A")
ap.add_argument("--w", type=int, default=1280)
ap.add_argument("--h", type=int, default=720)
ap.add_argument("--samples", type=int, default=24)
ap.add_argument("--out", default=os.path.join(L.ROOT, "lab", "renders", "epic", "redsea_test"))
a = ap.parse_args(argv)
env = os.environ
STYLE = a.style
rnd = random.Random(7)

sc = L.fresh_scene("redsea")
meta, layers = L.load_terrain("redsea")
tmat = P.terrain_material("terrain_red", "desert", sea=True)
for o in layers:
    o.data.materials.append(tmat)

# ----------------------------------------------------------------------------- 海的高度場
W0 = 40.0          # 通道半寬
HC = 14.0          # 水牆高出海面
FLOOR = -11.0      # 海底
X0, X1 = -1300.0, 40.0
c_start, c_end = -115.0, -215.0


def collapse(x, y=0.0):
    wob = 14.0 * L.vnoise2(np.asarray(y, dtype=np.float64) * 1.0, np.asarray(x, dtype=np.float64) * 0.0, 17.0, 5) if not np.isscalar(y) else 0.0
    return L.smoothstep(c_start, c_end, x + wob)   # x 越負（越遠）越接近 1


def sea_height(X, Y):
    s = np.abs(Y)
    c = collapse(X, Y)
    calm = L.smoothstep(-270.0, -480.0, X)       # 更遠處海面回復平靜
    cc = c * (1 - calm)
    rampx = L.smoothstep(-40.0, 6.0, X)           # 出口：海底升上岸邊
    floor = FLOOR * (1 - rampx)
    n1 = L.fbm2(X, Y, 90.0, 6.0, seed=31)
    n2 = L.fbm2(X, Y, 18.0, 2.0, seed=32)
    W = W0 * (1 - 0.94 * cc)
    inner_level = floor + 11.9 * cc ** 0.8
    ramp_w = 3.5 + 7.0 * cc
    t = L.smoothstep(W, W + ramp_w, s)
    crest = (HC * (1 - 0.45 * cc) + 5.0 * cc * (1 - cc) * 4.0 * (0.6 + 0.4 * n1)) * (1 - rampx)
    outside_decay = np.exp(-np.maximum(s - (W + ramp_w), 0) / (26 + 24 * cc))
    wall = crest * outside_decay * (1 + 0.12 * n1)
    base = inner_level * (1 - t) + wall * t
    turb = (n1 * 1.6 + n2 * 0.5) * (0.15 + 2.4 * cc)
    ripple = 0.04 * np.sin(Y * 1.7 + n1 * 5.0) + 0.03 * n2
    wetm = (inner_level > floor + 0.4) | (t > 0.02)
    z = base + np.where(wetm, turb * (0.25 + 0.75 * t + cc), ripple)
    far_sea = np.clip((s - 140.0) / 120.0, 0, 1)
    z = z * (1 - far_sea) + (n1 * 0.45 + n2 * 0.2) * far_sea
    cm = calm * np.exp(-s / 250.0)
    z = z * (1 - cm) + (n1 * 0.5) * cm
    edge = L.smoothstep(0, 1, np.minimum(np.minimum(X - X0, X1 - X) / 90.0, np.minimum(Y + 800.0, 800.0 - Y) / 90.0))
    # 岸邊與外圍邊界回到 0（但通道內的乾海底不受邊界淡出影響）
    chan = np.exp(-(s / (W0 + 8.0)) ** 8)
    z = np.where(chan > 0.6, z, z * edge)
    return z, c, cc, t, s


def build_sea():
    ys = np.concatenate([
        np.arange(-800.0, -110.0, 11.0),
        np.arange(-110.0, -70.0, 2.5),
        np.arange(-70.0, 70.0, 0.6),
        np.arange(70.0, 110.0, 2.5),
        np.arange(110.0, 800.01, 11.0)])
    xs = np.concatenate([np.arange(X0, -330.0, 5.0), np.arange(-330.0, -80.0, 0.9), np.arange(-80.0, X1 + 0.01, 2.0)])
    X, Y = np.meshgrid(xs, ys)
    z, c, cc, t, s = sea_height(X, Y)
    wet = (z > -10.4 * (1 - L.smoothstep(-40.0, 6.0, X))) | (t > 0.05)
    nf = L.fbm2(X, Y, 22.0, 1.5, seed=41)
    crest_h = HC * (1 - 0.45 * cc)
    crest_mask = np.exp(-((z - crest_h) / 2.0) ** 2) * (t > 0.6)
    nfb = L.fbm2(X, Y, 40.0, 5.0, seed=47)
    patches = L.smoothstep(0.1, 0.55, nfb + 0.25 * nf)
    foam = np.clip(0.8 * L.smoothstep(0.1, 0.8, cc) * patches + crest_mask * (0.45 + 0.5 * cc)
                   + 0.25 * (t > 0.02) * (t < 0.55) * (0.3 + 0.7 * (nf * 0.5 + 0.5)), 0, 1)
    ob = L.mesh_from_grid("sea", X, Y, z, {"wet": wet.astype(np.float32), "foam": foam.astype(np.float32), "cc": cc.astype(np.float32)}, None)
    return ob, (X, Y, z)


def sea_material():
    m = L.new_mat("sea_mat")
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(b.outputs["BSDF"], out.inputs["Surface"])
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    pos = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], pos.inputs["Vector"])
    def attr(name):
        n = nt.nodes.new("ShaderNodeAttribute")
        n.attribute_name = name
        n.attribute_type = "GEOMETRY"
        return n.outputs["Fac"]
    wet, foam, cc = attr("wet"), attr("foam"), attr("cc")
    P_ = geo.outputs["Position"]
    n_big = L.noise_tex(nt, P_, 0.03, 4.0)
    n_mid = L.noise_tex(nt, P_, 0.4, 4.0)
    n_fine = L.noise_tex(nt, P_, 1.2, 3.0, 0.5)
    z = pos.outputs["Z"]
    # 水色：深處青綠偏暗，牆頂變亮（光穿透）
    h01 = L.math_node(nt, "DIVIDE", L.math_node(nt, "ADD", z, 11.0), 26.0, clamp=True)
    wcol = L.ramp(nt, h01, [(0.0, P.lin("#06232b")), (0.35, P.lin("#0d4a52")), (0.7, P.lin("#1f8f86")), (1.0, P.lin("#8fd6c4"))])
    wcol = L.mix_rgb(nt, wcol, P.lin("#3a7f85"), L.math_node(nt, "MULTIPLY", L.math_node(nt, "SUBTRACT", n_big, 0.5), 0.5, clamp=True))
    # 乾海底：濕沙
    sand = L.mix_rgb(nt, P.lin("#4a3d30"), P.lin("#7a6a54"), n_mid)
    sand = L.mix_rgb(nt, sand, P.lin("#2d2822"), L.math_node(nt, "MULTIPLY", n_fine, 0.35))
    base = L.mix_rgb(nt, sand, wcol, wet)
    base = L.mix_rgb(nt, base, P.lin("#eef3ee"), L.math_node(nt, "MULTIPLY", foam, 0.95, clamp=True))
    if env.get('DBG') == 'foam':
        base = L.mix_rgb(nt, (0, 0, 0), (1, 1, 1), foam)
    elif env.get('DBG') == 'wet':
        base = L.mix_rgb(nt, (0, 0, 0), (1, 1, 1), wet)
    nt.links.new(base, b.inputs["Base Color"])
    # 粗糙度：水面光滑、泡沫粗糙、濕沙微光
    rough = L.math_node(nt, "ADD", L.math_node(nt, "MULTIPLY", foam, 0.7), L.math_node(nt, "ADD", L.math_node(nt, "MULTIPLY", wet, 0.16), L.math_node(nt, "MULTIPLY", L.math_node(nt, "SUBTRACT", 1.0, wet), 0.75)))
    nt.links.new(rough, b.inputs["Roughness"])
    for k, v in (("Specular IOR Level", 0.18), ("Coat Weight", 0.0), ("IOR", 1.12)):
        if k in b.inputs:
            b.inputs[k].default_value = v
    # 水牆自發光（透光）：越高越亮，泡沫少處
    if "Emission Color" in b.inputs:
        b.inputs["Emission Color"].default_value = (0.1, 0.55, 0.5, 1)
        nt.links.new(L.math_node(nt, "MULTIPLY", L.math_node(nt, "MULTIPLY", wet, h01), 0.35), b.inputs["Emission Strength"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.15
    bump.inputs["Distance"].default_value = 0.3
    nt.links.new(L.math_node(nt, "ADD", L.math_node(nt, "MULTIPLY", n_fine, 0.6), L.math_node(nt, "MULTIPLY", n_mid, 0.5)), bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


sea_ob, (SX, SY, SZ) = build_sea()
sea_ob.data.materials.append(sea_material())


# ----------------------------------------------------------------------------- 岸邊沙灘（自建）
def build_beach():
    xs = np.arange(-6.0, 262.0, 3.0)
    ys = np.arange(-800.0, 800.01, 4.0)
    X, Y = np.meshgrid(xs, ys)
    dune = L.fbm2(X, Y, 160.0, 8.0, seed=51)
    z = np.clip(X * 0.016, -0.6, 99) + 0.0
    z = z + (np.clip(X, 0, 400) / 200.0) * (2.5 * dune + 1.2) * L.smoothstep(10, 60, X)
    z += 0.08 * L.fbm2(X, Y, 6.0, 1.0, seed=53)
    # 與 mid 圖層接合：東緣與南北緣 120 m 內漸變到該處地形
    gm = L.Ground([o for o in layers if o.name.endswith("mid")])
    band = 120.0
    dx = np.minimum(262.0 - X, 1e9)
    dy = np.minimum(Y + 800.0, 800.0 - Y)
    d = np.minimum(dx, dy)
    w = 1.0 - L.smoothstep(0.0, band, d)
    sel = np.argwhere(w > 0.01)
    zz = z.copy()
    for (j, i) in sel:
        gz_ = gm.z(float(X[j, i]), float(Y[j, i]), top=3000.0)
        if gz_ is not None:
            zz[j, i] = z[j, i] * (1 - w[j, i]) + gz_ * w[j, i]
    return L.mesh_from_grid("beach", X, Y, zz, {"veg": np.zeros_like(zz), "sea": np.zeros_like(zz)}, None)


beach = build_beach()
beach.data.materials.append(tmat)

ground_objs = [sea_ob, beach]
ground = L.Ground(ground_objs)
gz = ground.z

# ----------------------------------------------------------------------------- 天空與光（黎明在鏡頭後方的東邊）
SUN_AZ = float(env.get("SUNAZ", 7.0))
sky, sunobj, sund = S.world("redsea", SUN_AZ, sun_el=float(env.get("SUNEL", 15.0)))

# ----------------------------------------------------------------------------- 黑暗（第 7 節「中間黑暗了」）
def dark_volume(name, cx, cy, cz, sx, sy, sz, dens, scale):
    bm = bmesh.new()
    L.box_bm((sx, sy, sz), (cx, cy, cz), bm)
    ob = L.mesh_obj(name, bm, None, smooth=False)
    m = L.new_mat(name + "_vol")
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = L.noise_tex(nt, tc.outputs["Object"], scale, 6.0, 0.6)
    nz2 = L.noise_tex(nt, tc.outputs["Object"], scale * 3.3, 3.0, 0.5)
    pv = nt.nodes.new("ShaderNodeVolumePrincipled")
    pv.inputs["Color"].default_value = (0.012, 0.012, 0.02, 1)
    if "Absorption Color" in pv.inputs:
        pv.inputs["Absorption Color"].default_value = (0.02, 0.02, 0.03, 1)
    # 邊緣淡出：橢球狀（由 Generated 座標到中心的距離）
    gen = nt.nodes.new("ShaderNodeTexCoord")
    vm = nt.nodes.new("ShaderNodeVectorMath")
    vm.operation = "SUBTRACT"
    vm.inputs[1].default_value = (0.5, 0.5, 0.5)
    nt.links.new(gen.outputs["Generated"], vm.inputs[0])
    ln = nt.nodes.new("ShaderNodeVectorMath")
    ln.operation = "LENGTH"
    nt.links.new(vm.outputs[0], ln.inputs[0])
    fm = nt.nodes.new("ShaderNodeMapRange")
    fm.interpolation_type = "SMOOTHSTEP"
    fm.inputs["From Min"].default_value = 0.5
    fm.inputs["From Max"].default_value = 0.18
    nt.links.new(ln.outputs["Value"], fm.inputs["Value"])
    fade = fm.outputs["Result"]
    shape = L.math_node(nt, "MULTIPLY", L.math_node(nt, "SUBTRACT", L.math_node(nt, "ADD", L.math_node(nt, "MULTIPLY", nz, 0.7), L.math_node(nt, "MULTIPLY", nz2, 0.3)), 0.32, clamp=True), 2.2, clamp=True)
    nt.links.new(L.math_node(nt, "MULTIPLY", L.math_node(nt, "MULTIPLY", shape, fade), dens), pv.inputs["Density"])
    outn = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(pv.outputs["Volume"], outn.inputs["Volume"])
    ob.data.materials.append(m)
    return ob


if not env.get("NOMASS"):
    dark_volume("darkness_mass", -360.0, 0.0, 120.0, 540.0, 1100.0, 150.0, float(env.get("MASS", 0.012)), 0.012)

# ----------------------------------------------------------------------------- 人群與車馬
fig_meshes = P.build_figure_meshes()
robe_cols = ["#d8cdb0", "#c9b88e", "#9a7b57", "#7a5a3d", "#a3553f", "#b97b45", "#5b6f8a", "#e2d6b6", "#8a7a63", "#6e5a47"]
sheep_m = P.build_sheep()
team_m = P.build_chariot_team(0.8)
team_m2 = P.build_chariot_team(-0.2)
horse_m = P.build_horse(gallop=0.9)
cart_m = P.build_cart()
n_obj = [0]


def uid(p):
    n_obj[0] += 1
    return f"{p}_{n_obj[0]}"


def place(mesh, x, y, yaw, scale=1.0, color=None, z_off=0.0, tilt=(0.0, 0.0), z=None):
    zz = gz(x, y) if z is None else z
    if zz is None:
        return None
    o = L.instance(mesh, uid("o"), (x, y, zz + z_off), rot=(tilt[0], tilt[1], yaw), scale=scale, color=color)
    return o


def lin_col(h):
    return tuple(L.srgb(h))


def person(x, y, heading, k=None, col=None, scale=None):
    k = rnd.randrange(len(fig_meshes)) if k is None else k
    return place(fig_meshes[k], x, y, heading + math.pi / 2 + rnd.uniform(-0.25, 0.25), scale or rnd.uniform(0.95, 1.05), lin_col(col or rnd.choice(robe_cols)))


# 以色列人：從通道（西）往東走上岸，岸上聚成一大片，有人回頭看
CLUSTERS = [(-44, -22), (-36, 10), (-26, -6), (-18, 24), (-48, 24), (-14, -26), (-30, 30), (-52, 0)]
N_HOST = int(env.get("NHOST", 700 if STYLE != 'B' else 260))
for i in range(N_HOST):
    r = rnd.random()
    if r < 0.5:            # 通道內的長隊（往東）：幾個群聚 + 沿中線的人流
        if rnd.random() < 0.65:
            cx, cy = rnd.choice(CLUSTERS)
            x, y = cx + rnd.gauss(0, 5.0), cy + rnd.gauss(0, 6.5)
        else:
            x, y = rnd.uniform(-56.0, -6.0), rnd.gauss(0, 14)
        y = max(-W0 + 4, min(W0 - 4, y))
        person(x, y, rnd.uniform(-0.3, 0.3))
    else:                  # 岸上
        x = (-3.0 + abs(rnd.gauss(0, 6.0))) if STYLE == 'B' else 3.0 + abs(rnd.gauss(0, 40.0))
        y = rnd.gauss(0, 30 if STYLE == 'B' else 34 + 0.25 * x)
        person(x, y, rnd.choice([math.pi, math.pi, 0.0, 0.5, 2.6]) + rnd.uniform(-0.4, 0.4))
for i in range(int(env.get("NSHEEP", 140))):
    x = rnd.uniform(-20, 90)
    y = rnd.gauss(0, 36)
    if x < 0:
        y = max(-W0 + 3, min(W0 - 3, y))
    place(sheep_m, x, y, rnd.uniform(0, 6.28), rnd.uniform(0.9, 1.15), lin_col(rnd.choice(["#e4dcc8", "#cdbf9f", "#8f7a5c", "#d6cdb8"])))
for i in range(int(env.get("NDONKEY", 26))):
    x = rnd.uniform(-20, 80)
    y = rnd.gauss(0, 34)
    if x < 0:
        y = max(-W0 + 4, min(W0 - 4, y))
    place(horse_m, x, y, rnd.uniform(-0.5, 0.5), 0.58, lin_col(rnd.choice(["#7d6b57", "#5f5043", "#9a8872"])))
for i in range(12):
    x = rnd.uniform(-18, 60)
    y = rnd.uniform(-34, 34)
    place(cart_m, x, y, rnd.uniform(-0.3, 0.3), 1.1, lin_col(rnd.choice(["#b8a27a", "#9a8460", "#c4b08a"])))

# 風格 B：幾位寫實人物站在通道口的岸邊，背對鏡頭看著前方
if STYLE == "B":
    heroes = H.build_all(("elder", "woman", "shepherd", "youth", "mother"))
    plan = [("elder", 15.0, -2.5, 180 + 8), ("woman", 13.0, 3.5, 180 - 12), ("shepherd", 17.0, 7.5, 180 + 25),
            ("youth", 11.5, -8.0, 180 - 6), ("mother", 16.5, -11.0, 180 + 30),
            ("elder", 9.5, 11.0, 180 - 20), ("mother", 12.5, 15.0, 180 + 14), ("youth", 19.0, 13.0, 180 + 5), ("woman", 10.0, -14.0, 180 - 30)]
    for kind, x, y, rel in plan:
        z = gz(x, y)
        o = L.instance(heroes[kind], f"hero_{kind}", (x, y, z), rot_z=math.radians(rel) - math.pi / 2, scale=rnd.uniform(0.98, 1.03))
        o.hide_render = False
        o.hide_viewport = False

# 埃及追兵：戰車與騎兵，越遠越被水吞沒（傾斜、半沉）；位置限制在水牆前緣之內
horse_cols = ["#4a3326", "#2f241d", "#6a4a32", "#d6cfc1", "#8a6a4a"]


def wall_front(x):
    cc = float(collapse(np.array([x]), 0.0)[0]) * (1 - float(L.smoothstep(-270.0, -480.0, np.array([x]))[0]))
    return W0 * (1 - 0.94 * cc), cc


def egypt_spot(xmin, xmax):
    x = -rnd.uniform(xmin, xmax)
    wf, cc = wall_front(x)
    y = rnd.uniform(-(wf - 4.0), (wf - 4.0))
    zsurf = float(sea_height(np.array([[x]]), np.array([[y]]))[0][0, 0])
    return x, y, zsurf, cc


N_CHARIOT = int(env.get("NCHARIOT", 40))
for i in range(N_CHARIOT):
    x, y, zsurf, cc = egypt_spot(130, 215)
    sunk = cc > 0.12
    tilt = (rnd.uniform(-0.6, 0.6) * (0.3 + cc), rnd.uniform(-0.4, 0.5) * cc) if sunk else (rnd.uniform(-0.04, 0.04), 0.0)
    zval = (zsurf - 0.5 - 1.6 * cc) if sunk else None
    m = rnd.choice([team_m, team_m2])
    place(m, x, y, rnd.uniform(-0.25, 0.25) + (rnd.uniform(-0.8, 0.8) if sunk else 0), 1.0, lin_col(rnd.choice(horse_cols)), z=zval, tilt=tilt)
for i in range(int(env.get("NCAV", 30))):
    x, y, zsurf, cc = egypt_spot(132, 220)
    zv = (zsurf - 0.5 - 1.3 * cc) if cc > 0.12 else None
    place(horse_m, x, y, rnd.uniform(-0.4, 0.4) + (rnd.uniform(-0.9, 0.9) if cc > 0.12 else 0), 1.0, lin_col(rnd.choice(horse_cols)), z=zv, tilt=(rnd.uniform(-0.5, 0.5) * cc, rnd.uniform(-0.4, 0.4) * cc))
for i in range(int(env.get("NFOOT", 110))):
    x, y, zsurf, cc = egypt_spot(134, 185)
    if cc > 0.25:
        continue
    person(x, y, rnd.uniform(-0.3, 0.3), col=rnd.choice(["#3b3a46", "#6b5a3a", "#a09074"]), scale=rnd.uniform(0.95, 1.05))

# ----------------------------------------------------------------------------- 浪花（水牆崩落處的白色水沫團）
spray_mat = L.pbr("spray", "#f1f5f2", 0.9)
_b = L.bsdf_of(spray_mat)
_b.inputs["Emission Color"].default_value = (0.9, 0.95, 0.95, 1)
_b.inputs["Emission Strength"].default_value = 0.6
spray_m = bpy.data.meshes.new("spray")
bm = bmesh.new()
L.sphere_bm(1.0, (0, 0, 0), (1, 1, 0.8), 1, bm, noise=0.3, seed=2)
bm.to_mesh(spray_m)
bm.free()
spray_m.materials.append(spray_mat)
for p in spray_m.polygons:
    p.use_smooth = True
ns = 0
for _ in range(int(env.get("NSPRAY", 0))):
    x = -rnd.uniform(60, 240)
    c = float(L.smoothstep(c_start, c_end, np.array([x]))[0])
    side = rnd.choice([-1, 1])
    yf = W0 * (1 - 0.94 * c)
    y = side * (yf + rnd.uniform(-6, 18) * (0.4 + c)) if rnd.random() < 0.7 else rnd.uniform(-W0, W0)
    zsurf = float(sea_height(np.array([[x]]), np.array([[y]]))[0][0, 0])
    z = zsurf + rnd.uniform(0.0, 5.0 + 9.0 * c)
    r = rnd.uniform(0.25, 0.9) * (0.6 + c)
    L.instance(spray_m, f"spray_{ns}", (x, y, z), rot_z=rnd.uniform(0, 6.28), scale=r)
    ns += 1

# ----------------------------------------------------------------------------- 相機
CAMX, CAMY = float(env.get("CAMX", 22)), float(env.get("CAMY", -4))
CAMZ = float(env.get("CAMZ", 22 if STYLE != "B" else 5))
TGT = (float(env.get("TGTX", -105)), float(env.get("TGTY", 0)), float(env.get("TGTZ", -2)))
cam = L.set_camera((CAMX, CAMY, CAMZ), TGT, lens=float(env.get("LENS", 30)))
L.render_settings(a.w, a.h, a.samples)
base = a.out[:-4] if a.out.endswith(".png") else a.out
t = L.render_pair(base, sun_dir=sund)
print("names", len(L.check_names()), "times", t, "sea verts", SX.size)
