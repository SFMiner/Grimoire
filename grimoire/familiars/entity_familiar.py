from __future__ import annotations

from typing import Any, Dict, Optional

from grimoire.familiars import register_familiar_class
from grimoire.familiars.types import FamiliarType

# Import GrimoireFamiliar lazily to avoid circular import at module import time.
import importlib

def _base_cls():
    interpreter = importlib.import_module("grimoire.interpreter")  # type: ignore
    return getattr(interpreter, "GrimoireFamiliar")


@register_familiar_class("Entity")
class EntityFamiliar(_base_cls()):
    """Familiar that wraps a game/entity dictionary and exposes it via sockets."""

    def __init__(self, name: str, entity_data: Optional[Dict[str, Any]] = None, *, true_name: Optional[str] = None):
        super().__init__(name, "Entity", capabilities={}, true_name=true_name)
        self.category = FamiliarType.ENTITY
        # Store arbitrary entity properties.
        self.properties: Dict[str, Any] = entity_data.copy() if entity_data else {}

        # Standard sockets
        self.add_socket("property_input", direction="input")
        self.add_socket("property_output", direction="output")

    # ------------------------------------------------------------------
    # Socket-driven operations
    # ------------------------------------------------------------------
    def _receive(self):
        """Continuously receive on property_input and update properties. (placeholder)"""
        pass

    # Example helper APIs
    def update_property(self, key: str, value: Any):
        self.properties[key] = value
        # broadcast updated property
        self.send_to_socket("property_output", {key: value})

    def get_property(self, key: str, default: Any = None) -> Any:
        return self.properties.get(key, default)

    # Override inquire to expose entity props
    def inquire(self, query: str):
        if query.startswith("prop:"):
            return self.properties.get(query[5:])
        return super().inquire(query)