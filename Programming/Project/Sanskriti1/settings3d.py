# settings3d.py
# Global config for the 3D Ursina build

# World/grid
TILE_SIZE = 1.0               # 1 unit per tile (meters)
GRID_W = 30                   # columns
GRID_H = 22                   # rows

# Camera
CAM_HEIGHT = 22               # top-down / angled camera height
CAM_TILT_DEG = 57             # camera pitch angle

# Player
PLAYER_SPEED = 3.8            # tiles per second
PLAYER_SPRINT_MULT = 1.8
PLAYER_MAX_STAMINA = 100.0
PLAYER_STAMINA_DRAIN = 28.0   # per second while sprinting
PLAYER_STAMINA_RECOVER = 15.0 # per second when not sprinting

# Guards
GUARD_SPEED = 2.8             # tiles per second baseline
GUARD_VISION_DISTANCE = 7.0   # tiles
GUARD_FOV_DEG = 70            # for LOS + visual cone scaling
GUARD_HEARING_RADIUS = 3      # tiles (reserved for future)

# Pathfinding cost
ORTHO_COST = 1.0
DIAG_COST = 1.4

# Runes and scoring
RUNE_SCORE = 100

# Levels
LEVEL_COUNT = 5

# Colors (simple tuples, Ursina will convert)
COLOR_WALL = (0.16, 0.16, 0.18, 1)
COLOR_FLOOR = (0.06, 0.06, 0.07, 1)
COLOR_PLAYER = (0.2, 0.85, 0.4, 1)
COLOR_GUARD = (0.85, 0.25, 0.25, 1)
COLOR_BOSS = (0.6, 0.2, 0.8, 1)
COLOR_RUNE = (0.95, 0.85, 0.25, 1)
COLOR_UI = (1, 1, 1, 1)
