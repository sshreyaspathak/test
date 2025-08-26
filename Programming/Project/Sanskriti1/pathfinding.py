# pathfinding.py
# A* on grid
import heapq
import math
from settings3d import ORTHO_COST, DIAG_COST

def neighbors(cell, grid):
    x, y = cell
    w = grid.shape[1]
    h = grid.shape[0]
    out = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and grid[ny, nx] == 0:
                cost = DIAG_COST if dx and dy else ORTHO_COST
                out.append(((nx, ny), cost))
    return out

def heuristic(a, b):
    return math.hypot(b[0]-a[0], b[1]-a[1])

def astar(grid, start, goal, max_nodes=10000):
    if start == goal:
        return [start]
    open_set = []
    heapq.heappush(open_set, (heuristic(start, goal), 0, start))
    came = {}
    g = {start: 0}
    nodes = 0
    while open_set:
        _, cost, cur = heapq.heappop(open_set)
        nodes += 1
        if cur == goal:
            path = [cur]
            while cur in came:
                cur = came[cur]
                path.append(cur)
            return list(reversed(path))
        for nxt, move_cost in neighbors(cur, grid):
            new_cost = cost + move_cost
            if nxt not in g or new_cost < g[nxt]:
                g[nxt] = new_cost
                came[nxt] = cur
                heapq.heappush(open_set, (new_cost + heuristic(nxt, goal), new_cost, nxt))
        if nodes > max_nodes:
            break
    return []
