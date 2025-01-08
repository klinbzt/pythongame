import sys
import pygame
from pygame.math import Vector2 as vector

# -----------------------------
# GLOBAL GAME SETTINGS / CONSTANTS
# -----------------------------

# Screen dimensions and framerate
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Tile size for grid-based levels
TILE_SIZE = 32

# Common colors
BLACK        = (  0,   0,   0)
WHITE        = (255, 255, 255)
GRAY         = (169, 169, 169)
GREEN        = (  0, 255,   0)
RED          = (255,   0,   0)
PURPLE       = ( 50,  50, 150)
LIGHT_PURPLE = ( 50,  50, 200)

# Default audio volume (0.0 = muted, 1.0 = max)
VOLUME = 0.5

# Default brightness (range can vary by your system; commonly 0.0 to 1.0)
BRIGHTNESS = 1.0
