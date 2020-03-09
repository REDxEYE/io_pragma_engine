from bpy.types import Node
import bpy

from .base_node import PragmaModelTreeNode


class PragmaBlankObjectProto:
    class BlankObject:
        @property
        def name(self):
            return "BLANK"

    @property
    def obj(self):
        return self.BlankObject()


class PragmaBlankObjectNode(Node, PragmaModelTreeNode):
    bl_idname = 'PragmaBlankObjectNode'
    bl_label = 'Empty Object Node'

    def init(self, context):
        self.outputs.new('PragmaObjectSocket', "Object")

    def draw_buttons(self, context, layout):
        layout.label(text="Blank object")

    def get_value(self):
        return PragmaBlankObjectProto()
