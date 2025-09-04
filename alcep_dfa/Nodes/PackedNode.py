from .ForestNode import ForestNode


class PackedNode(ForestNode):

    def __init__(self, parent: ForestNode, left_node: ForestNode | None, right_node: ForestNode):
        """
        Initialize a PackedNode instance.

        :param parent: The parent node.
        :param left_node: The left child node.
        :param right_node: The right child node.
        """
        self.left_node = left_node
        self.right_node = right_node
        self.parent = parent

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
