from wofa import FiniteAutomata
from alcep_dfa.Nodes import SymbolNode, EditNode
from alcep_dfa.Nodes.EditOperations import *
from .Constants import *
from collections import deque


def all_dfa_corrections(to_correct: FiniteAutomata, minimal_dfa: FiniteAutomata) -> SymbolNode:
    """
    TODO
    :param to_correct:
    :param minimal_dfa:
    :return:
    """

    """
    Preparation steps
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

    # Crate a dict that contains all nodes off the CSPPF. Key: the node label, value: the node object.
    node_cache = {}

    # Create a root node of the sppf.
    root_tuple = (frozenset({}.items()), frozenset(set()), frozenset(set()), frozenset([]))
    root_node = SymbolNode(*root_tuple)
    node_cache[root_tuple] = root_node

    # A deque that contains all nodes that still have to be considered in the further parse process
    nodes_to_be_consider = deque()

    # Get the initial state of the to_correct automaton
    old_initial_state = to_correct.get_initials().pop()

    """
    Chosen of the initial state steps
    """
    # Iterate over all states and mark them as initial state
    for state in range(to_correct.get_number_of_states()):

        if state == old_initial_state:
            current_edit_node = EditNode(edit_operations=[LeaveInitial(state=(TO_CORRECT, state))])
        else:
            current_edit_node = EditNode(edit_operations=[RemoveMarkAsInitial(state=(TO_CORRECT, old_initial_state)),
                                                          MarkAsInitial(state=(TO_CORRECT, state))])

        # Create a new node for the current status of the parse process
        new_node_tuple = (frozenset({state: (MINIMAL_DFA, START)}.items()), frozenset({(TO_CORRECT, state)}),
                          frozenset(set()), frozenset([]))
        new_node = SymbolNode(*new_node_tuple)
        node_cache[new_node_tuple] = new_node

        # Add the new node and the edit operation node as children of the root node
        root_node.add_family(left_node=new_node, right_node=current_edit_node)

        # Add the node into the deque of nodes to be considered
        nodes_to_be_consider.append(new_node)

    # Add a new state as the initial state
    current_edit_node = EditNode(edit_operations=[RemoveMarkAsInitial(state=old_initial_state),
                                                  AddNewState(state=(MINIMAL_DFA, START)),
                                                  MarkAsInitial(state=(MINIMAL_DFA, START))])

    # Create a new node for the current status of the parse process
    new_node_tuple = (frozenset({}.items()), frozenset({(MINIMAL_DFA, START)}),
                      frozenset({(MINIMAL_DFA, START)}), frozenset([]))
    new_node = SymbolNode(*new_node_tuple)
    node_cache[new_node_tuple] = new_node

    # Add the new node and the edit operation node as children of the root node
    root_node.add_family(left_node=new_node, right_node=current_edit_node)

    # Add the node into the deque of nodes to be considered
    nodes_to_be_consider.append(new_node)

    """
    Main parse process steps
    """

    while nodes_to_be_consider:
        current_node = nodes_to_be_consider.pop()

        # TODO process the current node

    # Return the root node
    return root_node
