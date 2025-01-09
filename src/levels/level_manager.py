import json
from os.path import join
from pytmx.util_pygame import load_pygame  # type: ignore
from utils.settings import *
from planets.planet import Planet
from levels.level import Level
#from ui.textbox import *

class LevelManager:
    def __init__(self, screen, clock):
        # General
        self.number_of_planets = 4
        self.root_path = None
        self.screen = screen
        self.clock = clock
        self.text_shown = False

        # Current Planet
        self.current_planet_index = 0
        self.current_planet = self.load_planet()

        # Current Level
        self.current_level_index = 0
        self.current_level = self.load_level()
        
        self.loadedsave = False
    def update_root_path(self):
        self.root_path = join("..", "levels", f"planet_{self.current_planet_index}")

    # Load planet data and return a Planet Instance
    def load_planet(self):
        self.update_root_path()

        config_path = join(self.root_path, "planet_config.json")

        with open(config_path, "r") as file:
            data = json.load(file)
        
        name = data["name"]
        gravity_strength = data["gravity_strength"]
        levels = data["levels"]

        # Create and return the Planet object
        return Planet(name, gravity_strength, levels)

    # Load level data and return a Level Instance
    def load_level(self):
        """
        Loads the current level and updates its parameters to match the saved or current game state.
        """
        print(f"Log: {self.current_level_index}")
        level_config = self.current_planet.levels[self.current_level_index]
        tmx_path = join(self.root_path, level_config["tmx_map"])

        level_data = {
            "planet": self.current_planet,
            "tmx_map": load_pygame(tmx_path),
            "permissions": level_config["permissions"],
        }

        # Update the current planet reference for consistency
        self.current_planet = level_data["planet"]
        
        print(f"Loaded level with {self.current_level_index}")
        # Return a new Level instance with the updated data
        return Level(level_data, self.callback)

    # Cleanup sprites of the previous level
    def cleanup_level(self):
        """
        Clear all resources associated with the current level.
        """
        if self.current_level:
            self.current_level.all_sprites.empty()
            self.current_level.collision_sprites.empty()

    # Callback for the next level
    def callback(self):
        """
        Handles progression to the next level or planet after completing a level.
        """
        # Clean up the resources of the level that was completed
        self.cleanup_level()

        # Move to the next level within the current planet
        if self.current_level_index < len(self.current_planet.levels) - 1:
            self.current_level_index += 1
        else:
            # Move to the next planet
            self.current_planet_index += 1

            if self.current_planet_index >= self.number_of_planets:
                print("Game Over!")
            else:
                # Load the next planet
                self.current_planet = self.load_planet()

            # Reset to the first level of the new planet
            self.current_level_index = 0

        # Load the next level
        self.current_level = self.load_level()

    def get_save_info(self):
        """
        Collect necessary information for saving the game.
        """
        if self.current_planet == None:
            return None
        save_info = {
            "current_planet_index": self.current_planet_index,
            "current_level_index": self.current_level_index,
            "planet_name": self.current_planet.name,
        }
        return save_info

    def load_save_info(self, save_info):
        """
        Update the planet and level information from the saved game data and return the loaded level.
        """
        if "current_planet_index" in save_info and "current_level_index" in save_info:
            # Update indices from save data
            self.current_planet_index = save_info["current_planet_index"]
            self.current_level_index = save_info["current_level_index"]
            # Debugging print statements
            print(f"Loaded save data: Planet Index = {self.current_planet_index}, Level Index = {self.current_level_index}")

            # Reload planet and level based on saved data
            self.current_planet = self.load_planet()  # Load planet based on saved index
            self.current_level = self.load_level()    # Load level based on saved index
        else:
            print("Invalid save data: 'current_planet_index' or 'current_level_index' missing.")
        return self.current_level  # Return the current level

    def run(self, dt):
        """
        Run the current level, updating its logic with the given delta time.
        """
        #if not self.text_shown:
        #    self.text_shown = True
        #    font = pygame.font.Font(None, 36)

        #    # Calculate box dimensions relative to the screen size
        #    box_width = SCREEN_WIDTH // 3  # e.g., 1/3 of the screen width
        #    box_height = SCREEN_HEIGHT // 4  # e.g., 1/4 of the screen height

        #    # Center the box on the screen
        #    box_position = ((SCREEN_WIDTH - box_width) // 2, (SCREEN_HEIGHT - box_height) // 2)

        #    # Create and display the text box
        #    text = TextBox(box_position, (box_width, box_height), self.screen, self.clock, "Bine ai venit în aplicația mea!", font=font, fade_time=2)
        #    text.run()

        if self.current_level:
            self.current_level.run(dt)