from enum import Enum, auto

class FamiliarType(Enum):
    """High-level semantic categories for familiars."""
    BASE = auto()        # Generic familiar
    ENTITY = auto()      # State management
    AI = auto()          # Decision making
    PERCEPTION = auto()  # Sensory processing
    MEMORY = auto()      # Data storage
    COMMUNICATION = auto() # Message handling

    def __str__(self) -> str:  # pragma: no cover
        return self.name.lower()

class FamiliarCapability(Enum):
    """Capabilities that familiars can have."""
    PROPERTY_MANAGEMENT = auto()
    GOAL_EVALUATION = auto() 
    SPATIAL_AWARENESS = auto()
    MESSAGE_ROUTING = auto()
    STATE_PERSISTENCE = auto()
    DECISION_MAKING = auto()
    SENSORY_PROCESSING = auto()

    def __str__(self) -> str:  # pragma: no cover
        return self.name.lower()