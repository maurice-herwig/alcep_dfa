from .visitor import Visitor
from alcep_dfa.Nodes import SymbolNode, EditNode, EndNode, PackedNode
from alcep_dfa.Nodes.EditOperations import *


class MinCorrectionVisitor(Visitor):

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
        return iter(node.get_children())

    def visit_packed_node_out(self, node: PackedNode):
        """
        Visit a PackedNode and calculate its minimal edits based on its child nodes.

        :param node: The PackedNode to visit.
        :return: None
        """
        try:
            if node.left_node is None:
                node.set_minimal_edits(edits=node.right_node.get_all_minimal_edits(),
                                       costs=node.right_node.get_minimal_edits_costs())
            elif node.right_node is None:
                node.set_minimal_edits(edits=node.left_node.get_all_minimal_edits(),
                                       costs=node.left_node.get_minimal_edits_costs())
            else:
                all_min_edits = []

                for min_edits_left in node.left_node.get_all_minimal_edits():
                    for min_edits_right in node.right_node.get_all_minimal_edits():
                        all_min_edits.append(min_edits_right + min_edits_left)

                node.set_minimal_edits(edits=all_min_edits,
                                       costs=node.left_node.get_minimal_edits_costs() +
                                             node.right_node.get_minimal_edits_costs())
        except:
            # If the get method raise an exception then the value is not set. This implies that the same node
            # is also a successor of the current packed node. In addition, no minimal arises from unwind loops.
            # Therefor if the min edit for a predecessor is not set, then it cannot be lead to minimal correction.
            pass

    def visit_symbol_node_out(self, node: SymbolNode):
        """
        Visit a SymbolNode and calculate its minimal edits based on its child nodes.

        :param node: The SymbolNode to visit.
        :return: None
        """
        all_min_edits = []
        min_costs = None
        first = True

        for child in node.get_children():
            try:
                child_costs = child.get_minimal_edits_costs()
            except:
                # If the get method raise an exception then the value is not set. This implies that the same node
                # is also a successor of the current symbol node. In addition, no minimal arises from unwind loops.
                # Therefor if the min edit for a predecessor is not set, then it cannot be lead to minimal correction.
                continue

            if first or child_costs < min_costs:
                min_costs = child_costs
                all_min_edits = child.get_all_minimal_edits()
                first = False
            elif child_costs == min_costs:
                all_min_edits.extend(child.get_all_minimal_edits())

        if not first:
            node.set_minimal_edits(edits=all_min_edits, costs=min_costs)

    def visit_end_node(self, node: EndNode):
        """
        Visit an EndNode and set its minimal edits to an empty list with zero cost.

        :param node: The EndNode to visit.
        :return: None
        """
        node.set_minimal_edits(edits=[[]], costs=0)

    def visit_edit_node(self, node: EditNode):
        """
        Visit an EditNode and calculate the total cost of its edit operations.

        :param node: The EditNode to visit.
        :return: None
        """

        # Calculate the total cost of the edit operations of the node
        sum_of_costs = 0
        for edit in node.get_edit_operations():
            match edit:
                case AddNewState():
                    sum_of_costs += self.costs_add_new_state
                case AddTransition():
                    sum_of_costs += self.costs_add_transition
                case LeaveInitial():
                    sum_of_costs += self.costs_leave_initial
                case LeaveTransition():
                    sum_of_costs += self.costs_leave_transition
                case MarkAsInitial():
                    sum_of_costs += self.costs_mark_as_initial
                case MarkStateAsFinal():
                    sum_of_costs += self.costs_mark_final
                case MarkStateAsNonFinal():
                    sum_of_costs += self.costs_mark_non_final
                case RemoveMarkAsInitial():
                    sum_of_costs += self.costs_remove_initial
                case RemoveTransition():
                    sum_of_costs += self.costs_remove_transition

        node.set_minimal_edits(edits=[[node.get_edit_operations()]], costs=sum_of_costs)
