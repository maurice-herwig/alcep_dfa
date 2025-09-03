from wofa import FiniteAutomata
from alcep_dfa.Nodes.SymbolNode import SymbolNode

TO_CORRECT = "to_correct"
MINIMAL_DFA = "minimal_dfa"
START = "start"


def all_dfa_corrections(to_correct: FiniteAutomata, minimal_dfa: FiniteAutomata) -> SymbolNode:
    """
    TODO
    :param to_correct:
    :param minimal_dfa:
    :return:
    """

    # Check that both automata are DFAs
    assert to_correct.is_deterministic(require_dead_state=False), "Input automaton to_correct must be a DFA."
    assert minimal_dfa.is_deterministic(require_dead_state=False), "Input automaton minimal_dfa must be a DFA."

    # Define an order on the alphabet
    alphabet = list(FiniteAutomata.get_alphabet())

    # Check that both automata used only alphabet symbols
    assert all(a in alphabet for _, a, _ in to_correct.get_transitions()), \
        "All letters in to_correct must be in the alphabet."
    assert all(a in alphabet for _, a, _ in minimal_dfa.get_transitions()), \
        "All letters in minimal_dfa must be in the alphabet."

    # Define an order on the states
    states_of_both = [(TO_CORRECT, state) for state in range(to_correct.get_number_of_states())] + \
                     [(MINIMAL_DFA, state) for state in range(minimal_dfa.get_number_of_states())] + \
                     [(MINIMAL_DFA, START)]

    # Create a root node of the sppf.
    root_node = SymbolNode({}, set(), set(), [])


    # TODO parse process

    # Return the root node
    return root_node
