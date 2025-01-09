import sys
import pygame
from pygame.math import Vector2 as vector
from utils.settings import *

# Define constants for better maintainability
BUTTON_FONT_SIZE = 40
TEXT_SCALE_FACTOR = 1.2
SHADOW_OFFSET = 2
MIN_HANDLE_WIDTH = 10
ANIMATION_SPEED = 0.2
HOVER_SCALE = 1.2
DEFAULT_SCALE = 0.85
BUTTON_BORDER_RADIUS = 20
SLIDER_BORDER_RADIUS = 20
FPS = 60  # Define FPS if not already defined in settings.py

class SettingsMenu:
    def __init__(self, screen):
        self.screen = screen
        self.active = True
        self.clock = pygame.time.Clock()

        # Font and colors
        self.font = pygame.font.Font(None, BUTTON_FONT_SIZE)
        self.text_color = BLACK
        self.button_color = WHITE
        self.hover_color = GRAY

        texture_image = pygame.image.load("../assets/graphics/tilesets/extra.png").convert_alpha()

        texture_coords = (0, 256, 128, 128)

        self.button_texture_gray = texture_image.subsurface(pygame.Rect(*texture_coords))
        # Preload resources
        self.background_image_original = pygame.image.load("../assets/graphics/intro/startupbrackground.png").convert()

        # Button properties
        self.hover_scale = HOVER_SCALE
        self.default_scale = DEFAULT_SCALE
        self.animation_speed = ANIMATION_SPEED

        # Buttons setup
        self.buttons = {
            "Brightness": {"hover_scale": self.default_scale, "y_offset": 0},
            "Fullscreen": {"hover_scale": self.default_scale, "y_offset": 0},
            "Volume":     {"hover_scale": self.default_scale, "y_offset": 0},
            "Back":       {"hover_scale": self.default_scale, "y_offset": 0},
        }
        self.selected_button_index = 0
        self.button_list = list(self.buttons.keys())

        # Use global defaults from settings.py
        self.volume = VOLUME
        self.brightness = BRIGHTNESS  # or just 1.0 if you don't have DEFAULT_BRIGHTNESS
        self.is_fullscreen = False

        # Slider flags
        self.volume_slider_active = False
        self.brightness_slider_active = False
        self.mouse_held = False

        # Cache screen size
        self.screen_width, self.screen_height = self.screen.get_size()

        # Pre-render static text surfaces
        self.pre_render_text()

        # Initialize cache for scaled text and shadows
        self.scaled_text_cache = {label: {} for label in self.button_list}

        # Calculate button sizes initially
        self.recalculate_button_sizes()

        # Apply initial volume/brightness right away (if desired)
        pygame.mixer.music.set_volume(self.volume)
        try:
            pygame.display.set_gamma(self.brightness)
        except pygame.error:
            pass

    def pre_render_text(self):
        """Pre-render the text surfaces for each button to optimize performance."""
        self.text_surfaces = {}
        for label in self.button_list:
            text_surface = self.font.render(label, True, WHITE)
            self.text_surfaces[label] = text_surface

    def recalculate_button_sizes(self):
        """Calculate and set the button rectangles based on screen size."""
        button_width = int(self.screen_width * 0.3)
        button_height = int(self.screen_height * 0.1)
        button_gap = int(self.screen_height * 0.05)

        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        for idx, label in enumerate(self.button_list):
            self.buttons[label]["rect"] = pygame.Rect(
                (self.screen_width - button_width) // 2,
                (self.screen_height - button_height) // 2 + (idx - 1) * (button_height + button_gap),
                button_width,
                button_height,
            )

    def run(self):
        """Main loop for the settings menu."""
        self.__init__(self.screen)

        while self.active:
            self.handle_events()
            self.render()
            self.clock.tick(FPS)
            pygame.display.update()
        self.cleanup()

    def render(self):
        """Render the settings menu."""
        self.screen.fill(BLACK)
        mouse_pos = pygame.mouse.get_pos()

        # Draw sliders if active
        if self.volume_slider_active:
            self.draw_slider(
                button_key="Volume",
                slider_value=self.volume,
                label=f"{int(self.volume * 100)}%"
            )

        if self.brightness_slider_active:
            self.draw_slider(
                button_key="Brightness",
                slider_value=self.brightness,
                label=f"{int(self.brightness * 100)}%"
            )

        screen_center = (self.screen_width // 2, self.screen_height // 2)
        for idx, label in enumerate(self.button_list):
            # Skip drawing the button if its slider is active
            if (label == "Volume" and self.volume_slider_active) or \
            (label == "Brightness" and self.brightness_slider_active):
                continue

            data = self.buttons[label]
            rect = data["rect"]
            hover_scale = data["hover_scale"]
            y_offset = data["y_offset"]

            # Determine target scale and y_offset based on selection and hover
            if idx == self.selected_button_index:
                target_hover_scale = self.hover_scale
                target_y_offset = 0
            else:
                target_hover_scale = self.default_scale
                target_y_offset = (idx - self.selected_button_index) * (
                    rect.height + int(self.screen_height * 0.05)
                )

            if rect.collidepoint(mouse_pos):
                target_hover_scale = self.hover_scale

            # Smoothly interpolate hover_scale and y_offset
            data["hover_scale"] += (target_hover_scale - hover_scale) * self.animation_speed
            data["y_offset"] += (target_y_offset - y_offset) * self.animation_speed

            # Calculate scaled rectangle
            scaled_width = int(rect.width * data["hover_scale"])
            scaled_height = int(rect.height * data["hover_scale"])
            scaled_rect = pygame.Rect(
                screen_center[0] - scaled_width // 2,
                screen_center[1] + data["y_offset"] - scaled_height // 2,
                scaled_width,
                scaled_height,
            )

            # Draw button texture
            scaled_texture = pygame.transform.scale(self.button_texture_gray, (scaled_width, scaled_height))
            self.screen.blit(scaled_texture, scaled_rect)

            # Draw text with shadow for buttons
            self.draw_text_with_shadow(label, scaled_rect)

    def draw_text_with_shadow(self, label, scaled_rect):
        """Helper method to draw text with a shadow effect for buttons."""
        # Get hover_scale for the label
        hover_scale = self.buttons[label]["hover_scale"]

        # Calculate scaled font size
        scaled_font_size = int(BUTTON_FONT_SIZE * hover_scale)

        # Ensure font size is at least 1
        scaled_font_size = max(1, scaled_font_size)

        # Check if the scaled font size is already in cache
        if scaled_font_size not in self.scaled_text_cache[label]:
            # Create a new font for the scaled size
            try:
                scaled_font = pygame.font.Font(None, scaled_font_size)
            except:
                # Fallback in case the font size is invalid
                scaled_font = self.font

            # Render the text
            text_surface = scaled_font.render(label, True, WHITE)

            # Scale the text surface
            up_width = int(text_surface.get_width() * TEXT_SCALE_FACTOR)
            up_height = int(text_surface.get_height() * TEXT_SCALE_FACTOR)
            text_upscaled = pygame.transform.smoothscale(text_surface, (up_width, up_height))

            # Render the shadow
            shadow_surface = scaled_font.render(label, True, (0, 0, 0))
            shadow_upscaled = pygame.transform.smoothscale(shadow_surface, (up_width, up_height))

            # Store in cache
            self.scaled_text_cache[label][scaled_font_size] = (text_upscaled, shadow_upscaled)
        else:
            text_upscaled, shadow_upscaled = self.scaled_text_cache[label][scaled_font_size]

        # Position the shadow
        shadow_rect = shadow_upscaled.get_rect(
            center=(scaled_rect.centerx + SHADOW_OFFSET, scaled_rect.centery + SHADOW_OFFSET)
        )
        self.screen.blit(shadow_upscaled, shadow_rect)

        # Position the text
        text_rect = text_upscaled.get_rect(center=scaled_rect.center)
        self.screen.blit(text_upscaled, text_rect)

    def draw_slider_label(self, label, scaled_rect):
        """Helper method to draw slider labels with a shadow effect."""
        # Render the slider label text
        text_surface = self.font.render(label, True, WHITE)

        # Scale the text surface
        up_width = int(text_surface.get_width() * TEXT_SCALE_FACTOR)
        up_height = int(text_surface.get_height() * TEXT_SCALE_FACTOR)
        text_upscaled = pygame.transform.smoothscale(text_surface, (up_width, up_height))

        # Render the shadow
        shadow_surface = self.font.render(label, True, (0, 0, 0))
        shadow_upscaled = pygame.transform.smoothscale(shadow_surface, (up_width, up_height))

        # Position the shadow
        shadow_rect = shadow_upscaled.get_rect(
            center=(scaled_rect.centerx + SHADOW_OFFSET, scaled_rect.centery + SHADOW_OFFSET)
        )
        self.screen.blit(shadow_upscaled, shadow_rect)

        # Position the text
        text_rect = text_upscaled.get_rect(center=scaled_rect.center)
        self.screen.blit(text_upscaled, text_rect)

    def draw_slider(self, button_key, slider_value, label):
        """Draw a slider for volume or brightness."""
        rect_data = self.buttons[button_key]
        rect = rect_data["rect"]
        hover_scale = rect_data["hover_scale"]
        y_offset = rect_data["y_offset"]

        screen_center = (self.screen_width // 2, self.screen_height // 2)
        scaled_width = int(rect.width * hover_scale)
        scaled_height = int(rect.height * hover_scale)

        slider_rect = pygame.Rect(
            screen_center[0] - scaled_width // 2,
            screen_center[1] + y_offset - scaled_height // 2,
            scaled_width,
            scaled_height,
        )

        # Draw slider background
        pygame.draw.rect(self.screen, PURPLE, slider_rect, border_radius=SLIDER_BORDER_RADIUS)

        # Draw slider handle
        handle_width = max(MIN_HANDLE_WIDTH, int(scaled_width * slider_value))
        handle_rect = pygame.Rect(slider_rect.left, slider_rect.top, handle_width, slider_rect.height)
        pygame.draw.rect(self.screen, LIGHT_PURPLE, handle_rect, border_radius=SLIDER_BORDER_RADIUS)

        # Draw slider label with shadow using the new method
        self.draw_slider_label(label, slider_rect)

    def handle_events(self):
        """Handle all incoming events."""
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if not (self.volume_slider_active or self.brightness_slider_active):
                    if event.key == pygame.K_UP:
                        self.selected_button_index = (self.selected_button_index - 1) % len(self.button_list)
                    elif event.key == pygame.K_DOWN:
                        self.selected_button_index = (self.selected_button_index + 1) % len(self.button_list)
                if event.key == pygame.K_RETURN:
                    self.handle_button_click(self.button_list[self.selected_button_index])
                elif event.key == pygame.K_LEFT:
                    self.adjust_slider(-0.05)
                elif event.key == pygame.K_RIGHT:
                    self.adjust_slider(+0.05)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.mouse_held = True
                    clicked_button = self.get_button_under_mouse(mouse_pos)
                    if clicked_button:
                        self.handle_button_click(clicked_button)
                elif event.button == 4:  # Mouse wheel up
                    self.adjust_slider(+0.05)
                elif event.button == 5:  # Mouse wheel down
                    self.adjust_slider(-0.05)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_held = False

            elif event.type == pygame.MOUSEMOTION:
                if self.mouse_held:
                    if self.volume_slider_active or self.brightness_slider_active:
                        self.adjust_slider_by_mouse(mouse_pos)

            elif event.type == pygame.VIDEORESIZE:
                # Handle window resizing by recalculating button sizes
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.screen_width, self.screen_height = self.screen.get_size()
                self.recalculate_button_sizes()

    def get_button_under_mouse(self, mouse_pos):
        """Return the label of the button under the mouse, if any."""
        for label, data in self.buttons.items():
            if data["rect"].collidepoint(mouse_pos):
                return label
        return None

    def adjust_slider_by_mouse(self, mouse_pos):
        """Adjust the active slider based on mouse position."""
        if self.volume_slider_active:
            self.volume = self.get_slider_value("Volume", mouse_pos)
            pygame.mixer.music.set_volume(self.volume)
        elif self.brightness_slider_active:
            self.brightness = self.get_slider_value("Brightness", mouse_pos)
            try:
                pygame.display.set_gamma(self.brightness)
            except pygame.error:
                pass

    def get_slider_value(self, button_key, mouse_pos):
        """Calculate the slider value based on mouse position."""
        rect_data = self.buttons[button_key]
        rect = rect_data["rect"]
        hover_scale = rect_data["hover_scale"]

        screen_center = (self.screen_width // 2, self.screen_height // 2)
        scaled_width = int(rect.width * hover_scale)
        scaled_left = screen_center[0] - scaled_width // 2
        scaled_right = scaled_left + scaled_width

        clamped_x = max(scaled_left, min(mouse_pos[0], scaled_right))
        return (clamped_x - scaled_left) / float(scaled_right - scaled_left) if scaled_right != scaled_left else 0

    def adjust_slider(self, delta):
        """Adjust the active slider by a delta value."""
        if self.volume_slider_active:
            self.volume = max(0.0, min(1.0, self.volume + delta))
            pygame.mixer.music.set_volume(self.volume)
        if self.brightness_slider_active:
            self.brightness = max(0.0, min(1.0, self.brightness + delta))
            try:
                pygame.display.set_gamma(self.brightness)
            except pygame.error:
                pass

    def handle_button_click(self, label):
        """Handle actions based on which button was clicked."""
        if label == "Brightness":
            self.brightness_slider_active = not self.brightness_slider_active
            # Deactivate other sliders to prevent multiple sliders active at the same time
            if self.brightness_slider_active:
                self.volume_slider_active = False
        elif label == "Fullscreen":
            self.is_fullscreen = not getattr(self, 'is_fullscreen', False)
            pygame.display.set_mode(
                (self.screen_width, self.screen_height),
                pygame.FULLSCREEN if self.is_fullscreen else pygame.RESIZABLE
            )
        elif label == "Volume":
            self.volume_slider_active = not self.volume_slider_active
            # Deactivate other sliders to prevent multiple sliders active at the same time
            if self.volume_slider_active:
                self.brightness_slider_active = False
        elif label == "Back":
            self.active = False

    def cleanup(self):
        """Clean up resources when the menu is closed."""
        del self.font
        del self.clock
        self.buttons.clear()
        self.text_surfaces.clear()
        self.scaled_text_cache.clear()
