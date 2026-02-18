from .visitor import Visitor


class ShrinkToAllowedMappings(Visitor):

    def __init__(self, allowed_mapping: dict):
        self.allowed_mapping = allowed_mapping

    def visit_packed_node_in(self, node):
        yield node.left_node
        yield node.right_node

    def visit_symbol_node_in(self, node):
        node_state_mapping = dict(node.state_mapping)

        is_mapping_allowed = all((node_state_mapping[key] == self.allowed_mapping[key]) for key in
                                 (node_state_mapping.keys() & self.allowed_mapping.keys())) \
                             and \
                             all(node_state_mapping[key] not in self.allowed_mapping.values() for key in
                                 node_state_mapping.keys() - self.allowed_mapping.keys())

        if is_mapping_allowed:
            return iter(node.get_children())
