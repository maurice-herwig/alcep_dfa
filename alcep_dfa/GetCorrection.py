from alcep_dfa.Nodes import SymbolNode, PackedNode, EditNode, EndNode
import random


def get_random_correction(root_node: SymbolNode) -> list:
    """
    Get a random correction from the SPPF rooted at the given root node.

    :param root_node: The root SymbolNode of the SPPF or a subtree.
    :return: A list of edit operations representing a random correction.
    """
    # Select a random child from the root node's children
    children = root_node.get_children()
    selected_child: PackedNode = random.choice(children)

    # Get the edit operations of the child's right child node
    child_right_child = selected_child.get_right_node()
    match child_right_child:
        case SymbolNode():
            right_correction = get_random_correction(child_right_child)
        case EditNode():
            right_correction = child_right_child.get_edit_operations()
        case EndNode():
            right_correction = []
        case _:
            raise Exception("The right child must be set")

    # Get the correction of the left child node if it exists
    child_left_child = selected_child.get_left_node()
    match child_left_child:
        case None:
            left_correction = []
        case SymbolNode():
            left_correction = get_random_correction(child_left_child)
        case _:
            raise Exception("The left child must be either None or a SymbolNode")

    return right_correction + left_correction
