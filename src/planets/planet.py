from utils.settings import *

class Planet:
    def __init__(self, name, gravity_strength, levels):
        self.name = name
        self.gravity_strength = gravity_strength
        self.levels = levels

    # Gravity now works based on both gravity_strength ( planet ) and mass ( entity )
    def apply_gravity(self, entity, dt):
        """Apply gravity to the entity's vertical velocity."""
        entity.direction.y += entity.mass * self.gravity_strength / 2 * dt
        entity.hitbox_rect.y += entity.direction.y * dt
        entity.direction.y += entity.mass * self.gravity_strength / 2 * dt

    def apply_gravity_on_wall_slide(self, entity, dt):
        """Apply gravity to the entity's vertical velocity when wall sliding."""
        entity.direction.y = 0
        entity.hitbox_rect.y += entity.mass * self.gravity_strength / 10 * dt

    # Not used yet, but might allow us to do some interesting stuff later on
    def reverse_gravity(self):
        self.gravity_strength *= -1
