from .visitor import Visitor
from alcep_dfa.Nodes import SymbolNode, PackedNode, EditNode, EndNode


class ShrinkToAllowedMappings(Visitor):

    def __init__(self, allowed_mapping: dict):
        self.allowed_mapping = allowed_mapping

    def visit_packed_node_in(self, node: PackedNode):
        yield node.left_node
        yield node.right_node

    def visit_symbol_node_in(self, node: SymbolNode):
        node_state_mapping = dict(node.state_mapping)

        is_mapping_allowed = all((node_state_mapping[key] == self.allowed_mapping[key]) for key in
                                 (node_state_mapping.keys() & self.allowed_mapping.keys())) \
                             and \
                             all(node_state_mapping[key] not in self.allowed_mapping.values() for key in
                                 node_state_mapping.keys() - self.allowed_mapping.keys())

        node.set_is_allowed_mapping(is_allowed_mapping=is_mapping_allowed)

        if is_mapping_allowed:
            return iter(node.get_children())

    def visit_packed_node_out(self, node: PackedNode):
        left_allowed_mapping = True
        rigth_allowed_mapping = True
        if node.left_node:
            match node.left_node:
                case SymbolNode():
                    left_allowed_mapping = node.left_node.get_is_allowed_mapping()
                case EditNode():
                    left_allowed_mapping = True
                case EndNode():
                    left_allowed_mapping = True
                case _:
                    raise Exception("Unexpected node type.")

        if node.right_node:
            match node.right_node:
                case SymbolNode():
                    rigth_allowed_mapping = node.right_node.get_is_allowed_mapping()
                case EditNode():
                    rigth_allowed_mapping = True
                case EndNode():
                    rigth_allowed_mapping = True
                case _:
                    raise Exception("Unexpected node type.")

        node.set_is_allowed_mapping(left_allowed_mapping and rigth_allowed_mapping)

    def visit_symbol_node_out(self, node: SymbolNode):
        if node.get_is_allowed_mapping():
            new_children = set()
            for child in node.get_children():
                if child.get_is_allowed_mapping():
                    new_children.add(child)

            if new_children:
                node.set_children(new_children)
            else:
                node.set_is_allowed_mapping(False)
