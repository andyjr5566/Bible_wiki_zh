"""Render a full 360-degree Shechem valley environment from the local DEM.

Run through shechem_panorama_make.ps1.  Each time of day produces an opaque
equirectangular sky plate and an RGBA terrain plate.  The camera points
southeast, placing the longitude wrap seam over the low, stable northwest
valley opening.
"""
import argparse
import json
import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))

import bpy
import numpy as np
from mathutils import Matrix, Vector
import epic_lib as L
import style_a as S


TIMES = [
    dict(name="dawn", sun_az=0.0, sun_el=7.5, sun_energy=6.5,
         sun_color=(1.0, 0.76, 0.5), glow_k=0.8, glow="#ffc58e", disc_k=400.0,
         disc_deg=1.4, horizon="#eab991", mid="#a8b5d0", zenith="#4a6492",
         ground="#7a6552", strength=1.0, clouds=0.9, cloud_scale=1.6,
         cloud_seed=3.0, fill=2.4, fill_color=(1.0, 0.78, 0.56)),
    dict(name="morning", sun_az=24.0, sun_el=24.0, sun_energy=5.4,
         sun_color=(1.0, 0.84, 0.66), glow_k=0.55, glow="#ffd89d", disc_k=110.0,
         disc_deg=1.15, horizon="#edd0ad", mid="#b6c5d6", zenith="#718caf",
         ground="#82735e", strength=0.96, clouds=0.72, cloud_scale=1.7,
         cloud_seed=13.0, fill=2.0, fill_color=(0.82, 0.86, 1.0)),
    dict(name="afternoon", sun_az=180.0, sun_el=23.0, sun_energy=5.2,
         sun_color=(1.0, 0.75, 0.52), glow_k=0.8, glow="#ffc07f", disc_k=150.0,
         disc_deg=1.2, horizon="#eab38e", mid="#9da9c4", zenith="#485d83",
         ground="#78604f", strength=0.98, clouds=0.78, cloud_scale=1.65,
         cloud_seed=27.0, fill=1.65, fill_color=(0.72, 0.79, 1.0)),
    dict(name="dusk", sun_az=180.0, sun_el=-1.5, sun_energy=1.2,
         sun_color=(1.0, 0.53, 0.39), glow_k=0.95, glow="#ff896c", disc_k=0.0,
         disc_deg=1.2, horizon="#d48c84", mid="#766a96", zenith="#292e58",
         ground="#302c42", strength=0.9, clouds=0.86, cloud_scale=1.55,
         cloud_seed=21.0, fill=0.32, fill_color=(0.58, 0.64, 1.0)),
    dict(name="night", sun_az=180.0, sun_el=-90.0, sun_energy=0.0,
         sun_color=(0.35, 0.48, 0.8), glow_k=0.0, glow="#435a8a", disc_k=0.0,
         disc_deg=1.0, horizon="#344665", mid="#1d2b4b", zenith="#0b1530",
         ground="#151f30", strength=0.96, clouds=0.16, cloud_scale=1.8,
         cloud_seed=35.0, fill=0.48, fill_color=(0.57, 0.68, 1.0)),
]

VERTICAL_EXAGGERATION = 1.25

DEM_DIR = ROOT / "collect" / "dem"
HEIGHT_FILE = DEM_DIR / "shechem_valley_height.png"
META_FILE = DEM_DIR / "shechem_valley_meta.json"


def mercator_pixel(lon, lat, meta):
    n = 256 * (2 ** meta["zoom"])
    ox = meta["origin_world_px"]["origin_x"]
    oy = meta["origin_world_px"]["origin_y"]
    lat_r = math.radians(lat)
    x = (lon + 180.0) / 360.0 * n - ox
    y = (0.5 - math.log((1 + math.sin(lat_r)) / (1 - math.sin(lat_r)))
         / (4 * math.pi)) * n - oy
    return x, y


def read_dem():
    if not HEIGHT_FILE.is_file() or not META_FILE.is_file():
        raise FileNotFoundError(f"Missing Shechem DEM source: {HEIGHT_FILE}")
    meta = json.loads(META_FILE.read_text(encoding="utf-8"))
    image = bpy.data.images.load(str(HEIGHT_FILE), check_existing=False)
    image.colorspace_settings.name = "Non-Color"
    width, height = image.size
    values = np.asarray(image.pixels[:], dtype=np.float32).reshape(height, width, image.channels)
    elevation = np.rint(values[:, :, 0][::-1, :] * 65535.0).astype(np.float32)
    bpy.data.images.remove(image)
    elevation -= float(meta["elevation_offset"])
    return meta, elevation


