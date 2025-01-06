import pygame
import os
from utils.settings import *

class LoadGameScreen:
    def __init__(self, screen):
        self.screen = screen
        self.active = True
        self.clock = pygame.time.Clock()

        self.saved_games_dir = "saved_games"  # Directory where saved games are stored

        # Button dimensions and gap
        self.button_width = 300
        self.button_height = 50
        self.button_gap = 20

        # Calculate screen dimensions
        screen_width, screen_height = self.screen.get_size()

        # Define the rectangles for displaying saved game names
        self.saved_game_buttons = []
        self.back_button_rect = None

    def load_saved_games(self):
        if not os.path.exists(self.saved_games_dir):
            os.makedirs(self.saved_games_dir)

        saved_files = [
            file for file in os.listdir(self.saved_games_dir) if file.endswith(".save")
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

    def render(self):
        self.screen.fill(BLACK)

        font = pygame.font.Font(None, 30)  # Font for the button text
        if self.no_games_message:
            no_games_text = font.render(self.no_games_message, True, WHITE)
            text_rect = no_games_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(no_games_text, text_rect)
        else:
            for label, rect in self.saved_game_buttons:
                pygame.draw.rect(self.screen, WHITE, rect)  # Ensure saved game buttons are white
                text = font.render(label, True, BLACK)  # Black text on white button
                text_rect = text.get_rect(center=rect.center)
                self.screen.blit(text, text_rect)

        pygame.draw.rect(self.screen, WHITE, self.back_button_rect)  # Ensure back button is white
        back_text = font.render("<-", True, BLACK)
        back_text_rect = back_text.get_rect(center=self.back_button_rect.center)
        self.screen.blit(back_text, back_text_rect)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for label, rect in self.saved_game_buttons + [("Back", self.back_button_rect)]:
                    if rect.collidepoint(event.pos):
                        self.handle_button_click(label)

    def handle_button_click(self, label):
        if label == "Back":
            print("Back button clicked!")
            self.active = False  # Close this screen and return to the previous screen
        elif label.endswith(".save"):
            print(f"Loading game: {label}")
            # Logic to load the saved game goes here
            self.active = False  # Close the screen after loading a game
