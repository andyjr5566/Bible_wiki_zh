"""史詩樣張用的材質與道具：地形材質、橡樹、立石、簡化人形、動物、戰車。"""
import math
import random

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

from epic_lib import (
    box_bm, join_objects, lathe_bm, math_node, mesh_obj, mix_rgb, new_mat, noise_tex, pbr, ramp, bsdf_of, srgb,
    sphere_bm, tube_bm, link,
)


def lin(h):
    return tuple(srgb(h))


# ----------------------------------------------------------------------------- 地形材質
def terrain_material(name="terrain", palette="levant", scale=1.0, sea=False, veg_k=1.0, field_scale=0.0035):
    """依坡度、海拔、綠度與雜訊上色：石灰岩坡、梯田條紋、谷底田塊、海水。"""
    m = new_mat(name)
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(b.outputs["BSDF"], out.inputs["Surface"])
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Normal"], sep.inputs["Vector"])
    pos = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], pos.inputs["Vector"])
    att = nt.nodes.new("ShaderNodeAttribute")
    att.attribute_name = "veg"
    att.attribute_type = "GEOMETRY"
    att_sea = nt.nodes.new("ShaderNodeAttribute")
    att_sea.attribute_name = "sea"
    att_sea.attribute_type = "GEOMETRY"

    P = geo.outputs["Position"]
    # 世界座標的雜訊
    n_big = noise_tex(nt, P, 0.0012 / scale, 3.0)
    n_mid = noise_tex(nt, P, 0.02 / scale, 4.0)
    n_fine = noise_tex(nt, P, 0.35 / scale, 5.0, 0.6)
    n_micro = noise_tex(nt, P, 3.0 / scale, 4.0, 0.6)

    if palette in ("levant", "levant_warm"):
        rock_a, rock_b = (lin("#b5a07c"), lin("#e2c996")) if palette == "levant_warm" else (lin("#b0a283"), lin("#dccb9f"))
        soil_a, soil_b = lin("#8a7350"), lin("#b09a68")
        grass_dry, grass_green = lin("#a9985a"), lin("#7d8c4c")
        scrub = lin("#4f5c35")
        field_cols = [lin("#8d7746"), lin("#6f8a3c"), lin("#b3a265"), lin("#76603f")]
    else:  # desert
        rock_a, rock_b = lin("#9b8a6c"), lin("#cdb994")
        soil_a, soil_b = lin("#a68a5b"), lin("#c8aa73")
        grass_dry, grass_green = lin("#b19d62"), lin("#808a47")
        scrub = lin("#6a6a3b")
        field_cols = [lin("#b69b66"), lin("#a58a58"), lin("#c2a870"), lin("#8d8650")]

    nz = sep.outputs["Z"]
    steep = math_node(nt, "SUBTRACT", 1.0, nz)  # 0 平 → 1 垂直
    steep_n = math_node(nt, "ADD", steep, math_node(nt, "MULTIPLY", math_node(nt, "SUBTRACT", n_mid, 0.5), 0.22))
    # smoothstep via map range
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.interpolation_type = "SMOOTHSTEP"
    mr.inputs["From Min"].default_value = 0.16
    mr.inputs["From Max"].default_value = 0.42
    nt.links.new(steep_n, mr.inputs["Value"])
    rockf = mr.outputs["Result"]

    # 梯田細線：沿等高線的細暗線，只在中坡
    zz = pos.outputs["Z"]
    wob = math_node(nt, "MULTIPLY", n_mid, 9.0)
    wave = math_node(nt, "SINE", math_node(nt, "ADD", math_node(nt, "MULTIPLY", zz, 0.9 / scale), wob))
    line = nt.nodes.new("ShaderNodeMapRange")
    line.interpolation_type = "SMOOTHSTEP"
    line.inputs["From Min"].default_value = 0.82
    line.inputs["From Max"].default_value = 0.97
    nt.links.new(wave, line.inputs["Value"])
    mid_slope = nt.nodes.new("ShaderNodeMapRange")
    mid_slope.interpolation_type = "SMOOTHSTEP"
    mid_slope.inputs["From Min"].default_value = 0.08
    mid_slope.inputs["From Max"].default_value = 0.2
    nt.links.new(steep_n, mid_slope.inputs["Value"])
    terr = math_node(nt, "MULTIPLY", line.outputs["Result"], math_node(nt, "MULTIPLY", mid_slope.outputs["Result"], math_node(nt, "SUBTRACT", 1.0, rockf)))

    # 岩面：灰米石灰岩 + 水平岩層
    strata = math_node(nt, "SINE", math_node(nt, "ADD", math_node(nt, "MULTIPLY", zz, 0.45 / scale), math_node(nt, "MULTIPLY", n_fine, 6.0)))
    strata = math_node(nt, "MULTIPLY", math_node(nt, "ADD", strata, 1.0), 0.5)
    rock = mix_rgb(nt, rock_a, rock_b, math_node(nt, "ADD", math_node(nt, "MULTIPLY", n_fine, 0.55), math_node(nt, "MULTIPLY", strata, 0.45), clamp=True))
    # 土與草：看綠度
    veg = math_node(nt, "MULTIPLY", att.outputs["Fac"], veg_k)
    vegn = math_node(nt, "ADD", veg, math_node(nt, "MULTIPLY", math_node(nt, "SUBTRACT", n_big, 0.5), 0.9), clamp=True)
    grass = mix_rgb(nt, grass_dry, grass_green, vegn)
    soil = mix_rgb(nt, soil_a, soil_b, n_fine)
    ground = mix_rgb(nt, soil, grass, math_node(nt, "ADD", vegn, math_node(nt, "MULTIPLY", math_node(nt, "SUBTRACT", n_micro, 0.5), 0.3), clamp=True))
    # 灌木點
    n_dots = noise_tex(nt, P, 0.9 / scale, 2.0, 0.6)
    shrub_mask = math_node(nt, "GREATER_THAN", math_node(nt, "ADD", n_dots, math_node(nt, "MULTIPLY", vegn, 0.3)), 0.8)
    shrub_mask = math_node(nt, "MULTIPLY", shrub_mask, math_node(nt, "SUBTRACT", 1.0, rockf))
    ground = mix_rgb(nt, ground, scrub, math_node(nt, "MULTIPLY", shrub_mask, 0.7))
    col = mix_rgb(nt, ground, rock, rockf)
    # 谷底與平坡的田塊（Voronoi）
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.feature = "F1"
    vor.inputs["Scale"].default_value = field_scale / scale
    nt.links.new(P, vor.inputs["Vector"])
    fcol = ramp(nt, vor.outputs["Distance"], [(0.0, field_cols[0]), (0.33, field_cols[1]), (0.66, field_cols[2]), (1.0, field_cols[3])])
    # 以 Voronoi 位置色（隨機色）選田塊色
    vor2 = nt.nodes.new("ShaderNodeTexVoronoi")
    vor2.feature = "F1"
    vor2.inputs["Scale"].default_value = field_scale / scale
    nt.links.new(P, vor2.inputs["Vector"])
    sepc = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(vor2.outputs["Color"], sepc.inputs["Color"])
    fcol = ramp(nt, sepc.outputs["Red"], [(0.0, field_cols[0]), (0.3, field_cols[1]), (0.6, field_cols[2]), (1.0, field_cols[3])])
    fcol = mix_rgb(nt, fcol, ground, 0.35)
    flat = nt.nodes.new("ShaderNodeMapRange")
    flat.interpolation_type = "SMOOTHSTEP"
    flat.inputs["From Min"].default_value = 0.035
    flat.inputs["From Max"].default_value = 0.012
    nt.links.new(steep, flat.inputs["Value"])
    farm = math_node(nt, "MULTIPLY", flat.outputs["Result"], math_node(nt, "SUBTRACT", 1.0, math_node(nt, "MULTIPLY", rockf, 1.0)))
    farm = math_node(nt, "MULTIPLY", farm, math_node(nt, "MULTIPLY", math_node(nt, "SUBTRACT", 1.0, att_sea.outputs["Fac"]), 1.0))
    col = mix_rgb(nt, col, fcol, math_node(nt, "MULTIPLY", farm, 0.8))
    # 明暗細節
    col = mix_rgb(nt, col, (0.5, 0.5, 0.5), math_node(nt, "MULTIPLY", math_node(nt, "SUBTRACT", n_micro, 0.5), 0.0), "MIX")
    n_grain = noise_tex(nt, P, 7.0 / scale, 4.0, 0.65)
    n_tuft = noise_tex(nt, P, 22.0 / scale, 3.0, 0.6)
    detail = math_node(nt, "ADD", 0.78, math_node(nt, "ADD", math_node(nt, "MULTIPLY", n_grain, 0.28), math_node(nt, "MULTIPLY", n_tuft, 0.2)))
    col = mix_rgb(nt, col, col, 1.0, "MULTIPLY") if False else col
    shade = nt.nodes.new("ShaderNodeMix")
    shade.data_type = "RGBA"
    shade.blend_type = "MULTIPLY"
    shade.inputs[0].default_value = 1.0
    nt.links.new(col, shade.inputs[6])
    sv = nt.nodes.new("ShaderNodeCombineColor")
    for nm in ("Red", "Green", "Blue"):
        nt.links.new(detail, sv.inputs[nm])
    nt.links.new(sv.outputs["Color"], shade.inputs[7])
    col = shade.outputs[2]
    # 海水
    if sea:
        seaf = nt.nodes.new("ShaderNodeMapRange")
        seaf.interpolation_type = "LINEAR"
        seaf.inputs["From Min"].default_value = 0.0
        seaf.inputs["From Max"].default_value = 1.0
        nt.links.new(att_sea.outputs["Fac"], seaf.inputs["Value"])
        depth = nt.nodes.new("ShaderNodeMapRange")
        depth.interpolation_type = "SMOOTHSTEP"
        depth.inputs["From Min"].default_value = 0.0
        depth.inputs["From Max"].default_value = 90.0
        nt.links.new(att_sea.outputs["Fac"], depth.inputs["Value"])
        wcol = mix_rgb(nt, lin("#3f9a98"), lin("#0b3552"), depth.outputs["Result"])
        issea = math_node(nt, "GREATER_THAN", att_sea.outputs["Fac"], 0.5)
        col = mix_rgb(nt, col, wcol, issea)
    nt.links.new(col, b.inputs["Base Color"])
    rough = math_node(nt, "ADD", 0.88, math_node(nt, "MULTIPLY", n_micro, -0.1))
    b.inputs["Roughness"].default_value = 0.9
    # 凹凸
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.4
    bump.inputs["Distance"].default_value = 0.3
    nt.links.new(math_node(nt, "ADD", math_node(nt, "MULTIPLY", n_grain, 0.7), math_node(nt, "MULTIPLY", n_micro, 0.5)), bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


# ----------------------------------------------------------------------------- 橡樹
def build_oak(seed=3, height=15.0, spread=17.0, trunk_r=0.9, leaf_hex="#5d6c34"):
    """泰博橡樹：短粗主幹、很低就分出厚重橫枝、寬圓冠。回傳（木質 obj, 葉冠 obj）。"""
    rnd = random.Random(seed)
    bark = pbr("oak_bark", "#4b3d30", 0.95)
    leaf = pbr("oak_leaf", leaf_hex, 0.75)
    # 葉色變化
    nt = leaf.node_tree
    b = bsdf_of(leaf)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    n = noise_tex(nt, tc.outputs["Object"], 0.55, 4.0)
    cr = ramp(nt, n, [(0.25, lin("#3d4c25")), (0.55, lin(leaf_hex)), (0.85, lin("#7d8a3f"))])
    nt.links.new(cr, b.inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.6
    nt.links.new(noise_tex(nt, tc.outputs["Object"], 14.0, 3.0), bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])

    wood = bmesh.new()
    foliage = bmesh.new()
    # 主幹：略彎，底部外擴
    trunk_pts = [(0, 0, -0.4), (0.05, 0.02, 0.8), (0.15, -0.05, 1.9), (0.1, 0.0, 2.8)]
    tube_bm(trunk_pts, [trunk_r * 1.35, trunk_r * 1.05, trunk_r * 0.95, trunk_r * 0.85], 14, wood)
    tips = []

    def branch(start, direction, length, r0, depth):
        pts = [Vector(start)]
        d = Vector(direction).normalized()
        steps = 5
        radii = []
        cur = Vector(start)
        for i in range(steps):
            d = (d + Vector((rnd.uniform(-0.18, 0.18), rnd.uniform(-0.18, 0.18), rnd.uniform(-0.05, 0.12)))).normalized()
            cur = cur + d * (length / steps)
            pts.append(cur.copy())
        for i in range(steps + 1):
            t = i / steps
            radii.append(max(r0 * (1 - 0.72 * t), 0.045))
        tube_bm(pts, radii, 8, wood, cap=False)
        if depth > 0:
            nsub = 2 if depth > 1 else 3
            for k in range(nsub):
                t = rnd.uniform(0.45, 0.9)
                idx = int(t * steps)
                p = pts[idx]
                ang = rnd.uniform(0, 2 * math.pi)
                nd = Vector((math.cos(ang), math.sin(ang), rnd.uniform(0.05, 0.55))) * 1.0 + d * 0.6
                branch(p, nd, length * rnd.uniform(0.55, 0.78), radii[idx] * 0.7, depth - 1)
        else:
            tips.append((pts[-1].copy(), d.copy()))

    top = Vector(trunk_pts[-1])
    nmain = 7
    for i in range(nmain):
        ang = 2 * math.pi * i / nmain + rnd.uniform(-0.3, 0.3)
        d = Vector((math.cos(ang), math.sin(ang), rnd.uniform(0.28, 0.75)))
        branch(top + Vector((0, 0, rnd.uniform(-0.3, 0.2))), d, spread * rnd.uniform(0.38, 0.5), trunk_r * 0.62, 2)
    # 葉團：每個枝尖幾團（中等），再在冠面包絡內撒許多小葉團，讓輪廓有細碎的起伏與空隙
    for p, d in tips:
        for k in range(rnd.randint(3, 5)):
            c = p + Vector((rnd.uniform(-2.4, 2.4), rnd.uniform(-2.4, 2.4), rnd.uniform(-0.6, 2.2)))
            rr = rnd.uniform(1.1, 2.2)
            sphere_bm(rr, tuple(c), (1.0, 1.0, rnd.uniform(0.55, 0.8)), 2, foliage, noise=0.3, seed=rnd.randint(0, 9999))
    n_fill = 150
    for _ in range(n_fill):
        a = rnd.uniform(0, 2 * math.pi)
        rad = spread * 0.62 * math.sqrt(rnd.random())
        zc = top.z + 1.3 + (1.0 - (rad / (spread * 0.62)) ** 2) * height * 0.38 * rnd.uniform(0.55, 1.0)
        c = Vector((math.cos(a) * rad, math.sin(a) * rad, zc))
        sphere_bm(rnd.uniform(0.5, 1.3), tuple(c), (1.0, 1.0, 0.7), 1, foliage, noise=0.35, seed=rnd.randint(0, 9999))
    # 把樹整體縮放到指定尺寸
    wo = mesh_obj("oak_wood", wood, bark)
    fo = mesh_obj("oak_crown", foliage, leaf)
    for o in (wo, fo):
        o.parent = None
    return wo, fo


def finish_oak(wo, fo, loc, scale, rot_z=0.0):
    root = bpy.data.objects.new("oak", None)
    link(root)
    root.location = loc
    root.scale = (scale, scale, scale)
    root.rotation_euler = (0, 0, rot_z)
    wo.parent = root
    fo.parent = root
    return root


# ----------------------------------------------------------------------------- 立石
def build_stone(length=3.4, width=1.15, height=0.95, seed=5):
    rnd = random.Random(seed)
    m = new_mat("stone_limestone")
    nt = m.node_tree
    b = bsdf_of(m)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    n1 = noise_tex(nt, tc.outputs["Object"], 2.2, 5.0)
    n2 = noise_tex(nt, tc.outputs["Object"], 11.0, 4.0)
    cr = ramp(nt, math_node(nt, "ADD", math_node(nt, "MULTIPLY", n1, 0.7), math_node(nt, "MULTIPLY", n2, 0.3)),
              [(0.2, lin("#9d9684")), (0.5, lin("#cbc3ae")), (0.8, lin("#e1d9c2"))])
    nt.links.new(cr, b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.92
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.9
    nt.links.new(n2, bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=4, radius=1.0)
    from mathutils import noise as mnoise
    for v in bm.verts:
        x, y, z = v.co
        # 長形粗石：平躺、上面略平、一端稍高，邊角鈍
        px, py, pz = x * length / 2, y * width / 2, z * height / 2
        if pz > 0:
            pz *= 0.82
        else:
            pz *= 0.55
        px *= 1.0 + 0.12 * math.sin(y * 2.0 + 1.0)
        n1 = mnoise.noise(Vector((px * 0.9 + seed, py * 0.9, pz * 0.9)))
        n2 = mnoise.noise(Vector((px * 3.1, py * 3.1 + seed, pz * 3.1)))
        d = 0.16 * n1 + 0.05 * n2
        v.co = Vector((px, py, pz)) + Vector((x, y, z)).normalized() * d
    bm.normal_update()
    ob = mesh_obj("stone", bm, m)
    return ob


# ----------------------------------------------------------------------------- 簡化人形
def _fig_mats():
    """三個材質槽：0 長袍（Object 顏色＋布紋）、1 皮膚、2 腰帶與頭巾邊（深色）。"""
    mats = []
    m = new_mat("fig_robe")
    nt = m.node_tree
    b = bsdf_of(m)
    oi = nt.nodes.new("ShaderNodeObjectInfo")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = noise_tex(nt, tc.outputs["Object"], 9.0, 3.0)
    col = mix_rgb(nt, oi.outputs["Color"], (0.55, 0.52, 0.5), math_node(nt, "MULTIPLY", math_node(nt, "SUBTRACT", 1.0, nz), 0.6), "MULTIPLY")
    nt.links.new(col, b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.92
    mats.append(m)
    mats.append(pbr("fig_skin", "#8a5b3d", 0.7))
    mats.append(pbr("fig_belt", "#4b3a2c", 0.9))
    return mats


def build_figure_meshes(kind_count=7, seed=1):
    """簡化人形（剪影到中景用）：寬肩、頭巾、袖、手、腰帶。身高約 1.7 m，原點在腳底，面向 -Y。"""
    rnd = random.Random(seed)
    mats = _fig_mats()
    meshes = []
    for k in range(kind_count):
        bm = bmesh.new()

        def part(fn, mi):
            n0 = len(bm.faces)
            fn()
            for f in list(bm.faces)[n0:]:
                f.material_index = mi

        h = rnd.uniform(1.62, 1.78) if k != 5 else 1.12
        s = h / 1.7
        child = k == 5
        # 長袍
        prof = [(0.31, 0.02), (0.29, 0.22), (0.25, 0.62), (0.205, 1.02), (0.2, 1.12), (0.215, 1.28), (0.2, 1.42), (0.12, 1.5), (0.06, 1.54)]
        part(lambda: lathe_bm([(r * s, z * s) for r, z in prof], 16, (1.12, 0.84), bm, closed_top=False), 0)
        # 肩與披肩
        part(lambda: sphere_bm(0.2 * s, (0, 0, 1.42 * s), (1.5, 0.78, 0.5), 1, bm), 0)
        # 腰帶
        part(lambda: lathe_bm([(0.215 * s, 1.07 * s), (0.225 * s, 1.1 * s), (0.225 * s, 1.15 * s), (0.215 * s, 1.18 * s)], 16, (1.12, 0.84), bm, closed_top=False), 2)
        # 頸、臉
        part(lambda: tube_bm([(0, 0, 1.5 * s), (0, -0.005, 1.6 * s)], [0.05 * s, 0.045 * s], 8, bm), 1)
        part(lambda: sphere_bm(0.1 * s, (0, -0.02 * s, 1.63 * s), (0.88, 0.95, 1.18), 1, bm), 1)
        # 頭巾：罩住頭頂與後腦，垂到肩
        part(lambda: sphere_bm(0.118 * s, (0, 0.012 * s, 1.655 * s), (1.0, 1.05, 1.0), 1, bm), 0)
        part(lambda: sphere_bm(0.1 * s, (0, 0.085 * s, 1.545 * s), (1.2, 0.55, 1.35), 1, bm), 0)
        part(lambda: tube_bm([(-0.1 * s, -0.03 * s, 1.68 * s), (0, -0.045 * s, 1.74 * s), (0.1 * s, -0.03 * s, 1.68 * s)], [0.018 * s] * 3, 6, bm, cap=False), 2)
        # 手臂與手
        swing = rnd.uniform(-0.12, 0.18)
        for sx in (-1, 1):
            sw = swing if sx > 0 else -swing
            pts = [(sx * 0.29 * s, 0.0, 1.41 * s), (sx * 0.335 * s, (-0.03 - 0.5 * sw) * s, 1.14 * s), (sx * 0.31 * s, (-0.08 - sw) * s, 0.92 * s)]
            part(lambda: tube_bm(pts, [0.062 * s, 0.056 * s, 0.045 * s], 8, bm), 0)
            part(lambda: sphere_bm(0.042 * s, pts[2], (1, 1, 1.2), 1, bm), 1)
        if k == 1:  # 牧杖
            part(lambda: tube_bm([(0.31 * s, -0.1 * s, 0.0), (0.31 * s, -0.1 * s, 1.85 * s)], [0.024, 0.02], 6, bm), 2)
        if k == 2:  # 背上的包袱
            part(lambda: sphere_bm(0.17 * s, (0, 0.19 * s, 1.2 * s), (1.0, 0.8, 1.1), 1, bm), 0)
        if k == 3:  # 頭頂水罐
            part(lambda: lathe_bm([(0.07, 1.74 * s), (0.12, 1.82 * s), (0.13, 1.9 * s), (0.08, 1.99 * s), (0.06, 2.04 * s)], 10, (1, 1), bm, closed_top=True), 2)
        if k == 4:  # 長杖
            part(lambda: tube_bm([(-0.31 * s, -0.1 * s, 0.0), (-0.31 * s, -0.1 * s, 2.0 * s)], [0.024, 0.02], 6, bm), 2)
        if k == 6:  # 懷抱嬰孩
            part(lambda: sphere_bm(0.1 * s, (0, -0.2 * s, 1.18 * s), (1.0, 0.9, 1.5), 1, bm), 0)
            part(lambda: sphere_bm(0.06 * s, (0, -0.22 * s, 1.34 * s), (1, 1, 1), 1, bm), 1)
        me = bpy.data.meshes.new(f"fig_{k}")
        bm.to_mesh(me)
        bm.free()
        for p in me.polygons:
            p.use_smooth = True
        for m in mats:
            me.materials.append(m)
        meshes.append(me)
    return meshes


# ----------------------------------------------------------------------------- 動物（簡化）
def build_sheep(seed=2):
    rnd = random.Random(seed)
    mat = new_mat("sheep_mat")
    nt = mat.node_tree
    b = bsdf_of(mat)
    oi = nt.nodes.new("ShaderNodeObjectInfo")
    nt.links.new(oi.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.95
    bm = bmesh.new()
    sphere_bm(0.3, (0, 0, 0.55), (1.35, 0.8, 0.85), 2, bm, noise=0.08, seed=1)
    sphere_bm(0.12, (0.42, 0, 0.62), (1.2, 0.8, 0.9), 1, bm)
    for sx in (-1, 1):
        for sy in (-1, 1):
            tube_bm([(sx * 0.25, sy * 0.13, 0.4), (sx * 0.25, sy * 0.13, 0.0)], [0.035, 0.022], 5, bm)
    me = bpy.data.meshes.new("sheep")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(mat)
    return me


def _objcolor_mat(name, rough=0.7):
    m = new_mat(name)
    nt = m.node_tree
    b = bsdf_of(m)
    oi = nt.nodes.new("ShaderNodeObjectInfo")
    nt.links.new(oi.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    return m


def _horse_into(bm, ox=0.0, oy=0.0, gallop=0.0, scale=1.0, part=None):
    """在 bm 內加一匹馬（面向 +X）。gallop：腿前後張開的程度（-1..1）。"""
    S = scale

    def P(x, y, z):
        return (ox + x * S, oy + y * S, z * S)

    n0 = len(bm.faces)
    sphere_bm(0.52 * S, P(0.0, 0, 1.2), (1.55, 0.56, 0.72), 2, bm)
    sphere_bm(0.46 * S, P(0.62, 0, 1.28), (1.0, 0.62, 0.85), 2, bm)         # 胸
    sphere_bm(0.5 * S, P(-0.62, 0, 1.25), (1.0, 0.6, 0.85), 2, bm)          # 臀
    tube_bm([P(0.75, 0, 1.38), P(1.02, 0, 1.68), P(1.18, 0, 1.92)], [0.24 * S, 0.17 * S, 0.12 * S], 8, bm)  # 頸
    tube_bm([P(1.18, 0, 1.94), P(1.5, 0, 1.78), P(1.72, 0, 1.52)], [0.13 * S, 0.1 * S, 0.065 * S], 8, bm)   # 頭
    sphere_bm(0.05 * S, P(1.14, 0.06, 2.08), (0.6, 0.6, 1.6), 1, bm)
    sphere_bm(0.05 * S, P(1.14, -0.06, 2.08), (0.6, 0.6, 1.6), 1, bm)
    g = gallop
    for (lx, ly, front) in ((0.62, 0.17, 1), (0.62, -0.17, 1), (-0.62, 0.17, 0), (-0.62, -0.17, 0)):
        sw = (0.42 if front else -0.38) * g * (1 if ly > 0 else -0.7)
        tube_bm([P(lx, ly, 1.1), P(lx + sw * 0.6, ly, 0.62), P(lx + sw, ly, 0.06)], [0.11 * S, 0.065 * S, 0.05 * S], 6, bm)
    tube_bm([P(-1.0, 0, 1.45), P(-1.3, 0, 1.3), P(-1.42 - 0.15 * g, 0, 0.75)], [0.07 * S, 0.075 * S, 0.035 * S], 6, bm)  # 尾
    tube_bm([P(0.82, 0, 1.72), P(1.0, 0, 1.98), P(1.15, 0, 2.02)], [0.03 * S, 0.04 * S, 0.03 * S], 5, bm)  # 鬃
    return bm


def build_horse(seed=2, gallop=0.6):
    mat = _objcolor_mat("horse_mat", 0.55)
    bm = bmesh.new()
    _horse_into(bm, gallop=gallop)
    me = bpy.data.meshes.new("horse")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(mat)
    return me


def build_chariot_team(gallop=0.7, seed=1, name="team"):
    """兩匹馬拉一輛戰車，面向 +X。材質槽：0 馬（Object 顏色）、1 戰車木與金、2 御者。腳底在 z=0。"""
    mats = [_objcolor_mat("team_horse", 0.55), pbr("team_wood", "#8a6a3c", 0.55, 0.0), pbr("team_crew", "#b9a888", 0.8)]
    bm = bmesh.new()

    def part(fn, mi):
        n0 = len(bm.faces)
        fn()
        for f in list(bm.faces)[n0:]:
            f.material_index = mi

    for oy, gp in ((0.55, gallop), (-0.55, gallop * 0.8 + 0.1)):
        part(lambda oy=oy, gp=gp: _horse_into(bm, ox=2.3, oy=oy, gallop=gp, scale=1.0), 0)
    # 軛與轅
    part(lambda: tube_bm([(0.2, 0, 0.95), (2.3, 0, 1.55)], [0.05, 0.05], 6, bm), 1)
    part(lambda: tube_bm([(1.95, -0.7, 1.62), (1.95, 0.7, 1.62)], [0.045, 0.045], 6, bm), 1)
    # 車廂：前低後高的弧形欄板
    part(lambda: box_bm((1.0, 1.15, 0.12), (-0.35, 0, 0.55), bm), 1)
    part(lambda: box_bm((0.08, 1.15, 0.65), (0.15, 0, 0.9), bm), 1)
    for sy in (-0.57, 0.57):
        part(lambda sy=sy: box_bm((0.95, 0.06, 0.5), (-0.38, sy, 0.88), bm), 1)
        # 輪
        cx, cz, R = -0.35, 0.5, 0.5
        for k in range(8):
            a = math.pi * k / 4
            part(lambda a=a, sy=sy: tube_bm([(cx + R * math.cos(a), sy * 1.12, cz + R * math.sin(a)), (cx - R * math.cos(a), sy * 1.12, cz - R * math.sin(a))], [0.022, 0.022], 5, bm, cap=False), 1)
        for k in range(20):
            a0, a1 = 2 * math.pi * k / 20, 2 * math.pi * (k + 1) / 20
            part(lambda a0=a0, a1=a1, sy=sy: tube_bm([(cx + R * math.cos(a0), sy * 1.12, cz + R * math.sin(a0)), (cx + R * math.cos(a1), sy * 1.12, cz + R * math.sin(a1))], [0.05, 0.05], 5, bm, cap=False), 1)
    tube_bm([(-0.35, -0.7, 0.5), (-0.35, 0.7, 0.5)], [0.04, 0.04], 6, bm)  # 車軸
    # 御者與弓手：兩個站立的人
    for oy, lean in ((0.22, 0.0), (-0.22, 0.0)):
        part(lambda oy=oy: lathe_bm([(0.19, 0.62), (0.2, 1.0), (0.2, 1.3), (0.15, 1.48), (0.06, 1.54)], 10, (1.0, 0.8), bm, offset=(-0.4, oy, 0.0), closed_top=False), 2)
        part(lambda oy=oy: sphere_bm(0.1, (-0.4, oy, 1.62), (1, 1, 1.1), 1, bm), 2)
        part(lambda oy=oy: sphere_bm(0.125, (-0.4, oy, 1.7), (1, 1, 0.8), 1, bm), 1)      # 王冠式頭盔
        part(lambda oy=oy: tube_bm([(-0.4, oy, 1.4), (-0.2, oy, 1.32), (0.0, oy, 1.28)], [0.05, 0.045, 0.04], 6, bm), 2)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    for m in mats:
        me.materials.append(m)
    return me


def build_cart(name="cart"):
    """雙輪牛車（羊皮與物品堆在上面），面向 +X。材質：0 木、1 貨物（Object 顏色）。"""
    mats = [pbr("cart_wood", "#6e5336", 0.8), _objcolor_mat("cart_load", 0.9)]
    bm = bmesh.new()

    def part(fn, mi):
        n0 = len(bm.faces)
        fn()
        for f in list(bm.faces)[n0:]:
            f.material_index = mi

    part(lambda: box_bm((2.4, 1.4, 0.12), (0, 0, 0.8), bm), 0)
    for sy in (-0.72, 0.72):
        for k in range(10):
            a = math.pi * k / 5
            part(lambda a=a, sy=sy: tube_bm([(0.5 * math.cos(a) * 1.0, sy, 0.62 + 0.5 * math.sin(a)), (-0.5 * math.cos(a), sy, 0.62 - 0.5 * math.sin(a))], [0.03, 0.03], 5, bm, cap=False), 0)
    part(lambda: tube_bm([(1.2, 0, 0.85), (3.4, 0, 0.95)], [0.05, 0.05], 6, bm), 0)
    part(lambda: sphere_bm(0.8, (-0.1, 0, 1.25), (1.2, 0.75, 0.6), 2, bm, noise=0.12, seed=3), 1)
    part(lambda: sphere_bm(0.45, (0.7, 0.2, 1.2), (1.0, 0.9, 0.7), 2, bm, noise=0.12, seed=5), 1)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    for m in mats:
        me.materials.append(m)
    return me


def build_chariot():
    mat = new_mat("chariot_mat")
    nt = mat.node_tree
    b = bsdf_of(mat)
    oi = nt.nodes.new("ShaderNodeObjectInfo")
    nt.links.new(oi.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.7
    bm = bmesh.new()
    box_bm((1.0, 1.1, 0.9), (-0.4, 0, 1.0), bm)
    box_bm((0.1, 1.1, 0.5), (0.05, 0, 1.2), bm)
    tube_bm([(0.0, 0, 0.9), (2.2, 0, 1.15)], [0.05, 0.05], 6, bm)                 # 轅
    for sy in (-0.62, 0.62):
        # 輪（八輻）
        for k in range(8):
            a = math.pi * k / 4
            tube_bm([(-0.4 + 0.45 * math.cos(a), sy, 0.5 + 0.45 * math.sin(a)), (-0.4 - 0.45 * math.cos(a), sy, 0.5 - 0.45 * math.sin(a))], [0.025, 0.025], 5, bm, cap=False)
        ring = []
        for k in range(18):
            a0 = 2 * math.pi * k / 18
            a1 = 2 * math.pi * (k + 1) / 18
            tube_bm([(-0.4 + 0.5 * math.cos(a0), sy, 0.5 + 0.5 * math.sin(a0)), (-0.4 + 0.5 * math.cos(a1), sy, 0.5 + 0.5 * math.sin(a1))], [0.05, 0.05], 5, bm, cap=False)
    # 御者
    lathe_bm([(0.22, 1.4), (0.2, 1.8), (0.1, 2.0)], 8, (1, 0.8), bm, offset=(-0.45, 0, 0.0))
    sphere_bm(0.1, (-0.45, 0, 2.18), (1, 1, 1.1), 1, bm)
    me = bpy.data.meshes.new("chariot")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    for p in me.polygons:
        p.use_smooth = True
    return me


# ----------------------------------------------------------------------------- 帳棚與小神像（第 2 節）
def build_tent(length=7.6, depth=3.3, ridge=2.05, front_h=1.6, name="tent"):
    """黑色山羊毛帳棚：一面長邊（朝 -y）敞開，其餘三面垂到地。原點在帳棚地面中心。
    材質槽：0 山羊毛布、1 木柱、2 地墊。回傳網格。"""
    import numpy as np

    mats = [new_mat("tent_hair"), pbr("tent_pole", "#6a4e33", 0.8), _objcolor_mat("tent_mat", 0.9)]
    nt = mats[0].node_tree
    b = bsdf_of(mats[0])
    tc = nt.nodes.new("ShaderNodeTexCoord")
    wv = nt.nodes.new("ShaderNodeTexWave")
    wv.wave_type = "BANDS"
    wv.bands_direction = "Y"
    wv.inputs["Scale"].default_value = 3.0
    wv.inputs["Distortion"].default_value = 2.0
    nt.links.new(tc.outputs["Object"], wv.inputs["Vector"])
    n1 = noise_tex(nt, tc.outputs["Object"], 14.0, 4.0)
    cr = ramp(nt, math_node(nt, "ADD", math_node(nt, "MULTIPLY", wv.outputs["Fac"], 0.6), math_node(nt, "MULTIPLY", n1, 0.5)),
              [(0.2, lin("#14100c")), (0.55, lin("#2b2219")), (0.9, lin("#4a3b2b"))])
    nt.links.new(cr, b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.95
    bm = bmesh.new()

    def part(fn, mi):
        n0 = len(bm.faces)
        fn()
        for f in list(bm.faces)[n0:]:
            f.material_index = mi

    nu, nv = 16, 34
    us = np.linspace(0, 1, nu)
    vs = np.linspace(0, 1, nv)
    prof_u = [0.0, 0.1, 0.3, 0.65, 1.0]
    prof_z = [0.0, ridge * 0.62, ridge, ridge * 0.9, front_h]

    def zprof(u):
        return float(np.interp(u, prof_u, prof_z))

    verts = {}
    for i, u in enumerate(us):
        for j, v in enumerate(vs):
            y = depth / 2 - u * depth
            x = (v - 0.5) * length
            sag = 0.16 * math.sin(math.pi * ((v * 2.0) % 1.0)) * (0.3 + 0.7 * u)
            z = max(zprof(u) - sag, 0.0) + 0.04 * math.sin(v * 31.0 + u * 5.0)
            verts[(i, j)] = bm.verts.new((x, y, z))
    n0 = len(bm.faces)
    for i in range(nu - 1):
        for j in range(nv - 1):
            bm.faces.new((verts[(i, j)], verts[(i, j + 1)], verts[(i + 1, j + 1)], verts[(i + 1, j)]))
    for f in list(bm.faces)[n0:]:
        f.material_index = 0
    # 兩端山牆
    for j, sgn in ((0, -1), (nv - 1, 1)):
        top = [verts[(i, j)] for i in range(nu)]
        base_pts = [bm.verts.new((top[-1].co.x, top[-1].co.y, 0.0)), bm.verts.new((top[0].co.x, top[0].co.y, 0.0))]
        try:
            f = bm.faces.new(top + base_pts if sgn > 0 else (top + base_pts)[::-1])
            f.material_index = 0
        except ValueError:
            pass
    # 柱
    for xp in (-length / 2, 0.0, length / 2):
        part(lambda xp=xp: tube_bm([(xp, depth / 2 - 0.1 * depth * 0.0 - 0.05 - depth * 0.3, 0.0), (xp, depth / 2 - 0.3 * depth, ridge - 0.02)], [0.05, 0.04], 6, bm), 1)
        part(lambda xp=xp: tube_bm([(xp, -depth / 2 + 0.08, 0.0), (xp, -depth / 2 + 0.08, front_h)], [0.045, 0.04], 6, bm), 1)
    # 地墊
    part(lambda: box_bm((length - 0.4, depth - 0.3, 0.03), (0, 0, 0.02), bm), 2)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = False
    for m in mats:
        me.materials.append(m)
    return me


def build_idols():
    """幾尊小神像（陶土與石頭，不命名是哪一位神）。回傳 {名稱: mesh}。高度約 0.3–0.5 m，原點在底面中心。"""
    clay = pbr("idol_clay", "#a86b43", 0.8)
    stone = pbr("idol_stone", "#bfb398", 0.85)
    dark = pbr("idol_dark", "#3a322b", 0.7)
    out = {}

    def finish(name, bm, mat):
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        for p in me.polygons:
            p.use_smooth = True
        me.materials.append(mat)
        out[name] = me

    bm = bmesh.new()   # 站立的人形像：長袍身 + 圓頭 + 高帽
    lathe_bm([(0.075, 0.0), (0.07, 0.12), (0.05, 0.26), (0.055, 0.32), (0.04, 0.36)], 12, (1.0, 0.8), bm, closed_top=False)
    sphere_bm(0.045, (0, 0, 0.395), (1, 1, 1.1), 1, bm)
    lathe_bm([(0.05, 0.42), (0.04, 0.46), (0.025, 0.52), (0.0, 0.54)], 10, (1, 1), bm, closed_top=True)
    tube_bm([(-0.06, 0, 0.3), (-0.12, -0.02, 0.22)], [0.016, 0.014], 6, bm)
    tube_bm([(0.06, 0, 0.3), (0.09, -0.04, 0.34)], [0.016, 0.014], 6, bm)
    finish("idol_standing", bm, clay)
    bm = bmesh.new()   # 坐像
    box_bm((0.16, 0.12, 0.08), (0, 0, 0.04), bm)
    lathe_bm([(0.06, 0.08), (0.055, 0.18), (0.04, 0.26)], 10, (1.0, 0.8), bm, closed_top=False)
    sphere_bm(0.04, (0, 0, 0.3), (1, 1, 1.1), 1, bm)
    lathe_bm([(0.055, 0.32), (0.04, 0.36), (0.0, 0.38)], 10, (1, 1), bm, closed_top=True)
    finish("idol_seated", bm, stone)
    bm = bmesh.new()   # 牛形像
    sphere_bm(0.1, (0, 0, 0.18), (1.5, 0.7, 0.85), 1, bm)
    sphere_bm(0.055, (0.15, 0, 0.23), (1.1, 0.9, 1.0), 1, bm)
    tube_bm([(0.17, 0.035, 0.28), (0.2, 0.08, 0.34), (0.22, 0.07, 0.4)], [0.012, 0.01, 0.006], 5, bm)
    tube_bm([(0.17, -0.035, 0.28), (0.2, -0.08, 0.34), (0.22, -0.07, 0.4)], [0.012, 0.01, 0.006], 5, bm)
    for sx, sy in ((0.1, 0.05), (0.1, -0.05), (-0.1, 0.05), (-0.1, -0.05)):
        tube_bm([(sx, sy, 0.11), (sx, sy, 0.0)], [0.02, 0.016], 5, bm)
    box_bm((0.34, 0.16, 0.02), (0.02, 0, 0.01), bm)
    finish("idol_bull", bm, dark)
    bm = bmesh.new()   # 石柱像（帶簡單臉形）
    lathe_bm([(0.07, 0.0), (0.06, 0.2), (0.05, 0.4), (0.03, 0.5)], 6, (1.0, 0.7), bm, closed_top=True)
    sphere_bm(0.03, (0, -0.04, 0.38), (1.2, 0.5, 1.4), 1, bm)
    finish("idol_pillar", bm, stone)
    bm = bmesh.new()   # 小型女像（雙臂交抱）
    lathe_bm([(0.05, 0.0), (0.045, 0.1), (0.035, 0.2), (0.04, 0.26)], 10, (1.0, 0.8), bm, closed_top=False)
    sphere_bm(0.034, (0, 0, 0.29), (1, 1, 1.1), 1, bm)
    tube_bm([(-0.04, -0.03, 0.2), (0.0, -0.05, 0.18), (0.04, -0.03, 0.2)], [0.012, 0.012, 0.012], 5, bm)
    finish("idol_small", bm, clay)
    return out
