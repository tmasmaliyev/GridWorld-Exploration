import random

from .action import Action
from typing import Optional, Union

class Agent:
    def __init__(
            self, 
            lr : Union[int, float] = 0.01,
            gamma : Union[int, float] = 0.99,
            epsilon : Union[int, float] = 0.1,
    ) -> None:
        self.q_table = {}
        self.actions = [Action.N, Action.S, Action.W, Action.E]

        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon

    def get_q(self, state, action : Action):
        return self.q_table.get((state, action), 0.0)

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        
        q_values = [self.get_q(state, action) for action in self.actions]
        max_q_value_index = max(enumerate(q_values), key=lambda x: x[1])[0][0]

        return self.actions[max_q_value_index]

    def update(self, state, action : Action, reward, next_state) -> None:
        # region Q - Learning -> Model free based (FIX: Adapt for general case)
        best_next_action = self.choose_action(next_state)

        old_q = self.get_q(state, action)
        next_q = self.get_q(next_state, best_next_action)

        new_q = old_q + self.lr * (reward + self.gamma * next_q - old_q)

        self.q_table[(state, action)] = new_q
        # endregion