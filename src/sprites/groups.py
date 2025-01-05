from utils.settings import *

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = vector()
    
    def draw(self, target_pos):
        self.offset.x =  - (target_pos[0] - SCREEN_WIDTH / 2)
        self.offset.y =  - (target_pos[1] - SCREEN_HEIGHT / 2)
        for sprite in sorted(self, key=lambda sprite: getattr(sprite, 'z', 0)):
            offset_pos = sprite.rect.topleft + self.offset
            self.display_surface.blit(sprite.image, offset_pos)