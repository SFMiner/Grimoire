#!/usr/bin/env python3
"""Grimoire global World-State store.

This rudimentary implementation provides a shared, mutable dictionary-like
object that all agents (familiars, spirits, archons, game-loop, etc.) can query
or mutate.  A lightweight publish/subscribe hook lets interested parties react
when keys change.

NOTE:  For now this is an in-memory singleton.  A future phase can replace it
with plane-aware or persistent back-ends.
"""
import threading
from typing import Any, Callable, Dict, List, Optional

__all__ = [
    "WorldState",
    "get_world_state",
]


class WorldState:
    """Thread-safe dict-like store with subscription hooks."""

    _instance: Optional["WorldState"] = None
    _lock = threading.RLock()

    # Attribute annotations for type-checkers
    _data: Dict[str, Any]
    _subscribers: Dict[str, List[Callable[[str, Any, Any], None]]]

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------
    def __new__(cls):  # noqa: D401
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                # Initialise internal storage lazily
                cls._instance._data = {}
                cls._instance._subscribers = {}
            return cls._instance

    # ------------------------------------------------------------------
    # Core kv helpers
    # ------------------------------------------------------------------
    def get(self, key: str, default: Any = None) -> Any:  # noqa: D401
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:  # noqa: D401
        old = self._data.get(key)
        self._data[key] = value
        self._notify(key, old, value)

    def update(self, mapping: Dict[str, Any]) -> None:  # noqa: D401
        for k, v in mapping.items():
            self.set(k, v)

    def to_dict(self) -> Dict[str, Any]:  # noqa: D401
        return dict(self._data)

    # ------------------------------------------------------------------
    # Subscription helpers
    # ------------------------------------------------------------------
    def subscribe(self, key: str, callback: Callable[[str, Any, Any], None]) -> None:
        """Call *callback(key, old, new)* whenever *key* changes."""
        self._subscribers.setdefault(key, []).append(callback)

    def unsubscribe(self, key: str, callback: Callable[[str, Any, Any], None]) -> None:
        if key in self._subscribers and callback in self._subscribers[key]:
            self._subscribers[key].remove(callback)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _notify(self, key: str, old: Any, new: Any):  # noqa: D401
        if key in self._subscribers:
            for cb in list(self._subscribers[key]):
                try:
                    cb(key, old, new)
                except Exception:  # pragma: no cover – best-effort notification
                    pass


# Convenience singleton accessor ------------------------------------------------

def get_world_state() -> WorldState:  # noqa: D401
    """Return the global *WorldState* singleton."""
    return WorldState()