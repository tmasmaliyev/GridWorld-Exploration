import random
from collections import defaultdict

from .action import Action
from typing import Union, Tuple, List

class Agent:
    def __init__(
            self, 
            grid_size : Tuple[int, int] = (40, 40),
            # visited_limit : int = 5,
            lr : Union[int, float] = 0.01,
            gamma : Union[int, float] = 0.99,
            epsilon : Union[int, float] = 0.999, 
            epsilon_decay_rate : Union[int, float] = 0.9
    ) -> None:
        self.grid_size = grid_size
        # self.visited_limit = visited_limit
        self.actions = {
            Action.N : (0, 1) , 
            Action.S : (0, -1), 
            Action.W : (-1, 0), 
            Action.E : (1, 0)
        }

        self.q_table = defaultdict(lambda: 0)
        # self.visited = defaultdict(lambda: 0)

        self.lr = lr
        self.gamma = gamma

        self.epsilon = epsilon
        self._epsilon = epsilon
    
        self.epsilon_decay_rate = epsilon_decay_rate

    def anneal_epsilon(self, episode : int) -> None:
        self.epsilon = self._epsilon * (self.epsilon_decay_rate ** episode)


    def get_q(self, state : Tuple[int, int], action : Action):
        return self.q_table.get((state, action), 0)
    
    def _applicable_actions(self, state : Tuple[int, int]) -> List[Action]:
        actions = []
        x, y = state

        for action, (dx, dy) in self.actions.items():
            new_x = x + dx
            new_y = y + dy
            if (new_x < 0 or new_y < 0 or \
                new_x >= self.grid_size[0] or new_y >= self.grid_size[1]):
                continue
            
            actions.append(action)
        
        random.shuffle(actions)

        return actions

    def choose_action(self, state : Tuple[int, int]):
        available_actions = self._applicable_actions(state)

        if random.random() < self.epsilon:
            return random.choice(available_actions)
        
        q_values = [self.get_q(state, action) for action in available_actions]

        max_q_value_index = max(enumerate(q_values), key=lambda x: x[1])[0]

        return available_actions[max_q_value_index]

    def update(
            self, 
            state : Tuple[int, int], 
            action : Action, 
            reward : Union[int, float], 
            next_state : Tuple[int, int]
    ) -> None:
        # region Q - Learning -> Model free based (FIX: Adapt for general case)
        best_next_action = self.choose_action(next_state)

        old_q = self.get_q(state, action)
        next_q = self.get_q(next_state, best_next_action)

        new_q = old_q + self.lr * (reward + self.gamma * next_q - old_q)

        self.q_table[(state, action)] = new_q
        # self.visited[(state), action] += 1
        # endregion