import pygame
from settings import FPS, BLACK, SCREEN_WIDTH, SCREEN_HEIGHT

class StartupScreen:
    def __init__(self, screen, sheets):
        self.screen = screen
        self.sheets = sheets # tuplu format din locatia imaginii si pozitia unde sa fie pusa!
        self.active = True

    def run(self):
        # Wait for player, to press start.
        while self.active:
            self.render()
            pygame.display.flip()

    def render(self):
        for sheet in self.sheets:
            processed_sheet = pygame.image.load(sheet[0])
            self.screen.blit(processed_sheet, sheet[1])
