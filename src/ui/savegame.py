import json
import pygame
import sys
import os
from os.path import join
from utils.settings import *

class SaveGame:
    def __init__(self, save_path='./saved_games/'):
        pygame.init()
        self.save_path = save_path
        self.cotinuegame = False

        # Overlay scales 0% -> 100%
        self.overlay_scale = 0.0
        self.overlay_target_scale = 1.0
        self.overlay_animation_speed = 0.1

        # Button “pop” animation
        self.animation_speed = 0.2
        self.hover_scale = 1.2
        self.default_scale = 1.0

        self.active = True
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

        # Buttons
        self.buttons = {
            "Save Game?": {
                "hover_scale": self.default_scale,
                "color": PURPLE  # (50, 50, 150)
            },
            "Don't Save": {
                "hover_scale": self.default_scale,
                "color": (90, 90, 180)
            },
            "Continue": {
                "hover_scale": self.default_scale,
                "color": LIGHT_PURPLE  # (50, 50, 200)
            }
        }
        self.button_list = list(self.buttons.keys())
        self.selected_button_index = 0
        self.screen = None

        # Overlay colors
        self.overlay_color = (60, 40, 110)       # Darker purple background
        self.overlay_frame_color = (220, 220, 255)  # Light pastel frame

    def save(self, save_info):
        save_name = save_info["planet_name"]
        save_filename = f"{save_name}_{save_info['current_planet_index']}_{save_info['current_level_index']}.json"
        save_file = join(self.save_path, save_filename)

        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        with open(save_file, 'w') as file:
            json.dump(save_info, file, indent=4)

        print(f"Game saved in {save_filename}!")

    def run(self, screen, save_info):
        """
        Show a popup overlay with larger stationary buttons
        that only 'pop' in size when selected.
        """
        self.screen = screen
        self.active = True
        self.overlay_scale = 0.0  # reset

        # Setup initial positions
        self.recalculate_button_sizes()

        while self.active:
            self.render_overlay()
            self.handle_events(save_info)
            self.clock.tick(FPS)
            pygame.display.update()

        return self.cotinuegame

    def recalculate_button_sizes(self):
        """
        Make the overlay relative to screen size, then define
        bigger buttons (80% overlay width, ~15% overlay height).
        """
        screen_width, screen_height = self.screen.get_size()

        # Overlay = 30% of screen width, 40% of screen height
        self.overlay_width = int(screen_width * 0.3)
        self.overlay_height = int(screen_height * 0.4)

        # Center the overlay
        self.overlay_x = (screen_width - self.overlay_width) // 2
        self.overlay_y = (screen_height - self.overlay_height) // 2

        # Larger buttons
        button_width = int(self.overlay_width * 0.6)      # 80% of overlay width
        button_height = int(self.overlay_height * 0.2)   # 20% of overlay height
        button_gap = 8

        total_height = len(self.button_list)*button_height + (len(self.button_list)-1)*button_gap
        overlay_center_x = self.overlay_x + self.overlay_width // 2
        overlay_center_y = self.overlay_y + self.overlay_height // 2
        start_y = overlay_center_y - total_height // 2

        for i, label in enumerate(self.button_list):
            top = start_y + i * (button_height + button_gap)
            left = overlay_center_x - button_width // 2

            self.buttons[label]["rect"] = pygame.Rect(left, top, button_width, button_height)
            self.buttons[label]["hover_scale"] = self.default_scale

    def handle_events(self, save_info):
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
                    chosen_label = self.button_list[self.selected_button_index]
                    self.handle_button_click(chosen_label, save_info)

    def render_overlay(self):
        """
        Scale the overlay from 0 to 100%, draw a frame,
        then draw the bigger stationary buttons with 'pop' on selection.
        """
        self.overlay_scale += (self.overlay_target_scale - self.overlay_scale) * self.overlay_animation_speed
        if abs(self.overlay_scale - self.overlay_target_scale) < 0.01:
            self.overlay_scale = self.overlay_target_scale

        current_width = int(self.overlay_width * self.overlay_scale)
        current_height = int(self.overlay_height * self.overlay_scale)

        overlay_rect = pygame.Rect(0, 0, current_width, current_height)
        center_x = self.overlay_x + self.overlay_width // 2
        center_y = self.overlay_y + self.overlay_height // 2
        overlay_rect.center = (center_x, center_y)

        pygame.draw.rect(self.screen, self.overlay_color, overlay_rect, border_radius=12)

        if current_width > 5 and current_height > 5:
            pygame.draw.rect(self.screen, self.overlay_frame_color, overlay_rect, width=3, border_radius=12)

        if self.overlay_scale > 0.2:
            self.render_buttons()

    def render_buttons(self):
        """
        Buttons remain stationary. They scale up on hover.
        """
        for idx, (label, data) in enumerate(self.buttons.items()):
            rect = data["rect"]
            hover_scale = data["hover_scale"]
            base_color = data["color"]

            # Decide scale based on whether it's selected
            if idx == self.selected_button_index:
                target_scale = self.hover_scale
            else:
                target_scale = self.default_scale

            data["hover_scale"] += (target_scale - hover_scale) * self.animation_speed
            new_scale = data["hover_scale"]

            # Compute scaled rect, centered on original rect
            scaled_width = int(rect.width * new_scale)
            scaled_height = int(rect.height * new_scale)
            scaled_rect = pygame.Rect(0, 0, scaled_width, scaled_height)
            scaled_rect.center = rect.center

            # Draw button background
            pygame.draw.rect(self.screen, base_color, scaled_rect, border_radius=8)

            # Label
            scaled_font_size = int(36 * new_scale)
            text_font = pygame.font.Font(None, scaled_font_size)
            text_surf = text_font.render(label, True, WHITE)

            # Shadow
            shadow_surf = text_font.render(label, True, BLACK)
            text_scale = 1.1
            tw = int(text_surf.get_width() * text_scale)
            th = int(text_surf.get_height() * text_scale)
            text_surf_up = pygame.transform.smoothscale(text_surf, (tw, th))
            shadow_surf_up = pygame.transform.smoothscale(shadow_surf, (tw, th))

            # Position text
            shadow_offset = 2
            shadow_rect = shadow_surf_up.get_rect(
                center=(scaled_rect.centerx + shadow_offset,
                        scaled_rect.centery + shadow_offset)
            )
            text_rect = text_surf_up.get_rect(center=scaled_rect.center)

            self.screen.blit(shadow_surf_up, shadow_rect)
            self.screen.blit(text_surf_up, text_rect)

    def handle_button_click(self, label, save_info):
        if label == "Save Game?":
            self.save(save_info)
            self.active = False
            self.cotinuegame = False
        elif label == "Don't Save":
            print("Game not saved.")
            self.active = False
            self.cotinuegame = False
        elif label == "Continue":
            print("Continuing game...")
            self.active = False
            self.cotinuegame = True
