import time

from src.problems.NQueensProblem import NQueensProblem
from src.utils.TimeoutRun import run_dpll, run_sat
from src.core.logic import *

BOARD_SIZE = 27

def at_most_one_q_row():
    clause = list()
    for i in range(1, BOARD_SIZE + 1):
        for j in range(1, BOARD_SIZE + 1):
            for k in range(j+1, BOARD_SIZE + 1):
                sij = expr(str('~')+str('S')+str(i)+str('_')+str(j))
                sik = expr(str('~')+str('S')+str(i)+str('_')+str(k))
                clause.append(expr(sij | sik))
    p = associate('&', clause)
    return p

def at_most_one_q_column():
    clause = list()
    for i in range(1, BOARD_SIZE + 1):
        for j in range(1, BOARD_SIZE + 1):
            for k in range(j+1, BOARD_SIZE + 1):
                sij = expr(str('~')+str('S')+str(j)+str('_')+str(i))
                sik = expr(str('~')+str('S')+str(k)+str('_')+str(i))
                clause.append(expr(sij | sik))
    p = associate('&', clause)
    return p


def diagonal_d1():
    clause = list()
    for d in list(reversed(range(1, BOARD_SIZE + 1))):
        for j in range(1, BOARD_SIZE + 1):
            for k in range(1, BOARD_SIZE + 1):
                if d - k <= 0 or d - k > BOARD_SIZE or j + k > BOARD_SIZE or j + k <= 0:
                    continue
                sij = expr(str('~')+str('S')+str(d)+str('_')+str(j))
                sik = expr(str('~')+str('S')+str(d-k)+str('_')+str(j+k))
                # print("SIJ {} SIK {}".format(sij, sik))
                clause.append(expr(sij | sik))
    p = associate('&', clause)
    # print(p)
    return p

def diagonal_m45():
    clause = list()
    for d in range(1, BOARD_SIZE + 1):
        for j in range(1, BOARD_SIZE + 1):
            for k in range(1, BOARD_SIZE + 1):
                if d + k <= 0 or d + k > BOARD_SIZE or j + k > BOARD_SIZE or j + k <= 0:
                    continue
                sij = expr(str('~')+str('S')+str(d)+str('_')+str(j))
                sik = expr(str('~')+str('S')+str(d+k)+str('_')+str(j+k))
                # print("SIJ {} SIK {}".format(sij, sik))
                clause.append(expr(sij | sik))
    p = associate('&', clause)
    # print(p)
    return p


def at_least():
    clause = list()
    c = list()

    for i in range(1, BOARD_SIZE + 1):
        for j in range(1, BOARD_SIZE + 1):
            sij = expr(str('S')+str(i)+str('_')+str(j))
            clause.append(expr(sij))
        c.append(associate('|', clause))
        clause.clear()
    p = associate('&', c)
    return p


if __name__ == '__main__':
    dpll_time_out = False
    for size in range(4, 15):
        BOARD_SIZE = size
        lst = list()
        lst.append(at_most_one_q_row())
        lst.append(at_most_one_q_column())
        lst.append(diagonal_m45())
        lst.append(diagonal_d1())
        lst.append(at_least())
        lst = list(filter(lambda x : x != True, lst))
        x = lst.copy()
        res = associate('&', x)
        # print(res)
        if not dpll_time_out:
            st = time.time()
            model = list()
            found = False
            try:
                found = run_dpll(dpll_satisfiable, res)
                if not isinstance(found, bool):
                    for k in found.keys():
                        if found[k]: model.append(k)
                else:
                    print("With board size: {} no solution was found".format(BOARD_SIZE))
            except TimeoutError:
                print('for size: {} with dpll time out'.format(BOARD_SIZE))
                dpll_time_out = True
            else:
                if not isinstance(found,bool): print('for size: {} with dpll time: {} model {}'.format(BOARD_SIZE, time.time() - st, model))

        clauses = conjuncts(to_cnf(res))
        symbols = list(prop_symbols(res))
        f = open("example.cnf", "w+")
        f.write("p cnf {} {}\n".format(len(symbols), len(clauses)))
        for cl in clauses:
            for lit in disjuncts(cl):
                sym, positive = inspect_literal(lit)
                if positive:
                    f.write("{} ".format(symbols.index(sym)+1))
                else:
                    f.write("-{} ".format(symbols.index(sym)+1))
            f.write("0 \n")
        f.close()
        st = time.time()
        try:
            # tm = runSAT(subprocess.call, ["./aalta", "example.cnf", "tests.out"])
            tm = run_sat()
        except TimeoutError:
            print("for size {} minisat timeout".format(BOARD_SIZE))
        else:
            import os
            print("Current Working Directory:", os.getcwd())
            print("Trying to open:", os.path.abspath("tests.out"))  # Changed from ../../tests.out
            f = open("tests.out", "r")
            f1 = f.readlines()
            res = list()
            st = ""
            for x in f1:
                if x.find("SAT") != -1 or x.find("UNSAT") != -1:
                    continue
                else:
                    b = x.split(" ")
                    a = filter(lambda k: int(k) > 0, b)
                    print("For size {} with minisat time taken {} model: ".format(BOARD_SIZE, tm), end='')
                    for u in a:
                        res.append(u)
                        st = st + " " + str(symbols[int(u) - 1])
                        print("{} ".format(symbols[int(u) - 1]), end='')
                    print()

            # Create NQUEENSPROBLEM
            st = (st.replace("S", "")).split(" ")
            st1 = ""
            result = BOARD_SIZE * [0]
            for x in st:
                x1 = x.split("_")
                if x1 == ['']: continue
                result[int(x1[0]) - 1] = int(x1[1]) -1

            res2 = tuple(result)
            print(res2)
            x1 = NQueensProblem(BOARD_SIZE, res2)
            r1 = NQueensProblem(BOARD_SIZE).goal_test(x1.initial)
            if not r1: print("With board size: {} no solution was found".format(BOARD_SIZE))

        print()