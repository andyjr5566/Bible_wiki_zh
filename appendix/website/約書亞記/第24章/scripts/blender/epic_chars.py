"""寫實人物（風格 B）：Quaternius Universal Base Characters（CC0）底模 + Blender 布料模擬的長袍、外衣與頭巾。

流程：匯入底模 → 擺成雙臂垂下的姿勢並烘成靜態網格 → 依身體截面生成長袍環片 → 布料模擬（上端固定、下擺受風）
      → 披風（正方形布從肩上垂落，碰撞身體與長袍）→ 頭巾（布蓋在頭上）→ 合併成一個網格。
所有布料在 Blender 背景模式逐格 frame_set 模擬，沒有使用快取檔。
"""
import math
import os
import random

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

import epic_lib as L
from epic_lib import ASSETS, srgb

UBC = os.path.join(ASSETS, "ubc")


# ----------------------------------------------------------------------------- 匯入與擺姿
def _import_fbx(name):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=os.path.join(UBC, name))
    return [o for o in bpy.data.objects if o not in before]


def _rot_about(pivot, axis, ang):
    return Matrix.Translation(pivot) @ Matrix.Rotation(ang, 4, axis) @ Matrix.Translation(-pivot)


def _pose_bone_world(arm, bone, M):
    """用世界座標的矩陣 M（左乘）轉動骨頭。"""
    pb = arm.pose.bones[bone]
    cur = arm.matrix_world @ pb.matrix
    pb.matrix = arm.matrix_world.inverted() @ (M @ cur)
    bpy.context.view_layer.update()


def bake_object(obj, name):
    """取出物件目前（含骨架/布料修改器）的網格，建成沒有修改器的新物件。"""
    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(ev)
    me.transform(obj.matrix_world)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    if len(me.materials) == 0:
        for m in obj.data.materials:
            me.materials.append(m)
    return ob


def load_character(gender="male", skin="Dark", arm_drop=74.0, elbow=16.0, stride=0.0, tag="c"):
    """回傳 dict：body, eyes, brows（靜態網格物件）與關鍵骨點。面向 +Y，腳底在 z=0。"""
    fbx = "Superhero_Male_FullBody.fbx" if gender == "male" else "Superhero_Female_FullBody.fbx"
    objs = _import_fbx(fbx)
    arm = next(o for o in objs if o.type == "ARMATURE")
    sgn = {"l": -1.0, "r": 1.0}
    for side in ("l", "r"):
        ub = arm.pose.bones[f"upperarm_{side}"]
        head = arm.matrix_world @ ub.head
        # 世界座標的 X 軸方向：左臂在 -X，向下放 = 繞 Y 軸轉
        phi = math.radians(-arm_drop) if side == "l" else math.radians(arm_drop)
        _pose_bone_world(arm, f"upperarm_{side}", _rot_about(head, "Y", phi))
        lb = arm.pose.bones[f"lowerarm_{side}"]
        h2 = arm.matrix_world @ lb.head
        # 手肘微彎（手往身體前方）
        _pose_bone_world(arm, f"lowerarm_{side}", _rot_about(h2, "X", math.radians(-elbow)))
        if stride:
            th = arm.pose.bones[f"thigh_{side}"]
            h3 = arm.matrix_world @ th.head
            s = stride if side == "l" else -stride
            _pose_bone_world(arm, f"thigh_{side}", _rot_about(h3, "X", math.radians(s)))
    out = {}
    key = {}
    for b in ("upperarm_l", "lowerarm_l", "hand_l", "upperarm_r", "lowerarm_r", "hand_r", "Head", "neck_01", "pelvis", "spine_03"):
        pb = arm.pose.bones[b]
        key[b] = ((arm.matrix_world @ pb.head).copy(), (arm.matrix_world @ pb.tail).copy())
    out["key"] = key
    for o in objs:
        if o.type != "MESH":
            continue
        low = o.name.lower()
        nm = "body" if low.startswith("superhero") else ("eyes" if low.startswith("eyes") else ("brows" if low.startswith("eyebrows") else o.name))
        b = bake_object(o, f"{tag}_{nm}")
        # 頂點群組（找手臂/頭的頂點用）：保留
        if nm == "body":
            for vg in o.vertex_groups:
                b.vertex_groups.new(name=vg.name)
            # 複製權重
            for v in o.data.vertices:
                for g in v.groups:
                    b.vertex_groups[g.group].add([v.index], g.weight, "REPLACE")
        out[nm] = b
    for o in objs:
        bpy.data.objects.remove(o, do_unlink=True)
    # 皮膚材質：貼上提供的基色貼圖
    skin_png = {("male", "Dark"): "T_Superhero_Male_Dark.png", ("male", "Light"): "T_Superhero_Male_Ligh.png",
                ("female", "Dark"): "T_Superhero_Female_Dark_BaseColor.png", ("female", "Light"): "T_Superhero_Female_Light_BaseColor.png"}[(gender, skin)]
    out["body"].data.materials.clear()
    out["body"].data.materials.append(skin_material(skin_png, f"skin_{gender}_{skin}"))
    return out


