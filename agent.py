import random
from collections import deque
from collections import namedtuple
import numpy as np
import torch

from learning_mode import Direction, Point
from model import Linear_QNet, QTrainer

MAX_MEMORY = 100_000
BATCH_SIZE = 15000
LR = 0.001

class Agent:

    def __init__(self, level):
        self.no_games = 0  # Number of games
        self.epsilon = 0  # Randomness
        self.gamma = 0.9  # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)  # popleft()
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        self.record = 0
        self.level = level

    def euclideanDistance(self, A, B):
        return pow(pow(A.x - B.x, 2) + pow(A.y - B.y, 2), .5)

    def closest_food(self, game):
        min_dist = self.euclideanDistance(game.head, game.food[0])
        idx = 0
        for i in range(1, len(game.food)):
            min_dist_new = self.euclideanDistance(game.head, game.food[i])
            if(min_dist_new < min_dist):
                idx = i

        return game.food[idx]

    def get_state(self, game):
        head = game.snake[0]
        point_l = Point(head.x - 20, head.y)
        point_r = Point(head.x + 20, head.y)
        point_u = Point(head.x, head.y - 20)
        point_d = Point(head.x, head.y + 20)

        # dir = (game.direction == Direction.LEFT)
        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        food = self.closest_food(game)

        state = [
            # Danger straight
            (dir_r and game.is_collision(point_r)[1]) or
            (dir_l and game.is_collision(point_l)[1]) or
            (dir_u and game.is_collision(point_u)[1]) or
            (dir_d and game.is_collision(point_d)[1]),

            # Danger right
            (dir_u and game.is_collision(point_r)[1]) or
            (dir_d and game.is_collision(point_l)[1]) or
            (dir_l and game.is_collision(point_u)[1]) or
            (dir_r and game.is_collision(point_d)[1]),

            # Danger left
            (dir_d and game.is_collision(point_r)[1]) or
            (dir_u and game.is_collision(point_l)[1]) or
            (dir_r and game.is_collision(point_u)[1]) or
            (dir_l and game.is_collision(point_d)[1]),

            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,

            # Food location
            food.x < game.head.x,  # food left
            food.x > game.head.x,  # food right
            food.y < game.head.y,  # food up
            food.y > game.head.y  # food down
        ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))  # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if self.level == 1:
            BATCH_SIZE = 1000
        else:
            BATCH_SIZE = 15000

        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)  # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        if self.level == 1:
            eps = 80
        else:
            eps = 100

        self.epsilon = eps - self.no_games
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move


def train(agent, game, play_mode):
    mode = None

    while mode == None:
        # get old state
        state_old = agent.get_state(game)

        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        if play_mode == 'AUTO':
            reward, done, mode, score = game.play_step(final_move, agent.no_games, 25)
        else:
            reward, done, mode, score = game.play_step(final_move, agent.no_games, 250)

        state_new = agent.get_state(game)

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            # train long memory
            if play_mode == 'AUTO':
                game.update_screen_game_over()

            game.reset()
            agent.no_games += 1
            agent.train_long_memory()

            if score > agent.record:
                agent.record = score

            print('Game', agent.no_games, 'Score', score, 'Record:', agent.record)

            if play_mode == 'AUTO':
                return
