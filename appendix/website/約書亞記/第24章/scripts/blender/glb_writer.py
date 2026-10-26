"""Blender 5.2 純標準庫 glTF 2.0 Binary (.glb) 匯出器（不依賴 numpy DLL）。

將當前專屬場景中被選取的物件階層（含父子節點、多材質插槽、平滑／平坦法線、PBR 基礎色與粗糙度）
以標準 Khronos glTF 2.0 二進位格式寫出，並執行 Blender Z-up → glTF Y-up 座標轉換：
  (x_b, y_b, z_b) -> (x_b, z_b, -y_b)   （右手座標系，det = +1，繞 X 軸 -90 度）
"""

from __future__ import annotations
import json
import struct
import bpy
from mathutils import Matrix


def export_selected_glb(scene: bpy.types.Scene, filepath: str) -> int:
    selected = [o for o in scene.objects if o.select_get()]
    selected_set = set(selected)

    # 材質索引表
    mat_list: list[bpy.types.Material] = []
    mat_index_map: dict[str, int] = {}

    def get_mat_idx(m: bpy.types.Material | None) -> int:
        if m is None:
            key = "__default__"
            if key not in mat_index_map:
                mat_index_map[key] = len(mat_list)
                mat_list.append(None)  # type: ignore[arg-type]
            return mat_index_map[key]
        if m.name not in mat_index_map:
            mat_index_map[m.name] = len(mat_list)
            mat_list.append(m)
        return mat_index_map[m.name]

    bin_chunks: list[bytes] = []
    buffer_views: list[dict] = []
    accessors: list[dict] = []
    meshes_gltf: list[dict] = []
    nodes_gltf: list[dict] = []

    byte_offset = 0

    def append_buffer_view(raw: bytes, target: int) -> int:
        nonlocal byte_offset
        pad = (4 - (len(raw) % 4)) % 4
        padded = raw + (b"\x00" * pad)
        bv_idx = len(buffer_views)
        buffer_views.append(
            {
                "buffer": 0,
                "byteOffset": byte_offset,
                "byteLength": len(raw),
                "target": target,
            }
        )
        bin_chunks.append(padded)
        byte_offset += len(padded)
        return bv_idx

    def build_mesh_gltf(obj: bpy.types.Object) -> int | None:
        if obj.type != "MESH" or obj.data is None:
            return None
        me: bpy.types.Mesh = obj.data.copy()
        # 套用物件自身的 rotation 與 scale 至網格頂點（保留 location 作為節點 translation，對齊 export_apply=True）
        rot_scale = obj.matrix_local.to_3x3().to_4x4()
        me.transform(rot_scale)
        me.calc_loop_triangles()
        corner_normals = me.corner_normals

        # 依 material_index 分組三角形
        buckets: dict[int, list] = {}
        for tri in me.loop_triangles:
            buckets.setdefault(tri.material_index, []).append(tri)

        primitives: list[dict] = []
        verts = me.vertices
        polys = me.polygons

        for m_slot_idx, tris in buckets.items():
            if not tris:
                continue
            bl_mat = me.materials[m_slot_idx] if m_slot_idx < len(me.materials) else None
            gltf_mat_idx = get_mat_idx(bl_mat)

            vert_map: dict[tuple, int] = {}
            pos_floats: list[float] = []
            nrm_floats: list[float] = []
            indices: list[int] = []

            min_x = min_y = min_z = 1e30
            max_x = max_y = max_z = -1e30

            for tri in tris:
                poly = polys[tri.polygon_index]
                use_smooth = poly.use_smooth
                fn = tri.normal

                for loop_idx in tri.loops:
                    v_idx = me.loops[loop_idx].vertex_index
                    co = verts[v_idx].co
                    nn = corner_normals[loop_idx].vector if use_smooth else fn

                    # Blender (x, y, z) -> glTF (x, z, -y)
                    gx, gy, gz = float(co.x), float(co.z), float(-co.y)
                    nx, ny, nz = float(nn.x), float(nn.z), float(-nn.y)

                    key = (
                        v_idx,
                        round(nx, 4),
                        round(ny, 4),
                        round(nz, 4),
                    )
                    out_i = vert_map.get(key)
                    if out_i is None:
                        out_i = len(pos_floats) // 3
                        vert_map[key] = out_i
                        pos_floats.extend((gx, gy, gz))
                        nrm_floats.extend((nx, ny, nz))
                        if gx < min_x:
                            min_x = gx
                        if gy < min_y:
                            min_y = gy
                        if gz < min_z:
                            min_z = gz
                        if gx > max_x:
                            max_x = gx
                        if gy > max_y:
                            max_y = gy
                        if gz > max_z:
                            max_z = gz
                    indices.append(out_i)

            v_count = len(pos_floats) // 3
            pos_bytes = struct.pack(f"<{len(pos_floats)}f", *pos_floats)
            nrm_bytes = struct.pack(f"<{len(nrm_floats)}f", *nrm_floats)
            use_u32 = v_count > 65535
            idx_bytes = (
                struct.pack(f"<{len(indices)}I", *indices)
                if use_u32
                else struct.pack(f"<{len(indices)}H", *indices)
            )

            pos_bv = append_buffer_view(pos_bytes, 34962)
            nrm_bv = append_buffer_view(nrm_bytes, 34962)
            idx_bv = append_buffer_view(idx_bytes, 34963)

            pos_acc = len(accessors)
            accessors.append(
                {
                    "bufferView": pos_bv,
                    "componentType": 5126,
                    "count": v_count,
                    "type": "VEC3",
                    "min": [min_x, min_y, min_z],
                    "max": [max_x, max_y, max_z],
                }
            )
            nrm_acc = len(accessors)
            accessors.append(
                {
                    "bufferView": nrm_bv,
                    "componentType": 5126,
                    "count": v_count,
                    "type": "VEC3",
                }
            )
            idx_acc = len(accessors)
            accessors.append(
                {
                    "bufferView": idx_bv,
                    "componentType": 5125 if use_u32 else 5123,
                    "count": len(indices),
                    "type": "SCALAR",
                }
            )

            primitives.append(
                {
                    "attributes": {"POSITION": pos_acc, "NORMAL": nrm_acc},
                    "indices": idx_acc,
                    "material": gltf_mat_idx,
                    "mode": 4,
                }
            )

        bpy.data.meshes.remove(me)
        if not primitives:
            return None
        mesh_idx = len(meshes_gltf)
        meshes_gltf.append({"name": obj.name, "primitives": primitives})
        return mesh_idx

    obj_to_node_idx: dict[bpy.types.Object, int] = {}
    for obj in selected:
        loc = obj.location
        tx, ty, tz = float(loc.x), float(loc.z), float(-loc.y)
        node_dict: dict = {"name": obj.name}
        if abs(tx) > 1e-6 or abs(ty) > 1e-6 or abs(tz) > 1e-6:
            node_dict["translation"] = [tx, ty, tz]
        m_idx = build_mesh_gltf(obj)
        if m_idx is not None:
            node_dict["mesh"] = m_idx
        n_idx = len(nodes_gltf)
        nodes_gltf.append(node_dict)
        obj_to_node_idx[obj] = n_idx

    root_nodes: list[int] = []
    for obj in selected:
        n_idx = obj_to_node_idx[obj]
        if obj.parent in selected_set:
            p_idx = obj_to_node_idx[obj.parent]
            nodes_gltf[p_idx].setdefault("children", []).append(n_idx)
        else:
            root_nodes.append(n_idx)

    materials_gltf: list[dict] = []
    for m in mat_list:
        if m is None:
            materials_gltf.append(
                {
                    "name": "default",
                    "pbrMetallicRoughness": {
                        "baseColorFactor": [0.85, 0.82, 0.75, 1.0],
                        "metallicFactor": 0.0,
                        "roughnessFactor": 0.85,
                    },
                }
            )
            continue
        col = [0.8, 0.8, 0.8, 1.0]
        rough = 0.8
        metal = 0.0
        if m.node_tree:
            bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
            if bsdf:
                bc = bsdf.inputs["Base Color"].default_value
                col = [float(bc[0]), float(bc[1]), float(bc[2]), float(bc[3])]
                rough = float(bsdf.inputs["Roughness"].default_value)
                metal = float(bsdf.inputs["Metallic"].default_value)
        materials_gltf.append(
            {
                "name": m.name,
                "pbrMetallicRoughness": {
                    "baseColorFactor": col,
                    "metallicFactor": metal,
                    "roughnessFactor": rough,
                },
            }
        )

    bin_blob = b"".join(bin_chunks)
    gltf_json = {
        "asset": {"version": "2.0", "generator": "jos24-blender52-glb-writer"},
        "scene": 0,
        "scenes": [{"name": scene.name, "nodes": root_nodes}],
        "nodes": nodes_gltf,
        "meshes": meshes_gltf,
        "materials": materials_gltf,
        "accessors": accessors,
        "bufferViews": buffer_views,
        "buffers": [{"byteLength": len(bin_blob)}],
    }

    json_bytes = json.dumps(gltf_json, separators=(",", ":")).encode("utf-8")
    json_pad = (4 - (len(json_bytes) % 4)) % 4
    json_bytes += b" " * json_pad

    total_len = 12 + 8 + len(json_bytes) + 8 + len(bin_blob)
    header = struct.pack("<III", 0x46546C67, 2, total_len)
    chunk0 = struct.pack("<II", len(json_bytes), 0x4E4F534A) + json_bytes
    chunk1 = struct.pack("<II", len(bin_blob), 0x004E4942) + bin_blob

    with open(filepath, "wb") as f:
        f.write(header)
        f.write(chunk0)
        f.write(chunk1)

    return total_len
