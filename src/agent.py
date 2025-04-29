import random
from collections import defaultdict

from .action import Action
from typing import Union, Tuple, List

class Agent:
    def __init__(
            self, 
            grid_size : Tuple[int, int] = (40, 40),
            lr : Union[int, float] = 0.01,
            gamma : Union[int, float] = 0.99,
            epsilon : Union[int, float] = 0.999, 
            move_penalty : Union[int, float] = -0.1,
            epsilon_decay_rate : Union[int, float] = 0.9,
            move_penalty_decay_rate : Union[int, float] = 1.1
    ) -> None:
        self.grid_size = grid_size

        self.actions = {
            Action.N : (0, 1) , 
            Action.S : (0, -1), 
            Action.W : (-1, 0), 
            Action.E : (1, 0)
        }

        self.q_table = defaultdict(lambda: 0)
        self.visited = defaultdict(lambda: 0)

        self.lr = lr
        self.gamma = gamma

        self.epsilon = epsilon
        self._epsilon = epsilon

        self.move_penalty = move_penalty
        self._move_penalty = move_penalty
    
        self.epsilon_decay_rate = epsilon_decay_rate
        self._move_penalty_decay_rate = move_penalty_decay_rate

    def anneal_epsilon(self, episode : int) -> None:
        self.epsilon = self._epsilon * (self.epsilon_decay_rate ** episode)
    
    def anneal_penalty(self, episode : int) -> None:
        self.move_penalty = self._move_penalty * (self._move_penalty_decay_rate ** episode)

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

        return actions
    
    def _explore_based_actions(self, state : Tuple[int, int]) -> List[Action]:
        unvisited_actions = []
        x, y = state

        for action, (dx, dy) in self.actions.items():
            new_x = x + dx
            new_y = y + dy

            if (new_x < 0 or new_y < 0 or \
                new_x >= self.grid_size[0] or new_y >= self.grid_size[1] or \
                self.visited[(new_x, new_y)] != 0
            ):
                continue
            
            unvisited_actions.append(action)

        return unvisited_actions

    def choose_action(self, state : Tuple[int, int]):
        available_actions = self._applicable_actions(state)

        if random.random() < self.epsilon:
            unvisited_actions = self._explore_based_actions(state)

            if unvisited_actions:
                return random.choice(unvisited_actions)

            return random.choice(available_actions)
        
        q_values = [self.get_q(state, action) for action in available_actions]

        max_q_value_index = max(enumerate(q_values), key=lambda x: x[1])[0]

        return available_actions[max_q_value_index]

    def update(
            self, 
            state : Tuple[int, int], 
            action : Action, 
            reward : Union[int, float], 
            next_state : Tuple[int, int],
    ) -> None:
        # region Q - Learning -> Model free based (FIX: Adapt for general case)
        best_next_action = self.choose_action(next_state)

        old_q = self.get_q(state, action)
        next_q = self.get_q(next_state, best_next_action)

        new_q = old_q + self.lr * (reward + self.gamma * next_q - old_q)

        self.q_table[(state, action)] = new_q
        self.visited[state] += 1
        # endregion
    
    def reset_visited_state(self) -> None:
        self.visited = defaultdict(lambda: 0)