_SKIN = {}


def skin_material(png, name):
    if name in _SKIN:
        return _SKIN[name]
    m = L.new_mat(name)
    nt = m.node_tree
    b = L.bsdf_of(m)
    img = bpy.data.images.load(os.path.join(UBC, png), check_existing=True)
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.62
    for k, v in (("Subsurface Weight", 0.08), ("Subsurface Radius", (0.8, 0.35, 0.2))):
        if k in b.inputs:
            b.inputs[k].default_value = v
    _SKIN[name] = m
    return m


def hair_object(style, tag="c", color_tint=None):
    """匯入髮型（Origin at 0 版），轉到角色座標（面向 +Y）。"""
    objs = _import_fbx(f"{style}.fbx")
    o = next(x for x in objs if x.type == "MESH")
    me = o.data
    me.transform(Matrix.Rotation(math.pi, 4, "Z") @ o.matrix_world)
    o.matrix_world = Matrix.Identity(4)
    for x in objs:
        if x is not o:
            bpy.data.objects.remove(x, do_unlink=True)
    o.name = f"{tag}_{style}"
    if color_tint is not None:
        for sl in o.material_slots:
            m = sl.material.copy()
            b = L.bsdf_of(m)
            b.inputs["Base Color"].default_value = (*color_tint, 1)
            sl.material = m
    return o


# ----------------------------------------------------------------------------- 身體截面
def torso_points(body):
    """回傳驅幹＋雙腿的頂點（排除手臂、手、頭）。"""
    me = body.data
    names = {i: vg.name for i, vg in enumerate(body.vertex_groups)}
    skip = ("upperarm", "lowerarm", "hand", "index", "middle", "pinky", "ring", "thumb", "Head", "clavicle")
    pts = []
    for v in me.vertices:
        if v.groups:
            g = max(v.groups, key=lambda g: g.weight)
            nm = names.get(g.group, "")
            if any(nm.startswith(s) for s in skip):
                continue
        pts.append(v.co[:])
    return np.array(pts, dtype=np.float64)


def slice_ellipse(pts, z, band=0.035):
    sel = pts[np.abs(pts[:, 2] - z) < band]
    if len(sel) < 4:
        return None
    return (sel[:, 0].min(), sel[:, 0].max(), sel[:, 1].min(), sel[:, 1].max())


# ----------------------------------------------------------------------------- 布料
_FAB = {}


