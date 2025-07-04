from __future__ import annotations

from typing import Any, Dict, Optional
import time

from grimoire.familiars import register_familiar_class
from grimoire.familiars.types import FamiliarType, FamiliarCapability

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
        self.familiar_type = FamiliarType.ENTITY
        self.capabilities = {FamiliarCapability.PROPERTY_MANAGEMENT}
        self.properties = entity_data or {}
        
        # Initialize properties container if available
        try:
            from grimoire.game.properties import EntityProperties
            self.properties_container = EntityProperties()
            if entity_data:
                for k, v in entity_data.items():
                    self.properties_container.add(k, v)
        except ImportError:
            # Fall back to simple dict if properties module unavailable
            self.properties_container = None

        # Auto-create standard sockets
        self.add_socket("property_input", direction="input")
        self.add_socket("property_output", direction="output")
        self.add_socket("state_query", direction="input")

        # default position (0,0) register in spatial grid
        try:
            from grimoire.game.spatial import get_global_grid
            self.position = (0, 0)
            get_global_grid().add_entity(self, self.position)
        except ImportError:
            # Fall back if spatial module unavailable
            self.position = (0, 0)

    # Position helpers
    def set_position(self, x: int, y: int):
        try:
            from grimoire.game.spatial import get_global_grid
            self.position = (x, y)
            get_global_grid().move_entity(self, self.position)
        except ImportError:
            # Fall back if spatial module unavailable
            self.position = (x, y)

    def get_current_time(self):
        """Get current timestamp for messages."""
        return time.time()

    # ------------------------------------------------------------------
    # Socket-driven operations
    # ------------------------------------------------------------------
    def _receive(self):
        """Continuously receive on property_input and update properties. (placeholder)"""
        pass

    # Enhanced property management with socket notifications
    def update_property(self, key: str, value: Any):
        """Update entity property and notify via socket"""
        old_value = self.properties.get(key)
        self.properties[key] = value
        
        # Update properties container if available
        if self.properties_container:
            try:
                self.properties_container.set_base(key, value)
            except KeyError:
                self.properties_container.add(key, value)
        
        # Send update notification via socket
        if hasattr(self, 'sockets') and "property_output" in self.sockets:
            self.send_to_socket("property_output", {
                "property": key,
                "old_value": old_value,
                "new_value": value,
                "timestamp": self.get_current_time()
            })

    def get_property(self, key: str, default: Any = None) -> Any:
        """Get property value with fallback to default."""
        if self.properties_container:
            return self.properties_container.get(key, default)
        return self.properties.get(key, default)

    def has_socket(self, socket_name: str) -> bool:
        """Check if socket exists."""
        return hasattr(self, 'sockets') and socket_name in self.sockets

    # Override inquire to expose entity props
    def inquire(self, query: str):
        if query.startswith("prop:"):
            return self.get_property(query[5:])
        if query == "position":
            return self.position
        if query == "capabilities":
            return list(self.capabilities)
        try:
            return super().inquire(query)
        except Exception:
            return None

    # Message handling for socket communication
    def receive_message(self, message):
        """Handle incoming messages from other familiars."""
        if hasattr(message, 'message_type'):
            if message.message_type == "property_query":
                # Respond to property queries
                property_name = message.payload.get("property")
                if property_name:
                    value = self.get_property(property_name)
                    # Send response back (implementation depends on message system)
                    return {"property": property_name, "value": value}
            elif message.message_type == "property_update":
                # Handle property updates from other familiars
                updates = message.payload
                if isinstance(updates, dict):
                    for key, value in updates.items():
                        self.update_property(key, value)
        return None