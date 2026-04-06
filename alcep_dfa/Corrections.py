from wofa import FiniteAutomata
import random
from collections import deque
from alcep_dfa.Nodes import SymbolNode, PackedNode, EditNode, EndNode
from alcep_dfa.Visitors import MinCostsComputationVisitor, ShrinkToMinimal, GetAllEditsVisitor, \
    ShrinkToAllowedMappings, ShrinkToMinimalDFAs, GetNumberOfCorrectionsVisitor
from alcep_dfa.Constants import MINIMAL_DFA, MINIMAL_DFA_START
from alcep_dfa import all_dfa_corrections


# TODO für 1:1 mapping filter nur auf den ersten buchstaben des Pfades beschränken
# TODO bei shrink_to_corrections_to_minimal_dfas kann es dazu führen das noch zyklen im SPPF enthalten sind.
#  Grund bisher unbekannt -> Grund finden und Bug beheben.

class Correction:
    """
    A class that represents and manages corrections from a given DFA to a minimal DFA.
    Corrections are modeled as a Shared Packed Parse Forest (SPPF), which efficiently 
    represents all possible sequences of edit operations.
    """

    def __init__(self, to_correct: FiniteAutomata, minimal_dfa: FiniteAutomata, alphabet=None, costs_add_new_state=1,
                 costs_add_transition=1, costs_leave_initial=0, costs_leave_transition=0, costs_mark_as_initial=1,
                 costs_mark_final=1, costs_mark_non_final=1, costs_remove_initial=1, costs_remove_transition=0):
        """
        Initializes the Correction object and computes the initial SPPF containing all valid corrections.

        :param to_correct: The Deterministic Finite Automata (DFA) that needs to be corrected.
        :param minimal_dfa: The target minimal DFA. We assume that this automaton is already minimized, 
            otherwise the results are not correct. Both automata must be defined over the same alphabet.
        :param alphabet: The alphabet over which the DFA is defined. If None, it defaults to the alphabet of the given DFA.
        """
        self.to_correct: FiniteAutomata = to_correct
        self.minimal_dfa: FiniteAutomata = minimal_dfa

        # Validate that both automata are deterministic
        if not to_correct.is_deterministic():
            raise Exception("The automata to correct must be a DFA.")

        if not minimal_dfa.is_deterministic():
            raise Exception("The minimal automata must be a DFA.")

        # Determine the alphabet to use
        if alphabet is None:
            self.alphabet = sorted(list(FiniteAutomata.get_alphabet()))
        else:
            self.alphabet = alphabet

        # Set the costs for each edit operation
        self.costs_add_new_state = costs_add_new_state
        self.costs_add_transition = costs_add_transition
        self.costs_leave_initial = costs_leave_initial
        self.costs_leave_transition = costs_leave_transition
        self.costs_mark_as_initial = costs_mark_as_initial
        self.costs_mark_final = costs_mark_final
        self.costs_mark_non_final = costs_mark_non_final
        self.costs_remove_initial = costs_remove_initial
        self.costs_remove_transition = costs_remove_transition

        self.miniml_costs_calculated = False

        # Compute the SPPF that represents all corrections from the to correct DFA to the minimal DFA.
        self.root_node = all_dfa_corrections(to_correct=to_correct, minimal_dfa=minimal_dfa, alphabet=self.alphabet)

    def get_random_correction(self) -> list:
        """
        Retrieves a single random sequence of edit operations from the SPPF.
        Traverses the SPPF recursively by randomly selecting child nodes until end nodes are reached.

        :return: A list of edit operations representing a randomly selected valid correction.
        """

        def __aux__(current_node: SymbolNode) -> list:
            """Auxiliary recursive function to traverse the SPPF randomly."""
            # Select a random child from the current node's children
            children = current_node.get_children()
            selected_child: PackedNode = random.choice(children)

            # Get the edit operations from the child's right child node
            child_right_child = selected_child.get_right_node()
            match child_right_child:
                case SymbolNode():
                    # Fixed referencing self.get_random_correction -> __aux__
                    right_correction = __aux__(current_node=child_right_child)
                case EditNode():
                    right_correction = [child_right_child.get_edit_operations()]
                case EndNode():
                    right_correction = []
                case _:
                    raise Exception("The right child must be set")

            # Get the edit operations from the child's left node if it exists
            child_left_child = selected_child.get_left_node()
            match child_left_child:
                case None:
                    left_correction = []
                case SymbolNode():
                    # Fixed referencing self.get_random_correction -> __aux__
                    left_correction = __aux__(child_left_child)
                case _:
                    raise Exception("The left child must be either None or a SymbolNode")

            return right_correction + left_correction

        # Start the recursive selection process from the root node
        if self.root_node is None:
            raise Exception("The SPPF is empty, no correction can be returned.")
        return __aux__(current_node=self.root_node)

    def compute_minimal_edit_costs(self):
        """
        Computes the minimal edit costs for all nodes in the SPPF using the MinCostsComputationVisitor.
        This updates the nodes internally with the minimal achievable cost to reach them.
        """
        # Create a visitor configured with the operation costs
        visitor = MinCostsComputationVisitor(costs_add_new_state=self.costs_add_new_state,
                                             costs_add_transition=self.costs_add_transition,
                                             costs_leave_initial=self.costs_leave_initial,
                                             costs_leave_transition=self.costs_leave_transition,
                                             costs_mark_as_initial=self.costs_mark_as_initial,
                                             costs_mark_final=self.costs_mark_final,
                                             costs_mark_non_final=self.costs_mark_non_final,
                                             costs_remove_initial=self.costs_remove_initial,
                                             costs_remove_transition=self.costs_remove_transition)

        if self.root_node is None:
            raise Exception("The SPPF is empty, no correction can be returned.")

        # Traverse the SPPF to compute minimal edit costs bottom-up for each node
        visitor.visit(root_node=self.root_node)

        self.miniml_costs_calculated = True

    def get_minimal_edit_costs(self) -> int:
        """
        Retrieves the minimal overall edit cost required to correct the DFA.
        Computes the costs first if they haven't been computed yet.

        :return: The integer value of the lowest possible total edit cost.
        """
        if not self.miniml_costs_calculated:
            self.compute_minimal_edit_costs()

        return self.root_node.get_minimal_edits_costs()

    def shrink_to_minimal_edits(self) -> SymbolNode:
        """
        Prunes the SPPF to only retain correction paths that possess the minimal edit cost.
        Any branches representing sub-optimal corrections are removed.

        :return: The root node of the modified SPPF containing only minimal corrections.
        """
        if not self.miniml_costs_calculated:
            self.compute_minimal_edit_costs()

        # Create a visitor to remove non-minimal nodes
        visitor = ShrinkToMinimal(costs_add_new_state=self.costs_add_new_state,
                                  costs_add_transition=self.costs_add_transition,
                                  costs_leave_initial=self.costs_leave_initial,
                                  costs_leave_transition=self.costs_leave_transition,
                                  costs_mark_as_initial=self.costs_mark_as_initial,
                                  costs_mark_final=self.costs_mark_final,
                                  costs_mark_non_final=self.costs_mark_non_final,
                                  costs_remove_initial=self.costs_remove_initial,
                                  costs_remove_transition=self.costs_remove_transition)

        # Apply the pruning process
        visitor.visit(root_node=self.root_node)

        return self.root_node

    def get_all_corrections(self) -> list:
        """
        Extracts every possible sequence of edit operations (correction) represented by the SPPF.

        :return: A list of lists, where each inner list contains the edit operations for one complete correction.
        """
        # Create a visitor to aggregate all valid edit sequences
        visitor = GetAllEditsVisitor()

        # Traverse the SPPF to populate the corrections list
        visitor.visit(root_node=self.root_node)

        return self.root_node.get_all_edits()

    def get_number_of_corrections(self) -> int:
        """
        Calculates the total number of distinct valid corrections in the SPPF.

        :return: The total count of possible corrections.
        """
        if self.root_node is None:
            raise Exception("The SPPF is empty, no correction can be returned.")

        # Create a visitor to compute the number of valid paths bottom-up
        visitor = GetNumberOfCorrectionsVisitor()

        # Traverse the SPPF to count variations
        visitor.visit(root_node=self.root_node)

        return self.root_node.get_number_of_corrections()

    def shrink_to_corrections_to_minimal_dfas(self):
        """
        Filters the SPPF to keep only corrections that lead exactly to the expected minimal DFA,
        discarding corrections that might result in equivalent but non-minimal cyclic structures.

        Uses Breadth-First Search (BFS) to track equivalence classes and identify redundancies.
        """
        if self.root_node is None:
            raise Exception("The SPPF is empty, no correction can be returned.")

        # Initialize BFS queue with a tuple: (current node, seen equivalence classes, last structural equivalence class)
        init_tuple = (self.root_node, frozenset(set()), None)
        queue = deque()
        queue.append(init_tuple)
        seen_tuples = {init_tuple}

        # Traverse layer by layer to map state equivalence cycles
        while queue:
            node, seen_eq_classes, last_edit_equivalence_class = queue.popleft()
            
            # Extract newly added equivalence classes from node parameters
            added_eq_classes = {k[1] for k in node.get_params_unfrozen()[3]}
            eq_class = node.get_equivalence_class()

            if node.is_intermediate():
                if last_edit_equivalence_class is None:
                    # Update equivalence class
                    current_eq_class = eq_class

                    # Detect cycle or redundant representation
                    if eq_class is not None and eq_class in seen_eq_classes:
                        node.set_contained_in_cor_to_minial_dfa(False)
                        continue

                    new_seen_eq_classes = seen_eq_classes.union({eq_class})
                else:
                    new_seen_eq_classes = seen_eq_classes
                    current_eq_class = last_edit_equivalence_class
            else:
                new_seen_eq_classes = seen_eq_classes.union(added_eq_classes)
                current_eq_class = None

            # Enqueue valid children for further evaluation
            for child in node.get_children():
                if child.left_node is not None and type(child.left_node) == SymbolNode:
                    new_tuple = (child.left_node, frozenset(new_seen_eq_classes), current_eq_class)
                    if new_tuple not in seen_tuples:
                        seen_tuples.add(new_tuple)
                        queue.append(new_tuple)
                if child.right_node is not None and type(child.right_node) == SymbolNode:
                    new_tuple = (child.right_node, frozenset(new_seen_eq_classes), current_eq_class)
                    if new_tuple not in seen_tuples:
                        seen_tuples.add(new_tuple)
                        queue.append(new_tuple)

        # Shrink the SPPF removing invalid cyclic branches discovered
        visitor = ShrinkToMinimalDFAs()
        visitor.visit(root_node=self.root_node)

        # SPPF structure has changed, invalidate cached costs
        self.miniml_costs_calculated = False

    def shrink_to_corrections_with_1_to_1_mapping(self):
        """
        Restricts the SPPF to corrections maintaining a strict 1-to-1 equivalence state mapping
        between the `to_correct` DFA and the `minimal_dfa`. 

        Calculates direct state mapping via identical distinct prefix pathways using BFS,
        then prunes SPPF paths not conforming to these permitted mappings.
        """
        def __compute_allowed_1_to_1_mapping():
            """
            Internal helper that identifies shortest reachability paths for states
            and formulates permitted state correlations.
            """
            def __aux(start_state, automata, smallest_states_paths):
                """
                Auxiliary Breadth-First Search discovering the shortest possible word 
                capable of reaching every accessible state from the provided start state.
                """
                queue = deque()
                queue.append((start_state, ""))

                while queue:
                    current_state, word = queue.popleft()

                    # Guarantee storage of exactly the shortest path only
                    if current_state in smallest_states_paths:
                        continue

                    smallest_states_paths[current_state] = word

                    # Expand path using alphabet characters
                    for letter in self.alphabet:
                        for next_state in automata.get_successors(s=current_state, a=letter):
                            if next_state not in smallest_states_paths:
                                queue.append((next_state, word + letter))

            # Store shortest paths matching a specific final state
            smallest_states_paths_to_correct = {}
            smallest_states_paths_minimal_dfa = {}
            
            # Start algorithm from the initial states
            (initial_state_minimal_dfa,) = self.minimal_dfa.get_initials()
            (initial_state_to_correct,) = self.to_correct.get_initials()
            
            __aux(start_state=initial_state_to_correct, automata=self.to_correct,
                  smallest_states_paths=smallest_states_paths_to_correct)

            __aux(start_state=initial_state_minimal_dfa, automata=self.minimal_dfa,
                  smallest_states_paths=smallest_states_paths_minimal_dfa)

            # Map the exact reverse lookup correlation between smallest paths and minimal dfa states
            swapped_stats_path_minimal_dfa = {value: key for key, value in smallest_states_paths_minimal_dfa.items()}

            # Populate mapping dictionary
            for state, path in smallest_states_paths_to_correct.items():
                if path in swapped_stats_path_minimal_dfa:
                    state_minimal_dfa = swapped_stats_path_minimal_dfa[path]

                    if state_minimal_dfa == initial_state_minimal_dfa:
                        allowed_mapping[state] = (MINIMAL_DFA_START, state_minimal_dfa)
                    else:
                        allowed_mapping[state] = (MINIMAL_DFA, state_minimal_dfa)

            return allowed_mapping

        allowed_mapping = dict()
        __compute_allowed_1_to_1_mapping()
        
        # Deploy a visitor to apply the calculated mappings restriction
        visitor = ShrinkToAllowedMappings(allowed_mapping=allowed_mapping)
        visitor.visit(root_node=self.root_node)

        self.miniml_costs_calculated = False
