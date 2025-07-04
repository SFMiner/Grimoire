#!/usr/bin/env python3
"""
Grimoire Effect Checker - Compile-time Effect Validation

This module provides compile-time checking for magical effects and aura
compatibility in function signatures and magical operations.
"""

from typing import List, Dict, Set, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum, auto

from .auras import (
    MagicalAura, Effect, AuraSet, AuraType, EffectType, 
    EffectIntensity, check_aura_compatibility
)


class ViolationType(Enum):
    """Types of effect violations."""
    INCOMPATIBLE_AURAS = auto()     # Auras that cannot coexist
    CONFLICTING_EFFECTS = auto()    # Effects that conflict
    MISSING_PREREQUISITE = auto()   # Required effect missing
    POWER_OVERLOAD = auto()         # Too much magical power
    INSTABILITY = auto()            # Unstable magical configuration
    TYPE_MISMATCH = auto()          # Wrong effect type for operation
    PERMISSION_DENIED = auto()      # Effect not allowed in context


@dataclass
class EffectViolation:
    """Represents a violation of effect rules."""
    violation_type: ViolationType
    message: str
    location: str = ""
    severity: str = "error"  # "error", "warning", "info"
    suggested_fix: Optional[str] = None


class EffectViolationError(Exception):
    """Raised when effect checking finds violations."""
    
    def __init__(self, violations: List[EffectViolation]):
        self.violations = violations
        super().__init__(self._format_violations())
    
    def _format_violations(self) -> str:
        lines = ["Effect violations found:"]
        for violation in self.violations:
            location = f" at {violation.location}" if violation.location else ""
            lines.append(f"  {violation.severity.upper()}: {violation.message}{location}")
            if violation.suggested_fix:
                lines.append(f"    Suggestion: {violation.suggested_fix}")
        return "\n".join(lines)


@dataclass
class FunctionSignature:
    """Represents a function signature with effect information."""
    name: str
    parameters: List[str]
    return_type: Optional[str]
    required_effects: List[Effect] = field(default_factory=list)
    produces_effects: List[Effect] = field(default_factory=list)
    consumes_effects: List[str] = field(default_factory=list)  # Effect names
    restrictions: List[str] = field(default_factory=list)
    context_requirements: Dict[str, Any] = field(default_factory=dict)
    
    def get_all_effects(self) -> List[Effect]:
        """Get all effects associated with this function."""
        return self.required_effects + self.produces_effects


@dataclass
class EffectContext:
    """Represents the current magical context for effect checking."""
    active_auras: AuraSet = field(default_factory=AuraSet)
    available_effects: Set[str] = field(default_factory=set)
    forbidden_effects: Set[str] = field(default_factory=set)
    power_limit: int = 100
    stability_requirement: float = 0.5
    plane_restrictions: Dict[str, List[str]] = field(default_factory=dict)
    
    def can_use_effect(self, effect: Effect) -> bool:
        """Check if an effect can be used in this context."""
        if effect.name in self.forbidden_effects:
            return False
        
        # Check power limits
        current_power = self.active_auras.get_total_power()
        if current_power + effect.aura.get_power_level() > self.power_limit:
            return False
        
        # Check stability
        test_aura_set = AuraSet()
        test_aura_set.auras = self.active_auras.auras.copy()
        test_aura_set.effects = self.active_auras.effects.copy()
        
        if not test_aura_set.add_effect(effect):
            return False
        
        if test_aura_set.get_stability_score() < self.stability_requirement:
            return False
        
        return True


