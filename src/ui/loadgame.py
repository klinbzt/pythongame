import os, json
from utils.settings import *
from ui.animatedtext import TextDisplay


class LoadGame:
    def __init__(self, screen):
        self.screen = screen
        self.active = True
        self.back = False
        self.getoldsave = False

        self.background_image_original = pygame.image.load("../assets/graphics/tilesets/new_background.png").convert()

        self.saved_games_dir = "saved_games"

        texture_image = pygame.image.load("../assets/graphics/tilesets/extra.png").convert_alpha()
        
        texture_coords_gray = (0, 256, 128, 128)
        texture_coords_bronze = (320, 256, 128, 128)
        texture_coords_delete_bronze = (515, 190, 64, 64)

        self.button_texture_gray = texture_image.subsurface(pygame.Rect(*texture_coords_gray))
        self.button_texture_bronze = texture_image.subsurface(pygame.Rect(*texture_coords_bronze))
        self.button_texture_delete_bronze = texture_image.subsurface(pygame.Rect(*texture_coords_delete_bronze))

        self.font = pygame.font.Font(None, 40)
        self.text_color = WHITE
        self.hover_scale = 1.35
        self.default_scale = 1.0

        self.shake_offset = 0
        self.shake_direction = 1
        self.shake_amplitude = 5
        self.shake_speed = 0.5

        self.saved_game_buttons = []
        self.selected_button_index = 0
        self.on_delete_button = False

        self.back_button = {"label": "Back", "hover_scale": self.default_scale, "y_offset": 0}

        self.clock = pygame.time.Clock()

        self.load_saved_games()

        # Confirmation text (initially None)
        self.confirmation_text_display = None

    def reset_confirmation_text(self):
        """Reset the confirmation text display."""
        self.confirmation_text_display = TextDisplay(
            position=(SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT - 110),
            text="[Are you sure you want to delete this saved game?]                    [Press Enter to confirm.]",
            font=self.font,
            screen=self.screen,
            max_chars=50,
            line_spacing=10
        )


    def load_saved_games(self):
        if not os.path.exists(self.saved_games_dir):
            os.makedirs(self.saved_games_dir)

        saved_files = [file for file in os.listdir(self.saved_games_dir) if file.endswith(".json")]
        self.saved_game_buttons = [{"label": file, "hover_scale": self.default_scale, "y_offset": 0} for file in saved_files]

    def render(self):
        self.screen.blit(self.background_image_original, (0, 0))

        if not self.saved_game_buttons:
            no_games_text = self.font.render("No saved games available.", True, WHITE)
            text_rect = no_games_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(no_games_text, text_rect)
            return None

        screen_center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        button_gap = int(SCREEN_HEIGHT * 0.05)
        button_height = int(SCREEN_HEIGHT * 0.1)
        button_width_factor = 0.25
        back_button_width_factor = 0.2

        for idx, button in enumerate(self.saved_game_buttons + [self.back_button]):
            is_back_button = idx == len(self.saved_game_buttons)
            is_selected = idx == self.selected_button_index and not self.on_delete_button
            target_scale = self.hover_scale if is_selected else self.default_scale
            target_offset = 0 if is_selected else (idx - self.selected_button_index) * (button_height + button_gap)

            button["hover_scale"] += (target_scale - button["hover_scale"]) * 0.2
            button["y_offset"] += (target_offset - button["y_offset"]) * 0.2

            hover_scale = button["hover_scale"]
            y_offset = button["y_offset"]

            shake_offset = 0
            if idx < len(self.saved_game_buttons) and idx == self.selected_button_index and self.on_delete_button:
                self.shake_offset += self.shake_speed * self.shake_direction
                if abs(self.shake_offset) >= self.shake_amplitude:
                    self.shake_direction *= -1
                shake_offset = int(self.shake_offset)

            width_factor = back_button_width_factor if is_back_button else button_width_factor
            scaled_width = int(SCREEN_WIDTH * width_factor * hover_scale)
            scaled_height = int(button_height * hover_scale)
            button_rect = pygame.Rect(
                screen_center[0] - scaled_width // 2 + shake_offset,
                screen_center[1] + y_offset - scaled_height // 2,
                scaled_width,
                scaled_height,
            )

            texture = (
                pygame.transform.scale(self.button_texture_bronze, (scaled_width, scaled_height))
                if is_back_button
                else pygame.transform.scale(self.button_texture_gray, (scaled_width, scaled_height))
            )
            self.screen.blit(texture, button_rect)

            text_color = (184, 115, 51) if is_back_button else WHITE
            text = self.font.render(button["label"], True, text_color)
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)

            if idx < len(self.saved_game_buttons):
                delete_is_selected = idx == self.selected_button_index and self.on_delete_button
                delete_button_scale = self.hover_scale if delete_is_selected else self.default_scale

                delete_button_size = int(scaled_height * 0.8 * delete_button_scale)
                delete_button_rect = pygame.Rect(
                    button_rect.right + 10,
                    button_rect.centery - delete_button_size // 2,
                    delete_button_size,
                    delete_button_size,
                )

                delete_texture = pygame.transform.scale(self.button_texture_delete_bronze, (delete_button_size, delete_button_size))
                self.screen.blit(delete_texture, delete_button_rect)
                button["delete_rect"] = delete_button_rect

        if self.on_delete_button:
            if not self.confirmation_text_display:
                self.reset_confirmation_text()
            self.confirmation_text_display.update()
            self.confirmation_text_display.render()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if self.on_delete_button:
                        self.on_delete_button = False
                    else:
                        self.selected_button_index = (self.selected_button_index - 1) % (len(self.saved_game_buttons) + 1)
                        self.confirmation_text_display = None
                elif event.key == pygame.K_DOWN:
                    if self.on_delete_button:
                        self.on_delete_button = False
                    else:
                        self.selected_button_index = (self.selected_button_index + 1) % (len(self.saved_game_buttons) + 1)
                        self.confirmation_text_display = None
                elif event.key == pygame.K_RIGHT:
                    if self.selected_button_index < len(self.saved_game_buttons):
                        self.on_delete_button = not self.on_delete_button
                        if self.on_delete_button:
                            self.reset_confirmation_text()
                elif event.key == pygame.K_LEFT:
                    if self.on_delete_button:
                        self.on_delete_button = False
                elif event.key == pygame.K_RETURN:
                    if self.on_delete_button:
                        self.delete_game(self.saved_game_buttons[self.selected_button_index]["label"])
                    elif self.selected_button_index == len(self.saved_game_buttons):
                        self.active = False
                        self.back = True
                    else:
                        self.load_game(self.saved_game_buttons[self.selected_button_index]["label"])
                elif event.key == pygame.K_BACKSPACE:
                    self.active = True
                    self.back = True

    def load_game(self, save_file):
        save_path = os.path.join(self.saved_games_dir, save_file)
        try:
            with open(save_path, "r") as file:
                self.loaded_save_data = json.load(file)
            self.getoldsave = True
            self.active = False
        except Exception as e:
            print(f"Error loading game {save_file}: {e}")
            return None

    def delete_game(self, save_file):
        save_path = os.path.join(self.saved_games_dir, save_file)
        try:
            os.remove(save_path)
            print(f"Deleted save file: {save_file}")
            self.load_saved_games()
        except Exception as e:
            print(f"Error deleting game {save_file}: {e}")

    def run(self):
        self.__init__(self.screen, self.level_manager)

        while self.active:
            self.handle_events()
            self.render()
            self.clock.tick(FPS)
            pygame.display.update()

        if self.back:
            return True

        return False
