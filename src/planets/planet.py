from utils.settings import *

class Planet:
    def __init__(self, name, gravity_strength, levels):
        self.name = name
        self.gravity_strength = gravity_strength
        self.levels = levels
    
    def get_level(self, level_index):
        """Return the level corresponding to the given number."""
        if 0 <= level_index <= len(self.levels) - 1:
            return self.levels[level_index]
        return None
        
    def apply_gravity(self, entity, dt):
        """Apply gravity to the entity's vertical velocity."""
        entity.direction.y += self.gravity_strength / 2 * dt
        entity.rect.y += entity.direction.y * dt
        entity.direction.y += self.gravity_strength / 2 * dt
    
    def apply_gravity_on_wall_slide(self, entity, dt):
        """Apply gravity to the entity's vertical velocity when wall sliding."""
        entity.direction.y = 0
        entity.rect.y += self.gravity_strength / 10 * dt
