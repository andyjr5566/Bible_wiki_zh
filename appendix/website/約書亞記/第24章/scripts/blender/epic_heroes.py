"""風格 B 用的幾位寫實人物（長老、婦人、持杖的男人、青年）。每位約 12 秒（含布料模擬）。"""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

import epic_chars as C
import epic_lib as L

SPECS = {
    "elder": dict(gender="male", skin="Dark", robe="#d9ceb2", trim="#8a4b34", cloak="#7b5a3a", cloak_trim="#3f2c1c",
                  head="#efe8d6", head_trim="#3a2a22", sash="#8a4b34", hair="Hair_Beard", staff=False, seed=2, stride=0.0),
    "woman": dict(gender="female", skin="Light", robe="#a3553f", trim="#3d2a20", cloak="#5d6679", cloak_trim="#2c2f3a",
                  head="#e4d8c3", head_trim="#6b3b2a", sash="#d8c6a0", hair=None, staff=False, seed=5, stride=0.0),
    "shepherd": dict(gender="male", skin="Dark", robe="#b88b4a", trim="#5b3a22", cloak="#6e7345", cloak_trim="#33361f",
                     head="#d9ccb0", head_trim="#4a3524", sash="#5b3a22", hair="Hair_Beard", staff=True, seed=8, stride=6.0),
    "youth": dict(gender="male", skin="Light", robe="#e1d8c0", trim="#7a4a38", cloak="#4c5f78", cloak_trim="#232b38",
                  head="#f1ead8", head_trim="#333a4a", sash="#a3553f", hair=None, staff=False, seed=11, stride=-5.0),
    "mother": dict(gender="female", skin="Dark", robe="#c9b88e", trim="#7a4a38", cloak="#8f6a46", cloak_trim="#3f2c1c",
                   head="#d8c7a6", head_trim="#6b3b2a", sash="#8a4b34", hair=None, staff=False, seed=14, stride=0.0),
}


def build_hero(kind, tag=None, wind=1.0):
    sp = SPECS[kind]
    tag = tag or kind
    ch = C.load_character(sp["gender"], sp["skin"], tag=tag, stride=sp["stride"])
    robe = C.make_robe(ch, sp["robe"], sp["trim"], tag=tag, seed=sp["seed"], wind=wind)
    sl = C.make_sleeves(ch, sp["robe"], sp["trim"], tag=tag)
    cloak = C.make_cloak(ch, robe, sl, sp["cloak"], sp["cloak_trim"], tag=tag, seed=sp["seed"], wind=0.3 * wind)
    hc = C.make_headcloth(ch, sp["head"], sp["head_trim"], tag=tag, colliders=[cloak], wind=0.25 * wind)
    sash = C.make_sash(ch, sp["sash"], tag=tag)
    parts = [ch["body"], ch["eyes"], ch["brows"], robe, cloak, hc, sash] + sl
    if sp["gender"] == "male":
        parts.append(C.make_agal(ch, tag))
    if sp["hair"]:
        parts.append(C.hair_object(sp["hair"], tag))
    if sp["staff"]:
        hand = ch["key"]["hand_r"][0]
        bm = bmesh.new()
        L.tube_bm([(hand.x + 0.02, hand.y - 0.04, 0.0), (hand.x + 0.02, hand.y - 0.04, 1.95)], [0.022, 0.018], 8, bm)
        me = bpy.data.meshes.new(f"{tag}_staff")
        bm.to_mesh(me)
        bm.free()
        me.materials.append(L.pbr(f"{tag}_staff_mat", "#4a3a2a", 0.85))
        st = bpy.data.objects.new(f"{tag}_staff", me)
        bpy.context.scene.collection.objects.link(st)
        parts.append(st)
    fig = C.finalize_character(parts, f"hero_{tag}")
    return fig


def build_all(kinds=("elder", "woman", "shepherd", "youth", "mother"), spacing=6.0, wind=1.0):
    """依序建好；每位先挪開（之後的模擬才不會碰到前面的人），最後全部歸位到原點。回傳 {kind: obj}。"""
    out = {}
    offs = {}
    for i, k in enumerate(kinds):
        fig = build_hero(k, wind=wind)
        off = Vector((30.0 + spacing * (i + 1), 0.0, 0.0))
        fig.data.transform(Matrix.Translation(off))
        fig.location = (0, 0, 0)
        out[k] = fig
        offs[k] = off
    for k, fig in out.items():
        fig.data.transform(Matrix.Translation(-offs[k]))
        fig.hide_render = True
        fig.hide_viewport = True
    return out
