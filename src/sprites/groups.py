from utils.settings import *
from sprites.sprite import Sprite
from entities.player import Player

class AllSprites(pygame.sprite.Group):
    def __init__(self, tmx_map):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = vector()
        self.bg_tiles = []
        self.borders = {
            'left': 0,
            'right': -1 * tmx_map.width * TILE_SIZE + SCREEN_WIDTH
        }
        try:
            bg_tile = tmx_map.get_layer_by_name("Background")
            z = Z_LAYERS["bg"]
            for pos_x, pos_y, surf in bg_tile.tiles():
                self.bg_tiles.append(Sprite((pos_x * TILE_SIZE, pos_y * TILE_SIZE), surf, self, Z_LAYERS["bg"]))
        except ValueError:
            print("Layer 'Background' not found.")

    def cam_constraint(self):
        self.offset.x = self.offset.x if self.offset.x < self.borders['left'] else self.borders['left']
        self.offset.x = self.offset.x if self.offset.x > self.borders['right'] else self.borders['right']

    def draw(self, target_pos):
        # Calculate camera offset
        self.offset.x = -(target_pos[0] - SCREEN_WIDTH / 2)
        self.offset.y = 0
        self.cam_constraint()

        # Combine background tiles with sprites for unified sorting
        all_drawables = self.bg_tiles + list(self)
        for drawable in sorted(all_drawables, key=lambda sprite: getattr(sprite, 'z', 0)):
            offset_pos = drawable.rect.topleft + self.offset
            if isinstance(drawable, Player):
                # Draw afterimages first for the player
                drawable.draw_afterimages(self.display_surface, self.offset)
            # Draw the sprite itself
            self.display_surface.blit(drawable.image, offset_pos)