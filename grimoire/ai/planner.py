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

"""Simple goal-driven planner choosing actions for AIFamiliar."""

from typing import List, Any, Optional
from .goals import Goal

class AIPlanner:
    def __init__(self):
        self.goals: List[Goal] = []

    # ------------------------------------------------------------------
    def add_goal(self, goal: Goal):
        self.goals.append(goal)
        # keep highest priority first
        self.goals.sort(key=lambda g: g.priority, reverse=True)

    def plan(self, familiar: Any):
        """Return best applicable action for highest priority unmet goal."""
        for goal in self.goals:
            if goal.is_satisfied(familiar):
                continue
            act = goal.select_action(familiar)
            if act is not None:
                return act
        return None