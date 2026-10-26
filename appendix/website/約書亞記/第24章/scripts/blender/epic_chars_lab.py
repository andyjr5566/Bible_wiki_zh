"""寫實人物試片：一個角色完整流程（含計時），輸出並排圖。"""
import sys, os, time, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import epic_lib as L, epic_chars as C, epic_props as P, bpy
from mathutils import Vector
args = sys.argv[sys.argv.index("--") + 1:]
out = args[0]
which = args[1] if len(args) > 1 else "all"
sc = L.fresh_scene("chars")
floor = L.mesh_obj("floor", (lambda bm: (L.box_bm((30, 14, 0.2), (0, 0, -0.1), bm), bm)[1])(__import__("bmesh").new()), L.pbr("floor", "#b09c78", 0.95))
t0 = time.time()
ch = C.load_character("male", "Dark", tag="m1")
print("load", time.time() - t0)
t0 = time.time()
robe = C.make_robe(ch, "#d9ceb2", "#8a4b34", tag="m1", seed=2)
print("robe", time.time() - t0)
sl = C.make_sleeves(ch, "#d9ceb2", "#8a4b34", tag="m1")
t0 = time.time()
cloak = C.make_cloak(ch, robe, sl, "#7b5a3a", "#3f2c1c", tag="m1")
print("cloak", time.time() - t0)
t0 = time.time()
hc = C.make_headcloth(ch, "#efe8d6", "#3a2a22", tag="m1", colliders=[cloak])
sash = C.make_sash(ch, "#8a4b34", tag="m1")
agal = C.make_agal(ch, "m1")
print("headcloth", time.time() - t0)
beard = C.hair_object("Hair_Beard", "m1")
for o in sl:
    pass
parts = [ch["body"], ch["eyes"], ch["brows"], beard, robe, cloak, hc, sash, agal] + sl
fig = C.finalize_character(parts, "hero_m1")
L.setup_world(30, 215, sun_energy=3.0, strength=1.0, horizon="#cfd6e0", mid="#b8c6dc", zenith="#8fa9d2", glow_k=0.3, fill=0.8)
L.set_camera((1.7, 3.2, 1.4), (0.0, 0.0, 1.0), lens=50)
L.render_settings(900, 1100, 48, exposure=-0.3)
L.render_to(out)
