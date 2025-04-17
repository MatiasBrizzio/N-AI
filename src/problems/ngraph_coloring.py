import time

from src.core.logic import *

import itertools


def zip_with_scalar(l, o):
    return [list(a) for a in zip(l, itertools.repeat(o))]


def sublist(lst, n):
    sub = []
    result = []
    for i in lst:
        sub += [i]
        if len(sub) == n: result += [sub]; sub = []
    if sub: result += [sub]
    return result


def gc2pl(neigh, numofcolours):
    # First we create all prop variables:
    lst = list()
    lstne = list()
    if isinstance(neigh, str):
        neighbors = parse_neighbors(neigh)
    else:
        neighbors = neigh
    row = len(neighbors)
    for i in neighbors:
        for j in range(1, numofcolours + 1):
            lst.append(expr(str(i) + str('_') + str(j)))
            lstne.append(expr(str('~') + str(i) + str('_') + str(j)))

    # each node must to be colored
    firstclause = list()
    for sl in sublist(lst, numofcolours):
        firstclause.append(associate('|', sl))

    # Each node has to be colored by only one colour
    for sl in sublist(lstne, numofcolours):
        for i in range(0, len(sl)):
            lst = zip_with_scalar(sl[i + 1:], sl[i])
            for x in lst:
                firstclause.append(associate('|', x))

    # two adj nodes must be colored by different colours
    visited = set()
    for state in neighbors:
        visited.add(state)
        adj = set(neighbors[state])
        for n_state in adj:
            for col in range(1, numofcolours + 1):
                cl = list()
                if str(state) > str(n_state): a, b = n_state, state
                else: a, b = state, n_state
                cl.append(expr(str('~') + str(a) + str('_') + str(col)))
                cl.append(expr(str('~') + str(b) + str('_') + str(col)))
                firstclause.append(associate('|', cl))

    b = list(set(firstclause))
    return associate('&', b)


def backtrackingalgaux(neighbors, colors, nodes, colorlist, index):
    if not nodes:
        return True

    for c1 in range(1, colors + 1):
        adj = set(neighbors[nodes[0]])
        found = False
        for aj in adj:
            if c1 == colorlist[(index.index(aj))]: found = True; break
        if not found:
            colorlist[index.index(nodes[0])] = c1
            if backtrackingalgaux(neighbors, colors, nodes[1:], colorlist, index):
                return True
            colorlist[index.index(nodes[0])] = 0


def backtrackingalg(graph, colors):
    if isinstance(graph, str):
        neighbors = parse_neighbors(graph)
    else:
        neighbors = graph
    nodes = list()
    colorlist = [0] * len(neighbors)
    index = list()

    for node in neighbors:
        adjs = set(neighbors[node])
        if node in adjs:
            return None

    for node in neighbors:
        index.append(node)
        nodes.append(node)

    if backtrackingalgaux(neighbors, colors, nodes, colorlist, index) is None:
        return None
    else:
        return zip(neighbors, colorlist)

"""
Random graph generator. It will create a graph with the number of nodes specified and 
two nodes will be connected with some probability
"""


def graph_generator(number_of_nodes, prob):
    import random
    graph = dict()
    nodes = list()
    for i in range(number_of_nodes):
        nodes.append(str('N') + str(i))
        graph[str('N') + str(i)] = list()
    for i in nodes:
        lst = list()
        for j in nodes:
            lst2 = list()
            # Self-cycle are not allowed
            if j == i:
                continue
            elif probability(prob):
                lst.append(j)
                graph[str(j)].append(i)
                graph[str(j)] = list(set(graph[str(j)] ))

        graph[str(i)] = list(set(graph[str(i)] + list(map(str, lst))))
    return graph


if __name__ == '__main__':
    for i in range(1, 10):
        nnodes = random.randint(1, 10)
        prob = random.uniform(0, 1)
        numcolors = random.randint(1, nnodes + 1)
        a = graph_generator(nnodes, prob)
        print("for graph with {} colors and {} nodes: {}  :".format(numcolors, nnodes, a))
        st = time.time()
        res = backtrackingalg(a, numcolors)
        print("Backtracking: Taken time: {}".format(time.time() - st))
        if res is None: print('No solution')
        else:
            for x in res:
                print(x)

        f = gc2pl(a, numcolors)
        # print(f)
        st = time.time()
        x = dpll_satisfiable(f)
        print("DPLL CNF: taken time: {}:".format(time.time() - st))
        if not x: print('No solution')
        else:
            for k in x.keys():
                if x[k]:
                    print(k, end=',')
            print()

        a = MapColoringSAT(list(map(str, list(range(1, numcolors + 1)))), a)
        st = time.time()
        x = dpll_satisfiable(a)
        print("DPLL book CNF taken time: {}:".format(time.time() - st))
        if not x: print('No solution')
        else:
            for k in x.keys():
                if x[k]: print(k, end=',')
            print()