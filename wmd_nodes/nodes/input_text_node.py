from bpy.types import Node
import bpy
from .base_node import PragmaModelTreeNode


class PragmaStringNode(Node, PragmaModelTreeNode):
    bl_idname = 'PragmaStringNode'
    bl_label = 'String Node'
    value: bpy.props.StringProperty(name="String")

    def init(self, context):
        self.outputs.new('NodeSocketString', "String")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value")

    def get_value(self):
        return self.value