# tests/test_local_search.py
import pytest
from random import shuffle
from src.core.search_algorithms.local import hill_climbing, simulated_annealing
from src.problems.EightPuzzleProblem import EightPuzzle

def test_hill_climbing():
    # Create a 3x3 EightPuzzle with a scrambled initial state
    initial = list(range(9))  # [0, 1, 2, 3, 4, 5, 6, 7, 8]
    shuffle(initial)
    while not EightPuzzle(tuple(initial), 3, tuple([1, 2, 3, 4, 5, 6, 7, 8, 0])).check_solvability(tuple(initial)):
        shuffle(initial)  # Ensure solvable state
    initial = tuple(initial)
    goal = (1, 2, 3, 4, 5, 6, 7, 8, 0)
    problem = EightPuzzle(initial=initial, n=3, goal=goal)
    result, visited, path_len = hill_climbing(problem)
    assert result is not None
    assert visited >= 0
    assert path_len >= 0
    assert problem.value(result.state) >= problem.value(initial)

def test_simulated_annealing():
    # Use a scrambled state for consistency
    initial = list(range(9))
    shuffle(initial)
    while not EightPuzzle(tuple(initial), 3, tuple([1, 2, 3, 4, 5, 6, 7, 8, 0])).check_solvability(tuple(initial)):
        shuffle(initial)
    initial = tuple(initial)
    goal = (1, 2, 3, 4, 5, 6, 7, 8, 0)
    problem = EightPuzzle(initial=initial, n=3, goal=goal)
    print(f"Initial state: {initial}, Value: {problem.value(initial)}")
    result, visited, path_len = simulated_annealing(problem)
    print(f"Result state: {result.state}, Value: {problem.value(result.state)}, Visited: {visited}, Path length: {path_len}")
    assert result is not None
    assert visited >= 0
    assert path_len >= 0
    assert problem.value(result.state) >= problem.value(initial)