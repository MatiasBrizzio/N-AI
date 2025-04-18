# src/core/compare.py
from src.core.graph import GraphProblem, romania_map, australia_map
from src.core.search_algorithms.informed import recursive_best_first_search
from src.core.search_algorithms.uninformed import depth_first_graph_search, breadth_first_graph_search, \
    breadth_first_tree_search, iterative_deepening_search, depth_limited_search
from src.utils.utils import print_table, name
from src.core.problem import Problem

class InstrumentedProblem(Problem):

    """Delegates to a problem, and keeps statistics."""

    def __init__(self, problem, initial):
        super().__init__(initial)
        self.problem = problem
        self.succs = self.goal_tests = self.states = 0
        self.found = None

    def actions(self, state):
        self.succs += 1
        return self.problem.actions(state)

    def result(self, state, action):
        self.states += 1
        return self.problem.result(state, action)

    def goal_test(self, state):
        self.goal_tests += 1
        result = self.problem.goal_test(state)
        if result:
            self.found = state
        return result

    def path_cost(self, c, state1, action, state2):
        return self.problem.path_cost(c, state1, action, state2)

    def value(self, state):
        return self.problem.value(state)

    def __getattr__(self, attr):
        return getattr(self.problem, attr)

    def __repr__(self):
        return '<{:4d}/{:4d}/{:4d}/{}>'.format(self.succs, self.goal_tests,
                                               self.states, str(self.found)[:4])


def compare_searchers(problems, header,
                      searchers=None):
    if searchers is None:
        searchers = [breadth_first_tree_search,
                     breadth_first_graph_search,
                     depth_first_graph_search,
                     iterative_deepening_search,
                     depth_limited_search,
                     recursive_best_first_search]

    def do(searcher, problem):
        p = InstrumentedProblem(problem)
        searcher(p)
        return p
    table = [[name(s)] + [do(s, p) for p in problems] for s in searchers]
    print_table(table, header)


def compare_graph_searchers():
    """Prints a table of search results."""
    compare_searchers(problems=[GraphProblem('Arad', 'Bucharest', romania_map),
                                GraphProblem('Oradea', 'Neamt', romania_map),
                                GraphProblem('Q', 'WA', australia_map)],
                      header=['Searcher', 'romania_map(Arad, Bucharest)',
                              'romania_map(Oradea, Neamt)', 'australia_map'])