def camera_pixel(meta, width, height):
    # The valley floor between the two named peaks, near historic Shechem.
    center_lon, center_lat = 35.26, 32.22
    px, py = mercator_pixel(center_lon, center_lat, meta)
    if not (1 <= px < width - 1 and 1 <= py < height - 1):
        raise ValueError(f"Camera centre falls outside DEM: {(px, py)}")
    return center_lon, center_lat, px, py


def make_terrain(meta, elevation, camera_px, camera_py, meters_per_pixel, ground_z, camera_z):
    height, width = elevation.shape
    # Blender's mesh helper expects increasing Y as row index increases. Flip
    # the north-up raster to south-to-north while retaining its true elevations.
    source_south_to_north = elevation[::-1, :].copy()
    bottom_row = (height - 1) - camera_py
    x_axis = (np.arange(width, dtype=np.float32) - camera_px) * meters_per_pixel
    y_axis = (np.arange(height, dtype=np.float32) - bottom_row) * meters_per_pixel
    xx, yy = np.meshgrid(x_axis, y_axis)
    roughness = L.fbm2(xx, yy, 145.0, 18.0, seed=91) * 4.0
    roughness += L.fbm2(xx, yy, 54.0, 9.0, seed=37) * 2.0
    roughness *= np.clip(np.sqrt(xx * xx + yy * yy) / 100.0, 0.0, 1.0)
    visual_z = source_south_to_north + roughness
    # Preserve the two DEM summit elevations while lightly breaking broad,
    # flat raster ridges at the scale of a few metres.
    for peak_lon, peak_lat, summit in ((35.2732, 32.2341, 949.0), (35.2732, 32.2004, 879.0)):
        peak_px, peak_py = mercator_pixel(peak_lon, peak_lat, meta)
        col, row = int(round(peak_px)), int(round(peak_py))
        radius = 20
        y0, y1 = max(0, row - radius), min(height, row + radius + 1)
        x0, x1 = max(0, col - radius), min(width, col + radius + 1)
        local = elevation[y0:y1, x0:x1]
        local_peak = np.unravel_index(np.argmax(local), local.shape)
        peak_row, peak_col = y0 + local_peak[0], x0 + local_peak[1]
        mesh_row = height - 1 - peak_row
        peak_x = (peak_col - camera_px) * meters_per_pixel
        peak_y = (camera_py - peak_row) * meters_per_pixel
        mask = (xx - peak_x) ** 2 + (yy - peak_y) ** 2 <= 130.0 ** 2
        visual_z[mask] = np.minimum(visual_z[mask], summit)
        visual_z[mesh_row, peak_col] = summit
    visual_z = np.minimum(visual_z, float(np.max(elevation)))
    # Keep the valley floor fixed and exaggerate elevation only along Blender Z.
    visual_z = ground_z + (visual_z - ground_z) * VERTICAL_EXAGGERATION
    terrain = L.mesh_from_grid("shechem_dem_terrain", xx, yy, visual_z, mat=None, smooth=True)
    return terrain, xx, yy, source_south_to_north


def s_rgb(hex_colour):
    return tuple(L.srgb(hex_colour))


