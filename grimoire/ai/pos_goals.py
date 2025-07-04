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