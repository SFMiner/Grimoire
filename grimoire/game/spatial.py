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

# Global shared grid ---------------------------------------------------------
_global_grid: SpatialGrid | None = None

def get_global_grid() -> SpatialGrid:
    global _global_grid
    if _global_grid is None:
        _global_grid = SpatialGrid()
    return _global_grid