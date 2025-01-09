import pygame
import time
from utils.settings import *
from ui.animatedtext import *

class TextBox:
    def __init__(self, position, size, screen, clock, text, font, fade_time=4):
        """
        Initialize the TextBox class.

        :param position: Tuple (x, y) for the top-left corner of the box.
        :param size: Tuple (width, height) of the box.
        :param screen: The screen surface where the box and text will be drawn.
        :param text: The text to display inside the box.
        :param font: The font object to render the text.
        :param fade_time: Time (in seconds) after which the box fades and disappears.
        """
        self.position = position
        self.size = size
        self.screen = screen
        self.text_display = TextDisplay(position, text, font, screen)
        self.start_time = time.time()
        self.fade_time = fade_time
        self.alpha = 255
        self.surface = pygame.Surface(size)
        self.surface.set_alpha(self.alpha)
        self.surface.fill(BLACK)
        self.clock = clock

        texture_image = pygame.image.load("../assets/graphics/tilesets/extra.png").convert_alpha()
        texture_coords_gray = (0, 0, 192, 192)
        self.button_texture_gray = texture_image.subsurface(pygame.Rect(*texture_coords_gray))
    def start(self):
        """Start displaying the text box."""
        self.start_time = time.time()

    def update(self):
        """Update the text box and fade out if necessary."""
        self.handle_skip()

        if self.start_time is None:
            return

        elapsed_time = time.time() - self.start_time

        # Calculate fade ratio for gamma adjustment
        if elapsed_time <= self.fade_time:
            fade_ratio = 1 - (elapsed_time / self.fade_time)
            self.gamma = int(255 * fade_ratio)  # Gamma reduces progressively
        else:
            self.gamma = 0  # Fully faded
            self.reset()

        # Update the text display
        self.text_display.update()


    def render(self):
        """Render the text box and center the animated text with gamma fading."""
        if self.start_time is None or self.gamma == 0:
            return

        # Scale the texture to match the size of the box
        scaled_texture = pygame.transform.scale(self.button_texture_gray, self.size)
        faded_texture = pygame.Surface(self.size).convert_alpha()
        faded_texture.blit(scaled_texture, (0, 0))
        faded_texture.fill((self.gamma, self.gamma, self.gamma), special_flags=pygame.BLEND_RGBA_MULT)

        # Draw the textured box with gamma fading
        self.screen.blit(faded_texture, self.position)

        # Render the animated text line by line, centered in the box
        x, y = self.position
        box_width, box_height = self.size
        total_text_height = len(self.text_display.lines) * (self.text_display.font.get_height() + self.text_display.line_spacing)

        # Start vertical alignment
        start_y = y + (box_height - total_text_height) // 2

        for i in range(self.text_display.current_line_index):
            line_surface = self.text_display.font.render(self.text_display.lines[i], True, (self.gamma, self.gamma, self.gamma))
            line_rect = line_surface.get_rect(center=(x + box_width // 2, start_y + i * (self.text_display.font.get_height() + self.text_display.line_spacing)))
            self.screen.blit(line_surface, line_rect)
            self.handle_skip()

        # Render the animated part of the current line
        if self.text_display.current_line_index < len(self.text_display.lines):
            current_surface = self.text_display.font.render(self.text_display.current_text, True, (self.gamma, self.gamma, self.gamma))
            current_rect = current_surface.get_rect(center=(x + box_width // 2, start_y + self.text_display.current_line_index * (self.text_display.font.get_height() + self.text_display.line_spacing)))
            self.screen.blit(current_surface, current_rect)
            self.handle_skip()


    def handle_skip(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.reset()

    def reset(self):
        """Reset the text box and hide it."""
        self.active = False
        self.start_time = None
        self.alpha = 255
        self.text_display.reset()

    def run(self):
        """Run the text box, displaying it and stopping after fade_time."""
        self.start()
        self.active = True

        while self.active:
            self.handle_skip()
            self.update()
            self.render()

            if not self.active:
                break 
            # Stop the loop after fade_time has elapsed
            if time.time() - self.start_time >= self.fade_time:
                self.active = False

            pygame.display.flip()
            self.clock.tick(FPS)  # Limit the frame rate