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