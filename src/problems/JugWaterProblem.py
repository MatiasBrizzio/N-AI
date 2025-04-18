# src/problems/JugWaterProblem.py
from src.core.problem import Problem

class JugWaterProblem(Problem):
    def actions(self, state):
        movements = []
        if state is None:
            return movements
        a, b = state
        if a < 4:
            movements.append('fill a')
        if b < 3:
            movements.append('fill b')
        if a == 2:
            movements.append('pourA')
        if b == 2:
            movements.append('pourB')
        if a > 0:
            movements.append('emptyA')
        if b > 0:
            movements.append('emptyB')
        if a + b <= 4 and b > 0:
            movements.append('fromBtoA')
        if a + b >= 3 and a > 0:
            movements.append('fromAtoB')
        if a + b <= 4 and b > 0:
            movements.append('fromBtoA2')
        if a + b <= 3 and a > 0:
            movements.append('fromAtoB2')
        if a == 0 and b == 2:
            movements.append('pass2')
        if a == 2:
            movements.append('empty2')
        return movements

    def result(self, state, action):
        if state is None:
            return state
        a, b = state
        if action == 'fill a':
            return (4, b)
        elif action == 'fill b':
            return (a, 3)
        elif action == 'pourA':
            return (a - 2, b)
        elif action == 'pourB':
            return (a, b - 2)  # Fix: Corrected 'b-d' to 'b-2'
        elif action == 'emptyA':
            return (0, b)
        elif action == 'emptyB':
            return (a, 0)
        elif action == 'fromBtoA':
            return (4, b - (4 - a))  # Fix: Corrected syntax
        elif action == 'fromAtoB':
            return (a - (3 - b), 3)
        elif action == 'fromBtoA2':
            return (a + b, 0)
        elif action == 'fromAtoB2':
            return (0, a + b)
        elif action == 'pass2':
            return (2, 0)
        elif action == 'empty2':
            return (0, b)
        return state  # Fallback

    def goal_test(self, state):
        if state is None:
            return False
        a, b = state
        return a == 2