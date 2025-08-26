# pathfinding.py
import heapq
import math

from settings import DIAGONAL_COST, ORTHO_COST

def neighbors(cell, grid):
    x, y = cell
    w = grid.shape[1]
    h = grid.shape[0]
    results = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and grid[ny, nx] == 0:
                cost = DIAGONAL_COST if dx != 0 and dy != 0 else ORTHO_COST
                results.append(((nx, ny), cost))
    return results

def heuristic(a, b):
    # Euclidean
    return math.hypot(b[0] - a[0], b[1] - a[1])

def astar(grid, start, goal, max_nodes=10000):
    """Return path as list of cells from start to goal, or [] if none."""
    if start == goal:
        return [start]
    open_set = []
    heapq.heappush(open_set, (0 + heuristic(start, goal), 0, start, None))
    came_from = {}
    cost_so_far = {start: 0}
    nodes = 0
    while open_set:
        _, current_cost, current, parent = heapq.heappop(open_set)
        nodes += 1
        if current == goal:
            # reconstruct
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            return list(reversed(path))
        for nxt, move_cost in neighbors(current, grid):
            new_cost = current_cost + move_cost
            if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                cost_so_far[nxt] = new_cost
                priority = new_cost + heuristic(nxt, goal)
                came_from[nxt] = current
                heapq.heappush(open_set, (priority, new_cost, nxt, current))
        if nodes > max_nodes:
            break
    return []
