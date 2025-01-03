from utils.settings import *
from os.path import join
from utils.helpers import *
from planets.planet import Planet
from levels.level import Level

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Shifting Realms")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        # Define planets with specific gravity
        self.planets = {
            0: load_planet(join("..", "levels", "planet_mock")),
            1: load_planet(join("..", "levels", "planet_one")),
            2: load_planet(join("..", "levels", "planet_two")),
            3: load_planet(join("..", "levels", "planet_three")),
        }

        # Define current level data
        self.current_planet = self.planets[0]
        self.current_tmx_map = 0

        # Issue! If the map doesn't load in time, the collisions aren't set up and the player falls off the map before it's loaded. Needs to be fixed asap

        # Create current level
        self.level = Level(self.current_planet, self.current_planet.get_tmx_map(0))
    
    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            # Run current level
            self.level.run(dt)
            
            pygame.display.update()

if __name__ == "__main__":
    game = Game()
    game.run()