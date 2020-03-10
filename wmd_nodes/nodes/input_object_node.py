from bpy.types import Node
import bpy

from .base_node import PragmaModelTreeNode


class PragmaBlankObjectProto:
    class BlankObject:
        name= "BLANK"

    @property
    def obj(self):
        return PragmaBlankObjectProto.BlankObject


class PragmaObjectProto:
    def __init__(self):
        self.obj = None


class PragmaObjectNode(Node, PragmaModelTreeNode):
    bl_idname = 'PragmaObjectNode'
    bl_label = 'Object Node'
    obj: bpy.props.PointerProperty(type=bpy.types.Object, name="Mesh object")
    blank: bpy.props.BoolProperty(name="Blank object")

    def init(self, context):
        self.outputs.new('PragmaObjectSocket', "Object")

    def draw_buttons(self, context, layout):
        layout.prop(self, "blank")
        if not self.blank:
            layout.prop(self, "obj")

    def get_value(self):
        if self.blank:
            return PragmaBlankObjectProto()
        else:
            obj = PragmaObjectProto()
            obj.obj = self.obj
            return obj
