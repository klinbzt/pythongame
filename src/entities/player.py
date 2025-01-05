from utils.settings import *
from utils.timer import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites, planet, permissions):
        super().__init__(groups)

        # Rendering
        self.z = Z_LAYERS['main']
        self.base_image = image.load("../assets/graphics/tilesets/player.png")
        self.image = self.base_image

        # Rects
        self.rect = self.base_image.get_rect(topleft = pos)
        self.prev_rect = self.rect.copy()

        # Movements
        self.planet = planet
        self.direction = vector()
        self.speed = 200
        self.mass = 100
        
		# Jump
        self.jump_height = 275
        self.jump = False
        self.wall_jump_height_factor = 1.5

        # Dash
        self.last_direction = vector(1, 0)
        self.dash_speed = 600
        self.dashing = False

        # Mass manipulation - heavy
        self.heavy_mode = False
        self.a_key_pressed = False

        # Mass manipulation - light
        self.light_mode = False
        self.s_key_pressed = False

        # Collision handling
        self.collision_sprites = collision_sprites
        self.on_surface = {"ground": False, "left": False, "right": False}
        self.platform = None

        # Permissions
        self.permissions = permissions

        # Timers
        self.timers = {
            "wall jump": Timer(400),
            "wall slide block": Timer(250),
            "dash cooldown": Timer(1000),
            "dash duration": Timer(200)
        }

    # Handle input
    def handle_input(self):
        keys = pygame.key.get_pressed()
        input_vector = vector(0, 0)

        # Don't allow left and right input while the "wall jump" timer is active
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

        # Check jump permission
        if self.permissions.get("jump", False) and keys[pygame.K_SPACE]:
            self.jump = True

        # Trigger dash if permission allow it
        if self.permissions.get("dash", False) and keys[pygame.K_d] and not self.dashing and not self.timers["dash cooldown"].active:
            self.start_dash()

        # Trigger heavy mode if permissions allow it
        # Only toggle when the key is first pressed. Reset when the key is released
        if self.permissions.get("heavy_mode", False) and keys[pygame.K_a]:
            if not self.a_key_pressed and not self.light_mode: # One mass manipulation mode can be active at a time
                if not self.heavy_mode:
                    self.mass *= 2
                    self.heavy_mode = True
                else:
                    self.mass /= 2
                    self.heavy_mode = False
                self.a_key_pressed = True
        else:
            self.a_key_pressed = False
        
        # Trigger light mode if permissions allow it
        # Only toggle when the key is first pressed. Reset when the key is released
        if self.permissions.get("light_mode", False) and keys[pygame.K_s]:
            if not self.s_key_pressed and not self.heavy_mode: # One mass manipulation mode can be active at a time
                if not self.light_mode:
                    self.mass /= 2
                    self.light_mode = True
                else:
                    self.mass *= 2
                    self.light_mode = False
                self.s_key_pressed = True
        else:
            self.s_key_pressed = False

    # Setup dash timers and cancel other actions ( like the current jump, if jumping )
    def start_dash(self):
        self.dashing = True
        self.timers["dash duration"].activate()  # Start dash duration timer
        self.timers["dash cooldown"].activate()  # Start cooldown timer

        # Cancel any ongoing jump
        self.direction.y = 0
        self.jump = False

    # Handle any movement related action or ability the player might make
    def handle_player_movement(self, dt):
        if self.dashing:
            # Dash movement in the last known direction
            self.rect.x += self.last_direction.x * self.dash_speed * dt
            self.collision("x")

            # Stop dashing when the dash duration ends
            if not self.timers["dash duration"].active:
                self.dashing = False
                # self.base_image.fill("red")
        else:
            # Move and check for collision on x axis
            self.rect.x += self.direction.x * self.speed * dt
            self.collision("x")

            # Apply gravity or wall slide physics if conditions are met
            if not self.on_surface["ground"] and any((self.on_surface["left"], self.on_surface["right"])) and self.permissions.get("wall_slide", False) and not self.timers["wall slide block"].active:
                self.planet.apply_gravity_on_wall_slide(self, dt)
            else:
                self.planet.apply_gravity(self, dt)

            # Jump logic
            if self.jump:
                if self.on_surface["ground"]:
                    self.direction.y -= self.jump_height
                    self.timers["wall slide block"].activate()
                elif self.permissions.get("wall_jump", False) and any((self.on_surface["left"], self.on_surface["right"])) and not self.timers["wall slide block"].active:
                    # Wall jump logic
                    self.timers["wall jump"].activate()
                    self.direction.y -= self.wall_jump_height_factor * self.jump_height
                    if self.on_surface["left"]:
                        self.direction.x = 1
                    else:
                        self.direction.x = -1
                self.jump = False

            self.handle_platform_movement(dt)
            self.collision("y")

    # Make player move alongside the platform
    def handle_platform_movement(self, dt):
        if self.platform:
            self.rect.topleft += self.platform.direction * self.platform.speed * dt

    # Make the player face the direction he last moved towards
    def handle_orientation(self):
        if self.last_direction.x < 0:
            self.image = pygame.transform.flip(self.base_image, True, False)
        elif self.last_direction.x > 0:
            self.image = self.base_image

    # Check what the player is currently in contact with ( nothing, the ground, or walls ( left, right ))
    def check_contact(self):
        ground_rect = pygame.Rect(self.rect.bottomleft, (self.rect.width, 2))
        right_rect = pygame.Rect(self.rect.topright + vector(0, self.rect.height / 4), (2, self.rect.height / 2))
        left_rect = pygame.Rect((self.rect.topleft + vector(-2, self.rect.height / 4)), (2, self.rect.height / 2))

        collide_rects = [sprite.rect for sprite in self.collision_sprites]

        self.on_surface["ground"] = False
        self.on_surface["right"] = False
        self.on_surface["left"] = False

        # Track if the player is on a platform
        self.platform = None
        for sprite in [sprite for sprite in self.collision_sprites.sprites() if hasattr(sprite, "moving")]:
            if sprite.rect.colliderect(ground_rect):
                self.platform = sprite
                self.on_surface["ground"] = True

        # Ground detection for non-moving surfaces
        if self.platform is None and ground_rect.collidelist(collide_rects) >= 0:
            self.on_surface["ground"] = True

        # Check for wall collisions
        if right_rect.collidelist(collide_rects) >= 0:
            self.on_surface["right"] = True

        if left_rect.collidelist(collide_rects) >= 0:
            self.on_surface["left"] = True

    # Check collisions between player and anything else
    def collision(self, axis):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.rect):
                # Check collision on x axis
                if axis == "x":
                    # Left
                    if self.rect.left <= sprite.rect.right and int(self.prev_rect.left) >= int (sprite.prev_rect.right):
                        self.rect.left = sprite.rect.right

                    # Right
                    if self.rect.right >= sprite.rect.left and int(self.prev_rect.right) <= int(sprite.prev_rect.left):
                        self.rect.right = sprite.rect.left
                # Check collision on y axis
                else:
                    # Top
                    if self.rect.top <= sprite.rect.bottom and int(self.prev_rect.top) >= int(sprite.prev_rect.bottom):
                        self.rect.top = sprite.rect.bottom
                        # Offset the player
                        if hasattr(sprite, "moving"):
                            self.rect.top += 6

                    # Bottom
                    if self.rect.bottom >= sprite.rect.top and int(self.prev_rect.top) <= int (sprite.prev_rect.top):
                        self.rect.bottom = sprite.rect.top

                    self.direction.y = 0

    # Update state
    def update(self, dt):
        update_timers(self)
        self.prev_rect = self.rect.copy()
        self.handle_input()
        self.handle_orientation()
        self.handle_player_movement(dt)
        self.check_contact()
