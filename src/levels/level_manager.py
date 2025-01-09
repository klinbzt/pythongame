import json
from os.path import join
from pytmx.util_pygame import load_pygame  # type: ignore
from utils.settings import *
from planets.planet import Planet
from levels.level import Level

class LevelManager:
    def __init__(self, loaded_save_data):
        # General
        self.number_of_planets = 4
        self.root_path = None

        # Current Planet
        self.current_planet_index = loaded_save_data["current_planet_index"]
        self.current_planet = self.load_planet()

        # Current Level
        self.current_level_index = loaded_save_data["current_level_index"]
        self.current_level = self.load_level()

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
        config_path = join(self.root_path, self.current_planet.levels[self.current_level_index]["tmx_map"])

        level_data = {
            "planet": self.current_planet,
            "tmx_map": load_pygame(config_path),
            "permissions": self.current_planet.levels[self.current_level_index]["permissions"],
        }

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

    # Return the info of the current level
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

    def run(self, dt):
        """
        Run the current level, updating its logic with the given delta time.
        """
        if self.current_level:
            self.current_level.run(dt)