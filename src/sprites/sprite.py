from utils.settings import *

class Sprite(pygame.sprite.Sprite):
	def __init__(self, pos, surf, groups):
		super().__init__(groups)
		self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
		self.image.fill(WHITE)

		# Rects
		self.rect = self.image.get_rect(topleft = pos)
		self.prev_rect = self.rect.copy()