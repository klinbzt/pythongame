from utils.settings import *
from levels.level_manager import LevelManager
from ui.startup import StartupScreen
from ui.savegame import SaveGame

class Game:
    def __init__(self):
        pygame.init()

        # Rendering
        pygame.display.set_caption("Shifting Realms")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Initialize the Clock
        self.clock = pygame.time.Clock()

        # Initialize the LevelManager
        self.level_manager = LevelManager(self.screen, self.clock)

        # Initialize the StartupScreen and the SaveGame screen
        self.startup_screen = StartupScreen(self.level_manager, self.clock)
        self.save_game = SaveGame(self.clock)

    def run(self):

        self.startup_screen.run()

        while True:
            dt = self.clock.tick(FPS)/1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: 
                        if self.save_game.run(self.screen, self.level_manager.get_save_info()) == False:
                            pygame.quit()
                            sys.exit()


            self.level_manager.run(dt)

            pygame.display.update()


if __name__ == "__main__":
    game = Game()
    game.run()