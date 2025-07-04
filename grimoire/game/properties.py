from __future__ import annotations

"""Entity property specifications and runtime value calculation."""

from dataclasses import dataclass, field
from typing import Dict, List

from .modifiers import Modifier

@dataclass
class PropertySpec:
    name: str
    base_value: float
    min_value: float | None = None
    max_value: float | None = None
    modifiers: List[Modifier] = field(default_factory=list)

    # --- runtime -----------------------------------------------------------
    def current_value(self) -> float:
        value = self.base_value
        for mod in self.modifiers:
            value = mod.apply(value)
        if self.min_value is not None:
            value = max(value, self.min_value)
        if self.max_value is not None:
            value = min(value, self.max_value)
        return value

    def add_modifier(self, mod: Modifier):
        self.modifiers.append(mod)

    def tick_modifiers(self):
        self.modifiers[:] = [m for m in self.modifiers if not m.tick()]


class EntityProperties:
    """Container for multiple `PropertySpec` objects keyed by name."""

    def __init__(self):
        self._props: Dict[str, PropertySpec] = {}

    # CRUD --------------------------------------------------
    def add(self, name: str, base: float, *, min_: float | None = None, max_: float | None = None):
        self._props[name] = PropertySpec(name, base, min_, max_)

    def get(self, name: str) -> float:
        return self._props[name].current_value()

    def set_base(self, name: str, value: float):
        self._props[name].base_value = value

    def modify(self, name: str, delta: float):
        spec = self._props[name]
        spec.base_value += delta

    def add_modifier(self, name: str, mod: Modifier):
        self._props[name].add_modifier(mod)

    def tick(self):
        for spec in self._props.values():
            spec.tick_modifiers()

    # helper for debug
    def as_dict(self):
        return {n: p.current_value() for n, p in self._props.items()}