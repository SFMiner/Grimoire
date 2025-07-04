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
        from grimoire.game.properties import EntityProperties
        self.properties_container = EntityProperties()
        if entity_data:
            for k, v in entity_data.items():
                self.properties_container.add(k, v)

        # Standard sockets
        self.add_socket("property_input", direction="input")
        self.add_socket("property_output", direction="output")

        # default position (0,0) register in spatial grid
        from grimoire.game.spatial import get_global_grid
        self.position = (0, 0)
        get_global_grid().add_entity(self, self.position)

    # Position helpers
    def set_position(self, x: int, y: int):
        from grimoire.game.spatial import get_global_grid
        self.position = (x, y)
        get_global_grid().move_entity(self, self.position)

    # ------------------------------------------------------------------
    # Socket-driven operations
    # ------------------------------------------------------------------
    def _receive(self):
        """Continuously receive on property_input and update properties. (placeholder)"""
        pass

    # Example helper APIs
    def update_property(self, key: str, value: Any):
        try:
            self.properties_container.set_base(key, value)
        except KeyError:
            self.properties_container.add(key, value)
        # broadcast updated property
        self.send_to_socket("property_output", {key: value})

    def get_property(self, key: str, default: Any = None) -> Any:
        return self.properties_container.get(key, default)

    # Override inquire to expose entity props
    def inquire(self, query: str):
        if query.startswith("prop:"):
            return self.properties_container.get(query[5:])
        if query == "position":
            return self.position
        return super().inquire(query)