# Grimoire Programming Language
# Copyright (C) 2025 Sean Miner
#
# This file is part of Grimoire.
#
# Grimoire is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Grimoire is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

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