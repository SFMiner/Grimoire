from enum import Enum, auto

class FamiliarType(Enum):
    """High-level categories for familiars.

    This enum is mainly intended for *semantic* grouping of familiars rather
    than being used as the technical *familiar_type* string (which is freeform
    and used by the interpreter).  Sub-classes may reference these categories
    to implement type-specific behaviour or capability restrictions.
    """

    ENTITY = auto()
    AI = auto()
    PERCEPTION = auto()
    MEMORY = auto()
    COMMUNICATION = auto()

    def __str__(self):  # pragma: no cover
        return self.name.lower()