from __future__ import annotations

from typing import Optional

from grimoire.familiars import register_familiar_class
from grimoire.familiars.types import FamiliarType

import importlib

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

        # Sockets for interfacing with planners / entity familiars
        self.add_socket("decision_output", direction="output")
        self.add_socket("state_input", direction="input")

    def plan(self):
        # placeholder simple decision
        action = {"type": "noop"}
        self.send_to_socket("decision_output", action)

    def autonomous_update(self):
        super().autonomous_update()
        self.plan()