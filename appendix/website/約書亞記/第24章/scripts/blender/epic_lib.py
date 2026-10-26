"""史詩段落樣張共用函式庫（Blender 5.2 背景模式）。

- numpy 的 linalg 擴充模組被應用程式控制封鎖，這裡先放一個空殼，讓 numpy 其餘部分（FBX/glTF 匯入器要用）可以載入。
- 地形由 epic_prep.py（系統 Python）預先產生，這裡只讀二進位檔。
"""
import array
import json
import math
import os
import random
import sys
import types

# ---- numpy 空殼（只替換被封鎖的 _umath_linalg，其餘照常） ----
class _Stub(types.ModuleType):
    def __getattr__(self, n):
        if n.startswith("__"):
            raise AttributeError(n)

        def f(*a, **k):
            raise RuntimeError("linalg stub: " + n)

        return f


sys.modules.setdefault("numpy.linalg._umath_linalg", _Stub("numpy.linalg._umath_linalg"))
import numpy as np  # noqa: E402

import bmesh  # noqa: E402
import bpy  # noqa: E402
import bpy  # noqa: E402
from mathutils import Euler, Matrix, Quaternion, Vector  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
CACHE = os.path.join(ROOT, "lab", "renders", "epic", "_cache")
ASSETS = os.path.join(HERE, "assets")


# ----------------------------------------------------------------------------- 場景
def fresh_scene(name="epic"):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.name = name
    sc.render.engine = "BLENDER_EEVEE"
    return sc


