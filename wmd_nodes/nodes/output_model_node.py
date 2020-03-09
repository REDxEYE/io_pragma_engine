import bpy
from bpy.types import Node
from .base_node import PragmaModelTreeNode


class PragmaModelNode(Node, PragmaModelTreeNode):
    bl_idname = 'PragmaModelNode'
    bl_label = "Model output"
    model_name_prop: bpy.props.StringProperty(name="Model name")

    def init(self, context):
        ob = self.inputs.new('PragmaObjectSocket', "Objects")
        ob.link_limit = 4096

        bd = self.inputs.new('PragmaBodygroupSocket', "Bodygroups")
        bd.link_limit = 4096

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        layout.prop(self, 'model_name_prop')
        layout.operator("pragma.evaluate_nodetree")

    def draw_label(self):
        return self.bl_label

    @property
    def model_name(self):
        return self.model_name_prop
