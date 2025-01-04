from utils.settings import *
from sprites.sprite import Sprite, MovingSprite
from entities.player import Player

class Level:
	def __init__(self, planet, tmx_map):
		self.planet = planet
		self.screen = pygame.display.get_surface()
		self.all_sprites = pygame.sprite.Group()
		self.collision_sprites = pygame.sprite.Group()

		self.setup(tmx_map)

	def setup(self, tmx_map):
		# Terrain (Tiles)
		try:
			terrain_layer = tmx_map.get_layer_by_name("Terrain")
			for pos_x, pos_y, surf in terrain_layer.tiles():
				Sprite((pos_x * TILE_SIZE, pos_y * TILE_SIZE), surf, (self.all_sprites, self.collision_sprites))
		except ValueError:
			print("Layer 'Terrain' not found.")

		# Moving Objects
		try:
			moving_objects_layer = tmx_map.get_layer_by_name("Moving Objects")
			for obj in moving_objects_layer:
				if obj.name == "moving_skel":
					# Moving on the x-axis
					if obj.width > obj.height:
						move_direction = "x"
						start_pos = (obj.x, obj.y + obj.height / 2)
						end_pos = (obj.x + obj.width, obj.y + obj.height / 2)
					# Moving on the y-axis
					else:
						move_direction = "y"
						start_pos = (obj.x + obj.width / 2, obj.y)
						end_pos = (obj.x + obj.width / 2, obj.y + obj.height)
					speed = obj.properties["speed"]

					MovingSprite((self.all_sprites, self.collision_sprites), start_pos, end_pos, move_direction, speed)
		except ValueError:
			print("Layer 'Moving Objects' not found.")
		
		# Objects
		try:
			objects_layer = tmx_map.get_layer_by_name("Objects")
			for obj in objects_layer:
				if obj.name == "player":
					Player((obj.x, obj.y), self.all_sprites, self.collision_sprites, self.planet)
		except ValueError:
			print("Layer 'Objects' not found.")

	def run(self, dt):
		self.screen.fill(BLACK)
		self.all_sprites.update(dt)
		self.all_sprites.draw(self.screen)