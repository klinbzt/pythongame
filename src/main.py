import sys
import pygame
from game_engine.engine import GameEngine
from game_engine.startup import StartupScreen 
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, sheets

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Shifting Realms")

    # Mai intai punem un ecran de start-up, apoi activam engine-ul propriu-zis.
    startupscreen = StartupScreen(screen, sheets) # sheets se afla in settings... (ar fii o idee sa-l punem altundeva :p)
    startupscreen.run()

    # Start la engine-ul jocului
    engine = GameEngine(screen)
    engine.run()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        pygame.quit()
        sys.exit()