"""寫實人物並排試片。"""
import sys, os, time, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import epic_lib as L, epic_heroes as H, bpy
args = sys.argv[sys.argv.index("--") + 1:]
sc = L.fresh_scene("heroes")
floor = L.mesh_obj("floor", (lambda bm: (L.box_bm((30, 14, 0.2), (0, 0, -0.1), bm), bm)[1])(__import__("bmesh").new()), L.pbr("floor", "#b09c78", 0.95))
t0 = time.time()
heroes = H.build_all()
print("build_all", time.time() - t0)
for i, (k, f) in enumerate(heroes.items()):
    f.hide_render = False; f.hide_viewport = False
    f.location = (-5.0 + i * 2.5, 0, 0)
    f.rotation_euler = (0, 0, math.radians(-25 + i * 12)) if False else (0, 0, 3.14159 + 0.0)
L.setup_world(30, 215, sun_energy=3.0, strength=1.0, horizon="#cfd6e0", mid="#b8c6dc", zenith="#8fa9d2", glow_k=0.3, fill=0.8)
L.set_camera((0.0, -7.5, 1.5), (0.0, 0.0, 1.0), lens=45)
L.render_settings(1800, 800, 48, exposure=-0.3)
L.render_to(args[0])
