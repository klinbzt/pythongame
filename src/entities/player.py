from utils.settings import *
from utils.timer import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites, planet, permissions, notify_level_callback):
        super().__init__(groups)

        # Rendering
        self.z = Z_LAYERS['main']

        # Player Animations
        self.sprite_sheet = pygame.image.load("../assets/graphics/tilesets/animated_player.png").convert_alpha()
        self.frame_width = 64
        self.frame_height = 64
        self.animations = self.load_animations()
        self.current_animation = 'idle'
        self.current_frame = 0
        self.animation_speed = 0.1
        self.animation_timer = 0

        # Player State
        self.alive = True
        self.spawn_pos = pos
        self.image = self.animations[self.current_animation][self.current_frame]
        self.rect = self.image.get_rect(topleft=pos)
        self.facing_right = True

        # Level State
        self.notify_level = notify_level_callback

        # Rects
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox_rect = self.rect.inflate(-40, -8)
        self.prev_rect = self.hitbox_rect.copy()

        # Safety check for player position
        screen_width, screen_height = pygame.display.get_surface().get_size()
        if not (0 <= pos[0] <= screen_width and 0 <= pos[1] <= screen_height):
            raise ValueError(f"Player position {pos} is out of screen bounds!")

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

        # Afterimage settings
        self.afterimages = []
        self.afterimage_lifetime = 200

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
            "dash duration": Timer(200),
            "afterimage duration": Timer(30),
            "display mode": Timer(2000),
        }

    def load_animations(self):
        """Extract individual frames from the sprite sheet and store them."""
        animations = {
            'idle': ([], 8),
            'run': ([], 8),
            "attack_1": ([], 4),
            "attack_2": ([], 3),
            "jump": ([], 4),
            "fall": ([], 4),
            "hit": ([], 2),
            "death": ([], 14),
        }

        # Adjust the coordinates and sizes based on your sprite sheet
        for row, (animation_name, (frames, frame_count)) in enumerate(animations.items()):
            for col in range(frame_count):
                x = col * self.frame_width
                y = row * self.frame_height
                frame = self.sprite_sheet.subsurface(pygame.Rect(x, y, self.frame_width, self.frame_height))
                frames.append(frame)
            animations[animation_name] = frames

        return animations
    
    def draw_afterimages(self, surface, offset):
        """Draw the player's afterimages."""
        if self.dashing:
            for afterimage in self.afterimages:
                offset_pos = vector(afterimage['pos']) + offset
                surface.blit(afterimage['image'], offset_pos)
    
    def handle_animation(self, dt):
        # Update the previous animation state
        self.previous_animation = self.current_animation

        # Determine the appropriate animation based on player state
        if not self.alive:
            self.current_animation = 'death'
        else:
            if self.dashing:
                # Add an afterimage at regular intervals while dashing
                if self.timers["afterimage duration"].active:
                    self.timers["afterimage duration"].update()
                else:
                    self.afterimages.append({
                        'image': self.image.copy(),
                        'pos': self.rect.topleft,
                        'alpha': 255,
                        'timer': self.afterimage_lifetime
                    })
                    self.timers["afterimage duration"].activate()

                # Update afterimages and apply fading (alpha decrease)
                for afterimage in self.afterimages[:]:
                    afterimage['timer'] -= dt * 1000
                    if afterimage['timer'] <= 0:
                        self.afterimages.remove(afterimage)
                    else:
                        afterimage['alpha'] -= 25
                        if afterimage['alpha'] < 0:
                            afterimage['alpha'] = 0
                        afterimage['image'].set_alpha(afterimage['alpha'])

            # Once the dash is over, clear everything related to the dash
            if not self.timers["dash duration"].active:
                self.timers["afterimage duration"].deactivate()
                self.afterimages.clear()
                self.last_direction = vector(1, 0)

            if self.on_surface["ground"]:
                if self.direction.x == 0:
                    self.current_animation = "idle"
                else:
                    self.current_animation = "run"
            else:
                if any((self.on_surface["left"], self.on_surface["right"])):
                    self.current_animation = "fall"
                else:
                    if self.direction.y < 0:
                        self.current_animation = "jump"
                    else:
                        self.current_animation = "fall"
        
        # If the animation has changed, reset the frame to 0
        if self.current_animation != self.previous_animation:
            self.current_frame = 0

        # Update the animation frame
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.animations[self.current_animation])

        # Always use the original frame from the animation list
        original_image = self.animations[self.current_animation][self.current_frame]

        # Flip the image if the player is facing left
        if not self.facing_right:
            self.image = pygame.transform.flip(original_image, True, False)
        else:
            self.image = original_image
    
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
                self.facing_right = True
            if keys[pygame.K_LEFT]:
                input_vector.x -= 1
                self.facing_right = False
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
                    self.timers["display mode"].activate()
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
                    self.timers["display mode"].activate()
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

    def respawn_player(self):
        # Reset player position
        self.hitbox_rect.topleft = self.spawn_pos
        self.rect.center = self.hitbox_rect.center
        self.facing_right = True

        # Reset animation
        self.current_animation = 'idle'
        self.current_frame = 0
        self.animation_timer = 0

        # Reset movement
        self.direction = vector(0, 0)
        self.jump = False
        self.dashing = False

        # Set alive state
        self.alive = True

        # Reset environment and physics
        self.on_surface = {"ground": False, "left": False, "right": False}
        self.platform = None
        self.mass = 100

        # Reset abilities
        self.heavy_mode = False
        self.a_key_pressed = False
        self.light_mode = False
        self.s_key_pressed = False

        # Reset abilities display
        self.notify_level("dash", active=False)
        self.notify_level("heavy_mode", active=False)
        self.notify_level("light_mode", active=False)

        # Reset timers
        reset_timers(self)

    # Update state
    def update(self, dt):
        update_timers(self)

        if self.hitbox_rect.bottom > SCREEN_HEIGHT + 2 * TILE_SIZE:
            self.respawn_player()
            return

        if self.current_animation == "death":
            if self.current_frame == len(self.animations[self.current_animation]) - 1:
                self.respawn_player()
                return
        else:
            self.prev_rect = self.hitbox_rect.copy()
            self.handle_input()
            self.handle_player_movement(dt)
            self.check_contact()

        self.handle_animation(dt)
