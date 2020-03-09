from bpy.types import Node
import bpy

from .base_node import PragmaModelTreeNode


class PragmaObjectNode(Node, PragmaModelTreeNode):
    bl_idname = 'PragmaObjectNode'
    bl_label = 'Object Node'
    obj: bpy.props.PointerProperty(type=bpy.types.Object, name="Mesh object")

    def init(self, context):
        self.outputs.new('PragmaObjectSocket', "Object")

    def draw_buttons(self, context, layout):
        layout.prop(self, "obj")
