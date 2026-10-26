"""《至於我和我家》場景道具模型建置腳本（Blender 5.2 背景模式）。

在專屬場景 `jos24_props_build` 建模，匯出：
- src/assets/models/props.glb（use_active_scene=True）
- lab/renders/props_sheet.png（1600x900 全尺寸檢查圖）

物件命名契約（對齊 src/scene/props.ts）：
- prop_tabor_oak：泰博橡樹（Quercus ithaburensis，低矮粗壯分枝樹幹＋oak_leaf_00..15 多層深橄欖綠樹冠團）
- prop_witness_stone：基色（Gezer）式天然未鑿刻石灰岩立石（原點在底部 (0,0,0)，高 2.38m，躺與立共用同一網格，無刻字）
- prop_joseph_coffin：約瑟的木棺（創50:26；書24:32，香柏木與青銅包角棺身＋雙抬槓）
- prop_scroll_table：寫律法書的木案與雙軸攤開羊皮卷（書24:26a）
"""

import math
import os
import random
import sys
import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
from glb_writer import export_selected_glb

SCENE = "jos24_props_build"
PROJECT_ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT_GLB = os.path.join(PROJECT_ROOT, "src", "assets", "models", "props.glb")
OUT_PNG = os.path.join(PROJECT_ROOT, "lab", "renders", "props_sheet.png")

os.makedirs(os.path.dirname(OUT_GLB), exist_ok=True)
os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)

if SCENE in bpy.data.scenes:
    old = bpy.data.scenes[SCENE]
    for o in list(old.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.scenes.remove(old)

sc = bpy.data.scenes.new(SCENE)
bpy.context.window.scene = sc

for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
    for d in list(coll):
        if d.users == 0:
            coll.remove(d)

MATS = {}


def srgb_to_lin(hex_col: str):
    c = tuple(int(hex_col[i : i + 2], 16) / 255.0 for i in (1, 3, 5))
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c)


