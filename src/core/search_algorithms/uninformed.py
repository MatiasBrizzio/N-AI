# src/core/search_algorithms/uninformed.py
import sys
from collections import deque
from src.core.problem import Node
from src.core.search_algorithms.informed import best_first_graph_search

infinity = float('inf')

def breadth_first_tree_search(problem):
    """Search the shallowest nodes in the search tree first.
        Search through the successors of a problem to find a goal.
        The argument frontier should be an empty queue.
        Repeats infinitely in case of loops. [Figure 3.7]"""

    frontier = deque([Node(problem.initial)])  # FIFO queue
    nofvisited = 0
    while frontier:
        node = frontier.popleft()
        nofvisited += 1
        #print(node)
        if problem.goal_test(node.state):
            print("breadth first tree search visited nodes: {}".format(nofvisited))
            return node
        frontier.extend(node.expand(problem))
    return None

def depth_first_tree_search(problem):
    """Search the deepest nodes in the search tree first.
        Search through the successors of a problem to find a goal.
        The argument frontier should be an empty queue.
        Repeats infinitely in case of loops. [Figure 3.7]"""

    frontier = [Node(problem.initial)]  # Stack
    visited = []
    nofvisited = 0
    while frontier:
        node = frontier.pop()
        if not node in visited:
            nofvisited += 1
            #print(node)
            visited.append(node)
        else:
            continue
        if problem.goal_test(node.state):
            print("Depth first tree search visited nodes: {}".format(nofvisited))
            return node
        frontier.extend(node.expand(problem))
    return None

def depth_first_graph_search(problem):
    """Search the deepest nodes in the search tree first.
        Search through the successors of a problem to find a goal.
        The argument frontier should be an empty queue.
        Does not get trapped by loops.
        If two paths reach a state, only use the first one. [Figure 3.7]"""
    frontier = [(Node(problem.initial))]  # Stack
    explored = set()
    nofvisited = 0
    while frontier:
        node = frontier.pop()
        if problem.goal_test(node.state):
            print("Depth first graph search visited nodes: {}".format(nofvisited))
            return node
        explored.add(node.state)
        nofvisited += 1
        #print(node)
        frontier.extend(child for child in node.expand(problem)
                        if child.state not in explored and
                        child not in frontier)
    return None

def breadth_first_graph_search(problem):
    """[Figure 3.11]
    Note that this function can be implemented in a
    single line as below:
    return graph_search(problem, FIFOQueue())
    """
    node = Node(problem.initial)
    nofvisited = 0
    if problem.goal_test(node.state):
        print("breadth first graph search visited nodes: {}".format(nofvisited))
        return node
    frontier = deque([node])
    explored = set()
    while frontier:
        node = frontier.popleft()
        explored.add(node.state)
        nofvisited += 1
        #print(node)
        for child in node.expand(problem):
            if child.state not in explored and child not in frontier:
                if problem.goal_test(child.state):
                    print("breadth first graph search visited nodes: {}".format(nofvisited))
                    return child
                frontier.append(child)
    return None

def depth_limited_search(problem, limit=50):
    """[Figure 3.17]"""
    def recursive_dls(node, problem, limit, visited):
        if problem.goal_test(node.state):
            # print("{} {} {}".format(node, visited, len(node.path())))
            return node, visited, len(node.path())
        elif limit == 0:
            return 'cutoff'
        else:
            cutoff_occurred = False
            for child in node.expand(problem):
                result = recursive_dls(child, problem, limit - 1, visited + 1)
                if result == 'cutoff':
                    cutoff_occurred = True
                elif result is not None:
                    return result, visited, len(node.path())
            return 'cutoff' if cutoff_occurred else None

    # Body of depth_limited_search:
    return recursive_dls(Node(problem.initial), problem, limit, 0)

def iterative_deepening_search(problem):
    """[Figure 3.18]"""
    for depth in range(sys.maxsize):
        result = depth_limited_search(problem, depth)
        if result != 'cutoff':
            return result

def depth_limited_search_graph(problem, limit=50):
    """[Figure 3.17]"""
    def recursive_dls(node, problem, limit, visited):
        visitedS = set()
        visitedS.add(node)
        if problem.goal_test(node.state):
            # print("{} {} {}".format(node, visited, len(node.path())))
            return node, visited, len(node.path())
        elif limit == 0:
            return 'cutoff', visited, len(node.path())
        else:
            cutoff_occurred = False
            for child in [x for x in node.expand(problem) for y in visitedS if x != y]:
                visitedS.add(child)
                result = recursive_dls(child, problem, limit - 1, visited + 1)
                lst = list(result)
                if lst[0] == 'cutoff':
                    cutoff_occurred = True
                elif lst[0] is not None:
                    # print(lst[0])
                    return lst[0], visited, len(lst[0].path())
            return 'cutoff', visited, len(node.path()) if cutoff_occurred else None

    # Body of depth_limited_search:
    return recursive_dls(Node(problem.initial), problem, limit, 0)


def iterative_deepening_search_graph(problem):
    """[Figure 3.18]"""
    for depth in range(sys.maxsize):
        result, visited, len = depth_limited_search_graph(problem, depth)
        if result != 'cutoff':
            return result, visited, len


def uniform_cost_search(problem):
    """[Figure 3.14]"""
    return best_first_graph_search(problem, lambda node: node.path_cost)
