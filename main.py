from wofa import get_solution, get_submission, FiniteAutomata
from alcep_dfa import Correction, apply_correction

if __name__ == '__main__':
    # Get the minimal DFA from exercise "A"
    minimal_dfa = get_solution(exercise="A")

    # Set the alphabet for the FiniteAutomata class
    FiniteAutomata.set_alphabet(sigma=minimal_dfa.calc_and_get_alphabet())

    # Minimize the DFA
    minimal_dfa.minimize()

    # Define a DFA to be corrected
    to_correct = get_submission("A", "90")  # FiniteAutomata({0}, [(0, 'a', 1), (1, '0', 0), (1, 'a', 2)], {1})
    print("DFA to be correct")
    print(to_correct)

    print("Minimal DFA of the target language")
    print(minimal_dfa)

    # Compute all corrections
    all_corrections = Correction(to_correct=to_correct, minimal_dfa=minimal_dfa)
    print("CSPPF are computed")

    all_corrections.shrink_to_corrections_to_minimal_dfas()
    number_of_corrections = all_corrections.get_number_of_corrections()
    print(f'Number of corrections: {number_of_corrections}')

    min_corrections = all_corrections.get_all_corrections()

    print("minimal corrections")
    for correction in min_corrections:
        print(f'Correction: {correction} correct to the following automata(s): ')

        for corrected in apply_correction(to_correct=to_correct, correction=correction):
            print(corrected)
