import time
import timeout_decorator
import subprocess
import os

@timeout_decorator.timeout(5, timeout_exception=TimeoutError)
def run_a(algorithm, node, h):
    try:
        if h is not None:
            a, b, c = algorithm(node, h)
        else:
            a, b, c = algorithm(node)
    except TimeoutError:
        raise TimeoutError
    else:
        return a, b, c


def run_algorithm(algorithm, _list, h=None):
    nodes = list()
    nums_visited = list()
    deeps = list()
    times = list()
    failed = 0
    for x in _list:
        try:
            start_time = time.time()
            if h is not None:
                node, num_visited, deep = run_a(algorithm, x, h)
                nodes.append(node)
                nums_visited.append(num_visited)
                deeps.append(deep)
                times.append(time.time() - start_time)
            else:
                node, num_visited, deep = run_a(algorithm, x, None)
                nodes.append(node)
                nums_visited.append(num_visited)
                deeps.append(deep)
                times.append(time.time() - start_time)
        except TimeoutError:
            failed += 1
            continue
        else:
            continue

    return nodes, nums_visited, deeps, times, failed


def print_all_solutions(alg, sol, vst, deep, tm, fal, h=None):
    print("For {} ".format(alg), end='')
    if h is not None:
        print(" With {}".format(h), end='')
    else:
        print("", end='')

    print(" Number of Solutions {} ".format(len(sol)), end='')
    if len(sol) != 0:
        print(" Avg visited nodes: {} ".format(sum(vst) / len(vst)), end='')
        print(" Avg deep reached: {} ".format(sum(deep) / len(deep)), end='')
        print(" Avg taken time: {} ".format(sum(tm) / len(tm)), end='')
    print(" Failed: {} ".format(fal), end='')
    print("")


@timeout_decorator.timeout(20, timeout_exception=TimeoutError)
def run_dpll(algorithm, s):
    try:
        a = algorithm(s)
    except TimeoutError:
        raise TimeoutError
    else:
        return a


@timeout_decorator.timeout(20, timeout_exception=TimeoutError)
def run_command():
    with open(os.devnull, 'w') as devnull:
        subprocess.call(["external/minisat", "example.cnf", "tests.out"], stdout=devnull, stderr=devnull)

def run_sat():
    try:
        start_time = time.time()
        run_command()
        end_time = time.time()
        time_taken = end_time - start_time
    except TimeoutError:
        raise TimeoutError
    else:
        return time_taken