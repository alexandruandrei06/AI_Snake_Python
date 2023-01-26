import pygame
import random
from menu import Menu
from manual_mode import ManualMode
from agent import Agent, train
from learning_mode import SnakeGameAI

if __name__ == '__main__':

    # initializing the game menu and selecting the game mode
    menu = Menu(640, 640)
    mode, level = menu.create_menu()

    if mode == None:
        running = False
    else:
        running = True

    agent_level_1 = Agent(1)
    game_level_1 = SnakeGameAI(1)

    agent_level_2 = Agent(2)
    game_level_2 = SnakeGameAI(2)

    print('Level', level)

    while running:
        if mode == 'MANUAL':
            manual_mode = ManualMode(640, 640, level)

            game_over = False
            score = 0
            while not game_over:
                game_over, score = manual_mode.play_step()

            manual_mode._update_screen_game_over()
            mode = 'MENU'
            print('Final Score', score)

        elif mode == 'LEARNING':
            print(mode)
            if level == 1:
                train(agent_level_1, game_level_1, 'LEARNING')
                mode = 'MENU'
            else:
                train(agent_level_2, game_level_2, 'LEARNING')
                mode = 'MENU'

        elif mode == 'AUTO':
            print(mode)
            if level == 1:
                train(agent_level_1, game_level_1, 'AUTO')
                mode = 'MENU'
            else:
                train(agent_level_2, game_level_2, 'AUTO')
                mode = 'MENU'

        elif mode == 'MENU':
            mode, level = menu.create_menu()

        elif mode == None:
            break
