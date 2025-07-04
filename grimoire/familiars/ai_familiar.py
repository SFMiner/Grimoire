from __future__ import annotations

from typing import Optional

from grimoire.familiars import register_familiar_class
from grimoire.familiars.types import FamiliarType

import importlib
from grimoire.ai import AIPlanner, Goal, Action, CallableCondition

def _base_cls():
    interpreter = importlib.import_module("grimoire.interpreter")  # type: ignore
    return getattr(interpreter, "GrimoireFamiliar")


@register_familiar_class("AI")
class AIFamiliar(_base_cls()):
    """Familiar equipped with rudimentary goal/action planning hooks."""

    def __init__(self, name: str, *, true_name: Optional[str] = None):
        super().__init__(name, "AI", capabilities={}, true_name=true_name)
        self.category = FamiliarType.AI
        self.goals = []  # To be expanded in future phases
        self.planner = AIPlanner()
        self.latest_perception = []

        # Sockets for interfacing with planners / entity familiars
        self.add_socket("decision_output", direction="output")
        self.add_socket("state_input", direction="input")
        from grimoire.game.spatial import get_global_grid
        self.position = (0,0)
        get_global_grid().add_entity(self, self.position)

    def set_position(self, x: int, y: int):
        from grimoire.game.spatial import get_global_grid
        self.position = (x, y)
        get_global_grid().move_entity(self, self.position)

    # ------------------------------------------------------------------
    # Goal & action registration helpers
    # ------------------------------------------------------------------
    def add_goal(self, name: str, priority: int, condition):
        self.planner.add_goal(Goal(name, priority, CallableCondition(condition)))

    def add_custom_goal(self, goal):
        from grimoire.ai.goals import Goal as _G
        if isinstance(goal, _G):
            self.planner.add_goal(goal)

    def add_action(self, goal_name: str, action_name: str, effect, precondition=lambda _: True):
        # find goal
        for g in self.planner.goals:
            if g.name == goal_name:
                g.add_action(Action(action_name, effect, precondition=CallableCondition(precondition)))
                break

    def plan(self):
        # update internal perception before planning
        try:
            data = self.receive_from_socket('state_input')
            if isinstance(data, list):
                self.latest_perception = data
        except RuntimeError:
            pass
        action = self.planner.plan(self)
        if action:
            action.execute(self)
            # log
            self.log_activity("self", "AI executed action", {"action": action.name})
        else:
            self.log_activity("self", "AI idle", {})

    def autonomous_update(self):
        super().autonomous_update()
        self.plan()