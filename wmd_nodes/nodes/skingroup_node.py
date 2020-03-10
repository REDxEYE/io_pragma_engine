import bpy
from bpy.types import Node
from typing import List, Union

from .base_node import PragmaModelTreeNode
from .input_material_node import PragmaMaterialNode
from ..sockets import PragmaMaterialSocket, PragmaSkinGroupSocket


class PragmaSkinGroupProto:
    def __init__(self):
        self.name: str = ""
        self.materials: List[bpy.types.Material] = []

    def __str__(self):
        tmp = f'Skingroup\n'
        for obj in self.materials:
            tmp += "\t" + obj.name
        tmp += '\n'
        return tmp


class PragmaSkingroupNode(Node, PragmaModelTreeNode):
    bl_idname = 'PragmaSkingroupNode'
    bl_label = "Skingroup"

    # bodygroup_name: bpy.props.StringProperty(name="Bodygroup name")

    def init(self, context):
        self.inputs.new('PragmaMaterialSocket', "Material")

        self.outputs.new('PragmaSkinGroupSocket', "Skingroup")

    def update(self, ):
        unused_count = 0
        for o in self.inputs:  # type:PragmaMaterialSocket
            if (not o.is_linked and o.material is None) and o.bl_idname == "PragmaMaterialSocket":
                unused_count += 1
        if unused_count > 1:
            for _ in range(unused_count - 1):
                self.inputs.remove(self.inputs[-1])
        if unused_count == 0:
            self.inputs.new("PragmaMaterialSocket", "Material")

    def draw_buttons(self, context, layout):
        self.update()

    def get_value(self):
        proto = PragmaSkinGroupProto()
        for input_socket in self.inputs:  # type:PragmaMaterialSocket
            if input_socket.is_linked:
                obj_node: PragmaMaterialNode = input_socket.links[0].from_node
                proto.materials.append(obj_node.get_value().mat)
            else:
                if input_socket.material:
                    proto.materials.append(input_socket.material)
        return proto


class PragmaSkinProto:
    def __init__(self):
        self.skins: List[PragmaSkinGroupProto] = []

    def __str__(self):
        tmp = "Skins:\n"
        for skin in self.skins:
            tmp += '\t' + str(skin) + '\n'
        return tmp


class PragmaSkinNode(Node, PragmaModelTreeNode):
    bl_idname = 'PragmaSkinNode'
    bl_label = "Skins"

    # bodygroup_name: bpy.props.StringProperty(name="Bodygroup name")

    def init(self, context):
        self.inputs.new('PragmaSkinGroupSocket', "Skingroups")

        self.outputs.new('PragmaSkinSocket', "Skins")

    def update(self, ):
        unused_count = 0
        for o in self.inputs:
            if (not o.is_linked) and o.bl_idname == "PragmaSkinGroupSocket":
                unused_count += 1
        if unused_count > 1:
            for _ in range(unused_count - 1):
                self.inputs.remove(self.inputs[-1])
        if unused_count == 0:
            self.inputs.new("PragmaSkinGroupSocket", "Skingroups")

    def draw_buttons(self, context, layout):
        self.update()

    def get_value(self):
        proto = PragmaSkinProto()
        for input_socket in self.inputs:  # type:PragmaSkinGroupSocket
            if input_socket.is_linked:
                obj_node: PragmaMaterialNode = input_socket.links[0].from_node
                proto.skins.append(obj_node.get_value())
        return proto
