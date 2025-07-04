from __future__ import annotations

"""Condition primitives used by AI goals/actions."""

from typing import Protocol, Callable, Any

class Condition(Protocol):
    """Condition Protocol: evaluates to bool when given a familiar or context."""

    def __call__(self, familiar: Any) -> bool:  # noqa: D401
        ...

# Concrete condition wrapper around callables
class CallableCondition:
    def __init__(self, func: Callable[[Any], bool]):
        self.func = func

    def __call__(self, familiar):
        return self.func(familiar)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<CallableCondition {self.func.__name__}>"