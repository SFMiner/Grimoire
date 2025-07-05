#!/usr/bin/env python3
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

"""
Grimoire Entity Familiar

A specialized familiar that manages entity properties, state, and interactions.
This familiar excels at property management, change tracking, and state persistence.
"""

import time
from typing import Any, Dict, List, Optional, Set, Callable
from dataclasses import dataclass, field
from collections import defaultdict

try:
    from ..interpreter import GrimoireFamiliar
except ImportError:
    # Fallback for testing
    from grimoire.interpreter import GrimoireFamiliar

# Import tag system for integration
try:
    from ..tag_system import Tag, TagSet, create_tag
    from ..tag_registry import TaggedEntity, tag_registry
    TAG_SYSTEM_AVAILABLE = True
except ImportError:
    TAG_SYSTEM_AVAILABLE = False
    # Create dummy classes if tag system not available
    class TaggedEntity:
        def __init__(self, name: str, entity_type: str, tags=None):
            pass

from . import register_familiar_class
from .types import FamiliarType, FamiliarCapability
from .messaging import FamiliarMessage, MessageType, create_property_update_message, get_global_router


@dataclass
class PropertyUpdate:
    """Represents a property change event."""
    property_name: str
    old_value: Any
    new_value: Any
    timestamp: float
    change_reason: str = "direct_update"
    
    def __post_init__(self):
        if self.timestamp == 0:
            self.timestamp = time.time()


