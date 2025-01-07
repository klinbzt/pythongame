from utils.settings import *
from utils.timer import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites, planet, permissions, notify_level_callback):
        super().__init__(groups)

        # Rendering
        self.z = Z_LAYERS['main']
        self.base_image = image.load("../assets/graphics/tilesets/player.png")
        self.image = self.base_image

        self.notify_level = notify_level_callback

        # Rects
        self.rect = self.base_image.get_rect(topleft = pos)
        self.hitbox_rect = self.rect.inflate(-40, -8)
        self.prev_rect = self.hitbox_rect.copy()

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

        self.display_mode_timer = Timer(2000)

        # Collision handling
        self.collision_sprites = collision_sprites
        self.on_surface = {"ground": False, "left": False, "right": False}
        self.platform = None

        # Permissions
        self.permissions = permissions

        # State
        self.alive = True

        # Timers
        self.timers = {
            "wall jump": Timer(400),
            "wall slide block": Timer(250),
            "dash cooldown": Timer(1000),
            "dash duration": Timer(200),
        }
    
    def set_notify_callback(self, callback):
        self.notify_mode = callback

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
        else:
            self.notify_level("dash", active=False)
        # Trigger heavy mode if permissions allow it
        # Only toggle when the key is first pressed. Reset when the key is released
        if self.permissions.get("heavy_mode", False) and keys[pygame.K_a]:
            if not self.a_key_pressed and not self.light_mode: # One mass manipulation mode can be active at a time
                if not self.heavy_mode:
                    self.mass *= 2
                    self.heavy_mode = True
                    self.notify_level("heavy_mode", active=True)
                    self.display_mode_timer.activate()
                else:
                    self.mass /= 2
                    self.heavy_mode = False
                    self.notify_level("heavy_mode", active=False)
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
                    self.notify_level("light_mode", active=True)
                    self.display_mode_timer.activate()
                else:
                    self.mass *= 2
                    self.light_mode = False
                    self.notify_level("light_mode", active=False)
                self.s_key_pressed = True
        else:
            self.s_key_pressed = False

    # Setup dash timers and cancel other actions ( like the current jump, if jumping )
    def start_dash(self):
        self.dashing = True
        self.timers["dash duration"].activate()  # Start dash duration timer
        self.timers["dash cooldown"].activate()  # Start cooldown timer
        self.notify_level("dash", active=True)

        # Cancel any ongoing jump
        self.direction.y = 0
        self.jump = False

    # Handle any movement related action or ability the player might make
    def handle_player_movement(self, dt):
        if self.dashing:
            # Dash movement in the last known direction
            self.hitbox_rect.x += self.last_direction.x * self.dash_speed * dt
            self.collision("x")
            self.rect.center = self.hitbox_rect.center

            # Stop dashing when the dash duration ends
            if not self.timers["dash duration"].active:
                self.dashing = False
                # self.base_image.fill("red")
        else:
            # Move and check for collision on x axis
            self.hitbox_rect.x += self.direction.x * self.speed * dt
            self.collision("x")
            self.rect.center = self.hitbox_rect.center
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
            self.rect.center = self.hitbox_rect.center

    # Make player move alongside the platform
    def handle_platform_movement(self, dt):
        if self.platform:
            self.hitbox_rect.topleft += self.platform.direction * self.platform.speed * dt

    # Make the player face the direction he last moved towards
    def handle_orientation(self):
        if self.last_direction.x < 0:
            self.image = pygame.transform.flip(self.base_image, True, False)
        elif self.last_direction.x > 0:
            self.image = self.base_image

    # Check what the player is currently in contact with ( nothing, the ground, or walls ( left, right ))
    def check_contact(self):
        ground_rect = pygame.Rect(self.hitbox_rect.bottomleft, (self.hitbox_rect.width, 2))
        right_rect = pygame.Rect(self.hitbox_rect.topright + vector(0, self.hitbox_rect.height / 4), (2, self.hitbox_rect.height / 2))
        left_rect = pygame.Rect((self.hitbox_rect.topleft + vector(-2, self.hitbox_rect.height / 4)), (2, self.hitbox_rect.height / 2))

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
            if sprite.rect.colliderect(self.hitbox_rect):
                # Check collision on x axis
                if axis == "x":
                    # Left
                    if self.hitbox_rect.left <= sprite.rect.right and int(self.prev_rect.left) >= int (sprite.prev_rect.right):
                        self.hitbox_rect.left = sprite.rect.right

                    # Right
                    if self.hitbox_rect.right >= sprite.rect.left and int(self.prev_rect.right) <= int(sprite.prev_rect.left):
                        self.hitbox_rect.right = sprite.rect.left
                # Check collision on y axis
                else:
                    # Top
                    if self.hitbox_rect.top <= sprite.rect.bottom and int(self.prev_rect.top) >= int(sprite.prev_rect.bottom):
                        self.hitbox_rect.top = sprite.rect.bottom
                        # Offset the player
                        if hasattr(sprite, "moving"):
                            self.hitbox_rect.top += 6

                    # Bottom
                    if self.hitbox_rect.bottom >= sprite.rect.top and int(self.prev_rect.top) <= int (sprite.prev_rect.top):
                        self.hitbox_rect.bottom = sprite.rect.top

                    self.direction.y = 0

                # If it touches a damage object, it dies
                if getattr(sprite, 'damage', True):
                    self.alive = False

    # Update state
    def update(self, dt):
        update_timers(self)
        if self.hitbox_rect.bottom > SCREEN_HEIGHT + 2 * TILE_SIZE:
            self.alive = False
        if self.alive:
            self.prev_rect = self.hitbox_rect.copy()
            self.handle_input()
            self.handle_orientation()
            self.handle_player_movement(dt)
            self.check_contact()
