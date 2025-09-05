from .ForestNode import ForestNode
from .PackedNode import PackedNode


class SymbolNode(ForestNode):

    def __init__(self, state_mapping: frozenset, current_state: tuple, queue: frozenset, added: frozenset,
                 seen_symbols: list):
        """
        Initialize a SymbolNode instance.

        :param state_mapping: The state mapping dictionary.
        :param current_state: The current state being processed.
        :param queue: The queue of states to be seen next.
        :param added: The added equivalence classes of new added states.
        :param seen_symbols: The list of symbols seen so far, for this node.
        """
        super().__init__()
        self.state_mapping = state_mapping
        self.current_state = current_state
        self.queue = queue
        self.added = added
        self.seen_symbols = seen_symbols
        self._children = set()

    def add_family(self, left_node: ForestNode | None, right_node: ForestNode):
        """
        Add a child family (left and right child nodes) to the current SymbolNode.

        :param left_node: The left child node.
        :param right_node: The right child node.
        :return: None
        """
        self._children.add(PackedNode(parent=self, left_node=left_node, right_node=right_node))

    def get_params_unfrozen(self) -> tuple:
        """
        Get the parameters of the SymbolNode.

        :return: A tuple containing the state mapping, queue, added equivalence classes, and seen symbols.
        """
        return dict(self.state_mapping), self.current_state, set(self.queue), set(self.added), list(self.seen_symbols)

    def get_children(self) -> list[PackedNode]:
        """
        Get the children of the SymbolNode.

        :return: A list of PackedNode children.
        """
        return list(self._children)

    def is_intermediate(self) -> bool:
        return bool(self.seen_symbols)
