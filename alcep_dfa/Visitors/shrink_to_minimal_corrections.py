from .visitor import Visitor
from alcep_dfa.Nodes import SymbolNode, PackedNode


class ShrinkToMinimal(Visitor):

    def __init__(self, costs_add_new_state, costs_add_transition, costs_leave_initial,
                 costs_leave_transition, costs_mark_as_initial, costs_mark_final,
                 costs_mark_non_final, costs_remove_initial, costs_remove_transition):
        self.costs_add_new_state = costs_add_new_state
        self.costs_add_transition = costs_add_transition
        self.costs_leave_initial = costs_leave_initial
        self.costs_leave_transition = costs_leave_transition
        self.costs_mark_as_initial = costs_mark_as_initial
        self.costs_mark_final = costs_mark_final
        self.costs_mark_non_final = costs_mark_non_final
        self.costs_remove_initial = costs_remove_initial
        self.costs_remove_transition = costs_remove_transition

    def visit_packed_node_in(self, node: PackedNode):
        yield node.left_node
        yield node.right_node

    def visit_symbol_node_in(self, node: SymbolNode):

        min_edits_costs = node.get_minimal_edits_costs()
        min_children = set()
        for child in node.get_children():
            try:
                if child.get_minimal_edits_costs() == min_edits_costs:
                    min_children.add(child)
            except:
                # If the get method raise an exception then the value is not set. This implies that the same node
                # is also a successor of the current packed node. In addition, no minimal arises from unwind loops.
                # Therefor if the min edit for a predecessor is not set, then it cannot be lead to minimal correction.
                continue

        if not min_children:
            raise Exception("There should be at least one child that leads to minimal correction.")

        # Set the children of the node to only the children that lead to minimal corrections.
        node.set_children(min_children)
        return iter(node.get_children())
