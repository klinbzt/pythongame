import sys
import pygame
from pygame.math import Vector2 as vector
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

        # Buttons
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

        # Slider flags
        self.volume_slider_active = False
        self.brightness_slider_active = False
        self.mouse_held = False

        self.recalculate_button_sizes()

        # Apply initial volume/brightness right away (if desired)
        pygame.mixer.music.set_volume(self.volume)
        try:
            pygame.display.set_gamma(self.brightness)
        except pygame.error:
            pass

    def recalculate_button_sizes(self):
        screen_width, screen_height = self.screen.get_size()
        button_width = int(screen_width * 0.3)
        button_height = int(screen_height * 0.1)
        button_gap = int(screen_height * 0.05)

        for idx, (label, data) in enumerate(self.buttons.items()):
            data["rect"] = pygame.Rect(
                (screen_width - button_width) // 2,
                (screen_height - button_height) // 2 + (idx - 1) * (button_height + button_gap),
                button_width,
                button_height,
            )

    def run(self):
        self.__init__(self.screen)
        while self.active:
            self.handle_events()
            self.render()
            self.clock.tick(FPS)
            pygame.display.update()
        self.cleanup()

    def render(self):
        self.recalculate_button_sizes()
        self.screen.fill(BLACK)
        mouse_pos = pygame.mouse.get_pos()

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

        screen_center = (self.screen.get_width() // 2, self.screen.get_height() // 2)
        for idx, (label, data) in enumerate(self.buttons.items()):
            if label == "Volume" and self.volume_slider_active:
                continue
            if label == "Brightness" and self.brightness_slider_active:
                continue

            rect = data["rect"]
            hover_scale = data["hover_scale"]
            y_offset = data["y_offset"]

            if idx == self.selected_button_index:
                target_hover_scale = self.hover_scale
                target_y_offset = 0
            else:
                target_hover_scale = self.default_scale
                target_y_offset = (idx - self.selected_button_index) * (
                    rect.height + int(self.screen.get_height() * 0.05)
                )

            if rect.collidepoint(mouse_pos):
                target_hover_scale = self.hover_scale

            data["hover_scale"] += (target_hover_scale - hover_scale) * self.animation_speed
            data["y_offset"] += (target_y_offset - y_offset) * self.animation_speed
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

            pygame.draw.rect(self.screen, PURPLE, scaled_rect, border_radius=20)
            if rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, self.hover_color, scaled_rect, width=4, border_radius=20)

            scaled_font_size = int(40 * hover_scale)
            text_font = pygame.font.Font(None, scaled_font_size)
            text_surface = text_font.render(label, True, WHITE)

            scale_factor = 1.2
            up_width = int(text_surface.get_width() * scale_factor)
            up_height = int(text_surface.get_height() * scale_factor)
            text_upscaled = pygame.transform.smoothscale(text_surface, (up_width, up_height))

            shadow_surface = text_font.render(label, True, (0, 0, 0))
            shadow_upscaled = pygame.transform.smoothscale(shadow_surface, (up_width, up_height))

            shadow_offset = 2
            shadow_rect = shadow_upscaled.get_rect(
                center=(scaled_rect.centerx + shadow_offset, scaled_rect.centery + shadow_offset)
            )
            self.screen.blit(shadow_upscaled, shadow_rect)

            text_rect = text_upscaled.get_rect(center=scaled_rect.center)
            self.screen.blit(text_upscaled, text_rect)

    def draw_slider(self, button_key, slider_value, label):
        rect_data = self.buttons[button_key]
        rect = rect_data["rect"]
        hover_scale = rect_data["hover_scale"]
        y_offset = rect_data["y_offset"]

        screen_center = (self.screen.get_width() // 2, self.screen.get_height() // 2)
        scaled_width = int(rect.width * hover_scale)
        scaled_height = int(rect.height * hover_scale)

        slider_rect = pygame.Rect(
            screen_center[0] - scaled_width // 2,
            screen_center[1] + y_offset - scaled_height // 2,
            scaled_width,
            scaled_height,
        )

        pygame.draw.rect(self.screen, PURPLE, slider_rect, border_radius=20)

        handle_width = int(scaled_width * slider_value)
        handle_rect = pygame.Rect(slider_rect.left, slider_rect.top, handle_width, slider_rect.height)
        pygame.draw.rect(self.screen, LIGHT_PURPLE, handle_rect, border_radius=20)

        text = self.font.render(label, True, WHITE)
        text_rect = text.get_rect(center=slider_rect.center)
        self.screen.blit(text, text_rect)

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
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

    def get_button_under_mouse(self, mouse_pos):
        for label, data in self.buttons.items():
            if data["rect"].collidepoint(mouse_pos):
                return label
        return None

    def adjust_slider_by_mouse(self, mouse_pos):
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
        rect_data = self.buttons[button_key]
        rect = rect_data["rect"]
        hover_scale = rect_data["hover_scale"]

        screen_center = (self.screen.get_width() // 2, self.screen.get_height() // 2)
        scaled_width = int(rect.width * hover_scale)
        scaled_left = screen_center[0] - scaled_width // 2
        scaled_right = scaled_left + scaled_width

        clamped_x = max(scaled_left, min(mouse_pos[0], scaled_right))
        return (clamped_x - scaled_left) / float(scaled_right - scaled_left)

    def adjust_slider(self, delta):
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
            self.active = False

    def cleanup(self):
        del self.font
        del self.clock
        del self.buttons
