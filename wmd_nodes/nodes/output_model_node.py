import bpy
from bpy.types import Node
from .base_node import PragmaModelTreeNode


class PragmaModelNode(Node, PragmaModelTreeNode):
    bl_idname = 'PragmaModelNode'
    bl_label = "Model output"
    model_name_prop: bpy.props.StringProperty(name="Model name")

    def init(self, context):
        self.inputs.new('PragmaObjectSocket', "Objects").link_limit = 4096
        self.inputs.new('PragmaBodygroupSocket', "Bodygroups").link_limit = 4096
        self.inputs.new('PragmaSkinSocket', "Skin")


    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        layout.prop(self, 'model_name_prop')
        layout.operator("pragma.evaluate_nodetree")

    def draw_label(self):
        return self.bl_label

    @property
    def model_name(self):
        return self.model_name_prop
