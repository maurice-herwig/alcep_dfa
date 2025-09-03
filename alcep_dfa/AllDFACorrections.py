from wofa import FiniteAutomata
from alcep_dfa.Nodes import SymbolNode, EditNode
from alcep_dfa.Nodes.EditOperations import *
from .Constants import *
from queue import Queue
import copy


def all_dfa_corrections(to_correct: FiniteAutomata, minimal_dfa: FiniteAutomata) -> SymbolNode:
    """
    Compute a SPPF that represents all possible ways to correct the to_correct DFA into a DFA that is language
    equivalent to the given minimal_dfa.

    :param to_correct: A DFA that should be corrected.
    :param minimal_dfa: A minimal DFA that defines the target language.
        !!! Must be the minimal DFA for the target language!!!

    :return: The root node of the SPPF that represents all possible corrections.
    """

    def aux_get_or_create_node(node_tuple):
        """
        auxiliary function that get or create a new node for the current status of the parse process.

        :param node_tuple: The tuple that defines the current status of the parse process.
        :return: The node for the current status of the parse process.
        """
        # Check if the node already exists.
        if node_tuple in node_cache:
            return node_cache[node_tuple]
        else:
            # Create a new node for the current status of the parse process and add it to the node_cache.
            new_created_node = SymbolNode(*node_tuple)
            node_cache[node_tuple] = new_created_node

            # If the queue is not empty, add the new node to the nodes_to_be_consider queue.
            if node_tuple[1]:
                nodes_to_be_consider.put(new_created_node)
            else:
                # TODO stop node hinzufügen
                pass

            return new_created_node

    """
    Start of the main all_dfa_corrections function
    Preparation steps
    """
    # Check that both automata are DFAs
    assert to_correct.is_deterministic(require_dead_state=False), "Input automaton to_correct must be a DFA."
    assert minimal_dfa.is_deterministic(require_dead_state=False), "Input automaton minimal_dfa must be a DFA."

    # Check that the minimal dfa have for each state at least one outgoing transition
    assert all(minimal_dfa.get_all_successors(s=q) for q in range(minimal_dfa.get_number_of_states())), \
        "The minimal_dfa have a state without outgoing transitions."

    # Define an order on the alphabet
    alphabet = list(FiniteAutomata.get_alphabet())

    # Check that both automata used only alphabet symbols
    assert all(a in alphabet for _, a, _ in to_correct.get_transitions()), \
        "All letters in to_correct must be in the alphabet."
    assert all(a in alphabet for _, a, _ in minimal_dfa.get_transitions()), \
        "All letters in minimal_dfa must be in the alphabet."

    # Get the initial state of the to_correct and minimal automaton
    [old_initial_state] = to_correct.get_initials()
    [minimal_dfa_start_state] = minimal_dfa.get_initials()

    # Define an order on the states
    states_of_both = [(TO_CORRECT, state) for state in range(to_correct.get_number_of_states())] + \
                     [(MINIMAL_DFA, state) for state in range(minimal_dfa.get_number_of_states())] + \
                     [(MINIMAL_DFA_START, minimal_dfa_start_state)]

    # Crate a dict that contains all nodes off the CSPPF. Key: the node label, value: the node object.
    node_cache = {}

    # Create a root node of the sppf.
    root_tuple = (frozenset({}.items()), frozenset(set()), frozenset(set()), frozenset([]))
    root_node = SymbolNode(*root_tuple)
    node_cache[root_tuple] = root_node

    # A queue that contains all nodes that still have to be considered in the further parse process
    nodes_to_be_consider = Queue()

    """
    Chosen of the initial state steps
    """
    # Iterate over all states and mark them as initial state
    for state in range(to_correct.get_number_of_states()):

        if state == old_initial_state:
            new_edit_node = EditNode(edit_operations=[LeaveInitial(state=(TO_CORRECT, state))])
        else:
            new_edit_node = EditNode(edit_operations=[RemoveMarkAsInitial(state=(TO_CORRECT, old_initial_state)),
                                                      MarkAsInitial(state=(TO_CORRECT, state))])

        # Create a new node for the current status of the parse process
        new_node_tuple = (
            frozenset({state: (MINIMAL_DFA_START, minimal_dfa_start_state)}.items()), frozenset({(TO_CORRECT, state)}),
            frozenset(set()), frozenset([]))
        new_node = SymbolNode(*new_node_tuple)
        node_cache[new_node_tuple] = new_node

        # Add the new node and the edit operation node as children of the root node
        root_node.add_family(left_node=new_node, right_node=new_edit_node)

        # Add the node into the queue of nodes to be considered
        nodes_to_be_consider.put(new_node)

    # Add a new state as the initial state
    new_edit_node = EditNode(edit_operations=[RemoveMarkAsInitial(state=old_initial_state),
                                              AddNewState(state=(MINIMAL_DFA_START, minimal_dfa_start_state)),
                                              MarkAsInitial(state=(MINIMAL_DFA_START, minimal_dfa_start_state))])

    # Create a new node for the current status of the parse process
    new_node_tuple = (frozenset({}.items()), frozenset({(MINIMAL_DFA_START, minimal_dfa_start_state)}),
                      frozenset({(MINIMAL_DFA_START, minimal_dfa_start_state)}), frozenset([]))
    new_node = SymbolNode(*new_node_tuple)
    node_cache[new_node_tuple] = new_node

    # Add the new node and the edit operation node as children of the root node
    root_node.add_family(left_node=new_node, right_node=new_edit_node)

    # Add the node into the queue of nodes to be considered
    nodes_to_be_consider.put(new_node)

    """
    Main parse process steps
    """
    # While there are still nodes to be considered. Compute for the next node all possible child nodes.
    while not nodes_to_be_consider.empty():
        # Get the next node to be considered
        current_node = nodes_to_be_consider.get()

        # Get the parameters of the current node
        state_mapping, queue, added, seen_symbols = current_node.get_params_unfrozen()

        # Get the smallest node from the queue
        state = next(s for s in states_of_both if s in queue)

        # Get the next symbol to be considered
        letter = alphabet[len(seen_symbols)]

        # Define the queue and the seen_symbols for the next node
        if len(seen_symbols) == len(alphabet) - 1:
            seen_symbols = []
            queue.remove(state)
        else:
            seen_symbols.append(letter)

        # Compute the next equivalence class of the state following the letter transition in the minimal_dfa
        # Therefore, first get the equivalence class of the current state
        if state[0] == TO_CORRECT:
            equivalence_class_state = state_mapping.get(state[1], None)[1]
        else:
            equivalence_class_state = state[1]

        # Get the next equivalence class of the state following the letter transition in the minimal_dfa
        # IF there is no transition for the letter, add as only child the intermediate node with that consider
        # the next symbol and continue with the next node in the queue to_be_considered
        next_equivalence_class_state = minimal_dfa.get_successors(s=equivalence_class_state, a=letter)
        if len(next_equivalence_class_state) == 0:
            # If there are no successor for this letter crate a new node that skip the letter.
            new_node = aux_get_or_create_node(node_tuple=(frozenset(state_mapping.items()), frozenset(queue),
                                                          frozenset(added), frozenset(seen_symbols)))

            current_node.add_family(left_node=None, right_node=new_node)
            continue

        [next_equivalence_class_state] = next_equivalence_class_state

        # Compute for the current status of the parser process (defined by the current node) all possible next states
        # for the current_State and the current considered letter. Thereby we have to consider the transition of the
        # equivalence class to next_equivalence_class for this letter (defined by the minimal_dfa).
        # For the next state we have the following opportunities:
        # 1. The next state is already mapped to the corresponding equivalence class
        # 2. The next state is not yet mapped to an equivalence class
        # 3. The next state is a new state (represented an equivalence class) for an equivalence class that
        #    is not yet be added before.
        # 4. The next state is a new state (represented an equivalence class) for an equivalence class that
        #    is already added before.
        # 5. Consider the special case that the next state is the start state of the minimal_dfa.
        #
        # Additionally, create for each opportunity the corresponding nodes and edit operations

        # 1. Change the current transition such that they lead to an in the automaton to be correct state
        # that is already mapped to the next equivalence class
        for next_state in [q for q, eq_class in state_mapping.items() if eq_class[1] == next_equivalence_class_state]:
            edit_operations = []
            # TODO entsprechende edits der transition hinzufügen

            # Create the new edit operation node and the get or create the new node.
            new_edit_node = EditNode(edit_operations=edit_operations)
            new_node = aux_get_or_create_node(node_tuple=(frozenset(state_mapping.items()), frozenset(queue),
                                                          frozenset(added), frozenset(seen_symbols)))

            # Add the new node and the edit operation node as children of the current node
            current_node.add_family(left_node=new_node, right_node=new_edit_node)

        # 2. Change the current transition such to a state in the automaton to be correct
        # that is not yet mapped to an equivalence class
        for next_state in [q for q in range(to_correct.get_number_of_states()) if q not in state_mapping.keys()]:

            # Mark the next_state with the corresponding equivalence class and add the next_state into the queue
            next_state_mapping = copy.copy(state_mapping)
            next_state_mapping[next_state] = (MINIMAL_DFA, next_equivalence_class_state)
            next_queue = copy.copy(queue)
            next_queue.add((TO_CORRECT, next_state))

            edit_operations = []
            # TODO entsprechende edits hinzufügen
            # TODO auch bezüglich akzeptanz
            if state[0] == TO_CORRECT:
                pass

            # Create the new edit operation node and the tuple that defines the new node by the current parameters
            new_edit_node = EditNode(edit_operations=edit_operations)
            new_node_tuple = (frozenset(next_state_mapping.items()), frozenset(next_queue),
                              frozenset(added), frozenset(seen_symbols))

            # Check if the new node already exists, otherwise create it and add it to the nodes_to_be_consider queue
            if new_node_tuple in node_cache:
                new_node = node_cache[new_node_tuple]
            else:
                new_node = SymbolNode(*new_node_tuple)
                node_cache[new_node_tuple] = new_node

                if next_queue:
                    nodes_to_be_consider.put(new_node)
                else:
                    # TODO stop node hinzufügen
                    pass

            # Add the new node and the edit operation node as children of the current node
            current_node.add_family(left_node=new_node, right_node=new_edit_node)

        # Start of the cases 3, 4 and 5.
        next_added = copy.copy(added)
        next_queue = copy.copy(queue)
        all_edit_options = []

        # 3. The next state is a new state (represented an equivalence class) for an equivalence class that is not
        # yet be added before. Then add this node to the added equivalence classes and added to the queue.
        if (MINIMAL_DFA, next_equivalence_class_state) not in added:
            next_added.add((MINIMAL_DFA, next_equivalence_class_state))
            next_queue.add((MINIMAL_DFA, next_equivalence_class_state))

        # 4. The next state is a new state (represented an equivalence class) for an equivalence class that is
        # already added before. Then we need to be considered the case that we connect the node to an already
        # created new node for this equivalence class.
        else:
            # TODO entsprechende edits hinzufügen. Aber am nachfolge knoten ändert sich nichts.
            # TODO edit knoten connect zu einem bereits hinzugefügten knoten der equivalenzklasse.
            pass

        # 5. Consider the special case that the next state is the start state of the minimal_dfa.
        # Then if we had added a new start state we need to be considered to connect to this state.
        if next_equivalence_class_state == minimal_dfa_start_state:
            if (MINIMAL_DFA_START, minimal_dfa_start_state) in added:
                # TODO entsprechende edits hinzufügen. Aber am nachfolge knoten ändert sich nichts.
                # TODO edit knoten connect zu einem bereits hinzugefügten knoten der equivalenzklasse.
                pass

        # Note that case 3. und 4. have the same edit operation sequence that add a new node of this
        # equivalence class.

        # TODO anstatt []  entsprechende edits hinzufügen für den case.
        all_edit_options.append([])

        # Get or create the new node for the current status of the parse process.
        new_node = aux_get_or_create_node(node_tuple=(frozenset(state_mapping.items()), frozenset(next_queue),
                                                      frozenset(next_added), frozenset(seen_symbols)))

        # Add for all possible edit operation sequences a new edit operation node
        # and add as a child of the current node.
        for edit_operations in all_edit_options:
            # Create the new edit operation node
            new_edit_node = EditNode(edit_operations=edit_operations)

            # Add the new node and the edit operation node as children of the current node
            current_node.add_family(left_node=new_node, right_node=new_edit_node)

    # Return the root node
    return root_node
