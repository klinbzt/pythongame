import pygame
from settings import FPS, BLACK, SCREEN_WIDTH, SCREEN_HEIGHT

class GameEngine:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.draw()
            self.update()
            self.clock.tick(FPS)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        """Update game state (logic, physics, etc.)"""
        pass

    def draw(self):
        """Render game elements on the screen."""
        self.screen.fill(BLACK)
        pygame.display.flip()