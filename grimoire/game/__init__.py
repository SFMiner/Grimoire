"""Game development helpers: entity property management, modifiers, effects, interactions."""

from .properties import PropertySpec, EntityProperties
from .modifiers import Modifier
from .effects import Effect
from .interactions import apply_damage

__all__ = [
    'PropertySpec', 'EntityProperties', 'Modifier', 'Effect', 'apply_damage'
]