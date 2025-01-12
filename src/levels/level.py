from utils.settings import *
from sprites.sprite import Sprite, MovingSprite
from entities.player import Player
from levels.flag import Flag
from sprites.groups import AllSprites
from utils.timer import Timer

class Level:
    def __init__(self, level_data, callback):
        self.screen = pygame.display.get_surface()

        # Level data ( Passed on by the Level Manager )
        self.planet = level_data["planet"]
        self.tmx_map = level_data["tmx_map"]
        self.permissions = level_data["permissions"]

        # Level sound ( Each planet has an audio_manager instance, so if we want, we can use a different set of sounds )
        self.audio_manager = level_data["planet"].audio_manager

        # Level sound flags
        self.bg_music_playing = False

        # Level allowed abilities images
        self.permission_images = {
            "dash": image.load("../assets/graphics/ui/dash.png").convert_alpha(),
            "heavy_mode": image.load("../assets/graphics/ui/heavy_mode.png").convert_alpha(),
            "light_mode": image.load("../assets/graphics/ui/light_mode.png").convert_alpha(),
        }

        self.permission_images_used = {
            "dash": image.load("../assets/graphics/ui/dash_used.png").convert_alpha(),
            "heavy_mode": image.load("../assets/graphics/ui/heavy_mode_used.png").convert_alpha(),
            "light_mode": image.load("../assets/graphics/ui/light_mode_used.png").convert_alpha(),
        }

        self.permission_timers = {
            "dash": Timer(1000),
            "heavy_mode": Timer(1000),
            "light_mode": Timer(1000),
        }

        # Callback
        self.callback = callback

        # Initialize sprite groups
        self.all_sprites = AllSprites(self.tmx_map)
        self.collision_sprites = pygame.sprite.Group()

        # Initialize level flags
        self.player = None
        self.flag = None

        # Setup the level
        self.setup()

    # Passed to player to notify when one of the allowed abilities has been used
    def notify(self, mode, active):
        if active:
            self.permission_timers[mode].activate()
        else:
            self.permission_timers[mode].deactivate()

    # Draw the boxes of the abilities that are allowed in this level
    def draw_permissions(self):
        x_offset = 10
        for mode, image in self.permission_images.items():
            if self.permissions[mode]:
                if self.permission_timers[mode].active:
                    active_image = self.permission_images_used[mode]
                else:
                    active_image = image
                if mode == "dash" and self.player.timers["dash cooldown"].active:
                    active_image = self.permission_images_used[mode]
                self.screen.blit(active_image, (x_offset, 10))
                x_offset += active_image.get_width() + 10

    # Setup the level by creating the sprites of the objects in each layer and initializing flags
    def setup(self):
        # Terrain Layer
        try:
            terrain_layer = self.tmx_map.get_layer_by_name("Terrain")
            z = Z_LAYERS["main"]
            for pos_x, pos_y, surf in terrain_layer.tiles():
                Sprite((pos_x * TILE_SIZE, pos_y * TILE_SIZE), surf, (self.all_sprites, self.collision_sprites), z)
        except ValueError:
            print("Layer 'Terrain' not found.")
        
        # Damage Tiles Layer
        try:
            damage_terrain_layer = self.tmx_map.get_layer_by_name("Damage_Terrain")
            z = Z_LAYERS["main"]
            for pos_x, pos_y, surf in damage_terrain_layer.tiles():
                damage_sprite = Sprite((pos_x * TILE_SIZE, pos_y * TILE_SIZE), surf,(self.all_sprites, self.collision_sprites))
                damage_sprite.damage = True
        except ValueError:
            print("Layer 'Damage_Terrain' not found.")

        # Moving Objects Layer
        try:
            moving_objects_layer = self.tmx_map.get_layer_by_name("Moving Objects")
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

                    # Create moving sprite
                    MovingSprite((self.all_sprites, self.collision_sprites), start_pos, end_pos, move_direction, speed)
        except ValueError:
            print("Layer 'Moving Objects' not found.")
        
        # Objects Layer
        try:
            objects_layer = self.tmx_map.get_layer_by_name("Objects")
            for obj in objects_layer:
                if obj.name == "player":
                    # Create the player
                    self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites, self.planet,
                                         self.permissions, self.notify, self.audio_manager)
                if obj.name == "flag":
                    # Create the flag
                    self.flag = Flag((obj.x, obj.y), self.all_sprites, self.collision_sprites)

            
        except ValueError:
            print("Layer 'Objects' not found.")
        
        # Decorations Layer
        try:
            decorations_layer = self.tmx_map.get_layer_by_name("Decorations")
            z = Z_LAYERS["fg"]
            for pos_x, pos_y, surf in decorations_layer.tiles():
                Sprite((pos_x * TILE_SIZE, pos_y * TILE_SIZE), surf, self.all_sprites, z)
        except ValueError:
            print("Layer 'Decorations' not found.")
    # Constraining the player to the map size
    def check_constraint(self):
        if self.player.hitbox_rect.left <= 0:
            self.player.hitbox_rect.left = 0
        if self.player.hitbox_rect.right > self.tmx_map.width * TILE_SIZE - TILE_SIZE:
            self.player.hitbox_rect.left = self.tmx_map.width * TILE_SIZE - 2 * TILE_SIZE

    # Run the level
    def run(self, dt):
        self.screen.fill(BLACK)
        self.all_sprites.update(dt)
        self.all_sprites.draw(self.player.hitbox_rect.center)
        self.check_constraint()
        self.draw_permissions()

        # Play background music if not already playing
        if not self.bg_music_playing:
            self.audio_manager.set_sound_volume("bg_music", 0.1)
            self.audio_manager.play('bg_music', loop=-1)
            self.bg_music_playing = True

        # Check if the level has been completed. If it was, play audio and go to the next level
        if self.flag.check_collision(self.player):
            self.audio_manager.stop("bg_music")
            self.audio_manager.set_sound_volume("next_level", 0.5)
            self.audio_manager.play("next_level")
            self.callback()
            return False
    
        return True