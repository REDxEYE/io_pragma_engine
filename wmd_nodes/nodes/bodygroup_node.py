import bpy
from bpy.types import Node
from typing import List, Union

from .base_node import PragmaModelTreeNode
from .blank_object_node import PragmaBlankObjectNode
from .input_object_node import PragmaObjectNode


class PragmaBodygroupProto:
    def __init__(self):
        self.name: str = ""
        self.objects: List[Union[bpy.types.Object, List[bpy.types.Object], None]] = []

    def __str__(self):
        tmp = f'"{self.name}"\n'
        for obj in self.objects:
            if type(obj) is list:
                tmp += "\t"
                for o in obj:
                    tmp += o.name + "+"
                tmp += '\n'
            else:
                tmp += "\t" + obj.name + '\n'
        return tmp


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
            if (not o.is_linked and o.obj is None) and o.bl_idname in ["PragmaObjectSocket", "PragmaBlankObjectNode"]:
                unused_count += 1
        if unused_count > 1:
            for _ in range(unused_count - 1):
                self.inputs.remove(self.inputs[-1])
        if unused_count == 0:
            ob = self.inputs.new("PragmaObjectSocket", "Objects")
            ob.link_limit = 4096

    def draw_buttons(self, context, layout):
        self.update()
        layout.prop(self, 'bodygroup_name')

    def draw_label(self):
        return 'Bodygroup: {}'.format(self.bodygroup_name)

    def get_value(self):
        proto = PragmaBodygroupProto()
        proto.name = self.bodygroup_name
        for input_socket in self.inputs:
            if input_socket.is_linked:
                if len(input_socket.links) > 1:
                    merge: List[bpy.types.Object] = []
                    for link in input_socket.links:
                        obj_node: Union[PragmaBlankObjectNode, PragmaObjectNode] = link.from_node
                        merge.append(obj_node.get_value())
                    proto.objects.append(merge)
                else:
                    obj_node: Union[PragmaBlankObjectNode, PragmaObjectNode] = input_socket.links[0].from_node
                    proto.objects.append(obj_node.get_value())
        return proto
