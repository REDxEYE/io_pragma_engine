from bpy.types import NodeSocket
import bpy


class PragmaObjectSocket(NodeSocket):
    bl_idname = 'PragmaObjectSocket'
    bl_lable = 'Object socket'
    type = "OBJECT"

    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def draw_color(self, context, node):
        return 0.2, 0.2, 0.2, 1.0
