# Here we declare and initialize consts

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)

# Startup screen
sheets = [
    ('../assets/images/test_buton1.png', (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)),
    ('../assets/images/test_title.png', (SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2 + 100))
]

# Player settings ( base settings can be altered later by power-ups, planet gravity, etc. )