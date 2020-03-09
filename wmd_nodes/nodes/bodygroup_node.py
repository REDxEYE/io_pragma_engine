import bpy
from bpy.types import Node
from .base_node import PragmaModelTreeNode


class PragmaBodygroupNode(Node, PragmaModelTreeNode):
    bl_idname = 'PragmaBodygroupNode'
    bl_label = "Bodygroup"
    bodygroup_name: bpy.props.StringProperty(name="Bodygroup name")

    def init(self, context):
        ob = self.inputs.new('PragmaObjectSocket', "Objects")
        ob.link_limit = 4096

        self.outputs.new('PragmaBodygroupSocket', "bodygroup")

    def update(self, ):
        unused_count = 0
        for o in self.inputs:
            if (not o.is_linked) and o.bl_idname == "PragmaObjectSocket":
                unused_count += 1
        if unused_count > 1:
            for _ in range(unused_count - 1):
                self.inputs.remove(self.inputs[-1])
        if unused_count == 0:
            ob = self.inputs.new("PragmaObjectSocket", "Objects")
            ob.link_limit = 4096

    def draw_buttons(self, context, layout):
        layout.prop(self, 'bodygroup_name')

    def draw_label(self):
        return 'Bodygroup: {}'.format(self.bodygroup_name)
