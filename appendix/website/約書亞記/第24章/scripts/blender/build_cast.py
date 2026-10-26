"""《至於我和我家》人物與群眾模型建置腳本（Blender 5.2 背景模式）。

在專屬場景 `jos24_cast_build` 建模，匯出：
- src/assets/models/cast.glb（use_active_scene=True）
- lab/renders/cast_sheet.png（1600x900 全尺寸檢查圖）

角色節點命名契約（對齊 src/scene/actors.ts）：
- fig_joshua（年邁約書亞：白長鬚、披肩外袍、無光環）
- fig_grandfather（爺爺：花白鬍鬚、風霜外袍）
- fig_father（父親：曠野世代、深褐袍與赭石腰帶）
- fig_mother（母親：赭紅長袍與頭巾）
- fig_daughter（女兒：迦南出生孩童比例、髮辮）
- fig_daughter_grown（第六幕長大的女兒：少女高挑比例、延續同色系衣袍與長巾）
- fig_jacob（創35 雅各：牧人外披與深褐鬚）
- fig_elder（支派長老：織紋滾邊袍、灰白鬚）
- crowd_silhouette（12 支派群眾 InstancedMesh 專用單一網格，高 1.70m，白色基底供 instanceColor 著色）
"""

import math
import os
import sys
import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
from glb_writer import export_selected_glb

SCENE = "jos24_cast_build"
PROJECT_ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT_GLB = os.path.join(PROJECT_ROOT, "src", "assets", "models", "cast.glb")
OUT_PNG = os.path.join(PROJECT_ROOT, "lab", "renders", "cast_sheet.png")

os.makedirs(os.path.dirname(OUT_GLB), exist_ok=True)
os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)

# 只在自己的場景 `jos24_cast_build` 操作，絕不動到其他場景
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


