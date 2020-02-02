from pathlib import Path

if __name__ == '__main__':
    import sys

    sys.path.append(r"F:\PYTHON_STUFF\blender_wmd")

from PyWMD.byte_io_wmd import ByteIO
from PyWMD.pragma_model import PragmaModel, PragmaBone, PragmaMeshV24Plus
import bpy
from mathutils import Vector, Quaternion, Matrix


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
                mesh_obj = bpy.data.objects.new(group.name, bpy.data.meshes.new('{}_MESH'.format(group.name)))
                mesh_obj.parent = armature
                group_collection.objects.link(mesh_obj)
                modifier = mesh_obj.modifiers.new(
                    type="ARMATURE", name="Armature")
                modifier.object = armature

                mesh_data = mesh_obj.data
                mesh_data.from_pydata(sub_mesh.vertices, [], sub_mesh.indices)
                mesh_data.update()
                mesh_data.use_auto_smooth = True
                mesh_data.normals_split_custom_set_from_vertices (sub_mesh.normals)


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
