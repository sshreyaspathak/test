# player3d.py
from ursina import Entity, Vec3, color, time, held_keys
from settings3d import (TILE_SIZE, PLAYER_SPEED, PLAYER_SPRINT_MULT,
                        PLAYER_MAX_STAMINA, PLAYER_STAMINA_DRAIN, PLAYER_STAMINA_RECOVER,
                        COLOR_PLAYER)
from utils3d import clamp, to_grid_from_world

class Player(Entity):
    def __init__(self, start_cell):
        x = start_cell[0] * TILE_SIZE
        z = start_cell[1] * TILE_SIZE
        super().__init__(model='capsule', color=color.rgba(*COLOR_PLAYER),
                         scale=Vec3(0.6, 1.1, 0.6), position=Vec3(x, 0.55, z))
        self.speed = PLAYER_SPEED
        self.sprinting = False
        self.stamina = PLAYER_MAX_STAMINA
        self.score = 0
        self.alive = True

    @property
    def cell(self):
        gx, gy = to_grid_from_world(self.x, self.z)
        return (gx, gy)

    def try_move(self, vx, vz, dt, grid):
        """Collision-aware movement: move if target cell isn't wall."""
        if vx == 0 and vz == 0:
            return
        new_x = self.x + vx * dt
        new_z = self.z + vz * dt
        gx, gy = to_grid_from_world(new_x, new_z)
        h, w = grid.shape
        gx = int(max(0, min(w-1, gx)))
        gy = int(max(0, min(h-1, gy)))
        if grid[gy, gx] == 0:
            self.x = new_x
            self.z = new_z

    def update_logic(self, grid):
        dt = time.dt
        vx = vz = 0.0
        # WASD on XZ plane
        if held_keys['w']: vz += 1
        if held_keys['s']: vz -= 1
        if held_keys['a']: vx -= 1
        if held_keys['d']: vx += 1
        self.sprinting = held_keys['shift']
        spd = self.speed * (PLAYER_SPRINT_MULT if (self.sprinting and self.stamina > 0) else 1.0)

        # normalize
        mag = (vx*vx + vz*vz) ** 0.5
        if mag > 0:
            vx /= mag; vz /= mag
            self.try_move(vx*spd, vz*spd, dt, grid)

        # stamina
        if self.sprinting and mag > 0 and self.stamina > 0:
            self.stamina -= PLAYER_STAMINA_DRAIN * dt
        else:
            self.stamina += PLAYER_STAMINA_RECOVER * dt
        self.stamina = clamp(self.stamina, 0.0, PLAYER_MAX_STAMINA)
