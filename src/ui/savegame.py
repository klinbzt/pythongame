import json
import pygame
import os
from os.path import join
from utils.settings import *

class SaveGame:
    def __init__(self, save_path='./saved_games/'):
        """
        Initialize the SaveGame class with a default save path.
        """
        self.save_path = save_path  # Directory to store save files

    def save(self, save_info):
        """
        Save the game data to a new JSON file with a unique name.
        """

        save_name = save_info["planet_name"]
        save_filename = f"{save_name}_{save_info['current_planet_index']}_{save_info['current_level_index']}.json"
        save_file = join(self.save_path, save_filename)

        # Create the directory if it doesn't exist
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        # Write save data to a new file
        with open(save_file, 'w') as file:
            json.dump(save_info, file, indent=4)

        print(f"Game saved in {save_filename}!")

    def run(self, screen, save_info):
        """
        Display "Save Game?", "Don't Save", and "Continue" buttons.
        """
        # Button properties
        font = pygame.font.Font(None, 36)
        text_color = (255, 255, 255)  # White

        # Save Game button
        save_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 75, 200, 50)
        save_button_color = (0, 128, 0)  # Green
        save_button_text = "Save Game?"

        # Don't Save button
        dont_save_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 15, 200, 50)
        dont_save_button_color = (255, 0, 0)  # Red
        dont_save_button_text = "Don't Save"

        # Continue button
        continue_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 45, 200, 40)
        continue_button_color = (0, 0, 255)  # Blue
        continue_button_text = "Continue"

        while True:
            screen.fill(BLACK)  # Clear the screen with black

            # Render "Save Game?" button
            pygame.draw.rect(screen, save_button_color, save_button_rect)
            save_text_surface = font.render(save_button_text, True, text_color)
            save_text_rect = save_text_surface.get_rect(center=save_button_rect.center)
            screen.blit(save_text_surface, save_text_rect)

            # Render "Don't Save" button
            pygame.draw.rect(screen, dont_save_button_color, dont_save_button_rect)
            dont_save_text_surface = font.render(dont_save_button_text, True, text_color)
            dont_save_text_rect = dont_save_text_surface.get_rect(center=dont_save_button_rect.center)
            screen.blit(dont_save_text_surface, dont_save_text_rect)

            # Render "Continue" button
            pygame.draw.rect(screen, continue_button_color, continue_button_rect)
            continue_text_surface = font.render(continue_button_text, True, text_color)
            continue_text_rect = continue_text_surface.get_rect(center=continue_button_rect.center)
            screen.blit(continue_text_surface, continue_text_rect)

            pygame.display.update()

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if save_button_rect.collidepoint(event.pos):
                        # Save game data
                        self.save(save_info)
                        print("Game saved!")
                        return False # Exit the save game screen after saving
                    elif dont_save_button_rect.collidepoint(event.pos):
                        # Exit without saving
                        print("Game not saved.")
                        return False # Exit the save game screen without saving
                    elif continue_button_rect.collidepoint(event.pos):
                        # Continue the game without saving
                        print("Continuing game...")
                        return True
