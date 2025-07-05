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
Grimoire Effect Composer - Effect Interaction and Composition

This module handles complex interactions between magical effects,
automatic composition rules, and conflict resolution.
"""

from typing import List, Dict, Set, Optional, Tuple, Callable, Any, Union
from dataclasses import dataclass, field
from enum import Enum, auto
import copy

from .auras import (
    MagicalAura, Effect, AuraSet, AuraType, EffectType, 
    EffectIntensity, compose_auras
)


class InteractionType(Enum):
    """Types of effect interactions."""
    SYNERGY = auto()        # Effects enhance each other
    AMPLIFICATION = auto()  # One effect amplifies another
    CANCELLATION = auto()   # Effects cancel each other out
    TRANSFORMATION = auto() # Effects transform into something new
    INTERFERENCE = auto()   # Effects interfere destructively
    RESONANCE = auto()      # Effects create harmonic resonance
    DISPERSION = auto()     # One effect disperses another
    ABSORPTION = auto()     # One effect absorbs another


class CompositionStrategy(Enum):
    """Strategies for composing effects."""
    SEQUENTIAL = auto()     # Apply effects in sequence
    PARALLEL = auto()       # Apply effects simultaneously
    LAYERED = auto()        # Apply effects in layers
    INTERLEAVED = auto()    # Interleave effect applications
    CONDITIONAL = auto()    # Apply based on conditions
    ADAPTIVE = auto()       # Adapt based on current state


@dataclass
class EffectInteraction:
    """Represents an interaction between two effects."""
    effect1: str
    effect2: str
    interaction_type: InteractionType
    result_modifier: float = 1.0  # Multiplier for the interaction result
    creates_new_effect: Optional[str] = None
    condition: Optional[Callable[[Effect, Effect], bool]] = None
    description: str = ""
    
    def applies_to(self, eff1: Effect, eff2: Effect) -> bool:
        """Check if this interaction applies to the given effects."""
        if self.condition:
            return self.condition(eff1, eff2)
        
        return ((eff1.name == self.effect1 and eff2.name == self.effect2) or
                (eff1.name == self.effect2 and eff2.name == self.effect1))


@dataclass
class CompositionRule:
    """Represents a rule for composing effects."""
    name: str
    condition: Callable[[List[Effect]], bool]
    strategy: CompositionStrategy
    transformation: Callable[[List[Effect]], List[Effect]]
    priority: int = 0
    description: str = ""
    
    def applies_to(self, effects: List[Effect]) -> bool:
        """Check if this rule applies to the given effects."""
        return self.condition(effects)
    
    def apply(self, effects: List[Effect]) -> List[Effect]:
        """Apply the composition rule to the effects."""
        return self.transformation(effects)


@dataclass
class CompositionResult:
    """Result of effect composition."""
    final_effects: List[Effect]
    interactions_applied: List[EffectInteraction]
    rules_applied: List[CompositionRule]
    warnings: List[str] = field(default_factory=list)
    stability_score: float = 1.0
    total_power: int = 0
    
    def is_stable(self) -> bool:
        """Check if the composition result is stable."""
        return self.stability_score >= 0.5


class EffectComposer:
    """Advanced composer for magical effects with interaction rules."""
    
    def __init__(self):
        self.interactions: List[EffectInteraction] = []
        self.composition_rules: List[CompositionRule] = []
        self.effect_library: Dict[str, Effect] = {}
        
        # Set up default interactions and rules
        self._setup_default_interactions()
        self._setup_default_composition_rules()
    
    def _setup_default_interactions(self):
        """Set up default effect interactions."""
        # Fire and Ice cancel each other
        self.add_interaction(EffectInteraction(
            "fire", "ice", InteractionType.CANCELLATION,
            result_modifier=0.0,
            description="Fire and ice effects cancel each other out"
        ))
        
        # Protection effects synergize
        self.add_interaction(EffectInteraction(
            "shield", "ward", InteractionType.SYNERGY,
            result_modifier=1.5,
            description="Shield and ward effects enhance each other"
        ))
        
        # Lightning amplifies metal effects
        self.add_interaction(EffectInteraction(
            "lightning", "metal", InteractionType.AMPLIFICATION,
            result_modifier=2.0,
            description="Lightning amplifies metal-based effects"
        ))
        
        # Healing and poison interfere
        self.add_interaction(EffectInteraction(
            "healing", "poison", InteractionType.INTERFERENCE,
            result_modifier=0.3,
            description="Healing and poison effects interfere with each other"
        ))
        
        # Time and space create resonance
        self.add_interaction(EffectInteraction(
            "time_warp", "teleport", InteractionType.RESONANCE,
            result_modifier=1.8,
            creates_new_effect="dimensional_rift",
            description="Time and space effects create dimensional resonance"
        ))
    
    def _setup_default_composition_rules(self):
        """Set up default composition rules."""
        # Elemental combination rule
        self.add_composition_rule(CompositionRule(
            name="elemental_fusion",
            condition=lambda effects: self._has_multiple_elements(effects),
            strategy=CompositionStrategy.LAYERED,
            transformation=self._fuse_elemental_effects,
            priority=10,
            description="Combine multiple elemental effects into fusion effects"
        ))
        
        # Protection stacking rule
        self.add_composition_rule(CompositionRule(
            name="protection_stacking",
            condition=lambda effects: self._has_multiple_protective_effects(effects),
            strategy=CompositionStrategy.PARALLEL,
            transformation=self._stack_protective_effects,
            priority=5,
            description="Stack multiple protective effects efficiently"
        ))
        
        # Power overflow prevention
        self.add_composition_rule(CompositionRule(
            name="power_regulation",
            condition=lambda effects: self._exceeds_power_threshold(effects),
            strategy=CompositionStrategy.SEQUENTIAL,
            transformation=self._regulate_power_levels,
            priority=15,
            description="Prevent magical power overflow by regulating effect intensity"
        ))
    
    def add_interaction(self, interaction: EffectInteraction) -> None:
        """Add an effect interaction rule."""
        self.interactions.append(interaction)
    
    def add_composition_rule(self, rule: CompositionRule) -> None:
        """Add a composition rule."""
        self.composition_rules.append(rule)
        # Keep rules sorted by priority (higher priority first)
        self.composition_rules.sort(key=lambda r: r.priority, reverse=True)
    
    def register_effect(self, effect: Effect) -> None:
        """Register an effect in the library."""
        self.effect_library[effect.name] = effect
    
    def compose_effects(self, effects: List[Effect]) -> CompositionResult:
        """Compose a list of effects with interaction resolution."""
        result = CompositionResult(
            final_effects=copy.deepcopy(effects),
            interactions_applied=[],
            rules_applied=[]
        )
        
        # Apply composition rules first
        for rule in self.composition_rules:
            if rule.applies_to(result.final_effects):
                try:
                    new_effects = rule.apply(result.final_effects)
                    result.final_effects = new_effects
                    result.rules_applied.append(rule)
                except Exception as e:
                    result.warnings.append(f"Rule '{rule.name}' failed: {e}")
        
        # Apply interactions
        result.final_effects = self._apply_interactions(result.final_effects, result)
        
        # Calculate final metrics
        result.stability_score = self._calculate_stability(result.final_effects)
        result.total_power = sum(eff.aura.get_power_level() for eff in result.final_effects)
        
        return result
    
    def _apply_interactions(self, effects: List[Effect], result: CompositionResult) -> List[Effect]:
        """Apply effect interactions to the list of effects."""
        final_effects = copy.deepcopy(effects)
        effects_to_remove = set()
        effects_to_add = []
        
        # Check all pairs of effects for interactions
        for i, effect1 in enumerate(final_effects):
            if i in effects_to_remove:
                continue
                
            for j, effect2 in enumerate(final_effects[i+1:], i+1):
                if j in effects_to_remove:
                    continue
                
                # Find applicable interactions
                for interaction in self.interactions:
                    if interaction.applies_to(effect1, effect2):
                        result.interactions_applied.append(interaction)
                        
                        if interaction.interaction_type == InteractionType.CANCELLATION:
                            # Both effects are cancelled
                            effects_to_remove.add(i)
                            effects_to_remove.add(j)
                            
                        elif interaction.interaction_type == InteractionType.SYNERGY:
                            # Enhance both effects
                            final_effects[i] = self._enhance_effect(effect1, interaction.result_modifier)
                            final_effects[j] = self._enhance_effect(effect2, interaction.result_modifier)
                            
                        elif interaction.interaction_type == InteractionType.AMPLIFICATION:
                            # One effect amplifies the other
                            if effect1.name == interaction.effect1:
                                final_effects[j] = self._enhance_effect(effect2, interaction.result_modifier)
                            else:
                                final_effects[i] = self._enhance_effect(effect1, interaction.result_modifier)
                                
                        elif interaction.interaction_type == InteractionType.TRANSFORMATION:
                            # Effects transform into something new
                            if interaction.creates_new_effect:
                                new_effect = self._create_transformed_effect(
                                    effect1, effect2, interaction.creates_new_effect
                                )
                                effects_to_add.append(new_effect)
                            effects_to_remove.add(i)
                            effects_to_remove.add(j)
                            
                        elif interaction.interaction_type == InteractionType.INTERFERENCE:
                            # Effects interfere, reducing power
                            final_effects[i] = self._weaken_effect(effect1, interaction.result_modifier)
                            final_effects[j] = self._weaken_effect(effect2, interaction.result_modifier)
                            
                        elif interaction.interaction_type == InteractionType.RESONANCE:
                            # Create resonance effect
                            if interaction.creates_new_effect:
                                resonance_effect = self._create_resonance_effect(
                                    effect1, effect2, interaction.creates_new_effect
                                )
                                effects_to_add.append(resonance_effect)
                        
                        # Only apply the first matching interaction per pair
                        break
        
        # Remove cancelled/transformed effects
        final_effects = [eff for i, eff in enumerate(final_effects) if i not in effects_to_remove]
        
        # Add new effects from transformations
        final_effects.extend(effects_to_add)
        
        return final_effects
    
    def _enhance_effect(self, effect: Effect, modifier: float) -> Effect:
        """Enhance an effect's power."""
        enhanced = copy.deepcopy(effect)
        # Increase intensity if possible
        current_intensity = enhanced.aura.intensity.to_value()
        new_intensity_value = min(int(current_intensity * modifier), EffectIntensity.EPIC.to_value())
        
        if new_intensity_value <= EffectIntensity.MINOR.to_value():
            enhanced.aura.intensity = EffectIntensity.MINOR
        elif new_intensity_value <= EffectIntensity.MODERATE.to_value():
            enhanced.aura.intensity = EffectIntensity.MODERATE
        elif new_intensity_value <= EffectIntensity.MAJOR.to_value():
            enhanced.aura.intensity = EffectIntensity.MAJOR
        else:
            enhanced.aura.intensity = EffectIntensity.EPIC
        
        # Also enhance stability and range
        enhanced.aura.stability = min(enhanced.aura.stability * 1.1, 1.0)
        enhanced.aura.range_modifier *= modifier
        
        return enhanced
    
    def _weaken_effect(self, effect: Effect, modifier: float) -> Effect:
        """Weaken an effect's power."""
        weakened = copy.deepcopy(effect)
        current_intensity = weakened.aura.intensity.to_value()
        new_intensity_value = max(int(current_intensity * modifier), 1)
        
        if new_intensity_value <= EffectIntensity.MINOR.to_value():
            weakened.aura.intensity = EffectIntensity.MINOR
        elif new_intensity_value <= EffectIntensity.MODERATE.to_value():
            weakened.aura.intensity = EffectIntensity.MODERATE
        elif new_intensity_value <= EffectIntensity.MAJOR.to_value():
            weakened.aura.intensity = EffectIntensity.MAJOR
        else:
            weakened.aura.intensity = EffectIntensity.EPIC
        
        weakened.aura.stability *= modifier
        weakened.aura.range_modifier *= modifier
        
        return weakened
    
    def _create_transformed_effect(self, effect1: Effect, effect2: Effect, new_name: str) -> Effect:
        """Create a new effect from transformation of two effects."""
        # Combine the auras
        combined_aura = compose_auras(effect1.aura, effect2.aura)
        if not combined_aura:
            # Fallback: use the stronger aura
            combined_aura = effect1.aura if effect1.aura.get_power_level() > effect2.aura.get_power_level() else effect2.aura
        
        return Effect(
            name=new_name,
            effect_type=EffectType.PERSISTENT,  # Transformed effects tend to be persistent
            aura=combined_aura,
            description=f"Transformed from {effect1.name} and {effect2.name}",
            prerequisites=list(set(effect1.prerequisites + effect2.prerequisites)),
            modifies=list(set(effect1.modifies + effect2.modifies))
        )
    
    def _create_resonance_effect(self, effect1: Effect, effect2: Effect, resonance_name: str) -> Effect:
        """Create a resonance effect from two interacting effects."""
        # Resonance effects are typically more powerful but less stable
        base_aura = effect1.aura if effect1.aura.get_power_level() > effect2.aura.get_power_level() else effect2.aura
        resonance_aura = copy.deepcopy(base_aura)
        
        # Enhance power but reduce stability
        if resonance_aura.intensity != EffectIntensity.EPIC:
            intensity_values = [EffectIntensity.MINOR, EffectIntensity.MODERATE, EffectIntensity.MAJOR, EffectIntensity.EPIC]
            current_index = intensity_values.index(resonance_aura.intensity)
            resonance_aura.intensity = intensity_values[min(current_index + 1, len(intensity_values) - 1)]
        
        resonance_aura.stability *= 0.7  # Less stable
        resonance_aura.range_modifier *= 1.5  # Larger range
        
        return Effect(
            name=resonance_name,
            effect_type=EffectType.CHANNELED,  # Resonance requires concentration
            aura=resonance_aura,
            description=f"Resonance effect from {effect1.name} and {effect2.name}",
            prerequisites=[effect1.name, effect2.name]
        )
    
    def _calculate_stability(self, effects: List[Effect]) -> float:
        """Calculate the overall stability of the effect composition."""
        if not effects:
            return 1.0
        
        aura_set = AuraSet()
        for effect in effects:
            aura_set.add_effect(effect)
        
        return aura_set.get_stability_score()
    
    # Composition rule helper methods
    def _has_multiple_elements(self, effects: List[Effect]) -> bool:
        """Check if there are multiple elemental effects."""
        elemental_types = {AuraType.ELEMENTAL}
        elemental_count = sum(1 for eff in effects if eff.aura.aura_type in elemental_types)
        return elemental_count >= 2
    
    def _has_multiple_protective_effects(self, effects: List[Effect]) -> bool:
        """Check if there are multiple protective effects."""
        protective_count = sum(1 for eff in effects if eff.aura.aura_type == AuraType.PROTECTIVE)
        return protective_count >= 2
    
    def _exceeds_power_threshold(self, effects: List[Effect]) -> bool:
        """Check if total power exceeds safe threshold."""
        total_power = sum(eff.aura.get_power_level() for eff in effects)
        return total_power > 50  # Threshold for power regulation
    
    def _fuse_elemental_effects(self, effects: List[Effect]) -> List[Effect]:
        """Fuse multiple elemental effects into combination effects."""
        elemental_effects = [eff for eff in effects if eff.aura.aura_type == AuraType.ELEMENTAL]
        other_effects = [eff for eff in effects if eff.aura.aura_type != AuraType.ELEMENTAL]
        
        if len(elemental_effects) >= 2:
            # Create a fused elemental effect
            base_effect = elemental_effects[0]
            fused_aura = copy.deepcopy(base_effect.aura)
            fused_aura.intensity = EffectIntensity.MAJOR  # Fusion increases power
            
            fused_effect = Effect(
                name="elemental_fusion",
                effect_type=EffectType.PERSISTENT,
                aura=fused_aura,
                description=f"Fusion of {', '.join(eff.name for eff in elemental_effects)}"
            )
            
            return other_effects + [fused_effect]
        
        return effects
    
    def _stack_protective_effects(self, effects: List[Effect]) -> List[Effect]:
        """Stack multiple protective effects efficiently."""
        protective_effects = [eff for eff in effects if eff.aura.aura_type == AuraType.PROTECTIVE]
        other_effects = [eff for eff in effects if eff.aura.aura_type != AuraType.PROTECTIVE]
        
        if len(protective_effects) >= 2:
            # Combine into a single stronger protective effect
            total_power = sum(eff.aura.get_power_level() for eff in protective_effects)
            base_effect = protective_effects[0]
            stacked_aura = copy.deepcopy(base_effect.aura)
            
            # Determine new intensity based on total power
            if total_power >= 20:
                stacked_aura.intensity = EffectIntensity.EPIC
            elif total_power >= 15:
                stacked_aura.intensity = EffectIntensity.MAJOR
            elif total_power >= 10:
                stacked_aura.intensity = EffectIntensity.MODERATE
            
            stacked_effect = Effect(
                name="layered_protection",
                effect_type=EffectType.PERSISTENT,
                aura=stacked_aura,
                description="Stacked protective effects"
            )
            
            return other_effects + [stacked_effect]
        
        return effects
    
    def _regulate_power_levels(self, effects: List[Effect]) -> List[Effect]:
        """Regulate power levels to prevent overflow."""
        total_power = sum(eff.aura.get_power_level() for eff in effects)
        if total_power <= 50:
            return effects
        
        # Reduce intensity of highest-power effects
        regulated_effects = []
        power_budget = 50
        
        # Sort effects by power level (lowest first)
        sorted_effects = sorted(effects, key=lambda eff: eff.aura.get_power_level())
        
        for effect in sorted_effects:
            effect_power = effect.aura.get_power_level()
            if effect_power <= power_budget:
                regulated_effects.append(effect)
                power_budget -= effect_power
            else:
                # Reduce this effect's intensity
                reduced_effect = copy.deepcopy(effect)
                if reduced_effect.aura.intensity != EffectIntensity.MINOR:
                    intensity_values = [EffectIntensity.MINOR, EffectIntensity.MODERATE, EffectIntensity.MAJOR, EffectIntensity.EPIC]
                    current_index = intensity_values.index(reduced_effect.aura.intensity)
                    reduced_effect.aura.intensity = intensity_values[max(current_index - 1, 0)]
                    regulated_effects.append(reduced_effect)
                    power_budget -= reduced_effect.aura.get_power_level()
        
        return regulated_effects


def compose_effects(effects: List[Effect]) -> CompositionResult:
    """Standalone function to compose effects with default rules."""
    composer = EffectComposer()
    return composer.compose_effects(effects)


def resolve_effect_conflicts(effects: List[Effect]) -> List[Effect]:
    """Resolve conflicts between effects using composition rules."""
    composer = EffectComposer()
    result = composer.compose_effects(effects)
    return result.final_effects