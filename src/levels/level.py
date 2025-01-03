from utils.settings import *
from sprites.sprite import Sprite
from entities.player import Player

class Level:
	def __init__(self, planet, tmx_map):
		self.planet = planet
		self.screen = pygame.display.get_surface()
		self.all_sprites = pygame.sprite.Group()
		self.collision_sprites = pygame.sprite.Group()

		self.setup(tmx_map)

	def setup(self, tmx_map):
		for pos_x, pos_y, surf in tmx_map.get_layer_by_name("Terrain").tiles():
			Sprite((pos_x * TILE_SIZE, pos_y * TILE_SIZE), surf, (self.all_sprites, self.collision_sprites))

		for obj in tmx_map.get_layer_by_name("Objects"):
			if obj.name == "player":
				# Change with obj.x, obj.y. This is only a temporary fix for the problem highlighted in main.py
				Player((250, -350), self.all_sprites, self.collision_sprites, self.planet)

	def run(self, dt):
		self.screen.fill(BLACK)
		self.all_sprites.update(dt)
		self.all_sprites.draw(self.screen)