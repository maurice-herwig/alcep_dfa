from .visitor import Visitor
from alcep_dfa.Nodes import SymbolNode, EditNode, EndNode, PackedNode, ForestNode


class GetNumberOfCorrectionsVisitor(Visitor):

    def on_cycle(self, node: ForestNode, path: list):
        raise Exception("Cannot compute number of corrections, due the presence of cycles in the graph.")

    def visit_packed_node_in(self, node: PackedNode):
        yield node.left_node
        yield node.right_node

    def visit_symbol_node_in(self, node: SymbolNode):
        return iter(node.get_children())

    def visit_packed_node_out(self, node: PackedNode):
        if node.left_node is None:
            node.set_number_of_corrections(node.right_node.get_number_of_corrections())
        elif node.right_node is None:
            node.set_number_of_corrections(node.left_node.get_number_of_corrections())
        else:
            node.set_number_of_corrections(
                node.left_node.get_number_of_corrections() * node.right_node.get_number_of_corrections())

    def visit_symbol_node_out(self, node: SymbolNode):
        number_of_corrections = 0
        for child in node.get_children():
            number_of_corrections += child.get_number_of_corrections()
        node.set_number_of_corrections(number_of_corrections)

    def visit_end_node(self, node: EndNode):
        node.set_number_of_corrections(1)

    def visit_edit_node(self, node: EditNode):
        node.set_number_of_corrections(1)
