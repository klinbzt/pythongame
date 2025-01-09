import pygame
from utils.settings import *

class TextDisplay:
    def __init__(self, position, text, font, screen, max_chars=30, line_spacing=10):
        """
        Initialize the TextDisplay class.

        :param position: Tuple (x, y) where the text should start rendering.
        :param text: The full text to render progressively.
        :param font: The font object to use for rendering.
        :param screen: The screen surface where the text will be drawn.
        :param max_chars: Maximum number of characters per line.
        :param line_spacing: Space between lines in pixels.
        """
        self.position = position
        self.text = text
        self.font = font
        self.screen = screen
        self.max_chars = max_chars
        self.line_spacing = line_spacing

        self.lines = self._split_text()  # Split the text into lines
        self.current_line_index = 0  # Current line being typed
        self.current_text = ""  # Current text being displayed
        self.typing_index = 0  # Typing progress index for the current line
        self.typing_speed = 1  # Characters per frame
        self.finished = False  # True when typing is complete

    def _split_text(self):
        """Split the text into lines of at most max_chars characters."""
        return [self.text[i:i + self.max_chars] for i in range(0, len(self.text), self.max_chars)]

    def update(self):
        """Update the typing progress for the current line."""
        if self.finished:
            return

        # Progressively type out the current line
        if self.current_line_index < len(self.lines):
            current_line = self.lines[self.current_line_index]
            if self.typing_index < len(current_line):
                self.current_text += current_line[self.typing_index]
                self.typing_index += 1
            else:
                # Move to the next line
                self.current_line_index += 1
                self.typing_index = 0
                self.current_text = ""
        else:
            self.finished = True  # Typing is complete

    def render(self):
        """Render the text on the screen."""
        if not self.lines:
            return

        x, y = self.position

        # Render all completed lines
        for i in range(self.current_line_index):
            text_surface = self.font.render(self.lines[i], True, WHITE)
            self.screen.blit(text_surface, (x, y + i * (self.font.get_height() + self.line_spacing)))

        # Render the progressively typed current line
        if self.current_line_index < len(self.lines):
            text_surface = self.font.render(self.current_text, True, WHITE)
            self.screen.blit(text_surface, (x, y + self.current_line_index * (self.font.get_height() + self.line_spacing)))

    def reset(self):
        """Reset the typing progress."""
        self.current_line_index = 0
        self.current_text = ""
        self.typing_index = 0
        self.finished = False
