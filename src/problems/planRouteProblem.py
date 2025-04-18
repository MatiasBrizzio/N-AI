# src/problems/planRouteProblem.py
from src.core.problem import Problem

class PlanRouteProblem(Problem):
    def __init__(self, initial, goal, allowed, dimrow):
        self.dimrow = dimrow
        self.goal = goal
        self.allowed = allowed
        super().__init__(initial, goal)

    def actions(self, state):
        possible_actions = ['Forward', 'TurnLeft', 'TurnRight']
        x, y = state.get_location()
        orientation = state.get_orientation()
        if x == 1 and orientation == 'LEFT':
            possible_actions.remove('Forward')
        if y == 1 and orientation == 'DOWN':
            possible_actions.remove('Forward')
        if x == self.dimrow and orientation == 'RIGHT':
            possible_actions.remove('Forward')
        if y == self.dimrow and orientation == 'UP':
            possible_actions.remove('Forward')
        return possible_actions

    def result(self, state, action):
        x, y = state.get_location()
        proposed_loc = []
        if action == 'Forward':
            if state.get_orientation() == 'UP':
                proposed_loc = [x, y + 1]
            elif state.get_orientation() == 'DOWN':
                proposed_loc = [x, y - 1]
            elif state.get_orientation() == 'LEFT':
                proposed_loc = [x - 1, y]
            elif state.get_orientation() == 'RIGHT':
                proposed_loc = [x + 1, y]
            else:
                raise Exception('InvalidOrientation')
        elif action == 'TurnLeft':
            if state.get_orientation() == 'UP':
                state.set_orientation('LEFT')
            elif state.get_orientation() == 'DOWN':
                state.set_orientation('RIGHT')
            elif state.get_orientation() == 'LEFT':
                state.set_orientation('DOWN')
            elif state.get_orientation() == 'RIGHT':
                state.set_orientation('UP')
            else:
                raise Exception('InvalidOrientation')
        elif action == 'TurnRight':
            if state.get_orientation() == 'UP':
                state.set_orientation('RIGHT')
            elif state.get_orientation() == 'DOWN':
                state.set_orientation('LEFT')
            elif state.get_orientation() == 'LEFT':
                state.set_orientation('UP')
            elif state.get_orientation() == 'RIGHT':
                state.set_orientation('DOWN')
            else:
                raise Exception('InvalidOrientation')
        if proposed_loc in self.allowed:
            state.set_location(proposed_loc[0], proposed_loc[1])
        return state

    def goal_test(self, state):
        return state.get_location() == tuple(self.goal)

    def h(self, node):
        x1, y1 = node.state.get_location()
        x2, y2 = self.goal
        return abs(x2 - x1) + abs(y2 - y1)