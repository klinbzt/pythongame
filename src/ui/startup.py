import pygame
import sys
import math
from utils.settings import *
from ui.loadgame import *

class StartupScreen:
    def __init__(self, screen):
        self.screen = screen
        self.active = True
        self.clock = pygame.time.Clock()

        self.loadgames = LoadGameScreen(self.screen)
        # Button dimensions and gap
        self.button_width = 250
        self.button_height = 80
        self.hover_scale = 1.2  # Maximum scale factor when hovering
        self.shake_strength = 2  # Smaller shake strength
        self.shake_decay = 0.05  # Lower decay rate for the shake effect
        self.shake_frequency = 30  # Frequency of the shake oscillation
        self.button_gap = 20
        self.animation_speed = 0.1  # Speed of the hover animation

        # Calculate screen dimensions
        screen_width, screen_height = self.screen.get_size()

        # Define button positions and hover scales
        self.buttons = {
            "Play": {
                "rect": pygame.Rect(
                    (screen_width - self.button_width) // 2,
                    (screen_height - self.button_height) // 2 - (self.button_height + self.button_gap),
                    self.button_width,
                    self.button_height,
                ),
                "hover_scale": 1.0,  # Current hover scale
                "shake_offset": 0.0,  # Current shake offset
            },
            "Load Game": {
                "rect": pygame.Rect(
                    (screen_width - self.button_width) // 2,
                    (screen_height - self.button_height) // 2,
                    self.button_width,
                    self.button_height,
                ),
                "hover_scale": 1.0,
                "shake_offset": 0.0,
            },
            "Settings": {
                "rect": pygame.Rect(
                    (screen_width - self.button_width) // 2,
                    (screen_height - self.button_height) // 2 + (self.button_height + self.button_gap),
                    self.button_width,
                    self.button_height,
                ),
                "hover_scale": 1.0,
                "shake_offset": 0.0,
            },
        }

    def run(self):
        while self.active:
            self.handle_events()
            self.render()
            self.clock.tick(FPS)
            pygame.display.update()

    def render(self):
        self.screen.fill(BLACK)  # Fill the background with black

        mouse_pos = pygame.mouse.get_pos()  # Get current mouse position

        base_font_size = 40  # Base font size
        scaled_font_size = base_font_size  # Start with the base size

        for label, data in self.buttons.items():
            rect = data["rect"]
            hover_scale = data["hover_scale"]
            shake_offset = data["shake_offset"]

            # Check if the mouse is hovering over the button
            if rect.collidepoint(mouse_pos):
                # Apply the shake effect based on sine wave
                shake_offset = math.sin(pygame.time.get_ticks() / self.shake_frequency) * self.shake_strength
                data["shake_offset"] = shake_offset  # Update shake offset

                # Smoothly increase the hover scale
                data["hover_scale"] = min(self.hover_scale, hover_scale + self.animation_speed)
                scaled_font_size = int(base_font_size * hover_scale)
            else:
                # Smoothly decrease the hover scale and decay the shake offset
                data["hover_scale"] = max(1.0, hover_scale - self.animation_speed)
                data["shake_offset"] = max(0.0, shake_offset - self.shake_decay)
                scaled_font_size = int(base_font_size * hover_scale)

            # Create a scaled rect based on the hover scale and shake offset
            scaled_width = int(rect.width * data["hover_scale"])
            scaled_height = int(rect.height * data["hover_scale"])
            scaled_rect = pygame.Rect(
                rect.centerx - scaled_width // 2 + int(shake_offset),
                rect.centery - scaled_height // 2,
                scaled_width,
                scaled_height,
            )

            # Draw the button
            pygame.draw.rect(self.screen, WHITE, scaled_rect)  # White button color

            # Render button text
            font = pygame.font.Font(None, scaled_font_size)
            text = font.render(label, True, (0, 0, 0))  # Black text
            text_rect = text.get_rect(center=scaled_rect.center)
            self.screen.blit(text, text_rect)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for label, data in self.buttons.items():
                    rect = data["rect"]
                    if rect.collidepoint(event.pos):
                        self.handle_button_click(label)

    def handle_button_click(self, label):
        if label == "Play":
            print("Play button clicked!")
            self.active = False
        elif label == "Load Game":
            print("Load Game button clicked!")
            self.loadgames.run()
            # Add logic to load saved game data
        elif label == "Settings":
            print("Settings button clicked!")
            # Add logic to open the settings menu
