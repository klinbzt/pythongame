import pygame
from settings import FPS, BLACK, SCREEN_WIDTH, SCREEN_HEIGHT

class GameEngine:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.game_start = False
        self.running = True

    def run(self):
        """Main game loop."""
        while self.running:
            
            
            self.handle_events()
            # self.screen.fill(BLACK)
            if not self.game_start:
                self.start_screen()
                pass
            self.draw()
            self.update()
            self.clock.tick(FPS)

    def start_screen(self):
        # Functie pentru start-ul jocului: -> Meniu de start, Buton pentru setari etc.
        # doar de test:
        sprite_sheet1 = pygame.image.load('../assets/images/test_title.png').convert_alpha()
        sprite_sheet2 = pygame.image.load('../assets/images/test_buton1.png').convert_alpha()

        self.screen.blit(sprite_sheet1, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 150))
        self.screen.blit(sprite_sheet2, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 50))
        pass
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        """Update game state (logic, physics, etc.)"""
        pass

    def draw(self):
        """Render game elements on the screen."""
        # self.screen.fill(BLACK)
        pygame.display.flip()