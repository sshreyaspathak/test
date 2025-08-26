# player.py
import pygame
from settings import TILE_SIZE, PLAYER_MAX_STAMINA, PLAYER_STAMINA_DRAIN, PLAYER_STAMINA_RECOVER, PLAYER_SPRINT_MULT
from utils import from_grid, to_grid, clamp
import math

class Player:
    def __init__(self, start_cell, tile_size=TILE_SIZE):
        self.cell = start_cell
        self.tile_size = tile_size
        self.x, self.y = from_grid(start_cell, tile_size)
        self.radius = tile_size * 0.35
        self.speed = 120.0  # pixels per second base
        self.sprinting = False
        self.stamina = PLAYER_MAX_STAMINA
        self.score = 0
        self.alive = True

    def rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)

    def update(self, dt, grid):
        keys = pygame.key.get_pressed()
        vx = vy = 0.0
        move = False

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            vy -= 1
            move = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            vy += 1
            move = True
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            vx -= 1
            move = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            vx += 1
            move = True

        self.sprinting = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

        if self.sprinting and self.stamina <= 0:
            self.sprinting = False

        speed = self.speed * (PLAYER_SPRINT_MULT if self.sprinting else 1.0)
        if vx != 0 or vy != 0:
            length = math.hypot(vx, vy)
            vx = vx / length * speed
            vy = vy / length * speed
            self.x += vx * dt
            self.y += vy * dt

        # stamina update
        if self.sprinting and move:
            self.stamina -= PLAYER_STAMINA_DRAIN * dt
        else:
            self.stamina += PLAYER_STAMINA_RECOVER * dt
        self.stamina = clamp(self.stamina, 0.0, PLAYER_MAX_STAMINA)

        # clamp inside screen and avoid walls (simple)
        max_x = grid.shape[1] * self.tile_size - self.tile_size * 0.5
        max_y = grid.shape[0] * self.tile_size - self.tile_size * 0.5
        min_x = self.tile_size * 0.5
        min_y = self.tile_size * 0.5
        self.x = clamp(self.x, min_x, max_x)
        self.y = clamp(self.y, min_y, max_y)

        self.cell = to_grid((self.x, self.y), self.tile_size)
