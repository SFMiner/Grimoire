from __future__ import annotations

from typing import Tuple
from math import hypot
from grimoire.game.spatial import get_global_grid, Position

__all__ = [
    'distance', 'path_length'
]

def distance(a: Position, b: Position) -> float:
    return hypot(b[0]-a[0], b[1]-a[1])


def path_length(start: Position, goal: Position) -> int:
    grid = get_global_grid()
    path = grid.find_path(start, goal)
    return len(path)-1 if path else 9999