from pathlib import Path

if __name__ == '__main__':
    import sys

    sys.path.append(r"F:\PYTHON_STUFF\blender_wmd")

from PyWMD.byte_io_wmd import ByteIO
from PyWMD.pragma_model import PragmaModel, PragmaBone
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
        bl_bone.tail = Vector([0, 0, 1]) + bl_bone.head

    bpy.ops.object.mode_set(mode='POSE')
    for root_bone in model.armature.roots:
        pose_bone(root_bone, armature_obj)

    bpy.ops.pose.armature_apply()
    bpy.ops.object.mode_set(mode='OBJECT')
    return armature_obj


def import_model(model_path: str):
    model_path = Path(model_path)
    reader = ByteIO(path=model_path)
    if PragmaModel.check_header(reader):
        model = PragmaModel()
        model.from_file(reader)
        model.set_name(model_path.stem)
        main_collection = bpy.data.collections.new(model_path.stem)
        bpy.context.scene.collection.children.link(main_collection)
        create_armature(model, main_collection)
        pass


if __name__ == '__main__':
    import_model(r"F:\PYTHON_STUFF\PyWMD\test_data\medic.wmd")
