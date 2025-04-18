from src.core.problem import Problem
import math

class EightPuzzle(Problem):
    """ The problem of sliding tiles numbered from 1 to 8 on a 3x3 board,
    where one of the squares is a blank. A state is represented as a tuple of length 9,
    where element at index i represents the tile number  at index i (0 if it's an empty square) """

    def __init__(self, initial, n, goal):
        """ Define goal state and initialize a problem """
        self.N = n
        self.goal = goal
        Problem.__init__(self, initial, goal)

    def find_blank_square(self, state):
        """Return the index of the blank square in a given state"""

        return state.index(0)


    def actions(self, state):
        """ Return the actions that can be executed in the given state.
        The result would be a list, since there are only four possible actions
        in any given state of the environment """

        possible_actions = ['UP', 'DOWN', 'LEFT', 'RIGHT']
        index_blank_square = self.find_blank_square(state)

        if index_blank_square % self.N == 0:
            possible_actions.remove('LEFT')
        if index_blank_square < self.N:
            possible_actions.remove('UP')
        if index_blank_square % self.N == (self.N - 1):
            possible_actions.remove('RIGHT')
        if index_blank_square > self.N * (self.N - 1) - 1:
            possible_actions.remove('DOWN')

        return possible_actions

    def result(self, state, action):
        """ Given state and action, return a new state that is the result of the action.
        Action is assumed to be a valid action in the state """

        # blank is the index of the blank square
        blank = self.find_blank_square(state)
        new_state = list(state)

        delta = {'UP':-self.N, 'DOWN':self.N, 'LEFT':-1, 'RIGHT':1}
        neighbor = blank + delta[action]
        new_state[blank], new_state[neighbor] = new_state[neighbor], new_state[blank]

        return tuple(new_state)

    def goal_test(self, state):
        """ Given a state, return True if state is a goal state or False, otherwise """

        return state == self.goal

    def check_solvability(self, state):
        """ Checks if the given state is solvable """
        inversion = 0
        for i in range(len(state)):
            for j in range(i+1, len(state)):
                if (state[i] > state[j]) and state[i] != 0 and state[j]!= 0:
                    inversion += 1

        return inversion % 2 == 0
    """
        all heuristics functions for eight puzzle problem
    """
    def linear(self, node):
        return sum([1 if node.state[i] != self.goal[i] else 0 for i in range(8)])

    def manhattan(self, node):
        state = node.state
        index_goal = {0: [2, 2], 1: [0, 0], 2: [0, 1], 3: [0, 2], 4: [1, 0], 5: [1, 1], 6: [1, 2], 7: [2, 0], 8: [2, 1]}
        index_state = {}
        index = [[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]]
        x, y = 0, 0

        for i in range(len(state)):
            index_state[state[i]] = index[i]

        mhd = 0

        for i in range(8):
            for j in range(2):
                mhd = abs(index_goal[i][j] - index_state[i][j]) + mhd

        return mhd


    def sqrt_manhattan(self, node):
        state = node.state
        index_goal = {0: [2, 2], 1: [0, 0], 2: [0, 1], 3: [0, 2], 4: [1, 0], 5: [1, 1], 6: [1, 2], 7: [2, 0], 8: [2, 1]}
        index_state = {}
        index = [[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]]
        x, y = 0, 0

        for i in range(len(state)):
            index_state[state[i]] = index[i]

        mhd = 0

        for i in range(8):
            for j in range(2):
                mhd = (index_goal[i][j] - index_state[i][j]) ** 2 + mhd

        return math.sqrt(mhd)

    def max_heuristic(self, node):
        score1 = self.manhattan(node)
        score2 = self.linear(node)
        return max(score1, score2)

    def gaschnig(self, node):
        res = 0
        state = list(node.state)
        solved = list(range(1,len(node.state)))
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

    def h(self, node):
        """ Return the heuristic value for a given state. Default heuristic function used is
        h(n) = number of misplaced tiles """
        return sum(s != g for (s, g) in zip(node.state, self.goal))
# ______________________________________________________________________________