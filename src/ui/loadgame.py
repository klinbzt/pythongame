import json
import pygame
import os
import sys
from utils.settings import *
from ui.savegame import SaveGame
from levels.level_manager import LevelManager


class LoadGame:
    def __init__(self, screen, level_manager):
        self.screen = screen
        self.active = True
        self.back = False
        self.getoldsave = False
        self.clock = pygame.time.Clock()

        self.saved_games_dir = "saved_games"  # Directory where saved games are stored

        # Button dimensions and gap
        self.button_width = 300
        self.button_height = 50
        self.button_gap = 20

        # Font and colors
        self.font = pygame.font.Font(None, 30)
        self.text_color = BLACK
        self.button_color = WHITE
        self.hover_color = WHITE

        # Define the rectangles for displaying saved game names
        self.saved_game_buttons = []
        self.delete_buttons = []  # Store delete button positions and related data
        self.back_button_rect = None

        # Confirmation dialog data
        self.confirm_delete = False
        self.selected_game = None
        self.delete_popup_rect = None

        # Initialize LevelManager
        self.level_manager = level_manager

    def load_saved_games(self):
        if not os.path.exists(self.saved_games_dir):
            os.makedirs(self.saved_games_dir)

        saved_files = [
            file for file in os.listdir(self.saved_games_dir) if file.endswith(".json")
        ]

        if not saved_files:
            self.no_games_message = "No saved games available."
        else:
            self.no_games_message = None
            for i, filename in enumerate(saved_files):
                rect_x = (SCREEN_WIDTH - self.button_width) // 2
                rect_y = (SCREEN_HEIGHT - len(saved_files) * (self.button_height + self.button_gap)) // 2 + i * (self.button_height + self.button_gap)
                self.saved_game_buttons.append((filename, pygame.Rect(rect_x, rect_y, self.button_width, self.button_height)))

        # Back button at the bottom
        back_rect_x = (SCREEN_WIDTH - self.button_width) // 2
        back_rect_y = SCREEN_HEIGHT - (self.button_height + self.button_gap)
        self.back_button_rect = pygame.Rect(back_rect_x, back_rect_y, self.button_width, self.button_height)

    def run(self):
        self.active = True
        
        while self.active:
            self.load_saved_games()
            self.handle_events()
            self.render()
            self.clock.tick(FPS)
            pygame.display.update()

        if self.back:
            return True
        return False

    def render(self):
        self.screen.fill(BLACK)

        if self.no_games_message:
            no_games_text = self.font.render(self.no_games_message, True, WHITE)
            text_rect = no_games_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(no_games_text, text_rect)
        else:
            for label, rect in self.saved_game_buttons:
                pygame.draw.rect(self.screen, self.button_color, rect)  # Button background
                text = self.font.render(label, True, self.text_color)
                text_rect = text.get_rect(center=rect.center)
                self.screen.blit(text, text_rect)

                # Render delete button (Red square) to the right of each saved game button
                delete_button_rect = pygame.Rect(rect.right + 10, rect.top, self.button_height, self.button_height)
                self.delete_buttons.append((label, delete_button_rect))
                pygame.draw.rect(self.screen, (255, 0, 0), delete_button_rect)
                pygame.draw.line(self.screen, (255, 255, 255), (delete_button_rect.x + 10, delete_button_rect.y + 10), (delete_button_rect.x + delete_button_rect.width - 10, delete_button_rect.y + delete_button_rect.height - 10), 3)
                pygame.draw.line(self.screen, (255, 255, 255), (delete_button_rect.x + delete_button_rect.width - 10, delete_button_rect.y + 10), (delete_button_rect.x + 10, delete_button_rect.y + delete_button_rect.height - 10), 3)

        # Render back button
        pygame.draw.rect(self.screen, self.button_color, self.back_button_rect)
        back_text = self.font.render("<-", True, self.text_color)
        back_text_rect = back_text.get_rect(center=self.back_button_rect.center)
        self.screen.blit(back_text, back_text_rect)

        if self.confirm_delete:
            self.render_confirmation_popup()

    def render_confirmation_popup(self):
        self.screen.fill(BLACK)
        # Calculate the text width and height
        message = f"Are you sure you want to delete {self.selected_game}?"
        text_surface = self.font.render(message, True, (255, 255, 255))
        text_width, text_height = text_surface.get_size()

        # Dynamically adjust the popup size based on text
        popup_width = max(300, text_width + 40)  # Ensure minimum width
        popup_height = max(200, text_height + 80)  # Ensure enough height for text and buttons

        self.delete_popup_rect = pygame.Rect((SCREEN_WIDTH - popup_width) // 2, (SCREEN_HEIGHT - popup_height) // 2, popup_width, popup_height)

        # Drawing rounded corners and gradient background for the popup
        pygame.draw.rect(self.screen, (0, 0, 0), self.delete_popup_rect, border_radius=15)
        pygame.draw.rect(self.screen, (50, 50, 50), self.delete_popup_rect.inflate(-5, -5), border_radius=15)

        # Add a subtle drop shadow effect
        shadow_rect = pygame.Rect(self.delete_popup_rect.x + 5, self.delete_popup_rect.y + 5, self.delete_popup_rect.width, self.delete_popup_rect.height)
        pygame.draw.rect(self.screen, (0, 0, 0), shadow_rect, border_radius=15)

        # Render centered text
        font = pygame.font.Font(None, 30)
        text = font.render(f"Are you sure you want to delete {self.selected_game}?", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.delete_popup_rect.centerx, self.delete_popup_rect.centery - 20))
        self.screen.blit(text, text_rect)

        # Draw confirmation buttons with styling
        yes_button = pygame.Rect(self.delete_popup_rect.centerx - 75, self.delete_popup_rect.bottom - 50, 150, 40)
        no_button = pygame.Rect(self.delete_popup_rect.centerx - 75, self.delete_popup_rect.bottom - 100, 150, 40)

        # Button colors and hover effects
        pygame.draw.rect(self.screen, (0, 255, 0), yes_button, border_radius=10)  # Green button for 'Yes'
        pygame.draw.rect(self.screen, (255, 0, 0), no_button, border_radius=10)  # Red button for 'No'

        # Add text to buttons
        yes_text = font.render("Yes", True, (0, 0, 0))
        no_text = font.render("No", True, (0, 0, 0))

        self.screen.blit(yes_text, yes_button)
        self.screen.blit(no_text, no_button)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for label, delete_button_rect in self.delete_buttons:
                    if delete_button_rect.collidepoint(event.pos):
                        self.selected_game = label
                        self.confirm_delete = True
                        return  # Exit to allow confirmation dialog

                if self.confirm_delete:
                    # Handle "Yes" and "No" clicks for deletion confirmation
                    yes_button_rect = pygame.Rect(self.delete_popup_rect.centerx - 75, self.delete_popup_rect.bottom - 50, 150, 40)
                    no_button_rect = pygame.Rect(self.delete_popup_rect.centerx - 75, self.delete_popup_rect.bottom - 100, 150, 40)

                    if yes_button_rect.collidepoint(event.pos):
                        self.delete_game(self.selected_game)
                        self.confirm_delete = False
                    elif no_button_rect.collidepoint(event.pos):
                        self.confirm_delete = False
                        self.selected_game = None

                # Handle back and saved game load clicks
                for label, rect in self.saved_game_buttons + [("Back", self.back_button_rect)]:
                    if rect.collidepoint(event.pos):
                        self.handle_button_click(label)

    def handle_button_click(self, label):
        if label == "Back":
            self.active = False  # Close this screen and return to the previous screen
            self.back = True
        elif label.endswith(".json"):  # Only load valid saved game files
            self.load_old_game_data(label)
            self.active = False  # Close the screen after loading a game
            self.getoldsave = True
    
    def load_old_game_data(self, save_file):
        save_path = os.path.join(self.saved_games_dir, save_file)

        try:
            with open(save_path, 'r') as file:
                save_data = json.load(file)

            # Extract saved game data
            current_planet_index = save_data.get("current_planet_index", 0)
            current_level_index = save_data.get("current_level_index", 0)
            planet_name = save_data.get("planet_name", "Unknown")

            permissions = save_data.get("permissions", "default_permission")
            gravity_strength = save_data.get("gravity_strength", 1.0)
            tmx_map = save_data.get("tmx_map", "default_map")

            print(f"Resuming game: Planet {planet_name}, Level {current_level_index}")
            print(f"Permissions: {permissions}, Gravity: {gravity_strength}, TMX Map: {tmx_map}")

            save_info = {
                "current_planet_index": current_planet_index,
                "current_level_index": current_level_index,
                "planet_name": planet_name,
                "permissions": permissions,
                "gravity_strength": gravity_strength,
                "tmx_map": tmx_map,
            }

            # Load game state into LevelManager
            print("Load game state into LevelManager")
            self.level_manager.load_save_info(save_info)

        except FileNotFoundError:
            print(f"Save file {save_file} not found!")
        except json.JSONDecodeError:
            print(f"Failed to load {save_file}: Invalid JSON format.")
    
    def delete_game(self, save_file):
        save_path = os.path.join(self.saved_games_dir, save_file)
        try:
            os.remove(save_path)
            print(f"Deleted {save_file}")

            # Refresh the saved games list and reset the screen
            self.saved_game_buttons.clear()  # Clear the existing saved game buttons
            self.delete_buttons.clear()      # Clear the delete button list
            self.load_saved_games()          # Reload saved games
            self.confirm_delete = False      # Close the confirmation popup
            
            # Re-render the updated saved games screen
            self.render()

        except FileNotFoundError:
            print(f"{save_file} not found for deletion.")

