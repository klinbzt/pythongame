from utils.settings import *

class StartupScreen:
    def __init__(self, screen, sheets):
        self.screen = screen
        self.sheets = sheets # tuplu format din locatia imaginii si pozitia unde sa fie pusa!
        self.active = True
        self.clock = pygame.time.Clock()

    def run(self):
        # Asteapta jucatorul sa apese start.
        while self.active:
            self.handle_events()
            self.render()
            self.clock.tick(FPS)
            pygame.display.flip()

    def render_animation_once(self):
        pass

    def render(self):
        self.screen.fill(BLACK)
        for sheet in self.sheets:
            processed_sheet = pygame.image.load(sheet[0])
            self.screen.blit(processed_sheet, sheet[1])

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0) # Daca user-ul inchide jocu din startup menu, ii dam exit fortat (reduce overhead...)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.active = False