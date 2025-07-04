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