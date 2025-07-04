"""Familiar class registry and helper utilities.

This sub-package groups specialised `GrimoireFamiliar` subclasses while providing a
simple registry mechanism that lets the interpreter map the *familiar_type* string
passed to the `summon` built-in to the appropriate Python class.
"""
from __future__ import annotations

from typing import Dict, Type

# The base class is imported lazily to avoid circular imports at module load time
# (the interpreter defines GrimoireFamiliar inside its module scope).
import importlib

def _get_base_familiar_cls():
    interpreter = importlib.import_module("grimoire.interpreter")  # type: ignore
    return getattr(interpreter, "GrimoireFamiliar")

# Registry -------------------------------------------------------------------
FAMILIAR_CLASS_REGISTRY: Dict[str, Type] = {}


def register_familiar_class(name: str):
    """Decorator to register a new familiar subclass under a type *name*."""

    def decorator(cls):  # type: ignore
        FAMILIAR_CLASS_REGISTRY[name] = cls
        return cls

    return decorator


def get_familiar_class(name: str):
    """Return the registered subclass for *name* or the base class."""
    return FAMILIAR_CLASS_REGISTRY.get(name, _get_base_familiar_cls())


# Public re-export
__all__ = [
    "register_familiar_class",
    "get_familiar_class",
    "FAMILIAR_CLASS_REGISTRY",
]