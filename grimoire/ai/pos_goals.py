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

from typing import Any, Optional
from grimoire.ai.goals import Goal
from grimoire.ai.actions import Action
from grimoire.ai.conditions import CallableCondition
from grimoire.ai.spatial_utils import distance
from grimoire.game.spatial import get_global_grid

class MoveToGoal(Goal):
    """Goal to move familiar towards target entity within radius."""

    def __init__(self, target_entity, radius: int = 1, priority: int = 5):
        def cond(fam):
            return distance(fam.position, target_entity.position) <= radius
        super().__init__(f"move_to_{target_entity.name}", priority, CallableCondition(cond))
        self.target = target_entity
        self.radius = radius
        # Add default movement action
        self.add_action(MoveTowardsAction(target_entity))


class MoveTowardsAction(Action):
    def __init__(self, target_entity):
        super().__init__(f"move_towards_{target_entity.name}", self._effect)
        self.target = target_entity

    def _effect(self, fam):
        grid = get_global_grid()
        path = grid.find_path(fam.position, self.target.position)
        if len(path) > 1:
            next_pos = path[1]
            fam.set_position(*next_pos)