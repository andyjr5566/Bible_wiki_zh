import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import epic_lib as L, epic_props as P, bpy
args = sys.argv[sys.argv.index("--") + 1:]
scene, cx, cy, cz, tx, ty, tz, out = args[0], *map(float, args[1:7]), args[7]
lens = float(args[8]) if len(args) > 8 else 24.0
sc = L.fresh_scene("scout")
meta, layers = L.load_terrain(scene)
mat = P.terrain_material("t", "levant")
for o in layers: o.data.materials.append(mat)
L.setup_world(25, 200, sun_energy=4.0, strength=1.0)
L.set_camera((cx, cy, cz), (tx, ty, tz), lens=lens)
L.render_settings(800, 450, 8, exposure=-1.0)
sc.view_settings.exposure = 0.3
L.render_to(out)
