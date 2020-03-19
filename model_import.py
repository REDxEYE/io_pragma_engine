import random
from pathlib import Path

from .PyWMD.byte_io_wmd import ByteIO, split
from .PyWMD.pragma_model import PragmaModel, PragmaBone, PragmaMeshV24Plus, PragmaSubMeshGeometryType
import bpy
from mathutils import Vector, Quaternion, Matrix


def get_material(mat_name, model_ob):
    if mat_name:
        mat_name = mat_name
    else:
        mat_name = "Material"
    mat_ind = 0
    md = model_ob.data
    mat = None
    for candidate in bpy.data.materials:  # Do we have this material already?
        if candidate.name == mat_name:
            mat = candidate
    if mat:
        if md.materials.get(mat.name):  # Look for it on this mesh_data
            for i in range(len(md.materials)):
                if md.materials[i].name == mat.name:
                    mat_ind = i
                    break
        else:  # material exists, but not on this mesh_data
            md.materials.append(mat)
            mat_ind = len(md.materials) - 1
    else:  # material does not exist
        mat = bpy.data.materials.new(mat_name)
        md.materials.append(mat)
        # Give it a random colour
        rand_col = []
        for i in range(3):
            rand_col.append(random.uniform(.4, 1))
        rand_col.append(1.0)
        mat.diffuse_color = rand_col

        mat_ind = len(md.materials) - 1

    return mat_ind


def create_child_bones(root_bone: PragmaBone, parent, armature):
    for child in root_bone.childs:
        bone = armature.edit_bones.new(child.name)
        bone.parent = parent
        create_child_bones(child, bone, armature)


def pose_bone(root_bone: PragmaBone, armature):
    bl_bone = armature.pose.bones.get(root_bone.name)
    pos = Vector(root_bone.position.values)
    rot = Quaternion(root_bone.rotation.values)
    print(f'Posing "{root_bone.name}" POS:{pos} ROT:{rot}')
    mat = Matrix.Translation(pos) @ rot.to_matrix().to_4x4()
    bl_bone.matrix_basis.identity()
    if bl_bone.parent:
        bl_bone.matrix = bl_bone.parent.matrix @ mat
    else:
        bl_bone.matrix = mat
    for child in root_bone.childs:
        pose_bone(child, armature)


def create_armature(model: PragmaModel, collection):
    bpy.ops.object.armature_add(enter_editmode=True)

    armature_obj = bpy.context.object
    try:
        bpy.context.scene.collection.objects.unlink(armature_obj)
    except:
        pass

    collection.objects.link(armature_obj)
    armature_obj.name = model.name + '_ARM'
    armature = armature_obj.data
    armature.name = model.name + "_ARM_DATA"

    armature_obj.select_set(True)
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='EDIT')
    armature.edit_bones.remove(armature.edit_bones[0])

    for root_bone in model.armature.roots:
        bone = armature.edit_bones.new(root_bone.name)
        create_child_bones(root_bone, bone, armature)

    for bone in model.armature.bones:  # type: PragmaBone
        bl_bone = armature.edit_bones.get(bone.name)
        bl_bone.tail = Vector([1, 0, 0]) + bl_bone.head

        pos = Vector(bone.position.values)
        rot = Quaternion(bone.rotation.values)
        bl_bone.transform(Matrix.Translation(pos) @ rot.to_matrix().to_4x4())

    bpy.ops.object.mode_set(mode='OBJECT')
    return armature_obj


