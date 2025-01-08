import json
import pygame
import sys
import os
from os.path import join
from utils.settings import *

#
# Sub-Overlay Class for "Exit Game"
# with "Save Game?" or "Don't Save" 
#
class ExitPopup:
    def __init__(self, save_path='./saved_games/'):
        self.save_path = save_path
        self.active = True
        self.cotinuegame = False

        # Overlay animation
        self.overlay_scale = 0.0
        self.overlay_target_scale = 1.0
        self.overlay_animation_speed = 0.1

        # Button “pop” animation
        self.animation_speed = 0.2
        self.hover_scale = 1.2
        self.default_scale = 1.0

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

        # Buttons: "Save Game?" + "Don't Save"
        self.buttons = {
            "Save Game?": {
                "hover_scale": self.default_scale,
                "color": PURPLE  # (50, 50, 150)
            },
            "Don't Save": {
                "hover_scale": self.default_scale,
                "color": (90, 90, 180)
            }
        }
        self.button_list = list(self.buttons.keys())
        self.selected_button_index = 0
        self.screen = None

        # Colors for the small overlay
        self.overlay_color = (60, 40, 110)
        self.overlay_frame_color = (220, 220, 255)

    def save_game_data(self, save_info):
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
        Sub-overlay: "Save Game?" or "Don't Save"
        Centered and scaled relative to screen size.
        """
        self.screen = screen
        self.active = True
        self.overlay_scale = 0.0

        self.recalculate_button_sizes()

        while self.active:
            self.render_overlay()
            self.handle_events(save_info)
            self.clock.tick(FPS)
            pygame.display.update()

        return self.cotinuegame

    def recalculate_button_sizes(self):
        sw, sh = self.screen.get_size()

        # We'll make this sub-overlay ~25% width and ~25% height
        self.overlay_width = int(sw * 0.25)
        self.overlay_height = int(sh * 0.25)

        self.overlay_x = (sw - self.overlay_width) // 2
        self.overlay_y = (sh - self.overlay_height) // 2

        # We have 2 big buttons
        button_width = int(self.overlay_width * 0.8)
        button_height = int(self.overlay_height * 0.3)
        button_gap = 10

        total_height = (len(self.button_list) * button_height +
                        (len(self.button_list) - 1) * button_gap)

        center_x = self.overlay_x + self.overlay_width // 2
        center_y = self.overlay_y + self.overlay_height // 2
        start_y = center_y - total_height // 2

        for i, label in enumerate(self.button_list):
            top = start_y + i * (button_height + button_gap)
            left = center_x - button_width // 2

            self.buttons[label]["rect"] = pygame.Rect(left, top, button_width, button_height)
            self.buttons[label]["hover_scale"] = self.default_scale

    def handle_events(self, save_info):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                if self.active:
                    self.render_overlay()
        
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_button_index = (self.selected_button_index - 1) % len(self.button_list)
                elif event.key == pygame.K_DOWN:
                    self.selected_button_index = (self.selected_button_index + 1) % len(self.button_list)
                elif event.key == pygame.K_RETURN:
                    chosen = self.button_list[self.selected_button_index]
                    self.handle_button_click(chosen, save_info)

    def render_overlay(self):
        self.recalculate_button_sizes()
        self.overlay_scale += (self.overlay_target_scale - self.overlay_scale) * 1
        if abs(self.overlay_scale - self.overlay_target_scale) < 0.01:
            self.overlay_scale = self.overlay_target_scale

        cw = int(self.overlay_width * self.overlay_scale)
        ch = int(self.overlay_height * self.overlay_scale)

        overlay_rect = pygame.Rect(0, 0, cw, ch)
        cx = self.overlay_x + self.overlay_width // 2
        cy = self.overlay_y + self.overlay_height // 2
        overlay_rect.center = (cx, cy)

        pygame.draw.rect(self.screen, self.overlay_color, overlay_rect, border_radius=12)
        if cw > 5 and ch > 5:
            pygame.draw.rect(self.screen, self.overlay_frame_color, overlay_rect, width=3, border_radius=12)

        if self.overlay_scale > 0.2:
            self.render_buttons()

    def render_buttons(self):
        for idx, (label, data) in enumerate(self.buttons.items()):
            rect = data["rect"]
            hover_scale = data["hover_scale"]
            base_color = data["color"]

            if idx == self.selected_button_index:
                target_scale = self.hover_scale
            else:
                target_scale = self.default_scale

            data["hover_scale"] += (target_scale - hover_scale) * self.animation_speed
            new_scale = data["hover_scale"]

            sw = int(rect.width * new_scale)
            sh = int(rect.height * new_scale)
            scaled_rect = pygame.Rect(0, 0, sw, sh)
            scaled_rect.center = rect.center

            pygame.draw.rect(self.screen, base_color, scaled_rect, border_radius=8)

            scaled_font_size = int(36 * new_scale)
            text_font = pygame.font.Font(None, scaled_font_size)
            text_surf = text_font.render(label, True, WHITE)

            shadow_surf = text_font.render(label, True, BLACK)
            text_scale = 1.1
            tw = int(text_surf.get_width() * text_scale)
            th = int(text_surf.get_height() * text_scale)
            text_surf_up = pygame.transform.smoothscale(text_surf, (tw, th))
            shadow_surf_up = pygame.transform.smoothscale(shadow_surf, (tw, th))

            shadow_offset = 2
            shadow_rect = shadow_surf_up.get_rect(center=(scaled_rect.centerx + shadow_offset,
                                                          scaled_rect.centery + shadow_offset))
            text_rect = text_surf_up.get_rect(center=scaled_rect.center)

            self.screen.blit(shadow_surf_up, shadow_rect)
            self.screen.blit(text_surf_up, text_rect)

    def handle_button_click(self, label, save_info):
        if label == "Save Game?":
            self.save_game_data(save_info)
            self.active = False
            self.cotinuegame = False
        elif label == "Don't Save":
            print("Game not saved.")
            self.active = False
            self.cotinuegame = False


#
# Main Overlay Class: 
#   - "Settings"
#   - "Exit Game" -> triggers the sub overlay above
#   - "Continue"
#
class SaveGame:
    def __init__(self, save_path='./saved_games/'):
        pygame.init()
        self.save_path = save_path
        self.cotinuegame = False

        self.overlay_scale = 0.0
        self.overlay_target_scale = 1.0
        self.overlay_animation_speed = 0.1

        self.animation_speed = 0.2
        self.hover_scale = 1.2
        self.default_scale = 1.0

        self.active = True
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

        # The main overlay buttons
        self.buttons = {
            "Settings": {
                "hover_scale": self.default_scale,
                "color": PURPLE
            },
            "Exit Game": {
                "hover_scale": self.default_scale,
                "color": (90, 90, 180)
            },
            "Continue": {
                "hover_scale": self.default_scale,
                "color": LIGHT_PURPLE
            }
        }
        self.button_list = list(self.buttons.keys())
        self.selected_button_index = 0
        self.screen = None

        self.overlay_color = (60, 40, 110)       
        self.overlay_frame_color = (220, 220, 255)

        # We'll attach an actual SettingsMenu instance later if needed
        from ui.menusettings import SettingsMenu
        self.settings = None

    def run(self, screen, save_info):
        """
        Main overlay with "Settings", "Exit Game", "Continue"
        in the center of the screen.
        """
        self.screen = screen
        self.active = True
        self.overlay_scale = 0.0

        # For demonstration, instantiate your actual settings class
        from ui.menusettings import SettingsMenu
        self.settings = SettingsMenu(self.screen)

        self.recalculate_button_sizes()

        while self.active:
            self.render_overlay()
            self.handle_events(save_info)
            self.clock.tick(FPS)
            pygame.display.update()

        return self.cotinuegame

    def recalculate_button_sizes(self):
        sw, sh = self.screen.get_size()
        # overlay 30% x 40% of screen
        self.overlay_width = int(sw * 0.3)
        self.overlay_height = int(sh * 0.4)
        self.overlay_x = (sw - self.overlay_width) // 2
        self.overlay_y = (sh - self.overlay_height) // 2

        # bigger buttons
        button_width = int(self.overlay_width * 0.6)
        button_height = int(self.overlay_height * 0.2)
        button_gap = 8

        total_height = (len(self.button_list) * button_height
                        + (len(self.button_list) - 1) * button_gap)
        cx = self.overlay_x + self.overlay_width // 2
        cy = self.overlay_y + self.overlay_height // 2
        start_y = cy - total_height // 2

        for i, label in enumerate(self.button_list):
            top = start_y + i * (button_height + button_gap)
            left = cx - button_width // 2
            self.buttons[label]["rect"] = pygame.Rect(left, top, button_width, button_height)
            self.buttons[label]["hover_scale"] = self.default_scale

    def render_overlay(self):
        self.recalculate_button_sizes()
        self.overlay_scale += (self.overlay_target_scale - self.overlay_scale) * 1
        if abs(self.overlay_scale - self.overlay_target_scale) < 0.01:
            self.overlay_scale = self.overlay_target_scale

        cw = int(self.overlay_width * self.overlay_scale)
        ch = int(self.overlay_height * self.overlay_scale)

        overlay_rect = pygame.Rect(0, 0, cw, ch)
        cx = self.overlay_x + self.overlay_width // 2
        cy = self.overlay_y + self.overlay_height // 2
        overlay_rect.center = (cx, cy)

        pygame.draw.rect(self.screen, self.overlay_color, overlay_rect, border_radius=12)
        if cw > 5 and ch > 5:
            pygame.draw.rect(self.screen, self.overlay_frame_color, overlay_rect, width=3, border_radius=12)

        if self.overlay_scale > 0.2:
            self.render_buttons()

    def render_buttons(self):
        for idx, (label, data) in enumerate(self.buttons.items()):
            rect = data["rect"]
            hover_scale = data["hover_scale"]
            base_color = data["color"]

            if idx == self.selected_button_index:
                target_scale = self.hover_scale
            else:
                target_scale = self.default_scale

            data["hover_scale"] += (target_scale - hover_scale) * self.animation_speed
            new_scale = data["hover_scale"]

            scaled_width = int(rect.width * new_scale)
            scaled_height = int(rect.height * new_scale)
            scaled_rect = pygame.Rect(0, 0, scaled_width, scaled_height)
            scaled_rect.center = rect.center

            pygame.draw.rect(self.screen, base_color, scaled_rect, border_radius=8)

            scaled_font_size = int(36 * new_scale)
            text_font = pygame.font.Font(None, scaled_font_size)
            text_surf = text_font.render(label, True, WHITE)

            shadow_surf = text_font.render(label, True, BLACK)
            text_scale = 1.1
            tw = int(text_surf.get_width() * text_scale)
            th = int(text_surf.get_height() * text_scale)
            text_surf_up = pygame.transform.smoothscale(text_surf, (tw, th))
            shadow_surf_up = pygame.transform.smoothscale(shadow_surf, (tw, th))

            shadow_offset = 2
            shadow_rect = shadow_surf_up.get_rect(
                center=(scaled_rect.centerx + shadow_offset, scaled_rect.centery + shadow_offset)
            )
            text_rect = text_surf_up.get_rect(center=scaled_rect.center)

            self.screen.blit(shadow_surf_up, shadow_rect)
            self.screen.blit(text_surf_up, text_rect)

    def handle_events(self, save_info):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                if self.active:
                    self.render_overlay()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_button_index = (self.selected_button_index - 1) % len(self.button_list)
                elif event.key == pygame.K_DOWN:
                    self.selected_button_index = (self.selected_button_index + 1) % len(self.button_list)
                elif event.key == pygame.K_RETURN:
                    chosen_label = self.button_list[self.selected_button_index]
                    self.handle_button_click(chosen_label, save_info)

    def handle_button_click(self, label, save_info):
        if label == "Settings":
            print("Settings button clicked!")
            # Show your settings
            self.settings.run()

        elif label == "Exit Game":
            print("Exit Game -> open sub overlay with Save/Don't Save")
            exit_popup = ExitPopup()
            keep_playing = exit_popup.run(self.screen, save_info)
            # After sub popup returns:
            self.active = False
            # If keep_playing is True, user didn't confirm exit
            self.cotinuegame = (False if not keep_playing else True)

        elif label == "Continue":
            print("Continuing game...")
            self.active = False
            self.cotinuegame = True
