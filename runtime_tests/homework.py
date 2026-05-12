from collections import defaultdict
from multiprocessing import Process, Queue
from pathlib import Path
from statistics import mean
from time import perf_counter
from wofa import get_solution, FiniteAutomata, SubmissionIterator
from alcep_dfa import Correction

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("Agg")


CORRECTION_TIMEOUT_SECONDS = 180


def run_correction_worker(to_correct, minimal_dfa, result_queue: Queue) -> None:
    # Run the correction computation in a separate process so it can be terminated on timeout.
    try:
        Correction(to_correct=to_correct, minimal_dfa=minimal_dfa)
        result_queue.put(("ok", None))
    except Exception as exc:
        result_queue.put(("error", repr(exc)))


def run_correction_with_timeout(to_correct, minimal_dfa, timeout_seconds: int) -> tuple[bool, str | None]:
    # Start a subprocess for the correction computation and stop it if the timeout is exceeded.
    result_queue = Queue()
    process = Process(target=run_correction_worker, args=(to_correct, minimal_dfa, result_queue))
    process.start()
    process.join(timeout_seconds)

    if process.is_alive():
        process.terminate()
        process.join()
        return False, "timeout"

    if not result_queue.empty():
        status, message = result_queue.get()
        if status == "ok":
            return True, None
        return False, message

    return False, "worker terminated without result"




def format_duration(seconds: float) -> str:
    # Format durations with a readable unit depending on their magnitude.
    if seconds < 0.001:
        return f"{seconds * 1_000_000:.2f} us"
    if seconds < 1:
        return f"{seconds * 1_000:.2f} ms"
    return f"{seconds:.3f} s"


def create_runtime_plot(runtime_records: list[tuple[int, float]], output_path: Path) -> None:
    # Create a scatter plot of runtime by number of states and overlay per-size averages.
    state_counts = [state_count for state_count, _ in runtime_records]
    runtimes = [runtime for _, runtime in runtime_records]

    averages_by_state_count = defaultdict(list)
    for state_count, runtime in runtime_records:
        averages_by_state_count[state_count].append(runtime)

    average_x = sorted(averages_by_state_count)
    average_y = [mean(averages_by_state_count[state_count]) for state_count in average_x]

    plt.figure(figsize=(10, 6))
    plt.scatter(state_counts, runtimes, alpha=0.7, s=45, label="Individual corrections")
    plt.plot(average_x, average_y, color="crimson", marker="o", linewidth=2, label="Average runtime")
    plt.yscale("log")
    plt.xlabel("Number of states")
    plt.ylabel("Runtime in seconds (log scale)")
    plt.title("Correction runtime by DFA size")
    plt.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def create_runtime_tikz_plot(runtime_records: list[tuple[int, float]], output_path: Path) -> None:
    # Create a pgfplots tikzpicture with individual runtimes and average runtime by state count.
    averages_by_state_count = defaultdict(list)
    for state_count, runtime in runtime_records:
        averages_by_state_count[state_count].append(runtime)

    average_points = [
        (state_count, mean(averages_by_state_count[state_count]))
        for state_count in sorted(averages_by_state_count)
    ]

    scatter_coordinates = "\n".join(
        f"        ({state_count}, {runtime})"
        for state_count, runtime in runtime_records
    )
    average_coordinates = "\n".join(
        f"        ({state_count}, {runtime})"
        for state_count, runtime in average_points
    )

    tikz_code = f"""\\begin{{tikzpicture}}
    \\begin{{axis}}[
        width=14cm,
        height=9cm,
        xlabel={{Number of states}},
        ylabel={{Runtime in seconds}},
        ymode=log,
        grid=both,
        minor grid style={{dashed, gray!30}},
        major grid style={{dashed, gray!60}},
        legend pos=north west,
        title={{Correction runtime by DFA size}},
    ]
        \\addplot[
            only marks,
            mark=*,
            mark size=2,
            opacity=0.7,
        ] coordinates {{
{scatter_coordinates}
        }};
        \\addlegendentry{{Individual corrections}}

        \\addplot[
            color=red,
            mark=*,
            line width=1pt,
        ] coordinates {{
{average_coordinates}
        }};
        \\addlegendentry{{Average runtime}}
    \\end{{axis}}
\\end{{tikzpicture}}
"""

    output_path.write_text(tikz_code, encoding="utf-8")


