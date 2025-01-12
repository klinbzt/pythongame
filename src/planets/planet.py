from utils.settings import *
from audio.audio_manager import AudioManager
from ui.textbox import *  

class Planet:
    def __init__(self, name, gravity_strength, levels):
        """
        Initialize the Planet class.

        :param name: Name of the planet.
        :param gravity_strength: Gravity strength of the planet.
        :param levels: Levels associated with the planet.
        :param screen: Pygame screen where the text will be displayed.
        :param font: Pygame font object for rendering the text.
        """
        self.name = name
        self.gravity_strength = gravity_strength
        self.levels = levels
        self.audio_manager = AudioManager()

    
    # Gravity now works based on both gravity_strength (planet) and mass (entity)
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
