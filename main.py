from wofa import get_solution, FiniteAutomata
from alcep_dfa import all_dfa_corrections, get_random_correction, apply_correction
import pprint

if __name__ == '__main__':
    # Get the minimal DFA from exercise "A"
    minimal_dfa = get_solution(exercise="A")

    # Set the alphabet for the FiniteAutomata class
    FiniteAutomata.set_alphabet(sigma=minimal_dfa.calc_and_get_alphabet())

    # Minimize the DFA
    minimal_dfa.minimize()

    print(minimal_dfa)
    # Define a DFA to be corrected
    to_correct = FiniteAutomata({0}, [(0, 'a', 1), (1, '0', 0), (1, 'a', 2)], {1})

    # Compute all corrections
    root_node = all_dfa_corrections(to_correct=to_correct, minimal_dfa=minimal_dfa)

    # Get a random correction from the computed SPPF
    correction = get_random_correction(root_node=root_node)

    pprint.pprint(correction)

    # Apply the correction to the to correct DFA
    corrected_automatas = apply_correction(to_correct=to_correct, correction=correction)

    # Print the corrected automatas and check if they are equivalent to the minimal DFA
    for corrected in corrected_automatas:
        print(corrected.equivalence_test(other=minimal_dfa))
        print(corrected)
