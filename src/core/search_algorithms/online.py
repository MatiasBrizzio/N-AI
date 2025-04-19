# src/core/search_algorithms/online.py
"""Online search algorithms for agents operating in dynamic or partially observable environments.

This module implements online depth-first search (DFS), LRTA* (Learning Real-Time A*),
and AND-OR graph search for problems defined in src.core.problem. Unlike offline search,
these algorithms interleave planning and action execution, making them suitable for real-time
applications like robotics, game agents, or dynamic puzzles in the N-AI project.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from src.core.problem import Problem
from src.utils.utils import argmin

class OnlineDFSAgent:
    """An online depth-first search (DFS) agent for dynamic environments.

    The agent explores the environment by executing actions and observing percepts in real time,
    maintaining a map of untried actions, unbacktracked states, and action results. It uses DFS
    to explore new actions and backtracks when necessary, suitable for deterministic, fully
    observable environments. Based on Figure 4.21 from "Artificial Intelligence: A Modern Approach."

    Subclasses must override `update_state` to convert percepts to states.

    Attributes:
        problem: The Problem instance defining actions, results, and goal test.
        s: The current state (None initially).
        a: The current action to execute (None initially or at goal).
        untried: Dict mapping states to lists of untried actions.
        unbacktracked: Dict mapping states to lists of states to backtrack to.
        result: Dict mapping (state, action) pairs to resulting states.
    """

    def __init__(self, problem: Problem):
        """Initialize the agent with a problem instance.

        Args:
            problem: A Problem subclass instance defining the environment.
        """
        self.problem = problem
        self.s = None
        self.a = None
        self.untried: Dict[Any, List[Any]] = {}
        self.unbacktracked: Dict[Any, List[Any]] = {}
        self.result: Dict[Tuple[Any, Any], Any] = {}

    def __call__(self, percept: Any) -> Optional[Any]:
        """Determine the next action based on the current percept.

        Updates the agent's state, selects an untried action, or backtracks if no untried actions
        remain. Returns None if at the goal or no action is possible.

        Args:
            percept: The current observation from the environment.

        Returns:
            The action to execute, or None if at the goal or no actions remain.
        """
        # Convert percept to state
        s1 = self.update_state(percept)
        # If at the goal, take no action
        if self.problem.goal_test(s1):
            self.a = None
        else:
            # Initialize untried actions for new states
            if s1 not in self.untried:
                self.untried[s1] = self.problem.actions(s1)
            # Update result and backtracking info for the previous state
            if self.s is not None:
                if s1 != self.result.get((self.s, self.a)):
                    self.result[(self.s, self.a)] = s1
                    # Add previous state to backtrack list (insert at front)
                    self.unbacktracked.setdefault(s1, []).insert(0, self.s)
            # If no untried actions, try backtracking
            if not self.untried[s1]:
                if not self.unbacktracked.get(s1):
                    self.a = None
                else:
                    # Backtrack to a previous state
                    back_state = self.unbacktracked[s1].pop(0)
                    for (s, b) in self.result:
                        if self.result[(s, b)] == back_state:
                            self.a = b
                            break
            else:
                # Try a new action from the untried list
                self.a = self.untried[s1].pop(0)
        # Update the current state
        self.s = s1
        return self.a

    def update_state(self, percept: Any) -> Any:
        """Convert a percept to a state.

        This default implementation assumes the percept is the state. Subclasses should override
        to process complex percepts.

        Args:
            percept: The observation from the environment.

        Returns:
            The state corresponding to the percept.
        """
        return percept

class OnlineSearchProblem(Problem):
    """A problem for online search in deterministic, fully observable environments.

    Defines a state-transition model using a graph structure, suitable for agents executing
    actions in real time. Based on Figure 4.23 from AIMA.

    Attributes:
        initial: The initial state.
        goal: The goal state.
        graph: A graph object with graph_dict (state to action-to-state mappings)
               and least_costs (state to least cost to goal).
    """

    def __init__(self, initial: Any, goal: Any, graph: Any):
        """Initialize the problem with initial state, goal, and graph.

        Args:
            initial: The starting state.
            goal: The target goal state.
            graph: An object with graph_dict (state transitions) and least_costs (heuristic costs).
        """
        self.initial = initial
        self.goal = goal
        self.graph = graph

    def actions(self, state: Any) -> List[Any]:
        """Return the list of possible actions from a state.

        Args:
            state: The current state.

        Returns:
            A list of actions available in the state.
        """
        return list(self.graph.graph_dict[state].keys())

    def output(self, state: Any, action: Any) -> Any:
        """Return the resulting state after taking an action.

        Args:
            state: The current state.
            action: The action to take.

        Returns:
            The resulting state.
        """
        return self.graph.graph_dict[state][action]

    def h(self, state: Any) -> float:
        """Return the least possible cost to reach a goal from the state.

        Args:
            state: The current state.

        Returns:
            The heuristic cost estimate to the goal.
        """
        return self.graph.least_costs[state]

    def c(self, s: Any, a: Any, s1: Any) -> float:
        """Return the cost of moving from state s to s1 via action a.

        This implementation assumes a uniform cost of 1 for all transitions.

        Args:
            s: The starting state.
            a: The action taken.
            s1: The resulting state.

        Returns:
            The cost of the transition (default: 1).
        """
        return 1

    def update_state(self, percept: Any) -> Any:
        """Update the state based on a percept.

        Not implemented; subclasses should override for specific environments.

        Args:
            percept: The observation from the environment.

        Raises:
            NotImplementedError: Always, as this is an abstract method.
        """
        raise NotImplementedError

    def goal_test(self, state: Any) -> bool:
        """Check if the state is the goal.

        Args:
            state: The state to test.

        Returns:
            True if the state matches the goal, False otherwise.
        """
        return state == self.goal

class LRTAStarAgent:
    """A Learning Real-Time A* (LRTA*) agent for online search.

    The agent learns heuristic estimates (H) while exploring, balancing exploration and exploitation
    to minimize costs in real-time. Suitable for deterministic, fully observable environments.
    Based on Figure 4.24 from AIMA.

    Attributes:
        problem: The OnlineSearchProblem instance defining actions, outputs, and costs.
        H: Dict mapping states to learned heuristic cost estimates.
        s: The current state (None initially).
        a: The current action to execute (None initially or at goal).
    """

    def __init__(self, problem: OnlineSearchProblem):
        """Initialize the agent with an OnlineSearchProblem.

        Args:
            problem: An OnlineSearchProblem instance defining the environment.
        """
        self.problem = problem
        self.H: Dict[Any, float] = {}
        self.s = None
        self.a = None

    def __call__(self, s1: Any) -> Optional[Any]:
        """Determine the next action based on the current state.

        Updates heuristic estimates and selects the action that minimizes the estimated cost to the
        goal. Returns None if at the goal.

        Args:
            s1: The current state (not a percept, unlike OnlineDFSAgent).

        Returns:
            The action to execute, or None if at the goal.
        """
        # If at the goal, take no action
        if self.problem.goal_test(s1):
            self.a = None
            return self.a
        # Initialize heuristic for new states
        if s1 not in self.H:
            self.H[s1] = self.problem.h(s1)
        # Update heuristic for the previous state
        if self.s is not None:
            # Compute the minimum cost over possible actions
            self.H[self.s] = min(
                self.LRTA_cost(self.s, b, self.problem.output(self.s, b), self.H)
                for b in self.problem.actions(self.s)
            )
        # Select the action that minimizes the cost
        self.a = argmin(
            self.problem.actions(s1),
            key=lambda b: self.LRTA_cost(s1, b, self.problem.output(s1, b), self.H)
        )
        # Update the current state
        self.s = s1
        return self.a

    def LRTA_cost(self, s: Any, a: Any, s1: Any, H: Dict[Any, float]) -> float:
        """Estimate the cost to move from state s to s1 via action a, plus the cost to the goal.

        Combines the transition cost (c) with the learned heuristic (H) for s1. If s1 is not in H,
        uses the problem's heuristic estimate.

        Args:
            s: The starting state.
            a: The action taken.
            s1: The resulting state.
            H: Dict of learned heuristic estimates.

        Returns:
            The estimated total cost (transition cost + heuristic to goal).
        """
        if s1 is None:
            return self.problem.h(s)
        # Use learned heuristic if available, otherwise fall back to problem.h
        try:
            return self.problem.c(s, a, s1) + H[s1]
        except KeyError:
            return self.problem.c(s, a, s1) + self.problem.h(s1)

def and_or_graph_search(problem: Problem) -> Optional[Union[List, Dict]]:
    """Perform AND-OR graph search for nondeterministic, fully observable environments.

    Handles environments where actions lead to multiple possible states (AND nodes) due to
    stochasticity. Returns a conditional plan mapping states to actions or subplans, ensuring
    the agent can reach the goal from any resulting state. Based on Figure 4.11 from AIMA.

    Args:
        problem: A Problem instance with initial state, goal test, actions, and result function.

    Returns:
        A conditional plan (list or dict) to reach the goal, or None if no plan exists.
        - For OR nodes: A list [action, subplan].
        - For AND nodes: A dict mapping states to subplans.
    """

    def or_search(state: Any, problem: Problem, path: List[Any]) -> Optional[List]:
        """Search from an OR node (agent chooses an action).

        Args:
            state: The current state.
            problem: The problem instance.
            path: List of states visited to avoid cycles.

        Returns:
            A plan as a list [action, subplan], or None if no plan exists.
        """
        # Return empty plan if at the goal
        if problem.goal_test(state):
            return []
        # Avoid cycles
        if state in path:
            return None
        # Try each action
        for action in problem.actions(state):
            plan = and_search(problem.result(state, action), problem, path + [state])
            if plan is not None:
                return [action, plan]
        return None

    def and_search(states: List[Any], problem: Problem, path: List[Any]) -> Optional[Dict]:
        """Search from an AND node (all possible resulting states).

        Args:
            states: List of possible states after an action.
            problem: The problem instance.
            path: List of states visited to avoid cycles.

        Returns:
            A plan as a dict mapping states to subplans, or None if any state has no plan.
        """
        plan = {}
        for s in states:
            plan[s] = or_search(s, problem, path)
            if plan[s] is None:
                return None
        return plan

    # Start search from the initial state
    return or_search(problem.initial, problem, [])