def fabric_material(name, hex_col, trim_hex=None, rough=0.92, weave=60.0, nap=0.0):
    if name in _FAB:
        return _FAB[name]
    m = L.new_mat(name)
    _FAB[name] = m
    nt = m.node_tree
    b = L.bsdf_of(m)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    base = srgb(hex_col)
    n1 = L.noise_tex(nt, tc.outputs["Object"], 3.0, 4.0)
    n2 = L.noise_tex(nt, tc.outputs["Object"], 55.0, 2.0)
    shade = L.math_node(nt, "ADD", 0.82, L.math_node(nt, "ADD", L.math_node(nt, "MULTIPLY", n1, 0.26), L.math_node(nt, "MULTIPLY", n2, 0.12)))
    # 織紋：兩向細條
    wv = nt.nodes.new("ShaderNodeTexWave")
    wv.wave_type = "BANDS"
    wv.inputs["Scale"].default_value = weave
    wv.inputs["Distortion"].default_value = 1.5
    nt.links.new(tc.outputs["Object"], wv.inputs["Vector"])
    wv2 = nt.nodes.new("ShaderNodeTexWave")
    wv2.wave_type = "BANDS"
    wv2.bands_direction = "Y"
    wv2.inputs["Scale"].default_value = weave
    nt.links.new(tc.outputs["Object"], wv2.inputs["Vector"])
    weave_v = L.math_node(nt, "ADD", wv.outputs["Fac"], wv2.outputs["Fac"])
    col = L.mix_rgb(nt, base, (0, 0, 0), 0.0)
    shaded = nt.nodes.new("ShaderNodeMix")
    shaded.data_type = "RGBA"
    shaded.blend_type = "MULTIPLY"
    shaded.inputs[0].default_value = 1.0
    shaded.inputs[6].default_value = (*base, 1)
    comb = nt.nodes.new("ShaderNodeCombineColor")
    for nm in ("Red", "Green", "Blue"):
        nt.links.new(L.math_node(nt, "ADD", shade, L.math_node(nt, "MULTIPLY", weave_v, 0.015)), comb.inputs[nm])
    nt.links.new(comb.outputs["Color"], shaded.inputs[7])
    nt.links.new(shaded.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    for k, v in (("Sheen Weight", 0.35), ("Sheen Roughness", 0.5)):
        if k in b.inputs:
            b.inputs[k].default_value = v
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.35
    bump.inputs["Distance"].default_value = 0.0015
    nt.links.new(L.math_node(nt, "ADD", L.math_node(nt, "MULTIPLY", weave_v, 0.25), L.math_node(nt, "MULTIPLY", n2, 0.8)), bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


_wind = None


def _ensure_wind(strength=0.0, direction=(1, 0, 0)):
    global _wind
    if _wind is None:
        bpy.ops.object.effector_add(type="WIND")
        _wind = bpy.context.active_object
        _wind.name = "wind"
    _wind.field.strength = strength
    _wind.field.flow = 0.0
    _wind.field.noise = 0.4
    d = Vector(direction).normalized()
    _wind.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    # 風的方向是物件的 -Z 軸反向（Blender：吹向 +Z 局部軸）
    _wind.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return _wind


def make_collider(obj, thickness=0.004):
    if not any(m.type == "COLLISION" for m in obj.modifiers):
        obj.modifiers.new("Collision", "COLLISION")
    obj.collision.thickness_outer = thickness
    obj.collision.thickness_inner = 0.1
    obj.collision.cloth_friction = 12.0
    obj.collision.use_culling = False
    return obj


def run_cloth(obj, frames, pin_group=None, mass=0.25, bending=6.0, tension=22.0, compression=22.0, shear=20.0,
              air=1.0, self_collision=False, wind=0.0, wind_dir=(1, 0.3, 0), quality=8, gravity=True,
              dist_min=0.006, pin_stiff=1.0):
    sc = bpy.context.scene
    sc.frame_start = 1
    sc.frame_end = frames
    md = obj.modifiers.new("Cloth", "CLOTH")
    s = md.settings
    s.quality = quality
    s.mass = mass
    s.tension_stiffness = tension
    s.compression_stiffness = compression
    s.shear_stiffness = shear
    s.bending_stiffness = bending
    s.air_damping = air
    try:
        s.tension_damping = 5.0
        s.compression_damping = 5.0
        s.shear_damping = 5.0
        s.bending_damping = 0.5
    except Exception:
        pass
    if pin_group:
        s.vertex_group_mass = pin_group
        s.pin_stiffness = pin_stiff
    cs = md.collision_settings
    cs.use_collision = True
    cs.distance_min = dist_min
    cs.collision_quality = 4
    cs.use_self_collision = self_collision
    if self_collision:
        cs.self_distance_min = 0.004
        cs.self_friction = 5.0
    md.point_cache.frame_start = 1
    md.point_cache.frame_end = frames
    if wind:
        w = _ensure_wind(wind, wind_dir)
        w.field.strength = wind
    elif _wind is not None:
        _wind.field.strength = 0.0
    sc.use_gravity = gravity
    sc.frame_set(1)
    for f in range(2, frames + 1):
        sc.frame_set(f)
    bpy.context.view_layer.update()
    baked = bake_object(obj, obj.name + "_baked")
    return baked


def _grid_mesh(name, rings, seg, closed_u=True):
    """rings: 由上往下的 (n_rings, seg, 3) 陣列；回傳網格物件（四邊形環片）。"""
    n = rings.shape[0]
    verts = rings.reshape(-1, 3)
    faces = []
    for i in range(n - 1):
        for j in range(seg):
            j2 = (j + 1) % seg
            faces.append((i * seg + j, i * seg + j2, (i + 1) * seg + j2, (i + 1) * seg + j))
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.update()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def _subdiv(ob, levels=1):
    m = ob.modifiers.new("subsurf", "SUBSURF")
    m.levels = levels
    m.render_levels = levels
    return m


def apply_modifiers(ob, name=None):
    b = bake_object(ob, name or ob.name + "_ap")
    for mt in ob.data.materials:
        pass
    return b


def make_robe(ch, hex_col, trim_hex, hem_z=0.07, top_z=None, seed=1, frames=36, wind=1.2, wind_dir=(1, 0.2, 0.0), tag="c",
              flare=0.17, pleat=0.03, neck_open=0.0):
    """長袍：由上而下的環片，依身體截面撐開並加褶，上端固定、下擺在風中垂落。"""
    rnd = random.Random(seed)
    body = ch["body"]
    pts = torso_points(body)
    key = ch["key"]
    neck_z = key["neck_01"][1].z
    top_z = top_z or (neck_z - 0.02)
    n_rings = 46
    seg = 56
    zs = np.linspace(top_z, hem_z, n_rings)
    rings = np.zeros((n_rings, seg, 3))
    ph = rnd.uniform(0, 6.28)
    for i, z in enumerate(zs):
        e = slice_ellipse(pts, z)
        if e is None:
            e = slice_ellipse(pts, z, 0.08)
        x0, x1, y0, y1 = e
        # 腿部兩條腿的外包：已含；增加衣料餘裕，越往下越寬（A 字）
        t = (top_z - z) / (top_z - hem_z)
        cx = (x0 + x1) / 2
        cy = (y0 + y1) / 2
        rx = (x1 - x0) / 2
        ry = (y1 - y0) / 2
        marg = 0.028 + 0.02 * t + flare * max(0.0, t - 0.5) ** 1.4
        zw = key['pelvis'][1].z + 0.12
        cinch = 1.0 - 0.055 * math.exp(-((z - zw) / 0.045) ** 2)
        rx = rx + marg + (0.0 if z > top_z - 0.06 else 0.0)
        ry = ry + marg * 0.9
        # 脖子處收小
        if z > neck_z - 0.1:
            k = (z - (neck_z - 0.1)) / 0.1
            rx = rx * (1 - 0.45 * k) + 0.0
            ry = ry * (1 - 0.15 * k)
        for j in range(seg):
            a = 2 * math.pi * j / seg
            fold = 1.0 + pleat * t * math.sin(a * 9 + ph + 3.0 * math.sin(a * 3)) + 0.012 * math.sin(a * 17 + ph * 2) * t
            rings[i, j] = (cx + rx * cinch * fold * math.cos(a), cy + ry * cinch * fold * math.sin(a), z)
    ob = _grid_mesh(f"{tag}_robe", rings, seg)
    # 固定組：上半身（z > 腰上）權重 1，向下漸降到 0
    vg = ob.vertex_groups.new(name="pin")
    waist = key["pelvis"][1].z + 0.12
    for i, z in enumerate(zs):
        wgt = 1.0 if z >= waist else max(0.0, 1.0 - (waist - z) / 0.28)
        wgt = wgt ** 1.5
        if wgt > 0.001:
            vg.add([i * seg + j for j in range(seg)], wgt, "REPLACE")
    # 底邊另設材質槽
    ob.data.materials.append(fabric_material(f"{tag}_robe_mat", hex_col))
    ob.data.materials.append(fabric_material(f"{tag}_robe_trim", trim_hex, weave=90.0))
    for p in ob.data.polygons:
        zc = np.mean([ob.data.vertices[i].co.z for i in p.vertices])
        if zc < hem_z + 0.07:
            p.material_index = 1
    make_collider(body)
    baked = run_cloth(ob, frames, pin_group="pin", wind=wind, wind_dir=wind_dir)
    bpy.data.objects.remove(ob, do_unlink=True)
    for m in baked.data.materials:
        pass
    baked.name = f"{tag}_robe_b"
    return baked


def make_sleeves(ch, hex_col, trim_hex, tag="c", wide=1.0):
    """袖子：沿手臂的環管（不模擬），袖口放寬。"""
    key = ch["key"]
    out = []
    for side in ("l", "r"):
        sh = key[f"upperarm_{side}"][0]
        el = key[f"lowerarm_{side}"][0]
        wr = key[f"hand_{side}"][0]
        pts = [sh + (sh - el).normalized() * 0.02, sh, (sh + el) / 2, el, (el + wr) / 2, wr + (el - wr).normalized() * -0.005]
        radii = [0.085, 0.085, 0.075, 0.072 * wide, 0.082 * wide, 0.09 * wide]
        bm = bmesh.new()
        L.tube_bm([p[:] for p in pts], radii, 14, bm, cap=False)
        me = bpy.data.meshes.new(f"{tag}_sleeve_{side}")
        bm.to_mesh(me)
        bm.free()
        for p in me.polygons:
            p.use_smooth = True
        ob = bpy.data.objects.new(f"{tag}_sleeve_{side}", me)
        bpy.context.scene.collection.objects.link(ob)
        me.materials.append(fabric_material(f"{tag}_sleeve_mat", hex_col))
        me.materials.append(fabric_material(f"{tag}_sleeve_trim", trim_hex, weave=90.0))
        # 袖口帶
        n = len(me.polygons)
        for p in me.polygons:
            if (sum((Vector(me.vertices[i].co) for i in p.vertices), Vector()) / len(p.vertices) - wr).length < 0.07:
                p.material_index = 1
        out.append(ob)
    return out


def _body_top(body):
    from mathutils.bvhtree import BVHTree
    dg = bpy.context.evaluated_depsgraph_get()
    return BVHTree.FromObject(body, dg)


def _sheet(name, x0, x1, y0, y1, z0, nx, ny, hole=None, hole_r=0.0):
    xs = np.linspace(x0, x1, nx)
    ys = np.linspace(y0, y1, ny)
    verts = [(float(xv), float(yv), z0) for yv in ys for xv in xs]
    faces = []
    for j in range(ny - 1):
        for i in range(nx - 1):
            idx = (j * nx + i, j * nx + i + 1, (j + 1) * nx + i + 1, (j + 1) * nx + i)
            if hole is not None:
                cx = sum(verts[k][0] for k in idx) / 4
                cy = sum(verts[k][1] for k in idx) / 4
                if (cx - hole[0]) ** 2 + (cy - hole[1]) ** 2 < hole_r ** 2:
                    continue
            faces.append(idx)
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def _pin_ring(ob, tree, center, r_in, r_out, lift=0.012, name="pin", ray_z=2.5):
    vg = ob.vertex_groups.new(name=name)
    me = ob.data
    for v in me.vertices:
        dx, dy = v.co.x - center[0], v.co.y - center[1]
        r = math.hypot(dx, dy)
        if r > r_out:
            continue
        w = 1.0 if r <= r_in else 1.0 - (r - r_in) / (r_out - r_in)
        if w <= 0.0:
            continue
        if r <= r_in:
            hit = tree.ray_cast(Vector((v.co.x, v.co.y, ray_z)), Vector((0, 0, -1)), 3.0)
            if hit[0] is not None:
                v.co.z = hit[0].z + lift
        vg.add([v.index], w ** 0.7, "REPLACE")
    return vg


def make_cloak(ch, robe, sleeves, hex_col, trim_hex, tag="c", width=1.25, length=1.3, frames=60, wind=0.25,
               wind_dir=(1, 0.4, 0), shift_y=-0.04, seed=3):
    """披風：中間有領口的方形布，領口周圍固定在肩上，其餘部分垂落、碰撞身體、長袍與袖子。"""
    key = ch["key"]
    neck = key["neck_01"][0]
    tree = _body_top(ch["body"])
    sh_z = neck.z + 0.0
    ob = _sheet(f"{tag}_cloak", -width / 2, width / 2, -length / 2 + shift_y, length / 2 + shift_y, sh_z, 60, 66,
                hole=(0.0, neck.y), hole_r=0.1)
    _pin_ring(ob, tree, (0.0, neck.y), 0.17, 0.22, ray_z=neck.z + 0.01)
    me = ob.data
    me.materials.append(fabric_material(f"{tag}_cloak_mat", hex_col, weave=40.0, rough=0.95))
    me.materials.append(fabric_material(f"{tag}_cloak_trim", trim_hex, weave=70.0))
    for p in me.polygons:
        c = sum((Vector(me.vertices[i].co) for i in p.vertices), Vector()) / len(p.vertices)
        if abs(c.x) > width / 2 * 0.95 or abs(c.y - shift_y) > length / 2 * 0.955:
            p.material_index = 1
    make_collider(ch["body"])
    for c in [robe] + sleeves:
        make_collider(c, 0.006)
    baked = run_cloth(ob, frames, pin_group="pin", wind=wind, wind_dir=wind_dir, self_collision=True, mass=0.3, bending=2.5,
                      quality=10, dist_min=0.01)
    bpy.data.objects.remove(ob, do_unlink=True)
    baked.name = f"{tag}_cloak_b"
    return baked


def make_headcloth(ch, hex_col, trim_hex=None, tag="c", frames=50, wind=0.2, wind_dir=(1, 0.4, 0), colliders=(), back=0.5, side=0.40, front=0.13):
    """頭巾：頭頂固定一圈，布往後與兩側垂落，前緣只到額頭，臉露出來。"""
    key = ch["key"]
    hc = key["Head"][0] + (key["Head"][1] - key["Head"][0]) * 0.5
    tree = _body_top(ch["body"])
    top = tree.ray_cast(Vector((hc.x, hc.y, 2.5)), Vector((0, 0, -1)), 3.0)
    z_top = (top[0].z if top[0] is not None else hc.z + 0.1)
    ob = _sheet(f"{tag}_hc", -side, side, hc.y - back, hc.y + front, z_top + 0.015, 46, 52)
    _pin_ring(ob, tree, (0.0, hc.y - 0.01), 0.055, 0.1, lift=0.01)
    me = ob.data
    me.materials.append(fabric_material(f"{tag}_hc_mat", hex_col, weave=70.0))
    if trim_hex:
        me.materials.append(fabric_material(f"{tag}_hc_trim", trim_hex, weave=90.0))
        for p in me.polygons:
            c = sum((Vector(me.vertices[i].co) for i in p.vertices), Vector()) / len(p.vertices)
            if abs(c.x) > side * 0.93 or c.y < hc.y - back * 0.93:
                p.material_index = 1
    make_collider(ch["body"])
    for c in colliders:
        make_collider(c, 0.006)
    baked = run_cloth(ob, frames, pin_group="pin", wind=wind, wind_dir=wind_dir, self_collision=True, mass=0.18, bending=1.8,
                      quality=10, dist_min=0.008)
    bpy.data.objects.remove(ob, do_unlink=True)
    baked.name = f"{tag}_hc_b"
    return baked


def make_sash(ch, hex_col, tag="c", turns=2, z=None):
    """腰間繩帶：圍腰兩圈，一端垂下。"""
    key = ch["key"]
    pts = torso_points(ch["body"])
    z = z or (key["pelvis"][1].z + 0.12)
    e = slice_ellipse(pts, z, 0.03)
    x0, x1, y0, y1 = e
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rx, ry = (x1 - x0) / 2 + 0.036, (y1 - y0) / 2 + 0.034
    bm = bmesh.new()
    path = []
    n = 60
    for t in range(n * turns + 1):
        a = 2 * math.pi * t / n
        zz = z + 0.02 * (t / (n * turns)) * 2 - 0.02
        path.append((cx + rx * math.cos(a), cy + ry * math.sin(a), zz))
    last = Vector(path[-1])
    for k in range(1, 8):
        path.append((last.x + 0.01 * k, last.y + 0.005 * k, last.z - 0.07 * k))
    L.tube_bm(path, [0.014] * len(path), 8, bm, cap=True)
    me = bpy.data.meshes.new(f"{tag}_sash")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(fabric_material(f"{tag}_sash_mat", hex_col, weave=40.0))
    ob = bpy.data.objects.new(f"{tag}_sash", me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def make_agal(ch, tag="c"):
    """頭巾上的黑色頭箍。"""
    key = ch["key"]
    hc = key["Head"][0] + (key["Head"][1] - key["Head"][0]) * 0.5
    bm = bmesh.new()
    path = []
    for t in range(41):
        a = 2 * math.pi * t / 40
        path.append((hc.x + 0.112 * math.cos(a), hc.y - 0.005 + 0.122 * math.sin(a), hc.z + 0.065))
    L.tube_bm(path, [0.011] * len(path), 6, bm, cap=False)
    me = bpy.data.meshes.new(f"{tag}_agal")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(L.pbr(f"{tag}_agal_mat", "#241c17", 0.7))
    ob = bpy.data.objects.new(f"{tag}_agal", me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def finalize_character(parts, name):
    """合併所有部件成單一物件（材質槽保留）。"""
    objs = [p for p in parts if p is not None]
    for o in objs:
        for m in list(o.modifiers):
            o.modifiers.remove(m)
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    objs[0].name = name
    return objs[0]
