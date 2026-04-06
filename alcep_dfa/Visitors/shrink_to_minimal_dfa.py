from .visitor import Visitor
from alcep_dfa.Nodes import SymbolNode, EditNode, EndNode, PackedNode, ForestNode


class ShrinkToMinimalDFAs(Visitor):

    def visit_packed_node_in(self, node: PackedNode):
        yield node.left_node
        yield node.right_node

    def visit_symbol_node_in(self, node: SymbolNode):
        contained_in = node.get_contained_in_cor_to_minial_dfa()
        if contained_in is None:
            node.set_contained_in_cor_to_minial_dfa(True)
            return iter(node.get_children())

    def visit_packed_node_out(self, node: PackedNode):
        left_in_min = True
        right_in_min = True

        if node.left_node:
            match node.left_node:
                case SymbolNode():
                    left_in_min = node.left_node.get_contained_in_cor_to_minial_dfa()
                case EditNode():
                    left_in_min = True
                case EndNode():
                    left_in_min = True
                case _:
                    raise Exception("Unexpected node type.")

        if node.right_node:
            match node.right_node:
                case SymbolNode():
                    right_in_min = node.right_node.get_contained_in_cor_to_minial_dfa()
                case EditNode():
                    right_in_min = True
                case EndNode():
                    right_in_min = True
                case _:
                    raise Exception("Unexpected node type.")

        node.set_contained_in_cor_to_minial_dfa(left_in_min and right_in_min)

    def visit_symbol_node_out(self, node: SymbolNode):
        contained_in = node.get_contained_in_cor_to_minial_dfa()
        if contained_in:
            new_children = set()
            for child in node.get_children():
                if child.get_contained_in_cor_to_minial_dfa():
                    new_children.add(child)

            if new_children:
                node.set_children(new_children)
            else:
                node.set_contained_in_cor_to_minial_dfa(False)
