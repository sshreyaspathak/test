# mapgen.py
import random
import numpy as np

from settings import GRID_W, GRID_H, TILE_SIZE
from utils import from_grid, to_grid

WALL = 1
FLOOR = 0

class Room:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h
    def center(self):
        cx = self.x + self.w // 2
        cy = self.y + self.h // 2
        return cx, cy
    def intersect(self, other):
        return not (self.x + self.w < other.x or other.x + other.w < self.x or
                    self.y + self.h < other.y or other.y + other.h < self.y)

def make_empty_grid(w=GRID_W, h=GRID_H):
    grid = np.ones((h, w), dtype=np.uint8)  # walls
    return grid

def carve_room(grid, room: Room):
    grid[room.y:room.y+room.h, room.x:room.x+room.w] = 0

def carve_h_corridor(grid, x1, x2, y):
    if x2 < x1:
        x1, x2 = x2, x1
    grid[y, x1:x2+1] = 0

def carve_v_corridor(grid, y1, y2, x):
    if y2 < y1:
        y1, y2 = y2, y1
    grid[y1:y2+1, x] = 0

def generate_level(seed=None, level_number=1):
    """Generates a grid, rune positions, player start and guard spawn list.
       As level increases, add more rooms/guards/complexity."""
    if seed is not None:
        random.seed(seed)
    grid = make_empty_grid()
    rooms = []
    max_rooms = 8 + level_number * 2
    min_size = 4
    max_size = 10

    for _ in range(max_rooms):
        w = random.randint(min_size, max_size)
        h = random.randint(min_size, max_size)
        x = random.randint(1, GRID_W - w - 2)
        y = random.randint(1, GRID_H - h - 2)
        new_room = Room(x, y, w, h)
        if any(new_room.intersect(other) for other in rooms):
            continue
        carve_room(grid, new_room)
        if rooms:
            # connect to previous room
            (x1, y1) = new_room.center()
            (x2, y2) = rooms[-1].center()
            if random.choice([True, False]):
                carve_h_corridor(grid, x1, x2, y1)
                carve_v_corridor(grid, y1, y2, x2)
            else:
                carve_v_corridor(grid, y1, y2, x1)
                carve_h_corridor(grid, x1, x2, y2)
        rooms.append(new_room)

    # sprinkle some pillars/walls randomly inside floors to add complexity
    for _ in range(40 + level_number * 10):
        rx = random.randint(1, GRID_W - 2)
        ry = random.randint(1, GRID_H - 2)
        if grid[ry, rx] == 0 and random.random() < 0.08:
            grid[ry, rx] = 1

    # choose player start at center of first room
    start_room = rooms[0] if rooms else Room(1,1,4,4)
    player_cell = start_room.center()

    # spawn runes scattered in other rooms
    runes = []
    for r in rooms[1:]:
        # place a rune somewhere inside room
        rx = random.randint(r.x, r.x + r.w - 1)
        ry = random.randint(r.y, r.y + r.h - 1)
        if grid[ry, rx] == 0:
            runes.append((rx, ry))

    # guard spawns - more as level increases
    guards = []
    guard_count = max(1, level_number + 1)
    for _ in range(guard_count):
        attempts = 0
        while attempts < 200:
            gx = random.randint(1, GRID_W - 2)
            gy = random.randint(1, GRID_H - 2)
            if grid[gy, gx] == 0 and (gx, gy) != player_cell and (gx, gy) not in runes:
                guards.append((gx, gy))
                break
            attempts += 1

    # final boss placed only at last level handled by main
    return grid, player_cell, runes, guards