def mat(name: str, hex_col: str, rough: float = 0.78):
    if name in MATS:
        return MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    lin = srgb_to_lin(hex_col)
    bsdf.inputs["Base Color"].default_value = (*lin, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    m.diffuse_color = (*lin, 1.0)
    MATS[name] = m
    return m


def obj_from_bm(name: str, bm: bmesh.types.BMesh, material):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    sc.collection.objects.link(o)
    o.data.materials.append(material)
    return o


def lathe(
    name: str,
    prof,
    material,
    seg: int = 24,
    cap_top: bool = False,
    scale=(1.0, 1.0, 1.0),
    loc=(0.0, 0.0, 0.0),
    arc=None,
    cap_bottom: bool = False,
):
    bm = bmesh.new()
    rings = []
    closed = arc is None
    n = seg if closed else seg + 1
    for r, z in prof:
        ring = []
        for i in range(n):
            a = (
                2.0 * math.pi * i / seg
                if closed
                else math.radians(arc[0] + (arc[1] - arc[0]) * i / seg)
            )
            ring.append(
                bm.verts.new(
                    (
                        r * math.cos(a) * scale[0] + loc[0],
                        r * math.sin(a) * scale[1] + loc[1],
                        z * scale[2] + loc[2],
                    )
                )
            )
        rings.append(ring)
    for k in range(len(rings) - 1):
        for i in range(seg):
            j = (i + 1) % n
            bm.faces.new((rings[k][i], rings[k][j], rings[k + 1][j], rings[k + 1][i]))
    if cap_top and closed:
        bm.faces.new(list(reversed(rings[-1])))
    if cap_bottom and closed:
        bm.faces.new(list(reversed(rings[0])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm(name, bm, material)


def sphere(
    name: str,
    r: float,
    loc,
    material,
    scale=(1.0, 1.0, 1.0),
    seg: int = 18,
    rings: int = 12,
    cut=None,
    face=None,
):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=r)
    if cut is not None:
        dead = [v for v in bm.verts if v.co.z < cut * r - 1e-6]
        bmesh.ops.delete(bm, geom=dead, context="VERTS")
    if face is not None:
        dead = [v for v in bm.verts if v.co.y < -0.3 * r and v.co.z < face * r]
        bmesh.ops.delete(bm, geom=dead, context="VERTS")
    bmesh.ops.scale(bm, vec=scale, verts=bm.verts)
    bmesh.ops.translate(bm, vec=loc, verts=bm.verts)
    return obj_from_bm(name, bm, material)


def cyl(name: str, r1: float, r2: float, h: float, loc, material, seg: int = 18, rot=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r1, radius2=r2, depth=h)
    if rot:
        bmesh.ops.rotate(bm, verts=bm.verts, matrix=Matrix.Rotation(rot[1], 3, rot[0]))
    bmesh.ops.translate(bm, vec=loc, verts=bm.verts)
    return obj_from_bm(name, bm, material)


def torus(name: str, R: float, r: float, loc, material, scale=(1.0, 1.0, 1.0), seg: int = 24, tseg: int = 8):
    bm = bmesh.new()
    for i in range(seg):
        a = 2.0 * math.pi * i / seg
        for k in range(tseg):
            b = 2.0 * math.pi * k / tseg
            bm.verts.new(
                (
                    (R + r * math.cos(b)) * math.cos(a),
                    (R + r * math.cos(b)) * math.sin(a),
                    r * math.sin(b),
                )
            )
    bm.verts.ensure_lookup_table()
    for i in range(seg):
        for k in range(tseg):
            a = i * tseg + k
            b = ((i + 1) % seg) * tseg + k
            c = ((i + 1) % seg) * tseg + (k + 1) % tseg
            d = i * tseg + (k + 1) % tseg
            bm.faces.new((bm.verts[a], bm.verts[b], bm.verts[c], bm.verts[d]))
    bmesh.ops.scale(bm, vec=scale, verts=bm.verts)
    bmesh.ops.translate(bm, vec=loc, verts=bm.verts)
    return obj_from_bm(name, bm, material)


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


SKIN = mat("skin", "#c8966c", 0.62)
SKIN_AGED = mat("skin_aged", "#bc8b63", 0.68)
SKIN_SHADE = mat("skin_shade", "#a57350", 0.62)
EYE = mat("eye", "#22170f", 0.35)
BLUSH = mat("blush", "#d68a78", 0.72)
HAIR_DARK = mat("hair_dark", "#2d2017", 0.85)

CAST_SPECS = [
    (
        "joshua",
        dict(
            robe="#3f4d5e",
            hem="#293440",
            sash="#a66b38",
            head="#e8e0cf",
            band="#5c432c",
            mantle="#6b563e",
            beard="#dfd9cc",
            long_beard=True,
            aged=True,
        ),
    ),
    (
        "grandfather",
        dict(
            robe="#786650",
            hem="#544636",
            sash="#9c7a4c",
            head="#ddd3be",
            band="#4a3928",
            mantle="#5e503f",
            beard="#b8b0a2",
            long_beard=False,
            aged=True,
        ),
    ),
    (
        "father",
        dict(
            robe="#6f5236",
            hem="#4a3523",
            sash="#a8743a",
            head="#d9cba8",
            band="#3a2a1e",
            beard="#3d2b1e",
        ),
    ),
    (
        "mother",
        dict(
            robe="#8e4b3c",
            hem="#5f2e25",
            sash="#d2a24c",
            head="#c9a46e",
            scarf=True,
        ),
    ),
    (
        "daughter",
        dict(
            robe="#b58a4f",
            hem="#8a6233",
            sash="#9e3b2e",
            head="#e3cd9e",
            child=True,
        ),
    ),
    (
        "daughter_grown",
        dict(
            robe="#b58a4f",
            hem="#8a6233",
            sash="#9e3b2e",
            head="#e3cd9e",
            scarf=True,
            young_woman=True,
        ),
    ),
    (
        "jacob",
        dict(
            robe="#6c5840",
            hem="#493a28",
            sash="#8f6239",
            head="#dfd3bc",
            band="#3f2e1f",
            mantle="#7d6447",
            beard="#4a3828",
        ),
    ),
    (
        "elder",
        dict(
            robe="#5c5346",
            hem="#3d362d",
            sash="#8f6d43",
            head="#ded5c3",
            band="#4a3b2a",
            mantle="#756856",
            beard="#9e9689",
        ),
    ),
]


def build_figure(id_: str, cfg: dict, x_pos: float):
    robe_m = mat(f"robe_{id_}", cfg["robe"], 0.86)
    hem_m = mat(f"hem_{id_}", cfg["hem"], 0.9)
    sash_m = mat(f"sash_{id_}", cfg["sash"], 0.72)
    head_m = mat(f"head_{id_}", cfg["head"], 0.88)
    skin_m = SKIN_AGED if cfg.get("aged") else SKIN

    child = bool(cfg.get("child"))
    yw = bool(cfg.get("young_woman"))

    parts = []
    if child:
        prof = [
            (0.84, 0.0),
            (0.82, 0.12),
            (0.74, 0.72),
            (0.61, 1.5),
            (0.55, 2.02),
            (0.53, 2.48),
            (0.46, 2.76),
            (0.29, 2.91),
            (0.0, 2.94),
        ]
    elif yw:
        prof = [
            (0.91, 0.0),
            (0.89, 0.14),
            (0.79, 0.82),
            (0.63, 1.72),
            (0.54, 2.08),
            (0.56, 2.46),
            (0.54, 2.72),
            (0.38, 2.91),
            (0.18, 3.0),
            (0.0, 3.02),
        ]
    else:
        prof = [
            (0.98, 0.0),
            (0.96, 0.12),
            (0.86, 0.8),
            (0.7, 1.7),
            (0.6, 2.05),
            (0.63, 2.46),
            (0.61, 2.74),
            (0.42, 2.93),
            (0.2, 3.02),
            (0.0, 3.04),
        ]

    parts.append(lathe(f"{id_}_robe", prof, robe_m, cap_bottom=True))

    # 迦南／黎凡特織紋下擺雙滾邊
    hem_r = prof[1][0]
    parts.append(
        lathe(
            f"{id_}_hem",
            [(hem_r + 0.012, 0.0), (hem_r + 0.016, 0.11), (hem_r - 0.018, 0.27)],
            hem_m,
        )
    )
    parts.append(
        torus(f"{id_}_hemtrim", hem_r - 0.01, 0.018, (0, 0, 0.31), sash_m, seg=24, tseg=6)
    )

    # 外披肩袍（約書亞、爺爺、雅各、長老）
    if cfg.get("mantle"):
        mantle_m = mat(f"mantle_{id_}", cfg["mantle"], 0.88)
        parts.append(
            lathe(
                f"{id_}_mantle",
                [(0.89, 0.55), (0.82, 1.45), (0.72, 2.25), (0.68, 2.76), (0.48, 2.95)],
                mantle_m,
                arc=(-42, 222),
            )
        )

    # 腰帶與垂帶
    wz = 1.75 if child else (1.98 if yw else 1.95)
    wr = 0.57 if child else (0.56 if yw else 0.62)
    parts.append(torus(f"{id_}_sash", wr, 0.068, (0, 0, wz), sash_m, scale=(1.0, 1.0, 1.38)))
    tail = cyl(f"{id_}_sashend", 0.065, 0.088, 0.68, (-0.27, -0.53, wz - 0.36), sash_m, seg=8)
    tail.rotation_euler = (0.12, 0.0, 0.0)
    parts.append(tail)

    # 頸與頭
    hz = 3.34 if child else 3.45
    hr = 0.54 if child else (0.45 if yw else 0.47)
    parts.append(cyl(f"{id_}_neck", 0.16, 0.18, 0.3, (0, 0, hz - hr - 0.02), skin_m, seg=12))
    parts.append(
        sphere(f"{id_}_head", hr, (0, 0, hz), skin_m, scale=(0.94, 0.94, 1.04), seg=22, rings=14)
    )

    # 五官與眉目
    fy = -hr * 0.92
    for s in (1, -1):
        parts.append(
            sphere(
                f"{id_}_eye{'L' if s > 0 else 'R'}",
                0.062 if child else 0.054,
                (s * hr * 0.33, fy, hz + 0.05),
                EYE,
                seg=10,
                rings=8,
                scale=(1.0, 0.6, 1.25),
            )
        )
        if cfg.get("aged"):
            brow_m = mat(f"beard_{id_}", cfg["beard"], 0.9)
            parts.append(
                sphere(
                    f"{id_}_brow{'L' if s > 0 else 'R'}",
                    0.06,
                    (s * hr * 0.33, fy - 0.01, hz + 0.15),
                    brow_m,
                    seg=8,
                    rings=6,
                    scale=(1.6, 0.55, 0.5),
                )
            )
        elif not cfg.get("beard"):
            parts.append(
                sphere(
                    f"{id_}_cheek{'L' if s > 0 else 'R'}",
                    0.075,
                    (s * hr * 0.48, fy * 0.93, hz - 0.11),
                    BLUSH,
                    seg=10,
                    rings=8,
                    scale=(1.2, 0.4, 0.8),
                )
            )

    parts.append(
        sphere(
            f"{id_}_nose",
            0.068,
            (0, fy - 0.03, hz - 0.06),
            SKIN_SHADE,
            seg=10,
            rings=8,
            scale=(0.8, 0.9, 1.1),
        )
    )

    # 鬍鬚（約書亞為垂胸長白鬚，爺爺／長老為花白鬚，父親／雅各為深褐鬚）
    if cfg.get("beard"):
        beard_m = mat(f"beard_{id_}", cfg["beard"], 0.9)
        if cfg.get("long_beard"):
            parts.append(
                sphere(
                    f"{id_}_beard_main",
                    hr * 0.86,
                    (0, -hr * 0.46, hz - hr * 0.62),
                    beard_m,
                    scale=(0.94, 0.76, 1.32),
                )
            )
            parts.append(
                sphere(
                    f"{id_}_beard_tip",
                    hr * 0.52,
                    (0, -hr * 0.52, hz - hr * 1.12),
                    beard_m,
                    scale=(0.82, 0.65, 1.15),
                )
            )
        else:
            parts.append(
                sphere(
                    f"{id_}_beard_main",
                    hr * 0.8,
                    (0, -hr * 0.42, hz - hr * 0.52),
                    beard_m,
                    scale=(0.95, 0.72, 1.02),
                )
            )
        parts.append(
            torus(
                f"{id_}_must",
                hr * 0.32,
                0.048,
                (0, fy * 0.96, hz - 0.2),
                beard_m,
                scale=(1.0, 0.35, 0.6),
                seg=16,
                tseg=6,
            )
        )

    # 頭巾與髮辮
    cover_parts = []
    if cfg.get("scarf") or child:
        parts.append(
            sphere(
                f"{id_}_hood",
                hr * 1.1,
                (0, hr * 0.05, hz + 0.02),
                head_m,
                scale=(1.0, 1.0, 1.05),
                cut=-0.55,
                face=0.42,
            )
        )
        drape_top = hz - 0.05
        dr = hr * 1.1
        parts.append(
            lathe(
                f"{id_}_drape",
                [
                    (dr, drape_top),
                    (dr * 1.08, drape_top - 0.36),
                    (0.64 if not child else 0.58, 2.58 if not child else 2.44),
                ],
                head_m,
                loc=(0, hr * 0.12, 0),
                arc=(-30, 210),
            )
        )
        parts.append(sphere(f"{id_}_fringe", hr * 0.98, (0, -0.02, hz + 0.06), HAIR_DARK, cut=0.45))
        if child or yw:
            braid_n = 4 if child else 5
            for k in range(braid_n):
                parts.append(
                    sphere(
                        f"{id_}_braid{k}",
                        0.105 - k * 0.011,
                        (0.0, hr * 0.96 + 0.06, hz - 0.44 - k * 0.19),
                        HAIR_DARK,
                        seg=10,
                        rings=8,
                        scale=(1.0, 1.0, 1.25),
                    )
                )
    else:
        band_m = mat(f"agal_{id_}", cfg.get("band", "#3a2a1e"), 0.82)
        cover_parts = [
            sphere(f"{id_}_kef", hr * 1.12, (0, hr * 0.05, hz + 0.02), head_m, cut=-0.5, face=0.4),
            lathe(
                f"{id_}_kefdrape",
                [(hr * 1.12, hz - 0.02), (hr * 1.2, hz - 0.45), (0.69, 2.68)],
                head_m,
                loc=(0, hr * 0.18, 0),
                arc=(-25, 205),
            ),
            torus(
                f"{id_}_agal",
                hr * 1.05,
                0.05,
                (0, hr * 0.04, hz + 0.24),
                band_m,
                scale=(1.0, 1.0, 0.9),
                seg=24,
                tseg=8,
            ),
        ]

    body_obj = join_parts(f"{id_}_body", parts, origin=(0.0, 0.0, 0.0))
    cover_obj = join_parts(f"{id_}_cover", cover_parts, origin=(0.0, 0.0, 0.0)) if cover_parts else None

    # 右手臂（原點在右肩，供 three.js 旋轉揮手／指向／寫字／推石／遞交）
    sh = (-0.48, -0.02, 2.38) if child else ((-0.51, -0.02, 2.58) if yw else (-0.56, -0.02, 2.62))
    alen = 0.82 if child else (0.94 if yw else 0.98)
    sl = cyl(f"{id_}_sleeve", 0.14, 0.195, alen, (sh[0] - 0.03, -0.02, sh[2] - alen / 2.0 - 0.03), robe_m, seg=14)
    sl.rotation_euler = (0.0, math.radians(-5.0), 0.0)
    cap = sphere(f"{id_}_shoulder", 0.145, (sh[0] - 0.01, -0.02, sh[2] - 0.03), robe_m, seg=12, rings=10, scale=(1.0, 0.95, 0.92))
    hand = sphere(
        f"{id_}_hand",
        0.13,
        (sh[0] - 0.06, -0.04, sh[2] - alen - 0.19),
        skin_m,
        seg=12,
        rings=10,
        scale=(0.85, 0.9, 1.08),
    )
    arm_obj = join_parts(f"{id_}_arm", [sl, cap, hand], origin=sh)

    root = bpy.data.objects.new(f"fig_{id_}", None)
    sc.collection.objects.link(root)
    for ch in (body_obj, cover_obj, arm_obj):
        if ch:
            ch.parent = root
    root.location = (x_pos, 0.0, 0.0)
    return root


def build_crowd_silhouette(x_pos: float):
    """十二支派群眾 InstancedMesh 專用低多邊形單一網格（實高 1.70m，白色材質讓 instanceColor 染色）"""
    white_m = mat("crowd_white", "#f4efe4", 0.88)
    parts = [
        lathe(
            "crowd_robe_part",
            [
                (0.32, 0.0),
                (0.30, 0.35),
                (0.24, 0.85),
                (0.26, 1.18),
                (0.18, 1.32),
                (0.11, 1.38),
            ],
            white_m,
            seg=12,
            cap_bottom=True,
        ),
        sphere("crowd_head_part", 0.16, (0.0, 0.0, 1.53), white_m, seg=12, rings=8, scale=(0.95, 0.95, 1.06)),
        lathe(
            "crowd_hood_part",
            [(0.18, 1.56), (0.21, 1.38), (0.25, 1.18)],
            white_m,
            seg=10,
            arc=(-25, 205),
        ),
    ]
    merged = join_parts("crowd_silhouette", parts, origin=(0.0, 0.0, 0.0))
    merged.location = (x_pos, 0.0, 0.0)
    return merged


roots = [build_figure(cid, cfg, idx * 2.55) for idx, (cid, cfg) in enumerate(CAST_SPECS)]
crowd_obj = build_crowd_silhouette(len(CAST_SPECS) * 2.55)

# 檢查名稱零 .001 撞名
bad_names = [o.name for o in sc.objects if ".00" in o.name]
if bad_names:
    raise RuntimeError(f"Object name collision detected: {bad_names}")

# 先選取正式角色與群眾網格匯出 GLB（不含預覽鏡射左手與相機燈光）
for o in bpy.context.selected_objects:
    o.select_set(False)
for o in sc.objects:
    if (
        o.name.startswith("fig_")
        or (o.parent and o.parent.name.startswith("fig_"))
        or o.name == "crowd_silhouette"
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
    print(f"[cast.glb] io_scene_gltf2 unavailable ({exc}), using glb_writer fallback")
    export_selected_glb(sc, OUT_GLB)

print(f"[cast.glb] exported size = {os.path.getsize(OUT_GLB)} bytes")

# 加上預覽用鏡射左手、地面、日光與相機，輸出 1600x900 全尺寸檢查圖
for r in roots:
    arm_r = next(c for c in r.children if c.name.endswith("_arm"))
    arm_l = arm_r.copy()
    arm_l.name = "prev_" + arm_r.name + "_L"
    sc.collection.objects.link(arm_l)
    arm_l.parent = r
    arm_l.location.x = -arm_r.location.x
    arm_l.scale.x = -1.0

ground_bm = bmesh.new()
bmesh.ops.create_grid(ground_bm, x_segments=2, y_segments=2, size=28.0)
ground = obj_from_bm("prev_ground", ground_bm, mat("prev_ground_m", "#dfd5c0", 0.95))
ground.location = (10.0, 0.0, 0.0)

sun = bpy.data.objects.new("prev_sun", bpy.data.lights.new("prev_sun", "SUN"))
sun.data.energy = 3.6
sun.rotation_euler = (math.radians(52), 0.0, math.radians(-26))
sc.collection.objects.link(sun)

fill = bpy.data.objects.new("prev_fill", bpy.data.lights.new("prev_fill", "SUN"))
fill.data.energy = 1.1
fill.rotation_euler = (math.radians(65), 0.0, math.radians(145))
sc.collection.objects.link(fill)

cam = bpy.data.objects.new("prev_cam", bpy.data.cameras.new("prev_cam"))
cam.location = (10.1, -22.5, 2.65)
cam.rotation_euler = (math.radians(85.5), 0.0, 0.0)
cam.data.lens = 28
sc.collection.objects.link(cam)
sc.camera = cam

world = bpy.data.worlds.new("prev_world")
world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs[0].default_value = (*srgb_to_lin("#e8e0cf"), 1.0)
bg.inputs[1].default_value = 0.85
sc.world = world

sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items.keys() else "CYCLES"
if sc.render.engine == "CYCLES":
    sc.cycles.samples = 24
sc.render.resolution_x = 1600
sc.render.resolution_y = 900
sc.render.filepath = OUT_PNG
bpy.ops.render.render(write_still=True)
print(f"[cast_sheet.png] rendered ({os.path.getsize(OUT_PNG)} bytes)")