def build_meshgroup(group, model, armature, collection):
    if len(group.sub_meshes) == 0:
        return
    for sub_mesh in group.sub_meshes:
        material = model.materials[sub_mesh.material_id]

        mesh_obj = bpy.data.objects.new(f"{group.name}_{material}",
                                        bpy.data.meshes.new(
                                            f'{group.name}_{material}_SUB_MESH'))  # type:bpy.types.Object
        mesh_obj.parent = armature
        collection.objects.link(mesh_obj)
        modifier = mesh_obj.modifiers.new(
            type="ARMATURE", name="Armature")
        modifier.object = armature

        mesh_data = mesh_obj.data  # type:bpy.types.Mesh
        split_value = 3 if sub_mesh.geometry_type == PragmaSubMeshGeometryType.Triangles else 4
        mesh_data.from_pydata(sub_mesh.vertices, [], split(sub_mesh.indices, split_value))
        mesh_data.update()

        get_material(material, mesh_obj)

        bpy.ops.object.select_all(action="DESELECT")
        mesh_obj.select_set(True)
        bpy.context.view_layer.objects.active = mesh_obj
        bpy.ops.object.shade_smooth()

        mesh_data.use_auto_smooth = True
        mesh_data.normals_split_custom_set_from_vertices(sub_mesh.normals)

        for uv_set_name, uv_set in sub_mesh.uv_sets.items():
            uv_layer = mesh_data.uv_layers.new(name=uv_set_name)
            uv_data = uv_layer.data
            for i in range(len(uv_data)):
                u = uv_set[mesh_data.loops[i].vertex_index]
                x = u[0]*1.333
                y = u[1]*1.333
                uv_data[i].uv = (x,y)

        weight_groups = {bone.name: mesh_obj.vertex_groups.new(name=bone.name) for bone in
                         model.armature.bones}
        id2bone_name = {i: bone.name for i, bone in enumerate(model.armature.bones)}

        for n, (bone_ids, weights) in enumerate(sub_mesh.weights):
            for bone_id, weight in zip(bone_ids, weights):
                if weight == 0.0 or bone_id == -1:
                    continue
                weight_groups[id2bone_name[bone_id]].add([n], weight, 'REPLACE')
        for n, (bone_ids, weights) in enumerate(sub_mesh.additional_weights):
            for bone_id, weight in zip(bone_ids, weights):
                if weight == 0.0 or bone_id == -1:
                    continue
                weight_groups[id2bone_name[bone_id]].add([n], weight, 'REPLACE')

        mesh_obj.shape_key_add(name='Base')

        for flex_name, flex_info in sub_mesh.flexes.items():
            frame = flex_info.frames[0]

            if not mesh_obj.data.shape_keys.key_blocks.get(flex_name):
                mesh_obj.shape_key_add(name=flex_name)

            for vid, v, _ in frame:
                vertex = mesh_obj.data.vertices[vid]
                vx = vertex.co.x
                vy = vertex.co.y
                vz = vertex.co.z
                fx, fy, fz = v.values
                mesh_obj.data.shape_keys.key_blocks[flex_name].data[vid].co = (
                    fx + vx, fy + vy, fz + vz)


def create_model(model, armature, collection):
    if model.mesh.bodygroups:
        for bodygroup_name, bodygroup in model.mesh.bodygroups.items():
            bodygroup_collection = bpy.data.collections.new("BP_" + bodygroup_name)
            collection.children.link(bodygroup_collection)
            for group in bodygroup:
                group_collection = bpy.data.collections.new(group.name)
                bodygroup_collection.children.link(group_collection)
                build_meshgroup(group, model, armature, group_collection)
    else:
        for group_id in set(model.mesh.group_ids):
            group = model.mesh.mesh_groups[group_id]
            build_meshgroup(group, model, armature, collection)


def import_model(model_path: str):
    model_path = Path(model_path)
    reader = ByteIO(path=model_path)
    if PragmaModel.check_header(reader):
        model = PragmaModel()
        model.from_file(reader)
        model.set_name(model_path.stem)
        main_collection = bpy.data.collections.new(model_path.stem)
        bpy.context.scene.collection.children.link(main_collection)
        armature = create_armature(model, main_collection)
        create_model(model, armature, main_collection)


if __name__ == '__main__':
    import_model(r"F:\PYTHON_STUFF\PyWMD\test_data\medic.wmd")
