import json
from os.path import join
from pytmx.util_pygame import load_pygame  # type: ignore
from utils.settings import *
from planets.planet import Planet

def load_planet(planet_dir_path):
	config_path = join(planet_dir_path, "planet_config.json")

	with open(config_path, "r") as file:
		data = json.load(file)
	
	name = data["name"]
	gravity_strength = data["gravity_strength"]
	levels = [load_pygame(join(planet_dir_path, level)) for level in data["levels"]]
    
    # Create and return the Planet object
	return Planet(name, gravity_strength, levels)
