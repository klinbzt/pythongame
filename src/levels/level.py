from utils.settings import *
from sprites.sprite import Sprite, MovingSprite
from entities.player import Player
from levels.flag import Flag

class Level:
    def __init__(self, planet, level, next_level_callback):
        """Initialize the level with the given planet, map, and callback for the next level."""
        self.screen = pygame.display.get_surface()

        # Sprites
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()

        # Level data
        self.planet = planet
        self.tmx_map = level["tmx_map"]
        self.permissions = level["permissions"]

        # Callback
        self.next_level_callback = next_level_callback

        self.setup()

    def setup(self):
        """Set up the level with terrain, moving objects, and player."""
        # Terrain (Tiles)
        try:
            terrain_layer = self.tmx_map.get_layer_by_name("Terrain")
            for pos_x, pos_y, surf in terrain_layer.tiles():
                Sprite((pos_x * TILE_SIZE, pos_y * TILE_SIZE), surf, (self.all_sprites, self.collision_sprites))
        except ValueError:
            print("Layer 'Terrain' not found.")

        # Moving Objects
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
        
        # Objects
        try:
            objects_layer = self.tmx_map.get_layer_by_name("Objects")
            for obj in objects_layer:
                if obj.name == "player":
                    # Create the player
                    self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites, self.planet, self.permissions)
                if obj.name == "flag":
                    # Create the flag
                    self.flag = Flag((obj.x, obj.y), self.all_sprites, self.collision_sprites, self.next_level_callback)
        except ValueError:
            print("Layer 'Objects' not found.")

    def run(self, dt):
        """Update and draw all sprites, and check for flag collision."""
        self.screen.fill(BLACK)
        self.all_sprites.update(dt)
        self.all_sprites.draw(self.screen)

        # Check for collision between player and flag
        self.flag.check_collision(self.player)
