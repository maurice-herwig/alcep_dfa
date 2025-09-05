from alcep_dfa.Nodes import SymbolNode, EditNode, EndNode, PackedNode, ForestNode
from collections import deque


class Visitor:
    """
    Most of the code in this class has been taken directly from the Lark Parser
    (https://github.com/lark-parser/lark/tree/master/lark).
    Only minor adjustments have been made to the data structure used here.
    """

    def visit_packed_node_in(self, node: PackedNode):
        pass

    def visit_symbol_node_in(self, node: SymbolNode):
        pass

    def visit_packed_node_out(self, node: PackedNode):
        pass

    def visit_symbol_node_out(self, node: SymbolNode):
        pass

    def visit_edit_node(self, node: EditNode):
        pass

    def visit_end_node(self, node: EndNode):
        pass

    def on_cycle(self, node: ForestNode, path: list):
        pass

    def visit(self, root_node: SymbolNode):
        # Visiting is a list of IDs of all symbol/intermediate nodes currently in
        # the stack. It serves two purposes: to detect when we 'recurse' in and out
        # of a symbol/intermediate so that we can process both up and down. Also,
        # since the SPPF can have cycles it allows us to detect if we're trying
        # to recurse into a node that's already on the stack (infinite recursion).
        visiting = set()

        # A list of nodes that are currently being visited. Used to detect cycle.
        path = []

        # We do not use recursion here to walk the Forest due to the limited stack size in python.
        # Therefore, input_stack is essentially our stack.
        input_stack = deque([(root_node)])

        # It is much faster to cache these as locals since they are called
        # many times in large parses.
        vpno = getattr(self, 'visit_packed_node_out')
        vpni = getattr(self, 'visit_packed_node_in')
        vsni = getattr(self, 'visit_symbol_node_in')
        vsno = getattr(self, 'visit_symbol_node_out')
        vino = getattr(self, 'visit_intermediate_node_out', vsno)
        vini = getattr(self, 'visit_intermediate_node_in', vsni)
        vsedit = getattr(self, 'visit_edit_node')
        vsend = getattr(self, 'visit_end_node')
        oc = getattr(self, 'on_cycle')

        # As long as the stack is not empty, visit the next node/the next iterable object.
        while input_stack:
            current = next(reversed(input_stack))
            try:
                next_node = next(current)
            except StopIteration:
                input_stack.pop()
                continue
            except TypeError:
                ### If the current object is not an iterator, pass through to Token/SymbolNode
                pass
            else:
                if next_node is None:
                    continue

                if id(next_node) in visiting:
                    oc(next_node, path)
                    continue

                input_stack.append(next_node)
                continue

            if isinstance(current, EditNode):
                vsedit(current)
                input_stack.pop()
                continue
            elif isinstance(current, EndNode):
                vsend(current)
                input_stack.pop()
                continue

            current_id = id(current)
            if current_id in visiting:
                if isinstance(current, PackedNode):
                    vpno(current)
                elif current.is_intermediate():
                    vino(current)
                else:
                    vsno(current)

                input_stack.pop()
                path.pop()
                visiting.remove(current_id)
            else:
                visiting.add(current_id)
                path.append(current)

                if isinstance(current, PackedNode):
                    next_node = vpni(current)
                elif current.is_intermediate():
                    next_node = vini(current)
                else:
                    next_node = vsni(current)

                if next_node is None:
                    continue

                if not isinstance(next_node, ForestNode):
                    next_node = iter(next_node)
                elif id(next_node) in visiting:
                    oc(next_node, path)
                    continue

                input_stack.append(next_node)
