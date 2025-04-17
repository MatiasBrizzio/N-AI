from random import *
from src.core.search import *
from src.utils.TimeoutRun import runAlgorithmm
from src.utils.TimeoutRun import printAllSolutions

def randomNQueens(bound, size):
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
        lst = randomNQueens(AMOUNT, tsize)
        for alg in [hill_climbing, hill_climbing_sideway, simulated_annealing, iterative_deepening_search_graph, hill_climbing_random_restart]:
            if alg == hill_climbing_random_restart:
                sol, vst, deep, tm, fal = runAlgorithmm(alg, lst, lambda: randomNQueens(1, tsize).pop(0))
            else:
                sol, vst, deep, tm, fal = runAlgorithmm(alg, lst)
            sl = list()
            for s in sol:
                if checkSol.goal_test(s.state):
                    sl.append(s)
            printAllSolutions(alg, sl, vst, deep, tm, fal)