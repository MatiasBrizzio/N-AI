# src/core/search_algorithms/informed.py
"""Informed search algorithms for solving problems in a state-space search framework.

This module implements best-first search, A* search, and recursive best-first search algorithms,
optimized for problems defined in src.core.problem. These algorithms use heuristic functions to guide
the search toward the goal state, making them suitable for puzzles like EightPuzzle or Boggle.
"""

from src.core.problem import Node
from src.utils.utils import PriorityQueue, memoize
from typing import Optional, Tuple, Union, Callable

# Constant for representing unreachable states or infinite cost
infinity = float('inf')

def best_first_graph_search(problem, f: Callable[[Node], float]) -> Tuple[Optional[Node], int, int]:
    """Perform best-first graph search to find a path to the goal state.

    This algorithm explores nodes with the lowest f scores first, where f is a user-specified function
    that estimates the desirability of a node (e.g., heuristic estimate to the goal for greedy search,
    or node depth for breadth-first search). It maintains a set of explored states to avoid revisiting
    and uses a priority queue for the frontier. The f values are memoized on nodes for efficiency.

    Args:
        problem: A Problem instance (from src.core.problem) defining the initial state, goal test,
                 and state transitions.
        f: A function that takes a Node and returns a float score to minimize (e.g., heuristic or depth).

    Returns:
        A tuple of (node, nodes_visited, path_length):
        - node: The goal Node if found, or None if no solution exists.
        - nodes_visited: The number of nodes expanded during the search.
        - path_length: The length of the solution path (number of actions), or 0 if no solution.

    Example:
        For greedy best-first search, use f = problem.h (heuristic to goal).
        For breadth-first search, use f = lambda n: n.depth.
    """
    # Memoize f to cache values on nodes, accessible as node.f
    f = memoize(f, 'f')
    # Initialize with the problem's initial state
    node = Node(problem.initial)
    # Use a priority queue to select nodes with the lowest f score
    frontier = PriorityQueue('min', f)
    frontier.append(node)
    # Track explored states to avoid cycles
    explored = set()
    nodes_visited = 0

    while frontier:
        # Pop the node with the lowest f score
        node = frontier.pop()
        # Check if this node is the goal
        if problem.goal_test(node.state):
            return node, nodes_visited, len(node.path())
        # Mark the state as explored
        explored.add(node.state)
        nodes_visited += 1

        # Expand the node to get child nodes
        for child in node.expand(problem):
            # Add child to frontier if not explored or in frontier
            if child.state not in explored and child not in frontier:
                frontier.append(child)
            # If child is in frontier with a higher f score, replace it
            elif child in frontier:
                if f(child) < frontier[child]:
                    del frontier[child]
                    frontier.append(child)

    # Return failure if no solution is found
    return None, nodes_visited, 0

def best_first_tree_search(problem, f: Callable[[Node], float]) -> Tuple[Optional[Node], int, int]:
    """Perform best-first tree search to find a path to the goal state.

    Similar to best_first_graph_search, but does not track explored states, allowing revisiting
    states (tree-like exploration). This can be faster for problems with few cycles but may
    explore redundant paths. The f function is memoized for efficiency.

    Args:
        problem: A Problem instance defining the initial state, goal test, and state transitions.
        f: A function that takes a Node and returns a float score to minimize.

    Returns:
        A tuple of (node, nodes_visited, path_length):
        - node: The goal Node if found, or None if no solution exists.
        - nodes_visited: The number of nodes expanded during the search.
        - path_length: The length of the solution path, or 0 if no solution.
    """
    # Memoize f to cache values on nodes
    f = memoize(f, 'f')
    # Initialize with the problem's initial state
    node = Node(problem.initial)
    # Use a priority queue to select nodes with the lowest f score
    frontier = PriorityQueue('min', f)
    frontier.append(node)
    nodes_visited = 0

    while frontier:
        # Pop the node with the lowest f score
        node = frontier.pop()
        nodes_visited += 1
        # Check if this node is the goal
        if problem.goal_test(node.state):
            return node, nodes_visited, len(node.path())
        # Expand the node and add all children to the frontier
        for child in node.expand(problem):
            frontier.append(child)

    # Return failure if no solution is found
    return None, nodes_visited, 0

