from bpy.types import Node
import bpy

from .base_node import PragmaModelTreeNode


class PragmaMaterialProto:
    def __init__(self):
        self.mat = None


class PragmaMaterialNode(Node, PragmaModelTreeNode):
    bl_idname = 'PragmaMaterialNode'
    bl_label = 'Material Node'
    mat: bpy.props.PointerProperty(type=bpy.types.Material, name="Material")

    def init(self, context):
        self.outputs.new('PragmaMaterialSocket', "Material")

    def draw_buttons(self, context, layout):
        layout.prop(self, "mat")

    def get_value(self):
        obj = PragmaMaterialProto()
        obj.mat = self.mat
        return obj
