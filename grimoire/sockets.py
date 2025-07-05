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

"""Light-weight socket implementation for data exchange between Familiars (and other runtime artifacts).

The goal is to provide a minimal but extendable foundation that can grow into the full
feature-set described in *Defining Sockets and Goals for agents.md* while immediately
unlocking simple data-flow scenarios.

The design keeps dependencies to a minimum to avoid import cycles.  Runtime classes such
as `GrimoireFamiliar` import `Socket` only when needed (type-hints are behind `if TYPE_CHECKING`).
"""

from typing import Any, List, TYPE_CHECKING

__all__ = [
    "Socket",
    "SocketDirectionError",
]


class SocketDirectionError(RuntimeError):
    """Raised when an invalid direction interaction is attempted."""


class Socket:
    """A communication endpoint attached to an owner (e.g. a Familiar).

    Parameters
    ----------
    owner: Any
        The runtime object that owns this socket (usually a `GrimoireFamiliar`).
    name: str
        Symbolic name of the socket (e.g. ``"attack_choice_output"``).
    data_type: str
        Optional semantic description of the data the socket carries.  Currently not
        enforced but reserved for future type-checking.
    direction: str {"input", "output"}
        Indicates whether the socket is a source (``"output"``) or sink (``"input"``).
    """

    def __init__(self, owner: Any, name: str, data_type: str | None = None, *, direction: str = "input"):
        self.owner = owner
        self.name = name
        self.data_type = data_type or "generic"
        if direction not in {"input", "output"}:
            raise ValueError("Socket direction must be 'input' or 'output'")
        self.direction = direction
        self.connections: List["Socket"] = []
        self._value: Any = None

    # ---------------------------------------------------------------------
    # Connection management
    # ---------------------------------------------------------------------
    def connect_to(self, other: "Socket") -> None:
        """Connect *this* output socket to *other* input socket."""
        if self.direction != "output":
            raise SocketDirectionError("Only output sockets can initiate connections")
        if other.direction != "input":
            raise SocketDirectionError("Can only connect to input sockets")
        if other in self.connections:
            return  # Already connected
        self.connections.append(other)

    def disconnect_from(self, other: "Socket") -> None:
        """Remove connection if present."""
        if other in self.connections:
            self.connections.remove(other)

    # ---------------------------------------------------------------------
    # Data flow helpers
    # ---------------------------------------------------------------------
    def send(self, data: Any) -> None:
        """Send *data* to all connected sockets.

        `send` may only be called on *output* sockets.  For now the transport is
        synchronous – receivers are updated immediately.
        """
        if self.direction != "output":
            raise SocketDirectionError("Cannot send from an input socket")
        self._value = data
        for sink in list(self.connections):
            sink._receive(data)

    def _receive(self, data: Any) -> None:
        """Internal method used by `send` of peer sockets."""
        if self.direction != "input":
            raise SocketDirectionError("Cannot receive on an output socket")
        self._value = data

    # ---------------------------------------------------------------------
    # Introspection helpers
    # ---------------------------------------------------------------------
    def has_value(self) -> bool:
        return self._value is not None

    @property
    def value(self) -> Any:
        """Return the last received (or sent) value."""
        return self._value

    # ---------------------------------------------------------------------
    # Debug helpers
    # ---------------------------------------------------------------------
    def __repr__(self) -> str:  # pragma: no cover – debug aid
        direction = "->" if self.direction == "output" else "<-"
        return f"<Socket {direction} {self.owner}.{self.name} ({len(self.connections)} connections)>"