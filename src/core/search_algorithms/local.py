# src/core/search_algorithms/local.py
import math
import random
import sys
from src.core.problem import Node
from src.utils.utils import argmax_random_tie, probability

def hill_climbing(problem):
    """From the initial node, keep choosing the neighbor with highest value,
    stopping when no neighbor is better. [Figure 4.2]"""
    current = Node(problem.initial)
    visited = 0
    while True:
        neighbors = current.expand(problem)
        #print("Node: {} neighbors: {} [7]:{}".format(current, neighbors, current.state[3]))
        if not neighbors:
            break
        neighbor = argmax_random_tie(neighbors,
                                     key=lambda node: problem.value(node.state))
        if problem.value(neighbor.state) <= problem.value(current.state):
            break
        current = neighbor
        visited += 1
    # print("{} {} {}".format(current, visited, len(current.path())))
    return current, visited, len(current.path())


def hill_climbing_random_restart(problem, randomGenerator, k=1000):
    result, visited, len = hill_climbing(problem)
    noVisited = 0
    if problem.goal_test(result.state):
        # print("  {} {} {}    ".format(result, noVisited, len(result.path())), end='')
        return result, noVisited, result.path().__len__()
    else:
        for i in range(k):
            current = randomGenerator()
            noVisited += 1
            result, visited, len = hill_climbing(current)
            if problem.goal_test(result.state):
                return result, noVisited, result.path().__len__()
        return None, noVisited, 0


def hill_climbing_sideway(problem, bound=200):
    """From the initial node, keep choosing the neighbor with highest value,
    stopping when no neighbor is better. [Figure 4.2]"""
    current = Node(problem.initial)
    current_movements = 0
    visited = 0
    while True:
        neighbors = current.expand(problem)
        #print("Node: {} neighbors: {} [7]:{}".format(current, neighbors, current.state[3]))
        if not neighbors:
            break
        neighbor = argmax_random_tie(neighbors,
                                     key=lambda node: problem.value(node.state))
        if problem.value(neighbor.state) < problem.value(current.state):
            break
        if problem.value(neighbor.state) == problem.value(current.state) and current_movements == bound:
            print("bound was reached")
            break
        elif problem.value(neighbor.state) == problem.value(current.state) and current_movements != bound:
            #print("Node: {} neighbors: {} [7]:{} sideway: {}".format(current, neighbors, current.state[3], current_movements))
            current_movements = current_movements+1
            current = neighbor
            visited += 1
        else:
            current = neighbor
            visited += 1
    # print("{} {} {}".format(current, visited, len(current.path())))
    return current, visited, len(current.path())

def exp_schedule(k=20, lam=0.005, limit=100):
    """One possible schedule function for simulated annealing"""
    return lambda t: (k * math.exp(-lam * t) if t < limit else 0)


def simulated_annealing(problem, schedule=exp_schedule()):
    """[Figure 4.5] CAUTION: This differs from the pseudocode as it
    returns a state instead of a Node."""
    current = Node(problem.initial)
    visited = 0
    for t in range(sys.maxsize):
        T = schedule(t)
        if T == 0:
            # print("{} {} {}".format(current, visited, len(current.path())))
            return current, visited,  len(current.path())
        neighbors = current.expand(problem)
        if not neighbors:
            return current, visited,  len(current.path())
        next_choice = random.choice(neighbors)
        delta_e = problem.value(next_choice.state) - problem.value(current.state)
        if delta_e > 0 or probability(math.exp(delta_e / T)):
            current = next_choice
            visited += 1


def simulated_annealing_full(problem, schedule=exp_schedule()):
    """ This version returns all the states encountered in reaching
    the goal state."""
    states = []
    current = Node(problem.initial)
    for t in range(sys.maxsize):
        states.append(current.state)
        T = schedule(t)
        if T == 0:
            return states
        neighbors = current.expand(problem)
        if not neighbors:
            return current.state
        next_choice = random.choice(neighbors)
        delta_e = problem.value(next_choice.state) - problem.value(current.state)
        if delta_e > 0 or probability(math.exp(delta_e / T)):
            current = next_choice
