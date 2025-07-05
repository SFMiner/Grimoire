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