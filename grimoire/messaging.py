from __future__ import annotations

"""Standardised inter-familiar message protocol.

This lightweight helper provides a unified structure (`Message`) for all
socket-based communications between familiars.  Using a dataclass enforces a
consistent schema while remaining serialisable as a normal Python `dict`.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional
import time

__all__ = ["Message", "build_message", "is_message"]


@dataclass
class Message:
    """A structured communication unit sent over sockets."""

    sender: str                # familiar true_name or friendly name
    target: Optional[str]      # intended recipient; None == broadcast
    category: str              # arbitrary category: "command", "info", etc.
    payload: Any               # the actual content
    timestamp: float = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        return cls(**data)  # type: ignore[arg-type]

    # Convenience pretty-print
    def __str__(self) -> str:  # pragma: no cover
        tgt = self.target or "*"
        return f"[{self.category}] {self.sender} -> {tgt}: {self.payload} (@{self.timestamp:.2f})"


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def build_message(sender: str, payload: Any, *, category: str = "generic", target: Optional[str] = None) -> Message:
    """Helper to quickly build Message objects."""
    return Message(sender=sender, target=target, category=category, payload=payload)


def is_message(obj: Any) -> bool:
    return isinstance(obj, Message) or (
        isinstance(obj, dict) and {"sender", "category", "payload", "timestamp"}.issubset(obj.keys())
    )