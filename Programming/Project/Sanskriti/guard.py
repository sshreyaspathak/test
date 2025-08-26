# guard.py
import math
import random
import time

import pygame
from settings import TILE_SIZE, GUARD_VISION_DISTANCE, GUARD_FOV, GUARD_SPEED, GUARD_HEARING_RADIUS
from utils import from_grid, to_grid, angle_between, angle_diff, distance, line_of_sight
from pathfinding import astar

# State constants
STATE_PATROL = "patrol"
STATE_ALERT = "alert"
STATE_CHASE = "chase"
STATE_SEARCH = "search"
STATE_IDLE = "idle"
STATE_BOSS = "boss"

class Guard:
    def __init__(self, start_cell, grid, patrol=None, is_boss=False):
        self.cell = start_cell
        self.grid = grid
        self.x, self.y = from_grid(start_cell, TILE_SIZE)
        self.radius = TILE_SIZE * 0.35
        self.speed = GUARD_SPEED * TILE_SIZE  # pixels per second
        self.vision_distance = GUARD_VISION_DISTANCE
        self.fov = GUARD_FOV
        self.heading = random.uniform(0, 360)
        self.state = STATE_PATROL
        self.patrol = patrol or [start_cell]
        self.patrol_index = 0
        self.path = []
        self.path_index = 0
        self.is_boss = is_boss
        # memory of recent player positions to mimic learning
        self.player_memory = []
        self.last_saw_time = None
        self.search_timer = 0

    def can_see_player(self, player_cell):
        # distance check
        dx = player_cell[0] - self.cell[0]
        dy = player_cell[1] - self.cell[1]
        dist = math.hypot(dx, dy)
        if dist > self.vision_distance:
            return False
        # fov check based on heading towards player
        guard_pos = (self.x, self.y)
        world_player = (player_cell[0] * TILE_SIZE + TILE_SIZE*0.5,
                        player_cell[1] * TILE_SIZE + TILE_SIZE*0.5)
        ang = angle_between(guard_pos, world_player)
        if angle_diff(ang, self.heading) > self.fov / 2:
            return False
        # line of sight check on grid
        if not line_of_sight(self.grid, self.cell, player_cell):
            return False
        return True

    def update_heading_from_movement(self, target_cell):
        tx, ty = target_cell
        gx, gy = self.cell
        world_g = (gx * TILE_SIZE + TILE_SIZE*0.5, gy * TILE_SIZE + TILE_SIZE*0.5)
        world_t = (tx * TILE_SIZE + TILE_SIZE*0.5, ty * TILE_SIZE + TILE_SIZE*0.5)
        self.heading = angle_between(world_g, world_t)

    def set_path_to(self, target_cell):
        path = astar(self.grid, self.cell, target_cell)
        if path and len(path) > 1:
            self.path = path[1:]
            self.path_index = 0
        else:
            self.path = []
            self.path_index = 0

    def patrol_behavior(self, dt):
        if not self.patrol:
            self.state = STATE_IDLE
            return
        target = self.patrol[self.patrol_index]
        if self.cell == target:
            self.patrol_index = (self.patrol_index + 1) % len(self.patrol)
            target = self.patrol[self.patrol_index]
            self.set_path_to(target)
        if not self.path:
            self.set_path_to(target)
        self.follow_path(dt)

    def follow_path(self, dt):
        if not self.path:
            return
        next_cell = self.path[self.path_index]
        world = (next_cell[0] * TILE_SIZE + TILE_SIZE*0.5,
                 next_cell[1] * TILE_SIZE + TILE_SIZE*0.5)
        dx = world[0] - self.x
        dy = world[1] - self.y
        dist = math.hypot(dx, dy)
        if dist < 3:
            # reached cell
            self.cell = next_cell
            self.path_index += 1
            if self.path_index >= len(self.path):
                self.path = []
                self.path_index = 0
            return
        vx = dx / dist * self.speed
        vy = dy / dist * self.speed
        self.x += vx * dt
        self.y += vy * dt
        self.cell = to_grid((self.x, self.y), TILE_SIZE)
        self.heading = math.degrees(math.atan2(dy, dx)) % 360

    def chase_behavior(self, player_cell, dt):
        # chasing uses A* to player cell
        self.set_path_to(player_cell)
        self.follow_path(dt)

    def search_behavior(self, dt):
        # wander around last known location
        self.search_timer -= dt
        if self.search_timer <= 0:
            self.state = STATE_PATROL

    def boss_decision(self, player_cell, dt, player_history):
        """Simple ML-like adaptive behavior:
        - store recent player positions; estimate next position by linear extrapolation;
        - compute intercept point and pathfind to it.
        - adapt vision distance slightly when "learning".
        """
        # update memory
        if player_cell:
            self.player_memory.append(player_cell)
            if len(self.player_memory) > 8:
                self.player_memory.pop(0)
        # predict next cell
        pred = player_cell
        if len(self.player_memory) >= 3:
            x0, y0 = self.player_memory[-3]
            x1, y1 = self.player_memory[-2]
            x2, y2 = self.player_memory[-1]
            vx = (x2 - x1)
            vy = (y2 - y1)
            pred = (x2 + vx, y2 + vy)
            # clamp into grid bounds
            pred = (max(0, min(pred[0], self.grid.shape[1]-1)),
                    max(0, min(pred[1], self.grid.shape[0]-1)))
        # choose intercept: try predicted pos, else player pos
        intercept = pred
        self.set_path_to(intercept)
        # If path is empty, fallback to player's cell
        if not self.path:
            self.set_path_to(player_cell)
        self.follow_path(dt)
        # adapt vision slightly when repeatedly failing to see player
        if self.last_saw_time is None or (time.time() - self.last_saw_time) > 5:
            self.vision_distance = min(self.vision_distance + 0.01, self.grid.shape[0] // 2)
        else:
            # grew confidence
            self.vision_distance = max(3, self.vision_distance - 0.05)

    def update(self, dt, player_cell, player_world_pos, player_history):
        # perception
        seen = self.can_see_player(player_cell)
        if seen:
            self.last_saw_time = pygame.time.get_ticks() / 1000.0
            if self.is_boss:
                self.state = STATE_BOSS
            else:
                self.state = STATE_CHASE
        else:
            # if recently saw, search for a bit
            if self.last_saw_time and (pygame.time.get_ticks()/1000.0 - self.last_saw_time) < 4:
                self.state = STATE_SEARCH
                self.search_timer = 3.0
            else:
                self.state = STATE_PATROL

        # behavior execution
        if self.state == STATE_PATROL:
            self.patrol_behavior(dt)
        elif self.state == STATE_CHASE:
            self.chase_behavior(player_cell, dt)
        elif self.state == STATE_SEARCH:
            self.search_behavior(dt)
        elif self.state == STATE_BOSS:
            self.boss_decision(player_cell, dt, player_history)
