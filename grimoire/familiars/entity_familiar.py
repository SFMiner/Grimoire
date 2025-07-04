#!/usr/bin/env python3
"""
Grimoire Entity Familiar

This module implements the EntityFamiliar class, which specializes in
managing entity properties, state persistence, and property-based interactions.
"""

import time
from typing import Any, Dict, Optional, Set, List
from dataclasses import dataclass
import copy

try:
    from ..interpreter import GrimoireFamiliar
except ImportError:
    # Fallback for testing
    from grimoire.interpreter import GrimoireFamiliar

from .types import FamiliarType, FamiliarCapability, get_familiar_spec, FamiliarCapabilityError
from . import register_familiar_class


@dataclass
class PropertyUpdate:
    """Represents a property update event."""
    property_name: str
    old_value: Any
    new_value: Any
    timestamp: float
    source: str
    
    def __post_init__(self):
        if self.timestamp == 0:
            self.timestamp = time.time()


@register_familiar_class("Entity")
class EntityFamiliar(GrimoireFamiliar):
    """
    Familiar specialized for entity property management and state handling.
    
    EntityFamiliars excel at:
    - Managing entity properties with change tracking
    - Notifying other familiars of property changes via sockets
    - Persisting entity state
    - Handling property queries and updates
    - Maintaining property history
    """
    
    def __init__(self, name: str, entity_data: Optional[Dict[str, Any]] = None, 
                 true_name: Optional[str] = None):
        # Initialize base familiar
        super().__init__(name, FamiliarType.ENTITY.name, {}, true_name)
        
        # Set familiar type and validate capabilities
        self.familiar_type = FamiliarType.ENTITY
        # Note: capabilities should be a dict for the base class, but we track our type capabilities separately
        self.capability_types = {
            FamiliarCapability.PROPERTY_MANAGEMENT,
            FamiliarCapability.SOCKET_MANAGEMENT,
            FamiliarCapability.STATE_PERSISTENCE
        }
        
        # Validate we have required capabilities
        spec = get_familiar_spec(self.familiar_type)
        missing = spec.required_capabilities - self.capability_types
        if missing:
            raise FamiliarCapabilityError(f"EntityFamiliar missing required capabilities: {missing}")
        
        # Initialize entity-specific attributes
        self.properties: Dict[str, Any] = entity_data or {}
        self.property_history: List[PropertyUpdate] = []
        self.property_watchers: Dict[str, Set[str]] = {}  # property -> set of watcher names
        self.max_history_size = 100
        self.change_tracking_enabled = True
        
        # Auto-create standard sockets based on specification
        self._setup_default_sockets()
        
        # Initialize property management
        self._setup_property_management()
    
    def _setup_default_sockets(self):
        """Set up default sockets for entity familiar."""
        spec = get_familiar_spec(self.familiar_type)
        
        for socket_name, direction in spec.default_sockets.items():
            try:
                self.add_socket(socket_name, direction=direction)
            except Exception as e:
                # Socket might already exist, that's OK
                pass
    
    def has_socket(self, name: str) -> bool:
        """Check if familiar has a socket with the given name."""
        return name in self.sockets
    
    def _setup_property_management(self):
        """Set up property management system."""
        # Set up socket handlers for property operations
        if self.has_socket("property_input"):
            # Property input socket can receive property update commands
            pass  # Socket handling would be implemented in socket system
        
        if self.has_socket("state_query"):
            # State query socket can receive requests for entity state
            pass  # Socket handling would be implemented in socket system
    
    def update_property(self, property_name: str, new_value: Any, 
                       source: str = "direct") -> bool:
        """
        Update entity property and notify via sockets.
        
        Args:
            property_name: Name of the property to update
            new_value: New value for the property
            source: Source of the update (for tracking)
            
        Returns:
            True if property was updated, False otherwise
        """
        old_value = self.properties.get(property_name)
        
        # Update the property
        self.properties[property_name] = new_value
        
        # Track the change if enabled
        if self.change_tracking_enabled:
            update = PropertyUpdate(
                property_name=property_name,
                old_value=old_value,
                new_value=new_value,
                timestamp=time.time(),
                source=source
            )
            self.property_history.append(update)
            
            # Trim history if too long
            if len(self.property_history) > self.max_history_size:
                self.property_history = self.property_history[-self.max_history_size:]
        
        # Notify watchers via socket
        self._notify_property_change(property_name, old_value, new_value)
        
        # Log activity
        self.log_activity(
            "self", 
            f"Property '{property_name}' updated from {old_value} to {new_value}",
            {
                "property": property_name,
                "old_value": old_value,
                "new_value": new_value,
                "source": source
            }
        )
        
        return True
    
    def get_property(self, property_name: str, default: Any = None) -> Any:
        """
        Get entity property value.
        
        Args:
            property_name: Name of the property to get
            default: Default value if property doesn't exist
            
        Returns:
            Property value or default
        """
        value = self.properties.get(property_name, default)
        
        # Log property access
        self.log_activity(
            "self",
            f"Property '{property_name}' accessed",
            {"property": property_name, "value": value}
        )
        
        return value
    
    def has_property(self, property_name: str) -> bool:
        """Check if entity has a specific property."""
        return property_name in self.properties
    
    def remove_property(self, property_name: str) -> bool:
        """
        Remove a property from the entity.
        
        Args:
            property_name: Name of the property to remove
            
        Returns:
            True if property was removed, False if it didn't exist
        """
        if property_name in self.properties:
            old_value = self.properties.pop(property_name)
            
            # Track the removal
            if self.change_tracking_enabled:
                update = PropertyUpdate(
                    property_name=property_name,
                    old_value=old_value,
                    new_value=None,
                    timestamp=time.time(),
                    source="removal"
                )
                self.property_history.append(update)
            
            # Notify watchers
            self._notify_property_change(property_name, old_value, None)
            
            self.log_activity(
                "self",
                f"Property '{property_name}' removed",
                {"property": property_name, "old_value": old_value}
            )
            
            return True
        return False
    
    def get_all_properties(self) -> Dict[str, Any]:
        """Get a copy of all entity properties."""
        return copy.deepcopy(self.properties)
    
    def set_properties(self, properties: Dict[str, Any], source: str = "batch") -> None:
        """
        Set multiple properties at once.
        
        Args:
            properties: Dictionary of property names and values
            source: Source of the updates
        """
        for prop_name, value in properties.items():
            self.update_property(prop_name, value, source)
    
    def get_property_history(self, property_name: Optional[str] = None) -> List[PropertyUpdate]:
        """
        Get property change history.
        
        Args:
            property_name: If specified, only return history for this property
            
        Returns:
            List of PropertyUpdate objects
        """
        if property_name:
            return [update for update in self.property_history 
                   if update.property_name == property_name]
        return copy.deepcopy(self.property_history)
    
    def add_property_watcher(self, property_name: str, watcher_name: str) -> None:
        """
        Add a watcher for property changes.
        
        Args:
            property_name: Property to watch
            watcher_name: Name of the watcher (usually another familiar)
        """
        if property_name not in self.property_watchers:
            self.property_watchers[property_name] = set()
        self.property_watchers[property_name].add(watcher_name)
    
    def remove_property_watcher(self, property_name: str, watcher_name: str) -> None:
        """Remove a property watcher."""
        if property_name in self.property_watchers:
            self.property_watchers[property_name].discard(watcher_name)
            if not self.property_watchers[property_name]:
                del self.property_watchers[property_name]
    
    def _notify_property_change(self, property_name: str, old_value: Any, new_value: Any) -> None:
        """Notify watchers of property changes via sockets."""
        if self.has_socket("property_output"):
            notification = {
                "type": "property_update",
                "entity": self.name,
                "property": property_name,
                "old_value": old_value,
                "new_value": new_value,
                "timestamp": time.time()
            }
            
            try:
                self.send_to_socket("property_output", notification)
                self.log_activity(
                    "inter_familiar",
                    f"Property change notification sent for '{property_name}'",
                    notification
                )
            except Exception as e:
                self.log_activity(
                    "self",
                    f"Failed to send property notification: {e}",
                    {"error": str(e), "property": property_name}
                )
    
    def get_state_snapshot(self) -> Dict[str, Any]:
        """Get a complete state snapshot for persistence."""
        return {
            "name": self.name,
            "familiar_type": self.familiar_type.name,
            "properties": copy.deepcopy(self.properties),
            "property_history": [
                {
                    "property_name": update.property_name,
                    "old_value": update.old_value,
                    "new_value": update.new_value,
                    "timestamp": update.timestamp,
                    "source": update.source
                }
                for update in self.property_history
            ],
            "capabilities": [cap.name for cap in self.capability_types],
            "creation_time": getattr(self, 'creation_time', time.time())
        }
    
    def restore_from_snapshot(self, snapshot: Dict[str, Any]) -> bool:
        """Restore state from a snapshot."""
        try:
            self.properties = snapshot.get("properties", {})
            
            # Restore property history
            history_data = snapshot.get("property_history", [])
            self.property_history = [
                PropertyUpdate(
                    property_name=h["property_name"],
                    old_value=h["old_value"],
                    new_value=h["new_value"],
                    timestamp=h["timestamp"],
                    source=h["source"]
                )
                for h in history_data
            ]
            
            self.log_activity(
                "self",
                "State restored from snapshot",
                {"properties_count": len(self.properties), "history_count": len(self.property_history)}
            )
            
            return True
        except Exception as e:
            self.log_activity(
                "self",
                f"Failed to restore from snapshot: {e}",
                {"error": str(e)}
            )
            return False
    
    def clear_property_history(self) -> None:
        """Clear the property change history."""
        old_count = len(self.property_history)
        self.property_history.clear()
        self.log_activity(
            "self",
            f"Property history cleared ({old_count} entries removed)",
            {"cleared_count": old_count}
        )
    
    def set_change_tracking(self, enabled: bool) -> None:
        """Enable or disable property change tracking."""
        self.change_tracking_enabled = enabled
        self.log_activity(
            "self",
            f"Change tracking {'enabled' if enabled else 'disabled'}",
            {"tracking_enabled": enabled}
        )
    
    def get_current_time(self) -> float:
        """Get current timestamp (can be overridden for testing)."""
        return time.time()
    
    # Override inquire to handle entity-specific queries
    def inquire(self, query: str) -> Any:
        """Handle entity-specific inquiries."""
        if query.startswith("property."):
            property_name = query[9:]  # Remove "property." prefix
            return self.get_property(property_name)
        elif query == "all_properties":
            return self.get_all_properties()
        elif query == "property_count":
            return len(self.properties)
        elif query == "change_history":
            return len(self.property_history)
        elif query.startswith("history."):
            property_name = query[8:]  # Remove "history." prefix
            return self.get_property_history(property_name)
        else:
            # Fall back to base familiar inquire
            return super().inquire(query)
    
    def __str__(self) -> str:
        return f"<EntityFamiliar {self.name} ({len(self.properties)} properties)>"
    
    def __repr__(self) -> str:
        return f"EntityFamiliar(name='{self.name}', properties={list(self.properties.keys())})"