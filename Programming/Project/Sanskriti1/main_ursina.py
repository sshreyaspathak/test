# main_ursina.py
# Sanskriti: The Lost Scripts — Ursina 3D Edition
from ursina import Ursina, Entity, Sky, DirectionalLight, AmbientLight, Vec3, color, camera, time, destroy
import random, math, sys
import numpy as np

from settings3d import *
from mapgen import generate_level
from player3d import Player
from guard3d import Guard
from ui3d import HUD, show_lore
from utils3d import world_from_grid

app = Ursina(title='Sanskriti: The Lost Scripts — 3D')

# Lighting & sky
Sky(color=color.rgba(0.04,0.04,0.05,1))
sun = DirectionalLight(shadows=False)
sun.look_at(Vec3(1,-2,1))
AmbientLight(color=color.rgba(0.5,0.5,0.6,1))

# Globals per level
level_num = 1
player = None
guards = []
runes = []
grid = None
hud = HUD()
player_history = []

# World holders
world_root = Entity()
floor_root = Entity(parent=world_root)
wall_root = Entity(parent=world_root)
rune_root = Entity(parent=world_root)
guard_root = Entity(parent=world_root)

def clear_world():
    for ch in list(world_root.children):
        destroy(ch)
    floor_root.children.clear()
    wall_root.children.clear()
    rune_root.children.clear()
    guard_root.children.clear()

def build_level(seed, level_n):
    global grid, player, guards, runes, player_history
    clear_world()
    grid, start_cell, rune_cells, guard_spawns = generate_level(seed=seed, level_number=level_n)

    # Build floor as tiles (thin quads) for clarity
    h, w = grid.shape
    for y in range(h):
        for x in range(w):
            if grid[y,x] == 0:
                wx, wz = world_from_grid((x,y))
                Entity(parent=floor_root, model='quad', color=color.rgba(*COLOR_FLOOR),
                       position=Vec3(wx, 0.0, wz), rotation_x=90, scale=Vec3(TILE_SIZE, TILE_SIZE, 1))

    # Build walls as cubes
    for y in range(h):
        for x in range(w):
            if grid[y,x] == 1:
                wx, wz = world_from_grid((x,y))
                Entity(parent=wall_root, model='cube', color=color.rgba(*COLOR_WALL),
                       position=Vec3(wx, 0.5, wz), scale=Vec3(TILE_SIZE, 1.0, TILE_SIZE))

    # Player
    player = Player(start_cell)

    # Runes as glowing spheres
    runes = []
    # ensure at least 3 runes
    rc = list(rune_cells)
    while len(rc) < 3:
        rx = random.randint(1, w-2); ry = random.randint(1, h-2)
        if grid[ry, rx] == 0 and (rx, ry) != start_cell:
            rc.append((rx, ry))
    for (rx, ry) in rc:
        wx, wz = world_from_grid((rx, ry))
        sphere = Entity(parent=rune_root, model='sphere', color=color.rgba(*COLOR_RUNE),
                        position=Vec3(wx, 0.4, wz), scale=0.35)
        runes.append({'cell': (rx, ry), 'entity': sphere})

    # Guards
    guards = []
    for sp in guard_spawns:
        g = Guard(sp, grid, is_boss=False)
        # scale difficulty per level
        g.speed = GUARD_SPEED * (1.0 + 0.08*level_n)
        g.vision_dist = GUARD_VISION_DISTANCE + 0.5 * level_n
        guards.append(g)

    # Final boss on last level
    if level_n == LEVEL_COUNT:
        # place boss near farthest walkable
        far = None; far_d = -1; target = (0,0)
        for y in range(h):
            for x in range(w):
                if grid[y,x]==0:
                    d = (x - start_cell[0])**2 + (y - start_cell[1])**2
                    if d > far_d: far_d = d; target = (x,y)
        boss = Guard(target, grid, is_boss=True)
        boss.speed = GUARD_SPEED * (1.1 + 0.1*level_n)
        guards.append(boss)

    # Camera
    cx, cz = world_from_grid((w//2, h//2))
    camera.position = (cx, CAM_HEIGHT, cz - 0.001)
    camera.rotation_x = CAM_TILT_DEG

    player_history = []

def check_player_caught():
    # If guard sees and is close enough in world space
    for g in guards:
        dx = g.x - player.x
        dz = g.z - player.z
        if (dx*dx + dz*dz) ** 0.5 < 0.55:
            return True
    return False

def collect_runes():
    # If player's cell matches a rune, collect it
    for r in list(runes):
        if player.cell == r['cell']:
            player.score += RUNE_SCORE
            destroy(r['entity'])
            runes.remove(r)

def level_loop():
    """Called each frame via Ursina's update hook."""
    global level_num
    dt = time.dt
    # Update player movement & stamina
    player.update_logic(grid)
    # Store history
    player_history.append(player.cell)
    if len(player_history) > 20:
        player_history.pop(0)
    # Guards
    for g in guards:
        g.update_logic(dt, player, player_history)
    # Rune collection
    collect_runes()
    # Caught?
    if check_player_caught():
        # Simple restart: show text and reload level
        from ursina import Text, invoke, destroy, held_keys
        t = Text(text='You were caught! Press R to retry.', position=(0,0), origin=(0,0), scale=1.2, color=color.white)
        def wait_retry():
            if held_keys['r']:
                destroy(t)
                build_level(seed=random.randint(0,999999), level_n=level_num)
                return
            invoke(wait_retry, delay=0.02)
        invoke(wait_retry, delay=0.02)
        # Temporarily disable updates until restart
        app.update = lambda: None
        def reenable():
            app.update = level_loop
        invoke(reenable, delay=0.05)
        return

    # Win condition
    if not runes:
        show_lore(get_lore_for_level(level_num))
        # advance after short delay to avoid double-trigger
        from ursina import invoke
        def next_level():
            nonlocal level_num
            level_num += 1
            if level_num <= LEVEL_COUNT:
                build_level(seed=random.randint(0,999999), level_n=level_num)
            else:
                show_lore(["You uncovered the Lost Scripts of Sanskriti.",
                           f"Final Score: {int(player.score)}",
                           "The past guides the seeker of truth."])
                # stop update
                app.update = lambda: None
        invoke(next_level, delay=0.25)
        # prevent multiple triggers
        app.update = lambda: None
        def reenable():
            app.update = level_loop
        invoke(reenable, delay=0.5)
        return

    # HUD
    hud.update(score=player.score, level=level_num, stamina=player.stamina)

def get_lore_for_level(n):
    lore = {
        1: ["Level I — Whispering Courtyards",
            "You recover the first shard of the script.",
            "It hums like a temple bell at dawn."],
        2: ["Level II — Hall of Mirrors",
            "Glyphs reflect memories you thought you forgot.",
            "The walls are listening."],
        3: ["Level III — Sunken Stacks",
            "Sanskrit curves entwine like rivers.",
            "A watcher prowls between shelves."],
        4: ["Level IV — Vault of Echoes",
            "Speak the signs and the signs will speak.",
            "Footsteps double in the dark."],
        5: ["Level V — Sanctum of the Last Script",
            "The sentinel of ages guards the final rune.",
            "Walk softly — the past looks back."]
    }
    return lore.get(n, ["An old script, half-remembered."])

def start_game():
    global level_num
    level_num = 1
    build_level(seed=random.randint(0, 999999), level_n=level_num)
    app.update = level_loop

# Start
start_game()
app.run()
