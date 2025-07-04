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