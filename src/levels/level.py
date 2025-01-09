from utils.settings import *
from sprites.sprite import Sprite, MovingSprite
from entities.player import Player
from levels.flag import Flag
from sprites.groups import AllSprites
from utils.timer import Timer

class Level:
    def __init__(self, level_data, callback):
        self.screen = pygame.display.get_surface()

        # Level data
        self.planet = level_data["planet"]
        self.tmx_map = level_data["tmx_map"]
        self.permissions = level_data["permissions"]

        self.permission_images = {
            "dash": image.load("../assets/graphics/ui/dash.png").convert_alpha(),
            "heavy_mode": image.load("../assets/graphics/ui/dash.png").convert_alpha(),
            "light_mode": image.load("../assets/graphics/ui/dash.png").convert_alpha(),
        }

        self.permission_images_used = {
            "dash": image.load("../assets/graphics/ui/dash1.png").convert_alpha(),
            "heavy_mode": image.load("../assets/graphics/ui/dash1.png").convert_alpha(),
            "light_mode": image.load("../assets/graphics/ui/dash1.png").convert_alpha(),
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

        # Initialize level general
        self.player = None
        self.flag = None

        # Setup the level
        self.setup()

    def notify(self, mode, active):
        if active:
            self.permission_timers[mode].activate()
        else:
            self.permission_timers[mode].deactivate()

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

    # PROBLEM: On planets with high gravity, the player is rendered, but the platforms / terrain isn't all setup, so the player falls through them and off the map. Needs fixing ASAP
    def setup(self):
        try:
            terrain_layer = self.tmx_map.get_layer_by_name("Terrain")
            z = Z_LAYERS["main"]
            for pos_x, pos_y, surf in terrain_layer.tiles():
                Sprite((pos_x * TILE_SIZE, pos_y * TILE_SIZE), surf, (self.all_sprites, self.collision_sprites), z)
        except ValueError:
            print("Layer 'Terrain' not found.")
        
        # Damage Tiles
        try:
            damage_terrain_layer = self.tmx_map.get_layer_by_name("Damage_Terrain")
            z = Z_LAYERS["main"]
            for pos_x, pos_y, surf in damage_terrain_layer.tiles():
                damage_sprite = Sprite((pos_x * TILE_SIZE, pos_y * TILE_SIZE), surf,(self.all_sprites, self.collision_sprites))
                damage_sprite.damage = True
        except ValueError:
            print("Layer 'Damage_Terrain' not found.")

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
                    self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites, self.planet, self.permissions, self.notify)
                if obj.name == "flag":
                    # Create the flag
                    self.flag = Flag((obj.x, obj.y), self.all_sprites, self.collision_sprites, self.callback)
        except ValueError:
            print("Layer 'Objects' not found.")
        
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

    # It shows wasted and ends the game
    def die(self):
        font = pygame.font.Font(None, 120)
        text = font.render("WASTED", True, (255, 0, 0))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)
        pygame.display.update()
        pygame.time.wait(1000)
        pygame.quit()
        exit()

    # Run the level
    def run(self, dt):
        self.screen.fill(BLACK)
        self.all_sprites.update(dt)
        self.all_sprites.draw(self.player.hitbox_rect.center)
        self.check_constraint()
        self.draw_permissions()

        if self.player.alive == False:
            self.die()

        if self.flag:
            self.flag.check_collision(self.player)