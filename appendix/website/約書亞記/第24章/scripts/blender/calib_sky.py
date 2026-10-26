import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import epic_lib as L
import bpy, numpy as np
out = os.environ.get("TEMP", ".") + "\sky_cal.png"
for rot in (0.0, 1.5708, 3.1416):
    sc = L.fresh_scene("cal")
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    nt = w.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    sky = nt.nodes.new("ShaderNodeTexSky"); sky.sky_type = "MULTIPLE_SCATTERING"
    sky.sun_elevation = math.radians(20); sky.sun_rotation = rot; sky.sun_disc = True
    bg = nt.nodes.new("ShaderNodeBackground"); bg.inputs["Strength"].default_value = 1e-5; sky.sun_size = math.radians(4); o = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(sky.outputs[0], bg.inputs[0]); nt.links.new(bg.outputs[0], o.inputs[0])
    cd = bpy.data.cameras.new("c"); cd.type = "PANO"
    try:
        cd.panorama_type = "EQUIRECTANGULAR"
    except Exception as e:
        print("pano", e)
    co = bpy.data.objects.new("c", cd); sc.collection.objects.link(co); sc.camera = co
    co.rotation_euler = (math.pi / 2, 0, -math.pi / 2)  # look +X... 
    L.render_settings(360, 180, 1, volumetric=False, raytrace=False)
    sc.view_settings.view_transform = "Standard"; sc.view_settings.exposure = 0
    sc.render.image_settings.color_depth = "8"
    L.render_to(out); import shutil; shutil.copy(out, out.replace(".png", f"_{rot:.2f}.png"))
    im = bpy.data.images.load(out)
    px = np.array(im.pixels[:]).reshape(180, 360, 4)[:, :, :3].sum(axis=2)
    thr = px.max()*0.9
    mask = px >= thr
    ys, xs = np.nonzero(mask)
    ang = (xs + 0.5) / 360 * 2 * math.pi
    cx = math.atan2(np.sin(ang).mean(), np.cos(ang).mean()) % (2 * math.pi)
    print("ROT", rot, "centroid az(deg from img left)", math.degrees(cx), "el", (ys.mean() + 0.5) - 90, "n", mask.sum())
    bpy.data.images.remove(im)
