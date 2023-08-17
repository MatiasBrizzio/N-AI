import time
import timeout_decorator


@timeout_decorator.timeout(5, timeout_exception=TimeoutError)
def runA(algorithm, node, h):
    try:
        if h is not None:
            a, b, c = algorithm(node, h)
        else:
            a, b, c = algorithm(node)
    except TimeoutError:
        raise TimeoutError
    else:
        return a, b, c


def runAlgorithmm(algorithm, listt, h=None):
    nodes = list()
    numsVisited = list()
    deeps = list()
    times = list()
    faileds = 0
    for x in listt:
        try:
            start_time = time.time()
            if h is not None:
                node, numVisited, deep = runA(algorithm, x, h)
                nodes.append(node)
                numsVisited.append(numVisited)
                deeps.append(deep)
                times.append(time.time() - start_time)
            else:
                node, numVisited, deep = runA(algorithm, x, None)
                nodes.append(node)
                numsVisited.append(numVisited)
                deeps.append(deep)
                times.append(time.time() - start_time)
        except TimeoutError:
            faileds += 1
            continue
        else:
            continue

    return nodes, numsVisited, deeps, times, faileds


def printAllSolutions(alg, sol, vst, deep, tm, fal, h=None):
    print("For {} ".format(alg), end='')
    if h is not None:
        print(" With {}".format(h), end='')
    else:
        print("", end='')

    print(" Number of Solutions {} ".format(len(sol)), end='')
    if len(sol) != 0:
        print(" Avg visited nodes: {} ".format(sum(vst) / len(vst)), end='')
        print(" Avg deep rached: {} ".format(sum(deep) / len(deep)), end='')
        print(" Avg taken time: {} ".format(sum(tm) / len(tm)), end='')
    print(" Failed: {} ".format(fal), end='')
    print("")