def mat(name: str, hex_col: str, rough: float = 0.85, metal: float = 0.0):
    if name in MATS:
        return MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    lin = srgb_to_lin(hex_col)
    bsdf.inputs["Base Color"].default_value = (*lin, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    m.diffuse_color = (*lin, 1.0)
    MATS[name] = m
    return m


def obj_from_bm(name: str, bm: bmesh.types.BMesh, material, smooth: bool = True):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = smooth
    o = bpy.data.objects.new(name, me)
    sc.collection.objects.link(o)
    o.data.materials.append(material)
    return o


def join_parts(name: str, parts, origin=(0.0, 0.0, 0.0)):
    for o in bpy.context.selected_objects:
        o.select_set(False)
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active
    o.name = name
    o.data.name = name
    off = Vector(origin)
    o.data.transform(Matrix.Translation(-off))
    o.location = off
    return o


def make_tube_along_points(name: str, pts, radii, material, seg: int = 10):
    """沿三維折線擠出扭轉樹幹／大枝"""
    bm = bmesh.new()
    rings = []
    for idx, pt in enumerate(pts):
        p = Vector(pt)
        if idx == 0:
            tangent = (Vector(pts[1]) - p).normalized()
        elif idx == len(pts) - 1:
            tangent = (p - Vector(pts[-2])).normalized()
        else:
            tangent = (Vector(pts[idx + 1]) - Vector(pts[idx - 1])).normalized()

        ref = Vector((1.0, 0.0, 0.0)) if abs(tangent.x) < 0.85 else Vector((0.0, 1.0, 0.0))
        u = tangent.cross(ref).normalized()
        v = tangent.cross(u).normalized()
        r = radii[idx]
        ring = []
        for s in range(seg):
            a = 2.0 * math.pi * s / seg + idx * 0.22
            bark_groove = 1.0 + 0.09 * math.sin(s * 3.0 + idx * 1.3)
            pos = p + (u * math.cos(a) + v * math.sin(a)) * (r * bark_groove)
            ring.append(bm.verts.new(pos))
        rings.append(ring)

    for k in range(len(rings) - 1):
        for s in range(seg):
            sn = (s + 1) % seg
            bm.faces.new((rings[k][s], rings[k][sn], rings[k + 1][sn], rings[k + 1][s]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm(name, bm, material, smooth=True)


# ---------------------------------------------------------------- 1. 泰博橡樹 (prop_tabor_oak)
def build_tabor_oak(x_offset: float):
    bark_m = mat("oak_bark", "#4b3b2c", 0.95)
    leaf_mats = [
        mat("oak_leaf_mid", "#3d4a30", 0.88),
        mat("oak_leaf_sun", "#4d5c3c", 0.85),
        mat("oak_leaf_deep", "#2f3a24", 0.90),
    ]

    oak_root = bpy.data.objects.new("prop_tabor_oak", None)
    sc.collection.objects.link(oak_root)

    wood_parts = []
    # 主幹：盤根寬底座，微傾扭轉上升至 2.2m 分枝（對照霍爾山泰博橡樹參考照）
    wood_parts.append(
        make_tube_along_points(
            "oak_trunk_main",
            [(0.0, 0.0, -0.05), (0.04, -0.03, 0.65), (-0.06, 0.05, 1.45), (0.02, 0.02, 2.25)],
            [0.72, 0.50, 0.43, 0.36],
            bark_m,
            seg=12,
        )
    )
    # 盤根隆起
    for r_idx in range(4):
        ang = r_idx * math.pi * 0.5 + 0.35
        dx, dy = math.cos(ang), math.sin(ang)
        wood_parts.append(
            make_tube_along_points(
                f"oak_root_{r_idx}",
                [(dx * 0.35, dy * 0.35, 0.38), (dx * 0.78, dy * 0.78, 0.08), (dx * 1.15, dy * 1.15, -0.04)],
                [0.22, 0.15, 0.07],
                bark_m,
                seg=8,
            )
        )

    # 五條大主枝向四面水平舒展成寬傘骨架
    bough_specs = [
        [(0.02, 0.02, 2.05), (-1.15, -0.45, 2.95), (-2.35, -0.82, 3.65)],
        [(0.02, 0.02, 2.10), (1.20, -0.35, 3.00), (2.42, -0.68, 3.72)],
        [(0.02, 0.02, 2.15), (-0.85, 1.05, 3.12), (-1.85, 1.95, 3.85)],
        [(0.02, 0.02, 2.15), (0.95, 1.08, 3.08), (1.98, 1.92, 3.78)],
        [(0.02, 0.02, 2.20), (0.05, -0.15, 3.45), (0.12, 0.08, 4.55)],
    ]
    for b_idx, b_pts in enumerate(bough_specs):
        wood_parts.append(
            make_tube_along_points(f"oak_bough_{b_idx}", b_pts, [0.27, 0.18, 0.09], bark_m, seg=9)
        )

    trunk_joined = join_parts("oak_trunk_joined", wood_parts, origin=(0.0, 0.0, 0.0))
    trunk_joined.parent = oak_root

    # 16 團有機多面體樹冠（獨立命名 oak_leaf_00..15，供前端隨山風微幅擺動）
    rng = random.Random(2426)
    canopy_blobs = [
        (0.0, 0.0, 4.95, 1.85, 1.75, 1.05, 1),
        (-1.65, -0.65, 4.05, 1.55, 1.45, 0.92, 0),
        (1.75, -0.55, 4.10, 1.55, 1.45, 0.92, 1),
        (-1.45, 1.45, 4.15, 1.50, 1.45, 0.90, 2),
        (1.55, 1.42, 4.12, 1.50, 1.45, 0.90, 0),
        (-2.55, -0.85, 3.62, 1.22, 1.18, 0.78, 2),
        (2.62, -0.72, 3.68, 1.24, 1.18, 0.78, 0),
        (-2.10, 2.05, 3.75, 1.18, 1.15, 0.76, 2),
        (2.15, 1.98, 3.72, 1.20, 1.15, 0.76, 1),
        (0.05, -1.85, 3.92, 1.38, 1.25, 0.84, 1),
        (-0.10, 2.15, 4.02, 1.42, 1.28, 0.85, 2),
        (-1.05, -0.15, 4.68, 1.42, 1.35, 0.88, 1),
        (1.10, 0.15, 4.65, 1.42, 1.35, 0.88, 1),
        (-2.35, 0.55, 3.78, 1.18, 1.15, 0.75, 0),
        (2.38, 0.62, 3.80, 1.18, 1.15, 0.75, 2),
        (0.0, 0.15, 5.48, 1.35, 1.30, 0.82, 1),
    ]
    for idx, (lx, ly, lz, sx, sy, sz, m_idx) in enumerate(canopy_blobs):
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
        for v in bm.verts:
            n = 1.0 + 0.14 * math.sin(v.co.x * 3.7 + idx) + 0.10 * math.cos(v.co.y * 4.1 - v.co.z * 2.9)
            v.co.x *= sx * n
            v.co.y *= sy * n
            v.co.z *= sz * (0.92 + 0.12 * rng.random())
        leaf_obj = obj_from_bm(f"oak_leaf_{idx:02d}", bm, leaf_mats[m_idx], smooth=False)
        leaf_obj.location = (lx, ly, lz)
        leaf_obj.parent = oak_root

    oak_root.location = (x_offset, 0.0, 0.0)
    return oak_root


# ---------------------------------------------------------------- 2. 見證的大石頭 (prop_witness_stone)
def build_witness_stone(x_offset: float):
    """基色（Gezer）式天然未鑿刻石灰岩巨石：原點在底部 (0,0,0)，高 2.38m，絕不刻任何文字或符號"""
    stone_m = mat("limestone_monolith", "#cfc2a8", 0.94)
    bm = bmesh.new()
    # 以高密度分段圓柱變形為扁長方圓頂天然石碑（Blender Z 向上 = glTF Y 向上）
    seg_u = 18
    seg_z = 12
    height = 2.38
    rings = []
    for kz in range(seg_z + 1):
        t = kz / seg_z
        z = t * height
        # 下寬上略收，頂端圓拱（對照 Gezer 1號立石參考照）
        taper = 1.0 - 0.18 * t
        crown = math.sqrt(max(0.04, 1.0 - ((t - 0.82) / 0.18) ** 2)) if t > 0.82 else 1.0
        rx = 0.48 * taper * (0.35 + 0.65 * crown)
        ry = 0.27 * taper * (0.40 + 0.60 * crown)
        ring = []
        for ku in range(seg_u):
            a = 2.0 * math.pi * ku / seg_u
            # 正背面略平（超橢圓截面）＋天然風化凹凸，不刻任何字
            ca, sa = math.cos(a), math.sin(a)
            sx = math.copysign(abs(ca) ** 0.78, ca) * rx
            sy = math.copysign(abs(sa) ** 0.82, sa) * ry
            pit = (
                0.022 * math.sin(z * 4.3 + a * 3.0)
                + 0.015 * math.cos(z * 7.1 - a * 2.0)
                + 0.010 * math.sin(z * 11.0 + a * 5.0)
            )
            ring.append(bm.verts.new((sx + ca * pit, sy + sa * pit * 0.7, z)))
        rings.append(ring)

    for kz in range(seg_z):
        for ku in range(seg_u):
            kn = (ku + 1) % seg_u
            bm.faces.new((rings[kz][ku], rings[kz][kn], rings[kz + 1][kn], rings[kz + 1][ku]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    stone_obj = obj_from_bm("prop_witness_stone", bm, stone_m, smooth=False)
    stone_obj.location = (x_offset, 0.0, 0.0)
    return stone_obj


# ---------------------------------------------------------------- 3. 約瑟的木棺 (prop_joseph_coffin)
def build_joseph_coffin(x_offset: float):
    cedar_m = mat("coffin_cedar", "#6d4c31", 0.84)
    trim_m = mat("coffin_ochre", "#b68846", 0.68)
    pole_m = mat("coffin_pole", "#523924", 0.90)

    parts = []
    # 棺身（長 1.78m、寬 0.56m、高 0.46m，底部在 Z=0.06）
    bm_box = bmesh.new()
    bmesh.ops.create_cube(bm_box, size=1.0)
    bmesh.ops.scale(bm_box, vec=(1.78, 0.56, 0.46), verts=bm_box.verts)
    bmesh.ops.translate(bm_box, vec=(0.0, 0.0, 0.29), verts=bm_box.verts)
    parts.append(obj_from_bm("coffin_body", bm_box, cedar_m, smooth=False))

    # 斜面微拱棺蓋
    bm_lid = bmesh.new()
    bmesh.ops.create_cube(bm_lid, size=1.0)
    for v in bm_lid.verts:
        if v.co.z > 0:
            v.co.x *= 0.92
            v.co.y *= 0.80
    bmesh.ops.scale(bm_lid, vec=(1.84, 0.60, 0.16), verts=bm_lid.verts)
    bmesh.ops.translate(bm_lid, vec=(0.0, 0.0, 0.59), verts=bm_lid.verts)
    parts.append(obj_from_bm("coffin_lid", bm_lid, cedar_m, smooth=False))

    # 三道橫向金赭木箍
    for bx in (-0.62, 0.0, 0.62):
        bm_b = bmesh.new()
        bmesh.ops.create_cube(bm_b, size=1.0)
        bmesh.ops.scale(bm_b, vec=(0.06, 0.59, 0.49), verts=bm_b.verts)
        bmesh.ops.translate(bm_b, vec=(bx, 0.0, 0.29), verts=bm_b.verts)
        parts.append(obj_from_bm(f"coffin_band_{bx:+.2f}", bm_b, trim_m, smooth=False))

    # 兩側長抬槓（長 2.68m）
    for sy_idx, sy in enumerate((-0.34, 0.34)):
        bm_p = bmesh.new()
        bmesh.ops.create_cone(bm_p, cap_ends=True, segments=10, radius1=0.032, radius2=0.032, depth=2.68)
        bmesh.ops.rotate(bm_p, verts=bm_p.verts, matrix=Matrix.Rotation(math.pi * 0.5, 3, "Y"))
        bmesh.ops.translate(bm_p, vec=(0.0, sy, 0.16), verts=bm_p.verts)
        parts.append(obj_from_bm(f"coffin_pole_{sy_idx}", bm_p, pole_m, smooth=True))

    coffin = join_parts("prop_joseph_coffin", parts, origin=(0.0, 0.0, 0.0))
    coffin.location = (x_offset, 0.0, 0.0)
    return coffin


# ---------------------------------------------------------------- 4. 木案與雙卷軸羊皮卷 (prop_scroll_table)
def build_scroll_table(x_offset: float):
    wood_m = mat("table_acacia", "#6b4b30", 0.86)
    parch_m = mat("scroll_parchment", "#ede0c2", 0.78)
    edge_m = mat("scroll_edge", "#c9b38c", 0.84)

    parts = []
    tilt = 0.16
    rot_m = Matrix.Rotation(-tilt, 3, "X")

    # 桌面（微向鏡頭前傾）
    bm_top = bmesh.new()
    bmesh.ops.create_cube(bm_top, size=1.0)
    bmesh.ops.scale(bm_top, vec=(1.08, 0.68, 0.055), verts=bm_top.verts)
    bmesh.ops.rotate(bm_top, verts=bm_top.verts, matrix=rot_m)
    bmesh.ops.translate(bm_top, vec=(0.0, 0.0, 0.92), verts=bm_top.verts)
    parts.append(obj_from_bm("table_top", bm_top, wood_m, smooth=False))

    # 四腳與橫棖
    for idx, (lx, ly) in enumerate([(-0.45, -0.26), (0.45, -0.26), (-0.45, 0.26), (0.45, 0.26)]):
        bm_leg = bmesh.new()
        bmesh.ops.create_cone(bm_leg, cap_ends=True, segments=8, radius1=0.04, radius2=0.034, depth=0.90)
        bmesh.ops.translate(bm_leg, vec=(lx, ly, 0.45), verts=bm_leg.verts)
        parts.append(obj_from_bm(f"table_leg_{idx}", bm_leg, wood_m, smooth=True))

    # 攤開的羊皮卷中頁
    bm_sheet = bmesh.new()
    bmesh.ops.create_cube(bm_sheet, size=1.0)
    bmesh.ops.scale(bm_sheet, vec=(0.74, 0.46, 0.012), verts=bm_sheet.verts)
    bmesh.ops.rotate(bm_sheet, verts=bm_sheet.verts, matrix=rot_m)
    bmesh.ops.translate(bm_sheet, vec=(0.0, 0.0, 0.958), verts=bm_sheet.verts)
    parts.append(obj_from_bm("scroll_sheet", bm_sheet, parch_m, smooth=False))

    # 左右兩側多層皮卷圓筒與木軸頭（對照 02-rolled-edges-parchment.jpg）
    for r_idx, rx in enumerate((-0.38, 0.38)):
        bm_roll = bmesh.new()
        bmesh.ops.create_cone(bm_roll, cap_ends=True, segments=16, radius1=0.044, radius2=0.044, depth=0.50)
        bmesh.ops.rotate(bm_roll, verts=bm_roll.verts, matrix=Matrix.Rotation(math.pi * 0.5, 3, "X"))
        bmesh.ops.rotate(bm_roll, verts=bm_roll.verts, matrix=rot_m)
        bmesh.ops.translate(bm_roll, vec=(rx, 0.0, 0.985), verts=bm_roll.verts)
        parts.append(obj_from_bm(f"scroll_roll_{r_idx}", bm_roll, edge_m, smooth=True))

        bm_spindle = bmesh.new()
        bmesh.ops.create_cone(bm_spindle, cap_ends=True, segments=10, radius1=0.018, radius2=0.018, depth=0.60)
        bmesh.ops.rotate(bm_spindle, verts=bm_spindle.verts, matrix=Matrix.Rotation(math.pi * 0.5, 3, "X"))
        bmesh.ops.rotate(bm_spindle, verts=bm_spindle.verts, matrix=rot_m)
        bmesh.ops.translate(bm_spindle, vec=(rx, 0.0, 0.985), verts=bm_spindle.verts)
        parts.append(obj_from_bm(f"scroll_spindle_{r_idx}", bm_spindle, wood_m, smooth=True))

    tbl = join_parts("prop_scroll_table", parts, origin=(0.0, 0.0, 0.0))
    tbl.location = (x_offset, 0.0, 0.0)
    return tbl


oak_o = build_tabor_oak(-4.2)
stone_o = build_witness_stone(0.8)
coffin_o = build_joseph_coffin(3.5)
table_o = build_scroll_table(6.2)

bad_names = [o.name for o in sc.objects if ".00" in o.name]
if bad_names:
    raise RuntimeError(f"Object name collision detected: {bad_names}")

# 將四件道具暫歸回原點後匯出？注意：匯出時保留各自父物件局部座標即可（props.ts 會把 cloned.position 設為 (0,0,0)！）
# 但對 join_parts 建立的單一網格物件（stone_o, coffin_o, table_o），export_apply=True 若不先移回 (0,0,0) 會不會把 location 烤進頂點？
# 重要細節：gltf exporter 預設保留物件 TRS，three.js 讀入後 c.position 會在 x_offset，props.ts 執行 cloned.position.set(0,0,0) 即精準歸零！
for o in bpy.context.selected_objects:
    o.select_set(False)
for o in sc.objects:
    if (
        o.name.startswith("prop_")
        or (o.parent and o.parent.name.startswith("prop_"))
    ):
        o.select_set(True)

try:
    bpy.ops.export_scene.gltf(
        filepath=OUT_GLB,
        export_format="GLB",
        use_selection=True,
        use_active_scene=True,
        export_apply=True,
        export_yup=True,
        export_cameras=False,
        export_lights=False,
    )
except Exception as exc:
    print(f"[props.glb] io_scene_gltf2 unavailable ({exc}), using glb_writer fallback")
    export_selected_glb(sc, OUT_GLB)

print(f"[props.glb] exported size = {os.path.getsize(OUT_GLB)} bytes")

# 渲染 1600x900 全尺寸檢查圖
ground_bm = bmesh.new()
bmesh.ops.create_grid(ground_bm, x_segments=2, y_segments=2, size=24.0)
ground = obj_from_bm("prev_ground", ground_bm, mat("prev_ground_m", "#dfd5c0", 0.95), smooth=False)
ground.location = (1.0, 0.0, 0.0)

sun = bpy.data.objects.new("prev_sun", bpy.data.lights.new("prev_sun", "SUN"))
sun.data.energy = 3.8
sun.rotation_euler = (math.radians(50), 0.0, math.radians(-32))
sc.collection.objects.link(sun)

fill = bpy.data.objects.new("prev_fill", bpy.data.lights.new("prev_fill", "SUN"))
fill.data.energy = 1.2
fill.rotation_euler = (math.radians(65), 0.0, math.radians(145))
sc.collection.objects.link(fill)

cam = bpy.data.objects.new("prev_cam", bpy.data.cameras.new("prev_cam"))
cam.location = (0.6, -16.8, 3.35)
cam.rotation_euler = (math.radians(83.5), 0.0, 0.0)
cam.data.lens = 28
sc.collection.objects.link(cam)
sc.camera = cam

world = bpy.data.worlds.new("prev_world")
world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs[0].default_value = (*srgb_to_lin("#e8e0cf"), 1.0)
bg.inputs[1].default_value = 0.88
sc.world = world

sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items.keys() else "CYCLES"
if sc.render.engine == "CYCLES":
    sc.cycles.samples = 24
sc.render.resolution_x = 1600
sc.render.resolution_y = 900
sc.render.filepath = OUT_PNG
bpy.ops.render.render(write_still=True)
print(f"[props_sheet.png] rendered ({os.path.getsize(OUT_PNG)} bytes)")
