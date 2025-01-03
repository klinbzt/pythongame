from utils.settings import *
from utils.timer import Timer

# Movements so far: left, right, jump, wall sliding, wall jump, dash

# I was thinking of adding anything beyond left and right movement gradually, as levels become more complex
# E.g: Lvl.1: Just move in a straight line to the flag. Unlock jumping
# Lvl.2: You gotta jump on some platforms / over some walls to the flag. Unlock wall sliding and wall jump
# Lvl.3: Combine the above to reach the flag for a few levels
# Lvl.x: Unlock dashing etc...

# TODO: Add mass to the player ( first ) and other physical objects ( later, maybe ) and include it in the gravity calculation, so maybe we can add powerups like "BecomeHeavy" / "BecomeLight" idk...

class Player(pygame.sprite.Sprite):
	def __init__(self, pos, groups, collision_sprites, planet):
		super().__init__(groups)
		self.image = pygame.Surface((64, 64))
		self.image.fill("red")
		self.planet = planet

		# Rects
		self.rect = self.image.get_rect(topleft = pos)
		self.prev_rect = self.rect.copy()

		# Movements
		self.direction = vector()
		self.last_direction = vector(1, 0)
		self.speed = 200
		self.jump_height = 350
		self.jump = False

		# Dash
		self.dash_speed = 600
		self.dashing = False
		self.dash_cooldown = Timer(1000)
		self.dash_duration = Timer(200)

		# Collisions
		self.collision_sprites = collision_sprites
		self.on_surface = {"ground": False, "left": False, "right": False}

		# Timer
		self.timers = {
			"wall jump": Timer(200),
			"dash cooldown": Timer(1000),
			"dash duration": Timer(200)
		}

	def handle_input(self):
		keys = pygame.key.get_pressed()
		input_vector = vector(0, 0)

		# Don't allow other input while the "wall jump" timer is active
		if not self.timers["wall jump"].active:
			if keys[pygame.K_RIGHT]:
				input_vector.x += 1
			if keys[pygame.K_LEFT]:
				input_vector.x -= 1
			if input_vector:
				self.direction.x = input_vector.normalize().x
				self.last_direction = vector(self.direction.x, 0)  # Update last direction
			else:
				self.direction.x = 0
		
		if keys[pygame.K_SPACE]:
			self.jump = True

		 # Trigger dash if D is pressed and cooldown is over
		if keys[pygame.K_d] and not self.dashing and not self.timers["dash cooldown"].active:
			self.start_dash()

	def start_dash(self):
		"""Start the dash movement."""
		self.dashing = True
		self.image.fill("blue")
		self.timers["dash duration"].activate()  # Start dash duration timer
		self.timers["dash cooldown"].activate()  # Start cooldown timer

		# Cancel any ongoing jump
		self.direction.y = 0
		self.jump = False

	def handle_movement(self, dt):
		if self.dashing:
			# Dash movement in the last known direction
			self.rect.x += self.last_direction.x * self.dash_speed * dt
			self.collision("x")

			# Stop dashing when the dash duration ends
			if not self.timers["dash duration"].active:
				self.dashing = False
				self.image.fill("red")
		else:
			# Move and check for collision on x axis
			self.rect.x += self.direction.x * self.speed * dt
			self.collision("x")

			# Move and check for collision on y axis
			if not self.on_surface["ground"] and any((self.on_surface["left"], self.on_surface["right"])):
				self.planet.apply_sliding_gravity(self, dt)
			else:
				self.planet.apply_gravity(self, dt)

			# Jump if the conditions are met ( be on the ground )
			if self.jump:
				if self.on_surface["ground"]:
					self.direction.y -= self.jump_height
				elif any((self.on_surface["left"], self.on_surface["right"])):
					# If the player is on a wall, activate the "wall jump" timer. In this window of time, the player can jump off of the wall in the oposite direction
					self.timers["wall jump"].activate()
					self.direction.y -= self.jump_height
					if self.on_surface["left"]:
						self.direction.x = 1
					else:
						self.direction.x = -1
				self.jump = False
			
			self.collision("y")
	
	def check_contact(self):
		ground_rect = pygame.Rect(self.rect.bottomleft, (self.rect.width, 2))
		right_rect = pygame.Rect(self.rect.topright + vector(0, self.rect.height / 4), (2, self.rect.height / 2))
		left_rect = pygame.Rect((self.rect.topleft + vector(-2, self.rect.height / 4)), (2, self.rect.height / 2))

		collide_rects = [sprite.rect for sprite in self.collision_sprites]

		if ground_rect.collidelist(collide_rects) >= 0:
			self.on_surface["ground"] = True
		else:
			self.on_surface["ground"] = False
		
		if right_rect.collidelist(collide_rects) >= 0:
			self.on_surface["right"] = True
		else:
			self.on_surface["right"] = False

		if left_rect.collidelist(collide_rects) >= 0:
			self.on_surface["left"] = True
		else:
			self.on_surface["left"] = False
	
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

	def update_timers(self):
		for timer in self.timers.values():
			timer.update()

	def update(self, dt):
		self.prev_rect = self.rect.copy()
		self.update_timers()
		self.handle_input()
		self.handle_movement(dt)
		self.check_contact()
