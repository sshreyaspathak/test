# utils.py
import math
import random
from collections import deque

import numpy as np

def clamp(x, a, b):
    return max(a, min(b, x))

def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def to_grid(pos, tile_size):
    x, y = pos
    return int(x // tile_size), int(y // tile_size)

def from_grid(cell, tile_size):
    x, y = cell
    return (x + 0.5) * tile_size, (y + 0.5) * tile_size

def line_of_sight(grid, a, b):
    """Bresenham-like integer grid line check between two cells a and b.
    grid is a 2D numpy array where 0=walkable, 1=wall"""
    x0, y0 = a
    x1, y1 = b
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    n = 1 + dx + dy
    x_inc = 1 if x1 > x0 else -1
    y_inc = 1 if y1 > y0 else -1
    error = dx - dy
    dx *= 2
    dy *= 2

    for _ in range(n):
        if grid[y, x] == 1:
            return False
        if error > 0:
            x += x_inc
            error -= dy
        else:
            y += y_inc
            error += dx
    return True

def angle_between(a_pos, b_pos):
    ax, ay = a_pos
    bx, by = b_pos
    return math.degrees(math.atan2(by - ay, bx - ax)) % 360

def angle_diff(a, b):
    d = (a - b + 180) % 360 - 180
    return abs(d)

def random_choice_weighted(items, weights):
    total = sum(weights)
    r = random.random() * total
    upto = 0
    for it, w in zip(items, weights):
        if upto + w >= r:
            return it
        upto += w
    return items[-1]
