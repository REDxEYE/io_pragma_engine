from bpy.types import NodeSocket
import bpy


class PragmaSkinSocket(NodeSocket):
    bl_idname = 'PragmaSkinSocket'
    bl_lable = 'Skin socket'
    type = "SKIN"

    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def draw_color(self, context, node):
        return 0.4, 0.8, 0.2, 1.0

class PragmaSkinGroupSocket(NodeSocket):
    bl_idname = 'PragmaSkinGroupSocket'
    bl_lable = 'Skin group socket'
    type = "SKINGROUP"

    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def draw_color(self, context, node):
        return 1, 0.8, 0.2, 1.0
