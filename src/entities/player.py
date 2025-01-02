from utils.settings import *
from physics.gravity import Gravity

class Player(pygame.sprite.Sprite, Gravity):
	def __init__(self, pos, groups, collision_sprites):
		super().__init__(groups)
		self.image = pygame.Surface((64, 64))
		self.image.fill("red")

		# Rects
		self.rect = self.image.get_rect(topleft = pos)
		self.prev_rect = self.rect.copy()

		# Physics
		self.gravity = 1300

		# Movements
		self.direction = vector()
		self.speed = 200
		self.jump = False
		self.jump_height = 800

		# Collisions
		self.collision_sprites = collision_sprites
		self.on_surface = {"ground": False, "left": False, "right": False}

	def handle_input(self):
		keys = pygame.key.get_pressed()
		input_vector = vector(0, 0)

		if keys[pygame.K_RIGHT]:
			input_vector.x += 1
		if keys[pygame.K_LEFT]:
			input_vector.x -= 1
		if input_vector:
			self.direction.x = input_vector.normalize().x
		else:
			self.direction.x = 0
		
		if keys[pygame.K_SPACE]:
			self.jump = True
	
	def handle_movement(self, dt):
		# Move and check for collision on x axis
		self.rect.x += self.direction.x * self.speed * dt
		self.collision("x")

		# Move and check for collision on y axis
		self.direction.y += self.gravity / 2 * dt
		self.rect.y += self.direction.y * dt
		self.direction.y += self.gravity / 2 * dt
		self.collision("y")

		if self.jump:
			self.check_contact()
			if self.on_surface["ground"]:
				self.direction.y -= self.jump_height
			self.jump = False
	
	def check_contact(self):
		ground_rect = pygame.Rect(self.rect.bottomleft, (self.rect.width, 2))
		collide_rects = [sprite.rect for sprite in self.collision_sprites]

		if ground_rect.collidelist(collide_rects) >= 0:
			self.on_surface["ground"] = True
		else:
			self.on_surface["ground"] = False
	
	def collision(self, axis):
		for sprite in self.collision_sprites:
			if sprite.rect.colliderect(self.rect):
				# Check collision on x axis
				if axis == "x":
					# Left
					if self.rect.left <= sprite.rect.right and self.prev_rect.left >= sprite.prev_rect.right:
						self.rect.left = sprite.rect.right

					# Right
					if self.rect.right >= sprite.rect.left and self.prev_rect.right <= sprite.prev_rect.left:
						self.rect.right = sprite.rect.left
				# Check collision on y axis
				else:
					# Top
					if self.rect.top <= sprite.rect.bottom and self.prev_rect.top >= sprite.prev_rect.bottom:
						self.rect.top = sprite.rect.bottom

					# Bottom
					if self.rect.bottom >= sprite.rect.top and self.prev_rect.top <= sprite.prev_rect.top:
						self.rect.bottom = sprite.rect.top
					
					self.direction.y = 0

	def update(self, dt):
		self.prev_rect = self.rect.copy()
		self.handle_input()
		self.handle_movement(dt)
