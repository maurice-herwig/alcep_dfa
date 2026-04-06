from .visitor import Visitor
from alcep_dfa.Nodes import SymbolNode, EditNode, EndNode, PackedNode, ForestNode


class GetAllEditsVisitor(Visitor):

    def on_cycle(self, node: ForestNode, path: list):
        raise Exception("Cannot compute all edits, due the presence of cycles in the graph.")

    def visit_packed_node_in(self, node: PackedNode):
        yield node.left_node
        yield node.right_node

    def visit_symbol_node_in(self, node: SymbolNode):
        return iter(node.get_children())

    def visit_packed_node_out(self, node: PackedNode):
        if node.left_node is None:
            node.set_all_edits(node.right_node.get_all_edits())
        elif node.right_node is None:
            node.set_all_edits(node.left_node.get_all_edits())
        else:
            if node.left_node.get_all_edits() and node.right_node.get_all_edits():
                all_edits = []
                for edits_left in node.left_node.get_all_edits():
                    for edits_right in node.right_node.get_all_edits():
                        all_edits.append(edits_right + edits_left)

                node.set_all_edits(all_edits)
            elif node.left_node.get_all_edits():
                node.set_all_edits(node.left_node.get_all_edits())
            elif node.right_node.get_all_edits():
                node.set_all_edits(node.right_node.get_all_edits())
            else:
                node.set_all_edits([])

    def visit_symbol_node_out(self, node: SymbolNode):
        all_edits = []
        for child in node.get_children():
            all_edits.extend(child.get_all_edits())
        node.set_all_edits(all_edits)

    def visit_end_node(self, node: EndNode):
        node.set_all_edits([])

    def visit_edit_node(self, node: EditNode):
        node.set_all_edits([[node.get_edit_operations()]])