def srgb(hex_col):
    c = [int(hex_col[i : i + 2], 16) / 255.0 for i in (1, 3, 5)]
    return [((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c]


def link(obj, coll=None):
    (coll or bpy.context.scene.collection).objects.link(obj)
    return obj


# ----------------------------------------------------------------------------- 材質小工具
def new_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    return m


def bsdf_of(m):
    return next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def pbr(name, hex_col, rough=0.8, metal=0.0, spec=0.35):
    m = new_mat(name)
    b = bsdf_of(m)
    b.inputs["Base Color"].default_value = (*srgb(hex_col), 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    for k in ("Specular IOR Level", "Specular"):
        if k in b.inputs:
            b.inputs[k].default_value = spec
            break
    m.diffuse_color = (*srgb(hex_col), 1)
    return m


def obj_color_mat(name, rough=0.85, noise=0.0, hem=False):
    """用 Object 顏色上色的材質（群眾共用一個網格、各自換色）。"""
    m = new_mat(name)
    nt = m.node_tree
    b = bsdf_of(m)
    oi = nt.nodes.new("ShaderNodeObjectInfo")
    if noise > 0:
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = 18.0
        nz.inputs["Detail"].default_value = 3.0
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        mx = nt.nodes.new("ShaderNodeMix")
        mx.data_type = "RGBA"
        mx.blend_type = "MULTIPLY"
        mx.inputs[0].default_value = noise
        nt.links.new(oi.outputs["Color"], mx.inputs[6])
        nt.links.new(nz.outputs["Color"], mx.inputs[7])
        nt.links.new(mx.outputs[2], b.inputs["Base Color"])
    else:
        nt.links.new(oi.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    return m


def mix_rgb(nt, a, b, fac, blend="MIX"):
    mx = nt.nodes.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    mx.blend_type = blend
    if isinstance(fac, (int, float)):
        mx.inputs[0].default_value = fac
    else:
        nt.links.new(fac, mx.inputs[0])
    for idx, v in ((6, a), (7, b)):
        if isinstance(v, (tuple, list)):
            mx.inputs[idx].default_value = (*v, 1) if len(v) == 3 else v
        else:
            nt.links.new(v, mx.inputs[idx])
    return mx.outputs[2]


def ramp(nt, fac, stops):
    r = nt.nodes.new("ShaderNodeValToRGB")
    el = r.color_ramp.elements
    while len(el) > 1:
        el.remove(el[-1])
    el[0].position = stops[0][0]
    el[0].color = (*stops[0][1], 1)
    for pos, col in stops[1:]:
        e = el.new(pos)
        e.color = (*col, 1)
    nt.links.new(fac, r.inputs["Fac"])
    return r.outputs["Color"]


def math_node(nt, op, a, b=None, clamp=False):
    n = nt.nodes.new("ShaderNodeMath")
    n.operation = op
    n.use_clamp = clamp
    for i, v in enumerate((a, b)):
        if v is None:
            continue
        if isinstance(v, (int, float)):
            n.inputs[i].default_value = v
        else:
            nt.links.new(v, n.inputs[i])
    return n.outputs[0]


def noise_tex(nt, vec, scale, detail=4.0, rough=0.5, w=None):
    n = nt.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = scale
    n.inputs["Detail"].default_value = detail
    n.inputs["Roughness"].default_value = rough
    nt.links.new(vec, n.inputs["Vector"])
    return n.outputs["Fac"]


# ----------------------------------------------------------------------------- 地形
def load_layer(scene_dir, info, smooth=True):
    base = os.path.join(scene_dir, info["name"])
    nv, nq = info["nv"], info["nq"]
    v = np.fromfile(base + ".v.bin", dtype=np.float32).reshape(-1, 3)
    q = np.fromfile(base + ".q.bin", dtype=np.uint32).reshape(-1, 4)
    veg = np.fromfile(base + ".veg.bin", dtype=np.float32)
    sea = np.fromfile(base + ".sea.bin", dtype=np.float32)
    me = bpy.data.meshes.new("terrain_" + info["name"])
    me.vertices.add(nv)
    me.vertices.foreach_set("co", v.ravel())
    me.polygons.add(nq)
    me.loops.add(nq * 4)
    me.loops.foreach_set("vertex_index", q.ravel().astype(np.int32))
    me.polygons.foreach_set("loop_start", np.arange(0, nq * 4, 4, dtype=np.int32))
    if smooth:
        me.polygons.foreach_set("use_smooth", np.ones(nq, dtype=bool))
    me.update(calc_edges=True)
    a = me.attributes.new("veg", "FLOAT", "POINT")
    a.data.foreach_set("value", veg)
    a = me.attributes.new("sea", "FLOAT", "POINT")
    a.data.foreach_set("value", sea)
    ob = bpy.data.objects.new("terrain_" + info["name"], me)
    link(ob)
    return ob


def load_terrain(scene):
    d = os.path.join(CACHE, scene)
    meta = json.load(open(os.path.join(d, "meta.json"), encoding="utf-8"))
    return meta, [load_layer(d, ly) for ly in meta["layers"]]


class Ground:
    """對地形做射線取高，放物件用。"""

    def __init__(self, objs):
        dg = bpy.context.evaluated_depsgraph_get()
        self.trees = [(BVHTree.FromObject(o, dg), o) for o in objs]

    def z(self, x, y, top=6000.0):
        best = None
        for t, o in self.trees:
            hit = t.ray_cast(Vector((x, y, top)), Vector((0, 0, -1)), 2 * top)
            if hit[0] is not None:
                if best is None or hit[0].z > best.z:
                    best = hit[0]
        return None if best is None else best.z

    def zn(self, x, y):
        best = None
        for t, o in self.trees:
            hit = t.ray_cast(Vector((x, y, 6000.0)), Vector((0, 0, -1)), 12000.0)
            if hit[0] is not None and (best is None or hit[0].z > best[0].z):
                best = hit
        return best  # (location, normal, index, dist) or None


# ----------------------------------------------------------------------------- 天空與光
def setup_world(sun_elev_deg, sun_az_deg, horizon="#f2b98a", mid="#8aa3c4", zenith="#27406b",
                ground="#6b5a4c", glow="#ffb36b", glow_k=1.2, disc_k=80.0, disc_deg=0.9, strength=1.0,
                sun_energy=4.0, sun_color=(1.0, 0.82, 0.6), sun_size_deg=0.6,
                fog_density=0.0, fog_color=(0.7, 0.78, 0.9), fog_aniso=0.35, haze_k=1.0, clouds=0.0, cloud_scale=2.2, cloud_seed=0.0, fill=0.0, fill_color=(1.0, 0.9, 0.8), cloud_lit=0.0):
    """自製天空：地平線暖色漸層到天頂深藍，加上沿太陽方向的光暈與日盤。
    sun_az_deg 為數學角（0 = 東，90 = 北，180 = 西，270 = 南）。回傳 (world, sun_obj, 指向太陽的單位向量)。"""
    sc = bpy.context.scene
    w = bpy.data.worlds.new("epic_world")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    el = math.radians(sun_elev_deg)
    az = math.radians(sun_az_deg)
    d = Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nrm = nt.nodes.new("ShaderNodeVectorMath")
    nrm.operation = "NORMALIZE"
    nt.links.new(tc.outputs["Generated"], nrm.inputs[0])
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(nrm.outputs[0], sep.inputs[0])
    dot = nt.nodes.new("ShaderNodeVectorMath")
    dot.operation = "DOT_PRODUCT"
    dot.inputs[1].default_value = d
    nt.links.new(nrm.outputs[0], dot.inputs[0])
    z = sep.outputs["Z"]
    # 垂直漸層：地平線 -> 中段 -> 天頂（上半球），下半球用地面色
    zc = math_node(nt, "MAXIMUM", z, 0.0)
    zs = math_node(nt, "POWER", zc, 0.62)
    sky = ramp(nt, zs, [(0.0, srgb(horizon)), (0.45, srgb(mid)), (1.0, srgb(zenith))])
    below = math_node(nt, "LESS_THAN", z, 0.0)
    col = mix_rgb(nt, sky, srgb(ground), math_node(nt, "MULTIPLY", below, 1.0))
    # 光暈
    s = math_node(nt, "MAXIMUM", dot.outputs["Value"], 0.0)
    g1 = math_node(nt, "MULTIPLY", math_node(nt, "POWER", s, 6.0), glow_k)
    g2 = math_node(nt, "MULTIPLY", math_node(nt, "POWER", s, 60.0), glow_k * 3.0)
    gl = math_node(nt, "ADD", g1, g2)
    # 地平線上的暖霧帶（太陽那一側更亮）
    hz = math_node(nt, "MULTIPLY", math_node(nt, "SUBTRACT", 1.0, math_node(nt, "MINIMUM", math_node(nt, "ABSOLUTE", z), 1.0)), 0.0)
    col = mix_rgb(nt, col, srgb(glow), math_node(nt, "MINIMUM", gl, 1.0))
    col = mix_rgb(nt, col, tuple(v * 1.0 for v in srgb(glow)), 0.0)
    # 雲：以天空方向投影到水平面的雜訊，越靠近太陽越亮
    if clouds > 0:
        xy = nt.nodes.new("ShaderNodeCombineXYZ")
        sx = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(nrm.outputs[0], sx.inputs[0])
        den = math_node(nt, "ADD", math_node(nt, "MAXIMUM", sx.outputs["Z"], 0.0), 0.22)
        nt.links.new(math_node(nt, "DIVIDE", sx.outputs["X"], den), xy.inputs["X"])
        nt.links.new(math_node(nt, "DIVIDE", sx.outputs["Y"], den), xy.inputs["Y"])
        xy.inputs["Z"].default_value = cloud_seed
        nn = noise_tex(nt, xy.outputs["Vector"], cloud_scale, 5.0, 0.55)
        # 拉長成帶狀雲
        cm = nt.nodes.new("ShaderNodeMapRange")
        cm.interpolation_type = "SMOOTHSTEP"
        cm.inputs["From Min"].default_value = 0.5 - 0.12 * clouds
        cm.inputs["From Max"].default_value = 0.62
        nt.links.new(nn, cm.inputs["Value"])
        cmask = math_node(nt, "MULTIPLY", cm.outputs["Result"], math_node(nt, "MINIMUM", math_node(nt, "MULTIPLY", sx.outputs["Z"], 9.0), 1.0))
        near = math_node(nt, "MINIMUM", math_node(nt, "MULTIPLY", math_node(nt, "POWER", s, 3.0), 1.6), 1.0)
        if cloud_lit > 0:      # 光源在鏡頭後方時，雲底仍被地平線一帶的暖光照亮（越靠近地平線越亮）
            lowc = math_node(nt, "SUBTRACT", 1.0, math_node(nt, "MINIMUM", math_node(nt, "MULTIPLY", sx.outputs["Z"], 3.2), 1.0))
            near = math_node(nt, "MINIMUM", math_node(nt, "ADD", near, math_node(nt, "MULTIPLY", lowc, cloud_lit)), 1.0)
        ccol = mix_rgb(nt, srgb("#7d7c92"), tuple(v * 2.2 for v in srgb(glow)), near)
        col = mix_rgb(nt, col, ccol, math_node(nt, "MULTIPLY", cmask, 0.85))
    # 日盤（HDR）
    c0 = math.cos(math.radians(disc_deg))
    disc = nt.nodes.new("ShaderNodeMapRange")
    disc.interpolation_type = "SMOOTHSTEP"
    disc.inputs["From Min"].default_value = c0 - 0.00008
    disc.inputs["From Max"].default_value = c0 + 0.00004
    nt.links.new(dot.outputs["Value"], disc.inputs["Value"])
    emit_sun = nt.nodes.new("ShaderNodeEmission")
    bgn = nt.nodes.new("ShaderNodeBackground")
    bgn.inputs["Strength"].default_value = strength
    nt.links.new(col, bgn.inputs["Color"])
    sunbg = nt.nodes.new("ShaderNodeBackground")
    sunbg.inputs["Color"].default_value = (1.0, 0.86, 0.62, 1)
    nt.links.new(math_node(nt, "MULTIPLY", disc.outputs["Result"], disc_k), sunbg.inputs["Strength"])
    add = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(bgn.outputs["Background"], add.inputs[0])
    nt.links.new(sunbg.outputs["Background"], add.inputs[1])
    out = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(add.outputs["Shader"], out.inputs["Surface"])
    if fog_density > 0:
        pv = nt.nodes.new("ShaderNodeVolumePrincipled")
        pv.inputs["Color"].default_value = (*fog_color, 1)
        pv.inputs["Density"].default_value = fog_density
        if "Anisotropy" in pv.inputs:
            pv.inputs["Anisotropy"].default_value = fog_aniso
        nt.links.new(pv.outputs["Volume"], out.inputs["Volume"])
    ld = bpy.data.lights.new("sun", "SUN")
    ld.energy = sun_energy
    ld.color = sun_color
    ld.angle = math.radians(sun_size_deg * 1.2)
    lo = bpy.data.objects.new("sun", ld)
    link(lo)
    lo.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    if fill > 0:
        fl = bpy.data.lights.new("fill", "SUN")
        fl.energy = fill
        fl.color = fill_color
        fl.angle = math.radians(25)
        fo = bpy.data.objects.new("fill", fl)
        link(fo)
        fd = Vector((-d.x, -d.y, 0.0)).normalized() * math.cos(math.radians(28)) + Vector((0, 0, math.sin(math.radians(28))))
        fo.rotation_euler = (-fd).to_track_quat("-Z", "Y").to_euler()
        try:
            fl.use_shadow = False
        except Exception:
            pass
    return w, lo, d


def set_camera(loc, target, lens=28.0, roll=0.0, clip=(0.3, 400000.0), name="cam", sensor=36.0):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.sensor_width = sensor
    cd.clip_start, cd.clip_end = clip
    co = bpy.data.objects.new(name, cd)
    link(co)
    co.location = Vector(loc)
    dirv = Vector(target) - Vector(loc)
    q = dirv.to_track_quat("-Z", "Y")
    co.rotation_euler = q.to_euler()
    if roll:
        co.rotation_euler.rotate_axis("Z", roll)
    bpy.context.scene.camera = co
    return co


def render_settings(w, h, samples=48, volumetric=True, vol_samples=48, tile=2, raytrace=True,
                    exposure=-3.0, look_gamma=1.0, shadows_res=1.0):
    sc = bpy.context.scene
    r = sc.render
    r.engine = "BLENDER_EEVEE"
    r.resolution_x, r.resolution_y, r.resolution_percentage = w, h, 100
    r.image_settings.file_format = "PNG"
    r.image_settings.color_mode = "RGB"
    r.image_settings.color_depth = "16"
    ev = sc.eevee
    ev.taa_render_samples = samples
    ev.use_raytracing = raytrace
    ev.use_shadows = True
    try:
        ev.shadow_ray_count = 2
        ev.shadow_step_count = 8
        ev.shadow_resolution_scale = shadows_res
    except Exception:
        pass
    try:
        ev.volumetric_tile_size = str(tile)
        ev.volumetric_samples = vol_samples
        ev.use_volumetric_shadows = True
        ev.volumetric_shadow_samples = 32
        ev.volumetric_start = 0.5
        ev.volumetric_end = 6000.0
        ev.use_volume_custom_range = True
    except Exception as e:
        print("vol settings:", e)
    try:
        ev.use_fast_gi = True
        ev.fast_gi_method = "AMBIENT_OCCLUSION_ONLY"
    except Exception as e:
        print("fast gi:", e)
    vs = sc.view_settings
    vs.view_transform = "Standard"
    vs.exposure = exposure
    try:
        vs.look = "None"
    except Exception:
        pass
    sc["hdr_exposure"] = exposure


def render_to(path):
    """渲染並存成原始 float32 線性資料（<path 去副檔名>.f32，形狀 H x W x 4）。回傳秒數。"""
    import time

    sc = bpy.context.scene
    base = os.path.abspath(path)
    if base.lower().endswith(".png"):
        base = base[:-4]
    os.makedirs(os.path.dirname(base), exist_ok=True)
    exr = base + "__tmp.exr"
    r = sc.render
    r.image_settings.file_format = "OPEN_EXR"
    r.image_settings.color_depth = "32"
    r.image_settings.color_mode = "RGBA"
    sc.render.filepath = exr
    t = time.time()
    bpy.ops.render.render(write_still=True)
    dt = time.time() - t
    img = bpy.data.images.load(exr)
    w, h = img.size
    buf = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(buf)
    buf.reshape(h, w, 4).tofile(base + ".f32")
    bpy.data.images.remove(img)
    try:
        os.remove(exr)
    except OSError:
        pass
    print(f"RENDER {os.path.basename(base)} {dt:.1f}s")
    return dt


# ----------------------------------------------------------------------------- 幾何小工具
def mesh_obj(name, bm_or_me, mat=None, coll=None, smooth=True):
    if isinstance(bm_or_me, bmesh.types.BMesh):
        me = bpy.data.meshes.new(name)
        bm_or_me.to_mesh(me)
        bm_or_me.free()
    else:
        me = bm_or_me
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    if mat is not None:
        me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def lathe_bm(profile, seg=24, squash=(1.0, 1.0), bm=None, offset=(0, 0, 0), closed_top=True):
    """profile: [(r, z), ...] 由下往上；squash=(x,y) 橫截面壓扁。"""
    bm = bm or bmesh.new()
    rings = []
    for r, z in profile:
        ring = []
        for i in range(seg):
            a = 2 * math.pi * i / seg
            ring.append(bm.verts.new((offset[0] + r * squash[0] * math.cos(a), offset[1] + r * squash[1] * math.sin(a), offset[2] + z)))
        rings.append(ring)
    for k in range(len(rings) - 1):
        for i in range(seg):
            j = (i + 1) % seg
            bm.faces.new((rings[k][i], rings[k][j], rings[k + 1][j], rings[k + 1][i]))
    if closed_top:
        c = bm.verts.new((offset[0], offset[1], offset[2] + profile[-1][1]))
        for i in range(seg):
            bm.faces.new((rings[-1][i], rings[-1][(i + 1) % seg], c)) if False else bm.faces.new((rings[-1][(i + 1) % seg], rings[-1][i], c))
    return bm


def sphere_bm(r, loc=(0, 0, 0), scale=(1, 1, 1), subs=2, bm=None, noise=0.0, seed=0):
    bm = bm or bmesh.new()
    rnd = random.Random(seed)
    m = Matrix.Translation(loc) @ Matrix.Diagonal((*scale, 1))
    res = bmesh.ops.create_icosphere(bm, subdivisions=subs, radius=r, matrix=m)
    if noise > 0:
        for v in res["verts"]:
            d = (v.co - Vector(loc))
            v.co += d.normalized() * rnd.uniform(-noise, noise) * r
    return bm


def tube_bm(points, radii, seg=10, bm=None, cap=True):
    bm = bm or bmesh.new()
    rings = []
    n = len(points)
    for i, (p, r) in enumerate(zip(points, radii)):
        p = Vector(p)
        if i < n - 1:
            t = (Vector(points[i + 1]) - p).normalized()
        else:
            t = (p - Vector(points[i - 1])).normalized()
        ref = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
        a = t.cross(ref).normalized()
        b = t.cross(a).normalized()
        ring = []
        for k in range(seg):
            th = 2 * math.pi * k / seg
            ring.append(bm.verts.new(p + (a * math.cos(th) + b * math.sin(th)) * r))
        rings.append(ring)
    for i in range(n - 1):
        for k in range(seg):
            k2 = (k + 1) % seg
            bm.faces.new((rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k]))
    if cap:
        for ring, rev in ((rings[0], True), (rings[-1], False)):
            try:
                f = bm.faces.new(ring[::-1] if rev else ring)
            except ValueError:
                pass
    return bm


def box_bm(size, loc=(0, 0, 0), bm=None, rot=None):
    bm = bm or bmesh.new()
    m = Matrix.Translation(loc)
    if rot is not None:
        m = m @ Euler(rot).to_matrix().to_4x4()
    m = m @ Matrix.Diagonal((size[0] / 2, size[1] / 2, size[2] / 2, 1))
    bmesh.ops.create_cube(bm, size=2.0, matrix=m)
    return bm


def join_objects(name, objs, mat=None):
    """把幾個物件合成一個（以第一個為底）。"""
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    objs[0].name = name
    return objs[0]


def instance(mesh_or_obj, name, loc, rot_z=0.0, scale=1.0, color=None, coll=None, rot=None):
    me = mesh_or_obj.data if hasattr(mesh_or_obj, "data") else mesh_or_obj
    ob = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(ob)
    ob.location = loc
    ob.rotation_euler = rot if rot is not None else (0, 0, rot_z)
    ob.scale = (scale, scale, scale) if isinstance(scale, (int, float)) else scale
    if color is not None:
        ob.color = (*color, 1) if len(color) == 3 else color
    return ob


def hide_render(ob):
    ob.hide_render = True
    ob.hide_viewport = True


def check_names():
    """撞名檢查：物件、網格、材質名稱不該有 .001。"""
    bad = []
    for coll in (bpy.data.objects, bpy.data.meshes, bpy.data.materials):
        for d in coll:
            if len(d.name) > 4 and d.name[-4] == "." and d.name[-3:].isdigit():
                bad.append(d.name)
    return bad


# ----------------------------------------------------------------------------- 深度圖與後製用資料
def L_math(nt, op, a, b):
    return math_node(nt, op, a, b, clamp=True)


def render_pair(base_path, sun_dir=None, depth_samples=4, y_pass=True):
    """渲染美術圖（<base>.png）與深度圖（<base>_depth.png）。
    深度編碼：v = 1 / (1 + z / 200)，z 為鏡頭前方公尺；天空 = 0。PNG 以 Standard 色彩管理輸出（後製要反 sRGB）。
    另存 <base>.json：太陽在畫面中的位置（0..1，左上為原點，可超出）。"""
    import mathutils
    from bpy_extras.object_utils import world_to_camera_view

    sc = bpy.context.scene
    cam = sc.camera
    meta = {}
    if sun_dir is not None:
        p = cam.location + Vector(sun_dir) * 20000.0
        co = world_to_camera_view(sc, cam, p)
        meta["sun_xy"] = [co.x, 1.0 - co.y]
        meta["sun_front"] = bool(co.z > 0)
    meta["res"] = [sc.render.resolution_x, sc.render.resolution_y]
    meta["hdr_scale"] = 1.0
    with open(base_path + ".json", "w", encoding="utf-8") as f:
        json.dump(meta, f)
    t_total = render_to(base_path)
    # 深度
    dm = new_mat("depth_mat")
    nt = dm.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    cd = nt.nodes.new("ShaderNodeCameraData")
    inv = math_node(nt, "DIVIDE", 1.0, math_node(nt, "ADD", 1.0, math_node(nt, "DIVIDE", cd.outputs["View Z Depth"], 200.0)))
    em = nt.nodes.new("ShaderNodeEmission")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sepz = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], sepz.inputs["Vector"])
    zr = math_node(nt, "DIVIDE", math_node(nt, "ADD", sepz.outputs["Z"], 500.0), 3500.0, clamp=True)
    comb = nt.nodes.new("ShaderNodeCombineColor")
    nt.links.new(inv, comb.inputs["Red"])
    nt.links.new(zr, comb.inputs["Green"])
    xr = L_math(nt, "DIVIDE", math_node(nt, "ADD", sepz.outputs["X"], 1400.0), 1800.0)
    nt.links.new(xr, comb.inputs["Blue"])
    yr = L_math(nt, "DIVIDE", math_node(nt, "ADD", sepz.outputs["Y"], 1500.0), 3000.0)
    nt.links.new(comb.outputs["Color"], em.inputs["Color"])
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    old_world = sc.world
    bw = bpy.data.worlds.new("black")
    bw.use_nodes = True
    for n in bw.node_tree.nodes:
        if n.type == "BACKGROUND":
            n.inputs["Color"].default_value = (0, 0, 0, 1)
    sc.world = bw
    vl = bpy.context.view_layer
    vl.material_override = dm
    old = (sc.view_settings.view_transform, sc.view_settings.exposure, sc.eevee.taa_render_samples, sc.eevee.use_raytracing)
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.exposure = 0.0
    sc.eevee.taa_render_samples = depth_samples
    sc.eevee.use_raytracing = False
    # 太陽燈與體積不參與深度圖
    t_depth = render_to(base_path + "_depth")
    # 第二張：世界座標 y 存在紅色（後製的黑暗帶要限制在通道附近）
    if y_pass:
        nt.links.new(yr, comb.inputs["Red"])
        t_depth += render_to(base_path + "_depth2")
    vl.material_override = None
    sc.world = old_world
    sc.view_settings.view_transform, sc.view_settings.exposure, sc.eevee.taa_render_samples, sc.eevee.use_raytracing = old
    return t_total, t_depth


# ----------------------------------------------------------------------------- numpy 雜訊與網格
def _hash2(ix, iy, seed):
    n = (ix.astype(np.int64) * 374761393 + iy.astype(np.int64) * 668265263 + seed * 2147483647) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    n = n ^ (n >> 16)
    return (n & 0xFFFF).astype(np.float32) / 65535.0


def vnoise2(x, y, wl, seed=1):
    u = x / wl
    v = y / wl
    iu = np.floor(u)
    iv = np.floor(v)
    fu = (u - iu).astype(np.float32)
    fv = (v - iv).astype(np.float32)
    su = fu * fu * (3 - 2 * fu)
    sv = fv * fv * (3 - 2 * fv)
    a = _hash2(iu, iv, seed)
    b = _hash2(iu + 1, iv, seed)
    c = _hash2(iu, iv + 1, seed)
    d = _hash2(iu + 1, iv + 1, seed)
    return (a + (b - a) * su + (c - a) * sv + (a - b - c + d) * su * sv) * 2 - 1


def fbm2(x, y, wl_max, wl_min, seed=1, gain=0.5):
    tot = np.zeros_like(x, dtype=np.float32)
    amp, norm, wl, k = 1.0, 0.0, wl_max, 0
    while wl >= wl_min:
        tot += amp * vnoise2(x, y, wl, seed + k * 17)
        norm += amp
        amp *= gain
        wl *= 0.5
        k += 1
    return tot / max(norm, 1e-6)


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def mesh_from_grid(name, X, Y, Z, attrs=None, mat=None, smooth=True):
    """X, Y, Z: (ny, nx) 陣列；attrs: {名稱: (ny, nx) 陣列} 存成點屬性。"""
    ny, nx = X.shape
    verts = np.stack([X, Y, Z], axis=-1).astype(np.float32).reshape(-1, 3)
    idx = np.arange(nx * ny, dtype=np.int32).reshape(ny, nx)
    q = np.stack([idx[:-1, :-1], idx[:-1, 1:], idx[1:, 1:], idx[1:, :-1]], axis=-1).reshape(-1, 4)
    nq = q.shape[0]
    me = bpy.data.meshes.new(name)
    me.vertices.add(verts.shape[0])
    me.vertices.foreach_set("co", verts.ravel())
    me.polygons.add(nq)
    me.loops.add(nq * 4)
    me.loops.foreach_set("vertex_index", q.ravel())
    me.polygons.foreach_set("loop_start", np.arange(0, nq * 4, 4, dtype=np.int32))
    if smooth:
        me.polygons.foreach_set("use_smooth", np.ones(nq, dtype=bool))
    me.update(calc_edges=True)
    for k, arr in (attrs or {}).items():
        a = me.attributes.new(k, "FLOAT", "POINT")
        a.data.foreach_set("value", np.asarray(arr, dtype=np.float32).ravel())
    if mat is not None:
        me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    link(ob)
    return ob
