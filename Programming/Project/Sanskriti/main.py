# main.py
import sys
import random
import pygame
import numpy as np
import time

from settings import WIDTH, HEIGHT, FPS, CAPTION, TILE_SIZE, GRID_W, GRID_H, RUNE_SCORE, LEVEL_COUNT
from mapgen import generate_level
from player import Player
from guard import Guard
from ui import draw_hud, draw_text, BIG
from utils import from_grid, to_grid, line_of_sight

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(CAPTION)
clock = pygame.time.Clock()

def draw_grid(screen, grid):
    h, w = grid.shape
    for y in range(h):
        for x in range(w):
            rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if grid[y, x] == 1:
                pygame.draw.rect(screen, (30,30,30), rect)
            else:
                pygame.draw.rect(screen, (10,10,10), rect)
    # optional grid lines
    # for x in range(w):
    #     pygame.draw.line(screen, (20,20,20), (x*TILE_SIZE, 0), (x*TILE_SIZE, HEIGHT))

def render_player(screen, player):
    pygame.draw.circle(screen, (40,200,80), (int(player.x), int(player.y)), int(player.radius))

def render_runes(screen, runes):
    for (rx, ry) in runes:
        cx = int(rx * TILE_SIZE + TILE_SIZE*0.5)
        cy = int(ry * TILE_SIZE + TILE_SIZE*0.5)
        pygame.draw.circle(screen, (230,200,60), (cx, cy), int(TILE_SIZE*0.25))
        # little glow
        pygame.draw.circle(screen, (255, 255, 200), (cx, cy), int(TILE_SIZE*0.12))

def render_guard(screen, guard):
    color = (200,50,50) if not guard.is_boss else (150,30,180)
    pygame.draw.circle(screen, color, (int(guard.x), int(guard.y)), int(guard.radius))
    # vision cone - simplistic polygon
    center = (guard.x, guard.y)
    pts = []
    deg = guard.fov / 2
    for angle in (-deg, deg):
        a = math.radians((guard.heading + angle) % 360)
        dx = math.cos(a) * guard.vision_distance * TILE_SIZE
        dy = math.sin(a) * guard.vision_distance * TILE_SIZE
        pts.append((int(center[0] + dx), int(center[1] + dy)))
    pts = [center] + pts
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.polygon(s, (200, 200, 80, 40), pts)
    screen.blit(s, (0,0))

import math

def run_game():
    level_num = 1
    total_score = 0
    random_seed = int(time.time())
    while level_num <= LEVEL_COUNT:
        # generate level
        seed = random_seed + level_num * 13
        grid, player_cell, runes, guard_spawns = generate_level(seed=seed, level_number=level_num)
        # add extra runes so player has to collect several
        random.shuffle(runes)
        runes_set = list(runes)
        # ensure at least 3 runes
        while len(runes_set) < 3:
            # find random floor cell
            h, w = grid.shape
            rx = random.randint(1, w-2)
            ry = random.randint(1, h-2)
            if grid[ry, rx] == 0 and (rx, ry) != player_cell:
                runes_set.append((rx, ry))
        player = Player(player_cell)
        guards = []
        # difficulty scaling
        for i, sp in enumerate(guard_spawns):
            is_boss = False
            g = Guard(sp, grid, patrol=None, is_boss=False)
            # increase guard vision/distance by level slightly
            g.vision_distance += level_num * 0.5
            g.speed = g.speed + level_num * 10
            guards.append(g)

        # final boss on last level
        if level_num == LEVEL_COUNT:
            # place boss near last room or random
            placed = False
            for y in range(grid.shape[0]):
                for x in range(grid.shape[1]):
                    if grid[y, x] == 0:
                        boss = Guard((x, y), grid, is_boss=True)
                        boss.vision_distance += 3
                        boss.fov += 20
                        guards.append(boss)
                        placed = True
                        break
                if placed:
                    break

        level_running = True
        level_complete = False
        lore_shown = False
        player_history = []  # store recent player cells for guards
        while level_running:
            dt = clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            # update
            player.update(dt, grid)
            player_history.append(player.cell)
            if len(player_history) > 20:
                player_history.pop(0)

            # rune collection
            for rune in runes_set[:]:
                if player.cell == rune:
                    player.score += RUNE_SCORE
                    runes_set.remove(rune)

            # guards update
            for g in guards:
                g.update(dt, player.cell, (player.x, player.y), player_history)
                # if guard sees player and close -> caught
                if g.can_see_player(player.cell):
                    if math.hypot(g.x - player.x, g.y - player.y) < TILE_SIZE * 0.8:
                        player.alive = False

            # check death
            if not player.alive:
                # simple death reset for level
                draw_text(screen, "You were caught! Press R to restart level.", (WIDTH//2, HEIGHT//2), center=True, font=BIG)
                pygame.display.flip()
                waiting = True
                while waiting:
                    for ev in pygame.event.get():
                        if ev.type == pygame.QUIT:
                            pygame.quit(); sys.exit()
                        if ev.type == pygame.KEYDOWN:
                            if ev.key == pygame.K_r:
                                waiting = False
                                level_running = False
                            if ev.key == pygame.K_ESCAPE:
                                pygame.quit(); sys.exit()
                break

            # check win condition: all runes collected
            if not runes_set:
                level_complete = True
                total_score += player.score
                level_running = False

            # rendering
            screen.fill((6,6,6))
            draw_grid(screen, grid)
            render_runes(screen, runes_set)
            for g in guards:
                render_guard(screen, g)
            render_player(screen, player)
            draw_hud(screen, player, level_num)

            pygame.display.flip()

        # level end: show lore text
        if level_complete:
            lore = get_lore_for_level(level_num)
            show_lore_screen(lore)
            level_num += 1
            # carry player score forward but reset per-level player stats
        else:
            # player died and restarted; do not advance level
            pass

    # game completed
    show_lore_screen(["You have uncovered the lost scripts of Sanskriti.",
                      f"Final Score: {total_score}",
                      "The past watches kindly upon those who seek knowledge."])
    pygame.quit()

def show_lore_screen(lines):
    waiting = True
    while waiting:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                waiting = False
        screen.fill((12,12,18))
        y = 120
        for line in lines:
            draw_text(screen, line, (WIDTH//2, y), center=True, font=BIG)
            y += 60
        draw_text(screen, "Press any key to continue...", (WIDTH//2, HEIGHT - 80), center=True)
        pygame.display.flip()
        clock.tick(30)

def get_lore_for_level(n):
    lore_texts = {
        1: ["Level I - Whispering Courtyards", "You uncovered the first fragment of the scripts.", "Symbols hum softly."],
        2: ["Level II - Hall of Mirrors", "The scripts reveal a ritual of memory.", "You feel observed."],
        3: ["Level III - Sunken Stacks", "The glyphs speak in riddles of balance.", "A guardian stirs."],
        4: ["Level IV - Vault of Echoes", "The language shifts when read aloud.", "Shadows shape into forms."],
        5: ["Level V - Sanctum of the Last Script", "The final fragment waits, guarded by the ancient sentinel.", "This is where past meets present."]
    }
    return lore_texts.get(n, ["An old script, half-remembered."])

if __name__ == "__main__":
    run_game()
