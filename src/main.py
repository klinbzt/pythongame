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

        # Initialize the LevelLoader
        self.level_manager = LevelManager()
        self.startup_screen = StartupScreen(self.level_manager, self.clock)
        self.save_game = SaveGame(self.clock)

        # Initialize saved data from a loaded game, if option is chosen
        self.loaded_save_data = self.startup_screen.run()
        if not self.loaded_save_data:
            self.loaded_save_data = {
                "current_planet_index": 0,
                "current_level_index": 0,
                "planet_name": "Tutorial"
            }
        
        self.level_manager = LevelManager(self.loaded_save_data)

    def run(self):
        while True:
            dt = self.clock.tick(FPS)/1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.save_game.run(self.screen, self.level_manager.get_save_info()) == False:
                        pygame.quit()
                        sys.exit()

            self.level_manager.run(dt)

            pygame.display.update()


if __name__ == "__main__":
    game = Game()
    game.run()
