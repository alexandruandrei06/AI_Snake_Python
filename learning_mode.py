import pygame
import random
from enum import Enum
import numpy as np
from collections import namedtuple
from time import sleep


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


BLOCK_SIZE = 20
SPEED = 300

Point = namedtuple('Point', 'x, y')

# Loading font
gameFont = pygame.font.Font('Font/eater.ttf', 30)
gameOverFont = pygame.font.Font('Font/eater.ttf', 50)

# Loading background image
game_background = pygame.image.load('Background/game_background.png')

# rgb colors
WHITE = (255, 255, 255)
RED = (255, 50, 50)
PURPLE = (255, 0, 255)
GREEN = (12, 135, 109)


class SnakeGameAI:

    def __init__(self, level, width=640, height=640):
        self.width = width
        self.height = height
        self.level = level

        # init screen
        self.screen = pygame.display.set_mode((self.width, self.height))

        self.clock = pygame.time.Clock()
        self.obstacles = []

        self.reset()

        self.button1 = gameFont.render('STOP', True, (255, 0, 0))
        self.button1X, self.button1Y = 550, 0

        self.button_width = 140
        self.button_height = 40

    def reset(self):
        # init game state
        self.direction = Direction.RIGHT

        self.head = Point(self.width / 2, self.height / 2)
        self.snake = [self.head,
                      Point(self.head.x - BLOCK_SIZE, self.head.y),
                      Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)]

        self.score = 0
        self.food = []
        self._place_food()
        self.obstacles = []
        if self.level == 2:
            self._place_obstacles()
        self.frame_iteration = 0

    # Place multiple deadly obstacles on random spots
    def _place_obstacles(self):
        for i in range(5):
            x = random.randint(0, (self.width - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            y = random.randint(0, (self.height - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            self.obstacles.append(Point(x, y))

    # Place food on a random spot
    def _place_food(self):
        if self.level == 1:
            x = 1
        else:
            if len(self.food):
                x = 1
            else:
                x = 4

        for i in range(x):
            x = random.randint(0, (self.width - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            y = random.randint(0, (self.height - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            self.food.append(Point(x, y))
            if Point(x, y) in self.snake or Point(x, y) in self.obstacles:
                self._place_food()

    def play_step(self, action, no_game, speed):
        self.frame_iteration += 1
        # 1. collect user input
        mouse = pygame.mouse.get_pos()
        mode = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.button1X <= mouse[0] <= self.button1X + self.button_width and \
                        self.button1Y <= mouse[1] <= self.button1Y + self.button_height:
                    mode = 'MENU'

        # 2. move
        self._move(action)  # update the head
        self.snake.insert(0, self.head)

        # 3. check if game over
        reward = 0
        game_over = False
        (obstacle, colision) = self.is_collision()
        if colision or self.frame_iteration > 100 * len(self.snake):
            game_over = True
            if obstacle:
                reward = -10
            else:
                reward = -10
            return reward, game_over, mode, self.score

        # 4. place new food or just move
        eat_ok = 0
        for i in range(len(self.food)):
            food = self.food[i]
            if self.head == food:
                self.food.pop(i)
                self.score += 1
                if self.level == 2:
                    reward = 15
                else:
                    reward = 10
                self._place_food()
                eat_ok = 1
                break

        if not eat_ok:
            self.snake.pop()

        # 5. update ui and clock
        self._update_ui(no_game)
        self.clock.tick(speed)
        # 6. return game over and score
        return reward, game_over, mode, self.score

    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # hits boundary
        if pt.x > self.width - BLOCK_SIZE or pt.x < 0 or pt.y > self.height - BLOCK_SIZE or pt.y < 0:
            return False, True
        # hits itself
        if pt in self.snake[1:]:
            return (False, True)

        if self.head in self.obstacles:
            return (True, True)

        return (False, False)

    def _update_ui(self, no_game):
        self.screen.blit(game_background, (0, 0))

        for pt in self.snake:
            pygame.draw.rect(self.screen, WHITE, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.screen, RED, pygame.Rect(pt.x + 2, pt.y + 2, 16, 16))

        # Draw food
        for food in self.food:
            pygame.draw.rect(self.screen, PURPLE, pygame.Rect(food.x, food.y, BLOCK_SIZE, BLOCK_SIZE))

        # Draw obstales
        for obstacle in self.obstacles:
            pygame.draw.rect(self.screen, GREEN, pygame.Rect(obstacle.x, obstacle.y, BLOCK_SIZE, BLOCK_SIZE))

        text = gameFont.render("Score: " + str(self.score), True, WHITE)
        self.screen.blit(text, [0, 0])

        text = gameFont.render("Game: " + str(no_game), True, WHITE)
        self.screen.blit(text, [0, 35])

        self.screen.blit(self.button1, (self.button1X, self.button1Y))

        pygame.display.flip()

    def update_screen_game_over(self):
        self.screen.blit(game_background, (0, 0))
        text = gameOverFont.render("Score: " + str(self.score), True, WHITE)
        self.screen.blit(text, [200, 250])
        pygame.display.flip()
        sleep(2.5)

    def _move(self, action):
        # [straight, right, left]

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx]  # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]  # right turn r -> d -> l -> u
        else:  # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]  # left turn r -> u -> l -> d

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)
