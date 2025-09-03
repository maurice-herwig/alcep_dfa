from .ForestNode import ForestNode


class EditNode(ForestNode):

    def __init__(self, edit_operations: list):
        """
        Initialize an EditNode instance.
        """
        self.edit_operations = edit_operations
