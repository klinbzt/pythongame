import sys
import pygame
from utils.settings import * 
from ui.menusettings import SettingsMenu
from ui.loadgame import LoadGame

class StartupScreen:
    def __init__(self, level_manager, clock):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        self.active = True
        self.clock = clock

        texture_image = pygame.image.load("../assets/graphics/tilesets/extra.png").convert_alpha()

        texture_coords = (0, 256, 128, 128)

        self.button_texture_gray = texture_image.subsurface(pygame.Rect(*texture_coords))
        # Preload resources
        self.background_image_original = pygame.image.load("../assets/graphics/tilesets/new_background.png").convert()

        # Scaled background placeholder
        self.background_image_scaled = None

        # Fonts
        self.font_cache = {}
        self.base_font_size = 40

        # External screens
        self.loadgames = LoadGame(self.screen, level_manager)
        self.settings = SettingsMenu(self.screen)

        # Animation settings
        self.animation_speed = 0.2
        self.hover_scale = 1.2
        self.default_scale = 1.0

        # Buttons with the texture from settings.py
        self.buttons = {
            "Play": {"hover_scale": self.default_scale, "y_offset": 0, "texture": self.button_texture_gray},
            "Load Game": {"hover_scale": self.default_scale, "y_offset": 0, "texture": self.button_texture_gray},
            "Settings": {"hover_scale": self.default_scale, "y_offset": 0, "texture": self.button_texture_gray},
        }

        self.selected_button_index = 0
        self.button_list = list(self.buttons.keys())

        # Initial calculations for button sizes and background
        self.recalculate_button_sizes()
        self.rescale_background()

    def recalculate_button_sizes(self):
        """Recalculate button sizes and positions based on the current screen size."""
        screen_width, screen_height = self.screen.get_size()
        button_width = int(screen_width * 0.3)   # 30% of screen width
        button_height = int(screen_height * 0.1)  # 10% of screen height
        button_gap = int(screen_height * 0.05)   # 5% of screen height

        for idx, (label, data) in enumerate(self.buttons.items()):
            data["rect"] = pygame.Rect(
                (screen_width - button_width) // 2,
                (screen_height - button_height) // 2 + (idx - 1) * (button_height + button_gap),
                button_width,
                button_height,
            )

    def rescale_background(self):
        """Scale the background image to the current screen size."""
        screen_size = self.screen.get_size()
        self.background_image_scaled = pygame.transform.scale(self.background_image_original, screen_size)

    def get_font(self, size):
        """Retrieve or create a font of a given size from the cache."""
        if size not in self.font_cache:
            self.font_cache[size] = pygame.font.Font(None, size)
        return self.font_cache[size]

    def run(self):
        while self.active:
            self.handle_events()
            self.render()
            self.clock.tick(FPS)
            pygame.display.update()

    def render(self):
        """Render the startup screen."""
        # Draw background
        self.screen.blit(self.background_image_scaled, (0, 0))

        # Draw buttons
        self.render_buttons()

    def render_buttons(self):
        """Render all buttons with hover and animation effects."""
        screen_center = (self.screen.get_width() // 2, self.screen.get_height() // 2)

        for idx, (label, data) in enumerate(self.buttons.items()):
            rect = data["rect"]
            current_hover_scale = data["hover_scale"]
            current_y_offset = data["y_offset"]

            # Determine target values based on button selection
            if idx == self.selected_button_index:
                target_hover_scale = self.hover_scale
                target_y_offset = 0
            else:
                target_hover_scale = self.default_scale
                target_y_offset = (idx - self.selected_button_index) * (rect.height + int(self.screen.get_height() * 0.05))

            # Smooth animation
            data["hover_scale"] += (target_hover_scale - current_hover_scale) * self.animation_speed
            data["y_offset"] += (target_y_offset - current_y_offset) * self.animation_speed

            # Apply scaling and position updates
            hover_scale = data["hover_scale"]
            y_offset = data["y_offset"]

            scaled_width = int(rect.width * hover_scale)
            scaled_height = int(rect.height * hover_scale)
            scaled_rect = pygame.Rect(
                screen_center[0] - scaled_width // 2,
                screen_center[1] + y_offset - scaled_height // 2,
                scaled_width,
                scaled_height,
            )

            # Draw button texture from settings
            scaled_texture = pygame.transform.scale(data["texture"], (scaled_width, scaled_height))
            self.screen.blit(scaled_texture, scaled_rect)

            # Render text with a slight upscale + shadow
            scaled_font_size = int(self.base_font_size * hover_scale)
            text_font = self.get_font(scaled_font_size)

            # Create the text surface
            text_surface = text_font.render(label, True, (255, 255, 255))
            upscale_factor = 1.2
            new_width = int(text_surface.get_width() * upscale_factor)
            new_height = int(text_surface.get_height() * upscale_factor)
            text_surface_upscaled = pygame.transform.smoothscale(text_surface, (new_width, new_height))

            # Create a shadow version
            text_shadow = text_font.render(label, True, (0, 0, 0))
            text_shadow_upscaled = pygame.transform.smoothscale(text_shadow, (new_width, new_height))

            # Draw the shadow slightly offset
            shadow_offset = 2
            shadow_rect = text_shadow_upscaled.get_rect(
                center=(scaled_rect.centerx + shadow_offset, scaled_rect.centery + shadow_offset)
            )
            self.screen.blit(text_shadow_upscaled, shadow_rect)

            # Draw the main text
            text_rect = text_surface_upscaled.get_rect(center=scaled_rect.center)
            self.screen.blit(text_surface_upscaled, text_rect)

    def handle_events(self):
        """Capture and handle user events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Handle window resizing
            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.recalculate_button_sizes()
                self.rescale_background()

            # Keyboard inputs
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_button_index = (self.selected_button_index - 1) % len(self.button_list)
                elif event.key == pygame.K_DOWN:
                    self.selected_button_index = (self.selected_button_index + 1) % len(self.button_list)
                elif event.key == pygame.K_RETURN:
                    self.handle_button_click(self.button_list[self.selected_button_index])

    def handle_button_click(self, label):
        """Handle button click events."""
        if label == "Play":
            print("Play button clicked!")
            self.active = False
        elif label == "Load Game":
            print("Load Game button clicked!")
            if not self.loadgames.run():
                self.active = False
        elif label == "Settings":
            print("Settings button clicked!")
            self.settings.run()
