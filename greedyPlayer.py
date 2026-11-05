from random import random, choice
from action import Action

ACTIONS = [None, Action.LEFT, Action.RIGHT]


class GreedyPlayer:
    def __init__(self, snake, eps, gamma=0.5):
        self.snake = snake
        self.eps = eps
        self.gamma = gamma

        self.action_values = {}
        self.eval_count = {}
        self.state = snake.save_state()

    def get_action(self):
        self.state = self.snake.save_state()

        random_value = random()
        explore = random_value < self.eps

        return self._random_action() if explore else self._greedy_action()

    def _value(self, state, action):
        return self.action_values.get((state, action), 0)

    def _greedy_action(self):
        max_action_ids = []
        max_action_value = max(self._value(self.state, action) for action in ACTIONS)

        for action in ACTIONS:
            if self._value(self.state, action) == max_action_value:
                max_action_ids.append(action)

        return choice(max_action_ids)

    def _random_action(self):
        return choice(ACTIONS)

    def reward(self, action, reward):
        next_state = self.snake.save_state()
        key = (self.state, action)

        self.eval_count[key] = self.eval_count.get(key, 0) + 1
        alpha = 1 / self.eval_count[key]

        best_next_value = max(self._value(next_state, a) for a in ACTIONS)
        target = reward + self.gamma * best_next_value

        self.action_values[key] = (1 - alpha) * self._value(self.state, action) + alpha * target
