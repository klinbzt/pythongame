import pygame
import sys
from utils.settings import *
from ui.loadgame import *
from ui.menusettings import SettingsMenu

class StartupScreen:
    def __init__(self, level_manager):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.active = True
        self.clock = pygame.time.Clock()

        # Preload resources
        self.background_image = pygame.image.load("../assets/graphics/intro/startupbrackground.png").convert()
        self.font = pygame.font.Font(None, 40)

        self.loadgames = LoadGame(self.screen, level_manager)
        self.settings = SettingsMenu(self.screen)
        self.animation_speed = 0.2
        self.hover_scale = 1.2
        self.default_scale = 1.0

        # Initialize button properties
        self.buttons = {
            "Play": {"hover_scale": self.default_scale, "y_offset": 0},
            "Load Game": {"hover_scale": self.default_scale, "y_offset": 0},
            "Settings": {"hover_scale": self.default_scale, "y_offset": 0},
        }

        self.selected_button_index = 0
        self.button_list = list(self.buttons.keys())
        self.recalculate_button_sizes()

    def recalculate_button_sizes(self):
        """Recalculate button sizes and positions based on the screen size."""
        screen_width, screen_height = self.screen.get_size()
        button_width = int(screen_width * 0.3)  # 30% of screen width
        button_height = int(screen_height * 0.1)  # 10% of screen height
        button_gap = int(screen_height * 0.05)  # 5% of screen height

        for idx, (label, data) in enumerate(self.buttons.items()):
            data["rect"] = pygame.Rect(
                (screen_width - button_width) // 2,
                (screen_height - button_height) // 2 + (idx - 1) * (button_height + button_gap),
                button_width,
                button_height,
            )

    def run(self):
        while self.active:
            self.handle_events()
            self.render()
            self.clock.tick(FPS)
            pygame.display.update()

    def render(self):
        # Recalculate button sizes before rendering
        self.recalculate_button_sizes()

        # Draw *non-pixelated* background
        scaled_bg = pygame.transform.scale(self.background_image, self.screen.get_size())
        self.screen.blit(scaled_bg, (0, 0))

        screen_center = (self.screen.get_width() // 2, self.screen.get_height() // 2)

        for idx, (label, data) in enumerate(self.buttons.items()):
            rect = data["rect"]
            hover_scale = data["hover_scale"]
            y_offset = data["y_offset"]

            # Determine target properties based on selection
            if idx == self.selected_button_index:
                target_hover_scale = self.hover_scale
                target_y_offset = 0
            else:
                target_hover_scale = self.default_scale
                target_y_offset = (idx - self.selected_button_index) * (rect.height + int(self.screen.get_height() * 0.05))

            # Smooth transitions
            data["hover_scale"] += (target_hover_scale - hover_scale) * self.animation_speed
            data["y_offset"] += (target_y_offset - y_offset) * self.animation_speed

            hover_scale = data["hover_scale"]
            y_offset = data["y_offset"]

            # Apply scaling and position updates
            scaled_width = int(rect.width * hover_scale)
            scaled_height = int(rect.height * hover_scale)
            scaled_rect = pygame.Rect(
                screen_center[0] - scaled_width // 2,
                screen_center[1] + y_offset - scaled_height // 2,
                scaled_width,
                scaled_height,
            )

            # Draw the button background
            button_base_color = (50, 50, 150)
            pygame.draw.rect(self.screen, button_base_color, scaled_rect, border_radius=20)

            ##
            # 1) SLIGHT UPSCALE USING SMOOTHSCALE
            ##
            # Render the original text (white)
            scaled_font_size = int(40 * hover_scale)
            text_font = pygame.font.Font(None, scaled_font_size)
            text_surface = text_font.render(label, True, (255, 255, 255))

            # Slightly upscale (e.g., 1.2x for a small "pop" effect)
            upscale_factor = 1.2
            new_width = int(text_surface.get_width() * upscale_factor)
            new_height = int(text_surface.get_height() * upscale_factor)

            text_surface_upscaled = pygame.transform.smoothscale(
                text_surface, (new_width, new_height)
            )

            ##
            # 2) SIMPLE SHADOW EFFECT
            ##
            # Create a black version of the same text for a shadow
            text_shadow = text_font.render(label, True, (0, 0, 0))
            text_shadow_upscaled = pygame.transform.smoothscale(
                text_shadow, (new_width, new_height)
            )

            # Draw the shadow just a couple of pixels offset (x+2, y+2)
            shadow_offset = 2
            shadow_rect = text_shadow_upscaled.get_rect(
                center=(scaled_rect.centerx + shadow_offset, scaled_rect.centery + shadow_offset)
            )
            self.screen.blit(text_shadow_upscaled, shadow_rect)

            # Draw the upscaled white text on top of the shadow
            text_rect = text_surface_upscaled.get_rect(center=scaled_rect.center)
            self.screen.blit(text_surface_upscaled, text_rect)
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_button_index = (self.selected_button_index - 1) % len(self.button_list)
                elif event.key == pygame.K_DOWN:
                    self.selected_button_index = (self.selected_button_index + 1) % len(self.button_list)
                elif event.key == pygame.K_RETURN:
                    self.handle_button_click(self.button_list[self.selected_button_index])

    def handle_button_click(self, label):
        if label == "Play":
            print("Play button clicked!")
            self.active = False
        elif label == "Load Game":
            print("Load Game button clicked!")
            if not self.loadgames.run():
                self.active = False
        elif label == "Settings":
            self.settings.run()
            print("Settings button clicked!")
