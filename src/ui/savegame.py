import os, json
from os.path import join
from utils.settings import *

#
# Sub-Overlay Class for "Exit Game"
# with "Save Game?" or "Don't Save"
#
class ExitPopup:
    def __init__(self, clock, save_path='./saved_games/'):
        self.save_path = save_path
        self.active = True
        self.cotinuegame = False

        # Overlay animation
        self.overlay_scale = 0.0
        self.overlay_target_scale = 1.0
        self.overlay_animation_speed = 0.1

        # Button "pop" animation
        self.animation_speed = 0.2
        self.hover_scale = 1.5
        self.default_scale = 1.0

        self.clock = clock
        self.font = pygame.font.Font(None, 36)

        # Load texture surface
        texture_image_surface = pygame.image.load("../assets/graphics/tilesets/terrain.png").convert_alpha()
        texture_coords_surface = (0, 0, 190, 190)  # Adjust as needed
        self.texture_surface = texture_image_surface.subsurface(pygame.Rect(*texture_coords_surface))

        # Buttons: "Save Game?" + "Don't Save"
        self.buttons = {
            "Save Game?": {
                "hover_scale": self.default_scale,
            },
            "Don't Save": {
                "hover_scale": self.default_scale,
            }
        }
        self.button_list = list(self.buttons.keys())
        self.selected_button_index = 0
        self.screen = None

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

        # Increase size of the overlay
        self.overlay_width = int(sw * 0.35)
        self.overlay_height = int(sh * 0.4)

        self.overlay_x = (sw - self.overlay_width) // 2
        self.overlay_y = (sh - self.overlay_height) // 2

        # Buttons' size and spacing
        button_width = int(self.overlay_width * 0.4)
        button_height = int(self.overlay_height * 0.25)
        button_gap = 8

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

    def render_overlay(self):
        self.recalculate_button_sizes()
        self.overlay_scale += (self.overlay_target_scale - self.overlay_scale) * 1
        if abs(self.overlay_scale - self.overlay_target_scale) < 0.01:
            self.overlay_scale = self.overlay_target_scale

        # Scale and center the texture surface
        cw = int(self.overlay_width)
        ch = int(self.overlay_height)
        scaled_surface = pygame.transform.scale(self.texture_surface, (cw, ch))
        cx = self.screen.get_width() // 2
        cy = self.screen.get_height() // 2

        rect = scaled_surface.get_rect(center=(cx, cy))
        self.screen.blit(scaled_surface, rect)

        if self.overlay_scale > 0.2:
            self.render_buttons()

    def render_buttons(self):
        for idx, (label, data) in enumerate(self.buttons.items()):
            rect = data["rect"]
            hover_scale = data["hover_scale"]

            # Adjust hover scaling
            if idx == self.selected_button_index:
                target_scale = self.hover_scale
            else:
                target_scale = self.default_scale

            data["hover_scale"] += (target_scale - hover_scale) * self.animation_speed
            new_scale = data["hover_scale"]

            # Scale the button
            sw = int(rect.width * new_scale)
            sh = int(rect.height * new_scale)
            scaled_rect = pygame.Rect(0, 0, sw, sh)
            scaled_rect.center = rect.center

            # Render the button texture
            texture_image = pygame.image.load("../assets/graphics/tilesets/extra.png").convert_alpha()
            button_texture_coords = (0, 256, 128, 128)  # Gray button
            button_texture = texture_image.subsurface(pygame.Rect(*button_texture_coords))
            scaled_texture = pygame.transform.scale(button_texture, (sw, sh))
            self.screen.blit(scaled_texture, scaled_rect)

            # Render button text
            text_font = pygame.font.Font(None, int(36 * new_scale))
            text_surf = text_font.render(label, True, WHITE)
            text_rect = text_surf.get_rect(center=scaled_rect.center)

            self.screen.blit(text_surf, text_rect)

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
                    chosen = self.button_list[self.selected_button_index]
                    self.handle_button_click(chosen, save_info)

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
    def __init__(self, clock, save_path='./saved_games/'):
        pygame.init()
        self.save_path = save_path
        self.cotinuegame = False
        self.clock = clock

        self.overlay_scale = 0.0
        self.overlay_target_scale = 1.0
        self.overlay_animation_speed = 0.1

        self.animation_speed = 0.2
        self.hover_scale = 2
        self.default_scale = 1.0

        self.active = True
        self.font = pygame.font.Font(None, 36)

        # Load texture surface (same as ExitPopup)
        texture_image_surface = pygame.image.load("../assets/graphics/tilesets/terrain.png").convert_alpha()
        texture_coords_surface = (0, 0, 190, 190)
        self.texture_surface = texture_image_surface.subsurface(pygame.Rect(*texture_coords_surface))

        # Load button textures
        texture_image = pygame.image.load("../assets/graphics/tilesets/extra.png").convert_alpha()
        texture_coords_gray = (0, 256, 128, 128)
        texture_coords_bronze = (320, 256, 128, 128)
        self.button_texture_gray = texture_image.subsurface(pygame.Rect(*texture_coords_gray))
        self.button_texture_bronze = texture_image.subsurface(pygame.Rect(*texture_coords_bronze))

        # The main overlay buttons
        self.buttons = {
            "Settings": {
                "hover_scale": self.default_scale,
                "texture": self.button_texture_gray
            },
            "Exit Game": {
                "hover_scale": self.default_scale,
                "texture": self.button_texture_bronze
            },
            "Continue": {
                "hover_scale": self.default_scale,
                "texture": self.button_texture_gray
            }
        }
        self.button_list = list(self.buttons.keys())
        self.selected_button_index = 0
        self.screen = None

    def run(self, screen, save_info):
        """
        Main overlay with "Settings", "Exit Game", "Continue"
        in the center of the screen.
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

        # Define dimensions for the overlay
        self.overlay_width = int(sw * 0.35)
        self.overlay_height = int(sh * 0.4)
        self.overlay_x = (sw - self.overlay_width) // 2
        self.overlay_y = (sh - self.overlay_height) // 2

        # Button sizes and spacing
        button_width = int(self.overlay_width * 0.5)
        button_height = int(self.overlay_height * 0.2)
        button_gap = 20

        # Smaller dimensions for the "Exit Game" button
        exit_button_width = int(self.overlay_width * 0.35)
        exit_button_height = int(self.overlay_height * 0.15)

        total_height = (len(self.button_list) * button_height +
                        (len(self.button_list) - 1) * button_gap)
        cx = self.overlay_x + self.overlay_width // 2
        cy = self.overlay_y + self.overlay_height // 2
        start_y = cy - total_height // 2

        for i, label in enumerate(self.button_list):
            top = start_y + i * (button_height + button_gap)
            left = cx - button_width // 2

            if label == "Exit Game":
                # Adjust size for the "Exit Game" button
                button_width = exit_button_width
                button_height = exit_button_height
                left = cx - button_width // 2
                top -= 5
                

            rect = pygame.Rect(left, top, button_width, button_height)
            self.buttons[label]["rect"] = rect
            self.buttons[label]["hover_scale"] = self.default_scale

            # Adjust text for "Exit Game"
            if label == "Exit Game":
                text_font = pygame.font.Font(None, int(22))
                text_color = (184, 115, 51)  # Bronze-like color
                text_surf = text_font.render(label, True, text_color)
                text_rect = text_surf.get_rect(midleft=(rect.left + 40, rect.centery))  # Shift text
                self.buttons[label]["text_rect"] = text_rect
                self.buttons[label]["text_surf"] = text_surf
            else:
                text_font = pygame.font.Font(None, 36)
                text_color = WHITE
                text_surf = text_font.render(label, True, text_color)
                text_rect = text_surf.get_rect(center=rect.center)
                self.buttons[label]["text_rect"] = text_rect
                self.buttons[label]["text_surf"] = text_surf

    def render_overlay(self):
        self.recalculate_button_sizes()
        self.overlay_scale += (self.overlay_target_scale - self.overlay_scale) * 1
        if abs(self.overlay_scale - self.overlay_target_scale) < 0.01:
            self.overlay_scale = self.overlay_target_scale

        # Scale and render the texture surface
        cw = int(self.overlay_width)
        ch = int(self.overlay_height)
        scaled_surface = pygame.transform.scale(self.texture_surface, (cw, ch))
        cx = self.screen.get_width() // 2
        cy = self.screen.get_height() // 2

        rect = scaled_surface.get_rect(center=(cx, cy))
        self.screen.blit(scaled_surface, rect)

        if self.overlay_scale > 0.2:
            self.render_buttons()

    def render_buttons(self):
        for idx, (label, data) in enumerate(self.buttons.items()):
            rect = data["rect"]
            hover_scale = data["hover_scale"]

            if idx == self.selected_button_index:
                target_scale = self.hover_scale
            else:
                target_scale = self.default_scale

            data["hover_scale"] += (target_scale - hover_scale) * self.animation_speed
            new_scale = data["hover_scale"]

            # Scale the button
            sw = int(rect.width * new_scale)
            sh = int(rect.height * new_scale)
            scaled_rect = pygame.Rect(0, 0, sw, sh)
            scaled_rect.center = rect.center

            texture = pygame.transform.scale(data["texture"], (sw, sh))
            self.screen.blit(texture, scaled_rect)

            # Render button text
            text_surf = data.get("text_surf")
            text_rect = data.get("text_rect")
            if text_surf and text_rect:
                self.screen.blit(text_surf, text_rect)

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

    def handle_button_click(self, label, save_info):
        if label == "Settings":
            print("Settings button clicked!")
        elif label == "Exit Game":
            print("Exit Game -> open sub overlay with Save/Don't Save")
            exit_popup = ExitPopup(self.clock)
            keep_playing = exit_popup.run(self.screen, save_info)
            self.active = False
            self.cotinuegame = (False if not keep_playing else True)
        elif label == "Continue":
            print("Continuing game...")
            self.active = False
            self.cotinuegame = True
