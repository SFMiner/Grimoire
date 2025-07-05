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

"""Goal representation for AI agents."""

from typing import List, Any
from .conditions import Condition, CallableCondition
from .actions import Action

class Goal:
    def __init__(self, name: str, priority: int, condition: Condition):
        self.name = name
        self.priority = priority
        self.condition = condition  # when True, goal satisfied
        self.actions: List[Action] = []

    # ------------------------------------------------------------------
    def is_satisfied(self, familiar: Any) -> bool:
        return bool(self.condition(familiar))

    def add_action(self, action: Action):
        self.actions.append(action)

    # choose first applicable action for now
    def select_action(self, familiar: Any) -> Action | None:
        for act in self.actions:
            if act.is_applicable(familiar):
                return act
        return None

    def __repr__(self):  # pragma: no cover
        return f"<Goal {self.name} prio={self.priority}>"