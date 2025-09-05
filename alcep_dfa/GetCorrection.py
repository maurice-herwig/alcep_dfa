from alcep_dfa.Nodes import SymbolNode, PackedNode, EditNode, EndNode
from alcep_dfa.Visitors import MinCorrectionVisitor
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
            right_correction = [child_right_child.get_edit_operations()]
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


def get_all_minimal_corrections(root_node: SymbolNode,
                                costs_add_new_state=1, costs_add_transition=1, costs_leave_initial=0,
                                costs_leave_transition=0, costs_mark_as_initial=1, costs_mark_final=1,
                                costs_mark_non_final=1, costs_remove_initial=1,
                                costs_remove_transition=1) -> (int, list):
    """
    Compute all minimal corrections depending on the costs for each edit operation.

    :param root_node: The root_node of the sppf that represent all minimal corrections.
    :param costs_add_new_state: The costs for adding a new state.
    :param costs_add_transition:
    :param costs_leave_initial:
    :param costs_leave_transition:
    :param costs_mark_as_initial:
    :param costs_mark_final:
    :param costs_mark_non_final:
    :param costs_remove_initial:
    :param costs_remove_transition:
    :return:
    """

    # Greate a minimal correction visitor
    visitor = MinCorrectionVisitor(costs_add_new_state=costs_add_new_state,
                                   costs_add_transition=costs_add_transition,
                                   costs_leave_initial=costs_leave_initial,
                                   costs_leave_transition=costs_leave_transition,
                                   costs_mark_as_initial=costs_mark_as_initial,
                                   costs_mark_final=costs_mark_final,
                                   costs_mark_non_final=costs_mark_non_final,
                                   costs_remove_initial=costs_remove_initial,
                                   costs_remove_transition=costs_remove_transition)

    # Use the visitor to set for each node the minimal edits attribute.
    visitor.visit(root_node=root_node)

    # Return the minimal costs and all minimal edit operations.
    return root_node.get_minimal_edits_costs(), root_node.get_all_minimal_edits()
