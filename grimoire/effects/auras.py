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
Grimoire Magical Aura System - Core Effect Types

This module defines the fundamental types and classes for magical effects
and auras in the Grimoire programming language.
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, Set, List, Optional, Union, Any
import copy


class AuraType(Enum):
    """Types of magical auras."""
    PROTECTIVE = auto()     # Shields and wards
    DESTRUCTIVE = auto()    # Damage and chaos
    CREATIVE = auto()       # Conjuration and creation
    TRANSFORMATIVE = auto() # Alteration and transmutation
    DIVINATORY = auto()     # Scrying and knowledge
    ENCHANTMENT = auto()    # Mind and charm effects
    NECROMANTIC = auto()    # Death and undeath
    ELEMENTAL = auto()      # Elemental forces
    TEMPORAL = auto()       # Time manipulation
    SPATIAL = auto()        # Space and teleportation


class EffectType(Enum):
    """Types of magical effects."""
    PERSISTENT = auto()     # Long-lasting effects
    INSTANTANEOUS = auto()  # Immediate effects
    CHANNELED = auto()      # Require concentration
    TRIGGERED = auto()      # Activate under conditions
    PASSIVE = auto()        # Always active
    RITUAL = auto()         # Require preparation
    COMBAT = auto()         # Combat-specific
    UTILITY = auto()        # Non-combat effects


class EffectIntensity(Enum):
    """Intensity levels of magical effects."""
    MINOR = auto()          # 1-3 intensity
    MODERATE = auto()       # 4-6 intensity  
    MAJOR = auto()          # 7-9 intensity
    EPIC = auto()           # 10+ intensity
    
    def to_value(self) -> int:
        """Convert intensity to numeric value."""
        return {
            EffectIntensity.MINOR: 2,
            EffectIntensity.MODERATE: 5,
            EffectIntensity.MAJOR: 8,
            EffectIntensity.EPIC: 12
        }[self]


@dataclass
class MagicalAura:
    """Represents a magical aura with specific properties."""
    aura_type: AuraType
    intensity: EffectIntensity
    duration: float = 0.0  # 0 = instantaneous, -1 = permanent
    range_modifier: float = 1.0
    stability: float = 1.0  # How stable the aura is (0-1)
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def is_compatible_with(self, other: 'MagicalAura') -> bool:
        """Check if this aura is compatible with another."""
        # Opposing aura types are incompatible
        incompatible_pairs = {
            (AuraType.PROTECTIVE, AuraType.DESTRUCTIVE),
            (AuraType.CREATIVE, AuraType.NECROMANTIC),
            (AuraType.TEMPORAL, AuraType.SPATIAL)  # Can cause paradoxes
        }
        
        pair = (self.aura_type, other.aura_type)
        reverse_pair = (other.aura_type, self.aura_type)
        
        return pair not in incompatible_pairs and reverse_pair not in incompatible_pairs
    
    def get_power_level(self) -> int:
        """Calculate the total power level of this aura."""
        base_power = self.intensity.to_value()
        stability_modifier = int(self.stability * 2)
        duration_modifier = min(int(self.duration / 10), 5) if self.duration > 0 else 0
        
        return base_power + stability_modifier + duration_modifier
    
    def can_stack_with(self, other: 'MagicalAura') -> bool:
        """Check if this aura can stack with another."""
        # Same aura types can stack if they're not too powerful
        if self.aura_type == other.aura_type:
            combined_power = self.get_power_level() + other.get_power_level()
            return combined_power <= 20  # Maximum stacking limit
        
        return self.is_compatible_with(other)


@dataclass
class Effect:
    """Represents a specific magical effect."""
    name: str
    effect_type: EffectType
    aura: MagicalAura
    description: str = ""
    prerequisites: List[str] = field(default_factory=list)
    conflicts_with: List[str] = field(default_factory=list)
    modifies: List[str] = field(default_factory=list)  # What this effect changes
    
    def is_active_type(self) -> bool:
        """Check if this effect requires active concentration."""
        return self.effect_type in [EffectType.CHANNELED, EffectType.RITUAL]
    
    def is_permanent_type(self) -> bool:
        """Check if this effect is permanent."""
        return self.effect_type in [EffectType.PASSIVE, EffectType.PERSISTENT]
    
    def conflicts_with_effect(self, other: 'Effect') -> bool:
        """Check if this effect conflicts with another."""
        # Direct conflicts
        if other.name in self.conflicts_with or self.name in other.conflicts_with:
            return True
        
        # Aura incompatibility
        if not self.aura.is_compatible_with(other.aura):
            return True
        
        # Modifying the same property
        if any(prop in other.modifies for prop in self.modifies):
            return True
        
        return False


