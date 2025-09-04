from wofa import get_solution, FiniteAutomata
from alcep_dfa import all_dfa_corrections, get_random_correction
import pprint

if __name__ == '__main__':
    # Get the minimal DFA from exercise "A"
    minimal_dfa = get_solution(exercise="A")

    # Set the alphabet for the FiniteAutomata class
    FiniteAutomata.set_alphabet(sigma=minimal_dfa.calc_and_get_alphabet())

    # Minimize the DFA
    minimal_dfa.minimize()

    # Define a DFA to be corrected
    to_correct = FiniteAutomata({0}, [(0, 'a', 1), (1, '0', 0), (1, 'a', 2)], {1})

    # Compute all corrections
    root_node = all_dfa_corrections(to_correct=to_correct, minimal_dfa=minimal_dfa)

    # Get a random correction from the computed SPPF
    correction = get_random_correction(root_node=root_node)

    pprint.pprint(correction)

    print(root_node)