@register_familiar_class("Entity")
class EntityFamiliar(GrimoireFamiliar):
    """
    A familiar specialized in entity property management.
    
    Capabilities:
    - Property change tracking and notifications
    - State persistence and snapshots
    - Property watchers and event handling
    - Socket-based property synchronization
    - Tag system integration (if available)
    """
    
    def __init__(self, name: str):
        # Create empty capabilities dict for base class
        capabilities = {}
        super().__init__(name, "Entity", capabilities)
        
        self.familiar_type = FamiliarType.ENTITY
        # Override capabilities with our set (the base class expects a dict)
        self.capability_types = {
            FamiliarCapability.PROPERTY_MANAGEMENT,
            FamiliarCapability.STATE_PERSISTENCE
        }
        
        # Property management
        self.properties: Dict[str, Any] = {}
        self.property_history: Dict[str, List[PropertyUpdate]] = defaultdict(list)
        self.property_watchers: Dict[str, List[Callable]] = defaultdict(list)
        self.max_history_per_property = 100
        
        # State management
        self.state_snapshots: List[Dict[str, Any]] = []
        self.max_snapshots = 10
        
        # Tag system integration
        if TAG_SYSTEM_AVAILABLE:
            from ..tag_registry import TaggedEntity as TaggedEntityClass
            self.tag_set = TagSet()
            # Create a tagged entity representation
            self._tagged_entity = TaggedEntityClass(name, "familiar")
            # Register this familiar as a tagged entity
            tag_registry.register_entity(self._tagged_entity)
        else:
            self.tag_set = None
            self._tagged_entity = None
        
        # Socket setup for property notifications
        self.setup_property_sockets()
        
        # Message handling
        self.message_handlers: Dict[MessageType, Callable] = {
            MessageType.PROPERTY_UPDATE: self._handle_property_update_message,
            MessageType.QUERY: self._handle_query_message,
            MessageType.NOTIFICATION: self._handle_notification_message
        }
    
    def setup_property_sockets(self):
        """Set up sockets for property-related communication."""
        # Input socket for property updates from other familiars
        self.add_socket("property_input", direction="input")
        
        # Output socket for property change notifications
        self.add_socket("property_output", direction="output")
        
        # State socket for persistence operations
        self.add_socket("state_socket", direction="input")
        
        # Message input socket for general messaging
        self.add_socket("message_input", direction="input")
        
        # Message output socket for sending messages
        self.add_socket("message_output", direction="output")
    
    def set_property(self, property_name: str, value: Any, reason: str = "direct_update") -> bool:
        """
        Set a property value with change tracking and notifications.
        
        Args:
            property_name: Name of the property to set
            value: New value for the property
            reason: Reason for the change (for tracking)
            
        Returns:
            True if property was set successfully
        """
        old_value = self.properties.get(property_name)
        
        # Check if value actually changed
        if old_value == value:
            return True
        
        # Update property
        self.properties[property_name] = value
        
        # Create update record
        update = PropertyUpdate(
            property_name=property_name,
            old_value=old_value,
            new_value=value,
            timestamp=time.time(),
            change_reason=reason
        )
        
        # Add to history
        self.property_history[property_name].append(update)
        
        # Trim history if too long
        if len(self.property_history[property_name]) > self.max_history_per_property:
            self.property_history[property_name] = self.property_history[property_name][-self.max_history_per_property//2:]
        
        # Notify watchers
        self._notify_property_watchers(property_name, old_value, value)
        
        # Send socket notification
        self._send_property_notification(property_name, old_value, value)
        
        # Send message notification to interested familiars
        self._send_property_message(property_name, old_value, value)
        
        return True
    
    def get_property(self, property_name: str, default: Any = None) -> Any:
        """Get a property value."""
        return self.properties.get(property_name, default)
    
    def has_property(self, property_name: str) -> bool:
        """Check if a property exists."""
        return property_name in self.properties
    
    def remove_property(self, property_name: str) -> bool:
        """Remove a property."""
        if property_name in self.properties:
            old_value = self.properties[property_name]
            del self.properties[property_name]
            
            # Record the removal
            update = PropertyUpdate(
                property_name=property_name,
                old_value=old_value,
                new_value=None,
                timestamp=time.time(),
                change_reason="property_removed"
            )
            self.property_history[property_name].append(update)
            
            # Notify watchers
            self._notify_property_watchers(property_name, old_value, None)
            
            return True
        return False
    
    def get_property_history(self, property_name: str, limit: int = 10) -> List[PropertyUpdate]:
        """Get the change history for a property."""
        history = self.property_history.get(property_name, [])
        return history[-limit:]
    
    def add_property_watcher(self, property_name: str, callback: Callable[[str, Any, Any], None]) -> None:
        """
        Add a callback function to watch property changes.
        
        Args:
            property_name: Property to watch (or "*" for all properties)
            callback: Function called with (property_name, old_value, new_value)
        """
        self.property_watchers[property_name].append(callback)
    
    def remove_property_watcher(self, property_name: str, callback: Callable) -> bool:
        """Remove a property watcher."""
        if property_name in self.property_watchers:
            try:
                self.property_watchers[property_name].remove(callback)
                return True
            except ValueError:
                pass
        return False
    
    def _notify_property_watchers(self, property_name: str, old_value: Any, new_value: Any) -> None:
        """Notify all watchers of a property change."""
        # Notify specific property watchers
        for callback in self.property_watchers.get(property_name, []):
            try:
                callback(property_name, old_value, new_value)
            except Exception as e:
                print(f"Error in property watcher for {property_name}: {e}")
        
        # Notify global watchers (watching "*")
        for callback in self.property_watchers.get("*", []):
            try:
                callback(property_name, old_value, new_value)
            except Exception as e:
                print(f"Error in global property watcher: {e}")
    
    def _send_property_notification(self, property_name: str, old_value: Any, new_value: Any) -> None:
        """Send property change notification via socket."""
        if "property_output" in self.sockets:
            notification = {
                "type": "property_change",
                "familiar_name": self.name,
                "property_name": property_name,
                "old_value": old_value,
                "new_value": new_value,
                "timestamp": time.time()
            }
            self.send_to_socket("property_output", notification)
    
    def _send_property_message(self, property_name: str, old_value: Any, new_value: Any) -> None:
        """Send property change message to interested familiars."""
        router = get_global_router()
        
        # Create property update message
        message = create_property_update_message(
            sender_name=self.name,
            sender_true_name=self.true_name,
            recipient_name="*",  # Broadcast to all interested familiars
            property_name=property_name,
            old_value=old_value,
            new_value=new_value
        )
        
        # Route the message
        router.route_message(message)
    
    def create_snapshot(self, snapshot_name: Optional[str] = None) -> str:
        """
        Create a snapshot of the current state.
        
        Args:
            snapshot_name: Optional name for the snapshot
            
        Returns:
            Snapshot ID
        """
        snapshot_id = snapshot_name or f"snapshot_{len(self.state_snapshots)}"
        
        snapshot = {
            "id": snapshot_id,
            "timestamp": time.time(),
            "properties": self.properties.copy(),
            "familiar_state": self.state
        }
        
        self.state_snapshots.append(snapshot)
        
        # Trim snapshots if too many
        if len(self.state_snapshots) > self.max_snapshots:
            self.state_snapshots = self.state_snapshots[-self.max_snapshots//2:]
        
        # Send snapshot notification
        if "state_socket" in self.sockets:
            self.send_to_socket("state_socket", {
                "type": "snapshot_created",
                "snapshot_id": snapshot_id,
                "timestamp": snapshot["timestamp"]
            })
        
        return snapshot_id
    
    def restore_snapshot(self, snapshot_id: str) -> bool:
        """
        Restore state from a snapshot.
        
        Args:
            snapshot_id: ID of the snapshot to restore
            
        Returns:
            True if snapshot was restored successfully
        """
        for snapshot in self.state_snapshots:
            if snapshot["id"] == snapshot_id:
                # Restore properties
                old_properties = self.properties.copy()
                self.properties = snapshot["properties"].copy()
                
                # Restore familiar state
                self.state = snapshot["familiar_state"]
                
                # Notify about all property changes
                for prop_name, new_value in self.properties.items():
                    old_value = old_properties.get(prop_name)
                    if old_value != new_value:
                        self._notify_property_watchers(prop_name, old_value, new_value)
                
                # Notify about removed properties
                for prop_name, old_value in old_properties.items():
                    if prop_name not in self.properties:
                        self._notify_property_watchers(prop_name, old_value, None)
                
                # Send restoration notification
                if "state_socket" in self.sockets:
                    self.send_to_socket("state_socket", {
                        "type": "snapshot_restored",
                        "snapshot_id": snapshot_id,
                        "timestamp": time.time()
                    })
                
                return True
        
        return False
    
    def get_snapshots(self) -> List[Dict[str, Any]]:
        """Get list of available snapshots."""
        return [
            {
                "id": snapshot["id"],
                "timestamp": snapshot["timestamp"],
                "property_count": len(snapshot["properties"])
            }
            for snapshot in self.state_snapshots
        ]
    
    def receive_message(self, message: FamiliarMessage) -> None:
        """Handle incoming messages."""
        if message.message_type in self.message_handlers:
            try:
                self.message_handlers[message.message_type](message)
            except Exception as e:
                print(f"Error handling message {message.message_id}: {e}")
    
    def _handle_property_update_message(self, message: FamiliarMessage) -> None:
        """Handle property update messages from other familiars."""
        payload = message.payload
        
        if "property_name" in payload:
            property_name = payload["property_name"]
            new_value = payload.get("new_value")
            
            # Update our local copy if this is a synchronized property
            if property_name.startswith("sync_"):
                self.set_property(property_name, new_value, "message_sync")
    
    def _handle_query_message(self, message: FamiliarMessage) -> None:
        """Handle query messages about properties."""
        payload = message.payload
        query = payload.get("query", "")
        
        response_payload = {}
        
        if query == "get_all_properties":
            response_payload["properties"] = self.properties.copy()
        elif query.startswith("get_property:"):
            prop_name = query.split(":", 1)[1]
            response_payload["property_value"] = self.get_property(prop_name)
        elif query == "get_property_count":
            response_payload["property_count"] = len(self.properties)
        elif query == "get_snapshots":
            response_payload["snapshots"] = self.get_snapshots()
        else:
            response_payload["error"] = f"Unknown query: {query}"
        
        # Send response
        if message.requires_response:
            response = message.create_response(
                sender_name=self.name,
                sender_true_name=self.true_name,
                payload=response_payload
            )
            
            router = get_global_router()
            router.route_message(response)
    
    def _handle_notification_message(self, message: FamiliarMessage) -> None:
        """Handle general notification messages."""
        payload = message.payload
        
        # Log the notification
        print(f"EntityFamiliar {self.name} received notification: {payload}")
    
    def inquire(self, property_name: str) -> Any:
        """
        Enhanced inquire method with property access support.
        
        Supports:
        - Basic familiar properties (name, true_name, state, familiar_type)
        - Entity properties via property management system
        - Property history and snapshots
        """
        # Handle basic familiar properties first
        if property_name == "name":
            return self.name
        elif property_name == "true_name":
            return self.true_name
        elif property_name == "state":
            return self.state
        elif property_name == "familiar_type":
            return self.familiar_type.name if hasattr(self.familiar_type, 'name') else str(self.familiar_type)
        elif property_name == "type":
            return self.familiar_type
        elif property_name == "capabilities":
            return list(self.capability_types) if hasattr(self, 'capability_types') else []
        elif property_name == "sockets":
            return list(self.sockets.keys())
        
        # Check entity properties
        if property_name in self.properties:
            return self.properties[property_name]
        
        # Special property queries
        if property_name == "property_count":
            return len(self.properties)
        elif property_name == "snapshot_count":
            return len(self.state_snapshots)
        elif property_name.startswith("property_history:"):
            prop_name = property_name.split(":", 1)[1]
            return self.get_property_history(prop_name)
        elif property_name == "all_properties":
            return self.properties.copy()
        elif property_name == "all_snapshots":
            return self.get_snapshots()
        
        return None
    
    def command(self, command: str, arguments: List[Any]) -> Any:
        """Handle commands for the entity familiar."""
        if command == "set_property":
            if len(arguments) >= 2:
                property_name = str(arguments[0])
                value = arguments[1]
                reason = str(arguments[2]) if len(arguments) > 2 else "command"
                return self.set_property(property_name, value, reason)
            else:
                raise RuntimeError("set_property requires at least 2 arguments (name, value)")
        
        elif command == "get_property":
            if len(arguments) >= 1:
                property_name = str(arguments[0])
                default = arguments[1] if len(arguments) > 1 else None
                return self.get_property(property_name, default)
            else:
                raise RuntimeError("get_property requires 1 argument (name)")
        
        elif command == "create_snapshot":
            snapshot_name = str(arguments[0]) if len(arguments) > 0 else None
            return self.create_snapshot(snapshot_name)
        
        elif command == "restore_snapshot":
            if len(arguments) >= 1:
                snapshot_id = str(arguments[0])
                return self.restore_snapshot(snapshot_id)
            else:
                raise RuntimeError("restore_snapshot requires 1 argument (snapshot_id)")
        
        elif command == "get_snapshots":
            return self.get_snapshots()
        
        elif command == "get_status":
            return self.get_status()
        
        else:
            # Fall back to base class command handling
            return super().command(command, arguments)
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the entity familiar."""
        return {
            "name": self.name,
            "true_name": self.true_name,
            "familiar_type": self.familiar_type.name,
            "state": self.state,
            "capabilities": [cap.name for cap in self.capability_types],
            "property_count": len(self.properties),
            "snapshot_count": len(self.state_snapshots),
            "total_property_changes": sum(len(history) for history in self.property_history.values()),
            "active_watchers": sum(len(watchers) for watchers in self.property_watchers.values()),
            "socket_count": len(self.sockets)
        }
    
    def __str__(self) -> str:
        return f"EntityFamiliar(name={self.name}, properties={len(self.properties)}, snapshots={len(self.state_snapshots)})"
    
    def __repr__(self) -> str:
        return f"EntityFamiliar(name='{self.name}', type={self.familiar_type.name}, properties={len(self.properties)})"
    
    # Tag system methods - delegate to the internal tagged entity
    def add_tag(self, tag) -> bool:
        """Add a tag to this familiar."""
        if TAG_SYSTEM_AVAILABLE and self._tagged_entity:
            return self._tagged_entity.add_tag(tag)
        return False
    
    def mark(self, tag) -> bool:
        """Add a mark (tag) to this familiar."""
        return self.add_tag(tag)
    
    def remove_tag(self, tag_pattern: str) -> int:
        """Remove tags matching the pattern."""
        if TAG_SYSTEM_AVAILABLE and self._tagged_entity:
            return self._tagged_entity.remove_tag(tag_pattern)
        return 0
    
    def unmark(self, tag_pattern: str) -> int:
        """Remove marks (tags) matching the pattern."""
        return self.remove_tag(tag_pattern)
    
    def has_tag(self, pattern: str) -> bool:
        """Check if this familiar has a tag matching the pattern."""
        if TAG_SYSTEM_AVAILABLE and self._tagged_entity:
            return self._tagged_entity.has_tag(pattern)
        return False
    
    def bears_mark(self, pattern: str) -> bool:
        """Check if this familiar bears a mark (tag) matching the pattern."""
        return self.has_tag(pattern)
    
    def get_tags(self):
        """Get all tags for this familiar."""
        if TAG_SYSTEM_AVAILABLE and self._tagged_entity:
            return self._tagged_entity.tags
        return []
    
    def get_marks(self):
        """Get all marks (tags) for this familiar."""
        return self.get_tags()