"""模型試片：把簡化人形、立石、橡樹、羊、馬、戰車並排渲染（用來看過再放進場景）。"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import epic_lib as L, epic_props as P, bpy
from mathutils import Vector
args = sys.argv[sys.argv.index("--") + 1:]
out = args[0]
sc = L.fresh_scene("lab")
floor = L.mesh_obj("floor", (lambda bm: (L.box_bm((60, 30, 0.2), (0, 0, -0.1), bm), bm)[1])(__import__("bmesh").new()), L.pbr("floor", "#b9ab8c", 0.95))
L.setup_world(35, 215, sun_energy=3.2, strength=1.0, horizon="#cfd6e0", mid="#b8c6dc", zenith="#8fa9d2", glow_k=0.3, fill=0.8)
figs = P.build_figure_meshes()
cols = ["#d8cdb0", "#9a7b57", "#a3553f", "#5b6f8a", "#c9b88e", "#7a5a3d", "#e2d6b6"]
for i, me in enumerate(figs):
    L.instance(me, f"f{i}", (-7.5 + i * 1.3, 0, 0), rot_z=0.2, color=tuple(L.srgb(cols[i])))
st = P.build_stone(); st.location = (-4.0, 4.0, 0.2); st.rotation_euler = (0, 0, 0.3)
wo, fo = P.build_oak(seed=4); P.finish_oak(wo, fo, (4.5, 7.0, 0), 0.5, 0.0)
sheep = P.build_sheep(); L.instance(sheep, "sh", (2.0, 3.0, 0), 0.5, 1.0, color=tuple(L.srgb("#d9d0bc")))
team = P.build_chariot_team(); L.instance(team, "tm", (-6.0, 3.0, 0), 0.4, 1.0, color=tuple(L.srgb("#5a3a26")))
team2 = P.build_chariot_team(gallop=-0.3); L.instance(team2, "tm2", (-1.0, 6.0, 0), -0.3, 1.0, color=tuple(L.srgb("#d8d0c0")))
cart = P.build_cart(); L.instance(cart, "ct", (4.0, 2.5, 0), 0.5, 1.0, color=tuple(L.srgb("#b8a27a")))
L.set_camera((0.5, -16.0, 4.5), (0.0, 3.0, 1.2), lens=38)
L.render_settings(1600, 800, 32, exposure=-0.5)
L.render_to(out)
