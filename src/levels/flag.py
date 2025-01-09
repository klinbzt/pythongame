from utils.settings import *

class Flag(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites, next_level_callback, sound):
        super().__init__(groups)
        self.image = image.load("../assets/graphics/tilesets/flag.png")

        self.rect = self.image.get_rect(topleft = pos)
        self.prev_rect = self.rect.copy()
        
        self.sound = sound
        self.collision_sprites = collision_sprites
        self.next_level_callback = next_level_callback

    def check_collision(self, player):
        if self.rect.colliderect(player.rect):
            self.sound.play()
            self.sound.set_volume(VOLUME)
            self.next_level_callback()