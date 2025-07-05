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

"""World state interface for AI agents.

This module provides a standardized interface for AI goals to query world state,
enabling consistent decision-making across different AI systems.
"""

from typing import Any, Dict, List, Optional, Tuple
import time
import copy

__all__ = ["WorldState", "WorldStateManager", "EntityState", "SpatialQuery"]


class EntityState:
    """Represents the state of a single entity."""
    
    def __init__(self, entity_id: str, entity_type: str = "generic"):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.properties = {}
        self.position = (0, 0)
        self.last_updated = time.time()
        
    def get_property(self, property_name: str, default: Any = None) -> Any:
        """Get a property value."""
        return self.properties.get(property_name, default)
    
    def set_property(self, property_name: str, value: Any):
        """Set a property value."""
        self.properties[property_name] = value
        self.last_updated = time.time()
    
    def update_properties(self, properties: Dict[str, Any]):
        """Update multiple properties at once."""
        self.properties.update(properties)
        self.last_updated = time.time()
    
    def get_distance_to(self, other_position: Tuple[float, float]) -> float:
        """Calculate distance to another position."""
        x1, y1 = self.position
        x2, y2 = other_position
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


class SpatialQuery:
    """Helper class for spatial queries."""
    
    @staticmethod
    def get_entities_in_radius(entities: Dict[str, EntityState], 
                              center: Tuple[float, float], 
                              radius: float) -> List[EntityState]:
        """Get all entities within a radius of a point."""
        result = []
        for entity in entities.values():
            if entity.get_distance_to(center) <= radius:
                result.append(entity)
        return result
    
    @staticmethod
    def get_nearest_entity(entities: Dict[str, EntityState], 
                          position: Tuple[float, float],
                          entity_type: Optional[str] = None) -> Optional[EntityState]:
        """Get the nearest entity to a position."""
        nearest = None
        min_distance = float('inf')
        
        for entity in entities.values():
            if entity_type and entity.entity_type != entity_type:
                continue
            
            distance = entity.get_distance_to(position)
            if distance < min_distance:
                min_distance = distance
                nearest = entity
        
        return nearest


class WorldState:
    """Standardized interface for AI goals to query world state."""
    
    def __init__(self):
        self.entities: Dict[str, EntityState] = {}
        self.global_properties: Dict[str, Any] = {}
        self.spatial_data: Dict[str, Any] = {}
        self.temporal_data: Dict[str, Any] = {}
        self.last_updated = time.time()
        
    def get_entity(self, entity_id: str) -> Optional[EntityState]:
        """Get a specific entity by ID."""
        return self.entities.get(entity_id)
    
    def get_entity_property(self, entity_id: str, property_name: str, default: Any = None) -> Any:
        """Get property of specific entity."""
        entity = self.entities.get(entity_id)
        if entity:
            return entity.get_property(property_name, default)
        return default
    
    def set_entity_property(self, entity_id: str, property_name: str, value: Any):
        """Set property of specific entity."""
        entity = self.entities.get(entity_id)
        if entity:
            entity.set_property(property_name, value)
        else:
            # Create new entity if it doesn't exist
            entity = EntityState(entity_id)
            entity.set_property(property_name, value)
            self.entities[entity_id] = entity
        
        self.last_updated = time.time()
    
    def get_entities_by_type(self, entity_type: str) -> List[EntityState]:
        """Get all entities of specific type."""
        return [entity for entity in self.entities.values() 
                if entity.entity_type == entity_type]
    
    def get_entities_in_area(self, center: Tuple[float, float], radius: float) -> List[EntityState]:
        """Get entities within spatial area."""
        return SpatialQuery.get_entities_in_radius(self.entities, center, radius)
    
    def get_nearest_entity(self, position: Tuple[float, float], 
                          entity_type: Optional[str] = None) -> Optional[EntityState]:
        """Get nearest entity to a position."""
        return SpatialQuery.get_nearest_entity(self.entities, position, entity_type)
    
    def get_global_property(self, property_name: str, default: Any = None) -> Any:
        """Get world-wide property (resources, time, etc.)."""
        return self.global_properties.get(property_name, default)
    
    def set_global_property(self, property_name: str, value: Any):
        """Set world-wide property."""
        self.global_properties[property_name] = value
        self.last_updated = time.time()
    
    def update_from_familiar(self, familiar):
        """Update world state from familiar's perspective."""
        if not hasattr(familiar, 'name'):
            return
        
        # Create or update entity state
        entity_id = familiar.name
        if entity_id not in self.entities:
            familiar_type = getattr(familiar, 'familiar_type', 'generic')
            self.entities[entity_id] = EntityState(entity_id, str(familiar_type))
        
        entity = self.entities[entity_id]
        
        # Update position if available
        if hasattr(familiar, 'position'):
            entity.position = familiar.position
        
        # Update properties if available
        if hasattr(familiar, 'properties'):
            if isinstance(familiar.properties, dict):
                entity.update_properties(familiar.properties)
        
        # Update from properties container if available
        if hasattr(familiar, 'properties_container'):
            try:
                # Try to get properties from container
                container_props = {}
                if hasattr(familiar.properties_container, 'properties'):
                    container_props = familiar.properties_container.properties
                entity.update_properties(container_props)
            except Exception:
                pass
        
        self.last_updated = time.time()
    
    def get_entity_count(self, entity_type: Optional[str] = None) -> int:
        """Get count of entities, optionally filtered by type."""
        if entity_type:
            return len(self.get_entities_by_type(entity_type))
        return len(self.entities)
    
    def get_world_summary(self) -> Dict[str, Any]:
        """Get a summary of the world state."""
        entity_types = {}
        for entity in self.entities.values():
            entity_types[entity.entity_type] = entity_types.get(entity.entity_type, 0) + 1
        
        return {
            'total_entities': len(self.entities),
            'entity_types': entity_types,
            'global_properties': list(self.global_properties.keys()),
            'last_updated': self.last_updated
        }


