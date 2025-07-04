#!/usr/bin/env python3
"""
Grimoire Familiar Type System

This module defines the core type system for familiars, including
familiar types, capabilities, and the foundation for the familiar hierarchy.
"""

from enum import Enum, auto
from typing import Set, Dict, Any, Optional
from dataclasses import dataclass


class FamiliarType(Enum):
    """Types of familiars with different specializations."""
    BASE = auto()           # Generic familiar
    ENTITY = auto()         # State management and property handling
    AI = auto()             # Decision making and goal evaluation
    PERCEPTION = auto()     # Sensory processing and world awareness
    MEMORY = auto()         # Data storage and retrieval
    COMMUNICATION = auto()  # Message handling and routing


class FamiliarCapability(Enum):
    """Capabilities that familiars can possess."""
    PROPERTY_MANAGEMENT = auto()    # Can manage entity properties
    GOAL_EVALUATION = auto()        # Can evaluate and pursue goals
    SPATIAL_AWARENESS = auto()      # Can understand spatial relationships
    MESSAGE_ROUTING = auto()        # Can route messages between familiars
    STATE_PERSISTENCE = auto()      # Can persist state across sessions
    DECISION_MAKING = auto()        # Can make autonomous decisions
    SENSORY_PROCESSING = auto()     # Can process sensory input
    MEMORY_STORAGE = auto()         # Can store and retrieve memories
    SOCKET_MANAGEMENT = auto()      # Can manage socket connections
    WORLD_MODELING = auto()         # Can maintain world state models


@dataclass
class FamiliarSpec:
    """Specification for a familiar type."""
    familiar_type: FamiliarType
    required_capabilities: Set[FamiliarCapability]
    optional_capabilities: Set[FamiliarCapability]
    default_sockets: Dict[str, str]  # socket_name -> direction
    description: str
    
    def has_capability(self, capability: FamiliarCapability) -> bool:
        """Check if this spec includes a capability."""
        return capability in self.required_capabilities or capability in self.optional_capabilities
    
    def is_required_capability(self, capability: FamiliarCapability) -> bool:
        """Check if a capability is required for this familiar type."""
        return capability in self.required_capabilities


# Predefined familiar specifications
FAMILIAR_SPECS: Dict[FamiliarType, FamiliarSpec] = {
    FamiliarType.BASE: FamiliarSpec(
        familiar_type=FamiliarType.BASE,
        required_capabilities={FamiliarCapability.SOCKET_MANAGEMENT},
        optional_capabilities=set(),
        default_sockets={
            "message_input": "input",
            "message_output": "output"
        },
        description="Basic familiar with minimal capabilities"
    ),
    
    FamiliarType.ENTITY: FamiliarSpec(
        familiar_type=FamiliarType.ENTITY,
        required_capabilities={
            FamiliarCapability.PROPERTY_MANAGEMENT,
            FamiliarCapability.SOCKET_MANAGEMENT,
            FamiliarCapability.STATE_PERSISTENCE
        },
        optional_capabilities={
            FamiliarCapability.SPATIAL_AWARENESS
        },
        default_sockets={
            "property_input": "input",
            "property_output": "output",
            "state_query": "input",
            "state_response": "output",
            "message_input": "input",
            "message_output": "output"
        },
        description="Entity management familiar for handling game objects and their properties"
    ),
    
    FamiliarType.AI: FamiliarSpec(
        familiar_type=FamiliarType.AI,
        required_capabilities={
            FamiliarCapability.GOAL_EVALUATION,
            FamiliarCapability.DECISION_MAKING,
            FamiliarCapability.SOCKET_MANAGEMENT,
            FamiliarCapability.WORLD_MODELING
        },
        optional_capabilities={
            FamiliarCapability.SPATIAL_AWARENESS,
            FamiliarCapability.MEMORY_STORAGE
        },
        default_sockets={
            "goal_input": "input",
            "decision_output": "output",
            "world_state_input": "input",
            "action_output": "output",
            "message_input": "input",
            "message_output": "output"
        },
        description="AI familiar for autonomous decision making and goal pursuit"
    ),
    
    FamiliarType.PERCEPTION: FamiliarSpec(
        familiar_type=FamiliarType.PERCEPTION,
        required_capabilities={
            FamiliarCapability.SENSORY_PROCESSING,
            FamiliarCapability.SPATIAL_AWARENESS,
            FamiliarCapability.SOCKET_MANAGEMENT
        },
        optional_capabilities={
            FamiliarCapability.MEMORY_STORAGE,
            FamiliarCapability.WORLD_MODELING
        },
        default_sockets={
            "sensor_input": "input",
            "perception_output": "output",
            "spatial_query": "input",
            "spatial_response": "output",
            "message_input": "input",
            "message_output": "output"
        },
        description="Perception familiar for sensory processing and spatial awareness"
    ),
    
    FamiliarType.MEMORY: FamiliarSpec(
        familiar_type=FamiliarType.MEMORY,
        required_capabilities={
            FamiliarCapability.MEMORY_STORAGE,
            FamiliarCapability.STATE_PERSISTENCE,
            FamiliarCapability.SOCKET_MANAGEMENT
        },
        optional_capabilities={
            FamiliarCapability.WORLD_MODELING
        },
        default_sockets={
            "memory_store": "input",
            "memory_retrieve": "input",
            "memory_response": "output",
            "persistence_control": "input",
            "message_input": "input",
            "message_output": "output"
        },
        description="Memory familiar for data storage and retrieval"
    ),
    
    FamiliarType.COMMUNICATION: FamiliarSpec(
        familiar_type=FamiliarType.COMMUNICATION,
        required_capabilities={
            FamiliarCapability.MESSAGE_ROUTING,
            FamiliarCapability.SOCKET_MANAGEMENT
        },
        optional_capabilities={
            FamiliarCapability.STATE_PERSISTENCE
        },
        default_sockets={
            "message_input": "input",
            "message_output": "output",
            "routing_control": "input",
            "broadcast_output": "output"
        },
        description="Communication familiar for message routing and inter-familiar communication"
    )
}


def get_familiar_spec(familiar_type: FamiliarType) -> FamiliarSpec:
    """Get the specification for a familiar type."""
    return FAMILIAR_SPECS.get(familiar_type, FAMILIAR_SPECS[FamiliarType.BASE])


def validate_familiar_capabilities(familiar_type: FamiliarType, 
                                 actual_capabilities: Set[FamiliarCapability]) -> bool:
    """Validate that a familiar has all required capabilities for its type."""
    spec = get_familiar_spec(familiar_type)
    return spec.required_capabilities.issubset(actual_capabilities)


def get_missing_capabilities(familiar_type: FamiliarType,
                           actual_capabilities: Set[FamiliarCapability]) -> Set[FamiliarCapability]:
    """Get capabilities missing from a familiar for its type."""
    spec = get_familiar_spec(familiar_type)
    return spec.required_capabilities - actual_capabilities


def get_recommended_sockets(familiar_type: FamiliarType) -> Dict[str, str]:
    """Get recommended socket configuration for a familiar type."""
    spec = get_familiar_spec(familiar_type)
    return spec.default_sockets.copy()


class FamiliarTypeError(Exception):
    """Raised when there's an error with familiar type operations."""
    pass


class FamiliarCapabilityError(Exception):
    """Raised when a familiar lacks required capabilities."""
    pass