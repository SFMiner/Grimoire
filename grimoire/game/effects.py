from __future__ import annotations

"""Simple one-shot effects that operate on entity properties."""

from typing import Callable, Any

class Effect:
    def __init__(self, name: str, apply_fn: Callable[[Any], None]):
        self.name = name
        self.apply_fn = apply_fn

    def apply(self, target):
        self.apply_fn(target)

    def __repr__(self):  # pragma: no cover
        return f"<Effect {self.name}>"