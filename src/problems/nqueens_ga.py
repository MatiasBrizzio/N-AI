from random import shuffle

from numpy import sort
from pyevolve import Consts, GSimpleGA, Selectors, Initializators, Util
from pyevolve import G1DList
from pyevolve import Mutators, Crossovers
from random import randint as rand_randint, uniform as rand_uniform, choice as rand_choice
import collections
collections.Callable = collections.abc.Callable
# Import standard modules
# Import other evolve modules


# The "n" in n-queens
BOARD_SIZE = 8

# The n-queens fitness function
def fitness(genome):
    """TODO-List refactor this method..0. to support genome's representation"""
    genomelist = genome.getInternalList()
    """Return number of conflicting queens for a given node"""
    num_conflicts = 0
    for (r1, c1) in enumerate(genomelist):
        for (r2, c2) in enumerate(genomelist):
            if (r1, c1) != (r2, c2):
                num_conflicts += conflict(r1, c1, r2, c2)

    num_conflicts = num_conflicts / 2
    maxNumOfConflicts = ((BOARD_SIZE * (BOARD_SIZE - 1)) / 2)
    res = maxNumOfConflicts - num_conflicts
    # print("board: {} number of conflicts: {} --- {}".format(genomelist, num_conflicts, res))
    return res


def conflict(row1, col1, row2, col2):
    """Would putting two queens in (row1, col1) and (row2, col2) conflict?"""
    return (row1 == row2 or  # same row
            col1 == col2 or  # same column
            row1 - col1 == row2 - col2 or  # same \ diagonal
            row1 + col1 == row2 + col2)  # same / diagonal


def queens_init(genome, **args):
    genome.genomeList = list(range(0, BOARD_SIZE))
    shuffle(genome.genomeList)
    # print(genome.genomeList)


def G1DListCrossoverTwoPoint(genome, **args):
    """ The G1DList crossover, Two Point

    .. warning:: You can't use this crossover method for lists with just one element.

    """
    sister = None
    brother = None
    gMom = args["mom"]
    gDad = args["dad"]

    if len(gMom) == 1:
        Util.raiseException("The 1D List have one element, can't use the Two Point Crossover method !", TypeError)

    cuts = [rand_randint(1, len(gMom) - 1), rand_randint(1, len(gMom) - 1)]
    print("cuts {}".format(cuts))
    if cuts[0] > cuts[1]:
        Util.listSwapElement(cuts, 0, 1)

    if args["count"] >= 1:
        sister = gMom.clone()
        sister.resetStats()
        sister[cuts[0]:cuts[1]] = gDad[cuts[0]:cuts[1]]

    if args["count"] == 2:
        brother = gDad.clone()
        brother.resetStats()
        brother[cuts[0]:cuts[1]] = gMom[cuts[0]:cuts[1]]

    print("father {} mother {} sister{} brother {}".format(gDad.genomeList, gMom.genomeList, sister.genomeList,
                                                           brother.genomeList))

    return (sister, brother)


def G1DListCrossoverSinglePoint(genome, **args):
    """ The crossover of G1DList, Single Point

    .. warning:: You can't use this crossover method for lists with just one element.

    """
    sister = None
    brother = None
    gMom = args["mom"]
    gDad = args["dad"]

    if len(gMom) == 1:
        Util.raiseException("The 1D List have one element, can't use the Single Point Crossover method !", TypeError)

    cut = rand_randint(1, len(gMom) - 1)

    if args["count"] >= 1:
        sister = gMom.clone()
        sister.resetStats()
        sister[cut:] = gDad[cut:]

    if args["count"] == 2:
        brother = gDad.clone()
        brother.resetStats()
        brother[cut:] = gMom[cut:]
    print("father {} mother {} sister{} brother {}".format(gDad.genomeList, gMom.genomeList, sister.genomeList,
                                                           brother.genomeList))

    return (sister, brother)


def run_main():
    """
        This Genetical algorithm follows the idea from:
        An Adaptive Genetic Algorithm for Solving N-Queens Problem, Sarkar and Nag
        this paper can be found on: https://arxiv.org/pdf/1802.02006.pdf

    """
    # create a initial genome representation it will a list of size BOARD_SIZE
    genome = G1DList.G1DList(BOARD_SIZE)

    # set internal params
    max_raw = ((BOARD_SIZE * (BOARD_SIZE - 1)) / 2)
    print(max_raw)
    genome.setParams(rangemin=0, rangemax=BOARD_SIZE)
    genome.setParams(bestrawscore=max_raw, roundDecimal=4)

    # Set the mutator operation, it will only swap one position...
    genome.mutator.set(Mutators.G1DListMutatorSwap)

    # set crossover function to use Order1 crossover function a known crossover function for GA's
    # The idea of this crossover algorithm can be found on:
    # http://www.dmi.unict.it/mpavone/nc-cs/materiale/moscato89.pdf
    genome.crossover.set(Crossovers.G1DListCrossoverOX)

    # Set fitness function
    genome.evaluator.set(fitness)

    # Set the initializator it will be used to generate the initial population
    genome.initializator.set(queens_init)

    # Create the GA with the genome set above
    ga = GSimpleGA.GSimpleGA(genome)

    ga.terminationCriteria.set(GSimpleGA.RawScoreCriteria)

    # Set the individual selector this selector will pick the best individual of
    # the population every time instead of pick a random one
    ga.selector.set(Selectors.GRankSelector)

    # ga.terminationCriteria.set(GSimpleGA.RawScoreCriteria)

    # Set Maximize the Evaluator Function
    ga.setMinimax(Consts.minimaxType["maximize"])

    # set GA population, generations
    popsize = [10000, 12000, 25000]
    generations = [[143, 125, 351], [453, 279, 170], [143, 382, 281]]

    # ga.setPopulationSize(30)
    # ga.setGenerations(250)

    # set mr and cr
    ga.setMutationRate(0.80)
    ga.setCrossoverRate(0.34)
    i = -1
    for psize in popsize:
        i += 1
        for generation in generations[i]:
            ga.setPopulationSize(psize)
            ga.setGenerations(generation)
            ga.currentGeneration = 0
            ga.evolve()
            best = ga.bestIndividual()

            solutions = list()
            if best.getRawScore() == max_raw:
                # print("Best {} Best individual score: {}".format(best.getInternalList(), best.getRawScore()))
                # print("Last population:")
                for chr in ga.getPopulation():
                    # print("chr {} score {} ".format(chr.genomeList, chr.getRawScore()))
                    if chr.getRawScore() == max_raw and chr not in solutions:
                        solutions.append(chr)
                print("population size: {} generations: {} solutions {}".format(psize, generation, len(solutions)))
            else:
                print("no solutions was found for population size: {} generations: {} solutions {}".format(psize, generation, len(solutions)))


if __name__ == "__main__":
    run_main()
