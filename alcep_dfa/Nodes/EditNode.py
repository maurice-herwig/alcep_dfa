from .ForestNode import ForestNode


class EditNode(ForestNode):

    def __init__(self, edit_operations: list):
        """
        Initialize an EditNode instance.
        """
        super().__init__()
        self.edit_operations = edit_operations

    def get_edit_operations(self) -> list:
        """
        Get the edit operations of the EditNode.

        :return: A list of edit operations.
        """
        return self.edit_operations
