import os
import sys
from pathlib import Path

bl_info = {
    "name": "Pragma Engine model(.wmd)",
    "author": "RED_EYE",
    "version": (0, 0, 3),
    "blender": (2, 80, 0),
    "location": "File > Import-Export > Import Pragma WMD file",
    "description": "Import/Export Pragma models",
    "category": "Import-Export"
}

import bpy
from bpy.props import StringProperty, BoolProperty, CollectionProperty, EnumProperty
from .model_import import import_model


class PyWMDPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    sfm_path: StringProperty(default='', name='SFM path')

    def draw(self, context):
        layout = self.layout
        # layout.label(text='Enter SFM install path:')
        # row = layout.row()
        # row.prop(self, 'sfm_path')


# noinspection PyUnresolvedReferences
class WMD_import_OT_operator(bpy.types.Operator):
    """Load Pragma Engine WMD models"""
    bl_idname = "py_wmd.wmd"
    bl_label = "Import Pragma WMD file"
    bl_options = {'UNDO'}

    filepath: StringProperty(subtype="FILE_PATH")
    files: CollectionProperty(name='File paths', type=bpy.types.OperatorFileListElement)

    import_textures: BoolProperty(name="Load textures", default=False, subtype='UNSIGNED')

    filter_glob: StringProperty(default="*.wmd", options={'HIDDEN'})

    def execute(self, context):

        if Path(self.filepath).is_file():
            directory = Path(self.filepath).parent.absolute()
        else:
            directory = Path(self.filepath).absolute()
        for file in self.files:
            import_model(str(directory / file.name))
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


classes = (PyWMDPreferences, WMD_import_OT_operator)
register_, unregister_ = bpy.utils.register_classes_factory(classes)


def menu_import(self, context):
    self.layout.operator(WMD_import_OT_operator.bl_idname, text="Pragma model (.wmd)")


def register():
    register_()
    bpy.types.TOPBAR_MT_file_import.append(menu_import)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_import)
    unregister_()


if __name__ == "__main__":
    register()
