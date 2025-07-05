"""Grimoire Goal Artifact framework (Phase 3).

`GoalArtifact` is a lightweight Python proxy that mirrors the concept of a
Grimoire *artifact* defined in source code.  AI familiars can hold references to
instances of these classes and evaluate goal satisfaction via the common
`is_satisfied(world_state)` API.

NOTE:  In a full compiler/runtime we would generate Python classes at parse
time; this interim implementation simply allows goals defined in Python while
still being referenceable from Grimoire scripts via the built-in
`define_goal()` helper.
"""
from __future__ import annotations

from typing import Any, Dict, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from grimoire.world_state import WorldState, get_world_state

__all__ = [
    "GoalArtifact",
    "register_goal",
]


_goal_registry: Dict[str, "GoalArtifact"] = {}


def register_goal(goal: "GoalArtifact") -> None:
    """Register a goal instance globally so AI familiars can discover it."""
    _goal_registry[goal.name] = goal


def get_registered_goals() -> Dict[str, "GoalArtifact"]:
    return dict(_goal_registry)


@dataclass
class GoalArtifact(ABC):
    """Base class for programmable goals.

    Sub-classes override `is_satisfied` and optionally `on_achieved`.
    """

    name: str
    priority: float = 0.5  # 0..1 weight
    target_satisfaction: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Runtime fields — not part of the dataclass init API
    _current: float = field(default=0.0, init=False, repr=False)

    # Expose for legacy code compatibility
    @property
    def current_satisfaction(self) -> float:  # noqa: D401
        return self._current

    # ------------------------------------------------------------------
    # Core API expected by AIFamiliar
    # ------------------------------------------------------------------
    def get_urgency(self) -> float:  # noqa: D401
        return (1.0 - self._current) * self.priority

    def evaluate(self, ws: Optional[WorldState] = None) -> float:  # noqa: D401
        self._current = self.is_satisfied(ws or get_world_state())
        return self._current

    def is_satisfied(self, ws: WorldState) -> float:  # noqa: D401
        """Return satisfaction (0-1).  Must be implemented by sub-class."""
        return 0.0

    def on_achieved(self, ws: WorldState) -> None:  # noqa: D401
        """Optional hook executed when goal becomes satisfied."""
        pass