from typing import List

import bpy
from bpy.types import NodeTree, Node, Operator
from . import nodes


class PragmaEvaluateNodeTree(Operator):
    bl_idname = "pragma.evaluate_nodetree"
    bl_label = "Evaluate tree"
    tmp_file: bpy.types.Text

    def execute(self, context: bpy.types.Context):
        if not bpy.data.texts.get('qc', False):
            self.tmp_file = bpy.data.texts.new('qc')
        else:
            self.tmp_file = bpy.data.texts['qc']
        all_nodes = context.space_data.node_tree.nodes
        outputs = []  # type:List[Node]
        for node in all_nodes:  # type: Node
            if node.bl_idname == "PragmaModelNode":
                outputs.append(node)
        for output in outputs:  # type:nodes.PragmaModelNode
            self.traverse_tree(output)
        return {'FINISHED'}

    def traverse_tree(self, start_node: nodes.PragmaModelNode):
        self.tmp_file.write(start_node.model_name + "\n")
        objects = start_node.inputs['Objects']
        bodygroups = start_node.inputs['Bodygroups']
        if objects.is_linked:
            for link in objects.links:
                self.tmp_file.write("\tmesh " + link.from_node.obj.name + "\n")
        else:
            self.tmp_file.write("\tmesh " + objects.obj.name + "\n")

        if bodygroups.is_linked:
            self.tmp_file.write("Bodygroups:\n")
            for link in bodygroups.links:
                self.tmp_file.write('\t"{}"\n'.format(link.from_node.bodygroup_name))


class PragmaModelTree(NodeTree):
    bl_idname = 'PragmaModelDefinition'
    bl_label = "Pragma model definition"
    bl_icon = 'NODETREE'

    def update(self, ):
        for link in self.links:  # type:bpy.types.NodeLink
            if link.from_socket.bl_idname != link.to_socket.bl_idname:
                self.links.remove(link)
        self.check_link_duplicates()

    def check_link_duplicates(self):
        to_remove = []
        for link in self.links:
            for link2 in self.links:
                if link == link2 or link in to_remove:
                    continue
                if link.from_node == link2.from_node and link.to_node == link2.to_node:
                    to_remove.append(link2)
                    break
        for link in to_remove:
            self.links.remove(link)
