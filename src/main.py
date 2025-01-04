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
            1: load_planet(join("..", "levels", "planet_one")),
            2: load_planet(join("..", "levels", "planet_two")),
            3: load_planet(join("..", "levels", "planet_three")),
        }

        # Define current level data
        self.current_level_index = 0
        self.current_planet_index = 1
        self.current_planet = self.planets[self.current_planet_index]

        # Issue! If the map doesn't load in time, the collisions aren't set up and the player falls off the map before it's loaded. Needs to be fixed asap

        # Create current level
        self.level = Level(
            self.current_planet,
            self.current_planet.get_level(self.current_level_index),
            self.next_level_callback
        )
    
    def next_level_callback(self):
        """Callback for transitioning to the next level or planet."""
        # Check if there's a next level on the current planet
        if self.current_level_index < len(self.current_planet.levels) - 1:
            # Move to the next level of the current planet
            self.current_level_index += 1
            self.level = Level(self.current_planet, self.current_planet.get_level(self.current_level_index), self.next_level_callback)
        else:
            # No more levels on the current planet, move to the next planet
            self.current_planet_index += 1

            # If we've run out of planets, end the game
            if self.current_planet_index >= len(self.planets):
                print("Game Over! You've completed all levels!")
                pygame.quit()
                sys.exit()

            # Reset to the first level of the new planet
            self.current_planet = self.planets[self.current_planet_index]
            self.current_level_index = 0
            self.level = Level(self.current_planet, self.current_planet.get_level(self.current_level_index), self.next_level_callback)
    
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