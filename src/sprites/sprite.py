from utils.settings import *

class Sprite(pygame.sprite.Sprite):
	def __init__(self, pos, surf = pygame.Surface((TILE_SIZE, TILE_SIZE)), groups = None, z = Z_LAYERS['main']):
		super().__init__(groups)
		self.image = surf
		# self.image.fill(WHITE)

		# Rects
		self.rect = self.image.get_rect(topleft = pos)
		self.prev_rect = self.rect.copy()
		self.z = z

class MovingSprite(Sprite):
	def __init__(self, groups, start_pos, end_pos, move_direction, speed):
		surf = pygame.Surface((192, 32))
		super().__init__(start_pos, surf, groups)
		self.image = image.load("../assets/graphics/tilesets/platforms.png")
		if move_direction == "x":
			self.rect.midleft = start_pos
		else:
			self.rect.midtop = start_pos
		self.start_pos = start_pos
		self.end_pos = end_pos

		# Movement
		self.moving = True
		self.speed = speed
		if move_direction == "x":
			self.direction = vector(1, 0)
		else:
			self.direction = vector(0, 1)
		self.move_direction = move_direction
	
	def check_bounds(self):
		# Keep platforms moving on the x axis in bounds
		if self.move_direction == "x":
			if self.rect.right >= self.end_pos[0] and self.direction.x == 1:
				self.direction.x = -1
				self.rect.right = self.end_pos[0]
			if self.rect.left <= self.start_pos[0] and self.direction.x == -1:
				self.direction.x = 1
				self.rect.left = self.start_pos[0]
		# Keep platforms moving on the y axis in bounds
		else:
			if self.rect.bottom >= self.end_pos[1] and self.direction.y == 1:
				self.direction.y = -1
				self.rect.bottom = self.end_pos[1]
			if self.rect.top <= self.start_pos[1] and self.direction.y == -1:
				self.direction.y = 1
				self.rect.top = self.start_pos[1]
	
	def update(self, dt):
		self.prev_rect = self.rect.copy()
		self.rect.topleft += self.direction * self.speed * dt
		self.check_bounds()