"""

"""

from random import shuffle

from src.utils.TimeoutRun import runAlgorithmm, printAllSolutions
from src.core.search import *
import math

"""
    Random generator of eight puzzle instances
"""


def random8Puzzle(amount, k):
    size = (k*k)
    goal = list(range(1, size))
    goal.append(0)
    print(goal)
    pop = []
    for x in range(amount):
        newpuzzle = list(range(0, size))
        shuffle(newpuzzle)
        pop.append(EightPuzzle(tuple(newpuzzle), k, tuple(goal)))
        newpuzzle.clear()
    return pop


"""
    all heuristics functions for eight puzzle problem
"""


def linear(node):
    goal = list(range(1, len(node.state)))
    goal.append(0)
    return sum([1 if node.state[i] != goal[i] else 0 for i in range(len(node.state))])


def max_heuristic(node):
    score1 = manh(node)
    score2 = linear(node)
    return max(score1, score2)


def gaschnig(node):
    res = 0
    state = list(node.state)
    solved = list(range(1, len(node.state)))
    solved.append(0)
    while state != solved:
        zi = state.index(0)
        if solved[zi] != 0:
            sv = solved[zi]
            ci = state.index(sv)
            state[ci], state[zi] = state[zi], state[ci]
        else:
            for i in range(len(state) * len(state)):
                if solved[i] != state[i]:
                    state[i], state[zi] = state[zi], state[i]
                    break
        res += 1
    return res


def manh(node):
    nd = list(node.state)
    goal = list(range(1, len(nd)))
    goal.append(0)
    k = exact_sqrt(len(nd))
    distance = 0
    for i in range(1, len(nd)):
        first = nd.index(i)
        second = goal.index(i)
        fx = first % k
        fy = first / k
        sx = second % k
        sy = second / k
        distance += abs(fx - sx) + abs(fy - sy)
    return math.floor(distance)


if __name__ == '__main__':
    res = random8Puzzle(5, 3)
    for alg in [astar_search, greedy_best_first_graph_search, iterative_deepening_search_graph, astar_tree_search, best_first_tree_search, iterative_deepening_search]:
        for h in [linear, manh, gaschnig, max_heuristic]:
            if alg == iterative_deepening_search_graph or alg == iterative_deepening_search:
                h = None
            sol, vst, deep, tm, fal = runAlgorithmm(alg, res, h)
            printAllSolutions(alg, sol, vst, deep, tm, fal, h)
