# guard3d.py
import time as _time
from ursina import Entity, Vec3, color
from settings3d import (TILE_SIZE, GUARD_SPEED, GUARD_VISION_DISTANCE, GUARD_FOV_DEG,
                        COLOR_GUARD, COLOR_BOSS)
from utils3d import to_grid_from_world, world_from_grid, los_grid, angle_to, ang_diff
from pathfinding import astar

STATE_PATROL = "patrol"
STATE_CHASE = "chase"
STATE_SEARCH = "search"
STATE_BOSS = "boss"

class Guard(Entity):
    def __init__(self, start_cell, grid, is_boss=False):
        x, z = world_from_grid(start_cell)
        super().__init__(model='capsule',
                         color=color.rgba(*(COLOR_BOSS if is_boss else COLOR_GUARD)),
                         scale=Vec3(0.6, 1.1, 0.6), position=Vec3(x, 0.55, z))
        self.grid = grid
        self.speed = GUARD_SPEED
        self.is_boss = is_boss
        self.vision_dist = GUARD_VISION_DISTANCE + (3 if is_boss else 0)
        self.fov = GUARD_FOV_DEG + (20 if is_boss else 0)
        self.state = STATE_PATROL
        self.path = []
        self.path_index = 0
        self.heading = 0.0
        self.player_memory = []
        self.last_saw_time = None
        self.search_timer = 0

        # visual "vision cone" (approx) — a translucent cone in front
        self.cone = Entity(parent=self, model='cone', color=color.rgba(1,1,0.5,0.12),
                           scale=Vec3(0.7 + self.fov/180, 0.4, self.vision_dist),
                           position=Vec3(0, 0.2, 0.4), rotation_x=90)

    @property
    def cell(self):
        gx, gy = to_grid_from_world(self.x, self.z)
        return (gx, gy)

    def _set_path_to(self, target_cell):
        p = astar(self.grid, self.cell, target_cell)
        if p and len(p) > 1:
            self.path = p[1:]; self.path_index = 0
        else:
            self.path = []; self.path_index = 0

    def _follow_path(self, dt):
        if not self.path:
            return
        nxt = self.path[self.path_index]
        tx, tz = world_from_grid(nxt)
        dx = tx - self.x
        dz = tz - self.z
        dist = (dx*dx + dz*dz) ** 0.5
        if dist < 0.05:
            # snap to tile
            self.x, self.z = tx, tz
            self.path_index += 1
            if self.path_index >= len(self.path):
                self.path = []; self.path_index = 0
            return
        vx = dx / max(0.0001, dist) * self.speed
        vz = dz / max(0.0001, dist) * self.speed
        self.x += vx * dt
        self.z += vz * dt
        # face movement direction
        self.heading = angle_to((self.x, self.z), (self.x + dx, self.z + dz))
        self.rotation_y = self.heading

    def can_see_player(self, player_cell, player_world, grid):
        # distance (grid distance for LOS check)
        dx = player_cell[0] - self.cell[0]
        dy = player_cell[1] - self.cell[1]
        if (dx*dx + dy*dy) ** 0.5 > self.vision_dist:
            return False
        # FOV yaw
        yaw_to_player = angle_to((self.x, self.z), player_world)
        if ang_diff(yaw_to_player, self.heading) > self.fov / 2:
            return False
        # line-of-sight through tiles
        return los_grid(grid, self.cell, player_cell)

    def patrol(self, dt):
        # simple idle drift: choose random target nearby when idle
        if not self.path:
            gx, gy = self.cell
            choices = [(gx+2,gy), (gx-2,gy), (gx,gy+2), (gx,gy-2)]
            valid = [(x,y) for (x,y) in choices if 0<=x<self.grid.shape[1] and 0<=y<self.grid.shape[0] and self.grid[y,x]==0]
            if valid:
                import random
                self._set_path_to(random.choice(valid))
        self._follow_path(dt)

    def chase(self, dt, player_cell):
        self._set_path_to(player_cell)
        self._follow_path(dt)

    def search(self, dt):
        self.search_timer -= dt
        if self.search_timer <= 0:
            self.state = STATE_PATROL

    def boss_logic(self, dt, player_cell, player_hist):
        if player_cell:
            self.player_memory.append(player_cell)
            if len(self.player_memory) > 8:
                self.player_memory.pop(0)
        # predict linear next
        pred = player_cell
        if len(self.player_memory) >= 3:
            x0,y0 = self.player_memory[-3]
            x1,y1 = self.player_memory[-2]
            x2,y2 = self.player_memory[-1]
            vx, vy = (x2-x1), (y2-y1)
            pred = (int(max(0, min(self.grid.shape[1]-1, x2+vx))),
                    int(max(0, min(self.grid.shape[0]-1, y2+vy))))
        target = pred or player_cell
        self._set_path_to(target)
        if not self.path:
            self._set_path_to(player_cell)
        self._follow_path(dt)
        # adaptive vision
        now = _time.time()
        if self.last_saw_time is None or (now - self.last_saw_time) > 5:
            self.vision_dist = min(self.vision_dist + 0.01, max(self.grid.shape))
        else:
            self.vision_dist = max(4, self.vision_dist - 0.05)
        self.cone.scale_z = self.vision_dist

    def update_logic(self, dt, player, player_hist):
        player_world = (player.x, player.z)
        seen = self.can_see_player(player.cell, player_world, self.grid)
        if seen:
            self.last_saw_time = _time.time()
            self.state = STATE_BOSS if self.is_boss else STATE_CHASE
        else:
            if self.last_saw_time and (_time.time() - self.last_saw_time) < 4:
                self.state = STATE_SEARCH
                self.search_timer = 2.5
            else:
                self.state = STATE_PATROL

        # rotate visual cone with heading
        self.rotation_y = self.heading
        # behaviors
        if self.state == STATE_PATROL:
            self.patrol(dt)
        elif self.state == STATE_CHASE:
            self.chase(dt, player.cell)
        elif self.state == STATE_SEARCH:
            self.search(dt)
        elif self.state == STATE_BOSS:
            self.boss_logic(dt, player.cell, player_hist)
