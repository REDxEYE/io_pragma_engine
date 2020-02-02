import random
from pathlib import Path

from .PyWMD.byte_io_wmd import ByteIO
from .PyWMD.pragma_model import PragmaModel, PragmaBone, PragmaMeshV24Plus
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


def create_model(model, armature, collection):
    for bodygroup_name, bodygroup in model.mesh.bodygroups.items():
        bodygroup_collection = bpy.data.collections.new("BP_" + bodygroup_name)
        collection.children.link(bodygroup_collection)
        for group in bodygroup:
            group_collection = bpy.data.collections.new(group.name)
            bodygroup_collection.children.link(group_collection)
            if len(group.sub_meshes) == 0:
                continue
            for sub_mesh in group.sub_meshes:
                material = model.materials[sub_mesh.material_id]

                mesh_obj = bpy.data.objects.new(group.name + "_" + material,
                                                bpy.data.meshes.new('{}_{}_SUB_MESH'.format(group.name, material)))
                mesh_obj.parent = armature
                group_collection.objects.link(mesh_obj)
                modifier = mesh_obj.modifiers.new(
                    type="ARMATURE", name="Armature")
                modifier.object = armature

                mesh_data = mesh_obj.data
                mesh_data.from_pydata(sub_mesh.vertices, [], sub_mesh.indices)
                mesh_data.update()

                get_material(material, mesh_obj)

                bpy.ops.object.select_all(action="DESELECT")
                mesh_obj.select_set(True)
                bpy.context.view_layer.objects.active = mesh_obj
                bpy.ops.object.shade_smooth()

                mesh_data.use_auto_smooth = True
                mesh_data.normals_split_custom_set_from_vertices(sub_mesh.normals)

                mesh_data.uv_layers.new()
                uv_data = mesh_data.uv_layers[0].data
                for i in range(len(uv_data)):
                    u = sub_mesh.uvs[mesh_data.loops[i].vertex_index]
                    uv_data[i].uv = u

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