if __name__ == '__main__':
    # Select the exercise for which submissions should be evaluated.
    task = 'H'

    # Store the runtime of each correction computation for incorrect submissions.
    runtimes = []
    # Store pairs of state count and runtime for plotting and later analysis.
    runtime_records = []
    # Group runtimes by the number of states of the processed incorrect DFA.
    runtimes_by_state_count = defaultdict(list)
    # Count correct submissions that are deterministic finite automata.
    correct_dfa = 0
    # Count correct submissions that are not deterministic finite automata.
    correct_non_dfa = 0
    # Count incorrect submissions that are deterministic finite automata.
    incorrect_dfa = 0
    # Count incorrect submissions that are not deterministic finite automata.
    incorrect_non_dfa = 0
    # Count correction computations that were aborted after exceeding the timeout.
    aborted_corrections = 0
    # Count correction computations that failed with an exception.
    failed_corrections = 0
    # Count submissions that could not be parsed into an automaton.
    non_parseable = 0
    # Count how many correction computations have been started.
    correction_index = 0
    # Load the reference solution for the selected exercise.
    solution = get_solution(exercise=task)
    # Use the solution alphabet as the global alphabet for parsed automata.
    FiniteAutomata.set_alphabet(solution.calc_and_get_alphabet())

    # Minimize the reference DFA so comparisons and corrections use a canonical target.
    solution.minimize()

    if not solution.is_deterministic():
        solution = solution.determine()

    # Iterate over all submissions for the selected exercise.
    for sub in SubmissionIterator(task=task):
        # Only process submissions that could be parsed successfully.
        if sub:
            # Remove transitions that are not part of the solution alphabet to avoid issues with
            # equivalence tests and corrections.
            sub.remove_non_alphabet_transitions()
            # Check whether the parsed submission is a DFA before considering corrections.
            is_dfa = sub.is_deterministic()

            # Count submissions that already define the target language.
            if solution.equivalence_test(other=sub):
                if is_dfa:
                    correct_dfa += 1
                else:
                    correct_non_dfa += 1
            else:
                if is_dfa:
                    # Count incorrect DFAs and measure how long the correction computation takes.
                    incorrect_dfa += 1
                    correction_index += 1
                    state_count = sub.get_number_of_states()
                    print(
                        f"[Correction {correction_index}] Starting correction computation "
                        f"for DFA with {state_count} states..."
                    )
                    start_time = perf_counter()
                    completed, error_message = run_correction_with_timeout(
                        to_correct=sub,
                        minimal_dfa=solution,
                        timeout_seconds=CORRECTION_TIMEOUT_SECONDS,
                    )
                    end_time = perf_counter()
                    runtime = end_time - start_time
                    if completed:
                        runtimes.append(runtime)
                        runtime_records.append((state_count, runtime))
                        runtimes_by_state_count[state_count].append(runtime)
                        print(
                            f"[Correction {correction_index}] States: {state_count} | "
                            f"Runtime: {format_duration(runtime)}"
                        )
                    elif error_message == "timeout":
                        aborted_corrections += 1
                        print(
                            f"[Correction {correction_index}] States: {state_count} | "
                            f"Aborted after {format_duration(runtime)}"
                        )
                    else:
                        failed_corrections += 1
                        print(
                            f"[Correction {correction_index}] States: {state_count} | "
                            f"Failed after {format_duration(runtime)} | {error_message}"
                        )
                else:
                    # Count incorrect submissions that are not DFAs.
                    incorrect_non_dfa += 1

        else:
            # Track submissions that are not parseable.
            non_parseable += 1

    # Compute the total number of processed submissions.
    correct = correct_dfa + correct_non_dfa
    incorrect = incorrect_dfa + incorrect_non_dfa
    total = correct + incorrect + non_parseable

    # Print the absolute distribution of submission categories.
    print("Submission distribution")
    print(f"  Correct:                {correct}")
    print(f"  Correct DFA:            {correct_dfa}")
    print(f"  Correct non-DFA:        {correct_non_dfa}")
    print(f"  Incorrect:              {incorrect}")
    print(f"  Incorrect DFA:          {incorrect_dfa}")
    print(f"  Incorrect non-DFA:      {incorrect_non_dfa}")
    print(f"  Aborted corrections:    {aborted_corrections}")
    print(f"  Failed corrections:     {failed_corrections}")
    print(f"  Not parseable:          {non_parseable}")
    print(f"  Total:                  {total}")

    # Print the relative distribution only if at least one submission was processed.
    if total > 0:
        print("Ratios")
        print(f"  Correct:                {correct / total:.2%}")
        print(f"  Correct DFA:            {correct_dfa / total:.2%}")
        print(f"  Correct non-DFA:        {correct_non_dfa / total:.2%}")
        print(f"  Incorrect:              {incorrect / total:.2%}")
        print(f"  Incorrect DFA:          {incorrect_dfa / total:.2%}")
        print(f"  Incorrect non-DFA:      {incorrect_non_dfa / total:.2%}")
        print(f"  Aborted corrections:    {aborted_corrections / total:.2%}")
        print(f"  Failed corrections:     {failed_corrections / total:.2%}")
        print(f"  Not parseable:          {non_parseable / total:.2%}")

    # Print summary statistics for the measured correction runtimes.
    print("Correction runtime statistics")
    if runtimes:
        print(f"  Number of measurements: {len(runtimes)}")
        print(f"  Minimum:                {format_duration(min(runtimes))}")
        print(f"  Maximum:                {format_duration(max(runtimes))}")
        print(f"  Average:                {format_duration(mean(runtimes))}")

        # Print runtime statistics grouped by DFA size to make size-dependent differences visible.
        print("Runtime by number of states")
        for state_count in sorted(runtimes_by_state_count):
            state_runtimes = runtimes_by_state_count[state_count]
            print(
                f"  States={state_count:>2} | Count={len(state_runtimes):>3} | "
                f"Min={format_duration(min(state_runtimes)):>10} | "
                f"Max={format_duration(max(state_runtimes)):>10} | "
                f"Avg={format_duration(mean(state_runtimes)):>10}"
            )

        # Save plot outputs to the temporary directory.
        tmp_dir = Path(__file__).resolve().parents[1] / "tmp"
        tmp_dir.mkdir(exist_ok=True)

        # Save a PNG plot that shows how runtime changes with the number of states.
        plot_path = tmp_dir / f"runtime_by_states_{task}.png"
        create_runtime_plot(runtime_records=runtime_records, output_path=plot_path)
        print(f"Runtime plot saved to:      {plot_path}")

        # Save the same plot as a pgfplots tikzpicture for LaTeX usage.
        tikz_path = tmp_dir / f"runtime_by_states_{task}.tex"
        create_runtime_tikz_plot(runtime_records=runtime_records, output_path=tikz_path)
        print(f"TikZ plot saved to:         {tikz_path}")
    else:
        print("  No runtimes were measured.")
