import bpy

from . import nodes
from . import sockets
from .model_tree_nodes import *

### Node Categories ###
# Node categories are a python system for automatically
# extending the Add menu, toolbar panels and search operator.
# For more examples see release/scripts/startup/nodeitems_builtins.py

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem


# our own base class with an appropriate poll function,
# so the categories only show up in our own tree type


class PragmaNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'PragmaModelDefinition'


# all categories in a list
node_categories = [
    # identifier, label, items list
    PragmaNodeCategory('Output', "Output", items=[
        # our basic node
        NodeItem("PragmaModelNode"),
    ]),
    PragmaNodeCategory("Inputs", "Inputs", items=[
        NodeItem("PragmaObjectNode"),
        NodeItem("PragmaMaterialNode"),
    ]),
    PragmaNodeCategory("Skins", "Skins", items=[
        NodeItem("PragmaSkingroupNode"),
        NodeItem("PragmaSkinNode"),
    ]),
    PragmaNodeCategory("Bodygroups", "Bodygroups", items=[
        NodeItem("PragmaBodygroupNode")
    ])
]

classes = (
    PragmaModelTree,

    nodes.PragmaObjectNode,
    nodes.PragmaModelNode,
    nodes.PragmaMaterialNode,

    nodes.PragmaBodygroupNode,
    nodes.PragmaSkinNode,
    nodes.PragmaSkingroupNode,

    sockets.PragmaObjectSocket,
    sockets.PragmaBodygroupSocket,
    sockets.PragmaMaterialSocket,
    sockets.PragmaSkinSocket,
    sockets.PragmaSkinGroupSocket,

    PragmaEvaluateNodeTree
)


def register_nodes():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    nodeitems_utils.register_node_categories('CUSTOM_NODES', node_categories)


def unregister_nodes():
    nodeitems_utils.unregister_node_categories('CUSTOM_NODES')

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
