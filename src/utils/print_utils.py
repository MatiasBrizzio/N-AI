from typing import Callable, List, Any, Optional

from src.problems.InstrumentedProblem import InstrumentedProblem


def print_all_solutions(
    algorithm: Callable,
    solutions: List[Any],
    visited: List[int],
    depths: List[int],
    times: List[float],
    failures: int,
    heuristic: Optional[Callable] = None
) -> None:
    """Print basic aggregated solutions and metrics."""
    alg_name = algorithm.__name__
    h_name = heuristic.__name__ if heuristic else "None"
    print(f"\nFor {alg_name} with {h_name}:")
    print(f"  Number of Solutions: {len(solutions)}")
    if solutions:
        print(f"  Avg visited nodes: {sum(visited) / len(visited):.2f}")
        print(f"  Avg depth reached: {sum(depths) / len(depths):.2f}")
        print(f"  Avg time taken: {sum(times) / len(times):.4f}s")
    print(f"  Failed: {failures}")

def print_all_solutions_with_stats(
    algorithm: Callable,
    solutions: List[Any],
    visited: List[int],
    depths: List[int],
    times: List[float],
    failures: int,
    heuristic: Optional[Callable] = None,
    instrumented_problems: Optional[List[InstrumentedProblem]] = None
) -> None:
    """Print solutions with detailed InstrumentedProblem statistics."""
    print_all_solutions(algorithm, solutions, visited, depths, times, failures, heuristic)
    if instrumented_problems:
        print("\nPer-puzzle statistics:")
        for i, (solution, prob) in enumerate(zip(solutions, instrumented_problems)):
            print(f"\nPuzzle {i+1}:")
            if solution:
                print(f"  Solution state: {solution.state}")
                print(f"  Nodes expanded (succs): {prob.succs}")
                print(f"  Goal tests: {prob.goal_tests}")
                print(f"  States generated: {prob.states}")
                print(f"  Goal state: {prob.found}")
                print(f"  Nodes visited: {visited[i]}")
                print(f"  Depth: {depths[i]}")
                print(f"  Time: {times[i]:.4f}s")
            else:
                print("  No solution found (timeout or failure)")
                print(f"  Partial stats - Nodes expanded: {prob.succs}, Goal tests: {prob.goal_tests}, States: {prob.states}")