def terrain_material(time_name, camera_z, haze_hex):
    mat = L.new_mat("shechem_hills_" + time_name)
    nt = mat.node_tree
    nt.nodes.clear()
    colour = nt.nodes.new("ShaderNodeVertexColor")
    colour.layer_name = "shechem_tone"
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    output = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(colour.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    bsdf.inputs["Roughness"].default_value = 0.96
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.14
    if "Emission Color" in bsdf.inputs:
        nt.links.new(colour.outputs["Color"], bsdf.inputs["Emission Color"])
    if "Emission Strength" in bsdf.inputs:
        bsdf.inputs["Emission Strength"].default_value = 0.42
    if time_name == "night":
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (0.022, 0.035, 0.09, 1)
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = 0.4
    return mat


def set_terrain_colour(terrain, xx, yy, elevation, camera_z, haze_hex, time_name):
    stops = ((430.0, "#7b6649"), (575.0, "#977852"), (700.0, "#ad8a61"),
             (850.0, "#bf9d6d"), (950.0, "#d2b587"))
    stop_heights = np.asarray([s[0] for s in stops], dtype=np.float32)
    stop_colours = np.asarray([L.srgb(s[1]) for s in stops], dtype=np.float32)
    base = np.stack([np.interp(elevation, stop_heights, stop_colours[:, c])
                     for c in range(3)], axis=-1)
    pigment = L.fbm2(xx, yy, 420.0, 42.0, seed=81)
    base *= (1.0 + pigment[:, :, None] * 0.08)
    distance = np.sqrt(xx * xx + yy * yy + (elevation - camera_z) ** 2)
    haze = np.clip(0.035 + (distance - 900.0) / (7900.0 - 900.0) * 0.76, 0.035, 0.78)
    haze_colour = np.asarray(L.srgb(haze_hex), dtype=np.float32)
    base = base * (1.0 - haze[:, :, None]) + haze_colour[None, None, :] * haze[:, :, None]
    base = np.clip(base, 0.0, 1.0)
    if time_name == "night":
        base *= np.asarray((0.5, 0.61, 0.86), dtype=np.float32)
    rgba = np.concatenate((base, np.ones((*base.shape[:2], 1), dtype=np.float32)), axis=-1)
    attr = terrain.data.color_attributes.get("shechem_tone")
    if attr is None:
        attr = terrain.data.color_attributes.new(name="shechem_tone", type="FLOAT_COLOR", domain="POINT")
    attr.data.foreach_set("color", rgba.reshape(-1))


def install_time_world(config):
    for ob in list(bpy.data.objects):
        if ob.type == "LIGHT":
            bpy.data.objects.remove(ob, do_unlink=True)
    world_cfg = dict(S.LIGHT["cover"])
    world_cfg.update(config)
    world_cfg.pop("name", None)
    sun_az = world_cfg.pop("sun_az")
    sun_el = world_cfg.pop("sun_el")
    world, _sun, _direction = L.setup_world(sun_el, sun_az, **world_cfg)
    if config["name"] == "night":
        add_night_sky(world)
        add_moon_light(azimuth=58.0, elevation=25.0)
    return world


def add_night_sky(world):
    nt = world.node_tree
    out = next(node for node in nt.nodes if node.type == "OUTPUT_WORLD")
    previous = out.inputs["Surface"].links[0].from_socket
    texcoord = next(node for node in nt.nodes if node.type == "TEX_COORD")
    normal = nt.nodes.new("ShaderNodeVectorMath")
    normal.operation = "NORMALIZE"
    nt.links.new(texcoord.outputs["Generated"], normal.inputs[0])
    separate = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(normal.outputs[0], separate.inputs[0])

    stars = nt.nodes.new("ShaderNodeTexVoronoi")
    stars.distance = "EUCLIDEAN"
    stars.inputs["Scale"].default_value = 145.0
    stars.inputs["Randomness"].default_value = 1.0
    nt.links.new(normal.outputs[0], stars.inputs["Vector"])
    pinprick = nt.nodes.new("ShaderNodeMath")
    pinprick.operation = "LESS_THAN"
    pinprick.inputs[1].default_value = 0.012
    nt.links.new(stars.outputs["Distance"], pinprick.inputs[0])
    above_horizon = nt.nodes.new("ShaderNodeMath")
    above_horizon.operation = "GREATER_THAN"
    above_horizon.inputs[1].default_value = 0.025
    nt.links.new(separate.outputs["Z"], above_horizon.inputs[0])
    star_mask = nt.nodes.new("ShaderNodeMath")
    star_mask.operation = "MULTIPLY"
    nt.links.new(pinprick.outputs[0], star_mask.inputs[0])
    nt.links.new(above_horizon.outputs[0], star_mask.inputs[1])
    star_emission = nt.nodes.new("ShaderNodeEmission")
    star_emission.inputs["Color"].default_value = (0.68, 0.79, 1.0, 1)
    star_emission.inputs["Strength"].default_value = 1.35
    star_mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(star_mask.outputs[0], star_mix.inputs[0])
    nt.links.new(previous, star_mix.inputs[1])
    nt.links.new(star_emission.outputs[0], star_mix.inputs[2])

    moon_az, moon_el = math.radians(58.0), math.radians(25.0)
    moon_dir = Vector((math.cos(moon_el) * math.cos(moon_az),
                       math.cos(moon_el) * math.sin(moon_az), math.sin(moon_el)))
    dot = nt.nodes.new("ShaderNodeVectorMath")
    dot.operation = "DOT_PRODUCT"
    dot.inputs[1].default_value = moon_dir
    nt.links.new(normal.outputs[0], dot.inputs[0])
    moon = nt.nodes.new("ShaderNodeMapRange")
    moon.interpolation_type = "SMOOTHSTEP"
    moon.inputs["From Min"].default_value = math.cos(math.radians(1.55))
    moon.inputs["From Max"].default_value = 1.0
    moon.clamp = True
    nt.links.new(dot.outputs["Value"], moon.inputs["Value"])
    moon_glow = nt.nodes.new("ShaderNodeMath")
    moon_glow.operation = "POWER"
    moon_glow.inputs[1].default_value = 48.0
    nt.links.new(dot.outputs["Value"], moon_glow.inputs[0])
    halo = nt.nodes.new("ShaderNodeMath")
    halo.operation = "MULTIPLY"
    halo.inputs[1].default_value = 0.28
    nt.links.new(moon_glow.outputs[0], halo.inputs[0])
    moon_strength = nt.nodes.new("ShaderNodeMath")
    moon_strength.operation = "MULTIPLY_ADD"
    moon_strength.inputs[1].default_value = 13.0
    nt.links.new(moon.outputs["Result"], moon_strength.inputs[0])
    nt.links.new(halo.outputs[0], moon_strength.inputs[2])
    moon_emission = nt.nodes.new("ShaderNodeEmission")
    moon_emission.inputs["Color"].default_value = (0.66, 0.78, 1.0, 1)
    nt.links.new(moon_strength.outputs[0], moon_emission.inputs["Strength"])

    add_moon = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(star_mix.outputs[0], add_moon.inputs[0])
    nt.links.new(moon_emission.outputs[0], add_moon.inputs[1])
    nt.links.new(add_moon.outputs[0], out.inputs["Surface"])


def add_moon_light(azimuth, elevation):
    az, el = math.radians(azimuth), math.radians(elevation)
    direction = Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))
    data = bpy.data.lights.new("shechem_moonlight", "SUN")
    data.energy = 0.78
    data.color = (0.54, 0.68, 1.0)
    data.angle = math.radians(3.0)
    light = bpy.data.objects.new("shechem_moonlight", data)
    L.link(light)
    light.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()


