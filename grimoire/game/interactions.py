"""Interaction utilities built atop property system."""

from __future__ import annotations

from typing import Any

from .modifiers import Modifier
from .properties import EntityProperties

# Example interaction: apply damage considering armor modifier

def apply_damage(entity_familiar: Any, amount: float):
    """Reduce 'health' property by damage-adjusted amount."""
    props: EntityProperties = entity_familiar.properties_container  # type: ignore[attr-defined]
    # Armor mitigates damage via multiplicative modifier named 'armor'
    armor_mod = 1.0
    try:
        # Suppose armor stored as modifier on health spec
        health_spec = props._props['health']  # noqa: protected-access
        for mod in health_spec.modifiers:
            if mod.name == 'armor' and mod.mod_type == 'mul':
                armor_mod = mod.value
                break
    except KeyError:
        pass
    effective = max(0, amount * armor_mod)
    props.modify('health', -effective)
    return effective