from __future__ import annotations

"""AI Action representation."""

from typing import Callable, Any, Optional
from .conditions import Condition, CallableCondition

class Action:
    def __init__(self, name: str, effect: Callable[[Any], None], *, precondition: Optional[Condition] = None):
        self.name = name
        self.effect = effect
        self.precondition: Condition = precondition or CallableCondition(lambda _: True)

    def is_applicable(self, familiar) -> bool:
        return self.precondition(familiar)

    def execute(self, familiar):
        self.effect(familiar)

    def __repr__(self):  # pragma: no cover
        return f"<Action {self.name}>"