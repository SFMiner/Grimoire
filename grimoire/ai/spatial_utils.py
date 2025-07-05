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