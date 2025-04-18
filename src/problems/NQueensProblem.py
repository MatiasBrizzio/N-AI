from src.core.problem import Problem, Node

class NQueensProblem(Problem):
    def __init__(self, N, node=None):
        self.N = N
        if node is None:
            self.initial = tuple([-1] * N)
        else:
            self.initial = node
        super().__init__(self.initial)

    def actions(self, state):
        movements = []
        original_state = list(state)
        for col in range(self.N):
            for row in range(self.N):
                aux_state = list(original_state)
                if original_state[col] != row:
                    aux_state[col] = row
                    movements.append(tuple(aux_state))
        return movements

    def result(self, state, action):
        return action

    def conflicted(self, state, row, col):
        return any(self.conflict(row, col, state[c], c) for c in range(col))

    def conflict(self, row1, col1, row2, col2):
        return (row1 == row2 or
                col1 == col2 or
                row1 - col1 == row2 - col2 or
                row1 + col1 == row2 + col2)

    def goal_test(self, state):
        return not any(self.conflicted(state, state[col], col) for col in range(len(state)))

    def h(self, node):
        num_conflicts = 0
        for r1, c1 in enumerate(node.state):
            for r2, c2 in enumerate(node.state):
                if (r1, c1) != (r2, c2):
                    num_conflicts += self.conflict(r1, c1, r2, c2)
        return num_conflicts

    def value(self, state):
        max_conflicts = (self.N * (self.N - 1)) / 2
        return max_conflicts - (self.h(Node(state)) / 2)