class EffectChecker:
    """Compile-time checker for magical effects and aura compatibility."""
    
    def __init__(self):
        self.function_signatures: Dict[str, FunctionSignature] = {}
        self.global_context = EffectContext()
        self.violation_handlers: Dict[ViolationType, Callable] = {}
        
        # Set up default violation handlers
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Set up default handlers for different violation types."""
        self.violation_handlers[ViolationType.INCOMPATIBLE_AURAS] = self._handle_incompatible_auras
        self.violation_handlers[ViolationType.CONFLICTING_EFFECTS] = self._handle_conflicting_effects
        self.violation_handlers[ViolationType.MISSING_PREREQUISITE] = self._handle_missing_prerequisite
        self.violation_handlers[ViolationType.POWER_OVERLOAD] = self._handle_power_overload
        self.violation_handlers[ViolationType.INSTABILITY] = self._handle_instability
    
    def register_function(self, signature: FunctionSignature) -> None:
        """Register a function signature for effect checking."""
        self.function_signatures[signature.name] = signature
    
    def check_function_call(self, function_name: str, context: EffectContext) -> List[EffectViolation]:
        """Check if a function call is valid in the given context."""
        violations = []
        
        if function_name not in self.function_signatures:
            violations.append(EffectViolation(
                ViolationType.TYPE_MISMATCH,
                f"Unknown function '{function_name}' - cannot verify effects",
                severity="warning"
            ))
            return violations
        
        signature = self.function_signatures[function_name]
        
        # Check required effects are available
        for required_effect in signature.required_effects:
            if required_effect.name not in context.available_effects:
                violations.append(EffectViolation(
                    ViolationType.MISSING_PREREQUISITE,
                    f"Function '{function_name}' requires effect '{required_effect.name}' but it's not available",
                    suggested_fix=f"Cast a spell that provides '{required_effect.name}' first"
                ))
        
        # Check produced effects are compatible with context
        for produced_effect in signature.produces_effects:
            if not context.can_use_effect(produced_effect):
                if produced_effect.name in context.forbidden_effects:
                    violations.append(EffectViolation(
                        ViolationType.PERMISSION_DENIED,
                        f"Effect '{produced_effect.name}' is forbidden in this context"
                    ))
                else:
                    violations.append(EffectViolation(
                        ViolationType.POWER_OVERLOAD,
                        f"Adding effect '{produced_effect.name}' would exceed power limits or cause instability"
                    ))
        
        # Check effect composition compatibility
        all_effects = context.active_auras.effects + signature.produces_effects
        composition_violations = self.check_effect_composition(all_effects, context)
        violations.extend(composition_violations)
        
        return violations
    
    def check_effect_composition(self, effects: List[Effect], context: EffectContext) -> List[EffectViolation]:
        """Check if a composition of effects is valid."""
        violations = []
        
        # Check for direct conflicts
        for i, effect1 in enumerate(effects):
            for effect2 in effects[i+1:]:
                if effect1.conflicts_with_effect(effect2):
                    violations.append(EffectViolation(
                        ViolationType.CONFLICTING_EFFECTS,
                        f"Effects '{effect1.name}' and '{effect2.name}' are incompatible"
                    ))
        
        # Check aura compatibility
        auras = [effect.aura for effect in effects]
        if not check_aura_compatibility(auras):
            violations.append(EffectViolation(
                ViolationType.INCOMPATIBLE_AURAS,
                "Some auras in the composition are incompatible"
            ))
        
        # Check power limits
        total_power = sum(effect.aura.get_power_level() for effect in effects)
        if total_power > context.power_limit:
            violations.append(EffectViolation(
                ViolationType.POWER_OVERLOAD,
                f"Total power ({total_power}) exceeds limit ({context.power_limit})"
            ))
        
        # Check stability
        test_set = AuraSet()
        for effect in effects:
            test_set.add_effect(effect)
        
        if test_set.get_stability_score() < context.stability_requirement:
            violations.append(EffectViolation(
                ViolationType.INSTABILITY,
                f"Effect composition is unstable (stability: {test_set.get_stability_score():.2f}, required: {context.stability_requirement})"
            ))
        
        return violations
    
    def validate_function_effects(self, function_name: str) -> List[EffectViolation]:
        """Validate the internal consistency of a function's effects."""
        violations = []
        
        if function_name not in self.function_signatures:
            return violations
        
        signature = self.function_signatures[function_name]
        
        # Check that required effects don't conflict with produced effects
        all_effects = signature.get_all_effects()
        for i, effect1 in enumerate(all_effects):
            for effect2 in all_effects[i+1:]:
                if effect1.conflicts_with_effect(effect2):
                    violations.append(EffectViolation(
                        ViolationType.CONFLICTING_EFFECTS,
                        f"Function '{function_name}' has conflicting effects: '{effect1.name}' and '{effect2.name}'"
                    ))
        
        # Check prerequisite chains
        for effect in signature.produces_effects:
            for prerequisite in effect.prerequisites:
                prerequisite_available = (
                    prerequisite in signature.consumes_effects or
                    any(e.name == prerequisite for e in signature.required_effects)
                )
                if not prerequisite_available:
                    violations.append(EffectViolation(
                        ViolationType.MISSING_PREREQUISITE,
                        f"Effect '{effect.name}' requires '{prerequisite}' but it's not available in function '{function_name}'"
                    ))
        
        return violations
    
    def check_plane_restrictions(self, plane_name: str, effects: List[Effect]) -> List[EffectViolation]:
        """Check if effects are allowed in a specific plane."""
        violations = []
        
        if plane_name in self.global_context.plane_restrictions:
            forbidden = self.global_context.plane_restrictions[plane_name]
            for effect in effects:
                if effect.name in forbidden:
                    violations.append(EffectViolation(
                        ViolationType.PERMISSION_DENIED,
                        f"Effect '{effect.name}' is not allowed in plane '{plane_name}'"
                    ))
        
        return violations
    
    # Violation handlers
    def _handle_incompatible_auras(self, violation: EffectViolation) -> str:
        return "Consider using different aura types or applying them in sequence rather than simultaneously."
    
    def _handle_conflicting_effects(self, violation: EffectViolation) -> str:
        return "Remove one of the conflicting effects or use a dispel effect between them."
    
    def _handle_missing_prerequisite(self, violation: EffectViolation) -> str:
        return "Cast the required prerequisite spell or effect first."
    
    def _handle_power_overload(self, violation: EffectViolation) -> str:
        return "Reduce the intensity of some effects or increase your magical capacity."
    
    def _handle_instability(self, violation: EffectViolation) -> str:
        return "Use fewer simultaneous effects or add stabilizing auras."
    
    def suggest_fix(self, violation: EffectViolation) -> str:
        """Get a suggested fix for a violation."""
        if violation.suggested_fix:
            return violation.suggested_fix
        
        handler = self.violation_handlers.get(violation.violation_type)
        if handler:
            return handler(violation)
        
        return "No specific suggestion available."
    
    def get_effect_requirements(self, effect_name: str) -> List[str]:
        """Get the requirements for using a specific effect."""
        requirements = []
        
        for signature in self.function_signatures.values():
            for effect in signature.produces_effects:
                if effect.name == effect_name:
                    requirements.extend(effect.prerequisites)
                    requirements.extend([req.name for req in signature.required_effects])
        
        return list(set(requirements))  # Remove duplicates


def validate_function_effects(signature: FunctionSignature) -> List[EffectViolation]:
    """Standalone function to validate a function signature's effects."""
    checker = EffectChecker()
    checker.register_function(signature)
    return checker.validate_function_effects(signature.name)


def check_effect_composition(effects: List[Effect], context: Optional[EffectContext] = None) -> List[EffectViolation]:
    """Standalone function to check effect composition."""
    if context is None:
        context = EffectContext()
    
    checker = EffectChecker()
    return checker.check_effect_composition(effects, context)


def create_basic_context(power_limit: int = 100, stability_requirement: float = 0.5) -> EffectContext:
    """Create a basic effect context for testing."""
    return EffectContext(
        power_limit=power_limit,
        stability_requirement=stability_requirement
    )