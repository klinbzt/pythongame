import sys
import pygame
from pygame.math import Vector2 as vector
from pygame import image

# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Tile dimensions
TILE_SIZE = 32

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Startup screen
sheets = [
    ('../assets/graphics/intro/test_buton1.png', (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)),
    ('../assets/graphics/intro/test_title.png', (SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2 + 100))
]

# layer ordering

Z_LAYERS = {
	'bg': 0,
	'clouds': 1,
	'bg tiles': 2,
	'path': 3,
	'bg details': 4,
	'main': 5,
	'water': 6,
	'fg': 7
}