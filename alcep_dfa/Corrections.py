from wofa import FiniteAutomata
import random
from collections import deque
from alcep_dfa.Nodes import SymbolNode, PackedNode, EditNode, EndNode
from alcep_dfa.Visitors import MinCostsComputationVisitor, ShrinkToMinimal, GetAllEditsVisitor, \
    ShrinkToAllowedMappings, ShrinkToMinimalDFAs, GetNumberOfCorrectionsVisitor
from alcep_dfa.Constants import MINIMAL_DFA, MINIMAL_DFA_START
from alcep_dfa import all_dfa_corrections


# TODO für 1:1 mapping filter nur auf den ersten buchstaben des Pfades beschränken
# TODO Docstrings

class Correction:

    def __init__(self, to_correct: FiniteAutomata, minimal_dfa: FiniteAutomata, alphabet=None, costs_add_new_state=1,
                 costs_add_transition=1, costs_leave_initial=0, costs_leave_transition=0, costs_mark_as_initial=1,
                 costs_mark_final=1, costs_mark_non_final=1, costs_remove_initial=1, costs_remove_transition=0):
        """

        :param to_correct:
        :param minimal_dfa: We assume that these automata is already minimized, otherwise the results are not correct.
            In addition, the automata must be defined over the same alphabet.
        :param alphabet:
        """
        self.to_correct: FiniteAutomata = to_correct
        self.minimal_dfa: FiniteAutomata = minimal_dfa

        if not to_correct.is_deterministic():
            raise Exception("The automata to correct must be a DFA.")

        if not minimal_dfa.is_deterministic():
            raise Exception("The minimal automata must be a DFA.")

        if alphabet is None:
            self.alphabet = sorted(list(FiniteAutomata.get_alphabet()))
        else:
            self.alphabet = alphabet

        # set the costs for each edit operation
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

        # Compute the SPPF that represents all corrections of the to correct DFA to the minimal DFA.
        self.root_node = all_dfa_corrections(to_correct=to_correct, minimal_dfa=minimal_dfa, alphabet=self.alphabet)

    def get_random_correction(self) -> list:
        """
        Get a random correction from the SPPF rooted at the given root node.


        :return: A list of edit operations representing a random correction.
        """

        def __aux__(current_node: SymbolNode) -> list:
            # Select a random child from the root node's children
            children = current_node.get_children()
            selected_child: PackedNode = random.choice(children)

            # Get the edit operations of the child's right child node
            child_right_child = selected_child.get_right_node()
            match child_right_child:
                case SymbolNode():
                    right_correction = self.get_random_correction(root_node=child_right_child)
                case EditNode():
                    right_correction = [child_right_child.get_edit_operations()]
                case EndNode():
                    right_correction = []
                case _:
                    raise Exception("The right child must be set")

            # Get the correction of the left child node if it exists
            child_left_child = selected_child.get_left_node()
            match child_left_child:
                case None:
                    left_correction = []
                case SymbolNode():
                    left_correction = self.get_random_correction(child_left_child)
                case _:
                    raise Exception("The left child must be either None or a SymbolNode")

            return right_correction + left_correction

        # Start the recursive process from the root node
        if self.root_node is None:
            raise Exception("The SPPF is empty, no correction can be returned.")
        return __aux__(current_node=self.root_node)

    def compute_minimal_edit_costs(self):
        # Greate a minimal correction visitor
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

        # Use the visitor to compute for each node the minimal edits costs
        visitor.visit(root_node=self.root_node)

        self.miniml_costs_calculated = True

    def get_minimal_edit_costs(self) -> int:

        if not self.miniml_costs_calculated:
            self.compute_minimal_edit_costs()

        return self.root_node.get_minimal_edits_costs()

    def shrink_to_minimal_edits(self) -> SymbolNode:

        if not self.miniml_costs_calculated:
            self.compute_minimal_edit_costs()

        # Create a shrink to minimal visitor
        visitor = ShrinkToMinimal(costs_add_new_state=self.costs_add_new_state,
                                  costs_add_transition=self.costs_add_transition,
                                  costs_leave_initial=self.costs_leave_initial,
                                  costs_leave_transition=self.costs_leave_transition,
                                  costs_mark_as_initial=self.costs_mark_as_initial,
                                  costs_mark_final=self.costs_mark_final,
                                  costs_mark_non_final=self.costs_mark_non_final,
                                  costs_remove_initial=self.costs_remove_initial,
                                  costs_remove_transition=self.costs_remove_transition)

        # Use the visitor to shrink the SPPF to only contain minimal corrections.
        visitor.visit(root_node=self.root_node)

        return self.root_node

    def get_all_corrections(self) -> list:
        """
        Get all corrections from the SPPF rooted at the given root node.

        :return: A list of lists of edit operations representing all corrections.
        """

        # Create a get all edits visitor
        visitor = GetAllEditsVisitor()

        # Use the visitor to get all corrections from the SPPF.
        visitor.visit(root_node=self.root_node)

        return self.root_node.get_all_edits()

    def get_number_of_corrections(self) -> int:
        """
        Get the number of corrections from the SPPF rooted at the given root node.

        :return: The number of corrections represented by the SPPF rooted at the given root node.
        """

        if self.root_node is None:
            raise Exception("The SPPF is empty, no correction can be returned.")

        # Create a get number of corrections visitor
        visitor = GetNumberOfCorrectionsVisitor()

        # Use the visitor to get all corrections from the SPPF.
        visitor.visit(root_node=self.root_node)

        return self.root_node.get_number_of_corrections()

    def shrink_to_corrections_to_minimal_dfas(self):

        if self.root_node is None:
            raise Exception("The SPPF is empty, no correction can be returned.")

        init_tuple = (self.root_node, frozenset(set()), None)
        queue = deque()
        queue.append(init_tuple)
        seen_tuples = {init_tuple}

        while queue:
            node, seen_eq_classes, last_edit_equivalence_class = queue.popleft()
            added_eq_classes = {k[1] for k in node.get_params_unfrozen()[3]}

            eq_class = node.get_equivalence_class()

            if node.is_intermediate():
                if last_edit_equivalence_class is None:
                    # Compute the equivalence class of the node
                    current_eq_class = eq_class

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

        # Shrink the node to only contain corrections that are contained in the minimal DFA
        visitor = ShrinkToMinimalDFAs()

        visitor.visit(root_node=self.root_node)

        self.miniml_costs_calculated = False

    def shrink_to_corrections_with_1_to_1_mapping(self):
        def __compute_allowed_1_to_1_mapping():

            def __aux(start_state, automata, smallest_states_paths):
                """Auxiliary function to compute the smallest word that leads to each state of the given automata,
                starting from the start state and using a breadth first search."""
                queue = deque()
                queue.append((start_state, ""))

                while queue:
                    current_state, word = queue.popleft()

                    if current_state in smallest_states_paths:
                        continue

                    smallest_states_paths[current_state] = word

                    for letter in self.alphabet:
                        for next_state in automata.get_successors(s=current_state, a=letter):
                            if next_state not in smallest_states_paths:
                                queue.append((next_state, word + letter))

            # Store for each state of the to correct DFA and the minimal DFA the smallest word that leads to this state,
            # which is computed by a DFS. This is used to compute the allowed 1 to 1 mapping between states of the to
            # correct DFA and states of the minimal DFA.
            smallest_states_paths_to_correct = {}
            smallest_states_paths_minimal_dfa = {}
            (initial_state_minimal_dfa,) = self.minimal_dfa.get_initials()
            (initial_state_to_correct,) = self.to_correct.get_initials()
            __aux(start_state=initial_state_to_correct, automata=self.to_correct,
                  smallest_states_paths=smallest_states_paths_to_correct)

            __aux(start_state=initial_state_minimal_dfa, automata=self.minimal_dfa,
                  smallest_states_paths=smallest_states_paths_minimal_dfa)

            swapped_stats_path_minimal_dfa = {value: key for key, value in smallest_states_paths_minimal_dfa.items()}

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
        visitor = ShrinkToAllowedMappings(allowed_mapping=allowed_mapping)

        visitor.visit(root_node=self.root_node)

        self.miniml_costs_calculated = False
