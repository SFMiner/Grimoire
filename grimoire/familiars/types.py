from enum import Enum, auto

class FamiliarType(Enum):
    """High-level semantic categories for familiars."""
    ENTITY = auto()
    AI = auto()
    PERCEPTION = auto()
    MEMORY = auto()
    COMMUNICATION = auto()

    def __str__(self) -> str:  # pragma: no cover
        return self.name.lower()