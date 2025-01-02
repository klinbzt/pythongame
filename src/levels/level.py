from utils.settings import *
from sprites.sprite import Sprite
from entities.player import Player

class Level:
	def __init__(self, tmx_map):
		self.screen = pygame.display.get_surface()
	
		self.all_sprites = pygame.sprite.Group()
		self.collision_sprites = pygame.sprite.Group()

		self.setup(tmx_map)

	def setup(self, tmx_map):
		for pos_x, pos_y, surf in tmx_map.get_layer_by_name("Terrain").tiles():
			Sprite((pos_x * TILE_SIZE, pos_y * TILE_SIZE), surf, (self.all_sprites, self.collision_sprites))

		for obj in tmx_map.get_layer_by_name("Objects"):
			if obj.name == "player":
				Player((obj.x, obj.y), self.all_sprites, self.collision_sprites)

	def run(self, dt):
		self.all_sprites.update(dt)
		self.screen.fill(BLACK)
		self.all_sprites.draw(self.screen)