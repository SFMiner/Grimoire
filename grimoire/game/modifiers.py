from __future__ import annotations

"""Modifier system for entity properties (e.g., armor, buffs)."""

from dataclasses import dataclass
from typing import Literal

ModifierType = Literal['add', 'mul']

@dataclass
class Modifier:
    name: str
    value: float
    mod_type: ModifierType = 'add'
    duration: int | None = None  # turns; None = permanent

    def apply(self, base: float) -> float:
        if self.mod_type == 'add':
            return base + self.value
        else:
            return base * self.value

    def tick(self):
        """Advance duration; return True if expired."""
        if self.duration is None:
            return False
        self.duration -= 1
        return self.duration <= 0