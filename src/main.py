from utils.settings import *
from levels.level_manager import LevelManager

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Shifting Realms")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        # Initialize the LevelLoader
        self.level_manager = LevelManager()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Run the current level
            self.level_manager.run(dt)

            pygame.display.update()

if __name__ == "__main__":
    game = Game()
    game.run()
