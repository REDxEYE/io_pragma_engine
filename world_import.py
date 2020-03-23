import random
from pathlib import Path

from .PyPragma.byte_io_wmd import ByteIO, split
from .PyPragma.wld import World, Entity
from .model_import import import_model

import bpy
from mathutils import Vector, Quaternion, Matrix



def import_map(world_path: str):
    wld_path = Path(world_path)
    reader = ByteIO(path=wld_path)
    if World.check_header(reader):
        world = World()
        world.from_file(reader)
        world_entity = world.get_entities_by_class("world")[0]
