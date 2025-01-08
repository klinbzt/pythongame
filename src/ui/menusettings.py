import pygame
import sys
from utils.settings import *

class SettingsMenu:
    def __init__(self, screen):
        self.screen = screen
        self.active = True
        self.clock = pygame.time.Clock()

        # Font and colors
        self.font = pygame.font.Font(None, 40)
        self.text_color = BLACK
        self.button_color = WHITE
        self.hover_color = GRAY

        # Button properties
        self.hover_scale = 1.2
        self.default_scale = 0.85
        self.animation_speed = 0.2

        self.buttons = {
            "Brightness": {"hover_scale": self.default_scale, "y_offset": 0},
            "Fullscreen": {"hover_scale": self.default_scale, "y_offset": 0},
            "Volume": {"hover_scale": self.default_scale, "y_offset": 0},
            "Back": {"hover_scale": self.default_scale, "y_offset": 0},
        }

        self.selected_button_index = 0
        self.button_list = list(self.buttons.keys())

        self.recalculate_button_sizes()

        # Volume control
        self.volume = 0.5  # Default volume (50%)
        self.volume_slider_width = 0  # Dynamically set to the button width when pressed
        self.volume_slider_max_width = 0
        self.volume_button_top_width = int(self.volume_slider_max_width * self.volume)

        # Brightness control
        self.brightness = 1.0  # Default brightness (100%)
        self.brightness_slider_width = 0
        self.brightness_slider_max_width = 0
        self.brightness_button_top_width = int(self.brightness_slider_max_width * self.brightness)

        # Initialize dragging state
        self.volume_slider_active = False
        self.brightness_slider_active = False

    def recalculate_button_sizes(self):
        """Recalculate button sizes and positions based on the screen size."""
        screen_width, screen_height = self.screen.get_size()
        button_width = int(screen_width * 0.3)   # 30% of screen width
        button_height = int(screen_height * 0.1) # 10% of screen height
        button_gap = int(screen_height * 0.05)   # 5% of screen height

        for idx, (label, data) in enumerate(self.buttons.items()):
            data["rect"] = pygame.Rect(
                (screen_width - button_width) // 2,
                (screen_height - button_height) // 2 + (idx - 1) * (button_height + button_gap),
                button_width,
                button_height,
            )

            # Set the volume and brightness slider widths
            if label == "Volume":
                self.volume_slider_width = data["rect"].width
                self.volume_slider_max_width = self.volume_slider_width
            elif label == "Brightness":
                self.brightness_slider_width = data["rect"].width
                self.brightness_slider_max_width = self.brightness_slider_width

    def run(self):
        # Re-initialize in case we return from other menus
        self.__init__(self.screen)

        while self.active:
            self.handle_events()
            self.render()
            self.clock.tick(FPS)
            pygame.display.update()

        self.cleanup()

    def render(self):
        # Recalculate button sizes before rendering
        self.recalculate_button_sizes()

        # Fill the screen with black
        self.screen.fill(BLACK)

        # Render volume slider if it's active
        if self.volume_slider_active:
            volume_button_rect = self.buttons["Volume"]["rect"]
            # Apply the hover_scale to match the selected button size
            scaled_width = int(volume_button_rect.width * self.buttons["Volume"]["hover_scale"])
            slider_rect = pygame.Rect(
                volume_button_rect.left,
                volume_button_rect.top - 100,
                scaled_width,
                int(volume_button_rect.height)
            )
            pygame.draw.rect(self.screen, PURPLE, slider_rect, border_radius=20)

            # Draw the slider handle for volume
            slider_handle_rect = pygame.Rect(
                volume_button_rect.left,
                volume_button_rect.top - 100,
                self.volume_button_top_width,
                int(volume_button_rect.height)
            )
            pygame.draw.rect(self.screen, LIGHT_PURPLE, slider_handle_rect, border_radius=20)

            # Draw the text inside the volume slider
            text = self.font.render(f"{int(self.volume * 100)}%", True, WHITE)
            text_rect = text.get_rect(center=slider_rect.center)
            self.screen.blit(text, text_rect)

        # Render brightness slider if it's active
        if self.brightness_slider_active:
            brightness_button_rect = self.buttons["Brightness"]["rect"]
            # Apply the hover_scale to match the selected button size
            scaled_width = int(brightness_button_rect.width * self.buttons["Brightness"]["hover_scale"])
            slider_rect = pygame.Rect(
                brightness_button_rect.left,
                brightness_button_rect.top + 100,
                scaled_width,
                int(brightness_button_rect.height)
            )
            pygame.draw.rect(self.screen, PURPLE, slider_rect, border_radius=20)

            # Draw the slider handle for brightness
            slider_handle_rect = pygame.Rect(
                brightness_button_rect.left,
                brightness_button_rect.top + 100,
                self.brightness_button_top_width,
                int(brightness_button_rect.height)
            )
            pygame.draw.rect(self.screen, LIGHT_PURPLE, slider_handle_rect, border_radius=20)

            # Draw the text inside the brightness slider
            text = self.font.render(f"{int(self.brightness * 100)}%", True, WHITE)
            text_rect = text.get_rect(center=slider_rect.center)
            self.screen.blit(text, text_rect)

        # Render other buttons with dynamic size and position
        screen_center = (self.screen.get_width() // 2, self.screen.get_height() // 2)

        for idx, (label, data) in enumerate(self.buttons.items()):
            # Skip rendering the button itself if its slider is active (we draw the slider instead)
            if label == "Volume" and self.volume_slider_active:
                continue
            if label == "Brightness" and self.brightness_slider_active:
                continue

            rect = data["rect"]
            hover_scale = data["hover_scale"]
            y_offset = data["y_offset"]

            # Determine target scale/offset based on selection
            if idx == self.selected_button_index:
                target_hover_scale = self.hover_scale
                target_y_offset = 0
            else:
                target_hover_scale = self.default_scale
                target_y_offset = (idx - self.selected_button_index) * (
                    rect.height + int(self.screen.get_height() * 0.05)
                )

            # Smooth transitions
            data["hover_scale"] += (target_hover_scale - hover_scale) * self.animation_speed
            data["y_offset"] += (target_y_offset - y_offset) * self.animation_speed

            hover_scale = data["hover_scale"]
            y_offset = data["y_offset"]

            # Compute scaled rectangle
            scaled_width = int(rect.width * hover_scale)
            scaled_height = int(rect.height * hover_scale)
            scaled_rect = pygame.Rect(
                screen_center[0] - scaled_width // 2,
                screen_center[1] + y_offset - scaled_height // 2,
                scaled_width,
                scaled_height,
            )

            # Draw button background
            button_base_color = PURPLE
            pygame.draw.rect(self.screen, button_base_color, scaled_rect, border_radius=20)

            ##
            # 1) SLIGHT UPSCALE USING SMOOTHSCALE
            ##
            scaled_font_size = int(40 * hover_scale)
            text_font = pygame.font.Font(None, scaled_font_size)
            text_surface = text_font.render(label, True, (255, 255, 255))

            # Slightly upscale (e.g., 1.2x) for a small "pop" effect
            scale_factor = 1.2
            up_width = int(text_surface.get_width() * scale_factor)
            up_height = int(text_surface.get_height() * scale_factor)
            text_upscaled = pygame.transform.smoothscale(text_surface, (up_width, up_height))

            ##
            # 2) SIMPLE SHADOW EFFECT
            ##
            shadow_surface = text_font.render(label, True, (0, 0, 0))
            shadow_upscaled = pygame.transform.smoothscale(shadow_surface, (up_width, up_height))

            # Draw shadow offset by a couple of pixels (2, 2)
            shadow_offset = 2
            shadow_rect = shadow_upscaled.get_rect(
                center=(scaled_rect.centerx + shadow_offset, scaled_rect.centery + shadow_offset)
            )
            self.screen.blit(shadow_upscaled, shadow_rect)

            # Blit the upscaled white text on top of the shadow
            text_rect = text_upscaled.get_rect(center=scaled_rect.center)
            self.screen.blit(text_upscaled, text_rect)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and not (self.volume_slider_active or self.brightness_slider_active):
                    self.selected_button_index = (self.selected_button_index - 1) % len(self.button_list)
                elif event.key == pygame.K_DOWN and not (self.volume_slider_active or self.brightness_slider_active):
                    self.selected_button_index = (self.selected_button_index + 1) % len(self.button_list)
                elif event.key == pygame.K_RETURN:
                    self.handle_button_click(self.button_list[self.selected_button_index])
                elif event.key == pygame.K_LEFT:
                    if self.volume_slider_active:
                        self.volume = max(0.0, self.volume - 0.05)
                        self.volume_button_top_width = int(self.volume_slider_width * self.volume)
                    if self.brightness_slider_active:
                        self.brightness = max(0.0, self.brightness - 0.05)
                        self.brightness_button_top_width = int(self.brightness_slider_width * self.brightness)
                elif event.key == pygame.K_RIGHT:
                    if self.volume_slider_active:
                        self.volume = min(1.0, self.volume + 0.05)
                        self.volume_button_top_width = int(self.volume_slider_width * self.volume)
                    if self.brightness_slider_active:
                        self.brightness = min(1.0, self.brightness + 0.05)
                        self.brightness_button_top_width = int(self.brightness_slider_width * self.brightness)

    def handle_button_click(self, label):
        if label == "Brightness":
            self.brightness_slider_active = not self.brightness_slider_active
        elif label == "Fullscreen":
            self.is_fullscreen = not getattr(self, 'is_fullscreen', False)
            pygame.display.set_mode(
                (SCREEN_WIDTH, SCREEN_HEIGHT),
                pygame.FULLSCREEN if self.is_fullscreen else 0
            )
        elif label == "Volume":
            self.volume_slider_active = not self.volume_slider_active
        elif label == "Back":
            self.active = False  # Go back to main menu

    def cleanup(self):
        """Free up resources used by the settings menu."""
        del self.font
        del self.clock
        del self.buttons
