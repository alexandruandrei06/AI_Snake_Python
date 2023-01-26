import pygame
from collections import namedtuple
from enum import Enum
import random
from time import sleep


Point = namedtuple('Point', 'x, y')

# Loading font
gameFont = pygame.font.Font('Font/eater.ttf', 30)
gameOverFont = pygame.font.Font('Font/eater.ttf', 50)

# Loading background image
game_background = pygame.image.load('Background/game_background.png')

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

BLOCK_SIZE = 20
SPEED = 25

# rgb colors
WHITE = (255, 255, 255)
RED = (255,50,50)
PURPLE = (255, 0, 255)
GREEN = (12, 135, 109)


class ManualMode:

    def __init__(self, width, height, level):
        # Set width & height
        self.width = width
        self.height = height

        # init screen
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()

        # init game state
        self.direction = Direction.RIGHT
        self.head = Point(self.width / 2, self.height / 2)

        self.level = level

        self.snake = [self.head,
                      Point(self.head.x - BLOCK_SIZE, self.head.y),
                      Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)]

        self.score = 0
        self.food = []
        self.obstacles = []
        self._place_food()
        if self.level == 2:
            self._place_obstacles()

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
            if Point(x, y) in self.snake:
                self._place_food()

    # Place multiple deadly obstacles on random spots
    def _place_obstacles(self):
        for i in range(10):
            x = random.randint(0, (self.width - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            y = random.randint(0, (self.height - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            self.obstacles.append(Point(x, y))

    def play_step(self):

        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                    self.direction = Direction.LEFT
                    break
                elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                    self.direction = Direction.RIGHT
                    break
                elif event.key == pygame.K_UP and self.direction != Direction.DOWN:
                    self.direction = Direction.UP
                    break
                elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                    self.direction = Direction.DOWN
                    break

        # 2. move
        self._move(self.direction)  # update the head
        self.snake.insert(0, self.head)

        # 3. check if game over
        game_over = False
        if self._is_collision():
            game_over = True
            return game_over, self.score

        # 4. place new food or just move
        eat_ok = 0
        for i in range(len(self.food)):
            food = self.food[i]
            if self.head == food:
                self.food.pop(i)
                self.score += 1
                self._place_food()
                eat_ok = 1
                break

        if not eat_ok:
            self.snake.pop()

        # 5. update ui and clock
        self._update_screen()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return game_over, self.score

    # Check collision with the boundary or itself
    def _is_collision(self):
        # hits boundary
        if self.head.x > self.width - BLOCK_SIZE or \
                self.head.x < 0 or \
                self.head.y > self.height - BLOCK_SIZE or \
                self.head.y < 0:
            return True
        # hits itself
        if self.head in self.snake[1:]:
            return True

        if self.head in self.obstacles:
            return True

        return False

    # Draw scene
    def _update_screen(self):
        self.screen.blit(game_background, (0, 0))

        # Draw snake
        for pt in self.snake:
            pygame.draw.rect(self.screen, WHITE, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.screen, RED, pygame.Rect(pt.x + 2, pt.y + 2, 16, 16))

        # Draw food
        for food in self.food:
            pygame.draw.rect(self.screen, PURPLE, pygame.Rect(food.x, food.y, BLOCK_SIZE, BLOCK_SIZE))

        #Draw obstales
        for obstacle in self.obstacles:
            pygame.draw.rect(self.screen, GREEN, pygame.Rect(obstacle.x, obstacle.y, BLOCK_SIZE, BLOCK_SIZE))

        # Draw live score
        text = gameFont.render("Score: " + str(self.score), True, WHITE)
        self.screen.blit(text, [0, 0])
        pygame.display.flip()

    # Draw scene after game over
    def _update_screen_game_over(self):
        self.screen.blit(game_background, (0, 0))
        text = gameOverFont.render("Score: " + str(self.score), True, WHITE)
        self.screen.blit(text, [200, 250])
        pygame.display.flip()
        sleep(2.5)

    # Move head of the snake
    def _move(self, direction):
        x = self.head.x
        y = self.head.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE

        self.direction = direction
        self.head = Point(x, y)