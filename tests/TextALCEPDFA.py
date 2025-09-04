import unittest
from wofa import get_solution, FiniteAutomata
from alcep_dfa import all_dfa_corrections, get_random_correction, apply_correction


class TestALCEPDFA(unittest.TestCase):

    def test(self):
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

        # Get different random corrections and check that the application leads
        # to an automaton equivalent to the minimal DFA
        for _ in range(100):

            # Get a random correction
            correction = get_random_correction(root_node=root_node)

            # Apply the correction to the to correct DFA and iterate over all resulting automata
            for corrected_automata in apply_correction(to_correct=to_correct, correction=correction):

                # Check for each resulting automaton that it is equivalent to the minimal DFA
                self.assertTrue(corrected_automata.equivalence_test(other=minimal_dfa))
