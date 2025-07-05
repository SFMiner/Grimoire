# Grimoire Programming Language
# Copyright (C) 2025 Sean Miner
#
# This file is part of Grimoire.
#
# Grimoire is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Grimoire is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

"""Very simple 2D spatial grid for entity positioning & queries."""

from typing import Dict, List, Tuple, Any
from collections import defaultdict
import math

Position = Tuple[int, int]

class SpatialGrid:
    def __init__(self, width: int = 100, height: int = 100, cell_size: int = 10):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        # map cell_index -> set(entity)
        self.cells: Dict[Tuple[int, int], set] = defaultdict(set)
        self.positions: Dict[Any, Position] = {}
        self.obstacles: set[Position] = set()  # blocked world-grid cells

    # ------------------------------------------------------------------
    def _cell(self, pos: Position) -> Tuple[int, int]:
        return (pos[0] // self.cell_size, pos[1] // self.cell_size)

    def add_entity(self, entity, pos: Position):
        self.positions[entity] = pos
        self.cells[self._cell(pos)].add(entity)

    def move_entity(self, entity, new_pos: Position):
        old = self.positions.get(entity)
        if old is not None:
            self.cells[self._cell(old)].discard(entity)
        self.positions[entity] = new_pos
        self.cells[self._cell(new_pos)].add(entity)

    def remove_entity(self, entity):
        pos = self.positions.pop(entity, None)
        if pos is not None:
            self.cells[self._cell(pos)].discard(entity)

    # ------------------------------------------------------------------
    # Obstacle/terrain helpers
    # ------------------------------------------------------------------
    def add_obstacle(self, x: int, y: int):
        self.obstacles.add((x, y))

    def remove_obstacle(self, x: int, y: int):
        self.obstacles.discard((x, y))

    # simple square query
    def query_radius(self, center: Position, radius: int) -> List[Any]:
        min_x = max(center[0] - radius, 0)
        max_x = min(center[0] + radius, self.width)
        min_y = max(center[1] - radius, 0)
        max_y = min(center[1] + radius, self.height)
        res = []
        cell_min = (min_x // self.cell_size, min_y // self.cell_size)
        cell_max = (max_x // self.cell_size, max_y // self.cell_size)
        for cx in range(cell_min[0], cell_max[0] + 1):
            for cy in range(cell_min[1], cell_max[1] + 1):
                for ent in self.cells.get((cx, cy), ()):  # type: ignore[arg-type]
                    pos = self.positions[ent]
                    if (pos[0]-center[0])**2 + (pos[1]-center[1])**2 <= radius**2:
                        res.append(ent)
        return res

    # Simple line-of-sight: returns True if straight-line distance <= radius and no obstacles (placeholder)
    def line_of_sight(self, a: Position, b: Position, max_distance: int | None = None) -> bool:
        dx = b[0] - a[0]
        dy = b[1] - a[1]
        dist_sq = dx * dx + dy * dy
        if max_distance is not None and dist_sq > max_distance * max_distance:
            return False
        # Bresenham line algorithm between points in grid space (cell units)
        x0, y0 = a
        x1, y1 = b
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            if (x, y) in self.obstacles and (x, y) != a and (x, y) != b:
                return False
            if (x, y) == (x1, y1):
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        if max_distance is not None:
            return dx*dx + dy*dy <= max_distance*max_distance
        return True

    def query_visible(self, center: Position, radius: int) -> List[Any]:
        """Return entities within *radius* that have direct line-of-sight to *center*."""
        candidates = self.query_radius(center, radius)
        return [e for e in candidates if self.line_of_sight(center, self.positions[e], radius)]

    # ------------------------------------------------------------------
    # Cone of vision query
    # ------------------------------------------------------------------
    def query_cone(self, center: Position, radius: int, facing: Tuple[float,float], fov_deg: float) -> List[Any]:
        """Return entities within *radius* inside a cone defined by *facing* unit vector and field-of-view angle."""
        import math
        facing_x, facing_y = facing
        norm = math.hypot(facing_x, facing_y)
        if norm == 0:
            return []
        facing_x /= norm
        facing_y /= norm
        half_angle = math.radians(fov_deg) / 2
        cos_limit = math.cos(half_angle)
        visible = []
        for ent in self.query_visible(center, radius):
            pos = self.positions[ent]
            vec_x, vec_y = pos[0]-center[0], pos[1]-center[1]
            dist = math.hypot(vec_x, vec_y)
            if dist == 0:
                continue
            vec_x /= dist
            vec_y /= dist
            dot = vec_x * facing_x + vec_y * facing_y
            if dot >= cos_limit:
                visible.append(ent)
        return visible

    # ------------------------------------------------------------------
    # Pathfinding (A*)
    # ------------------------------------------------------------------
    def find_path(self, start: Position, goal: Position) -> List[Position]:
        """Very simple A* ignoring diagonal moves."""
        from heapq import heappush, heappop
        open_set: list[tuple[int, Position]] = []
        heappush(open_set, (0, start))
        came: Dict[Position, Position | None] = {start: None}
        g_score: Dict[Position, int] = {start: 0}

        def neighbors(pos: Position):
            for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                nx, ny = pos[0]+dx, pos[1]+dy
                if 0<=nx<self.width and 0<=ny<self.height and (nx,ny) not in self.obstacles:
                    yield (nx, ny)

        while open_set:
            _, current = heappop(open_set)
            if current == goal:
                # reconstruct
                path = []
                while current is not None:
                    path.append(current)
                    current = came[current]
                return path[::-1]
            for n in neighbors(current):
                tentative = g_score[current] + 1
                if tentative < g_score.get(n, 1e9):
                    came[n] = current
                    g_score[n] = tentative
                    heappush(open_set, (tentative + abs(n[0]-goal[0])+abs(n[1]-goal[1]), n))
        return []

# Global shared grid ---------------------------------------------------------
_global_grid: SpatialGrid | None = None

def get_global_grid() -> SpatialGrid:
    global _global_grid
    if _global_grid is None:
        _global_grid = SpatialGrid()
    return _global_grid