class WorldStateManager:
    """Manages world state updates and provides filtered views for AI agents."""
    
    def __init__(self):
        self.world_state = WorldState()
        self.familiar_registry: Dict[str, Any] = {}
        self.update_frequency = 1.0  # seconds
        self.last_update = 0.0
        
    def register_familiar(self, familiar):
        """Register a familiar for world state updates."""
        if hasattr(familiar, 'name'):
            self.familiar_registry[familiar.name] = familiar
            self.world_state.update_from_familiar(familiar)
    
    def unregister_familiar(self, familiar_name: str):
        """Unregister a familiar from world state updates."""
        if familiar_name in self.familiar_registry:
            del self.familiar_registry[familiar_name]
            # Remove entity from world state
            if familiar_name in self.world_state.entities:
                del self.world_state.entities[familiar_name]
    
    def update_world_state(self):
        """Update world state from all registered familiars."""
        current_time = time.time()
        if current_time - self.last_update < self.update_frequency:
            return
        
        for familiar in self.familiar_registry.values():
            self.world_state.update_from_familiar(familiar)
        
        self.last_update = current_time
    
    def get_world_state_for_ai(self, ai_familiar) -> WorldState:
        """Get world state filtered for specific AI's perspective."""
        # For now, return the full world state
        # In future, could implement visibility, knowledge limitations, etc.
        self.update_world_state()
        return self.world_state
    
    def get_world_state_copy(self) -> WorldState:
        """Get a copy of the world state for safe manipulation."""
        return copy.deepcopy(self.world_state)
    
    def set_update_frequency(self, frequency: float):
        """Set how often world state is updated (in seconds)."""
        self.update_frequency = max(0.1, frequency)  # Minimum 0.1 seconds
    
    def get_entity_interactions(self, entity_id: str, radius: float = 10.0) -> List[EntityState]:
        """Get entities that an entity can interact with."""
        entity = self.world_state.get_entity(entity_id)
        if not entity:
            return []
        
        return self.world_state.get_entities_in_area(entity.position, radius)
    
    def simulate_action_outcome(self, action, entity_id: str) -> Dict[str, Any]:
        """Simulate the outcome of an action for prediction."""
        # Create a copy of world state to simulate on
        simulated_state = self.get_world_state_copy()
        
        # Apply action effects (simplified simulation)
        if hasattr(action, 'effects'):
            for effect_key, effect_value in action.effects.items():
                if effect_key.startswith('entity.'):
                    property_name = effect_key[7:]  # Remove 'entity.'
                    current_value = simulated_state.get_entity_property(entity_id, property_name, 0)
                    
                    # Apply effect (simplified - could be more complex)
                    if isinstance(effect_value, str) and effect_value.startswith('+'):
                        new_value = current_value + float(effect_value[1:])
                    elif isinstance(effect_value, str) and effect_value.startswith('-'):
                        new_value = current_value - float(effect_value[1:])
                    else:
                        new_value = effect_value
                    
                    simulated_state.set_entity_property(entity_id, property_name, new_value)
        
        return {
            'predicted_world_state': simulated_state,
            'changes': getattr(action, 'effects', {})
        }