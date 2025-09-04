from wofa import FiniteAutomata
from alcep_dfa.Nodes.EditOperations import *
from alcep_dfa.Constants import *
from collections import defaultdict
import copy


def apply_correction(to_correct: FiniteAutomata, correction: list[list[EditOperation]]):
    """
    Apply the given correction to the given automata and return all possible resulting automata.

    :param to_correct: The automata to be corrected.
    :param correction: The correction to be applied.
    :return: A list of all possible resulting automata.
    """

    def aux_unroll_transitions(trans_options: list) -> list:
        """
        Auxiliary function to unroll the transition options into all possible combinations of transitions.

        :param trans_options: The list of transition options to be unrolled.
        :return: The list of all possible combinations of transitions.
        """
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

    old_transitions = to_correct.get_transitions()
    old_states = {q for q, _, p in old_transitions}.union({p for q, _, p in old_transitions})
    states = set()
    initials = set()
    finals = copy.copy(to_correct.get_finals())
    eq_class_to_state_mapping = defaultdict(list)
    transitions_options = []

    # Get the first free state number
    n = max(old_states) + 1 if old_states else 0

    # Iterate over operations in the correction list and add the resulting states and transitions
    # into the above initialised sets/lists
    for correction_part in correction:

        this_step_added_eq_class = None
        this_step_added_state_number = -1

        for operation in correction_part:

            match operation:
                case AddNewState():
                    type, eq_class = operation.get_state()
                    this_step_added_eq_class = (type, eq_class)
                    eq_class_to_state_mapping[this_step_added_eq_class].append(n)
                    states.add(n)
                    this_step_added_state_number = n
                    n += 1

                case AddTransition():
                    (source_type, source_eq_class), symbol, (target_type, target_eq_class) = operation.get_transition()

                    if source_type == TO_CORRECT:
                        source_states = [source_eq_class]
                    else:
                        source_states = eq_class_to_state_mapping[(source_type, source_eq_class)]

                    if target_type == TO_CORRECT:
                        target_state = target_eq_class
                    else:
                        if (target_type, target_eq_class) == this_step_added_eq_class:
                            target_state = this_step_added_state_number
                        else:
                            target_state = eq_class_to_state_mapping[(target_type, target_eq_class)]

                    for source_state in source_states:
                        transitions_options.append((copy.copy(source_state), symbol, copy.copy(target_state)))

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
                    elif (state_type, eq_class) == this_step_added_eq_class:
                        initials.add(this_step_added_state_number)
                    else:
                        raise Exception("A new state can only set as initial is it was added in the same step")

                case MarkStateAsFinal():
                    state_type, eq_class = operation.get_state()
                    if state_type == TO_CORRECT:
                        finals.add(eq_class)
                    elif (state_type, eq_class) == this_step_added_eq_class:
                        finals.add(this_step_added_state_number)
                    else:
                        raise Exception("A new state can only set as final is it was added in the same step")

                case MarkStateAsNonFinal():
                    _, eq_class = operation.get_state()
                    finals.remove(eq_class)

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
