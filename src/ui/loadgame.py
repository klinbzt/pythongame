import pygame
import sys
import os
import json
from utils.settings import *


class LoadGame:
    def __init__(self, screen, level_manager):
        self.screen = screen
        self.level_manager = level_manager
        self.active = True
        self.back = False
        self.getoldsave = False

        self.saved_games_dir = "saved_games"

        # Font and colors
        self.font = pygame.font.Font(None, 40)
        self.text_color = WHITE
        self.button_color = (45, 45, 45)
        self.hover_color = (60, 60, 60)
        self.delete_color = (255, 0, 0)
        self.delete_hover_color = (255, 50, 50)  # Brighter red when delete is selected

        # Animation settings
        self.animation_speed = 0.2
        self.hover_scale = 1.2
        self.default_scale = 1.0

        # Button properties
        self.saved_game_buttons = []
        self.selected_button_index = 0
        self.on_delete_button = False  # Tracks if the red delete button is selected

        # Back button
        self.back_button = {"label": "Back", "hover_scale": self.default_scale, "y_offset": 0}

        # Clock for framerate
        self.clock = pygame.time.Clock()

        self.load_saved_games()

    def load_saved_games(self):
        """Load all saved games and initialize buttons."""
        if not os.path.exists(self.saved_games_dir):
            os.makedirs(self.saved_games_dir)

        saved_files = [file for file in os.listdir(self.saved_games_dir) if file.endswith(".json")]
        self.saved_game_buttons = [{"label": file, "hover_scale": self.default_scale, "y_offset": 0} for file in saved_files]

    def release_resources(self):
        """Free up resources when finished."""
        self.font = None
        self.clock = None
        self.saved_game_buttons.clear()

    def run(self):
        """Main loop of the load game screen."""
        self.__init__(self.screen, self.level_manager)

        while self.active:
            self.handle_events()
            self.render()
            self.clock.tick(FPS)
            pygame.display.update()

        # Free up resources once the loop ends
        self.release_resources()
        return self.back

    def render(self):
        """Render buttons with animations."""
        self.screen.fill(BLACK)

        if not self.saved_game_buttons:
            # Display no games available
            no_games_text = self.font.render("No saved games available.", True, WHITE)
            text_rect = no_games_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(no_games_text, text_rect)
            return

        # Calculate layout properties
        screen_center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        button_gap = int(SCREEN_HEIGHT * 0.05)
        button_height = int(SCREEN_HEIGHT * 0.1)

        for idx, button in enumerate(self.saved_game_buttons + [self.back_button]):
            is_selected = idx == self.selected_button_index and not self.on_delete_button
            target_scale = self.hover_scale if is_selected else self.default_scale
            target_offset = 0 if is_selected else (idx - self.selected_button_index) * (button_height + button_gap)

            # Smooth animations
            button["hover_scale"] += (target_scale - button["hover_scale"]) * self.animation_speed
            button["y_offset"] += (target_offset - button["y_offset"]) * self.animation_speed

            hover_scale = button["hover_scale"]
            y_offset = button["y_offset"]

            # Calculate button size and position
            scaled_width = int(SCREEN_WIDTH * 0.3 * hover_scale)
            scaled_height = int(button_height * hover_scale)
            button_rect = pygame.Rect(
                screen_center[0] - scaled_width // 2,
                screen_center[1] + y_offset - scaled_height // 2,
                scaled_width,
                scaled_height,
            )

            # Draw button
            color = self.hover_color if is_selected else self.button_color
            pygame.draw.rect(self.screen, color, button_rect, border_radius=15)

            # Render button label
            text = self.font.render(button["label"], True, WHITE)
            text_rect = text.get_rect(midleft=(button_rect.left + 10, button_rect.centery))
            self.screen.blit(text, text_rect)

            # Draw delete button next to each save button
            if idx < len(self.saved_game_buttons):
                delete_is_selected = idx == self.selected_button_index and self.on_delete_button
                delete_button_scale = self.hover_scale if delete_is_selected else self.default_scale

                delete_button_size = int(scaled_height * 0.6 * delete_button_scale)
                delete_button_rect = pygame.Rect(
                    button_rect.right + 10,
                    button_rect.centery - delete_button_size // 2,
                    delete_button_size,
                    delete_button_size,
                )

                delete_color = self.delete_hover_color if delete_is_selected else self.delete_color
                pygame.draw.rect(self.screen, delete_color, delete_button_rect, border_radius=8)

                # Store delete button rect for collision detection
                button["delete_rect"] = delete_button_rect

    def handle_events(self):
        """Handle keyboard and mouse events."""
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
                elif event.key == pygame.K_DOWN:
                    if self.on_delete_button:
                        self.on_delete_button = False
                    else:
                        self.selected_button_index = (self.selected_button_index + 1) % (len(self.saved_game_buttons) + 1)
                elif event.key == pygame.K_RIGHT:
                    if self.selected_button_index < len(self.saved_game_buttons):
                        self.on_delete_button = not self.on_delete_button
                elif event.key == pygame.K_LEFT:
                    if self.on_delete_button:
                        self.on_delete_button = False
                elif event.key == pygame.K_RETURN:
                    if self.on_delete_button:
                        self.delete_game(self.saved_game_buttons[self.selected_button_index]["label"])
                    elif self.selected_button_index == len(self.saved_game_buttons):
                        self.active = False  # Back button selected
                        self.back = True
                    else:
                        self.load_game(self.saved_game_buttons[self.selected_button_index]["label"])
                elif event.key == pygame.K_BACKSPACE:
                    self.active = False
                    self.back = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_pos = event.pos
                    for idx, button in enumerate(self.saved_game_buttons):
                        button_rect = pygame.Rect(
                            SCREEN_WIDTH // 2 - (SCREEN_WIDTH * 0.3 * button["hover_scale"] // 2),
                            SCREEN_HEIGHT // 2 + button["y_offset"] - (SCREEN_HEIGHT * 0.1 * button["hover_scale"] // 2),
                            SCREEN_WIDTH * 0.3 * button["hover_scale"],
                            SCREEN_HEIGHT * 0.1 * button["hover_scale"]
                        )
                        if button_rect.collidepoint(mouse_pos):
                            self.load_game(button["label"])
                        elif "delete_rect" in button and button["delete_rect"].collidepoint(mouse_pos):
                            self.delete_game(button["label"])

    def load_game(self, save_file):
        """Load a selected game."""
        save_path = os.path.join(self.saved_games_dir, save_file)
        try:
            with open(save_path, "r") as file:
                save_data = json.load(file)
            self.level_manager.load_save_info(save_data)
            self.active = False
            self.getoldsave = True
        except Exception as e:
            print(f"Error loading game {save_file}: {e}")

    def delete_game(self, save_file):
        """Delete the selected save file."""
        save_path = os.path.join(self.saved_games_dir, save_file)
        try:
            os.remove(save_path)
            print(f"Deleted save file: {save_file}")
            self.load_saved_games()  # Refresh the button list
        except Exception as e:
            print(f"Error deleting game {save_file}: {e}")
