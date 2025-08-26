# settings.py
# Game configuration and constants

import pygame

# Window
WIDTH, HEIGHT = 960, 720
FPS = 60
CAPTION = "Sanskriti: The Lost Scripts"

# Grid
TILE_SIZE = 32
GRID_W = WIDTH // TILE_SIZE
GRID_H = HEIGHT // TILE_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (120, 120, 120)
DARK_GRAY = (40, 40, 40)
RED = (200, 40, 40)
GREEN = (40, 200, 40)
BLUE = (40, 100, 200)
YELLOW = (230, 180, 40)
ORANGE = (255, 140, 0)
PURPLE = (140, 40, 200)

# Player
PLAYER_SPEED = 2.0  # tiles per second base (converted appropriately)
PLAYER_SPRINT_MULT = 1.9
PLAYER_MAX_STAMINA = 100.0
PLAYER_STAMINA_DRAIN = 30.0  # per second while sprinting
PLAYER_STAMINA_RECOVER = 15.0  # per second when not sprinting

# Guard
GUARD_SPEED = 1.4
GUARD_VISION_DISTANCE = 6  # in tiles (short for stealth)
GUARD_FOV = 70  # degrees
GUARD_HEARING_RADIUS = 3  # tiles for cautious reaction

# Pathfinding
DIAGONAL_COST = 1.4
ORTHO_COST = 1.0

# Levels
LEVEL_COUNT = 5

# Rune
RUNE_SCORE = 100

# Misc
FONT_NAME = None  # default pygame font
