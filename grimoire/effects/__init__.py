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