def add_night_stars(camera_z):
    import random
    import bmesh

    rnd = random.Random(2406)
    bm = bmesh.new()
    center = Vector((0.0, 0.0, camera_z))
    sphere_radius = 15000.0
    for _ in range(320):
        z = rnd.uniform(0.045, 0.98)
        az = rnd.uniform(0.0, math.tau)
        planar = math.sqrt(1.0 - z * z)
        direction = Vector((planar * math.cos(az), planar * math.sin(az), z))
        location = center + direction * sphere_radius
        size = rnd.uniform(18.0, 35.0)
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=size,
                                   matrix=Matrix.Translation(location))
    mesh = bpy.data.meshes.new("shechem_night_stars_mesh")
    bm.to_mesh(mesh)
    bm.free()
    material = bpy.data.materials.new("shechem_night_stars")
    material.diffuse_color = (0.72, 0.82, 1.0, 1.0)
    material.use_nodes = True
    nt = material.node_tree
    nt.nodes.clear()
    emission = nt.nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = (0.72, 0.82, 1.0, 1.0)
    emission.inputs["Strength"].default_value = 3.5
    output = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(emission.outputs["Emission"], output.inputs["Surface"])
    mesh.materials.append(material)
    stars = bpy.data.objects.new("shechem_night_stars", mesh)
    L.link(stars)
    stars.hide_render = True
    return stars


def add_night_moon(camera_z):
    import bmesh

    az, el = math.radians(58.0), math.radians(25.0)
    direction = Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))
    position = Vector((0.0, 0.0, camera_z)) + direction * 15000.0
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=260.0,
                               matrix=Matrix.Translation(position))
    mesh = bpy.data.meshes.new("shechem_night_moon_mesh")
    bm.to_mesh(mesh)
    bm.free()
    material = bpy.data.materials.new("shechem_night_moon")
    material.diffuse_color = (0.72, 0.82, 1.0, 1.0)
    material.use_nodes = True
    nt = material.node_tree
    nt.nodes.clear()
    emission = nt.nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = (0.72, 0.82, 1.0, 1.0)
    emission.inputs["Strength"].default_value = 3.1
    output = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(emission.outputs["Emission"], output.inputs["Surface"])
    mesh.materials.append(material)
    moon = bpy.data.objects.new("shechem_night_moon", mesh)
    L.link(moon)
    moon.hide_render = True
    return moon


