from .ForestNode import ForestNode


class PackedNode(ForestNode):

    def __init__(self, parent: ForestNode, left_node: ForestNode | None, right_node: ForestNode):
        """
        Initialize a PackedNode instance.

        :param parent: The parent node.
        :param left_node: The left child node.
        :param right_node: The right child node.
        """
        super().__init__()
        self.left_node = left_node
        self.right_node = right_node
        self.parent = parent
        self.is_allowed_mapping = None

    def get_right_node(self) -> ForestNode:
        """
        Get the right child node.

        :return: The right child node.
        """
        return self.right_node

    def get_left_node(self) -> ForestNode:
        """
        Get the left child node.

        :return: The left child node.
        """
        return self.left_node


    def set_is_allowed_mapping(self, is_allowed_mapping: bool):
        self.is_allowed_mapping = is_allowed_mapping

    def get_is_allowed_mapping(self) -> bool:
        return self.is_allowed_mapping

