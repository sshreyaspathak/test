# utils3d.py
import math
import random
import numpy as np
from settings3d import TILE_SIZE

def clamp(x, a, b):
    return max(a, min(b, x))

def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def to_grid_from_world(x, z):
    """Convert world (x,z) to integer grid (gx, gy)."""
    return int(round(x / TILE_SIZE)), int(round(z / TILE_SIZE))

def world_from_grid(cell):
    """Convert grid (gx, gy) to world (x,z) centered in tile."""
    gx, gy = cell
    return gx * TILE_SIZE, gy * TILE_SIZE

def los_grid(grid, a, b):
    """Line of sight on tile grid using Bresenham-like step.
       grid: 2D numpy array (0=floor,1=wall) in [row(y)][col(x)].
       a,b: (gx, gy)
    """
    x0, y0 = a
    x1, y1 = b
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    n = 1 + dx + dy
    x_inc = 1 if x1 > x0 else -1
    y_inc = 1 if y1 > y0 else -1
    err = dx - dy
    dx *= 2
    dy *= 2
    for _ in range(n):
        if grid[y, x] == 1:
            return False
        if err > 0:
            x += x_inc
            err -= dy
        else:
            y += y_inc
            err += dx
    return True

def angle_to(a, b):
    """Angle (degrees) from a(x,z) to b(x,z) in XZ plane."""
    ax, az = a
    bx, bz = b
    ang = math.degrees(math.atan2(bx - ax, bz - az))  # yaw-style
    return (ang + 360) % 360

def ang_diff(a, b):
    d = (a - b + 180) % 360 - 180
    return abs(d)

def choose_weighted(items, weights):
    t = sum(weights)
    r = random.random() * t
    up = 0
    for it, w in zip(items, weights):
        if up + w >= r:
            return it
        up += w
    return items[-1]
