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

from typing import Optional

from grimoire.familiars import register_familiar_class
from grimoire.familiars.types import FamiliarType

import importlib

def _base_cls():
    interpreter = importlib.import_module("grimoire.interpreter")  # type: ignore
    return getattr(interpreter, "GrimoireFamiliar")


@register_familiar_class("Perception")
class PerceptionFamiliar(_base_cls()):
    """Familiar that provides environmental perception capabilities."""

    def __init__(self, name: str, *, vision_range: int = 5, true_name: Optional[str] = None):
        super().__init__(name, "Perception", capabilities={}, true_name=true_name)
        self.category = FamiliarType.PERCEPTION
        self.vision_range = vision_range

        self.add_socket("perception_output", direction="output")
        # register with spatial grid as sensor (no position, but treat as entity for queries)
        from grimoire.game.spatial import get_global_grid
        self.position = (0, 0)
        get_global_grid().add_entity(self, self.position)

    def set_position(self, x: int, y: int):
        from grimoire.game.spatial import get_global_grid
        self.position = (x, y)
        get_global_grid().move_entity(self, self.position)

    def scan_environment(self):
        from grimoire.game.spatial import get_global_grid
        grid = get_global_grid()
        entities = grid.query_visible(self.position, self.vision_range)
        perceived = [e.name for e in entities if e is not self]
        self.send_to_socket("perception_output", perceived)

    def autonomous_update(self):
        super().autonomous_update()
        self.scan_environment()