# mapgen.py
# Room-and-corridor procedural generation (same logic as 2D, but engine-agnostic)
import random
import numpy as np
from settings3d import GRID_W, GRID_H

WALL = 1
FLOOR = 0

class Room:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h
    def center(self):
        return self.x + self.w // 2, self.y + self.h // 2
    def intersect(self, other):
        return not (self.x + self.w < other.x or other.x + other.w < self.x or
                    self.y + self.h < other.y or other.y + other.h < self.y)

def make_empty_grid(w=GRID_W, h=GRID_H):
    return np.ones((h, w), dtype=np.uint8)

def carve_room(grid, room):
    grid[room.y:room.y+room.h, room.x:room.x+room.w] = FLOOR

def carve_h(grid, x1, x2, y):
    if x2 < x1: x1, x2 = x2, x1
    grid[y, x1:x2+1] = FLOOR

def carve_v(grid, y1, y2, x):
    if y2 < y1: y1, y2 = y2, y1
    grid[y1:y2+1, x] = FLOOR

def generate_level(seed=None, level_number=1):
    if seed is not None:
        random.seed(seed)
    grid = make_empty_grid()
    rooms = []
    max_rooms = 8 + level_number * 2
    min_size = 4
    max_size = 9

    for _ in range(max_rooms):
        w = random.randint(min_size, max_size)
        h = random.randint(min_size, max_size)
        x = random.randint(1, GRID_W - w - 2)
        y = random.randint(1, GRID_H - h - 2)
        new = Room(x, y, w, h)
        if any(new.intersect(r) for r in rooms):
            continue
        carve_room(grid, new)
        if rooms:
            (x1, y1) = new.center()
            (x2, y2) = rooms[-1].center()
            if random.random() < 0.5:
                carve_h(grid, x1, x2, y1); carve_v(grid, y1, y2, x2)
            else:
                carve_v(grid, y1, y2, x1); carve_h(grid, x1, x2, y2)
        rooms.append(new)

    # sprinkle pillars
    tries = 40 + level_number * 10
    for _ in range(tries):
        rx = random.randint(1, GRID_W-2)
        ry = random.randint(1, GRID_H-2)
        if grid[ry, rx] == FLOOR and random.random() < 0.08:
            grid[ry, rx] = WALL

    start_room = rooms[0] if rooms else Room(1,1,5,5)
    player_cell = start_room.center()

    # runes in rooms
    runes = []
    for r in rooms[1:]:
        rx = random.randint(r.x, r.x + r.w - 1)
        ry = random.randint(r.y, r.y + r.h - 1)
        if grid[ry, rx] == FLOOR:
            runes.append((rx, ry))

    # guard spawns
    guards = []
    guard_count = max(1, level_number + 1)
    placed = 0
    attempts = 0
    while placed < guard_count and attempts < 800:
        gx = random.randint(1, GRID_W-2)
        gy = random.randint(1, GRID_H-2)
        attempts += 1
        if grid[gy, gx] == FLOOR and (gx, gy) != player_cell and (gx, gy) not in runes:
            guards.append((gx, gy)); placed += 1

    return grid, player_cell, runes, guards
