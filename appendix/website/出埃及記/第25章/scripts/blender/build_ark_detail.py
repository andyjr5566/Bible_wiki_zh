"""Build the web-ready Ark detail asset from the preserved source GLB.

Run inside Blender 5.x, for example:
  blender --background --python scripts/blender/build_ark_detail.py

The source GLB is never overwritten. The processed and public GLBs are derived
outputs; the existing asset ID and runtime transform remain unchanged.
"""

from pathlib import Path

import bpy


PROJECT_ROOT = Path(r"C:\Obsidian\Hermes\scripture\appendix\website\出埃及記\第25章")
SOURCE = PROJECT_ROOT / "assets/source/sketchfab/ark-of-the-covenant-alternative/ark_of_the_covenant_alternative.glb"
PROCESSED = PROJECT_ROOT / "assets/processed/sketchfab/ark-of-the-covenant-alternative/ark-alternative.glb"
PUBLIC = PROJECT_ROOT / "public/models/ark-alternative.glb"
BLEND = PROJECT_ROOT / "assets/processed/sketchfab/ark-of-the-covenant-alternative/ark-alternative-improved.blend"


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        # Do not remove materials or meshes that Blender keeps linked while importing.
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def material(name: str, color: tuple[float, float, float], metallic: float, roughness: float) -> bpy.types.Material:
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = next((node for node in nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def replace_materials() -> None:
    # Keep the PBR response restrained for the website's HDR-like scene lights;
    # the same materials remain readable in Blender preview and Three.js.
    gold = material("ArkGoldImproved", (0.055, 0.012, 0.001), 0.12, 0.58)
    wood = material("ArkAcaciaWoodImproved", (0.022, 0.0035, 0.0008), 0.0, 0.72)

    body = bpy.data.objects.get("Ark_0")
    if body is None:
        raise RuntimeError("Expected source mesh Ark_0 was not found")
    # The source mesh keeps poles as two end islands at local X ±1.0 and the
    # body inside local X ±0.3. This separates wood body faces from gold poles
    # without changing geometry or the source hierarchy.
    body.data.materials.clear()
    body.data.materials.append(gold)
    body.data.materials.append(wood)
    for polygon in body.data.polygons:
        polygon.material_index = 1 if abs(polygon.center.x) < 0.5 else 0

    cherubim = bpy.data.objects.get("Ark_0.001")
    if cherubim is None:
        raise RuntimeError("Expected source mesh Ark_0.001 was not found")
    cherubim.data.materials.clear()
    cherubim.data.materials.append(gold)

    # Ark_1 is the thin chest panel in the supplied hierarchy. Keep it with
    # the wooden body so the educational color cue reads as one wooden chest
    # under a separate gold cover and cherubim assembly.
    chest_panel = bpy.data.objects.get("Ark_1")
    if chest_panel is None:
        raise RuntimeError("Expected source mesh Ark_1 was not found")
    chest_panel.data.materials.clear()
    chest_panel.data.materials.append(wood)

    root = bpy.data.objects.get("Ark")
    if root is None:
        raise RuntimeError("Expected source root Ark was not found")
    root["asset_id"] = "tabernacle-ark-alternative"
    root["historical_status"] = "reconstructed"
    root["material_note"] = "Wooden chest with gold overlay, gold cover/cherubim and gold carrying poles; visual material separation for teaching."


def export_glb(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    root = bpy.data.objects.get("Ark")
    root.select_set(True)
    for child in root.children_recursive:
        child.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=True,
        export_apply=False,
        export_materials="EXPORT",
        export_cameras=False,
        export_lights=False,
        export_animations=False,
        export_yup=True,
    )


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)
    clear_scene()
    bpy.ops.import_scene.gltf(filepath=str(SOURCE))
    replace_materials()
    export_glb(PROCESSED)
    export_glb(PUBLIC)
    BLEND.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    print(f"Built Ark detail: {PROCESSED}")
    print(f"Built runtime copy: {PUBLIC}")
    print(f"Saved editable blend: {BLEND}")


if __name__ == "__main__":
    main()
