#!/usr/bin/env python3
"""
Grimoire Effects System - Magical Aura and Effect Management

This package implements the effect tracking system for Grimoire, providing
aura types, effect composition, and compile-time effect checking for
magical function signatures.
"""

from .auras import (
    AuraType, EffectType, EffectIntensity,
    MagicalAura, Effect, AuraSet,
    compose_auras, check_aura_compatibility
)

from .checker import (
    EffectChecker, EffectViolationError,
    validate_function_effects, check_effect_composition
)

from .composer import (
    EffectComposer, CompositionRule, EffectInteraction,
    compose_effects, resolve_effect_conflicts
)

__all__ = [
    # Core effect types
    'AuraType', 'EffectType', 'EffectIntensity',
    'MagicalAura', 'Effect', 'AuraSet',
    
    # Aura operations
    'compose_auras', 'check_aura_compatibility',
    
    # Effect checking
    'EffectChecker', 'EffectViolationError',
    'validate_function_effects', 'check_effect_composition',
    
    # Effect composition
    'EffectComposer', 'CompositionRule', 'EffectInteraction',
    'compose_effects', 'resolve_effect_conflicts'
]