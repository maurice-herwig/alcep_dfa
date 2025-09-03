class SymbolNode:
    alphabet = list()

    @classmethod
    def set_alphabet(cls, alphabet: list):
        """
        Set the alphabet order for all SymbolNode instances.

        :param alphabet: List of symbols representing the alphabet.
        :return: None
        """
        cls.alphabet = alphabet

    def __init__(self, state_mapping: dict, queue: set, added: set, seen_symbols: list):
        """
        Initialize a SymbolNode instance.

        :param state_mapping: The state mapping dictionary.
        :param queue: The queue of states to be seen next.
        :param added: The added equivalence classes of new added states.
        :param seen_symbols: The list of symbols seen so far, for this node.
        """
        self.state_mapping = state_mapping
        self.queue = queue
        self.added = added
        self.seen_symbols = seen_symbols
