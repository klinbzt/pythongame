from utils.settings import *
from pytmx.util_pygame import load_pygame
from os.path import join
from levels.level import Level

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Shifting Realms")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.tmx_maps = {0: load_pygame(join("..", "levels", "planet_mock", "level_mock.tmx"))}

        self.level = Level(self.tmx_maps[0])
    
    def run(self):
        while True:
            dt = self.clock.tick() / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            self.level.run(dt)
            
            pygame.display.update()

if __name__ == "__main__":
    game = Game()
    game.run()