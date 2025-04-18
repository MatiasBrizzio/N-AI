from random import *
from src.core.search_algorithms.local import hill_climbing, hill_climbing_sideway, hill_climbing_random_restart, \
    simulated_annealing
from src.core.search_algorithms.uninformed import iterative_deepening_search_graph
from src.problems.NQueensProblem import NQueensProblem
from src.utils.TimeoutRun import run_algorithm
from src.utils.TimeoutRun import print_all_solutions

def random_nqueens(bound, size):
    pop = []
    l = list()
    for x in range(bound):
        for y in range(size):
            z = randint(0, size - 1)
            l.append(z)
        pop.append(NQueensProblem(size, (tuple(l))))
        l.clear()
    return pop


if __name__ == '__main__':
    AMOUNT = 10
    checkSol = NQueensProblem(8)
    for tsize in range(8, 10):
        print("Running with board size {}".format(tsize))
        lst = random_nqueens(AMOUNT, tsize)
        for alg in [hill_climbing, hill_climbing_sideway, simulated_annealing, iterative_deepening_search_graph, hill_climbing_random_restart]:
            if alg == hill_climbing_random_restart:
                sol, vst, deep, tm, fal = run_algorithm(alg, lst, lambda: random_nqueens(1, tsize).pop(0))
            else:
                sol, vst, deep, tm, fal = run_algorithm(alg, lst)
            sl = list()
            for s in sol:
                if checkSol.goal_test(s.state):
                    sl.append(s)
            print_all_solutions(alg, sl, vst, deep, tm, fal)