from bpy.types import NodeSocket
import bpy


class PragmaObjectSocket(NodeSocket):
    bl_idname = 'PragmaObjectSocket'
    bl_lable = 'Object socket'
    type = "OBJECT"
    obj: bpy.props.PointerProperty(type=bpy.types.Object, name="Mesh object")

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "obj", text=text)

    def draw_color(self, context, node):
        return 0.2, 0.2, 0.2, 1.0