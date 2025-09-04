from wofa import FiniteAutomata
from alcep_dfa.Nodes.EditOperations import *
from alcep_dfa.Constants import *
from collections import defaultdict
import copy


def apply_correction(to_correct: FiniteAutomata, correction: list[EditOperation]) -> list[FiniteAutomata]:
    def aux_unroll_transitions(trans_options: list) -> list:
        if not trans_options:
            return []

        else:
            next_options = aux_unroll_transitions(trans_options=trans_options[1:])

            current_options = []
            source_states, letter, target_states = trans_options[0]
            for source_option in (source_states if isinstance(source_states, list) else [source_states]):
                for target_option in (target_states if isinstance(target_states, list) else [target_states]):
                    current_options.append((source_option, letter, target_option))

            # Merge current_options with next_options
            res = []
            for current in current_options:
                if next_options:
                    for next_option in next_options:
                        res.append([current] + next_option)
                else:
                    res.append([current])
            return res

    # Initialize sets and lists to hold states, initials, finals, and transitions for the resulting automata
    transitions_options = []
    states = set()
    initials = set()
    finals = copy.copy(to_correct.get_finals())

    n = to_correct.get_number_of_states()
    eq_class_to_state_mapping = defaultdict(list)

    # Iterate over operations in the correction list and add the resulting states and transitions
    # into the above initialised sets/lists
    for operation in correction:
        match operation:
            case AddNewState():
                _, eq_class = operation.get_state()
                eq_class_to_state_mapping[eq_class].append(n)
                states.add(n)
                n += 1
            case AddTransition():
                (source_type, source_eq_class), symbol, (target_type, target_eq_class) = operation.get_transition()

                if source_type == TO_CORRECT:
                    source_state = source_eq_class
                else:
                    source_state = eq_class_to_state_mapping[source_eq_class]

                if target_type == TO_CORRECT:
                    target_state = target_eq_class
                else:
                    target_state = eq_class_to_state_mapping[target_eq_class]

                transitions_options.append((source_state, symbol, target_state))

            case LeaveInitial():
                _, eq_class = operation.get_state()
                initials.add(eq_class)
                states.add(eq_class)

            case LeaveTransition():
                (_, source_eq_class), symbol, (_, target_eq_class) = operation.get_transition()
                transitions_options.append((source_eq_class, symbol, target_eq_class))

            case MarkAsInitial():
                state_type, eq_class = operation.get_state()
                if state_type == TO_CORRECT:
                    initials.add(eq_class)
                else:
                    initials.add(eq_class_to_state_mapping[eq_class][-1])

            case MarkStateAsFinal():
                state_type, eq_class = operation.get_state()
                if state_type == TO_CORRECT:
                    finals.add(eq_class)
                else:
                    finals.add(eq_class_to_state_mapping[eq_class][-1])

            case MarkStateAsNonFinal():
                _, eq_class = operation.get_state()
                initials.remove(eq_class)

            case RemoveMarkAsInitial():
                pass

            case RemoveTransition():
                pass

            case _:
                raise Exception("Unknown edit operation")

    correct_automatas = []
    # Create all possible combinations of transitions and construct the corresponding automata
    for this_transitions in aux_unroll_transitions(transitions_options):

        this_states = copy.copy(states)
        for s, _, t in this_transitions:
            this_states.add(s)
            this_states.add(t)

        this_initials = initials.intersection(this_states)
        this_finals = finals.intersection(this_states)

        correct_automatas.append(FiniteAutomata(initials=this_initials,
                                                transitions=this_transitions,
                                                finals=this_finals))
    return correct_automatas
