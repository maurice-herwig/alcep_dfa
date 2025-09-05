from wofa import get_solution, FiniteAutomata
from alcep_dfa import all_dfa_corrections, get_random_correction, apply_correction, get_all_minimal_corrections

if __name__ == '__main__':
    # Get the minimal DFA from exercise "A"
    minimal_dfa = get_solution(exercise="A")

    # Set the alphabet for the FiniteAutomata class
    FiniteAutomata.set_alphabet(sigma=minimal_dfa.calc_and_get_alphabet())

    # Minimize the DFA
    minimal_dfa.minimize()

    # Define a DFA to be corrected
    to_correct = FiniteAutomata({0}, [(0, 'a', 1), (1, '0', 0), (1, 'a', 2)], {1})
    print("DFA to be correct")
    print(to_correct)

    print("Minimal DFA of the target language")
    print(minimal_dfa)

    # Compute all corrections
    root_node = all_dfa_corrections(to_correct=to_correct, minimal_dfa=minimal_dfa)

    # Compute  all minimal corrections
    costs, min_corrections = get_all_minimal_corrections(root_node=root_node)

    print(f'The minimal correction has cost: {costs}')
    print("minimal corrections")
    for correction in min_corrections:
        print(f'Correction: {correction} correct to the following automata(s): ')

        for corrected in apply_correction(to_correct=to_correct, correction=correction):
            print(corrected)

    # Get a random correction from the computed SPPF
    correction = get_random_correction(root_node=root_node)

    print(f'A selected random correction {correction} correct to the following automata(s): ')
    # Apply the correction to the to correct DFA and
    # print the corrected automatas and check if they are equivalent to the minimal DFA
    for corrected in apply_correction(to_correct=to_correct, correction=correction):
        print(corrected)
