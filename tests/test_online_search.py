# tests/test_online_search.py
import pytest
import sys
import os

# Add project root to sys.path (robust version)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.search_algorithms.online import OnlineDFSAgent, OnlineSearchProblem

class SimpleGraph:
    """A simple graph for basic testing: A -> B, A -> C, B -> A, C -> A."""

    def __init__(self):
        self.graph_dict = {'A': {'B': 'B', 'C': 'C'}, 'B': {'A': 'A'}, 'C': {'A': 'A'}}
        self.least_costs = {'A': 2, 'B': 1, 'C': 1}


class ComplexGraph:
    """A complex graph for detailed testing:
    A -> B, C
    B -> A, D
    C -> A, D
    D -> B, E
    E -> (goal, no outgoing edges)
    """

    def __init__(self):
        self.graph_dict = {
            'A': {'to_B': 'B', 'to_C': 'C'},
            'B': {'to_A': 'A', 'to_D': 'D'},
            'C': {'to_A': 'A', 'to_D': 'D'},
            'D': {'to_B': 'B', 'to_E': 'E'},
            'E': {}  # Goal state with no outgoing edges
        }
        self.least_costs = {'A': 4, 'B': 3, 'C': 3, 'D': 2, 'E': 0}


def test_online_dfs_agent_simple():
    """Test OnlineDFSAgent on a simple graph, verifying action selection and goal termination."""
    problem = OnlineSearchProblem(initial='A', goal='B', graph=SimpleGraph())
    agent = OnlineDFSAgent(problem)
    action = agent('A')  # First percept: start at A
    assert action in ['B', 'C'], f"Expected action 'B' or 'C', got {action}"
    assert agent('B') is None, "Expected None at goal state B"
    assert agent.s == 'B', "Agent should be in state B"
    assert len(agent.untried.get('A', [])) < 2, "Agent should have tried at least one action from A"


def test_online_dfs_agent_complex():
    """Test OnlineDFSAgent on a complex graph, tracking nodes visited and path taken."""
    problem = OnlineSearchProblem(initial='A', goal='E', graph=ComplexGraph())
    agent = OnlineDFSAgent(problem)

    # Track visited states and actions
    visited = []
    actions = []
    percepts = ['A']  # Start at A

    # Simulate agent exploration until goal or max steps
    max_steps = 15  # Increased to allow more exploration
    for _ in range(max_steps):
        action = agent(percepts[-1])
        if action is None:  # Goal reached
            break
        next_state = problem.output(percepts[-1], action)
        print(f"Step {_}: Action: {action}, Next state: {next_state}, Untried: {agent.untried}, Unbacktracked: {agent.unbacktracked}")
        percepts.append(next_state)
        visited.append(next_state)
        actions.append(action)

    print(f"Final: Visited: {visited}, Actions: {actions}, Unbacktracked: {agent.unbacktracked}, Result: {agent.result}")
    # Verify goal reached
    assert agent.s == 'E', f"Expected final state 'E', got {agent.s}"
    assert action is None, "Expected None action at goal"

    # Verify path properties
    assert visited[-1] == 'E', "Path should end at goal E"
    assert set(visited).issubset({'A', 'B', 'C', 'D', 'E'}), f"Unexpected states in path: {visited}"
    # Check for key transition (D -> E)
    assert any(visited[i] == 'D' and visited[i+1] == 'E' for i in range(len(visited)-1)), \
        "Path should include D -> E transition"
    # Limit excessive revisits
    from collections import Counter
    visit_counts = Counter(visited)
    assert visit_counts.get('A', 0) <= 3, f"Visited A too many times: {visit_counts['A']}"
    assert visit_counts.get('C', 0) <= 3, f"Visited C too many times: {visit_counts['C']}"

    # Verify internal state
    assert len(agent.untried.get('A', [])) == 0, "All actions from A should be tried"
    assert 'E' not in agent.untried or len(agent.untried['E']) == 0, "Goal should have no untried actions"
    assert ('A', actions[0]) in agent.result, "Result should record first transition"


def test_online_dfs_agent_unreachable_goal():
    """Test OnlineDFSAgent when the goal is unreachable."""

    class UnreachableGraph:
        def __init__(self):
            self.graph_dict = {'A': {'B': 'B'}, 'B': {'A': 'A'}}  # No path to C
            self.least_costs = {'A': 2, 'B': 1}

    problem = OnlineSearchProblem(initial='A', goal='C', graph=UnreachableGraph())
    agent = OnlineDFSAgent(problem)

    visited = []
    percepts = ['A']
    max_steps = 5

    for _ in range(max_steps):
        action = agent(percepts[-1])
        if action is None:  # No actions left
            break
        next_state = problem.output(percepts[-1], action)
        percepts.append(next_state)
        visited.append(next_state)

    assert agent.s in ['A', 'B'], f"Expected final state in A or B, got {agent.s}"
    assert action is None, "Expected None when no actions remain"
    assert set(visited).issubset({'A', 'B'}), f"Visited unexpected states: {visited}"
    assert len(agent.untried.get('A', [])) == 0, "All actions from A should be tried"
    assert len(agent.untried.get('B', [])) == 0, "All actions from B should be tried"


def test_online_dfs_agent_backtracking():
    """Test OnlineDFSAgent's backtracking behavior."""
    class BacktrackGraph:
        def __init__(self):
            self.graph_dict = {
                'A': {'to_B': 'B', 'to_C': 'C'},
                'B': {'to_A': 'A'},  # Dead end
                'C': {'to_D': 'D'},
                'D': {'to_E': 'E'},
                'E': {}  # Goal
            }
            self.least_costs = {'A': 3, 'B': 4, 'C': 2, 'D': 1, 'E': 0}

    problem = OnlineSearchProblem(initial='A', goal='E', graph=BacktrackGraph())
    agent = OnlineDFSAgent(problem)

    visited = []
    actions = []
    percepts = ['A']

    for _ in range(10):
        action = agent(percepts[-1])
        if action is None:
            break
        next_state = problem.output(percepts[-1], action)
        print(f"Step {_}: Action: {action}, Next state: {next_state}, Untried: {agent.untried}, Unbacktracked: {agent.unbacktracked}")
        percepts.append(next_state)
        visited.append(next_state)
        actions.append(action)

    print(f"Final: Visited: {visited}, Actions: {actions}, Unbacktracked: {agent.unbacktracked}, Result: {agent.result}")
    assert agent.s == 'E', f"Expected final state 'E', got {agent.s}"
    assert visited[-1] == 'E', "Last visited state should be goal"
    assert 'B' in visited, "Should visit B before backtracking"
    assert 'C' in visited, "Should visit C after backtracking"
    assert ('A', 'to_B') in agent.result, "Should record transition to B"
    assert ('C', 'to_D') in agent.result, "Should record transition to D"
    # Allow unbacktracked['A'] to contain states if goal is reached
    assert set(agent.unbacktracked.get('A', [])).issubset({'A', 'B', 'C'}), \
        f"Unbacktracked for A contains invalid states: {agent.unbacktracked.get('A', [])}"