def astar_search(problem, h: Optional[Callable[[Node], float]] = None) -> Tuple[Optional[Node], int, int]:
    """Perform A* graph search to find the optimal path to the goal state.

    A* search uses f(n) = g(n) + h(n), where g(n) is the path cost from the initial state to node n,
    and h(n) is the heuristic estimate to the goal. The heuristic must be admissible (never overestimate)
    for optimality. If h is not provided, the problem's default heuristic (problem.h) is used.

    Args:
        problem: A Problem instance with initial state, goal test, and heuristic function.
        h: Optional heuristic function mapping a Node to a float (default: problem.h).

    Returns:
        A tuple of (node, nodes_visited, path_length):
        - node: The goal Node if found, or None if no solution exists.
        - nodes_visited: The number of nodes expanded during the search.
        - path_length: The length of the solution path, or 0 if no solution.

    Example:
        For EightPuzzle, h might be the Manhattan distance heuristic.
    """
    # Use the provided heuristic or the problem's default
    h = memoize(h or problem.h, 'h')
    # Run best-first graph search with f(n) = g(n) + h(n)
    return best_first_graph_search(problem, lambda n: n.path_cost + h(n))

def astar_tree_search(problem, h: Optional[Callable[[Node], float]] = None) -> Tuple[Optional[Node], int, int]:
    """Perform A* tree search to find a path to the goal state.

    Similar to astar_search, but uses tree search (no explored set), allowing revisiting states.
    This is less memory-intensive but may explore redundant paths and is not guaranteed to find
    the optimal path unless the heuristic is consistent.

    Args:
        problem: A Problem instance with initial state, goal test, and heuristic function.
        h: Optional heuristic function mapping a Node to a float (default: problem.h).

    Returns:
        A tuple of (node, nodes_visited, path_length):
        - node: The goal Node if found, or None if no solution exists.
        - nodes_visited: The number of nodes expanded during the search.
        - path_length: The length of the solution path, or 0 if no solution.
    """
    # Use the provided heuristic or the problem’s default
    h = memoize(h or problem.h, 'h')
    # Run best-first tree search with f(n) = g(n) + h(n)
    return best_first_tree_search(problem, lambda n: n.path_cost + h(n))

def recursive_best_first_search(problem, h: Optional[Callable[[Node], float]] = None) -> Optional[Node]:
    """Perform recursive best-first search (RBFS) to find a path to the goal state.

    RBFS is a recursive version of best-first search that uses less memory by maintaining only
    the current path and a limit on f values. It explores successors in order of increasing f(n),
    backtracking when the f value exceeds the limit. The heuristic must be admissible for correctness.

    Based on Figure 3.26 from "Artificial Intelligence: A Modern Approach."

    Args:
        problem: A Problem instance with initial state, goal test, and heuristic function.
        h: Optional heuristic function mapping a Node to a float (default: problem.h).

    Returns:
        The goal Node if found, or None if no solution exists.

    Note:
        Unlike other searches, RBFS returns only the goal node (not nodes_visited or path_length).
    """
    # Use the provided heuristic or the problem’s default
    h = memoize(h or problem.h, 'h')

    def RBFS(problem, node: Node, flimit: float) -> Tuple[Optional[Node], float]:
        """Recursive helper for RBFS.

        Args:
            problem: The problem instance.
            node: Current node being explored.
            flimit: Upper bound on f values for this branch.

        Returns:
            A tuple of (result, f_value):
            - result: The goal Node if found, or None if no solution.
            - f_value: The f value of the best alternative or infinity if no solution.
        """
        # Check if the current node is the goal
        if problem.goal_test(node.state):
            return node, 0  # Second value is unused
        # Expand the node to get successors
        successors = node.expand(problem)
        if not successors:
            return None, infinity
        # Compute f values for successors, ensuring at least node.f
        for s in successors:
            s.f = max(s.path_cost + h(s), node.f)
        while True:
            # Sort successors by f value (lowest first)
            successors.sort(key=lambda x: x.f)
            best = successors[0]
            # If best f exceeds the limit, return failure
            if best.f > flimit:
                return None, best.f
            # Get the second-best f value as the alternative limit
            alternative = successors[1].f if len(successors) > 1 else infinity
            # Recursively search the best successor
            result, best.f = RBFS(problem, best, min(flimit, alternative))
            if result is not None:
                return result, best.f

    # Initialize the root node with its f value
    node = Node(problem.initial)
    node.f = h(node)
    # Start recursive search with infinite f limit
    result, _ = RBFS(problem, node, infinity)
    return result

# Alias for convenience, as greedy best-first search is a special case of best_first_graph_search
greedy_best_first_graph_search = best_first_graph_search