@dataclass
class AuraSet:
    """Represents a collection of magical auras and effects."""
    auras: List[MagicalAura] = field(default_factory=list)
    effects: List[Effect] = field(default_factory=list)
    active_effects: Set[str] = field(default_factory=set)
    
    def add_aura(self, aura: MagicalAura) -> bool:
        """Add an aura to the set if compatible."""
        for existing_aura in self.auras:
            if not existing_aura.is_compatible_with(aura):
                return False
        
        self.auras.append(aura)
        return True
    
    def add_effect(self, effect: Effect) -> bool:
        """Add an effect to the set if compatible."""
        # Check conflicts with existing effects
        for existing_effect in self.effects:
            if existing_effect.conflicts_with_effect(effect):
                return False
        
        # Add the effect's aura
        if not self.add_aura(effect.aura):
            return False
        
        self.effects.append(effect)
        if effect.is_active_type():
            self.active_effects.add(effect.name)
        
        return True
    
    def remove_effect(self, effect_name: str) -> bool:
        """Remove an effect from the set."""
        effect_to_remove = None
        for effect in self.effects:
            if effect.name == effect_name:
                effect_to_remove = effect
                break
        
        if effect_to_remove:
            self.effects.remove(effect_to_remove)
            self.active_effects.discard(effect_name)
            # Note: We don't remove the aura as it might be shared
            return True
        
        return False
    
    def get_total_power(self) -> int:
        """Calculate total power of all auras in the set."""
        return sum(aura.get_power_level() for aura in self.auras)
    
    def get_aura_types(self) -> Set[AuraType]:
        """Get all aura types present in the set."""
        return {aura.aura_type for aura in self.auras}
    
    def has_aura_type(self, aura_type: AuraType) -> bool:
        """Check if the set contains a specific aura type."""
        return aura_type in self.get_aura_types()
    
    def get_effects_by_type(self, effect_type: EffectType) -> List[Effect]:
        """Get all effects of a specific type."""
        return [effect for effect in self.effects if effect.effect_type == effect_type]
    
    def is_stable(self) -> bool:
        """Check if the aura set is stable (no conflicting effects)."""
        for i, effect1 in enumerate(self.effects):
            for effect2 in self.effects[i+1:]:
                if effect1.conflicts_with_effect(effect2):
                    return False
        return True
    
    def get_stability_score(self) -> float:
        """Calculate the overall stability of the aura set."""
        if not self.auras:
            return 1.0
        
        total_stability = sum(aura.stability for aura in self.auras)
        base_stability = total_stability / len(self.auras)
        
        # Reduce stability for high power levels
        power_penalty = min(self.get_total_power() / 100, 0.5)
        
        return max(base_stability - power_penalty, 0.0)


def compose_auras(aura1: MagicalAura, aura2: MagicalAura) -> Optional[MagicalAura]:
    """Compose two auras into a single combined aura."""
    if not aura1.is_compatible_with(aura2):
        return None
    
    if not aura1.can_stack_with(aura2):
        return None
    
    # Create combined aura
    # If same type, enhance intensity; if different, take the stronger
    if aura1.aura_type == aura2.aura_type:
        # Same type - combine intensities
        combined_intensity = min(
            max(aura1.intensity.to_value(), aura2.intensity.to_value()) + 2,
            EffectIntensity.EPIC.to_value()
        )
        
        if combined_intensity <= EffectIntensity.MINOR.to_value():
            intensity = EffectIntensity.MINOR
        elif combined_intensity <= EffectIntensity.MODERATE.to_value():
            intensity = EffectIntensity.MODERATE
        elif combined_intensity <= EffectIntensity.MAJOR.to_value():
            intensity = EffectIntensity.MAJOR
        else:
            intensity = EffectIntensity.EPIC
        
        aura_type = aura1.aura_type
    else:
        # Different types - take the stronger one
        if aura1.get_power_level() >= aura2.get_power_level():
            intensity = aura1.intensity
            aura_type = aura1.aura_type
        else:
            intensity = aura2.intensity
            aura_type = aura2.aura_type
    
    # Combine other properties
    combined_duration = max(aura1.duration, aura2.duration)
    combined_range = (aura1.range_modifier + aura2.range_modifier) / 2
    combined_stability = min(aura1.stability, aura2.stability) * 0.9  # Slightly less stable
    
    # Merge properties
    combined_properties = {**aura1.properties, **aura2.properties}
    
    return MagicalAura(
        aura_type=aura_type,
        intensity=intensity,
        duration=combined_duration,
        range_modifier=combined_range,
        stability=combined_stability,
        properties=combined_properties
    )


def check_aura_compatibility(auras: List[MagicalAura]) -> bool:
    """Check if a list of auras are all compatible with each other."""
    for i, aura1 in enumerate(auras):
        for aura2 in auras[i+1:]:
            if not aura1.is_compatible_with(aura2):
                return False
    return True


# Predefined common auras
COMMON_AURAS = {
    "protection": MagicalAura(
        AuraType.PROTECTIVE, EffectIntensity.MODERATE,
        duration=600.0, stability=0.9
    ),
    "fireball": MagicalAura(
        AuraType.DESTRUCTIVE, EffectIntensity.MAJOR,
        duration=0.0, range_modifier=2.0
    ),
    "healing": MagicalAura(
        AuraType.CREATIVE, EffectIntensity.MODERATE,
        duration=0.0, stability=1.0
    ),
    "teleport": MagicalAura(
        AuraType.SPATIAL, EffectIntensity.MAJOR,
        duration=0.0, stability=0.7
    ),
    "scrying": MagicalAura(
        AuraType.DIVINATORY, EffectIntensity.MINOR,
        duration=300.0, range_modifier=10.0
    )
}


def get_common_aura(name: str) -> Optional[MagicalAura]:
    """Get a predefined common aura by name."""
    aura = COMMON_AURAS.get(name)
    return copy.deepcopy(aura) if aura else None