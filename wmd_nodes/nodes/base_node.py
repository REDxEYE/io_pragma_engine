
class PragmaModelTreeNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'PragmaModelDefinition'

    def get_value(self):
        return None