def build_scene(width, height, samples, work_dir):
    meta, elevation = read_dem()
    lon, lat, camera_px, camera_py = camera_pixel(meta, elevation.shape[1], elevation.shape[0])
    mpp = float(meta["meters_per_pixel_at_center_lat"])
    camera_row = int(round(camera_py))
    camera_col = int(round(camera_px))
    ground_z = float(elevation[camera_row, camera_col])
    camera_z = ground_z + 2.0
    print("DEM_EXTREMA", float(elevation.min()), float(elevation.max()), flush=True)
    print("CAMERA", {"lon": lon, "lat": lat, "pixel": [camera_px, camera_py],
                     "ground_m": ground_z, "elevation_m": camera_z}, flush=True)

    sc = L.fresh_scene("shechem_panorama")
    terrain, terrain_x, terrain_y, terrain_z = make_terrain(
        meta, elevation, camera_px, camera_py, mpp, ground_z, camera_z)
    cam = L.set_camera((0.0, 0.0, camera_z), (0.0, 1.0, camera_z), clip=(0.1, 30000.0))
    cam.data.type = "PANO"
    cam.data.panorama_type = "EQUIRECTANGULAR"
    heading = Vector((math.cos(math.radians(330.0)), math.sin(math.radians(330.0)), 0.0))
    cam.rotation_euler = heading.to_track_quat("-Z", "Y").to_euler()  # center SE; seam is NW.
    stars_obj = add_night_stars(camera_z)
    moon_obj = add_night_moon(camera_z)
    L.render_settings(width, height, samples=samples, volumetric=False, raytrace=False, exposure=-3.0)
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.cycles.sample_clamp_indirect = 3.0
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sc.render.image_settings.color_mode = "RGBA"

    os.makedirs(work_dir, exist_ok=True)
    for config in TIMES:
        name = config["name"]
        install_time_world(config)
        haze_hex = config["horizon"]
        set_terrain_colour(terrain, terrain_x, terrain_y, terrain_z, camera_z, haze_hex, name)
        terrain.data.materials.clear()
        terrain.data.materials.append(terrain_material(name, camera_z, haze_hex))
        folder = os.path.join(work_dir, name)
        os.makedirs(folder, exist_ok=True)

        terrain.hide_render = True
        stars_obj.hide_render = name != "night"
        moon_obj.hide_render = name != "night"
        sc.render.film_transparent = False
        L.render_to(os.path.join(folder, "sky"))

        stars_obj.hide_render = True
        moon_obj.hide_render = True
        terrain.hide_render = False
        sc.render.film_transparent = True
        L.render_to(os.path.join(folder, "hills"))
        print("TIME_COMPLETE", name, flush=True)

    summary = {
        "format": "single 360-degree equirectangular panorama, 2:1",
        "resolution": [width, height],
        "seam": "left/right wrap at the northwest valley opening; camera forward is southeast",
        "dem": str(HEIGHT_FILE.relative_to(ROOT)).replace("\\", "/"),
        "dem_projection": meta["projection"],
        "meters_per_pixel": mpp,
        "camera_lon_lat": [lon, lat],
        "camera_ground_elevation_m": ground_z,
        "dem_min_max_elevation_m": [float(elevation.min()), float(elevation.max())],
        "mountain_reference_elevations_m": {"Ebal": 949, "Gerizim": 879},
        "vertical_exaggeration": VERTICAL_EXAGGERATION,
        "scene_orientation": {
            "north": "-Z", "south": "+Z", "east": "+X", "west": "-X",
            "camera_forward_bearing_degrees": 120,
            "scene_yaw_degrees": -30,
            "horizontal_texture_flip": True,
            "Ebal": "north", "Gerizim": "south",
        },
        "paint_choice": S.PAINT_CHOICE,
        "paint_amount": S.PAINT[S.PAINT_CHOICE]["amount"],
        "times": [cfg["name"] for cfg in TIMES],
    }
    Path(work_dir, "shechem-panorama-source.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    raw_args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    parser.add_argument("--w", type=int, default=4096)
    parser.add_argument("--h", type=int, default=2048)
    parser.add_argument("--samples", type=int, default=32)
    args = parser.parse_args(raw_args)
    build_scene(args.w, args.h, args.samples, os.path.abspath(args.out))


if __name__ == "__main__":
    main()
